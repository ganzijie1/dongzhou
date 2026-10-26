# P50-P60：可达安全、状态估计、并发系统、随机流与多目标价值

本批次把 11 篇专题文档落成相互独立、可测试的数学模块。它们用于分析、候选生成、安全过滤和运行时诊断，不直接扩展引擎的合法动作集，也不绕过碰撞、资源、冷却、目标有效性与联合规划约束。

## 1. P50：Backward Reachable Tube 与追逃博弈

模块：rl/p50_reachability_pursuit_evasion_math.py。

- backward_reachable_tube() 在有限离散状态和确定性对抗转移上反向计算最坏情形可达管。
- finite_horizon_reach_avoid() 计算有限时域随机 reach-avoid 最大概率及逐时策略。
- constant_speed_intercept_time() 解恒速拦截的最早非负时间，可用于追击候选的快速筛选。

边界：离散 BRT 是有限状态近似；连续地图需要先网格化或构造抽象状态，恒速拦截也不包含障碍、转向半径和技能延迟。

## 2. P51：CLF、CBF、CLF-CBF-QP 与高阶障碍函数

模块：rl/p51_clf_cbf_safety_math.py。

- affine_cbf_constraint() 与 affine_clf_constraint() 生成控制仿射系统的一阶线性约束。
- minimum_change_safety_filter() 以最小控制改动满足硬 CBF，并通过松弛变量处理 CLF 目标。
- high_order_barrier_chain() 计算相对阶大于一时的递推障碍量。

边界：安全保证依赖模型、Lie 导数、采样频率和可行性。离散碰撞规则仍由引擎最终裁决，QP 输出不能直接越过合法动作掩码。

## 3. P52：EKF、UKF、粒子滤波、IMM 与 H-infinity 滤波

模块：rl/p52_state_estimation_math.py。

- 提供 EKF 预测/更新及 Joseph 形式协方差更新。
- 提供无迹变换的 sigma 点、加权均值与协方差。
- 提供粒子权重更新、有效样本量和系统重采样。
- 提供 IMM 混合概率、状态与协方差融合。
- 提供 H-infinity 信息形式协方差更新。

边界：调用方负责状态流形、角度环绕、观测关联和模型切换概率的语义；数值正定检查不等价于模型正确。

## 4. P53：标记点过程

模块：rl/p53_marked_point_process_math.py。

- marked_exponential_intensity() 支持自激、互激、抑制和时变基线。
- hawkes_log_likelihood() 给出非负指数 Hawkes 过程的对数似然。
- compensator_increments() 支持时间重标度诊断。
- branching_ratio() 检查非负激励核的稳定性。

边界：带抑制的裁剪强度不应套用非负 Hawkes 的闭式似然；游戏事件的漏记和并发时间戳需要在拟合前处理。

## 5. P54：Cox / Determinantal Point Process 与空间统计

模块：rl/p54_spatial_point_process_math.py。

- 提供 PPP 空区域概率、覆盖概率和接触距离分布。
- 提供 Thomas 聚簇过程的对相关函数。
- 提供有限 DPP 核合法性审计、二阶包含概率和 L-ensemble 子集概率。
- 提供观测点集的接触距离与最近邻距离。

边界：有限 DPP 作用于离散候选点；连续地图的边界修正、不可行地形和非均匀暴露度应由调用方显式建模。

## 6. P55：可达图

模块：rl/p55_reachability_graph_math.py。

- reachable_set() 与 reach_avoid_shortest_path() 处理合法边构成的可达域和避险路径。
- strongly_connected_components() 识别困住单位的封闭区域。
- adversarial_attractor() 计算轮流对抗图上的强制可达集合。
- maximum_reach_probability() 处理有限 MDP 的无限时域目标可达概率。

边界：图边必须来自引擎真实通行、技能、传送和时序规则；缺失动态阻挡时，可达结论只对当前图快照成立。

## 7. P56：死锁与活锁监测

模块：rl/p56_deadlock_livelock_math.py。

