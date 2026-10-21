"""Planning and control primitives from the chapter-one mathematics map."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import isfinite, sqrt
from typing import Sequence

import numpy as np
from scipy.optimize import linprog

from rl.decision_math import ZeroSumSolution, solve_zero_sum_game


@dataclass(frozen=True)
class StochasticShortestPathResult:
    """Optimal values and a deterministic policy for a finite SSP."""

    values: np.ndarray
    action_values: np.ndarray
    policy: np.ndarray
    residual: float


def stochastic_shortest_path(
    transitions: Sequence[Sequence[Sequence[float]]],
    costs: Sequence[Sequence[float]],
    terminal_states: Sequence[int],
) -> StochasticShortestPathResult:
    """Solve a finite stochastic shortest-path problem by its Bellman LP.

    Costs must be non-negative. The linear program is unbounded when a state
    has no proper route to a terminal state, which is reported as an error.
    """

    probability = np.asarray(transitions, dtype=np.float64)
    stage_cost = np.asarray(costs, dtype=np.float64)
    if probability.ndim != 3:
        raise ValueError("SSP transitions must have shape S x A x S")
    states, actions, next_states = probability.shape
    if states == 0 or actions == 0 or next_states != states:
        raise ValueError("SSP transition dimensions are invalid")
    if stage_cost.shape != (states, actions):
        raise ValueError("SSP costs must have shape S x A")
    if np.any(~np.isfinite(probability)) or np.any(~np.isfinite(stage_cost)):
        raise ValueError("SSP inputs must be finite")
    if np.any(probability < 0.0) or not np.allclose(
        probability.sum(axis=-1), 1.0
    ):
        raise ValueError("SSP transition rows must be probability distributions")
    if np.any(stage_cost < 0.0):
        raise ValueError("SSP costs must be non-negative")
    terminals = frozenset(int(state) for state in terminal_states)
    if not terminals or any(state < 0 or state >= states for state in terminals):
        raise ValueError("SSP terminal states are invalid")

    inequality_rows = []
    bounds: list[tuple[float, float | None]] = []
    for state in range(states):
        bounds.append((0.0, 0.0) if state in terminals else (0.0, None))
        if state in terminals:
            continue
        for action in range(actions):
            row = -probability[state, action].copy()
            row[state] += 1.0
            inequality_rows.append((row, stage_cost[state, action]))
    if not inequality_rows:
        values = np.zeros(states, dtype=np.float64)
    else:
        matrix = np.vstack([row for row, _bound in inequality_rows])
        upper = np.asarray([bound for _row, bound in inequality_rows])
        result = linprog(
            -np.ones(states, dtype=np.float64),
            A_ub=matrix,
            b_ub=upper,
            bounds=bounds,
            method="highs",
        )
        if not result.success or result.x is None:
            raise ValueError(
                "SSP has no finite proper solution from every non-terminal state"
            )
        values = np.asarray(result.x, dtype=np.float64)

    action_values = stage_cost + np.einsum("sak,k->sa", probability, values)
    policy = np.argmin(action_values, axis=1).astype(np.int64)
    for terminal in terminals:
        action_values[terminal] = 0.0
        policy[terminal] = -1
    bellman = np.min(action_values, axis=1)
    bellman[list(terminals)] = 0.0
    residual = float(np.max(np.abs(values - bellman)))
    return StochasticShortestPathResult(values, action_values, policy, residual)


@dataclass(frozen=True)
class POSGStepResult:
    """Posterior state belief and its observation likelihood."""

    belief: tuple[float, ...]
    observation_probability: float


class FinitePOSG:
    """Belief filtering and zero-sum stage solving for a finite POSG."""

    def __init__(
        self,
        transitions: Sequence[Sequence[Sequence[Sequence[float]]]],
        observations: Sequence[Sequence[Sequence[Sequence[float]]]],
        payoffs: Sequence[Sequence[Sequence[float]]],
    ) -> None:
        self.transitions = np.asarray(transitions, dtype=np.float64)
        self.observations = np.asarray(observations, dtype=np.float64)
        self.payoffs = np.asarray(payoffs, dtype=np.float64)
        if self.transitions.ndim != 4:
            raise ValueError("POSG transitions must have shape S x A x B x S")
        states, rows, columns, next_states = self.transitions.shape
        if not states or not rows or not columns or next_states != states:
            raise ValueError("POSG transition dimensions are invalid")
        if self.observations.ndim != 4 or self.observations.shape[:3] != (
            rows,
            columns,
            states,
        ):
            raise ValueError("POSG observations must have shape A x B x S x O")
        if self.payoffs.shape != (states, rows, columns):
            raise ValueError("POSG payoffs must have shape S x A x B")
        arrays = (self.transitions, self.observations, self.payoffs)
        if any(np.any(~np.isfinite(array)) for array in arrays):
            raise ValueError("POSG inputs must be finite")
        if np.any(self.transitions < 0.0) or not np.allclose(
            self.transitions.sum(axis=-1), 1.0
        ):
            raise ValueError("POSG transition rows must sum to one")
        if np.any(self.observations < 0.0) or not np.allclose(
            self.observations.sum(axis=-1), 1.0
        ):
            raise ValueError("POSG observation rows must sum to one")
        self.states = states
        self.row_actions = rows
        self.column_actions = columns

    def _belief(self, belief: Sequence[float]) -> np.ndarray:
        probability = np.asarray(belief, dtype=np.float64)
        if probability.shape != (self.states,) or np.any(~np.isfinite(probability)):
            raise ValueError("POSG belief has invalid dimensions or values")
        if np.any(probability < 0.0) or probability.sum() <= 0.0:
            raise ValueError("POSG belief must contain non-negative mass")
        return probability / probability.sum()

    def update_belief(
        self,
        belief: Sequence[float],
        row_action: int,
        column_action: int,
        observation: int,
    ) -> POSGStepResult:
        """Apply the controlled Bayes filter after one joint action."""

        if not 0 <= row_action < self.row_actions:
            raise ValueError("POSG row action is out of range")
        if not 0 <= column_action < self.column_actions:
            raise ValueError("POSG column action is out of range")
        if not 0 <= observation < self.observations.shape[-1]:
            raise ValueError("POSG observation is out of range")
        prior = self._belief(belief)
        predicted = prior @ self.transitions[:, row_action, column_action, :]
        unnormalized = predicted * self.observations[
            row_action, column_action, :, observation
        ]
        evidence = float(unnormalized.sum())
        if evidence <= 0.0:
            raise ValueError("POSG observation has zero probability under the belief")
        posterior = unnormalized / evidence
        return POSGStepResult(tuple(float(value) for value in posterior), evidence)

    def solve_stage(self, belief: Sequence[float]) -> ZeroSumSolution:
        """Solve the zero-sum Bayesian stage game induced by a belief."""

        probability = self._belief(belief)
        expected_payoff = np.einsum("s,sab->ab", probability, self.payoffs)
        return solve_zero_sum_game(expected_payoff)


@dataclass(frozen=True)
class EventTriggeredControlResult:
    states: np.ndarray
    controls: np.ndarray
    triggered: tuple[bool, ...]


def simulate_event_triggered_control(
    system: Sequence[Sequence[float]],
    control_matrix: Sequence[Sequence[float]],
    feedback_gain: Sequence[Sequence[float]],
    initial_state: Sequence[float],
    *,
    steps: int,
    absolute_threshold: float = 0.0,
    relative_threshold: float = 0.1,
) -> EventTriggeredControlResult:
    """Simulate linear feedback that transmits only when state error is large."""

    state_matrix = np.asarray(system, dtype=np.float64)
    input_matrix = np.asarray(control_matrix, dtype=np.float64)
    gain = np.asarray(feedback_gain, dtype=np.float64)
    initial = np.asarray(initial_state, dtype=np.float64)
    if state_matrix.ndim != 2 or state_matrix.shape[0] != state_matrix.shape[1]:
        raise ValueError("event-triggered system matrix must be square")
    dimensions = state_matrix.shape[0]
    if initial.shape != (dimensions,):
        raise ValueError("event-triggered initial state has invalid dimensions")
    if input_matrix.ndim != 2 or input_matrix.shape[0] != dimensions:
        raise ValueError("event-triggered control matrix has invalid dimensions")
    if gain.shape != (input_matrix.shape[1], dimensions):
        raise ValueError("event-triggered feedback gain has invalid dimensions")
    arrays = (state_matrix, input_matrix, gain, initial)
    if any(np.any(~np.isfinite(array)) for array in arrays):
        raise ValueError("event-triggered control inputs must be finite")
    if steps < 0:
        raise ValueError("event-triggered control steps must be non-negative")
    if (
        not isfinite(absolute_threshold)
        or not isfinite(relative_threshold)
        or absolute_threshold < 0.0
        or relative_threshold < 0.0
    ):
        raise ValueError("event-trigger thresholds must be finite and non-negative")

    states = np.empty((steps + 1, dimensions), dtype=np.float64)
    controls = np.empty((steps, input_matrix.shape[1]), dtype=np.float64)
    states[0] = initial
    transmitted = initial.copy()
    triggers = []
    for time in range(steps):
        state = states[time]
        threshold = absolute_threshold + relative_threshold * np.linalg.norm(state)
        trigger = time == 0 or np.linalg.norm(state - transmitted) > threshold
        if trigger:
            transmitted = state.copy()
        control = -(gain @ transmitted)
        states[time + 1] = state_matrix @ state + input_matrix @ control
        controls[time] = control
        triggers.append(trigger)
    return EventTriggeredControlResult(states, controls, tuple(triggers))


@dataclass(frozen=True)
class FastMarchingResult:
    arrival_times: np.ndarray
    accepted: np.ndarray


def fast_marching(
    speed: Sequence[Sequence[float]],
    sources: Sequence[tuple[int, int]],
    *,
    spacing: float = 1.0,
) -> FastMarchingResult:
    """Solve |grad T| F = 1 on a 2-D Cartesian grid.

    Positive speed cells are traversable; zero-speed cells are obstacles. The
    first-order upwind update is the standard isotropic Fast Marching method.
    """

    velocity = np.asarray(speed, dtype=np.float64)
    if velocity.ndim != 2 or not velocity.size:
        raise ValueError("Fast Marching speed must be a non-empty 2-D grid")
    if np.any(~np.isfinite(velocity)) or np.any(velocity < 0.0):
        raise ValueError("Fast Marching speed must be finite and non-negative")
    if not isfinite(spacing) or spacing <= 0.0:
        raise ValueError("Fast Marching spacing must be positive and finite")
    source_cells = tuple(dict.fromkeys((int(row), int(column)) for row, column in sources))
    if not source_cells:
        raise ValueError("Fast Marching needs at least one source")
    rows, columns = velocity.shape
    if any(
        row < 0
        or row >= rows
        or column < 0
        or column >= columns
        or velocity[row, column] <= 0.0
        for row, column in source_cells
    ):
        raise ValueError("Fast Marching source is outside traversable space")

    arrival = np.full((rows, columns), np.inf, dtype=np.float64)
    accepted = np.zeros((rows, columns), dtype=bool)
    heap: list[tuple[float, int, int]] = []

    def neighbors(row: int, column: int):
        for next_row, next_column in (
            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
        ):
            if 0 <= next_row < rows and 0 <= next_column < columns:
                yield next_row, next_column

    def accepted_time(row: int, column: int) -> float:
        if 0 <= row < rows and 0 <= column < columns and accepted[row, column]:
            return float(arrival[row, column])
        return float("inf")

    def update(row: int, column: int) -> float:
        horizontal = min(
            accepted_time(row, column - 1), accepted_time(row, column + 1)
        )
        vertical = min(accepted_time(row - 1, column), accepted_time(row + 1, column))
        step = spacing / velocity[row, column]
        if not isfinite(horizontal):
            return vertical + step
        if not isfinite(vertical):
            return horizontal + step
        low, high = sorted((horizontal, vertical))
        if high - low >= step:
            return low + step
        discriminant = max(0.0, 2.0 * step * step - (high - low) ** 2)
        return 0.5 * (low + high + sqrt(discriminant))

    for row, column in source_cells:
        arrival[row, column] = 0.0
        heappush(heap, (0.0, row, column))
    while heap:
        time, row, column = heappop(heap)
        if accepted[row, column] or time > arrival[row, column] + 1e-12:
            continue
        accepted[row, column] = True
        for next_row, next_column in neighbors(row, column):
            if accepted[next_row, next_column] or velocity[next_row, next_column] <= 0.0:
                continue
            candidate = update(next_row, next_column)
            if candidate + 1e-12 < arrival[next_row, next_column]:
                arrival[next_row, next_column] = candidate
                heappush(heap, (candidate, next_row, next_column))
    return FastMarchingResult(arrival, accepted)
