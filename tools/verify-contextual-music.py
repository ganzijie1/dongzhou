#!/usr/bin/env python3
"""Verify complete contextual-music coverage and audio integrity."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import soundfile as sf

from runtime_speech import extract_runtime_speech


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PATH = ROOT / "web-game" / "scenario" / "campaign.json"
PLAN_PATH = ROOT / "web-game" / "audio" / "context-music-plan.json"
MANIFEST_PATH = ROOT / "web-game" / "audio" / "context-music-manifest.json"
STAGE_DIR = ROOT / "web-game" / "scenario" / "stage"
SECTIONS = ("intro", "victory", "defeat")


def as_entries(value) -> list[dict]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [item for item in value.values() if isinstance(item, dict)]
    return []


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    expected_battles = len(campaign["stages"])
    expected_sections = sum(
        bool(as_entries(stage.get("story", {}).get(section)))
        for stage in campaign["stages"] for section in SECTIONS
    )
    all_story_speakers = sorted({
        str(entry.get("speaker") or "").strip()
        for stage in campaign["stages"]
        for section in (*SECTIONS, "events")
        for entry in as_entries((stage.get("story") or {}).get(section))
        if str(entry.get("speaker") or "").strip()
    })
    expected_story_events = sum(len(as_entries(stage.get("story", {}).get("events"))) for stage in campaign["stages"])
    expected_runtime_events = sum(len(extract_runtime_speech(stage, STAGE_DIR, all_story_speakers)) for stage in campaign["stages"])
    expected_events = expected_story_events + expected_runtime_events
    expected_total = expected_battles + expected_sections + expected_events
    cues = manifest.get("cues", [])
    if len(cues) != expected_total:
        fail(f"Music cue count mismatch: {len(cues)} != {expected_total}")
    if len(plan.get("cues", [])) != expected_total:
        fail("Music plan does not match campaign source")

    cue_ids = [cue["id"] for cue in cues]
    if len(cue_ids) != len(set(cue_ids)):
        fail("Duplicate music cue IDs")
    files = [cue["file"] for cue in cues]
    if len(files) != len(set(files)):
        fail("Duplicate music file paths")

    kinds = Counter(cue["kind"] for cue in cues)
    if kinds["battle"] != expected_battles or kinds["event"] != expected_events:
        fail(f"Music kind coverage mismatch: {dict(kinds)}")
    event_cues = [cue for cue in cues if cue.get("kind") == "event"]
    if any(not str(cue.get("triggerText") or "").strip() for cue in event_cues):
        fail("Runtime event music cue missing trigger text")

    stage_battles = Counter(cue["stageId"] for cue in cues if cue["kind"] == "battle")
    bad_stages = [stage["id"] for stage in campaign["stages"] if stage_battles[str(stage["id"])] != 1]
    if bad_stages:
        fail(f"Stages without exactly one battle loop: {bad_stages}")

    invalid = []
    loop_seams = []
    total_bytes = 0
    for cue in cues:
        path = ROOT / "web-game" / cue["file"]
        if not path.exists() or path.stat().st_size < 1024:
            invalid.append(f"missing_or_tiny:{cue['id']}")
            continue
        info = sf.info(path)
        duration = info.frames / info.samplerate
        if info.channels != 2 or info.samplerate != 24_000:
            invalid.append(f"format:{cue['id']}")
        if abs(duration - float(cue["durationTarget"])) > 0.08:
            invalid.append(f"duration:{cue['id']}")
        if file_hash(path) != cue.get("sha256"):
            invalid.append(f"hash:{cue['id']}")
        audio, _ = sf.read(path, dtype="float32", always_2d=True)
        rms = float(np.sqrt(np.mean(np.square(audio), dtype=np.float64)))
        peak = float(np.max(np.abs(audio)))
        if not math.isfinite(rms) or rms < 0.006 or peak < 0.04 or peak > 1.0:
            invalid.append(f"signal:{cue['id']}:{rms:.4f}:{peak:.4f}")
        if cue.get("loop"):
            window = min(len(audio) // 8, int(info.samplerate * 0.25))
            seam = float(np.sqrt(np.mean(np.square(audio[:window] - audio[-window:]), dtype=np.float64)))
            loop_seams.append(seam)
            if seam > 0.16:
                invalid.append(f"loop_seam:{cue['id']}:{seam:.4f}")
        total_bytes += path.stat().st_size

    if invalid:
        fail("Invalid contextual music assets: " + ", ".join(invalid[:20]))
    if manifest.get("summary", {}).get("totalBytes") != total_bytes:
        fail("Manifest total byte count is stale")

    result = {
        "result": "PASS",
        "stages": expected_battles,
        "storySections": expected_sections,
        "storyEvents": expected_story_events,
        "luaRuntimeEvents": expected_runtime_events,
        "cues": expected_total,
        "byKind": dict(sorted(kinds.items())),
        "audioBytes": total_bytes,
        "maxLoopSeamRms": round(max(loop_seams, default=0.0), 6),
        "historicalClaimBounded": "no cue is represented as a reconstructed historical composition" in manifest.get("policy", {}).get("historicalClaim", ""),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
