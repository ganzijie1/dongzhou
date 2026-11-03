#!/usr/bin/env python3
"""Deterministic speech metrics used by the contextual voice review pipeline."""

from __future__ import annotations

import math
import re
from typing import Iterable


PUNCTUATION_RE = re.compile(r"[，。！？；：、,.!?;:]")
TRAILING_PUNCTUATION_RE = re.compile(r"[，。！？；：、,.!?;:]+$")
_OPENCC = None


def spoken_character_count(text: str) -> int:
    return len(re.sub(r"[\s，。！？；：、,.!?;:‘’“”\-—…（）()《》〈〉]", "", text or ""))


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
