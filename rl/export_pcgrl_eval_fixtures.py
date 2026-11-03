import argparse
import json
import math
from pathlib import Path

import numpy as np
import onnxruntime as ort

from pcgrl_mobile import CELL_COUNT, TILE_COUNT, build_features, hash_unit


def mobile_sample(logits: np.ndarray, seed: int) -> list[int]:
    tiles = []
    for index in range(CELL_COUNT):
        best_tile = 0
        best_score = -math.inf
        for tile in range(TILE_COUNT):
            probability = (hash_unit(seed ^ ((tile * 0x45D9F3B) & 0xFFFFFFFF), index, 0x27D4EB2D) + 1.0) * 0.5
            probability = max(1e-7, min(1.0 - 1e-7, probability))
            score = float(logits[index, tile]) - math.log(-math.log(probability)) * 0.85
            if math.isfinite(score) and score > best_score:
                best_score = score
                best_tile = tile
        tiles.append(best_tile)
    return tiles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("unity-remake/Assets/Resources/Models/PcgrlMasui.onnx"))
    parser.add_argument("--output", type=Path, default=Path("tmp/pcgrl-mobile-fixtures.json"))
    parser.add_argument("--samples-per-level", type=int, default=120)
    args = parser.parse_args()

    session = ort.InferenceSession(str(args.model), providers=["CPUExecutionProvider"])
    fixtures = []
    for label, difficulty in (("easy", 0.0), ("medium", 0.5), ("hard", 1.0)):
        for index in range(args.samples_per_level):
            seed = 700_001 + index * 7919 + int(difficulty * 997)
            features = build_features(difficulty, seed)[None, ...]
            logits = session.run(["logits"], {"cells": features})[0][0]
            fixtures.append({"difficulty": label, "difficulty_value": difficulty, "seed": seed, "tiles": mobile_sample(logits, seed)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixtures, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"fixtures": len(fixtures), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
