import numpy as np

from rl.p47_blackwell_adversarial_bandit_math import (
    blackwell_action,
    calibration_error,
    global_observability_residual,
    run_exp3,
    swap_regret,
)


def test_exp3_moves_probability_toward_lower_loss_action():
    result = run_exp3(np.tile([0.0, 1.0], (500, 1)), exploration=0.1, seed=7)
    assert result.final_probabilities[0] > 0.9


def test_blackwell_action_pushes_violated_coordinate_down():
    assert blackwell_action([[0.0, 2.0], [2.0, 0.0]], [1.0, -1.0], [0.0, 0.0]) == 0


def test_signal_span_detects_global_observability():
    losses = [[0.0, 1.0], [1.0, 0.0]]
    signals = [np.eye(2), np.eye(2)]
    assert global_observability_residual(losses, signals) < 1e-12


def test_swap_regret_and_calibration_are_explicit():
    losses = [[0.0, 1.0], [1.0, 0.0], [0.0, 1.0]]
    assert np.isclose(swap_regret(losses, [1, 1, 1]), 1.0)
    assert np.isclose(calibration_error([0.0, 1.0], [0.0, 1.0], bins=2), 0.0)
