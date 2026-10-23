import numpy as np
import pytest

from rl.p15_inverse_optimization_math import (
    InverseLPObservation,
    StackelbergObservation,
    bayesian_inverse_mdp,
    discounted_occupancy,
    fit_revealed_linear_cost,
    inverse_linear_program,
    inverse_linear_rhs,
    inverse_logit_stackelberg_utility,
    inverse_mdp_policy,
    inverse_stackelberg_follower_utility,
    potential_based_reward_shaping,
    solve_incentive_stackelberg,
)


def test_inverse_lp_recovers_reference_cost_and_kkt_certificate():
    # Unit box written as A x <= b; the lower-left corner minimizes 2x + y.
    observation = InverseLPObservation(
        np.array([[-1.0, 0.0], [0.0, -1.0], [1.0, 0.0], [0.0, 1.0]]),
        np.array([0.0, 0.0, 1.0, 1.0]),
        np.array([0.0, 0.0]),
    )
    result = inverse_linear_program([observation], [2.0, 1.0])
    assert np.allclose(result.cost, [2.0, 1.0])
    assert np.allclose(result.duals[0], [2.0, 1.0, 0.0, 0.0])
    assert result.active_sets == ((0, 1),)
    assert result.stationarity_residual < 1e-9
    assert result.complementarity_residual < 1e-9


def test_inverse_lp_uses_all_observations_and_rejects_infeasible_points():
    lower_left = InverseLPObservation(
        np.array([[-1.0, 0.0], [0.0, -1.0]]),
        np.zeros(2),
        np.zeros(2),
    )
    second_copy = InverseLPObservation(
        np.array([[-2.0, 0.0], [0.0, -3.0]]),
        np.zeros(2),
        np.zeros(2),
    )
    result = inverse_linear_program([lower_left, second_copy], [1.0, 4.0])
    assert np.allclose(result.cost, [1.0, 4.0])
    assert len(result.duals) == 2
    infeasible = InverseLPObservation(
        np.array([[1.0, 0.0]]), np.array([0.0]), np.array([1.0, 0.0])
    )
    with pytest.raises(ValueError, match="infeasible"):
        inverse_linear_program([infeasible], [1.0, 1.0])


def test_inverse_linear_rhs_projects_reference_and_honors_active_rows():
    result = inverse_linear_rhs(
        [[1.0, 0.0], [0.0, 1.0]],
        [[2.0, 1.0], [1.0, 3.0]],
        [1.0, 5.0],
        active_constraints=[[0], []],
    )
    assert np.allclose(result.bounds, [2.0, 5.0])
    assert np.allclose(result.adjustments, [1.0, 0.0])
    assert result.maximum_primal_violation == 0.0
    assert result.active_residual == 0.0
    with pytest.raises(ValueError, match="inconsistent"):
        inverse_linear_rhs(
            [[1.0]], [[1.0], [2.0]], [0.0], active_constraints=[[0], [0]]
        )


def test_soft_revealed_cost_reports_noise_and_identifiability_rank():
    result = fit_revealed_linear_cost(
        [[0.0, 0.0], [0.0, 0.0]],
        [[[1.0, 0.0], [0.0, 1.0]], [[1.0, 1.0], [2.0, 0.0]]],
        [2.0, 1.0],
        margin=0.5,
    )
    assert np.allclose(result.cost, [2.0, 1.0])
    assert np.allclose(result.slacks, 0.0)
    assert result.maximum_violation == 0.0
    assert result.comparison_rank == 2


def _two_state_mdp():
    transition = np.zeros((2, 2, 2))
    transition[0, :, 0] = 1.0
    transition[1, :, 1] = 1.0
    features = np.zeros((2, 2, 2))
    features[0, 0, 0] = 1.0
    features[1, 1, 1] = 1.0
    return transition, features


def test_discounted_occupancy_and_feature_expectations():
    transition, features = _two_state_mdp()
    policy = np.array([[1.0, 0.0], [0.0, 1.0]])
    result = discounted_occupancy(
        transition,
        policy,
        [0.5, 0.5],
        discount=0.9,
        features=features,
    )
    assert np.isclose(result.state_action.sum(), 10.0)
    assert np.allclose(result.state, [5.0, 5.0])
    assert np.allclose(result.feature_expectations, [5.0, 5.0])


