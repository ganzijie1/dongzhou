# P24-P30：部分可观测规划、多智能体协调、资源约束与有限样本保证

本文对应：

- `rl/p24_belief_space_planning_math.py`
- `rl/p25_stochastic_game_math.py`
- `rl/p26_factor_graph_distributed_math.py`
- `rl/p27_constrained_budgeted_mdp_math.py`
- `rl/p28_continuous_time_mdp_math.py`
- `rl/p29_extreme_tail_importance_math.py`
- `rl/p30_finite_sample_guarantees_math.py`

这些模块把本轮文档中的数学方法接入游戏模型，但不直接改写实时战斗动作。模块产出候选策略、价值、风险、置信界和诊断量；真正执行仍必须经过原生动作掩码、资源、地图通行、联合规划和战斗规则。

## 1. P24：Alpha-vector、PBVI、POMCPOW、DESPOT 与 I-POMDP

有限时域 POMDP 的分段线性凸价值表示为：

$$
V_t(b)=\max_{\alpha\in\Gamma_t} b^{\mathsf T}\alpha.
$$

`alpha_vector_dynamic_programming()` 枚举观察分支并用信念单纯形上的线性规划删除处处劣势的向量；`alpha_vector_action()` 在给定信念上返回动作与价值。精确备份的复杂度随观察数和向量数指数增长，因此实现设置候选上限并在超限时显式报错。

`point_based_value_iteration()` 只在调用方给出的可达信念点上备份，适合离线构建对线、转线和视野不完整时的策略表。它只保证这些点上的改进，不把有限信念集结果伪称为全信念空间最优。

`pomcpow_plan()` 使用状态粒子、动作渐进扩宽和观察渐进扩宽处理大观察空间；`despot_scenario_plan()` 在固定随机情景上比较有限策略树，并返回经验下界、Hoeffding 罚项和正则化下界。两者都要求独立种子的回放外验证。

`interactive_belief_update()` 更新“世界状态 × 对手类型”的联合信念；`finite_level_logit_reasoning()` 实现有限层级的软最佳反应。它是截断 I-POMDP 近似，不是无限嵌套信念的精确解。

游戏映射：隐藏敌方位置是状态不确定性，草丛/战争迷雾反馈是观察，侦察与交战是动作；对手类型可表示激进、保守、诱敌等有限模型。

## 2. P25：Shapley 算子、随机博弈、MPE 与势博弈

折扣零和随机博弈满足 Shapley 方程：

