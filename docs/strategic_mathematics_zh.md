# 战术数学层：信念、风险、补给流、多目标、最优传输、谱图与鲁棒博弈

本实现为原生合法动作增加一个可选的数学先验层。它不修改地图规则、伤害结算、占位和行动点，也不创建新动作。最终动作仍由 `JointTurnPlanner`、CP-SAT/MILP/QUBO 与 MAPF 合法性检查决定。

## 1. 模块结构

| 文件 | 数学能力 |
|---|---|
| `rl/belief_risk.py` | 离散贝叶斯信念、负观测更新、CVaR、熵风险、独立损失卷积 |
| `rl/strategic_flow.py` | 最大流、最小割、多源流、共享容量多商品流 |
| `rl/decision_math.py` | Pareto 前沿、epsilon 字典序、最优传输、谱图、零和博弈 |
| `rl/strategic_math.py` | 状态化顾问，将全部数学结果转换为动作先验 |

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
