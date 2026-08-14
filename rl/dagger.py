"""Candidate-action behavior cloning and DAgger with a HAPPO expert."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.distributions import Categorical

from rl.happo import HAPPO, decision_role
from rl.mappo import Decision, current_decision, pad_candidates
from rl.mengde_env import MengdeEnv
from rl.offline_rl import CandidatePolicy


@dataclass
class ImitationSample:
    local: np.ndarray
    candidates: np.ndarray
    action: int


def load_happo_expert(state_features: int) -> HAPPO:
    expert = HAPPO(state_features, seed=2026)
    payload = torch.load(
        Path("rl/models/ppo_mappo_happo_comparison/happo.pt"), map_location="cpu"
    )
    expert.actors.load_state_dict(payload["actors"])
    expert.critic.load_state_dict(payload["critic"])
    return expert


def expert_choice(expert: HAPPO, env: MengdeEnv, decision: Decision) -> int:
    role = decision_role(env, decision)
    choice, _ = expert.choose(decision, role, deterministic=True)
    return choice


class BehaviorCloning:
    def __init__(
        self, *, learning_rate: float = 3e-4, seed: int = 2026,
        device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        self.device = torch.device(device)
        self.policy = CandidatePolicy().to(self.device)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), learning_rate)
        self.rng = np.random.default_rng(seed)

    def train(
        self, samples: list[ImitationSample], updates: int, *, batch_size: int = 128
    ) -> dict[str, float]:
        if not samples:
            raise ValueError("behavior cloning requires expert samples")
        metrics = []
        for _ in range(updates):
            indices = self.rng.integers(len(samples), size=min(batch_size, len(samples)))
            selected = [samples[int(index)] for index in indices]
            candidates, mask = pad_candidates(
                [sample.candidates for sample in selected], self.device
            )
            local = torch.as_tensor(
                np.stack([sample.local for sample in selected]), device=self.device
            )
            actions = torch.as_tensor(
                [sample.action for sample in selected], device=self.device
            )
            logits = self.policy(local, candidates).masked_fill(~mask, -1e9)
            distribution = Categorical(logits=logits)
            loss = -distribution.log_prob(actions).mean()
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
            self.optimizer.step()
            accuracy = (torch.argmax(logits, dim=1) == actions).float().mean()
            metrics.append((float(loss), float(accuracy), float(distribution.entropy().mean())))
        mean = np.mean(metrics[-100:], axis=0)
        return {
            "cross_entropy": float(mean[0]), "expert_accuracy": float(mean[1]),
            "entropy": float(mean[2]), "updates": float(updates),
            "samples": float(len(samples)),
        }

    @torch.no_grad()
    def choose(self, decision: Decision) -> int:
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(
            decision.candidates, device=self.device
        ).unsqueeze(0)
        return int(torch.argmax(self.policy(local, candidates)[0]))

    def save(self, path: str | Path, algorithm: str) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {"algorithm": algorithm, "policy": self.policy.state_dict()}, destination
        )

    @property
    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.policy.parameters())


def collect_expert_data(
    env: MengdeEnv, expert: HAPPO, episodes: int, *, seed: int
) -> tuple[list[ImitationSample], dict[str, float]]:
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    samples: list[ImitationSample] = []
    summaries = []
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total, actions = 0.0, 0
        while True:
            decision = current_decision(env, observation, width, height)
            choice = expert_choice(expert, env, decision)
            samples.append(
                ImitationSample(
                    local=decision.local.copy(),
                    candidates=decision.candidates.copy(), action=choice,
                )
            )
            observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[choice]["index"])
            )
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        summaries.append((total, actions, int(info["status"]) == 3))
    return samples, {
        "episodes": float(episodes), "samples": float(len(samples)),
        "mean_return": float(np.mean([item[0] for item in summaries])),
        "mean_actions": float(np.mean([item[1] for item in summaries])),
        "win_rate": float(np.mean([item[2] for item in summaries])),
    }


def dagger_aggregate(
    env: MengdeEnv,
    expert: HAPPO,
    learner: BehaviorCloning,
    episodes: int,
    *,
    beta: float,
    seed: int,
) -> tuple[list[ImitationSample], dict[str, float]]:
    map_info = env.map_info()
    width, height = int(map_info["width"]), int(map_info["height"])
    rng = np.random.default_rng(seed)
    samples: list[ImitationSample] = []
    disagreements, expert_executions, actions = 0, 0, 0
    returns, victories = [], []
    for episode in range(episodes):
        observation, info = env.reset(seed=seed + episode)
        total = 0.0
        while True:
            decision = current_decision(env, observation, width, height)
            label = expert_choice(expert, env, decision)
            learner_action = learner.choose(decision)
            disagreements += int(label != learner_action)
            use_expert = rng.random() < beta
            executed = label if use_expert else learner_action
            expert_executions += int(use_expert)
            samples.append(
                ImitationSample(
                    local=decision.local.copy(),
                    candidates=decision.candidates.copy(), action=label,
                )
            )
            observation, reward, terminated, truncated, info = env.step(
                int(decision.actions[executed]["index"])
            )
            total += float(reward)
            actions += 1
            if terminated or truncated:
                break
        returns.append(total)
        victories.append(int(info["status"]) == 3)
    return samples, {
        "beta": beta, "new_samples": float(len(samples)),
        "disagreement_rate": disagreements / max(1, actions),
        "expert_execution_rate": expert_executions / max(1, actions),
        "rollout_mean_return": float(np.mean(returns)),
        "rollout_win_rate": float(np.mean(victories)),
    }


def save_samples(samples: list[ImitationSample], path: str | Path) -> None:
    maximum = max(len(sample.candidates) for sample in samples)
    candidates = np.zeros((len(samples), maximum, samples[0].candidates.shape[1]), dtype=np.float32)
    masks = np.zeros((len(samples), maximum), dtype=np.bool_)
    for row, sample in enumerate(samples):
        candidates[row, :len(sample.candidates)] = sample.candidates
        masks[row, :len(sample.candidates)] = True
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        destination, locals=np.stack([sample.local for sample in samples]),
        candidates=candidates, masks=masks,
        actions=np.asarray([sample.action for sample in samples], dtype=np.int64),
    )
