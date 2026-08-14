"""Evaluate conservative CC0 weak supervision on the strict map LOMO split."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

import evaluate_terrain_domain_shift as audit
from terrain_semantic_dinov3 import dino_cells


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets/training/external_cc0/opengameart"
CACHE_DIR = ROOT / "output/terrain_model/dinov3_feature_cache"
REPORT = ROOT / "output/terrain_model/terrain_external_cc0_lomo_report.json"
SEED = 20260813


def usable_tiles(path: Path, tile_size: int = 32) -> list[Image.Image]:
    sheet = Image.open(path).convert("RGBA")
    tiles = []
    for y in range(0, sheet.height - tile_size + 1, tile_size):
        for x in range(0, sheet.width - tile_size + 1, tile_size):
            tile = sheet.crop((x, y, x + tile_size, y + tile_size))
            alpha = np.asarray(tile.getchannel("A"))
            if (alpha > 32).mean() < 0.72:
                continue
            background = Image.new("RGBA", tile.size, (126, 137, 105, 255))
            tiles.append(Image.alpha_composite(background, tile).convert("RGB"))
    if not tiles:
        raise RuntimeError(f"No usable tiles in {path}")
    return tiles


def mosaic_features(path: Path, label: str):
    tiles = usable_tiles(path)
    all_features, labels, groups = [], [], []
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    for variant in range(4):
        cache = CACHE_DIR / f"cc0-{path.stem}-v{variant}-{digest}.npy"
        if cache.is_file():
            features = np.load(cache)
        else:
            rng = np.random.default_rng(SEED + variant)
            canvas = Image.new("RGB", (10 * 48, 10 * 48))
            for index in range(100):
                tile = tiles[int(rng.integers(len(tiles)))].resize(
                    (48, 48), Image.Resampling.NEAREST
                )
                if variant:
                    tile = ImageEnhance.Color(tile).enhance(0.82 + 0.12 * variant)
                    tile = ImageEnhance.Brightness(tile).enhance(0.88 + 0.08 * variant)
                canvas.paste(tile, ((index % 10) * 48, (index // 10) * 48))
            features = dino_cells(canvas, 10, 10)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            np.save(cache, features)
        all_features.append(features)
        labels.extend([label] * len(features))
        groups.extend([f"cc0-{path.stem}-v{variant}"] * len(features))
    return np.concatenate(all_features), np.asarray(labels), np.asarray(groups)


def choose_c(x, y, groups):
    train, validation = audit.data.choose_group_split(audit.data.CLASSES[y], groups)
    best = None
    for c in (0.003, 0.01, 0.03, 0.1, 0.3):
        prediction = audit.fit_predict(x[train], y[train], x[validation], c)
        score = audit.f1_score(
            y[validation], prediction, labels=np.arange(len(audit.data.CLASSES)),
            average="macro", zero_division=0,
        )
        candidate = (score, -c, c)
        if best is None or candidate > best:
            best = candidate
    return float(best[2])


def main():
    map_x, map_labels, map_groups, map_names, _ = audit.data.trusted_map_cells()
    texture_x, texture_labels, texture_groups, _ = audit.data.texture_cells()
    grass = mosaic_features(SOURCE_DIR / "grasslands.png", "g")
    mountain = mosaic_features(SOURCE_DIR / "snowy_mountain.png", "m")
    external_x = np.concatenate((grass[0], mountain[0]))
    external_labels = np.concatenate((grass[1], mountain[1]))
    external_groups = np.concatenate((grass[2], mountain[2]))
    folds, truths, predictions = [], [], []
    for held_out in sorted(set(map_names.tolist())):
        source, target = map_names != held_out, map_names == held_out
        train_x = np.concatenate((map_x[source], texture_x, external_x)).astype(np.float32)
        train_labels = np.concatenate((map_labels[source], texture_labels, external_labels))
        train_y = audit.data.class_index(train_labels)
        train_groups = np.concatenate((map_groups[source], texture_groups, external_groups))
        test_x = map_x[target].astype(np.float32)
        test_y = audit.data.class_index(map_labels[target])
        c = choose_c(train_x, train_y, train_groups)
        prediction = audit.fit_predict(train_x, train_y, test_x, c)
        folds.append({"held_out_map": held_out, "selected_c": c,
                      **audit.metrics(test_y, prediction)})
        truths.append(test_y); predictions.append(prediction)
    pooled = audit.metrics(np.concatenate(truths), np.concatenate(predictions))
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "external_sources": ["CC0 grasslands", "CC0 snowy mountain"],
        "external_role": "training-only weak supervision",
        "external_cells": int(len(external_labels)),
        "folds": folds, "pooled": pooled,
        "production_promotion": False, "auto_apply": False,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(pooled, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
