from rl.p79_decentralized_supervisory_control_math import (
    coobservability_violations,
    current_state_opacity,
    fuse_local_decisions,
    is_codiagnosable,
    is_coobservable,
    is_diagnosable,
)


def test_coobservability_finds_ambiguous_local_veto():
    plant = [(), ("u",), ("v",), ("u", "go"), ("v", "go")]
    specification = [(), ("u",), ("v",), ("v", "go")]
    observable = [{"go"}]
    controllable = [{"go"}]
    assert not is_coobservable(specification, plant, observable, controllable)
    assert coobservability_violations(
        specification, plant, observable, controllable
    )[0].event == "go"


def test_decision_fusion_supports_both_architectures():
    decisions = [{"move": True, "cast": False}, {"move": False}]
    assert fuse_local_decisions(decisions) == {"move": False, "cast": False}
    assert fuse_local_decisions(decisions, architecture="disjunctive") == {
        "move": True,
        "cast": False,
    }


def test_diagnosability_and_codiagnosability_depend_on_observers():
    language = [(), ("seen",), ("fault",), ("fault", "alarm")]
    assert not is_diagnosable(language, {"seen", "alarm"}, "fault")
    assert is_codiagnosable(language, [{"fault"}, {"seen", "alarm"}], "fault")


def test_current_state_opacity_reports_revealing_observations():
    opaque = current_state_opacity(
        {("a",): "secret", ("a", "hidden"): "public"},
        {"secret"},
        {"a"},
    )
    leaking = current_state_opacity(
        {("a",): "secret", ("b",): "public"},
        {"secret"},
        {"a", "b"},
    )
    assert opaque.opaque and not opaque.leaking_observations
    assert not leaking.opaque and leaking.leaking_observations == frozenset({("a",)})
