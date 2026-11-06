#!/usr/bin/env python3
"""Verify compact H5 audio coverage, hashes, packs, and size budget."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("packs", type=Path)
    parser.add_argument("--max-mib", type=float, default=195.0)
    return parser.parse_args()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    archive = args.archive.resolve()
    packs = args.packs.resolve()
    if archive.stat().st_size > args.max_mib * 1024 * 1024:
        raise RuntimeError(f"Archive exceeds {args.max_mib:.2f} MiB")

    with zipfile.ZipFile(archive) as bundle:
        names = set(bundle.namelist())
        voice = json.loads(bundle.read("audio/dialogue-manifest.json"))
        music = json.loads(bundle.read("audio/context-music-manifest.json"))
        pack_index = json.loads(bundle.read("audio/music-pack-index.json"))
        voice_bytes = 0
        for entry in voice["entries"]:
            path = entry["file"]
            if path not in names:
                raise RuntimeError(f"Missing compact voice: {path}")
            data = bundle.read(path)
            if sha_bytes(data) != entry["sha256"]:
                raise RuntimeError(f"Compact voice hash mismatch: {path}")
            voice_bytes += len(data)

        base_files = set()
        missing_cues = {}
        for cue in music["cues"]:
            original = cue["file"]
            fallback = cue.get("fallbackFile") or original
            if fallback not in names:
                raise RuntimeError(f"Missing fallback music: {cue['id']} -> {fallback}")
            if sha_bytes(bundle.read(fallback)) != cue.get("fallbackSha256"):
                raise RuntimeError(f"Fallback hash mismatch: {cue['id']}")
            base_files.add(fallback)
            if cue.get("availableInBase"):
                if original not in names:
                    raise RuntimeError(f"Base cue marked available but absent: {cue['id']}")
            else:
                if not cue.get("packId"):
                    raise RuntimeError(f"External cue has no pack: {cue['id']}")
                missing_cues[cue["id"]] = cue

    indexed = {record["id"]: record for record in pack_index["packs"]}
    packed_cues = {}
    for pack_id, record in indexed.items():
        path = packs / record["archive"]
        if not path.is_file() or sha_file(path) != record["sha256"]:
            raise RuntimeError(f"Missing or corrupt music pack: {pack_id}")
        with zipfile.ZipFile(path) as package:
            manifest = json.loads(package.read("pack-manifest.json"))
            if manifest["id"] != pack_id:
                raise RuntimeError(f"Pack identity mismatch: {pack_id}")
            for item in manifest["files"]:
                cue_id = item["cueId"]
                if cue_id in packed_cues:
                    raise RuntimeError(f"Cue appears in multiple packs: {cue_id}")
                data = package.read(item["file"])
                if sha_bytes(data) != item["sha256"]:
                    raise RuntimeError(f"Packed cue hash mismatch: {cue_id}")
                packed_cues[cue_id] = pack_id

    if set(packed_cues) != set(missing_cues):
        absent = sorted(set(missing_cues) - set(packed_cues))
        extra = sorted(set(packed_cues) - set(missing_cues))
        raise RuntimeError(f"Pack coverage mismatch; missing={absent[:5]}, extra={extra[:5]}")
    for cue_id, pack_id in packed_cues.items():
        if missing_cues[cue_id]["packId"] != pack_id:
            raise RuntimeError(f"Cue pack reference mismatch: {cue_id}")

    print(json.dumps({
        "result": "PASS",
        "archiveMiB": round(archive.stat().st_size / 1024 / 1024, 2),
        "voices": len(voice["entries"]),
        "voiceMiB": round(voice_bytes / 1024 / 1024, 2),
        "musicCues": len(music["cues"]),
        "baseMusicFiles": len(base_files),
        "externalMusicCues": len(missing_cues),
        "musicPacks": len(indexed),
        "packMiB": round(sum((packs / item["archive"]).stat().st_size for item in indexed.values()) / 1024 / 1024, 2),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
