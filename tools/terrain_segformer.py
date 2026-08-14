"""SegFormer terrain segmentation pipeline for Mengde battle maps.

Lua grids are exported only as weak LabelMe pre-annotations. Training defaults
to human-reviewed annotations and validation is held out by complete map asset.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from collections import Counter, deque
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageEnhance
from torch.utils.data import DataLoader, Dataset
from transformers import SegformerConfig, SegformerForSemanticSegmentation

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import terrain_semantic_model as base


MODEL_SOURCE = (
    ROOT / "output" / "model_cache" / "modelscope"
    / "segformer-b2-cityscapes"
)
DATASET_DIR = ROOT / "output" / "terrain_model" / "segformer_dataset"
MODEL_DIR = ROOT / "output" / "terrain_model" / "segformer-b2-mengde"
REPORT_PATH = ROOT / "output" / "terrain_model" / "segformer_report.json"

# Ten visual classes. Exact gameplay subtypes remain a review decision.
CLASS_NAMES = (
    "open", "forest", "mountain", "rock", "water", "barrier",
    "city", "gate", "camp", "supply",
)
CHAR_TO_CLASS = {
    "f": "open", "g": "open", "w": "open", "F": "forest",
    "m": "mountain", "r": "rock", "~": "water", "W": "barrier",
    "P": "barrier", "i": "city", "h": "city", "G": "gate",
    "e": "camp", "D": "camp", "b": "supply", "c": "supply",
    "C": "supply",
}
CLASS_TO_CHAR = {
    "open": "f", "forest": "F", "mountain": "m", "rock": "r",
    "water": "~", "barrier": "W", "city": "i", "gate": "G",
    "camp": "e", "supply": "b",
}
ID_TO_NAME = dict(enumerate(CLASS_NAMES))
NAME_TO_ID = {name: index for index, name in ID_TO_NAME.items()}
IMAGENET_MEAN = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)


def unique_consistent_stages() -> list[dict]:
    """Return one stage per bitmap, excluding conflicting reused assets."""
    grouped: dict[str, list[dict]] = {}
    for stage in base.iter_stages():
        grouped.setdefault(stage["asset"].name, []).append(stage)
    result = []
    for stages in grouped.values():
        grids = {(s["width"], s["height"], "".join(s["rows"])) for s in stages}
        if len(grids) == 1:
            result.append(stages[0])
    return sorted(result, key=lambda stage: stage["asset"].name)


def cell_polygon(image: Image.Image, x: int, y: int, width: int, height: int):
    left, top, right, bottom = base.cell_bounds(image, x, y, width, height)
    return [[left, top], [right - 1, top], [right - 1, bottom - 1], [left, bottom - 1]]


def export_annotations(output_dir: Path, limit: int, holdout: str) -> dict:
    """Export weak grid rectangles as LabelMe pre-annotations."""
    annotations = output_dir / "annotations"
    images = output_dir / "images"
    masks = output_dir / "weak_masks"
    for directory in (annotations, images, masks):
        directory.mkdir(parents=True, exist_ok=True)

    stages = unique_consistent_stages()
    chosen = [s for s in stages if s["asset"].name != holdout][:limit]
    held = next((s for s in stages if s["asset"].name == holdout), None)
    if held is None:
        raise RuntimeError(f"Holdout map was not found: {holdout}")
    chosen.append(held)

    manifest = {
        "schema_version": 1,
        "supervision": "weak Lua pre-annotations; set reviewed=true only after visual review",
        "classes": list(CLASS_NAMES),
        "holdout": holdout,
        "maps": [],
    }
    for stage in chosen:
        image = Image.open(stage["asset"]).convert("RGB")
        image_name = stage["asset"].name
        image.save(images / image_name)
        shapes = []
        mask = Image.new("L", image.size, color=255)
        mask_array = np.asarray(mask).copy()
        counts = Counter()
        for y, row in enumerate(stage["rows"]):
            for x, char in enumerate(row):
                label = CHAR_TO_CLASS[char]
                counts[label] += 1
                shapes.append({
                    "label": label,
                    "points": cell_polygon(image, x, y, stage["width"], stage["height"]),
                    "group_id": None,
                    "description": f"weak grid cell ({x},{y}); verify image semantics",
                    "shape_type": "polygon",
                    "flags": {"weak": True},
                })
                left, top, right, bottom = base.cell_bounds(
                    image, x, y, stage["width"], stage["height"]
                )
                mask_array[top:bottom, left:right] = NAME_TO_ID[label]
        mask = Image.fromarray(mask_array.astype(np.uint8), mode="L")
        mask_name = f"{Path(image_name).stem}.png"
        mask.save(masks / mask_name)
        annotation = {
            "version": "5.8.1",
            "flags": {"reviewed": False, "holdout": image_name == holdout},
            "shapes": shapes,
            "imagePath": f"../images/{image_name}",
            "imageData": None,
            "imageHeight": image.height,
            "imageWidth": image.width,
            "grid": [stage["width"], stage["height"]],
            "source_stage": stage["path"].name,
        }
        annotation_path = annotations / f"{Path(image_name).stem}.json"
        annotation_path.write_text(
            json.dumps(annotation, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest["maps"].append({
            "asset": image_name,
            "annotation": str(annotation_path.relative_to(output_dir)),
            "weak_mask": str((masks / mask_name).relative_to(output_dir)),
            "grid": [stage["width"], stage["height"]],
            "holdout": image_name == holdout,
            "reviewed": False,
            "class_cells": dict(sorted(counts.items())),
        })
    (output_dir / "labels.txt").write_text(
        "__ignore__\n" + "\n".join(CLASS_NAMES) + "\n", encoding="utf-8"
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def _mask_from_labelme(annotation: dict, size: tuple[int, int]) -> Image.Image:
    """Rasterize polygons without importing LabelMe/Qt."""
    from PIL import ImageDraw

    mask = Image.new("L", size, color=255)
    draw = ImageDraw.Draw(mask)
    for shape in annotation["shapes"]:
        label = shape["label"]
        if label not in NAME_TO_ID:
            continue
        draw.polygon([tuple(point) for point in shape["points"]], fill=NAME_TO_ID[label])
    return mask


def load_records(dataset_dir: Path, allow_weak: bool) -> list[dict]:
    manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    records = []
    for item in manifest["maps"]:
        annotation_path = dataset_dir / item["annotation"]
        annotation = json.loads(annotation_path.read_text(encoding="utf-8"))
        reviewed = bool(annotation.get("flags", {}).get("reviewed"))
        if not reviewed and not allow_weak:
            continue
        records.append({
            **item,
            "image_path": dataset_dir / "images" / item["asset"],
            "annotation_path": annotation_path,
            "annotation": annotation,
            "reviewed": reviewed,
        })
    return records


def _jitter(image: Image.Image, rng: random.Random) -> Image.Image:
    image = ImageEnhance.Color(image).enhance(rng.uniform(0.75, 1.25))
    image = ImageEnhance.Brightness(image).enhance(rng.uniform(0.85, 1.15))
    image = ImageEnhance.Contrast(image).enhance(rng.uniform(0.85, 1.15))
    hsv = np.asarray(image.convert("HSV")).copy()
    hsv[..., 0] = (hsv[..., 0].astype(np.int16) + rng.randint(-12, 12)) % 256
    return Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")


def tensorize(image: Image.Image) -> torch.Tensor:
    array = np.asarray(image, dtype=np.float32) / 255.0
    array = (array - IMAGENET_MEAN) / IMAGENET_STD
    return torch.from_numpy(array).permute(2, 0, 1)


class TerrainDataset(Dataset):
    def __init__(self, records: list[dict], crop_size: int, patches_per_map: int,
                 augment: bool, seed: int = 20260809):
        self.records = records
        self.crop_size = crop_size
        self.patches_per_map = patches_per_map
        self.augment = augment
        self.seed = seed

    def __len__(self):
        return len(self.records) * self.patches_per_map

    def __getitem__(self, index):
        record = self.records[index // self.patches_per_map]
        rng = random.Random(self.seed + index)
        image = Image.open(record["image_path"]).convert("RGB")
        mask = _mask_from_labelme(record["annotation"], image.size)
        scale = max(self.crop_size / min(image.size), rng.uniform(0.65, 1.0))
        resized = (max(self.crop_size, round(image.width * scale)),
                   max(self.crop_size, round(image.height * scale)))
        image = image.resize(resized, Image.Resampling.BICUBIC)
        mask = mask.resize(resized, Image.Resampling.NEAREST)
        rare_shapes = [
            shape for shape in record["annotation"]["shapes"]
            if shape["label"] not in {"open", "forest"}
        ]
        if rare_shapes and index % 2 == 0:
            shape = rare_shapes[index % len(rare_shapes)]
            center_x = sum(point[0] for point in shape["points"]) / len(shape["points"])
            center_y = sum(point[1] for point in shape["points"]) / len(shape["points"])
            center_x *= resized[0] / record["annotation"]["imageWidth"]
            center_y *= resized[1] / record["annotation"]["imageHeight"]
            left = max(0, min(resized[0] - self.crop_size, round(center_x - self.crop_size / 2)))
            top = max(0, min(resized[1] - self.crop_size, round(center_y - self.crop_size / 2)))
        else:
            left = rng.randint(0, resized[0] - self.crop_size)
            top = rng.randint(0, resized[1] - self.crop_size)
        box = (left, top, left + self.crop_size, top + self.crop_size)
        image, mask = image.crop(box), mask.crop(box)
        if self.augment:
            image = _jitter(image, rng)
            if rng.random() < 0.5:
                image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                mask = mask.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return tensorize(image), torch.from_numpy(np.asarray(mask, dtype=np.int64).copy())


def build_model(source: Path) -> SegformerForSemanticSegmentation:
    if not (source / "config.json").is_file():
        raise RuntimeError(f"SegFormer source model is missing: {source}")
    config = SegformerConfig.from_pretrained(source, local_files_only=True)
    config.num_labels = len(CLASS_NAMES)
    config.id2label = ID_TO_NAME
    config.label2id = NAME_TO_ID
    model = SegformerForSemanticSegmentation(config)
    safetensors_path = source / "model.safetensors"
    if safetensors_path.is_file():
        from safetensors.torch import load_file

        checkpoint = load_file(str(safetensors_path))
    else:
        checkpoint_path = source / "pytorch_model.bin"
        if not checkpoint_path.is_file():
            raise RuntimeError(f"No model weights found under {source}")
        # This file is a trusted, project-cached NVIDIA/ModelScope artifact.
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    current = model.state_dict()
    compatible = {
        name: value for name, value in checkpoint.items()
        if name in current and current[name].shape == value.shape
    }
    missing, unexpected = model.load_state_dict(compatible, strict=False)
    loaded_encoder = sum(name.startswith("segformer.encoder") for name in compatible)
    if loaded_encoder < 100:
        raise RuntimeError(
            f"Pretrained encoder did not load correctly ({loaded_encoder} tensors); "
            f"missing={len(missing)}, unexpected={len(unexpected)}"
        )
    return model


def train(dataset_dir: Path, source: Path, output: Path, epochs: int,
          batch_size: int, patches_per_map: int, allow_weak: bool,
          freeze_encoder: bool) -> dict:
    records = load_records(dataset_dir, allow_weak)
    holdout = [record for record in records if record["holdout"]]
    training = [record for record in records if not record["holdout"]]
    if not training or not holdout:
        raise RuntimeError(
            "Training and holdout maps are required. Review annotations or pass --allow-weak."
        )
    random.seed(20260809)
    np.random.seed(20260809)
    torch.manual_seed(20260809)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(source).to(device)
    if freeze_encoder:
        for parameter in model.segformer.parameters():
            parameter.requires_grad = False
    loader = DataLoader(
        TerrainDataset(training, 512, patches_per_map, True),
        batch_size=batch_size, shuffle=True, num_workers=0,
    )
    optimizer = torch.optim.AdamW(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=6e-5, weight_decay=0.01,
    )
    cell_counts = Counter(
        shape["label"]
        for record in training for shape in record["annotation"]["shapes"]
        if shape["label"] in NAME_TO_ID
    )
    total_cells = sum(cell_counts.values())
    class_weights = torch.tensor([
        min(4.0, max(0.5, math.sqrt(total_cells / (len(CLASS_NAMES) * max(1, cell_counts[name])))))
        for name in CLASS_NAMES
    ], dtype=torch.float32, device=device)
    losses = []
    started = time.perf_counter()
    model.train()
    for _epoch in range(epochs):
        for pixels, labels in loader:
            optimizer.zero_grad(set_to_none=True)
            labels = labels.to(device)
            logits = model(pixel_values=pixels.to(device)).logits
            logits = F.interpolate(
                logits, size=labels.shape[-2:], mode="bilinear", align_corners=False
            )
            loss = F.cross_entropy(
                logits, labels, weight=class_weights, ignore_index=255
            )
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
    output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output, safe_serialization=True)
    report = evaluate(model, holdout, device)
    report.update({
        "backbone": "MiT-B2",
        "decoder": "SegFormer all-MLP",
        "learning_rate": 6e-5,
        "crop_size": 512,
        "epochs": epochs,
        "training_maps": [r["asset"] for r in training],
        "holdout_maps": [r["asset"] for r in holdout],
        "supervision": "weak Lua labels" if allow_weak else "human-reviewed LabelMe",
        "mean_training_loss": float(np.mean(losses)),
        "training_seconds": time.perf_counter() - started,
        "device": str(device),
        "encoder_frozen": freeze_encoder,
        "class_weights": {
            name: float(class_weights[index].cpu())
            for index, name in ID_TO_NAME.items()
        },
        "sampling": "50% rare-terrain-centered crops, 50% random crops",
    })
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def infer_pixels(model, image: Image.Image, device: torch.device):
    target_h = 512
    target_w = math.ceil((image.width * target_h / image.height) / 32) * 32
    resized = image.resize((target_w, target_h), Image.Resampling.BICUBIC)
    pixels = tensorize(resized).unsqueeze(0).to(device)
    started = time.perf_counter()
    with torch.inference_mode():
        logits = model(pixel_values=pixels).logits
        logits = F.interpolate(logits, size=(target_h, target_w), mode="bilinear", align_corners=False)
        probabilities = logits.softmax(1)[0]
    elapsed = (time.perf_counter() - started) * 1000
    confidence, predicted = probabilities.max(0)
    return predicted.cpu().numpy(), confidence.cpu().numpy(), resized, elapsed


def clean_small_components(labels: np.ndarray, min_size: int = 24) -> np.ndarray:
    """Replace tiny connected regions with their boundary majority class."""
    result = labels.copy()
    height, width = labels.shape
    seen = np.zeros_like(labels, dtype=bool)
    for sy in range(height):
        for sx in range(width):
            if seen[sy, sx]:
                continue
            label = int(labels[sy, sx])
            queue = deque([(sx, sy)])
            seen[sy, sx] = True
            component, boundary = [], []
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if labels[ny, nx] == label and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((nx, ny))
                    elif labels[ny, nx] != label:
                        boundary.append(int(labels[ny, nx]))
            if len(component) < min_size and boundary:
                replacement = Counter(boundary).most_common(1)[0][0]
                for x, y in component:
                    result[y, x] = replacement
    return result


def grid_vote(labels: np.ndarray, confidence: np.ndarray, width: int, height: int):
    rows, review = [], []
    for gy in range(height):
        chars = []
        for gx in range(width):
            left = round(gx * labels.shape[1] / width)
            right = round((gx + 1) * labels.shape[1] / width)
            top = round(gy * labels.shape[0] / height)
            bottom = round((gy + 1) * labels.shape[0] / height)
            patch = labels[top:bottom, left:right]
            values, counts = np.unique(patch, return_counts=True)
            terrain_id = int(values[counts.argmax()])
            vote = float(counts.max() / counts.sum())
            mean_conf = float(confidence[top:bottom, left:right].mean())
            name = ID_TO_NAME[terrain_id]
            chars.append(CLASS_TO_CHAR[name])
            if vote < 0.70 or mean_conf < 0.72 or name in {"barrier", "gate", "camp", "supply"}:
                review.append({
                    "x": gx, "y": gy, "class": name,
                    "vote": round(vote, 4), "confidence": round(mean_conf, 4),
                })
        rows.append("".join(chars))
    return rows, review


def _metrics(predicted: np.ndarray, target: np.ndarray) -> dict:
    valid = target != 255
    ious = {}
    for index, name in ID_TO_NAME.items():
        intersection = np.logical_and(predicted == index, target == index) & valid
        union = np.logical_or(predicted == index, target == index) & valid
        if union.any():
            ious[name] = float(intersection.sum() / union.sum())
    return {
        "pixel_accuracy": float((predicted[valid] == target[valid]).mean()),
        "class_iou": ious,
        "miou": float(np.mean(list(ious.values()))) if ious else 0.0,
    }


def evaluate(model, records: list[dict], device: torch.device) -> dict:
    metrics, timings = [], []
    model.eval()
    for record in records:
        image = Image.open(record["image_path"]).convert("RGB")
        mask = _mask_from_labelme(record["annotation"], image.size)
        predicted, confidence, resized, elapsed = infer_pixels(model, image, device)
        predicted = clean_small_components(predicted)
        target = np.asarray(mask.resize(resized.size, Image.Resampling.NEAREST))
        metrics.append(_metrics(predicted, target))
        timings.append(elapsed)
    return {
        "validation": "complete held-out map assets",
        "miou": float(np.mean([item["miou"] for item in metrics])),
        "pixel_accuracy": float(np.mean([item["pixel_accuracy"] for item in metrics])),
        "per_map": metrics,
        "mean_inference_ms": float(np.mean(timings)),
    }


def predict(model_dir: Path, image_path: Path, output_path: Path,
            width: int, height: int) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SegformerForSemanticSegmentation.from_pretrained(
        model_dir, local_files_only=True
    ).to(device).eval()
    image = Image.open(image_path).convert("RGB")
    predicted, confidence, _resized, elapsed = infer_pixels(model, image, device)
    cleaned = clean_small_components(predicted)
    rows, review = grid_vote(cleaned, confidence, width, height)
    payload = {
        "image": str(image_path), "model": str(model_dir),
        "grid": [width, height], "rows": rows,
        "postprocess": "4-connected small-component cleanup + per-cell majority vote",
        "inference_ms": elapsed, "device": str(device),
        "review_required": review, "auto_apply": False,
        "warning": "Merged visual classes need review before exact Lua terrain subtypes are chosen.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def smoke(source: Path) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(source).to(device).eval()
    pixels = torch.zeros((1, 3, 128, 128), device=device)
    with torch.inference_mode():
        logits = model(pixel_values=pixels).logits
    return {
        "architecture": "MiT-B2 + SegFormer all-MLP decoder",
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "logits_shape": list(logits.shape), "device": str(device),
        "source": str(source),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export")
    export.add_argument("--output", type=Path, default=DATASET_DIR)
    export.add_argument("--limit", type=int, default=19)
    export.add_argument("--holdout", default="m008.png")
    train_parser = sub.add_parser("train")
    train_parser.add_argument("--dataset", type=Path, default=DATASET_DIR)
    train_parser.add_argument("--source", type=Path, default=MODEL_SOURCE)
    train_parser.add_argument("--output", type=Path, default=MODEL_DIR)
    train_parser.add_argument("--epochs", type=int, default=20)
    train_parser.add_argument("--batch-size", type=int, default=2)
    train_parser.add_argument("--patches-per-map", type=int, default=16)
    train_parser.add_argument("--allow-weak", action="store_true")
    train_parser.add_argument("--freeze-encoder", action="store_true")
    predict_parser = sub.add_parser("predict")
    predict_parser.add_argument("image", type=Path)
    predict_parser.add_argument("--model", type=Path, default=MODEL_DIR)
    predict_parser.add_argument("--output", type=Path, required=True)
    predict_parser.add_argument("--width", type=int, default=19)
    predict_parser.add_argument("--height", type=int, default=14)
    smoke_parser = sub.add_parser("smoke")
    smoke_parser.add_argument("--source", type=Path, default=MODEL_SOURCE)
    args = parser.parse_args()
    if args.command == "export":
        result = export_annotations(args.output, args.limit, args.holdout)
    elif args.command == "train":
        result = train(args.dataset, args.source, args.output, args.epochs,
                       args.batch_size, args.patches_per_map, args.allow_weak,
                       args.freeze_encoder)
    elif args.command == "predict":
        result = predict(args.model, args.image, args.output, args.width, args.height)
    else:
        result = smoke(args.source)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
