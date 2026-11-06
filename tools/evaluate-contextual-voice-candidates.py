#!/usr/bin/env python3
"""Run reproducible acoustic, ASR, and speaker-embedding evaluation on voice candidates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from voice_quality_metrics import (
    analyze_audio,
    character_error_rate,
    normalize_transcript,
    transcript_edit_operations,
    validate_critical_terms,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
REVIEW_PATH = ROOT / "output" / "voice-production" / "contextual-human-review.json"
SUMMARY_PATH = ROOT / "output" / "voice-production" / "contextual-evaluation-summary.json"
REPORT_PATH = ROOT / "output" / "voice-production" / "contextual-evaluation-report.md"
EMBEDDING_ROOT = ROOT / "output" / "voice-production" / "speaker-embeddings"
# The legacy cache contains zero-byte placeholders from an interrupted download.
SPEAKER_MODEL_ROOT = WORKSPACE / ".tools" / "models" / "speechbrain-ecapa-complete"
SPEAKER_RUNTIME_ROOT = ROOT / "output" / "voice-production" / "model-runtime" / "ecapa"
ASR_MODEL_ROOT = WORKSPACE / ".tools" / "models" / "faster-whisper-small-complete"
MODEL_CACHE_ROOT = WORKSPACE / ".tools" / "models"
WAVLM_MODEL = WORKSPACE / ".tools" / "models" / "wavlm-base-plus-sv"
DEMOGRAPHIC_MODEL = WORKSPACE / ".tools" / "models" / "wav2vec2-age-gender-complete"
EMOTION_MODEL = WORKSPACE / ".tools" / "models" / "emotion2vec-plus-large"

EMOTION_EXPECTATIONS = {
    "restrained": {"neutral"},
    "grief_or_grievance": {"sad", "fearful", "angry"},
    "urgent_or_commanding": {"angry", "surprised", "neutral"},
    "wary_suspicion": {"fearful", "neutral"},
    "controlled_fear": {"fearful", "neutral"},
    "cold_blame": {"angry", "neutral"},
    "restrained_indignation": {"angry", "sad", "neutral"},
    "urgent_moral_resolve": {"angry", "sad", "neutral"},
    "cold_intimidation": {"angry", "neutral"},
    "grief_to_resolve": {"sad", "angry", "neutral"},
    "performed_ease": {"neutral", "happy"},
    "contained_accusation": {"angry", "sad", "neutral"},
    "controlled_vengeance": {"angry", "neutral"},
    "principled_resolve": {"angry", "neutral"},
    "decisive_action": {"angry", "neutral"},
    "spent_grief": {"sad", "neutral"},
}

EMOTION_LABEL_ALIASES = {
    "生气": "angry",
    "厌恶": "disgusted",
    "害怕": "fearful",
    "开心": "happy",
    "中立": "neutral",
    "其他": "other",
    "难过": "sad",
    "吃惊": "surprised",
    "未知": "unknown",
}

AGE_BAND_REFERENCES = {
    "child": (0, 17),
    "young_adult": (18, 38),
    "adult": (25, 52),
    "mature": (35, 62),
    "late_middle": (48, 78),
    "elder": (58, 100),
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=str(INDEX_PATH), help="Candidate index to evaluate in place.")
    parser.add_argument("--asr", action="store_true", help="Run independent Mandarin ASR and CER.")
    parser.add_argument("--speaker-embeddings", action="store_true", help="Extract ECAPA-TDNN embeddings.")
    parser.add_argument("--wavlm-embeddings", action="store_true", help="Extract independent WavLM X-vector embeddings.")
    parser.add_argument("--emotion", action="store_true", help="Run emotion2vec coarse emotion evidence.")
    parser.add_argument(
        "--research-demographics",
        action="store_true",
        help="Run the non-commercial age/gender model as a soft research alert only.",
    )
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--asr-model", default="small")
    parser.add_argument("--entry-ids", default="", help="Comma-separated entry IDs to re-evaluate.")
    parser.add_argument("--entry-id-file", type=Path, help="Newline- or comma-separated entry IDs to re-evaluate.")
    parser.add_argument("--limit", type=int, default=0, help="Limit candidate files for diagnostics.")
    parser.add_argument("--checkpoint-every", type=int, default=250)
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


def critical_terms(entry: dict) -> list[str]:
    delivery = entry.get("delivery") or {}
    context = entry.get("context") or {}
    terms = []
    for source in (
        delivery.get("focusWords") or [],
        delivery.get("pivotWords") or [],
        context.get("criticalTerms") or [],
    ):
        for term in source:
            if term and term not in terms:
                terms.append(term)
    if entry.get("speaker") in entry.get("text", ""):
        terms.append(entry["speaker"])
    return terms


def text_validation(entry: dict, hypothesis: str, model_name: str, metadata: dict | None = None) -> dict:
    reference = entry["text"]
    normalized_reference = normalize_transcript(reference)
    normalized_hypothesis = normalize_transcript(hypothesis)
    exact = normalized_reference == normalized_hypothesis
    term_evidence = validate_critical_terms(reference, hypothesis, critical_terms(entry))
    status = "verified_exact" if exact else "manual_review_required"
    if term_evidence["missingTerms"]:
        status = "manual_hard_gate_review"
    return {
        "model": model_name,
        "reference": reference,
        "hypothesis": hypothesis,
        "normalizedReference": normalized_reference,
        "normalizedHypothesis": normalized_hypothesis,
        "cer": round(character_error_rate(reference, hypothesis), 4),
        "exactMatch": exact,
        "editOperations": transcript_edit_operations(reference, hypothesis),
        "criticalTerms": term_evidence,
        "status": status,
        "caveat": "No universal CER threshold is used. Ancient names and terms require listening confirmation.",
        **(metadata or {}),
    }


def load_speaker_encoder(device: str):
    from speechbrain.inference.speaker import EncoderClassifier

    return EncoderClassifier.from_hparams(
        source=str(SPEAKER_MODEL_ROOT),
        savedir=str(SPEAKER_RUNTIME_ROOT),
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


def load_identity_reference_embeddings(encoder, cards: list[dict]):
    import numpy as np

    cache_root = EMBEDDING_ROOT / "identity-references"
    card_ids: list[str] = []
    embeddings: list[object] = []
    for card in cards:
        reference = ROOT / card["referenceFile"]
        if not reference.is_file():
            continue
        stat = reference.stat()
        reference_version = f"{stat.st_size}-{stat.st_mtime_ns}"
        cache = cache_root / f"{card['id']}-{reference_version}.npy"
        cache.parent.mkdir(parents=True, exist_ok=True)
        if cache.is_file():
            embedding = np.load(cache).astype(np.float32)
        else:
            embedding = encode_speaker(encoder, reference)
            np.save(cache, embedding)
        embedding /= max(float(np.linalg.norm(embedding)), 1e-8)
        card_ids.append(card["id"])
        embeddings.append(embedding)
    matrix = np.vstack(embeddings) if embeddings else np.empty((0, 0), dtype=np.float32)
    return card_ids, matrix, {card_id: index for index, card_id in enumerate(card_ids)}


def load_wavlm_encoder(device: str):
    from transformers import Wav2Vec2FeatureExtractor, WavLMForXVector

    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(str(WAVLM_MODEL), local_files_only=True)
    model = WavLMForXVector.from_pretrained(str(WAVLM_MODEL), local_files_only=True).to(device)
    model.eval()
    return feature_extractor, model


def encode_wavlm(bundle, path: Path, device: str):
    import librosa
    import numpy as np
    import soundfile as sf
    import torch

    feature_extractor, model = bundle
    waveform, sample_rate = sf.read(path, dtype="float32")
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)
    if sample_rate != 16000:
        waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)
    inputs = feature_extractor(waveform, sampling_rate=16000, return_tensors="pt")
    inputs = {name: value.to(device) for name, value in inputs.items()}
    with torch.inference_mode():
        embedding = model(**inputs).embeddings.squeeze(0)
        embedding = torch.nn.functional.normalize(embedding, dim=-1)
    return embedding.detach().cpu().numpy().astype(np.float32)


def load_emotion_model(device: str):
    try:
        from funasr import AutoModel
    except ImportError as error:
        raise RuntimeError("--emotion requires funasr; install voice-evaluation-requirements.txt") from error
    return AutoModel(model=str(EMOTION_MODEL), hub="ms", device=device, disable_update=True)


def classify_emotion(model, path: Path, expected: str) -> dict:
    result = model.generate(
        input=str(path), batch_size=1, granularity="utterance", extract_embedding=False,
    )
    record = result[0] if result else {}
    raw_labels = [str(label).lower() for label in record.get("labels", [])]
    labels = [canonical_emotion_label(label) for label in raw_labels]
    scores = [float(score) for score in record.get("scores", [])]
    ranked = sorted(zip(labels, scores), key=lambda item: item[1], reverse=True)
    expected_labels = sorted(EMOTION_EXPECTATIONS.get(expected, set()))
    top_label = ranked[0][0] if ranked else "unknown"
    return {
        "model": str(EMOTION_MODEL),
        "targetContextState": expected,
        "acceptedCoarseLabels": expected_labels,
        "rankedLabels": [{"label": label, "score": round(score, 5)} for label, score in ranked],
        "topLabel": top_label,
        "status": "coarse_consistent" if top_label in expected_labels else "manual_context_review",
        "caveat": "A coarse utterance emotion label cannot verify dramatic intent or state transition.",
    }


def canonical_emotion_label(label: str) -> str:
    value = str(label or "").strip().lower()
    if "/" in value:
        left, right = value.rsplit("/", 1)
        if right:
            return right
        value = left
    return EMOTION_LABEL_ALIASES.get(value, value)


def normalize_emotion_evidence(evidence: dict, expected: str) -> dict:
    if not evidence or evidence.get("status") == "not_run":
        return evidence
    ranked = evidence.get("rankedLabels") or []
    for item in ranked:
        item["label"] = canonical_emotion_label(item.get("label", ""))
    ranked.sort(key=lambda item: float(item.get("score", 0)), reverse=True)
    top_label = canonical_emotion_label(evidence.get("topLabel") or (ranked[0]["label"] if ranked else "unknown"))
    expected_labels = sorted(EMOTION_EXPECTATIONS.get(expected, set()))
    evidence["topLabel"] = top_label
    evidence["acceptedCoarseLabels"] = expected_labels
    evidence["status"] = "coarse_consistent" if top_label in expected_labels else "manual_context_review"
    return evidence


def load_demographic_model(device: str):
    import torch
    import torch.nn as nn
    from transformers import Wav2Vec2Model, Wav2Vec2PreTrainedModel, Wav2Vec2Processor

    class ModelHead(nn.Module):
        def __init__(self, config, labels: int):
            super().__init__()
            self.dense = nn.Linear(config.hidden_size, config.hidden_size)
            self.dropout = nn.Dropout(config.final_dropout)
            self.out_proj = nn.Linear(config.hidden_size, labels)

        def forward(self, features):
            value = self.dropout(features)
            value = torch.tanh(self.dense(value))
            return self.out_proj(self.dropout(value))

    class AgeGenderModel(Wav2Vec2PreTrainedModel):
        def __init__(self, config):
            super().__init__(config)
            self.wav2vec2 = Wav2Vec2Model(config)
            self.age = ModelHead(config, 1)
            self.gender = ModelHead(config, 3)
            self.post_init()

        def forward(self, input_values):
            hidden = self.wav2vec2(input_values)[0].mean(dim=1)
            return self.age(hidden), torch.softmax(self.gender(hidden), dim=1)

    processor = Wav2Vec2Processor.from_pretrained(str(DEMOGRAPHIC_MODEL), local_files_only=True)
    model = AgeGenderModel.from_pretrained(str(DEMOGRAPHIC_MODEL), local_files_only=True).to(device)
    model.eval()
    return processor, model


def classify_demographics(bundle, path: Path, card: dict, device: str) -> dict:
    import librosa
    import soundfile as sf
    import torch

    processor, model = bundle
    waveform, sample_rate = sf.read(path, dtype="float32")
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)
    if sample_rate != 16000:
        waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)
    values = processor(waveform, sampling_rate=16000)["input_values"][0]
    values = torch.from_numpy(values).reshape(1, -1).to(device)
    with torch.inference_mode():
        age, probabilities = model(values)
    predicted_age = float(age.squeeze().detach().cpu()) * 100.0
    probability_values = probabilities.squeeze().detach().cpu().tolist()
    labels = ("female", "male", "child")
    probability_map = {label: round(float(value), 5) for label, value in zip(labels, probability_values)}
    top_label = max(probability_map, key=probability_map.get)
    expected_gender = card.get("gender")
    age_reference = AGE_BAND_REFERENCES.get(card.get("ageBand"))
    alerts = []
    if expected_gender in ("male", "female") and top_label != expected_gender:
        alerts.append("possible_gender_mismatch")
    if age_reference and not age_reference[0] <= predicted_age <= age_reference[1]:
        alerts.append("possible_age_mismatch")
    return {
        "model": str(DEMOGRAPHIC_MODEL),
        "license": "CC-BY-NC-SA-4.0; research evaluation only, never shipped or used as a release gate",
        "predictedAgeYears": round(predicted_age, 2),
        "classProbabilities": probability_map,
        "topClass": top_label,
        "expectedGender": expected_gender,
        "expectedAgeBand": card.get("ageBand"),
        "softAlerts": alerts,
        "status": "soft_alert" if alerts else "no_soft_alert",
        "caveat": "Age/gender inference degrades under strong emotion and is never a hard gate.",
    }


def cosine(left, right) -> float:
    import numpy as np

    return float(np.dot(left, right) / max(np.linalg.norm(left) * np.linalg.norm(right), 1e-8))


def load_saved_embedding(candidate: dict, field: str):
    import numpy as np

    metadata = candidate.get(field) or {}
    relative = metadata.get("file")
    if not relative:
        return None
    path = (ROOT / relative).resolve()
    if ROOT.resolve() not in path.parents or not path.is_file():
        return None
    return np.load(path)


def add_cross_sentence_identity_evidence(index: dict, field: str, label: str, cache: dict) -> None:
    import numpy as np

    records = []
    for entry in index["entries"]:
        for candidate in entry.get("candidates", []):
            key = (entry["entryId"], int(candidate["candidate"]))
            embedding = cache.get(key)
            if embedding is None:
                embedding = load_saved_embedding(candidate, field)
            if embedding is not None:
                records.append((entry, candidate, embedding))
    if not records:
        return
    matrix = np.vstack([item[2] for item in records]).astype(np.float32)
    matrix /= np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-8)
    similarities = matrix @ matrix.T
    speakers = np.asarray([item[0]["speaker"] for item in records], dtype=object)
    entry_ids = np.asarray([item[0]["entryId"] for item in records], dtype=object)
    for row, (entry, candidate, _) in enumerate(records):
        same_mask = (speakers == entry["speaker"]) & (entry_ids != entry["entryId"])
        different_mask = speakers != entry["speaker"]
        same = similarities[row, same_mask]
        different = similarities[row, different_mask]
        evidence = candidate.setdefault("identityEvidence", {})
        if same.size and different.size:
            same_mean = float(np.mean(same))
            nearest_other = float(np.max(different))
            evidence[label] = {
                "withinSpeakerCrossTextMean": round(same_mean, 4),
                "withinSpeakerCrossTextMinimum": round(float(np.min(same)), 4),
                "nearestOtherSpeakerSimilarity": round(nearest_other, 4),
                "unCalibratedSeparationMargin": round(same_mean - nearest_other, 4),
                "status": "requires_project_calibration",
            }
        else:
            evidence[label] = {
                "status": "insufficient_cross_sentence_or_cross_speaker_samples",
            }


def attach_evidence_tracks(entry: dict, candidate: dict, card: dict) -> None:
    analysis = candidate["analysis"]
    text = candidate.get("textValidation") or {"status": "not_run"}
    identity = candidate.get("identityEvidence") or {}
    emotion = normalize_emotion_evidence(
        candidate.get("emotionEvidence") or {"status": "not_run"},
        entry.get("delivery", {}).get("emotion", ""),
    )
    demographics = candidate.get("demographicEvidence") or {"status": "not_run"}
    ecapa = identity.get("ecapaTdnn") or {}
    wavlm = identity.get("wavlmXVector") or {}
    reference_retrieval = identity.get("identityReferenceRetrieval") or {}
    ecapa_margin = ecapa.get("unCalibratedSeparationMargin")
    wavlm_margin = wavlm.get("unCalibratedSeparationMargin")
    if ecapa_margin is not None and wavlm_margin is not None:
        directional_agreement = (ecapa_margin >= 0) == (wavlm_margin >= 0)
        dual_model = {
            "status": "uncalibrated_direction_agreement" if directional_agreement else "uncalibrated_direction_conflict",
            "directionalAgreement": directional_agreement,
            "caveat": "Margin direction is diagnostic only; both models still require project calibration.",
        }
    else:
        dual_model = {"status": "insufficient_dual_model_evidence"}
    delivery = entry.get("delivery") or {}
    state = entry.get("context", {}).get("performanceState") or {}
    candidate["evidenceTracks"] = {
        "content": {
            "status": text.get("status", "not_run"),
            "cer": text.get("cer"),
            "criticalTerms": text.get("criticalTerms", {}),
            "hardGateRule": "Any confirmed missing or wrong line/name/term blocks release.",
        },
        "identity": {
            "status": (
                "identity_drift_hard_review" if reference_retrieval.get("status") == "identity_drift_hard_review"
                else "requires_project_calibration" if identity else "not_run"
            ),
            "models": identity,
            "dualModelComparison": dual_model,
            "approvedAnchorAvailable": bool(entry.get("approvedAnchorCandidate")),
            "hardGateRule": "A confirmed wrong speaker blocks release; uncalibrated similarity never passes it.",
        },
        "expression": {
            "status": emotion.get("status", "not_run"),
            "targetEmotion": delivery.get("emotion"),
            "emotionBefore": delivery.get("emotionBefore") or state.get("emotionBefore"),
            "emotionAfter": delivery.get("emotionAfter") or state.get("emotionAfter"),
            "pivotWords": delivery.get("pivotWords") or state.get("pivotWords") or [],
            "focusWords": delivery.get("focusWords") or state.get("focusWords") or [],
            "coarseModelEvidence": emotion,
            "transitionReview": "requires_time_aligned_or_human_review",
            "hardGateRule": "Only a human-confirmed opposite emotional direction blocks release.",
        },
        "demographics": {
            "status": demographics.get("status", "not_run"),
            "expectedGender": card.get("gender"),
            "expectedAgeBand": card.get("ageBand"),
            "modelEvidence": demographics,
            "gatePolicy": "soft_alert_only",
        },
        "quality": {
            "status": "pass" if analysis["waveformGate"] and not analysis["broadcastCadence"]["hardReject"] else "fail",
            "waveformGate": analysis["waveformGate"],
            "qualityScore": analysis["qualityScore"],
            "paceScore": analysis["speechTiming"]["paceScore"],
            "pauseScore": analysis["pauseStructure"]["pauseScore"],
            "energyScore": analysis["energy"]["energyScore"],
            "broadcastCadence": analysis["broadcastCadence"],
            "pitchAlert": analysis["pitch"]["warning"],
            "gatePolicy": "Broken audio and high-confidence broadcast cadence are automatic hard failures.",
        },
        "human": {
            "status": "pending_blind_context_review",
            "protocol": "P.808-style blind candidate comparison plus dialogue-pair/full-scene review",
        },
    }


def review_priority(candidate: dict) -> tuple[str, list[str]]:
    reasons = []
    tracks = candidate.get("evidenceTracks") or {}
    content = tracks.get("content") or {}
    if (tracks.get("quality") or {}).get("status") == "fail":
        reasons.append("broken_audio")
    if (tracks.get("quality") or {}).get("broadcastCadence", {}).get("hardReject"):
        reasons.append("broadcast_cadence_hard_reject")
    if content.get("status") == "manual_hard_gate_review":
        reasons.append("critical_term_mismatch")
    if (tracks.get("demographics") or {}).get("status") == "soft_alert":
        reasons.append("demographic_soft_alert")
    if (tracks.get("expression") or {}).get("status") == "manual_context_review":
        reasons.append("coarse_emotion_conflict")
    if (tracks.get("identity") or {}).get("dualModelComparison", {}).get("status") == "uncalibrated_direction_conflict":
        reasons.append("speaker_model_direction_conflict")
    if (tracks.get("identity") or {}).get("status") == "identity_drift_hard_review":
        reasons.append("identity_reference_not_ranked_first")
    if reasons:
        return "high", reasons
    if content.get("status") == "manual_review_required":
        reasons.append("asr_not_exact")
    if (tracks.get("quality") or {}).get("pitchAlert"):
        reasons.append("pitch_soft_alert")
    if reasons:
        return "medium", reasons
    return "normal", ["blind_context_review_pending"]


def write_report(index: dict, summary: dict) -> None:
    lines = [
        "# 东周角色配音论文式分轨验收报告",
        "",
        f"生成时间：{summary['evaluatedAt']}",
        "",
        "> 本报告不设置总分放行线。内容、身份、表达、人口属性、音质和人工语境评审彼此独立。",
        "",
        "## 总览",
        "",
        f"- 台词：{summary['entries']} 条",
        f"- 候选：{summary['candidatesProcessed']} 个",
        f"- 高优先复核：{summary['reviewQueue'].get('high', 0)} 个",
        f"- 中优先复核：{summary['reviewQueue'].get('medium', 0)} 个",
        f"- 已批准角色锚点：{summary['approvedAnchors']} 个",
        "",
        "## 逐句证据",
        "",
    ]
    for entry in index["entries"]:
        lines.extend([f"### {entry['speaker']}：{entry['text']}", ""])
        delivery = entry.get("delivery") or {}
        lines.append(
            f"目标：`{delivery.get('emotion', '未标注')}`；状态："
            f"`{delivery.get('emotionBefore', '未标注')}` -> `{delivery.get('emotionAfter', '未标注')}`。"
        )
        lines.append("")
        for candidate in sorted(entry.get("candidates", []), key=lambda item: int(item["candidate"])):
            priority, reasons = review_priority(candidate)
            tracks = candidate.get("evidenceTracks") or {}
            lines.append(
                f"- 候选 {candidate['candidate']} | 优先级 `{priority}` | "
                f"内容 `{tracks.get('content', {}).get('status')}` | "
                f"身份 `{tracks.get('identity', {}).get('status')}` | "
                f"表达 `{tracks.get('expression', {}).get('status')}` | "
                f"人口属性 `{tracks.get('demographics', {}).get('status')}` | "
                f"音质 `{tracks.get('quality', {}).get('status')}` | 原因：{', '.join(reasons)}"
            )
        lines.append("")
    lines.extend([
        "## 放行结论",
        "",
        "当前没有人工盲听记录，也没有本项目标定的声纹阈值，因此所有候选保持隔离，不能进入游戏正式资源。",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


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
    index_path = Path(args.index).resolve()
    if ROOT.resolve() not in index_path.parents or not index_path.is_file():
        raise RuntimeError(f"Unsafe or missing candidate index: {index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("schemaVersion") not in (1, 2, 3):
        raise RuntimeError("Unsupported candidate index schema")
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    reviews = load_reviews()
    anchors = approved_anchors(reviews)
    reviewed = {(item["entryId"], int(item["candidate"])): item for item in reviews}
    selected_entry_ids = {item.strip() for item in args.entry_ids.split(",") if item.strip()}
    if args.entry_id_file:
        raw_entry_ids = args.entry_id_file.read_text(encoding="utf-8")
        selected_entry_ids.update(
            item.strip() for item in raw_entry_ids.replace(",", "\n").splitlines() if item.strip()
        )
    if selected_entry_ids:
        known_entry_ids = {entry["entryId"] for entry in index["entries"]}
        missing_entry_ids = sorted(selected_entry_ids - known_entry_ids)
        if missing_entry_ids:
            raise RuntimeError(f"Unknown entry IDs: {', '.join(missing_entry_ids)}")

    asr = load_asr(args.asr_model, args.device) if args.asr else None
    encoder = load_speaker_encoder(args.device) if args.speaker_embeddings else None
    wavlm = load_wavlm_encoder(args.device) if args.wavlm_embeddings else None
    emotion_model = load_emotion_model(args.device) if args.emotion else None
    demographic_model = load_demographic_model(args.device) if args.research_demographics else None
    embedding_cache: dict[tuple[str, int], object] = {}
    wavlm_cache: dict[tuple[str, int], object] = {}
    processed = 0
    warnings = defaultdict(int)
    reference_card_ids, reference_matrix, reference_positions = (
        load_identity_reference_embeddings(encoder, cards) if encoder is not None else ([], None, {})
    )

    for entry in index["entries"]:
        if selected_entry_ids and entry["entryId"] not in selected_entry_ids:
            continue
        card = cards_by_id[entry["voiceCardId"]]
        entry.setdefault("alerts", [])
        entry.setdefault("gates", {})
        entry["gates"].pop("pitchSanity", None)
        entry["gates"].pop("gender", None)
        entry["gates"].setdefault("calibration", "pending_project_calibration")
        entry["gates"].setdefault("humanReview", "pending_blind_review")
        entry["gates"].setdefault("broadcastCadence", "pending_generation")
        for candidate in entry.get("candidates", []):
            if args.limit and processed >= args.limit:
                break
            path = safe_candidate_path(candidate)
            analysis = candidate.get("analysis")
            if not analysis:
                import soundfile as sf

                waveform, sample_rate = sf.read(path, dtype="float32")
                analysis = analyze_audio(waveform, sample_rate, entry["text"], entry["delivery"], card)
                candidate["analysis"] = analysis
            base_score = (
                0.35 * analysis["qualityScore"]
                + 0.25 * analysis["speechTiming"]["paceScore"]
                + 0.20 * analysis["pauseStructure"]["pauseScore"]
                + 0.20 * analysis["energy"]["energyScore"]
            )
            cadence = analysis["broadcastCadence"]
            candidate["automaticAcousticTriageScore"] = round(
                base_score * (0.0 if cadence["hardReject"] else 1.0 - 0.25 * cadence["riskScore"]), 4,
            )
            candidate["automaticRankScore"] = candidate["automaticAcousticTriageScore"]
            if analysis["pitch"]["warning"]:
                warnings["pitch_outside_broad_reference"] += 1
            if cadence["hardReject"]:
                warnings["broadcast_cadence_hard_reject"] += 1
            elif cadence["riskScore"] >= 0.65:
                warnings["broadcast_cadence_review"] += 1
            if asr is not None:
                hypothesis, metadata = transcribe(asr, path)
                candidate["textValidation"] = text_validation(
                    entry, hypothesis, f"faster-whisper/{args.asr_model}", metadata,
                )
            elif candidate.get("textValidation", {}).get("hypothesis") is not None:
                previous_validation = candidate["textValidation"]
                candidate["textValidation"] = text_validation(
                    entry,
                    previous_validation["hypothesis"],
                    previous_validation.get("model", "existing_asr_result"),
                    {
                        name: previous_validation[name]
                        for name in ("language", "languageProbability")
                        if name in previous_validation
                    },
                )
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
                target_position = reference_positions.get(card["id"])
                if target_position is not None and len(reference_card_ids) > 1:
                    import numpy as np

                    similarities = reference_matrix @ embedding
                    target_similarity = float(similarities[target_position])
                    impostor_scores = similarities.copy()
                    impostor_scores[target_position] = -2.0
                    best_impostor_position = int(np.argmax(impostor_scores))
                    margin = target_similarity - float(impostor_scores[best_impostor_position])
                    candidate["speakerEmbedding"]["identityReferenceRetrieval"] = {
                        "targetVoiceCardId": card["id"],
                        "targetSimilarity": round(target_similarity, 4),
                        "bestImpostorVoiceCardId": reference_card_ids[best_impostor_position],
                        "bestImpostorSimilarity": round(float(impostor_scores[best_impostor_position]), 4),
                        "separationMargin": round(margin, 4),
                        "status": "target_ranked_first" if margin >= 0 else "identity_drift_hard_review",
                        "caveat": "Relative retrieval is a drift screen, not a calibrated identity acceptance threshold.",
                    }
                    candidate.setdefault("identityEvidence", {})["identityReferenceRetrieval"] = candidate["speakerEmbedding"]["identityReferenceRetrieval"]
            if wavlm is not None:
                embedding = encode_wavlm(wavlm, path, args.device)
                key = (entry["entryId"], int(candidate["candidate"]))
                wavlm_cache[key] = embedding
                embedding_path = EMBEDDING_ROOT / "wavlm" / entry["entryId"] / f"candidate-{candidate['candidate']}.npy"
                embedding_path.parent.mkdir(parents=True, exist_ok=True)
                import numpy as np

                np.save(embedding_path, embedding)
                candidate["wavlmSpeakerEmbedding"] = {
                    "model": str(WAVLM_MODEL),
                    "dimension": int(embedding.shape[0]),
                    "file": str(embedding_path.relative_to(ROOT)).replace("\\", "/"),
                    "thresholdPolicy": "project_calibration_required",
                }
            if emotion_model is not None:
                candidate["emotionEvidence"] = classify_emotion(
                    emotion_model, path, entry.get("delivery", {}).get("emotion", ""),
                )
            if demographic_model is not None:
                candidate["demographicEvidence"] = classify_demographics(
                    demographic_model, path, card, args.device,
                )
            processed += 1
            if args.checkpoint_every > 0 and processed % args.checkpoint_every == 0:
                index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"[evaluation {processed}] checkpoint={index_path}", flush=True)
        entry["candidates"].sort(key=lambda item: item["automaticAcousticTriageScore"], reverse=True)
        if entry["candidates"]:
            entry["gates"]["waveform"] = "pending_candidate_selection"
            entry["gates"]["prosody"] = "pending_contextual_panel_review"
            entry["gates"]["broadcastCadence"] = (
                "fail_all_candidates" if all(item["analysis"]["broadcastCadence"]["hardReject"] for item in entry["candidates"])
                else "pending_contextual_panel_review"
            )
            entry["alerts"] = sorted({
                alert
                for item in entry["candidates"]
                for alert in (
                    (["pitch_outside_broad_reference"] if item["analysis"]["pitch"]["warning"] else [])
                    + (["broadcast_cadence_review"] if item["analysis"]["broadcastCadence"]["riskScore"] >= 0.65 else [])
                )
            })

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
    add_cross_sentence_identity_evidence(index, "speakerEmbedding", "ecapaTdnn", embedding_cache)
    add_cross_sentence_identity_evidence(index, "wavlmSpeakerEmbedding", "wavlmXVector", wavlm_cache)

    review_counts = defaultdict(int)
    for entry in index["entries"]:
        card = cards_by_id[entry["voiceCardId"]]
        for candidate in entry.get("candidates", []):
            attach_evidence_tracks(entry, candidate, card)
            priority, reasons = review_priority(candidate)
            candidate["reviewQueue"] = {"priority": priority, "reasons": reasons}
            review_counts[priority] += 1

    index["schemaVersion"] = 3
    index["evaluatedAt"] = datetime.now(timezone.utc).isoformat()
    if not isinstance(index.get("policy"), dict):
        index["policy"] = {"legacyPolicy": str(index.get("policy") or "")}
    index["policy"]["pitch"] = "Median F0 is an alert only and is excluded from rank and promotion gates."
    index["policy"]["identity"] = "Cross-sentence identity requires an approved anchor, at least two distinct texts, and project-calibrated thresholds."
    index["policy"]["content"] = "No universal CER threshold is used; confirmed missing or wrong content and critical terms are hard failures."
    index["policy"]["expression"] = "Coarse emotion models provide evidence only; dialogue-pair and full-scene human review decide contextual acting."
    index["policy"]["demographics"] = "Age/gender inference is a research-only soft alert and never a release gate."
    index["policy"]["automaticTriage"] = "The acoustic triage score orders listening work only and is never a quality or release score."
    index["policy"]["broadcastCadence"] = "High-confidence equal-timing cadence is an automatic rejection; borderline cadence still requires full-scene listening."
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    all_candidates = [candidate for entry in index["entries"] for candidate in entry.get("candidates", [])]
    warnings = defaultdict(int)
    for candidate in all_candidates:
        analysis = candidate.get("analysis") or {}
        pitch = analysis.get("pitch") or {}
        cadence = analysis.get("broadcastCadence") or {}
        if pitch.get("warning"):
            warnings["pitch_outside_broad_reference"] += 1
        if cadence.get("hardReject"):
            warnings["broadcast_cadence_hard_reject"] += 1
        elif float(cadence.get("riskScore") or 0) >= 0.65:
            warnings["broadcast_cadence_review"] += 1
    evidence_coverage = {
        "asr": sum(bool(item.get("textValidation")) for item in all_candidates),
        "ecapaTdnn": sum(bool(item.get("speakerEmbedding")) for item in all_candidates),
        "wavlmXVector": sum(bool(item.get("wavlmSpeakerEmbedding")) for item in all_candidates),
        "emotion2vec": sum(bool(item.get("emotionEvidence")) for item in all_candidates),
        "researchDemographics": sum(bool(item.get("demographicEvidence")) for item in all_candidates),
    }
    full_coverage = len(all_candidates)
    summary = {
        "schemaVersion": 2,
        "evaluatedAt": index["evaluatedAt"],
        "entries": len(index["entries"]),
        "candidatesProcessed": processed,
        "asrEnabled": evidence_coverage["asr"] == full_coverage,
        "speakerEmbeddingsEnabled": evidence_coverage["ecapaTdnn"] == full_coverage,
        "wavlmEmbeddingsEnabled": evidence_coverage["wavlmXVector"] == full_coverage,
        "emotionEnabled": evidence_coverage["emotion2vec"] == full_coverage,
        "researchDemographicsEnabled": evidence_coverage["researchDemographics"] == full_coverage,
        "runOptions": {
            "asr": args.asr,
            "ecapaTdnn": args.speaker_embeddings,
            "wavlmXVector": args.wavlm_embeddings,
            "emotion2vec": args.emotion,
            "researchDemographics": args.research_demographics,
        },
        "evidenceCoverage": evidence_coverage,
        "approvedAnchors": len(anchors),
        "warnings": dict(warnings),
        "reviewQueue": dict(review_counts),
        "report": str(REPORT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "promotionPolicy": "No candidate can ship before calibrated identity and panel blind-review gates pass.",
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(index, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
