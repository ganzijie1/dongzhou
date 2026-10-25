import numpy as np

from rl.p32_common_information_game_math import (
    bayesian_correlated_equilibrium,
    common_information_belief_update,
    evaluate_two_agent_policy_graph,
    occupancy_state_transition,
)


def test_common_information_update_uses_action_and_public_signal():
    posterior = common_information_belief_update(
        [0.5, 0.5],
        [0.8, 0.2],
        [[0.9, 0.1], [0.1, 0.9]],
        [0.25, 0.75],
    )
    assert np.allclose(posterior, [0.4868421052631579, 0.5131578947368421])


def test_occupancy_state_transition_preserves_probability():
    occupancy = np.zeros((1, 2, 2))
    occupancy[0] = [[0.1, 0.2], [0.3, 0.4]]
    first = np.eye(2)
    second = np.eye(2)
    kernel = np.zeros((1, 2, 2, 2, 2, 1, 2, 2))
    for t1 in range(2):
        for t2 in range(2):
            for a1 in range(2):
                for a2 in range(2):
                    kernel[0, t1, t2, a1, a2, 0, a1, a2] = 1.0
    updated = occupancy_state_transition(occupancy, first, second, kernel)
    assert np.isclose(updated.sum(), 1.0)
    assert np.allclose(updated, occupancy)


def test_policy_graph_evaluation_tracks_controller_nodes():
    result = evaluate_two_agent_policy_graph(
        [1.0],
        (0, 0),
        np.ones((1, 1, 1, 1)),
        np.ones((1, 1, 1, 1, 1)),
        np.array([[[2.0]]]),
        np.ones((1, 1)),
        np.ones((1, 1)),
        np.ones((1, 1, 1)),
        np.ones((1, 1, 1)),
        horizon=3,
        discount=0.5,
    )
    assert np.isclose(result.expected_return, 3.5)
    assert np.isclose(result.final_occupancy.sum(), 1.0)


def test_bce_recovers_coordination_without_obedience_violation():
    prior = np.array([[1.0]])
    payoffs = np.zeros((2, 1, 1, 2, 2))
    payoffs[:, 0, 0, 0, 0] = 2.0
    payoffs[:, 0, 0, 1, 1] = 1.0
    result = bayesian_correlated_equilibrium(prior, payoffs)
    assert np.isclose(result.joint_distribution[0, 0, 0, 0], 1.0)
    assert np.allclose(result.expected_payoffs, [2.0, 2.0])
    assert result.minimum_obedience_slack >= -1e-9
