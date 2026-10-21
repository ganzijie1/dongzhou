"""Tests for the strategic mathematics layer and planner priors."""

from __future__ import annotations

from math import isclose

import numpy as np

from rl.belief_risk import (
    BayesianGridTracker,
    DiscreteBelief,
    bernoulli_loss_distribution,
    conditional_value_at_risk,
    entropic_risk,
)
from rl.decision_math import (
    SpectralGraph,
    integral_transport_assignment,
    lexicographic_choice,
    optimal_transport,
    pareto_front,
    solve_zero_sum_game,
)
from rl.strategic_flow import CapacityNetwork, Commodity, solve_multi_commodity_flow
from rl.strategic_math import StrategicMathAdvisor
from rl.runtime_policy import RuntimeBattlePolicy


def test_bayesian_prediction_and_negative_observation() -> None:
    adjacency = {
        (0, 0): ((1, 0),),
        (1, 0): ((0, 0), (2, 0)),
        (2, 0): ((1, 0),),
    }
    belief = DiscreteBelief.observed((1, 0)).predict(
        adjacency, stay_probability=0.0
    )
    assert belief.probabilities == {(0, 0): 0.5, (2, 0): 0.5}
    tracker = BayesianGridTracker()
    tracker.beliefs[7] = belief
    tracker.update({}, visible_cells={(0, 0)})
    assert tracker.beliefs[7].probabilities == {(2, 0): 1.0}


def test_cvar_entropic_risk_and_loss_convolution() -> None:
    assert isclose(
        conditional_value_at_risk((0.0, 10.0), 0.9, (0.9, 0.1)), 10.0
    )
    assert isclose(entropic_risk((2.0, 4.0), 0.0), 3.0)
    losses, probabilities = bernoulli_loss_distribution(
        ((0.5, 10.0), (0.5, 20.0))
    )
    assert losses == (0.0, 10.0, 20.0, 30.0)
    assert probabilities == (0.25, 0.25, 0.25, 0.25)


def test_max_flow_min_cut_and_multi_commodity_capacity() -> None:
    network = CapacityNetwork(
        {
            ("s", "a"): 1.0,
            ("s", "b"): 1.0,
            ("a", "t"): 1.0,
            ("b", "t"): 1.0,
        }
    )
    result = network.max_flow("s", "t")
    assert isclose(result.value, 2.0)
    assert set(result.cut_edges) in (
        {("s", "a"), ("s", "b")},
        {("a", "t"), ("b", "t")},
    )

    shared = CapacityNetwork(
        {
            ("a", "hub"): 1.0,
            ("b", "hub"): 1.0,
            ("hub", "t"): 1.0,
        }
    )
    allocation = solve_multi_commodity_flow(
        shared,
        (Commodity("a", "t", 1.0), Commodity("b", "t", 1.0)),
    )
    assert isclose(sum(allocation.delivered), 1.0)
    assert isclose(sum(allocation.unmet), 1.0)


def test_pareto_and_lexicographic_selection() -> None:
    objectives = {
        "aggressive": (10.0, 2.0),
        "safe": (4.0, 9.0),
        "inferior": (3.0, 1.0),
    }
    assert set(pareto_front(objectives)) == {"aggressive", "safe"}
    assert lexicographic_choice(objectives) == "aggressive"
    assert lexicographic_choice(
        objectives, maximize=(True, True), tolerances=(7.0, 0.0)
    ) == "safe"


def test_optimal_transport_preserves_marginals_and_assignment() -> None:
    result = optimal_transport(
        {"left": 1.0, "right": 1.0},
        {0: 1.0, 10: 1.0},
        {("left", 0): 0.0, ("left", 10): 10.0,
         ("right", 0): 10.0, ("right", 10): 0.0},
    )
    assert isclose(result.cost, 0.0)
    assert integral_transport_assignment(result) == {"left": 0, "right": 10}
    assert all(isclose(value, 1.0) for value in result.source_marginals.values())
    assert all(isclose(value, 1.0) for value in result.target_marginals.values())


def test_spectral_partition_and_effective_resistance() -> None:
    graph = SpectralGraph.from_grid(((0, 0), (1, 0), (2, 0)))
    result = graph.analyze()
    assert isclose(result.algebraic_connectivity, 1.0)
    assert result.left_partition and result.right_partition
    centrality = graph.resistance_centrality()
    assert centrality[(1, 0)] > centrality[(0, 0)]
    assert centrality[(1, 0)] > centrality[(2, 0)]


