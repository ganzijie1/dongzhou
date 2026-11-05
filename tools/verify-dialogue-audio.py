#!/usr/bin/env python3
"""Validate generated dialogue assets against the exported campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from runtime_speech import extract_runtime_speech


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "web-game" / "audio" / "dialogue-manifest.json"
CAMPAIGN_PATH = ROOT / "web-game" / "scenario" / "campaign.json"
EXTRA_STORY_PATHS = (ROOT / "web-game" / "scenario" / "map-elites-chuisha.json",)
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
STAGE_DIR = ROOT / "web-game" / "scenario" / "stage"
EDGE_VOICE_GENDERS = {
    "zh-CN-XiaoxiaoNeural": "female",
    "zh-CN-XiaoyiNeural": "female",
    "zh-CN-YunyangNeural": "male",
    "zh-CN-YunjianNeural": "male",
    "zh-CN-YunxiNeural": "male",
    "zh-CN-YunxiaNeural": "male",
}
EXCLUDED_SPEAKERS = {"", "旁白", "原著", "史官", "军令", "下回预告", "下一回预告", "下关提示"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-stages", default="", help="Require complete audio coverage for comma-separated stage IDs or 'all'.")
    return parser.parse_args()


def split_story_text(text: str, max_length: int = 110) -> list[str]:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    if not clean or len(clean) <= max_length:
        return [clean] if clean else []
    sentences = re.findall(r"[^。！？；]+[。！？；]?", clean) or [clean]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) > max_length:
            chunks.append(current)
            current = ""
        if len(sentence) > max_length:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(sentence[index:index + max_length] for index in range(0, len(sentence), max_length))
        else:
            current += sentence
    if current:
        chunks.append(current)
    return chunks


def duration_seconds(path: Path) -> float:
    try:
        import soundfile as sf
    except ImportError:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            check=True, capture_output=True, text=True,
        )
        return float(result.stdout.strip())
    info = sf.info(path)
    return info.frames / info.samplerate


def campaign_lines() -> set[tuple[str, str]]:
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    stages = list(campaign["stages"])
    stages.extend(json.loads(path.read_text(encoding="utf-8")) for path in EXTRA_STORY_PATHS if path.exists())
    lines: set[tuple[str, str]] = set()
    story_speakers: set[str] = set()
    for stage in stages:
        for section in ("intro", "events", "victory", "defeat"):
            raw = stage.get("story", {}).get(section, [])
            entries = raw if isinstance(raw, list) else list(raw.values())
            for entry in entries:
                speaker = str(entry.get("speaker") or "旁白")
                text = str(entry.get("text") or "")
                if speaker not in EXCLUDED_SPEAKERS:
                    story_speakers.add(speaker)
                lines.add((speaker, text))
                lines.update((speaker, chunk) for chunk in split_story_text(text))
    for stage in campaign["stages"]:
        for runtime_call in extract_runtime_speech(stage, STAGE_DIR, sorted(story_speakers)):
            speaker = runtime_call["speaker"]
            text = runtime_call["text"]
            lines.add((speaker, text))
            lines.update((speaker, chunk) for chunk in split_story_text(text))
    return lines


def main() -> None:
    args = parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    source_lines = campaign_lines()
    ids: set[str] = set()
    line_keys: set[tuple[str, str]] = set()
    total_bytes = 0
    total_duration = 0.0
    backend_counts: dict[str, int] = {}

    if manifest.get("schemaVersion") not in {1, 2, 3, 4, 5}:
        raise RuntimeError("Unsupported dialogue manifest schema")
    if not entries:
        raise RuntimeError("Dialogue manifest has no entries")

    for entry in entries:
        entry_id = str(entry.get("id", ""))
        line_key = (str(entry.get("speaker", "")), str(entry.get("text", "")))
        if not entry_id or entry_id in ids:
            raise RuntimeError(f"Duplicate or empty dialogue id: {entry_id}")
        if line_key in line_keys:
            raise RuntimeError(f"Duplicate speaker/text pair: {line_key}")
        if line_key not in source_lines:
            raise RuntimeError(f"Dialogue does not match campaign text: {line_key}")
        if manifest.get("narrationExcluded") and line_key[0] in EXCLUDED_SPEAKERS:
            raise RuntimeError(f"Narration or system text must not be voiced: {line_key}")
        if manifest.get("schemaVersion") in {2, 3, 4, 5} and (not entry.get("ageBand") or not entry.get("ageBasis")):
            raise RuntimeError(f"Missing age provenance for {entry_id}")
        if manifest.get("schemaVersion") in {4, 5}:
            if not entry.get("contextId") or not entry.get("firstOccurrence") or not entry.get("occurrences"):
                raise RuntimeError(f"Missing contextual selectors for {entry_id}")
            if not entry.get("styleAnchor"):
                raise RuntimeError(f"Missing style anchor for {entry_id}")
        if manifest.get("schemaVersion") in {2, 3, 4, 5}:
            backend = str(entry.get("backend", ""))
            if backend not in {"qwen3-tts-voice-design-clone", "qwen3-tts-contextual-voice-design", "edge-tts"}:
                raise RuntimeError(f"Missing or unsupported render backend for {entry_id}: {backend}")
            backend_counts[backend] = backend_counts.get(backend, 0) + 1
            card_id = str(entry.get("voiceCardId", ""))
            card = cards_by_id.get(card_id)
            if not card or card.get("speaker") != line_key[0]:
                raise RuntimeError(f"Missing or mismatched voice card for {entry_id}: {card_id}")
            if entry.get("gender") != card.get("gender"):
                raise RuntimeError(f"Manifest gender differs from voice card for {entry_id}")
            if backend == "edge-tts":
                voice = str(entry.get("voice", ""))
                rendered_gender = EDGE_VOICE_GENDERS.get(voice)
                if rendered_gender != card.get("gender"):
                    raise RuntimeError(
                        f"Voice gender mismatch for {entry_id}: {card.get('gender')} character uses {voice}"
                    )
                if entry.get("genderVerification") != "provider-voice-contract":
                    raise RuntimeError(f"Missing provider gender verification for {entry_id}")
                if manifest.get("schemaVersion") >= 5:
                    contextual = entry.get("contextualProsody") or {}
                    required = {"emotion", "speechAct", "pace", "intensity", "pauseStrength", "dominance", "pausePlan"}
                    if not required.issubset(contextual):
                        raise RuntimeError(f"Missing contextual Edge prosody for {entry_id}")
            elif entry.get("genderVerification") != "human-reviewed":
                raise RuntimeError(
                    f"Unreviewed custom voice for {entry_id}; Qwen voices require a human acoustic gender review"
                )
            elif backend == "qwen3-tts-contextual-voice-design":
                review = entry.get("voiceReview") or {}
                required_gates = {"text": "pass", "identity": "pass", "prosody": "pass", "gender": "pass", "humanApproval": "approved"}
                failed = {key: value for key, value in required_gates.items() if review.get(key) != value}
                if failed:
                    raise RuntimeError(f"Contextual voice lacks promotion gates for {entry_id}: {failed}")

        relative = Path(str(entry.get("file", "")))
        if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() != ".ogg":
            raise RuntimeError(f"Unsafe or unsupported dialogue path: {relative}")
        audio_path = ROOT / "web-game" / relative
        if not audio_path.is_file():
            raise RuntimeError(f"Missing dialogue audio: {audio_path}")
        digest = hashlib.sha256(audio_path.read_bytes()).hexdigest()
        if digest != entry.get("sha256"):
            raise RuntimeError(f"Hash mismatch: {audio_path}")
        measured = duration_seconds(audio_path)
        declared = float(entry.get("duration", 0))
        if measured < 0.35 or measured > 30:
            raise RuntimeError(f"Implausible duration {measured:.3f}s: {audio_path}")
        if abs(measured - declared) > 0.05:
            raise RuntimeError(f"Duration mismatch for {audio_path}: {declared:.3f}s vs {measured:.3f}s")

        ids.add(entry_id)
        line_keys.add(line_key)
        total_bytes += audio_path.stat().st_size
        total_duration += measured

    if args.require_stages:
        plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
        wanted = args.require_stages.strip().lower()
        required_ids = {entry["id"] for entry in plan["entries"]} if wanted == "all" else {
            occurrence["entryId"]
            for occurrence in plan["occurrences"]
            if occurrence["stageId"] in {item.strip() for item in args.require_stages.split(",") if item.strip()}
        }
        missing = required_ids - ids
        if missing:
            raise RuntimeError(f"Missing {len(missing)} required character lines; first IDs: {sorted(missing)[:10]}")

    print(json.dumps({
        "result": "PASS",
        "entries": len(entries),
        "speakers": len({entry["speaker"] for entry in entries}),
        "duration_seconds": round(total_duration, 3),
        "bytes": total_bytes,
        "model": manifest.get("model", ""),
        "backend_counts": backend_counts,
        "narration_excluded": bool(manifest.get("narrationExcluded", False)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
