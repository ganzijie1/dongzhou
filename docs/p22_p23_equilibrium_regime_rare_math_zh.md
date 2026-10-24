# P22-P23：线性可解控制、均衡延拓、在线阶段与稀有事件

本文对应：

- `rl/p22_equilibrium_control_continuation_math.py`
- `rl/p23_regime_rare_event_math.py`

这些模块属于离线分析、回放校准、版本压力测试和低频策略层，不绕过原生合法动作、资源、碰撞、联合规划与 MAPF 检查。

## 1. LMDP 与 KL Control

`finite_horizon_lmdp()` 求解正向 KL 控制成本下的有限时域线性可解 MDP。被动转移为零的边在受控转移中仍为零。Bellman 方程为：

$$
V_t(x)=q_t(x)-\lambda\log\sum_y p_0(y\mid x)\exp(-V_{t+1}(y)/\lambda).
$$

desirability 变量为：

$$
z_t(x)=\exp(-V_t(x)/\lambda).
$$

`average_cost_lmdp()` 解非负矩阵的 Perron 特征问题：

$$
\operatorname{Diag}(e^{-q/\lambda})P_0z=\mu z,
\qquad \rho=-\lambda\log\mu.
$$

两种求解器都返回残差和完整受控转移，不生成被动模型支持集之外的动作。

## 2. Nash、QRE、VI 与 Stackelberg 的隐式灵敏度

`implicit_equilibrium_sensitivity()` 对任意局部方程系统：

$$
R(z^\star,\theta)=0
$$

求解：

$$
R_z\frac{\mathrm dz^\star}{\mathrm d\theta}=-R_\theta.
$$

它返回条件数、最小奇异值、秩、线性残差和是否使用伪逆。调用方必须自己保证当前 Nash、VI、KKT 或 Stackelberg 分支的活动集与支持集稳定。

`solve_bimatrix_logit_qre()` 在去除单纯形冗余的 log-odds 坐标中求双矩阵 Logit QRE，并返回对双方理性强度的隐式灵敏度。局部残差为：

$$
R(p,q)=\begin{bmatrix}p-B_1(q)\\q-B_2(p)\end{bmatrix}.
$$

QRE 多解时，返回值只代表初值选中的局部分支。

P17 的 `implicit_hypergradient()`、`equality_qp_sensitivity()` 和 `linear_program_active_set_sensitivity()` 继续负责无约束下层、等式 QP 与固定活动集 LP；P22 补充通用均衡 Jacobian、QRE 与分支诊断。

## 3. 分布鲁棒 Nash 与 Stackelberg

`finite_distributionally_robust_nash()` 接受有限情景成本和模糊分布多面体的顶点。每个纯策略组合的鲁棒成本为：

$$
\varphi_i(a)=\max_{q\in\mathcal Q_i}\sum_s q_s c_{i,s}(a).
$$

随后精确枚举纯鲁棒 Nash。它不声称求得混合分布鲁棒 Nash。

`finite_distributionally_robust_stackelberg()` 分别计算领导者和跟随者的最坏期望成本，支持 optimistic 与 pessimistic 破同分，再枚举纯领导者承诺。共享分布、连续承诺或内生模糊集合需要更一般的原始对偶模型。

## 4. 伪弧长延拓与分岔

`pseudo_arclength_continuation()` 跟踪：

$$
F(z,\lambda)=0.
$$

切向量满足：

$$
\begin{bmatrix}F_z&F_\lambda\end{bmatrix}t=0,
\qquad \lVert t\rVert=1.
$$

校正器解增广系统：

$$
\begin{bmatrix}F(z,\lambda)\\t_k^{\mathsf T}(u-u_p)\end{bmatrix}=0.
$$

返回整条路径、切向量、均衡残差、状态 Jacobian 最小奇异值、实际步长和折叠候选索引。

`classify_static_bifurcation()` 用秩、左右核与横截量区分 regular、fold candidate、branch candidate 和 higher-codimension candidate。`detect_dynamic_bifurcations()` 对连续时间检测零特征值/Hopf 候选，对离散时间检测加一、减一和单位圆复特征值候选。它们是局部谱诊断，不替代高阶非退化证明。

## 5. BOCPD

`BayesianOnlineChangePointDetector` 使用已知观测方差的 Normal-Normal 共轭模型，维护 run length 后验：

$$
p(r_t\mid x_{1:t}).
$$

增长消息为：

$$
\alpha_t(r+1)=\alpha_{t-1}(r)(1-H)p(x_t\mid r).
$$

变点消息为：

$$
\alpha_t(0)=\sum_r\alpha_{t-1}(r)Hp(x_t\mid r_t=0).
$$

实现全程保存归一化对数消息，返回变点概率、MAP run length、预测对数证据和因最大 run length 截断而删除的质量。常数危险率仍需用回放校准。

## 6. HSMM

`hsmm_forward()` 和 `hsmm_viterbi()` 接受逐时刻状态发射对数似然、段级转移矩阵、初始分布和显式持续时间分布。段结束前向递推为：

$$
\alpha_t(j)=\sum_d p_j(d)B_j(t,d)\sum_i\alpha_{t-d}(i)A_{ij}.
$$

Viterbi 返回逐帧状态、半开区间段列表和最优路径对数概率。持续时间上界必须覆盖业务中的长阶段，否则长段会被强制拆分。

## 7. Adaptive Multilevel Splitting

`adaptive_multilevel_splitting()` 对轨迹对象执行自适应淘汰、复制与续跑。若每轮淘汰 k 个、粒子总数为 N，估计量使用：

$$
\widehat p=\left(1-\frac{k}{N}\right)^J\frac{N_A}{N}.
$$

调用方提供初始轨迹模拟、反应坐标和保持越级前缀的 branching 函数。返回层级、终态得分、祖先编号、谱系集中度、并列层数和收敛状态。无偏性仍依赖连续得分、正确复制核和停止规则。

## 8. Subset Simulation

`subset_simulation()` 使用高分代表失败的统一约定，按经验分位数建立嵌套事件，并用随机游走 Metropolis 从条件分布采样：

$$
p_F=P(F_1)\prod_{j=2}^{m}P(F_j\mid F_{j-1}).
$$

返回概率、层级、各层实际条件概率、接受率、最终条件样本和得分。接受率不能替代有效样本量和多模态覆盖诊断；正式极端概率报告应独立重复完整算法。

## 9. 游戏模型接入

推荐离线/低频管线：

1. BOCPD 监测版本、对手或网络状态变点；
2. HSMM 解释对线、转线、团战、撤退等阶段及持续时间；
3. LMDP 在原生合法转移支持集上生成平滑策略先验；
4. QRE/Nash/Stackelberg 灵敏度用于平衡参数局部分析；
5. 伪弧长延拓扫描版本参数并保存多分支与临界点；
6. AMS 估计路径型团灭、基地失守等稀有事件；
7. Subset Simulation 估计高维阵容、延迟和玩家类型共同导致的失败概率；
8. 所有建议再次经过原生规则、动作掩码、联合规划与回放验证。

## 10. 回归测试

```powershell
python -m pytest `
  rl/p22_equilibrium_control_continuation_math_test.py `
  rl/p23_regime_rare_event_math_test.py -q
```

定向测试覆盖 LMDP 支持集、平均成本特征残差、QRE 灵敏度、有限鲁棒博弈、折叠穿越、静态/动态分岔、BOCPD 均值突变、HSMM 显式三步段、AMS 谱系与 Subset Simulation 正态尾概率。
