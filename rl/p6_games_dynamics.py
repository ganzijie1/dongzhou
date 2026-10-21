"""P6 evolutionary/cooperative games, inverse learning, and hybrid dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog
from scipy.special import logsumexp


Player = Hashable
Coalition = frozenset[Player]
Mode = Hashable


@dataclass(frozen=True)
class ReplicatorResult:
    trajectory: np.ndarray
    mean_payoffs: np.ndarray


def replicator_dynamics(
    payoff_matrix: Sequence[Sequence[float]],
    initial_population: Sequence[float],
    *,
    step_size: float = 0.02,
    steps: int = 1_000,
) -> ReplicatorResult:
    """Integrate replicator dynamics with a positivity-preserving exponential step."""

    payoff = np.asarray(payoff_matrix, dtype=np.float64)
    population = np.asarray(initial_population, dtype=np.float64)
    if (
        payoff.ndim != 2
        or payoff.shape[0] != payoff.shape[1]
        or population.shape != (payoff.shape[0],)
        or np.any(~np.isfinite(payoff))
        or np.any(~np.isfinite(population))
        or np.any(population < 0.0)
        or population.sum() <= 0.0
    ):
        raise ValueError("replicator inputs are invalid")
    if not isfinite(step_size) or step_size <= 0.0 or steps < 0:
        raise ValueError("replicator integration settings are invalid")
    population = population / population.sum()
    trajectory = np.empty((steps + 1, population.size), dtype=np.float64)
    mean_payoffs = np.empty(steps + 1, dtype=np.float64)
    for index in range(steps + 1):
        strategy_payoffs = payoff @ population
        mean = float(population @ strategy_payoffs)
        trajectory[index] = population
        mean_payoffs[index] = mean
        if index < steps:
            exponent = np.clip(step_size * (strategy_payoffs - mean), -700.0, 700.0)
            population = population * np.exp(exponent)
            population /= population.sum()
    return ReplicatorResult(trajectory, mean_payoffs)


@dataclass(frozen=True)
class CooperativeGameResult:
    allocation: Mapping[Player, float]
    maximum_excess: float
    excesses: Mapping[Coalition, float]


def _coalitions(players: tuple[Player, ...]) -> tuple[Coalition, ...]:
    return tuple(
        frozenset(group)
        for size in range(1, len(players))
        for group in combinations(players, size)
    )


def _coalition_values(
    players: tuple[Player, ...], value: Callable[[Coalition], float]
) -> dict[Coalition, float]:
    coalitions = (frozenset(), *_coalitions(players), frozenset(players))
    result = {coalition: float(value(coalition)) for coalition in coalitions}
    if any(not isfinite(number) for number in result.values()):
        raise ValueError("cooperative-game values must be finite")
    return result


def _excess_map(
    players: tuple[Player, ...], values: Mapping[Coalition, float], allocation: np.ndarray
) -> dict[Coalition, float]:
    positions = {player: index for index, player in enumerate(players)}
    return {
        coalition: values[coalition]
        - sum(float(allocation[positions[player]]) for player in coalition)
        for coalition in _coalitions(players)
    }


def least_core_allocation(
    players: Sequence[Player], value: Callable[[Coalition], float]
) -> CooperativeGameResult:
    """Find an efficient allocation minimizing the largest proper-coalition excess."""

    ordered = tuple(dict.fromkeys(players))
    if not ordered:
        raise ValueError("a cooperative game needs at least one player")
    values = _coalition_values(ordered, value)
    if len(ordered) == 1:
        allocation = np.array([values[frozenset(ordered)]])
        return CooperativeGameResult({ordered[0]: float(allocation[0])}, 0.0, {})
    coalitions = _coalitions(ordered)
    positions = {player: index for index, player in enumerate(ordered)}
    objective = np.zeros(len(ordered) + 1)
    objective[-1] = 1.0
    inequality = np.zeros((len(coalitions), len(ordered) + 1))
    bounds = np.zeros(len(coalitions))
    for row, coalition in enumerate(coalitions):
        for player in coalition:
            inequality[row, positions[player]] = -1.0
        inequality[row, -1] = -1.0
        bounds[row] = -values[coalition]
    equality = np.zeros((1, len(ordered) + 1))
    equality[0, : len(ordered)] = 1.0
    solved = linprog(
        objective,
        A_ub=inequality,
        b_ub=bounds,
        A_eq=equality,
        b_eq=[values[frozenset(ordered)]],
        bounds=[(None, None)] * (len(ordered) + 1),
        method="highs",
    )
    if not solved.success:
        raise RuntimeError(f"least-core optimization failed: {solved.message}")
    allocation = solved.x[:-1]
    excesses = _excess_map(ordered, values, allocation)
    return CooperativeGameResult(
        dict(zip(ordered, map(float, allocation), strict=True)),
        max(excesses.values(), default=0.0),
        excesses,
    )


def nucleolus_allocation(
    players: Sequence[Player],
    value: Callable[[Coalition], float],
    *,
    tolerance: float = 1e-9,
) -> CooperativeGameResult:
    """Compute a small finite game's nucleolus by sequential excess minimization."""

    ordered = tuple(dict.fromkeys(players))
    if not ordered or tolerance <= 0.0:
        raise ValueError("nucleolus inputs are invalid")
    values = _coalition_values(ordered, value)
    if len(ordered) == 1:
        amount = values[frozenset(ordered)]
        return CooperativeGameResult({ordered[0]: amount}, 0.0, {})
    positions = {player: index for index, player in enumerate(ordered)}
    remaining = list(_coalitions(ordered))
    fixed: list[tuple[Coalition, float]] = []
    allocation = np.zeros(len(ordered))
    while remaining:
        variable_count = len(ordered) + 1
        objective = np.zeros(variable_count)
        objective[-1] = 1.0
        a_eq = [np.r_[np.ones(len(ordered)), 0.0]]
        b_eq = [values[frozenset(ordered)]]
        for coalition, excess in fixed:
            row = np.zeros(variable_count)
            for player in coalition:
                row[positions[player]] = 1.0
            a_eq.append(row)
            b_eq.append(values[coalition] - excess)
        a_ub = []
        b_ub = []
        for coalition in remaining:
            row = np.zeros(variable_count)
            for player in coalition:
                row[positions[player]] = -1.0
            row[-1] = -1.0
            a_ub.append(row)
            b_ub.append(-values[coalition])
        solved = linprog(
            objective,
            A_ub=np.asarray(a_ub),
            b_ub=np.asarray(b_ub),
            A_eq=np.asarray(a_eq),
            b_eq=np.asarray(b_eq),
            bounds=[(None, None)] * variable_count,
            method="highs",
        )
        if not solved.success:
            raise RuntimeError(f"nucleolus optimization failed: {solved.message}")
        allocation = solved.x[:-1]
        level = float(solved.x[-1])

        base_eq = np.asarray([row[:-1] for row in a_eq])
        base_b = np.asarray(b_eq)
        face_ub = []
        face_b = []
        for coalition in remaining:
            row = np.zeros(len(ordered))
            for player in coalition:
                row[positions[player]] = -1.0
            face_ub.append(row)
            face_b.append(level - values[coalition])
        forced: list[Coalition] = []
        for coalition in remaining:
            objective_x = np.zeros(len(ordered))
            for player in coalition:
                objective_x[positions[player]] = -1.0
            probe = linprog(
                objective_x,
                A_ub=np.asarray(face_ub),
                b_ub=np.asarray(face_b),
                A_eq=base_eq,
                b_eq=base_b,
                bounds=[(None, None)] * len(ordered),
                method="highs",
            )
            threshold = values[coalition] - level
            if probe.success and -float(probe.fun) <= threshold + tolerance:
                forced.append(coalition)
        if not forced:
            forced = [
                coalition
                for coalition in remaining
                if abs(values[coalition] - sum(allocation[positions[p]] for p in coalition) - level)
                <= tolerance
            ]
        previous_rank = np.linalg.matrix_rank(base_eq, tol=tolerance)
        added = False
        for coalition in forced:
            row = np.zeros(len(ordered))
            for player in coalition:
                row[positions[player]] = 1.0
            candidate = np.vstack([base_eq, row])
            if np.linalg.matrix_rank(candidate, tol=tolerance) > previous_rank:
                fixed.append((coalition, level))
                base_eq = candidate
                previous_rank += 1
                added = True
            remaining.remove(coalition)
        if previous_rank >= len(ordered) or not remaining:
            break
        if not added and not forced:
            raise RuntimeError("nucleolus constraints did not reduce the feasible face")
    excesses = _excess_map(ordered, values, allocation)
    return CooperativeGameResult(
        dict(zip(ordered, map(float, allocation), strict=True)),
        max(excesses.values(), default=0.0),
        excesses,
    )


