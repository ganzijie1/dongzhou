from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "rl/play_gui.py"


def main():
    text = PATH.read_text(encoding="utf-8")
    anchor = 'if _original_name == "__main__":'
    if anchor not in text:
        raise RuntimeError("play_gui main anchor missing")
    block = '''_chapter50_previous_unit_sprite_role = unit_sprite_role


def unit_sprite_role(detail):
    name = str(detail.get("name")) if detail is not None else ""
    if name == "LingAo50":
        return "lingao"
    return _chapter50_previous_unit_sprite_role(detail)


_chapter50_previous_load_unit_sprites = load_unit_sprites


def load_unit_sprites():
    animations = _chapter50_previous_load_unit_sprites()
    animations["lingao"] = _load_chapter35_beast_sprites("lingao")
    return animations


_chapter50_previous_portrait_for_unit = portrait_for_unit
_chapter50_lingao_portrait_cache = {}


def portrait_for_unit(detail, portraits):
    name = str(detail.get("name")) if detail is not None else ""
    if name != "LingAo50":
        return _chapter50_previous_portrait_for_unit(detail, portraits)
    filename = "chapter50-lingao.png"
    if filename not in _chapter50_lingao_portrait_cache:
        source = Path(__file__).resolve().parent / "assets" / "portraits" / filename
        _chapter50_lingao_portrait_cache[filename] = pygame.image.load(str(source)).convert_alpha()
    return _chapter50_lingao_portrait_cache[filename]


'''
    PATH.write_text(text.replace(anchor, block + anchor, 1), encoding="utf-8")
    print("Ling Ao custom portrait and animation role registered.")


if __name__ == "__main__":
    main()
