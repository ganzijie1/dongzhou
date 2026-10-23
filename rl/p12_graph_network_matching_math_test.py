import numpy as np

from rl.p12_graph_network_matching_math import (
    ConnectionsNetwork,
    GraphSignalProcessor,
    blocking_pairs,
    deferred_acceptance,
    dynamic_sbm_log_likelihood,
    estimate_dynamic_sbm,
    optimize_dynamic_tasks,
    optimize_hero_lineup,
    optimize_two_team_roles,
    simulate_dynamic_sbm,
)


def test_graph_fourier_round_trip_and_heat_smoothing():
    processor = GraphSignalProcessor([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    signal = np.array([1.0, 0.0, 0.0])
    assert np.allclose(
        processor.inverse_fourier_transform(processor.fourier_transform(signal)), signal
    )
    smoothed = processor.heat_filter(signal, time=1.0)
    assert processor.total_variation(smoothed) < processor.total_variation(signal)
    assert np.isclose(smoothed.sum(), signal.sum())
    assert np.allclose(
        processor.wavelet_coefficients(np.ones(3), scale=1.0), 0.0, atol=1e-10
    )


def test_dynamic_sbm_simulation_estimation_and_likelihood():
    sample = simulate_dynamic_sbm(
        8,
        4,
        [[0.9, 0.1], [0.1, 0.8]],
        [[0.9, 0.1], [0.2, 0.8]],
        [0.5, 0.5],
        seed=7,
    )
    assert sample.memberships.shape == (4, 8)
    assert np.all(sample.adjacencies == sample.adjacencies.transpose(0, 2, 1))
    block, transition = estimate_dynamic_sbm(
        sample.memberships, sample.adjacencies, smoothing=1.0
    )
    assert block.shape == (2, 2)
    assert np.allclose(transition.sum(axis=1), 1.0)
    assert np.isfinite(
        dynamic_sbm_log_likelihood(sample, block, transition, [0.5, 0.5])
    )


def test_known_dynamic_sbm_estimates_have_expected_structure():
    labels = [[0, 0, 1, 1], [0, 0, 1, 1]]
    graph = np.array(
        [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=float
    )
    block, transition = estimate_dynamic_sbm(labels, [graph, graph], smoothing=0.0)
    assert np.allclose(block, [[1.0, 0.0], [0.0, 1.0]])
    assert np.allclose(transition, np.eye(2))


def test_dynamic_sbm_unobserved_group_uses_neutral_block_probability():
    labels = [[0, 0], [0, 0]]
    graphs = [np.array([[0, 1], [1, 0]], dtype=float)] * 2
    block, transition = estimate_dynamic_sbm(
        labels, graphs, group_count=2, smoothing=0.0
    )
    assert block[1, 1] == 0.5
    assert np.allclose(transition[1], [0.5, 0.5])


def test_connections_network_pairwise_stability():
    model = ConnectionsNetwork(["a", "b", "c"], decay=0.5, link_cost=0.2)
    complete = [("a", "b"), ("a", "c"), ("b", "c")]
    assert model.pairwise_stability_violations(complete) == ()
    assert any(value[0] == "add" for value in model.pairwise_stability_violations([]))


def test_deferred_acceptance_is_stable_with_capacity():
    proposer = {"p1": ["r1", "r2"], "p2": ["r1", "r2"], "p3": ["r2"]}
    receiver = {"r1": ["p2", "p1"], "r2": ["p1", "p3", "p2"]}
    result = deferred_acceptance(proposer, receiver, capacities={"r1": 1, "r2": 2})
    assert result.assignments == {"p2": "r1", "p1": "r2", "p3": "r2"}
    assert (
        blocking_pairs(result, proposer, receiver, capacities={"r1": 1, "r2": 2}) == ()
    )


def test_two_team_role_assignment_honors_party_and_fairness():
    players = ["a", "b", "c", "d"]
    roles = ["front", "back"]
    skill = {
        ("a", "front"): 10,
        ("a", "back"): 1,
        ("b", "front"): 1,
        ("b", "back"): 10,
        ("c", "front"): 9,
        ("c", "back"): 1,
        ("d", "front"): 1,
        ("d", "back"): 9,
    }
    result = optimize_two_team_roles(
        players,
        roles,
        skill,
        parties=[["a", "b"]],
        pair_synergy={("a", "b"): 2.0},
        max_role_gap=1.0,
    )
    team_for = {player: team for (team, _), player in result.slots.items()}
    assert team_for["a"] == team_for["b"]
    for role in roles:
        left = skill[(result.slots[(0, role)], role)]
        right = skill[(result.slots[(1, role)], role)]
        assert abs(left - right) <= 1.0 + 1e-8


def test_dynamic_tasks_trade_utility_for_switching_cost():
    agents = ["a", "b"]
    tasks = ["lane", "jungle"]
    utilities = [
        {("a", "lane"): 5, ("a", "jungle"): 0, ("b", "lane"): 0, ("b", "jungle"): 5},
        {("a", "lane"): 0, ("a", "jungle"): 6, ("b", "lane"): 6, ("b", "jungle"): 0},
    ]
    bounds = [{"lane": 1, "jungle": 1}, {"lane": 1, "jungle": 1}]
    cheap = optimize_dynamic_tasks(
        agents, tasks, utilities, bounds, bounds, switch_cost=0.0
    )
    costly = optimize_dynamic_tasks(
        agents, tasks, utilities, bounds, bounds, switch_cost=7.0
    )
    assert cheap.switch_count == 2
    assert costly.switch_count == 0


def test_hero_lineup_honors_bans_uniqueness_pool_coverage_and_synergy():
    result = optimize_hero_lineup(
        ["top", "support"],
        ["tank", "healer", "assassin", "banned"],
        {
            ("top", "tank"): 8,
            ("top", "assassin"): 9,
            ("support", "healer"): 8,
            ("support", "tank"): 3,
        },
        banned_heroes=["banned"],
        allowed_heroes={"top": ["tank", "assassin"], "support": ["tank", "healer"]},
        pair_synergy={("tank", "healer"): 3.0},
        hero_coverage={("tank", "frontline"): 1.0, ("healer", "sustain"): 1.0},
        minimum_coverage={"frontline": 1.0, "sustain": 1.0},
    )
    assert result.selections == {"top": "tank", "support": "healer"}
    assert len(set(result.selections.values())) == 2
    assert result.coverage == {"frontline": 1.0, "sustain": 1.0}
