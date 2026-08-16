from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from tools.extra_chapters71_108_data import HISTORICAL_DEATHS, STAGES, all_new_heroes
    from tools.integrate_chapters82_108 import make_stage
except ImportError:
    from extra_chapters71_108_data import HISTORICAL_DEATHS, STAGES, all_new_heroes
    from integrate_chapters82_108 import make_stage


ROOT = Path(__file__).resolve().parents[1]
TEMP_SOURCE = Path(r"C:\tmp\dongzhou_chapters_71_108.json")
SOURCE_71_81 = ROOT / "assets/lzc/chapter_sources/dongzhou_71_81.json"
STAGE_DIR = ROOT / "game/sce/dongzhou/stage"
MANIFEST_DIR = ROOT / "assets/lzc/map_sources"

INSERT_AFTER = {
    "71": ["72a"], "73": ["73b", "74"], "75": ["76", "77"], "78": ["78b"],
    "82": ["82b", "83a"], "84": ["84b"], "86": ["86b"], "101": ["101a"],
    "106": ["107a"], "107": ["108a"],
}

NEXT_BATTLE = {
    "72a": "昭关脱逃", "73b": "江上刺庆忌", "74": "柏举之战", "75": "郢都攻防",
    "76": "秦楚复郢", "77": "鲁国平叛", "78b": "携李之战", "82b": "叶公平楚",
    "83a": "笠泽灭吴", "84b": "中山之战", "86b": "商於拓境", "101a": "鄗代之战",
    "107a": "城父败李信", "108a": "六国归一",
}


def load_sources() -> dict[int, dict]:
    rows = json.loads(TEMP_SOURCE.read_text(encoding="utf-8"))
    subset = [row for row in rows if 71 <= int(row["ordinal"]) <= 81]
    SOURCE_71_81.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_71_81.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {int(row["ordinal"]): row for row in rows}


def source_supplement(spec: dict, sources: dict[int, dict], count: int = 10) -> str:
    chapters = spec.get("sources", (spec["chapter"],))
    pieces: list[str] = []
    for chapter in chapters:
        text = re.sub(r"\s+", "", sources[chapter]["text"])
        start, end = spec.get("slice", (0.0, 1.0)) if chapter == spec["chapter"] else (0.0, 1.0)
        text = text[int(len(text) * start):int(len(text) * end)]
        sentences = [item for item in re.split(r"(?<=[。！？])", text) if len(item) >= 16]
        if not sentences:
            continue
        stride = max(1, len(sentences) // count)
        pieces.extend(sentences[index][:170] for index in range(0, len(sentences), stride))
    pieces = pieces[:count]
    return "".join(
        f'  {{speaker="原著",text="{piece.replace(chr(34), chr(39))}"}},\n'
        for piece in pieces
    )


def make_extra_stage(spec: dict, manifest: dict, sources: dict[int, dict]) -> str:
    if spec["outcome"] != "attempt":
        text = make_stage(spec, manifest, sources, NEXT_BATTLE[spec["id"]])
        return text.replace(" intro={\n", " intro={\n" + source_supplement(spec, sources), 1)
    adapted = dict(spec, outcome="death")
    text = make_stage(adapted, manifest, sources, NEXT_BATTLE[spec["id"]])
    text = text.replace(" intro={\n", " intro={\n" + source_supplement(spec, sources), 1)
    enemy_id, enemy_label = spec["enemy"]
    own_id, own_label = spec["own"][0]
    ex, ey = manifest["mission"]["enemy_position"]
    text = text.replace(
        f'game:generate_unit("{enemy_id}",1,Enum.force.enemy,{{{ex},{ey}}});',
        f'game:generate_unit("{enemy_id}",1,Enum.force.enemy,{{{ex},{ey}}});game:set_unit_invulnerable("{enemy_id}",true);',
        1,
    )
    text = text.replace(
        f'if not game:has_unit("{enemy_id}")then return Enum.status.victory end',
        f'if game:is_unit_within("{own_id}",{{{ex},{ey}}},1)then return Enum.status.victory end',
        1,
    )
    text = text.replace(
        f"{enemy_label}按原著记载在此役败亡，相关死亡已写入历史结局。",
        f"{own_label}已突破护卫接近{enemy_label}；交锋成败及其结局按原著剧情收束。",
        1,
    )
    return text


def insert_stage_ids(ids: list[str]) -> list[str]:
    additions = {value for values in INSERT_AFTER.values() for value in values}
    ids = [stage_id for stage_id in ids if stage_id not in additions]
    result: list[str] = []
    for stage_id in ids:
        result.append(stage_id)
        result.extend(INSERT_AFTER.get(stage_id, ()))
    return result


def update_config(heroes: list[tuple[str, str, str, str, str, int]]) -> None:
    path = ROOT / "game/sce/dongzhou/config.lua"
    text = path.read_text(encoding="utf-8")
    missing = [hero for hero in heroes if f'id = "{hero[0]}"' not in text]
    if missing:
        block = "\n".join(
            f'        ,{{ id = "{hero_id}", class = "{klass}", stat = {{96,94,96,95,94}}, model = "{model}" }}'
            for hero_id, klass, model, _, _, _ in missing
        )
        marker = "    },\n    equipments = {}"
        assert marker in text
        text = text.replace(marker, "\n" + block + "\n" + marker, 1)
    match = re.search(r"stages = \{([^}]*)\}", text)
    assert match
    ids = re.findall(r'"([0-9]+[a-z]?)"', match.group(1))
    replacement = "stages = { " + ", ".join(f'\"{stage_id}\"' for stage_id in insert_stage_ids(ids)) + " }"
    text = text[:match.start()] + replacement + text[match.end():]
    path.write_text(text, encoding="utf-8")


def update_save() -> None:
    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"STAGE_TABLE_VERSION = \d+", "STAGE_TABLE_VERSION = 18", text, count=1)
    match = re.search(r"CURRENT_DONGZHOU_STAGES = \((.*?)\n\)", text, re.S)
    assert match
    ids = re.findall(r'"([0-9]+[a-z]?)"', match.group(1))
    replacement = "CURRENT_DONGZHOU_STAGES = (\n    " + ",".join(f'\"{stage_id}\"' for stage_id in insert_stage_ids(ids)) + "\n)"
    text = text[:match.start()] + replacement + text[match.end():]
    path.write_text(text, encoding="utf-8")


