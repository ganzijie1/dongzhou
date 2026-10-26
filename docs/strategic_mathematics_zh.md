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
| `rl/p7_political_campaign_math.py` | 因子图/DBN、信号博弈、时变多层网络、Hawkes、随机库存与跨期物流 |
| `rl/p8_adaptive_mechanism_math.py` | VCG、契约设计、LinUCB、Whittle 指数、高斯过程、在线共形与 E-process |
| `rl/p9_dynamic_topology_tensor_math.py` | 图序列精确 H0 Zigzag、图 Ricci 曲率、多关系张量 HOSVD |
| `rl/p10_uncertainty_epistemic_causal_math.py` | Credal Set、Dempster-Shafer、动态认知逻辑、AGM、QRE/认知层级、SCM、VOI |
| `rl/p11_stochastic_decomposition_math.py` | 情景树、两阶段随机规划、Benders、列生成/Dantzig-Wolfe、SDDP、多面体与割平面 |
| `rl/p12_graph_network_matching_math.py` | 图信号与图小波、动态 SBM、网络形成、稳定匹配、5v5 组队/英雄/动态任务匹配 |
| `rl/p13_metric_persistence_spacetime_math.py` | Wasserstein/GW/FGW/GH、持久层、多参数持久性、时空与随机格点动力学 |
| `rl/p14_tensor_completion_math.py` | SNN、CP、Tucker、TT、t-SVD/TNN 张量补全与缺失机制诊断 |
| `rl/p15_inverse_optimization_math.py` | 逆线性规划、逆 MDP/IRL、逆 Stackelberg 参数反演与激励反应映射 |
| `rl/p16_multiagent_game_math.py` | Dec-POMDP、序列形式、CFR+、Double Oracle/PSRO、CE/CCE、多跟随者与动态 Stackelberg |
| `rl/p17_bilevel_active_learning_math.py` | 双层 LP、KKT/MPEC、隐式超梯度、可微 QP/LP、主动偏好学习、最优实验设计与置信域 |
| `rl/p18_robust_distributional_mdp_math.py` | TV/KL/Wasserstein 鲁棒 MDP、分布型 Bellman、指数风险、reach-avoid、鲁棒占用与策略切换 |
| `rl/p19_dynamic_topology_graphon_math.py` | H0/H1/H2 持久与 Zigzag、vineyard、Mapper、未知标签动态 SBM、Graphon 与高阶扩散 |
| `rl/p20_controlled_koopman_causal_math.py` | DMDc/EDMDc、Koopman MPC、Perron-Frobenius、可行核、因果发现、ICP 与敏感性界 |
| `rl/p21_adaptive_safe_economic_math.py` | 生存概率、有限情景鲁棒控制、鲁棒可行核、在线检测与切换、Perron-Frobenius 投入产出、时序回放因果与跨关卡诊断 |
| `rl/p22_equilibrium_control_continuation_math.py` | LMDP/KL Control、QRE 与通用均衡隐式灵敏度、分布鲁棒 Nash/Stackelberg、伪弧长延拓与分岔诊断 |
| `rl/p23_regime_rare_event_math.py` | BOCPD、显式持续时间 HSMM、Adaptive Multilevel Splitting、Subset Simulation |

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

## 23. P7：政治推断、外交信号、事件连锁与长期后勤

- 因子图与动态贝叶斯网络：`DiscreteFactorGraph` 对有界离散模型做精确枚举边缘化，超过显式组合预算时拒绝运行；`FiniteDynamicBayesianFilter` 对有限隐藏状态执行预测和观测校正，可用于忠诚、阴谋、疾病与援军状态。后验只来自调用方给出的先验、转移和似然。
- 信号博弈：`pure_signaling_equilibria()` 枚举有限纯策略完美贝叶斯均衡。路径上信念使用 Bayes 法则，离轨行动必须存在使其成为最优响应的信念。它不宣称求解一般混合策略或连续类型信号博弈。
- 时变多层网络：`TemporalMultilayerNetwork` 分开保存宗族、盟约、敌对、贸易和指挥等关系层，输出聚合快照、节点强度、时间波动、谱半径及带同节点层间耦合的 supra-adjacency。
- Hawkes 事件过程：`ExponentialHawkesProcess` 使用多元指数核描述谣言、叛乱、会盟和战争的自激连锁，输出条件强度、对数似然、分支率和稳定条件下的平稳强度。强度是统计风险，不是剧情必然触发器。
- 随机库存：`solve_stochastic_inventory()` 对整数需求、有限订货能力和丢失销售模型做有限时域动态规划，显式计入订货、持有、缺货和期末残值。
- 跨期物流：`solve_dynamic_inventory_flow()` 在时间展开网络上联合优化库存、运输、缺供与弃置。运输有容量、成本和整数期旅行时间；当前模型是确定性 LP，随机性由库存动态规划或外部情景层处理。

## 24. P8：激励机制、自适应资源分配与序贯可信度

