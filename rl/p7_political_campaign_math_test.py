import math

import numpy as np

from rl.p7_political_campaign_math import (
    DiscreteFactor,
    DiscreteFactorGraph,
    ExponentialHawkesProcess,
    FiniteDynamicBayesianFilter,
    ShippingArc,
    TemporalMultilayerNetwork,
    pure_signaling_equilibria,
    solve_dynamic_inventory_flow,
    solve_stochastic_inventory,
)


def test_factor_graph_and_dynamic_bayesian_filter_update_hidden_state():
    graph = DiscreteFactorGraph(
        {"plot": (False, True), "rumor": (False, True)},
        (
            DiscreteFactor(("plot",), np.array([0.8, 0.2])),
            DiscreteFactor(
                ("plot", "rumor"),
                np.array([[0.9, 0.1], [0.2, 0.8]]),
            ),
        ),
    )
    posterior = graph.marginal(("plot",), {"rumor": True})
    assert np.allclose(posterior, [1.0 / 3.0, 2.0 / 3.0])

    tracker = FiniteDynamicBayesianFilter(
        ("loyal", "plotting"),
        ("quiet", "warning"),
        [0.9, 0.1],
        [[0.9, 0.1], [0.2, 0.8]],
        [[0.9, 0.1], [0.2, 0.8]],
    )
    step = tracker.update("warning")
    assert math.isclose(step.observation_probability, 0.219, rel_tol=1e-12)
    assert step.posterior[1] > step.predictive[1]


def test_signaling_game_finds_separating_equilibrium():
    types = ("strong", "weak")
    messages = ("strong-claim", "weak-claim")
    actions = ("trust", "challenge")
    sender = np.array(
        [
            [[2.0, 0.0], [2.0, 0.0]],
            [[-1.0, -3.0], [2.0, 0.0]],
        ]
    )
    receiver = np.array(
        [
            [[1.0, 0.0], [1.0, 0.0]],
            [[0.0, 1.0], [0.0, 1.0]],
        ]
    )
    equilibria = pure_signaling_equilibria(
        types, messages, actions, [0.5, 0.5], sender, receiver
    )
    separating = [
        equilibrium
        for equilibrium in equilibria
        if equilibrium.sender_strategy
        == {"strong": "strong-claim", "weak": "weak-claim"}
        and equilibrium.receiver_strategy
        == {"strong-claim": "trust", "weak-claim": "challenge"}
    ]
    assert len(separating) == 1
    assert separating[0].posteriors["strong-claim"]["strong"] == 1.0


def test_temporal_multilayer_network_preserves_layers_and_reports_change():
    adjacency = np.zeros((2, 2, 3, 3))
    adjacency[0, 0, 0, 1] = adjacency[0, 0, 1, 0] = 1.0
    adjacency[1, 0, 0, 1] = adjacency[1, 0, 1, 0] = 1.0
    adjacency[1, 1, 1, 2] = adjacency[1, 1, 2, 1] = -0.5
    network = TemporalMultilayerNetwork(("qin", "chu", "qi"), ("alliance", "hostility"), adjacency)
    diagnostics = network.diagnostics([1.0, 1.0])
    assert diagnostics.aggregate_snapshots.shape == (2, 3, 3)
    assert diagnostics.volatility[0] == 0.0
    assert diagnostics.volatility[1] > 0.0
    assert network.supra_adjacency(1, coupling=0.2).shape == (6, 6)


def test_hawkes_process_reports_stability_intensity_and_likelihood():
    process = ExponentialHawkesProcess(
        [0.2, 0.1],
        [[0.3, 0.1], [0.2, 0.2]],
        decay=1.0,
    )
    assert process.stable
    intensity = process.intensity(2.0, [(1.0, 0)])
    assert np.all(intensity > process.baseline)
    assert np.all(process.stationary_intensity() > process.baseline)
    assert math.isfinite(process.log_likelihood([(0.5, 0), (1.5, 1)], 2.0))


def test_stochastic_inventory_and_time_expanded_supply_flow():
    policy = solve_stochastic_inventory(
        ({2: 1.0}, {2: 1.0}),
        initial_inventory=0,
        order_capacity=3,
        holding_cost=0.1,
        shortage_cost=10.0,
        order_cost=1.0,
    )
    assert policy.orders[0, 0] == 2
    assert policy.expected_cost < 20.0

    flow = solve_dynamic_inventory_flow(
        ("west", "east"),
        2,
        (ShippingArc("west", "east", 10.0, 1.0),),
        initial_inventory={"west": 0.0, "east": 0.0},
        supply={(0, "west"): 10.0},
        demand={(1, "east"): 5.0},
        storage_capacity={"west": 10.0, "east": 10.0},
        shortage_penalty={"west": 100.0, "east": 100.0},
    )
    assert math.isclose(flow.shipments[(0, "west", "east")], 5.0)
    assert math.isclose(flow.unmet[(1, "east")], 0.0, abs_tol=1e-9)
