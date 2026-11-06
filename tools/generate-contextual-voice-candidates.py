#!/usr/bin/env python3
"""Generate isolated Qwen3-TTS candidates; never replace shipped audio directly."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from voice_quality_metrics import analyze_audio


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
MODEL_PATH = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-VoiceDesign"
CUSTOM_VOICE_MODEL_PATH = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-CustomVoice-complete"
QWEN_PYTHON = WORKSPACE / ".tools" / "venvs" / "qwen3-tts" / "Scripts" / "python.exe"
OUTPUT_ROOT = ROOT / "output" / "voice-production" / "contextual-candidates"
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
CUSTOM_OUTPUT_ROOT = ROOT / "output" / "voice-production" / "custom-voice-contextual-candidates"
CUSTOM_INDEX_PATH = ROOT / "output" / "voice-production" / "custom-voice-contextual-index.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("voice-design", "custom-voice"), default="voice-design")
    parser.add_argument("--stages", default="01", help="Comma-separated stage IDs, or 'all'.")
    parser.add_argument("--speakers", default="", help="Comma-separated exact speaker names.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of dialogue lines.")
    parser.add_argument("--one-per-speaker", action="store_true", help="Keep the first selected line for each speaker.")
    parser.add_argument("--candidates", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=12, help="Batch independent scenes while preserving in-scene order.")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--index-path", default="", help="Optional isolated index path for parallel disjoint stage shards.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--plan-only", action="store_true", help="Write the review queue without loading Qwen.")
    parser.add_argument("--analyze-only", action="store_true", help="Re-score existing candidates without loading Qwen.")
    return parser.parse_args()


def seed_for(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big")


def selected_entries(plan: dict, stages: set[str] | None, speakers: set[str]) -> list[dict]:
    if stages is None:
        ids = {entry["id"] for entry in plan["entries"]}
    else:
        ids = {item["entryId"] for item in plan["occurrences"] if item["stageId"] in stages}
    entries = [
        entry for entry in plan["entries"]
        if entry["id"] in ids and (not speakers or entry["speaker"] in speakers)
    ]
    occurrence_order = {item["entryId"]: index for index, item in enumerate(plan["occurrences"])}
    return sorted(entries, key=lambda entry: occurrence_order.get(entry["id"], 10**9))


def acoustic_summary(analysis: dict) -> str:
    timing = analysis["speechTiming"]
    pauses = analysis["pauseStructure"]
    energy = analysis["energy"]
    pitch = analysis["pitch"]
    return (
        f"时长{analysis['duration']:.2f}秒，语速{timing['speechRateCharsPerSecond']:.2f}字/秒，"
        f"内部停顿{pauses['internalPauseCount']}次、共{pauses['internalPauseDuration']:.2f}秒，"
        f"能量动态范围{energy['dynamicRangeDb']:.2f}dB，"
        + (f"中位基频{pitch['medianF0Hz']:.1f}Hz" if pitch.get("medianF0Hz") else "基频留待完整质检")
    )


def analyze_audio_fast(waveform, sample_rate: int, text: str, delivery: dict) -> dict:
    """Cheap causal summary; full release metrics are recomputed by the evaluator."""
    import librosa
    import numpy as np

    audio = np.asarray(waveform, dtype=np.float32).reshape(-1)
    duration = len(audio) / max(sample_rate, 1)
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    rms = float(np.sqrt(np.mean(np.square(audio)))) if len(audio) else 0.0
    clipping = float(np.mean(np.abs(audio) >= 0.995)) if len(audio) else 1.0
    raw_silence = float(np.mean(np.abs(audio) < 0.003)) if len(audio) else 1.0
    intervals = librosa.effects.split(audio, top_db=34, frame_length=1024, hop_length=512)
    segments = [(int(start), int(end)) for start, end in intervals if end > start]
    speech_duration = sum(end - start for start, end in segments) / max(sample_rate, 1)
    pauses = [
        {"start": round(left / sample_rate, 3), "end": round(right / sample_rate, 3), "duration": round((right - left) / sample_rate, 3)}
        for (_, left), (right, _) in zip(segments, segments[1:]) if right > left
    ]
    pause_duration = sum(item["duration"] for item in pauses)
    chars = len(re.findall(r"[\u3400-\u9fffA-Za-z0-9]", text))
    speech_rate = chars / max(duration, 0.001)
    target_rate = 3.6 * float(delivery.get("pace", 1.0))
    pace_score = math.exp(-1.8 * abs(math.log(max(speech_rate, 0.1) / max(target_rate, 0.1))))
    frame_rms = librosa.feature.rms(y=audio, frame_length=1024, hop_length=512)[0]
    active = frame_rms[frame_rms > max(1e-7, np.max(frame_rms, initial=0.0) * 0.02)]
    if len(active):
        active_db = 20.0 * np.log10(active + 1e-7)
        dynamic_range = float(np.quantile(active_db, 0.90) - np.quantile(active_db, 0.10))
        variation = float(np.std(active) / max(np.mean(active), 1e-7))
    else:
        dynamic_range = variation = 0.0
    target_dynamic = 8.0 + 12.0 * float(delivery.get("intensity", 0.4))
    energy_score = math.exp(-abs(dynamic_range - target_dynamic) / 14.0)
    expected_boundaries = len(re.findall(r"[，、；：。！？!?;:]", text))
    pause_count_error = abs(len(pauses) - expected_boundaries)
    pause_score = math.exp(-0.22 * pause_count_error)
    waveform_gate = 0.35 <= duration <= 30.0 and clipping <= 0.0005 and peak >= 0.015 and rms >= 0.003 and raw_silence <= 0.78
    return {
        "duration": round(duration, 3), "peak": round(peak, 6), "rms": round(rms, 6),
        "clippingRatio": round(clipping, 7), "rawSilenceRatio": round(raw_silence, 5),
        "waveformGate": waveform_gate, "qualityScore": 1.0 if waveform_gate else 0.0,
        "speechTiming": {
            "spokenCharacters": chars, "speechDuration": round(speech_duration, 3),
            "speechRateCharsPerSecond": round(speech_rate, 3),
            "articulationRateCharsPerSecond": round(chars / max(speech_duration, 0.001), 3),
            "targetSpeechRate": round(target_rate, 3), "paceScore": round(pace_score, 4),
        },
        "pauseStructure": {
            "speechSegmentCount": len(segments), "internalPauseCount": len(pauses),
            "internalPauseDuration": round(pause_duration, 3),
            "internalPauseRatio": round(pause_duration / max(duration, 0.001), 4),
            "pauseScore": round(pause_score, 4), "events": pauses,
        },
        "energy": {"dynamicRangeDb": round(dynamic_range, 3), "rmsVariation": round(variation, 4), "energyScore": round(energy_score, 4)},
        "broadcastCadence": {"riskScore": 0.0, "hardReject": False, "evidenceAvailable": False, "status": "pending_full_evaluation"},
        "pitch": {"medianF0Hz": 0.0, "warning": False, "status": "pending_full_evaluation"},
        "prosodyScore": round(0.4 * pace_score + 0.3 * pause_score + 0.3 * energy_score, 4),
        "analysisTier": "fast_causal_summary_pending_full_evaluation",
    }


def model_is_complete(path: Path) -> bool:
    return (
        (path / "model.safetensors").stat().st_size > 3_000_000_000
        and (path / "speech_tokenizer" / "model.safetensors").stat().st_size > 500_000_000
    )


def load_model(path: Path, device: str):
    import torch
    from qwen_tts import Qwen3TTSModel

    if not model_is_complete(path):
        raise RuntimeError(f"Incomplete Qwen TTS model: {path}")
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    model = Qwen3TTSModel.from_pretrained(
        str(path), dtype=dtype, attn_implementation="sdpa", low_cpu_mem_usage=False,
    )
    model.model.to(device)
    model.device = torch.device(device)
    return model


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
            "identity": "pending_approved_anchor",
            "humanReview": "pending_blind_review",
            "calibration": "pending_project_calibration",
            "waveform": "pending_generation",
            "prosody": "pending_generation",
            "broadcastCadence": "pending_generation",
        },
        "alerts": [],
        "approvedAnchorCandidate": None,
        "promotionEligible": False,
    }


def write_index(records: list[dict], plan_only: bool, index_path: Path, backend: str) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    custom_voice = backend == "custom-voice"
    payload = {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "backend": "qwen3-tts-contextual-custom-voice" if custom_voice else "qwen3-tts-contextual-voice-design",
        "model": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice" if custom_voice else "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        "planOnly": plan_only,
        "policy": {
            "isolation": "Candidates are written under output and never overwrite web-game audio.",
            "ranking": "Waveform, pace, pause, and energy scores only; pitch is excluded from ranking and missing review gates are never imputed.",
            "promotion": "Every automatic and human-review gate plus explicit approval is required before deployment.",
            "pitch": "Median F0 is an alert only; it never changes promotion eligibility or automatic rank.",
            "breath": "Breath-like events are acoustic proxies pending human confirmation.",
            "broadcastCadence": "Repeated equal timing, uniform emphasis and fixed endings are a hard rejection when evidence is sufficient.",
        },
        "entries": records,
    }
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def custom_voice_speaker(card: dict) -> str:
    if card.get("gender") == "female":
        return "Vivian" if card.get("ageBand") in {"child", "young_adult"} else "Serena"
    if card.get("ageBand") in {"mature", "late_middle", "elder"}:
        return "Uncle_Fu"
    return "Dylan"


def generate_custom_voice_batched(
    entries: list[dict],
    records: list[dict],
    cards_by_id: dict[str, dict],
    model,
    torch,
    sf,
    args: argparse.Namespace,
    all_records: list[dict],
    index_path: Path,
) -> None:
    """Batch one ready line per scene so context remains causal within every scene."""
    stage_queues: dict[str, list[tuple[dict, dict]]] = {}
    stage_order: list[str] = []
    for entry, record in zip(entries, records):
        occurrence = entry.get("firstOccurrence") or {}
        stage_id = str(occurrence.get("stageId", ""))
        if stage_id not in stage_queues:
            stage_queues[stage_id] = []
            stage_order.append(stage_id)
        stage_queues[stage_id].append((entry, record))

    previous_scene_audio: dict[str, str] = {}
    previous_speaker_audio: dict[tuple[str, str], str] = {}
    completed = 0
    while completed < len(entries):
        available = [
            (stage_id, stage_queues[stage_id][0][0], stage_queues[stage_id][0][1])
            for stage_id in stage_order if stage_queues[stage_id]
        ]
        available.sort(key=lambda item: len(item[1]["text"]))
        ready = available[: max(1, args.batch_size)]
        for stage_id, _, _ in ready:
            stage_queues[stage_id].pop(0)
        if not ready:
            raise RuntimeError("Contextual batch scheduler stalled")

        jobs: list[dict] = []
        for stage_id, entry, record in ready:
            card = cards_by_id[entry["voiceCardId"]]
            instruction_parts = [entry["context"]["synthesisInstruction"]]
            scene_summary = previous_scene_audio.get(stage_id)
            speaker_summary = previous_speaker_audio.get((stage_id, entry["speaker"]))
            if scene_summary:
                instruction_parts.append(f"上一句场景声学摘要：{scene_summary}。保持对话承接，但不要机械复制其节奏。")
            if speaker_summary:
                instruction_parts.append(f"本角色上一句声学摘要：{speaker_summary}。保持同一人物、年龄和声纹重心，同时服从当前剧情状态。")
            instruction = "".join(instruction_parts)
            record["effectiveSynthesisInstruction"] = instruction
            source_speaker = custom_voice_speaker(card)
            record["sourceSpeaker"] = source_speaker
            path = CUSTOM_OUTPUT_ROOT / entry["id"] / "candidate-1.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            jobs.append({
                "stageId": stage_id,
                "entry": entry,
                "record": record,
                "card": card,
                "instruction": instruction,
                "speaker": source_speaker,
                "path": path,
            })

        missing = [job for job in jobs if args.force or not job["path"].exists()]
        generated: dict[str, tuple[object, int, int]] = {}
        if missing:
            batch_seed = seed_for("|".join(job["entry"]["id"] for job in missing))
            torch.manual_seed(batch_seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(batch_seed)
            wavs, sample_rate = model.generate_custom_voice(
                text=[job["entry"]["text"] for job in missing],
                language=["Chinese"] * len(missing),
                speaker=[job["speaker"] for job in missing],
                instruct=[job["instruction"] for job in missing],
                max_new_tokens=240,
                do_sample=True,
                top_p=0.88,
                temperature=0.78,
                repetition_penalty=1.08,
            )
            if len(wavs) != len(missing):
                raise RuntimeError(f"CustomVoice batch returned {len(wavs)} outputs for {len(missing)} jobs")
            for job, waveform in zip(missing, wavs):
                sf.write(job["path"], waveform, sample_rate)
                generated[job["entry"]["id"]] = (waveform, sample_rate, batch_seed)

        for job in jobs:
            entry = job["entry"]
            record = job["record"]
            if entry["id"] in generated:
                waveform, sample_rate, batch_seed = generated[entry["id"]]
            else:
                waveform, sample_rate = sf.read(job["path"], dtype="float32")
                batch_seed = seed_for(entry["id"])
            analysis = analyze_audio_fast(waveform, sample_rate, entry["text"], entry["delivery"])
            cadence = analysis["broadcastCadence"]
            base_rank = (
                0.35 * analysis["qualityScore"]
                + 0.25 * analysis["speechTiming"]["paceScore"]
                + 0.20 * analysis["pauseStructure"]["pauseScore"]
                + 0.20 * analysis["energy"]["energyScore"]
            )
            record["candidates"] = [{
                "candidate": 1,
                "seed": seed_for(f"{entry['id']}|1"),
                "batchSeed": batch_seed,
                "file": str(job["path"].relative_to(ROOT)).replace("\\", "/"),
                "analysis": analysis,
                "automaticRankScore": round(base_rank * (0.0 if cadence["hardReject"] else 1.0 - 0.25 * cadence["riskScore"]), 4),
            }]
            record["gates"]["waveform"] = "pass" if analysis["waveformGate"] else "fail"
            record["gates"]["prosody"] = "pass" if analysis["prosodyScore"] >= 0.55 else "fail"
            record["gates"]["broadcastCadence"] = "fail" if cadence["hardReject"] else "pass"
            record["alerts"] = ["pitch_outside_broad_reference"] if analysis["pitch"]["warning"] else []
            if cadence["riskScore"] >= 0.65:
                record["alerts"].append("broadcast_cadence_review")
            summary = acoustic_summary(analysis)
            previous_scene_audio[job["stageId"]] = summary
            previous_speaker_audio[(job["stageId"], entry["speaker"])] = summary
            completed += 1
        write_index(all_records, False, index_path, args.backend)
        print(f"[{completed}/{len(entries)}] contextual scene batches", flush=True)


def main() -> None:
    args = parse_args()
    custom_voice = args.backend == "custom-voice"
    model_path = CUSTOM_VOICE_MODEL_PATH if custom_voice else MODEL_PATH
    output_root = CUSTOM_OUTPUT_ROOT if custom_voice else OUTPUT_ROOT
    index_path = Path(args.index_path).resolve() if args.index_path else (CUSTOM_INDEX_PATH if custom_voice else INDEX_PATH)
    if not args.plan_only and not args.analyze_only and importlib.util.find_spec("qwen_tts") is None:
        if not QWEN_PYTHON.exists():
            raise RuntimeError("Qwen TTS runtime is missing; install qwen-tts in the project voice environment")
        result = subprocess.run([str(QWEN_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])
        raise SystemExit(result.returncode)
    if args.candidates < 1:
        raise RuntimeError("--candidates must be positive")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if plan.get("schemaVersion") != 4:
        raise RuntimeError("Rebuild the voice plan with schema 4 before contextual synthesis")
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
    if index_path.exists():
        previous = json.loads(index_path.read_text(encoding="utf-8"))
        preserved_records = [item for item in previous.get("entries", []) if item.get("entryId") not in selected_ids]
    all_records = preserved_records + records
    write_index(all_records, args.plan_only, index_path, args.backend)
    print(json.dumps({"selectedLines": len(entries), "planOnly": args.plan_only, "backend": args.backend, "index": str(index_path)}, ensure_ascii=False))
    if args.plan_only or not entries:
        return

    import soundfile as sf

    model = None
    torch = None
    if not args.analyze_only:
        import torch as torch_module
        torch = torch_module
        model = load_model(model_path, args.device)
    try:
        if custom_voice and args.candidates == 1 and args.batch_size > 1 and not args.analyze_only:
            generate_custom_voice_batched(
                entries, records, cards_by_id, model, torch, sf, args, all_records, index_path,
            )
            return
        previous_scene_audio: dict[str, str] = {}
        previous_speaker_audio: dict[tuple[str, str], str] = {}
        for line_index, (entry, record) in enumerate(zip(entries, records), start=1):
            card = cards_by_id[entry["voiceCardId"]]
            entry_dir = output_root / entry["id"]
            entry_dir.mkdir(parents=True, exist_ok=True)
            occurrence = entry.get("firstOccurrence") or {}
            stage_id = str(occurrence.get("stageId", ""))
            instruction_parts = [entry["context"]["synthesisInstruction"]]
            scene_summary = previous_scene_audio.get(stage_id)
            speaker_summary = previous_speaker_audio.get((stage_id, entry["speaker"]))
            if scene_summary:
                instruction_parts.append(f"上一句场景声学摘要：{scene_summary}。保持对话承接，但不要机械复制其节奏。")
            if speaker_summary:
                instruction_parts.append(f"本角色上一句声学摘要：{speaker_summary}。保持同一人物、年龄和声纹重心，同时服从当前剧情状态。")
            instruction = "".join(instruction_parts)
            record["effectiveSynthesisInstruction"] = instruction
            for candidate_index in range(1, args.candidates + 1):
                path = entry_dir / f"candidate-{candidate_index}.wav"
                if path.exists() and not args.force:
                    waveform, sample_rate = sf.read(path, dtype="float32")
                else:
                    if args.analyze_only:
                        raise RuntimeError(f"Analyze-only candidate is missing: {path}")
                    seed = seed_for(f"{entry['id']}|{candidate_index}")
                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(seed)
                    generation = {
                        "text": entry["text"], "language": "Chinese", "instruct": instruction,
                        "max_new_tokens": max(160, min(640, len(entry["text"]) * 6 + 80)),
                        "do_sample": True, "top_p": 0.88, "temperature": 0.78, "repetition_penalty": 1.08,
                    }
                    if custom_voice:
                        source_speaker = custom_voice_speaker(card)
                        record["sourceSpeaker"] = source_speaker
                        generation["speaker"] = source_speaker
                        wavs, sample_rate = model.generate_custom_voice(**generation)
                    else:
                        wavs, sample_rate = model.generate_voice_design(**generation)
                    waveform = wavs[0]
                    sf.write(path, waveform, sample_rate)
                analysis = analyze_audio(waveform, sample_rate, entry["text"], entry["delivery"], card)
                cadence = analysis["broadcastCadence"]
                base_rank = (
                    0.35 * analysis["qualityScore"]
                    + 0.25 * analysis["speechTiming"]["paceScore"]
                    + 0.20 * analysis["pauseStructure"]["pauseScore"]
                    + 0.20 * analysis["energy"]["energyScore"]
                )
                record["candidates"].append({
                    "candidate": candidate_index,
                    "seed": seed_for(f"{entry['id']}|{candidate_index}"),
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "analysis": analysis,
                    "automaticRankScore": round(base_rank * (0.0 if cadence["hardReject"] else 1.0 - 0.25 * cadence["riskScore"]), 4),
                })
            record["candidates"].sort(key=lambda item: item["automaticRankScore"], reverse=True)
            best_analysis = record["candidates"][0]["analysis"]
            record["gates"]["waveform"] = "pass" if best_analysis["waveformGate"] else "fail"
            record["gates"]["prosody"] = "pass" if record["candidates"][0]["analysis"]["prosodyScore"] >= 0.55 else "fail"
            record["gates"]["broadcastCadence"] = "fail" if best_analysis["broadcastCadence"]["hardReject"] else "pass"
            record["alerts"] = ["pitch_outside_broad_reference"] if best_analysis["pitch"]["warning"] else []
            if best_analysis["broadcastCadence"]["riskScore"] >= 0.65:
                record["alerts"].append("broadcast_cadence_review")
            summary = acoustic_summary(best_analysis)
            previous_scene_audio[stage_id] = summary
            previous_speaker_audio[(stage_id, entry["speaker"])] = summary
            write_index(all_records, False, index_path, args.backend)
            print(f"[{line_index}/{len(entries)}] {entry['speaker']} {entry['id']}", flush=True)
    finally:
        if model is not None:
            del model
        gc.collect()
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()
    write_index(all_records, False, index_path, args.backend)


if __name__ == "__main__":
    main()