- VCG：`vcg_mechanism()` 在有限结果集合上最大化申报总福利，并返回 Clarke pivot 外部性支付与个体效用。真实性结论依赖准线性效用、正确结果集合和真实申报，不能直接外推到串谋或预算约束场景。
- 契约理论：`solve_limited_liability_contract()` 以线性规划求使指定行动满足激励相容与参与约束的最小期望工资，工资非负且结果概率必须显式提供。
- 上下文臂：`LinUCBBandit` 为斥候、外交官和军队分配维护每个臂的线性回报估计与置信上界，只从真实上下文和奖励更新。
- Restless bandit：`whittle_indices()` 对两状态折扣臂计算被动补贴下的 Whittle 指数，并单独返回 indexability 数值诊断。非 indexable 模型不能依据指数得到经典策略保证。
- 高斯过程与贝叶斯优化：`GaussianProcessRegressor` 使用精确 RBF 后验输出均值和标准差，`propose()` 在调用方提供的有限候选集中以期望改进选点。核、噪声和样本决定不确定度，不能把后验当作真实威胁场。
- 在线共形：`AdaptiveConformalRegressor` 使用滚动残差与自适应误覆盖率形成序贯区间。漂移下的自适应是工程校准机制，不自动继承静态交换性样本的有限样本覆盖定理。
- E-process：`BernoulliMixtureEProcess` 对固定 Bernoulli 零假设累计 beta 混合似然比，并用历史最大 E-value 支持随时有效的拒绝规则。观测若不满足条件零假设，保证不成立。

## 25. P9：动态图拓扑、网络曲率与多关系张量

- H0 Zigzag 持久同调：`graph_h0_zigzag_persistence()` 接受固定顶点、边逐步增删且每步包含关系明确的图序列。实现从各时刻连通分量构造 A 型 quiver 表示，通过子区间 limit-to-colimit 广义秩及 Möbius 反演得到精确 H0 区间重数。该 P9 图接口仅计算 H0；一般复形的 H1/H2 Zigzag 条形码由 P19 的 `zigzag_persistence()` 提供。
- Forman-Ricci 曲率：`forman_ricci_curvature()` 输出无权图边的组合曲率，用低成本指标识别局部树状瓶颈。
- Ollivier-Ricci 曲率：`ollivier_ricci_curvature()` 在每条边的懒惰随机游走测度之间求精确有限最优传输，得到局部收缩曲率。实现适合小图离线分析，不进入逐动作热路径。
- 多关系张量：`multirelational_hosvd()` 对“人物乘人物乘关系（乘时间）”张量执行截断高阶 SVD，返回核心张量、各模因子、重构和相对误差。潜在因子只表示低秩结构，不能直接命名为真实阵营或因果关系。

P7-P9 默认用于低频战略推断、离线分析、回放解释和参数校准。任何输出若转为在线动作先验，仍必须经过现有 CP-SAT/MILP/QUBO 联合选择、MAPF 和原生规则验证。定向回归为：

```powershell
python -m pytest `
  rl/p7_political_campaign_math_test.py `
  rl/p8_adaptive_mechanism_math_test.py `
  rl/p9_dynamic_topology_tensor_math_test.py -q
