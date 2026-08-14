"""Create an independent Flatland/Forest/Mountain review proposal.

The target map is excluded from training so stale Lua labels cannot teach the
model that every wooded foothill is Mountain. Predictions remain review-only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.terrain_semantic_dinov3 import build_dataset, cached_cells


CLASSES = np.asarray(["f", "F", "m"])
COLORS = {
    "f": np.asarray([128, 185, 84], dtype=np.uint8),
    "F": np.asarray([22, 126, 55], dtype=np.uint8),
    "m": np.asarray([177, 105, 73], dtype=np.uint8),
}
TARGET_MAP = "m008-large-v2.png"
SEED = 20260810


def grouped_split(groups: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    names = np.asarray(sorted(set(groups.tolist())))
    rng = np.random.default_rng(SEED)
    rng.shuffle(names)
    validation_names = set(names[: max(1, round(len(names) * 0.25))])
    validation = np.isin(groups, list(validation_names))
    return ~validation, validation


def metrics(truth: np.ndarray, predicted: np.ndarray) -> dict:
    return {
        "macro_f1": float(f1_score(truth, predicted, average="macro")),
        "classes": classification_report(
            truth, predicted, labels=CLASSES.tolist(), output_dict=True,
            zero_division=0,
        ),
    }


def fit_models(x: np.ndarray, y: np.ndarray, weights: np.ndarray):
    linear = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            C=0.025, class_weight="balanced", max_iter=2000,
            random_state=SEED,
        ),
    )
    linear.fit(x, y, logisticregression__sample_weight=weights)
    trees = ExtraTreesClassifier(
        n_estimators=320, min_samples_leaf=3, max_features="sqrt",
        class_weight="balanced", n_jobs=-1, random_state=SEED,
    )
    trees.fit(x, y, sample_weight=weights)
    return linear, trees


def ordered_probabilities(model, x: np.ndarray) -> np.ndarray:
    raw = model.predict_proba(x)
    ordered = np.zeros((len(x), len(CLASSES)), dtype=np.float32)
    for source, terrain in enumerate(model.classes_):
        ordered[:, int(np.flatnonzero(CLASSES == terrain)[0])] = raw[:, source]
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path,
        default=ROOT / "output/terrain_model/m008_large_v2_manifest.json",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "output/terrain_model/m008_three_class_fusion.json",
    )
    args = parser.parse_args()

    x, labels, groups, weights, _, excluded = build_dataset()
    common = np.isin(labels, CLASSES) & (groups != TARGET_MAP)
    x, labels, groups, weights = (
        x[common], labels[common], groups[common], weights[common]
    )
    train, validation = grouped_split(groups)
    validation_models = fit_models(x[train], labels[train], weights[train])
    validation_probabilities = np.mean(
        [ordered_probabilities(model, x[validation]) for model in validation_models],
        axis=0,
    )
    validation_prediction = CLASSES[validation_probabilities.argmax(axis=1)]

    models = fit_models(x, labels, weights)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    width, height = map(int, manifest["grid"])
    image_path = ROOT / manifest["map"]
    target_x = cached_cells(image_path, width, height)
    model_probabilities = [ordered_probabilities(model, target_x) for model in models]
    probabilities = np.mean(model_probabilities, axis=0)
    prediction = CLASSES[probabilities.argmax(axis=1)]
    confidence = probabilities.max(axis=1)
    model_predictions = [CLASSES[value.argmax(axis=1)] for value in model_probabilities]

    source = np.asarray(list("".join(manifest["terrain_rows"])))
    natural = np.isin(source, CLASSES)
    rows = []
    review_required = []
    for y in range(height):
        row = []
        for x_pos in range(width):
            index = y * width + x_pos
            terrain = str(prediction[index]) if natural[index] else str(source[index])
            row.append(terrain)
            disagreement = model_predictions[0][index] != model_predictions[1][index]
            if natural[index] and (confidence[index] < 0.72 or disagreement):
                review_required.append({
                    "position": [x_pos, y],
                    "prediction": terrain,
                    "confidence": float(confidence[index]),
                    "linear": str(model_predictions[0][index]),
                    "trees": str(model_predictions[1][index]),
                    "probabilities": {
                        str(label): float(probabilities[index, class_index])
                        for class_index, label in enumerate(CLASSES)
                    },
                })
        rows.append("".join(row))

    payload = {
        "backend": "DINOv3-S directional features + handcrafted texture; linear/ExtraTrees fusion",
        "target_excluded_from_training": True,
        "auto_apply": False,
        "classes": CLASSES.tolist(),
        "grid": [width, height],
        "training_maps": sorted(set(groups.tolist())),
        "training_counts": dict(sorted(Counter(labels.tolist()).items())),
        "validation": metrics(labels[validation], validation_prediction),
        "prediction_counts": dict(sorted(Counter(prediction[natural].tolist()).items())),
        "rows": rows,
        "review_required": sorted(
            review_required, key=lambda item: item["confidence"]
        ),
        "excluded_conflicting_assets": excluded,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    rgb = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.uint8)
    overlay = rgb.copy()
    cell_w, cell_h = rgb.shape[1] // width, rgb.shape[0] // height
    for y in range(height):
        for x_pos in range(width):
            index = y * width + x_pos
            if natural[index]:
                color = COLORS[str(prediction[index])]
                patch = overlay[y * cell_h:(y + 1) * cell_h, x_pos * cell_w:(x_pos + 1) * cell_w]
                patch[:] = (patch.astype(np.uint16) * 2 + color.astype(np.uint16)) // 3
    Image.fromarray(overlay).save(args.output.with_suffix(".png"))
    print(json.dumps({
        "validation_macro_f1": payload["validation"]["macro_f1"],
        "prediction_counts": payload["prediction_counts"],
        "review_required": len(review_required),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
