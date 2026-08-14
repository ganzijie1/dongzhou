"""Train a selective natural-terrain adapter from trusted real cells.

This model is deliberately separate from the structural terrain contract.  It
only predicts f/g/F/m and abstains when its metric and discriminative heads do
not agree.  Weak Lua rows are never used as ground truth here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.cluster import MiniBatchKMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.terrain_semantic_dinov3 import cached_cells, dino_cells


CLASSES = np.asarray(["f", "g", "F", "m"])
TRUSTED_MANIFESTS = [
    ROOT / "output/terrain_model/m008_large_v2_manifest.json",
    ROOT / "output/terrain_model/m058_fully_reviewed_manifest.json",
]
TEXTURES = {
    "g": [
        ROOT / "assets/lzc/map_sources/haojing/grass.png",
        ROOT / "assets/lzc/map_sources/changshao/grass.png",
    ],
    "f": [ROOT / "assets/lzc/map_sources/changshao/plain.png"],
}
MODEL = ROOT / "output/terrain_model/terrain_trusted_adapter.pt"
REPORT = ROOT / "output/terrain_model/terrain_trusted_adapter_report.json"
SEED = 20260813


class CosineAdapter(nn.Module):
    def __init__(self, feature_count: int, hidden: int = 128):
        super().__init__()
        self.adapter = nn.Sequential(
            nn.Linear(feature_count, hidden), nn.LayerNorm(hidden), nn.GELU(),
            nn.Dropout(0.08), nn.Linear(hidden, hidden),
        )
        self.classifier = nn.Parameter(torch.empty(len(CLASSES), hidden))
        nn.init.normal_(self.classifier, std=0.02)

    def embed(self, features: torch.Tensor) -> torch.Tensor:
        return nn.functional.normalize(self.adapter(features), dim=-1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        embedding = self.embed(features)
        weights = nn.functional.normalize(self.classifier, dim=-1)
        return 16.0 * embedding @ weights.T


def class_index(labels: np.ndarray) -> np.ndarray:
    return np.asarray(
        [int(np.flatnonzero(CLASSES == value)[0]) for value in labels],
        dtype=np.int64,
    )


def trusted_manifest_cells(manifest_path: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    width, height = map(int, manifest["grid"])
    image_path = ROOT / manifest["map"]
    features = cached_cells(image_path, width, height)
    labels = np.asarray(list("".join(manifest["terrain_rows"])))
    mixed = {
        (int(item["position"][0]), int(item["position"][1]))
        for item in manifest.get("terrain_layers", [])
    }
    structure = {
        tuple(map(int, point))
        for field in ("fence_cells", "camp_cells")
        for point in manifest.get(field, [])
    }
    keep, groups, provenance = [], [], []
    for index, label in enumerate(labels):
        x, y = index % width, index // width
        if label not in set(CLASSES) or (x, y) in mixed or (x, y) in structure:
            continue
        keep.append(index)
        groups.append(f"{image_path.stem}-block-{x // 5}-{y // 5}")
        provenance.append({"source": image_path.name, "position": [x, y], "label": label})
    return features[keep], labels[keep], np.asarray(groups), provenance


def trusted_map_cells() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    all_x, all_y, all_groups, all_maps, provenance = [], [], [], [], []
    for manifest_path in TRUSTED_MANIFESTS:
        features, labels, groups, source = trusted_manifest_cells(manifest_path)
        all_x.append(features)
        all_y.append(labels)
        all_groups.append(groups)
        all_maps.extend([Path(source[0]["source"]).name] * len(labels))
        provenance.extend(source)
    return (
        np.concatenate(all_x), np.concatenate(all_y), np.concatenate(all_groups),
        np.asarray(all_maps), provenance,
    )


def texture_cells() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    all_x, all_y, all_groups, provenance = [], [], [], []
    # A 10x10 tile keeps ViT attention memory bounded and makes source splits spatial.
    cells_per_tile, source_cell = 10, 48
    for label, paths in TEXTURES.items():
        for path in paths:
            image = Image.open(path).convert("RGB")
            tiles_x = image.width // (cells_per_tile * source_cell)
            tiles_y = image.height // (cells_per_tile * source_cell)
            for tile_y in range(tiles_y):
                for tile_x in range(tiles_x):
                    box = (
                        tile_x * cells_per_tile * source_cell,
                        tile_y * cells_per_tile * source_cell,
                        (tile_x + 1) * cells_per_tile * source_cell,
                        (tile_y + 1) * cells_per_tile * source_cell,
                    )
                    crop = image.crop(box)
                    cache_key = hashlib.sha256(
                        path.read_bytes() + f"{tile_x},{tile_y}".encode("ascii")
                    ).hexdigest()[:16]
                    cache = ROOT / "output/terrain_model/dinov3_feature_cache" / (
                        f"trusted-{path.stem}-{tile_x}-{tile_y}-{cache_key}.npy"
                    )
                    if cache.is_file():
                        features = np.load(cache)
                    else:
                        features = dino_cells(crop, cells_per_tile, cells_per_tile)
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        np.save(cache, features)
                    count = len(features)
                    group = f"texture-{path.parent.name}-{path.stem}-{tile_x}-{tile_y}"
                    all_x.append(features)
                    all_y.extend([label] * count)
                    all_groups.extend([group] * count)
                    provenance.append({
                        "source": str(path.relative_to(ROOT)), "tile": [tile_x, tile_y],
                        "label": label, "cells": count,
                    })
    return np.concatenate(all_x), np.asarray(all_y), np.asarray(all_groups), provenance


def choose_group_split(labels: np.ndarray, groups: np.ndarray):
    best = None
    for attempt, (train, validation) in enumerate(GroupShuffleSplit(
        n_splits=80, test_size=0.25, random_state=SEED
    ).split(np.zeros(len(labels)), labels, groups)):
        if set(labels[train]) != set(CLASSES) or set(labels[validation]) != set(CLASSES):
            continue
        train_counts = Counter(labels[train]); validation_counts = Counter(labels[validation])
        balance = min(validation_counts.values()) / max(validation_counts.values())
        candidate = (balance, -attempt, train, validation)
        if best is None or candidate[:2] > best[:2]:
            best = candidate
    if best is None:
        raise RuntimeError("Could not construct a grouped split containing every class")
    return best[2], best[3]


def fit_adapter(x: np.ndarray, y: np.ndarray, epochs: int, device: torch.device):
    torch.manual_seed(SEED)
    model = CosineAdapter(x.shape[1]).to(device)
    counts = np.bincount(y, minlength=len(CLASSES)).astype(np.float32)
    sample_weights = 1.0 / np.maximum(counts[y], 1.0)
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)
    loader = DataLoader(
        TensorDataset(torch.from_numpy(x), torch.from_numpy(y)), batch_size=256,
        sampler=sampler, drop_last=False,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=5e-4)
    for _ in range(epochs):
        model.train()
        for features, target in loader:
            features, target = features.to(device), target.to(device)
            # MIC-inspired consistency is applied in feature space, not claimed as full MIC.
            mask_a = torch.rand_like(features).gt(0.04)
            mask_b = torch.rand_like(features).gt(0.04)
            logits_a = model(features * mask_a)
            logits_b = model(features * mask_b)
            probability = torch.softmax(logits_a, dim=1)
            pt = probability.gather(1, target[:, None]).squeeze(1).clamp_min(1e-6)
            focal = (-((1.0 - pt) ** 1.5) * pt.log()).mean()
            consistency = nn.functional.mse_loss(
                torch.softmax(logits_a, dim=1), torch.softmax(logits_b, dim=1)
            )
            loss = focal + 0.35 * consistency
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 3.0)
            optimizer.step()
    return model.eval()


@torch.inference_mode()
def adapter_outputs(model: CosineAdapter, x: np.ndarray, device: torch.device):
    tensor = torch.from_numpy(x).to(device)
    probabilities = torch.softmax(model(tensor), dim=1).cpu().numpy()
    embeddings = model.embed(tensor).cpu().numpy()
    return probabilities, embeddings


def fit_prototypes(embeddings: np.ndarray, labels: np.ndarray):
    prototypes, owners = [], []
    for class_id in range(len(CLASSES)):
        values = embeddings[labels == class_id]
        clusters = max(1, min(8, len(values) // 35))
        centers = MiniBatchKMeans(
            n_clusters=clusters, random_state=SEED + class_id, n_init=10,
            batch_size=256,
        ).fit(values).cluster_centers_
        centers /= np.maximum(np.linalg.norm(centers, axis=1, keepdims=True), 1e-8)
        prototypes.append(centers)
        owners.extend([class_id] * len(centers))
    return np.concatenate(prototypes), np.asarray(owners)


def prototype_probabilities(embeddings: np.ndarray, prototypes: np.ndarray, owners: np.ndarray):
    similarities = embeddings @ prototypes.T
    logits = np.full((len(embeddings), len(CLASSES)), -100.0, dtype=np.float32)
    for class_id in range(len(CLASSES)):
        class_scores = similarities[:, owners == class_id]
        top = np.sort(class_scores, axis=1)[:, -min(3, class_scores.shape[1]):]
        logits[:, class_id] = top.mean(axis=1) / 0.08
    logits -= logits.max(axis=1, keepdims=True)
    probability = np.exp(logits)
    return probability / probability.sum(axis=1, keepdims=True)


def select_threshold(probabilities: np.ndarray, truth: np.ndarray, agreement: np.ndarray):
    order = np.sort(probabilities, axis=1)
    confidence, margin = order[:, -1], order[:, -1] - order[:, -2]
    predicted = probabilities.argmax(axis=1)
    best = None
    for threshold in np.arange(0.55, 0.951, 0.025):
        for min_margin in np.arange(0.05, 0.351, 0.025):
            accepted = agreement & (confidence >= threshold) & (margin >= min_margin)
            if accepted.sum() < 20:
                continue
            precision = float((predicted[accepted] == truth[accepted]).mean())
            per_class = []
            for class_id in range(len(CLASSES)):
                chosen = accepted & (predicted == class_id)
                if chosen.sum() >= 3:
                    per_class.append(float((truth[chosen] == class_id).mean()))
            minimum_precision = min(per_class) if per_class else 0.0
            coverage = float(accepted.mean())
            qualifies = precision >= 0.90 and minimum_precision >= 0.80
            score = (int(qualifies), coverage, precision, minimum_precision)
            if best is None or score > best[0]:
                best = (score, float(threshold), float(min_margin))
    if best is None:
        return 0.95, 0.35
    return best[1], best[2]


def evaluate(truth: np.ndarray, probabilities: np.ndarray, agreement: np.ndarray,
             threshold: float, min_margin: float):
    predicted = probabilities.argmax(axis=1)
    order = np.sort(probabilities, axis=1)
    accepted = agreement & (order[:, -1] >= threshold) & (
        order[:, -1] - order[:, -2] >= min_margin
    )
    report = classification_report(
        truth, predicted, labels=np.arange(len(CLASSES)), target_names=CLASSES.tolist(),
        output_dict=True, zero_division=0,
    )
    accepted_accuracy = float((predicted[accepted] == truth[accepted]).mean()) if accepted.any() else 0.0
    return {
        "macro_f1": float(f1_score(truth, predicted, average="macro")),
        "coverage": float(accepted.mean()), "accepted_cells": int(accepted.sum()),
        "accepted_accuracy": accepted_accuracy,
        "disagreement_rate": float((~agreement).mean()),
        "classes": {label: report[label] for label in CLASSES},
        "confusion_matrix": confusion_matrix(truth, predicted).tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=40)
    args = parser.parse_args()
    map_x, map_y, map_groups, map_names, map_sources = trusted_map_cells()
    texture_x, texture_y, texture_groups, texture_sources = texture_cells()
    x = np.concatenate((map_x, texture_x)).astype(np.float32)
    labels = np.concatenate((map_y, texture_y))
    groups = np.concatenate((map_groups, texture_groups))
    train, validation = choose_group_split(labels, groups)
    y = class_index(labels)
    scaler = StandardScaler().fit(x[train])
    scaled = scaler.transform(x).astype(np.float32)
    baseline = make_pipeline(
        StandardScaler(), LogisticRegression(
            C=0.03, class_weight="balanced", max_iter=2500, random_state=SEED,
        ),
    ).fit(x[train], labels[train])
    baseline_prediction = baseline.predict(x[validation])
    baseline_report = classification_report(
        labels[validation], baseline_prediction, labels=CLASSES.tolist(),
        output_dict=True, zero_division=0,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = fit_adapter(scaled[train], y[train], args.epochs, device)
    train_probability, train_embedding = adapter_outputs(model, scaled[train], device)
    validation_probability, validation_embedding = adapter_outputs(model, scaled[validation], device)
    prototypes, owners = fit_prototypes(train_embedding, y[train])
    owners = owners.astype(np.int64)
    metric_probability = prototype_probabilities(validation_embedding, prototypes, owners)
    ensemble = 0.55 * validation_probability + 0.45 * metric_probability
    agreement = validation_probability.argmax(1) == metric_probability.argmax(1)
    threshold, min_margin = select_threshold(ensemble, y[validation], agreement)
    result = evaluate(y[validation], ensemble, agreement, threshold, min_margin)
    payload = {
        "purpose": "selective f/g/F/m classifier; structures remain contract-owned",
        "feature_backend": "frozen DINOv3 dense directional features plus handcrafted texture",
        "method": "cosine adapter + focal loss + masked feature consistency + multi-prototype ensemble",
        "supervision": "two fully reviewed maps plus named real texture sources; no weak Lua rows",
        "split": "grouped by 5x5 map blocks and non-overlapping 10x10 texture tiles",
        "device": str(device), "epochs": args.epochs,
        "samples": int(len(labels)), "training_cells": int(len(train)),
        "validation_cells": int(len(validation)),
        "label_counts": dict(sorted(Counter(labels.tolist()).items())),
        "training_groups": sorted(set(groups[train].tolist())),
        "validation_groups": sorted(set(groups[validation].tolist())),
        "baseline_linear_macro_f1": float(np.mean([
            baseline_report[label]["f1-score"] for label in CLASSES
        ])),
        "baseline_classes": {label: baseline_report[label] for label in CLASSES},
        "selection": {"confidence": threshold, "margin": min_margin, "requires_head_agreement": True},
        "validation": result,
        "trusted_maps": sorted(set(map_names.tolist())),
        "production_promotion": False, "auto_apply": False,
        "limitations": [
            "Production promotion is decided by the separate leave-one-map-out report.",
            "Snow, rivers, walls, fences, camps and castles are outside this head.",
            "Automatic Lua writes remain disabled even after model promotion.",
        ],
        "provenance": {"trusted_map_cells": map_sources, "texture_tiles": texture_sources},
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": model.cpu().state_dict(), "feature_count": int(x.shape[1]),
        "hidden": 128, "classes": CLASSES.tolist(), "mean": scaler.mean_.astype(np.float32),
        "scale": scaler.scale_.astype(np.float32), "prototypes": prototypes.astype(np.float32),
        "prototype_owners": owners, "confidence_threshold": threshold,
        "margin_threshold": min_margin, "auto_apply": False,
    }, MODEL)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "baseline_macro_f1": payload["baseline_linear_macro_f1"],
        "adapter_macro_f1": result["macro_f1"], "selective_coverage": result["coverage"],
        "selective_accuracy": result["accepted_accuracy"], "report": str(REPORT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