```

## 26. P10：不精确概率、证据、信念与因果决策

- 不精确概率：`CredalSet` 用有限概率多面体的顶点表示计算事件概率和期望的上下界，并支持 maximin 行动。它不声称有限顶点能表达任意无限维 Credal Set。
- Dempster-Shafer：`MassFunction` 实现 belief、plausibility、pignistic probability 和归一化 Dempster 合成，同时返回冲突质量；全冲突时显式失败。
- 动态认知逻辑：`EpistemicModel` 在有限 Kripke 模型上计算知识、公共知识和公开宣告更新。可访问关系由调用者提供，不自动推断角色真实认知。
- AGM 信念修正：`RankedBeliefState` 使用有限 Grove 排序实现 revision 与 contraction，满足该有限排序语义，而不是通用命题逻辑定理证明器。
- 有限理性博弈：`logit_qre()` 求双人有限博弈的阻尼 Logit QRE 固定点；`cognitive_hierarchy()` 使用截断 Poisson 层级权重和 Logit 响应。结果依赖温度、层级分布和初始化。
- 结构因果模型：`StructuralCausalModel` 验证有限 DAG，执行前向模拟、`do` 干预、固定个体反事实和 ATE。结构方程、外生样本及可识别性假设必须由调用方给出。
- 信息价值：`expected_value_of_perfect_information()` 与 `expected_value_of_sample_information()` 只从显式状态概率、行动收益、信号似然和采样成本计算 VOI，不补写未知收益。

## 27. P11：随机规划、分解优化与割平面

- 情景树与多阶段 LP：`ScenarioTree` 校验唯一根、逐层父子关系、每处分支概率和路径概率；`solve_multistage_scenario_tree_lp()` 为每个信息节点建立唯一决策块，以节点共享历史自然实施非预见性，并支持任意深度的局部及父子连接线性约束。
- 两阶段随机规划：`solve_two_stage_stochastic_lp()` 构造确定性等价 LP；`solve_two_stage_benders()` 使用逐情景最优性割实现 L-shaped 分解，并与确定性等价解交叉验证。
- Benders 边界：当前实现要求非负追索成本和相对完全追索；追索不可行或无界会显式报错，不伪造可行性割。
- Dantzig-Wolfe/列生成：`column_generation()` 解等式受限主问题，从定价回调加入负约化成本列，并检测重复负价列造成的停滞。定价器的完整性由调用方负责。
- SDDP：`sddp_inventory()` 是标量库存的专用实现，使用 LP 对偶生成分段线性下界；它不是任意维、多风险度量 SDDP 的通用替代。
- 多面体与割：`Polyhedron` 支持小型满维顶点枚举，`chvatal_gomory_cut()` 与 `minimal_cover_cut()` 生成可审计有效不等式，`solve_binary_linear_program()` 用于小型基准核验。

## 28. P12：图信号、动态网络与匹配博弈

- 图信号处理：`GraphSignalProcessor` 对无向非负加权图计算组合/归一化 Laplacian、图傅里叶变换、谱滤波、热核、图小波和总变差。谱结果只对调用方给出的图和权重成立。
- 动态随机块模型：`simulate_dynamic_sbm()` 生成 Markov 社区与动态图；`estimate_dynamic_sbm()` 在社区标签已知时估计块概率和转移矩阵；`dynamic_sbm_log_likelihood()` 给出完整数据似然。标签未知时的谱估计与跨时刻标签对齐由 P19 的 `estimate_dynamic_sbm_unknown_labels()` 提供。
- 网络形成：`ConnectionsNetwork` 实现 Jackson-Wolinsky connections utility，并逐边检查单边删边和双边加边的成对稳定性偏离。
- 稳定匹配：`deferred_acceptance()` 支持不完整偏好和接收方容量，`blocking_pairs()` 独立检查阻挡对。固定优先级下的经典稳定性不外推到同伴外部性或不可拆组排。
- 5v5 组队与位置：`optimize_two_team_roles()` 用 MILP 实现两队位置容量、玩家唯一性、组排同队、二元协同线性化和逐位置公平差约束。
- 英雄层：`optimize_hero_lineup()` 实现每人一英雄、同队唯一、禁选、个人候选池、职责最低覆盖和英雄对协同。敌方克制或顺序 BP 只有在调用方显式转成价值或额外阶段时才会进入模型。
- 局内任务层：`optimize_dynamic_tasks()` 在时间展开 MILP 中处理任务最小/最大人数、显式 idle 状态和分配切换成本，输出逐时刻任务及真实切换数。

## 29. P13：几何距离、广义持久性与时空随机格点

- 四种距离：`wasserstein_distance()` 求有限离散最优传输 LP；`gromov_wasserstein_distance()` 和 `fused_gromov_wasserstein_distance()` 用条件梯度求平方结构失真的局部解；`finite_gromov_hausdorff_distance()` 在显式候选预算内枚举有限对应并给出精确 GH 值。
- 距离边界：GW/FGW 非凸，返回给定初始化下的收敛结果，不保证全局最优；GH 枚举是小规模离线算法，超过 `max_candidates` 会拒绝运行。
- 多参数持久性：`MultiparameterPersistenceModule` 校验网格 cover map 维度和交换方块，计算 Hilbert 函数、秩不变量和单调 fibered path 的秩摘要；它不把多参数模块错误压成普通条形码。
- 持久层：`PersistentSheafSequence` 复用 `CellularSheaf`，要求调用方显式提供相邻零阶上链映射，验证全局截面被映到全局截面，再计算持久 Betti 数与层 Laplacian 谱。
- Zigzag：动态图边增删的精确 H0 Zigzag 继续由 `p9_dynamic_topology_tensor_math.py` 提供；P19 的 `zigzag_persistence()` 进一步从 GF(2) 链复形、同调诱导映射和广义秩计算 H0/H1/H2 区间分解。
- 时空格点：`minkowski_interval()`、`causally_precedes()`、`time_expanded_shortest_path()` 和 `explicit_graph_diffusion_step()` 分别提供离散因果锥、动态阻塞寻路和带 CFL 检查的显式扩散。既有 `SpaceTimeGrid` 继续负责顶点、终点和换位冲突预留。
- 随机格点：`site_percolation()`、`bond_percolation()`、`conductance_laplacian()`、`effective_resistance()`、`first_passage_time()` 与 `estimate_spectral_dimension()` 覆盖渗流、随机介质传播和谱统计；既有 `random_geometry.py` 继续负责点过程、Voronoi、Delaunay 和部署约束。
- 空间格点：坐标、邻域、射线、形态学、Pick/Ehrhart、Poisson、各向异性测地线及数字拓扑继续由 `lattice_geometry.py` 与 `advanced_lattice_geometry.py` 提供，不复制第二套坐标语义。

## 30. P14：张量补全与缺失机制

- 掩码与诊断：`missingness_diagnostics()` 区分观测值与缺失值，报告观测率、各模式最低覆盖、全缺纤维和全缺切片；`completion_metrics()` 和 `inverse_propensity_weighted_loss()` 提供外部评估与倾向修正损失。
- SNN：`complete_snn_halrtc()` 用 ADMM 和各模展开奇异值软阈值最小化核范数之和，适合小型离线张量。
- CP：`complete_cp_weighted()` 只遍历观测坐标，使用解析梯度拟合正则化 CP 因子，并允许异方差权重。
- Tucker：`complete_tucker_projection()` 交替执行截断 HOSVD 投影与观测一致性投影；已有 `multirelational_hosvd()` 仍只负责完整张量分解。
- Tensor Train：`tensor_train_svd()` 返回 TT 核和截断误差，`complete_tensor_train_projection()` 在 TT 低秩集合与观测约束之间迭代投影。
- t-SVD/TNN：`tubal_nuclear_prox()` 在第三模 FFT 切片上做奇异值软阈值，`complete_tubal_tnn()` 用 ADMM 完成三阶张量。
- 恢复边界：低秩不等于可辨识。整条纤维缺失、高相干、MNAR、秩选择错误或信息量不足时，算法可能有多个同样符合观测的解；接口只返回数值解和诊断，不编造未观测真值或不确定性保证。

P10-P14 的定向回归为：

```powershell
python -m pytest `
  rl/p10_uncertainty_epistemic_causal_math_test.py `
  rl/p11_stochastic_decomposition_math_test.py `
  rl/p12_graph_network_matching_math_test.py `
  rl/p13_metric_persistence_spacetime_math_test.py `
  rl/p14_tensor_completion_math_test.py -q
```

