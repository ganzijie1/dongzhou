#!/usr/bin/env python3
"""Convert contextual Qwen performances to stable character tone colors with OpenVoice V2."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from voice_quality_metrics import analyze_audio


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
SOURCE_INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
OPENVOICE_ROOT = WORKSPACE / ".tools" / "OpenVoice"
OPENVOICE_MODEL = WORKSPACE / ".tools" / "models" / "OpenVoiceV2" / "converter"
OUTPUT_ROOT = ROOT / "output" / "voice-production" / "identity-converted-candidates"
TARGET_EMBEDDING_ROOT = ROOT / "output" / "voice-production" / "openvoice-target-embeddings"
INDEX_PATH = ROOT / "output" / "voice-production" / "identity-converted-index.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-index", default=str(SOURCE_INDEX_PATH), help="Contextual source candidate index.")
    parser.add_argument("--stages", default="01", help="Comma-separated stage IDs, or all.")
    parser.add_argument("--speakers", default="", help="Comma-separated exact speaker names.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--candidates", type=int, default=2, help="Top source candidates per line.")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def safe_path(relative: str) -> Path:
    value = Path(relative)
    path = (ROOT / value).resolve()
    if value.is_absolute() or ".." in value.parts or ROOT.resolve() not in path.parents or not path.is_file():
        raise RuntimeError(f"Unsafe or missing source candidate: {relative}")
    return path


def selected_entries(source_index: dict, plan_by_id: dict[str, dict], stages: set[str] | None, speakers: set[str]) -> list[dict]:
    entries = []
    for entry in source_index.get("entries", []):
        planned = plan_by_id.get(entry.get("entryId")) or {}
        stage_id = str((planned.get("firstOccurrence") or {}).get("stageId", ""))
        if stages is not None and stage_id not in stages:
            continue
        if speakers and entry.get("speaker") not in speakers:
            continue
        if entry.get("candidates"):
            entries.append(entry)
    return entries


def main() -> None:
    args = parse_args()
    if not OPENVOICE_ROOT.is_dir() or not (OPENVOICE_MODEL / "checkpoint.pth").is_file():
        raise RuntimeError("OpenVoice V2 code or converter checkpoint is missing")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    plan_by_id = {entry["id"]: entry for entry in plan["entries"]}
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    source_index_path = Path(args.source_index).resolve()
    if ROOT.resolve() not in source_index_path.parents or not source_index_path.is_file():
        raise RuntimeError(f"Unsafe or missing source index: {source_index_path}")
    source_index = json.loads(source_index_path.read_text(encoding="utf-8"))
    stages = None if args.stages.lower() == "all" else {item.strip() for item in args.stages.split(",") if item.strip()}
    speakers = {item.strip() for item in args.speakers.split(",") if item.strip()}
    selected = selected_entries(source_index, plan_by_id, stages, speakers)[: args.limit or None]

    sys.path.insert(0, str(OPENVOICE_ROOT))
    import soundfile as sf
    import torch
    from openvoice.api import ToneColorConverter

    converter = ToneColorConverter(str(OPENVOICE_MODEL / "config.json"), device=args.device, enable_watermark=False)
    converter.load_ckpt(str(OPENVOICE_MODEL / "checkpoint.pth"))
    target_embeddings: dict[str, object] = {}
    records = []
    try:
        for line_index, source_entry in enumerate(selected, start=1):
            entry = plan_by_id[source_entry["entryId"]]
            card = cards_by_id[entry["voiceCardId"]]
            reference = ROOT / card["referenceFile"]
            if not reference.is_file():
                raise RuntimeError(f"Missing character identity reference: {card['speaker']} {reference}")
            target_cache = TARGET_EMBEDDING_ROOT / f"{card['id']}.pt"
            if card["id"] not in target_embeddings:
                if target_cache.is_file():
                    target_embeddings[card["id"]] = torch.load(target_cache, map_location=args.device).to(args.device)
                else:
                    target_embedding = converter.extract_se([str(reference)])
                    target_cache.parent.mkdir(parents=True, exist_ok=True)
                    torch.save(target_embedding.detach().cpu(), target_cache)
                    target_embeddings[card["id"]] = target_embedding
            record = {
                "entryId": entry["id"],
                "speaker": entry["speaker"],
                "text": entry["text"],
                "voiceCardId": card["id"],
                "expectedGender": card["gender"],
                "expectedAgeBand": card["ageBand"],
                "context": entry["context"],
                "delivery": entry["delivery"],
                "identityReference": str(reference.relative_to(ROOT)).replace("\\", "/"),
                "candidates": [],
                "gates": {
                    "waveform": "pending_generation",
                    "broadcastCadence": "pending_generation",
                    "text": "pending_independent_asr",
                    "identity": "pending_dual_model_retrieval",
                    "expression": "pending_emotion_and_scene_review",
                    "demographics": "pending_soft_evidence",
                    "humanReview": "pending_full_scene_blind_review",
                },
                "promotionEligible": False,
            }
            ranked_sources = sorted(source_entry["candidates"], key=lambda item: item.get("automaticRankScore", 0), reverse=True)
            for source in ranked_sources[: max(1, args.candidates)]:
                source_path = safe_path(source["file"])
                output_dir = OUTPUT_ROOT / entry["id"]
                output_dir.mkdir(parents=True, exist_ok=True)
                output = output_dir / f"candidate-{source['candidate']}.wav"
                if args.force or not output.is_file():
                    source_embedding = converter.extract_se([str(source_path)])
                    converter.convert(
                        audio_src_path=str(source_path),
                        src_se=source_embedding,
                        tgt_se=target_embeddings[card["id"]],
                        output_path=str(output),
                        tau=0.3,
                        message="dongzhou-contextual-voice",
                    )
                waveform, sample_rate = sf.read(output, dtype="float32")
                analysis = analyze_audio(waveform, sample_rate, entry["text"], entry["delivery"], card)
                base_score = (
                    0.35 * analysis["qualityScore"]
                    + 0.25 * analysis["speechTiming"]["paceScore"]
                    + 0.20 * analysis["pauseStructure"]["pauseScore"]
                    + 0.20 * analysis["energy"]["energyScore"]
                )
                cadence = analysis["broadcastCadence"]
                record["candidates"].append({
                    "candidate": int(source["candidate"]),
                    "sourceFile": source["file"],
                    "file": str(output.relative_to(ROOT)).replace("\\", "/"),
                    "analysis": analysis,
                    "automaticRankScore": round(base_score * (0.0 if cadence["hardReject"] else 1.0 - 0.25 * cadence["riskScore"]), 4),
                })
            record["candidates"].sort(key=lambda item: item["automaticRankScore"], reverse=True)
            if record["candidates"]:
                best = record["candidates"][0]["analysis"]
                record["gates"]["waveform"] = "pass" if best["waveformGate"] else "fail"
                record["gates"]["broadcastCadence"] = "fail" if best["broadcastCadence"]["hardReject"] else "pass"
            records.append(record)
            INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
            INDEX_PATH.write_text(json.dumps({
                "schemaVersion": 1,
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "backend": f"{source_index.get('backend', 'contextual-source')}+openvoice-v2-tone-color-conversion",
                "sourceBackend": source_index.get("backend", "unknown"),
                "policy": {
                    "isolation": "Review candidates only; conversion never overwrites shipped game audio.",
                    "identityConversion": "OpenVoice V2 transfers target tone color while retaining the contextual source performance.",
                    "promotion": "Independent text, identity, expression, demographic soft evidence and full-scene review remain required.",
                },
                "entries": records,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[{line_index}/{len(selected)}] {entry['speaker']} {entry['id']}", flush=True)
    finally:
        del converter
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
