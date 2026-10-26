import numpy as np
import pytest

from rl.p57_timed_automata_petri_math import (
    PetriNet,
    TimedEdge,
    p_invariant_residual,
    run_timed_trace,
    stochastic_race,
)


def test_timed_automaton_enforces_cooldown_guard_and_invariant():
    edges = [
        TimedEdge("Ready", "Cooldown", "cast", {}, {}, ("x",)),
        TimedEdge("Cooldown", "Ready", "ready", {"x": 5.0}, {"x": 5.0}, ("x",)),
    ]
    result = run_timed_trace("Ready", ["x"], {"Cooldown": {"x": 5.0}}, edges, [(0.0, "cast"), (5.0, "ready")])
    assert result.location == "Ready"
    assert np.isclose(result.clocks["x"], 0.0)
    with pytest.raises(ValueError):
        run_timed_trace("Ready", ["x"], {"Cooldown": {"x": 5.0}}, edges, [(0.0, "cast"), (6.0, "ready")])


def test_petri_net_reachability_deadlock_and_token_invariant():
    net = PetriNet.create([[1], [0]], [[0], [1]])
    assert net.reachable_markings([1, 0]) == ((0, 1), (1, 0))
    assert net.deadlocks([1, 0], terminal_markings=[[0, 1]]) == ()
    assert net.deadlocks([1, 0]) == ((0, 1),)
    assert np.allclose(p_invariant_residual(net, [1.0, 1.0]), [0.0])


def test_stochastic_race_with_one_positive_rate_selects_that_transition():
    wait, transition = stochastic_race([0.0, 2.0], np.random.default_rng(3))
    assert wait >= 0.0
    assert transition == 1
