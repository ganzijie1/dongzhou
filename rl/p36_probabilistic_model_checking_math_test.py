import numpy as np

from rl.p36_probabilistic_model_checking_math import (
    csl_time_bounded_reachability,
    ctmc_uniformization,
    dtmc_reachability,
    hoeffding_sample_size,
    mdp_reachability,
    pctl_bounded_until,
    sequential_probability_ratio_test,
    statistical_model_check,
)


def test_dtmc_reachability_and_bounded_until():
    transition = [[0.5, 0.5], [0.0, 1.0]]
    result = dtmc_reachability(transition, [False, True])
    bounded = pctl_bounded_until(
        transition, [True, True], [False, True], steps=2
    )
    assert np.allclose(result.probabilities, [1.0, 1.0], atol=1e-9)
    assert np.allclose(bounded, [0.75, 1.0])


def test_mdp_min_max_reachability_exposes_scheduler_range():
    transition = np.array(
        [
            [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
        ]
    )
    maximum = mdp_reachability(transition, [False, True, False], maximize=True)
    minimum = mdp_reachability(transition, [False, True, False], maximize=False)
    assert maximum.probabilities[0] == 1.0
    assert minimum.probabilities[0] == 0.0


def test_ctmc_uniformization_and_csl_reachability_match_exponential_clock():
    generator = [[-2.0, 2.0], [0.0, 0.0]]
    transient = ctmc_uniformization(generator, [1.0, 0.0], time=1.0)
    reach = csl_time_bounded_reachability(generator, [False, True], time=1.0)
    expected = 1.0 - np.exp(-2.0)
    assert np.isclose(transient.distribution[1], expected, atol=1e-10)
    assert np.isclose(reach[0], expected, atol=1e-10)
    assert reach[1] == 1.0


def test_statistical_model_check_and_sample_size():
    result = statistical_model_check([True] * 90 + [False] * 10, delta=0.05)
    assert result.estimate == 0.9
    assert result.lower < result.estimate < result.upper
    assert hoeffding_sample_size(epsilon=0.1, delta=0.05) == 185


def test_sprt_accepts_high_probability_null_and_low_probability_alternative():
    high = sequential_probability_ratio_test(
        [True] * 100,
        null_probability=0.8,
        alternative_probability=0.5,
        alpha=0.05,
        beta=0.05,
    )
    low = sequential_probability_ratio_test(
        [False] * 100,
        null_probability=0.8,
        alternative_probability=0.5,
        alpha=0.05,
        beta=0.05,
    )
    assert high.decision == "accept_null"
    assert low.decision == "accept_alternative"
