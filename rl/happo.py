"""Turn-based HAPPO adaptation for Mengde's heterogeneous unit classes.

Each unit class owns an independent actor. Actors are updated sequentially in
a randomized order while a centralized critic evaluates the full battle state.
For the native AEC turn order, preceding-policy ratios are propagated forward
within each episode as the sequential HAPPO correction factor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

from rl.mappo import (
    ACTION_FEATURES,
    LOCAL_FEATURES,

    Decision,
    action_features as base_action_features,
    local_observation,
    select_agent_actions,
)
from rl.mengde_env import MengdeEnv
from rl.happo_targeting import TARGET_FEATURE_NAMES, add_target_priority_features
from rl.happo_target_aux import target_priority_ranking_loss
from rl.tactical_policy import FEATURE_COUNT, action_features as tactical_action_features


ROLE_NAMES = (
    "Lord", "King", "Infantry", "Cavalry", "Archer", "Strategist",
    "Support", "Artillery", "Fighter", "Bandit", "Other",
)
HAPPO_ACTION_FEATURES = ACTION_FEATURES + FEATURE_COUNT


class HAPPOActor(nn.Module):
    def __init__(self, hidden: int = 128) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(LOCAL_FEATURES + HAPPO_ACTION_FEATURES, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, local: torch.Tensor, candidates: torch.Tensor) -> torch.Tensor:
        expanded = local.unsqueeze(1).expand(-1, candidates.shape[1], -1)
        return self.network(torch.cat((expanded, candidates), dim=-1)).squeeze(-1)


class PopArtCritic(nn.Module):
    """Shared central critic with output-preserving return normalization."""

    def __init__(
        self, state_features: int, hidden: int = 256,
        beta: float = 0.999, epsilon: float = 1e-5,
    ) -> None:
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(state_features, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
        )
        self.output = nn.Linear(hidden, 1)
        self.beta = beta
        self.epsilon = epsilon
        self.register_buffer("mean", torch.zeros(1))
        self.register_buffer("second_moment", torch.ones(1))
        self.register_buffer("std", torch.ones(1))

    def normalized(self, state: torch.Tensor) -> torch.Tensor:
        return self.output(self.body(state)).squeeze(-1)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.normalized(state) * self.std + self.mean

    def normalize(self, values: torch.Tensor) -> torch.Tensor:
        return (values - self.mean) / self.std

    @torch.no_grad()
    def update_stats(self, values: torch.Tensor) -> None:
        old_mean = self.mean.clone()
        old_std = self.std.clone()
        batch_mean = values.mean()
        batch_second = torch.square(values).mean()
        new_mean = self.beta * self.mean + (1.0 - self.beta) * batch_mean
        new_second = (
            self.beta * self.second_moment
            + (1.0 - self.beta) * batch_second
        )
        new_std = torch.sqrt(
            torch.clamp(
                new_second - torch.square(new_mean), min=self.epsilon
            )
        )
        self.output.weight.mul_(old_std / new_std)
        self.output.bias.mul_(old_std).add_(
            old_mean - new_mean
        ).div_(new_std)
        self.mean.copy_(new_mean)
        self.second_moment.copy_(new_second)
        self.std.copy_(new_std)


def happo_decision(
    env: MengdeEnv,
    observation: np.ndarray,
    width: int,
    height: int,
    actions: list[dict[str, Any]] | None = None,
) -> Decision:
    legal = env.list_actions() if actions is None else actions
    agent_id, selected = select_agent_actions(legal)
    units = env.unit_info()
    basic = base_action_features(selected, units, width, height, agent_id)
    tactical = tactical_action_features(
        selected, units, width, height, fast_path_features=True
    )
    tactical = add_target_priority_features(selected, units, tactical)
    return Decision(
        agent_id=agent_id,
        actions=selected,
        local=local_observation(observation, agent_id, env.max_units),
        candidates=np.concatenate((basic, tactical), axis=1),
    )


def pad_happo_candidates(
    values: list[np.ndarray], device: torch.device
) -> tuple[torch.Tensor, torch.Tensor]:
    maximum = max(len(value) for value in values)
    padded = np.zeros(
        (len(values), maximum, HAPPO_ACTION_FEATURES), dtype=np.float32
    )
    mask = np.zeros((len(values), maximum), dtype=np.bool_)
    for row, value in enumerate(values):
        padded[row, : len(value)] = value
        mask[row, : len(value)] = True
    return torch.as_tensor(padded, device=device), torch.as_tensor(mask, device=device)


@dataclass
class HAPPOTransition:
    state: np.ndarray
    local: np.ndarray
    candidates: np.ndarray
    choice: int
    role: str
    log_prob: float
    value: float
    reward: float
    done: bool
    behavior_bias: np.ndarray | None = None


def normalized_role(value: str) -> str:
    return value if value in ROLE_NAMES else "Other"


def decision_role(env: MengdeEnv, decision: Decision) -> str:
    unit = next(unit for unit in env.unit_info() if int(unit["id"]) == decision.agent_id)
    return normalized_role(str(unit["class"]))


class HAPPO:
    def __init__(
        self,
        state_features: int,
        *,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        entropy_coef: float = 0.02,
        value_coef: float = 0.5,
        target_aux_coef: float = 0.15,
        seed: int = 42,
        device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.device = torch.device(device)
        self.actors = nn.ModuleDict({role: HAPPOActor() for role in ROLE_NAMES}).to(self.device)
        self.critic = PopArtCritic(state_features).to(self.device)
        self.actor_optimizers = {
            role: torch.optim.Adam(self.actors[role].parameters(), learning_rate)
            for role in ROLE_NAMES
        }
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), learning_rate)
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_range = clip_range
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.target_aux_coef = target_aux_coef
        self.rng = np.random.default_rng(seed)
        self._bootstrap_value = 0.0

    @torch.no_grad()
    def choose(
        self, decision: Decision, role: str, deterministic: bool = False,
        behavior_bias: np.ndarray | None = None,
    ) -> tuple[int, float]:
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(decision.candidates, device=self.device).unsqueeze(0)
        logits = self.actors[normalized_role(role)](local, candidates)[0]
        if behavior_bias is not None:
            logits = logits + torch.as_tensor(behavior_bias, device=self.device)
        distribution = Categorical(logits=logits)
        choice = torch.argmax(distribution.logits) if deterministic else distribution.sample()
        return int(choice), float(distribution.log_prob(choice))

    def _value(self, state: np.ndarray) -> float:
        with torch.no_grad():
            tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
            return float(self.critic(tensor)[0])

    def collect(self, env: MengdeEnv, steps: int, seed: int) -> list[HAPPOTransition]:
        observation, _ = env.reset(seed=seed)
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        transitions: list[HAPPOTransition] = []
        for _ in range(steps):
            decision = happo_decision(env, observation, width, height)
            role = decision_role(env, decision)
            value = self._value(observation)
            choice, log_prob = self.choose(decision, role)
            next_observation, reward, terminated, truncated, _ = env.step(
                int(decision.actions[choice]["index"])
            )
            done = terminated or truncated
            transitions.append(
                HAPPOTransition(
                    state=observation.copy(), local=decision.local,
                    candidates=decision.candidates, choice=choice, role=role,
                    log_prob=log_prob, value=value, reward=float(reward), done=done,
                )
            )
            observation = next_observation
            if done:
                observation, _ = env.reset(seed=seed + len(transitions))
        self._bootstrap_value = self._value(observation)
        return transitions

    def _advantages(
        self, transitions: list[HAPPOTransition]
    ) -> tuple[np.ndarray, np.ndarray]:
        rewards = np.asarray([item.reward for item in transitions], dtype=np.float32)
        values = np.asarray(
            [item.value for item in transitions] + [self._bootstrap_value], dtype=np.float32
        )
        dones = np.asarray([item.done for item in transitions], dtype=np.float32)
        advantages = np.zeros(len(transitions), dtype=np.float32)
        gae = 0.0
        for index in range(len(transitions) - 1, -1, -1):
            nonterminal = 1.0 - dones[index]
            delta = rewards[index] + self.gamma * values[index + 1] * nonterminal - values[index]
            gae = delta + self.gamma * self.gae_lambda * nonterminal * gae
            advantages[index] = gae
        returns = advantages + values[:-1]
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        return advantages, returns

    def _role_ratios(
        self, role: str, indices: np.ndarray, transitions: list[HAPPOTransition],
        batch_size: int,
    ) -> np.ndarray:
        if len(indices) == 0:
            return np.empty(0, dtype=np.float32)
        result = np.empty(len(indices), dtype=np.float32)
        positions = np.asarray(sorted(
            range(len(indices)),
            key=lambda pos: len(transitions[int(indices[pos])].candidates),
        ))
        for start in range(0, len(positions), batch_size):
            batch_positions = positions[start : start + batch_size]
            batch_indices = indices[batch_positions]
            candidates, mask = pad_happo_candidates(
                [transitions[int(index)].candidates for index in batch_indices],
                self.device,
            )
            locals_ = torch.as_tensor(
                np.stack([
                    transitions[int(index)].local for index in batch_indices
                ]),
                device=self.device,
            )
            choices = torch.as_tensor(
                [transitions[int(index)].choice for index in batch_indices],
                device=self.device,
            )
            old = torch.as_tensor(
                [transitions[int(index)].log_prob for index in batch_indices],
                device=self.device,
            )
            with torch.no_grad():
                logits = self.actors[role](locals_, candidates)
                bias_tensor = torch.zeros_like(logits)
                for row, index in enumerate(batch_indices):
                    bias = transitions[int(index)].behavior_bias
                    if bias is not None:
                        bias_tensor[row, : len(bias)] = torch.as_tensor(
                            bias, device=self.device
                        )
                logits = (logits + bias_tensor).masked_fill(~mask, -1e9)
                current = Categorical(logits=logits).log_prob(choices)
            result[batch_positions] = torch.exp(current - old).cpu().numpy()
        return result

    @staticmethod
    def _propagate_correction(
        correction: np.ndarray,
        role_indices: np.ndarray,
        ratios: np.ndarray,
        transitions: list[HAPPOTransition],
    ) -> None:
        by_index = {int(index): float(ratio) for index, ratio in zip(role_indices, ratios)}
        running = 1.0
        for index, transition in enumerate(transitions):
            correction[index] = np.clip(correction[index] * running, 0.5, 2.0)
            if index in by_index:
                running = float(np.clip(running * by_index[index], 0.5, 2.0))
            if transition.done:
                running = 1.0

    def update(
        self,
        transitions: list[HAPPOTransition],
        *,
        epochs: int = 4,
        batch_size: int = 128,
    ) -> dict[str, Any]:
        advantages, returns = self._advantages(transitions)
        old_log_probs = np.asarray([item.log_prob for item in transitions], dtype=np.float32)
        choices = np.asarray([item.choice for item in transitions], dtype=np.int64)
        correction = np.ones(len(transitions), dtype=np.float32)
        active_roles = sorted({item.role for item in transitions})
        role_order = [active_roles[int(index)] for index in self.rng.permutation(len(active_roles))]
        actor_losses: list[float] = []
        target_losses: list[float] = []
        entropies: list[float] = []

        for role in role_order:
            role_indices = np.asarray(
                [index for index, item in enumerate(transitions) if item.role == role],
                dtype=np.int64,
            )
            optimizer = self.actor_optimizers[role]
            for _ in range(epochs):
                order = np.asarray(sorted(
                    role_indices,
                    key=lambda index: len(transitions[int(index)].candidates),
                ))
                for start in range(0, len(order), batch_size):
                    indices = order[start : start + batch_size]
                    candidates, mask = pad_happo_candidates(
                        [transitions[int(index)].candidates for index in indices], self.device
                    )
                    locals_ = torch.as_tensor(
                        np.stack([transitions[int(index)].local for index in indices]),
                        device=self.device,
                    )
                    logits = self.actors[role](locals_, candidates)
                    bias_tensor = torch.zeros_like(logits)
                    for row, index in enumerate(indices):
                        bias = transitions[int(index)].behavior_bias
                        if bias is not None:
                            bias_tensor[row, : len(bias)] = torch.as_tensor(
                                bias, device=self.device
                            )
                    logits = (logits + bias_tensor).masked_fill(~mask, -1e9)
                    distribution = Categorical(logits=logits)
                    choice_tensor = torch.as_tensor(choices[indices], device=self.device)
                    new_log_probs = distribution.log_prob(choice_tensor)
                    old_tensor = torch.as_tensor(old_log_probs[indices], device=self.device)
                    weighted_advantage = torch.as_tensor(
                        advantages[indices] * correction[indices], device=self.device
                    )
                    ratio = torch.exp(new_log_probs - old_tensor)
                    policy_loss = -torch.min(
                        ratio * weighted_advantage,
                        torch.clamp(
                            ratio, 1.0 - self.clip_range, 1.0 + self.clip_range
                        ) * weighted_advantage,
                    ).mean()
                    entropy = distribution.entropy().mean()
                    target_loss = target_priority_ranking_loss(
                        logits, candidates, mask
                    )
                    loss = (
                        policy_loss - self.entropy_coef * entropy
                        + self.target_aux_coef * target_loss
                    )
                    optimizer.zero_grad()
                    loss.backward()
                    nn.utils.clip_grad_norm_(self.actors[role].parameters(), 0.5)
                    optimizer.step()
                    actor_losses.append(float(policy_loss))
                    target_losses.append(float(target_loss))
                    entropies.append(float(entropy))
            ratios = self._role_ratios(
                role, role_indices, transitions, batch_size
            )
            self._propagate_correction(correction, role_indices, ratios, transitions)

        states = np.stack([item.state for item in transitions])
        return_values = torch.as_tensor(returns, device=self.device)
        self.critic.update_stats(return_values)
        normalized_returns = self.critic.normalize(return_values).cpu().numpy()
        value_losses: list[float] = []
        for _ in range(epochs):
            order = self.rng.permutation(len(transitions))
            for start in range(0, len(order), batch_size):
                indices = order[start : start + batch_size]
                state_tensor = torch.as_tensor(states[indices], device=self.device)
                return_tensor = torch.as_tensor(
                    normalized_returns[indices], device=self.device
                )
                value_loss = torch.square(
                    self.critic.normalized(state_tensor) - return_tensor
                ).mean()
                self.critic_optimizer.zero_grad()
                (self.value_coef * value_loss).backward()
                nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)
                self.critic_optimizer.step()
                value_losses.append(float(value_loss))

        return {
            "policy_loss": float(np.mean(actor_losses)),
            "value_loss": float(np.mean(value_losses)),
            "target_priority_loss": float(np.mean(target_losses)),
            "entropy": float(np.mean(entropies)),
            "mean_correction": float(np.mean(correction)),
            "role_order": role_order,
        }

    def learn(
        self,
        env: MengdeEnv,
        total_steps: int,
        *,
        rollout_steps: int = 512,
        epochs: int = 4,
        batch_size: int = 128,
        seed: int = 42,
    ) -> list[dict[str, Any]]:
        history: list[dict[str, Any]] = []
        completed = 0
        while completed < total_steps:
            count = min(rollout_steps, total_steps - completed)
            transitions = self.collect(env, count, seed + completed)
            metrics = self.update(
                transitions, epochs=epochs, batch_size=batch_size
            )
            completed += count
            metrics["steps"] = completed
            history.append(metrics)
        return history

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "algorithm": "turn-based-happo",
                "actors": self.actors.state_dict(),
                "critic": self.critic.state_dict(),
                "roles": ROLE_NAMES,
                "action_features": HAPPO_ACTION_FEATURES,
                "target_priority_features": TARGET_FEATURE_NAMES,
                "value_normalization": "popart",
                "entropy_coef": self.entropy_coef,
                "target_aux_coef": self.target_aux_coef,
            },
            destination,
        )

    @property
    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.actors.parameters()) + sum(
            parameter.numel() for parameter in self.critic.parameters()
        )
