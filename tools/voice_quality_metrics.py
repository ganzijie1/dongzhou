#!/usr/bin/env python3
"""Deterministic speech metrics used by the contextual voice review pipeline."""

from __future__ import annotations

import math
import re
from typing import Iterable


PUNCTUATION_RE = re.compile(r"[。！？；：，、,.!?;:]")
TRAILING_PUNCTUATION_RE = re.compile(r"[。！？；：，、,.!?;:]+$")
_OPENCC = None


def spoken_character_count(text: str) -> int:
    return len(re.sub(r"[\s。！？；：，、,.!?;:“”‘’（）()《》〈〉【】\[\]…—-]", "", text or ""))


def expected_internal_boundaries(text: str) -> int:
    clean = TRAILING_PUNCTUATION_RE.sub("", (text or "").strip())
    return len(PUNCTUATION_RE.findall(clean))


def pitch_sanity_range(card: dict) -> tuple[float, float]:
    if card.get("gender") == "female":
        return (135.0, 285.0)
    return {
        "child": (120.0, 260.0),
        "young_adult": (75.0, 205.0),
        "adult": (70.0, 190.0),
        "mature": (65.0, 175.0),
        "late_middle": (60.0, 165.0),
        "elder": (60.0, 165.0),
    }.get(card.get("ageBand"), (65.0, 190.0))


def merge_intervals(intervals, sample_rate: int, minimum_gap_seconds: float = 0.12) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    minimum_gap = int(sample_rate * minimum_gap_seconds)
    for start, end in intervals:
        start = int(start)
        end = int(end)
        if not merged or start - merged[-1][1] >= minimum_gap:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def interval_duration(intervals: Iterable[tuple[int, int]], sample_rate: int) -> float:
    return sum(end - start for start, end in intervals) / sample_rate


def _coefficient_of_variation(values) -> float:
    import numpy as np

    array = np.asarray(values, dtype=np.float64)
    if len(array) < 2 or float(np.mean(array)) <= 1e-8:
        return 1.0
    return float(np.std(array) / np.mean(array))


def _frame_mask(frame_times, intervals: list[tuple[int, int]], sample_rate: int):
    import numpy as np

    mask = np.zeros(len(frame_times), dtype=bool)
    for start, end in intervals:
        mask |= (frame_times >= start / sample_rate) & (frame_times <= end / sample_rate)
    return mask


def _breath_proxy_events(audio, sample_rate: int, speech_intervals: list[tuple[int, int]]) -> list[dict]:
    """Find breath-like noise between speech regions; this is deliberately not a classifier."""
    import librosa
    import numpy as np

    events: list[dict] = []
    for (_, left_end), (right_start, _) in zip(speech_intervals, speech_intervals[1:]):
        duration = (right_start - left_end) / sample_rate
        if not 0.10 <= duration <= 0.80:
            continue
        segment = audio[left_end:right_start]
        if len(segment) < 64:
            continue
        rms = float(np.sqrt(np.mean(np.square(segment))))
        if rms < 0.00035:
            continue
        centroid = float(np.median(librosa.feature.spectral_centroid(y=segment, sr=sample_rate)))
        flatness = float(np.median(librosa.feature.spectral_flatness(y=segment)))
        if centroid >= 900.0 and flatness >= 0.01:
            events.append({
                "start": round(left_end / sample_rate, 3),
                "end": round(right_start / sample_rate, 3),
                "duration": round(duration, 3),
                "rms": round(rms, 6),
                "spectralCentroidHz": round(centroid, 2),
                "spectralFlatness": round(flatness, 6),
            })
    return events


