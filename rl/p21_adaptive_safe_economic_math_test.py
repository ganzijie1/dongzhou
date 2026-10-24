import numpy as np

from rl.p21_adaptive_safe_economic_math import (
    FixedSharePolicySelector,
    TwoSidedCUSUMDetector,
    cross_environment_transfer_diagnostics,
    finite_horizon_survival_probability,
    infinite_horizon_survival_probability,
    lagged_conditional_independence_graph,
    lagged_replay_design,
    leontief_input_output_analysis,
    perron_frobenius_analysis,
    robust_viability_kernel,
    scenario_robust_value_iteration,
)


def test_finite_and_infinite_survival_probabilities():
    transition = np.array(
        [
            [[0.0, 0.8, 0.2], [0.0, 0.5, 0.5]],
            [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        ]
    )
    finite = finite_horizon_survival_probability(
        transition, [0, 1], horizon=3
    )
    infinite = infinite_horizon_survival_probability(transition, [0, 1])
    assert np.allclose(finite.values[:, 0], [1.0, 0.8, 0.8, 0.8])
    assert finite.policy[0, 0] == 0
    assert infinite.converged
    assert np.allclose(infinite.values, [0.8, 1.0, 0.0])


def test_scenario_robust_value_iteration_uses_common_safe_action():
    scenarios = np.array(
        [
            [
                [[0.0, 1.0], [0.5, 0.5]],
                [[0.0, 1.0], [0.0, 1.0]],
            ],
            [
                [[1.0, 0.0], [0.5, 0.5]],
                [[0.0, 1.0], [0.0, 1.0]],
            ],
        ]
    )
    reward = np.array([[0.0, 0.0], [1.0, 1.0]])
    result = scenario_robust_value_iteration(scenarios, reward, discount=0.9)
    assert result.converged
    assert result.policy[0] == 1
    assert result.values[0] > 0.0


def test_robust_viability_requires_one_action_safe_in_every_scenario():
    scenarios = np.array(
        [
            [
                [[1.0, 0.0], [1.0, 0.0]],
                [[0.0, 1.0], [0.0, 1.0]],
            ],
            [
                [[0.0, 1.0], [1.0, 0.0]],
                [[0.0, 1.0], [0.0, 1.0]],
            ],
        ]
    )
    result = robust_viability_kernel(scenarios, [0])
    assert result.viable_states == (0,)
    assert result.viable_actions[0] == (1,)


def test_cusum_and_fixed_share_detect_and_adapt_without_immediate_flapping():
    detector = TwoSidedCUSUMDetector(
        0.0, allowance=0.1, threshold=1.0, minimum_observations=3
    )
    assert not detector.update(0.0).alarm
    assert not detector.update(0.0).alarm
    event = detector.update(2.0)
    assert event.alarm and event.direction == "up"

    selector = FixedSharePolicySelector(
        2,
        learning_rate=1.0,
        share=0.02,
        switch_margin=0.1,
        minimum_dwell=2,
    )
    first = selector.update([1.0, 0.0])
    second = selector.update([1.0, 0.0])
    assert not first.changed
    assert second.changed and second.active_policy == 1
    assert np.isclose(second.probabilities.sum(), 1.0)


def test_perron_frobenius_and_leontief_balances():
    matrix = np.array([[0.5, 0.5], [0.2, 0.8]])
    pf = perron_frobenius_analysis(matrix)
    assert np.isclose(pf.spectral_radius, 1.0)
    assert pf.irreducible
    assert pf.left_residual < 1e-10
    assert pf.right_residual < 1e-10

    coefficients = np.array([[0.2, 0.1], [0.1, 0.2]])
    result = leontief_input_output_analysis(
        coefficients,
        [1.0, 2.0],
        direct_labor=[0.5, 0.4],
        real_wage_bundle=[0.2, 0.1],
    )
    assert result.productive
    assert result.balance_residual < 1e-12
    assert np.all(result.gross_output >= np.array([1.0, 2.0]))
    assert result.labor_values is not None
    assert result.maximum_profit_rate is not None

    zero_system = leontief_input_output_analysis(np.zeros((2, 2)), [1.0, 2.0])
    assert zero_system.spectral_radius == 0.0
    assert np.array_equal(zero_system.gross_output, [1.0, 2.0])


def test_lagged_replay_never_crosses_episodes_and_finds_directed_lag():
    random = np.random.default_rng(31)
    episodes = []
    for _ in range(3):
        values = np.zeros((180, 2))
        for step in range(1, values.shape[0]):
            values[step, 0] = 0.7 * values[step - 1, 0] + random.normal(scale=0.3)
            values[step, 1] = 1.5 * values[step - 1, 0] + random.normal(scale=0.2)
        episodes.append(values)
    design = lagged_replay_design(episodes, maximum_lag=1)
    assert design.predictors.shape == (3 * 179, 2)
    assert np.array_equal(design.episode_indices[:179], np.zeros(179))
    assert design.time_indices[179] == 1
    graph = lagged_conditional_independence_graph(
        design, significance=1e-5, minimum_effect=0.2
    )
    assert graph.adjacency[0, 0, 0]
    assert graph.adjacency[0, 0, 1]
    assert not graph.adjacency[0, 1, 0]


def test_cross_environment_transfer_reports_held_out_risk():
    random = np.random.default_rng(47)
    environments = []
    for mean in (-2.0, 0.0, 2.0):
        cause = random.normal(loc=mean, size=250)
        nuisance = random.normal(size=250)
        outcome = 2.0 * cause + random.normal(scale=0.1, size=250)
        environments.append(np.column_stack((cause, nuisance, outcome)))
    result = cross_environment_transfer_diagnostics(
        environments, target=2, predictors=[0]
    )
    assert result.worst_environment_rmse < 0.15
    assert result.coefficient_spread < 0.05
    assert np.allclose(result.coefficients[:, 1], 2.0, atol=0.02)
