# P31-P39：优化、机制、风险、验证、平均场、网络与量子博弈

本轮把当前 12 份数学文档接入可执行游戏模型，聚合为九个模块：

- `rl/p31_variational_stochastic_optimization_math.py`
- `rl/p32_common_information_game_math.py`
- `rl/p33_offline_reinforcement_learning_math.py`
- `rl/p34_bayesian_mechanism_contract_math.py`
- `rl/p35_large_deviation_risk_math.py`
- `rl/p36_probabilistic_model_checking_math.py`
- `rl/p37_master_mean_field_control_math.py`
- `rl/p38_stochastic_network_calculus_math.py`
- `rl/p39_quantum_game_math.py`

这些模块属于离线分析、校准、验证或低频规划层。它们不创建原生游戏不存在的动作，也不绕过地图、资源、碰撞、技能、联合规划和回放验收。

## 1. P31：VI、Mirror/Extragradient、Proximal 与随机逼近

对应 Mirror Descent、Extragradient、Optimistic Mirror Descent、Minty/Stampacchia VI、Proximal Point、Operator Splitting、Robbins-Monro、ODE method、Two-timescale actor-critic、Borkar-Meyn 与 Polyak-Ruppert 文档。

`mirror_descent_simplex()` 实现熵镜像下降，适合动作概率和资源份额；`extragradient()` 处理单调 VI 与鞍点旋转；`optimistic_gradient()` 使用上一轮梯度预测当前在线更新。

`variational_inequality_gap()` 分开报告有限比较集上的 Stampacchia 与 Minty gap，避免混用两个定义。`affine_proximal_point()` 精确解仿射 resolvent；`douglas_rachford()` 接受两个外部 proximal operator。

`robbins_monro()`、`two_timescale_stochastic_approximation()` 和 `polyak_ruppert_average()` 暴露完整迭代轨迹；`borkar_meyn_stability_diagnostic()` 只做经验径向漂移检查，不伪称稳定性证明。

游戏用途：求解局部零和战术鞍点、在线资源份额、双时间尺度价值/策略更新和分布式协调子问题。

## 2. P32：Common Information、Occupancy-state、Policy Graph 与 BCE

`common_information_belief_update()` 在公共动作和公共信号后更新隐藏状态 belief。`occupancy_state_transition()` 用两个只依赖私人类型的去中心化策略推进“世界状态 × 私人类型”分布。

`evaluate_two_agent_policy_graph()` 精确评估有限时域 Dec-POMDP policy graph，包括动作节点、私人观察与节点转移。`bayesian_correlated_equilibrium()` 用 LP 求有限双玩家 Bayesian correlated equilibrium，并报告最小 obedience slack。

游戏用途：战争迷雾下的队伍公共信念、有限通信策略图、角色私人信息和推荐策略激励审计。

## 3. P33：FQE、FQI、CQL 与 DICE

`fitted_q_evaluation()` 对固定策略做 tabular FQE；`fitted_q_iteration()` 做经验 Bellman 最优备份。未观测动作不会被伪装成有数据支持的精确估计。

`conservative_q_learning()` 同时优化 Bellman 误差和 log-sum-exp 保守项，使数据外动作价值下降。`discounted_occupancy_ratio()` 从已知小型 MDP 精确计算目标/行为占用测度比、unsupported mass 和 concentrability；`marginalized_importance_value()` 使用边缘密度比估计折扣价值。

`linear_bellman_completeness_diagnostic()` 把 Bellman backup 投影到给定线性函数类，报告最大和均方残差。小残差不证明全分布 completeness。

游戏用途：回放策略评估、离线候选策略训练、数据覆盖审计和版本外 OPE。

## 4. P34：Bayesian Mechanism、VCG、Myerson 与 Principal-Agent

`vcg_clarke_pivot()` 对有限结果集选择社会福利最大结果并计算 Clarke pivot 外部性支付。`myerson_iid_single_item_auction()` 实现正则 i.i.d. 单物品场景中的二价加保留价形式；`regular_virtual_value()` 计算给定 CDF/PDF 上的虚拟价值。

`audit_two_player_direct_mechanism()` 对有限直接机制逐项审计 DSIC、BIC、interim IR 与期望收入。`optimal_hidden_action_contract()` 枚举要诱导的行动并用 LP 求满足 IC、IR 和有限责任的最低成本结果合同。

游戏用途：角色/资源分配、匹配激励、团队奖励与隐藏行动审计。虚拟支付只能用于模型和策划机制，不能绕过真实产品合规与经济系统规则。

## 5. P35：Donsker-Varadhan、LDP、Chernoff/Cramér 与风险敏感控制

`donsker_varadhan_discrete()` 返回 log moment、最优指数倾斜分布、KL 成本和变分值；`entropy_robust_expectation()` 给出 KL 惩罚分布鲁棒解释。

`cramer_transform()` 数值计算有限分布对数矩母函数的 Legendre-Fenchel 共轭；`chernoff_tail_bound()` 限制非负倾斜用于右尾。`freidlin_wentzell_action()` 计算小噪声路径作用量的 Euler 近似。

`finite_horizon_risk_sensitive_dp()` 在 tabular MDP 上执行乘法动态规划，并在 `theta=0` 时恢复风险中性期望递推。`exponential_tilt_samples()` 同时报告重要性权重和 ESS。

