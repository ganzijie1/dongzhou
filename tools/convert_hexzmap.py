"""Decode Cao Cao MOD Hexzmap terrain grids and validate battle-map images."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from tools.e5_archive import E5Archive


def decode_entry(payload: bytes) -> dict[str, object]:
    if len(payload) < 2 or payload[0] % 3 or payload[1] % 3:
        raise ValueError("invalid Hexzmap dimensions")
    width, height = payload[0] // 3, payload[1] // 3
    count = width * height
    if len(payload) >= count + 2:
        codes = list(payload[2:2 + count])
        padding = len(payload) - count - 2
    elif len(payload) == count:
        # Some maps reuse the first two cells for dimensions instead of
        # prefixing the grid. Those cells lie outside the usable boundary;
        # copy the adjacent terrain value so consumers never see metadata.
        codes = list(payload)
        codes[0:2] = [codes[2], codes[2]]
        padding = 0
    else:
        raise ValueError(f"truncated Hexzmap grid: need {count}, got {len(payload)}")
    return {
        "width": width,
        "height": height,
        "terrain_codes": codes,
        "rows": [codes[y * width:(y + 1) * width] for y in range(height)],
        "padding_bytes": padding,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--map-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive = E5Archive(args.archive)
    stages = []
    for index in range(len(archive.entries)):
        stage = {"index": index, **decode_entry(archive.read(index))}
        if args.map_dir is not None:
            image_path = args.map_dir / f"m{index:03}.jpg"
            if image_path.is_file():
                with Image.open(image_path) as image:
                    actual = list(image.size)
                expected = [int(stage["width"]) * 48, int(stage["height"]) * 48]
                stage["image"] = image_path.name
                stage["image_size"] = actual
                stage["image_matches_grid"] = actual == expected
        stages.append(stage)

    result = {"format": "Ls12/Hexzmap", "source": args.archive.name, "stages": stages}
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    matches = sum(bool(stage.get("image_matches_grid")) for stage in stages)
    images = sum("image" in stage for stage in stages)
    print(f"decoded {len(stages)} terrain grids; validated {matches}/{images} battle-map images")


if __name__ == "__main__":
    main()