## 31. P15：逆线性规划、逆 MDP 与逆 Stackelberg

- KKT 逆线性规划：`inverse_linear_program()` 接受一个或多个已观测最优解及各自的线性可行域，在活动约束法锥的交集中寻找最接近参考代价的目标系数，并返回每次观测的对偶乘子、原始可行性、驻点与互补残差。参考代价或显式分量归一化负责处理正比例缩放不唯一性。
- 逆约束：`inverse_linear_rhs()` 在约束法向量已知时，将参考右端项投影到包含全部观测的最近可行边界；调用方可声明观测在哪些约束上活动，冲突的活动边界会显式失败。
- 带噪声揭示偏好：`fit_revealed_linear_cost()` 只需要“选择结果优于候选替代”的有限比较，通过软间隔 LP 反演共同线性代价。它同样适用于没有连续 KKT 表达的逆组合优化，并显式返回逐比较松弛量和比较矩阵秩。
- 逆 MDP：`inverse_mdp_policy()` 对有限折扣 MDP 和完整确定性观测策略建立策略评价后的线性优势约束，反演状态-动作特征权重，返回奖励、价值、全部动作优势、松弛量和可辨识秩。轨迹型最大熵 IRL 继续复用 `p6_games_dynamics.maximum_entropy_irl()`。
- 占用测度：`discounted_occupancy()` 精确解折扣状态访问线性系统，返回未归一化状态/状态-动作占用及可选特征期望，可用于学徒学习、策略比较和回放审计。
- 奖励等价类：`potential_based_reward_shaping()` 对状态-动作或状态-动作-后继奖励应用势函数塑形。逆 MDP 权重不唯一时，调用方必须结合该等价关系、特征秩和外部先验解释结果，不能把某组权重称为唯一真实动机。
- 贝叶斯逆 MDP：`bayesian_inverse_mdp()` 在调用方给出的有限奖励假设和先验上做精确后验更新，用最优 Q 值上的 Boltzmann 行动似然解释部分状态-动作演示，并返回后验、MAP、后验均值、证据和各假设行动概率。它不声称覆盖连续参数空间。
- 理性跟随者反演：`inverse_stackelberg_follower_utility()` 从多个领导者混合承诺与跟随者响应建立最佳响应不等式，估计线性收益权重，并返回后悔值、软约束松弛和信息秩。
- 有限理性跟随者反演：`inverse_logit_stackelberg_utility()` 在固定理性精度下最大化 Logit 响应似然，输出每条观测的选择概率、正则化负对数似然、收敛状态和信息秩。理性精度与收益尺度不能同时从相同行为中任意识别，因此精度是调用方显式参数。
- 激励型逆 Stackelberg：`solve_incentive_stackelberg()` 精确枚举有限反应映射，即领导者承诺“跟随者选择每个行动时我如何反应”，随后按 strong 或 weak 破同分规则求跟随者最佳响应与领导者最优承诺。指数规模由 `max_profiles` 明确限制，超限时拒绝伪装成通用大规模算法。
- 运行边界：P15 是离线校准、回放解释和候选参数层，不从故事文本猜测收益，不把相关性当因果，也不自动覆盖原生战斗 AI。进入在线决策前仍需经过既有联合规划、MAPF 和规则合法性检查。

P15 定向回归为：

```powershell
python -m pytest rl/p15_inverse_optimization_math_test.py -q
```

## 32. P16：多智能体不完全信息与均衡求解

- Dec-POMDP：`FiniteDecPOMDP` 校验有限联合转移与联合观测核，提供公共后验更新，并精确评估由各智能体局部观测历史索引的确定性策略树。它面向有限时域小模型，不冒充无限时域 Dec-POMDP 通用求解器。
- 序列形式：`solve_sequence_form_zero_sum()` 直接接受双方 realization-plan 流守恒矩阵，以一对原始/对偶 LP 求零和扩展式博弈，返回实现计划、博弈值、对偶间隙和流残差。
- CFR+：`cfr_plus_zero_sum()` 对有限零和矩阵实施正部累积遗憾与线性平均，单独报告 exploitability；原有 `CounterfactualRegretMinimizer` 继续负责树上的普通 CFR。
- Double Oracle/PSRO：`double_oracle_zero_sum()` 和 `psro_zero_sum()` 在显式有限策略库上反复求受限 Nash 元博弈并加入精确纯最佳响应，保留种群及 exploitability 轨迹。
- 相关均衡：`correlated_equilibrium()` 以激励约束 LP 求福利最大的 CE 或 CCE；`multiplicative_weights_bimatrix()` 用全信息乘法权重生成经验联合分布，并返回双方平均外部遗憾和 CCE 偏差。
- 多跟随者 Stackelberg：`solve_multi_follower_stackelberg()` 枚举跟随者联合纯响应，以单边偏离约束确保该响应是 Nash 均衡，再优化领导者混合承诺。其破同分语义是乐观型。
- 动态 Stackelberg：`solve_dynamic_stackelberg()` 枚举有限时域确定性 Markov 领导者承诺，对每个承诺用反向动态规划求跟随者最佳响应，支持 strong/weak 破同分并设置 `max_policies`。