def test_inverse_mdp_recovers_policy_optimal_reward_and_advantages():
    transition, features = _two_state_mdp()
    result = inverse_mdp_policy(
        transition,
        features,
        [0, 1],
        [1.0, 1.0],
        discount=0.9,
        margin=0.5,
    )
    assert np.allclose(result.reward_weights, [1.0, 1.0])
    assert np.allclose(result.slacks, 0.0)
    assert result.advantages[0, 1] >= 0.5
    assert result.advantages[1, 0] >= 0.5
    assert result.comparison_rank == 2


def test_potential_shaping_preserves_action_advantage():
    transition, _features = _two_state_mdp()
    reward = np.array([[2.0, 0.0], [0.0, 3.0]])
    shaped = potential_based_reward_shaping(
        transition, reward, [4.0, -2.0], discount=0.9
    )
    assert np.isclose(shaped[0, 0] - shaped[0, 1], 2.0)
    assert np.isclose(shaped[1, 1] - shaped[1, 0], 3.0)


def test_bayesian_inverse_mdp_updates_finite_reward_hypotheses():
    transition = np.ones((1, 2, 1))
    features = np.array([[[1.0, 0.0], [0.0, 1.0]]])
    result = bayesian_inverse_mdp(
        transition,
        features,
        [(0, 0)] * 8,
        [[2.0, 0.0], [0.0, 2.0]],
        discount=0.9,
        precision=2.0,
    )
    assert result.map_index == 0
    assert np.allclose(result.map_weights, [2.0, 0.0])
    assert result.posterior[0] > 0.99
    assert np.isclose(result.posterior.sum(), 1.0)
    assert result.action_probabilities[0, 0, 0] > 0.95


def _stackelberg_features():
    features = np.zeros((2, 2, 2))
    features[0, 0, 0] = 1.0
    features[1, 1, 1] = 1.0
    return features


def test_inverse_stackelberg_recovers_rational_follower_utility():
    observations = [
        StackelbergObservation(np.array([1.0, 0.0]), 0),
        StackelbergObservation(np.array([0.0, 1.0]), 1),
    ]
    result = inverse_stackelberg_follower_utility(
        _stackelberg_features(),
        observations,
        [1.0, 2.0],
        margin=0.5,
    )
    assert np.allclose(result.follower_weights, [1.0, 2.0])
    assert np.allclose(result.regrets, 0.0)
    assert np.allclose(result.slacks, 0.0)
    assert result.comparison_rank == 2


def test_inverse_logit_stackelberg_improves_observed_choice_likelihood():
    observations = []
    for _ in range(8):
        observations.append(StackelbergObservation(np.array([1.0, 0.0]), 0))
        observations.append(StackelbergObservation(np.array([0.0, 1.0]), 1))
    result = inverse_logit_stackelberg_utility(
        _stackelberg_features(),
        observations,
        [0.0, 0.0],
        l2_regularization=0.1,
    )
    assert result.converged
    assert np.all(result.follower_weights > 0.0)
    assert np.all(result.choice_probabilities[:, 0][::2] > 0.5)
    assert np.all(result.choice_probabilities[:, 1][1::2] > 0.5)
    assert result.negative_log_likelihood < len(observations) * np.log(2.0)
    assert result.information_rank == 2


def test_incentive_stackelberg_builds_punishing_reaction_map():
    result = solve_incentive_stackelberg(
        [[5.0, 0.0], [1.0, 4.0]],
        [[2.0, 3.0], [0.0, 1.0]],
    )
    assert result.reaction_map == (0, 1)
    assert result.follower_response == 0
    assert result.leader_value == 5.0
    assert result.follower_value == 2.0
    assert result.best_response_set == (0,)


def test_stackelberg_tie_breaking_and_profile_budget_are_explicit():
    leader = [[3.0, 0.0], [1.0, 2.0]]
    follower = [[1.0, 1.0], [1.0, 1.0]]
    strong = solve_incentive_stackelberg(leader, follower, tie_breaking="strong")
    weak = solve_incentive_stackelberg(leader, follower, tie_breaking="weak")
    assert strong.leader_value >= weak.leader_value
    assert strong.tie_breaking == "strong"
    assert weak.tie_breaking == "weak"
    with pytest.raises(ValueError, match="budget"):
        solve_incentive_stackelberg(
            np.zeros((3, 5)), np.zeros((3, 5)), max_profiles=100
        )