游戏用途：团灭、翻盘和关键资源丢失等尾部损失；风险参数与指数矩必须由独立回放校准。

## 6. P36：PCTL、CSL、概率自动机与统计模型检测

`dtmc_reachability()` 求 DTMC 无界可达最小不动点；`mdp_reachability()` 对 MDP/概率自动机计算最小或最大调度器概率；`pctl_bounded_until()` 计算步数有界 until。

`ctmc_uniformization()` 用 Poisson 级数求 CTMC 瞬态分布并报告截断质量；`csl_time_bounded_reachability()` 通过目标吸收化验证真实时间窗口可达性质。

`statistical_model_check()` 给固定样本 Hoeffding 区间；`sequential_probability_ratio_test()` 实现带无差异区间的 Wald SPRT。统计结论依赖独立轨迹与预先固定的停止规则。

游戏用途：验证“限定步数内集结”“限定秒数内响应”“团灭概率不超过阈值”和版本回归门禁。

## 7. P37：Master Equation、有限玩家误差与 Mean-field Control

`solve_finite_state_mfg()` 用松弛前向-后向迭代求有限状态 MFG，可选熵正则策略。`empirical_lions_derivative()` 对经验粒子 lift 做中心差分并按粒子数缩放。

`master_equation_residual()` 按本轮文档的损失最小化符号约定组合时间、状态 Laplacian、Hamiltonian 和测度导数项。`mean_field_control_marginal_cost()` 加入总体分布外部性，明确区分分散 MFG 与社会规划 MFC。

`finite_player_error_diagnostic()` 分开报告价值误差与 epsilon-Nash 单方改善；`estimate_finite_player_rate()` 只拟合经验幂律，不把有限范围拟合当成普适定理。

游戏用途：大量单位/兵线/玩家生态的分布控制。十名高度异质英雄默认不强行当作单总体无限玩家极限。

## 8. P38：随机 Network Calculus 与有效带宽

`min_plus_convolution()`、`min_plus_deconvolution()`、`concatenate_service_curves()` 和 `leftover_service_curve()` 提供离散网络演算。`deterministic_queue_bounds()` 计算有限网格上的垂直 backlog 与水平 delay 偏差。

`effective_bandwidth()` 与 `effective_capacity()` 使用稳定 log-sum-exp 计算有限时间指数矩；`effective_bandwidth_chernoff_bound()` 给单个倾斜参数下的容量尾界。

`stochastic_split_bound()` 组合到达和服务违约函数；`constant_service_tail_bound()` 给独立增量常数服务队列的几何级数界；`markov_modulated_effective_bandwidth()` 用倾斜矩阵谱半径处理战斗/非战斗阶段。

游戏用途：收包、解码、推理、动作仲裁和发包的端到端实时链；平均吞吐不能替代高分位延迟与拥塞保证。

## 9. P39：量子博弈

`density_matrix()`、`partial_trace()`、`apply_quantum_channel()` 和 `povm_probabilities()` 提供可审计量子态、CPTP 和测量基础。`ewl_two_player_game()` 实现 EWL 协议，并显式接收策略集外部构造的局部幺正操作。

`chsh_optimal_quantum_strategy()` 复现 Bell 态 CHSH 策略、Tsirelson 胜率与无信号残差。`depolarizing_channel()` 用于噪声消融；`finite_quantum_nash_diagnostic()` 对已经评估的有限量子策略集计算单方偏离 regret。

游戏用途以理论比较和经典计算机上的量子启发式相关模型为主。没有量子硬件、空间分离和测量协议时，不把复数模型称为物理量子优势。

## 10. 推荐联合流程

1. P32 维护公共 belief 与分散策略结构；
2. P33 从回放评估候选策略并检查覆盖；
3. P31 求解 VI、鞍点和两时间尺度更新；
4. P34 审计分配、激励和团队合同；
5. P35 评估尾部与风险敏感策略；
6. P36 把关键安全需求写成可达/时限概率并验证；
7. P37 在大群体层建模分散均衡与社会最优差异；
8. P38 验证实时服务链的 backlog、延迟与拥塞；
9. P39 仅在协议和资源匹配时研究量子或量子启发式相关性；
10. 所有候选动作继续通过原生动作掩码、资源、碰撞、MAPF、联合规划和战斗规则。

## 11. 回归测试

```powershell
python -m pytest `
  rl/p31_variational_stochastic_optimization_math_test.py `
  rl/p32_common_information_game_math_test.py `
  rl/p33_offline_reinforcement_learning_math_test.py `
  rl/p34_bayesian_mechanism_contract_math_test.py `
  rl/p35_large_deviation_risk_math_test.py `
  rl/p36_probabilistic_model_checking_math_test.py `
  rl/p37_master_mean_field_control_math_test.py `
  rl/p38_stochastic_network_calculus_math_test.py `
  rl/p39_quantum_game_math_test.py -q
```

定向测试覆盖 44 个核心契约，包括迭代收敛、Bayes 更新、BCE obedience、离线覆盖、DSIC/BIC/IR、DV 对偶、风险敏感递推、PCTL/CSL、MFG 外部性、min-plus 组合、EWL 经典恢复和 CHSH Tsirelson 胜率。
