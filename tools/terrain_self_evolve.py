"""Build and train a five-class self-evolving natural-terrain specialist.

Labels are known before rendering, so model predictions can never become their
own training truth. Splits are grouped by complete maps. Snow changes only open
ground to ``s``; snow-covered forests and mountains remain ``F`` and ``m``.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from terrain_semantic_model import cell_bounds, image_cells


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "output/terrain_model/self_evolve_fgsFm"
MODEL = ROOT / "output/terrain_model/terrain_fgsFm_self_evolved.joblib"
REPORT = ROOT / "output/terrain_model/terrain_fgsFm_self_evolution_report.json"
CLASSES = np.asarray(["f", "g", "s", "F", "m"])
NAMES = {"f": "Flatland", "g": "Grass", "s": "Snow", "F": "Forest", "m": "Mountain"}
SEED = 20260812
GRID = (8, 6)
CELL = 40


def smooth_regions(rng: np.random.Generator, width: int, height: int, weights: np.ndarray) -> np.ndarray:
    seed_count = int(rng.integers(6, 11))
    seeds = np.column_stack((rng.uniform(0, width, seed_count), rng.uniform(0, height, seed_count)))
    labels = rng.choice(len(CLASSES), seed_count, p=weights / weights.sum())
    yy, xx = np.mgrid[0:height, 0:width]
    distance = (xx[..., None] - seeds[:, 0]) ** 2 + (yy[..., None] - seeds[:, 1]) ** 2
    grid = labels[distance.argmin(axis=2)]
    # A small majority pass produces broad natural regions without erasing narrow real bands.
    for _ in range(2):
        result = grid.copy()
        for y in range(height):
            for x in range(width):
                local = grid[max(0, y - 1):min(height, y + 2), max(0, x - 1):min(width, x + 2)]
                counts = np.bincount(local.reshape(-1), minlength=len(CLASSES))
                if counts.max() >= 5:
                    result[y, x] = counts.argmax()
        grid = result
    # Every map contains at least one cell of every class; class-level metrics remain meaningful.
    for label in range(len(CLASSES)):
        if not np.any(grid == label):
            grid[int(rng.integers(height)), int(rng.integers(width))] = label
    return grid


def cell_texture(label: str, rng: np.random.Generator, snowy_variant: bool) -> Image.Image:
    size = CELL + 16
    if label == "f":
        base = np.array([150, 139, 101]) + rng.integers(-22, 23, 3)
    elif label == "g":
        base = np.array([92, 126, 69]) + rng.integers(-18, 19, 3)
    elif label == "s":
        base = np.array([219, 225, 220]) + rng.integers(-9, 10, 3)
    elif label == "F":
        base = np.array([202, 210, 199]) if snowy_variant else np.array([71, 101, 57])
        base += rng.integers(-13, 14, 3)
    else:
        base = np.array([177, 181, 176]) if snowy_variant else np.array([113, 105, 91])
        base += rng.integers(-15, 16, 3)
    noise = rng.normal(0, 11 if label != "s" else 6, (size, size, 1))
    array = np.clip(base.reshape(1, 1, 3) + noise, 0, 255).astype(np.uint8)
    image = Image.fromarray(array, "RGB").filter(ImageFilter.GaussianBlur(0.7)).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    if label == "f":
        for _ in range(16):
            x, y = rng.integers(0, size, 2); length = int(rng.integers(5, 17))
            draw.line((x, y, min(size, x + length), y + int(rng.integers(-2, 3))), fill=(92, 79, 55, 85), width=1)
    elif label == "g":
        for _ in range(45):
            x, y = rng.integers(0, size, 2); h = int(rng.integers(3, 10))
            draw.line((x, y, x + int(rng.integers(-2, 3)), max(0, y - h)), fill=(42, 85, 38, 120), width=1)
    elif label == "s":
        for _ in range(12):
            x, y = rng.integers(0, size, 2); rx = int(rng.integers(5, 15))
            draw.arc((x - rx, y - 3, x + rx, y + 5), 190, 350, fill=(125, 153, 169, 65), width=2)
    elif label == "F":
        for _ in range(18):
            x, y = rng.integers(3, size - 3, 2); radius = int(rng.integers(4, 10))
            canopy = (54, 91, 43, 235) if snowy_variant else (35, 78, 35, 235)
            draw.ellipse((x - radius, y - radius // 2, x + radius, y + radius), fill=canopy)
            draw.line((x, y + radius // 2, x, y + radius + 3), fill=(74, 52, 34, 210), width=2)
            if snowy_variant:
                draw.arc((x - radius, y - radius // 2, x + radius, y + radius // 2), 185, 350, fill=(235, 240, 237, 225), width=3)
    else:
        for _ in range(10):
            x, y = rng.integers(3, size - 3, 2); rw = int(rng.integers(8, 18)); rh = int(rng.integers(7, 16))
            rock = (101, 105, 105, 245) if snowy_variant else (87, 79, 69, 245)
            points = [(x - rw, y + rh), (x - rw // 3, y - rh), (x + rw // 4, y - rh // 3), (x + rw, y + rh)]
            draw.polygon(points, fill=rock, outline=(61, 61, 58, 225))
            draw.line((x - rw // 3, y - rh, x + rw // 4, y + rh), fill=(174, 176, 170, 115), width=2)
            if snowy_variant:
                draw.line((x - rw // 3, y - rh, x + rw // 3, y - rh // 4), fill=(240, 243, 240, 230), width=3)
    return image


def render_map(labels: np.ndarray, rng: np.random.Generator) -> Image.Image:
    width, height = labels.shape[1], labels.shape[0]
    canvas = Image.new("RGBA", (width * CELL, height * CELL), (110, 112, 88, 255))
    snow_weather = bool(rng.random() < 0.34)
    for y in range(height):
        for x in range(width):
            label = str(CLASSES[labels[y, x]])
            # Snow weather changes the palette of forests/mountains, never their semantic label.
            snowy_variant = snow_weather and label in {"F", "m"} and rng.random() < 0.9
            texture = cell_texture(label, rng, snowy_variant)
            canvas.alpha_composite(texture, (x * CELL - 8, y * CELL - 8))
    merged = canvas.filter(ImageFilter.GaussianBlur(float(rng.uniform(0.15, 0.55))))
    merged = ImageEnhance.Color(merged.convert("RGB")).enhance(float(rng.uniform(0.82, 1.18)))
    merged = ImageEnhance.Contrast(merged).enhance(float(rng.uniform(0.88, 1.12)))
    return merged


def generate_map(index: int, split: str, weights: np.ndarray) -> dict:
    rng = np.random.default_rng(SEED + index * 7919)
    labels = smooth_regions(rng, GRID[0], GRID[1], weights)
    image = render_map(labels, rng)
    name = f"terrain-{index:04d}.png"
    path = DATASET / split / name
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True)
    rows = ["".join(CLASSES[labels[y]].tolist()) for y in range(GRID[1])]
    return {"id": index, "split": split, "image": str(path.relative_to(ROOT)), "grid": list(GRID), "rows": rows}


def metrics(truth: np.ndarray, prediction: np.ndarray) -> dict:
    report = classification_report(truth, prediction, labels=CLASSES.tolist(), output_dict=True, zero_division=0)
    return {
        "accuracy": float(accuracy_score(truth, prediction)),
        "macro_f1": float(f1_score(truth, prediction, labels=CLASSES.tolist(), average="macro")),
        "minimum_class_f1": float(min(report[c]["f1-score"] for c in CLASSES)),
        "classes": {c: report[c] for c in CLASSES},
        "confusion_matrix": confusion_matrix(truth, prediction, labels=CLASSES.tolist()).tolist(),
    }


def load_entries(entries: list[dict]):
    features, labels, groups = [], [], []
    for entry in entries:
        image = Image.open(ROOT / entry["image"]).convert("RGB")
        cells = image_cells(image, *entry["grid"])
        truth = np.asarray(list("".join(entry["rows"])))
        features.append(cells); labels.append(truth); groups.extend([entry["id"]] * len(truth))
    return np.concatenate(features), np.concatenate(labels), np.asarray(groups)


def fit(x: np.ndarray, y: np.ndarray, seed: int):
    return ExtraTreesClassifier(
        n_estimators=180, max_depth=22, max_features=0.72, min_samples_leaf=2,
        class_weight="balanced_subsample", random_state=seed, n_jobs=-1,
    ).fit(x, y)


def confusion_weights(result: dict) -> np.ndarray:
    matrix = np.asarray(result["confusion_matrix"], dtype=np.float64)
    errors = matrix.sum(axis=1) - np.diag(matrix)
    f1 = np.asarray([result["classes"][c]["f1-score"] for c in CLASSES])
    weights = 1.0 + errors / np.maximum(matrix.sum(axis=1), 1.0) + (1.0 - f1)
    return weights / weights.sum()


def build_montage(entries: list[dict], output: Path):
    thumbs = []
    for entry in entries[:25]:
        thumbs.append(Image.open(ROOT / entry["image"]).convert("RGB").resize((256, 192)))
    montage = Image.new("RGB", (5 * 256, 5 * 192), (30, 30, 30))
    for i, thumb in enumerate(thumbs):
        montage.paste(thumb, ((i % 5) * 256, (i // 5) * 192))
    output.parent.mkdir(parents=True, exist_ok=True); montage.save(output, "PNG")


def run(count: int = 1000):
    if count != 1000:
        raise ValueError("the acceptance protocol is fixed at exactly 1000 complete maps")
    if DATASET.exists():
        shutil.rmtree(DATASET)
    DATASET.mkdir(parents=True)
    entries = []
    weights = np.ones(len(CLASSES), dtype=np.float64) / len(CLASSES)
    # Validation and final test maps are generated once from a fixed balanced distribution.
    for index in range(800, 1000):
        split = "validation" if index < 900 else "test"
        entries.append(generate_map(index, split, weights))

    history, promoted_model = [], None
    train_entries = []
    starts = [0, 200, 500]
    ends = [200, 500, 800]
    validation_entries = [e for e in entries if e["split"] == "validation"]
    validation_x, validation_y, _ = load_entries(validation_entries)
    best = None
    for generation, (start, end) in enumerate(zip(starts, ends), 1):
        for index in range(start, end):
            entry = generate_map(index, "train", weights)
            entries.append(entry); train_entries.append(entry)
        train_x, train_y, _ = load_entries(train_entries)
        candidate = fit(train_x, train_y, SEED + generation)
        result = metrics(validation_y, candidate.predict(validation_x))
        promote = best is None or (
            result["macro_f1"] >= best["macro_f1"] - 1e-9
            and result["minimum_class_f1"] >= best["minimum_class_f1"] - 1e-9
        )
        history.append({
            "generation": generation, "training_maps": len(train_entries),
            "hard_class_sampling": {c: float(weights[i]) for i, c in enumerate(CLASSES)},
            "validation": result, "promoted": promote,
        })
        if promote:
            best, promoted_model = result, candidate
        weights = confusion_weights(result)

    if promoted_model is None:
        raise RuntimeError("no candidate was promoted")
    test_entries = [e for e in entries if e["split"] == "test"]
    test_x, test_y, _ = load_entries(test_entries)
    test_result = metrics(test_y, promoted_model.predict(test_x))
    acceptance = (
        test_result["macro_f1"] >= 0.92
        and test_result["minimum_class_f1"] >= 0.88
        and all(test_result["classes"][c]["recall"] >= 0.88 for c in CLASSES)
    )
    ordered = sorted(entries, key=lambda e: e["id"])
    (DATASET / "manifest.json").write_text(json.dumps({
        "version": 1, "classes": NAMES, "snow_rule": "only white open ground is s; snowy F/m retain F/m",
        "split": {"train": 800, "validation": 100, "test": 100}, "maps": ordered,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    build_montage(test_entries, DATASET / "test_montage.png")
    bundle = {
        "classifier": promoted_model, "classes": CLASSES.tolist(), "names": NAMES,
        "grid_cell_feature_version": 1, "confidence_threshold": 0.72,
        "snow_rule": "white open ground only; snowy forest/mountain keep F/m",
        "synthetic_acceptance": acceptance, "validation": best, "test": test_result,
        "auto_apply": False,
    }
    joblib.dump(bundle, MODEL)
    report = {
        "purpose": "five-class common visual terrain specialist",
        "classes": NAMES, "maps_generated": count, "split_by_complete_map": True,
        "truth_source": "programmatic pre-render terrain matrices; never model predictions",
        "evolution": history, "held_out_test": test_result,
        "synthetic_acceptance": acceptance,
        "production_promotion": False,
        "production_blocker": "must still beat incumbent on separately reviewed real-map fixtures",
        "auto_apply": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def predict(model_path: Path, image_path: Path, width: int, height: int, output: Path):
    bundle = joblib.load(model_path)
    image = Image.open(image_path).convert("RGB")
    probabilities = bundle["classifier"].predict_proba(image_cells(image, width, height))
    best = probabilities.argmax(axis=1)
    labels = bundle["classifier"].classes_[best]
    confidence = probabilities[np.arange(len(best)), best]
    payload = {
        "image": str(image_path), "grid": [width, height],
        "rows": ["".join(labels[y * width:(y + 1) * width]) for y in range(height)],
        "classes": NAMES, "snow_rule": bundle["snow_rule"],
        "review_required": [{"x": int(i % width), "y": int(i // width), "predicted": str(labels[i]),
                             "confidence": round(float(confidence[i]), 4)}
                            for i in np.flatnonzero(confidence < 0.72)],
        "auto_apply": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run"); run_parser.add_argument("--count", type=int, default=1000)
    pred = sub.add_parser("predict"); pred.add_argument("image", type=Path); pred.add_argument("--width", type=int, required=True)
    pred.add_argument("--height", type=int, required=True); pred.add_argument("--model", type=Path, default=MODEL)
    pred.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run": run(args.count)
    else: predict(args.model, args.image, args.width, args.height, args.output)


if __name__ == "__main__":
    main()
