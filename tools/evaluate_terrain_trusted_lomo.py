"""Evaluate the trusted natural-terrain adapter by leaving out whole maps."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler

import train_terrain_trusted_adapter as adapter


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output/terrain_model/terrain_trusted_lomo_report.json"
PROMOTION = {
    "pooled_macro_f1": 0.85,
    "minimum_class_recall": 0.75,
    "selective_accuracy": 0.98,
    "selective_coverage": 0.50,
}


def accepted_mask(probabilities: np.ndarray, agreement: np.ndarray,
                  confidence: float, margin: float) -> np.ndarray:
    ordered = np.sort(probabilities, axis=1)
    return agreement & (ordered[:, -1] >= confidence) & (
        ordered[:, -1] - ordered[:, -2] >= margin
    )


def run_fold(held_out: str, epochs: int, device: torch.device):
    map_x, map_labels, map_groups, map_names, _ = adapter.trusted_map_cells()
    texture_x, texture_labels, texture_groups, _ = adapter.texture_cells()
    training_map = map_names != held_out
    held_out_map = map_names == held_out
    train_x = np.concatenate((map_x[training_map], texture_x)).astype(np.float32)
    train_labels = np.concatenate((map_labels[training_map], texture_labels))
    train_groups = np.concatenate((map_groups[training_map], texture_groups))
    inner_train, calibration = adapter.choose_group_split(train_labels, train_groups)
    scaler = StandardScaler().fit(train_x[inner_train])
    scaled_train = scaler.transform(train_x).astype(np.float32)
    y = adapter.class_index(train_labels)
    model = adapter.fit_adapter(scaled_train[inner_train], y[inner_train], epochs, device)
    _, inner_embedding = adapter.adapter_outputs(
        model, scaled_train[inner_train], device
    )
    prototypes, owners = adapter.fit_prototypes(inner_embedding, y[inner_train])
    owners = owners.astype(np.int64)

    calibration_probability, calibration_embedding = adapter.adapter_outputs(
        model, scaled_train[calibration], device
    )
    calibration_metric = adapter.prototype_probabilities(
        calibration_embedding, prototypes, owners
    )
    calibration_ensemble = 0.55 * calibration_probability + 0.45 * calibration_metric
    calibration_agreement = (
        calibration_probability.argmax(1) == calibration_metric.argmax(1)
    )
    confidence, margin = adapter.select_threshold(
        calibration_ensemble, y[calibration], calibration_agreement
    )

    test_x = scaler.transform(map_x[held_out_map]).astype(np.float32)
    truth = adapter.class_index(map_labels[held_out_map])
    probability, embedding = adapter.adapter_outputs(model, test_x, device)
    metric = adapter.prototype_probabilities(embedding, prototypes, owners)
    ensemble = 0.55 * probability + 0.45 * metric
    agreement = probability.argmax(1) == metric.argmax(1)
    predicted = ensemble.argmax(1)
    accepted = accepted_mask(ensemble, agreement, confidence, margin)
    supported = np.unique(truth)
    per_class = classification_report(
        truth, predicted, labels=np.arange(len(adapter.CLASSES)),
        target_names=adapter.CLASSES.tolist(), output_dict=True, zero_division=0,
    )
    return {
        "held_out_map": held_out,
        "training_maps": sorted(set(map_names[training_map].tolist())),
        "training_label_counts": dict(sorted(Counter(train_labels.tolist()).items())),
        "held_out_label_counts": dict(sorted(Counter(map_labels[held_out_map].tolist()).items())),
        "calibrated_thresholds": {"confidence": confidence, "margin": margin},
        "macro_f1_supported": float(f1_score(
            truth, predicted, labels=supported, average="macro", zero_division=0
        )),
        "selective_accuracy": float(
            (predicted[accepted] == truth[accepted]).mean()
        ) if accepted.any() else 0.0,
        "selective_coverage": float(accepted.mean()),
        "accepted_cells": int(accepted.sum()),
        "classes": {label: per_class[label] for label in adapter.CLASSES},
        "confusion_matrix": confusion_matrix(
            truth, predicted, labels=np.arange(len(adapter.CLASSES))
        ).tolist(),
        "truth": truth.tolist(),
        "prediction": predicted.tolist(),
        "accepted": accepted.tolist(),
    }


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    map_names = adapter.trusted_map_cells()[3]
    folds = [run_fold(name, 40, device) for name in sorted(set(map_names.tolist()))]
    truth = np.concatenate([np.asarray(fold.pop("truth")) for fold in folds])
    predicted = np.concatenate([np.asarray(fold.pop("prediction")) for fold in folds])
    accepted = np.concatenate([np.asarray(fold.pop("accepted"), dtype=bool) for fold in folds])
    report = classification_report(
        truth, predicted, labels=np.arange(len(adapter.CLASSES)),
        target_names=adapter.CLASSES.tolist(), output_dict=True, zero_division=0,
    )
    pooled = {
        "macro_f1": float(f1_score(truth, predicted, average="macro")),
        "selective_accuracy": float((predicted[accepted] == truth[accepted]).mean())
        if accepted.any() else 0.0,
        "selective_coverage": float(accepted.mean()),
        "classes": {label: report[label] for label in adapter.CLASSES},
        "confusion_matrix": confusion_matrix(truth, predicted).tolist(),
    }
    checks = {
        "pooled_macro_f1": pooled["macro_f1"] >= PROMOTION["pooled_macro_f1"],
        "minimum_class_recall": min(
            pooled["classes"][label]["recall"] for label in adapter.CLASSES
        ) >= PROMOTION["minimum_class_recall"],
        "selective_accuracy": pooled["selective_accuracy"] >= PROMOTION["selective_accuracy"],
        "selective_coverage": pooled["selective_coverage"] >= PROMOTION["selective_coverage"],
    }
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "threshold_calibration": "training-side spatial groups only",
        "trusted_maps": sorted(set(map_names.tolist())),
        "device": str(device), "promotion_thresholds": PROMOTION,
        "folds": folds, "pooled": pooled, "promotion_checks": checks,
        "production_promotion": all(checks.values()),
        "auto_apply": False,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "pooled_macro_f1": pooled["macro_f1"],
        "minimum_class_recall": min(
            pooled["classes"][label]["recall"] for label in adapter.CLASSES
        ),
        "selective_accuracy": pooled["selective_accuracy"],
        "selective_coverage": pooled["selective_coverage"],
        "production_promotion": payload["production_promotion"],
        "report": str(REPORT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
