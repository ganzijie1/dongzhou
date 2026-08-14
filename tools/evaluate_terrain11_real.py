"""Evaluate the synthetic 11-class model on reviewed real Mengde maps."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, f1_score

from terrain_semantic_model import image_cells


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "output/terrain_model/terrain_11_self_evolved.joblib"
OUTPUT = ROOT / "output/terrain_model/terrain_11_real_domain_report.json"
CLASSES = ["f", "g", "F", "m", "W", "C", "e", "P", "~"]


def source_image(manifest: dict) -> Path | None:
    for key in ("map", "source_base"):
        value = manifest.get(key)
        if value:
            path = ROOT / value
            if path.is_file():
                return path
    return None


def scores(y: np.ndarray, prediction: np.ndarray) -> dict:
    report = classification_report(y, prediction, labels=CLASSES, output_dict=True, zero_division=0)
    supported = [c for c in CLASSES if report[c]["support"] > 0]
    return {
        "macro_f1_supported": float(np.mean([report[c]["f1-score"] for c in supported])),
        "minimum_class_f1": float(min(report[c]["f1-score"] for c in supported)),
        "classes": {c: report[c] for c in CLASSES},
        "confusion_matrix": confusion_matrix(y, prediction, labels=CLASSES).tolist(),
    }


def main():
    model = joblib.load(MODEL)["classifier"]
    truths, predictions, per_map = [], [], []
    for path in sorted((ROOT / "assets/lzc/map_sources").glob("m*_manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        rows = manifest.get("terrain_rows", [])
        grid = manifest.get("grid", [])
        image_path = source_image(manifest)
        if len(grid) != 2 or len(rows) != grid[1] or image_path is None:
            continue
        truth = np.asarray(list("".join(rows)))
        eligible = np.isin(truth, CLASSES)
        if not eligible.any():
            continue
        image = Image.open(image_path).convert("RGB")
        prediction = model.predict(image_cells(image, int(grid[0]), int(grid[1])))
        local_truth, local_prediction = truth[eligible], prediction[eligible]
        truths.append(local_truth); predictions.append(local_prediction)
        metric = scores(local_truth, local_prediction)
        per_map.append({
            "manifest": path.name, "image": str(image_path.relative_to(ROOT)),
            "grid": grid, "eligible_cells": int(eligible.sum()),
            "truth_counts": dict(Counter(local_truth.tolist())), **metric,
        })
    truth = np.concatenate(truths); prediction = np.concatenate(predictions)
    payload = {
        "evaluation": "reviewed real map manifests; no cells used in synthetic training",
        "maps": len(per_map), "cells": int(len(truth)),
        "aggregate": scores(truth, prediction), "per_map": per_map,
        "production_promotion": False, "auto_apply": False,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"maps": payload["maps"], "cells": payload["cells"], "aggregate": payload["aggregate"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
