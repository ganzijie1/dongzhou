import math

import numpy as np

from rl.p8_adaptive_mechanism_math import (
    AdaptiveConformalRegressor,
    BernoulliMixtureEProcess,
    GaussianProcessRegressor,
    LinUCBBandit,
    RestlessArm,
    solve_limited_liability_contract,
    vcg_mechanism,
    whittle_indices,
)


def test_vcg_uses_externality_payments():
    result = vcg_mechanism(
        ("qin", "chu"),
        ("qin-gets-command", "chu-gets-command"),
        {
            ("qin", "qin-gets-command"): 10.0,
            ("qin", "chu-gets-command"): 0.0,
            ("chu", "qin-gets-command"): 0.0,
            ("chu", "chu-gets-command"): 7.0,
        },
    )
    assert result.outcome == "qin-gets-command"
    assert result.payments["qin"] == 7.0
    assert result.utilities["qin"] == 3.0


def test_contract_enforces_incentive_compatibility_and_participation():
    result = solve_limited_liability_contract(
        [[0.8, 0.2], [0.2, 0.8]],
        [0.0, 0.3],
        1,
    )
    assert np.all(result.wages >= 0.0)
    assert result.incentive_slacks[0] >= -1e-9
    assert result.desired_utility >= -1e-9
    assert math.isclose(result.expected_wage, 0.4, abs_tol=1e-8)


def test_linucb_learns_from_contextual_reward():
    bandit = LinUCBBandit(("scout", "diplomat"), 1, exploration=0.1)
    contexts = {"scout": [1.0], "diplomat": [1.0]}
    bandit.update("scout", [1.0], 3.0)
    assert bandit.select(contexts) == "scout"
    assert bandit.scores(contexts)["scout"] > bandit.scores(contexts)["diplomat"]


def test_two_state_whittle_indices_match_immediate_reward_advantage():
    identity = np.eye(2)
    result = whittle_indices(
        RestlessArm(identity, identity, np.zeros(2), np.array([0.0, 1.0])),
        tolerance=1e-7,
    )
    assert result.indexable
    assert np.allclose(result.indices, [0.0, 1.0], atol=1e-5)


def test_gaussian_process_returns_posterior_and_expected_improvement():
    process = GaussianProcessRegressor(noise_variance=1e-8).fit(
        [[0.0], [1.0]], [0.0, 1.0]
    )
    prediction = process.predict([[0.0], [1.0]])
    assert np.allclose(prediction.mean, [0.0, 1.0], atol=1e-5)
    assert np.all(prediction.standard_deviation < 1e-3)
    index, acquisition = process.propose([[0.5], [1.5]])
    assert index in (0, 1)
    assert np.all(acquisition >= 0.0)


def test_online_conformal_and_e_process_update_sequentially():
    conformal = AdaptiveConformalRegressor(
        [1.0] * 20, target_alpha=0.1, learning_rate=0.05, window=20
    )
    before = conformal.current_alpha
    assert conformal.update(0.0, 5.0)
    assert conformal.current_alpha < before
    assert 5.0 in conformal.residuals

    process = BernoulliMixtureEProcess(0.5)
    status = None
    for _ in range(20):
        status = process.update(True)
    assert status is not None and status.e_value > 20.0
    assert process.rejects(0.05)
