import numpy as np

from rl.p39_quantum_game_math import (
    chsh_optimal_quantum_strategy,
    density_matrix,
    depolarizing_channel,
    ewl_classical_cooperate,
    ewl_classical_defect,
    ewl_quantum_strategy,
    ewl_two_player_game,
    finite_quantum_nash_diagnostic,
    partial_trace,
)


def test_bell_state_partial_trace_is_maximally_mixed():
    bell = density_matrix([1.0, 0.0, 0.0, 1.0])
    assert np.allclose(partial_trace(bell, (2, 2), trace_out=0), np.eye(2) / 2.0)
    assert np.allclose(partial_trace(bell, (2, 2), trace_out=1), np.eye(2) / 2.0)


def test_ewl_recovers_classical_outcomes_and_quantum_cooperation():
    first = np.array([[3.0, 0.0], [5.0, 1.0]])
    second = first.T
    classical = ewl_two_player_game(
        ewl_classical_defect(),
        ewl_classical_cooperate(),
        first,
        second,
        entanglement=0.0,
    )
    assert np.allclose(classical.outcome_probabilities, [[0.0, 0.0], [1.0, 0.0]])
    assert np.allclose(classical.expected_payoffs, [5.0, 0.0])
    quantum = ewl_two_player_game(
        ewl_quantum_strategy(),
        ewl_quantum_strategy(),
        first,
        second,
        entanglement=np.pi / 2.0,
    )
    assert np.allclose(quantum.outcome_probabilities, [[1.0, 0.0], [0.0, 0.0]])
    assert np.allclose(quantum.expected_payoffs, [3.0, 3.0])


def test_chsh_strategy_reaches_tsirelson_win_rate_without_signalling():
    result = chsh_optimal_quantum_strategy()
    assert np.isclose(result.winning_probability, np.cos(np.pi / 8.0) ** 2)
    assert result.no_signalling_residual < 1e-12


def test_depolarization_reduces_purity():
    pure = density_matrix([1.0, 0.0])
    noisy = depolarizing_channel(pure, probability=0.5)
    assert np.trace(noisy @ noisy).real < np.trace(pure @ pure).real
    assert np.allclose(noisy, np.diag([0.75, 0.25]))


def test_finite_quantum_strategy_nash_diagnostic_reports_deviation_regret():
    payoffs = np.array(
        [
            [[2.0, 0.0], [3.0, 1.0]],
            [[2.0, 3.0], [0.0, 1.0]],
        ]
    )
    cooperative = finite_quantum_nash_diagnostic(payoffs, (0, 0))
    defect = finite_quantum_nash_diagnostic(payoffs, (1, 1))
    assert not cooperative.is_nash
    assert np.allclose(cooperative.regrets, [1.0, 1.0])
    assert defect.is_nash
