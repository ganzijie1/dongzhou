from rl.p68_supervisory_control_math import is_controllable, is_observable, natural_projection, supervisor_enabled_events, supremal_controllable_sublanguage


def test_supremal_language_removes_unsafe_uncontrollable_prefix():
    plant = {(), ("move",), ("move", "hit"), ("wait",)}
    specification = {(), ("move",), ("wait",)}
    assert not is_controllable(specification, plant, {"hit"})
    supremal = supremal_controllable_sublanguage(specification, plant, {"hit"})
    assert supremal == {(), ("wait",)}


def test_projection_observability_and_supervisor():
    language = {(), ("move",), ("wait",)}
    assert natural_projection(("silent", "move"), {"move"}) == ("move",)
    assert is_observable(language, language, {"move"}, {"move", "wait"})
    assert supervisor_enabled_events((), language, language, {"wait"}) == {"move", "wait"}