def update_gui(heroes: list[tuple[str, str, str, str, str, int]], manifests: dict[str, dict]) -> None:
    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    marker = "# Dongzhou supplemental chapters 71-108 metadata"
    if marker in text:
        text = text[:text.index("\n" + marker)] + "\n\n" + text[text.index('if _original_name == "__main__":'):]
    labels = {hero_id: label for hero_id, _, _, label, _, _ in heroes}
    bios = {hero_id: bio for hero_id, _, _, _, bio, _ in heroes}
    portraits = {hero_id: portrait for hero_id, _, _, _, _, portrait in heroes}
    speakers = {labels[hero_id]: portrait for hero_id, portrait in portraits.items()}
    sizes = {f"{spec['map']}.png": tuple(manifests[spec["id"]]["grid"] + [48]) for spec in STAGES}
    addition = (
        f"\n{marker}\n_LARGE_BATTLE_MAPS.update({sizes!r})\n"
        f"HERO_LABELS.update({labels!r})\nHERO_BIOS.update({bios!r})\n"
        f"PORTRAIT_INDEX_BY_HERO.update({portraits!r})\nSPEAKER_PORTRAIT_INDEX.update({speakers!r})\n"
        f"HISTORICAL_DEATH_HEROES.update({HISTORICAL_DEATHS!r})\n\n"
    )
    anchor = 'if _original_name == "__main__":'
    assert anchor in text
    path.write_text(text.replace(anchor, addition + anchor, 1), encoding="utf-8")


def update_older_tests() -> None:
    path = ROOT / "rl/chapters71_80_test.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('    "75": ("m123", "ch75_77", (92, 64)),\n', "")
    text = text.replace(
        '    assert CURRENT_DONGZHOU_STAGES[first_stage:first_stage + len(STAGES)] == tuple(STAGES)\n    assert CURRENT_DONGZHOU_STAGES[first_stage + len(STAGES)] == "81"',
        '    positions = [CURRENT_DONGZHOU_STAGES.index(stage_id) for stage_id in STAGES]\n    assert positions == sorted(positions)\n    assert CURRENT_DONGZHOU_STAGES.index("80") < CURRENT_DONGZHOU_STAGES.index("81")',
    )
    text = text.replace('    assert \'"71", "72", "73", "75", "78", "79", "80"\' in config\n', "")
    text = text.replace('    assert "第七十四回" in (ROOT / "game/sce/dongzhou/stage/75.lua").read_text(encoding="utf-8")\n', "")
    text = text.replace('    assert "第七十五至七十七回" in (ROOT / "game/sce/dongzhou/stage/75.lua").read_text(encoding="utf-8")\n', "")
    text = text.replace(
        '    rows75 = stage_rows((ROOT / "game/sce/dongzhou/stage/75.lua").read_text(encoding="utf-8"))\n'
        '    assert reachable(rows75, (83, 29), (15, 48))\n'
        '    assert reachable(rows75, (15, 48), (88, 8))\n',
        "",
    )
    text = text.replace(
        'chapters 71-80 ok: seven battle maps, merged 74-77 narrative, terrain contracts, saves, and runtime launches',
        'chapters 71-80 legacy stages ok: terrain contracts, saves, and runtime launches',
    )
    path.write_text(text, encoding="utf-8")

    path = ROOT / "rl/chapters82_108_test.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '    assert CURRENT_DONGZHOU_STAGES[-len(STAGE_IDS):] == tuple(STAGE_IDS)\n    assert STAGE_TABLE_VERSION == 17',
        '    positions = [CURRENT_DONGZHOU_STAGES.index(stage_id) for stage_id in STAGE_IDS]\n    assert positions == sorted(positions)\n    assert STAGE_TABLE_VERSION >= 17',
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    sources = load_sources()
    manifests: dict[str, dict] = {}
    for spec in STAGES:
        path = MANIFEST_DIR / f"{spec['map']}_ch{spec['id']}_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifests[spec["id"]] = manifest
        (STAGE_DIR / f"{spec['id']}.lua").write_text(make_extra_stage(spec, manifest, sources), encoding="utf-8")
    heroes = all_new_heroes()
    update_config(heroes)
    update_save()
    update_gui(heroes, manifests)
    update_older_tests()
    print(f"integrated {len(STAGES)} split and supplemental stages across chapters 71-108")


if __name__ == "__main__":
    main()
