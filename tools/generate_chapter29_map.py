"""Build chapter 29's Luoyi relief map from the local GPT Image 2 source."""

from __future__ import annotations

from PIL import Image, ImageEnhance

from tools.generate_chapter21_maps import ROOT, SIZE, cover


def main() -> None:
    source = ROOT / "output/imagegen/chapter19-luoyi-gpt2.png"
    image = cover(Image.open(source).convert("RGB"))
    scaled = image.resize(
        (round(SIZE[0] * 1.025), round(SIZE[1] * 1.025)),
        Image.Resampling.LANCZOS,
    )
    left = (scaled.width - SIZE[0]) // 2
    top = max(0, (scaled.height - SIZE[1]) // 2 - 10)
    image = scaled.crop((left, top, left + SIZE[0], top + SIZE[1]))
    image = ImageEnhance.Color(image).enhance(1.03)
    image = ImageEnhance.Contrast(image).enhance(1.09)
    image = ImageEnhance.Brightness(image).enhance(1.01)

    destination = ROOT / "assets/lzc/map/m049.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG", compress_level=3)
    assert Image.open(destination).size == SIZE
    print(destination, destination.stat().st_size)


if __name__ == "__main__":
    main()
