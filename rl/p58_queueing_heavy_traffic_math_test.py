import numpy as np

from rl.p58_queueing_heavy_traffic_math import (
    fluid_queue_path,
    jackson_network_metrics,
    jackson_traffic_rates,
    kingman_mean_wait,
    little_law,
    mm1_metrics,
    reflected_brownian_path,
    square_root_staffing,
)


def test_little_law_and_mm1_metrics_agree():
    metrics = mm1_metrics(1.0, 2.0)
    assert np.isclose(metrics.mean_system_size, little_law(1.0, metrics.mean_system_time))
    assert np.isclose(metrics.mean_queue_size, little_law(1.0, metrics.mean_waiting_time))


def test_jackson_traffic_equations_include_internal_visits():
    rates = jackson_traffic_rates([1.0, 0.0], [[0.0, 0.5], [0.0, 0.0]])
    assert np.allclose(rates, [1.0, 0.5])
    metrics = jackson_network_metrics([1.0, 0.0], [[0.0, 0.5], [0.0, 0.0]], [2.0, 2.0])
    assert np.allclose(metrics.mean_node_sizes, [1.0, 1.0 / 3.0])
    assert np.isclose(metrics.external_mean_time, 4.0 / 3.0)


def test_kingman_matches_mm1_wait_for_unit_scv():
    assert np.isclose(kingman_mean_wait(1.0, 0.5, 1.0, 1.0), 0.5)


def test_fluid_and_reflected_paths_respect_nonnegative_queue():
    fluid = fluid_queue_path([0.0, 1.0, 3.0], 2.0, [0.0, 3.0], [1.0, 1.0])
    assert np.allclose(fluid, [2.0, 1.0, 5.0])
    reflected = reflected_brownian_path([0.0, 0.5, 1.0], initial=0.0, drift=-1.0, volatility=0.5, rng=np.random.default_rng(2))
    assert np.all(reflected >= -1e-12)
    assert square_root_staffing(100.0, 1.0) == 110
