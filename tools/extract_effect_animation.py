"""Extract a numbered effect sequence from a TexturePacker PVR.CCZ atlas."""

from __future__ import annotations

import argparse
import plistlib
import re
from pathlib import Path

from extract_unit_animation import decode_atlas, extract_frame


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plist", type=Path)
    parser.add_argument("pvr_ccz", type=Path)
    parser.add_argument("prefix")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with args.plist.open("rb") as stream:
        frames = plistlib.load(stream)["frames"]
    pattern = re.compile(rf"{re.escape(args.prefix)}-(\d+)\.png")
    selected = sorted(
        ((int(match.group(1)), name) for name in frames
         if (match := pattern.fullmatch(name)) is not None),
        key=lambda item: item[0],
    )
    if not selected:
        raise ValueError(f"No frames found for prefix {args.prefix!r}")
    atlas = decode_atlas(args.pvr_ccz)
    args.output.mkdir(parents=True, exist_ok=True)
    for output_index, (_, frame_name) in enumerate(selected):
        extract_frame(atlas, frames[frame_name]).save(args.output / f"{output_index}.png")


if __name__ == "__main__":
    main()
