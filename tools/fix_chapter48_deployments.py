from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def update(path: Path, replacements: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        if old not in text:
            raise RuntimeError(f"missing deployment anchor: {old}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


update(ROOT / "game/sce/dongzhou/stage/48a.lua", {
    'game:generate_unit("GongZiJian48", 1, Enum.force.enemy, {35,12})':
        'game:generate_unit("GongZiJian48", 1, Enum.force.enemy, {36,14})',
    'game:generate_unit("GongZiPang48", 1, Enum.force.enemy, {36,14})':
        'game:generate_unit("GongZiPang48", 1, Enum.force.enemy, {35,12})',
})

update(ROOT / "game/sce/dongzhou/stage/48b.lua", {
    '{ position = {44,11}, hero = "XunLinFu47" }': '{ position = {43,10}, hero = "XunLinFu47" }',
    '{ position = {47,11}, hero = "XiQue45" }': '{ position = {48,10}, hero = "XiQue45" }',
    '{ position = {44,19}, hero = "YuPian48" }': '{ position = {43,21}, hero = "YuPian48" }',
    '{ position = {47,19}, hero = "LuanDun45" }': '{ position = {48,21}, hero = "LuanDun45" }',
    '{ position = {49,13}, hero = "XuJia48" }': '{ position = {45,18}, hero = "XuJia48" }',
    '{ position = {41,15}, hero = "ZhaoChuan48" }': '{ position = {39,15}, hero = "ZhaoChuan48" }',
    '{ position = {49,17}, hero = "HanJue48" }': '{ position = {50,15}, hero = "HanJue48" }',
    'game:generate_unit("XiQiShu26", 1, Enum.force.enemy, {12,11})':
        'game:generate_unit("XiQiShu26", 1, Enum.force.enemy, {12,10})',
    'game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {17,11})':
        'game:generate_unit("BaiYiBing26", 1, Enum.force.enemy, {17,10})',
    'game:generate_unit("ShiHui47", 1, Enum.force.enemy, {15,20})':
        'game:generate_unit("ShiHui47", 1, Enum.force.enemy, {17,21})',
})

print("Chapter 48 deployments aligned with manifests.")
