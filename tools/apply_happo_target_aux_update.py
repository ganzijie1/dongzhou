from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor missing: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


path = ROOT / "rl/happo.py"
replace_once(
    path,
    "from rl.happo_targeting import TARGET_FEATURE_NAMES, add_target_priority_features\n",
    "from rl.happo_targeting import TARGET_FEATURE_NAMES, add_target_priority_features\n"
    "from rl.happo_target_aux import target_priority_ranking_loss\n",
)
replace_once(
    path,
    "        entropy_coef: float = 0.02,\n        value_coef: float = 0.5,\n",
    "        entropy_coef: float = 0.02,\n"
    "        value_coef: float = 0.5,\n"
    "        target_aux_coef: float = 0.15,\n",
)
replace_once(
    path,
    "        self.value_coef = value_coef\n        self.rng = np.random.default_rng(seed)\n",
    "        self.value_coef = value_coef\n"
    "        self.target_aux_coef = target_aux_coef\n"
    "        self.rng = np.random.default_rng(seed)\n",
)
replace_once(
    path,
    "        actor_losses: list[float] = []\n        entropies: list[float] = []\n",
    "        actor_losses: list[float] = []\n"
    "        target_losses: list[float] = []\n"
    "        entropies: list[float] = []\n",
)
replace_once(
    path,
    "                    entropy = distribution.entropy().mean()\n                    loss = policy_loss - self.entropy_coef * entropy\n",
    "                    entropy = distribution.entropy().mean()\n"
    "                    target_loss = target_priority_ranking_loss(\n"
    "                        logits, candidates, mask\n"
    "                    )\n"
    "                    loss = (\n"
    "                        policy_loss - self.entropy_coef * entropy\n"
    "                        + self.target_aux_coef * target_loss\n"
    "                    )\n",
)
replace_once(
    path,
    "                    actor_losses.append(float(policy_loss))\n                    entropies.append(float(entropy))\n",
    "                    actor_losses.append(float(policy_loss))\n"
    "                    target_losses.append(float(target_loss))\n"
    "                    entropies.append(float(entropy))\n",
)
replace_once(
    path,
    '            "value_loss": float(np.mean(value_losses)),\n            "entropy": float(np.mean(entropies)),\n',
    '            "value_loss": float(np.mean(value_losses)),\n'
    '            "target_priority_loss": float(np.mean(target_losses)),\n'
    '            "entropy": float(np.mean(entropies)),\n',
)
replace_once(
    path,
    '                "entropy_coef": self.entropy_coef,\n',
    '                "entropy_coef": self.entropy_coef,\n'
    '                "target_aux_coef": self.target_aux_coef,\n',
)
print("HAPPO pairwise target-ranking auxiliary loss installed.")
