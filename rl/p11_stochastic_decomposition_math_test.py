import numpy as np

from rl.p11_stochastic_decomposition_math import (
    InventoryStage,
    MasterColumn,
    Polyhedron,
    ScenarioLinearNode,
    ScenarioNode,
    ScenarioTree,
    TwoStageScenario,
    chvatal_gomory_cut,
    column_generation,
    minimal_cover_cut,
    sddp_inventory,
    solve_binary_linear_program,
    solve_multistage_scenario_tree_lp,
    solve_two_stage_benders,
    solve_two_stage_stochastic_lp,
)


def _recourse_scenarios():
    return (
        TwoStageScenario(
            "low",
            0.5,
            np.array([4.0]),
            np.array([[1.0]]),
            np.array([[1.0]]),
            np.array([1.0]),
        ),
        TwoStageScenario(
            "high",
            0.5,
            np.array([4.0]),
            np.array([[1.0]]),
            np.array([[1.0]]),
            np.array([3.0]),
        ),
    )


def test_scenario_tree_probabilities_and_paths():
    tree = ScenarioTree(
        (
            ScenarioNode("root", 0, None, 1.0),
            ScenarioNode("rain", 1, "root", 0.25),
            ScenarioNode("dry", 1, "root", 0.75),
            ScenarioNode("flood", 2, "rain", 1.0),
            ScenarioNode("calm", 2, "dry", 1.0),
        )
    )
    assert tree.probability("flood") == 0.25
    assert tree.path("flood") == ("root", "rain", "flood")
    assert set(tree.leaves) == {"flood", "calm"}


def test_multistage_scenario_tree_lp_shares_history_decisions():
    tree = ScenarioTree(
        [
            ScenarioNode("root", 0, None, 1.0),
            ScenarioNode("low", 1, "root", 0.5),
            ScenarioNode("high", 1, "root", 0.5),
        ]
    )
    empty_local = np.zeros((0, 1))
    models = [
        ScenarioLinearNode(
            "root",
            np.array([1.2]),
            empty_local,
            np.zeros(0),
            np.zeros((0, 0)),
            np.zeros((0, 1)),
            np.zeros(0),
            ((0.0, None),),
        ),
        ScenarioLinearNode(
            "low",
            np.array([2.0]),
            empty_local,
            np.zeros(0),
            np.array([[-1.0]]),
            np.array([[-1.0]]),
            np.array([-1.0]),
            ((0.0, None),),
        ),
        ScenarioLinearNode(
            "high",
            np.array([2.0]),
            empty_local,
            np.zeros(0),
            np.array([[-1.0]]),
            np.array([[-1.0]]),
            np.array([-3.0]),
            ((0.0, None),),
        ),
    ]
    result = solve_multistage_scenario_tree_lp(tree, models)
    assert np.isclose(result.decisions["root"][0], 1.0)
    assert np.isclose(result.decisions["low"][0], 0.0)
    assert np.isclose(result.decisions["high"][0], 2.0)
    assert np.isclose(result.objective, 3.2)


def test_deterministic_equivalent_and_benders_agree():
    scenarios = _recourse_scenarios()
    direct = solve_two_stage_stochastic_lp(
        [1.0], [], [], scenarios, first_bounds=[(0.0, 3.0)]
    )
    decomposed = solve_two_stage_benders(
        [1.0], [], [], scenarios, first_bounds=[(0.0, 3.0)]
    )
    assert np.allclose(direct.first_stage, [3.0])
    assert np.allclose(decomposed.first_stage, direct.first_stage)
    assert np.isclose(decomposed.objective, direct.objective)
    assert decomposed.cut_count > 0


def test_column_generation_adds_negative_reduced_cost_pattern():
    initial = (
        MasterColumn("single-a", 1.0, np.array([1.0, 0.0])),
        MasterColumn("single-b", 1.0, np.array([0.0, 1.0])),
    )

    def pricing(dual):
        combined = MasterColumn("combined", 1.5, np.array([1.0, 1.0]))
        return (
            combined if combined.cost - dual @ combined.coefficients < -1e-9 else None
        )

    result = column_generation([1.0, 1.0], initial, pricing)
    assert np.isclose(result.objective, 1.5)
    assert result.weights == {"combined": 1.0}
    assert len(result.columns) == 3


def test_inventory_sddp_learns_deterministic_order():
    result = sddp_inventory(
        (InventoryStage((2.0,), (1.0,), 1.0, 0.0, 10.0, 3.0),),
        0.0,
        iterations=3,
        terminal_holding=0.0,
        terminal_shortage=0.0,
    )
    assert np.isclose(result.first_order, 2.0)
    assert np.isclose(result.lower_bound, 2.0)


def test_polyhedron_vertices_and_chvatal_gomory_cut():
    square = Polyhedron(
        np.array([[-1.0, 0.0], [0.0, -1.0], [1.0, 0.0], [0.0, 1.0]]),
        np.array([0.0, 0.0, 1.0, 1.0]),
    )
    assert len(square.vertices()) == 4
    cut = chvatal_gomory_cut([[0.5, 0.5]], [0.75], [2.0])
    assert np.allclose(cut.coefficients, [1.0, 1.0])
    assert cut.rhs == 1.0


def test_cover_cut_and_binary_solution():
    cover, cut = minimal_cover_cut([2.0, 2.0, 2.0], 3.0, [0.8, 0.8, 0.1])
    assert cover == (0, 1)
    assert cut.violation([0.8, 0.8, 0.1]) > 0.0
    solved = solve_binary_linear_program(
        [3.0, 2.0, 1.0], [[2.0, 2.0, 2.0]], [3.0], maximize=True
    )
    assert solved.objective == 3.0
