"""P5 belief-space planning, dynamic risk, verification, learning, and DMD."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, log, sqrt
from random import Random
from statistics import NormalDist
from typing import Callable, Hashable, Mapping, Sequence

import numpy as np

from rl.belief_risk import conditional_value_at_risk
from rl.decision_math import solve_zero_sum_game


State = Hashable
Action = Hashable
Observation = Hashable
History = tuple[Hashable, ...]


@dataclass
class _POMCPAction:
    visits: int = 0
    total_value: float = 0.0

    @property
    def mean_value(self) -> float:
        return self.total_value / self.visits if self.visits else 0.0


@dataclass
class _POMCPNode:
    visits: int = 0
    actions: dict[Action, _POMCPAction] = field(default_factory=dict)


@dataclass(frozen=True)
class POMCPResult:
    action: Action
    action_values: Mapping[Action, float]
    action_visits: Mapping[Action, int]
    simulations: int


class POMCPPlanner:
    """Small finite POMCP planner using root sampling and UCB tree search."""

    def __init__(
        self,
        *,
        simulations: int = 1_000,
        horizon: int = 8,
        discount: float = 0.95,
        exploration: float = sqrt(2.0),
        seed: int = 2026,
    ) -> None:
        if simulations <= 0 or horizon <= 0:
            raise ValueError("POMCP simulations and horizon must be positive")
        if not 0.0 <= discount <= 1.0:
            raise ValueError("POMCP discount must be in [0, 1]")
        if not isfinite(exploration) or exploration < 0.0:
            raise ValueError("POMCP exploration must be finite and non-negative")
        self.simulations = int(simulations)
        self.horizon = int(horizon)
        self.discount = float(discount)
        self.exploration = float(exploration)
        self.random = Random(seed)
        self.tree: dict[History, _POMCPNode] = {}

    @staticmethod
    def _available(
        state: State, actions: Callable[[State], Sequence[Action]]
    ) -> tuple[Action, ...]:
        result = tuple(dict.fromkeys(actions(state)))
        if not result:
            raise ValueError(f"POMCP state has no legal actions: {state!r}")
        return result

    def _rollout(
        self,
        state: State,
        depth: int,
        actions: Callable[[State], Sequence[Action]],
        model: Callable[[State, Action, Random], tuple[State, Observation, float]],
    ) -> float:
        if depth >= self.horizon:
            return 0.0
        choices = self._available(state, actions)
        action = choices[self.random.randrange(len(choices))]
        next_state, _observation, reward = model(state, action, self.random)
        value = float(reward)
        if not isfinite(value):
            raise ValueError("POMCP rewards must be finite")
        return value + self.discount * self._rollout(
            next_state, depth + 1, actions, model
        )

    def _simulate(
        self,
        state: State,
        history: History,
        depth: int,
        actions: Callable[[State], Sequence[Action]],
        model: Callable[[State, Action, Random], tuple[State, Observation, float]],
    ) -> float:
        if depth >= self.horizon:
            return 0.0
        choices = self._available(state, actions)
        node = self.tree.get(history)
        if node is None:
            self.tree[history] = _POMCPNode(
                actions={action: _POMCPAction() for action in choices}
            )
            return self._rollout(state, depth, actions, model)
        if tuple(node.actions) != choices:
            raise ValueError("POMCP legal actions must agree for one history")
        unvisited = [action for action in choices if node.actions[action].visits == 0]
        if unvisited:
            selected = unvisited[0]
        else:
            selected = max(
                choices,
                key=lambda action: (
                    node.actions[action].mean_value
                    + self.exploration
                    * sqrt(log(max(1, node.visits)) / node.actions[action].visits),
                    repr(action),
                ),
            )
        next_state, observation, reward = model(state, selected, self.random)
        immediate = float(reward)
        if not isfinite(immediate):
            raise ValueError("POMCP rewards must be finite")
        total = immediate + self.discount * self._simulate(
            next_state,
            history + (selected, observation),
            depth + 1,
            actions,
            model,
        )
        node.visits += 1
        stats = node.actions[selected]
        stats.visits += 1
        stats.total_value += total
        return total

    def plan(
        self,
        particles: Sequence[State],
        actions: Callable[[State], Sequence[Action]],
        model: Callable[[State, Action, Random], tuple[State, Observation, float]],
    ) -> POMCPResult:
        belief = tuple(particles)
        if not belief:
            raise ValueError("POMCP needs at least one belief particle")
        self.tree.clear()
        root_actions = self._available(belief[0], actions)
        self.tree[()] = _POMCPNode(
            actions={action: _POMCPAction() for action in root_actions}
        )
        for _ in range(self.simulations):
            state = belief[self.random.randrange(len(belief))]
            self._simulate(state, (), 0, actions, model)
        root = self.tree[()]
        selected = max(
            root_actions,
            key=lambda action: (
                root.actions[action].visits,
                root.actions[action].mean_value,
                repr(action),
            ),
        )
        return POMCPResult(
            selected,
            {action: root.actions[action].mean_value for action in root_actions},
            {action: root.actions[action].visits for action in root_actions},
            self.simulations,
        )


@dataclass(frozen=True)
class DynamicRiskResult:
    values: np.ndarray
    action_values: np.ndarray
    policy: np.ndarray
    alpha: float


def nested_cvar_mdp(
    transitions: Sequence[Sequence[Sequence[Sequence[float]]]],
    costs: Sequence[Sequence[Sequence[Sequence[float]]]],
    terminal_costs: Sequence[float],
    *,
    alpha: float = 0.9,
    discount: float = 1.0,
) -> DynamicRiskResult:
    """Backward induction with time-consistent nested conditional CVaR."""

    probability = np.asarray(transitions, dtype=np.float64)
    stage = np.asarray(costs, dtype=np.float64)
    terminal = np.asarray(terminal_costs, dtype=np.float64)
    if probability.ndim != 4 or stage.shape != probability.shape:
        raise ValueError("risk MDP transitions and costs must be aligned T x S x A x S")
    horizon, states, actions, next_states = probability.shape
    if states == 0 or actions == 0 or next_states != states or terminal.shape != (states,):
        raise ValueError("risk MDP dimensions are invalid")
    if any(np.any(~np.isfinite(array)) for array in (probability, stage, terminal)):
        raise ValueError("risk MDP values must be finite")
    if np.any(probability < 0.0) or not np.allclose(probability.sum(axis=-1), 1.0):
        raise ValueError("risk MDP transition rows must be probability distributions")
    if not 0.0 <= alpha < 1.0 or not 0.0 <= discount <= 1.0:
        raise ValueError("risk MDP alpha/discount are invalid")
    values = np.empty((horizon + 1, states), dtype=np.float64)
    values[-1] = terminal
    action_values = np.empty((horizon, states, actions), dtype=np.float64)
    policy = np.empty((horizon, states), dtype=np.int64)
    for time in range(horizon - 1, -1, -1):
        for state in range(states):
            for action in range(actions):
                losses = stage[time, state, action] + discount * values[time + 1]
                action_values[time, state, action] = conditional_value_at_risk(
                    tuple(losses),
                    alpha,
                    tuple(probability[time, state, action]),
                )
            selected = int(np.argmin(action_values[time, state]))
            policy[time, state] = selected
            values[time, state] = action_values[time, state, selected]
    return DynamicRiskResult(values, action_values, policy, float(alpha))


@dataclass(frozen=True)
class StochasticGameResult:
    values: tuple[float, ...]
    row_strategies: tuple[tuple[float, ...], ...]
    column_strategies: tuple[tuple[float, ...], ...]
    iterations: int
    residual: float


def solve_discounted_zero_sum_stochastic_game(
    rewards: Sequence[Sequence[Sequence[float]]],
    transitions: Sequence[Sequence[Sequence[Sequence[float]]]],
    *,
    discount: float = 0.95,
    tolerance: float = 1e-10,
    max_iterations: int = 10_000,
) -> StochasticGameResult:
    """Shapley value iteration for a finite discounted zero-sum Markov game."""

    reward = np.asarray(rewards, dtype=np.float64)
    probability = np.asarray(transitions, dtype=np.float64)
    if reward.ndim != 3 or probability.shape != reward.shape + (reward.shape[0],):
        raise ValueError("stochastic-game arrays must be S x A x B and S x A x B x S")
    if any(np.any(~np.isfinite(array)) for array in (reward, probability)):
        raise ValueError("stochastic-game inputs must be finite")
    if np.any(probability < 0.0) or not np.allclose(probability.sum(axis=-1), 1.0):
        raise ValueError("stochastic-game transition rows must sum to one")
    if not 0.0 <= discount < 1.0 or tolerance <= 0.0 or max_iterations <= 0:
        raise ValueError("stochastic-game solver parameters are invalid")
    states = reward.shape[0]
    values = np.zeros(states, dtype=np.float64)
    row_strategies: tuple[tuple[float, ...], ...] = ()
    column_strategies: tuple[tuple[float, ...], ...] = ()
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        updated = np.empty_like(values)
        rows = []
        columns = []
        for state in range(states):
            matrix = reward[state] + discount * np.tensordot(
                probability[state], values, axes=([-1], [0])
            )
            equilibrium = solve_zero_sum_game(matrix)
            updated[state] = equilibrium.value
            rows.append(tuple(equilibrium.row_strategy))
            columns.append(tuple(equilibrium.column_strategy))
        residual = float(np.max(np.abs(updated - values)))
        values = updated
        row_strategies = tuple(rows)
        column_strategies = tuple(columns)
        if residual <= tolerance:
            return StochasticGameResult(
                tuple(map(float, values)),
                row_strategies,
                column_strategies,
                iteration,
                residual,
            )
    raise RuntimeError(
        f"stochastic-game value iteration did not converge; residual={residual}"
    )


@dataclass(frozen=True)
class ModelCheckingResult:
    probabilities: tuple[float, ...]
    expected_steps: tuple[float, ...]
    iterations: int
    residual: float


def dtmc_reachability(
    transitions: Sequence[Sequence[float]],
    targets: Sequence[int],
    *,
    unsafe: Sequence[int] = (),
    horizon: int | None = None,
    tolerance: float = 1e-12,
    max_iterations: int = 100_000,
) -> ModelCheckingResult:
    """Bounded or unbounded reach-avoid probabilities for a finite DTMC."""

    matrix = np.asarray(transitions, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0:
        raise ValueError("DTMC transition matrix must be non-empty and square")
    if np.any(~np.isfinite(matrix)) or np.any(matrix < 0.0) or not np.allclose(matrix.sum(axis=1), 1.0):
        raise ValueError("DTMC rows must be finite probability distributions")
    size = matrix.shape[0]
    target_set = frozenset(map(int, targets))
    unsafe_set = frozenset(map(int, unsafe))
    if not target_set or target_set & unsafe_set or any(
        state < 0 or state >= size for state in target_set | unsafe_set
    ):
        raise ValueError("DTMC target/unsafe states are invalid")
    probabilities = np.zeros(size, dtype=np.float64)
    probabilities[list(target_set)] = 1.0
    fixed = target_set | unsafe_set
    iterations = horizon if horizon is not None else max_iterations
    if iterations is None or iterations < 0:
        raise ValueError("DTMC horizon must be non-negative")
    residual = 0.0
    actual = 0
    for actual in range(1, int(iterations) + 1):
        updated = matrix @ probabilities
        updated[list(target_set)] = 1.0
        if unsafe_set:
            updated[list(unsafe_set)] = 0.0
        residual = float(np.max(np.abs(updated - probabilities)))
        probabilities = updated
        if horizon is None and residual <= tolerance:
            break
    transient = [state for state in range(size) if state not in fixed]
    expected = np.full(size, np.inf, dtype=np.float64)
    expected[list(target_set)] = 0.0
    almost_sure = [state for state in transient if probabilities[state] >= 1.0 - 1e-10]
    if almost_sure:
        sub = matrix[np.ix_(almost_sure, almost_sure)]
        try:
            expected[almost_sure] = np.linalg.solve(
                np.eye(len(almost_sure)) - sub,
                np.ones(len(almost_sure)),
            )
        except np.linalg.LinAlgError:
            pass
    return ModelCheckingResult(
        tuple(map(float, probabilities)),
        tuple(map(float, expected)),
        actual,
        residual,
    )


@dataclass(frozen=True)
class OptimalStoppingResult:
    values: np.ndarray
    stop: np.ndarray


def finite_horizon_optimal_stopping(
    transitions: Sequence[Sequence[float]],
    stop_rewards: Sequence[Sequence[float]],
    continue_rewards: Sequence[Sequence[float]],
    *,
    discount: float = 1.0,
) -> OptimalStoppingResult:
    """Backward induction for a finite-state finite-horizon stopping problem."""

    matrix = np.asarray(transitions, dtype=np.float64)
    stop_reward = np.asarray(stop_rewards, dtype=np.float64)
    continue_reward = np.asarray(continue_rewards, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("stopping transition matrix must be square")
    states = matrix.shape[0]
    if stop_reward.ndim != 2 or stop_reward.shape[1] != states:
        raise ValueError("stopping rewards must be (horizon + 1) x states")
    horizon = stop_reward.shape[0] - 1
    if continue_reward.shape != (horizon, states):
        raise ValueError("continuation rewards must be horizon x states")
    if any(np.any(~np.isfinite(array)) for array in (matrix, stop_reward, continue_reward)):
        raise ValueError("stopping inputs must be finite")
    if np.any(matrix < 0.0) or not np.allclose(matrix.sum(axis=1), 1.0):
        raise ValueError("stopping transition rows must sum to one")
    if not 0.0 <= discount <= 1.0:
        raise ValueError("stopping discount must be in [0, 1]")
    values = np.empty_like(stop_reward)
    stop = np.ones_like(stop_reward, dtype=bool)
    values[-1] = stop_reward[-1]
    for time in range(horizon - 1, -1, -1):
        continuation = continue_reward[time] + discount * matrix @ values[time + 1]
        stop[time] = stop_reward[time] >= continuation
        values[time] = np.maximum(stop_reward[time], continuation)
    return OptimalStoppingResult(values, stop)


class ExponentiatedGradient:
    """Entropic mirror ascent/descent on a probability simplex."""

    def __init__(self, dimension: int, *, learning_rate: float = 0.1) -> None:
        if dimension <= 0 or not isfinite(learning_rate) or learning_rate <= 0.0:
            raise ValueError("mirror descent needs a dimension and positive learning rate")
        self.learning_rate = float(learning_rate)
        self.weights = np.ones(dimension, dtype=np.float64) / dimension

    def update(self, gradient: Sequence[float], *, maximize: bool = False) -> tuple[float, ...]:
        values = np.asarray(gradient, dtype=np.float64)
        if values.shape != self.weights.shape or np.any(~np.isfinite(values)):
            raise ValueError("mirror-descent gradient has invalid shape or values")
        direction = 1.0 if maximize else -1.0
        logits = np.log(np.maximum(self.weights, 1e-300)) + direction * self.learning_rate * values
        logits -= logits.max()
        updated = np.exp(logits)
        self.weights = updated / updated.sum()
        return tuple(map(float, self.weights))


@dataclass(frozen=True)
class OPEStep:
    reward: float
    behavior_probability: float
    target_probability: float
    q_value: float
    next_value: float


@dataclass(frozen=True)
class SequentialDREstimate:
    value: float
    standard_error: float
    confidence_interval: tuple[float, float]
    episode_values: tuple[float, ...]


def sequential_doubly_robust_ope(
    episodes: Sequence[Sequence[OPEStep]],
    initial_values: Sequence[float],
    *,
    discount: float = 1.0,
    importance_clip: float | None = None,
    confidence: float = 0.95,
) -> SequentialDREstimate:
    """Per-decision sequential doubly robust off-policy evaluation."""

    if len(episodes) != len(initial_values) or len(episodes) < 2:
        raise ValueError("sequential DR needs aligned data from at least two episodes")
    if not 0.0 <= discount <= 1.0 or not 0.0 < confidence < 1.0:
        raise ValueError("sequential DR discount/confidence are invalid")
    if importance_clip is not None and (
        not isfinite(importance_clip) or importance_clip <= 0.0
    ):
        raise ValueError("importance clip must be positive and finite")
    estimates = []
    for trajectory, initial in zip(episodes, initial_values):
        estimate = float(initial)
        if not isfinite(estimate):
            raise ValueError("initial value predictions must be finite")
        ratio = 1.0
        for time, step in enumerate(trajectory):
            values = (
                float(step.reward),
                float(step.behavior_probability),
                float(step.target_probability),
                float(step.q_value),
                float(step.next_value),
            )
            if not all(map(isfinite, values)) or values[1] <= 0.0 or values[2] < 0.0:
                raise ValueError("sequential DR step contains invalid values")
            ratio *= values[2] / values[1]
            if importance_clip is not None:
                ratio = min(ratio, importance_clip)
            temporal_error = values[0] + discount * values[4] - values[3]
            estimate += (discount**time) * ratio * temporal_error
        estimates.append(estimate)
    array = np.asarray(estimates, dtype=np.float64)
    mean = float(array.mean())
    standard_error = float(array.std(ddof=1) / sqrt(array.size))
    critical = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    radius = critical * standard_error
    return SequentialDREstimate(
        mean,
        standard_error,
        (mean - radius, mean + radius),
        tuple(map(float, array)),
    )


@dataclass(frozen=True)
class DMDResult:
    operator: np.ndarray
    eigenvalues: np.ndarray
    modes: np.ndarray
    rank: int
    relative_residual: float

    def predict(self, state: Sequence[float], steps: int = 1) -> np.ndarray:
        if steps < 0:
            raise ValueError("DMD prediction steps must be non-negative")
        vector = np.asarray(state, dtype=np.float64)
        if vector.shape != (self.operator.shape[0],):
            raise ValueError("DMD prediction state has invalid shape")
        return np.linalg.matrix_power(self.operator, steps) @ vector


def dynamic_mode_decomposition(
    snapshots: Sequence[Sequence[float]],
    *,
    rank: int | None = None,
) -> DMDResult:
    """Exact DMD over columns of a feature-by-time snapshot matrix."""

    data = np.asarray(snapshots, dtype=np.float64)
    if data.ndim != 2 or data.shape[1] < 2 or np.any(~np.isfinite(data)):
        raise ValueError("DMD snapshots must be a finite feature x time matrix")
    before, after = data[:, :-1], data[:, 1:]
    left, singular, right_t = np.linalg.svd(before, full_matrices=False)
    numerical_rank = int(np.sum(singular > singular[0] * 1e-12)) if singular.size else 0
    selected_rank = numerical_rank if rank is None else int(rank)
    if selected_rank <= 0 or selected_rank > numerical_rank:
        raise ValueError("DMD rank must be within the numerical snapshot rank")
    left_r = left[:, :selected_rank]
    singular_r = singular[:selected_rank]
    right_r = right_t[:selected_rank].T
    reduced = left_r.T @ after @ right_r @ np.diag(1.0 / singular_r)
    eigenvalues, eigenvectors = np.linalg.eig(reduced)
    modes = after @ right_r @ np.diag(1.0 / singular_r) @ eigenvectors
    operator = after @ right_r @ np.diag(1.0 / singular_r) @ left_r.T
    denominator = max(float(np.linalg.norm(after)), 1e-15)
    residual = float(np.linalg.norm(after - operator @ before) / denominator)
    return DMDResult(operator, eigenvalues, modes, selected_rank, residual)


def extended_dynamic_mode_decomposition(
    states: Sequence[Sequence[float]],
    observables: Callable[[np.ndarray], Sequence[float]],
    *,
    rank: int | None = None,
) -> DMDResult:
    """EDMD by lifting state snapshots through a supplied observable map."""

    data = np.asarray(states, dtype=np.float64)
    if data.ndim != 2 or data.shape[1] < 2 or np.any(~np.isfinite(data)):
        raise ValueError("EDMD states must be a finite state x time matrix")
    lifted = np.column_stack(
        [np.asarray(observables(data[:, index]), dtype=np.float64) for index in range(data.shape[1])]
    )
    if lifted.ndim != 2 or np.any(~np.isfinite(lifted)):
        raise ValueError("EDMD observables must return aligned finite vectors")
    return dynamic_mode_decomposition(lifted, rank=rank)