## 33. P17：双层优化、可微求解与主动逆学习

- 双层 LP：`solve_finite_bilevel_linear()` 对离散上层选择逐一求下层 LP，并在下层最优面上执行 optimistic/pessimistic 破同分。连续上层或非凸下层不在该有限枚举器的保证范围内。
- KKT/MPEC：`linear_program_kkt_certificate()` 独立计算原始、对偶、驻点和互补残差，用于审计把下层问题改写成 MPEC 后的候选解。
- 隐式超梯度：`implicit_hypergradient()` 使用隐函数定理计算下层最优点对参数的灵敏度；病态 Hessian 会切换到伪逆并显式报告条件数。
- 可微 QP/LP：`equality_qp_sensitivity()` 对严格凸等式 QP 的 KKT 系统求解并求导；`linear_program_active_set_sensitivity()` 在固定活动集假设下计算顶点 Jacobian、秩、零度和残差。活动集变化处不可直接沿用局部导数。
- 主动偏好与 IRL：`logistic_preference_fisher_information()` 计算成对 Logit 查询的期望 Fisher 信息；`expected_information_gain()` 对有限假设和实验似然计算互信息；`active_irl_query()` 进一步从奖励权重假设和轨迹特征差构造 Boltzmann 选择似然，选择最能区分奖励的演示对。
- 最优实验设计：`greedy_optimal_design()` 对秩一信息增量执行 D-optimal 或 A-optimal 贪心选样，返回完整信息矩阵、目标历史和条件数。
- 置信域：`wald_confidence_ellipsoid()` 在可辨识子空间构造 Wald 椭球，并把不可辨识零空间作为无界圆柱方向返回，避免伪造唯一参数。

## 34. P18：鲁棒、分布型与风险敏感 MDP

- 模糊集合：`worst_case_discrete_expectation()` 对有限分布精确或数值求解 TV、KL 与 Wasserstein 球内最坏期望，并返回实际对手分布和模糊距离。
- 鲁棒 MDP：`robust_value_iteration()` 假设 state-action rectangular 模糊集合，逐状态动作调用最坏期望，返回鲁棒价值、策略和最坏转移核。非矩形跨状态耦合不由该 Bellman 递推覆盖。
- 分布型 Bellman：`categorical_bellman_projection()` 实现 C51 固定支撑投影；`quantile_bellman_targets()` 与 `quantile_huber_loss()` 提供分位数回归目标和损失。
- 风险敏感控制：`entropic_risk_value_iteration()` 使用指数确定性等价递推；`discrete_cvar()` 对有限分布精确处理上下尾及边界原子的分数质量。
- 随机 reach-avoid：`stochastic_reach_avoid()` 用有限时域动态规划最大化先到目标、避开失败集的概率。
- 鲁棒占用测度：`robust_reward_occupancy_lp()` 在固定转移和多个奖励情景下最大化最坏折扣回报，返回占用、恢复策略、各情景回报与流守恒残差。
- 在线切换：`PageHinkleyPolicySwitcher` 对损失上漂移做单侧 Page-Hinkley 检测并循环切换候选策略；阈值仍需用真实回放校准。

## 35. P19：高阶动态拓扑、未知社区与 Graphon

- 普通持久同调：`persistent_homology()` 用标准 GF(2) 边界列约化计算 H0/H1/H2 区间，要求调用方提供面闭合且过滤值单调的有限单纯复形。
- 高阶 Zigzag：`zigzag_persistence()` 对相邻包含方向可前可后的复形序列计算 H0/H1/H2 同调空间及诱导映射，再通过子区间 limit-to-colimit 广义秩和 Möbius 反演得到精确区间重数。
- Vineyard 与 Mapper：`match_persistence_diagrams()` 用瓶颈型 L-infinity 代价匹配相邻图；`mapper_graph()` 在一维 cover 上做半径连通分量聚类并按共享样本连边。
- 未知标签动态 SBM：`estimate_dynamic_sbm_unknown_labels()` 对每个动态图快照做谱嵌入与 KMeans，再以最大重叠跨时刻对齐标签，估计块概率、标签转移和完整数据似然。它是谱估计器，不是全贝叶斯后验。
- Graphon：`histogram_graphon_estimate()` 按度或外部分数排序后估计分块 graphon；`graphon_logit_mean_field()` 求二元行动 Logit 图极限固定点并报告收敛残差。
- 高阶扩散：`hodge_laplacian()` 构造 0/1/2 维定向组合 Hodge Laplacian；`simplicial_heat_diffusion()` 使用矩阵指数扩散顶点、边或面上的 cochain 信号。

## 36. P20：受控 Koopman、转移算子与因果发现

