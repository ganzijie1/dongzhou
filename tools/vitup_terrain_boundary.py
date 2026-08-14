"""Evaluate official ViT-Up S+ features on a reviewed three-class map."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VITUP_ROOT = ROOT / "tools/vendor/vit-up"
SPLUS_ROOT = ROOT / "output/model_cache/modelscope/dinov3-vits16plus-pretrain-lvd1689m"
CLASSES = np.asarray(["f", "F", "m"])
COLORS = np.asarray([[128, 185, 84], [22, 126, 55], [177, 105, 73]], dtype=np.uint8)


def class_metrics(truth: np.ndarray, predicted: np.ndarray) -> dict:
    result = {}
    f1_values = []
    for terrain in CLASSES:
        true_positive = int(((truth == terrain) & (predicted == terrain)).sum())
        false_positive = int(((truth != terrain) & (predicted == terrain)).sum())
        false_negative = int(((truth == terrain) & (predicted != terrain)).sum())
        precision = true_positive / max(1, true_positive + false_positive)
        recall = true_positive / max(1, true_positive + false_negative)
        f1 = 2 * precision * recall / max(1e-12, precision + recall)
        result[str(terrain)] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": int((truth == terrain).sum()),
        }
        f1_values.append(f1)
    return {
        "accuracy": float((truth == predicted).mean()),
        "macro_f1": float(np.mean(f1_values)),
        "classes": result,
    }


def load_model():
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    torch.compile = lambda model, *args, **kwargs: model
    sys.path.insert(0, str(VITUP_ROOT))
    import vit_up.inference.vit_up_wrapper as wrapper

    wrapper.MODEL_SPECS["vit_up_dinov3_splus"]["backbone_model_name"] = str(SPLUS_ROOT)
    return wrapper.ViTUpWrapper(
        "vit_up_dinov3_splus",
        device="cpu",
        use_bfloat16=False,
        query_chunk_size=512,
    ).eval()


def query_grid(width: int, height: int, scale: int) -> torch.Tensor:
    points = []
    for y in range(height):
        for x in range(width):
            for sub_y in range(scale):
                for sub_x in range(scale):
                    points.append((
                        (x + (sub_x + 0.5) / scale) / width,
                        (y + (sub_y + 0.5) / scale) / height,
                    ))
    return torch.tensor(points, dtype=torch.float32).unsqueeze(0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path,
        default=ROOT / "output/terrain_model/m008_large_v2_manifest.json",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "output/terrain_model/m008_vitup_boundary.json",
    )
    parser.add_argument("--scale", type=int, default=4)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    width, height = map(int, manifest["grid"])
    reviewed = np.asarray(list("".join(manifest["terrain_rows"]))).reshape(height, width)
    natural = np.isin(reviewed, CLASSES)
    protected = {tuple(layer["position"]) for layer in manifest.get("terrain_layers", [])}
    image_path = ROOT / manifest["map"]
    image = Image.open(image_path).convert("RGB")

    model = load_model()
    with torch.inference_mode():
        dense = model(image, query_grid(width, height, args.scale))[0]
        dense = torch.nn.functional.normalize(dense.float(), dim=1)
    features = dense.reshape(height, width, args.scale * args.scale, -1)

    prototypes = []
    prototype_cells = {}
    for terrain in CLASSES:
        cells = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if reviewed[y, x] == terrain and (x, y) not in protected
        ]
        if not cells:
            raise RuntimeError(f"No pure prototype cells for {terrain}")
        samples = torch.cat([features[y, x] for x, y in cells], dim=0)
        prototypes.append(torch.nn.functional.normalize(samples.mean(dim=0), dim=0))
        prototype_cells[str(terrain)] = [list(point) for point in cells]
    prototypes = torch.stack(prototypes)

    scores = torch.einsum("hwsd,kd->hwsk", features, prototypes)
    probabilities = torch.softmax(scores / 0.07, dim=-1)
    sub_labels = scores.argmax(dim=-1).cpu().numpy()
    cell_labels = np.zeros((height, width), dtype=np.int64)
    confidence = np.zeros((height, width), dtype=np.float32)
    mixed_cells = []
    for y in range(height):
        for x in range(width):
            counts = np.bincount(sub_labels[y, x], minlength=len(CLASSES))
            order = np.argsort(counts)[::-1]
            cell_labels[y, x] = order[0]
            confidence[y, x] = float(probabilities[y, x, :, order[0]].mean())
            if natural[y, x] and counts[order[1]]:
                mixed_cells.append({
                    "position": [x, y],
                    "primary_terrain": str(CLASSES[order[0]]),
                    "secondary_terrain": str(CLASSES[order[1]]),
                    "coverage": round(int(counts[order[1]]) * 255 / int(counts.sum())),
                })

    predicted = CLASSES[cell_labels]
    truth = reviewed[natural]
    natural_prediction = predicted[natural]
    disagreements = [
        {
            "position": [x, y],
            "expected": str(reviewed[y, x]),
            "predicted": str(predicted[y, x]),
            "confidence": float(confidence[y, x]),
        }
        for y in range(height)
        for x in range(width)
        if natural[y, x] and reviewed[y, x] != predicted[y, x]
    ]
    payload = {
        "backend": "official ViT-Up DINOv3-S+; eager CPU inference",
        "backbone": str(SPLUS_ROOT),
        "auto_apply": False,
        "grid": [width, height],
        "scale": args.scale,
        "prototype_cells": prototype_cells,
        "metrics_against_reviewed_map": class_metrics(truth, natural_prediction),
        "prediction_counts": dict(sorted(Counter(natural_prediction.tolist()).items())),
        "disagreements": sorted(disagreements, key=lambda item: item["confidence"]),
        "mixed_cells": mixed_cells,
        "rows": [
            "".join(str(predicted[y, x]) if natural[y, x] else str(reviewed[y, x]) for x in range(width))
            for y in range(height)
        ],
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    overlay = np.asarray(image, dtype=np.uint8).copy()
    cell_width, cell_height = image.width // width, image.height // height
    for y in range(height):
        for x in range(width):
            if natural[y, x]:
                patch = overlay[y * cell_height:(y + 1) * cell_height, x * cell_width:(x + 1) * cell_width]
                patch[:] = (patch.astype(np.uint16) * 2 + COLORS[cell_labels[y, x]].astype(np.uint16)) // 3
    Image.fromarray(overlay).save(args.output.with_suffix(".png"))
    print(json.dumps({
        "metrics": payload["metrics_against_reviewed_map"],
        "prediction_counts": payload["prediction_counts"],
        "disagreements": len(disagreements),
        "mixed_cells": len(mixed_cells),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
