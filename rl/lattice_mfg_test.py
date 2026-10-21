"""Mass, optimality, multi-population, and planner tests for lattice MFG."""

from __future__ import annotations

from math import isclose

import numpy as np

from rl.joint_turn_planner import JointTurnPlanner
from rl.lattice_mfg import (
    LatticeMFG,
    LatticeMFGConfig,
    LatticeMFGError,
    MultiPopulationLatticeMFG,
)


def _unit(unit_id: int, x: int, y: int) -> dict:
    return {
        "id": unit_id,
        "force": 4,
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


def _action(index: int, x: int, y: int) -> dict:
    return {
        "index": index,
        "unit": 1,
        "type": 1,
        "x": x,
        "y": y,
        "target": None,
        "damage": 0,
    }


def test_backward_forward_solver_conserves_mass_and_reaches_goal() -> None:
    model = LatticeMFG.from_grid(
        3,
        1,
        config=LatticeMFGConfig(
            horizon=4,
            temperature=0.35,
            congestion_weight=1.0,
            relaxation=0.5,
            tolerance=1e-7,
        ),
    )
    result = model.solve({(0, 0): 1.0}, {(2, 0): -8.0})
    assert result.converged
    assert result.fixed_point_residual <= 1e-7
    assert np.all(result.densities >= 0.0)
    assert np.allclose(result.densities.sum(axis=1), 1.0)
    assert np.allclose(result.policies.sum(axis=2), 1.0)
    assert result.density(4)[(2, 0)] > 0.99


def test_grid_builder_respects_impassable_cells() -> None:
    model = LatticeMFG.from_grid(
        3,
        2,
        movement_costs=[1, 255, 1, 1, 1, 1],
        config=LatticeMFGConfig(horizon=2),
    )
    assert (1, 0) not in model.cells
    assert all((1, 0) not in edge for edge in model.edge_costs)
    result = model.solve({(0, 0): 1.0}, {(2, 0): -5.0})
    assert np.allclose(result.densities.sum(axis=1), 1.0)


def test_zero_temperature_uses_deterministic_bellman_action() -> None:
    model = LatticeMFG.from_grid(
        2,
        1,
        config=LatticeMFGConfig(
            horizon=1,
            temperature=0.0,
            congestion_weight=0.0,
            relaxation=1.0,
        ),
    )
    result = model.solve({(0, 0): 1.0}, {(0, 0): 0.0, (1, 0): -4.0})
    source = model.index[(0, 0)]
    target = model.index[(1, 0)]
    assert result.policies[0, source, target] == 1.0


def test_invalid_density_is_rejected() -> None:
    model = LatticeMFG.from_grid(2, 1, config=LatticeMFGConfig(horizon=1))
    try:
        model.solve({(0, 0): -1.0, (1, 0): 2.0}, {})
    except LatticeMFGError:
        pass
    else:
        raise AssertionError("negative MFG density must fail")


def test_result_generates_legal_centered_action_priors() -> None:
    model = LatticeMFG.from_grid(
        2,
        1,
        config=LatticeMFGConfig(
            horizon=1,
            temperature=0.2,
            congestion_weight=0.0,
        ),
    )
    result = model.solve({(0, 0): 1.0}, {(1, 0): -6.0})
    actions = [_action(0, 0, 0), _action(1, 1, 0)]
    priors = result.action_priors(actions, [_unit(1, 0, 0)])
    assert priors[1] > priors[0]
    assert isclose(sum(priors.values()), 0.0, abs_tol=1e-12)
    chosen = JointTurnPlanner().choose(
        actions,
        [_unit(1, 0, 0)],
        2,
        1,
        movement_costs={1: [1, 1]},
        mfg_priors=priors,
    )
    assert chosen.action_index == 1
    assert chosen.reason == "mfg-prior"


def test_action_prior_supports_native_multi_cell_move_endpoint() -> None:
    model = LatticeMFG.from_grid(
        3,
        1,
        config=LatticeMFGConfig(
            horizon=2,
            temperature=0.25,
            congestion_weight=0.0,
        ),
    )
    result = model.solve({(0, 0): 1.0}, {(2, 0): -7.0})
    actions = [_action(0, 0, 0), _action(1, 2, 0)]
    priors = result.action_priors(actions, [_unit(1, 0, 0)])
    assert priors[1] > priors[0]


def test_multi_population_asymmetric_interaction_preserves_each_mass() -> None:
    config = LatticeMFGConfig(
        horizon=2,
        temperature=0.5,
        congestion_weight=0.25,
        tolerance=1e-6,
    )
    models = {
        "infantry": LatticeMFG.from_grid(2, 1, config=config),
        "archer": LatticeMFG.from_grid(2, 1, config=config),
    }
    solver = MultiPopulationLatticeMFG(
        models,
        {
            ("infantry", "archer"): 1.0,
            ("archer", "infantry"): -0.25,
        },
        tolerance=1e-5,
    )
    result = solver.solve(
        {"infantry": {(0, 0): 1.0}, "archer": {(1, 0): 1.0}},
        {"infantry": {(1, 0): -2.0}, "archer": {(0, 0): -2.0}},
    )
    assert result.residuals
    for population in result.populations.values():
        assert np.allclose(population.densities.sum(axis=1), 1.0)
