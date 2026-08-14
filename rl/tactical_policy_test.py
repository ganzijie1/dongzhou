"""Regression tests for learned ranged/melee formation coordination."""

from __future__ import annotations

from pathlib import Path

from rl.tactical_policy import action_features, choose_action, load_ranker


def unit(unit_id, force, unit_class, x, y, attack_offsets):
    distances = [abs(dx) + abs(dy) for dx, dy in attack_offsets]
    return {
        "id": unit_id, "force": force, "class": unit_class, "x": x, "y": y,
        "attack_offsets": attack_offsets, "attack_min": min(distances),
        "attack_max": max(distances), "move": 5, "hp": 100, "max_hp": 100,
        "done": False, "dead": False,
    }


def main() -> None:
    melee = ((0, -1), (0, 1), (-1, 0), (1, 0))
    ranged = ((0, -2), (1, -1), (2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0), (-1, -1))
    units = [
        unit(0, 1, "Infantry", 5, 2, melee),
        unit(1, 1, "Infantry", 6, 2, melee),
        unit(2, 4, "Infantry", 5, 3, melee),  # adjacent front line
        unit(3, 4, "Cavalry", 6, 3, melee),   # adjacent front line
        unit(4, 4, "Infantry", 5, 4, melee),  # rear blocker
        unit(5, 4, "Cavalry", 6, 4, melee),   # rear blocker
        unit(6, 4, "Archer", 5, 6, ranged),
        unit(7, 4, "Archer", 6, 6, ranged),
    ]
    width, height = 12, 10
    costs = [255] * (width * height)
    for y in range(2, 8):
        for x in (5, 6):
            costs[y * width + x] = 1
    costs[4 * width + 4] = 1
    costs[4 * width + 7] = 1
    movement_costs = {6: costs, 7: costs}
    blocked_actions = [
        {"index": 0, "unit": 2, "type": 0, "x": 5, "y": 3, "target": None},
        {"index": 1, "unit": 3, "type": 0, "x": 6, "y": 3, "target": None},
        {"index": 2, "unit": 4, "type": 0, "x": 5, "y": 4, "target": None},
        {"index": 3, "unit": 4, "type": 1, "x": 4, "y": 4, "target": None},
        {"index": 4, "unit": 5, "type": 0, "x": 6, "y": 4, "target": None},
        {"index": 5, "unit": 5, "type": 1, "x": 7, "y": 4, "target": None},
        {"index": 6, "unit": 6, "type": 0, "x": 5, "y": 6, "target": None},
    ]
    features = action_features(blocked_actions, units, width, height, movement_costs)
    assert features[0, 15] == 0 and features[1, 15] == 0
    assert features[2, 15] == 1 and features[3, 16] == 1
    assert features[4, 15] == 1 and features[5, 16] == 1

    model = load_ranker(Path("rl/models/enemy_tactical_ranker.pt"))
    assert choose_action(model, blocked_actions, units, width, height, None, movement_costs) in (3, 5)

    # One rear unit steps aside. A firing route now exists, so the remaining
    # melee units no longer receive a clearing preference and the archer shoots.
    units[4]["x"], units[4]["y"] = 4, 4
    firing_actions = [
        {"index": 0, "unit": 3, "type": 2, "x": 6, "y": 3, "target": 1, "damage": 30},
        {"index": 1, "unit": 6, "type": 2, "x": 5, "y": 4, "target": 0, "damage": 30},
        {"index": 2, "unit": 5, "type": 0, "x": 6, "y": 4, "target": None},
    ]
    reopened = action_features(firing_actions, units, width, height, movement_costs)
    assert reopened[2, 15] == 0, "melee was asked to move despite an open archer route"
    assert choose_action(model, firing_actions, units, width, height, None, movement_costs) == 1
    print("learned tactics ok: Dijkstra clears one rear blocker, preserves front line, archer fires")


if __name__ == "__main__":
    main()