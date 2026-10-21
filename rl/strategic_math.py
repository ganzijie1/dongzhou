"""Stateful mathematical advisor for legal tactical action priors.

The advisor never creates actions.  It combines Bayesian beliefs, CVaR,
supply-flow redundancy, Pareto filtering, optimal transport, graph spectra,
and one-step robust payoffs into centered priors for native legal actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence

from rl.belief_risk import (
    BayesianGridTracker,
    bernoulli_loss_distribution,
    conditional_value_at_risk,
)
from rl.decision_math import (
    SpectralGraph,
    integral_transport_assignment,
    optimal_transport,
    pareto_front,
    solve_zero_sum_game,
)
from rl.lattice_geometry import Cell, LatticeCoordinate
from rl.strategic_flow import CapacityNetwork
from rl.tactical_policy import attack_offsets


Action = Mapping[str, Any]
Unit = Mapping[str, Any]


def _position(item: Mapping[str, Any]) -> Cell:
    return int(item["x"]), int(item["y"])


def _same_side(left: int, right: int) -> bool:
    return left == right or (bool(left & 0x03) and bool(right & 0x03))


@dataclass(frozen=True)
class StrategicMathConfig:
    cvar_alpha: float = 0.8
    belief_stay_probability: float = 0.25
    risk_weight: float = 1.0
    pareto_bonus: float = 1.0
    supply_weight: float = 0.35
    transport_weight: float = 0.5
    spectral_weight: float = 0.25
    robust_weight: float = 0.5
    game_strategy_weight: float = 1.0
    max_risk_events: int = 12
    max_flow_cells: int = 256
    max_spectral_cells: int = 256

    def __post_init__(self) -> None:
        if not 0.0 <= self.cvar_alpha < 1.0:
            raise ValueError("cvar_alpha must be in [0, 1)")
        if not 0.0 <= self.belief_stay_probability <= 1.0:
            raise ValueError("belief_stay_probability must be in [0, 1]")
        weights = (
            self.risk_weight,
            self.pareto_bonus,
            self.supply_weight,
            self.transport_weight,
            self.spectral_weight,
            self.robust_weight,
            self.game_strategy_weight,
        )
        if any(not isfinite(value) or value < 0.0 for value in weights):
            raise ValueError("strategic math weights must be finite and non-negative")
        if self.max_risk_events <= 0:
            raise ValueError("max_risk_events must be positive")


@dataclass(frozen=True)
class StrategicMathDiagnostics:
    priors: Mapping[int, float]
    components: Mapping[int, Mapping[str, float]]
    pareto_actions: frozenset[int]
    enemy_beliefs: Mapping[int, Mapping[Cell, float]]
    transport_targets: Mapping[int, Cell]
    algebraic_connectivity: float | None
    game_strategies: Mapping[int, Mapping[int, float]] = field(default_factory=dict)
    supply_cut_edges: Mapping[Cell, tuple[tuple[Any, Any], ...]] = field(
        default_factory=dict
    )


class StrategicMathAdvisor:
    def __init__(self, config: StrategicMathConfig | None = None) -> None:
        self.config = config or StrategicMathConfig()
        self.beliefs = BayesianGridTracker()
        self.enemy_profiles: dict[int, dict[str, Any]] = {}
        self.previous_ready: frozenset[int] = frozenset()
        self.previous_force: int | None = None
        self._spectral_cache: dict[
            frozenset[Cell], tuple[dict[Cell, float], float]
        ] = {}
        self._network_cache: dict[frozenset[Cell], CapacityNetwork] = {}
        self._supply_cache: dict[
            tuple[frozenset[Cell], tuple[Cell, ...], Cell],
            tuple[float, tuple[tuple[Any, Any], ...]],
        ] = {}

    def reset(self) -> None:
        self.beliefs.reset()
        self.enemy_profiles.clear()
        self.previous_ready = frozenset()
        self.previous_force = None
        self._spectral_cache.clear()
        self._network_cache.clear()
        self._supply_cache.clear()

    @staticmethod
    def _adjacency(cells: Iterable[Cell]) -> dict[Cell, tuple[Cell, ...]]:
        region = set(cells)
        return {
            cell: tuple(
                neighbor
                for neighbor in LatticeCoordinate.neighbors4(cell)
                if neighbor in region
            )
            for cell in region
        }

    def _update_beliefs(
        self,
        units: Sequence[Unit],
        acting_force: int,
        ready: frozenset[int],
        passable: set[Cell],
        visible_cells: Iterable[Cell],
    ) -> None:
        new_turn = (
            self.previous_force != acting_force
            or not ready.issubset(self.previous_ready)
        )
        live_opponents = [
            unit for unit in units
            if not bool(unit.get("dead", False))
            and not _same_side(int(unit["force"]), acting_force)
        ]
        visible = {
            int(unit["id"]): _position(unit)
            for unit in live_opponents
            if bool(unit.get("visible", not bool(unit.get("hidden", False))))
        }
        hidden_ids = set(self.beliefs.beliefs) - set(visible)
        if new_turn and hidden_ids:
            self.beliefs.predict(
                self._adjacency(passable),
                unit_ids=hidden_ids,
                stay_probability=self.config.belief_stay_probability,
            )
        for unit in live_opponents:
            unit_id = int(unit["id"])
            if unit_id in visible:
                self.enemy_profiles[unit_id] = dict(unit)
        for unit in units:
            if bool(unit.get("dead", False)):
                unit_id = int(unit["id"])
                self.beliefs.remove(unit_id)
                self.enemy_profiles.pop(unit_id, None)
        self.beliefs.update(visible, visible_cells=visible_cells)
        self.previous_force = acting_force
        self.previous_ready = ready

    def _risk_distribution(self, destination: Cell) -> tuple[tuple[float, ...], tuple[float, ...]]:
        events: list[tuple[float, float]] = []
        for unit_id, belief in self.beliefs.beliefs.items():
            profile = self.enemy_profiles.get(unit_id)
            if profile is None:
                continue
            offsets = set(attack_offsets(profile))
            probability = sum(
                mass for cell, mass in belief.probabilities.items()
                if (destination[0] - cell[0], destination[1] - cell[1]) in offsets
            )
            if probability <= 1e-12:
                continue
            loss = max(1.0, float(profile.get("atk", 100.0)))
            events.append((min(1.0, probability), loss))
        events.sort(key=lambda item: item[0] * item[1], reverse=True)
        if len(events) > self.config.max_risk_events:
            retained = events[: self.config.max_risk_events]
            residual = sum(chance * loss for chance, loss in events[self.config.max_risk_events :])
            events = retained + ([(1.0, residual)] if residual > 0.0 else [])
        return bernoulli_loss_distribution(events)

    @staticmethod
    def _transport_targets(
        friendlies: Sequence[Unit],
        targets: Sequence[Cell] | Mapping[int, Cell] | None,
    ) -> dict[int, Cell]:
        if targets is None:
            return {}
        if isinstance(targets, Mapping):
            return {
                int(unit_id): (int(cell[0]), int(cell[1]))
                for unit_id, cell in targets.items()
            }
        units = [int(unit["id"]) for unit in friendlies]
        cells = [(int(cell[0]), int(cell[1])) for cell in targets]
        if len(units) != len(cells) or not units:
            raise ValueError("formation target count must match friendly unit count")
        current = {int(unit["id"]): _position(unit) for unit in friendlies}
        indexed_targets = {(index, cell): 1.0 for index, cell in enumerate(cells)}
        result = optimal_transport(
            {unit_id: 1.0 for unit_id in units},
            indexed_targets,
            lambda unit_id, target: float(
                LatticeCoordinate.manhattan(current[unit_id], target[1])
            ),
        )
        assignment = integral_transport_assignment(result)
        return {unit_id: target[1] for unit_id, target in assignment.items()}

    @staticmethod
    def _center_by_unit(
        values: Mapping[int, float], actions: Sequence[Action]
    ) -> dict[int, float]:
        grouped: dict[int, list[int]] = {}
        for action in actions:
            grouped.setdefault(int(action["unit"]), []).append(int(action["index"]))
        centered: dict[int, float] = {}
        for indices in grouped.values():
            raw = [float(values.get(index, 0.0)) for index in indices]
            mean = sum(raw) / len(raw)
            variance = sum((value - mean) ** 2 for value in raw) / len(raw)
            scale = max(1.0, variance**0.5)
            centered.update(
                (index, (value - mean) / scale)
                for index, value in zip(indices, raw)
            )
        return centered

    def action_priors(
        self,
        actions: Sequence[Action],
        units: Sequence[Unit],
        width: int,
        height: int,
        *,
        passable_cells: Iterable[Cell] | None = None,
        visible_cells: Iterable[Cell] = (),
        supply_sites: Iterable[Cell] = (),
        formation_targets: Sequence[Cell] | Mapping[int, Cell] | None = None,
        opponent_payoffs: Mapping[int, Sequence[float]] | None = None,
    ) -> StrategicMathDiagnostics:
        if not actions:
            raise ValueError("strategic math needs legal actions")
        by_id = {int(unit["id"]): unit for unit in units if not bool(unit.get("dead", False))}
        acting_force = int(by_id[int(actions[0]["unit"])]["force"])
        ready = frozenset(int(action["unit"]) for action in actions)
        passable = set(passable_cells or (
            (x, y) for y in range(height) for x in range(width)
        ))
        if not passable:
            raise ValueError("strategic math needs at least one passable cell")
        self._update_beliefs(
            units, acting_force, ready, passable, visible_cells
        )
        friendlies = [
            unit for unit in by_id.values()
            if _same_side(int(unit["force"]), acting_force)
        ]
        opponents = [
            unit for unit in by_id.values()
            if not _same_side(int(unit["force"]), acting_force)
        ]
        targets = self._transport_targets(friendlies, formation_targets)

        spectral_scores: dict[Cell, float] = {}
        algebraic_connectivity: float | None = None
        map_key = frozenset(passable)
        if 1 < len(passable) <= self.config.max_spectral_cells:
            cached_spectrum = self._spectral_cache.get(map_key)
            if cached_spectrum is None:
                spectral = SpectralGraph.from_grid(tuple(passable)).analyze()
                maximum = max(
                    (abs(value) for value in spectral.fiedler_vector.values()),
                    default=0.0,
                )
                scores = (
                    {
                        cell: 1.0 - abs(value) / maximum
                        for cell, value in spectral.fiedler_vector.items()
                    }
                    if maximum > 1e-12 else {}
                )
                cached_spectrum = (scores, spectral.algebraic_connectivity)
                self._spectral_cache[map_key] = cached_spectrum
            spectral_scores, algebraic_connectivity = cached_spectrum

        sites = tuple(dict.fromkeys((int(x), int(y)) for x, y in supply_sites if (int(x), int(y)) in passable))
        supply_scores: dict[Cell, float] = {}
        supply_cuts: dict[Cell, tuple[tuple[Any, Any], ...]] = {}
        if sites and len(passable) <= self.config.max_flow_cells:
            network = self._network_cache.get(map_key)
            if network is None:
                network = CapacityNetwork.from_grid(passable)
                self._network_cache[map_key] = network
            destinations = {_position(action) for action in actions}
            for destination in destinations:
                if destination not in passable:
                    continue
                cache_key = (map_key, sites, destination)
                cached_flow = self._supply_cache.get(cache_key)
                if cached_flow is None:
                    result = network.multi_source_flow(
                        {site: 4.0 for site in sites}, {destination: 16.0}
                    )
                    cached_flow = (result.value, result.cut_edges)
                    self._supply_cache[cache_key] = cached_flow
                supply_scores[destination], supply_cuts[destination] = cached_flow

        components: dict[int, dict[str, float]] = {}
        objectives: dict[int, tuple[float, float, float, float]] = {}
        risk_distributions: dict[int, tuple[tuple[float, ...], tuple[float, ...]]] = {}
        for action in actions:
            action_index = int(action["index"])
            destination = _position(action)
            losses, probabilities = self._risk_distribution(destination)
            risk_distributions[action_index] = (losses, probabilities)
            risk = conditional_value_at_risk(
                losses, self.config.cvar_alpha, probabilities
            )
            damage = float(action.get("expected_damage", action.get("damage", 0.0)))
            enemy_distance = min(
                (
                    LatticeCoordinate.manhattan(destination, _position(enemy))
                    for enemy in opponents
                    if bool(enemy.get("visible", not bool(enemy.get("hidden", False))))
                ),
                default=0,
            )
            supply = supply_scores.get(destination, 0.0)
            objectives[action_index] = (
                damage,
                -risk,
                -float(enemy_distance),
                supply,
            )
            payoff_values = tuple((opponent_payoffs or {}).get(action_index, ()))
            robust = min(map(float, payoff_values)) if payoff_values else damage - max(losses)
            transport = 0.0
            target = targets.get(int(action["unit"]))
            if target is not None:
                transport = -float(LatticeCoordinate.manhattan(destination, target))
            components[action_index] = {
                "cvar": risk,
                "supply_flow": supply,
                "transport": transport,
                "spectral_separator": spectral_scores.get(destination, 0.0),
                "robust_worst_case": robust,
            }

        pareto_actions: set[int] = set()
        game_strategies: dict[int, dict[int, float]] = {}
        for unit_id in ready:
            unit_actions = [
                action for action in actions if int(action["unit"]) == unit_id
            ]
            candidates = {
                int(action["index"]): objectives[int(action["index"])]
                for action in unit_actions
            }
            pareto_actions.update(map(int, pareto_front(candidates)))
            response_rows = [
                tuple((opponent_payoffs or {}).get(int(action["index"]), ()))
                for action in unit_actions
            ]
            if (
                response_rows
                and response_rows[0]
                and all(len(row) == len(response_rows[0]) for row in response_rows)
            ):
                equilibrium = solve_zero_sum_game(response_rows)
                game_strategies[unit_id] = {
                    int(action["index"]): probability
                    for action, probability in zip(unit_actions, equilibrium.row_strategy)
                }
                for action, probability in zip(unit_actions, equilibrium.row_strategy):
                    components[int(action["index"])]["robust_mixed_probability"] = probability

        raw: dict[int, float] = {}
        for action in actions:
            action_index = int(action["index"])
            part = components[action_index]
            pareto = self.config.pareto_bonus if action_index in pareto_actions else 0.0
            part["pareto"] = pareto
            mixed = part.get("robust_mixed_probability", 0.0)
            raw[action_index] = (
                -self.config.risk_weight * part["cvar"]
                + pareto
                + self.config.supply_weight * part["supply_flow"]
                + self.config.transport_weight * part["transport"]
                + self.config.spectral_weight * part["spectral_separator"]
                + self.config.robust_weight * part["robust_worst_case"]
                + self.config.game_strategy_weight * mixed
            )
        priors = self._center_by_unit(raw, actions)
        return StrategicMathDiagnostics(
            priors,
            components,
            frozenset(pareto_actions),
            {
                unit_id: dict(belief.probabilities)
                for unit_id, belief in self.beliefs.beliefs.items()
            },
            targets,
            algebraic_connectivity,
            game_strategies,
            supply_cuts,
        )
