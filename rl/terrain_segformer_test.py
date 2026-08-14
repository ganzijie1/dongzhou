"""Regression tests for the experimental SegFormer terrain pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import terrain_segformer as seg


def test_class_schema() -> None:
    assert len(seg.CLASS_NAMES) == 10
    assert set(seg.CHAR_TO_CLASS) == set(seg.base.CHAR_NAMES)
    assert seg.CHAR_TO_CLASS["W"] == "barrier"
    assert seg.CHAR_TO_CLASS["P"] == "barrier"


def test_small_component_cleanup() -> None:
    labels = np.zeros((8, 8), dtype=np.int64)
    labels[3, 3] = seg.NAME_TO_ID["water"]
    cleaned = seg.clean_small_components(labels, min_size=2)
    assert cleaned[3, 3] == seg.NAME_TO_ID["open"]


def test_grid_vote_shape_and_review() -> None:
    labels = np.zeros((28, 38), dtype=np.int64)
    labels[:14, :18] = seg.NAME_TO_ID["forest"]
    confidence = np.full(labels.shape, 0.9, dtype=np.float32)
    rows, review = seg.grid_vote(labels, confidence, 19, 14)
    assert len(rows) == 14
    assert all(len(row) == 19 for row in rows)
    assert rows[0][0] == "F"
    assert rows[-1][-1] == "f"
    assert not review


def test_exported_holdout_isolated() -> None:
    manifest_path = seg.DATASET_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    holdouts = [item for item in manifest["maps"] if item["holdout"]]
    assert len(holdouts) == 1
    assert holdouts[0]["asset"] == "m008.png"
    assert all(not item["reviewed"] for item in manifest["maps"])


if __name__ == "__main__":
    tests = [
        test_class_schema,
        test_small_component_cleanup,
        test_grid_vote_shape_and_review,
        test_exported_holdout_isolated,
    ]
    for test in tests:
        test()
    print(f"SegFormer terrain tests passed: {len(tests)}")
