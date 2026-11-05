#!/usr/bin/env python3
"""Extract Lua battle speech and recover the most likely speaking role."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

try:
    from pypinyin import lazy_pinyin
except ImportError:  # The build still works, but named-role recovery is less precise.
    lazy_pinyin = None


SPEECH_PATTERN = re.compile(
    r'push_cmd_speak\s*\(\s*([^,]+)\s*,\s*"((?:[^"\\]|\\.)*)"\s*\)'
)
GENERATED_UNIT_PATTERN = re.compile(
    r'(?:local\s+)?([A-Za-z_]\w*)\s*=\s*game:generate_unit\s*\(\s*"([^"]+)"'
)
COMMANDERS_PATTERN = re.compile(r'gcommanders\s*=\s*\{([^}]*)\}', re.DOTALL)
QUOTED_VALUE_PATTERN = re.compile(r'"([^"]+)"')
REFERENCE_HERO_PATTERN = re.compile(r'\[\s*"([^"]+)"\s*\]')

HERO_SPEAKER_ALIASES = {
    "ChengDeChen": "成得臣",
    "ChongEr": "重耳",
    "ChuBianJiang": "楚军边将",
    "JiGuang": "公子光",
    "PalaceDoctor": "医者",
    "PalaceSearchGuard": "宫中搜卒",
    "QinJiang": "秦军将领",
    "TuRenFei": "徒人费",
    "XunYing": "智罃",
}


def normalized_pinyin(value: str) -> str:
    if not value:
        return ""
    if lazy_pinyin is None:
        return re.sub(r"[^a-z0-9]", "", value.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(lazy_pinyin(value)).lower())


def hero_base(hero_id: str) -> str:
    return re.sub(r"\d+[a-z]?", "", str(hero_id), flags=re.IGNORECASE).strip("_-")


def role_fallback(hero_id: str, reference: str) -> str:
    value = f"{hero_id} {reference}".lower()
    labels = (
        (("archer", "bow"), "战场弓手"),
        (("guard", "soldier", "warrior", "escort"), "战场军士"),
        (("hunter",), "猎人"),
        (("deadman",), "死士"),
        (("ambush", "infiltrator"), "伏兵将领"),
        (("vanguard",), "前军将领"),
        (("lord", "king", "gong", "hou"), "战场主将"),
        (("captain", "commander", "leader"), "战场将领"),
    )
    for tokens, label in labels:
        if any(token in value for token in tokens):
            return label
    return "战场人物"


def match_speaker(hero_id: str, speakers: list[str], reference: str = "") -> str:
    raw_base = hero_base(hero_id)
    if raw_base in HERO_SPEAKER_ALIASES:
        return HERO_SPEAKER_ALIASES[raw_base]
    base = normalized_pinyin(raw_base)
    if not base:
        return role_fallback(hero_id, reference)
    ranked: list[tuple[int, int, str]] = []
    for speaker in speakers:
        candidate = normalized_pinyin(speaker)
        if not candidate:
            continue
        if base == candidate:
            ranked.append((3, len(candidate), speaker))
        elif len(candidate) >= 4 and (base.startswith(candidate) or candidate.startswith(base)):
            ranked.append((2, len(candidate), speaker))
        elif len(candidate) >= 5 and candidate in base:
            ranked.append((1, len(candidate), speaker))
    if ranked:
        return max(ranked)[2]
    return role_fallback(hero_id, reference)


def decode_lua_string(value: str) -> str:
    return (value.replace(r"\n", "\n").replace(r'\"', '"').replace(r"\\", "\\"))


def extract_runtime_speech(stage: dict, stage_dir: Path, speakers: list[str]) -> list[dict]:
    stage_file = str(stage.get("file") or "")
    source_path = stage_dir / stage_file
    if not stage_file or not source_path.exists():
        return []
    source = source_path.read_text(encoding="utf-8")
    generated_units = {
        variable: hero_id
        for variable, hero_id in GENERATED_UNIT_PATTERN.findall(source)
    }
    commander_match = COMMANDERS_PATTERN.search(source)
    commanders = QUOTED_VALUE_PATTERN.findall(commander_match.group(1)) if commander_match else []
    results: list[dict] = []
    for source_index, match in enumerate(SPEECH_PATTERN.finditer(source)):
        reference = match.group(1).strip()
        text = decode_lua_string(match.group(2)).strip()
        hero_id = ""
        if re.fullmatch(r"\d+", reference):
            commander_index = int(reference)
            if 0 <= commander_index < len(commanders):
                hero_id = commanders[commander_index]
        elif re.fullmatch(r'"[^"]+"', reference):
            hero_id = reference[1:-1]
        else:
            bracket_reference = REFERENCE_HERO_PATTERN.search(reference)
            hero_id = generated_units.get(reference, "") or (bracket_reference.group(1) if bracket_reference else "")
        speaker = match_speaker(hero_id, speakers, reference) if hero_id else role_fallback("", reference)
        digest = hashlib.sha256(f"{stage_file}|{source_index}|{speaker}|{text}".encode("utf-8")).hexdigest()[:10]
        results.append({
            "sourceIndex": source_index,
            "reference": reference,
            "heroId": hero_id,
            "speaker": speaker,
            "text": text,
            "eventId": f"lua-{source_index:03d}-{digest}",
            "sourceFile": stage_file,
        })
    return results
