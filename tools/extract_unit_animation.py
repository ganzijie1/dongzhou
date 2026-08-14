"""Extract Cao Cao unit movement frames from a TexturePacker PVR.CCZ atlas."""

from __future__ import annotations

import argparse
import plistlib
import re
import struct
import zlib
from pathlib import Path

from PIL import Image


PAIR_RE = re.compile(r"\{\{(-?\d+),(-?\d+)\},\{(-?\d+),(-?\d+)\}\}")
SIZE_RE = re.compile(r"\{(-?\d+),(-?\d+)\}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plist", type=Path)
    parser.add_argument("pvr_ccz", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def decode_atlas(path: Path) -> Image.Image:
    data = path.read_bytes()
    if data[:4] != b"CCZ!":
        raise ValueError(f"Not a CCZ archive: {path}")
    pvr = zlib.decompress(data[16:])
    header_size, height, width = struct.unpack_from("<III", pvr)
    bits_per_pixel = struct.unpack_from("<I", pvr, 24)[0]
    bytes_per_pixel = bits_per_pixel // 8
    pixels = pvr[header_size:header_size + width * height * bytes_per_pixel]
    if header_size != 52 or len(pixels) != width * height * bytes_per_pixel:
        raise ValueError(f"Truncated PVR pixel data: {path}")
    if bits_per_pixel == 32:
        image = Image.frombytes("RGBA", (width, height), pixels)
    elif bits_per_pixel == 16:
        masks = struct.unpack_from("<IIII", pvr, 28)
        channels = bytearray(width * height * 4)
        for pixel_index, (value,) in enumerate(struct.iter_unpack("<H", pixels)):
            for channel_index, mask in enumerate(masks):
                shift = (mask & -mask).bit_length() - 1
                maximum = mask >> shift
                channels[pixel_index * 4 + channel_index] = round(
                    ((value & mask) >> shift) * 255 / maximum
                )
        image = Image.frombytes("RGBA", (width, height), bytes(channels))
    else:
        raise ValueError(f"Unsupported PVR pixel depth {bits_per_pixel}: {path}")
    return image


def parse_rect(value: str) -> tuple[int, int, int, int]:
    match = PAIR_RE.fullmatch(value)
    if match is None:
        raise ValueError(f"Invalid TexturePacker rectangle: {value}")
    return tuple(map(int, match.groups()))


def parse_size(value: str) -> tuple[int, int]:
    match = SIZE_RE.fullmatch(value)
    if match is None:
        raise ValueError(f"Invalid TexturePacker size: {value}")
    return tuple(map(int, match.groups()))


def extract_frame(atlas: Image.Image, metadata: dict[str, object]) -> Image.Image:
    x, y, width, height = parse_rect(str(metadata["frame"]))
    source_x, source_y, _, _ = parse_rect(str(metadata["sourceColorRect"]))
    source_size = parse_size(str(metadata["sourceSize"]))
    if metadata.get("rotated", False):
        crop = atlas.crop((x, y, x + height, y + width))
        crop = crop.transpose(Image.Transpose.ROTATE_90)
    else:
        crop = atlas.crop((x, y, x + width, y + height))
    result = Image.new("RGBA", source_size)
    result.alpha_composite(crop, (source_x, source_y))
    return result


def main() -> None:
    args = parse_args()
    atlas = decode_atlas(args.pvr_ccz)
    with args.plist.open("rb") as stream:
        frames = plistlib.load(stream)["frames"]
    args.output.mkdir(parents=True, exist_ok=True)
    selected_frames = {
        "down_0": ("MOV", 1), "down_1": ("MOV", 2),
        "up_0": ("MOV", 3), "up_1": ("MOV", 4),
        "left_0": ("MOV", 5), "left_1": ("MOV", 6),
        "stand_down": ("MOV", 7), "stand_up": ("MOV", 8),
        "stand_left": ("MOV", 9),
        "weak_0": ("MOV", 10), "weak_1": ("MOV", 11),
        "hit_down": ("SPC", 1), "hit_up": ("SPC", 2),
        "hit_left": ("SPC", 3), "hit_failed": ("SPC", 4),
        "hit_recover": ("SPC", 5),
    }
    for direction, first_frame in (("down", 1), ("up", 5), ("left", 9)):
        for index in range(4):
            selected_frames[f"attack_{direction}_{index}"] = ("ATK", first_frame + index)
    unit_name = next(iter(frames)).split("ATK", 1)[0].split("MOV", 1)[0]
    for output_name, (frame_group, frame_number) in selected_frames.items():
        frame_name = f"{unit_name}{frame_group}-{frame_number}.png"
        extract_frame(atlas, frames[frame_name]).save(args.output / f"{output_name}.png")


if __name__ == "__main__":
    main()
