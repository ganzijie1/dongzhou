"""Collect human state-action demonstrations from the real mengde rules."""

from __future__ import annotations

import argparse
from pathlib import Path

from rl.demo_data import save_transitions
from rl.mengde_env import MengdeEnv


ACTION_NAMES = {0: "等待", 1: "移动", 2: "攻击"}


def print_board(observation) -> None:
    width = max(1, round(float(observation[2]) * 64))
    height = max(1, round(float(observation[3]) * 64))
    board = [[" . " for _ in range(width)] for _ in range(height)]
    for unit_id in range((len(observation) - 4) // 16):
        offset = 4 + unit_id * 16
        if observation[offset] < 0.5 or observation[offset + 4] < 0.5:
            continue
        if observation[offset + 1] > 0.5:
            marker = "O"
        elif observation[offset + 2] > 0.5:
            marker = "A"
        else:
            marker = "E"
        x = round(float(observation[offset + 6]) * max(1, width - 1))
        y = round(float(observation[offset + 7]) * max(1, height - 1))
        board[y][x] = f"{marker}{unit_id % 10} "
    print("\n    " + "".join(f"{x % 10:>3}" for x in range(width)))
    for y, row in enumerate(board):
        print(f"{y:>3} " + "".join(row))
    print("O=己方，A=友军，E=敌军；数字为单位编号的个位。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("rl/demonstrations/player.npz"))
    parser.add_argument("--scenario", default="example")
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--max-actions", type=int, default=2048)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    observations = []
    actions = []
    next_observations = []
    dones = []

    with MengdeEnv(args.executable, args.scenario, max_actions=args.max_actions) as env:
        observation, _ = env.reset()
        episode = 1
        while episode <= args.episodes:
            legal = env.list_actions()
            print(f"\n第 {episode}/{args.episodes} 局")
            print_board(observation)
            unit_ids = sorted({int(action["unit"]) for action in legal})
            print("本回合可行动单位：" + ", ".join(map(str, unit_ids)))
            raw_unit = input("选择单位编号（q 结束并保存）: ").strip()
            if raw_unit.lower() == "q":
                save_transitions(
                    args.output, observations, actions, next_observations, dones
                )
                print(f"已保存 {len(actions)} 条示范到 {args.output}")
                return
            try:
                selected_unit = int(raw_unit)
            except ValueError:
                print("请输入有效单位编号。")
                continue
            unit_actions = [
                action for action in legal if int(action["unit"]) == selected_unit
            ]
            if not unit_actions:
                print("该单位当前不可行动。")
                continue

            print("可选动作：")
            for action in unit_actions:
                name = ACTION_NAMES[int(action["type"])]
                target = "" if action["target"] is None else f" -> 目标{action['target']}"
                print(
                    f"{action['index']:4d}: 单位{action['unit']} {name} "
                    f"({action['x']}, {action['y']}){target}"
                )

            while True:
                raw = input("动作编号（q 结束并保存）: ").strip()
                if raw.lower() == "q":
                    save_transitions(
                        args.output, observations, actions, next_observations, dones
                    )
                    print(f"已保存 {len(actions)} 条示范到 {args.output}")
                    return
                try:
                    selected = int(raw)
                    if any(int(action["index"]) == selected for action in unit_actions):
                        break
                except ValueError:
                    pass
                print("请输入列表中的动作编号。")

            next_observation, _, terminated, truncated, _ = env.step(selected)
            done = terminated or truncated
            observations.append(observation.copy())
            actions.append(selected)
            next_observations.append(next_observation.copy())
            dones.append(done)
            observation = next_observation
            if done:
                episode += 1
                if episode <= args.episodes:
                    observation, _ = env.reset()

    save_transitions(args.output, observations, actions, next_observations, dones)
    print(f"已保存 {len(actions)} 条示范到 {args.output}")


if __name__ == "__main__":
    main()
