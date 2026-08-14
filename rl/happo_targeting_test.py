"""Regression checks for HAPPO's learned vulnerable-target preference."""

import numpy as np

from rl.happo_targeting import (
    TARGET_DEF_WEAKNESS,
    TARGET_LOWEST_DEF,
    TARGET_LOWEST_HP,
    TARGET_LOWEST_SPIRIT,
    TARGET_SPIRIT_WEAKNESS,
    add_target_priority_features,
    target_selection_reward,
)
from rl.tactical_policy import FEATURE_COUNT


def unit(unit_id, force, hp, maximum, defense, spirit):
    return {
        "id": unit_id, "force": force, "hp": hp, "max_hp": maximum,
        "def": defense, "int": spirit, "x": unit_id, "y": 1,
        "attack_min": 1, "attack_max": 1,
        "attack_offsets": ((1, 0),), "done": False, "dead": False,
    }


def main() -> None:
    units = [
        unit(0, 4, 100, 100, 80, 80),
        unit(1, 1, 25, 100, 95, 90),   # lowest HP
        unit(2, 1, 80, 100, 35, 85),   # lowest defense
        unit(3, 1, 75, 100, 80, 25),   # lowest spirit
    ]
    actions = []
    for action_type in (2, 3):
        for target in (1, 2, 3):
            actions.append({
                "index": len(actions), "unit": 0, "type": action_type,
                "x": 0, "y": 1, "target": target, "damage": 30,
                "skill": "fire_0" if action_type == 3 else None,
            })
    tactical = add_target_priority_features(
        actions, units, np.zeros((len(actions), FEATURE_COUNT), dtype=np.float32)
    )

    assert tactical[0, TARGET_LOWEST_HP] == 1.0
    assert tactical[1, TARGET_LOWEST_DEF] == 1.0
    assert tactical[5, TARGET_LOWEST_SPIRIT] == 1.0
    assert tactical[1, TARGET_DEF_WEAKNESS] > tactical[0, TARGET_DEF_WEAKNESS]
    assert tactical[5, TARGET_SPIRIT_WEAKNESS] > tactical[3, TARGET_SPIRIT_WEAKNESS]

    physical_low_hp = target_selection_reward(actions[0], tactical[0], units)
    physical_low_def = target_selection_reward(actions[1], tactical[1], units)
    physical_robust = target_selection_reward(actions[2], tactical[2], units)
    magic_low_spirit = target_selection_reward(actions[5], tactical[5], units)
    magic_robust = target_selection_reward(actions[4], tactical[4], units)
    assert physical_low_hp > physical_robust
    assert physical_low_def > physical_robust
    assert magic_low_spirit > magic_robust

    nonlethal = dict(actions[0], damage=24)
    lethal = dict(actions[0], damage=25)
    assert target_selection_reward(lethal, tactical[0], units) >= target_selection_reward(nonlethal, tactical[0], units) + 0.44
    print("happo targeting ok: low HP/DEF physical and low HP/INT magic signals")


if __name__ == "__main__":
    main()
