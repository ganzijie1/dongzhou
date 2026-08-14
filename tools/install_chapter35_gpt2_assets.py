"""Install reviewed GPT Image 2 portraits and sprite sheets for chapter 35."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/imagegen"
PORTRAITS = ROOT / "rl/assets/portraits"
ANIMATIONS = ROOT / "rl/assets/unit_anim"


def axis_groups(stats: list[tuple[int, int, int, int, int]], axis: int) -> list[tuple[int, int]]:
    centers = sorted(((box[axis] + box[axis + 2]) / 2, box) for box in stats)
    gaps = sorted(range(len(centers) - 1), key=lambda i: centers[i + 1][0] - centers[i][0], reverse=True)[:3]
    cuts = sorted(i + 1 for i in gaps)
    groups = []
    start = 0
    for stop in cuts + [len(centers)]:
        boxes = [box for _, box in centers[start:stop]]
        groups.append((min(box[axis] for box in boxes), max(box[axis + 2] for box in boxes)))
        start = stop
    assert len(groups) == 4 and all(groups[i][1] < groups[i + 1][0] for i in range(3))
    return groups


def atlas_cells(path: Path) -> list[list[Image.Image]]:
    image = Image.open(path).convert("RGBA")
    alpha = np.asarray(image.getchannel("A")) >= 128
    labels, count = ndimage.label(alpha, np.ones((3, 3), dtype=int))
    sizes = np.bincount(labels.ravel())
    stats = []
    for component in range(1, count + 1):
        if sizes[component] <= 300:
            continue
        ys, xs = np.where(labels == component)
        stats.append((int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1), int(sizes[component])))
    stats = sorted(stats, key=lambda item: item[4], reverse=True)[:16]
    assert len(stats) == 16, f"expected 16 main sprites in {path}, found {len(stats)}"
    x_groups = axis_groups(stats, 0)
    y_groups = axis_groups(stats, 1)
    x_bounds = [0] + [(x_groups[i][1] + x_groups[i + 1][0]) // 2 for i in range(3)] + [image.width]
    y_bounds = [0] + [(y_groups[i][1] + y_groups[i + 1][0]) // 2 for i in range(3)] + [image.height]
    return [[image.crop((x_bounds[x], y_bounds[y], x_bounds[x + 1], y_bounds[y + 1])) for x in range(4)] for y in range(4)]


def normalize(cell: Image.Image) -> Image.Image:
    bbox = cell.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
    assert bbox is not None
    sprite = cell.crop(bbox)
    scale = min(54 / sprite.width, 54 / sprite.height)
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    frame = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    frame.alpha_composite(sprite, ((64 - size[0]) // 2, 59 - size[1]))
    return frame


def install_sheet(role: str, source: str) -> None:
    cells = atlas_cells(SOURCE / source)
    destination = ANIMATIONS / role
    destination.mkdir(parents=True, exist_ok=True)
    for row, direction in enumerate(("down", "left", "right", "up")):
        idle, walk, attack, hit = (normalize(cell) for cell in cells[row])
        idle.save(destination / f"stand_{direction}.png")
        idle.save(destination / f"{direction}_0.png")
        walk.save(destination / f"{direction}_1.png")
        for index, frame in enumerate((idle, walk, attack, attack)):
            frame.save(destination / f"attack_{direction}_{index}.png")
        hit.save(destination / f"hit_{direction}.png")
    normalize(cells[0][3]).save(destination / "hit_failed.png")
    normalize(cells[0][0]).save(destination / "hit_recover.png")
    normalize(cells[1][3]).save(destination / "weak_0.png")
    normalize(cells[2][3]).save(destination / "weak_1.png")


def install_portrait(source: str, destination: str) -> None:
    image = Image.open(SOURCE / source).convert("RGB")
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image.crop((left, top, left + side, top + side)).resize((256, 256), Image.Resampling.LANCZOS).save(PORTRAITS / destination)


def main() -> None:
    install_portrait("chapter35-human-bear-portrait-gpt2.png", "chapter35-human-bear.png")
    install_portrait("chapter35-mo-beast-portrait-gpt2.png", "chapter35-mo-beast.png")
    install_sheet("bear", "chapter35-human-bear-spritesheet-gpt2-v2-alpha.png")
    install_sheet("mo_beast", "chapter35-mo-beast-spritesheet-gpt2-v2-alpha.png")
    print("Installed GPT Image 2 chapter 35 portraits and 32-frame directional sprite sets.")


if __name__ == "__main__":
    main()