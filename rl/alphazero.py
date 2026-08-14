"""AlphaZero-style policy/value learning with PUCT search for Mengde.

The native environment is deterministic but has no cheap in-memory clone. Each
simulation therefore resets an isolated simulator and replays the episode's
action history before traversing the search tree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from rl.mappo import ACTION_FEATURES, LOCAL_FEATURES, Decision, current_decision, pad_candidates
from rl.mengde_env import MengdeEnv


class PolicyValueNetwork(nn.Module):
    def __init__(self, state_features: int, hidden: int = 128) -> None:
        super().__init__()
        self.policy = nn.Sequential(
            nn.Linear(LOCAL_FEATURES + ACTION_FEATURES, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1),
        )
        self.value = nn.Sequential(
            nn.Linear(state_features, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1), nn.Tanh(),
        )

    def forward(
        self, state: torch.Tensor, local: torch.Tensor, candidates: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        expanded = local.unsqueeze(1).expand(-1, candidates.shape[1], -1)
        logits = self.policy(torch.cat((expanded, candidates), dim=-1)).squeeze(-1)
        return logits, self.value(state).squeeze(-1)


@dataclass
class Edge:
    action: int
    prior: float
    visits: int = 0
    value_sum: float = 0.0
    child: "Node | None" = None

    @property
    def value(self) -> float:
        return self.value_sum / self.visits if self.visits else 0.0


@dataclass
class Node:
    edges: list[Edge] = field(default_factory=list)

    @property
    def expanded(self) -> bool:
        return bool(self.edges)


@dataclass
class SearchResult:
    node: Node
    decision: Decision
    policy: np.ndarray
    action: int
    choice: int
    simulations: int
    replay_steps: int


@dataclass
class TrainingSample:
    state: np.ndarray
    local: np.ndarray
    candidates: np.ndarray
    policy: np.ndarray
    value: float = 0.0


class AlphaZero:
    def __init__(
        self,
        state_features: int,
        *,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        c_puct: float = 1.5,
        dirichlet_alpha: float = 0.3,
        dirichlet_fraction: float = 0.25,
        value_scale: float = 25.0,
        seed: int = 42,
        device: str = "cpu",
    ) -> None:
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.device = torch.device(device)
        self.network = PolicyValueNetwork(state_features).to(self.device)
        self.optimizer = torch.optim.Adam(self.network.parameters(), learning_rate)
        self.gamma = gamma
        self.c_puct = c_puct
        self.dirichlet_alpha = dirichlet_alpha
        self.dirichlet_fraction = dirichlet_fraction
        self.value_scale = value_scale
        self.rng = np.random.default_rng(seed)

    @torch.no_grad()
    def evaluate(self, state: np.ndarray, decision: Decision) -> tuple[np.ndarray, float]:
        state_tensor = torch.as_tensor(state, device=self.device).unsqueeze(0)
        local = torch.as_tensor(decision.local, device=self.device).unsqueeze(0)
        candidates = torch.as_tensor(decision.candidates, device=self.device).unsqueeze(0)
        logits, value = self.network(state_tensor, local, candidates)
        priors = torch.softmax(logits[0], dim=0).cpu().numpy()
        return priors.astype(np.float64), float(value[0])

    def _replay(
        self, env: MengdeEnv, history: list[int], seed: int
    ) -> tuple[np.ndarray, bool, int]:
        observation, _ = env.reset(seed=seed)
        steps = 0
        for action in history:
            observation, _, terminated, truncated, _ = env.step(action)
            steps += 1
            if terminated or truncated:
                return observation, True, steps
        return observation, False, steps

    def _expand(
        self, node: Node, state: np.ndarray, decision: Decision
    ) -> float:
        priors, value = self.evaluate(state, decision)
        node.edges = [
            Edge(action=int(action["index"]), prior=float(prior))
            for action, prior in zip(decision.actions, priors)
        ]
        return value

    def _select(self, node: Node) -> Edge:
        total = max(1, sum(edge.visits for edge in node.edges))
        scale = np.sqrt(total)
        return max(
            node.edges,
            key=lambda edge: edge.value
            + self.c_puct * edge.prior * scale / (1 + edge.visits),
        )

    def search(
        self,
        simulator: MengdeEnv,
        history: list[int],
        seed: int,
        *,
        simulations: int = 16,
        temperature: float = 1.0,
        add_noise: bool = False,
        max_depth: int = 32,
    ) -> SearchResult:
        if simulations < 2:
            raise ValueError("MCTS needs at least two simulations")
        map_info = simulator.map_info()
        width, height = int(map_info["width"]), int(map_info["height"])
        root_state, terminal, replay_steps = self._replay(simulator, history, seed)
        if terminal:
            raise ValueError("cannot search from a terminal history")
        root_decision = current_decision(simulator, root_state, width, height)
        root = Node()
        self._expand(root, root_state, root_decision)
        if add_noise and len(root.edges) > 1:
            noise = self.rng.dirichlet(
                np.full(len(root.edges), self.dirichlet_alpha, dtype=np.float64)
            )
            for edge, sample in zip(root.edges, noise):
                edge.prior = (
                    (1.0 - self.dirichlet_fraction) * edge.prior
                    + self.dirichlet_fraction * float(sample)
                )

        for _ in range(simulations):
            observation, terminal, used = self._replay(simulator, history, seed)
            replay_steps += used
            node = root
            path: list[tuple[Edge, float]] = []
            leaf_value = 0.0
            for _depth in range(max_depth):
                edge = self._select(node)
                observation, reward, terminated, truncated, _ = simulator.step(edge.action)
                replay_steps += 1
                path.append((edge, float(reward)))
                if terminated or truncated:
                    leaf_value = 0.0
                    break
                if edge.child is None:
                    edge.child = Node()
                node = edge.child
                if not node.expanded:
                    decision = current_decision(simulator, observation, width, height)
                    leaf_value = self._expand(node, observation, decision)
                    break
            value = leaf_value
            for edge, reward in reversed(path):
                value = reward / self.value_scale + self.gamma * value
                edge.visits += 1
                edge.value_sum += value

        counts = np.asarray([edge.visits for edge in root.edges], dtype=np.float64)
        if temperature <= 1e-6:
            policy = np.zeros_like(counts)
            policy[int(np.argmax(counts))] = 1.0
        else:
            scaled = np.power(counts + 1e-12, 1.0 / temperature)
            policy = scaled / scaled.sum()
        choice = (
            int(self.rng.choice(len(policy), p=policy))
            if temperature > 1e-6 else int(np.argmax(policy))
        )
        return SearchResult(
            node=root, decision=root_decision, policy=policy.astype(np.float32),
            action=root.edges[choice].action, choice=choice,
            simulations=simulations, replay_steps=replay_steps,
        )

    def self_play_episode(
        self,
        env: MengdeEnv,
        simulator: MengdeEnv,
        *,
        seed: int,
        simulations: int = 12,
        temperature_moves: int = 12,
    ) -> tuple[list[TrainingSample], dict[str, float]]:
        observation, info = env.reset(seed=seed)
        history: list[int] = []
        samples: list[TrainingSample] = []
        rewards: list[float] = []
        replay_steps = 0
        while True:
            temperature = 1.0 if len(history) < temperature_moves else 0.0
            result = self.search(
                simulator, history, seed, simulations=simulations,
                temperature=temperature, add_noise=True,
            )
            samples.append(
                TrainingSample(
                    state=observation.copy(), local=result.decision.local.copy(),
                    candidates=result.decision.candidates.copy(), policy=result.policy.copy(),
                )
            )
            history.append(result.action)
            replay_steps += result.replay_steps
            observation, reward, terminated, truncated, info = env.step(result.action)
            rewards.append(float(reward))
            if terminated or truncated:
                break

        value = 0.0
        for index in range(len(samples) - 1, -1, -1):
            value = rewards[index] / self.value_scale + self.gamma * value
            samples[index].value = float(np.clip(value, -1.0, 1.0))
        return samples, {
            "return": float(sum(rewards)),
            "actions": float(len(history)),
            "status": float(info["status"]),
            "simulator_steps": float(replay_steps),
        }

    def update(
        self, samples: list[TrainingSample], *, epochs: int = 4, batch_size: int = 64
    ) -> dict[str, float]:
        if not samples:
            raise ValueError("cannot train AlphaZero without self-play samples")
        states = np.stack([sample.state for sample in samples])
        locals_ = np.stack([sample.local for sample in samples])
        targets = np.asarray([sample.value for sample in samples], dtype=np.float32)
        losses: list[tuple[float, float, float]] = []
        for _ in range(epochs):
            order = self.rng.permutation(len(samples))
            for start in range(0, len(order), batch_size):
                indices = order[start : start + batch_size]
                candidates, mask = pad_candidates(
                    [samples[int(index)].candidates for index in indices], self.device
                )
                maximum = candidates.shape[1]
                policies = np.zeros((len(indices), maximum), dtype=np.float32)
                for row, index in enumerate(indices):
                    policy = samples[int(index)].policy
                    policies[row, : len(policy)] = policy
                logits, values = self.network(
                    torch.as_tensor(states[indices], device=self.device),
                    torch.as_tensor(locals_[indices], device=self.device), candidates,
                )
                logits = logits.masked_fill(~mask, -1e9)
                log_policy = torch.log_softmax(logits, dim=-1)
                target_policy = torch.as_tensor(policies, device=self.device)
                policy_loss = -(target_policy * log_policy).sum(dim=-1).mean()
                value_target = torch.as_tensor(targets[indices], device=self.device)
                value_loss = torch.square(values - value_target).mean()
                loss = policy_loss + value_loss
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.network.parameters(), 1.0)
                self.optimizer.step()
                entropy = -(torch.softmax(logits, -1) * log_policy).sum(-1).mean()
                losses.append((float(policy_loss), float(value_loss), float(entropy)))
        means = np.mean(losses, axis=0)
        return {
            "policy_loss": float(means[0]), "value_loss": float(means[1]),
            "policy_entropy": float(means[2]), "samples": float(len(samples)),
        }

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {"algorithm": "alphazero-puct", "network": self.network.state_dict(),
             "gamma": self.gamma, "c_puct": self.c_puct,
             "value_scale": self.value_scale}, destination,
        )

    @property
    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.network.parameters())