- DMDc/EDMDc：`dynamic_mode_decomposition_with_control()` 从列快照拟合线性状态与控制矩阵；`extended_dynamic_mode_decomposition_with_control()` 在调用方给出的有限观测字典上做岭回归升维。两者返回相对残差，不把短轨迹拟合当作真实物理定律。
- Koopman MPC：`koopman_mpc()` 在有限控制候选集上枚举升维线性模型的二次 MPC，显式限制控制序列数量。
- Perron-Frobenius：`ulam_transfer_operator()` 将状态转移样本投影到矩形分箱，估计 Ulam Markov 算子、平稳分布、样本分箱和越界数量。
- Viability Kernel：`stochastic_viability_kernel()` 迭代删除无法以指定单步概率留在当前集合中的状态，返回最大受控不变子集与逐状态可行动作。
- NOTEARS：`notears_linear()` 以增广拉格朗日优化线性结构方程的光滑无环约束，并返回阈值化 DAG、无环残差、拟合损失和收敛状态。
- 条件独立：`partial_correlation_test()` 提供高斯偏相关检验；`pc_skeleton()` 逐阶条件化删除独立边并保存 separating set，当前不执行 v-structure 和 Meek 定向。
- 不变因果预测：`invariant_causal_prediction()` 枚举小型线性预测变量子集，以跨环境残差均值和方差检验筛选不变集合并取交集。结论依赖环境干预充分性、线性和残差检验假设。
- 敏感性界：`omitted_variable_sensitivity()` 用 partial-R2 给出遗漏混杂偏差与置信区间；`discounted_model_transfer_bound()` 用 simulation lemma 控制奖励和转移误差引起的折扣价值偏差。

## 37. P21：非平稳安全控制、经济转移算子与回放迁移

- 生存概率：`finite_horizon_survival_probability()` 最大化有限时域内始终留在安全集的概率；`infinite_horizon_survival_probability()` 从安全集指示函数递减迭代到最大不动点，并报告收敛残差。它们与“目标先达”的 reach-avoid 事件保持区分。
- 有限情景鲁棒控制：`scenario_robust_value_iteration()` 对 state-action rectangular 的有限转移/奖励情景执行最坏情景 Bellman 迭代；`robust_viability_kernel()` 要求同一动作在所有给定情景下满足留存概率阈值。全局固定情景或跨状态耦合不确定性不在其保证范围内。
- 在线适应：`TwoSidedCUSUMDetector` 检测相对已校准均值的上下漂移；`FixedSharePolicySelector` 以固定共享指数权重追踪非平稳策略专家，并用最小驻留时间和切换优势抑制抖动。只有单策略反馈时不能使用其全信息更新假设。
- Perron-Frobenius：`perron_frobenius_analysis()` 返回非负方阵的谱半径、左右 Perron 向量、不可约性与残差；`leontief_input_output_analysis()` 在统一列投入约定下求 Leontief 逆、总产出、劳动价值和可选工资增广系统的最大利润率。经济解释仅对显式假设成立。
- 回放时序图：`lagged_replay_design()` 保证滞后特征不跨局；`lagged_conditional_independence_graph()` 用联合线性回归和 t 检验给出 `[lag, source, target]` 候选边、效应、p 值与条件数。它是预测候选而非因果证明。
- 跨关卡迁移：先由 P20 `invariant_causal_prediction()` 筛选不变候选，再由 `cross_environment_transfer_diagnostics()` 留一关卡拟合并报告各环境 RMSE、系数和离散度，防止平均性能掩盖单关卡失效。

## 38. P22：线性可解控制、可微均衡与分岔延拓

- LMDP/KL Control：`finite_horizon_lmdp()` 以 log-sum-exp 稳定求解有限时域 soft Bellman，并保持被动转移支持集；`average_cost_lmdp()` 解 Perron 特征问题并返回平均成本、受控转移和特征残差。
- 均衡隐式微分：`implicit_equilibrium_sensitivity()` 对局部 Nash、VI、KKT 或 Stackelberg 残差系统求灵敏度，报告秩、最小奇异值、条件数、伪逆使用和线性残差。
- Logit QRE：`solve_bimatrix_logit_qre()` 在非冗余 log-odds 坐标求双矩阵 QRE，并对双方理性强度做隐式求导。多解时只解释当前初值选中的分支。
- 分布鲁棒博弈：`finite_distributionally_robust_nash()` 对有限模糊分布顶点精确枚举纯鲁棒 Nash；`finite_distributionally_robust_stackelberg()` 支持 optimistic/pessimistic 跟随者破同分并枚举纯领导者决策。
- 均衡延拓：`pseudo_arclength_continuation()` 以切向预测和增广 Newton 校正穿过简单折叠，返回路径、残差、最小奇异值、步长与折叠候选。
- 分岔诊断：`classify_static_bifurcation()` 检查秩、左右核和横截量；`detect_dynamic_bifurcations()` 区分连续时间稳态/Hopf 与离散时间稳态/flip/Neimark-Sacker 候选。候选标签不替代高阶非退化证明。

## 39. P23：在线阶段检测与稀有事件模拟

