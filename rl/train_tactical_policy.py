"""Train the formation-aware enemy action ranker from tactical examples."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from rl.tactical_policy import DEFAULT_MODEL_PATH, FEATURE_COUNT, FEATURE_NAMES, TacticalRanker


def build_examples(seed: int, count: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    features = np.zeros((count, FEATURE_COUNT), dtype=np.float32)
    action_types = rng.integers(0, 4, size=count)
    features[np.arange(count), action_types] = 1.0
    features[:, 4] = rng.random(count)
    features[:, 5] = rng.integers(0, 2, size=count)
    features[:, 6] = 1.0 - features[:, 5]
    features[:, 7:10] = rng.random((count, 3))
    features[:, 10] = rng.random(count) * features[:, 1]
    features[:, 11] = rng.integers(0, 2, size=count) * (features[:, 1] + features[:, 2] > 0)
    features[:, 12] = rng.integers(0, 2, size=count)
    features[:, 13] = features[:, 5] * features[:, 2]
    features[:, 14] = features[:, 6] * features[:, 2]
    features[:, 15] = features[:, 6] * rng.integers(0, 2, size=count)
    features[:, 16] = features[:, 15] * features[:, 1] * rng.integers(0, 2, size=count)
    features[:, 17] = features[:, 16] * rng.integers(0, 2, size=count)
    features[:, 18:20] = rng.integers(0, 2, size=(count, 2))

    # This target is used only to supervise the network. Runtime selection is
    # performed by the learned value function together with the PPO prior.
    targets = (
        -1.8 * features[:, 0]
        + 0.4 * features[:, 1]
        + 4.2 * features[:, 2]
        + 3.7 * features[:, 3]
        + 3.0 * features[:, 4]
        + 1.8 * features[:, 13]
        + 0.6 * features[:, 14]
        + 1.0 * features[:, 8]
        + 0.8 * features[:, 9]
        - 0.5 * features[:, 10]
        + 0.5 * features[:, 11] * features[:, 5]
        - 1.7 * features[:, 15] * (1.0 - features[:, 16])
        + 4.5 * features[:, 16]
        + 0.7 * features[:, 17]
        + 0.4 * features[:, 18]
        - 0.5 * features[:, 19] * features[:, 14]
    ).astype(np.float32)
    targets += rng.normal(0.0, 0.08, size=count).astype(np.float32)
    return features, targets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--examples", type=int, default=60_000)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    features, targets = build_examples(args.seed, args.examples)
    split = int(len(features) * 0.9)
    train_x = torch.from_numpy(features[:split])
    train_y = torch.from_numpy(targets[:split])
    valid_x = torch.from_numpy(features[split:])
    valid_y = torch.from_numpy(targets[split:])

    model = TacticalRanker()
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-4)
    loss_fn = torch.nn.SmoothL1Loss()
    batch_size = 512
    generator = torch.Generator().manual_seed(args.seed)
    for _ in range(args.epochs):
        order = torch.randperm(len(train_x), generator=generator)
        for start in range(0, len(order), batch_size):
            indices = order[start : start + batch_size]
            loss = loss_fn(model(train_x[indices]), train_y[indices])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        validation_mae = torch.mean(torch.abs(model(valid_x) - valid_y)).item()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "version": 1,
            "feature_names": FEATURE_NAMES,
            "state_dict": model.state_dict(),
            "validation_mae": validation_mae,
            "examples": args.examples,
            "seed": args.seed,
        },
        args.output,
    )
    print(f"saved {args.output} validation_mae={validation_mae:.4f}")


if __name__ == "__main__":
    main()
