"""Run a trained Mirror Mode policy against the built-in mengde opponent."""

from __future__ import annotations

import argparse
from pathlib import Path

from sb3_contrib import MaskablePPO

from rl.mengde_env import MengdeEnv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--max-actions", type=int, default=2048)
    args = parser.parse_args()

    with MengdeEnv(args.executable, args.scenario, max_actions=args.max_actions) as env:
        model = MaskablePPO.load(args.model, env=env)
        for episode in range(1, args.episodes + 1):
            observation, _ = env.reset()
            total_reward = 0.0
            while True:
                action, _ = model.predict(
                    observation,
                    action_masks=env.action_masks(),
                    deterministic=False,
                )
                observation, reward, terminated, truncated, _ = env.step(int(action))
                total_reward += reward
                if terminated or truncated:
                    print(f"episode={episode} reward={total_reward:.3f}")
                    break


if __name__ == "__main__":
    main()
