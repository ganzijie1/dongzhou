import numpy as np

from rl.p69_contract_barrier_composition_math import AssumeGuaranteeContract, allocate_risk_budget, conditional_contract_failure, independent_risk_bound, sampled_barrier_certificate, union_risk_bound


def test_contract_saturation_and_refinement():
    universe = frozenset({"safe", "unsafe", "absent"})
    broad = AssumeGuaranteeContract(frozenset({"safe", "unsafe"}), frozenset({"safe"}), universe)
    refined = AssumeGuaranteeContract(frozenset({"safe", "unsafe", "absent"}), frozenset({"safe"}), universe)
    assert refined.refines(broad)
    assert broad.accepts({"absent"}) and not broad.accepts({"unsafe"})


def test_barrier_and_probability_composition():
    assert sampled_barrier_certificate([-1, 0], [1], [-0.1, 0])
    assert np.isclose(union_risk_bound([0.1, 0.2]), 0.3)
    assert np.isclose(independent_risk_bound([0.1, 0.2]), 0.28)
    assert np.isclose(conditional_contract_failure(0.1, 0.2), 0.28)
    assert np.allclose(allocate_risk_budget(0.3, [1, 2]), [0.1, 0.2])
