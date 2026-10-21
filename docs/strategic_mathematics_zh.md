# 战术数学层：信念、风险、补给流、多目标、最优传输、谱图与鲁棒博弈

本实现为原生合法动作增加一个可选的数学先验层。它不修改地图规则、伤害结算、占位和行动点，也不创建新动作。最终动作仍由 `JointTurnPlanner`、CP-SAT/MILP/QUBO 与 MAPF 合法性检查决定。

## 1. 模块结构

| 文件 | 数学能力 |
|---|---|
| `rl/belief_risk.py` | 离散贝叶斯信念、负观测更新、CVaR、熵风险、独立损失卷积 |
| `rl/strategic_flow.py` | 最大流、最小割、多源流、共享容量多商品流 |
| `rl/decision_math.py` | Pareto 前沿、epsilon 字典序、最优传输、谱图、零和博弈 |
| `rl/strategic_math.py` | 状态化顾问，将全部数学结果转换为动作先验 |
| `rl/uncertainty_math.py` | 粒子滤波、信息增益、机会约束、分类与回归共形预测 |
| `rl/control_math.py` | 离散 MPC、Dirichlet 对手模型、Kaplan-Meier 生存分析、最大权匹配 |
| `rl/causal_math.py` | 双重稳健平均处理效应，用于回放和消融评估 |

所有排序和冲突处理都是确定性的，适合固定种子回放。无效概率、负容量、不平衡运输质量、非有限收益和求解失败会显式报错。

## 2. 贝叶斯敌情

隐藏单位使用网格概率分布：

```text
预测：上一时刻位置 -> 相邻可通行格随机转移
校正：已观测位置变为点质量；可见但无人位置的概率清零
```

对应滤波形式为：

