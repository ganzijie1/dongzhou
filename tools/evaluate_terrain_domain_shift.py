"""Diagnose whole-map terrain domain shift without target-label tuning.

The target bitmap may be used for unsupervised feature normalization, but its
labels are touched only after predictions have been produced.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import RobustScaler, StandardScaler

import train_terrain_trusted_adapter as data


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output/terrain_model/terrain_domain_shift_report.json"
SEED = 20260813


def domain_standardize(values: np.ndarray, domains: np.ndarray) -> np.ndarray:
    """Normalize each image/domain using no labels from that domain."""
    result = np.empty_like(values, dtype=np.float32)
    for domain in np.unique(domains):
        mask = domains == domain
        chunk = values[mask]
        center = np.median(chunk, axis=0)
        scale = np.quantile(chunk, 0.75, axis=0) - np.quantile(chunk, 0.25, axis=0)
        scale = np.where(scale > 1e-5, scale, 1.0)
        result[mask] = np.clip((chunk - center) / scale, -8.0, 8.0)
    return result


def texture_domains(groups: np.ndarray) -> np.ndarray:
    # Keep separate source images/styles, while merging their spatial tiles.
    return np.asarray(["-".join(group.split("-")[:3]) for group in groups])


def fit_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray,
                c: float) -> np.ndarray:
    scaler = StandardScaler().fit(train_x)
    model = LogisticRegression(
        C=c, class_weight="balanced", max_iter=2500, solver="lbfgs",
        random_state=SEED,
    ).fit(scaler.transform(train_x), train_y)
    return model.predict(scaler.transform(test_x))


def choose_c(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> float:
    train, validation = data.choose_group_split(y, groups)
    best = None
    for c in (0.003, 0.01, 0.03, 0.1, 0.3):
        prediction = fit_predict(x[train], y[train], x[validation], c)
        score = f1_score(
            y[validation], prediction, labels=np.arange(len(data.CLASSES)),
            average="macro", zero_division=0,
        )
        candidate = (score, -c, c)
        if best is None or candidate > best:
            best = candidate
    return float(best[2])


def metrics(truth: np.ndarray, prediction: np.ndarray) -> dict:
    report = classification_report(
        truth, prediction, labels=np.arange(len(data.CLASSES)),
        target_names=data.CLASSES.tolist(), output_dict=True, zero_division=0,
    )
    return {
        "macro_f1": float(f1_score(
            truth, prediction, labels=np.arange(len(data.CLASSES)),
            average="macro", zero_division=0,
        )),
        "minimum_recall": float(min(report[label]["recall"] for label in data.CLASSES)),
        "classes": {label: report[label] for label in data.CLASSES},
        "confusion_matrix": confusion_matrix(
            truth, prediction, labels=np.arange(len(data.CLASSES))
        ).tolist(),
    }


def main() -> None:
    map_x, map_labels, map_groups, map_names, _ = data.trusted_map_cells()
    texture_x, texture_labels, texture_groups, _ = data.texture_cells()
    dino_dim = map_x.shape[1] - 213
    methods = {
        "all_raw": lambda x, domains: x,
        "dino_raw": lambda x, domains: x[:, :dino_dim],
        "all_per_domain_robust": domain_standardize,
        "dino_per_domain_robust": lambda x, domains: domain_standardize(
            x[:, :dino_dim], domains
        ),
        "dino_raw_plus_normalized_handcrafted": lambda x, domains: np.concatenate((
            x[:, :dino_dim], domain_standardize(x[:, dino_dim:], domains)
        ), axis=1),
    }
    folds = []
    pooled = {name: {"truth": [], "prediction": []} for name in methods}
    texture_domain = texture_domains(texture_groups)
    for held_out in sorted(set(map_names.tolist())):
        source_mask, target_mask = map_names != held_out, map_names == held_out
        train_x = np.concatenate((map_x[source_mask], texture_x)).astype(np.float32)
        train_labels = np.concatenate((map_labels[source_mask], texture_labels))
        train_y = data.class_index(train_labels)
        train_groups = np.concatenate((map_groups[source_mask], texture_groups))
        train_domains = np.concatenate((map_names[source_mask], texture_domain))
        test_x = map_x[target_mask].astype(np.float32)
        test_y = data.class_index(map_labels[target_mask])
        test_domains = map_names[target_mask]
        fold = {
            "held_out_map": held_out,
            "training_label_counts": dict(sorted(Counter(train_labels.tolist()).items())),
            "held_out_label_counts": dict(sorted(Counter(map_labels[target_mask].tolist()).items())),
            "methods": {},
        }
        for name, transform in methods.items():
            transformed_train = transform(train_x, train_domains).astype(np.float32)
            transformed_test = transform(test_x, test_domains).astype(np.float32)
            c = choose_c(transformed_train, train_y, train_groups)
            prediction = fit_predict(transformed_train, train_y, transformed_test, c)
            fold["methods"][name] = {"selected_c": c, **metrics(test_y, prediction)}
            pooled[name]["truth"].append(test_y)
            pooled[name]["prediction"].append(prediction)
        folds.append(fold)
    pooled_metrics = {}
    for name, values in pooled.items():
        pooled_metrics[name] = metrics(
            np.concatenate(values["truth"]), np.concatenate(values["prediction"])
        )
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "target_label_access": "metrics-only after prediction",
        "target_bitmap_access": "permitted for unsupervised per-image statistics",
        "dino_feature_dimensions": dino_dim,
        "handcrafted_feature_dimensions": map_x.shape[1] - dino_dim,
        "folds": folds,
        "pooled": pooled_metrics,
        "production_promotion": False,
        "auto_apply": False,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({name: {
        "macro_f1": score["macro_f1"], "minimum_recall": score["minimum_recall"]
    } for name, score in pooled_metrics.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
