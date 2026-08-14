"""Train a lightweight specialist for Flatland, Forest, and Mountain cells."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report, f1_score
from scipy.ndimage import binary_closing, binary_opening, label as component_label
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import terrain_semantic_model as base
from tools.terrain_semantic_dinov3 import build_dataset, cached_cells, consistent_stages


COMMON = np.asarray(["f", "F", "m"])
REVIEWED_MAP = "m008-large-v2.png"
DEFAULT_MODEL = ROOT / "output" / "terrain_model" / "terrain_common_dinov3.pt"
DEFAULT_REPORT = ROOT / "output" / "terrain_model" / "training_report_dinov3_common.json"
SEED = 20260809


class CommonHead(nn.Module):
    def __init__(self, feature_count: int, hidden: int):
        super().__init__()
        if hidden:
            self.network = nn.Sequential(
                nn.Linear(feature_count, hidden),
                nn.GELU(),
                nn.Dropout(0.08),
                nn.Linear(hidden, len(COMMON)),
            )
        else:
            self.network = nn.Linear(feature_count, len(COMMON))

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features)


def group_split(groups: np.ndarray, fraction: float = 0.25):
    rng = np.random.default_rng(SEED)
    candidates = np.asarray(sorted(set(groups.tolist()) - {REVIEWED_MAP}))
    rng.shuffle(candidates)
    test_groups = set(candidates[:max(1, round(len(set(groups.tolist())) * fraction))])
    test = np.flatnonzero(np.isin(groups, list(test_groups)))
    train = np.flatnonzero(~np.isin(groups, list(test_groups)))
    return train, test


def normalize(x: np.ndarray, train: np.ndarray):
    mean = x[train].mean(axis=0, dtype=np.float64).astype(np.float32)
    std = x[train].std(axis=0, dtype=np.float64).astype(np.float32)
    std[std < 1e-5] = 1.0
    return ((x - mean) / std).astype(np.float32), mean, std


def fit(
    hidden: int,
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    epochs: int,
    batch_size: int,
) -> CommonHead:
    torch.manual_seed(SEED + hidden)
    model = CommonHead(x.shape[1], hidden)
    counts = np.bincount(y, minlength=len(COMMON)).astype(np.float32)
    class_weights = np.sqrt(counts.max() / np.maximum(counts, 1.0))
    class_weights /= class_weights.mean()
    class_weights = torch.from_numpy(class_weights)
    dataset = TensorDataset(
        torch.from_numpy(x), torch.from_numpy(y), torch.from_numpy(weights)
    )
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=7e-4, weight_decay=3e-4)
    for _ in range(epochs):
        model.train()
        for features, target, sample_weight in loader:
            losses = nn.functional.cross_entropy(
                model(features), target, weight=class_weights, reduction="none"
            )
            loss = (losses * sample_weight).sum() / sample_weight.sum().clamp_min(1.0)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
    return model.eval()


@torch.inference_mode()
def predict(model: CommonHead, x: np.ndarray):
    probabilities = torch.softmax(model(torch.from_numpy(x)), dim=1).numpy()
    return COMMON[probabilities.argmax(axis=1)], probabilities.max(axis=1)


def spatial_postprocess(
    prediction: np.ndarray,
    confidence: np.ndarray,
    width: int,
    height: int,
    eligible: np.ndarray,
    protected_positions: set[tuple[int, int]] | None = None,
    confidence_threshold: float = 0.72,
    min_component_size: int = 12,
) -> tuple[np.ndarray, dict]:
    """Smooth low-confidence natural cells without touching structures or broad regions."""
    grid = np.asarray(prediction).reshape(height, width).copy()
    original = grid.copy()
    confidence_grid = np.asarray(confidence).reshape(height, width)
    eligible_grid = np.asarray(eligible, dtype=bool).reshape(height, width)
    protected = np.zeros((height, width), dtype=bool)
    for x, y in protected_positions or set():
        if 0 <= x < width and 0 <= y < height:
            protected[y, x] = True

    connectivity = np.asarray([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
    for terrain in COMMON:
        components, count = component_label((grid == terrain) & eligible_grid, connectivity)
        for component in range(1, count + 1):
            cells = components == component
            if int(cells.sum()) >= min_component_size:
                protected |= cells

    low_confidence = eligible_grid & (confidence_grid < confidence_threshold) & ~protected

    def neighborhood_scores(x: int, y: int, values: np.ndarray) -> dict[str, float]:
        x0, x1 = max(0, x - 1), min(width, x + 2)
        y0, y1 = max(0, y - 1), min(height, y + 2)
        local_values = values[y0:y1, x0:x1]
        local_confidence = confidence_grid[y0:y1, x0:x1]
        local_eligible = eligible_grid[y0:y1, x0:x1]
        return {
            str(terrain): float(local_confidence[(local_values == terrain) & local_eligible].sum())
            for terrain in COMMON
        }

    vote_changes = 0
    voted = grid.copy()
    for y, x in np.argwhere(low_confidence):
        scores = neighborhood_scores(int(x), int(y), grid)
        ranked = sorted(scores, key=scores.get, reverse=True)
        winner, runner_up = ranked[0], ranked[1]
        if winner != grid[y, x] and scores[winner] >= scores[runner_up] + 0.25:
            voted[y, x] = winner
            vote_changes += 1

    kernel = np.ones((3, 3), dtype=bool)
    morphology_proposals: dict[tuple[int, int], str] = {}
    for terrain in COMMON:
        mask = (voted == terrain) & eligible_grid
        smoothed = binary_opening(
            binary_closing(mask, structure=kernel), structure=kernel
        )
        for y, x in np.argwhere(smoothed & low_confidence & (voted != terrain)):
            scores = neighborhood_scores(int(x), int(y), voted)
            ranked = sorted(scores, key=scores.get, reverse=True)
            if ranked[0] == terrain and scores[ranked[0]] >= scores[ranked[1]] + 0.25:
                morphology_proposals[(int(x), int(y))] = str(terrain)

    result = voted.copy()
    for (x, y), terrain in morphology_proposals.items():
        result[y, x] = terrain
    result[protected | ~eligible_grid] = original[protected | ~eligible_grid]
    changed = result != original
    return result.reshape(-1), {
        "confidence_threshold": confidence_threshold,
        "kernel": "3x3 close then open per natural class",
        "min_protected_component": min_component_size,
        "eligible_cells": int(eligible_grid.sum()),
        "low_confidence_cells": int(low_confidence.sum()),
        "protected_cells": int(protected.sum()),
        "vote_changes": vote_changes,
        "morphology_changes": int(sum(result[y, x] != voted[y, x] for x, y in morphology_proposals)),
        "total_changes": int(changed.sum()),
    }


def evaluate_spatial_postprocess(
    model: CommonHead,
    mean: np.ndarray,
    std: np.ndarray,
    validation_maps: set[str],
) -> dict:
    raw_correct = post_correct = eligible_total = changes = 0
    per_map = []
    for stage in consistent_stages()[0]:
        asset_name = stage["asset"].name
        if asset_name not in validation_maps:
            continue
        features = cached_cells(stage["asset"], stage["width"], stage["height"])
        scaled = ((features - mean) / std).astype(np.float32)
        raw, confidence = predict(model, scaled)
        truth = np.asarray(list("".join(stage["rows"])))
        eligible = np.isin(truth, COMMON)
        post, stats = spatial_postprocess(
            raw, confidence, stage["width"], stage["height"], eligible
        )
        count = int(eligible.sum())
        raw_hits = int((raw[eligible] == truth[eligible]).sum())
        post_hits = int((post[eligible] == truth[eligible]).sum())
        raw_correct += raw_hits
        post_correct += post_hits
        eligible_total += count
        changes += int(stats["total_changes"])
        per_map.append({
            "map": asset_name,
            "cells": count,
            "raw_accuracy": raw_hits / count if count else 0.0,
            "post_accuracy": post_hits / count if count else 0.0,
            **stats,
        })
    return {
        "raw_accuracy": raw_correct / eligible_total if eligible_total else 0.0,
        "post_accuracy": post_correct / eligible_total if eligible_total else 0.0,
        "eligible_cells": eligible_total,
        "total_changes": changes,
        "maps": per_map,
    }

def metrics(truth: np.ndarray, predicted: np.ndarray) -> dict:
    return {
        "accuracy": float(accuracy_score(truth, predicted)),
        "macro_f1": float(f1_score(truth, predicted, average="macro")),
        "classes": classification_report(
            truth, predicted, labels=COMMON.tolist(), output_dict=True, zero_division=0
        ),
    }


def train(model_path: Path, report_path: Path, epochs: int, batch_size: int):
    x, labels, groups, weights, _, excluded = build_dataset()
    common_mask = np.isin(labels, COMMON)
    x = x[common_mask]
    labels = labels[common_mask]
    groups = groups[common_mask]
    weights = weights[common_mask]
    y = np.asarray([int(np.flatnonzero(COMMON == label)[0]) for label in labels], dtype=np.int64)
    # The only fully reviewed natural-terrain map must outweigh legacy weak Lua rows.
    weights = np.where(groups == REVIEWED_MAP, weights * 6.0, weights).astype(np.float32)
    train_indices, test_indices = group_split(groups)
    scaled, mean, std = normalize(x, train_indices)
    reviewed_indices = np.flatnonzero(groups == REVIEWED_MAP)

    experiments = {}
    candidates = {}
    for name, hidden in (("linear", 0), ("mlp128", 128)):
        print(f"training common {name}", flush=True)
        candidate = fit(
            hidden, scaled[train_indices], y[train_indices], weights[train_indices],
            epochs, batch_size,
        )
        candidates[name] = candidate
        test_prediction, _ = predict(candidate, scaled[test_indices])
        reviewed_prediction, _ = predict(candidate, scaled[reviewed_indices])
        experiments[name] = {
            "hidden": hidden,
            "unseen_maps": metrics(labels[test_indices], test_prediction),
            "reviewed_queshan_fit": metrics(labels[reviewed_indices], reviewed_prediction),
        }

    def score(name: str):
        result = experiments[name]
        return (
            result["unseen_maps"]["macro_f1"]
            + result["reviewed_queshan_fit"]["macro_f1"]
        )

    selected = max(experiments, key=score)
    spatial_validation = evaluate_spatial_postprocess(
        candidates[selected], mean, std, set(groups[test_indices].tolist())
    )
    report = {
        "purpose": "specialist for common terrain only; never predicts structures",
        "classes": {"f": "Flatland", "F": "Forest", "m": "Mountain"},
        "split": "grouped by complete map; reviewed Queshan kept in training",
        "samples": int(len(labels)),
        "maps": int(len(set(groups.tolist()))),
        "label_counts": dict(sorted(Counter(labels.tolist()).items())),
        "reviewed_map_weight_multiplier": 6.0,
        "epochs": epochs,
        "batch_size": batch_size,
        "validation_maps": sorted(set(groups[test_indices].tolist())),
        "experiments": experiments,
        "selected": selected,
        "spatial_postprocess_validation": spatial_validation,
        "auto_apply": False,
        "excluded_conflicting_assets": excluded,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    all_indices = np.arange(len(labels))
    scaled_all, mean, std = normalize(x, all_indices)
    final = fit(
        int(experiments[selected]["hidden"]), scaled_all, y, weights,
        epochs, batch_size,
    )
    torch.save({
        "state_dict": final.state_dict(),
        "feature_count": int(x.shape[1]),
        "hidden": int(experiments[selected]["hidden"]),
        "classes": COMMON.tolist(),
        "mean": mean,
        "std": std,
        "validation": experiments[selected],
        "auto_apply": False,
    }, model_path)
    return report


def predict_reviewed(
    model_path: Path,
    image_path: Path,
    width: int,
    height: int,
    manifest_path: Path,
    output_path: Path,
):
    bundle = torch.load(model_path, map_location="cpu", weights_only=False)
    model = CommonHead(int(bundle["feature_count"]), int(bundle["hidden"]))
    model.load_state_dict(bundle["state_dict"])
    model.eval()
    features = cached_cells(image_path, width, height)
    scaled = ((features - bundle["mean"]) / bundle["std"]).astype(np.float32)
    common_prediction, common_confidence = predict(model, scaled)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reviewed = np.asarray(list("".join(manifest["terrain_rows"])))
    if len(reviewed) != width * height:
        raise ValueError("manifest terrain size differs from prediction grid")
    common_mask = np.isin(reviewed, COMMON)
    protected_positions = {
        (int(layer["position"][0]), int(layer["position"][1]))
        for layer in manifest.get("terrain_layers", [])
    }
    postprocessed_prediction, postprocess_stats = spatial_postprocess(
        common_prediction,
        common_confidence,
        width,
        height,
        common_mask,
        protected_positions,
    )
    final = reviewed.copy()
    final[common_mask] = postprocessed_prediction[common_mask]
    confidence = common_confidence.copy()
    confidence[~common_mask] = 1.0
    disagreements = [
        {
            "x": int(index % width),
            "y": int(index // width),
            "expected": str(reviewed[index]),
            "predicted": str(common_prediction[index]),
            "confidence": round(float(common_confidence[index]), 4),
        }
        for index in np.flatnonzero(common_mask & (common_prediction != reviewed))
    ]
    rows = ["".join(final[y * width:(y + 1) * width]) for y in range(height)]
    common_rows = [
        "".join(common_prediction[y * width:(y + 1) * width])
        for y in range(height)
    ]
    postprocessed_common_rows = [
        "".join(postprocessed_prediction[y * width:(y + 1) * width])
        for y in range(height)
    ]
    payload = {
        "image": str(image_path),
        "feature_backend": "dinov3-common-mlp128+reviewed-structure-contract",
        "grid": [width, height],
        "rows": rows,
        "common_rows": common_rows,
        "postprocessed_common_rows": postprocessed_common_rows,
        "common_classes": COMMON.tolist(),
        "reviewed_common_cells": int(common_mask.sum()),
        "common_accuracy": float((common_prediction[common_mask] == reviewed[common_mask]).mean()),
        "postprocessed_common_accuracy": float(
            (postprocessed_prediction[common_mask] == reviewed[common_mask]).mean()
        ),
        "spatial_postprocess": postprocess_stats,
        "common_disagreements": disagreements,
        "terrain_protocol": manifest.get("terrain_protocol", {}),
        "terrain_layers": manifest.get("terrain_layers", []),
        "secondary_source": "reviewed manifest; the classifier predicts primary natural terrain only",
        "structure_source": str(manifest_path),
        "auto_apply": False,
        "warning": "Common terrain predictions are suggestions; reviewed structure cells remain manifest-owned.",
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    base.draw_prediction_overlay(
        Image.open(image_path).convert("RGB"), final, confidence,
        width, height, 0.72, output_path.with_suffix(".png"),
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--epochs", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--predict-image", type=Path)
    parser.add_argument("--width", type=int, default=19)
    parser.add_argument("--height", type=int, default=14)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.predict_image:
        if args.manifest is None or args.output is None:
            parser.error("--predict-image requires --manifest and --output")
        report = predict_reviewed(
            args.model, args.predict_image, args.width, args.height,
            args.manifest, args.output,
        )
    else:
        report = train(args.model, args.report, args.epochs, args.batch_size)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