$$
b_{t+1}(s')\propto P(o_{t+1}\mid s')\sum_sP(s'\mid s,a_t)b_t(s).
$$

单位字典可用 `visible=false` 或 `hidden=true` 表示未观测。环境若能给出当前可见格，应通过 `strategic_math_context()` 返回 `visible_cells`，这样负观测才能排除这些格点。

## 3. CVaR 尾部风险

顾问把敌军位置概率转成目的格损失分布，并计算上尾条件风险价值：

$$
\operatorname{CVaR}_{\alpha}(L)=
\min_{\eta}\left[\eta+\frac{1}{1-\alpha}\mathbb E(L-\eta)_+\right].
$$

默认 $\alpha=0.8$。这意味着规划器不仅考虑平均受击量，也会惩罚低概率但高损失的落点。最多精确卷积 12 个主要威胁事件，其余事件按期望损失聚合，避免状态数指数增长。

## 4. 补给网络流

可通行格构成容量网络，补给点是多源节点，候选目的格是汇点。顾问使用最大流值衡量补给路径冗余，并保留最小割边用于解释关键粮道。

独立 API 还支持共享边容量的分数多商品流：

$$
\sum_k f^k_{uv}\le c_{uv}.
$$

每类物资或每支部队可以作为一个 commodity。无法满足的需求由显式 `unmet` 变量记录，不能被静默丢弃。

## 5. Pareto 与字典序决策

每个动作使用以下默认目标向量：

```text
(预期伤害, -CVaR, -敌军距离, 补给流量)
```

非支配动作获得 Pareto 奖励。`lexicographic_choice()` 可用于任务硬优先级，例如“主将生存 > 守门 > 输出”，无需把所有目标压进一个难以校准的权重和。

## 6. Wasserstein 最优传输

环境传入一组无归属的阵型目标格时，顾问求解有限 Kantorovich 问题：

$$
\min_{\pi\ge0}\sum_{i,j}\pi_{ij}c_{ij}
$$

并满足源、目标边际。单位质量情况下可提取确定性单位到槽位分配。环境也可以直接传入 `{unit_id: cell}`，跳过重新分配。

## 7. 图拉普拉斯谱

对不超过配置上限的可通行图构造：

$$
L=D-A.
$$

第二特征值记录代数连通度，Fiedler 向量用于识别自然战区分界。靠近谱分割面的候选格获得小幅战略位置先验。独立 API 还提供有效电阻与电阻中心性。

## 8. 局部鲁棒博弈

`solve_zero_sum_game()` 求解有限零和矩阵博弈：

$$
\max_{p\in\Delta}\min_j\sum_i p_iA_{ij}.
$$

返回双方混合策略、博弈值、对偶间隙和每个纯动作的最坏收益。运行时若提供同一单位全部候选动作的完整响应矩阵，顾问会求解混合均衡并把策略概率加入动作先验，同时保留纯动作最坏收益；否则使用“动作伤害减最坏损失”的一步鲁棒近似。

## 9. 运行时启用

旧关卡默认关闭新先验，以保持既有数值和回放：

```python
from rl.runtime_policy import RuntimeBattlePolicy

policy = RuntimeBattlePolicy(enable_strategic_math=True)
```

启用后，后端状态会增加 `+math`。诊断结果位于：

```python
policy.last_strategic_math
policy.strategic_math_error
```

环境可选实现：

```python
def strategic_math_context(actions):
    return {
        "visible_cells": {(x, y), ...},
        "passable_cells": {(x, y), ...},
        "supply_sites": {(x, y), ...},
        "formation_targets": [(x, y), ...],
        "opponent_payoffs": {action_index: [payoff_1, payoff_2, ...]},
    }
```

缺少 `passable_cells` 时，运行时从原生移动代价中取 `cost < 255` 的格点；缺少 `supply_sites` 时读取原生 `supply_info()`。

## 10. 性能边界

- 最大流和谱图只在地图格点数不超过配置上限时自动运行；
- 最优传输和多商品流依赖 SciPy/HiGHS；
- 不对大地图计算全局有效电阻，避免立方复杂度进入逐动作热路径；
- 数学层只输出先验，非法动作仍不可能进入规划器；
- 任何异常都会使运行时禁用本次数学先验并回退到原规划链。

## 11. 验证

```powershell
python -m pytest rl/strategic_mathematics_test.py -q
python -m pytest rl/joint_turn_planner_test.py rl/runtime_policy_test.py -q
```

测试覆盖概率归一化与负观测、CVaR 尾部、多商品共享容量、Pareto 支配、运输边际、谱分割与有效电阻、零和混合均衡、顾问风险降权，以及运行时只选择原生合法动作。

## 12. P0：敌情、风险、侦察与瓶颈

- POMDP 信念：`BayesianGridTracker` 提供精确有限网格滤波；`ParticleBeliefTracker` 用于状态空间过大时的采样近似。
- CMDP 风险：`evaluate_chance_constraint()` 同时返回超限概率、CVaR 和可行性。在线顾问以 `fatal_probability`、`chance_violation` 约束高伤亡动作。
- 信息论侦察：`expected_information_gain()` 计算互信息；在线顾问根据隐藏敌军信念计算目的格的完美探测信息量。
- 战场瓶颈：`CapacityNetwork.max_flow()` 返回最大流及最小割边，供粮道、关隘和撤退路线分析。

## 13. P1：多回合控制与任务分配

- 最优传输：`optimal_transport()` 生成编队到目标阵位的最小总代价搬运方案。
- MPC：`DiscreteMPC.solve()` 在有限时域内计算动作序列，只执行 `first_action`，下一回合用新状态重新求解。
- 对手建模：`DirichletOpponentModel` 按上下文累计敌方行动，输出带先验平滑的后验预测，而不是把少量样本当成确定规律。
- 生存分析：`KaplanMeierEstimator` 从阵亡和删失回放估计生存率及离散危险率。
- 匹配：`maximum_weight_matching()` 为单位、攻击目标、治疗对象和阵位求最大权一对一分配；在线战术槽继续复用 `UnitSlotAllocator`。

## 14. P2：全局优化、群体、可信度与因果

- MILP/CP-SAT：`TacticalOptimizationPortfolio` 在共享动作约束模型上选择 CP-SAT、SciPy MILP 或验证过的 QUBO 回退。
- 谱图论：`SpectralGraph` 输出代数连通度、Fiedler 分割、有效电阻和电阻中心性。
- 均值场博弈：`LatticeMFG` 与 `MultiPopulationLatticeMFG` 用后向 Bellman、前向 Kolmogorov 固定点处理大规模拥堵和多兵种相互作用。
- 共形预测：`SplitConformalClassifier` 输出类别集合，`SplitConformalRegressor` 输出对称区间；二者必须使用独立校准集，不把模型置信度冒充覆盖保证。
- 因果推断：`doubly_robust_ate()` 联合倾向概率与结果模型，评估某个策略模块在回放中的平均因果效应及置信区间。

P1/P2 中需要历史样本的模块不会自动伪造训练数据。对手后验必须来自真实敌方动作，生存曲线必须包含阵亡/删失记录，共形阈值必须来自独立校准集，因果估计必须提供真实处理、结果和倾向概率。

新增验证：

```powershell
python -m pytest rl/priority_mathematics_test.py rl/strategic_mathematics_test.py -q
```
