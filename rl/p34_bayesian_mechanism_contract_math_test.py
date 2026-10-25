import numpy as np

from rl.p34_bayesian_mechanism_contract_math import (
    audit_two_player_direct_mechanism,
    myerson_iid_single_item_auction,
    optimal_hidden_action_contract,
    regular_virtual_value,
    vcg_clarke_pivot,
)


def test_vcg_internalizes_externality():
    result = vcg_clarke_pivot([[10.0, 0.0], [0.0, 7.0]])
    assert result.outcome == 0
    assert np.allclose(result.payments, [7.0, 0.0])
    assert np.allclose(result.utilities, [3.0, 0.0])


def test_myerson_iid_regular_auction_is_second_price_with_reserve():
    result = myerson_iid_single_item_auction([3.0, 8.0, 5.0], reserve=4.0)
    assert result.winner == 1
    assert result.revenue == 5.0
    assert np.allclose(result.payments, [0.0, 5.0, 0.0])
    assert np.allclose(regular_virtual_value([0.5], [0.5], [1.0]), [0.0])


def test_second_price_direct_mechanism_is_dsic_bic_and_ir():
    prior = np.full((2, 2), 0.25)
    allocation = np.zeros((2, 2, 3))
    payments = np.zeros((2, 2, 2))
    values = [1.0, 2.0]
    for first_type, first_bid in enumerate(values):
        for second_type, second_bid in enumerate(values):
            if first_bid >= second_bid:
                allocation[first_type, second_type, 0] = 1.0
                payments[0, first_type, second_type] = second_bid
            else:
                allocation[first_type, second_type, 1] = 1.0
                payments[1, first_type, second_type] = first_bid
    first_values = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
    second_values = np.array([[0.0, 1.0, 0.0], [0.0, 2.0, 0.0]])
    audit = audit_two_player_direct_mechanism(
        prior, allocation, payments, (first_values, second_values)
    )
    assert audit.dsic and audit.bic and audit.interim_ir
    assert audit.minimum_dsic_slack >= -1e-10


def test_hidden_action_contract_rewards_informative_success():
    result = optimal_hidden_action_contract(
        [[0.8, 0.2], [0.2, 0.8]],
        [0.0, 1.0],
        [0.0, 5.0],
        outside_option=0.0,
    )
    assert result.target_action == 1
    assert result.wages[1] > result.wages[0]
    assert result.principal_utility > 0.0
    assert np.min(result.incentive_slacks) >= -1e-9
