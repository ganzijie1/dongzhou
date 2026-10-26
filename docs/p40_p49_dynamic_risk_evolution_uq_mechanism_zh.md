# P40-P49：动态风险、因果评估、混合动力、演化、拥塞、证书与机制

本轮把十篇专题文档接入为十个独立、可测试的数学模块。它们服务于战局分析、候选生成、离线校准和安全审计，不扩展游戏原生合法动作集合，也不会绕过资源、碰撞、地图、联合规划或战斗规则。

## 1. P40：动态风险、Nested CVaR 与 BSDE

模块：`rl/p40_dynamic_risk_bsde_math.py`

- `discrete_cvar()` 对离散损失分布计算 VaR、上尾 CVaR 与显式尾部权重；可审计究竟由哪些失败情景抬高风险。
- `nested_cvar_markov_chain()` 对固定策略做逐状态、逐时刻的嵌套 CVaR 反向递推，保持动态风险的时间一致性。
- `entropic_risk()` 用稳定 log-sum-exp 计算指数风险；风险厌恶为零时退化为期望。
- `bsde_backward_euler()` 在调用方提供的信息分区上执行条件均值型离散 BSDE Euler 递推。

游戏用途：评估撤退、守点、救援或资源链在多阶段坏情景下的累计风险。BSDE 接口是离散数值原语，不把有限样本分区近似声称为连续时间精确解。

## 2. P41：Restless Bandit、Gittins 与 Whittle Index

模块：`rl/p41_restless_bandit_index_math.py`

- `gittins_index()` 通过退休选项 Bellman 方程和二分求有限状态折扣 Gittins 指数。
- `whittle_indices()` 对主动/被动两套转移和收益求补贴阈值，并在补贴网格上审计被动集合是否单调扩大。
- `select_whittle_arms()` 在并发容量约束下选择最高指数任务。

游戏用途：有限操作位下安排侦察、治疗、占点、补给和技能冷却关注对象。只有通过 indexability 诊断后，Whittle 数字才有标准指数解释；它仍是拉格朗日松弛启发式，不等价于一般 RMAB 的全局最优解。

## 3. P42：序贯因果推断与因果 OPE

模块：`rl/p42_sequential_causal_ope_math.py`

- `sequential_g_computation()` 在有限时域表格模型中执行目标策略干预的 g-formula。
- `per_decision_importance_sampling()` 和 `sequential_doubly_robust()` 给出 PDIS、序贯 DR、轨迹值、最终权重与有效样本量。
- `proximal_bridge_score()` 提供给定 outcome/treatment bridge 后的近端因果分数原语。
- `marginal_sensitivity_probability_bounds()` 用 Rosenbaum odds-ratio 因子给隐藏混杂敏感性区间。

游戏用途：用回放比较策略、估计技能或编队干预效果，并显式暴露覆盖不足。序贯可交换性、positivity、模型正确性或 bridge 存在性仍需由数据设计支持，单个估计值不是因果证明。

## 4. P43：PDMP

模块：`rl/p43_pdmp_math.py`

- `next_event_time_by_hazard()` 沿确定性流积分强度并反演下一跳时刻；`linear_hazard_event_time()` 提供线性强度的闭式版本。
- `pdmp_generator()` 计算漂移导数项与跳跃期望项。
- `controlled_hjb_backup()` 比较有限控制动作的 PDMP HJB 局部值。
- `time_rescaling_increments()` 保留积分强度样本，供指数性与拟合诊断使用。

游戏用途：在连续位移、冷却或资源增长之间穿插死亡、受击、状态切换和刷新事件。强度模型必须从回放校准；零强度区间和有限仿真时域不会被伪造为已发生事件。

## 5. P44：演化动力学、ESS 与阻力树

模块：`rl/p44_evolutionary_dynamics_math.py`

- `replicator_rhs()`、`replicator_mutator_rhs()` 与 `logit_response()` 给出复制子、突变选择和有限理性响应原语。
- `pure_ess_diagnostic()` 依次检查纯策略 Nash 条件和中性一阶条件下的二阶入侵条件。
- `stationary_distribution()` 计算有限 Markov 链平稳分布。
- `resistance_tree_potentials()` 与 `stochastically_stable_states()` 精确枚举小状态集的有向入树，识别小噪声长期稳定状态。

游戏用途：分析版本生态、阵容克制、模仿学习和带突变策略更新。阻力树枚举限制在至多八个状态；大状态空间需要专门的有向最小树算法。

## 6. P45：Wardrop、拥塞博弈与 Smoothness PoA

模块：`rl/p45_congestion_wardrop_poa_math.py`

- `wardrop_parallel_affine()` 用水位法求平行仿射路由的 Wardrop 流量、延迟、总成本和 VI gap。
- `social_optimum_parallel_affine()` 使用边际成本求社会最优流量，可与 `price_of_anarchy()` 对照。
- `rosenthal_potential()` 精确计算有限原子拥塞博弈的势函数。
- `smoothness_poa_bound()` 把给定的 smoothness 参数转换为 PoA 上界。

