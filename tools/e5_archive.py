"""Read the LS12/E5 resource archives used by Cao Cao engine mods."""

from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path


class BitReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.bit_position = 0

    def read(self, count: int) -> int:
        if self.bit_position + count > len(self.data) * 8:
            raise EOFError("truncated LS12 stream")
        value = 0
        for _ in range(count):
            byte = self.data[self.bit_position // 8]
            value = (value << 1) | ((byte >> (7 - self.bit_position % 8)) & 1)
            self.bit_position += 1
        return value

    def read_code(self) -> int:
        prefix = 0
        width = 0
        while True:
            bit = self.read(1)
            prefix = (prefix << 1) | bit
            width += 1
            if bit == 0:
                return prefix + self.read(width)


def decode_chunk(data: bytes, dictionary: bytes, expected_size: int) -> bytes:
    reader = BitReader(data)
    output = bytearray()
    while len(output) < expected_size:
        code = reader.read_code()
        if code < 0x100:
            output.append(dictionary[code])
            continue
        distance = code - 0x100
        length = reader.read_code() + 3
        if distance <= 0 or distance > len(output):
            raise ValueError(f"invalid LS12 back-reference {distance} at {len(output)}")
        if len(output) + length > expected_size:
            raise ValueError("LS12 back-reference exceeds expected entry size")
        for _ in range(length):
            output.append(output[-distance])
    return bytes(output)


@dataclass(frozen=True)
class Entry:
    unpacked_size: int
    packed_size: int
    offset: int


class E5Archive:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        if len(self.data) < 284 or self.data[:4] != b"Ls12":
            raise ValueError(f"not an LS12/E5 archive: {path}")
        self.dictionary = self.data[16:272]
        first_data_offset = struct.unpack_from(">I", self.data, 280)[0]
        entry_count = (first_data_offset - 272) // 12
        self.entries = []
        for index in range(entry_count):
            packed_size, unpacked_size, offset = struct.unpack_from(
                ">III", self.data, 272 + index * 12
            )
            self.entries.append(Entry(unpacked_size, packed_size, offset))
        if not self.entries or any(
            entry.offset + entry.packed_size > len(self.data) for entry in self.entries
        ):
            raise ValueError(f"invalid E5 entry table: {path}")

    def read(self, index: int) -> bytes:
        entry = self.entries[index]
        packed = self.data[entry.offset:entry.offset + entry.packed_size]
        if entry.packed_size == entry.unpacked_size:
            return packed
        return decode_chunk(packed, self.dictionary, entry.unpacked_size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--entry", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive = E5Archive(args.archive)
    compressed = sum(e.packed_size != e.unpacked_size for e in archive.entries)
    print(f"{len(archive.entries)} entries ({compressed} compressed)")
    if args.entry is not None:
        payload = archive.read(args.entry)
        print(f"entry {args.entry}: {len(payload):,} bytes; prefix={payload[:24].hex(' ')}")
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(payload)


if __name__ == "__main__":
    main()