def test_zero_sum_game_finds_mixed_equilibrium() -> None:
    result = solve_zero_sum_game(((1.0, -1.0), (-1.0, 1.0)))
    assert all(isclose(value, 0.5, abs_tol=1e-8) for value in result.row_strategy)
    assert all(isclose(value, 0.5, abs_tol=1e-8) for value in result.column_strategy)
    assert isclose(result.value, 0.0, abs_tol=1e-8)
    assert result.duality_gap <= 1e-8


def test_strategic_advisor_penalizes_tail_risk_and_uses_all_layers() -> None:
    units = [
        {
            "id": 1, "force": 1, "class": "Infantry", "x": 0, "y": 0,
            "hp": 100, "max_hp": 100, "atk": 100, "dead": False,
            "attack_offsets": ((-1, 0), (1, 0)),
        },
        {
            "id": 2, "force": 4, "class": "Infantry", "x": 2, "y": 0,
            "hp": 100, "max_hp": 100, "atk": 100, "dead": False,
            "attack_offsets": ((-1, 0), (1, 0)),
        },
    ]
    actions = [
        {"index": 0, "unit": 1, "type": 0, "x": 0, "y": 0, "damage": 0},
        {"index": 1, "unit": 1, "type": 1, "x": 1, "y": 0, "damage": 0},
    ]
    result = StrategicMathAdvisor().action_priors(
        actions,
        units,
        3,
        1,
        passable_cells={(0, 0), (1, 0), (2, 0)},
        supply_sites={(0, 0)},
        formation_targets=((0, 0),),
        opponent_payoffs={0: (0.0, -1.0), 1: (-100.0, -50.0)},
    )
    assert result.components[1]["cvar"] > result.components[0]["cvar"]
    assert result.priors[0] > result.priors[1]
    assert result.transport_targets == {1: (0, 0)}
    assert result.algebraic_connectivity is not None
    assert result.supply_cut_edges
    assert result.enemy_beliefs[2] == {(2, 0): 1.0}
    assert result.game_strategies[1][0] > 1.0 - 1e-8


def test_runtime_strategic_math_opt_in_preserves_legal_actions() -> None:
    class FakeEnv:
        max_units = 8

        def unit_info(self):
            return [
                {
                    "id": 1, "force": 1, "class": "Infantry", "x": 0, "y": 0,
                    "hp": 100, "max_hp": 100, "atk": 100, "move": 5,
                    "done": False, "dead": False,
                    "attack_offsets": ((-1, 0), (1, 0)),
                },
                {
                    "id": 2, "force": 4, "class": "Infantry", "x": 2, "y": 0,
                    "hp": 100, "max_hp": 100, "atk": 100, "move": 5,
                    "done": False, "dead": False,
                    "attack_offsets": ((-1, 0), (1, 0)),
                },
            ]

        def map_info(self):
            return {"width": 3, "height": 1, "terrain": ["Plain"] * 3}

        def movement_costs(self, unit_id):
            return [1, 1, 1]

        def supply_info(self):
            return {"sites": [{"x": 0, "y": 0}]}

    actions = [
        {"index": 0, "unit": 1, "type": 0, "x": 0, "y": 0, "damage": 0},
        {"index": 1, "unit": 1, "type": 1, "x": 1, "y": 0, "damage": 0},
    ]
    policy = RuntimeBattlePolicy(
        happo_path="missing-happo.pt",
        cql_path="missing-cql.pt",
        enable_lattice_fields=False,
        enable_qubo_optimizer=False,
        enable_strategic_math=True,
    )
    selected = policy.choose(
        FakeEnv(), actions, np.zeros(132, dtype=np.float32), 3, 1
    )
    assert selected == 0
    assert selected in {int(action["index"]) for action in actions}
    assert policy.backend == "joint-mapf+math"
    assert policy.last_strategic_math is not None
    assert policy.strategic_math_error is None


def main() -> None:
    test_bayesian_prediction_and_negative_observation()
    test_cvar_entropic_risk_and_loss_convolution()
    test_max_flow_min_cut_and_multi_commodity_capacity()
    test_pareto_and_lexicographic_selection()
    test_optimal_transport_preserves_marginals_and_assignment()
    test_spectral_partition_and_effective_resistance()
    test_zero_sum_game_finds_mixed_equilibrium()
    test_strategic_advisor_penalizes_tail_risk_and_uses_all_layers()
    test_runtime_strategic_math_opt_in_preserves_legal_actions()
    print("strategic mathematics ok: beliefs, risk, flow, Pareto, OT, spectra, game")


if __name__ == "__main__":
    main()
