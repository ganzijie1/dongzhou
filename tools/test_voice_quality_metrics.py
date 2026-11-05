#!/usr/bin/env python3
"""Regression tests for contextual dialogue voice metrics."""

from __future__ import annotations

import math
import unittest

import numpy as np

from voice_quality_metrics import (
    analyze_audio,
    character_error_rate,
    expected_internal_boundaries,
    merge_intervals,
    normalize_transcript,
    spoken_character_count,
    transcript_edit_operations,
    validate_critical_terms,
)


class VoiceQualityMetricsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_rate = 24000
        self.card = {"gender": "male", "ageBand": "mature"}
        self.delivery = {"pace": 1.0, "intensity": 0.5, "pauseStrength": 0.5}

    def tone(self, seconds: float, frequency: float = 110.0, amplitude: float = 0.08) -> np.ndarray:
        t = np.arange(int(seconds * self.sample_rate), dtype=np.float32) / self.sample_rate
        envelope = np.minimum(1.0, np.minimum(t * 30.0, (seconds - t) * 30.0))
        return (amplitude * envelope * np.sin(2.0 * math.pi * frequency * t)).astype(np.float32)

    def test_text_normalization_and_cer(self) -> None:
        self.assertEqual(normalize_transcript("周王，白矢在此！"), "周王白矢在此")
        self.assertEqual(normalize_transcript("王駕暫緩"), "王驾暂缓")
        self.assertEqual(spoken_character_count("周王，白矢在此！"), 6)
        self.assertEqual(expected_internal_boundaries("月属阴、日属阳。阴盛阳衰。"), 2)
        self.assertAlmostEqual(character_error_rate("周王白矢在此", "周王白石在此"), 1 / 6)

    def test_merge_short_gaps(self) -> None:
        intervals = np.array([[0, 1000], [1100, 2000], [5000, 6000]])
        self.assertEqual(merge_intervals(intervals, 1000), [(0, 2000), (5000, 6000)])

    def test_transcript_evidence_preserves_named_term_errors(self) -> None:
        operations = transcript_edit_operations("周王，白矢在此！", "周王白石在此")
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0]["type"], "substitute")
        terms = validate_critical_terms(
            "赤弓在手，白矢已发。周王，偿还血债！",
            "赤弓在手，白石已发。周王，偿还血债！",
            ["白矢", "周王", "不在原文"],
        )
        self.assertEqual(terms["terms"], ["白矢", "周王"])
        self.assertEqual(terms["missingTerms"], ["白矢"])
        self.assertEqual(terms["status"], "manual_hard_gate_review")

    def test_pause_and_articulation_are_separate(self) -> None:
        audio = np.concatenate([
            self.tone(0.8),
            np.zeros(int(0.35 * self.sample_rate), dtype=np.float32),
            self.tone(0.8),
        ])
        analysis = analyze_audio(audio, self.sample_rate, "王师暂缓，速返镐京！", self.delivery, self.card)
        pauses = analysis["pauseStructure"]
        timing = analysis["speechTiming"]
        self.assertEqual(pauses["internalPauseCount"], 1)
        self.assertGreater(pauses["internalPauseDuration"], 0.25)
        self.assertGreater(timing["articulationRateCharsPerSecond"], timing["speechRateCharsPerSecond"])
        self.assertTrue(analysis["waveformGate"])

    def test_pitch_is_an_alert_not_a_gate(self) -> None:
        audio = self.tone(1.2, frequency=250.0)
        analysis = analyze_audio(audio, self.sample_rate, "此事不可泄露。", self.delivery, self.card)
        self.assertTrue(analysis["pitch"]["warning"])
        self.assertNotIn("pitchGate", analysis)
        self.assertIn("classifier", analysis["pitch"]["caveat"])


if __name__ == "__main__":
    unittest.main()
