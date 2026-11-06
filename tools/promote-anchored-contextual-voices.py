#!/usr/bin/env python3
"""Promote a fully evaluated anchored Qwen render set into the web game."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
INDEX_PATH = ROOT / "output" / "voice-production" / "anchored-contextual-clone-index.json"
RENDER_INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-render-index.json"
EDGE_INDEX_PATH = ROOT / "output" / "voice-production" / "edge-coverage-index.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--bitrate", default="56k")
    parser.add_argument("--allow-pending-human-review", action="store_true")
    return parser.parse_args()


def candidate_file(record: dict) -> Path:
    return ROOT / record["candidates"][0]["file"]


def validate_record(record: dict, allow_pending_human_review: bool) -> list[str]:
    reasons: list[str] = []
    candidates = record.get("candidates") or []
    if len(candidates) != 1:
        return ["candidate_count_not_one"]
    candidate = candidates[0]
    analysis = candidate.get("analysis") or {}
    if not candidate_file(record).is_file():
        reasons.append("missing_wav")
    if analysis.get("waveformGate") is not True:
        reasons.append("waveform_gate_not_passed")
    text_validation = candidate.get("textValidation") or {}
    if not text_validation:
        reasons.append("missing_asr_evidence")
    elif not text_validation.get("normalizedHypothesis"):
        reasons.append("empty_asr_hypothesis")
    if (text_validation.get("criticalTerms") or {}).get("missingTerms"):
        reasons.append("critical_term_mismatch")
    if not candidate.get("speakerEmbedding") or not candidate.get("wavlmSpeakerEmbedding"):
        reasons.append("missing_identity_evidence")
    if not candidate.get("emotionEvidence"):
        reasons.append("missing_emotion_evidence")
    demographics = candidate.get("demographicEvidence") or {}
    probabilities = demographics.get("classProbabilities") or {}
    expected = record.get("expectedGender")
    opposite = "female" if expected == "male" else "male"
    if probabilities.get(opposite, 0) >= 0.85:
        reasons.append("high_confidence_gender_mismatch")
    cadence = analysis.get("broadcastCadence") or {}
    if cadence.get("hardReject") is True:
        reasons.append("broadcast_cadence_hard_reject")
    if not allow_pending_human_review:
        gates = record.get("gates") or {}
        if gates.get("humanReview") not in {"pass", "approved"}:
            reasons.append("human_review_pending")
    return reasons


def encode(task: tuple[dict, dict, str]) -> tuple[str, dict]:
    plan_entry, record, bitrate = task
    source = candidate_file(record)
    target = ROOT / "web-game" / plan_entry["file"]
    replacement = target.with_suffix(".new.ogg")
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-af", "loudnorm=I=-18:LRA=7:TP=-1.5", "-ar", "48000", "-ac", "1",
        "-c:a", "libopus", "-application", "audio", "-b:a", bitrate,
        "-vbr", "constrained", "-compression_level", "10", str(replacement),
    ], check=True)
    replacement.replace(target)
    return plan_entry["id"], {
        "backend": "qwen3-tts-anchored-contextual-clone",
        "model": "Qwen3-TTS-12Hz-1.7B-Base",
        "voice": plan_entry["voiceCardId"],
        "method": record["method"],
        "genderVerification": "independent-research-model-soft-evidence-plus-acoustic-audit",
        "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "humanReview": (record.get("gates") or {}).get("humanReview", "pending_blind_review"),
    }


def main() -> None:
    args = parse_args()
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    records = {record["entryId"]: record for record in index.get("entries", [])}
    plan_ids = {entry["id"] for entry in plan["entries"]}
    if set(records) != plan_ids:
        missing = sorted(plan_ids - set(records))
        extra = sorted(set(records) - plan_ids)
        raise RuntimeError(f"Render index is not complete: missing={len(missing)} extra={len(extra)}")
    rejected = {
        entry_id: validate_record(record, args.allow_pending_human_review)
        for entry_id, record in records.items()
    }
    rejected = {entry_id: reasons for entry_id, reasons in rejected.items() if reasons}
    if rejected:
        report = ROOT / "output" / "voice-production" / "anchored-promotion-rejections.json"
        report.write_text(json.dumps(rejected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError(f"Promotion blocked for {len(rejected)} entries; see {report}")
    tasks = [(entry, records[entry["id"]], args.bitrate) for entry in plan["entries"]]
    render_index: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        for index_number, (entry_id, render) in enumerate(executor.map(encode, tasks), start=1):
            render_index[entry_id] = render
            if index_number == 1 or index_number % 100 == 0 or index_number == len(tasks):
                print(f"[encode {index_number}/{len(tasks)}]", flush=True)
    RENDER_INDEX_PATH.write_text(json.dumps(render_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    edge_index = json.loads(EDGE_INDEX_PATH.read_text(encoding="utf-8")) if EDGE_INDEX_PATH.exists() else {}
    for entry_id in render_index:
        edge_index.pop(entry_id, None)
    EDGE_INDEX_PATH.write_text(json.dumps(edge_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    module_path = ROOT / "tools" / "generate-dialogue-voice-production.py"
    spec = importlib.util.spec_from_file_location("dialogue_voice_production", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load manifest writer: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.write_manifest()


if __name__ == "__main__":
    main()
