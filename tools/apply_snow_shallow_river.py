from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing: {path} {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main():
    config = ROOT / "game/sce/dongzhou/config.lua"
    replace_once(config,
        '        { id = "Grass", char = "g" },\n        { id = "Forest", char = "F" },',
        '        { id = "Grass", char = "g" },\n        { id = "Snow", char = "s" },\n        { id = "Forest", char = "F" },')
    replace_once(config,
        '        { id = "Water", char = "~" },\n        { id = "Watchtower", char = "c" },',
        '        { id = "Water", char = "~" },\n        { id = "ShallowRiver", char = "v" },\n        { id = "Watchtower", char = "c" },')
    replace_once(config,
        '        {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {2, 1, 2, 1, 1, 1, 2}, {2, 1, 2, 1, 1, 1, 2},',
        '        {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {2, 2, 3, 2, 2, 2, 2}, {2, 1, 2, 1, 1, 1, 2}, {2, 1, 2, 1, 1, 1, 2},')
    replace_once(config,
        '{255, 255, 255, 255, 255, 255, 255}, {255, 255, 255, 255, 255, 255, 255}, {255, 255, 255, 255, 255, 255, 255},\n        {1, 1, 1, 1, 1, 1, 1}',
        '{255, 255, 255, 255, 255, 255, 255}, {255, 255, 255, 255, 255, 255, 255}, {255, 255, 255, 255, 255, 255, 255}, {3, 2, 4, 2, 2, 2, 3},\n        {1, 1, 1, 1, 1, 1, 1}')
    replace_once(config,
        '        {100, 100, 110, 100, 100, 100, 100}, {100, 100, 105, 100, 100, 100, 100}, {100, 110, 85, 110, 110, 110, 100}, {95, 105, 90, 105, 105, 105, 95},',
        '        {100, 100, 110, 100, 100, 100, 100}, {100, 100, 105, 100, 100, 100, 100}, {95, 100, 90, 100, 100, 100, 95}, {100, 110, 85, 110, 110, 110, 100}, {95, 105, 90, 105, 105, 105, 95},')
    replace_once(config,
        '{100, 100, 100, 100, 100, 100, 100}, {110, 110, 105, 110, 110, 110, 110}',
        '{100, 100, 100, 100, 100, 100, 100}, {90, 100, 80, 100, 100, 100, 90}, {110, 110, 105, 110, 110, 110, 110}')
    gui = ROOT / "rl/play_gui.py"
    replace_once(gui,
        'TERRAIN_LABELS.update({"Gate": "城门",',
        'TERRAIN_LABELS.update({"Snow": "雪地", "ShallowRiver": "小河", "Water": "大河", "Gate": "城门",')
    print("Snow and shallow-river terrain semantics integrated.")


if __name__ == "__main__":
    main()
