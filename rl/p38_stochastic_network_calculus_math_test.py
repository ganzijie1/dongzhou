import numpy as np

from rl.p38_stochastic_network_calculus_math import (
    concatenate_service_curves,
    constant_service_tail_bound,
    deterministic_queue_bounds,
    effective_bandwidth,
    effective_bandwidth_chernoff_bound,
    effective_capacity,
    markov_modulated_effective_bandwidth,
    min_plus_convolution,
    rate_latency_curve,
    stochastic_split_bound,
    token_bucket_curve,
)


def test_min_plus_convolution_and_service_concatenation():
    first = rate_latency_curve(rate=2.0, latency=1.0, horizon=6)
    second = rate_latency_curve(rate=3.0, latency=2.0, horizon=6)
    combined = concatenate_service_curves([first, second])
    assert np.allclose(combined, min_plus_convolution(first, second))
    assert np.allclose(combined, rate_latency_curve(rate=2.0, latency=3.0, horizon=6))


def test_token_bucket_rate_latency_bounds_match_geometry_on_grid():
    arrival = token_bucket_curve(burst=4.0, rate=1.0, horizon=20)
    service = rate_latency_curve(rate=2.0, latency=3.0, horizon=20)
    bounds = deterministic_queue_bounds(arrival, service)
    assert bounds.backlog == 7.0
    assert bounds.delay_steps == 5.0
    assert bounds.stable_on_grid


def test_effective_bandwidth_capacity_and_chernoff_bound():
    arrivals = [1.0, 1.0, 3.0, 3.0]
    services = [4.0, 4.0, 2.0, 2.0]
    bandwidth = effective_bandwidth(arrivals, theta=0.5, duration=1.0)
    capacity = effective_capacity(services, theta=0.5, duration=1.0)
    bound = effective_bandwidth_chernoff_bound(
        arrivals, theta=0.5, duration=1.0, capacity_rate=5.0
    )
    assert bandwidth > np.mean(arrivals)
    assert capacity < np.mean(services)
    assert 0.0 < bound < 1.0


def test_stochastic_split_and_constant_service_tail_bounds():
    combined = stochastic_split_bound([0.5, 0.2, 0.1], [0.4, 0.2, 0.05])
    assert np.allclose(combined, [0.9, 0.6, 0.4])
    result = constant_service_tail_bound(
        np.log(1.2),
        theta=1.0,
        service_per_slot=1.0,
        backlog_threshold=5.0,
        delay_threshold=5.0,
    )
    assert result.traffic_factor < 1.0
    assert result.backlog_probability < 0.02
    assert result.delay_probability == result.backlog_probability


def test_markov_modulated_effective_bandwidth_detects_burst_state():
    value = markov_modulated_effective_bandwidth(
        [[0.9, 0.1], [0.2, 0.8]], [0.0, 5.0], theta=0.2
    )
    assert 0.0 < value < 5.0
