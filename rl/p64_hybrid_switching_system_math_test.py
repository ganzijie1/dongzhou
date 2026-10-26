import numpy as np

from rl.p64_hybrid_switching_system_math import detect_zeno, minimum_average_dwell_time, saltation_matrix, switching_lyapunov_bound, validate_hybrid_trace


def test_saltation_and_dwell_time_bounds():
    matrix = saltation_matrix([1.0], [-1.0], [1.0])
    assert np.allclose(matrix, [[-1.0]])
    dwell = minimum_average_dwell_time(2.0, 4.0)
    assert np.isclose(switching_lyapunov_bound(1.0, 2.0, 4.0, 1, dwell), 1.0)


def test_hybrid_trace_and_zeno_detection():
    assert validate_hybrid_trace(["move", "stun", "move"], [1.0, 2.0], {("move", "stun"), ("stun", "move")})
    assert detect_zeno([0.0, 0.1, 0.11, 0.111, 0.1111], minimum_interval=0.02, consecutive=3)
