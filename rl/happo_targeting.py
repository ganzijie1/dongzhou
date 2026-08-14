"""Learnable target-vulnerability signals for HAPPO candidate actions."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


# These replace redundant tactical-policy columns while preserving the shared
# 34-dimensional HAPPO/CQL candidate schema.
TARGET_HP_WEAKNESS = 6
TARGET_DEF_WEAKNESS = 7
TARGET_SPIRIT_WEAKNESS = 8
TARGET_LOWEST_HP = 12
TARGET_LOWEST_DEF = 18
TARGET_LOWEST_SPIRIT = 19

TARGET_FEATURE_NAMES = {
    TARGET_HP_WEAKNESS: "target_hp_weakness",
    TARGET_DEF_WEAKNESS: "target_defense_weakness",
    TARGET_SPIRIT_WEAKNESS: "target_spirit_weakness",
    TARGET_LOWEST_HP: "target_is_lowest_hp",
    TARGET_LOWEST_DEF: "target_is_lowest_defense",
    TARGET_LOWEST_SPIRIT: "target_is_lowest_spirit",
}


def _weakness(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 0.5
    return float((maximum - value) / (maximum - minimum))


def add_target_priority_features(
    actions: Sequence[dict[str, Any]],
    units: Sequence[dict[str, Any]],
    tactical: np.ndarray,
) -> np.ndarray:
    """Replace redundant columns with relative vulnerability descriptors."""
    result = np.asarray(tactical, dtype=np.float32).copy()
    for column in TARGET_FEATURE_NAMES:
        result[:, column] = 0.0
    if not actions:
        return result

    by_id = {
        int(unit["id"]): unit
        for unit in units
        if not bool(unit.get("dead", False))
    }
    actor = by_id.get(int(actions[0]["unit"]))
    if actor is None:
        return result
    actor_force = int(actor["force"])
    target_ids = {
        int(action["target"])
        for action in actions
        if int(action.get("type", 0)) in (2, 3)
        and action.get("target") is not None
        and int(action["target"]) in by_id
        and int(by_id[int(action["target"])]["force"]) != actor_force
    }
    if not target_ids:
        return result

    targets = [by_id[target_id] for target_id in target_ids]
    hp_ratios = {
        int(target["id"]): float(target["hp"])
        / max(1.0, float(target["max_hp"]))
        for target in targets
    }
    defenses = {int(target["id"]): float(target.get("def", 0)) for target in targets}
    spirits = {int(target["id"]): float(target.get("int", 0)) for target in targets}
    hp_min, hp_max = min(hp_ratios.values()), max(hp_ratios.values())
    def_min, def_max = min(defenses.values()), max(defenses.values())
    spirit_min, spirit_max = min(spirits.values()), max(spirits.values())

    for row, action in enumerate(actions):
        target_value = action.get("target")
        if target_value is None or int(target_value) not in target_ids:
            continue
        target_id = int(target_value)
        hp = hp_ratios[target_id]
        defense = defenses[target_id]
        spirit = spirits[target_id]
        result[row, TARGET_HP_WEAKNESS] = _weakness(hp, hp_min, hp_max)
        result[row, TARGET_DEF_WEAKNESS] = _weakness(defense, def_min, def_max)
        result[row, TARGET_SPIRIT_WEAKNESS] = _weakness(
            spirit, spirit_min, spirit_max
        )
        result[row, TARGET_LOWEST_HP] = float(hp <= hp_min + 1e-6)
        result[row, TARGET_LOWEST_DEF] = float(defense <= def_min + 1e-6)
        result[row, TARGET_LOWEST_SPIRIT] = float(
            spirit <= spirit_min + 1e-6
        )
    return result


def target_selection_reward(
    action: dict[str, Any],
    tactical: np.ndarray,
    units: Sequence[dict[str, Any]],
) -> float:
    """Dense training signal; runtime target selection remains policy-driven."""
    action_type = int(action.get("type", 0))
    target_value = action.get("target")
    if action_type not in (2, 3) or target_value is None:
        return 0.0

    target = next(
        (unit for unit in units if int(unit["id"]) == int(target_value)), None
    )
    if target is None:
        return 0.0

    hp_signal = (
        0.25 * float(tactical[TARGET_HP_WEAKNESS])
        + 0.15 * float(tactical[TARGET_LOWEST_HP])
    )
    if action_type == 2:
        resistance_signal = (
            0.22 * float(tactical[TARGET_DEF_WEAKNESS])
            + 0.12 * float(tactical[TARGET_LOWEST_DEF])
        )
    else:
        resistance_signal = (
            0.22 * float(tactical[TARGET_SPIRIT_WEAKNESS])
            + 0.12 * float(tactical[TARGET_LOWEST_SPIRIT])
        )
    predicted_damage = max(0.0, float(action.get("damage", 0)))
    lethal = predicted_damage > 0.0 and predicted_damage >= float(target["hp"])
    return hp_signal + resistance_signal + 0.45 * float(lethal)
