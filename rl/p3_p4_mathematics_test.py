"""Regression tests for the P3/P4 mathematical toolbox."""

from __future__ import annotations

from math import inf, isclose

import numpy as np

from rl.advanced_game_math import (
    CounterfactualRegretMinimizer,
    DecisionNode,
    TerminalNode,
    solve_stackelberg_game,
)
from rl.online_selection_math import (
    CUSUMChangeDetector,
    TemporalRequirement,
    UCB1Bandit,
    greedy_submodular_maximize,
    stl_always,
    stl_eventually,
    stl_until,
    weighted_coverage_value,
)
from rl.safety_robust_math import (
    control_barrier_filter,
    hamilton_jacobi_reachability,
    solve_network_interdiction,
    wasserstein_worst_case_expectation,
)
from rl.sensitivity_math import (
    exact_shapley_values,
    fit_block_maxima,
    sobol_sensitivity,
)
from rl.strategic_flow import CapacityNetwork
from rl.topology_flow_math import (
    corridor_modulus,
    discrete_conformal_map,
    hodge_decomposition,
    jackson_network,
    mm1_queue,
    persistent_homology,
)


def test_hamilton_jacobi_reachability_and_barrier_filter() -> None:
    result = hamilton_jacobi_reachability(
        (0, 1, 2),
        lambda state: ("advance", "risk") if state < 2 else (),
        lambda _state, _control: ("clear", "gust"),
        lambda state, control, disturbance: min(
            2,
            state + (control == "advance" or disturbance == "clear"),
        ),
        (2,),
        horizon=2,
    )
    assert result.can_reach(0)
    assert result.policy[(2, 0)] == "advance"

    filtered = control_barrier_filter(
        0,
        ("left", "right"),
        lambda state, action: state + (-1 if action == "left" else 1),
        lambda state: state + 1.0,
        alpha=0.2,
    )
    assert [entry.safe for entry in filtered] == [False, True]
    assert filtered[1].margin > 0.0


def test_wasserstein_dro_and_exact_network_interdiction() -> None:
    robust = wasserstein_worst_case_expectation(
        (1.0, 0.0),
        (0.0, 10.0),
        ((0.0, 1.0), (1.0, 0.0)),
        radius=0.2,
    )
    assert isclose(robust.worst_case_expectation, 2.0, abs_tol=1e-9)
    assert np.allclose(robust.adversarial_distribution, (0.8, 0.2))
    assert isclose(robust.transport_cost, 0.2, abs_tol=1e-9)

    network = CapacityNetwork(
        {
            ("s", "a"): 1.0,
            ("a", "t"): 1.0,
            ("s", "b"): 1.0,
            ("b", "t"): 1.0,
        }
    )
    interdiction = solve_network_interdiction(network, "s", "t", budget=1.0)
    assert len(interdiction.removed_edges) == 1
    assert isclose(interdiction.remaining_flow, 1.0)
    assert isclose(interdiction.spent_budget, 1.0)


def test_submodular_coverage_change_detection_bandit_and_temporal_logic() -> None:
    coverage = {
        "a": {"x": 1.0, "y": 1.0},
        "b": {"y": 1.0, "z": 1.0},
        "c": {"x": 1.0},
    }
    selection = greedy_submodular_maximize(
        tuple(coverage),
        lambda chosen: weighted_coverage_value(chosen, coverage),
        cardinality=2,
    )
    assert set(selection.selected) == {"a", "b"}
    assert isclose(selection.value, 3.0)

    detector = CUSUMChangeDetector(0.0, drift=0.1, threshold=1.0)
    statuses = [detector.update(value) for value in (0.0, 0.6, 0.7)]
    assert statuses[-1].changed and statuses[-1].direction == "increase"

    bandit = UCB1Bandit(("safe", "fast"))
    assert bandit.select() == "safe"
    bandit.update("safe", 0.25)
    assert bandit.select() == "fast"
    bandit.update("fast", 0.75)
    assert bandit.counts == {"safe": 1, "fast": 1}
    assert bandit.means["fast"] > bandit.means["safe"]

    assert stl_always((2.0, 1.0, 3.0)) == 1.0
    assert stl_eventually((-2.0, -1.0, 0.5)) == 0.5
    assert stl_until((2.0, 1.0, -1.0), (-2.0, 0.5, 3.0)) == 0.5
    assert TemporalRequirement("always").satisfied((1.0, 0.0))