游戏用途：分析多人抢线、堵门、野区路线和服务队列。当前闭式求解器只覆盖斜率严格为正的平行仿射网络；一般拓扑需另接网络流或 VI 求解器。

## 7. P46：多项式优化、SOS 与矩松弛

模块：`rl/p46_polynomial_sos_moment_math.py`

- `monomial_powers()`、`evaluate_polynomial()` 管理多重指数和多项式评价。
- `sos_gram_coefficients()` 与 `sos_gram_residual()` 核验给定 Gram 矩阵能否重构目标多项式，并报告最小特征值。
- `moment_matrix()`、`localizing_matrix()` 构造矩与局部化矩阵。
- `flat_extension_holds()` 比较数值秩，提供原子测度可提取性的必要诊断。

游戏用途：核验安全区域、不变量、碰撞约束或策略界的多项式证书。模块核验调用方给出的证书，不内置 SDP 求解器；数值半正定和 flatness 也不替代严格有理证书。

## 8. P47：Blackwell、对抗 Bandit、Partial Monitoring 与校准

模块：`rl/p47_blackwell_adversarial_bandit_math.py`

- `run_exp3()` 对逐轮有界损失运行 EXP3，并保留动作概率和累计损失。
- `external_regret()`、`swap_regret()` 分别审计外部与内部映射偏离收益。
- `blackwell_action()` 针对坐标上界目标集选择把违反方向推回目标集的动作。
- `global_observability_residual()` 检查损失差是否落在联合信号行空间；`calibration_error()` 计算分箱校准误差。

游戏用途：对抗版本漂移下的英雄/路线选择、只观察局部反馈时的学习、约束向量长期可达与胜率预测校准。EXP3 保证依赖损失有界和随机化协议，不能用一次运行的好结果替代理论条件。

## 9. P48：PCE、Sparse Grid、MLMC 与动态 Sobol

模块：`rl/p48_uncertainty_quantification_math.py`

- `total_degree_indices()` 生成总次数 PCE 基；`pce_statistics()` 在正交归一基约定下给出均值、方差、一阶与总 Sobol 指数。
- `dynamic_sobol_indices()` 对随时间变化的 PCE 系数先逐时刻分解，再做时间积分。
- `smolyak_level_indices()` 生成各向同性 Smolyak 层级组合。
- `mlmc_optimal_allocation()` 根据层方差与成本分配样本；`mlmc_estimate()` 汇总望远镜差分均值。

游戏用途：把伤害、延迟、命中率、队伍配合和地图扰动的不确定性分解到输入因素，并减少高保真仿真的预算。PCE 统计要求所用基相对于输入分布正交归一；输入相关时不能直接套用独立 Sobol 解释。

## 10. P49：动态机制设计与信息 Elicitation

模块：`rl/p49_dynamic_mechanism_elicitation_math.py`

- `promised_utility()` 聚合当前效用与折扣继续效用；`dynamic_ic_audit()` 和 `participation_audit()` 报告逐类型偏离 regret 与参与 slack。
- `dynamic_pivot_payment()` 计算给定福利反事实下的外部性支付。
- `logarithmic_score()`、`brier_score()`、`expected_binary_score()` 支持 proper scoring rule 的真实性比较。
- `peer_prediction_payments()` 用报告条件信念和相邻同伴报告计算 log/Brier 支付。

游戏用途：设计动态任务合同、队内资源分配、预测奖励和无金标准信息征集。真实性只在信念、相关性、支付可承诺和串谋假设成立时成立；接口不会从观测数据自动推导这些制度前提。

## 11. 联合接入顺序

1. P42 从回放审计覆盖、隐藏混杂与候选策略价值；
2. P48 量化参数不确定性并决定高成本仿真预算；
3. P43/P44 分别描述混合事件动力学与长期策略生态；
4. P40 对多阶段候选做时间一致风险排序；
5. P41/P47 在有限关注容量和对抗反馈下分配在线试探；
6. P45 检查共享路线/资源的均衡拥塞与社会成本；
7. P46 核验安全或不变量多项式证书；
8. P49 审计奖励、合同、预测支付的 IC、IR 与真实性；
9. 最终动作仍经过原生合法动作掩码、资源、碰撞、MAPF、联合规划和战斗规则。

## 12. 回归测试

```powershell
python -m pytest `
  rl/p40_dynamic_risk_bsde_math_test.py `
  rl/p41_restless_bandit_index_math_test.py `
  rl/p42_sequential_causal_ope_math_test.py `
  rl/p43_pdmp_math_test.py `
  rl/p44_evolutionary_dynamics_math_test.py `
  rl/p45_congestion_wardrop_poa_math_test.py `
  rl/p46_polynomial_sos_moment_math_test.py `
  rl/p47_blackwell_adversarial_bandit_math_test.py `
  rl/p48_uncertainty_quantification_math_test.py `
  rl/p49_dynamic_mechanism_elicitation_math_test.py -q
```

测试覆盖退化极限、概率归一化、嵌套递推、指数阈值、因果权重、事件时刻、单纯形质量守恒、均衡 gap、Gram 重构、反馈可观测性、Sobol 分解以及 IC/IR 审计。
