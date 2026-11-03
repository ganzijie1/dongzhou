"""Train and export the lightweight Masui PCGRL policy used by the Android build.

The policy uses a parallel wide action: one categorical terrain action per cell.
Training follows the PCGRL idea of optimizing computable playability metrics. A
small safe prior is learned first, then REINFORCE improves connectivity, target
obstacle density, route length, spawn safety, and local terrain compatibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical


WIDTH = 19
HEIGHT = 14
CELL_COUNT = WIDTH * HEIGHT
FEATURE_COUNT = 9
TILE_COUNT = 4
MODEL_VERSION = "pcgrl-masui-2026-11-02"
SCHEMA_VERSION = "pcgrl-wide19x14-cell9-tile4-v1"
TARGET_RATIOS = (0.12, 0.19, 0.26)
TARGET_PATHS = (18, 23, 28)
OWN_SPAWNS = ((2, 6), (3, 4), (3, 6), (3, 8), (4, 3), (4, 9), (5, 5))
ENEMY_SPAWNS = ((16, 6), (15, 5), (15, 7), (14, 4), (14, 8), (13, 6))
SPAWNS = OWN_SPAWNS + ENEMY_SPAWNS


def _u32(value: int) -> int:
    return value & 0xFFFFFFFF


def hash_unit(seed: int, index: int, salt: int) -> float:
    value = _u32(seed ^ _u32(index * 0x9E3779B9) ^ salt)
    value = _u32((value ^ (value >> 16)) * 0x7FEB352D)
    value = _u32((value ^ (value >> 15)) * 0x846CA68B)
    value ^= value >> 16
    return ((value >> 8) & 0xFFFFFF) / 16777215.0 * 2.0 - 1.0


def build_features(difficulty: float, seed: int) -> np.ndarray:
    result = np.zeros((CELL_COUNT, FEATURE_COUNT), dtype=np.float32)
    spawn_set = set(SPAWNS)
    for index in range(CELL_COUNT):
        y, x = divmod(index, WIDTH)
        edge_distance = min(x, WIDTH - 1 - x, y, HEIGHT - 1 - y)
        result[index] = (
            x / (WIDTH - 1) * 2.0 - 1.0,
            y / (HEIGHT - 1) * 2.0 - 1.0,
            min(edge_distance, 4) / 4.0,
            1.0 if x <= 5 else 0.0,
            1.0 if x >= WIDTH - 6 else 0.0,
            1.0 if abs(y - (HEIGHT - 1) / 2.0) <= 2.0 else 0.0,
            float(difficulty),
            hash_unit(seed, index, 0xA341316C),
            hash_unit(seed, index, 0xC8013EA4),
        )
        if (x, y) in spawn_set:
            result[index, 5] = 1.5
    return result


class CellPolicy(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(FEATURE_COUNT, 32),
            nn.Tanh(),
            nn.Linear(32, 32),
            nn.Tanh(),
            nn.Linear(32, TILE_COUNT),
        )

    def forward(self, cells: torch.Tensor) -> torch.Tensor:
        return self.network(cells)


def heuristic_targets(difficulty: float, seed: int) -> np.ndarray:
    ratio = np.interp(difficulty, (0.0, 0.5, 1.0), TARGET_RATIOS)
    targets = np.zeros(CELL_COUNT, dtype=np.int64)
    safe = protected_cells()
    for index in range(CELL_COUNT):
        y, x = divmod(index, WIDTH)
        if (x, y) in safe:
            targets[index] = 0 if hash_unit(seed, index, 17) < 0.55 else 1
            continue
        roll = (hash_unit(seed, index, 29) + 1.0) * 0.5
        if roll < ratio:
            targets[index] = 2 if hash_unit(seed, index, 43) < 0.15 else 3
        else:
            targets[index] = 0 if hash_unit(seed, index, 61) < 0.25 else 1
    return targets


def protected_cells() -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for x, y in SPAWNS:
        result.add((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                result.add((nx, ny))
    for x in range(2, WIDTH - 2):
        result.add((x, HEIGHT // 2))
    return result


def _bfs(tiles: np.ndarray, start: tuple[int, int]) -> dict[tuple[int, int], int]:
    if tiles[start[1], start[0]] >= 2:
        return {}
    distances = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            point = (x + dx, y + dy)
            if not (0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT):
                continue
            if point in distances or tiles[point[1], point[0]] >= 2:
                continue
            distances[point] = distances[(x, y)] + 1
            queue.append(point)
    return distances


def map_metrics(flat_tiles: np.ndarray, difficulty: float) -> dict[str, float | bool]:
    tiles = np.asarray(flat_tiles, dtype=np.int64).reshape(HEIGHT, WIDTH)
    distances = _bfs(tiles, OWN_SPAWNS[0])
    connected = all(point in distances for point in SPAWNS)
    path_length = distances.get(ENEMY_SPAWNS[0], 0)
    blocked_ratio = float(np.mean(tiles >= 2))
    spawn_clear = float(np.mean([tiles[y, x] < 2 for x, y in protected_cells()]))
    incompatible = 0
    edges = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = x + dx, y + dy
                if nx >= WIDTH or ny >= HEIGHT:
                    continue
                edges += 1
                incompatible += {int(tiles[y, x]), int(tiles[ny, nx])} == {2, 3}
    target_ratio = float(np.interp(difficulty, (0.0, 0.5, 1.0), TARGET_RATIOS))
    target_path = float(np.interp(difficulty, (0.0, 0.5, 1.0), TARGET_PATHS))
    ratio_score = max(0.0, 1.0 - abs(blocked_ratio - target_ratio) / 0.20)
    path_score = max(0.0, 1.0 - abs(path_length - target_path) / 18.0) if connected else 0.0
    compatibility = 1.0 - incompatible / max(1, edges)
    reward = 4.0 * float(connected) + 1.5 * spawn_clear + 1.5 * ratio_score + path_score + 0.5 * compatibility
    valid = connected and spawn_clear == 1.0 and abs(blocked_ratio - target_ratio) <= 0.10 and incompatible == 0
    return {
        "reward": reward,
        "valid": valid,
        "connected": connected,
        "blocked_ratio": blocked_ratio,
        "ratio_error": abs(blocked_ratio - target_ratio),
        "path_length": float(path_length),
        "spawn_clear": spawn_clear,
        "incompatible_edges": float(incompatible),
    }


def _batch_features(difficulties: np.ndarray, seeds: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(np.stack([build_features(float(d), int(s)) for d, s in zip(difficulties, seeds)]))


def train_policy(seed: int, warm_steps: int, rl_steps: int, batch_size: int) -> CellPolicy:
    torch.set_num_threads(1)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    model = CellPolicy()
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-3)

    model.train()
    for step in range(warm_steps):
        difficulties = np.random.choice((0.0, 0.5, 1.0), batch_size)
        seeds = np.random.randint(1, 2**31 - 1, batch_size)
        features = _batch_features(difficulties, seeds)
        targets = torch.from_numpy(np.stack([heuristic_targets(float(d), int(s)) for d, s in zip(difficulties, seeds)]))
        loss = nn.functional.cross_entropy(model(features).reshape(-1, TILE_COUNT), targets.reshape(-1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    optimizer = torch.optim.Adam(model.parameters(), lr=8e-4)
    baseline = 0.0
    for step in range(rl_steps):
        difficulties = np.random.choice((0.0, 0.5, 1.0), batch_size)
        seeds = np.random.randint(1, 2**31 - 1, batch_size)
        features = _batch_features(difficulties, seeds)
        logits = model(features)
        distribution = Categorical(logits=logits)
        actions = distribution.sample()
        rewards = torch.tensor(
            [map_metrics(actions[i].numpy(), float(difficulties[i]))["reward"] for i in range(batch_size)],
            dtype=torch.float32,
        )
        baseline = 0.97 * baseline + 0.03 * float(rewards.mean())
        advantages = (rewards - baseline).clamp(-4.0, 4.0)
        loss = -(advantages.detach() * distribution.log_prob(actions).mean(dim=1)).mean()
        loss -= 0.003 * distribution.entropy().mean()
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % 100 == 0 or step == rl_steps - 1:
            print(f"rl_step={step:04d} reward={rewards.mean():.4f} baseline={baseline:.4f}")
    return model.eval()


def sample_policy(model: CellPolicy, difficulty: float, seed: int) -> np.ndarray:
    generator = torch.Generator().manual_seed(seed)
    with torch.no_grad():
        logits = model(torch.from_numpy(build_features(difficulty, seed)).unsqueeze(0))[0]
        return torch.multinomial(torch.softmax(logits, dim=-1), 1, generator=generator).squeeze(-1).numpy()


def sample_baseline(difficulty: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ratio = float(np.interp(difficulty, (0.0, 0.5, 1.0), TARGET_RATIOS))
    probabilities = ((1.0 - ratio) * 0.55, (1.0 - ratio) * 0.45, ratio * 0.55, ratio * 0.45)
    return rng.choice(TILE_COUNT, CELL_COUNT, p=probabilities)


def evaluate(model: CellPolicy, samples_per_level: int = 120) -> dict[str, object]:
    rows: list[dict[str, float | bool | str]] = []
    for label, difficulty in (("easy", 0.0), ("medium", 0.5), ("hard", 1.0)):
        for index in range(samples_per_level):
            seed = 100_003 + index * 7919 + int(difficulty * 997)
            for method, tiles in (("policy", sample_policy(model, difficulty, seed)), ("random", sample_baseline(difficulty, seed))):
                rows.append({"method": method, "level": label, **map_metrics(tiles, difficulty)})
    summary: dict[str, object] = {}
    for method in ("policy", "random"):
        subset = [row for row in rows if row["method"] == method]
        summary[method] = {
            "samples": len(subset),
            "valid_rate": float(np.mean([row["valid"] for row in subset])),
            "connected_rate": float(np.mean([row["connected"] for row in subset])),
            "mean_reward": float(np.mean([row["reward"] for row in subset])),
            "mean_ratio_error": float(np.mean([row["ratio_error"] for row in subset])),
            "mean_spawn_clear": float(np.mean([row["spawn_clear"] for row in subset])),
        }
    policy = summary["policy"]
    random_result = summary["random"]
    summary["gate"] = {
        "passed": bool(
            policy["connected_rate"] >= random_result["connected_rate"] + 0.25
            and policy["mean_reward"] > random_result["mean_reward"]
            and policy["mean_ratio_error"] <= 0.11
        ),
        "criteria": "connectivity +0.25 and reward higher than random baseline; obstacle-ratio MAE <= 0.11",
    }
    return summary


@dataclass
class ExportMetadata:
    model_version: str
    schema_version: str
    width: int
    height: int
    features: int
    tiles: int
    training_algorithm: str
    source_inspiration: list[str]
    model_sha256: str
    model_bytes: int
    evaluation: dict[str, object]


def export(model: CellPolicy, output: Path, evaluation: dict[str, object]) -> ExportMetadata:
    output.parent.mkdir(parents=True, exist_ok=True)
    example = torch.from_numpy(build_features(0.5, 42)).unsqueeze(0)
    torch.onnx.export(
        model,
        example,
        output,
        input_names=["cells"],
        output_names=["logits"],
        dynamic_axes=None,
        opset_version=17,
        do_constant_folding=True,
    )
    payload = output.read_bytes()
    metadata = ExportMetadata(
        model_version=MODEL_VERSION,
        schema_version=SCHEMA_VERSION,
        width=WIDTH,
        height=HEIGHT,
        features=FEATURE_COUNT,
        tiles=TILE_COUNT,
        training_algorithm="safe-prior warm start + REINFORCE over PCGRL functional metrics",
        source_inspiration=[
            "https://github.com/amidos2006/gym-pcgrl",
            "https://github.com/smearle/control-pcgrl",
        ],
        model_sha256=hashlib.sha256(payload).hexdigest(),
        model_bytes=len(payload),
        evaluation=evaluation,
    )
    output.with_suffix(".metadata.json").write_text(json.dumps(asdict(metadata), ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("unity-remake/Assets/Resources/Models/PcgrlMasui.onnx"))
    parser.add_argument("--seed", type=int, default=20261102)
    parser.add_argument("--warm-steps", type=int, default=240)
    parser.add_argument("--rl-steps", type=int, default=700)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--eval-samples", type=int, default=120)
    args = parser.parse_args()
    model = train_policy(args.seed, args.warm_steps, args.rl_steps, args.batch_size)
    evaluation = evaluate(model, args.eval_samples)
    if not evaluation["gate"]["passed"]:
        raise SystemExit(f"release gate failed: {json.dumps(evaluation, ensure_ascii=False)}")
    metadata = export(model, args.output, evaluation)
    print(json.dumps(asdict(metadata), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
