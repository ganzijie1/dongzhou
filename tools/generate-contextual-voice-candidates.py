#!/usr/bin/env python3
"""Generate isolated Qwen3-TTS candidates; never replace shipped audio directly."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
MODEL_PATH = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-VoiceDesign"
OUTPUT_ROOT = ROOT / "output" / "voice-production" / "contextual-candidates"
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="01", help="Comma-separated stage IDs, or 'all'.")
    parser.add_argument("--speakers", default="", help="Comma-separated exact speaker names.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of dialogue lines.")
    parser.add_argument("--one-per-speaker", action="store_true", help="Keep the first selected line for each speaker.")
    parser.add_argument("--candidates", type=int, default=3)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--plan-only", action="store_true", help="Write the review queue without loading Qwen.")
    return parser.parse_args()


def seed_for(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big")


def selected_entries(plan: dict, stages: set[str] | None, speakers: set[str]) -> list[dict]:
    if stages is None:
        ids = {entry["id"] for entry in plan["entries"]}
    else:
        ids = {item["entryId"] for item in plan["occurrences"] if item["stageId"] in stages}
    return [
        entry for entry in plan["entries"]
        if entry["id"] in ids and (not speakers or entry["speaker"] in speakers)
    ]


def model_is_complete(path: Path) -> bool:
    return (
        (path / "model.safetensors").stat().st_size > 3_000_000_000
        and (path / "speech_tokenizer" / "model.safetensors").stat().st_size > 500_000_000
    )


def load_model(device: str):
    import torch
    from qwen_tts import Qwen3TTSModel

    if not model_is_complete(MODEL_PATH):
        raise RuntimeError(f"Incomplete VoiceDesign model: {MODEL_PATH}")
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    model = Qwen3TTSModel.from_pretrained(
        str(MODEL_PATH), dtype=dtype, attn_implementation="sdpa", low_cpu_mem_usage=False,
    )
    model.model.to(device)
    model.device = torch.device(device)
    return model


def analyze_audio(waveform, sample_rate: int, text: str, delivery: dict) -> dict:
    import numpy as np

    audio = np.asarray(waveform, dtype=np.float32).reshape(-1)
    duration = len(audio) / sample_rate
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    rms = float(np.sqrt(np.mean(np.square(audio)))) if len(audio) else 0.0
    clipping = float(np.mean(np.abs(audio) >= 0.995)) if len(audio) else 1.0
    silence = float(np.mean(np.abs(audio) < 0.003)) if len(audio) else 1.0
    chars_per_second = len(text.strip()) / max(duration, 0.001)

    # Historical dramatic Mandarin is normally more deliberate than news reading.
    target_cps = 3.6 * float(delivery.get("pace", 1.0))
    pace_error = abs(math.log(max(chars_per_second, 0.1) / max(target_cps, 0.1)))
    pace_score = math.exp(-1.8 * pace_error)
    target_rms = 0.055 + 0.06 * float(delivery.get("intensity", 0.4))
    energy_error = abs(math.log(max(rms, 0.001) / target_rms))
    energy_score = math.exp(-1.4 * energy_error)
    prosody_score = 0.7 * pace_score + 0.3 * energy_score

    duration_ok = 0.35 <= duration <= 30.0
    quality_score = 1.0
    if not duration_ok:
        quality_score = 0.0
    quality_score *= max(0.0, 1.0 - clipping * 100.0)
    if peak < 0.015 or rms < 0.003:
        quality_score *= 0.1
    if silence > 0.78:
        quality_score *= 0.4
    return {
        "duration": round(duration, 3),
        "peak": round(peak, 6),
        "rms": round(rms, 6),
        "clippingRatio": round(clipping, 7),
        "silenceRatio": round(silence, 5),
        "charsPerSecond": round(chars_per_second, 3),
        "targetCharsPerSecond": round(target_cps, 3),
        "prosodyScore": round(prosody_score, 4),
        "qualityScore": round(quality_score, 4),
        "durationGate": duration_ok,
    }


def empty_record(entry: dict, card: dict, candidates: int) -> dict:
    return {
        "entryId": entry["id"],
        "speaker": entry["speaker"],
        "text": entry["text"],
        "voiceCardId": card["id"],
        "expectedGender": card["gender"],
        "expectedAgeBand": card["ageBand"],
        "context": entry["context"],
        "delivery": entry["delivery"],
        "requestedCandidates": candidates,
        "candidates": [],
        "gates": {
            "text": "pending_independent_asr",
            "identity": "pending_speaker_embedding",
            "gender": "pending_human_reference_review",
            "prosody": "pending_generation",
        },
        "promotionEligible": False,
    }


def write_index(records: list[dict], plan_only: bool) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "backend": "qwen3-tts-contextual-voice-design",
        "model": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        "planOnly": plan_only,
        "policy": {
            "isolation": "Candidates are written under output and never overwrite web-game audio.",
            "ranking": "Automatic quality and prosody scores only; missing ASR, identity, and gender gates are not imputed.",
            "promotion": "All four gates plus explicit review approval are required before deployment.",
        },
        "entries": records,
    }
    INDEX_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.candidates < 1:
        raise RuntimeError("--candidates must be positive")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if plan.get("schemaVersion") != 3:
        raise RuntimeError("Rebuild the voice plan with schema 3 before contextual synthesis")
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    stages = None if args.stages.strip().lower() == "all" else {item.strip() for item in args.stages.split(",") if item.strip()}
    speakers = {item.strip() for item in args.speakers.split(",") if item.strip()}
    entries = selected_entries(plan, stages, speakers)
    if args.one_per_speaker:
        first_by_speaker: dict[str, dict] = {}
        for entry in entries:
            first_by_speaker.setdefault(entry["speaker"], entry)
        entries = list(first_by_speaker.values())
    entries = entries[: args.limit or None]
    records = [empty_record(entry, cards_by_id[entry["voiceCardId"]], args.candidates) for entry in entries]
    selected_ids = {entry["id"] for entry in entries}
    preserved_records: list[dict] = []
    if INDEX_PATH.exists():
        previous = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        preserved_records = [item for item in previous.get("entries", []) if item.get("entryId") not in selected_ids]
    all_records = preserved_records + records
    write_index(all_records, args.plan_only)
    print(json.dumps({"selectedLines": len(entries), "planOnly": args.plan_only, "index": str(INDEX_PATH)}, ensure_ascii=False))
    if args.plan_only or not entries:
        return

    import soundfile as sf
    import torch

    model = load_model(args.device)
    try:
        for line_index, (entry, record) in enumerate(zip(entries, records), start=1):
            entry_dir = OUTPUT_ROOT / entry["id"]
            entry_dir.mkdir(parents=True, exist_ok=True)
            instruction = entry["context"]["synthesisInstruction"]
            for candidate_index in range(1, args.candidates + 1):
                path = entry_dir / f"candidate-{candidate_index}.wav"
                if path.exists() and not args.force:
                    waveform, sample_rate = sf.read(path, dtype="float32")
                else:
                    seed = seed_for(f"{entry['id']}|{candidate_index}")
                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(seed)
                    wavs, sample_rate = model.generate_voice_design(
                        text=entry["text"], language="Chinese", instruct=instruction,
                        do_sample=True, top_p=0.88, temperature=0.78, repetition_penalty=1.08,
                    )
                    waveform = wavs[0]
                    sf.write(path, waveform, sample_rate)
                analysis = analyze_audio(waveform, sample_rate, entry["text"], entry["delivery"])
                record["candidates"].append({
                    "candidate": candidate_index,
                    "seed": seed_for(f"{entry['id']}|{candidate_index}"),
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "analysis": analysis,
                    "automaticRankScore": round(0.55 * analysis["prosodyScore"] + 0.45 * analysis["qualityScore"], 4),
                })
            record["candidates"].sort(key=lambda item: item["automaticRankScore"], reverse=True)
            record["gates"]["prosody"] = "pass" if record["candidates"][0]["analysis"]["prosodyScore"] >= 0.55 else "fail"
            write_index(all_records, False)
            print(f"[{line_index}/{len(entries)}] {entry['speaker']} {entry['id']}", flush=True)
    finally:
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    write_index(all_records, False)


if __name__ == "__main__":
    main()
