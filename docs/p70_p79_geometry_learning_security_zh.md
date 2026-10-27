# P70-P79：几何控制、轨迹优化、安全学习与分布式监督

本批模块把连续控制、可达集、采样控制、信息几何、轨迹表征、安全学习和分布式安全接入游戏模型。P72 保留给时序逻辑（STL）路线，本次不占用该编号。

## P70 收缩理论与增量稳定性

`rl/p70_contraction_incremental_stability_math.py` 提供收缩度量上下界、连续/离散收缩判据、最大收缩率、增量误差界、离散测地能量及测地反馈。可用于证明两个近邻游戏状态在相同闭环控制下是否会重新靠拢，并构造对模型误差有恢复能力的跟踪器。

## P71 可达集的集合表示

`rl/p71_set_reachability_math.py` 实现 Zonotope、Constrained Zonotope、支撑函数、盒区间降阶、线性一步可达集和截断 Taylor Model。它适合批量传播角色位置、速度、延迟和扰动的不确定集合，避免只检查单条预测轨迹。

## P73 风险敏感路径积分控制

`rl/p73_path_integral_control_math.py` 实现指数代价权重、熵风险、desirability、KL-control 策略、控制即推断后验和 MPPI 控制更新。接口会报告有效样本量，便于识别权重塌缩，服务于走位、追逃和动态避障。

## P74 微分动态规划

`rl/p74_differential_dynamic_programming_math.py` 提供 iLQR 的 Q 函数导数、DDP 二阶动力学曲率修正、正则化反馈律、价值导数回传、期望下降量、有限差分线性化和 SQP KKT 残差。它可作为短时域技能轨迹优化器，也能审计一次迭代是否真的下降。

## P75 Fisher-Rao 与自然梯度

`rl/p75_information_geometry_math.py` 覆盖概率单纯形校验、Fisher-Rao 内积/距离/测地线、分类策略自然梯度、熵镜像步、经验 Fisher 和参数空间自然梯度。用于在策略分布而非欧氏参数距离下限制更新幅度。

## P76 轨迹签名与粗糙路径

`rl/p76_path_signature_rough_math.py` 实现签名维数、Witt 维数、二阶签名、Chen 拼接、二阶 log-signature、shuffle 恒等式残差、lead-lag 变换、路径变差和受控 Euler 积分。它能把不等长回放编码为保留事件次序的固定维特征。

## P77 高斯过程与安全贝叶斯优化

`rl/p77_safe_bayesian_optimization_math.py` 提供 RBF 核、GP 后验、置信界、EI、GP-UCB/LCB、离散 SafeOpt 集合、多保真自回归协方差和成本感知采集函数。适合在真实对局预算受限时调节战术阈值，同时用安全下界阻止明显危险试验。

## P78 拜占庭鲁棒协同与抗攻击估计

`rl/p78_byzantine_resilient_estimation_math.py` 实现 Trimmed Mean、W-MSR、几何中位数、创新 Mahalanobis 分数、CUSUM、静态攻击残差、可观测矩阵、稀疏可观测性审计和图 r-reachability。它可降低异常队友状态、坏传感器或恶意消息对集结决策的影响。

## P79 分布式事件系统与部分观测监督控制

`rl/p79_decentralized_supervisory_control_math.py` 在有限回放语言上实现 conjunctive coobservability 审计、本地决策融合、diagnosability、codiagnosability 和 current-state opacity。它可检测“每个局部控制器都无法安全否决”的动作冲突，判断故障是否能被至少一个观察器识别，并检查隐藏战术状态是否从可观测事件中泄露。

## 联合接入顺序

1. P71 传播当前状态与扰动集合，P70 检查闭环跟踪是否增量稳定。
2. P74 或 P73 生成候选轨迹，P75 约束策略分布更新，P76 压缩回放轨迹。
3. P77 在安全集合内选择下一组参数；P78 聚合多智能体估计并检测异常。
4. P79 在动作下发前审计局部可观测性、故障诊断和信息隐藏约束。

所有结果均是决策支持量：有限回放语言不等价于无界自动机证明，GP 置信区间依赖核与噪声假设，收缩或可达集证书也只对给定模型和扰动界有效。

## 验证

```powershell
python -m pytest rl/p70_contraction_incremental_stability_math_test.py rl/p71_set_reachability_math_test.py rl/p73_path_integral_control_math_test.py rl/p74_differential_dynamic_programming_math_test.py rl/p75_information_geometry_math_test.py rl/p76_path_signature_rough_math_test.py rl/p77_safe_bayesian_optimization_math_test.py rl/p78_byzantine_resilient_estimation_math_test.py rl/p79_decentralized_supervisory_control_math_test.py -q
```