- BOCPD：`BayesianOnlineChangePointDetector` 对已知观测方差的 Normal-Normal 段模型维护 run-length 后验、变点概率、MAP 段长、预测证据和截断质量，全程使用归一化对数消息。
- HSMM：`hsmm_forward()` 对显式持续时间段做 log-domain 前向递推；`hsmm_viterbi()` 返回逐帧状态、段区间和最优对数概率。持续时间上界和段级转移语义由调用方明确提供。
- AMS：`adaptive_multilevel_splitting()` 通过反应坐标、固定淘汰数、越级前缀复制和原动力学续跑估计路径稀有事件，同时报告谱系集中度与并列层级。
- Subset Simulation：`subset_simulation()` 以自适应分位层和条件随机游走 Metropolis 估计高维失败概率，返回各层实际条件概率、接受率和最终条件样本。正式报告仍需独立重复和有效样本量分析。
- 联合接入：BOCPD 负责在线漂移告警，HSMM 负责阶段与持续时间，LMDP 提供合法支持集内的平滑先验，延拓分析版本临界点，AMS/Subset Simulation 评估路径型与输入型极端风险。全部结果仍需经过规则、动作掩码、联合规划和回放验证。

## 40. P24-P30：信念规划、随机博弈、约束控制与统计保证

- P24 `p24_belief_space_planning_math.py`：精确 alpha-vector、PBVI、POMCPOW、DESPOT 情景规划、联合状态/对手类型信念更新与有限层级 Logit 推理。
- P25 `p25_stochastic_game_math.py`：零和矩阵博弈、折扣/平均回报 Shapley 迭代、一般和策略评估、MPE gap、纯 MPE 枚举与阶段势结构残差。
- P26 `p26_factor_graph_distributed_math.py`：Sum-Product/LBP、Junction Tree、Max-Sum/DCOP 与共识 ADMM；树上精确性与环图近似性分开报告。
- P27 `p27_constrained_budgeted_mdp_math.py`：折扣占用测度 CMDP、预算影子价格、策略复核、逐路径整数预算动态规划与 Pareto 剪枝。
- P28 `p28_continuous_time_mdp_math.py`：CTMDP uniformization、折扣/平均回报控制、固定策略评估与 Poisson 瞬态传播。
- P29 `p29_extreme_tail_importance_math.py`：GEV、POT/GPD、经验及理论尾相关、带防御混合的交叉熵重要抽样与有效样本量。
- P30 `p30_finite_sample_guarantees_math.py`：PAC-MDP 声称审计、PAC-Bayes-kl、经验 Bernstein、anytime confidence sequence、CRC、漂移加权共形阈值与权重 ESS。

完整公式、游戏映射与假设边界见 `docs/p24_p30_planning_risk_guarantees_zh.md`。P24-P30 继续遵守“候选建议不等于可执行动作”的边界：所有输出必须经过原生合法动作、资源、碰撞、联合规划、MAPF 与回放验收。

P16-P30 定向回归为：

```powershell
python -m pytest `
  rl/p16_multiagent_game_math_test.py `
  rl/p17_bilevel_active_learning_math_test.py `
  rl/p18_robust_distributional_mdp_math_test.py `
  rl/p19_dynamic_topology_graphon_math_test.py `
  rl/p20_controlled_koopman_causal_math_test.py `
  rl/p21_adaptive_safe_economic_math_test.py `
  rl/p22_equilibrium_control_continuation_math_test.py `
  rl/p23_regime_rare_event_math_test.py `
  rl/p24_belief_space_planning_math_test.py `
  rl/p25_stochastic_game_math_test.py `
  rl/p26_factor_graph_distributed_math_test.py `
  rl/p27_constrained_budgeted_mdp_math_test.py `
  rl/p28_continuous_time_mdp_math_test.py `
  rl/p29_extreme_tail_importance_math_test.py `
  rl/p30_finite_sample_guarantees_math_test.py -q
