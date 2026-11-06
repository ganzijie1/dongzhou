#!/usr/bin/env python3
"""Build a compact H5 audio set without mutating the production masters."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web-game"
VOICE_MANIFEST = WEB / "audio" / "dialogue-manifest.json"
MUSIC_MANIFEST = WEB / "audio" / "context-music-manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", required=True, type=Path)
    parser.add_argument("--packs-output", required=True, type=Path)
    parser.add_argument("--music-budget-mib", type=float, default=24.0)
    parser.add_argument("--base-stages", type=int, default=8)
    parser.add_argument("--pack-target-mib", type=float, default=16.0)
    parser.add_argument("--workers", type=int, default=max(2, min(8, os.cpu_count() or 2)))
    return parser.parse_args()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def safe_source(relative: str, prefix: str) -> Path:
    normalized = relative.replace("\\", "/")
    if not normalized.startswith(prefix) or ".." in normalized.split("/") or ":" in normalized:
        raise RuntimeError(f"Unsafe audio path: {relative}")
    source = WEB / Path(normalized)
    if not source.is_file():
        raise RuntimeError(f"Missing audio source: {relative}")
    return source


def critical_voice(entry: dict) -> bool:
    delivery = entry.get("delivery") or {}
    contextual = entry.get("contextualProsody") or {}
    intensity = max(float(delivery.get("intensity") or 0), float(contextual.get("intensity") or 0))
    emotion = str(contextual.get("emotion") or delivery.get("emotion") or "").lower()
    anchor = str(entry.get("styleAnchor") or "").lower()
    expressive = ("whisper", "grief", "rage", "revenge", "panic", "cry", "death", "oath", "lament")
    return intensity >= 0.78 or any(token in emotion or token in anchor for token in expressive)


def encode_voice(task: tuple[dict, Path]) -> dict:
    entry, staging = task
    relative = str(entry["file"]).replace("\\", "/")
    source = safe_source(relative, "audio/dialogue/")
    target = staging / Path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    bitrate = "48k" if critical_voice(entry) else "40k"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-map_metadata", "-1", "-ar", "48000", "-ac", "1", "-c:a", "libopus",
        "-application", "audio", "-b:a", bitrate, "-vbr", "constrained",
        "-compression_level", "10", str(target),
    ]
    subprocess.run(command, check=True)
    updated = dict(entry)
    updated["sha256"] = digest(target)
    updated["bytes"] = target.stat().st_size
    updated["deliveryEncoding"] = {
        "codec": "opus", "channels": 1, "sampleRate": 48000,
        "targetBitrateKbps": int(bitrate[:-1]), "vbr": "constrained",
        "source": "production-opus-master",
    }
    return updated


def music_distance(cue: dict, candidate: dict) -> tuple:
    return (
        0 if bool(cue.get("loop")) == bool(candidate.get("loop")) else 100,
        0 if cue.get("kind") == candidate.get("kind") else 20,
        0 if cue.get("era") == candidate.get("era") else 8,
        0 if cue.get("mood") == candidate.get("mood") else 4,
        0 if cue.get("scene") == candidate.get("scene") else 2,
        abs(float(cue.get("tempo") or 0) - float(candidate.get("tempo") or 0)) / 40,
        str(candidate.get("id") or ""),
    )


def select_base_music(cues: list[dict], budget_bytes: int, base_stages: int) -> set[str]:
    by_file = {str(cue["file"]): cue for cue in cues}
    selected: set[str] = set()

    for cue in cues:
        if int(cue.get("stageIndex") or 0) <= base_stages:
            selected.add(str(cue["file"]))

    representatives: dict[tuple, dict] = {}
    for cue in cues:
        key = (bool(cue.get("loop")), cue.get("kind"), cue.get("era"), cue.get("mood"))
        current = representatives.get(key)
        if current is None or int(cue.get("entryCount") or 0) > int(current.get("entryCount") or 0):
            representatives[key] = cue
    selected.update(str(cue["file"]) for cue in representatives.values())

    def total_size(files: set[str]) -> int:
        return sum(safe_source(path, "audio/context-music/").stat().st_size for path in files)

    if total_size(selected) > budget_bytes:
        mandatory = {str(cue["file"]) for cue in cues if int(cue.get("stageIndex") or 0) <= base_stages}
        selected = set(mandatory)
        for cue in sorted(representatives.values(), key=lambda item: (-int(item.get("entryCount") or 0), str(item.get("id") or ""))):
            path = str(cue["file"])
            size = safe_source(path, "audio/context-music/").stat().st_size
            if total_size(selected) + size <= budget_bytes:
                selected.add(path)

    prioritized = sorted(cues, key=lambda cue: (int(cue.get("stageIndex") or 9999), 0 if cue.get("kind") == "battle" else 1, str(cue.get("id") or "")))
    used = total_size(selected)
    for cue in prioritized:
        path = str(cue["file"])
        if path in selected:
            continue
        size = safe_source(path, "audio/context-music/").stat().st_size
        if used + size <= budget_bytes:
            selected.add(path)
            used += size

    if not selected:
        raise RuntimeError("Compact music selection is empty")
    return selected


def build_music(staging: Path, packs_output: Path, budget_mib: float, base_stages: int, pack_target_mib: float) -> dict:
    manifest = json.loads(MUSIC_MANIFEST.read_text(encoding="utf-8"))
    cues = list(manifest.get("cues") or [])
    budget_bytes = int(budget_mib * 1024 * 1024)
    selected = select_base_music(cues, budget_bytes, base_stages)
    selected_cues = [cue for cue in cues if str(cue["file"]) in selected]
    selected_by_file = {str(cue["file"]): cue for cue in selected_cues}

    for relative in sorted(selected):
        source = safe_source(relative, "audio/context-music/")
        target = staging / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    stage_missing: dict[str, list[dict]] = defaultdict(list)
    compact_cues = []
    for cue in cues:
        updated = dict(cue)
        relative = str(cue["file"])
        if relative in selected:
            fallback = cue
            updated["availableInBase"] = True
            updated["packId"] = ""
        else:
            compatible = [candidate for candidate in selected_cues if bool(candidate.get("loop")) == bool(cue.get("loop"))]
            if not compatible:
                compatible = selected_cues
            fallback = min(compatible, key=lambda candidate: music_distance(cue, candidate))
            updated["availableInBase"] = False
            stage_missing[str(cue.get("stageId") or "")].append(cue)
        updated["fallbackFile"] = str(fallback["file"])
        updated["fallbackSha256"] = str(fallback.get("sha256") or digest(safe_source(str(fallback["file"]), "audio/context-music/")))
        compact_cues.append(updated)

    packs_output.mkdir(parents=True, exist_ok=False)
    target_bytes = int(pack_target_mib * 1024 * 1024)
    stage_order = {
        str(cue.get("stageId") or ""): int(cue.get("stageIndex") or 9999)
        for cue in cues
    }
    stage_groups = []
    for stage_id, missing in sorted(stage_missing.items(), key=lambda item: (stage_order.get(item[0], 9999), item[0])):
        size = sum(safe_source(str(cue["file"]), "audio/context-music/").stat().st_size for cue in missing)
        stage_groups.append((stage_id, missing, size))

    groups: list[list[tuple[str, list[dict], int]]] = []
    current: list[tuple[str, list[dict], int]] = []
    current_size = 0
    for group in stage_groups:
        if current and current_size + group[2] > target_bytes:
            groups.append(current)
            current = []
            current_size = 0
        current.append(group)
        current_size += group[2]
    if current:
        groups.append(current)

    pack_records = []
    cue_pack: dict[str, str] = {}
    for index, group in enumerate(groups, 1):
        stage_ids = [item[0] for item in group]
        first_index = stage_order.get(stage_ids[0], index)
        last_index = stage_order.get(stage_ids[-1], first_index)
        pack_id = f"music-{first_index:03d}-{last_index:03d}"
        archive_path = packs_output / f"{pack_id}.zip"
        files = []
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for _, missing, _ in group:
                for cue in missing:
                    relative = str(cue["file"])
                    source = safe_source(relative, "audio/context-music/")
                    archive.write(source, relative)
                    files.append({"cueId": cue["id"], "file": relative, "sha256": cue["sha256"], "bytes": source.stat().st_size})
                    cue_pack[str(cue["id"])] = pack_id
            pack_manifest = {"schemaVersion": 1, "id": pack_id, "stages": stage_ids, "files": files}
            archive.writestr("pack-manifest.json", json.dumps(pack_manifest, ensure_ascii=False, indent=2).encode("utf-8"))
        pack_records.append({
            "id": pack_id, "archive": archive_path.name, "stageIds": stage_ids,
            "bytes": archive_path.stat().st_size, "sha256": digest(archive_path), "files": len(files),
            "deployment": "Extract at the H5 root so audio/context-music paths become available.",
        })

    for cue in compact_cues:
        if not cue["availableInBase"]:
            cue["packId"] = cue_pack.get(str(cue["id"]), "")

    base_bytes = sum((staging / Path(relative)).stat().st_size for relative in selected)
    compact_manifest = dict(manifest)
    compact_manifest["schemaVersion"] = max(2, int(manifest.get("schemaVersion") or 1))
    compact_manifest["cues"] = compact_cues
    compact_manifest["compactDelivery"] = {
        "mode": "base-with-external-packs", "musicBudgetMiB": budget_mib,
        "baseBytes": base_bytes, "baseFiles": len(selected), "fallbackEnabled": True,
        "packIndex": "audio/music-pack-index.json",
    }
    compact_manifest.setdefault("summary", {})["baseBytes"] = base_bytes
    compact_manifest["summary"]["baseFiles"] = len(selected)

    audio_dir = staging / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "context-music-manifest.json").write_text(json.dumps(compact_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    pack_index = {"schemaVersion": 1, "baseFiles": len(selected), "baseBytes": base_bytes, "packs": pack_records}
    (audio_dir / "music-pack-index.json").write_text(json.dumps(pack_index, ensure_ascii=False, indent=2), encoding="utf-8")
    (packs_output / "music-pack-index.json").write_text(json.dumps(pack_index, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"baseMusicBytes": base_bytes, "baseMusicFiles": len(selected), "musicPacks": len(pack_records)}


def main() -> None:
    args = parse_args()
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required")
    staging = args.staging.resolve()
    staging.mkdir(parents=True, exist_ok=True)
    voice_manifest = json.loads(VOICE_MANIFEST.read_text(encoding="utf-8"))
    entries = list(voice_manifest.get("entries") or [])
    tasks = [(entry, staging) for entry in entries]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        encoded = list(executor.map(encode_voice, tasks))
    encoded_by_id = {entry["id"]: entry for entry in encoded}
    voice_manifest["entries"] = [encoded_by_id[entry["id"]] for entry in entries]
    voice_manifest["compactDelivery"] = {
        "codec": "opus", "standardBitrateKbps": 40, "criticalBitrateKbps": 48,
        "vbr": "constrained", "criticalEntries": sum(critical_voice(entry) for entry in entries),
    }
    audio_dir = staging / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    (audio_dir / "dialogue-manifest.json").write_text(json.dumps(voice_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    music_result = build_music(staging, args.packs_output.resolve(), args.music_budget_mib, args.base_stages, args.pack_target_mib)
    voice_bytes = sum((staging / Path(entry["file"])).stat().st_size for entry in encoded)
    result = {
        "result": "PASS", "voices": len(encoded), "voiceBytes": voice_bytes,
        "criticalVoices": voice_manifest["compactDelivery"]["criticalEntries"], **music_result,
        "packsOutput": str(args.packs_output.resolve()),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
