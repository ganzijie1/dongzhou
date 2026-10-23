import numpy as np

from rl.p10_uncertainty_epistemic_causal_math import (
    CredalSet,
    EpistemicModel,
    MassFunction,
    RankedBeliefState,
    StructuralCausalModel,
    StructuralEquation,
    cognitive_hierarchy,
    expected_value_of_perfect_information,
    expected_value_of_sample_information,
    logit_qre,
)


def test_credal_set_returns_lower_upper_and_maximin_choice():
    credal = CredalSet(
        ("safe", "danger"),
        ({"safe": 0.8, "danger": 0.2}, {"safe": 0.5, "danger": 0.5}),
    )
    assert np.allclose(credal.probability_interval({"danger"}), (0.2, 0.5))
    choice, lower = credal.maximin_action(
        {
            "advance": {"safe": 5.0, "danger": -8.0},
            "hold": {"safe": 1.0, "danger": 1.0},
        }
    )
    assert choice == "hold"
    assert lower["hold"] == 1.0


def test_dempster_shafer_belief_plausibility_and_combination():
    first = MassFunction(
        {"left", "right"},
        {frozenset({"left"}): 0.6, frozenset({"left", "right"}): 0.4},
    )
    second = MassFunction(
        {"left", "right"},
        {frozenset({"right"}): 0.5, frozenset({"left", "right"}): 0.5},
    )
    assert first.belief({"left"}) == 0.6
    assert first.plausibility({"left"}) == 1.0
    combined, conflict = first.combine(second)
    assert np.isclose(conflict, 0.3)
    assert np.isclose(sum(combined.pignistic().values()), 1.0)
    assert combined.belief({"left"}) > combined.belief({"right"})


def test_public_announcement_changes_knowledge():
    model = EpistemicModel(
        ("left", "right"),
        {"left": {"enemy_left"}, "right": set()},
        {"scout": {"left": {"left", "right"}, "right": {"left", "right"}}},
    )
    assert not model.knows("scout", "left", "enemy_left")
    updated = model.public_announcement("enemy_left")
    assert updated.worlds == ("left",)
    assert updated.knows("scout", "left", "enemy_left")


def test_ranked_agm_revision_and_contraction():
    state = RankedBeliefState(
        ("left", "right", "none"), {"left": 0, "right": 2, "none": 1}
    )
    revised = state.revise(lambda world: world == "right")
    assert revised.most_plausible == frozenset({"right"})
    contracted = revised.contract(lambda world: world == "right")
    assert not contracted.accepts(lambda world: world == "right")


def test_qre_and_cognitive_hierarchy_return_probabilities():
    row = [[1.0, -1.0], [-1.0, 1.0]]
    column = [[-1.0, 1.0], [1.0, -1.0]]
    qre = logit_qre(row, column, precision=2.0)
    assert qre.converged
    assert np.allclose(qre.row_strategy, [0.5, 0.5], atol=1e-7)
    assert np.allclose(qre.column_strategy, [0.5, 0.5], atol=1e-7)
    hierarchy = cognitive_hierarchy(row, column, maximum_level=4)
    assert np.isclose(hierarchy.level_weights.sum(), 1.0)
    assert np.isclose(hierarchy.row_strategy.sum(), 1.0)
    assert np.isclose(hierarchy.column_strategy.sum(), 1.0)


def test_scm_do_intervention_and_unit_level_counterfactual():
    model = StructuralCausalModel(
        {
            "position": StructuralEquation(
                ("orders", "terrain"),
                lambda parents, _exo: parents["orders"] + parents["terrain"],
            ),
            "damage": StructuralEquation(
                ("position", "enemy"),
                lambda parents, _exo: 2.0 * parents["position"] + parents["enemy"],
            ),
        }
    )
    exogenous = {"orders": 1.0, "terrain": 2.0, "enemy": 3.0}
    factual = model.simulate(exogenous)
    counterfactual = model.counterfactual(exogenous, {"position": 0.0})
    assert factual["damage"] == 9.0
    assert counterfactual["damage"] == 3.0
    ate = model.average_treatment_effect(
        (exogenous, {**exogenous, "enemy": 5.0}),
        treatment="position",
        control_value=0.0,
        treated_value=1.0,
        outcome="damage",
    )
    assert ate == 2.0


def test_perfect_and_sample_information_value_are_consistent():
    prior = {"left": 0.5, "right": 0.5}
    utility = {
        "guard_left": {"left": 4.0, "right": 0.0},
        "guard_right": {"left": 0.0, "right": 4.0},
    }
    perfect = expected_value_of_perfect_information(prior, utility)
    sample = expected_value_of_sample_information(
        prior,
        utility,
        {
            "left_report": {"left": 0.8, "right": 0.2},
            "right_report": {"left": 0.2, "right": 0.8},
        },
    )
    assert perfect.baseline_value == 2.0
    assert perfect.value_of_information == 2.0
    assert 0.0 < sample.value_of_information < perfect.value_of_information
