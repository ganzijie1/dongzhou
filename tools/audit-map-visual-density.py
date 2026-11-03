"""Audit the mobile battle-map decluttering contract against all campaign stages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter


STRUCTURE_DETAIL_TERRAINS = frozenset("WcbeGDPhC")
BARRIER_TERRAINS = frozenset("r~v")
STRUCTURAL_TERRAINS = STRUCTURE_DETAIL_TERRAINS | BARRIER_TERRAINS
EDGE_THRESHOLD = 0.12


def load_rows(raw: object) -> list[str]:
    if isinstance(raw, list):
        return [str(row) for row in raw]
    if isinstance(raw, dict):
        return [str(raw[key]) for key in sorted(raw, key=lambda value: int(value))]
    return []


def terrain_mask(rows: list[str], width: int, height: int, cell_pixels: int, chars: frozenset[str]) -> Image.Image:
    data = np.zeros((height * cell_pixels, width * cell_pixels), dtype=np.uint8)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char in chars:
                data[y * cell_pixels:(y + 1) * cell_pixels, x * cell_pixels:(x + 1) * cell_pixels] = 255
    return Image.fromarray(data, mode="L")


def apply_declutter(image: Image.Image, structure_mask: Image.Image, barrier_mask: Image.Image) -> Image.Image:
    reduced = image.resize(
        (max(1, round(image.width * 0.58)), max(1, round(image.height * 0.58))),
        Image.Resampling.LANCZOS,
    )
    calm = reduced.resize(image.size, Image.Resampling.LANCZOS)
    calm = ImageEnhance.Color(calm).enhance(0.86)
    calm = ImageEnhance.Contrast(calm).enhance(0.90)
    calm = ImageEnhance.Brightness(calm).enhance(0.99)
    barrier_outer = barrier_mask.filter(ImageFilter.MaxFilter(7))
    barrier_inner = barrier_mask.filter(ImageFilter.MinFilter(7))
    barrier_boundary = ImageChops.subtract(barrier_outer, barrier_inner).filter(ImageFilter.GaussianBlur(0.8))
    barrier_boundary = barrier_boundary.point(lambda value: round(value * 0.55))
    mixed = Image.composite(image, calm, barrier_boundary)
    feather = structure_mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    feather = ImageChops.lighter(structure_mask, feather)
    return Image.composite(image, mixed, feather)


def luminance(image: Image.Image) -> np.ndarray:
    return np.asarray(image.convert("L"), dtype=np.float32) / 255.0


def metric_mask(mask: Image.Image, invert: bool = False) -> np.ndarray:
    working = ImageChops.invert(mask) if invert else mask
    working = working.filter(ImageFilter.MinFilter(5))
    return np.asarray(working, dtype=np.uint8) >= 250


def visual_metrics(image: Image.Image, mask: np.ndarray) -> dict[str, float]:
    gray = luminance(image)
    if not mask.any():
        return {"edge_density": 0.0, "hf_energy_ratio": 0.0}
    gy, gx = np.gradient(gray)
    magnitude = np.hypot(gx, gy)
    blurred = np.asarray(image.convert("L").filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0
    high = gray - blurred
    centered = gray - float(gray[mask].mean())
    hf_ratio = float(np.mean(np.square(high[mask])) / (np.mean(np.square(centered[mask])) + 1e-8))
    return {
        "edge_density": float(np.mean(magnitude[mask] > EDGE_THRESHOLD)),
        "hf_energy_ratio": hf_ratio,
    }


def reduction(before: float, after: float) -> float:
    return float((before - after) / before) if before > 1e-8 else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("docs/map-visual-density-report.json"))
    parser.add_argument("--preview-dir", type=Path, default=Path("tmp/map-density-qa"))
    parser.add_argument("--cell-pixels", type=int, default=32)
    args = parser.parse_args()

    root = args.root.resolve()
    campaign_path = root / "web-game" / "scenario" / "campaign.json"
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    records: list[dict[str, object]] = []
    failures: list[str] = []
    preview_pair: tuple[Image.Image, Image.Image] | None = None
    preview_score = -1.0

    for stage in campaign["stages"]:
        size = [int(value) for value in stage["stage"]["map"]["size"]]
        width, height = size
        rows = load_rows(stage["stage"]["map"]["terrain"])
        if len(rows) != height or any(len(row) != width for row in rows):
            failures.append(f"{stage['id']}: terrain dimensions do not match {width}x{height}")
            continue
        asset_name = Path(stage["mapAsset"]).stem + ".webp"
        asset = root / "web-game" / "assets" / "maps" / asset_name
        if not asset.exists():
            failures.append(f"{stage['id']}: missing {asset_name}")
            continue

        target_size = (width * args.cell_pixels, height * args.cell_pixels)
        with Image.open(asset) as source:
            original = source.convert("RGB").resize(target_size, Image.Resampling.LANCZOS)
        structure = terrain_mask(rows, width, height, args.cell_pixels, STRUCTURE_DETAIL_TERRAINS)
        barriers = terrain_mask(rows, width, height, args.cell_pixels, BARRIER_TERRAINS)
        semantic = ImageChops.lighter(structure, barriers)
        processed = apply_declutter(original, structure, barriers)
        ground = metric_mask(semantic, invert=True)
        structure_core = metric_mask(structure)
        before = visual_metrics(original, ground)
        after = visual_metrics(processed, ground)
        if structure_core.any():
            original_data = np.asarray(original, dtype=np.int16)
            processed_data = np.asarray(processed, dtype=np.int16)
            mae = float(np.mean(np.abs(original_data[structure_core] - processed_data[structure_core])))
            fidelity = 1.0 - mae / 255.0
        else:
            fidelity = 1.0
        item = {
            "stage_id": str(stage["id"]),
            "stage_index": int(stage["index"]),
            "map_asset": asset_name,
            "logical_size": size,
            "structural_cells": sum(char in STRUCTURAL_TERRAINS for row in rows for char in row),
            "detail_preserved_cells": sum(char in STRUCTURE_DETAIL_TERRAINS for row in rows for char in row),
            "before": before,
            "after": after,
            "edge_reduction": reduction(before["edge_density"], after["edge_density"]),
            "hf_reduction": reduction(before["hf_energy_ratio"], after["hf_energy_ratio"]),
            "structural_fidelity": fidelity,
        }
        records.append(item)
        score = before["edge_density"] + before["hf_energy_ratio"]
        if score > preview_score:
            preview_score = score
            preview_pair = (original.copy(), processed.copy())

    edge_reductions = np.asarray([item["edge_reduction"] for item in records], dtype=np.float64)
    hf_reductions = np.asarray([item["hf_reduction"] for item in records], dtype=np.float64)
    fidelities = np.asarray([item["structural_fidelity"] for item in records], dtype=np.float64)
    thresholds = {"median_edge_reduction_min": 0.15, "median_hf_reduction_min": 0.20, "structural_fidelity_min": 0.995}
    summary = {
        "stages": len(records),
        "maps": len({item["map_asset"] for item in records}),
        "median_edge_reduction": float(np.median(edge_reductions)) if len(records) else 0.0,
        "median_hf_reduction": float(np.median(hf_reductions)) if len(records) else 0.0,
        "minimum_structural_fidelity": float(np.min(fidelities)) if len(records) else 0.0,
    }
    if len(records) != int(campaign["stageCount"]):
        failures.append(f"audited {len(records)} of {campaign['stageCount']} stages")
    if summary["median_edge_reduction"] < thresholds["median_edge_reduction_min"]:
        failures.append("median ground edge reduction is below the release threshold")
    if summary["median_hf_reduction"] < thresholds["median_hf_reduction_min"]:
        failures.append("median ground high-frequency reduction is below the release threshold")
    if summary["minimum_structural_fidelity"] < thresholds["structural_fidelity_min"]:
        failures.append("structural core fidelity is below the release threshold")

    report = {
        "schema_version": "dongzhou-map-density-v1",
        "method": {
            "render_cell_pixels": args.cell_pixels,
            "mode": "balanced-compact",
            "scale": 0.58,
            "saturation": 0.86,
            "contrast": 0.90,
            "edge_threshold": EDGE_THRESHOLD,
            "structural_terrains": sorted(STRUCTURAL_TERRAINS),
            "detail_preserved_terrains": sorted(STRUCTURE_DETAIL_TERRAINS),
            "boundary_preserved_terrains": sorted(BARRIER_TERRAINS),
            "note": "Offline image metrics are release screening only; they do not prove gameplay improvement.",
        },
        "thresholds": thresholds,
        "summary": summary,
        "densest_stages": sorted(records, key=lambda item: item["before"]["edge_density"] + item["before"]["hf_energy_ratio"], reverse=True)[:20],
        "failures": failures,
        "result": "FAIL" if failures else "PASS",
    }
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if records and preview_pair:
        preview_dir = args.preview_dir if args.preview_dir.is_absolute() else root / args.preview_dir
        preview_dir.mkdir(parents=True, exist_ok=True)
        preview_pair[0].save(preview_dir / "map-density-before.png")
        preview_pair[1].save(preview_dir / "map-density-after.png")

    print(json.dumps({**summary, "failures": failures, "result": report["result"]}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