$$
V(s)=\operatorname{val}_{x,y}
\left[r(s,a,b)+\gamma\sum_{s'}P(s'\mid s,a,b)V(s')\right].
$$

`solve_zero_sum_matrix_game()` 用原始/对偶 LP 返回双方混合策略、价值与对偶间隙；`shapley_value_iteration()` 在每个状态解矩阵博弈。`average_reward_zero_sum_game()` 使用相对价值迭代，并返回 span 残差；只有满足遍历/通信条件时，单一平均收益解释才成立。

`evaluate_general_sum_policy()` 评估双方平稳混合策略；`markov_perfect_equilibrium_gap()` 计算逐方最佳反应改进量，作为 MPE 候选证书；`enumerate_pure_markov_perfect_equilibria()` 仅对规模受控的纯平稳策略做精确枚举。

`stage_potential_residual()` 检查有限阶段博弈是否满足精确势函数的单边偏差等式。残差接近零只说明所给收益表接近势博弈，不保证动态随机博弈整体具有势结构。

游戏映射：状态是兵线、资源、存活与地图控制摘要；双方联合行动是开团、拉扯、转线或换资源；MPE gap 可审计某个版本策略是否仍有明显单边改进空间。

## 3. P26：因子图、Junction Tree、Max-Sum/DCOP 与 ADMM

因子分解写成：

$$
p(x)\propto\prod_f\psi_f(x_f).
$$

`loopy_belief_propagation()` 实现 Sum-Product：树上给出精确边缘分布，环图上返回迭代残差与收敛标志。环图收敛不等于边缘分布精确。

`junction_tree_calibrate()` 校验树结构和 running-intersection property，再做 clique 消息传递，返回 clique/变量边缘分布及 separator 一致性残差。

`max_sum_dcop()` 对分解效用运行 Max-Sum。树因子图在规模上限内用全局枚举审计最优指派；环图返回局部消息解、残差和是否收敛，不能把局部解标成全局最优。

共识 ADMM 解：

$$
\min_{x_i,z}\sum_i f_i(x_i),\qquad x_i=z.
$$

`consensus_admm()` 接受各子问题的 proximal operator，返回局部变量、共识变量、对偶变量、原始/对偶残差和自适应罚参数历史。

游戏映射：英雄局部目标、技能配合、集火冲突和路线占用作为因子；Max-Sum/DCOP 生成团队候选指派，ADMM 用于低频分布式资源配额。最终指派仍交给动作合法性和联合路径规划检查。

## 4. P27：占用测度 CMDP 与 Budgeted MDP

`solve_discounted_cmdp()` 解未归一化折扣占用测度 LP：

$$
\sum_a x(s,a)-\gamma\sum_{s',a'}P(s\mid s',a')x(s',a')=\mu_0(s),
$$

$$
\max_x\sum_{s,a}r(s,a)x(s,a),\qquad
\sum_{s,a}c_k(s,a)x(s,a)\le B_k.
$$

占用总质量为 $1/(1-\gamma)$，因此预算使用普通折扣和单位。返回流守恒残差、预算违反量和 LP 影子价格；`evaluate_discounted_policy()` 用线性方程独立复核策略价值。

`finite_horizon_budgeted_mdp()` 把剩余整数预算加入状态，并要求所有正概率后继都不超预算。这是逐路径硬预算，不是期望预算。`pareto_prune()` 保留收益最大化、成本最小化意义下的非支配候选。

游戏映射：血量、法力、技能冷却次数、侦察次数、经济和风险额度都可作为约束。期望消耗用 CMDP，绝不能超出的消耗用 Budgeted MDP。

## 5. P28：CTMDP 与 uniformization

连续时间生成元满足非对角元素非负且逐行和为零。`uniformize_ctmdp()` 选择：

$$
\Lambda\ge\max_{s,a}(-Q^a_{ss}),\qquad
P^a=I+Q^a/\Lambda.
$$

`discounted_ctmdp_value_iteration()` 通过：

$$
V(s)=\max_a\left[
\frac{r(s,a)}{\beta+\Lambda}
+\frac{\Lambda}{\beta+\Lambda}\sum_{s'}P^a_{ss'}V(s')
\right]
$$

求解连续时间折扣 HJB，并在原始生成元上报告残差。`evaluate_ctmdp_policy()` 用线性系统精确复核固定策略。

`average_reward_ctmdp()` 做相对价值迭代并报告 span 残差；`uniformized_transient_distribution()` 用 Poisson 级数计算固定策略下的瞬态分布和截断质量。

游戏映射：技能触发、复活、兵线到达和网络事件可按不同速率发生。uniformization 允许在保留连续时间语义的同时复用离散规划器；速率必须来自日志校准，不能由帧率直接冒充。

## 6. P29：GEV/POT、尾相关与交叉熵重要抽样

`fit_gev()` 拟合分块最大值，使用常见形状参数 $\xi$；`gev_return_level()` 计算给定非超越概率的返回水平。`fit_gpd()` 对阈值超额量拟合 GPD，`pot_tail_probability()` 使用：

$$
P(X>x)=P(X>u)P(X-u>x-u\mid X>u).
$$

阈值、分块长度和独立性需要用诊断选择；接口不会把一次拟合自动解释为可靠外推。

`empirical_tail_dependence()` 给出有限分位点的秩估计；`student_t_tail_dependence()` 和 `archimedean_tail_dependence()` 返回指定 copula 的渐近尾相关系数。有限阈值估计与渐近系数不可混用。

`cross_entropy_gaussian_importance_sampling()` 自适应高斯提议分布，并在最终估计中加入原分布防御混合。返回概率、标准误、事件有效样本量、提议均值/协方差和各轮 elite 阈值。正式稀有事件结论应跨种子重复并结合 P23 AMS/Subset Simulation 交叉验证。

游戏映射：极端延迟、连续控制失败、团灭链和多变量同时恶化可作为尾部事件；尾相关用于识别风险是否共同爆发，而不是只看各指标的边缘分布。

## 7. P30：PAC、经验 Bernstein、Anytime CS 与共形风险控制

`pac_mdp_diagnostics()` 比较执行价值与参考最优价值，统计超过 $\epsilon$ 的坏步数。它只审计调用方提供的 PAC-MDP 理论上界，不凭状态数和样本数杜撰适用于所有算法的界。

`pac_bayes_strategy_bound()` 对有限策略后验计算 Gibbs 经验风险和：

$$
\mathrm{KL}(Q\Vert P),
$$

再用 PAC-Bayes-kl 不等式反演真实风险上界。先验必须在查看当前训练样本前确定；数据依赖先验需使用相应修正理论。

`empirical_bernstein_upper()` 利用样本方差给有界 IID 指标的一侧上界。`anytime_hoeffding_confidence_sequence()` 通过可求和的逐时刻错误预算给出任意停止仍有效的置信序列；它比固定时刻区间保守，但允许持续监控。

`conformal_risk_control()` 用：

$$
\widehat R^+(\lambda)=
\frac{\sum_{i=1}^n L_i(\lambda)+B}{n+1}
$$

选择风险上界不超过目标的最大控制参数。`weighted_conformal_quantile()` 把测试点权重作为无穷大校准分数质量，适用于已知或估计密度比下的协变量漂移；若校准质量不足会返回无穷大而不是伪造有限阈值。`density_ratio_weights()` 和 `effective_sample_size()` 用于报告权重退化。

游戏映射：用 PAC/PAC-Bayes 审计策略族，用经验 Bernstein 或置信序列监控胜率、死亡率和违规率，用 CRC 选择风险阈值，用加权共形处理地图、版本或玩家分布漂移。覆盖保证仍依赖交换性、密度比和损失界等假设。

## 8. 推荐联合流程

1. P24 从战争迷雾与对手类型信念生成候选行动；
2. P25 审计双方策略和单边改进，P26 协调队内局部任务；
3. P27 施加期望资源约束和逐路径硬预算；
4. P28 对异步事件做连续时间价值与瞬态风险评估；
5. P29 压测延迟、团灭和资源崩溃等尾部事件；
6. P30 给离线评估和在线监控附加有限样本上界；
7. 候选动作通过原生动作掩码、资源、碰撞、MAPF、联合规划和战斗规则后才可执行；
8. 所有近似模块保存残差、收敛标志、随机种子和回放版本。

## 9. 回归测试

```powershell
python -m pytest `
  rl/p24_belief_space_planning_math_test.py `
  rl/p25_stochastic_game_math_test.py `
  rl/p26_factor_graph_distributed_math_test.py `
  rl/p27_constrained_budgeted_mdp_math_test.py `
  rl/p28_continuous_time_mdp_math_test.py `
  rl/p29_extreme_tail_importance_math_test.py `
  rl/p30_finite_sample_guarantees_math_test.py -q
```

定向测试覆盖 alpha-vector 支配剪枝、PBVI、渐进扩宽、情景下界、嵌套信念、Shapley/MPE、因子图与 Junction Tree、Max-Sum、ADMM、占用测度与硬预算、uniformization、连续时间 Bellman、GEV/GPD 与尾 copula、重要抽样、PAC-Bayes、任意时刻置信序列、CRC 和加权共形阈值。
