"""DINOv3 dense-feature terrain classifier for Mengde battle maps."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import joblib
import numpy as np
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score,
    precision_recall_curve, precision_recall_fscore_support,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from transformers import AutoModel

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import terrain_semantic_model as base


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = (
    ROOT / "output" / "model_cache" / "modelscope"
    / "dinov3-vits16-pretrain-lvd1689m"
)
FEATURE_CACHE = ROOT / "output" / "terrain_model" / "dinov3_feature_cache"
DEFAULT_MODEL = ROOT / "output" / "terrain_model" / "terrain_semantic_dinov3.joblib"
DEFAULT_REPORT = ROOT / "output" / "terrain_model" / "training_report_dinov3.json"
BASELINE_REPORT = ROOT / "output" / "terrain_model" / "training_report_handcrafted.json"
_DINO = None
_DINO_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_backbone():
    global _DINO
    weights = MODEL_DIR / "model.safetensors"
    if not weights.is_file() or weights.stat().st_size < 80_000_000:
        raise RuntimeError(
            "DINOv3 weights are missing. Clone "
            "https://www.modelscope.cn/facebook/"
            "dinov3-vits16-pretrain-lvd1689m.git into "
            f"{MODEL_DIR}"
        )
    if _DINO is None:
        _DINO = AutoModel.from_pretrained(MODEL_DIR, local_files_only=True)
        _DINO.to(_DINO_DEVICE).eval()
    return _DINO


def dino_cells(image: Image.Image, width: int, height: int) -> np.ndarray:
    """Map 19x14 logical cells directly to DINOv3 16x16 patch tokens."""
    aligned = image.convert("RGB").resize(
        (width * 32, height * 32), Image.Resampling.BICUBIC
    )
    pixels = np.asarray(aligned, dtype=np.float32) / 255.0
    pixels = (
        pixels - np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
    ) / np.asarray([0.229, 0.224, 0.225], dtype=np.float32)
    tensor = torch.from_numpy(pixels).permute(2, 0, 1).unsqueeze(0).to(_DINO_DEVICE)
    with torch.inference_mode():
        output = load_backbone()(pixel_values=tensor)
    tokens = output.last_hidden_state[0, -(width * height * 4):]
    grid = tokens.reshape(height * 2, width * 2, -1)
    grid = grid.reshape(height, 2, width, 2, -1)
    mean_tokens = grid.mean(dim=(1, 3))
    max_tokens = grid.amax(dim=(1, 3))
    horizontal_delta = grid[:, :, :, 1].mean(dim=1) - grid[:, :, :, 0].mean(dim=1)
    vertical_delta = grid[:, 1].mean(dim=2) - grid[:, 0].mean(dim=2)
    pooled = torch.cat(
        (mean_tokens, max_tokens, horizontal_delta, vertical_delta), dim=-1
    )
    pooled = pooled.reshape(width * height, -1).cpu().numpy().astype(np.float32)
    pooled /= np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-8)
    handcrafted = base.image_cells(image, width, height)
    return np.concatenate([pooled, handcrafted], axis=1)


def cached_cells(asset: Path, width: int, height: int) -> np.ndarray:
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:16]
    path = FEATURE_CACHE / (
        f"{asset.stem}-{width}x{height}-2x-directional-v2-{digest}.npy"
    )
    if path.is_file():
        return np.load(path)
    features = dino_cells(Image.open(asset).convert("RGB"), width, height)
    FEATURE_CACHE.mkdir(parents=True, exist_ok=True)
    np.save(path, features)
    return features


def consistent_stages() -> tuple[list[dict], list[str]]:
    by_asset: dict[str, list[dict]] = defaultdict(list)
    for stage in base.iter_stages():
        by_asset[stage["asset"].name].append(stage)
    accepted: list[dict] = []
    excluded: list[str] = []
    for asset_name, stages in sorted(by_asset.items()):
        label_sets = {"".join(stage["rows"]) for stage in stages}
        grids = {(stage["width"], stage["height"]) for stage in stages}
        if len(label_sets) != 1 or len(grids) != 1:
            excluded.append(asset_name)
            continue
        accepted.append(stages[0])
    return accepted, excluded


def reviewed_manifests() -> dict[str, dict]:
    manifests: dict[str, dict] = {}
    for path in sorted((ROOT / "output" / "terrain_model").glob("*_manifest.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        asset = Path(str(payload.get("map", ""))).name
        rows = payload.get("terrain_rows")
        if asset and isinstance(rows, list):
            manifests[asset] = payload
    return manifests


def build_dataset():
    features, labels, groups, weights, sources = [], [], [], [], []
    manifests = reviewed_manifests()
    stages, excluded = consistent_stages()
    for index, stage in enumerate(stages, 1):
        asset_name = stage["asset"].name
        print(
            f"[{index}/{len(stages)}] DINOv3 {asset_name}",
            flush=True,
        )
        cells = cached_cells(stage["asset"], stage["width"], stage["height"])
        flat = list("".join(stage["rows"]))
        sample_weights = np.ones(len(flat), dtype=np.float32)
        manifest = manifests.get(asset_name)
        reviewed = bool(
            manifest
            and manifest.get("terrain_rows") == stage["rows"]
            and manifest.get("grid") == [stage["width"], stage["height"]]
        )
        if reviewed:
            sample_weights.fill(3.0)
            structure_cells = {
                (int(cell[0]), int(cell[1]))
                for region in manifest.get("structure_regions", {}).values()
                for cell in region
            }
            special_cells = {
                (int(cell[0]), int(cell[1]))
                for field in ("camp_cells", "fence_cells")
                for cell in manifest.get(field, [])
            }
            for cell_index, terrain in enumerate(flat):
                point = (cell_index % stage["width"], cell_index // stage["width"])
                if point in structure_cells or point in special_cells or terrain in {"e", "P"}:
                    sample_weights[cell_index] = 8.0
        features.append(cells)
        labels.extend(flat)
        groups.extend([asset_name] * len(flat))
        weights.extend(sample_weights.tolist())
        sources.append({
            "stage": stage["path"].stem,
            "asset": asset_name,
            "cells": len(flat),
            "supervision": "reviewed manifest" if reviewed else "weak Lua",
            "mean_weight": float(sample_weights.mean()),
        })
    return (
        np.concatenate(features),
        np.asarray(labels),
        np.asarray(groups),
        np.asarray(weights, dtype=np.float32),
        sources,
        excluded,
    )


def classifier(c: float = 0.03):
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1500,
            class_weight="balanced",
            solver="lbfgs",
            C=c,
            random_state=20260809,
        ),
    )


def binary_classifier(c: float = 0.03):
    return make_pipeline(
        StandardScaler(),
        LinearSVC(
            C=c,
            class_weight="balanced",
            dual="auto",
            max_iter=8000,
            random_state=20260809,
        ),
    )


def fit_multiclass(model, x: np.ndarray, y: np.ndarray, weights: np.ndarray):
    return model.fit(x, y, logisticregression__sample_weight=weights)


def fit_binary(model, x: np.ndarray, y: np.ndarray, weights: np.ndarray):
    return model.fit(x, y, linearsvc__sample_weight=weights)


def choose_threshold(truth: np.ndarray, scores: np.ndarray, min_recall: float) -> float:
    if not truth.any():
        return float("inf")
    precision, recall, thresholds = precision_recall_curve(truth, scores)
    eligible = np.flatnonzero(recall[:-1] >= min_recall)
    if not len(eligible):
        return float(np.median(scores[truth]))
    best = eligible[np.argmax(precision[:-1][eligible])]
    return float(thresholds[best])


def supported_predictions(
    probabilities: np.ndarray,
    classes: np.ndarray,
    camp_scores: np.ndarray,
    camp_threshold: float,
    fence_scores: np.ndarray,
    fence_threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    raw_best = probabilities.argmax(axis=1)
    raw = classes[raw_best].astype("<U1")
    supported = raw.copy()
    camp_index = int(np.flatnonzero(classes == "e")[0])
    non_camp = probabilities.copy()
    non_camp[:, camp_index] = -1.0
    unsupported_camp = (supported == "e") & (camp_scores < camp_threshold)
    supported[unsupported_camp] = classes[
        non_camp[unsupported_camp].argmax(axis=1)
    ]
    supported[camp_scores >= camp_threshold] = "e"
    fence_index = int(np.flatnonzero(classes == "P")[0])
    non_fence = probabilities.copy()
    non_fence[:, fence_index] = -1.0
    unsupported_fence = (supported == "P") & (fence_scores < fence_threshold)
    supported[unsupported_fence] = classes[
        non_fence[unsupported_fence].argmax(axis=1)
    ]
    supported[fence_scores >= fence_threshold] = "P"
    confidence = probabilities[np.arange(len(raw_best)), raw_best]
    return supported, confidence


def fence_classifier():
    return binary_classifier()


def camp_classifier():
    return binary_classifier()


def train(model_path: Path, report_path: Path) -> dict:
    x, y, groups, weights, sources, excluded = build_dataset()
    outer_train, outer_test = next(
        GroupShuffleSplit(
            n_splits=1, test_size=0.25, random_state=20260809
        ).split(x, y, groups)
    )
    inner_train_rel, inner_validation_rel = next(
        GroupShuffleSplit(
            n_splits=1, test_size=0.25, random_state=20260810
        ).split(x[outer_train], y[outer_train], groups[outer_train])
    )
    inner_train = outer_train[inner_train_rel]
    inner_validation = outer_train[inner_validation_rel]

    tuning = []
    for c in (0.01, 0.03, 0.1, 0.3):
        candidate = fit_multiclass(
            classifier(c), x[inner_train], y[inner_train], weights[inner_train]
        )
        candidate_prediction = candidate.predict(x[inner_validation])
        tuning.append({
            "c": c,
            "accuracy": float(accuracy_score(y[inner_validation], candidate_prediction)),
            "macro_f1": float(f1_score(
                y[inner_validation], candidate_prediction, average="macro"
            )),
        })
    selected = max(tuning, key=lambda item: (item["macro_f1"], item["accuracy"]))
    selected_c = float(selected["c"])

    inner_fence = fit_binary(
        binary_classifier(selected_c),
        x[inner_train],
        y[inner_train] == "P",
        weights[inner_train],
    )
    inner_camp = fit_binary(
        binary_classifier(selected_c),
        x[inner_train],
        y[inner_train] == "e",
        weights[inner_train],
    )
    fence_threshold = choose_threshold(
        y[inner_validation] == "P",
        inner_fence.decision_function(x[inner_validation]),
        min_recall=0.85,
    )
    camp_threshold = choose_threshold(
        y[inner_validation] == "e",
        inner_camp.decision_function(x[inner_validation]),
        min_recall=0.75,
    )

    probe = fit_multiclass(
        classifier(selected_c), x[outer_train], y[outer_train], weights[outer_train]
    )
    probabilities = probe.predict_proba(x[outer_test])
    raw_prediction = probe.classes_[probabilities.argmax(axis=1)]
    fence_probe = fit_binary(
        binary_classifier(selected_c),
        x[outer_train],
        y[outer_train] == "P",
        weights[outer_train],
    )
    camp_probe = fit_binary(
        binary_classifier(selected_c),
        x[outer_train],
        y[outer_train] == "e",
        weights[outer_train],
    )
    fence_scores = fence_probe.decision_function(x[outer_test])
    camp_scores = camp_probe.decision_function(x[outer_test])
    predicted, _ = supported_predictions(
        probabilities,
        probe.classes_,
        camp_scores,
        camp_threshold,
        fence_scores,
        fence_threshold,
    )

    accuracy = float(accuracy_score(y[outer_test], predicted))
    macro_f1 = float(f1_score(y[outer_test], predicted, average="macro"))
    raw_accuracy = float(accuracy_score(y[outer_test], raw_prediction))
    raw_macro_f1 = float(f1_score(y[outer_test], raw_prediction, average="macro"))

    fence_truth = y[outer_test] == "P"
    fence_binary = fence_scores >= fence_threshold
    fence_precision, fence_recall, fence_f1, _ = precision_recall_fscore_support(
        fence_truth, fence_binary, average="binary", zero_division=0
    )
    camp_truth = y[outer_test] == "e"
    camp_binary = camp_scores >= camp_threshold
    camp_precision, camp_recall, camp_f1, _ = precision_recall_fscore_support(
        camp_truth, camp_binary, average="binary", zero_division=0
    )

    reviewed_sources = [
        source["asset"] for source in sources
        if source["supervision"] == "reviewed manifest"
    ]
    report = {
        "supervision": "reviewed manifests weighted; remaining Lua labels are weak",
        "feature_backend": "dinov3-vits16-modelscope+2x2-directional-pooling+handcrafted",
        "feature_dimensions": int(x.shape[1]),
        "split": "nested grouped-by-complete-map train/tune/test",
        "samples": int(len(y)),
        "maps": int(len(set(groups.tolist()))),
        "reviewed_manifest_maps": reviewed_sources,
        "excluded_conflicting_assets": excluded,
        "training_maps": sorted(set(groups[outer_train].tolist())),
        "validation_maps": sorted(set(groups[outer_test].tolist())),
        "label_counts": dict(sorted(Counter(y.tolist()).items())),
        "selected_c": selected_c,
        "inner_tuning": tuning,
        "raw_accuracy": raw_accuracy,
        "raw_macro_f1": raw_macro_f1,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "classes": classification_report(
            y[outer_test], predicted, output_dict=True, zero_division=0
        ),
        "auto_apply_eligible": accuracy >= 0.90 and macro_f1 >= 0.85,
        "fence_review": {
            "strategy": "review-weighted binary LinearSVC support head",
            "threshold_source": "inner grouped validation",
            "threshold": fence_threshold,
            "precision": float(fence_precision),
            "recall": float(fence_recall),
            "f1": float(fence_f1),
            "validation_candidates": int(fence_binary.sum()),
            "validation_fences": int(fence_truth.sum()),
        },
        "camp_review": {
            "strategy": "review-weighted binary LinearSVC with same-ground hard negatives",
            "threshold_source": "inner grouped validation",
            "threshold": camp_threshold,
            "precision": float(camp_precision),
            "recall": float(camp_recall),
            "f1": float(camp_f1),
            "validation_candidates": int(camp_binary.sum()),
            "validation_camps": int(camp_truth.sum()),
        },
        "sources": sources,
    }
    if BASELINE_REPORT.is_file():
        baseline = json.loads(BASELINE_REPORT.read_text(encoding="utf-8"))
        report["baseline"] = {
            "accuracy": baseline["accuracy"],
            "macro_f1": baseline["macro_f1"],
            "accuracy_delta": accuracy - baseline["accuracy"],
            "macro_f1_delta": macro_f1 - baseline["macro_f1"],
        }

    final = fit_multiclass(classifier(selected_c), x, y, weights)
    final_fence = fit_binary(binary_classifier(selected_c), x, y == "P", weights)
    final_camp = fit_binary(binary_classifier(selected_c), x, y == "e", weights)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "classifier": final,
        "fence_classifier": final_fence,
        "camp_classifier": final_camp,
        "fence_review_threshold": fence_threshold,
        "camp_review_threshold": camp_threshold,
        "feature_backend": "dinov3-directional-v3-reviewed-camp",
        "feature_version": 3,
        "characters": base.CHAR_NAMES,
        "selected_c": selected_c,
        "validation": {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "auto_apply_eligible": report["auto_apply_eligible"],
        },
    }, model_path)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def predict(model_path: Path, image_path: Path, width: int, height: int,
            output_path: Path, threshold: float) -> dict:
    bundle = joblib.load(model_path)
    features = cached_cells(image_path, width, height)
    probabilities = bundle["classifier"].predict_proba(features)
    classes = bundle["classifier"].classes_
    raw_chars = classes[probabilities.argmax(axis=1)]

    fence_scores = bundle["fence_classifier"].decision_function(features)
    fence_threshold = float(bundle["fence_review_threshold"])
    camp_scores = bundle["camp_classifier"].decision_function(features)
    camp_threshold = float(bundle["camp_review_threshold"])
    chars, confidence = supported_predictions(
        probabilities,
        classes,
        camp_scores,
        camp_threshold,
        fence_scores,
        fence_threshold,
    )
    rows = [
        "".join(chars[y * width:(y + 1) * width])
        for y in range(height)
    ]
    raw_rows = [
        "".join(raw_chars[y * width:(y + 1) * width])
        for y in range(height)
    ]
    review = [
        {
            "x": i % width,
            "y": i // width,
            "predicted": str(chars[i]),
            "raw_prediction": str(raw_chars[i]),
            "terrain": base.CHAR_NAMES.get(str(chars[i]), "Unknown"),
            "confidence": round(float(confidence[i]), 4),
        }
        for i in range(len(chars))
        if confidence[i] < threshold
    ]
    fence_review = [
        {
            "x": i % width,
            "y": i // width,
            "supported_prediction": str(chars[i]),
            "fence_score": round(float(fence_scores[i]), 4),
        }
        for i in range(len(chars))
        if fence_scores[i] >= fence_threshold
    ]
    camp_review = [
        {
            "x": i % width,
            "y": i // width,
            "supported_prediction": str(chars[i]),
            "camp_score": round(float(camp_scores[i]), 4),
        }
        for i in range(len(chars))
        if camp_scores[i] >= camp_threshold
    ]
    payload = {
        "image": str(image_path),
        "feature_backend": bundle.get("feature_backend", "dinov3"),
        "feature_version": bundle.get("feature_version", 1),
        "grid": [width, height],
        "rows": rows,
        "raw_rows": raw_rows,
        "threshold": threshold,
        "mean_confidence": float(confidence.mean()),
        "minimum_confidence": float(confidence.min()),
        "review_required": review,
        "fence_review_required": fence_review,
        "camp_review_required": camp_review,
        "auto_apply": bool(
            bundle["validation"]["auto_apply_eligible"]
            and not review and not fence_review and not camp_review
        ),
        "warning": "Supported predictions remain review candidates; never write them directly to Lua.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    base.draw_prediction_overlay(
        Image.open(image_path).convert("RGB"),
        chars,
        confidence,
        width,
        height,
        threshold,
        output_path.with_suffix(".png"),
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    train_parser = sub.add_parser("train")
    train_parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    train_parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    predict_parser = sub.add_parser("predict")
    predict_parser.add_argument("image", type=Path)
    predict_parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    predict_parser.add_argument("--width", type=int, default=19)
    predict_parser.add_argument("--height", type=int, default=14)
    predict_parser.add_argument("--threshold", type=float, default=0.72)
    predict_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "train":
        result = train(args.model, args.report)
    else:
        result = predict(
            args.model, args.image, args.width, args.height,
            args.output, args.threshold,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
