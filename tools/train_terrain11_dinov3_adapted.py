"""Train a high-recall hierarchical terrain model on reviewed DINOv3 features."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import classification_report, confusion_matrix

from terrain_semantic_dinov3 import cached_cells


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "output/terrain_model/terrain_11_dinov3_adapted.joblib"
REPORT = ROOT / "output/terrain_model/terrain_11_dinov3_adapted_report.json"
NATURAL = np.asarray(["f", "g", "F", "m"])
STRUCTURE = np.asarray(["W", "C", "e", "P", "~"])
TEST = {"m066", "m076", "m081", "m084", "m086", "m089", "m091"}
VALIDATION = {"m058", "m065", "m074", "m079", "m087"}
SEED = 20260812


def load_split(split: str):
    features, labels, groups = [], [], []
    for path in sorted((ROOT / "assets/lzc/map_sources").glob("m*_manifest.json")):
        mid = path.name.split("_")[0]
        current = "test" if mid in TEST else "validation" if mid in VALIDATION else "train"
        if current != split:
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        grid, rows = manifest.get("grid", []), manifest.get("terrain_rows", [])
        image_path = ROOT / manifest.get("map", "")
        if len(grid) != 2 or len(rows) != grid[1] or not image_path.is_file():
            continue
        truth = np.asarray(list("".join(rows)))
        eligible = np.isin(truth, np.concatenate((NATURAL, STRUCTURE)))
        print(f"DINOv3 {split} {mid} {grid[0]}x{grid[1]}", flush=True)
        cells = cached_cells(image_path, int(grid[0]), int(grid[1]))
        features.append(cells[eligible])
        labels.append(truth[eligible])
        groups.extend([mid] * int(eligible.sum()))
    return np.concatenate(features), np.concatenate(labels), np.asarray(groups)


def classifier(seed: int, estimators: int = 260):
    return ExtraTreesClassifier(
        n_estimators=estimators, max_depth=30, max_features="sqrt",
        min_samples_leaf=1, class_weight="balanced", n_jobs=-1,
        random_state=seed,
    )


def choose_gate_threshold(model, x, y, minimum_recall=0.90):
    classes = model.classes_.tolist()
    index = classes.index("structure")
    probability = model.predict_proba(x)[:, index]
    truth = np.isin(y, STRUCTURE)
    candidates = np.unique(np.quantile(probability, np.linspace(0.0, 1.0, 401)))
    selected = 0.5
    best_precision = -1.0
    for threshold in candidates:
        predicted = probability >= threshold
        tp = int((predicted & truth).sum())
        recall = tp / max(1, int(truth.sum()))
        precision = tp / max(1, int(predicted.sum()))
        if recall >= minimum_recall and precision > best_precision:
            selected, best_precision = float(threshold), precision
    return selected


def fit(train_x, train_y, validation_x, validation_y):
    gate_truth = np.where(np.isin(train_y, STRUCTURE), "structure", "natural")
    gate_weights = np.where(gate_truth == "structure", 6.0, 1.0)
    gate = classifier(SEED).fit(train_x, gate_truth, sample_weight=gate_weights)
    threshold = choose_gate_threshold(gate, validation_x, validation_y)
    natural_mask = np.isin(train_y, NATURAL)
    structure_mask = np.isin(train_y, STRUCTURE)
    natural = classifier(SEED + 1, 360).fit(train_x[natural_mask], train_y[natural_mask])
    structure_weights = np.asarray([
        {"W": 3.0, "C": 15.0, "e": 12.0, "P": 5.0, "~": 5.0}[str(label)]
        for label in train_y[structure_mask]
    ])
    structure = classifier(SEED + 2, 360).fit(
        train_x[structure_mask], train_y[structure_mask], sample_weight=structure_weights)
    return {"gate": gate, "gate_threshold": threshold, "natural": natural, "structure": structure}


def predict(bundle, x):
    gate_classes = bundle["gate"].classes_.tolist()
    p_structure = bundle["gate"].predict_proba(x)[:, gate_classes.index("structure")]
    structure_mask = p_structure >= bundle["gate_threshold"]
    result = np.empty(len(x), dtype="<U1")
    result[~structure_mask] = bundle["natural"].predict(x[~structure_mask])
    result[structure_mask] = bundle["structure"].predict(x[structure_mask])
    return result, p_structure


def score(truth, predicted):
    labels = NATURAL.tolist() + STRUCTURE.tolist()
    report = classification_report(truth, predicted, labels=labels, output_dict=True, zero_division=0)
    supported = [label for label in labels if report[label]["support"] > 0]
    structure_truth = np.isin(truth, STRUCTURE)
    structure_prediction = np.isin(predicted, STRUCTURE)
    true_positive = int((structure_truth & structure_prediction).sum())
    return {
        "macro_f1_supported": float(np.mean([report[label]["f1-score"] for label in supported])),
        "minimum_class_f1": float(min(report[label]["f1-score"] for label in supported)),
        "structure_gate_recall": true_positive / max(1, int(structure_truth.sum())),
        "structure_gate_precision": true_positive / max(1, int(structure_prediction.sum())),
        "classes": {label: report[label] for label in labels},
        "confusion_matrix": confusion_matrix(truth, predicted, labels=labels).tolist(),
    }


def main():
    train_x, train_y, train_groups = load_split("train")
    validation_x, validation_y, validation_groups = load_split("validation")
    test_x, test_y, test_groups = load_split("test")
    bundle = fit(train_x, train_y, validation_x, validation_y)
    validation_prediction, _ = predict(bundle, validation_x)
    test_prediction, _ = predict(bundle, test_x)
    validation = score(validation_y, validation_prediction)
    held_out = score(test_y, test_prediction)
    required = NATURAL.tolist() + STRUCTURE.tolist()
    production = (
        held_out["macro_f1_supported"] >= 0.72
        and held_out["structure_gate_recall"] >= 0.85
        and all(held_out["classes"][label]["recall"] >= 0.45 for label in required)
    )
    bundle.update({
        "natural_classes": NATURAL.tolist(), "structure_classes": STRUCTURE.tolist(),
        "confidence_threshold": 0.72, "production_promotion": production,
        "synthetic_specialist": str(ROOT / "output/terrain_model/terrain_11_self_evolved.joblib"),
        "unverified_classes": ["s", "v"], "auto_apply": False,
    })
    joblib.dump(bundle, MODEL)
    payload = {
        "feature_backend": "DINOv3 dense 2x directional tokens plus handcrafted features",
        "split": "grouped by complete reviewed maps",
        "training_maps": sorted(set(train_groups)), "validation_maps": sorted(set(validation_groups)),
        "test_maps": sorted(set(test_groups)), "gate_threshold": bundle["gate_threshold"],
        "training_cells": int(len(train_y)), "validation_cells": int(len(validation_y)),
        "test_cells": int(len(test_y)), "validation": validation,
        "held_out_real_test": held_out, "unverified_real_classes": ["s", "v"],
        "production_promotion": production, "auto_apply": False,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
