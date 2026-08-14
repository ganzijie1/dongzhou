"""Evaluate Freeciv full-map weak supervision on Mengde strict map LOMO."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

import evaluate_terrain_domain_shift as audit
from terrain_semantic_dinov3 import dino_cells


ROOT = Path(__file__).resolve().parents[1]
FREECIV = ROOT / "output/external/freeciv"
CACHE = ROOT / "output/terrain_model/dinov3_feature_cache"
REPORT = ROOT / "output/terrain_model/terrain_freeciv_lomo_report.json"
CODE_TO_LABEL = {"p": "f", "g": "g", "f": "F", "h": "m", "m": "m"}
SPRITE_ROW = {"p": 1, "g": 2, "f": 3, "h": 4, "m": 5}
SCENARIOS = (
    "earth-small.sav", "europe.sav", "british-isles.sav", "france.sav",
    "iberian-peninsula.sav", "italy.sav", "japan.sav", "north_america.sav",
)


def sprites() -> dict[str, Image.Image]:
    sheet = Image.open(FREECIV / "data/amplio2/terrain1.png").convert("RGBA")
    result = {}
    for code, row in SPRITE_ROW.items():
        tile = sheet.crop((1, 1 + row * 48, 97, 1 + (row + 1) * 48))
        # Preserve the whole isometric texture but adapt it to the square-cell encoder.
        result[code] = tile.resize((48, 48), Image.Resampling.LANCZOS)
    return result


def scenario_rows(path: Path) -> list[str]:
    rows = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r't(\d{4})="(.*)"$', line)
        if match:
            rows[int(match.group(1))] = match.group(2)
    return [rows[index] for index in sorted(rows)]


def candidate_windows(rows: list[str], size: int = 10):
    height, width = len(rows), min(map(len, rows))
    candidates = []
    for y in range(0, height - size + 1, size):
        for x in range(0, width - size + 1, size):
            codes = [rows[yy][x:x + size] for yy in range(y, y + size)]
            labels = [CODE_TO_LABEL.get(code) for row in codes for code in row]
            supported = sum(label is not None for label in labels)
            represented = len({label for label in labels if label is not None})
            if supported >= 65 and represented >= 2:
                candidates.append((represented, supported, x, y, codes, labels))
    candidates.sort(reverse=True)
    return candidates[:8]


def render_window(codes, tile_images, style: int) -> Image.Image:
    palette = {
        "p": (143, 127, 88), "g": (93, 127, 70), "f": (54, 87, 48),
        "h": (116, 100, 78), "m": (91, 83, 74), " ": (54, 87, 117),
        ":": (37, 67, 101), "+": (77, 113, 139),
    }
    image = Image.new("RGB", (480, 480), (117, 105, 77))
    for y, row in enumerate(codes):
        for x, code in enumerate(row):
            base = Image.new("RGBA", (48, 48), palette.get(code, (124, 111, 78)) + (255,))
            if code in tile_images:
                base = Image.alpha_composite(base, tile_images[code])
            image.paste(base.convert("RGB"), (x * 48, y * 48))
    if style:
        image = ImageEnhance.Color(image).enhance(0.78 + 0.16 * style)
        image = ImageEnhance.Contrast(image).enhance(0.90 + 0.08 * style)
    return image


def freeciv_cells():
    tile_images = sprites()
    all_x, all_y, all_groups = [], [], []
    provenance = []
    for scenario in SCENARIOS:
        path = FREECIV / "data/scenarios" / scenario
        rows = scenario_rows(path)
        for rank, (_, supported, x, y, codes, labels) in enumerate(candidate_windows(rows)):
            style = rank % 3
            digest = hashlib.sha256(
                (scenario + str(x) + str(y) + str(style)).encode("ascii")
                + (FREECIV / "data/amplio2/terrain1.png").read_bytes()
            ).hexdigest()[:12]
            cache = CACHE / f"freeciv-{Path(scenario).stem}-{x}-{y}-{digest}.npy"
            if cache.is_file():
                features = np.load(cache)
            else:
                features = dino_cells(render_window(codes, tile_images, style), 10, 10)
                CACHE.mkdir(parents=True, exist_ok=True)
                np.save(cache, features)
            keep = np.asarray([label is not None for label in labels])
            all_x.append(features[keep])
            all_y.extend(label for label in labels if label is not None)
            all_groups.extend([f"freeciv-{Path(scenario).stem}-{x}-{y}"] * int(keep.sum()))
            provenance.append({"scenario": scenario, "origin": [x, y],
                               "supported_cells": supported})
    return np.concatenate(all_x), np.asarray(all_y), np.asarray(all_groups), provenance


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
    external_x, external_labels, external_groups, provenance = freeciv_cells()
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
    payload = {
        "evaluation": "leave-one-fully-reviewed-map-out",
        "external_source": "Freeciv GPL-2.0 full scenario maps + official terrain codes",
        "external_role": "training-only weak semantic pretraining",
        "external_cells": int(len(external_labels)), "windows": provenance,
        "folds": folds,
        "pooled": audit.metrics(np.concatenate(truths), np.concatenate(predictions)),
        "production_promotion": False, "auto_apply": False,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["pooled"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
