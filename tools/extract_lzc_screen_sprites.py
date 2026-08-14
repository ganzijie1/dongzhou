"""Extract transparent battle sprites from a captured Li Zicheng game window."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


SPRITES = {
    "warrior": ((1540, 358), [(5, 7), (26, 1), (44, 10), (45, 46), (5, 47)]),
    "guard": ((1588, 407), [(7, 5), (32, 2), (44, 11), (43, 47), (6, 47)]),
    "fighter": ((1540, 455), [(6, 4), (30, 1), (45, 13), (43, 47), (6, 47)]),
    "wolf": ((1014, 358), [(2, 5), (44, 4), (47, 32), (34, 44), (3, 43)]),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = Image.open(args.capture).convert("RGB")
    args.output.mkdir(parents=True, exist_ok=True)

    for name, (center, polygon) in SPRITES.items():
        x, y = center
        crop = source.crop((x - 24, y - 24, x + 24, y + 24))
        rgb = np.asarray(crop)
        red, green, blue = (rgb[:, :, channel].astype(float) for channel in range(3))
        grass = (green > 30) & (green > red * 1.10) & (green > blue * 1.15)
        shape = Image.new("L", (48, 48))
        ImageDraw.Draw(shape).polygon(polygon, fill=255)
        alpha = np.asarray(shape).copy()
        alpha[grass] = 0
        if name == "fighter":
            pants = Image.new("L", (48, 48))
            ImageDraw.Draw(pants).polygon([(15, 29), (35, 28), (37, 43), (17, 44)], fill=255)
            alpha[np.asarray(pants) > 0] = 255
        # Remove tiny disconnected flecks while retaining weapon tips.
        seen = np.zeros((48, 48), dtype=bool)
        components: list[list[tuple[int, int]]] = []
        for py in range(48):
            for px in range(48):
                if not alpha[py, px] or seen[py, px]:
                    continue
                queue = deque([(px, py)])
                seen[py, px] = True
                component = []
                while queue:
                    qx, qy = queue.popleft()
                    component.append((qx, qy))
                    for nx in range(max(0, qx - 1), min(48, qx + 2)):
                        for ny in range(max(0, qy - 1), min(48, qy + 2)):
                            if alpha[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                queue.append((nx, ny))
                components.append(component)
        keep = {point for component in components if len(component) >= 4 for point in component}
        alpha[:, :] = 0
        for px, py in keep:
            alpha[py, px] = 255
        result = crop.convert("RGBA")
        result.putalpha(Image.fromarray(alpha))
        result.save(args.output / f"{name}.png")
        print(f"{name}: {np.count_nonzero(alpha)} opaque pixels")


if __name__ == "__main__":
    main()