def test_stackelberg_commitment_and_cfr_matching_pennies() -> None:
    commitment = solve_stackelberg_game(
        [[3.0, 0.0], [1.0, 2.0]],
        [[2.0, 0.0], [0.0, 1.0]],
    )
    assert commitment.follower_response == 0
    assert np.allclose(commitment.leader_strategy, (1.0, 0.0))
    assert isclose(commitment.leader_value, 3.0)

    root = DecisionNode(
        0,
        "player-zero",
        {
            "heads": DecisionNode(
                1,
                "player-one",
                {
                    "heads": TerminalNode(1.0),
                    "tails": TerminalNode(-1.0),
                },
            ),
            "tails": DecisionNode(
                1,
                "player-one",
                {
                    "heads": TerminalNode(-1.0),
                    "tails": TerminalNode(1.0),
                },
            ),
        },
    )
    equilibrium = CounterfactualRegretMinimizer().solve(root, iterations=10_000)
    for strategy in equilibrium.strategies.values():
        assert all(isclose(probability, 0.5, abs_tol=0.04) for probability in strategy.values())
    assert isclose(equilibrium.average_utility, 0.0, abs_tol=0.04)


def test_queueing_hodge_persistence_and_conformal_geometry() -> None:
    queue = mm1_queue(2.0, 4.0)
    assert isclose(queue.utilization, 0.5)
    assert isclose(queue.mean_system_size, 1.0)
    assert isclose(queue.mean_queue_size, 0.5)
    assert isclose(queue.mean_system_time, 0.5)
    assert isclose(queue.mean_wait_time, 0.25)
    network = jackson_network((1.0, 0.0), ((0.0, 0.5), (0.0, 0.0)), (2.0, 1.0))
    assert np.allclose(network.throughputs, (1.0, 0.5))

    decomposition = hodge_decomposition(
        ((0, 1), (1, 2), (2, 3), (3, 0)),
        (1.0, 1.0, 1.0, 1.0),
        faces=((0, 1, 2, 3),),
    )
    assert np.allclose(decomposition.gradient, 0.0, atol=1e-10)
    assert np.allclose(decomposition.curl, 1.0, atol=1e-10)
    assert decomposition.energy_fractions["curl"] > 0.999999

    intervals = persistent_homology(
        {0: 0.0, 1: 0.0, 2: 0.0},
        {(0, 1): 1.0, (1, 2): 1.0, (0, 2): 1.0},
        {(0, 1, 2): 2.0},
    )
    assert any(
        interval.dimension == 1
        and interval.birth == 1.0
        and interval.death == 2.0
        for interval in intervals
    )
    assert any(interval.dimension == 0 and interval.death == inf for interval in intervals)

    source = {
        "sw": (0.0, 0.0),
        "se": (1.0, 0.0),
        "ne": (1.0, 1.0),
        "nw": (0.0, 1.0),
        "center": (0.5, 0.5),
    }
    triangles = (
        ("sw", "se", "center"),
        ("se", "ne", "center"),
        ("ne", "nw", "center"),
        ("nw", "sw", "center"),
    )
    mapping = discrete_conformal_map(
        source,
        triangles,
        {key: value for key, value in source.items() if key != "center"},
    )
    assert np.allclose(mapping.coordinates["center"], (0.5, 0.5))
    assert isclose(mapping.maximum_distortion, 1.0, abs_tol=1e-9)
    assert corridor_modulus(10.0, 2.0) == 5.0


def test_shapley_sobol_and_extreme_value_analysis() -> None:
    def coalition_value(coalition: frozenset[str]) -> float:
        result = float("a" in coalition) + 2.0 * float("b" in coalition)
        if {"a", "b"} <= coalition:
            result += 3.0
        return result

    attribution = exact_shapley_values(("a", "b"), coalition_value)
    assert isclose(attribution.values["a"], 2.5)
    assert isclose(attribution.values["b"], 3.5)
    assert isclose(attribution.explained_value, attribution.total_value - attribution.baseline)

    sensitivity = sobol_sensitivity(
        lambda parameters: parameters["x"] + 2.0 * parameters["y"],
        {"x": (0.0, 1.0), "y": (0.0, 1.0)},
        samples=20_000,
        seed=7,
    )
    assert isclose(sensitivity.first_order["x"], 0.2, abs_tol=0.03)
    assert isclose(sensitivity.first_order["y"], 0.8, abs_tol=0.03)
    assert isclose(sensitivity.total_order["x"], 0.2, abs_tol=0.03)
    assert isclose(sensitivity.total_order["y"], 0.8, abs_tol=0.03)

    maxima = np.random.default_rng(11).gumbel(loc=10.0, scale=2.0, size=1000)
    extreme = fit_block_maxima(maxima)
    assert extreme.observations == 1000
    assert extreme.scale > 0.0
    assert extreme.return_level(100.0) > extreme.return_level(10.0)
