"""All-stage runtime binding and hard-bound tests for lattice fields."""

from __future__ import annotations

from math import isfinite

import numpy as np

from rl.lattice_field_runtime import (
    RuntimeLatticeFieldConfig,
    UniversalLatticeFieldController,
)
from rl.runtime_policy import RuntimeBattlePolicy


def _unit(unit_id: int, force: int, x: int, y: int) -> dict:
    return {
        "id": unit_id,
        "force": force,
        "class": "Infantry",
        "x": x,
        "y": y,
        "attack_offsets": ((0, -1), (0, 1), (-1, 0), (1, 0)),
        "attack_min": 1,
        "attack_max": 1,
        "move": 5,
        "hp": 100,
        "max_hp": 100,
        "atk": 100,
        "done": False,
        "dead": False,
    }


def _actions(count: int, width: int, height: int) -> list[dict]:
    return [
        {
            "index": index,
            "unit": 1,
            "type": 1,
            "x": index % width,
            "y": (index // width) % height,
            "target": None,
            "damage": 0,
        }
        for index in range(count)
    ]


class _Environment:
    max_units = 8

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.units = [_unit(1, 4, 0, 0), _unit(2, 1, width - 1, height - 1)]

    def unit_info(self) -> list[dict]:
        return [dict(unit) for unit in self.units]

    def map_info(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "terrain": ["Plain"] * (self.width * self.height),
        }

    def movement_costs(self, unit_id: int) -> list[int]:
        assert unit_id == 1
        return [1] * (self.width * self.height)


def test_controller_returns_only_finite_native_action_priors() -> None:
    actions = _actions(12, 6, 4)
    units = [_unit(1, 4, 0, 0), _unit(2, 1, 5, 3)]
    result = UniversalLatticeFieldController().priors(
        actions,
        units,
        6,
        4,
        movement_costs={1: [1] * 24},
    )
    legal = {int(action["index"]) for action in actions}
    assert result.mfg_priors
    assert result.quantum_priors
    assert set(result.mfg_priors) <= legal
    assert set(result.quantum_priors) <= legal
    assert all(isfinite(value) for value in result.mfg_priors.values())
    assert all(isfinite(value) for value in result.quantum_priors.values())
    assert result.quantum_max_dimension <= 128


def test_discrete_bottleneck_and_random_spacing_feed_runtime_mfg() -> None:
    actions = _actions(3, 3, 1)
    actions.append(
        {
            "index": 3,
            "unit": 3,
            "type": 0,
            "x": 2,
            "y": 0,
            "target": None,
            "damage": 0,
        }
    )
    units = [_unit(1, 4, 0, 0), _unit(3, 4, 2, 0), _unit(2, 1, 2, 0)]
    result = UniversalLatticeFieldController().priors(
        actions,
        units,
        3,
        1,
        movement_costs={1: [1, 1, 1]},
    )
    assert result.articulation_cells == 1
    assert result.formation_spacing == 2.0


def test_large_action_surface_is_deterministically_bounded() -> None:
    controller = UniversalLatticeFieldController(
        RuntimeLatticeFieldConfig(
            mfg_max_cells=24,
            quantum_max_cells=5,
            quantum_max_dimension=32,
        )
    )
    actions = _actions(120, 86, 56)
    units = [_unit(1, 4, 0, 0), _unit(2, 1, 85, 55)]
    first = controller.priors(actions, units, 86, 56)
    second = controller.priors(actions, units, 86, 56)
    assert first.active_cells <= 24
    assert first.omitted_cells > 0
    assert first.mfg_priors == second.mfg_priors
    assert first.quantum_priors == second.quantum_priors
    assert first.quantum_max_dimension <= 32


def test_oversized_army_degrades_coverage_without_disabling_fields() -> None:
    config = RuntimeLatticeFieldConfig(
        mfg_max_cells=12,
        quantum_max_cells=3,
        quantum_max_dimension=8,
        quantum_max_regions=4,
    )
    units = [_unit(unit_id, 4, unit_id - 1, 0) for unit_id in range(1, 31)]
    units.append(_unit(99, 1, 39, 0))
    actions = [
        {
            "index": unit_id - 1,
            "unit": unit_id,
            "type": 0,
            "x": unit_id - 1,
            "y": 0,
            "target": None,
            "damage": 0,
        }
        for unit_id in range(1, 31)
    ]
    result = UniversalLatticeFieldController(config).priors(
        actions,
        units,
        40,
        1,
        movement_costs={unit_id: [1] * 40 for unit_id in range(1, 31)},
    )
    assert result.active_cells == 12
    assert result.omitted_cells == 18
    assert result.mfg_priors
    assert result.quantum_priors
    assert result.quantum_regions == 4


def test_default_runtime_policy_binds_fields_across_map_sizes() -> None:
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
    )
    for width, height in ((10, 9), (86, 56)):
        environment = _Environment(width, height)
        actions = _actions(8, width, height)
        selected = policy.choose(
            environment,
            actions,
            np.zeros(132, dtype=np.float32),
            width,
            height,
        )
        assert selected in {int(action["index"]) for action in actions}
        assert "+mfg" in policy.backend
        assert "+quantum" in policy.backend
        assert policy.last_field_diagnostics is not None


def test_runtime_policy_can_explicitly_disable_automatic_fields() -> None:
    environment = _Environment(10, 9)
    actions = _actions(4, 10, 9)
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
        enable_lattice_fields=False,
    )
    policy.choose(
        environment,
        actions,
        np.zeros(132, dtype=np.float32),
        10,
        9,
    )
    assert policy.backend == "joint-mapf+cp-sat-optimal"
    assert policy.last_field_diagnostics is None


def test_runtime_policy_can_disable_qubo_for_ablation() -> None:
    environment = _Environment(10, 9)
    actions = _actions(4, 10, 9)
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
        enable_lattice_fields=False,
        enable_qubo_optimizer=False,
    )
    selected = policy.choose(
        environment,
        actions,
        np.zeros(132, dtype=np.float32),
        10,
        9,
    )
    assert selected in {int(action["index"]) for action in actions}
    assert policy.backend == "joint-mapf"
    assert policy.planner.last_optimizer_backend == "disabled"


def test_runtime_policy_can_pin_milp_backend() -> None:
    environment = _Environment(10, 9)
    actions = _actions(4, 10, 9)
    policy = RuntimeBattlePolicy(
        happo_path="rl/models/missing-happo.pt",
        cql_path="rl/models/missing-cql.pt",
        enable_lattice_fields=False,
        optimization_backend="milp",
    )
    selected = policy.choose(
        environment,
        actions,
        np.zeros(132, dtype=np.float32),
        10,
        9,
    )
    assert selected in {int(action["index"]) for action in actions}
    assert policy.backend == "joint-mapf+milp-optimal"
    assert policy.planner.last_optimizer_solution is not None
    assert policy.planner.last_optimizer_solution.optimal
