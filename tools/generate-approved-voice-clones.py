#!/usr/bin/env python3
"""Clone approved character anchors across distinct dialogue lines in an isolated output tree."""

from __future__ import annotations

import argparse
import gc
import hashlib
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
MODEL_PATH = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-Base"
OUTPUT_ROOT = ROOT / "output" / "voice-production" / "approved-voice-clones"
INDEX_PATH = ROOT / "output" / "voice-production" / "approved-voice-clone-index.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="01", help="Comma-separated stage IDs, or all.")
    parser.add_argument("--speakers", default="", help="Comma-separated approved speaker names.")
    parser.add_argument("--candidates", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    return parser.parse_args()


def seed_for(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big")


def model_is_complete(path: Path) -> bool:
    return (
        (path / "model.safetensors").stat().st_size > 3_000_000_000
        and (path / "speech_tokenizer" / "model.safetensors").stat().st_size > 500_000_000
    )


def load_model(device: str):
    import torch
    from qwen_tts import Qwen3TTSModel

    if not model_is_complete(MODEL_PATH):
        raise RuntimeError(f"Incomplete Base model: {MODEL_PATH}")
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    model = Qwen3TTSModel.from_pretrained(
        str(MODEL_PATH), dtype=dtype, attn_implementation="sdpa", low_cpu_mem_usage=False,
    )
    model.model.to(device)
    model.device = torch.device(device)
    return model


def approved_anchors(source_index: dict) -> dict[str, dict]:
    anchors: dict[str, dict] = {}
    for entry in source_index["entries"]:
        number = entry.get("approvedAnchorCandidate")
        if number is None or entry.get("gates", {}).get("humanReview") != "anchor_approved_single_reviewer":
            continue
        candidate = next((item for item in entry["candidates"] if int(item["candidate"]) == int(number)), None)
        if candidate:
            anchors[entry["speaker"]] = {
                "entryId": entry["entryId"],
                "candidate": int(number),
                "text": entry["text"],
                "path": ROOT / candidate["file"],
            }
    return anchors


def selected_entries(plan: dict, stages: set[str] | None, speakers: set[str], approved: set[str]) -> list[dict]:
    if stages is None:
        entry_ids = {entry["id"] for entry in plan["entries"]}
    else:
        entry_ids = {item["entryId"] for item in plan["occurrences"] if item["stageId"] in stages}
    return [
        entry for entry in plan["entries"]
        if entry["id"] in entry_ids and entry["speaker"] in approved and (not speakers or entry["speaker"] in speakers)
    ]


def main() -> None:
    args = parse_args()
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    source_index = json.loads(SOURCE_INDEX_PATH.read_text(encoding="utf-8"))
    anchors = approved_anchors(source_index)
    if not anchors:
        raise RuntimeError("No single-reviewer-approved anchors. Complete the blind review before cloning.")
    stages = None if args.stages.lower() == "all" else {item.strip() for item in args.stages.split(",") if item.strip()}
    speakers = {item.strip() for item in args.speakers.split(",") if item.strip()}
    entries = selected_entries(plan, stages, speakers, set(anchors))[: args.limit or None]
    records = [{
        "entryId": entry["id"],
        "speaker": entry["speaker"],
        "text": entry["text"],
        "voiceCardId": entry["voiceCardId"],
        "anchor": {
            "entryId": anchors[entry["speaker"]]["entryId"],
            "candidate": anchors[entry["speaker"]]["candidate"],
        },
        "candidates": [],
        "gates": {
            "waveform": "pending_generation",
            "text": "pending_independent_asr",
            "identity": "pending_speaker_embedding",
            "humanReview": "pending_cross_sentence_blind_review",
            "calibration": "pending_project_calibration",
        },
        "promotionEligible": False,
    } for entry in entries]
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "backend": "qwen3-tts-base-approved-anchor-clone",
        "model": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "isolation": "Review candidates only; never overwrite web-game audio.",
        "entries": records,
    }
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"approvedSpeakers": sorted(anchors), "selectedLines": len(entries), "planOnly": args.plan_only}, ensure_ascii=False))
    if args.plan_only or not entries:
        return

    import soundfile as sf
    import torch

    model = load_model(args.device)
    prompts = {
        speaker: model.create_voice_clone_prompt(
            ref_audio=str(anchor["path"]), ref_text=anchor["text"], x_vector_only_mode=False,
        )
        for speaker, anchor in anchors.items() if not speakers or speaker in speakers
    }
    try:
        for line_number, (entry, record) in enumerate(zip(entries, records), start=1):
            entry_dir = OUTPUT_ROOT / entry["id"]
            entry_dir.mkdir(parents=True, exist_ok=True)
            for candidate_number in range(1, args.candidates + 1):
                path = entry_dir / f"candidate-{candidate_number}.wav"
                seed = seed_for(f"clone|{entry['id']}|{candidate_number}")
                if path.exists() and not args.force:
                    waveform, sample_rate = sf.read(path, dtype="float32")
                else:
                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(seed)
                    wavs, sample_rate = model.generate_voice_clone(
                        text=entry["text"], language="Chinese", voice_clone_prompt=prompts[entry["speaker"]],
                        do_sample=True, top_p=0.86, temperature=0.72, repetition_penalty=1.08,
                    )
                    waveform = wavs[0]
                    sf.write(path, waveform, sample_rate)
                analysis = analyze_audio(waveform, sample_rate, entry["text"], entry["delivery"], cards_by_id[entry["voiceCardId"]])
                record["candidates"].append({
                    "candidate": candidate_number,
                    "seed": seed,
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "analysis": analysis,
                    "automaticRankScore": round(
                        0.35 * analysis["qualityScore"]
                        + 0.25 * analysis["speechTiming"]["paceScore"]
                        + 0.20 * analysis["pauseStructure"]["pauseScore"]
                        + 0.20 * analysis["energy"]["energyScore"],
                        4,
                    ),
                })
            record["candidates"].sort(key=lambda item: item["automaticRankScore"], reverse=True)
            record["gates"]["waveform"] = "pass" if record["candidates"][0]["analysis"]["waveformGate"] else "fail"
            INDEX_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[{line_number}/{len(entries)}] {entry['speaker']} {entry['id']}", flush=True)
    finally:
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
