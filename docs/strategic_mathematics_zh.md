# 战术数学层：从可信决策到拓扑、博弈与敏感度分析

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
| `rl/safety_robust_math.py` | HJ 鲁棒可达性、控制屏障函数、Wasserstein DRO、网络阻断 |
| `rl/online_selection_math.py` | 次模选择、CUSUM 变点、UCB1、STL 时序逻辑 |
| `rl/advanced_game_math.py` | Stackelberg 承诺博弈、有限扩展式博弈 CFR |
| `rl/topology_flow_math.py` | 排队网络、Hodge 分解、持久同调、离散共形映射 |
| `rl/sensitivity_math.py` | 精确 Shapley、Sobol 全局敏感度、GEV 极值理论 |
| `rl/p5_decision_math.py` | POMCP、嵌套 CVaR、随机博弈、模型检验、离线评估、DMD/EDMD |
| `rl/p6_structure_math.py` | 细胞层、Morse/Reeb、Schrodinger 桥、信息几何、热带代数、拟阵 |
| `rl/p6_games_dynamics.py` | 演化/合作博弈、最大熵逆强化学习、随机混杂系统 |
| `rl/advanced_lattice_geometry.py` | 离散微积分、Poisson、各向异性测地线、形态重建与拓扑保持细化 |
| `rl/graph_dynamics.py` | 连续图动力学、DeGroot 共识、Altafini 有符号网络与结构平衡 |
| `rl/chapter1_planning_math.py` | 随机最短路、POSG 信念更新、事件触发控制、Fast Marching |
| `rl/chapter1_structure_fields.py` | 超图 Laplacian、势场、反应扩散、相场、有限群表示与等变投影 |
| `rl/chapter1_reliability_rare_math.py` | 吸收链、更新过程、系统可靠性、重要性采样、大偏差与有限约束验证 |

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
        "reachability_values": {(x, y): robust_reachability, ...},
        "barrier_values": {(x, y): safety_margin, ...},
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

## 15. P3：安全、鲁棒、选择与在线适应

- Hamilton-Jacobi 可达性：`hamilton_jacobi_reachability()` 对有限状态的控制-扰动博弈做后向递推。某状态只有在存在一个控制，使所有允许扰动后的状态都进入上一层胜集时才算鲁棒可达。
- 控制屏障函数：`control_barrier_filter()` 使用离散条件 $h(x^+)\ge(1-\alpha)h(x)$ 标出安全动作和屏障裕量。在线顾问可读取 `barrier_values`，按违规量惩罚候选动作。
- Wasserstein 分布鲁棒优化：`wasserstein_worst_case_expectation()` 在有限 1-Wasserstein 球内求最坏期望损失，同时返回对抗分布与运输计划，便于审计保守性来自哪里。
- 双层网络阻断：`solve_network_interdiction()` 枚举小规模候选边，外层选择阻断，内层重新求最大流；候选边超过配置上限会拒绝精确求解，避免指数复杂度误入热路径。
- 次模优化：`greedy_submodular_maximize()` 为侦察点、技能覆盖和传感器布置提供单调次模目标下的贪心选择，并返回每步边际收益。
- 在线变化与学习：`CUSUMChangeDetector` 检测敌方策略均值变化；`UCB1Bandit` 在多个策略臂间做确定性探索-利用。它们只消费实际观测和奖励，不生成虚构样本。
- 时序逻辑：`stl_always()`、`stl_eventually()`、`stl_until()` 和 `TemporalRequirement` 输出定量鲁棒度，用于“全程守住”“时限内到达”“坚持到援军抵达”等约束。

`reachability_values` 与 `barrier_values` 是环境可选上下文。缺失时两项贡献为零，不改变既有决策。数学层仍只调整合法动作的先验，不绕过原生规则。

## 16. P4：博弈、流形拓扑、归因与尾部风险

