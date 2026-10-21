"""Bounded lattice MFG and quantum-field priors for every battle stage.

The controller builds a rolling graph from native legal actions.  It never
creates an action and it has no chapter-specific branches, so the common
runtime policy can use it for current and future stages without duplicating
scenario configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping, Sequence

import numpy as np

from rl.discrete_geometry import RegionAnalysis
from rl.lattice_geometry import Cell, LatticeCoordinate
from rl.lattice_mfg import LatticeMFG, LatticeMFGConfig
from rl.quantum_lattice_field import BosonicLatticeConfig, BosonicLatticeField
from rl.random_geometry import RandomGeometryStatistics


Action = Mapping[str, Any]
Unit = Mapping[str, Any]


def _cell(item: Mapping[str, Any]) -> Cell:
    return int(item["x"]), int(item["y"])


def _same_side(left: int, right: int) -> bool:
    if left == right:
        return True
    return bool(left & 0x03) and bool(right & 0x03)


@dataclass(frozen=True)
class RuntimeLatticeFieldConfig:
    """Hard bounds for predictable per-decision runtime on large maps."""

    mfg_horizon: int = 3
    mfg_max_cells: int = 160
    mfg_max_iterations: int = 40
    quantum_max_cells: int = 6
    quantum_max_dimension: int = 64
    quantum_max_regions: int = 24
    quantum_delta_time: float = 0.55
    prior_clip: float = 3.0

    def __post_init__(self) -> None:
        if self.mfg_horizon <= 0 or self.mfg_max_cells <= 0:
            raise ValueError("MFG runtime bounds must be positive")
        if self.mfg_max_iterations <= 0:
            raise ValueError("MFG iteration bound must be positive")
        if (
            self.quantum_max_cells <= 0
            or self.quantum_max_dimension <= 0
            or self.quantum_max_regions <= 0
        ):
            raise ValueError("quantum runtime bounds must be positive")
        if self.quantum_delta_time < 0.0 or self.prior_clip <= 0.0:
            raise ValueError("field time and prior clip must be valid")


@dataclass(frozen=True)
class RuntimeLatticeFieldResult:
    mfg_priors: Mapping[int, float]
    quantum_priors: Mapping[int, float]
    active_cells: int
    omitted_cells: int
    mfg_converged: bool
    mfg_residual: float
    quantum_regions: int
    quantum_max_dimension: int
    articulation_cells: int
    formation_spacing: float


class UniversalLatticeFieldController:
    """Construct bounded field priors from the live native action surface."""

    def __init__(self, config: RuntimeLatticeFieldConfig | None = None) -> None:
        self.config = config or RuntimeLatticeFieldConfig()
        self.last_result: RuntimeLatticeFieldResult | None = None
        self._topology_signature: tuple[int, int, tuple[bool, ...]] | None = None
        self._articulation_points: frozenset[Cell] = frozenset()

    def reset(self) -> None:
        self.last_result = None
        self._topology_signature = None
        self._articulation_points = frozenset()

    def priors(
        self,
        actions: Sequence[Action],
        units: Sequence[Unit],
        width: int,
        height: int,
        *,
        movement_costs: Mapping[int, Sequence[int]] | None = None,
    ) -> RuntimeLatticeFieldResult:
        if not actions:
            raise ValueError("lattice field controller needs legal actions")
        if width <= 0 or height <= 0:
            raise ValueError("lattice field controller needs positive map dimensions")
        by_id = {
            int(unit["id"]): unit
            for unit in units
            if not bool(unit.get("dead", False))
        }
        ready_ids = tuple(sorted({int(action["unit"]) for action in actions}))
        missing = [unit_id for unit_id in ready_ids if unit_id not in by_id]
        if missing:
            raise ValueError(f"actions reference unknown units: {missing}")
        acting_force = int(by_id[ready_ids[0]]["force"])
        opponents = tuple(
            unit
            for unit in by_id.values()
            if not _same_side(int(unit["force"]), acting_force)
        )
        selected_cells, omitted = self._active_cells(
            actions,
            by_id,
            ready_ids,
            opponents,
        )
        edges = self._edge_costs(
            actions,
            by_id,
            selected_cells,
            width,
            height,
            movement_costs or {},
        )
        articulation = self._discrete_topology(
            ready_ids,
            width,
            height,
            movement_costs or {},
        )
        friendly_positions = tuple(_cell(by_id[unit_id]) for unit_id in ready_ids)
        spacing = RandomGeometryStatistics.nearest_neighbor_summary(
            friendly_positions,
            LatticeCoordinate.manhattan,
        )["mean"]
        congestion_weight = 0.6
        if isfinite(spacing):
            congestion_weight += 0.8 / (1.0 + spacing)
        config = LatticeMFGConfig(
            horizon=self.config.mfg_horizon,
            temperature=0.45,
            congestion_weight=congestion_weight,
            congestion_power=1.0,
            relaxation=0.55,
            tolerance=1e-5,
            max_iterations=self.config.mfg_max_iterations,
        )
        base_capacity = max(0.2, 1.0 / max(1, len(ready_ids)))
        capacities = {
            cell: (
                max(0.1, 0.5 * base_capacity)
                if cell in articulation
                else base_capacity
            )
            for cell in selected_cells
        }
        model = LatticeMFG(
            selected_cells,
            edge_costs=edges,
            capacities=capacities,
            config=config,
        )
        initial: dict[Cell, float] = {}
        for unit_id in ready_ids:
            position = _cell(by_id[unit_id])
            initial[position] = initial.get(position, 0.0) + 1.0
        terminal = {
            cell: self._terminal_cost(cell, opponents, width, height)
            for cell in selected_cells
        }
        result = model.solve(initial, terminal)
        raw_mfg = result.action_priors(actions, units)
        mfg_priors = self._normalize(raw_mfg, actions)
        quantum_priors, regions, maximum_dimension = self._quantum_priors(
            actions,
            by_id,
            ready_ids,
            result.density(min(1, self.config.mfg_horizon)),
            mfg_priors,
        )
        output = RuntimeLatticeFieldResult(
            mfg_priors=mfg_priors,
            quantum_priors=quantum_priors,
            active_cells=len(selected_cells),
            omitted_cells=omitted,
            mfg_converged=result.converged,
            mfg_residual=result.fixed_point_residual,
            quantum_regions=regions,
            quantum_max_dimension=maximum_dimension,
            articulation_cells=len(articulation),
            formation_spacing=float(spacing),
        )
        self.last_result = output
        return output

    def _discrete_topology(
        self,
        ready_ids: Sequence[int],
        width: int,
        height: int,
        movement_costs: Mapping[int, Sequence[int]],
    ) -> frozenset[Cell]:
        costs = next(
            (
                movement_costs[unit_id]
                for unit_id in ready_ids
                if len(movement_costs.get(unit_id, ())) == width * height
            ),
            None,
        )
        if costs is None:
            return frozenset()
        passable = tuple(int(cost) < 255 for cost in costs)
        signature = width, height, passable
        if signature != self._topology_signature:
            cells = (
                (index % width, index // width)
                for index, traversable in enumerate(passable)
                if traversable
            )
            self._articulation_points = RegionAnalysis.articulation_points(cells)
            self._topology_signature = signature
        return self._articulation_points

    def _active_cells(
        self,
        actions: Sequence[Action],
        by_id: Mapping[int, Unit],
        ready_ids: Sequence[int],
        opponents: Sequence[Unit],
    ) -> tuple[tuple[Cell, ...], int]:
        mandatory = {_cell(by_id[unit_id]) for unit_id in ready_ids}
        grouped: dict[int, list[Cell]] = {unit_id: [] for unit_id in ready_ids}
        for action in actions:
            unit_id = int(action["unit"])
            destination = _cell(action)
            if destination not in grouped[unit_id]:
                grouped[unit_id].append(destination)
        enemy_cells = tuple(_cell(unit) for unit in opponents)

        def rank(unit_id: int, destination: Cell) -> tuple[float, int, int, int]:
            enemy_distance = min(
                (
                    LatticeCoordinate.manhattan(destination, enemy)
                    for enemy in enemy_cells
                ),
                default=0,
            )
            own_distance = LatticeCoordinate.manhattan(
                _cell(by_id[unit_id]), destination
            )
            return float(enemy_distance), own_distance, destination[1], destination[0]

        for unit_id in ready_ids:
            grouped[unit_id].sort(key=lambda cell: rank(unit_id, cell))
        selected: set[Cell] = set()
        for unit_id in ready_ids:
            selected.add(_cell(by_id[unit_id]))
            if len(selected) >= self.config.mfg_max_cells:
                break
        cursors = {unit_id: 0 for unit_id in ready_ids}
        while len(selected) < self.config.mfg_max_cells:
            progressed = False
            for unit_id in ready_ids:
                if _cell(by_id[unit_id]) not in selected:
                    continue
                candidates = grouped[unit_id]
                while (
                    cursors[unit_id] < len(candidates)
                    and candidates[cursors[unit_id]] in selected
                ):
                    cursors[unit_id] += 1
                if cursors[unit_id] >= len(candidates):
                    continue
                selected.add(candidates[cursors[unit_id]])
                cursors[unit_id] += 1
                progressed = True
                if len(selected) >= self.config.mfg_max_cells:
                    break
            if not progressed:
                break
        all_cells = mandatory | {_cell(action) for action in actions}
        return tuple(sorted(selected, key=lambda cell: (cell[1], cell[0]))), (
            len(all_cells) - len(selected)
        )

    @staticmethod
    def _edge_costs(
        actions: Sequence[Action],
        by_id: Mapping[int, Unit],
        cells: Sequence[Cell],
        width: int,
        height: int,
        movement_costs: Mapping[int, Sequence[int]],
    ) -> dict[tuple[Cell, Cell], float]:
        valid = set(cells)
        edges: dict[tuple[Cell, Cell], float] = {}
        for source in cells:
            for target in LatticeCoordinate.neighbors4(source):
                if target in valid:
                    edges[(source, target)] = 1.0
        for action in actions:
            unit_id = int(action["unit"])
            source = _cell(by_id[unit_id])
            target = _cell(action)
            if source not in valid or target not in valid or source == target:
                continue
            distance = LatticeCoordinate.manhattan(source, target)
            costs = movement_costs.get(unit_id)
            if costs is not None and len(costs) == width * height:
                target_cost = int(costs[target[1] * width + target[0]])
                step_cost = max(1.0, float(target_cost))
            else:
                step_cost = 1.0
            move = max(1, int(by_id[unit_id].get("move", 1)))
            edges[(source, target)] = max(0.25, distance * step_cost / move)
        return edges

    @staticmethod
    def _terminal_cost(
        cell: Cell,
        opponents: Sequence[Unit],
        width: int,
        height: int,
    ) -> float:
        if not opponents:
            return 0.0
        distance = min(
            LatticeCoordinate.manhattan(cell, _cell(enemy))
            for enemy in opponents
        )
        scale = max(1, width + height - 2)
        threat = 0.0
        for enemy in opponents:
            relative = cell[0] - int(enemy["x"]), cell[1] - int(enemy["y"])
            offsets = {
                (int(offset[0]), int(offset[1]))
                for offset in enemy.get("attack_offsets", ())
            }
            if relative in offsets:
                threat += max(0.5, float(enemy.get("atk", 100)) / 200.0)
        return 4.0 * distance / scale + threat

    def _quantum_priors(
        self,
        actions: Sequence[Action],
        by_id: Mapping[int, Unit],
        ready_ids: Sequence[int],
        density: Mapping[Cell, float],
        mfg_priors: Mapping[int, float],
    ) -> tuple[dict[int, float], int, int]:
        grouped: dict[int, list[Action]] = {unit_id: [] for unit_id in ready_ids}
        for action in actions:
            grouped[int(action["unit"])].append(action)
        raw: dict[int, float] = {}
        regions = 0
        maximum_dimension = 0
        quantum_ids = sorted(
            ready_ids,
            key=lambda unit_id: (-len(grouped[unit_id]), unit_id),
        )[: self.config.quantum_max_regions]
        for unit_id in quantum_ids:
            current = _cell(by_id[unit_id])
            candidates = sorted(
                grouped[unit_id],
                key=lambda action: (
                    -float(mfg_priors.get(int(action["index"]), 0.0)),
                    int(action["index"]),
                ),
            )
            cells = [current]
            for action in candidates:
                destination = _cell(action)
                if destination not in cells:
                    cells.append(destination)
                if len(cells) >= self.config.quantum_max_cells:
                    break
            occupation = tuple(1 if index == 0 else 0 for index in range(len(cells)))
            edges = tuple(
                (current, destination)
                for destination in cells[1:]
            )
            field = BosonicLatticeField(
                cells,
                {occupation: 1.0},
                edges=edges,
                config=BosonicLatticeConfig(
                    max_occupancy=1,
                    hopping=1.0,
                    interaction=0.0,
                    max_dimension=self.config.quantum_max_dimension,
                ),
            )
            endpoint_scores: dict[Cell, list[float]] = {}
            for action in candidates:
                destination = _cell(action)
                if destination in field.index:
                    endpoint_scores.setdefault(destination, []).append(
                        float(mfg_priors.get(int(action["index"]), 0.0))
                    )
            potentials = {
                cell: -sum(values) / len(values)
                for cell, values in endpoint_scores.items()
            }
            field.evolve(
                self.config.quantum_delta_time,
                potentials=potentials,
                mfg_density=density,
                density_coupling=0.5,
                dephasing=0.05,
            )
            raw.update(field.action_priors(grouped[unit_id]))
            regions += 1
            maximum_dimension = max(maximum_dimension, field.dimension)
        return self._normalize(raw, actions), regions, maximum_dimension

    def _normalize(
        self,
        priors: Mapping[int, float],
        actions: Sequence[Action],
    ) -> dict[int, float]:
        grouped: dict[int, list[int]] = {}
        action_units = {
            int(action["index"]): int(action["unit"])
            for action in actions
        }
        for index, value in priors.items():
            numeric = float(value)
            if int(index) not in action_units or not isfinite(numeric):
                continue
            grouped.setdefault(action_units[int(index)], []).append(int(index))
        normalized: dict[int, float] = {}
        for indexes in grouped.values():
            values = np.asarray([float(priors[index]) for index in indexes])
            centered = values - float(values.mean())
            scale = float(centered.std())
            if scale > 1e-8:
                centered /= scale
            centered = np.clip(
                centered,
                -self.config.prior_clip,
                self.config.prior_clip,
            )
            normalized.update(
                (index, float(value))
                for index, value in zip(indexes, centered)
            )
        return normalized
