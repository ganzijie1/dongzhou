"""Compare lightweight CE and Focal-Tversky heads on frozen DINOv3 cells."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score,
    precision_recall_curve, precision_recall_fscore_support,
)
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.terrain_semantic_dinov3 import (
    ROOT,
    build_dataset,
    choose_threshold,
    supported_predictions,
)

DEFAULT_MODEL = ROOT / "output" / "terrain_model" / "terrain_semantic_dinov3_focal.pt"
DEFAULT_REPORT = ROOT / "output" / "terrain_model" / "training_report_dinov3_focal.json"
SEED = 20260809


class TerrainHead(nn.Module):
    """One projection computes multiclass terrain plus Camp/Fence support logits."""

    def __init__(self, feature_count: int, class_count: int):
        super().__init__()
        self.output = nn.Linear(feature_count, class_count + 2)

    def forward(self, features: torch.Tensor):
        logits = self.output(features)
        return logits[:, :-2], logits[:, -2], logits[:, -1]


def seed_everything() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)


def effective_class_weights(labels: np.ndarray, class_count: int) -> torch.Tensor:
    counts = np.bincount(labels, minlength=class_count).astype(np.float64)
    beta = 0.999
    weights = (1.0 - beta) / np.maximum(1.0 - np.power(beta, counts), 1e-12)
    weights /= weights.mean()
    return torch.tensor(weights, dtype=torch.float32)


def focal_multiclass(
    logits: torch.Tensor,
    target: torch.Tensor,
    alpha: torch.Tensor,
    sample_weight: torch.Tensor,
    gamma: float = 2.0,
) -> torch.Tensor:
    log_probability = torch.log_softmax(logits, dim=1)
    log_pt = log_probability.gather(1, target[:, None]).squeeze(1)
    pt = log_pt.exp()
    loss = -alpha[target] * (1.0 - pt).pow(gamma) * log_pt
    return (loss * sample_weight).sum() / sample_weight.sum().clamp_min(1.0)


def focal_binary(
    logits: torch.Tensor,
    target: torch.Tensor,
    sample_weight: torch.Tensor,
    gamma: float = 2.0,
) -> torch.Tensor:
    probability = torch.sigmoid(logits)
    pt = torch.where(target > 0.5, probability, 1.0 - probability)
    positive_count = target.sum().clamp_min(1.0)
    negative_count = (1.0 - target).sum().clamp_min(1.0)
    positive_alpha = negative_count / (positive_count + negative_count)
    alpha = torch.where(target > 0.5, positive_alpha, 1.0 - positive_alpha)
    loss = -alpha * (1.0 - pt).pow(gamma) * pt.clamp_min(1e-6).log()
    return (loss * sample_weight).sum() / sample_weight.sum().clamp_min(1.0)


def focal_tversky(
    logits: torch.Tensor,
    target: torch.Tensor,
    sample_weight: torch.Tensor,
    false_positive_weight: float = 0.3,
    false_negative_weight: float = 0.7,
    gamma: float = 0.75,
) -> torch.Tensor:
    probability = torch.sigmoid(logits)
    true_positive = (sample_weight * probability * target).sum()
    false_positive = (sample_weight * probability * (1.0 - target)).sum()
    false_negative = (sample_weight * (1.0 - probability) * target).sum()
    score = (true_positive + 1.0) / (
        true_positive
        + false_positive_weight * false_positive
        + false_negative_weight * false_negative
        + 1.0
    )
    return (1.0 - score).pow(gamma)


def make_loader(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    batch_size: int,
) -> DataLoader:
    dataset = TensorDataset(
        torch.from_numpy(x.astype(np.float32, copy=False)),
        torch.from_numpy(y.astype(np.int64, copy=False)),
        torch.from_numpy(weights.astype(np.float32, copy=False)),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def train_head(
    mode: str,
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    classes: np.ndarray,
    epochs: int,
    batch_size: int,
) -> TerrainHead:
    seed_everything()
    model = TerrainHead(x.shape[1], len(classes))
    optimizer = torch.optim.AdamW(model.parameters(), lr=8e-4, weight_decay=2e-4)
    alpha = effective_class_weights(y, len(classes))
    camp_index = int(np.flatnonzero(classes == "e")[0])
    fence_index = int(np.flatnonzero(classes == "P")[0])
    loader = make_loader(x, y, weights, batch_size)
    model.train()
    for _ in range(epochs):
        for features, target, sample_weight in loader:
            terrain_logits, camp_logits, fence_logits = model(features)
            camp_target = (target == camp_index).float()
            fence_target = (target == fence_index).float()
            if mode == "ce":
                terrain_loss = nn.functional.cross_entropy(
                    terrain_logits, target, weight=alpha, reduction="none"
                )
                terrain_loss = (
                    terrain_loss * sample_weight
                ).sum() / sample_weight.sum().clamp_min(1.0)
                camp_loss = nn.functional.binary_cross_entropy_with_logits(
                    camp_logits, camp_target, weight=sample_weight
                )
                fence_loss = nn.functional.binary_cross_entropy_with_logits(
                    fence_logits, fence_target, weight=sample_weight
                )
            else:
                terrain_loss = focal_multiclass(
                    terrain_logits, target, alpha, sample_weight
                )
                camp_loss = focal_binary(camp_logits, camp_target, sample_weight)
                camp_loss = camp_loss + focal_tversky(
                    camp_logits, camp_target, sample_weight
                )
                fence_loss = focal_binary(fence_logits, fence_target, sample_weight)
                fence_loss = fence_loss + focal_tversky(
                    fence_logits, fence_target, sample_weight
                )
            loss = terrain_loss + 0.5 * camp_loss + 0.5 * fence_loss
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
    return model.eval()


@torch.inference_mode()
def infer(model: TerrainHead, x: np.ndarray):
    terrain, camp, fence = model(torch.from_numpy(x.astype(np.float32, copy=False)))
    return (
        torch.softmax(terrain, dim=1).numpy(),
        camp.numpy(),
        fence.numpy(),
    )


def scale_features(x: np.ndarray, train_indices: np.ndarray):
    mean = x[train_indices].mean(axis=0, dtype=np.float64).astype(np.float32)
    std = x[train_indices].std(axis=0, dtype=np.float64).astype(np.float32)
    std[std < 1e-5] = 1.0
    return ((x - mean) / std).astype(np.float32), mean, std


def rare_aware_group_split(
    groups: np.ndarray,
    labels: np.ndarray,
    test_fraction: float,
    seed: int,
    protected_train_group: str = "m008-large-v2.png",
):
    """Hold out complete maps while keeping scarce P examples on both sides."""
    rng = np.random.default_rng(seed)
    unique_groups = np.asarray(sorted(set(groups.tolist())))
    target_count = max(1, int(round(len(unique_groups) * test_fraction)))
    fence_groups = [
        group for group in unique_groups
        if group != protected_train_group
        and np.any((groups == group) & (labels == "P"))
    ]
    rng.shuffle(fence_groups)
    test_groups = set(fence_groups[:max(1, min(2, len(fence_groups) // 2))])
    candidates = [
        group for group in unique_groups
        if group != protected_train_group and group not in test_groups
    ]
    rng.shuffle(candidates)
    test_groups.update(candidates[:max(0, target_count - len(test_groups))])
    test_mask = np.isin(groups, list(test_groups))
    train_indices = np.flatnonzero(~test_mask)
    test_indices = np.flatnonzero(test_mask)
    if not np.any(labels[test_indices] == "P") or not np.any(labels[train_indices] == "P"):
        raise RuntimeError("Rare-aware split failed to place Fence examples on both sides")
    return train_indices, test_indices


def select_threshold(truth: np.ndarray, scores: np.ndarray, beta: float) -> float:
    """Choose an F-beta threshold on a complete-map calibration fold."""
    precision, recall, thresholds = precision_recall_curve(truth, scores)
    if not len(thresholds):
        return float("inf")
    beta_squared = beta * beta
    f_beta = (
        (1.0 + beta_squared) * precision[:-1] * recall[:-1]
        / np.maximum(beta_squared * precision[:-1] + recall[:-1], 1e-12)
    )
    return float(thresholds[int(np.argmax(f_beta))])


def binary_metrics(truth: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    predicted = scores >= threshold
    precision, recall, f1, _ = precision_recall_fscore_support(
        truth, predicted, average="binary", zero_division=0
    )
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1-score": float(f1),
        "support": int(truth.sum()),
        "candidates": int(predicted.sum()),
    }


def evaluate(
    model: TerrainHead,
    x: np.ndarray,
    y_chars: np.ndarray,
    classes: np.ndarray,
    indices: np.ndarray,
    camp_threshold: float,
    fence_threshold: float,
) -> dict:
    probabilities, camp_scores, fence_scores = infer(model, x[indices])
    prediction = classes[probabilities.argmax(axis=1)]
    truth = y_chars[indices]
    report = classification_report(truth, prediction, output_dict=True, zero_division=0)
    return {
        "accuracy": float(accuracy_score(truth, prediction)),
        "macro_f1": float(f1_score(truth, prediction, average="macro")),
        "camp_multiclass": report.get("e", {}),
        "fence_multiclass": report.get("P", {}),
        "camp_support": binary_metrics(truth == "e", camp_scores, camp_threshold),
        "fence_support": binary_metrics(truth == "P", fence_scores, fence_threshold),
        "classes": report,
    }

def train(output_model: Path, output_report: Path, epochs: int, batch_size: int):
    x, y_chars, groups, weights, sources, excluded = build_dataset()
    classes = np.asarray(sorted(set(y_chars.tolist())))
    class_to_index = {name: index for index, name in enumerate(classes)}
    y = np.asarray([class_to_index[name] for name in y_chars], dtype=np.int64)
    outer_train, outer_test = rare_aware_group_split(
        groups, y_chars, 0.25, SEED
    )
    inner_train_rel, inner_validation_rel = rare_aware_group_split(
        groups[outer_train], y_chars[outer_train], 0.25, 20260810
    )
    inner_train = outer_train[inner_train_rel]
    inner_validation = outer_train[inner_validation_rel]
    scaled, mean, std = scale_features(x, inner_train)

    experiments = {}
    selected_thresholds = {}
    candidate_models = {}
    for mode in ("ce", "focal_tversky"):
        print(f"training {mode} head", flush=True)
        model = train_head(
            mode, scaled[inner_train], y[inner_train], weights[inner_train],
            classes, epochs, batch_size,
        )
        _, camp_scores, fence_scores = infer(model, scaled[inner_validation])
        camp_threshold = select_threshold(
            y_chars[inner_validation] == "e", camp_scores, beta=1.0
        )
        fence_threshold = select_threshold(
            y_chars[inner_validation] == "P", fence_scores, beta=2.0
        )
        candidate_models[mode] = model
        selected_thresholds[mode] = (camp_threshold, fence_threshold)
        experiments[mode] = {
            "inner_validation": evaluate(
                model, scaled, y_chars, classes, inner_validation,
                camp_threshold, fence_threshold,
            ),
            "outer_validation": evaluate(
                model, scaled, y_chars, classes, outer_test,
                camp_threshold, fence_threshold,
            ),
            "camp_threshold": camp_threshold,
            "fence_threshold": fence_threshold,
        }

    # Selection emphasizes scarce structural classes without ignoring global quality.
    def selection_score(mode: str) -> float:
        metrics = experiments[mode]["inner_validation"]
        return (
            metrics["macro_f1"]
            + 0.5 * float(metrics["camp_support"].get("f1-score", 0.0))
            + 0.5 * float(metrics["fence_support"].get("f1-score", 0.0))
        )

    selected_mode = max(experiments, key=selection_score)
    camp_threshold, fence_threshold = selected_thresholds[selected_mode]
    # Keep the calibrated inner model for the untouched outer-map evaluation.
    final_probe = candidate_models[selected_mode]
    outer_metrics = evaluate(
        final_probe, scaled, y_chars, classes, outer_test,
        camp_threshold, fence_threshold,
    )
    report = {
        "feature_backend": "frozen-dinov3-directional-v2+handcrafted",
        "head": "single lightweight linear multitask projection",
        "split": (
            "nested grouped-by-complete-map, rare-aware Fence coverage; "
            "identical folds and budget for CE and Focal-Tversky"
        ),
        "losses": {
            "ce": "effective-number class-balanced CE + BCE support heads",
            "focal_tversky": (
                "effective-number focal(gamma=2) + binary focal + "
                "Focal-Tversky(fp=0.3, fn=0.7, gamma=0.75)"
            ),
        },
        "samples": int(len(y)),
        "maps": int(len(set(groups.tolist()))),
        "feature_dimensions": int(x.shape[1]),
        "label_counts": dict(sorted(Counter(y_chars.tolist()).items())),
        "training_maps": sorted(set(groups[outer_train].tolist())),
        "validation_maps": sorted(set(groups[outer_test].tolist())),
        "epochs_per_head": epochs,
        "batch_size": batch_size,
        "experiments": experiments,
        "selected_mode": selected_mode,
        "outer_validation": outer_metrics,
        "auto_apply_eligible": (
            outer_metrics["accuracy"] >= 0.90
            and outer_metrics["macro_f1"] >= 0.85
            and float(outer_metrics["camp_support"].get("recall", 0.0)) >= 0.90
            and float(outer_metrics["fence_support"].get("recall", 0.0)) >= 0.95
        ),
        "excluded_conflicting_assets": excluded,
        "sources": sources,
    }
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Fit the selected model on all reviewed/weak data for future review suggestions.
    all_indices = np.arange(len(y))
    scaled, mean, std = scale_features(x, all_indices)
    final_model = train_head(
        selected_mode, scaled, y, weights, classes, epochs, batch_size,
    )
    torch.save({
        "state_dict": final_model.state_dict(),
        "feature_count": int(x.shape[1]),
        "classes": classes.tolist(),
        "mean": mean,
        "std": std,
        "camp_threshold": camp_threshold,
        "fence_threshold": fence_threshold,
        "selected_mode": selected_mode,
        "validation": outer_metrics,
        "auto_apply_eligible": report["auto_apply_eligible"],
    }, output_model)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=1024)
    args = parser.parse_args()
    result = train(args.model, args.report, args.epochs, args.batch_size)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
