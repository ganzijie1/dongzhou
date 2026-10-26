import numpy as np

from rl.p43_pdmp_math import (
    controlled_hjb_backup,
    linear_hazard_event_time,
    next_event_time_by_hazard,
    pdmp_generator,
)


def test_constant_hazard_inversion_matches_exponential_clock():
    event = next_event_time_by_hazard(lambda t: [t], lambda state: 2.0, np.exp(-4.0), max_time=3.0)
    assert np.isclose(event, 2.0)
    assert np.isclose(linear_hazard_event_time(2.0, 0.0, np.exp(-4.0)), 2.0)


def test_hazard_returns_none_when_horizon_is_too_short():
    assert next_event_time_by_hazard(lambda t: [t], lambda state: 1.0, np.exp(-2.0), max_time=1.0) is None


def test_pdmp_generator_combines_flow_and_jump_terms():
    value = pdmp_generator([2.0], [3.0], 0.5, 4.0, [2.0, 8.0], [0.25, 0.75])
    assert np.isclose(value, 7.25)


def test_hjb_backup_selects_minimum_generator_action():
    result = controlled_hjb_backup([1.0, 0.5], [0.0, 1.0], [2.0, 0.0], [0.0, 10.0], 1.0)
    assert np.allclose(result.action_values, [-1.0, 1.5])
    assert result.action == 0