- Stackelberg 博弈：`solve_stackelberg_game()` 枚举跟随者最优响应并解线性规划，返回乐观破同分假设下的领导者承诺策略。
- 反事实遗憾最小化：`CounterfactualRegretMinimizer` 在有限双人零和扩展式博弈上累计信息集遗憾与平均策略，可表达同时行动、隐藏信息和序贯诱导。
- 排队论：`mm1_queue()` 给出单瓶颈利用率、排队长度和等待时间；`jackson_network()` 解开放 Jackson 网络流量方程。到达率不小于服务率时明确报告不稳定。
- Hodge 分解：`hodge_decomposition()` 将有向边流分为梯度、面旋度与调和分量，用于区分目标驱动推进、局部绕圈和全局环流。
- 持久同调：`persistent_homology()` 对顶点、边、三角形过滤复形计算 $H_0/H_1$ 区间，识别跨尺度稳定的连通分量与包围洞结构。
- 共形几何：`discrete_conformal_map()` 用余切权重调和参数化网格，并报告每个三角形的奇异值畸变；`corridor_modulus()` 量化长宽比。它适合地图参数化和形状比较，不替代碰撞或寻路。
- Shapley 归因：`exact_shapley_values()` 对小规模协作因素做精确子集枚举，满足效率性，解释伤害、地形、补给等因素的边际贡献。默认限制参与者数量以控制 $2^n$ 复杂度。
- Sobol 敏感度：`sobol_sensitivity()` 使用独立 Saltelli/Jansen 采样估计一阶与总效应。有限样本估计不强制裁剪到 $[0,1]$，因此采样误差和模型不稳定不会被隐藏。
- 极值理论：`fit_block_maxima()` 拟合 GEV 区块极大值并提供重现水平，只接受有限、非恒定的真实极值样本；它不外推论文或回放中不存在的结论。

P4 方法默认是离线设计、回放解释或低频求解工具。CFR、精确 Shapley、持久同调、Sobol 和 GEV 不进入逐动作热路径。

新增验证：

```powershell
python -m pytest rl/priority_mathematics_test.py rl/strategic_mathematics_test.py rl/p3_p4_mathematics_test.py -q
```

## 17. P5：信念空间规划、动态风险与数据驱动动力学

- POMCP：`POMCPPlanner` 从根信念抽样，用 UCB 在历史树上选择动作，并通过生成模型完成状态转移、观测和回报采样。它返回访问次数、动作价值与最佳动作；样本数有限时不声称得到精确 POMDP 最优策略。
- 时间一致动态风险：`nested_cvar_mdp()` 逐层嵌套条件 CVaR，而不是只在整条轨迹末端计算一次静态 CVaR。损失递推为

$$
V_t(s)=\min_a\operatorname{CVaR}_{\alpha}\left(c_t(s,a,S_{t+1})+V_{t+1}(S_{t+1})\mid s,a\right).
$$

- 零和随机博弈：`solve_discounted_zero_sum_stochastic_game()` 迭代 Shapley 算子，并在每个状态调用矩阵博弈求解器，输出状态价值和双方混合策略。
- 概率模型检验：`dtmc_reachability()` 计算有限或无限时域 reach-avoid 概率，并在可达条件满足时求期望命中时间。它只接受显式 DTMC，不把经验频率自动当作已验证转移概率。
- 最优停止：`finite_horizon_optimal_stopping()` 比较立即停止收益与继续价值，返回每个时刻/状态的停止集合。
- 镜像下降：`ExponentiatedGradient` 在概率单纯形上做熵正则更新，保持非负与归一化。
- 序列双重稳健离线评估：`sequential_doubly_robust_ope()` 组合重要性比与状态/动作价值基线。行为策略概率、目标策略概率、奖励和基线都必须来自真实记录或独立估计；实现不会补造缺失日志。
- Koopman/DMD：`dynamic_mode_decomposition()` 从连续快照拟合线性演化模态；`extended_dynamic_mode_decomposition()` 在用户提供的观测字典上拟合 Koopman 近似。秩截断会显式保留，不能把短轨迹的拟合模态解释成已证实的物理规律。

P5 默认用于信念规划、低频策略求解、回放评估与动力学辨识。只有经过预算和回放验证的结果才适合转换成在线先验。

## 18. P6：层、拓扑结构、熵输运与高阶博弈

- 细胞层与 Sheaf Laplacian：`CellularSheaf` 为顶点/边定义 stalk 和限制映射。余边界矩阵为 $\delta$，层拉普拉斯为

$$
L_{\mathcal F}=\delta^{\mathsf T}\delta.
$$

  `consistency_energy()` 计算局部信息不一致度，`global_sections()` 求全局一致截面，`diffuse()` 用 $\exp(-tL_{\mathcal F})$ 做一致性扩散。
