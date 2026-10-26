import numpy as np

from rl.p49_dynamic_mechanism_elicitation_math import (
    dynamic_ic_audit,
    dynamic_pivot_payment,
    expected_binary_score,
    participation_audit,
    peer_prediction_payments,
    promised_utility,
)


def test_promised_utility_combines_current_and_discounted_continuation():
    assert np.isclose(promised_utility([1.0, 3.0], [4.0, 2.0], [0.25, 0.75], discount=0.5), 3.75)


def test_dynamic_ic_and_participation_audits_report_slack():
    audit = dynamic_ic_audit([[3.0, 2.0], [1.0, 4.0]])
    assert audit.incentive_compatible
    slack, participates = participation_audit([3.0, 1.0], [2.0, 1.5])
    assert np.allclose(slack, [1.0, -0.5])
    assert not participates


def test_proper_scores_reward_truthful_binary_report_in_expectation():
    truth = expected_binary_score(0.7, 0.7, rule="brier")
    lie = expected_binary_score(0.7, 0.2, rule="brier")
    assert truth > lie


def test_peer_prediction_uses_report_conditioned_beliefs_and_pivot_externality():
    beliefs = [[0.8, 0.2], [0.1, 0.9]]
    truthful = peer_prediction_payments([1, 1], beliefs)
    inconsistent = peer_prediction_payments([0, 1], beliefs)
    assert truthful.sum() > inconsistent.sum()
    assert np.isclose(dynamic_pivot_payment(10.0, 7.5), 2.5)
