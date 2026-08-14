"""Install the reviewed GPT Image 2 Ling Ao portrait and directional sprite set."""

from pathlib import Path

from PIL import Image

from install_chapter35_gpt2_assets import install_sheet


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/imagegen"
PORTRAITS = ROOT / "rl/assets/portraits"


def main():
    portrait = Image.open(SOURCE / "chapter50-lingao-portrait-gpt2.png").convert("RGB")
    side = min(portrait.size)
    left = (portrait.width - side) // 2
    top = (portrait.height - side) // 2
    portrait.crop((left, top, left + side, top + side)).resize(
        (256, 256), Image.Resampling.LANCZOS
    ).save(PORTRAITS / "chapter50-lingao.png")

    install_sheet("lingao", "chapter50-lingao-sheet-gpt2-alpha.png")
    print("Installed Ling Ao portrait and 32-frame directional animation set.")


if __name__ == "__main__":
    main()
