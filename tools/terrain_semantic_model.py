"""Train, predict, and audit grid terrain labels from Mengde battle-map images.

Stage Lua files are treated as weak supervision. Validation is split by complete
map assets, and low-confidence predictions are never considered auto-approved.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
from PIL import Image, ImageDraw
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import GroupShuffleSplit


ROOT = Path(__file__).resolve().parents[1]
STAGE_DIR = ROOT / "game" / "sce" / "dongzhou" / "stage"
MAP_DIR = ROOT / "assets" / "lzc" / "map"
DEFAULT_MODEL = ROOT / "output" / "terrain_model" / "terrain_semantic.joblib"
DEFAULT_REPORT = ROOT / "output" / "terrain_model" / "training_report.json"
IMPASSABLE = {"W", "r", "~", "P"}
RESTORATIVE = {"G", "D", "C"}
CHAR_NAMES = {
    "f": "Flatland", "g": "Grass", "F": "Forest", "w": "Wasteland",
    "m": "Mountain", "r": "RockyMountain", "W": "Wall", "~": "Water",
    "c": "Watchtower", "b": "Storehouse", "e": "Camp", "G": "Gate",
    "D": "DeerFort", "P": "Fence", "i": "CityInterior",
    "h": "Residence", "C": "Castle",
}


def parse_stage(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    asset_match = re.search(r'map_asset\s*=\s*"([^"]+)"', text)
    size_match = re.search(r"size\s*=\s*\{\s*(\d+)\s*,\s*(\d+)\s*\}", text)
    terrain_match = re.search(
        r"terrain\s*=\s*\{(?P<body>.*?)\}\s*,\s*(?:has_terrain_layers|file)",
        text,
        re.DOTALL,
    )
    if not (asset_match and size_match and terrain_match):
        return None
    rows = re.findall(r'"([A-Za-z~]+)"', terrain_match.group("body"))
    width, height = map(int, size_match.groups())
    if len(rows) != height or any(len(row) != width for row in rows):
        return None
    asset = MAP_DIR / asset_match.group(1)
    if not asset.is_file():
        return None
    return {
        "path": path,
        "text": text,
        "asset": asset,
        "width": width,
        "height": height,
        "rows": rows,
    }


def iter_stages() -> Iterable[dict]:
    for path in sorted(STAGE_DIR.glob("*.lua")):
        stage = parse_stage(path)
        if stage:
            yield stage


def cell_bounds(image: Image.Image, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
    return (
        round(x * image.width / width), round(y * image.height / height),
        round((x + 1) * image.width / width), round((y + 1) * image.height / height),
    )


def patch_features(patch: Image.Image) -> np.ndarray:
    rgb = np.asarray(patch.convert("RGB").resize((8, 8)), dtype=np.float32) / 255.0
    hsv = np.asarray(patch.convert("HSV"), dtype=np.float32) / 255.0
    gray = np.asarray(patch.convert("L"), dtype=np.float32) / 255.0
    gx = np.abs(np.diff(gray, axis=1))
    gy = np.abs(np.diff(gray, axis=0))
    summary = np.concatenate([
        rgb.reshape(-1), rgb.mean((0, 1)), rgb.std((0, 1)),
        hsv.mean((0, 1)), hsv.std((0, 1)),
        np.quantile(gray, [0.1, 0.25, 0.5, 0.75, 0.9]),
        np.array([gx.mean(), gx.std(), gy.mean(), gy.std()], dtype=np.float32),
    ])
    return summary.astype(np.float32)


def image_cells(image: Image.Image, width: int, height: int) -> np.ndarray:
    return np.stack([
        patch_features(image.crop(cell_bounds(image, x, y, width, height)))
        for y in range(height) for x in range(width)
    ])


def build_dataset() -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    groups: list[str] = []
    sources: list[dict] = []
    for stage in iter_stages():
        image = Image.open(stage["asset"]).convert("RGB")
        cells = image_cells(image, stage["width"], stage["height"])
        flat_labels = list("".join(stage["rows"]))
        features.append(cells)
        labels.extend(flat_labels)
        groups.extend([stage["asset"].name] * len(flat_labels))
        sources.append({
            "stage": stage["path"].stem, "asset": stage["asset"].name,
            "cells": len(flat_labels), "image_size": list(image.size),
        })
    if not features:
        raise RuntimeError("No stage/image pairs were found")
    return np.concatenate(features), np.asarray(labels), np.asarray(groups), sources


def train(model_path: Path, report_path: Path) -> dict:
    x, y, groups, sources = build_dataset()
    unique_groups = np.unique(groups)
    if len(unique_groups) < 2:
        raise RuntimeError("At least two distinct map assets are required")
    train_idx, test_idx = next(GroupShuffleSplit(
        n_splits=1, test_size=0.25, random_state=20260809
    ).split(x, y, groups))
    validation_model = ExtraTreesClassifier(
        n_estimators=60, max_depth=14, max_features="sqrt", min_samples_leaf=4,
        class_weight="balanced_subsample", random_state=20260809, n_jobs=-1,
    ).fit(x[train_idx], y[train_idx])
    predicted = validation_model.predict(x[test_idx])
    report = {
        "supervision": "weak labels parsed from stage Lua terrain arrays",
        "split": "grouped by complete map asset",
        "samples": int(len(y)), "maps": int(len(unique_groups)),
        "training_maps": sorted(set(groups[train_idx].tolist())),
        "validation_maps": sorted(set(groups[test_idx].tolist())),
        "label_counts": dict(sorted(Counter(y.tolist()).items())),
        "accuracy": float(accuracy_score(y[test_idx], predicted)),
        "macro_f1": float(f1_score(y[test_idx], predicted, average="macro")),
        "classes": classification_report(
            y[test_idx], predicted, output_dict=True, zero_division=0
        ),
        "sources": sources,
    }
    report["auto_apply_eligible"] = (
        report["accuracy"] >= 0.90 and report["macro_f1"] >= 0.85
    )
    final_model = ExtraTreesClassifier(
        n_estimators=80, max_depth=14, max_features="sqrt", min_samples_leaf=4,
        class_weight="balanced_subsample", random_state=20260809, n_jobs=-1,
    ).fit(x, y)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "classifier": final_model, "characters": CHAR_NAMES,
        "feature_version": 1, "trained_maps": sorted(unique_groups.tolist()),
        "validation": {
            "accuracy": report["accuracy"], "macro_f1": report["macro_f1"],
            "auto_apply_eligible": report["auto_apply_eligible"],
        },
    }, model_path)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def predict(model_path: Path, image_path: Path, width: int, height: int,
            output_path: Path, threshold: float) -> dict:
    bundle = joblib.load(model_path)
    classifier = bundle["classifier"]
    image = Image.open(image_path).convert("RGB")
    probabilities = classifier.predict_proba(image_cells(image, width, height))
    best = probabilities.argmax(axis=1)
    chars = classifier.classes_[best]
    confidence = probabilities[np.arange(len(best)), best]
    rows = ["".join(chars[y * width:(y + 1) * width]) for y in range(height)]
    review = [
        {"x": i % width, "y": i // width, "predicted": str(chars[i]),
         "terrain": CHAR_NAMES.get(str(chars[i]), "Unknown"),
         "confidence": round(float(confidence[i]), 4)}
        for i in range(len(chars)) if confidence[i] < threshold
    ]
    payload = {
        "image": str(image_path), "grid": [width, height], "rows": rows,
        "threshold": threshold, "review_required": review,
        "mean_confidence": float(confidence.mean()),
        "minimum_confidence": float(confidence.min()),
        "auto_apply": bool(
            bundle.get("validation", {}).get("auto_apply_eligible", False)
            and not review
        ),
        "warning": "Predictions are suggestions; review low-confidence cells and structural rules.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    draw_prediction_overlay(image, chars, confidence, width, height, threshold,
                            output_path.with_suffix(".png"))
    return payload


def draw_prediction_overlay(image: Image.Image, chars: np.ndarray, confidence: np.ndarray,
                            width: int, height: int, threshold: float, path: Path) -> None:
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    for i, char in enumerate(chars):
        x, y = i % width, i // width
        left, top, right, bottom = cell_bounds(overlay, x, y, width, height)
        color = (230, 48, 48) if confidence[i] < threshold else (255, 230, 40)
        draw.rectangle((left, top, right - 1, bottom - 1), outline=color, width=2)
        draw.text((left + 3, top + 3), f"{char} {confidence[i]:.2f}", fill=color,
                  stroke_width=2, stroke_fill=(0, 0, 0))
    overlay.save(path, "PNG", compress_level=3)


def audit(stage_path: Path) -> dict:
    stage = parse_stage(stage_path)
    if not stage:
        raise RuntimeError(f"Could not parse stage or map asset: {stage_path}")
    rows, text = stage["rows"], stage["text"]
    width, height = stage["width"], stage["height"]
    positions = [(int(x), int(y)) for x, y in re.findall(
        r'(?:position\s*=\s*|Enum\.force\.\w+\s*,\s*)\{\s*(\d+)\s*,\s*(\d+)\s*\}', text
    )]
    sites = {(int(x), int(y)) for x, y in re.findall(
        r'id\s*=\s*"[^"]+"[^\r\n]*position\s*=\s*\{\s*(\d+)\s*,\s*(\d+)\s*\}', text
    )}
    errors: list[str] = []
    for x, y in positions:
        if not (0 <= x < width and 0 <= y < height):
            errors.append(f"position outside map: ({x},{y})")
        elif rows[y][x] in IMPASSABLE:
            errors.append(f"unit/deploy position on impassable {rows[y][x]}: ({x},{y})")
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char in RESTORATIVE and (x, y) not in sites:
                errors.append(f"restorative {char} has no site: ({x},{y})")
            if char == "W":
                neighbors = sum(
                    0 <= nx < width and 0 <= ny < height and rows[ny][nx] in {"W", "G"}
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                )
                if neighbors == 0:
                    errors.append(f"isolated wall: ({x},{y})")
    return {
        "stage": str(stage_path), "asset": str(stage["asset"]),
        "grid": [width, height], "errors": errors, "ok": not errors,
    }


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
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    if args.command == "train":
        result = train(args.model, args.report)
    elif args.command == "predict":
        result = predict(args.model, args.image, args.width, args.height,
                         args.output, args.threshold)
    else:
        result = audit(args.stage)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