@dataclass(frozen=True)
class MaxEntropyIRLResult:
    reward_weights: np.ndarray
    rewards: np.ndarray
    policy: np.ndarray
    empirical_feature_counts: np.ndarray
    expected_feature_counts: np.ndarray
    gradient_norm: float


def maximum_entropy_irl(
    transition: Sequence[Sequence[Sequence[float]]],
    features: Sequence[Sequence[float]],
    demonstrations: Sequence[Sequence[int]],
    *,
    iterations: int = 300,
    learning_rate: float = 0.1,
    discount: float = 1.0,
    l2_penalty: float = 0.0,
) -> MaxEntropyIRLResult:
    """Learn a linear state reward with finite-horizon maximum-entropy IRL."""

    dynamics = np.asarray(transition, dtype=np.float64)
    feature_matrix = np.asarray(features, dtype=np.float64)
    demos = tuple(tuple(int(state) for state in path) for path in demonstrations)
    if dynamics.ndim != 3 or dynamics.shape[0] != dynamics.shape[2]:
        raise ValueError("IRL transition must have shape (states, actions, states)")
    states, _actions, next_states = dynamics.shape
    if (
        next_states != states
        or feature_matrix.ndim != 2
        or feature_matrix.shape[0] != states
        or np.any(~np.isfinite(dynamics))
        or np.any(dynamics < 0.0)
        or not np.allclose(dynamics.sum(axis=2), 1.0)
        or np.any(~np.isfinite(feature_matrix))
    ):
        raise ValueError("IRL model is invalid")
    if not demos or len({len(path) for path in demos}) != 1 or len(demos[0]) < 2:
        raise ValueError("IRL demonstrations must have one common horizon of at least two")
    if any(state < 0 or state >= states for path in demos for state in path):
        raise ValueError("IRL demonstration contains an unknown state")
    if (
        iterations <= 0
        or learning_rate <= 0.0
        or not 0.0 < discount <= 1.0
        or l2_penalty < 0.0
    ):
        raise ValueError("IRL optimization settings are invalid")

    horizon = len(demos[0])
    powers = discount ** np.arange(horizon)
    empirical = np.mean(
        [sum(powers[t] * feature_matrix[state] for t, state in enumerate(path)) for path in demos],
        axis=0,
    )
    initial = np.bincount([path[0] for path in demos], minlength=states).astype(np.float64)
    initial /= initial.sum()
    weights = np.zeros(feature_matrix.shape[1], dtype=np.float64)

    def policy_and_counts(current_weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        rewards = feature_matrix @ current_weights
        policy = np.empty((horizon, states, dynamics.shape[1]), dtype=np.float64)
        next_value = np.zeros(states, dtype=np.float64)
        for time_index in range(horizon - 1, -1, -1):
            action_values = rewards[:, None] + discount * np.einsum(
                "sak,k->sa", dynamics, next_value
            )
            normalizer = logsumexp(action_values, axis=1)
            policy[time_index] = np.exp(action_values - normalizer[:, None])
            next_value = normalizer
        occupancy = initial.copy()
        expected = np.zeros(feature_matrix.shape[1], dtype=np.float64)
        for time_index in range(horizon):
            expected += powers[time_index] * (occupancy @ feature_matrix)
            if time_index + 1 < horizon:
                occupancy = np.einsum(
                    "s,sa,sak->k", occupancy, policy[time_index], dynamics
                )
        return policy, expected

    for _ in range(iterations):
        policy, expected = policy_and_counts(weights)
        gradient = empirical - expected - l2_penalty * weights
        weights += learning_rate * gradient
    policy, expected = policy_and_counts(weights)
    gradient = empirical - expected - l2_penalty * weights
    return MaxEntropyIRLResult(
        weights,
        feature_matrix @ weights,
        policy,
        empirical,
        expected,
        float(np.linalg.norm(gradient)),
    )


def _identity_reset(state: np.ndarray) -> np.ndarray:
    return state.copy()


@dataclass(frozen=True)
class HybridTransition:
    source: Mode
    target: Mode
    guard: Callable[[np.ndarray], bool]
    probability: float | Callable[[np.ndarray], float] = 1.0
    reset: Callable[[np.ndarray], np.ndarray] = _identity_reset


@dataclass(frozen=True)
class HybridTrajectory:
    modes: tuple[Mode, ...]
    states: np.ndarray


class StochasticHybridSystem:
    """Continuous flows with guarded probabilistic discrete mode changes."""

    def __init__(
        self,
        flows: Mapping[Mode, Callable[[np.ndarray, float, np.random.Generator], np.ndarray]],
        transitions: Sequence[HybridTransition],
    ) -> None:
        if not flows:
            raise ValueError("a hybrid system needs at least one mode")
        self.flows = dict(flows)
        self.transitions = tuple(transitions)
        if any(edge.source not in self.flows or edge.target not in self.flows for edge in self.transitions):
            raise ValueError("hybrid transition references an unknown mode")

    def step(
        self,
        mode: Mode,
        state: Sequence[float],
        step_size: float,
        rng: np.random.Generator,
    ) -> tuple[Mode, np.ndarray]:
        if mode not in self.flows or not isfinite(step_size) or step_size <= 0.0:
            raise ValueError("hybrid step inputs are invalid")
        current = np.asarray(state, dtype=np.float64)
        flowed = np.asarray(self.flows[mode](current.copy(), step_size, rng), dtype=np.float64)
        if flowed.shape != current.shape or np.any(~np.isfinite(flowed)):
            raise ValueError("hybrid flow returned an invalid state")
        enabled = [edge for edge in self.transitions if edge.source == mode and edge.guard(flowed)]
        probabilities = np.asarray(
            [edge.probability(flowed) if callable(edge.probability) else edge.probability for edge in enabled],
            dtype=np.float64,
        )
        if np.any(~np.isfinite(probabilities)) or np.any(probabilities < 0.0) or probabilities.sum() > 1.0 + 1e-12:
            raise ValueError("enabled hybrid transition probabilities are invalid")
        draw = rng.random()
        cumulative = 0.0
        for edge, probability in zip(enabled, probabilities, strict=True):
            cumulative += float(probability)
            if draw < cumulative:
                reset = np.asarray(edge.reset(flowed.copy()), dtype=np.float64)
                if reset.shape != flowed.shape or np.any(~np.isfinite(reset)):
                    raise ValueError("hybrid reset returned an invalid state")
                return edge.target, reset
        return mode, flowed

    def simulate(
        self,
        initial_mode: Mode,
        initial_state: Sequence[float],
        *,
        step_size: float,
        steps: int,
        seed: int | None = None,
    ) -> HybridTrajectory:
        if steps < 0:
            raise ValueError("hybrid simulation steps must be non-negative")
        rng = np.random.default_rng(seed)
        mode = initial_mode
        state = np.asarray(initial_state, dtype=np.float64)
        modes = [mode]
        states = [state.copy()]
        for _ in range(steps):
            mode, state = self.step(mode, state, step_size, rng)
            modes.append(mode)
            states.append(state.copy())
        return HybridTrajectory(tuple(modes), np.stack(states))

    def estimate_reach_probability(
        self,
        initial_mode: Mode,
        initial_state: Sequence[float],
        target: Callable[[Mode, np.ndarray], bool],
        *,
        step_size: float,
        steps: int,
        samples: int = 1_000,
        seed: int | None = None,
    ) -> float:
        if samples <= 0:
            raise ValueError("reachability estimation needs positive samples")
        seeds = np.random.SeedSequence(seed).spawn(samples)
        hits = 0
        for sample_seed in seeds:
            trajectory = self.simulate(
                initial_mode,
                initial_state,
                step_size=step_size,
                steps=steps,
                seed=int(sample_seed.generate_state(1)[0]),
            )
            if any(target(mode, state) for mode, state in zip(trajectory.modes, trajectory.states, strict=True)):
                hits += 1
        return hits / samples
