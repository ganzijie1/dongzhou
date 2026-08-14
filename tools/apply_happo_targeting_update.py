from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


happo = ROOT / "rl/happo.py"
replace_once(
    happo,
    "from rl.mengde_env import MengdeEnv\nfrom rl.tactical_policy import FEATURE_COUNT, action_features as tactical_action_features\n",
    "from rl.mengde_env import MengdeEnv\n"
    "from rl.happo_targeting import TARGET_FEATURE_NAMES, add_target_priority_features\n"
    "from rl.tactical_policy import FEATURE_COUNT, action_features as tactical_action_features\n",
)
replace_once(
    happo,
    "    tactical = tactical_action_features(\n        selected, units, width, height, fast_path_features=True\n    )\n",
    "    tactical = tactical_action_features(\n"
    "        selected, units, width, height, fast_path_features=True\n"
    "    )\n"
    "    tactical = add_target_priority_features(selected, units, tactical)\n",
)
replace_once(
    happo,
    '                "action_features": HAPPO_ACTION_FEATURES,\n',
    '                "action_features": HAPPO_ACTION_FEATURES,\n'
    '                "target_priority_features": TARGET_FEATURE_NAMES,\n',
)

trainer = ROOT / "rl/train_happo_dongzhou.py"
replace_once(
    trainer,
    "from rl.happo import HAPPO, HAPPOTransition, decision_role, happo_decision\n",
    "from rl.happo import HAPPO, HAPPOTransition, decision_role, happo_decision\n"
    "from rl.happo_targeting import target_selection_reward\n",
)
replace_once(
    trainer,
    "            shaped_reward += 0.20 * float(action_type in (2, 3))\n",
    "            shaped_reward += 0.20 * float(action_type in (2, 3))\n"
    "            shaped_reward += target_selection_reward(chosen, tactical, units)\n",
)

print("HAPPO target-priority features and reward shaping installed.")
