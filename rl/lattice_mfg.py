"""Finite-state mean field games on tactical lattice graphs.

The solver uses a backward entropy-regularized Bellman pass and a forward
Kolmogorov pass.  It is deliberately independent of rendering and native unit
mutation: its output is a density flow and action prior over already legal
actions, which the joint MAPF planner may consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Any, Mapping, Sequence

import numpy as np

from rl.lattice_geometry import Cell, LatticeCoordinate


class LatticeMFGError(ValueError):
    """Raised when a lattice MFG violates a probability or graph invariant."""


@dataclass(frozen=True)
class LatticeMFGConfig:
    horizon: int = 8
    temperature: float = 0.35
    congestion_weight: float = 2.0
    congestion_power: float = 1.0
    relaxation: float = 0.45
    tolerance: float = 1e-7
    max_iterations: int = 250
    allow_wait: bool = True

    def __post_init__(self) -> None:
        if self.horizon <= 0:
            raise LatticeMFGError("horizon must be positive")
        if self.temperature < 0.0:
            raise LatticeMFGError("temperature cannot be negative")
        if self.congestion_weight < 0.0 or self.congestion_power <= 0.0:
            raise LatticeMFGError("congestion parameters must be non-negative")
        if not 0.0 < self.relaxation <= 1.0:
            raise LatticeMFGError("relaxation must be in (0, 1]")
        if self.tolerance <= 0.0 or self.max_iterations <= 0:
            raise LatticeMFGError("solver tolerance and iterations must be positive")


@dataclass(frozen=True)
class LatticeMFGResult:
    cells: tuple[Cell, ...]
    densities: np.ndarray
    values: np.ndarray
    policies: np.ndarray
    residuals: tuple[float, ...]
    converged: bool

    @property
    def iterations(self) -> int:
        return len(self.residuals)

    @property
    def fixed_point_residual(self) -> float:
        return self.residuals[-1] if self.residuals else 0.0

    def density(self, time: int) -> dict[Cell, float]:
        row = self.densities[int(time)]
        return {cell: float(row[index]) for index, cell in enumerate(self.cells)}

    def value(self, time: int) -> dict[Cell, float]:
        row = self.values[int(time)]
        return {cell: float(row[index]) for index, cell in enumerate(self.cells)}

    def edge_flow(self, time: int) -> dict[tuple[Cell, Cell], float]:
        index = int(time)
        flow = self.densities[index, :, None] * self.policies[index]
        return {
            (source, target): float(flow[row, column])
            for row, source in enumerate(self.cells)
            for column, target in enumerate(self.cells)
            if flow[row, column] > 0.0
        }

    def action_priors(
        self,
        actions: Sequence[Mapping[str, Any]],
        units: Sequence[Mapping[str, Any]],
        *,
        time: int = 0,
    ) -> dict[int, float]:
        """Convert endpoint continuation values to centered per-unit priors.

        Native move actions may cross several lattice edges in one turn, while
        an MFG policy step only contains adjacent transitions.  Endpoint value
        therefore provides the consistent prior for every native-legal landing
        cell; MAPF remains responsible for the intervening path.
        """
        if not 0 <= time < self.policies.shape[0]:
            raise LatticeMFGError("action-prior time is outside the solved horizon")
        cell_index = {cell: index for index, cell in enumerate(self.cells)}
        by_id = {int(unit["id"]): unit for unit in units}
        grouped: dict[int, list[Mapping[str, Any]]] = {}
        for action in actions:
            unit_id = int(action["unit"])
            if unit_id in by_id:
                grouped.setdefault(unit_id, []).append(action)
        priors: dict[int, float] = {}
        for unit_id, candidates in grouped.items():
            unit = by_id[unit_id]
            if (int(unit["x"]), int(unit["y"])) not in cell_index:
                continue
            raw: list[float] = []
            valid: list[Mapping[str, Any]] = []
            continuation_time = min(time + 1, self.values.shape[0] - 1)
            for action in candidates:
                target = cell_index.get((int(action["x"]), int(action["y"])))
                if target is None:
                    continue
                raw.append(-float(self.values[continuation_time, target]))
                valid.append(action)
            if not valid:
                continue
            center = sum(raw) / len(raw)
            priors.update(
                (int(action["index"]), score - center)
                for action, score in zip(valid, raw)
            )
        return priors


class LatticeMFG:
    """Entropy-regularized MFG on a finite directed tactical graph."""

    def __init__(
        self,
        cells: Sequence[Cell],
        *,
        edge_costs: Mapping[tuple[Cell, Cell], float] | None = None,
        capacities: Mapping[Cell, float] | None = None,
        config: LatticeMFGConfig | None = None,
    ) -> None:
        self.config = config or LatticeMFGConfig()
        self.cells = tuple(cells)
        if not self.cells or len(set(self.cells)) != len(self.cells):
            raise LatticeMFGError("MFG cells must be non-empty and unique")
        self.index = {cell: position for position, cell in enumerate(self.cells)}
        self.dimension = len(self.cells)
        self.edge_costs = self._build_edges(edge_costs)
        self.targets = tuple(
            tuple(
                self.index[target]
                for source, target in self.edge_costs
                if source == cell
            )
            for cell in self.cells
        )
        if any(not targets for targets in self.targets):
            raise LatticeMFGError("every MFG cell needs at least one outgoing action")
        self.capacities = np.asarray(
            [float((capacities or {}).get(cell, 1.0)) for cell in self.cells],
            dtype=np.float64,
        )
        if np.any(~np.isfinite(self.capacities)) or np.any(self.capacities <= 0.0):
            raise LatticeMFGError("cell capacities must be finite and positive")

    @classmethod
    def from_grid(
        cls,
        width: int,
        height: int,
        *,
        movement_costs: Sequence[int] | None = None,
        blocked_cost: int = 255,
        config: LatticeMFGConfig | None = None,
    ) -> "LatticeMFG":
        if width <= 0 or height <= 0:
            raise LatticeMFGError("grid dimensions must be positive")
        costs = list(movement_costs or [1] * (width * height))
        if len(costs) != width * height:
            raise LatticeMFGError("movement-cost grid has invalid dimensions")
        cells = tuple(
            (index % width, index // width)
            for index, cost in enumerate(costs)
            if int(cost) < blocked_cost
        )
        valid = set(cells)
        edges: dict[tuple[Cell, Cell], float] = {}
        for source in cells:
            for target in LatticeCoordinate.neighbors4(source):
                if target in valid:
                    target_cost = costs[target[1] * width + target[0]]
                    edges[(source, target)] = max(1.0, float(target_cost))
        return cls(cells, edge_costs=edges, config=config)

    def solve(
        self,
        initial_density: Mapping[Cell, float] | Sequence[float] | np.ndarray,
        terminal_cost: Mapping[Cell, float] | Sequence[float] | np.ndarray,
        *,
        external_costs: Sequence[Mapping[Cell, float]] | np.ndarray | None = None,
        initial_guess: np.ndarray | None = None,
    ) -> LatticeMFGResult:
        initial = self._vector(initial_density, "initial density")
        if np.any(initial < 0.0) or float(initial.sum()) <= 0.0:
            raise LatticeMFGError("initial density must be non-negative with positive mass")
        initial /= float(initial.sum())
        terminal = self._vector(terminal_cost, "terminal cost")
        external = self._external_costs(external_costs)
        if initial_guess is None:
            density = np.repeat(initial[None, :], self.config.horizon + 1, axis=0)
        else:
            density = np.asarray(initial_guess, dtype=np.float64).copy()
            if density.shape != (self.config.horizon + 1, self.dimension):
                raise LatticeMFGError("initial density trajectory has invalid dimensions")
            density = self._normalize_trajectory(density, initial)

        residuals: list[float] = []
        converged = False
        values = np.zeros_like(density)
        policies = np.zeros((self.config.horizon, self.dimension, self.dimension))
        for _ in range(self.config.max_iterations):
            values, policies = self._backward(density, terminal, external)
            propagated = self._forward(initial, policies)
            residual = float(np.max(np.sum(np.abs(propagated - density), axis=1)))
            residuals.append(residual)
            density[1:] = (
                (1.0 - self.config.relaxation) * density[1:]
                + self.config.relaxation * propagated[1:]
            )
            density = self._normalize_trajectory(density, initial)
            if residual <= self.config.tolerance:
                converged = True
                break

        values, policies = self._backward(density, terminal, external)
        propagated = self._forward(initial, policies)
        final_residual = float(np.max(np.sum(np.abs(propagated - density), axis=1)))
        if not residuals or abs(final_residual - residuals[-1]) > 1e-15:
            residuals.append(final_residual)
        if final_residual <= self.config.tolerance:
            density = propagated
            converged = True
        self._validate_solution(density, policies)
        return LatticeMFGResult(
            self.cells,
            density.copy(),
            values.copy(),
            policies.copy(),
            tuple(residuals),
            converged,
        )

    def _build_edges(
        self,
        supplied: Mapping[tuple[Cell, Cell], float] | None,
    ) -> dict[tuple[Cell, Cell], float]:
        valid = set(self.cells)
        edges: dict[tuple[Cell, Cell], float] = {}
        if supplied is None:
            for source in self.cells:
                for target in LatticeCoordinate.neighbors4(source):
                    if target in valid:
                        edges[(source, target)] = 1.0
        else:
            for (source, target), cost in supplied.items():
                if source not in valid or target not in valid:
                    raise LatticeMFGError("edge references a cell outside the MFG graph")
                value = float(cost)
                if not isfinite(value) or value < 0.0:
                    raise LatticeMFGError("edge costs must be finite and non-negative")
                edges[(source, target)] = value
        if self.config.allow_wait:
            for cell in self.cells:
                edges.setdefault((cell, cell), 0.0)
        return edges

    def _vector(
        self,
        values: Mapping[Cell, float] | Sequence[float] | np.ndarray,
        label: str,
    ) -> np.ndarray:
        if isinstance(values, Mapping):
            result = np.asarray([float(values.get(cell, 0.0)) for cell in self.cells])
        else:
            result = np.asarray(values, dtype=np.float64)
        if result.shape != (self.dimension,) or np.any(~np.isfinite(result)):
            raise LatticeMFGError(f"{label} has invalid dimensions or values")
        return result.copy()

    def _external_costs(
        self,
        values: Sequence[Mapping[Cell, float]] | np.ndarray | None,
    ) -> np.ndarray:
        if values is None:
            return np.zeros((self.config.horizon, self.dimension), dtype=np.float64)
        if isinstance(values, np.ndarray):
            result = np.asarray(values, dtype=np.float64)
        else:
            result = np.asarray(
                [
                    [float(row.get(cell, 0.0)) for cell in self.cells]
                    for row in values
                ],
                dtype=np.float64,
            )
        if result.shape != (self.config.horizon, self.dimension):
            raise LatticeMFGError("external costs have invalid dimensions")
        if np.any(~np.isfinite(result)):
            raise LatticeMFGError("external costs must be finite")
        return result

    def _backward(
        self,
        density: np.ndarray,
        terminal: np.ndarray,
        external: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        horizon = self.config.horizon
        values = np.zeros((horizon + 1, self.dimension), dtype=np.float64)
        policies = np.zeros((horizon, self.dimension, self.dimension), dtype=np.float64)
        values[horizon] = terminal
        for time in range(horizon - 1, -1, -1):
            occupancy = np.maximum(0.0, density[time + 1] / self.capacities)
            congestion = self.config.congestion_weight * np.power(
                occupancy, self.config.congestion_power
            )
            for source, targets in enumerate(self.targets):
                source_cell = self.cells[source]
                q_values = np.asarray(
                    [
                        self.edge_costs[(source_cell, self.cells[target])]
                        + congestion[target]
                        + external[time, target]
                        + values[time + 1, target]
                        for target in targets
                    ],
                    dtype=np.float64,
                )
                if self.config.temperature == 0.0:
                    best = int(np.argmin(q_values))
                    probabilities = np.zeros(len(targets), dtype=np.float64)
                    probabilities[best] = 1.0
                    values[time, source] = float(q_values[best])
                else:
                    logits = -q_values / self.config.temperature
                    maximum = float(np.max(logits))
                    weights = np.exp(logits - maximum)
                    probabilities = weights / float(weights.sum())
                    values[time, source] = -self.config.temperature * (
                        maximum + log(float(weights.sum()))
                    )
                policies[time, source, list(targets)] = probabilities
        return values, policies

    @staticmethod
    def _forward(initial: np.ndarray, policies: np.ndarray) -> np.ndarray:
        horizon, dimension, _ = policies.shape
        density = np.zeros((horizon + 1, dimension), dtype=np.float64)
        density[0] = initial
        for time in range(horizon):
            density[time + 1] = density[time] @ policies[time]
        return density

    @staticmethod
    def _normalize_trajectory(density: np.ndarray, initial: np.ndarray) -> np.ndarray:
        result = np.maximum(density, 0.0)
        result[0] = initial
        for time in range(1, len(result)):
            mass = float(result[time].sum())
            if mass <= 0.0:
                raise LatticeMFGError("density trajectory lost all mass")
            result[time] /= mass
        return result

    @staticmethod
    def _validate_solution(density: np.ndarray, policies: np.ndarray) -> None:
        if np.any(density < -1e-10):
            raise LatticeMFGError("MFG density became negative")
        if not np.allclose(density.sum(axis=1), 1.0, atol=1e-8):
            raise LatticeMFGError("MFG density does not conserve mass")
        if np.any(policies < -1e-10):
            raise LatticeMFGError("MFG policy contains negative probability")
        if not np.allclose(policies.sum(axis=2), 1.0, atol=1e-8):
            raise LatticeMFGError("MFG policy rows must sum to one")


@dataclass(frozen=True)
class MultiPopulationMFGResult:
    populations: Mapping[str, LatticeMFGResult]
    residuals: tuple[float, ...]
    converged: bool


class MultiPopulationLatticeMFG:
    """Outer fixed point for asymmetric interactions between unit classes."""

    def __init__(
        self,
        models: Mapping[str, LatticeMFG],
        interactions: Mapping[tuple[str, str], float],
        *,
        relaxation: float = 0.5,
        tolerance: float = 1e-6,
        max_iterations: int = 80,
    ) -> None:
        if not models:
            raise LatticeMFGError("multi-population MFG needs at least one population")
        if not 0.0 < relaxation <= 1.0 or tolerance <= 0.0 or max_iterations <= 0:
            raise LatticeMFGError("invalid multi-population solver parameters")
        dimensions = {(model.cells, model.config.horizon) for model in models.values()}
        if len(dimensions) != 1:
            raise LatticeMFGError("all populations must share cells and horizon")
        self.models = dict(models)
        self.interactions = {key: float(value) for key, value in interactions.items()}
        self.relaxation = float(relaxation)
        self.tolerance = float(tolerance)
        self.max_iterations = int(max_iterations)

    def solve(
        self,
        initial_densities: Mapping[str, Mapping[Cell, float] | Sequence[float]],
        terminal_costs: Mapping[str, Mapping[Cell, float] | Sequence[float]],
    ) -> MultiPopulationMFGResult:
        names = tuple(self.models)
        guesses: dict[str, np.ndarray] = {}
        initial_vectors: dict[str, np.ndarray] = {}
        for name in names:
            model = self.models[name]
            initial = model._vector(initial_densities[name], f"{name} initial density")
            initial /= float(initial.sum())
            initial_vectors[name] = initial
            guesses[name] = np.repeat(
                initial[None, :], model.config.horizon + 1, axis=0
            )
        residuals: list[float] = []
        results: dict[str, LatticeMFGResult] = {}
        converged = False
        for _ in range(self.max_iterations):
            candidates: dict[str, LatticeMFGResult] = {}
            for name in names:
                model = self.models[name]
                external = np.zeros((model.config.horizon, model.dimension))
                for other in names:
                    coefficient = self.interactions.get((name, other), 0.0)
                    if coefficient:
                        external += coefficient * guesses[other][1:]
                candidates[name] = model.solve(
                    initial_vectors[name],
                    terminal_costs[name],
                    external_costs=external,
                    initial_guess=guesses[name],
                )
            residual = max(
                float(
                    np.max(
                        np.sum(
                            np.abs(candidates[name].densities - guesses[name]), axis=1
                        )
                    )
                )
                for name in names
            )
            residuals.append(residual)
            for name in names:
                guesses[name][1:] = (
                    (1.0 - self.relaxation) * guesses[name][1:]
                    + self.relaxation * candidates[name].densities[1:]
                )
            results = candidates
            if residual <= self.tolerance:
                converged = True
                break
        return MultiPopulationMFGResult(results, tuple(residuals), converged)