- 离散 Morse 与 Reeb 图：`discrete_morse_critical_points()` 根据 lower/upper link 连通分量识别极小、鞍点和极大；`discrete_reeb_graph()` 将相同标量水平的连通分量压缩成商图，用于地形关键结构和通道层级分析。
- Schrodinger 桥：`schrodinger_bridge()` 对严格正的有限参考核做 Sinkhorn 缩放，寻找满足起止边缘分布的最小相对熵耦合。零质量或稀疏支持问题需先用专门的支持约束求解器处理。
- 信息几何：分类分布提供 Fisher 信息矩阵、Fisher-Rao 距离、KL 散度和自然梯度更新。所有概率在计算前归一化，但零概率被拒绝，避免对数和度量奇异性被静默掩盖。
- 热带代数：`max_plus_matmul()`、`max_plus_power()` 与 `max_plus_cycle_mean()` 表达最大加法动态规划和关键循环平均权重，可用于最长时序、瓶颈循环与离散事件系统分析。
- 拟阵约束：`matroid_greedy()` 对合法拟阵求精确最大权独立集；`submodular_matroid_greedy()` 在拟阵约束下做单调次模贪心并返回逐步边际收益。独立性由外部 oracle 决定，错误 oracle 不会被数学层修复。
- 演化与合作博弈：`replicator_dynamics()` 保持种群状态在概率单纯形内；`least_core_allocation()` 最小化最大联盟 excess；`nucleolus_allocation()` 对小型有限博弈逐层做 excess 的字典序最小化。
- 最大熵逆强化学习：`maximum_entropy_irl()` 从等长状态示范估计线性奖励和软策略。它只解释给定特征与已知转移下的示范，不把相关性写成因果偏好。
- 随机混杂系统：`StochasticHybridSystem` 将连续流、守卫条件、概率模式切换和 reset map 组合，并提供蒙特卡洛可达概率估计。概率结果必须连同样本量和随机种子解释。

P6 是结构建模与离线分析层，不自动接管原生行动。Sheaf 限制映射、联盟价值、IRL 特征、混杂流和转移概率均要求调用者提供有来源的数据。

## 19. 格点几何深化

`advanced_lattice_geometry.py` 在已有坐标、射线、形态学、数字拓扑和 MAPF 合同之上增加以下能力：

- `DiscreteFieldCalculus`：不规则方格域上的梯度、散度、图拉普拉斯与 Dirichlet 能量；外边界采用缺边的 Neumann 语义。
- `solve_lattice_poisson()`：在四邻接域上求带 Dirichlet 边界的离散 Poisson 方程，并返回最大线性残差。每个连通分量必须至少有一个边界格。
- `anisotropic_geodesic_distance()`：用每格对称正定度量张量计算各向异性测地距离和前驱路径；这是格点 Dijkstra 的 Eikonal 近似，不冒充连续快速行进法的高阶精度。
- `signed_euclidean_distance()`：有限域上“内部为正、外部为负”的精确格心欧氏距离。
- `morphological_reconstruction()`：受 mask 约束的测地膨胀，可删除与 marker 不连通的伪区域。
- `topology_preserving_thinning()`：Zhang-Suen 数字细化，保留 8 邻接前景的拓扑骨架。
- `lattice_topology_signature()`：统一输出面积、数字周长、连通分量、洞数与欧拉特征 $\chi=\beta_0-\beta_1$。

这些函数使用与 `lattice_geometry.py` 相同的 `(x, y)` 格点表示，可直接消费原生可通行格集合，但不会改变碰撞、地形代价或单位占位规则。

## 20. P5/P6 与格点回归

```powershell
python -m pytest `
  rl/p5_decision_math_test.py `
  rl/p6_structure_math_test.py `
  rl/p6_games_dynamics_test.py `
  rl/advanced_lattice_geometry_test.py -q
```

定向回归覆盖 POMCP 行动选择、尾部风险、随机博弈、DTMC 可达性、序列 DR、DMD/EDMD、层一致性、Morse/Reeb、熵桥、信息几何、热带循环均值、拟阵、核仁、IRL、混杂切换以及格点数值/拓扑不变量。完整 RL 测试仍用于检查与既有规划器的兼容性。

## 21. 图动力学、DeGroot 与 Altafini

`graph_dynamics.py` 统一采用 $A_{ij}$ 表示节点 $j$ 对节点 $i$ 的影响。普通 Laplacian 使用 $L=D-A$，有符号 Laplacian 的度数使用绝对边权：

$$
(D_s)_{ii}=\sum_j|A_{ij}|,\qquad L_s=D_s-A.
$$

- 连续图动力学：`continuous_graph_dynamics()` 使用矩阵指数精确计算指定时刻的 $\dot x=-Lx$。普通图拒绝负权；Altafini 路径显式使用有符号 Laplacian。
- DeGroot：`degroot_dynamics()` 要求非负行随机矩阵，返回完整轨迹、左稳态影响力、共识值、逐步共识误差、谱收缩率和 `ergodic` 诊断。周期矩阵或多重单位特征值不会被误报为收敛。
- 稳态影响力：`stationary_influence()` 求解 $\pi^{\mathsf T}W=\pi^{\mathsf T}$ 与 $\sum_i\pi_i=1$，因此非对称信任网络的极限是加权共识，不假定为算术平均。
- 结构平衡：`structural_balance()` 在有向有符号图上检查是否存在 $\sigma_i\in\{-1,+1\}$，使 $\sigma_iA_{ij}\sigma_j\ge0$，并返回两阵营符号和连通分量。
- Altafini：`continuous_altafini_dynamics()` 与 `discrete_altafini_dynamics()` 分别处理连续和离散有符号传播。平衡网络返回 gauge 轨迹与二部共识误差；非平衡网络只报告状态范数，不虚构阵营划分。
- 外部控制：`controlled_degroot_dynamics()` 实现 $x_{k+1}=Wx_k+Bu_k$，可选状态裁剪用于有限士气区间。裁剪使系统变为非线性，线性共识结论不能直接沿用。

