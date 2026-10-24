import numpy as np

from rl.p23_regime_rare_event_math import (
    BayesianOnlineChangePointDetector,
    adaptive_multilevel_splitting,
    hsmm_forward,
    hsmm_viterbi,
    subset_simulation,
)


def test_bocpd_detects_a_mean_shift_and_keeps_normalized_history():
    detector = BayesianOnlineChangePointDetector(
        hazard=0.02,
        observation_variance=0.09,
        prior_mean=0.0,
        prior_mean_variance=25.0,
        maximum_run_length=40,
    )
    updates = [detector.update(value) for value in [0.0] * 25 + [4.0] * 15]
    change = updates[25]
    assert np.isclose(change.run_length_posterior.sum(), 1.0)
    assert change.change_probability > 0.5
    assert change.map_run_length == 0
    assert updates[-1].map_run_length >= 10
    assert updates[-1].run_length_posterior.size <= 41


def test_hsmm_forward_and_viterbi_recover_explicit_three_step_segments():
    emission = np.array(
        [
            [0.0, -12.0],
            [0.0, -12.0],
            [0.0, -12.0],
            [-12.0, 0.0],
            [-12.0, 0.0],
            [-12.0, 0.0],
        ]
    )
    transition = np.array([[0.0, 1.0], [1.0, 0.0]])
    initial = np.array([1.0, 0.0])
    duration = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    forward = hsmm_forward(emission, transition, initial, duration)
    decoded = hsmm_viterbi(emission, transition, initial, duration)
    assert np.isclose(forward.log_likelihood, 0.0)
    assert np.array_equal(decoded.states, [0, 0, 0, 1, 1, 1])
    assert decoded.segments == ((0, 0, 3), (1, 3, 6))


def test_ams_preserves_levels_and_reports_genealogy():
    horizon = 12

    def simulate(rng):
        return np.cumsum(rng.normal(loc=0.05, scale=0.5, size=horizon))

    def score(path):
        return float(np.max(path))

    def branch(path, level, rng):
        path = np.asarray(path)
        crossing = int(np.flatnonzero(path >= level)[0])
        child = path.copy()
        if crossing + 1 < horizon:
            increments = rng.normal(
                loc=0.05, scale=0.5, size=horizon - crossing - 1
            )
            child[crossing + 1 :] = child[crossing] + np.cumsum(increments)
        return child

    result = adaptive_multilevel_splitting(
        simulate,
        branch,
        score,
        target_level=2.0,
        particle_count=80,
        kill_count=8,
        random_state=41,
        max_iterations=200,
    )
    assert result.converged
    assert 0.0 < result.probability <= 1.0
    assert result.target_count > 0
    assert 1.0 / 80.0 <= result.genealogy_concentration <= 1.0
    assert np.all(np.diff(result.levels) >= -1e-12)


def test_subset_simulation_estimates_a_standard_normal_tail():
    def sample(count, rng):
        return rng.normal(size=(count, 1))

    def log_density(point):
        return float(-0.5 * point[0] ** 2)

    def score(point):
        return float(point[0])

    result = subset_simulation(
        sample,
        log_density,
        score,
        target_level=2.0,
        sample_count=3000,
        conditional_probability=0.1,
        proposal_scale=0.8,
        random_state=17,
        max_levels=8,
    )
    assert result.converged
    assert 0.01 < result.probability < 0.05
    assert result.levels
    assert all(0.0 <= value <= 1.0 for value in result.acceptance_rates)
    assert result.samples.shape == (3000, 1)