def analyze_audio(waveform, sample_rate: int, text: str, delivery: dict, card: dict) -> dict:
    import librosa
    import numpy as np

    audio = np.asarray(waveform, dtype=np.float32).reshape(-1)
    duration = len(audio) / sample_rate
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    rms = float(np.sqrt(np.mean(np.square(audio)))) if len(audio) else 0.0
    clipping = float(np.mean(np.abs(audio) >= 0.995)) if len(audio) else 1.0
    raw_silence = float(np.mean(np.abs(audio) < 0.003)) if len(audio) else 1.0

    raw_intervals = librosa.effects.split(audio, top_db=34, frame_length=1024, hop_length=256)
    speech_intervals = merge_intervals(raw_intervals, sample_rate)
    speech_duration = interval_duration(speech_intervals, sample_rate)
    initial_silence = speech_intervals[0][0] / sample_rate if speech_intervals else duration
    final_silence = (len(audio) - speech_intervals[-1][1]) / sample_rate if speech_intervals else duration
    internal_pauses = [
        {
            "start": round(left_end / sample_rate, 3),
            "end": round(right_start / sample_rate, 3),
            "duration": round((right_start - left_end) / sample_rate, 3),
        }
        for (_, left_end), (right_start, _) in zip(speech_intervals, speech_intervals[1:])
    ]
    internal_pause_duration = sum(item["duration"] for item in internal_pauses)
    internal_pause_ratio = internal_pause_duration / max(duration, 0.001)

    character_count = spoken_character_count(text)
    speech_rate = character_count / max(duration, 0.001)
    articulation_rate = character_count / max(speech_duration, 0.001)
    target_speech_rate = 3.6 * float(delivery.get("pace", 1.0))
    pace_error = abs(math.log(max(speech_rate, 0.1) / max(target_speech_rate, 0.1)))
    pace_score = math.exp(-1.8 * pace_error)

    expected_boundaries = expected_internal_boundaries(text)
    pause_strength = float(delivery.get("pauseStrength", 0.4))
    target_pause_ratio = 0.015 + 0.16 * pause_strength
    pause_ratio_error = abs(internal_pause_ratio - target_pause_ratio)
    pause_count_error = abs(len(internal_pauses) - expected_boundaries)
    pause_score = math.exp(-7.0 * pause_ratio_error) * math.exp(-0.22 * pause_count_error)

    hop_length = 256
    frame_length = 1024
    frame_rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
    frame_times = librosa.frames_to_time(np.arange(len(frame_rms)), sr=sample_rate, hop_length=hop_length)
    speech_mask = _frame_mask(frame_times, speech_intervals, sample_rate)
    speech_rms = frame_rms[speech_mask & (frame_rms > 1e-7)]
    if len(speech_rms):
        speech_db = 20.0 * np.log10(speech_rms + 1e-7)
        energy_dynamic_range = float(np.quantile(speech_db, 0.90) - np.quantile(speech_db, 0.10))
        energy_variation = float(np.std(speech_rms) / max(np.mean(speech_rms), 1e-7))
    else:
        energy_dynamic_range = 0.0
        energy_variation = 0.0
    segment_durations = [(end - start) / sample_rate for start, end in speech_intervals]
    segment_rms = [
        float(np.sqrt(np.mean(np.square(audio[start:end]))))
        for start, end in speech_intervals if end > start
    ]
    pause_durations = [item["duration"] for item in internal_pauses]
    duration_regularity = math.exp(-3.2 * _coefficient_of_variation(segment_durations))
    pause_regularity = math.exp(-3.5 * _coefficient_of_variation(pause_durations))
    energy_uniformity = math.exp(-4.0 * _coefficient_of_variation(segment_rms))
    target_dynamic_range = 8.0 + 12.0 * float(delivery.get("intensity", 0.4))
    energy_score = math.exp(-abs(energy_dynamic_range - target_dynamic_range) / 14.0)

    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
    spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0]
    harmonic = librosa.effects.harmonic(audio)
    harmonic_ratio = float(np.sqrt(np.mean(np.square(harmonic))) / max(rms, 1e-6))
    f0, _, _ = librosa.pyin(audio, fmin=55.0, fmax=400.0, sr=sample_rate)
    voiced_f0 = f0[np.isfinite(f0)]
    median_f0 = float(np.median(voiced_f0)) if len(voiced_f0) else 0.0
    f0_p10 = float(np.quantile(voiced_f0, 0.1)) if len(voiced_f0) else 0.0
    f0_p90 = float(np.quantile(voiced_f0, 0.9)) if len(voiced_f0) else 0.0
    terminal_directions: list[int] = []
    for start, end in speech_intervals:
        segment_mask = _frame_mask(frame_times, [(start, end)], sample_rate)
        segment_f0 = f0[segment_mask[:len(f0)]] if len(f0) else np.asarray([])
        segment_f0 = segment_f0[np.isfinite(segment_f0)]
        if len(segment_f0) < 6:
            continue
        edge = max(2, len(segment_f0) // 3)
        delta = float(np.median(segment_f0[-edge:]) - np.median(segment_f0[:edge]))
        terminal_directions.append(-1 if delta < -2.0 else 1 if delta > 2.0 else 0)
    if terminal_directions:
        terminal_uniformity = max(terminal_directions.count(value) for value in (-1, 0, 1)) / len(terminal_directions)
    else:
        terminal_uniformity = 0.0
    cadence_evidence = len(speech_intervals) >= 4 and len(internal_pauses) >= 3
    broadcast_risk = (
        0.35 * duration_regularity
        + 0.25 * pause_regularity
        + 0.20 * energy_uniformity
        + 0.20 * terminal_uniformity
    ) if cadence_evidence else 0.0
    broadcast_hard_reject = cadence_evidence and broadcast_risk >= 0.86
    f0_min, f0_max = pitch_sanity_range(card)
    pitch_warning = not median_f0 or not (f0_min <= median_f0 <= f0_max)

    duration_ok = 0.35 <= duration <= 30.0
    waveform_gate = duration_ok and clipping <= 0.0005 and peak >= 0.015 and rms >= 0.003 and raw_silence <= 0.78
    quality_score = 1.0 if duration_ok else 0.0
    quality_score *= max(0.0, 1.0 - clipping * 100.0)
    if peak < 0.015 or rms < 0.003:
        quality_score *= 0.1
    if raw_silence > 0.78:
        quality_score *= 0.4

    breath_events = _breath_proxy_events(audio, sample_rate, speech_intervals)
    prosody_score = 0.40 * pace_score + 0.30 * pause_score + 0.30 * energy_score
    return {
        "duration": round(duration, 3),
        "peak": round(peak, 6),
        "rms": round(rms, 6),
        "clippingRatio": round(clipping, 7),
        "rawSilenceRatio": round(raw_silence, 5),
        "waveformGate": waveform_gate,
        "qualityScore": round(quality_score, 4),
        "speechTiming": {
            "spokenCharacters": character_count,
            "speechDuration": round(speech_duration, 3),
            "speechRateCharsPerSecond": round(speech_rate, 3),
            "articulationRateCharsPerSecond": round(articulation_rate, 3),
            "targetSpeechRate": round(target_speech_rate, 3),
            "paceScore": round(pace_score, 4),
            "initialSilence": round(initial_silence, 3),
            "finalSilence": round(final_silence, 3),
        },
        "pauseStructure": {
            "speechSegmentCount": len(speech_intervals),
            "internalPauseCount": len(internal_pauses),
            "internalPauseDuration": round(internal_pause_duration, 3),
            "internalPauseRatio": round(internal_pause_ratio, 4),
            "expectedSemanticBoundaries": expected_boundaries,
            "targetPauseRatio": round(target_pause_ratio, 4),
            "pauseScore": round(pause_score, 4),
            "events": internal_pauses,
        },
        "breathProxy": {
            "count": len(breath_events),
            "events": breath_events,
            "reviewStatus": "pending_human_confirmation",
            "caveat": "Energy and spectral heuristics only; these events are not confirmed breaths.",
        },
        "energy": {
            "dynamicRangeDb": round(energy_dynamic_range, 3),
            "targetDynamicRangeDb": round(target_dynamic_range, 3),
            "rmsVariation": round(energy_variation, 4),
            "energyScore": round(energy_score, 4),
        },
        "broadcastCadence": {
            "riskScore": round(broadcast_risk, 4),
            "hardReject": broadcast_hard_reject,
            "evidenceAvailable": cadence_evidence,
            "segmentDurationCv": round(_coefficient_of_variation(segment_durations), 4),
            "pauseDurationCv": round(_coefficient_of_variation(pause_durations), 4),
            "segmentEnergyCv": round(_coefficient_of_variation(segment_rms), 4),
            "terminalDirectionUniformity": round(terminal_uniformity, 4),
            "caveat": "Acoustic cadence gate for repeated equal timing, uniform emphasis and fixed endings; borderline cases still require scene listening.",
        },
        "pitch": {
            "medianF0Hz": round(median_f0, 2),
            "f0P10Hz": round(f0_p10, 2),
            "f0P90Hz": round(f0_p90, 2),
            "broadReferenceRangeHz": [f0_min, f0_max],
            "warning": pitch_warning,
            "caveat": "F0 is an anomaly warning only, never a gender, age, identity, or acting classifier.",
        },
        "voiceQuality": {
            "medianSpectralCentroidHz": round(float(np.median(spectral_centroid)), 2),
            "medianSpectralFlatness": round(float(np.median(spectral_flatness)), 6),
            "harmonicEnergyRatio": round(harmonic_ratio, 4),
            "caveat": "Spectral and harmonic measures are descriptive proxies, not identity or demographic classifiers.",
        },
        "prosodyScore": round(prosody_score, 4),
    }


def normalize_transcript(text: str) -> str:
    global _OPENCC
    clean = (text or "").lower()
    try:
        if _OPENCC is None:
            from opencc import OpenCC

            _OPENCC = OpenCC("t2s")
        clean = _OPENCC.convert(clean)
    except ImportError:
        pass
    return re.sub(r"[^\u3400-\u9fffA-Za-z0-9]", "", clean)


def character_error_rate(reference: str, hypothesis: str) -> float:
    reference = normalize_transcript(reference)
    hypothesis = normalize_transcript(hypothesis)
    if not reference:
        return 0.0 if not hypothesis else 1.0
    previous = list(range(len(hypothesis) + 1))
    for row, ref_char in enumerate(reference, start=1):
        current = [row]
        for column, hyp_char in enumerate(hypothesis, start=1):
            current.append(min(
                current[-1] + 1,
                previous[column] + 1,
                previous[column - 1] + (ref_char != hyp_char),
            ))
        previous = current
    return previous[-1] / len(reference)


def transcript_edit_operations(reference: str, hypothesis: str) -> list[dict]:
    """Return a deterministic character-level alignment for review evidence."""
    reference = normalize_transcript(reference)
    hypothesis = normalize_transcript(hypothesis)
    rows = len(reference) + 1
    columns = len(hypothesis) + 1
    cost = [[0] * columns for _ in range(rows)]
    back = [[""] * columns for _ in range(rows)]
    for row in range(1, rows):
        cost[row][0] = row
        back[row][0] = "delete"
    for column in range(1, columns):
        cost[0][column] = column
        back[0][column] = "insert"
    for row in range(1, rows):
        for column in range(1, columns):
            if reference[row - 1] == hypothesis[column - 1]:
                cost[row][column] = cost[row - 1][column - 1]
                back[row][column] = "equal"
                continue
            choices = (
                (cost[row - 1][column - 1] + 1, "substitute"),
                (cost[row - 1][column] + 1, "delete"),
                (cost[row][column - 1] + 1, "insert"),
            )
            cost[row][column], back[row][column] = min(choices, key=lambda item: (item[0], item[1]))

    operations: list[dict] = []
    row, column = len(reference), len(hypothesis)
    while row or column:
        operation = back[row][column]
        if operation == "equal":
            row -= 1
            column -= 1
            continue
        if operation == "substitute":
            operations.append({
                "type": operation,
                "reference": reference[row - 1],
                "hypothesis": hypothesis[column - 1],
                "referenceIndex": row - 1,
            })
            row -= 1
            column -= 1
        elif operation == "delete":
            operations.append({
                "type": operation,
                "reference": reference[row - 1],
                "hypothesis": "",
                "referenceIndex": row - 1,
            })
            row -= 1
        elif operation == "insert":
            operations.append({
                "type": operation,
                "reference": "",
                "hypothesis": hypothesis[column - 1],
                "referenceIndex": row,
            })
            column -= 1
        else:
            raise RuntimeError("Broken transcript alignment")
    operations.reverse()
    return operations


def validate_critical_terms(reference: str, hypothesis: str, terms: Iterable[str]) -> dict:
    """Check only terms that actually occur in the reference utterance."""
    normalized_reference = normalize_transcript(reference)
    normalized_hypothesis = normalize_transcript(hypothesis)
    try:
        from pypinyin import Style, lazy_pinyin

        hypothesis_pinyin = "".join(lazy_pinyin(
            normalized_hypothesis, style=Style.NORMAL, errors=lambda value: list(value),
        ))
    except ImportError:
        lazy_pinyin = None
        Style = None
        hypothesis_pinyin = ""
    applicable: list[str] = []
    missing: list[str] = []
    phonetic_matches: list[str] = []
    phonetic_near_matches: list[dict] = []
    for raw_term in terms:
        term = normalize_transcript(str(raw_term))
        if len(term) < 2 or term not in normalized_reference or term in applicable:
            continue
        applicable.append(term)
        if term in normalized_hypothesis:
            continue
        term_pinyin = "".join(lazy_pinyin(
            term, style=Style.NORMAL, errors=lambda value: list(value),
        )) if lazy_pinyin is not None else ""
        if term_pinyin and term_pinyin in hypothesis_pinyin:
            phonetic_matches.append(term)
            continue
        best_distance = 1.0
        best_window = ""
        if lazy_pinyin is not None and term_pinyin:
            for width in range(max(1, len(term) - 1), len(term) + 2):
                for start in range(0, max(0, len(normalized_hypothesis) - width) + 1):
                    window = normalized_hypothesis[start:start + width]
                    window_pinyin = "".join(lazy_pinyin(
                        window, style=Style.NORMAL, errors=lambda value: list(value),
                    ))
                    distance = character_error_rate(term_pinyin, window_pinyin)
                    if distance < best_distance:
                        best_distance = distance
                        best_window = window
        if best_window and best_distance <= 0.20:
            phonetic_near_matches.append({
                "term": term, "hypothesisWindow": best_window, "distance": round(best_distance, 4),
            })
        else:
            missing.append(term)
    return {
        "terms": applicable,
        "missingTerms": missing,
        "phoneticMatches": phonetic_matches,
        "phoneticNearMatches": phonetic_near_matches,
        "status": "pass" if not missing else "manual_hard_gate_review",
        "caveat": "Literal or tone-free pinyin ASR matches are supporting evidence; names and archaic terms still require listening confirmation.",
    }
