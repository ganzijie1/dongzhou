"""Train a masked PPO baseline without requiring demonstration files."""

from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from rl.mengde_env import MengdeEnv
from rl.smoke_test import find_executable


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path)
    parser.add_argument("--output", type=Path, default=Path("rl/models/enemy_ppo"))
    parser.add_argument("--steps", type=int, default=30_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    env = MengdeEnv(find_executable(args.executable), max_episode_actions=100)
    try:
        model = MaskablePPO(
            "MlpPolicy",
            env,
            learning_rate=3e-4,
            n_steps=512,
            batch_size=128,
            n_epochs=4,
            gamma=0.99,
            policy_kwargs={"net_arch": {"pi": [128, 128], "vf": [128, 128]}},
            seed=args.seed,
            verbose=1,
        )
        model.learn(total_timesteps=args.steps)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        model.save(args.output)
        print(f"saved {args.output}.zip")
    finally:
        env.close()


if __name__ == "__main__":
    main()
