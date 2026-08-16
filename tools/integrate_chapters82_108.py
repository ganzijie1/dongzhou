from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from tools.chapters82_108_data import HISTORICAL_DEATHS, STAGES, STAGE_IDS, all_new_heroes
except ImportError:
    from chapters82_108_data import HISTORICAL_DEATHS, STAGES, STAGE_IDS, all_new_heroes


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "assets/lzc/chapter_sources/dongzhou_82_108.json"
STAGE_DIR = ROOT / "game/sce/dongzhou/stage"
MANIFEST_DIR = ROOT / "assets/lzc/map_sources"


def lua_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "")


def lua_story(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f'  {{speaker="{lua_escape(speaker)}",text="{lua_escape(text)}"}},'
        for speaker, text in items
    )


def stage_number(stage_id: str) -> int:
    return int("".join(character for character in stage_id if character.isdigit()))


def source_rows() -> dict[int, dict]:
    return {int(row["ordinal"]): row for row in json.loads(SOURCE_PATH.read_text(encoding="utf-8"))}


def chapter_title(row: dict) -> str:
    return re.sub(r"^第[^回]+回", "", row["title"]).strip()


def story_chunks(text: str, start: float = 0.0, end: float = 1.0, count: int = 16) -> list[str]:
    text = re.sub(r"\s+", "", text)
    sentences = [part.strip() for part in re.split(r"(?<=[。！？])", text) if 18 <= len(part.strip()) <= 260]
    lo, hi = int(len(sentences) * start), max(int(len(sentences) * end), 1)
    sentences = sentences[lo:hi] or sentences
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) > 190 and current:
            chunks.append(current)
            current = sentence
        else:
            current += sentence
    if current:
        chunks.append(current)
    if len(chunks) <= count:
        return chunks
    indices = [round(index * (len(chunks) - 1) / (count - 1)) for index in range(count)]
    return [chunks[index] for index in indices]