这些方法适合生成士气、命令、恐慌、情报判断和协同权重等低频状态。边权必须来自明确规则、日志估计或校准模型；负边应表示真正的反向状态作用，而不是普通伤害减益。传播结果只能作为动作先验，最终行动仍由 CP-SAT/MILP/QUBO、MAPF 和原生规则验证。

新增验证：

```powershell
python -m pytest rl/graph_dynamics_test.py -q
```

## 22. 第一章数学能力全覆盖

第一章列出的 20 类数学已映射到可执行实现。已有能力直接复用，缺失能力由三个 `chapter1_*` 模块补齐：

| 场景 | 数学 | 实现 |
|---|---|---|
| 多单位联合行动 | CP-SAT、MILP、QUBO、约束规划 | `classical_optimization.py`、`quantum_optimization.py` |
| 路径与交通 | A*、MAPF、网络流、时空图 | `lattice_geometry.py`、`joint_turn_planner.py`、`strategic_flow.py` |
| 隐藏敌情 | POMDP、POSG、贝叶斯滤波 | `belief_risk.py`、`p5_decision_math.py`、`FinitePOSG` |
| 多回合随机规划 | MDP、随机最短路、MCTS | `nested_cvar_mdp()`、`stochastic_shortest_path()`、`alphazero.py` |
| 主动对抗 | Stackelberg、随机博弈、微分博弈 | `advanced_game_math.py`、`p5_decision_math.py`、离散 HJ-Isaacs 递推 |
| 风险与最坏情形 | CVaR、分布鲁棒优化、机会约束 | `belief_risk.py`、`safety_robust_math.py`、`uncertainty_math.py` |
| 动态重规划 | MPC、混杂系统、事件触发控制 | `control_math.py`、`p6_games_dynamics.py`、`simulate_event_triggered_control()` |
| 安全集 | HJ 可达性、控制屏障函数 | `safety_robust_math.py` |
| 连续代价寻路 | Eikonal、Fast Marching | `fast_marching()`；各向异性离散近似仍在 `advanced_lattice_geometry.py` |
| 阵型重构 | 最优传输、Wasserstein 几何 | `decision_math.py`、`safety_robust_math.py` |
| 空间控制 | Voronoi、Delaunay、计算几何 | `random_geometry.py`、`discrete_geometry.py` |
| 高阶协同 | 超图、超图 Laplacian | `normalized_hypergraph_laplacian()` |
| 士气与命令 | 图动力学、DeGroot、Altafini | `graph_dynamics.py` |
| 战场场模型 | 势场、反应扩散、相场 | `artificial_potential_force()`、`gray_scott_reaction_diffusion()`、`allen_cahn_phase_field()` |
| 地形拓扑 | Morse、持久同调、TDA | `p6_structure_math.py`、`topology_flow_math.py` |
| 对称性 | 群论、表示论、等变网络 | `permutation_representation()`、`invariant_group_average()`、`equivariant_linear_projection()` |
| 侦察价值 | 信息论、互信息 | `uncertainty_math.py` |
| 生存与损失 | 吸收马尔可夫链、更新过程、可靠性理论 | `analyze_absorbing_markov_chain()`、`discrete_renewal_process()`、系统可靠性函数 |
| 极端条件 | 重要性采样、大偏差理论 | `importance_sampling_estimate()`、`bernoulli_large_deviation_rate()` |
| 规则验证 | 时序逻辑、SMT、模型检验 | `online_selection_math.py`、`solve_finite_constraints()`、`p5_decision_math.py` |

`solve_finite_constraints()` 是显式有限域上的精确、穷举式 SMT 风格验证器，不宣称支持通用一阶理论或无限域。Fast Marching 当前实现二维、各向同性、一阶迎风格式；零速度格为障碍。POSG 实现提供受联合动作控制的贝叶斯滤波和零和阶段博弈，不把阶段解冒充完整无限时域 POSG 解。

这些能力遵循同一决策边界：几何、概率、场模型和拓扑只生成候选、代价或先验；CP-SAT/MILP/QUBO 负责联合选择；MAPF 与原生规则负责最终合法性验证。第一章新增定向回归为：

```powershell
python -m pytest rl/chapter1_mathematics_test.py -q
```
