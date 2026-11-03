#!/usr/bin/env python3
"""Run reproducible acoustic, ASR, and speaker-embedding evaluation on voice candidates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from voice_quality_metrics import analyze_audio, character_error_rate, normalize_transcript


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
REVIEW_PATH = ROOT / "output" / "voice-production" / "contextual-human-review.json"
SUMMARY_PATH = ROOT / "output" / "voice-production" / "contextual-evaluation-summary.json"
EMBEDDING_ROOT = ROOT / "output" / "voice-production" / "speaker-embeddings"
SPEAKER_MODEL_ROOT = WORKSPACE / ".tools" / "models" / "speechbrain-spkrec-ecapa-voxceleb"
ASR_MODEL_ROOT = WORKSPACE / ".tools" / "models" / "faster-whisper-small"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asr", action="store_true", help="Run independent Mandarin ASR and CER.")
    parser.add_argument("--speaker-embeddings", action="store_true", help="Extract ECAPA-TDNN embeddings.")
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--asr-model", default="small")
    parser.add_argument("--limit", type=int, default=0, help="Limit candidate files for diagnostics.")
    return parser.parse_args()


def safe_candidate_path(candidate: dict) -> Path:
    relative = Path(candidate["file"])
    path = (ROOT / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or ROOT.resolve() not in path.parents or not path.is_file():
        raise RuntimeError(f"Unsafe or missing candidate path: {relative}")
    return path


def load_reviews() -> list[dict]:
    if not REVIEW_PATH.exists():
        return []
    payload = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    return payload.get("reviews", [])


def approved_anchors(reviews: list[dict]) -> dict[str, tuple[str, int]]:
    anchors: dict[str, tuple[str, int]] = {}
    for review in reviews:
        if review.get("anchorApproved") and not any((review.get("hardErrors") or {}).values()):
            anchors[review["speaker"]] = (review["entryId"], int(review["candidate"]))
    return anchors


def load_asr(model_name: str, device: str):
    from faster_whisper import WhisperModel

    compute_type = "float16" if device == "cuda" else "int8"
    source = str(ASR_MODEL_ROOT) if (ASR_MODEL_ROOT / "model.bin").exists() else model_name
    return WhisperModel(source, device=device, compute_type=compute_type, download_root=str(ASR_MODEL_ROOT.parent))


def transcribe(model, path: Path) -> tuple[str, dict]:
    segments, info = model.transcribe(
        str(path), language="zh", beam_size=5, vad_filter=True,
        condition_on_previous_text=False, word_timestamps=False,
    )
    text = "".join(segment.text.strip() for segment in segments)
    return text, {
        "language": info.language,
        "languageProbability": round(float(info.language_probability), 4),
    }


def load_speaker_encoder(device: str):
    from speechbrain.inference.speaker import EncoderClassifier

    return EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir=str(SPEAKER_MODEL_ROOT),
        run_opts={"device": device},
    )


def encode_speaker(encoder, path: Path):
    import numpy as np
    import torch
    import torchaudio

    waveform, sample_rate = torchaudio.load(str(path))
    waveform = waveform.mean(dim=0, keepdim=True)
    if sample_rate != 16000:
        waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
    with torch.inference_mode():
        embedding = encoder.encode_batch(waveform).squeeze().detach().cpu().numpy().astype(np.float32)
    embedding /= max(float(np.linalg.norm(embedding)), 1e-8)
    return embedding


def cosine(left, right) -> float:
    import numpy as np

    return float(np.dot(left, right) / max(np.linalg.norm(left) * np.linalg.norm(right), 1e-8))


def update_entry_gates(entry: dict, anchors: dict[str, tuple[str, int]], reviewed: dict[tuple[str, int], dict]) -> None:
    selected = anchors.get(entry["speaker"])
    if not selected:
        entry["gates"]["text"] = "pending_candidate_selection"
        entry["gates"]["identity"] = "pending_approved_anchor"
        entry["gates"]["humanReview"] = "pending_blind_review"
        entry["approvedAnchorCandidate"] = None
        entry["promotionEligible"] = False
        return
    anchor_entry, anchor_candidate = selected
    if anchor_entry == entry["entryId"]:
        entry["approvedAnchorCandidate"] = anchor_candidate
    review = reviewed.get((entry["entryId"], anchor_candidate))
    if review:
        entry["gates"]["humanReview"] = "anchor_approved_single_reviewer"
    chosen = next((item for item in entry["candidates"] if int(item["candidate"]) == anchor_candidate), None)
    if chosen and chosen.get("textValidation"):
        entry["gates"]["text"] = chosen["textValidation"]["status"]
    entry["promotionEligible"] = False


def main() -> None:
    args = parse_args()
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if index.get("schemaVersion") not in (1, 2):
        raise RuntimeError("Unsupported candidate index schema")
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    reviews = load_reviews()
    anchors = approved_anchors(reviews)
    reviewed = {(item["entryId"], int(item["candidate"])): item for item in reviews}

    asr = load_asr(args.asr_model, args.device) if args.asr else None
    encoder = load_speaker_encoder(args.device) if args.speaker_embeddings else None
    embedding_cache: dict[tuple[str, int], object] = {}
    processed = 0
    warnings = defaultdict(int)

    for entry in index["entries"]:
        card = cards_by_id[entry["voiceCardId"]]
        entry.setdefault("alerts", [])
        entry.setdefault("gates", {})
        entry["gates"].pop("pitchSanity", None)
        entry["gates"].pop("gender", None)
        entry["gates"].setdefault("calibration", "pending_project_calibration")
        entry["gates"].setdefault("humanReview", "pending_blind_review")
        for candidate in entry.get("candidates", []):
            if args.limit and processed >= args.limit:
                break
            path = safe_candidate_path(candidate)
            import soundfile as sf

            waveform, sample_rate = sf.read(path, dtype="float32")
            analysis = analyze_audio(waveform, sample_rate, entry["text"], entry["delivery"], card)
            candidate["analysis"] = analysis
            candidate["automaticRankScore"] = round(
                0.35 * analysis["qualityScore"]
                + 0.25 * analysis["speechTiming"]["paceScore"]
                + 0.20 * analysis["pauseStructure"]["pauseScore"]
                + 0.20 * analysis["energy"]["energyScore"],
                4,
            )
            if analysis["pitch"]["warning"]:
                warnings["pitch_outside_broad_reference"] += 1
            if asr is not None:
                hypothesis, metadata = transcribe(asr, path)
                cer = character_error_rate(entry["text"], hypothesis)
                candidate["textValidation"] = {
                    "model": f"faster-whisper/{args.asr_model}",
                    "reference": entry["text"],
                    "hypothesis": hypothesis,
                    "normalizedReference": normalize_transcript(entry["text"]),
                    "normalizedHypothesis": normalize_transcript(hypothesis),
                    "cer": round(cer, 4),
                    "status": "pass" if cer <= 0.12 else "warning_human_text_review",
                    "caveat": "ASR errors on ancient names and terms require human review.",
                    **metadata,
                }
            elif candidate.get("textValidation", {}).get("hypothesis") is not None:
                text_validation = candidate["textValidation"]
                hypothesis = text_validation["hypothesis"]
                cer = character_error_rate(entry["text"], hypothesis)
                text_validation.update({
                    "normalizedReference": normalize_transcript(entry["text"]),
                    "normalizedHypothesis": normalize_transcript(hypothesis),
                    "cer": round(cer, 4),
                    "status": "pass" if cer <= 0.12 else "warning_human_text_review",
                })
            if encoder is not None:
                embedding = encode_speaker(encoder, path)
                embedding_cache[(entry["entryId"], int(candidate["candidate"]))] = embedding
                embedding_path = EMBEDDING_ROOT / entry["entryId"] / f"candidate-{candidate['candidate']}.npy"
                embedding_path.parent.mkdir(parents=True, exist_ok=True)
                import numpy as np

                np.save(embedding_path, embedding)
                candidate["speakerEmbedding"] = {
                    "model": "speechbrain/spkrec-ecapa-voxceleb",
                    "dimension": int(embedding.shape[0]),
                    "file": str(embedding_path.relative_to(ROOT)).replace("\\", "/"),
                }
            processed += 1
        entry["candidates"].sort(key=lambda item: item["automaticRankScore"], reverse=True)
        if entry["candidates"]:
            best = entry["candidates"][0]["analysis"]
            entry["gates"]["waveform"] = "pass" if best["waveformGate"] else "fail"
            entry["gates"]["prosody"] = "pass" if best["prosodyScore"] >= 0.55 else "warning_human_prosody_review"
            entry["alerts"] = ["pitch_outside_broad_reference"] if best["pitch"]["warning"] else []

    if encoder is not None:
        for entry in index["entries"]:
            anchor = anchors.get(entry["speaker"])
            if not anchor:
                continue
            anchor_embedding = embedding_cache.get(anchor)
            if anchor_embedding is None:
                continue
            distinct_entries = set()
            similarities = []
            for other in index["entries"]:
                if other["speaker"] != entry["speaker"]:
                    continue
                for candidate in other.get("candidates", []):
                    key = (other["entryId"], int(candidate["candidate"]))
                    embedding = embedding_cache.get(key)
                    if embedding is None or key == anchor:
                        continue
                    score = cosine(anchor_embedding, embedding)
                    candidate.setdefault("speakerEmbedding", {})["similarityToApprovedAnchor"] = round(score, 4)
                    distinct_entries.add(other["entryId"])
                    similarities.append(score)
            if len(distinct_entries) >= 2:
                entry["identityEvaluation"] = {
                    "anchor": {"entryId": anchor[0], "candidate": anchor[1]},
                    "meanSimilarity": round(sum(similarities) / len(similarities), 4),
                    "minimumSimilarity": round(min(similarities), 4),
                    "status": "requires_project_threshold_calibration",
                }
                entry["gates"]["identity"] = "pending_project_threshold_calibration"
            else:
                entry["gates"]["identity"] = "pending_cross_sentence_samples"

    for entry in index["entries"]:
        update_entry_gates(entry, anchors, reviewed)
    index["schemaVersion"] = 2
    index["evaluatedAt"] = datetime.now(timezone.utc).isoformat()
    index.setdefault("policy", {})["pitch"] = "Median F0 is an alert only and is excluded from rank and promotion gates."
    index["policy"]["identity"] = "Cross-sentence identity requires an approved anchor, at least two distinct texts, and project-calibrated thresholds."
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "schemaVersion": 1,
        "evaluatedAt": index["evaluatedAt"],
        "entries": len(index["entries"]),
        "candidatesProcessed": processed,
        "asrEnabled": args.asr,
        "speakerEmbeddingsEnabled": args.speaker_embeddings,
        "approvedAnchors": len(anchors),
        "warnings": dict(warnings),
        "promotionPolicy": "No candidate can ship before calibrated identity and panel blind-review gates pass.",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