def stage_story(spec: dict, sources: dict[int, dict], next_battle: str) -> tuple[str, str, list[tuple[str, str]], list[tuple[str, str]]]:
    chapters = spec.get("sources", (spec["chapter"],))
    if not isinstance(chapters, tuple):
        chapters = tuple(chapters)
    selected: list[str] = []
    per_chapter = max(8, 18 // len(chapters))
    for chapter in chapters:
        row = sources[chapter]
        start, end = spec.get("slice", (0.0, 1.0)) if chapter == spec["chapter"] else (0.0, 1.0)
        selected.extend(story_chunks(row["text"], start, end, per_chapter))
    selected = selected[:18]
    title = "；".join(chapter_title(sources[chapter]) for chapter in chapters)
    if len(chapters) == 2:
        chapter_label = f"第{chapters[0]}至{chapters[-1]}回"
    else:
        chapter_label = sources[chapters[0]]["title"].split("回", 1)[0] + "回"
    own_label = spec["own"][0][1]
    enemy_label = spec["enemy"][1]
    intro = [
        ("", spec["focus"]),
        (own_label, spec["objective"]),
        (enemy_label, f"{spec['battle']}胜负未分，守军各依地势列阵，绝不轻退。"),
    ]
    split = max(7, len(selected) // 2)
    intro.extend(("", chunk) for chunk in selected[:split])
    outcome_text = {
        "death": f"{enemy_label}按原著记载在此役败亡，相关死亡已写入历史结局。",
        "capture": f"{enemy_label}军势瓦解并被控制，依原著结局作俘获或请降处理。",
        "retreat": f"{enemy_label}不可由玩家击杀；其部众溃散后将按史实路线撤离战场。",
    }[spec["outcome"]]
    victory = [("", chunk) for chunk in selected[split:]]
    reward = 26000 + stage_number(spec["id"]) * 20
    victory.extend([
        ("", outcome_text),
        (own_label, f"{spec['battle']}既定目标已经完成，收束军伍并依史实继续后续进程。"),
        ("军令", f"{spec['battle']}完成，获得{reward}金币。下一关：{next_battle}。"),
    ])
    return chapter_label, title, intro, victory


def positions(values: list[list[int]]) -> str:
    return "{" + ",".join(f"{{{x},{y}}}" for x, y in values) + "}"


def make_stage(spec: dict, manifest: dict, sources: dict[int, dict], next_battle: str) -> str:
    rows = "\n".join(f'        "{row}",' for row in manifest["terrain_rows"])
    mission = manifest["mission"]
    own_ids = [hero_id for hero_id, _ in spec["own"]]
    chapter_label, title, intro, victory = stage_story(spec, sources, next_battle)
    sites = []
    for index, (x, y) in enumerate(manifest["supply_sites"]):
        sites.append(f' {{id="site_{index}",name="战地补给点",position={{{x},{y}}},restore_hp=18,restore_mp=10,rewards={{}}}},')
    deploy = ",".join(
        f'{{position={{{position[0]},{position[1]}}},hero="{hero_id}"}}'
        for (hero_id, _), position in zip(spec["own"], mission["own_positions"])
    )
    enemy_id = spec["enemy"][0]
    enemy_position = mission["enemy_position"]
    retreat_exit = mission["retreat_exit"]
    reward = 26000 + stage_number(spec["id"]) * 20
    invulnerable = f'game:set_unit_invulnerable("{enemy_id}",true)' if spec["outcome"] == "retreat" else ""
    if spec["outcome"] == "retreat":
        update = (
            'if phase==1 and not game:has_unit("LateZhouGuardEnemy") and not game:has_unit("LateZhouArcherEnemy")then '
            f'phase=2;game:push_cmd_speak(enemy_unit,"主力已溃，依史实撤出战场！");'
            f'game:push_cmd_move(enemy_unit,{{{retreat_exit[0]},{retreat_exit[1]}}})end'
        )
        victory_condition = (
            f'if phase==2 and game:is_unit_within("{enemy_id}",{{{retreat_exit[0]},{retreat_exit[1]}}},1)then '
            "return Enum.status.victory end"
        )
    else:
        update = ""
        victory_condition = f'if not game:has_unit("{enemy_id}")then return Enum.status.victory end'
    commanders = "{" + ",".join(f'"{hero_id}"' for hero_id in own_ids) + "}"
    return f'''gally_hold_position=true
gsupply_enabled=true
gitems={{{{id="medicine",name="金疮药",hp=120,mp=0,price=120,initial=2}},{{id="spirit_powder",name="清心散",hp=0,mp=30,price=150,initial=1}}}}
gcommanders={commanders}
gevents_enabled=true
gduel_enabled=false
gduels={{}}
gsites={{
{chr(10).join(sites)}
}}
gstory={{chapter="{lua_escape(chapter_label)}",title="{lua_escape(title)}",battle_title="{lua_escape(spec['battle'])}",objective="{lua_escape(spec['objective'])}",map_asset="{spec['map']}.png",
 intro={{
{lua_story(intro)}
 }},
 events={{{{id="historical_outcome",trigger="scripted",turn=0,hp_percent=0,speaker="{lua_escape(spec['enemy'][1])}",text="{lua_escape(spec['focus'])}"}}}},
 victory={{
{lua_story(victory)}
 }},
 defeat={{{{speaker="",text="任一主将被击退，或未能完成原著记载的战役目标，本关失败。"}}}}
}}
local phase=1
local enemy_unit=0
local function many(game,h,p,f)for _,v in ipairs(p)do game:generate_unit(h,1,f,v)end end
function on_deploy(game)for _,h in ipairs(gcommanders)do game:appoint_hero(h,1)end end
function on_begin(game)
 enemy_unit=game:generate_unit("{enemy_id}",1,Enum.force.enemy,{{{enemy_position[0]},{enemy_position[1]}}});{invulnerable}
 many(game,"LateZhouGuardOwn",{positions(mission['own_guards'])},Enum.force.own)
 many(game,"LateZhouArcherOwn",{positions(mission['own_archers'])},Enum.force.own)
 many(game,"LateZhouGuardEnemy",{positions(mission['enemy_guards'])},Enum.force.enemy)
 many(game,"LateZhouArcherEnemy",{positions(mission['enemy_archers'])},Enum.force.enemy)
end
function on_update(game){update}
end
function on_victory(game)end
function on_defeat(game)end
function end_condition(game)
 for _,h in ipairs(gcommanders)do if not game:has_unit(h)then return Enum.status.defeat end end
 {victory_condition}
 return Enum.status.undecided
end
gstage={{title_id="Dongzhou{spec['id']}",turn_limit=36,map={{blocked_edges={{}},size={{{manifest['grid'][0]},{manifest['grid'][1]}}},terrain={{
{rows}
}},file="map.bmp"}},deploy={{unselectables={{{deploy}}},num_required_selectables=0,selectables={{}}}},rewards={{equipments={{}},money={reward}}}}}
'''


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
    current_tail = '"79", "80", "81" }'
    if f'"{STAGE_IDS[-1]}" }}' not in text:
        assert current_tail in text
        replacement = '"79", "80", "81", ' + ", ".join(f'"{stage_id}"' for stage_id in STAGE_IDS) + " }"
        text = text.replace(current_tail, replacement, 1)
    path.write_text(text, encoding="utf-8")


def update_save() -> None:
    path = ROOT / "rl/save_system.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("STAGE_TABLE_VERSION = 16", "STAGE_TABLE_VERSION = 17", 1)
    if f'"{STAGE_IDS[-1]}"\n)' not in text:
        marker = '"79","80","81"\n)'
        assert marker in text
        replacement = '"79","80","81",' + ",".join(f'"{stage_id}"' for stage_id in STAGE_IDS) + "\n)"
        text = text.replace(marker, replacement, 1)
    path.write_text(text, encoding="utf-8")


def update_gui(heroes: list[tuple[str, str, str, str, str, int]], manifests: dict[str, dict]) -> None:
    path = ROOT / "rl/play_gui.py"
    text = path.read_text(encoding="utf-8")
    if "# Dongzhou chapters 82-108 metadata" in text:
        return
    labels = {hero_id: label for hero_id, _, _, label, _, _ in heroes}
    bios = {hero_id: bio for hero_id, _, _, _, bio, _ in heroes}
    portraits = {hero_id: portrait for hero_id, _, _, _, _, portrait in heroes}
    speakers = {label: portraits[hero_id] for hero_id, label in labels.items()}
    sizes = {f"{spec['map']}.png": tuple(manifests[spec["id"]]["grid"] + [48]) for spec in STAGES}
    addition = (
        "\n# Dongzhou chapters 82-108 metadata\n"
        f"_LARGE_BATTLE_MAPS.update({sizes!r})\n"
        f"HERO_LABELS.update({labels!r})\n"
        f"HERO_BIOS.update({bios!r})\n"
        f"PORTRAIT_INDEX_BY_HERO.update({portraits!r})\n"
        f"SPEAKER_PORTRAIT_INDEX.update({speakers!r})\n"
        f"HISTORICAL_DEATH_HEROES.update({HISTORICAL_DEATHS!r})\n\n"
    )
    anchor = 'if _original_name == "__main__":'
    assert anchor in text
    path.write_text(text.replace(anchor, addition + anchor, 1), encoding="utf-8")


def update_previous_test() -> None:
    path = ROOT / "rl/chapter81_test.py"
    text = path.read_text(encoding="utf-8")
    old = '    assert CURRENT_DONGZHOU_STAGES[-3:] == ("79", "80", "81")'
    new = '    assert CURRENT_DONGZHOU_STAGES[CURRENT_DONGZHOU_STAGES.index("81") - 2:CURRENT_DONGZHOU_STAGES.index("81") + 1] == ("79", "80", "81")'
    if old in text:
        text = text.replace(old, new, 1)
    text = text.replace("assert STAGE_TABLE_VERSION == 16", "assert STAGE_TABLE_VERSION >= 16", 1)
    path.write_text(text, encoding="utf-8")
    batch_path = ROOT / "rl/chapters71_80_test.py"
    batch_text = batch_path.read_text(encoding="utf-8")
    batch_text = batch_text.replace("assert STAGE_TABLE_VERSION == 16", "assert STAGE_TABLE_VERSION >= 15", 1)
    batch_path.write_text(batch_text, encoding="utf-8")


def main() -> None:
    sources = source_rows()
    manifests = {}
    for index, spec in enumerate(STAGES):
        manifest_path = MANIFEST_DIR / f"{spec['map']}_ch{spec['id']}_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifests[spec["id"]] = manifest
        next_battle = STAGES[index + 1]["battle"] if index + 1 < len(STAGES) else "天下一统"
        (STAGE_DIR / f"{spec['id']}.lua").write_text(make_stage(spec, manifest, sources, next_battle), encoding="utf-8")
    heroes = all_new_heroes()
    update_config(heroes)
    update_save()
    update_gui(heroes, manifests)
    update_previous_test()
    print(f"integrated {len(STAGES)} stages covering Dongzhou chapters 82-108")


if __name__ == "__main__":
    main()