- 等待图环检测用于互相占位和资源等待死锁。
- 绕数、周期性和方向翻转指标用于识别绕塔、绕墙和来回振荡。
- 综合诊断区分位移停滞、低速发呆、周期活锁和轨道式绕圈。

边界：监测器只报告证据，不自行决定攻击、撤退或寻路；阈值必须在真实回放上校准，并保留目标进展信号以减少误报。

## 8. P57：Timed Automata、Petri Net 与并发系统

模块：rl/p57_timed_automata_petri_math.py。

- validate_timed_trace() 验证显式时钟、守卫、重置和位置不变量。
- Petri 网接口覆盖使能、发射、可达标识、死锁和 P-invariant 残差。
- timed_transition_available() 检查时间窗，exponential_race() 采样随机 Petri 网的竞争事件。

边界：显式状态枚举只适合小型并发子系统；大型行为树和技能系统应先做组合抽象，避免状态爆炸。

## 9. P58：排队网络与重交通极限

模块：rl/p58_queueing_heavy_traffic_math.py。

- 提供 Little 定律、M/M/1、Jackson 交通方程和节点性能。
- 提供 Kingman 等待时间近似与无限服务器均值。
- 提供流体队列、反射布朗近似和平方根人员配置。

边界：Jackson/BCMP 型结论依赖到达、服务和路由假设；战斗事件通常非平稳且相关，重交通结果应作为容量压力指标而非精确逐帧预测。

## 10. P59：Wasserstein 梯度流与 Fokker-Planck 方程

模块：rl/p59_wasserstein_fokker_planck_math.py。

- wasserstein_1d_squared() 计算一维加权经验分布的精确二阶 Wasserstein 距离。
- 提供 Boltzmann 熵、自由能、相对 Fisher 信息和耗散诊断。
- gaussian_heat_jko_sigma() 给出高斯热流 JKO 步的标量更新。
- fokker_planck_no_flux_step() 提供一维无通量显式基准步。

边界：显式离散必须满足稳定性条件；一维基准不能替代二维地图上的守恒有限体积求解器，重归一化只修正数值漂移。

## 11. P60：向量价值、非支配 Bellman、Chebyshev 与超体积

模块：rl/p60_multiobjective_value_math.py。

- nondominated() 维护最大化目标下的 Pareto 前沿。
- weighted_minkowski_sum() 与 nondominated_bellman_backup() 完成有限候选集的集合值备份。
- chebyshev_loss() 支持参考点驱动的标量化。
- hypervolume_2d() 与 hypervolume_contributions_2d() 计算二维最大化前沿相对参考点的超体积。

边界：集合值 Bellman 会随时域和分支快速增长，需在前沿剪枝后再接入；当前动作标签只记录本次备份来源，不是完整后继策略树。

## 12. 建议的联合接入顺序

1. P52 从不完整观测形成状态与不确定性估计。
2. P53/P54 更新事件强度与空间风险。
3. P55 在原生合法边上生成可达候选。
4. P50 对候选做追逃和 reach-avoid 评估。
5. P51 对连续控制量做最小改动安全过滤。
6. P56/P57 监视停滞、并发冲突与时序违规。
7. P58 估计资源通道、任务队列和服务拥塞。
8. P59 分析群体密度、扩散和分布迁移。
9. P60 只在合法且安全的候选中做多目标选择。
10. 所有结果最终通过引擎动作掩码、碰撞、资源、冷却、联合规划和回放验收。

## 13. 回归验证

专项测试命令：

    python -m pytest rl/p50_reachability_pursuit_evasion_math_test.py rl/p51_clf_cbf_safety_math_test.py rl/p52_state_estimation_math_test.py rl/p53_marked_point_process_math_test.py rl/p54_spatial_point_process_math_test.py rl/p55_reachability_graph_math_test.py rl/p56_deadlock_livelock_math_test.py rl/p57_timed_automata_petri_math_test.py rl/p58_queueing_heavy_traffic_math_test.py rl/p59_wasserstein_fokker_planck_math_test.py rl/p60_multiobjective_value_math_test.py -q

本批次包含 38 项专项测试，覆盖正常路径、输入校验、边界条件和关键不变量。
