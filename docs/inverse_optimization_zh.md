# 逆优化模型在东周战役分析中的实现

本文对应 `rl/p15_inverse_optimization_math.py`。模块解决的不是“给定目标求最优行动”，而是从已经观察到的行动反推目标、奖励或激励结构。所有输入都必须由关卡、回放或调用方显式提供；实现不会从剧情文字补造收益和转移概率。

## 1. 统一问题

前向模型写为：

$$
x^*(\theta)\in\arg\min_{x\in\mathcal X(\theta)}F(x;\theta).
$$

逆问题观测到 $\hat x$，反求使它最优或近似最优的参数 $\theta$：

$$
\min_{\theta,\xi}\ D(\theta,\theta_0)+\rho\|\xi\|_1,
$$

其中 $\theta_0$ 是可审计的参考参数，$\xi$ 记录行为噪声或模型错配。若约束秩不足、只观测一个动作或奖励存在塑形等价，则逆解通常不唯一。因此各接口返回残差、松弛量和秩，而不是只返回一组看似精确的系数。

## 2. 逆线性规划

对前向问题

$$
\min_x c^\mathsf T x,\qquad Ax\le b,
$$

已知可行观测 $\hat x$。活动约束的 KKT 条件为

$$
c+A^\mathsf T\lambda=0,
\qquad \lambda\ge0,
\qquad \lambda_i(A_i\hat x-b_i)=0.
$$

`inverse_linear_program()` 对一个或多个观测联合求解这些条件，并最小化 $\|c-c_0\|_1$。它适合从已知兵力、粮道或部署可行域中反推策划使用的线性权重。

若目标系数已知而约束右端项未知，`inverse_linear_rhs()` 在已知法向量 $A$ 下反演 $b$。未声明活动面的约束取最接近参考值且包含全部观测的边界；声明活动面后，观测必须位于同一一致边界。约束法向量也未知时问题存在额外缩放、旋转和冗余不唯一性，当前接口不会伪称能够唯一恢复。

当可行域是组合集合、活动约束不可得，或观测带噪声时，`fit_revealed_linear_cost()` 使用有限比较

$$
c^\mathsf T\hat x_i
\le c^\mathsf T x_{ij}+\xi_{ij}
$$

进行软间隔拟合。候选替代必须真实可行；若漏掉关键替代，只能说明观测优于已提供候选，不能证明全局最优。

## 3. 逆 MDP 与 IRL

有限折扣 MDP 输入转移 $P(s'\mid s,a)$、特征 $\phi(s,a)$ 和观测确定性策略 $\pi$，线性奖励为

$$
r_w(s,a)=w^\mathsf T\phi(s,a).
$$

固定策略价值满足

$$
V^\pi_w=(I-\gamma P_\pi)^{-1}r_{w,\pi}.
$$

`inverse_mdp_policy()` 用以下优势条件拟合 $w$：

$$
Q^\pi_w(s,\pi(s))-Q^\pi_w(s,a)\ge m-\xi_{sa}.
$$

接口返回每个状态、每个动作的优势以及松弛量，所以可以定位哪条演示不能被当前特征和转移模型解释。

`discounted_occupancy()` 解

$$
d=\mu+\gamma P_\pi^\mathsf T d
$$

并返回 $d(s,a)=d(s)\pi(a\mid s)$ 与特征期望。轨迹级随机策略学习则继续使用现有 `maximum_entropy_irl()`，其有限时域策略以最大熵分布解释演示，而不是假设每个动作绝对最优。

奖励存在势函数等价：

$$
r'(s,a,s')=r(s,a,s')+\gamma\Phi(s')-\Phi(s).
$$

`potential_based_reward_shaping()` 显式生成该等价奖励，用于检验“不同权重但同一策略”的情况。任何动机解释都必须声明特征、折扣、转移和归一化约定。

`bayesian_inverse_mdp()` 为调用方给出的有限奖励权重集合计算精确后验。每个候选先通过价值迭代得到最优 $Q$，再以 Boltzmann 行动似然解释可能只覆盖部分状态的演示。返回值包括后验、MAP、后验均值、模型证据和行动概率；它不把有限候选集外的奖励纳入结论。

## 4. 逆 Stackelberg 参数推断

领导者先承诺混合策略 $x$，理性跟随者选择

$$
y\in\arg\max_j\sum_i x_iU_F(i,j;\theta).
$$

当跟随者收益由特征线性参数化时，`inverse_stackelberg_follower_utility()` 将每条观测响应转换为最佳响应不等式，并联合拟合共同权重。返回的 regret 衡量观测响应在拟合收益下距离最佳响应有多远。

有限理性模型使用 Logit 响应：

$$
P(y=j\mid x,\theta)=
\frac{\exp(\beta u_j(x;\theta))}
{\sum_k\exp(\beta u_k(x;\theta))}.
$$

`inverse_logit_stackelberg_utility()` 最大化观测选择似然。$\beta$ 与收益尺度相乘出现，因此实现固定 $\beta$，避免声称能从同一数据同时识别二者。

## 5. 激励型逆 Stackelberg

另一类“逆 Stackelberg”不是估计未知参数，而是让领导者承诺反应映射

$$
\alpha:Y\to X.
$$

跟随者在知道整张映射后选择

$$
y^*\in\arg\max_y U_F(\alpha(y),y),
$$

领导者再最大化 $U_L(\alpha(y^*),y^*)$。`solve_incentive_stackelberg()` 对小型有限博弈精确枚举反应映射，并分别支持：

- `strong`：跟随者收益并列时选择对领导者最有利的响应；
- `weak`：跟随者收益并列时选择对领导者最不利的响应。

这可用于离线设计外交回应、守城威慑和任务奖惩。映射是承诺机制，不应与“观察领导者混合策略后推断跟随者偏好”的参数反演混为一谈。

## 6. 在 dongzhou 中的典型用法

- 回放权重审计：从玩家或脚本选择的补给、阵型、外交行动反推线性权重，检查设计参数与实际行为是否一致。
- 战术风格学习：从状态策略反推“保主将、占地形、输出、节省行动点”等奖励特征权重，再以优势和松弛定位模型解释失败处。
- 敌将偏好估计：从我方不同承诺下的敌方响应估计跟随者收益；样本少时保留参考参数并报告秩不足。
- 威慑与奖惩设计：对小行动集构造可审计反应映射，明确区分强、弱破同分假设。

这些结果默认只用于低频离线分析、参数校准和回放解释。若要进入在线行动评分，调用方必须限制权重幅度，并继续通过原生合法动作、联合规划和路径冲突检查。

## 7. 验证

```powershell
python -m pytest rl/p15_inverse_optimization_math_test.py -q
```

回归覆盖 KKT 证书、多观测、带噪声比较、占用测度、逆 MDP 优势、势函数塑形、理性与 Logit 跟随者反演、反应映射、破同分规则和规模预算。
