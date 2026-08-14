"""Parameter-sharing MAPPO for Mengde's sequential multi-unit turns.

The shared actor sees one unit plus each legal action's descriptors. The
central critic sees the complete native battle observation during training.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

from rl.mengde_env import MengdeEnv


LOCAL_FEATURES = 20
ACTION_FEATURES = 14


class SharedActor(nn.Module):
    def __init__(self, hidden: int = 128) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(LOCAL_FEATURES + ACTION_FEATURES, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, local: torch.Tensor, candidates: torch.Tensor) -> torch.Tensor:
        expanded = local.unsqueeze(1).expand(-1, candidates.shape[1], -1)
        return self.network(torch.cat((expanded, candidates), dim=-1)).squeeze(-1)


class CentralCritic(nn.Module):
    def __init__(self, state_features: int, hidden: int = 256) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_features, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state).squeeze(-1)


@dataclass
class Decision:
    agent_id: int
    actions: list[dict[str, Any]]
    local: np.ndarray
    candidates: np.ndarray


@dataclass
class Transition:
    state: np.ndarray
    local: np.ndarray
    candidates: np.ndarray
    choice: int
    log_prob: float
    value: float
    reward: float
    done: bool


def local_observation(observation: np.ndarray, agent_id: int, max_units: int) -> np.ndarray:
    local = np.zeros(LOCAL_FEATURES, dtype=np.float32)
    local[:4] = observation[:4]
    if 0 <= agent_id < max_units:
        start = 4 + agent_id * 16
        local[4:] = observation[start : start + 16]
    return local


def select_agent_actions(actions: list[dict[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
    if not actions:
        raise ValueError("native environment returned no legal actions")
    agent_id = min(int(action["unit"]) for action in actions)
    return agent_id, [action for action in actions if int(action["unit"]) == agent_id]


def action_features(
    actions: list[dict[str, Any]],
    units: list[dict[str, Any]],
    width: int,
    height: int,
    agent_id: int,
) -> np.ndarray:
    by_id = {int(unit["id"]): unit for unit in units}
    actor = by_id[agent_id]
    actor_x, actor_y = int(actor["x"]), int(actor["y"])
    result = np.zeros((len(actions), ACTION_FEATURES), dtype=np.float32)
    for row, action in enumerate(actions):
        action_type = max(0, min(3, int(action["type"])))
        result[row, action_type] = 1.0
        x, y = int(action["x"]), int(action["y"])
        result[row, 4] = x / max(1, width - 1)
        result[row, 5] = y / max(1, height - 1)
        result[row, 6] = abs(x - actor_x) + abs(y - actor_y)
        result[row, 6] /= max(1, width + height - 2)
        target_id = action.get("target")
        target = by_id.get(int(target_id)) if target_id is not None else None
        if target is not None:
            result[row, 7] = 1.0
            result[row, 8] = (int(target["x"]) - x) / max(1, width - 1)
            result[row, 9] = (int(target["y"]) - y) / max(1, height - 1)
            result[row, 10] = float(target["hp"]) / max(1.0, float(target["max_hp"]))
            result[row, 11] = float(int(target["force"]) != int(actor["force"]))
        result[row, 12] = float(bool(action.get("skill")))
        result[row, 13] = 1.0
    return result


def current_decision(env: MengdeEnv, observation: np.ndarray, width: int, height: int) -> Decision:
    actions = env.list_actions()
    agent_id, selected = select_agent_actions(actions)
    units = env.unit_info()
    return Decision(
        agent_id=agent_id,
        actions=selected,
        local=local_observation(observation, agent_id, env.max_units),
        candidates=action_features(selected, units, width, height, agent_id),
    )


def pad_candidates(values: list[np.ndarray], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    maximum = max(len(value) for value in values)
    padded = np.zeros((len(values), maximum, ACTION_FEATURES), dtype=np.float32)
    mask = np.zeros((len(values), maximum), dtype=np.bool_)
    for row, value in enumerate(values):
        padded[row, : len(value)] = value
        mask[row, : len(value)] = True
    return torch.as_tensor(padded, device=device), torch.as_tensor(mask, device=device)


class MAPPO:
    def __init__(
        self,
        state_features: int,
        *,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
        seed: int = 42,
        device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.device = torch.device(device)
        self.actor = SharedActor().to(self.device)
        self.critic = CentralCritic(state_features).to(self.device)
        self.optimizer = torch.optim.Adam(
            [*self.actor.parameters(), *self.critic.parameters()], learning_rate
        )
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_range = clip_range
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.rng = np.random.default_rng(seed)

    @torch.no_grad()
    def choose(self, decision: Decision, deterministic: bool = False) -> tuple[int, float, float]:
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(decision.candidates, device=self.device).unsqueeze(0)
        distribution = Categorical(logits=self.actor(local, candidates)[0])
        choice = torch.argmax(distribution.logits) if deterministic else distribution.sample()
        return int(choice), float(distribution.log_prob(choice)), 0.0

    def _value(self, state: np.ndarray) -> float:
        with torch.no_grad():
            tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
            return float(self.critic(tensor)[0])

    def collect(self, env: MengdeEnv, steps: int, seed: int) -> list[Transition]:
        observation, _ = env.reset(seed=seed)
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        transitions: list[Transition] = []
        for _ in range(steps):
            decision = current_decision(env, observation, width, height)
            value = self._value(observation)
            choice, log_prob, _ = self.choose(decision)
            next_observation, reward, terminated, truncated, _ = env.step(
                int(decision.actions[choice]["index"])
            )
            done = terminated or truncated
            transitions.append(
                Transition(
                    state=observation.copy(), local=decision.local,
                    candidates=decision.candidates, choice=choice,
                    log_prob=log_prob, value=value, reward=float(reward), done=done,
                )
            )
            observation = next_observation
            if done:
                observation, _ = env.reset(seed=seed + len(transitions))
        self._bootstrap_value = self._value(observation)
        return transitions

    def update(self, transitions: list[Transition], epochs: int = 4, batch_size: int = 128) -> dict[str, float]:
        rewards = np.asarray([item.reward for item in transitions], dtype=np.float32)
        values = np.asarray([item.value for item in transitions] + [self._bootstrap_value], dtype=np.float32)
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

        old_log_probs = np.asarray([item.log_prob for item in transitions], dtype=np.float32)
        choices = np.asarray([item.choice for item in transitions], dtype=np.int64)
        locals_ = np.stack([item.local for item in transitions])
        states = np.stack([item.state for item in transitions])
        losses: list[tuple[float, float, float]] = []
        for _ in range(epochs):
            order = self.rng.permutation(len(transitions))
            for start in range(0, len(order), batch_size):
                indices = order[start : start + batch_size]
                candidates, mask = pad_candidates(
                    [transitions[int(i)].candidates for i in indices], self.device
                )
                local_tensor = torch.as_tensor(locals_[indices], device=self.device)
                logits = self.actor(local_tensor, candidates).masked_fill(~mask, -1e9)
                distribution = Categorical(logits=logits)
                choice_tensor = torch.as_tensor(choices[indices], device=self.device)
                new_log_probs = distribution.log_prob(choice_tensor)
                old_tensor = torch.as_tensor(old_log_probs[indices], device=self.device)
                advantage_tensor = torch.as_tensor(advantages[indices], device=self.device)
                ratio = torch.exp(new_log_probs - old_tensor)
                policy_loss = -torch.min(
                    ratio * advantage_tensor,
                    torch.clamp(ratio, 1.0 - self.clip_range, 1.0 + self.clip_range) * advantage_tensor,
                ).mean()
                state_tensor = torch.as_tensor(states[indices], device=self.device)
                return_tensor = torch.as_tensor(returns[indices], device=self.device)
                value_loss = torch.square(self.critic(state_tensor) - return_tensor).mean()
                entropy = distribution.entropy().mean()
                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_([*self.actor.parameters(), *self.critic.parameters()], 0.5)
                self.optimizer.step()
                losses.append((float(policy_loss), float(value_loss), float(entropy)))
        mean = np.mean(losses, axis=0)
        return {"policy_loss": float(mean[0]), "value_loss": float(mean[1]), "entropy": float(mean[2])}

    def learn(
        self,
        env: MengdeEnv,
        total_steps: int,
        *,
        rollout_steps: int = 512,
        epochs: int = 4,
        batch_size: int = 128,
        seed: int = 42,
    ) -> list[dict[str, float]]:
        history = []
        completed = 0
        while completed < total_steps:
            count = min(rollout_steps, total_steps - completed)
            transitions = self.collect(env, count, seed + completed)
            metrics = self.update(transitions, epochs=epochs, batch_size=batch_size)
            completed += count
            metrics["steps"] = float(completed)
            history.append(metrics)
        return history

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "algorithm": "parameter-sharing-mappo",
                "actor": self.actor.state_dict(),
                "critic": self.critic.state_dict(),
                "local_features": LOCAL_FEATURES,
                "action_features": ACTION_FEATURES,
            },
            destination,
        )

    @property
    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.actor.parameters()) + sum(
            parameter.numel() for parameter in self.critic.parameters()
        )
