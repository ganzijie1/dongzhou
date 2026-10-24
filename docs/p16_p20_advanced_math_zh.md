# P16-P20 高级数学能力说明

本文记录 `dongzhou` 新增的多智能体博弈、双层优化、鲁棒 MDP、高阶动态拓扑、受控 Koopman 与因果发现接口。所有实现都面向有限、显式输入；返回值包含残差、对偶间隙、exploitability、秩、条件数、似然或收敛标志，不能用“求解器返回了数值”替代模型假设验证。

## P16 多智能体与不完全信息

有限 Dec-POMDP 使用联合转移与观测核：

$$
b'(s')\propto O(o\mid s',a)\sum_sP(s'\mid s,a)b(s).
$$

`FiniteDecPOMDP` 评估各智能体仅依赖自身观测历史的策略树。`solve_sequence_form_zero_sum()` 以 realization plan 流守恒求扩展式零和博弈；`cfr_plus_zero_sum()`、`double_oracle_zero_sum()` 和 `psro_zero_sum()` 分别提供遗憾最小化与策略库扩展。CE/CCE 使用线性激励约束，不把独立混合 Nash 与相关设备混为一谈。

多跟随者 Stackelberg 只接受可被领导者混合承诺诱导的纯 Nash 联合响应；动态 Stackelberg 枚举确定性 Markov 承诺。二者规模均可能指数增长，预算超限时显式停止。

## P17 双层优化与主动学习

双层问题写成：

$$
\min_x F(x,y^*(x)),\qquad
y^*(x)\in\arg\min_y f(x,y).
$$

`solve_finite_bilevel_linear()` 对有限上层选择精确枚举，下层为 LP。`linear_program_kkt_certificate()` 用原始可行、对偶可行、驻点和互补条件检查 MPEC 候选。

平滑下层满足 $\nabla_yf(\theta,y^*)=0$ 时，隐式灵敏度为：

$$
\frac{dy^*}{d\theta}
=-\left(\nabla^2_{yy}f\right)^{-1}\nabla^2_{y\theta}f.
$$

`implicit_hypergradient()` 实现该公式，并在 Hessian 病态时标记伪逆。可微 QP 解完整 KKT 线性系统；LP 灵敏度只在活动集和基不改变的局部成立。

主动查询层使用 Fisher 信息、D-optimal 的 log determinant、A-optimal 的逆信息迹，以及有限假设互信息。`active_irl_query()` 将候选轨迹对的折扣特征差与有限奖励假设转成 Boltzmann 选择似然，从而直接挑选最能区分奖励的演示查询。Wald 置信域沿信息矩阵零空间无界，明确表示数据无法识别的参数方向。

## P18 鲁棒与分布型动态决策

矩形鲁棒 Bellman 算子为：

$$
(TV)(s)=\max_a\left[r(s,a)+\gamma
\min_{p\in\mathcal P_{sa}}p^\mathsf TV\right].
$$

`worst_case_discrete_expectation()` 支持 TV、KL 与离散 Wasserstein 模糊球；`robust_value_iteration()` 假设每个 state-action 的对手转移可独立选择。跨状态耦合或非矩形模糊集不能直接使用该递推。

C51 将 Bellman 后的原子线性投影回固定支撑；分位数接口提供 quantile Huber 损失。指数风险通过 log-sum-exp 确定性等价传播，CVaR 对有限原子的尾部质量精确切分。`stochastic_reach_avoid()` 直接优化目标先达概率，`robust_reward_occupancy_lp()` 则在共享占用流上最大化最差奖励情景。

## P19 高阶动态拓扑与 Graphon

链复形满足：

$$
\partial_k\partial_{k+1}=0,
\qquad H_k=\ker\partial_k/\operatorname{im}\partial_{k+1}.
$$

普通持久同调使用 GF(2) 边界矩阵列约化。高阶 Zigzag 对每个相邻包含计算同调诱导映射；对子区间求 limit-to-colimit 广义秩后做 Möbius 反演，因此输出的是 H0/H1/H2 区间重数，不是逐帧 Betti 数的视觉猜测。

Vineyard 用相邻持久图的 L-infinity 指派跟踪特征；Mapper 的结果依赖 cover、重叠与局部聚类半径。动态 SBM 使用谱聚类和标签对齐，不提供社区标签后验。Graphon 分块估计依赖节点排序；Logit 平均场返回给定初始化与阻尼下的固定点。

高阶扩散使用：

$$
L_k=\partial_k^\mathsf T\partial_k
+\partial_{k+1}\partial_{k+1}^\mathsf T,
\qquad x(t)=e^{-tL_k}x(0).
$$

## P20 受控算子与因果发现

DMDc 拟合：

$$
X'\approx AX+BU.
$$

EDMDc 将状态先映入调用方定义的有限观测字典，再拟合 Koopman 近似。`koopman_mpc()` 只在显式控制候选上求有限时域二次代价。Ulam 方法通过状态分箱估计 Perron-Frobenius 转移矩阵，结果依赖分箱分辨率和样本覆盖。

`stochastic_viability_kernel()` 求指定单步留存概率下的最大受控不变子集。`notears_linear()` 使用：

$$
h(W)=\operatorname{tr}(e^{W\circ W})-d=0
$$

约束候选图无环。PC 骨架依赖高斯偏相关和显著性阈值；ICP 依赖跨环境机制不变性。它们是结构候选和诊断工具，不会仅凭观测数据自动证明因果方向。遗漏变量 partial-R2 与 simulation-lemma 界用于量化结论对隐藏混杂和跨关卡模型误差的敏感度。

## 验证

```powershell
python -m pytest `
  rl/p16_multiagent_game_math_test.py `
  rl/p17_bilevel_active_learning_math_test.py `
  rl/p18_robust_distributional_mdp_math_test.py `
  rl/p19_dynamic_topology_graphon_math_test.py `
  rl/p20_controlled_koopman_causal_math_test.py -q
```

这些模块默认不接管在线战斗控制。建议流程是“回放或策划数据 -> 数学分析/校准 -> 产生有限候选或权重 -> 既有规划器与规则层复核”。

后续的生存概率、有限情景鲁棒控制、在线变化检测、Perron-Frobenius 投入产出模型、时序回放因果图与跨关卡迁移诊断见 `docs/p21_adaptive_safe_economic_math_zh.md`。
