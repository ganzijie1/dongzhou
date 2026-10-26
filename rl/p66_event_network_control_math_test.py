import numpy as np

from rl.p66_event_network_control_math import AgeOfInformationTracker, data_rate_lower_bound, event_trigger, packet_hold_update, uniform_quantize


def test_aoi_discards_stale_generation_timestamp():
    tracker = AgeOfInformationTracker()
    assert np.isclose(tracker.receive(2.0, 3.0), 1.0)
    assert np.isclose(tracker.receive(1.0, 4.0), 2.0)


def test_quantization_trigger_and_packet_hold():
    quantized, saturated = uniform_quantize([-2.0, 0.0, 2.0], bits=2, limit=1.0)
    assert np.array_equal(saturated, [True, False, True])
    assert np.all(np.abs(quantized) <= 1.0)
    assert event_trigger([1.0, 0.0], [1.0, 0.0], relative_threshold=0.5)
    assert np.array_equal(packet_hold_update([1], [2], False), [1])


def test_data_rate_uses_only_unstable_modes():
    assert np.isclose(data_rate_lower_bound([2.0, 0.5, -4.0]), 3.0)