```

P16-P20 的完整公式见 `docs/p16_p20_advanced_math_zh.md`，P21 见 `docs/p21_adaptive_safe_economic_math_zh.md`，P22-P23 见 `docs/p22_p23_equilibrium_regime_rare_math_zh.md`，P24-P30 见 `docs/p24_p30_planning_risk_guarantees_zh.md`。这些模块默认属于离线分析、校准或低频规划层；任何结果进入实战动作前仍必须通过原生合法动作、联合规划、MAPF 和战斗规则检查。

## 41. P31-P39：优化、分散信息、离线 RL、机制、风险与系统验证

- P31 `p31_variational_stochastic_optimization_math.py`：Mirror Descent、Extragradient、Optimistic Gradient、Minty/Stampacchia gap、Proximal Point、Douglas-Rachford、Robbins-Monro、两时间尺度递推、Polyak-Ruppert 与经验稳定性诊断。
- P32 `p32_common_information_game_math.py`：公共 belief、occupancy-state、双智能体 Dec-POMDP policy graph 与 Bayesian correlated equilibrium LP。
- P33 `p33_offline_reinforcement_learning_math.py`：tabular FQE/FQI/CQL、折扣占用测度比、unsupported mass、concentrability、边缘重要性价值与 Bellman completeness 投影残差。
- P34 `p34_bayesian_mechanism_contract_math.py`：VCG、正则 i.i.d. Myerson 保留价拍卖、DSIC/BIC/interim-IR 审计和隐藏行动合同 LP。
- P35 `p35_large_deviation_risk_math.py`：离散 Donsker-Varadhan 对偶、KL 风险、Cramér/Chernoff、Freidlin-Wentzell 路径作用量、风险敏感有限时域 DP 与指数倾斜 ESS。
- P36 `p36_probabilistic_model_checking_math.py`：DTMC/MDP 可达、PCTL bounded-until、CTMC uniformization、CSL 时限可达、固定样本 SMC 与 SPRT。
- P37 `p37_master_mean_field_control_math.py`：有限状态 MFG、经验 Lions 导数、Master Equation 残差、MFC 社会边际成本和有限玩家误差/速率诊断。
- P38 `p38_stochastic_network_calculus_math.py`：min-plus、服务串联、backlog/delay、随机违约分裂、有效带宽/容量、常数服务尾界与 Markov 调制流量。
- P39 `p39_quantum_game_math.py`：密度矩阵、部分迹、CPTP、POVM、EWL、CHSH、退极化和有限量子策略 Nash 审计。

完整接口、游戏映射、数学边界和 P31-P39 回归命令见 `docs/p31_p39_optimization_mechanism_risk_systems_zh.md`。这些模块扩展分析与候选生成能力，不扩展原生合法动作集合。

## 42. P40-P49：动态风险、因果评估、混合动力、演化、拥塞与机制

- P40 `p40_dynamic_risk_bsde_math.py`：离散 CVaR、熵风险、固定策略 Nested CVaR 与信息分区离散 BSDE。
- P41 `p41_restless_bandit_index_math.py`：Gittins 退休指数、Whittle 补贴指数、indexability 诊断与容量选择。
- P42 `p42_sequential_causal_ope_math.py`：序贯 g-formula、PDIS、序贯 DR、近端 bridge 分数、隐藏混杂敏感性与权重 ESS。
- P43 `p43_pdmp_math.py`：积分风险率事件时刻、线性强度闭式反演、PDMP 生成元、受控 HJB backup 与时间重标度量。
- P44 `p44_evolutionary_dynamics_math.py`：复制子、突变选择、Logit 响应、纯 ESS、平稳分布与小状态阻力树。
- P45 `p45_congestion_wardrop_poa_math.py`：平行仿射 Wardrop/社会最优、VI gap、Rosenthal 势、PoA 与 smoothness 上界。
- P46 `p46_polynomial_sos_moment_math.py`：多项式评价、SOS Gram 重构、矩阵/局部化矩阵与 flat-extension 数值诊断。
- P47 `p47_blackwell_adversarial_bandit_math.py`：EXP3、外部/交换 regret、Blackwell 目标集动作、partial-monitoring 全局可观测性与校准误差。
- P48 `p48_uncertainty_quantification_math.py`：正交 PCE 统计、动态 Sobol、Smolyak 层级集合、MLMC 分配与估计。
- P49 `p49_dynamic_mechanism_elicitation_math.py`：承诺效用、动态 IC/IR 审计、pivot 外部性、proper scoring 与 peer prediction 支付。

完整公式映射、适用边界、联合流程和 P40-P49 回归命令见 `docs/p40_p49_dynamic_risk_evolution_uq_mechanism_zh.md`。这十个模块继续属于分析、校准和候选生成层，所有输出进入实战前仍需通过原生合法动作、资源、碰撞、联合规划、MAPF 与回放验收。

## 43. P50-P60：可达安全、状态估计、并发、随机流与多目标价值

- P50 `p50_reachability_pursuit_evasion_math.py`：离散最坏情形 BRT、随机 reach-avoid 动态规划与恒速拦截时间。
- P51 `p51_clf_cbf_safety_math.py`：控制仿射 CLF/CBF 约束、带 CLF 松弛的最小改动安全过滤与高阶障碍递推。
- P52 `p52_state_estimation_math.py`：EKF、无迹变换、粒子重采样、IMM 混合与 H-infinity 信息滤波。
- P53 `p53_marked_point_process_math.py`：自激/互激/抑制标记强度、Hawkes 似然、补偿过程与分枝比。
- P54 `p54_spatial_point_process_math.py`：PPP、Thomas 聚簇、有限 DPP、覆盖概率、接触距离与最近邻距离。
- P55 `p55_reachability_graph_math.py`：可达域、避险最短路、强连通分量、对抗吸引域与最大目标可达概率。
- P56 `p56_deadlock_livelock_math.py`：等待环、轨迹绕数、周期、方向翻转及卡墙、绕塔、发呆等综合诊断。
- P57 `p57_timed_automata_petri_math.py`：时间自动机轨迹验证、Petri 网使能/发射/可达/死锁/P-invariant 与随机事件竞争。
- P58 `p58_queueing_heavy_traffic_math.py`：Little、M/M/1、Jackson、Kingman、流体队列、反射布朗近似与平方根配置。
- P59 `p59_wasserstein_fokker_planck_math.py`：一维 Wasserstein、自由能、Fisher 信息、Gaussian JKO 与无通量 Fokker-Planck 基准步。
- P60 `p60_multiobjective_value_math.py`：Pareto 前沿、集合值 Bellman 备份、Chebyshev 标量化和二维超体积。

完整接口、假设边界、联合接入顺序和 P50-P60 回归命令见 `docs/p50_p60_reachability_concurrency_flow_multiobjective_zh.md`。这些工具不自动扩大原生动作集：P50/P55 生成可达候选，P51 过滤连续控制，P56/P57 监视运行时异常，P60 只在合法安全候选中做多目标选择。
