# P21 非平稳安全控制、Perron-Frobenius 经济模型与回放因果迁移

本文说明 `rl/p21_adaptive_safe_economic_math.py` 的输入契约、数学含义和使用边界。P21 补充 P18 的鲁棒 MDP 与 P20 的 Koopman/因果发现能力，仍属于回放分析、离线校准和低频规划层，不直接生成或绕过原生合法动作。

## 1. 生存概率与 reach-avoid

给定安全集 $K$，有限时域生存价值为

$$
V_0(s)=\mathbf{1}_K(s),\qquad
V_{h+1}(s)=\mathbf{1}_K(s)\max_a\sum_{s'}P(s'\mid s,a)V_h(s').
$$

`finite_horizon_survival_probability()` 返回所有剩余步数下的价值和策略。它计算的是整段轨迹始终留在安全集的概率，与 P18 的“到达目标且避开失败集”不是同一个事件。

无限时域函数 `infinite_horizon_survival_probability()` 从 $\mathbf{1}_K$ 开始做单调递减迭代，求 Bellman 算子的最大不动点：

$$
V^*(s)=\mathbf{1}_K(s)\max_a\sum_{s'}P(s'\mid s,a)V^*(s').
$$

返回值包含收敛标志和残差。无折扣不动点可能收敛很慢，部署前必须检查 `converged`，不能把迭代上限处的数值当作证明。

游戏中可把“单位未阵亡、补给不断、据点未失守”编码成安全状态，把 P18 `stochastic_reach_avoid()` 用于任务成功概率，把本节接口用于全程生存约束。

## 2. 有限情景鲁棒 Bellman 与鲁棒可行核

`scenario_robust_value_iteration()` 对每个状态动作允许对手从有限情景中选择最坏模型：

$$
(TV)(s)=\max_a\min_{k\in\mathcal K}
\left[r_k(s,a)+\gamma\sum_{s'}P_k(s'\mid s,a)V(s')\right].
$$

这是 state-action rectangular 假设。它允许不同状态动作选择不同最坏情景，不适用于“整局只能固定选择同一个全局情景”的耦合不确定性。

三类鲁棒模型必须区分：

- P18 `robust_reward_occupancy_lp()`：固定转移，多奖励情景，共享一套折扣占用测度。
- P18 `robust_value_iteration()`：TV、KL 或 Wasserstein 模糊球，逐状态动作选择最坏转移分布。
- P21 `scenario_robust_value_iteration()`：有限转移/奖励情景，逐状态动作选择最坏情景。

`robust_viability_kernel()` 使用同一有限情景集合，保留满足

$$
\exists a\quad\min_k P_k(S_{t+1}\in K_i\mid s,a)\ge\beta
$$

的状态，并迭代到集合不再缩小。返回的 `viable_actions` 是在所有给定情景下共同安全的动作；它不覆盖情景集之外的未知模型。

## 3. 在线变化检测与策略切换

`TwoSidedCUSUMDetector` 对已校准基准均值 $\mu_0$ 同时累计上漂移和下漂移：

$$
G_t^+=\max(0,G_{t-1}^+ + x_t-\mu_0-k),
$$

$$
G_t^-=\max(0,G_{t-1}^- + \mu_0-x_t-k).
$$

任一统计量超过阈值 $h$ 时报警，并报告方向。`allowance` 控制忽略的小波动，`minimum_observations` 避免开局即报警。P18 `PageHinkleyPolicySwitcher` 更适合未知均值下的单侧损失上漂移；CUSUM 更适合有稳定基线的双侧变化。

`FixedSharePolicySelector` 将候选策略视为专家，按观测损失做指数权重更新，再混入固定共享质量：

$$
\widetilde w_{i,t+1}\propto w_{i,t}e^{-\eta\ell_{i,t}},\qquad
w_{i,t+1}=(1-\alpha)\widetilde w_{i,t+1}+\frac{\alpha}{N}.
$$

`minimum_dwell` 和 `switch_margin` 分别限制最小驻留时间和切换优势，减少策略抖动。调用方必须提供每个候选策略在同一回放窗口上的可比损失；只有当前策略的反馈时，不能伪装成全信息更新，应改用带探索的 bandit 方法。

## 4. Perron-Frobenius 与投入产出系统

`perron_frobenius_analysis()` 接受非负方阵 $M$，返回谱半径、归一化左右 Perron 向量、不可约性和特征残差：

$$
Mv=\rho(M)v,\qquad u^{\mathsf T}M=\rho(M)u^{\mathsf T}.
$$

在 P20 中，Ulam 方法先从状态转移样本估计 Markov 矩阵，再用左 Perron 向量解释平稳占用。本节的通用接口还能分析补给传播、资源复制和经济投入产出矩阵。

`leontief_input_output_analysis()` 使用“列表示产出部门、$A_{ij}$ 表示生产一单位部门 $j$ 产出所需的部门 $i$ 投入”的约定，求解

$$
x=Ax+d,\qquad x=(I-A)^{-1}d.
$$

只有 $\rho(A)<1$ 时系统才被判为生产性。若给出直接劳动行向量 $\ell$，总劳动价值为

$$
v^{\mathsf T}=\ell^{\mathsf T}(I-A)^{-1}.
$$

若再给出每单位劳动的实物工资束 $b$，接口分析工资预付约定下的增广矩阵

$$
A_w=A+b\ell^{\mathsf T},\qquad R=\rho(A_w)^{-1}-1.
$$

这里的 $R$ 只对应这一个 Sraffa 型、单一利润率、工资实物化且预付的模型。它不是一般市场利润率，也不能单凭游戏经济日志验证劳动价值论或任何经济学流派。日本数理马克思传统中常见的 Perron-Frobenius、Leontief、Morishima 型分析可以用这些数值量做可复核实验，但理论解释必须另行给出假设。

在游戏中，部门可映射为粮草、兵器、运输和兵员，$d$ 是关卡需求，$x$ 是维持该需求所需总产出。若矩阵不可生产，接口显式报错，避免把爆炸性资源循环当作正常均衡。

## 5. 从回放构造时序因果候选

`lagged_replay_design()` 将多段回放构造成

$$
X_t=f(X_{t-1},\ldots,X_{t-L})+\varepsilon_t,
$$

并保留原始回合编号和时间索引。每行只使用同一回合内的历史，绝不把上一局结尾拼到下一局开头。

`lagged_conditional_independence_graph()` 对所有滞后变量联合回归，并用系数 t 检验筛选“给定其余滞后后仍有条件关联”的有向边。输出张量索引为 `[lag-1, source, target]`，同时返回系数、p 值和设计矩阵条件数。

这个图是线性时滞预测候选，接近条件 Granger 筛选，不等于结构因果图。共同原因、策略选择偏差、隐藏状态、非线性和自相关误差都可能制造伪边。P20 `notears_linear()` 可分析同一时刻的无环候选，`pc_skeleton()` 可做高斯条件独立骨架；两者同样不能仅凭观察回放证明方向。

## 6. 不变因果预测与跨关卡迁移

先用 P20 `invariant_causal_prediction()` 在多个关卡环境中筛选残差机制较稳定的预测变量集合，再用 P21 `cross_environment_transfer_diagnostics()` 做留一环境验证。对每个关卡 $e$，它只在其余关卡拟合：

$$
\widehat\beta_{-e}=\arg\min_\beta
\sum_{j\ne e}\lVert y_j-X_j\beta\rVert_2^2,
$$

然后报告被留出关卡上的 RMSE、各次拟合系数和系数离散度。最坏关卡误差用于发现平均指标掩盖的迁移失败。

推荐顺序是“按局切分回放 -> 构造滞后候选 -> NOTEARS/条件独立生成候选图 -> ICP 筛不变父变量 -> 留一关卡诊断 -> 用 P20 `discounted_model_transfer_bound()` 给价值误差上界”。必须按整局或玩家分组切分，不能把相邻帧随机分到训练集和验证集。

## 7. 验证与接入边界

定向回归：

```powershell
python -m pytest rl/p21_adaptive_safe_economic_math_test.py -q
```

所有概率核必须非负且逐行和为 1，经济矩阵必须非负，回放必须是有限二维数值数组。P21 返回策略索引、可行动作集合、风险和结构候选，但真正进入游戏执行前仍要经过原生合法动作、地图通行、资源、联合规划和战斗规则检查。
