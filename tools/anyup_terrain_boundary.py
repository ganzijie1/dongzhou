"""Evaluate AnyUp boundary refinement on a reviewed Mengde terrain map.

This uses the official AnyUp weights with the local DINOv3-S backbone. The
image-guided cost aggregation is an explicit proxy, not the trained CAFe-DINO
aggregator, whose weights and 1024-D DINOv3.txt backbone are incompatible with
the local 384-D CPU pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
ANYUP_ROOT = ROOT / "tools" / "vendor" / "DINO_Soars" / "anyup"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ANYUP_ROOT) not in sys.path:
    sys.path.insert(0, str(ANYUP_ROOT))

from tools.terrain_semantic_dinov3 import load_backbone


class CompatRMSNorm(nn.Module):
    def __init__(self, dimension: int, eps: float = 1e-6, elementwise_affine: bool = True):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dimension)) if elementwise_affine else None

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        result = value * torch.rsqrt(value.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return result if self.weight is None else result * self.weight


if not hasattr(nn, "RMSNorm"):
    nn.RMSNorm = CompatRMSNorm

from anyup.model import AnyUp


CLASSES = np.asarray(["f", "F", "m"])
COLORS = np.asarray([[126, 176, 82], [35, 120, 58], [205, 80, 60]], dtype=np.uint8)
FOREST_PROTOTYPE_CELLS = {
    (5, 19), (2, 16), (1, 16), (0, 18),
    (7, 21), (2, 14), (2, 17), (8, 21),
}


def image_tensor(image: Image.Image, width: int, height: int) -> torch.Tensor:
    resized = image.resize((width, height), Image.Resampling.BICUBIC)
    pixels = np.asarray(resized, dtype=np.float32) / 255.0
    pixels = (pixels - np.asarray([0.485, 0.456, 0.406])) / np.asarray([0.229, 0.224, 0.225])
    return torch.from_numpy(pixels.astype(np.float32)).permute(2, 0, 1).unsqueeze(0)


@torch.inference_mode()
def dino_grid(image: Image.Image, width: int, height: int) -> torch.Tensor:
    tensor = image_tensor(image, width * 16, height * 16)
    output = load_backbone()(pixel_values=tensor)
    tokens = output.last_hidden_state[0, -(width * height):]
    return tokens.reshape(height, width, -1).permute(2, 0, 1).unsqueeze(0)


def guided_cost_aggregation(scores: torch.Tensor, rgb: torch.Tensor) -> torch.Tensor:
    """Aggregate a 3x3 score volume while respecting strong color edges."""
    _, height, width = scores.shape
    padded_scores = torch.nn.functional.pad(scores, (1, 1, 1, 1), mode="replicate")
    padded_rgb = torch.nn.functional.pad(rgb, (1, 1, 1, 1), mode="replicate")
    weighted = torch.zeros_like(scores)
    weights = torch.zeros((1, height, width), dtype=scores.dtype)
    for dy in range(3):
        for dx in range(3):
            neighbor_rgb = padded_rgb[:, dy:dy + height, dx:dx + width]
            color_distance = (rgb - neighbor_rgb).pow(2).mean(dim=0, keepdim=True)
            spatial = 1.0 if dx == 1 and dy == 1 else 0.72
            weight = torch.exp(-color_distance / 0.018) * spatial
            weighted += padded_scores[:, dy:dy + height, dx:dx + width] * weight
            weights += weight
    return weighted / weights.clamp_min(1e-6)


def cell_summary(labels: np.ndarray, width: int, height: int, scale: int) -> tuple[list[str], list[dict]]:
    rows = []
    coverage = []
    for y in range(height):
        row = []
        for x in range(width):
            patch = labels[y * scale:(y + 1) * scale, x * scale:(x + 1) * scale]
            counts = np.bincount(patch.reshape(-1), minlength=len(CLASSES))
            order = np.argsort(counts)[::-1]
            row.append(str(CLASSES[order[0]]))
            if counts[order[1]]:
                coverage.append({
                    "position": [x, y],
                    "primary_terrain": str(CLASSES[order[0]]),
                    "secondary_terrain": str(CLASSES[order[1]]),
                    "coverage": round(int(counts[order[1]]) * 255 / int(counts.sum())),
                })
        rows.append("".join(row))
    return rows, coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "output/terrain_model/m008_large_v2_manifest.json")
    parser.add_argument("--weights", type=Path, default=ROOT / "output/model_cache/anyup_paper.pth")
    parser.add_argument("--output", type=Path, default=ROOT / "output/terrain_model/m008_anyup_boundary.json")
    parser.add_argument("--scale", type=int, default=4)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    width, height = map(int, manifest["grid"])
    reviewed = np.asarray(list("".join(manifest["terrain_rows"]))).reshape(height, width)
    image = Image.open(ROOT / manifest["map"]).convert("RGB")
    features = dino_grid(image, width, height)
    normalized_cells = torch.nn.functional.normalize(features[0], dim=0)

    protected = {tuple(layer["position"]) for layer in manifest.get("terrain_layers", [])}
    prototypes = []
    for terrain in CLASSES:
        if terrain == "F":
            sample_positions = FOREST_PROTOTYPE_CELLS
        else:
            sample_positions = {
                (x, y)
                for y in range(height)
                for x in range(width)
                if reviewed[y, x] == terrain
                and (x, y) not in protected
                and (x, y) not in FOREST_PROTOTYPE_CELLS
            }
        points = [normalized_cells[:, y, x] for x, y in sample_positions]
        if not points:
            raise RuntimeError(f"No pure prototype cells for {terrain}")
        prototypes.append(torch.nn.functional.normalize(torch.stack(points).mean(dim=0), dim=0))
    prototypes = torch.stack(prototypes)

    upsampler = AnyUp().eval()
    upsampler.load_state_dict(torch.load(args.weights, map_location="cpu"))
    guidance = image_tensor(image, width * args.scale, height * args.scale)
    with torch.inference_mode():
        dense = upsampler(
            guidance,
            features,
            output_size=(height * args.scale, width * args.scale),
            q_chunk_size=256,
        )[0]
        dense = torch.nn.functional.normalize(dense, dim=0)
        raw_scores = torch.einsum("kc,chw->khw", prototypes, dense)
        rgb = torch.from_numpy(
            np.asarray(image.resize((width * args.scale, height * args.scale)), dtype=np.float32) / 255.0
        ).permute(2, 0, 1)
        aggregate_scores = guided_cost_aggregation(raw_scores, rgb)

    raw_labels = raw_scores.argmax(dim=0).numpy()
    aggregate_labels = aggregate_scores.argmax(dim=0).numpy()
    raw_rows, raw_coverage = cell_summary(raw_labels, width, height, args.scale)
    aggregate_rows, aggregate_coverage = cell_summary(aggregate_labels, width, height, args.scale)
    experiment_truth = reviewed.copy()
    for x, y in FOREST_PROTOTYPE_CELLS:
        experiment_truth[y, x] = "F"
    natural_mask = np.isin(experiment_truth, CLASSES)
    raw_grid = np.asarray(list("".join(raw_rows))).reshape(height, width)
    aggregate_grid = np.asarray(list("".join(aggregate_rows))).reshape(height, width)
    southwest = {(x, y) for y, stop in {14: 5, 15: 5, 16: 6, 17: 7, 18: 9, 19: 10, 20: 11, 21: 12}.items() for x in range(stop)}

    payload = {
        "backend": "official AnyUp weights + local DINOv3-S",
        "cost_aggregation": "image-guided 3x3 proxy; not official trained CAFe-DINO aggregator",
        "auto_apply": False,
        "grid": [width, height],
        "scale": args.scale,
        "forest_prototype_cells": sorted([list(point) for point in FOREST_PROTOTYPE_CELLS]),
        "raw_cell_accuracy": float((raw_grid[natural_mask] == experiment_truth[natural_mask]).mean()),
        "aggregate_cell_accuracy": float((aggregate_grid[natural_mask] == experiment_truth[natural_mask]).mean()),
        "southwest_mountain_cells": len(southwest),
        "southwest_raw_counts": {
            str(terrain): sum(raw_grid[y, x] == terrain for x, y in southwest)
            for terrain in CLASSES
        },
        "southwest_aggregate_counts": {
            str(terrain): sum(aggregate_grid[y, x] == terrain for x, y in southwest)
            for terrain in CLASSES
        },
        "raw_rows": raw_rows,
        "aggregate_rows": aggregate_rows,
        "raw_mixed_cells": raw_coverage,
        "aggregate_mixed_cells": aggregate_coverage,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    mask = COLORS[aggregate_labels]
    mask_image = Image.fromarray(mask).resize(image.size, Image.Resampling.NEAREST)
    Image.blend(image, mask_image, 0.34).save(args.output.with_suffix(".png"))
    print(json.dumps({key: payload[key] for key in (
        "raw_cell_accuracy", "aggregate_cell_accuracy", "southwest_mountain_cells",
        "southwest_raw_counts", "southwest_aggregate_counts",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
