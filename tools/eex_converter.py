"""Convert Cao Cao MOD EEX scripts into inspectable UTF-8 JSON.

The parser follows the original EEX editor's scene/section layout and reads
opcode schemas from its ``style.txt`` file.  It intentionally preserves raw
opcode and parameter identifiers so unsupported engine features are not lost.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Parameter:
    kind: int
    name: str


@dataclass(frozen=True)
class Opcode:
    number: int
    name: str
    size: int
    parameters: tuple[Parameter, ...]


def read_style(path: Path) -> dict[int, Opcode]:
    text = path.read_text(encoding="gb18030")
    blocks = [block for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if block.strip()]
    result: dict[int, Opcode] = {}
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 4:
            continue
        number, name, size, count = int(lines[0]), lines[1], int(lines[2]), int(lines[3])
        parameters: list[Parameter] = []
        cursor = 4
        while cursor + 1 < len(lines) and len(parameters) < count:
            kind = int(lines[cursor])
            parameter_name = lines[cursor + 1]
            parameters.append(Parameter(kind, parameter_name))
            cursor += 2
            if cursor + 1 < len(lines):
                try:
                    enum_count = int(lines[cursor])
                    int(lines[cursor + 1])
                except ValueError:
                    continue
                cursor += 1 + enum_count * 2
        result[number] = Opcode(number, name, size, tuple(parameters))
    # New-engine extensions embedded in CczSceneEditor2. LZC uses 0x77 for
    # integer/pointer variable arithmetic; the legacy style.txt ends at 0x6b.
    result.setdefault(119, Opcode(119, "变量运算", 26, (
        Parameter(81, "目标变量类型"),
        Parameter(4, "目标变量编号"),
        Parameter(83, "操作数类型"),
        Parameter(82, "运算符"),
        Parameter(4, "操作数"),
    )))
    result.setdefault(120, Opcode(120, "整型变量赋值", 20, (
        Parameter(4, "变量编号"),
        Parameter(84, "赋值方式"),
        Parameter(2, "人物编号"),
        Parameter(85, "人物属性"),
    )))
    result.setdefault(114, Opcode(114, "信息传送", 0, (
        Parameter(4, "信息编号"),
        Parameter(5, "信息内容"),
    )))
    result.setdefault(117, Opcode(117, "S特殊形象指定", 14, (
        Parameter(2, "人物编号"),
        Parameter(80, "形象编号"),
        Parameter(82, "设置方式"),
    )))
    result[70] = Opcode(70, "友军出场设定", 1042, (
        Parameter(2, "人物编号"), Parameter(38, "隐藏"),
        Parameter(4, "横坐标"), Parameter(4, "纵坐标"),
        Parameter(43, "朝向"), Parameter(62, "等级加成"),
        Parameter(69, "队伍限制"), Parameter(7, "AI方针"),
        Parameter(2, "目标人物"), Parameter(4, "目标横坐标"), Parameter(4, "目标纵坐标"),
    ))
    result[71] = Opcode(71, "敌军出场设定", 4482, (
        Parameter(2, "人物编号"), Parameter(38, "敌方援军"), Parameter(38, "隐藏"),
        Parameter(4, "横坐标"), Parameter(4, "纵坐标"),
        Parameter(43, "朝向"), Parameter(62, "等级加成"),
        Parameter(69, "队伍限制"), Parameter(7, "AI方针"),
        Parameter(2, "目标人物"), Parameter(4, "目标横坐标"), Parameter(4, "目标纵坐标"),
    ))
    return result


class EEXParser:
    def __init__(self, path: Path, opcodes: dict[int, Opcode]) -> None:
        self.path = path
        self.data = path.read_bytes()
        self.opcodes = opcodes
        if self.data[:4] != b"EEX\x00":
            raise ValueError(f"not an EEX script: {path}")

    def u16(self, offset: int) -> int:
        return struct.unpack_from("<H", self.data, offset)[0]

    def i16(self, offset: int) -> int:
        return struct.unpack_from("<h", self.data, offset)[0]

    def i32(self, offset: int) -> int:
        return struct.unpack_from("<i", self.data, offset)[0]

    def scene_offsets(self) -> list[int]:
        result: list[int] = []
        cursor = 10
        while cursor + 4 <= len(self.data):
            offset = self.i32(cursor)
            if offset > 65535 or offset < 10:
                break
            result.append(offset)
            cursor += 4
        return result

    def value(self, kind: int, offset: int) -> tuple[int | str, int]:
        if kind == 4:
            return self.i32(offset), offset + 4
        if kind == 5:
            end = self.data.index(0, offset)
            return self.data[offset:end].decode("gb18030", errors="replace"), end + 1
        return self.i16(offset), offset + 2

    def instruction(self, offset: int) -> tuple[dict[str, Any], int]:
        start = offset
        number = self.u16(offset)
        if number == 0:
            return {"offset": start, "opcode": 0, "name": "指令块结束"}, offset + 2
        style = self.opcodes.get(number)
        if style is None:
            raise ValueError(f"unknown opcode {number} at 0x{offset:x}")
        offset += 2
        values: list[dict[str, Any]] = []

        fixed_deployment_words = {75: 11}
        if number in fixed_deployment_words and not style.parameters:
            end = start + style.size
            words = list(struct.unpack_from(f"<{(end - offset) // 2}h", self.data, offset))
            record_words = fixed_deployment_words[number]
            records = [words[index:index + record_words] for index in range(0, len(words), record_words)]
            return {
                "offset": start,
                "opcode": number,
                "name": style.name,
                "record_words": record_words,
                "records": records,
            }, end

        if number == 1:
            condition, offset = self.instruction(offset)
            block_size = self.u16(offset)
            offset += 2
            then_items: list[dict[str, Any]] = []
            while self.u16(offset) != 0:
                item, offset = self.instruction(offset)
                then_items.append(item)
            offset += 2

            else_items: list[dict[str, Any]] = []
            if offset + 6 <= len(self.data) and self.u16(offset) == 1 and self.u16(offset + 2) == 3:
                else_size = self.u16(offset + 4)
                offset += 6
                while self.u16(offset) != 0:
                    item, offset = self.instruction(offset)
                    else_items.append(item)
                offset += 2
            else:
                else_size = 0
            return {
                "offset": start,
                "opcode": number,
                "name": style.name,
                "condition": condition,
                "then_size": block_size,
                "then": then_items,
                "else_size": else_size,
                "else": else_items,
            }, offset

        if number == 5:
            parameter_id = self.u16(offset)
            offset += 2
            true_count = self.u16(offset)
            offset += 2
            true_values = [self.i16(offset + index * 2) for index in range(true_count)]
            offset += true_count * 2
            false_parameter_id = self.u16(offset)
            false_count = self.u16(offset + 2)
            offset += 4
            false_values = [self.i16(offset + index * 2) for index in range(false_count)]
            offset += false_count * 2
            values = [
                {"parameter_id": parameter_id, "name": "成立变量", "value": true_values},
                {"parameter_id": false_parameter_id, "name": "不成立变量", "value": false_values},
            ]
        else:
            limit = start + style.size if number in (70, 71) else None
            while True:
                for parameter in style.parameters:
                    parameter_id = self.u16(offset)
                    raw, offset = self.value(parameter.kind, offset + 2)
                    values.append({
                        "parameter_id": parameter_id,
                        "type": parameter.kind,
                        "name": parameter.name,
                        "value": raw,
                    })
                if limit is None or offset >= limit:
                    break
            if limit is not None and offset != limit:
                raise ValueError(f"opcode {number} size mismatch at 0x{start:x}")

        return {
            "offset": start,
            "opcode": number,
            "name": style.name,
            "parameters": values,
        }, offset

    def section(self, offset: int) -> tuple[dict[str, Any], int]:
        payload_size = self.u16(offset)
        end = offset + payload_size + 2
        cursor = offset + 2
        conditions: list[dict[str, Any]] = []
        while self.u16(cursor) != 0:
            item, cursor = self.instruction(cursor)
            conditions.append(item)
        cursor += 2
        instruction_size = self.u16(cursor)
        instruction_end = cursor + instruction_size
        cursor += 2
        instructions: list[dict[str, Any]] = []
        while cursor < instruction_end:
            item, cursor = self.instruction(cursor)
            instructions.append(item)
        if cursor != instruction_end or end < instruction_end:
            raise ValueError(
                f"section boundary mismatch at 0x{offset:x}: section=0x{end:x}, instructions=0x{cursor:x}"
            )
        trailing = self.data[cursor:end]
        return {
            "offset": offset,
            "size": payload_size,
            "conditions": conditions,
            "instructions": instructions,
            "trailing_bytes": trailing.hex(" "),
        }, end

    def parse(self) -> dict[str, Any]:
        scenes: list[dict[str, Any]] = []
        for scene_index, offset in enumerate(self.scene_offsets()):
            section_count = self.i16(offset)
            cursor = offset + 2
            sections: list[dict[str, Any]] = []
            for section_index in range(max(0, section_count)):
                section_start = cursor
                section_end = min(len(self.data), section_start + self.u16(section_start) + 2)
                try:
                    section, cursor = self.section(section_start)
                except (ValueError, IndexError, struct.error) as error:
                    section = {
                        "offset": section_start,
                        "size": self.u16(section_start),
                        "index": section_index,
                        "parse_error": str(error),
                        "raw_bytes": self.data[section_start:section_end].hex(" "),
                        "conditions": [],
                        "instructions": [],
                    }
                    cursor = section_end
                sections.append(section)
            scenes.append({
                "index": scene_index,
                "offset": offset,
                "section_count": section_count,
                "sections": sections,
            })
        result = {
            "format": "EEX",
            "source": self.path.name,
            "kind": self.path.stem[:1].upper(),
            "scene_count": len(scenes),
            "scenes": scenes,
            "deployment_tables": self.deployment_tables(),
        }
        result["summary"] = summarize(result)
        return result

    def deployment_tables(self) -> list[dict[str, Any]]:
        """Locate the adjacent fixed-size 70/71 tables even inside an unsupported section."""
        tables: list[dict[str, Any]] = []
        for offset in range(0, max(0, len(self.data) - self.opcodes[70].size - 2)):
            if self.u16(offset) != 70:
                continue
            enemy_offset = offset + self.opcodes[70].size
            if self.u16(enemy_offset) != 71:
                continue
            friend, friend_end = self.instruction(offset)
            enemy, enemy_end = self.instruction(enemy_offset)
            friend["record_count"] = 20
            enemy["record_count"] = 80
            tables.append({
                "offset": offset,
                "friend": friend,
                "enemy": enemy,
                "end_offset": enemy_end,
                "contiguous": friend_end == enemy_offset,
            })
        return tables


def summarize(document: dict[str, Any]) -> dict[str, Any]:
    def flatten(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for item in items:
            result.append(item)
            if "condition" in item:
                result.extend(flatten([item["condition"]]))
                result.extend(flatten(item["then"]))
                result.extend(flatten(item["else"]))
        return result

    instructions = []
    unparsed_sections = 0
    for scene in document["scenes"]:
        for section in scene["sections"]:
            unparsed_sections += int("parse_error" in section)
            instructions.extend(flatten(section["conditions"] + section["instructions"]))
    instructions = [item for item in instructions if item["opcode"] != 0]
    deployments = [item for item in instructions if item["opcode"] in (70, 71, 75)]
    deployment_tables = document.get("deployment_tables", [])
    dialogue = [
        parameter["value"]
        for item in instructions
        for parameter in item.get("parameters", [])
        if isinstance(parameter.get("value"), str) and parameter["value"].strip()
    ]
    return {
        "section_count": sum(scene["section_count"] for scene in document["scenes"] if scene["section_count"] > 0),
        "instruction_count": len(instructions),
        "unparsed_section_count": unparsed_sections,
        "deployment_instruction_count": len(deployments) + len(deployment_tables) * 2,
        "deployment": deployments,
        "deployment_tables": deployment_tables,
        "text": dialogue,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="EEX file or directory containing EEX files")
    parser.add_argument("--style", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    opcodes = read_style(args.style)
    inputs = sorted(args.input.glob("*.eex")) if args.input.is_dir() else [args.input]
    args.output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for source in inputs:
        document = EEXParser(source, opcodes).parse()
        target = args.output / f"{source.stem}.json"
        target.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.append({"source": source.name, **document["summary"]})
        print(f"{source.name}: {document['scene_count']} scenes, {document['summary']['instruction_count']} instructions")
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
