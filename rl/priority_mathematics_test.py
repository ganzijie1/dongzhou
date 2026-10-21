"""Regression tests for the P0/P1/P2 mathematical capability set."""

from __future__ import annotations

from math import isclose, isinf

from rl.causal_math import doubly_robust_ate
from rl.control_math import (
    DirichletOpponentModel,
    DiscreteMPC,
    KaplanMeierEstimator,
    maximum_weight_matching,
)
from rl.uncertainty_math import (
    ParticleBeliefTracker,
    SplitConformalClassifier,
    SplitConformalRegressor,
    evaluate_chance_constraint,
    expected_information_gain,
    shannon_entropy,
)


def test_entropy_and_perfect_scout_information_gain() -> None:
    assert isclose(shannon_entropy((0.5, 0.5)), 1.0)
    information = expected_information_gain(
        {"left": 0.5, "right": 0.5},
        {
            "seen": {"left": 1.0, "right": 0.0},
            "clear": {"left": 0.0, "right": 1.0},
        },
    )
    assert isclose(information, 1.0)


def test_particle_filter_predicts_and_conditions_hidden_state() -> None:
    tracker = ParticleBeliefTracker({"origin": 1.0}, particle_count=2000, seed=7)
    tracker.predict({"origin": {"left": 0.25, "right": 0.75}})
    assert 0.70 < tracker.distribution["right"] < 0.80
    tracker.update({"left": 0.0, "right": 1.0})
    assert tracker.distribution == {"right": 1.0}


def test_chance_constraint_rejects_excess_tail_probability() -> None:
    result = evaluate_chance_constraint(
        (0.0, 100.0),
        (0.8, 0.2),
        loss_limit=50.0,
        maximum_violation=0.1,
        cvar_alpha=0.9,
    )
    assert isclose(result.violation_probability, 0.2)
    assert isclose(result.cvar, 100.0)
    assert result.feasible is False


def test_discrete_mpc_reaches_goal_over_horizon() -> None:
    controller = DiscreteMPC(horizon=3)
    result = controller.solve(
        0,
        lambda _state, _time: (-1, 1),
        lambda state, action, _time: state + action,
        lambda _state, _action, next_state, _time: abs(3 - next_state),
    )
    assert result.first_action == 1
    assert result.actions == (1, 1, 1)
    assert result.states == (0, 1, 2, 3)
    assert isclose(result.expected_cost, 3.0)


def test_dirichlet_opponent_model_preserves_uncertainty() -> None:
    model = DirichletOpponentModel(("attack", "retreat"), prior=1.0)
    for _ in range(3):
        model.update("low_hp", "attack")
    probabilities = model.predictive("low_hp")
    assert isclose(probabilities["attack"], 0.8)
    assert isclose(probabilities["retreat"], 0.2)
    assert isclose(model.expected_payoff("low_hp", {"attack": 10.0}), 8.0)


def test_kaplan_meier_handles_events_and_censoring() -> None:
    estimator = KaplanMeierEstimator().fit(
        (1.0, 2.0, 2.0, 3.0),
        (True, True, False, True),
    )
    assert isclose(estimator.survival_at(1.0), 0.75)
    assert isclose(estimator.hazard_at(2.0), 1.0 / 3.0)
    assert isclose(estimator.survival_at(3.0), 0.0)


def test_maximum_weight_matching_assigns_distinct_tasks() -> None:
    result = maximum_weight_matching(
        ("infantry", "archer"),
        ("gate", "ridge"),
        {
            ("infantry", "gate"): 9.0,
            ("infantry", "ridge"): 1.0,
            ("archer", "gate"): 2.0,
            ("archer", "ridge"): 8.0,
        },
    )
    assert result.assignments == {"infantry": "gate", "archer": "ridge"}
    assert isclose(result.utility, 17.0)

    optional = maximum_weight_matching(
        ("wounded", "fresh"),
        ("charge", "hold"),
        {
            ("wounded", "charge"): -8.0,
            ("wounded", "hold"): -1.0,
            ("fresh", "charge"): 6.0,
            ("fresh", "hold"): 2.0,
        },
    )
    assert optional.assignments == {"fresh": "charge"}
    assert isclose(optional.utility, 6.0)


def test_split_conformal_classification_and_regression() -> None:
    classifier = SplitConformalClassifier().fit(
        ((0.9, 0.1), (0.8, 0.2), (0.1, 0.9), (0.2, 0.8)),
        (0, 0, 1, 1),
    )
    assert classifier.predict_sets(((0.95, 0.05),), alpha=0.25) == (frozenset({0}),)
    regressor = SplitConformalRegressor().fit((2.0, 4.0, 6.0), (1.0, 5.0, 7.0))
    assert regressor.intervals((10.0,), alpha=0.25) == ((9.0, 11.0),)
    low_sample_interval = regressor.intervals((10.0,), alpha=0.1)[0]
    assert isinf(low_sample_interval[0]) and isinf(low_sample_interval[1])
    assert low_sample_interval[0] < 0.0 < low_sample_interval[1]


def test_doubly_robust_estimator_recovers_known_effect() -> None:
    estimate = doubly_robust_ate(
        outcomes=(0.0, 2.0, 0.0, 2.0),
        treatments=(0, 1, 0, 1),
        propensities=(0.5, 0.5, 0.5, 0.5),
        predicted_treated=(2.0, 2.0, 2.0, 2.0),
        predicted_control=(0.0, 0.0, 0.0, 0.0),
    )
    assert isclose(estimate.effect, 2.0)
    assert isclose(estimate.standard_error, 0.0)
    assert estimate.confidence_interval == (2.0, 2.0)


def main() -> None:
    tests = [
        test_entropy_and_perfect_scout_information_gain,
        test_particle_filter_predicts_and_conditions_hidden_state,
        test_chance_constraint_rejects_excess_tail_probability,
        test_discrete_mpc_reaches_goal_over_horizon,
        test_dirichlet_opponent_model_preserves_uncertainty,
        test_kaplan_meier_handles_events_and_censoring,
        test_maximum_weight_matching_assigns_distinct_tasks,
        test_split_conformal_classification_and_regression,
        test_doubly_robust_estimator_recovers_known_effect,
    ]
    for test in tests:
        test()
    print(f"priority mathematics ok: {len(tests)} tests")


if __name__ == "__main__":
    main()
