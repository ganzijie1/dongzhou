"""Two-level hierarchical PPO for Mengde's sequential battle environment.

The manager samples a latent tactical option every few environment decisions.
The worker scores the active unit's legal actions conditioned on that option.
Both levels are trained end-to-end with PPO; options do not hard-code actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.distributions import Categorical

from rl.mappo import ACTION_FEATURES, LOCAL_FEATURES, Decision, current_decision, pad_candidates
from rl.mengde_env import MengdeEnv


class ManagerActor(nn.Module):
    def __init__(self, state_features: int, options: int, hidden: int = 128) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_features, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, options),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)


class WorkerActor(nn.Module):
    def __init__(self, options: int, hidden: int = 128) -> None:
        super().__init__()
        self.options = options
        self.network = nn.Sequential(
            nn.Linear(LOCAL_FEATURES + options + ACTION_FEATURES, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(
        self, local: torch.Tensor, option: torch.Tensor, candidates: torch.Tensor
    ) -> torch.Tensor:
        option_one_hot = torch.nn.functional.one_hot(
            option, num_classes=self.options
        ).to(dtype=local.dtype)
        context = torch.cat((local, option_one_hot), dim=-1)
        context = context.unsqueeze(1).expand(-1, candidates.shape[1], -1)
        return self.network(torch.cat((context, candidates), dim=-1)).squeeze(-1)


class ValueNetwork(nn.Module):
    def __init__(self, features: int, hidden: int = 256) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(features, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
            nn.Linear(hidden, 1),
        )

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return self.network(values).squeeze(-1)


@dataclass
class WorkerTransition:
    state: np.ndarray
    local: np.ndarray
    candidates: np.ndarray
    choice: int
    option: int
    log_prob: float
    value: float
    reward: float
    done: bool


@dataclass
class ManagerTransition:
    state: np.ndarray
    option: int
    log_prob: float
    value: float
    reward: float
    duration: int
    done: bool


class HPPO:
    """HiPPO-style manager/worker PPO with fixed-duration latent options."""

    def __init__(
        self,
        state_features: int,
        *,
        num_options: int = 4,
        option_horizon: int = 4,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_range: float = 0.2,
        entropy_coef: float = 0.01,
        manager_entropy_coef: float = 0.02,
        value_coef: float = 0.5,
        seed: int = 42,
        device: str = "cpu",
    ) -> None:
        if num_options < 2 or option_horizon < 1:
            raise ValueError("H-PPO needs at least two options and a positive horizon")
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.device = torch.device(device)
        self.state_features = state_features
        self.num_options = num_options
        self.option_horizon = option_horizon
        self.manager = ManagerActor(state_features, num_options).to(self.device)
        self.worker = WorkerActor(num_options).to(self.device)
        self.manager_critic = ValueNetwork(state_features).to(self.device)
        self.worker_critic = ValueNetwork(state_features + num_options).to(self.device)
        self.manager_optimizer = torch.optim.Adam(
            [*self.manager.parameters(), *self.manager_critic.parameters()], learning_rate
        )
        self.worker_optimizer = torch.optim.Adam(
            [*self.worker.parameters(), *self.worker_critic.parameters()], learning_rate
        )
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_range = clip_range
        self.entropy_coef = entropy_coef
        self.manager_entropy_coef = manager_entropy_coef
        self.value_coef = value_coef
        self.rng = np.random.default_rng(seed)
        self._worker_bootstrap = 0.0
        self._manager_bootstrap = 0.0

    def _option_state(self, state: np.ndarray, option: int) -> np.ndarray:
        result = np.zeros(self.state_features + self.num_options, dtype=np.float32)
        result[: self.state_features] = state
        result[self.state_features + option] = 1.0
        return result

    @torch.no_grad()
    def choose_option(
        self, state: np.ndarray, deterministic: bool = False
    ) -> tuple[int, float, float]:
        tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
        distribution = Categorical(logits=self.manager(tensor)[0])
        option = torch.argmax(distribution.logits) if deterministic else distribution.sample()
        return (
            int(option), float(distribution.log_prob(option)),
            float(self.manager_critic(tensor)[0]),
        )

    @torch.no_grad()
    def choose_action(
        self, decision: Decision, option: int, deterministic: bool = False
    ) -> tuple[int, float]:
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(decision.candidates, device=self.device).unsqueeze(0)
        option_tensor = torch.as_tensor([option], device=self.device)
        distribution = Categorical(
            logits=self.worker(local, option_tensor, candidates)[0]
        )
        choice = torch.argmax(distribution.logits) if deterministic else distribution.sample()
        return int(choice), float(distribution.log_prob(choice))

    def _worker_value(self, state: np.ndarray, option: int) -> float:
        with torch.no_grad():
            value = torch.as_tensor(
                self._option_state(state, option), device=self.device
            ).unsqueeze(0)
            return float(self.worker_critic(value)[0])

    def _manager_value(self, state: np.ndarray) -> float:
        with torch.no_grad():
            value = torch.as_tensor(state, device=self.device).unsqueeze(0)
            return float(self.manager_critic(value)[0])

    def collect(
        self, env: MengdeEnv, steps: int, seed: int
    ) -> tuple[list[WorkerTransition], list[ManagerTransition]]:
        observation, _ = env.reset(seed=seed)
        map_info = env.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        workers: list[WorkerTransition] = []
        managers: list[ManagerTransition] = []
        option: int | None = None
        remaining = 0
        manager_start: tuple[np.ndarray, int, float, float] | None = None
        segment_reward = 0.0
        segment_duration = 0

        for _ in range(steps):
            if option is None:
                option, manager_log_prob, manager_value = self.choose_option(observation)
                manager_start = (
                    observation.copy(), option, manager_log_prob, manager_value
                )
                remaining = self.option_horizon
                segment_reward = 0.0
                segment_duration = 0

            decision = current_decision(env, observation, width, height)
            worker_value = self._worker_value(observation, option)
            choice, worker_log_prob = self.choose_action(decision, option)
            next_observation, reward, terminated, truncated, _ = env.step(
                int(decision.actions[choice]["index"])
            )
            done = terminated or truncated
            workers.append(
                WorkerTransition(
                    state=observation.copy(), local=decision.local,
                    candidates=decision.candidates, choice=choice, option=option,
                    log_prob=worker_log_prob, value=worker_value,
                    reward=float(reward), done=done,
                )
            )
            segment_reward += (self.gamma ** segment_duration) * float(reward)
            segment_duration += 1
            remaining -= 1
            observation = next_observation

            if done or remaining == 0:
                assert manager_start is not None
                state, selected, log_prob, value = manager_start
                managers.append(
                    ManagerTransition(
                        state=state, option=selected, log_prob=log_prob, value=value,
                        reward=segment_reward, duration=segment_duration, done=done,
                    )
                )
                option = None
                manager_start = None
            if done:
                observation, _ = env.reset(seed=seed + len(workers))

        if manager_start is not None:
            state, selected, log_prob, value = manager_start
            managers.append(
                ManagerTransition(
                    state=state, option=selected, log_prob=log_prob, value=value,
                    reward=segment_reward, duration=segment_duration, done=False,
                )
            )

        self._manager_bootstrap = (
            0.0 if managers[-1].done else self._manager_value(observation)
        )
        if workers[-1].done:
            self._worker_bootstrap = 0.0
        else:
            bootstrap_option = option
            if bootstrap_option is None:
                bootstrap_option, _, _ = self.choose_option(observation, deterministic=True)
            self._worker_bootstrap = self._worker_value(observation, bootstrap_option)
        return workers, managers

    def _step_advantages(
        self, transitions: list[WorkerTransition]
    ) -> tuple[np.ndarray, np.ndarray]:
        rewards = np.asarray([item.reward for item in transitions], dtype=np.float32)
        values = np.asarray(
            [item.value for item in transitions] + [self._worker_bootstrap], dtype=np.float32
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

    def _option_advantages(
        self, transitions: list[ManagerTransition]
    ) -> tuple[np.ndarray, np.ndarray]:
        values = np.asarray(
            [item.value for item in transitions] + [self._manager_bootstrap], dtype=np.float32
        )
        advantages = np.zeros(len(transitions), dtype=np.float32)
        gae = 0.0
        for index in range(len(transitions) - 1, -1, -1):
            item = transitions[index]
            nonterminal = 1.0 - float(item.done)
            discount = self.gamma ** item.duration
            delta = item.reward + discount * values[index + 1] * nonterminal - values[index]
            gae = delta + discount * self.gae_lambda * nonterminal * gae
            advantages[index] = gae
        returns = advantages + values[:-1]
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        return advantages, returns

    def update(
        self,
        workers: list[WorkerTransition],
        managers: list[ManagerTransition],
        *,
        epochs: int = 4,
        batch_size: int = 128,
    ) -> dict[str, Any]:
        worker_advantages, worker_returns = self._step_advantages(workers)
        manager_advantages, manager_returns = self._option_advantages(managers)
        worker_losses: list[tuple[float, float, float]] = []
        manager_losses: list[tuple[float, float, float]] = []

        for _ in range(epochs):
            order = self.rng.permutation(len(workers))
            for start in range(0, len(order), batch_size):
                indices = order[start : start + batch_size]
                candidates, mask = pad_candidates(
                    [workers[int(index)].candidates for index in indices], self.device
                )
                local = torch.as_tensor(
                    np.stack([workers[int(index)].local for index in indices]), device=self.device
                )
                options = torch.as_tensor(
                    [workers[int(index)].option for index in indices], device=self.device
                )
                logits = self.worker(local, options, candidates).masked_fill(~mask, -1e9)
                distribution = Categorical(logits=logits)
                choices = torch.as_tensor(
                    [workers[int(index)].choice for index in indices], device=self.device
                )
                old_log_probs = torch.as_tensor(
                    [workers[int(index)].log_prob for index in indices], device=self.device
                )
                advantages = torch.as_tensor(worker_advantages[indices], device=self.device)
                ratio = torch.exp(distribution.log_prob(choices) - old_log_probs)
                policy_loss = -torch.min(
                    ratio * advantages,
                    torch.clamp(ratio, 1.0 - self.clip_range, 1.0 + self.clip_range) * advantages,
                ).mean()
                value_input = torch.as_tensor(
                    np.stack([
                        self._option_state(workers[int(index)].state, workers[int(index)].option)
                        for index in indices
                    ]), device=self.device,
                )
                returns = torch.as_tensor(worker_returns[indices], device=self.device)
                value_loss = torch.square(self.worker_critic(value_input) - returns).mean()
                entropy = distribution.entropy().mean()
                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy
                self.worker_optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(
                    [*self.worker.parameters(), *self.worker_critic.parameters()], 0.5
                )
                self.worker_optimizer.step()
                worker_losses.append((float(policy_loss), float(value_loss), float(entropy)))

            manager_order = self.rng.permutation(len(managers))
            manager_batch = max(8, batch_size // self.option_horizon)
            for start in range(0, len(manager_order), manager_batch):
                indices = manager_order[start : start + manager_batch]
                states = torch.as_tensor(
                    np.stack([managers[int(index)].state for index in indices]), device=self.device
                )
                options = torch.as_tensor(
                    [managers[int(index)].option for index in indices], device=self.device
                )
                old_log_probs = torch.as_tensor(
                    [managers[int(index)].log_prob for index in indices], device=self.device
                )
                distribution = Categorical(logits=self.manager(states))
                advantages = torch.as_tensor(manager_advantages[indices], device=self.device)
                ratio = torch.exp(distribution.log_prob(options) - old_log_probs)
                policy_loss = -torch.min(
                    ratio * advantages,
                    torch.clamp(ratio, 1.0 - self.clip_range, 1.0 + self.clip_range) * advantages,
                ).mean()
                returns = torch.as_tensor(manager_returns[indices], device=self.device)
                value_loss = torch.square(self.manager_critic(states) - returns).mean()
                entropy = distribution.entropy().mean()
                loss = (
                    policy_loss + self.value_coef * value_loss
                    - self.manager_entropy_coef * entropy
                )
                self.manager_optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(
                    [*self.manager.parameters(), *self.manager_critic.parameters()], 0.5
                )
                self.manager_optimizer.step()
                manager_losses.append((float(policy_loss), float(value_loss), float(entropy)))

        worker_mean = np.mean(worker_losses, axis=0)
        manager_mean = np.mean(manager_losses, axis=0)
        usage = np.bincount(
            [item.option for item in managers], minlength=self.num_options
        ).astype(np.float64)
        usage /= max(1.0, usage.sum())
        return {
            "worker_policy_loss": float(worker_mean[0]),
            "worker_value_loss": float(worker_mean[1]),
            "worker_entropy": float(worker_mean[2]),
            "manager_policy_loss": float(manager_mean[0]),
            "manager_value_loss": float(manager_mean[1]),
            "manager_entropy": float(manager_mean[2]),
            "manager_decisions": len(managers),
            "option_usage": usage.tolist(),
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
            workers, managers = self.collect(env, count, seed + completed)
            metrics = self.update(
                workers, managers, epochs=epochs, batch_size=batch_size
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
                "algorithm": "hierarchical-ppo",
                "manager": self.manager.state_dict(),
                "worker": self.worker.state_dict(),
                "manager_critic": self.manager_critic.state_dict(),
                "worker_critic": self.worker_critic.state_dict(),
                "num_options": self.num_options,
                "option_horizon": self.option_horizon,
                "state_features": self.state_features,
            },
            destination,
        )

    @property
    def parameter_count(self) -> int:
        return sum(
            parameter.numel()
            for module in (self.manager, self.worker, self.manager_critic, self.worker_critic)
            for parameter in module.parameters()
        )
