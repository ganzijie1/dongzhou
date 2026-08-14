"""Candidate-action IQL and discrete CQL for Mengde offline datasets."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from rl.mappo import ACTION_FEATURES, LOCAL_FEATURES, Decision
from rl.offline_dataset import OfflineDataset


class CandidateQ(nn.Module):
    def __init__(
        self, state_features: int, hidden: int = 128,
        action_features: int = ACTION_FEATURES,
    ) -> None:
        super().__init__()
        self.state_encoder = nn.Sequential(
            nn.Linear(state_features, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.action_encoder = nn.Sequential(
            nn.Linear(action_features, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.head = nn.Sequential(
            nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1)
        )

    def forward(self, state: torch.Tensor, candidates: torch.Tensor) -> torch.Tensor:
        context = self.state_encoder(state).unsqueeze(1)
        actions = self.action_encoder(candidates)
        return self.head(context + actions).squeeze(-1)


class CandidatePolicy(nn.Module):
    def __init__(
        self, hidden: int = 128, action_features: int = ACTION_FEATURES
    ) -> None:
        super().__init__()
        self.local_encoder = nn.Sequential(
            nn.Linear(LOCAL_FEATURES, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.action_encoder = nn.Sequential(
            nn.Linear(action_features, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.head = nn.Sequential(
            nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1)
        )

    def forward(self, local: torch.Tensor, candidates: torch.Tensor) -> torch.Tensor:
        context = self.local_encoder(local).unsqueeze(1)
        actions = self.action_encoder(candidates)
        return self.head(context + actions).squeeze(-1)


class StateValue(nn.Module):
    def __init__(self, state_features: int, hidden: int = 256) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_features, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state).squeeze(-1)


class OfflineBatcher:
    def __init__(self, dataset: OfflineDataset, device: torch.device, seed: int) -> None:
        self.dataset = dataset
        self.device = device
        self.rng = np.random.default_rng(seed)

    def sample(self, size: int) -> dict[str, torch.Tensor]:
        indices = self.rng.integers(len(self.dataset), size=min(size, len(self.dataset)))
        return {
            "states": torch.as_tensor(self.dataset.states[indices], device=self.device),
            "locals": torch.as_tensor(self.dataset.locals[indices], device=self.device),
            "candidates": torch.as_tensor(self.dataset.candidates[indices], device=self.device),
            "masks": torch.as_tensor(self.dataset.masks[indices], device=self.device),
            "actions": torch.as_tensor(self.dataset.actions[indices], device=self.device),
            "rewards": torch.as_tensor(self.dataset.rewards[indices], device=self.device),
            "next_states": torch.as_tensor(self.dataset.next_states[indices], device=self.device),
            "next_candidates": torch.as_tensor(
                self.dataset.next_candidates[indices], device=self.device
            ),
            "next_masks": torch.as_tensor(self.dataset.next_masks[indices], device=self.device),
            "dones": torch.as_tensor(self.dataset.dones[indices], device=self.device),
        }


def _soft_update(target: nn.Module, source: nn.Module, tau: float) -> None:
    with torch.no_grad():
        for target_parameter, source_parameter in zip(
            target.parameters(), source.parameters()
        ):
            target_parameter.lerp_(source_parameter, tau)


class IQL:
    def __init__(
        self, state_features: int, *, expectile: float = 0.7,
        temperature: float = 3.0, discount: float = 0.99,
        learning_rate: float = 3e-4, seed: int = 2026, device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        self.device = torch.device(device)
        self.q1 = CandidateQ(state_features).to(self.device)
        self.q2 = CandidateQ(state_features).to(self.device)
        self.target_q1 = copy.deepcopy(self.q1).requires_grad_(False)
        self.target_q2 = copy.deepcopy(self.q2).requires_grad_(False)
        self.value = StateValue(state_features).to(self.device)
        self.policy = CandidatePolicy().to(self.device)
        self.q_optimizer = torch.optim.Adam(
            [*self.q1.parameters(), *self.q2.parameters()], learning_rate
        )
        self.value_optimizer = torch.optim.Adam(self.value.parameters(), learning_rate)
        self.policy_optimizer = torch.optim.Adam(self.policy.parameters(), learning_rate)
        self.expectile = expectile
        self.temperature = temperature
        self.discount = discount

    def train(
        self, dataset: OfflineDataset, updates: int, *, batch_size: int = 256
    ) -> dict[str, float]:
        batcher = OfflineBatcher(dataset, self.device, 2026)
        metrics = []
        for _ in range(updates):
            batch = batcher.sample(batch_size)
            action = batch["actions"].unsqueeze(1)
            with torch.no_grad():
                target_q = torch.minimum(
                    self.target_q1(batch["states"], batch["candidates"]),
                    self.target_q2(batch["states"], batch["candidates"]),
                ).gather(1, action).squeeze(1)
            value = self.value(batch["states"])
            difference = target_q - value
            weight = torch.where(
                difference > 0, self.expectile, 1.0 - self.expectile
            )
            value_loss = (weight * difference.square()).mean()
            self.value_optimizer.zero_grad()
            value_loss.backward()
            self.value_optimizer.step()

            with torch.no_grad():
                target = batch["rewards"] + self.discount * (
                    1.0 - batch["dones"]
                ) * self.value(batch["next_states"])
            q1 = self.q1(batch["states"], batch["candidates"]).gather(
                1, action
            ).squeeze(1)
            q2 = self.q2(batch["states"], batch["candidates"]).gather(
                1, action
            ).squeeze(1)
            q_loss = (q1 - target).square().mean() + (q2 - target).square().mean()
            self.q_optimizer.zero_grad()
            q_loss.backward()
            self.q_optimizer.step()

            with torch.no_grad():
                advantage = target_q - self.value(batch["states"])
                advantage_weight = torch.exp(
                    self.temperature * advantage
                ).clamp(max=100.0)
            logits = self.policy(batch["locals"], batch["candidates"])
            logits = logits.masked_fill(~batch["masks"], -1e9)
            log_prob = torch.log_softmax(logits, dim=-1).gather(
                1, action
            ).squeeze(1)
            policy_loss = -(advantage_weight * log_prob).mean()
            self.policy_optimizer.zero_grad()
            policy_loss.backward()
            self.policy_optimizer.step()
            _soft_update(self.target_q1, self.q1, 0.005)
            _soft_update(self.target_q2, self.q2, 0.005)
            metrics.append((float(q_loss), float(value_loss), float(policy_loss)))
        mean = np.mean(metrics[-100:], axis=0)
        return {"q_loss": float(mean[0]), "value_loss": float(mean[1]),
                "policy_loss": float(mean[2]), "updates": float(updates)}

    @torch.no_grad()
    def choose(self, state: np.ndarray, decision: Decision) -> int:
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(
            decision.candidates, device=self.device
        ).unsqueeze(0)
        return int(torch.argmax(self.policy(local, candidates)[0]))

    def save(self, path: str | Path) -> None:
        destination = Path(path); destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"algorithm": "iql", "q1": self.q1.state_dict(),
                    "q2": self.q2.state_dict(), "value": self.value.state_dict(),
                    "policy": self.policy.state_dict()}, destination)

    @property
    def parameter_count(self) -> int:
        return sum(p.numel() for module in (self.q1, self.q2, self.value, self.policy)
                   for p in module.parameters())


class CQL:
    def __init__(
        self, state_features: int, *, conservative_weight: float = 1.0,
        action_features: int = ACTION_FEATURES,
        discount: float = 0.99, learning_rate: float = 3e-4,
        seed: int = 2026, device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        self.device = torch.device(device)
        self.action_features = int(action_features)
        self.q1 = CandidateQ(state_features, action_features=self.action_features).to(self.device)
        self.q2 = CandidateQ(state_features, action_features=self.action_features).to(self.device)
        self.target_q1 = copy.deepcopy(self.q1).requires_grad_(False)
        self.target_q2 = copy.deepcopy(self.q2).requires_grad_(False)
        self.optimizer = torch.optim.Adam(
            [*self.q1.parameters(), *self.q2.parameters()], learning_rate
        )
        self.conservative_weight = conservative_weight
        self.discount = discount

    def train(
        self, dataset: OfflineDataset, updates: int, *, batch_size: int = 256
    ) -> dict[str, float]:
        if int(dataset.candidates.shape[2]) != self.action_features:
            raise ValueError("dataset action feature schema does not match CQL")
        batcher = OfflineBatcher(dataset, self.device, 2027)
        metrics = []
        for _ in range(updates):
            batch = batcher.sample(batch_size)
            action = batch["actions"].unsqueeze(1)
            with torch.no_grad():
                next_q = torch.minimum(
                    self.target_q1(batch["next_states"], batch["next_candidates"]),
                    self.target_q2(batch["next_states"], batch["next_candidates"]),
                ).masked_fill(~batch["next_masks"], -1e9).max(dim=1).values
                next_q = torch.where(batch["dones"] > 0, 0.0, next_q)
                target = batch["rewards"] + self.discount * next_q
            all_q1 = self.q1(batch["states"], batch["candidates"])
            all_q2 = self.q2(batch["states"], batch["candidates"])
            data_q1 = all_q1.gather(1, action).squeeze(1)
            data_q2 = all_q2.gather(1, action).squeeze(1)
            bellman = (data_q1 - target).square().mean() + (
                data_q2 - target
            ).square().mean()
            conservative = (
                torch.logsumexp(all_q1.masked_fill(~batch["masks"], -1e9), dim=1)
                - data_q1
            ).mean() + (
                torch.logsumexp(all_q2.masked_fill(~batch["masks"], -1e9), dim=1)
                - data_q2
            ).mean()
            loss = bellman + self.conservative_weight * conservative
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_([*self.q1.parameters(), *self.q2.parameters()], 1.0)
            self.optimizer.step()
            _soft_update(self.target_q1, self.q1, 0.005)
            _soft_update(self.target_q2, self.q2, 0.005)
            metrics.append((float(bellman), float(conservative)))
        mean = np.mean(metrics[-100:], axis=0)
        return {"bellman_loss": float(mean[0]),
                "conservative_penalty": float(mean[1]), "updates": float(updates)}

    @torch.no_grad()
    def choose(self, state: np.ndarray, decision: Decision) -> int:
        state_tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(
            decision.candidates, device=self.device
        ).unsqueeze(0)
        values = torch.minimum(
            self.q1(state_tensor, candidates), self.q2(state_tensor, candidates)
        )
        return int(torch.argmax(values[0]))

    def save(self, path: str | Path) -> None:
        destination = Path(path); destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"algorithm": "cql", "q1": self.q1.state_dict(),
                    "q2": self.q2.state_dict(), "action_features": self.action_features}, destination)

    @property
    def parameter_count(self) -> int:
        return sum(p.numel() for module in (self.q1, self.q2) for p in module.parameters())
