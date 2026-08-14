"""Collapse-resistant discrete CQL for candidate-action battle policies."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import torch
from torch import nn

from rl.mappo import ACTION_FEATURES, LOCAL_FEATURES, Decision
from rl.offline_dataset import OfflineDataset
from rl.offline_rl import CandidatePolicy, CandidateQ, _soft_update


class ConditionedCandidateQ(nn.Module):
    """Candidate Q conditioned on both the battle and the acting unit."""

    def __init__(self, state_features: int, hidden: int = 128) -> None:
        super().__init__()
        self.state_encoder = nn.Sequential(
            nn.Linear(state_features, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.local_encoder = nn.Sequential(
            nn.Linear(LOCAL_FEATURES, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.action_encoder = nn.Sequential(
            nn.Linear(ACTION_FEATURES, hidden), nn.ReLU(), nn.Linear(hidden, hidden)
        )
        self.head = nn.Sequential(
            nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1)
        )

    def forward(
        self, state: torch.Tensor, local: torch.Tensor, candidates: torch.Tensor
    ) -> torch.Tensor:
        context = self.state_encoder(state) + self.local_encoder(local)
        actions = self.action_encoder(candidates)
        return self.head(context.unsqueeze(1) + actions).squeeze(-1)


class BalancedOfflineBatcher:
    """Inverse-square-root action balancing keeps rare skills in each batch."""

    def __init__(self, dataset: OfflineDataset, device: torch.device, seed: int) -> None:
        self.dataset = dataset
        self.device = device
        self.rng = np.random.default_rng(seed)
        rows = np.arange(len(dataset))
        selected = dataset.candidates[rows, dataset.actions, :4]
        action_types = np.argmax(selected, axis=1)
        counts = np.bincount(action_types, minlength=4).astype(np.float64)
        weights = 1.0 / np.sqrt(np.maximum(1.0, counts[action_types]))
        self.probabilities = weights / weights.sum()
        self.action_type_counts = counts.astype(np.int64)

    def sample(self, size: int) -> dict[str, torch.Tensor]:
        count = min(size, len(self.dataset))
        indices = self.rng.choice(
            len(self.dataset), size=count, replace=True, p=self.probabilities
        )
        dataset = self.dataset
        return {
            "states": torch.as_tensor(dataset.states[indices], device=self.device),
            "locals": torch.as_tensor(dataset.locals[indices], device=self.device),
            "candidates": torch.as_tensor(dataset.candidates[indices], device=self.device),
            "masks": torch.as_tensor(dataset.masks[indices], device=self.device),
            "actions": torch.as_tensor(dataset.actions[indices], device=self.device),
            "rewards": torch.as_tensor(dataset.rewards[indices], device=self.device),
            "next_states": torch.as_tensor(dataset.next_states[indices], device=self.device),
            "next_locals": torch.as_tensor(dataset.next_locals[indices], device=self.device),
            "next_candidates": torch.as_tensor(
                dataset.next_candidates[indices], device=self.device
            ),
            "next_masks": torch.as_tensor(dataset.next_masks[indices], device=self.device),
            "dones": torch.as_tensor(dataset.dones[indices], device=self.device),
        }


class AdaptiveCQL:
    """Unit-conditioned CQL with entropy control and behavior support."""

    def __init__(
        self,
        state_features: int,
        *,
        conservative_weight: float = 1.0,
        behavior_weight: float = 0.5,
        target_entropy_ratio: float = 0.55,
        initial_temperature: float = 0.2,
        discount: float = 0.99,
        learning_rate: float = 3e-4,
        seed: int = 2026,
        device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        self.device = torch.device(device)
        self.q1 = ConditionedCandidateQ(state_features).to(self.device)
        self.q2 = ConditionedCandidateQ(state_features).to(self.device)
        self.target_q1 = copy.deepcopy(self.q1).requires_grad_(False)
        self.target_q2 = copy.deepcopy(self.q2).requires_grad_(False)
        self.policy = CandidatePolicy().to(self.device)
        self.q_optimizer = torch.optim.Adam(
            [*self.q1.parameters(), *self.q2.parameters()], learning_rate
        )
        self.policy_optimizer = torch.optim.Adam(
            self.policy.parameters(), learning_rate
        )
        self.log_temperature = torch.tensor(
            np.log(initial_temperature), dtype=torch.float32,
            device=self.device, requires_grad=True,
        )
        self.temperature_optimizer = torch.optim.Adam(
            [self.log_temperature], learning_rate
        )
        self.conservative_weight = conservative_weight
        self.behavior_weight = behavior_weight
        self.target_entropy_ratio = target_entropy_ratio
        self.discount = discount

    @property
    def temperature(self) -> torch.Tensor:
        return self.log_temperature.exp().clamp(0.01, 2.0)

    @staticmethod
    def _masked_policy(
        logits: torch.Tensor, masks: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        masked_logits = logits.masked_fill(~masks, -1e9)
        log_probability = torch.log_softmax(masked_logits, dim=-1)
        probability = torch.softmax(masked_logits, dim=-1)
        entropy = -(probability * log_probability).sum(dim=-1)
        return probability, log_probability, entropy

    def train(
        self, dataset: OfflineDataset, updates: int, *, batch_size: int = 256
    ) -> dict[str, float | list[int]]:
        batcher = BalancedOfflineBatcher(dataset, self.device, 2028)
        metrics: list[tuple[float, ...]] = []
        for _ in range(updates):
            batch = batcher.sample(batch_size)
            action = batch["actions"].unsqueeze(1)
            with torch.no_grad():
                next_logits = self.policy(
                    batch["next_locals"], batch["next_candidates"]
                )
                next_probability, next_log_probability, _ = self._masked_policy(
                    next_logits, batch["next_masks"]
                )
                next_q = torch.minimum(
                    self.target_q1(
                        batch["next_states"], batch["next_locals"],
                        batch["next_candidates"],
                    ),
                    self.target_q2(
                        batch["next_states"], batch["next_locals"],
                        batch["next_candidates"],
                    ),
                )
                next_value = (
                    next_probability
                    * (next_q - self.temperature.detach() * next_log_probability)
                ).sum(dim=1)
                next_value = torch.where(batch["dones"] > 0, 0.0, next_value)
                target = batch["rewards"] + self.discount * next_value

            all_q1 = self.q1(
                batch["states"], batch["locals"], batch["candidates"]
            )
            all_q2 = self.q2(
                batch["states"], batch["locals"], batch["candidates"]
            )
            data_q1 = all_q1.gather(1, action).squeeze(1)
            data_q2 = all_q2.gather(1, action).squeeze(1)
            bellman = (data_q1 - target).square().mean() + (
                data_q2 - target
            ).square().mean()
            legal_count = batch["masks"].sum(dim=1).clamp(min=1).float()
            conservative = (
                torch.logsumexp(
                    all_q1.masked_fill(~batch["masks"], -1e9), dim=1
                ) - legal_count.log() - data_q1
            ).mean() + (
                torch.logsumexp(
                    all_q2.masked_fill(~batch["masks"], -1e9), dim=1
                ) - legal_count.log() - data_q2
            ).mean()
            q_loss = bellman + self.conservative_weight * conservative
            self.q_optimizer.zero_grad()
            q_loss.backward()
            nn.utils.clip_grad_norm_([*self.q1.parameters(), *self.q2.parameters()], 1.0)
            self.q_optimizer.step()

            logits = self.policy(batch["locals"], batch["candidates"])
            probability, log_probability, entropy = self._masked_policy(
                logits, batch["masks"]
            )
            with torch.no_grad():
                policy_q = torch.minimum(
                    self.q1(
                        batch["states"], batch["locals"], batch["candidates"]
                    ),
                    self.q2(
                        batch["states"], batch["locals"], batch["candidates"]
                    ),
                )
            rl_loss = (
                probability
                * (self.temperature.detach() * log_probability - policy_q)
            ).sum(dim=1).mean()
            behavior_loss = -log_probability.gather(1, action).mean()
            policy_loss = rl_loss + self.behavior_weight * behavior_loss
            self.policy_optimizer.zero_grad()
            policy_loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.policy_optimizer.step()

            target_entropy = self.target_entropy_ratio * legal_count.log()
            temperature_loss = (
                self.log_temperature * (entropy.detach() - target_entropy)
            ).mean()
            self.temperature_optimizer.zero_grad()
            temperature_loss.backward()
            self.temperature_optimizer.step()

            _soft_update(self.target_q1, self.q1, 0.005)
            _soft_update(self.target_q2, self.q2, 0.005)
            normalized_entropy = (
                entropy / legal_count.log().clamp(min=1.0)
            ).mean()
            metrics.append((
                float(bellman), float(conservative), float(policy_loss),
                float(behavior_loss), float(normalized_entropy),
                float(self.temperature.detach()),
            ))
        mean = np.mean(metrics[-100:], axis=0)
        return {
            "bellman_loss": float(mean[0]),
            "conservative_penalty": float(mean[1]),
            "policy_loss": float(mean[2]),
            "behavior_loss": float(mean[3]),
            "normalized_entropy": float(mean[4]),
            "temperature": float(mean[5]),
            "updates": float(updates),
            "dataset_action_type_counts": batcher.action_type_counts.tolist(),
        }

    @torch.no_grad()
    def probabilities(self, state: np.ndarray, decision: Decision) -> np.ndarray:
        del state
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(
            decision.candidates, device=self.device
        ).unsqueeze(0)
        return torch.softmax(self.policy(local, candidates)[0], dim=-1).cpu().numpy()

    @torch.no_grad()
    def choose(
        self, state: np.ndarray, decision: Decision, *, deterministic: bool = True,
        rng: np.random.Generator | None = None,
    ) -> int:
        probabilities = self.probabilities(state, decision)
        if deterministic:
            return int(np.argmax(probabilities))
        generator = rng or np.random.default_rng()
        return int(generator.choice(len(probabilities), p=probabilities))

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "algorithm": "adaptive-cql",
                "q1": self.q1.state_dict(),
                "q2": self.q2.state_dict(),
                "policy": self.policy.state_dict(),
                "log_temperature": self.log_temperature.detach().cpu(),
                "conservative_weight": self.conservative_weight,
                "behavior_weight": self.behavior_weight,
                "target_entropy_ratio": self.target_entropy_ratio,
            },
            destination,
        )

    @property
    def parameter_count(self) -> int:
        return sum(
            parameter.numel()
            for module in (self.q1, self.q2, self.policy)
            for parameter in module.parameters()
        )
class SupportedCQL:
    """Legacy CQL values plus a balanced, entropy-regularized support prior."""

    def __init__(
        self, state_features: int, *, support_weight: float = 0.05,
        entropy_coef: float = 0.02, learning_rate: float = 3e-4,
        seed: int = 2026, device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        self.device = torch.device(device)
        self.q1 = CandidateQ(state_features).to(self.device)
        self.q2 = CandidateQ(state_features).to(self.device)
        self.policy = CandidatePolicy().to(self.device)
        self.policy_optimizer = torch.optim.Adam(
            self.policy.parameters(), learning_rate
        )
        self.support_weight = support_weight
        self.entropy_coef = entropy_coef

    def load_legacy_values(self, path: str | Path) -> None:
        payload = torch.load(Path(path), map_location=self.device)
        self.q1.load_state_dict(payload["q1"])
        self.q2.load_state_dict(payload["q2"])
        self.q1.eval(); self.q2.eval()
        for parameter in (*self.q1.parameters(), *self.q2.parameters()):
            parameter.requires_grad_(False)

    def train_support(
        self, dataset: OfflineDataset, updates: int, *, batch_size: int = 256
    ) -> dict[str, float | list[int]]:
        batcher = BalancedOfflineBatcher(dataset, self.device, 2029)
        metrics: list[tuple[float, float]] = []
        for _ in range(updates):
            batch = batcher.sample(batch_size)
            logits = self.policy(batch["locals"], batch["candidates"])
            _, log_probability, entropy = AdaptiveCQL._masked_policy(
                logits, batch["masks"]
            )
            behavior_loss = -log_probability.gather(
                1, batch["actions"].unsqueeze(1)
            ).mean()
            loss = behavior_loss - self.entropy_coef * entropy.mean()
            self.policy_optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.policy_optimizer.step()
            legal_count = batch["masks"].sum(dim=1).clamp(min=1).float()
            normalized_entropy = (
                entropy / legal_count.log().clamp(min=1.0)
            ).mean()
            metrics.append((float(behavior_loss), float(normalized_entropy)))
        mean = np.mean(metrics[-100:], axis=0)
        self.policy.eval()
        return {
            "behavior_loss": float(mean[0]),
            "normalized_entropy": float(mean[1]),
            "updates": float(updates),
            "support_weight": self.support_weight,
            "entropy_coef": self.entropy_coef,
            "dataset_action_type_counts": batcher.action_type_counts.tolist(),
        }

    @torch.no_grad()
    def probabilities(self, state: np.ndarray, decision: Decision) -> np.ndarray:
        state_tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(
            decision.candidates, device=self.device
        ).unsqueeze(0)
        q_values = torch.minimum(
            self.q1(state_tensor, candidates), self.q2(state_tensor, candidates)
        )[0]
        q_std = q_values.std(unbiased=False).clamp(min=0.25)
        normalized_q = (q_values - q_values.mean()) / q_std
        support = torch.log_softmax(self.policy(local, candidates)[0], dim=-1)
        scores = normalized_q + self.support_weight * support
        return torch.softmax(scores, dim=-1).cpu().numpy()

    @torch.no_grad()
    def choose(
        self, state: np.ndarray, decision: Decision, *, deterministic: bool = True,
        rng: np.random.Generator | None = None,
    ) -> int:
        probabilities = self.probabilities(state, decision)
        if deterministic:
            return int(np.argmax(probabilities))
        generator = rng or np.random.default_rng()
        return int(generator.choice(len(probabilities), p=probabilities))

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "algorithm": "supported-cql",
            "q1": self.q1.state_dict(), "q2": self.q2.state_dict(),
            "policy": self.policy.state_dict(),
            "support_weight": self.support_weight,
            "entropy_coef": self.entropy_coef,
        }, destination)

    @property
    def parameter_count(self) -> int:
        return sum(
            parameter.numel() for module in (self.q1, self.q2, self.policy)
            for parameter in module.parameters()
        )
class UniformOfflineBatcher(BalancedOfflineBatcher):
    """Uniform replay used when CQL statistics must match the behavior data."""

    def __init__(self, dataset: OfflineDataset, device: torch.device, seed: int) -> None:
        super().__init__(dataset, device, seed)
        self.probabilities = np.full(len(dataset), 1.0 / len(dataset))


class CriticAdaptiveCQL:
    """CQL-Lagrange focused on critic extrapolation rather than policy entropy."""

    def __init__(
        self, state_features: int, *, action_features: int = ACTION_FEATURES,
        initial_alpha: float = 1.0, min_alpha: float = 0.05,
        max_alpha: float = 5.0, target_conservative_gap: float | None = None,
        behavior_weight: float = 0.05, normalize_rewards: bool = False,
        discount: float = 0.99, learning_rate: float = 3e-4,
        alpha_learning_rate: float = 1e-3,
        seed: int = 2026, device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        self.device = torch.device(device)
        self.action_features = int(action_features)
        self.q1 = CandidateQ(state_features, action_features=self.action_features).to(self.device)
        self.q2 = CandidateQ(state_features, action_features=self.action_features).to(self.device)
        self.target_q1 = copy.deepcopy(self.q1).requires_grad_(False)
        self.target_q2 = copy.deepcopy(self.q2).requires_grad_(False)
        self.policy = CandidatePolicy(
            action_features=self.action_features
        ).to(self.device)
        self.q_optimizer = torch.optim.Adam(
            [*self.q1.parameters(), *self.q2.parameters()], learning_rate
        )
        self.policy_optimizer = torch.optim.Adam(
            self.policy.parameters(), learning_rate
        )
        self.log_alpha = torch.tensor(
            np.log(initial_alpha), dtype=torch.float32, device=self.device,
            requires_grad=True,
        )
        self.alpha_optimizer = torch.optim.Adam([self.log_alpha], alpha_learning_rate)
        self.min_log_alpha = float(np.log(min_alpha))
        self.max_log_alpha = float(np.log(max_alpha))
        self.target_conservative_gap = target_conservative_gap
        self.behavior_weight = behavior_weight
        self.normalize_rewards = False
        self.discount = discount
        self.reward_low = 0.0
        self.reward_high = 0.0
        self.reward_scale = 1.0

    def load_legacy_values(self, path: str | Path) -> None:
        if self.action_features != ACTION_FEATURES:
            raise ValueError("legacy Q weights require the 14-feature schema")
        payload = torch.load(Path(path), map_location=self.device)
        self.q1.load_state_dict(payload["q1"])
        self.q2.load_state_dict(payload["q2"])
        self.target_q1.load_state_dict(payload["q1"])
        self.target_q2.load_state_dict(payload["q2"])
    @property
    def alpha(self) -> torch.Tensor:
        return self.log_alpha.exp().clamp(
            float(np.exp(self.min_log_alpha)), float(np.exp(self.max_log_alpha))
        )

    @staticmethod
    def _ood_mean(
        values: torch.Tensor, masks: torch.Tensor, actions: torch.Tensor
    ) -> torch.Tensor:
        ood_mask = masks.clone()
        ood_mask.scatter_(1, actions.unsqueeze(1), False)
        counts = ood_mask.sum(dim=1)
        total = values.masked_fill(~ood_mask, 0.0).sum(dim=1)
        data = values.gather(1, actions.unsqueeze(1)).squeeze(1)
        return torch.where(counts > 0, total / counts.clamp(min=1), data)

    @staticmethod
    def _conservative_penalty(
        values: torch.Tensor, masks: torch.Tensor, data: torch.Tensor
    ) -> torch.Tensor:
        legal_values = values.masked_fill(~masks, -1e9)
        return torch.logsumexp(legal_values, dim=1) - data

    def train(
        self, dataset: OfflineDataset, updates: int, *, batch_size: int = 256
    ) -> dict[str, float | list[int]]:
        feature_count = int(dataset.candidates.shape[2])
        if feature_count != self.action_features:
            raise ValueError(
                f"CQL expects {self.action_features} action features, "
                f"dataset has {feature_count}"
            )
        batcher = BalancedOfflineBatcher(dataset, self.device, 2030)
        self.reward_low = float(np.min(dataset.rewards))
        self.reward_high = float(np.max(dataset.rewards))
        self.reward_scale = 1.0
        if self.target_conservative_gap is None:
            legal_counts = dataset.masks.sum(axis=1).clip(min=1)
            self.target_conservative_gap = max(
                0.5, float(np.log(legal_counts).mean() - 0.5)
            )
        metrics: list[tuple[float, ...]] = []
        for _ in range(updates):
            batch = batcher.sample(batch_size)
            actions = batch["actions"]
            action_column = actions.unsqueeze(1)
            with torch.no_grad():
                next_q = torch.minimum(
                    self.target_q1(batch["next_states"], batch["next_candidates"]),
                    self.target_q2(batch["next_states"], batch["next_candidates"]),
                ).masked_fill(~batch["next_masks"], -1e9).max(dim=1).values
                next_q = torch.where(batch["dones"] > 0, 0.0, next_q)
                target = batch["rewards"] + self.discount * next_q

            all_q1 = self.q1(batch["states"], batch["candidates"])
            all_q2 = self.q2(batch["states"], batch["candidates"])
            data_q1 = all_q1.gather(1, action_column).squeeze(1)
            data_q2 = all_q2.gather(1, action_column).squeeze(1)
            penalty1 = self._conservative_penalty(
                all_q1, batch["masks"], data_q1
            )
            penalty2 = self._conservative_penalty(
                all_q2, batch["masks"], data_q2
            )
            conservative = 0.5 * (penalty1.mean() + penalty2.mean())
            bellman = (data_q1 - target).square().mean() + (
                data_q2 - target
            ).square().mean()
            q_loss = bellman + self.alpha.detach() * (
                penalty1.mean() + penalty2.mean()
            )
            self.q_optimizer.zero_grad()
            q_loss.backward()
            nn.utils.clip_grad_norm_([*self.q1.parameters(), *self.q2.parameters()], 1.0)
            self.q_optimizer.step()

            alpha_loss = -self.alpha * (
                conservative.detach() - self.target_conservative_gap
            )
            self.alpha_optimizer.zero_grad()
            alpha_loss.backward()
            self.alpha_optimizer.step()
            with torch.no_grad():
                self.log_alpha.clamp_(self.min_log_alpha, self.max_log_alpha)

            logits = self.policy(batch["locals"], batch["candidates"])
            probability, log_probability, entropy = AdaptiveCQL._masked_policy(
                logits, batch["masks"]
            )
            with torch.no_grad():
                actor_q = torch.minimum(
                    self.q1(batch["states"], batch["candidates"]),
                    self.q2(batch["states"], batch["candidates"]),
                )
            max_q_loss = -(probability * actor_q).sum(dim=1).mean()
            behavior_loss = -log_probability.gather(1, action_column).mean()
            policy_loss = max_q_loss + self.behavior_weight * behavior_loss
            self.policy_optimizer.zero_grad()
            policy_loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.policy_optimizer.step()

            _soft_update(self.target_q1, self.q1, 0.005)
            _soft_update(self.target_q2, self.q2, 0.005)
            ood_q1 = self._ood_mean(all_q1, batch["masks"], actions)
            ood_q2 = self._ood_mean(all_q2, batch["masks"], actions)
            q_data_mean = 0.5 * (data_q1.mean() + data_q2.mean())
            q_ood_mean = 0.5 * (ood_q1.mean() + ood_q2.mean())
            ood_gap = q_ood_mean - q_data_mean
            legal_count = batch["masks"].sum(dim=1).clamp(min=1).float()
            normalized_entropy = (
                entropy / legal_count.log().clamp(min=1.0)
            ).mean()
            q_spread = 0.5 * (
                data_q1.std(unbiased=False) + data_q2.std(unbiased=False)
            )
            metrics.append((
                float(bellman), float(conservative), float(q_data_mean),
                float(q_ood_mean), float(ood_gap), float(self.alpha.detach()),
                float(policy_loss),
                float(behavior_loss), float(normalized_entropy), float(q_spread),
            ))
        mean = np.mean(metrics[-100:], axis=0)
        return {
            "bellman_loss": float(mean[0]),
            "conservative_penalty": float(mean[1]),
            "q_data_mean": float(mean[2]),
            "q_ood_mean": float(mean[3]),
            "q_ood_minus_data": float(mean[4]),
            "alpha": float(mean[5]),
            "policy_loss": float(mean[6]),
            "behavior_loss": float(mean[7]),
            "diagnostic_normalized_entropy": float(mean[8]),
            "q_data_std": float(mean[9]),
            "reward_min": self.reward_low,
            "reward_max": self.reward_high,
            "reward_scale": self.reward_scale,
            "reward_mode": "raw",
            "target_conservative_gap": self.target_conservative_gap,
            "action_features": self.action_features,
            "behavior_weight": self.behavior_weight,
            "updates": float(updates),
            "dataset_action_type_counts": batcher.action_type_counts.tolist(),
        }

    @torch.no_grad()
    def probabilities(self, state: np.ndarray, decision: Decision) -> np.ndarray:
        if int(decision.candidates.shape[1]) != self.action_features:
            raise ValueError("decision action feature schema does not match CQL")
        state_tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(
            decision.candidates, device=self.device
        ).unsqueeze(0)
        values = torch.minimum(
            self.q1(state_tensor, candidates), self.q2(state_tensor, candidates)
        )[0]
        return torch.softmax(values - values.max(), dim=-1).cpu().numpy()

    @torch.no_grad()
    def choose(self, state: np.ndarray, decision: Decision) -> int:
        return int(np.argmax(self.probabilities(state, decision)))

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "algorithm": "logsumexp-adaptive-cql",
            "q1": self.q1.state_dict(), "q2": self.q2.state_dict(),
            "policy": self.policy.state_dict(),
            "log_alpha": self.log_alpha.detach().cpu(),
            "reward_mode": "raw",
            "reward_range": (self.reward_low, self.reward_high),
            "reward_scale": self.reward_scale,
            "target_conservative_gap": self.target_conservative_gap,
            "action_features": self.action_features,
            "behavior_weight": self.behavior_weight,
            "normalize_rewards": self.normalize_rewards,
        }, destination)

    @property
    def parameter_count(self) -> int:
        return sum(
            parameter.numel() for module in (self.q1, self.q2, self.policy)
            for parameter in module.parameters()
        )