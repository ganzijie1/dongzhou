# Robbins–Monro、ODE Method、Two-Timescale Actor–Critic、Borkar–Meyn 稳定性与 Polyak–Ruppert Averaging

## 摘要

随机逼近研究如何只依赖带噪、逐步到达的数据求解未知期望方程。Robbins–Monro 提供基本递推；ODE method 把小步长随机迭代解释为常微分方程轨迹；Two-timescale actor–critic 让快速 critic 跟踪当前策略价值、慢速 actor 更新策略；Borkar–Meyn 条件通过分析无穷远处的缩放动力学证明迭代不会发散；Polyak–Ruppert averaging 则通过尾部平均降低渐近方差并减弱步长常数的敏感性。

这五部分共同回答在线强化学习中的核心问题：更新目标是什么、噪声能否平均掉、快慢变量是否真正分离、参数会不会逃向无穷远，以及最终估计的统计波动有多大。

本文给出统一递推、主要假设、收敛结论、失败模式、数值诊断，以及它们在 5v5 游戏在线策略学习中的应用边界。

## 一、随机根问题

设随机观测为 $Z$，希望求解未知期望方程：

$$g(\theta)=\mathbb E[G(\theta,Z)]=0$$

由于无法直接计算期望，只能在第 $n$ 步得到带噪样本：

$$Y_{n+1}=G(\theta_n,Z_{n+1})$$

基本随机逼近递推为：

$$\theta_{n+1}=\theta_n-a_nY_{n+1}$$

其中 $a_n>0$ 是步长。

若使用漂移方向 $h=-g$，同一个递推也常写成：

$$\theta_{n+1}=\theta_n+a_n\left[h(\theta_n)+M_{n+1}+\varepsilon_{n+1}\right]$$

这里 $M_{n+1}$ 是零均值噪声，$\varepsilon_{n+1}$ 是偏差或近似误差。

## 二、经典 Robbins–Monro 问题

原始 Robbins–Monro 问题考虑标量响应 $Y(\theta)$，其均值为：

$$m(\theta)=\mathbb E[Y(\theta)]$$

目标是求：

$$m(\theta^*)=\alpha$$

迭代为：

$$\theta_{n+1}=\theta_n-a_n\left(Y_{n+1}-\alpha\right)$$

如果 $m$ 在根附近递增，则观测高于目标时向较小参数移动，观测低于目标时向较大参数移动。

在向量情形中，符号约定必须与稳定漂移一致。若使用更新 $\theta_{n+1}=\theta_n-a_ng(\theta_n)$，局部稳定通常要求根附近 Jacobian 的实部为正；若写成加号漂移 $h=-g$，则要求 $\dot\theta=h(\theta)$ 在根处稳定。

## 三、步长条件

最常见的 Robbins–Monro 步长条件为：

$$\sum_{n=0}^{\infty}a_n=\infty$$

以及：

$$\sum_{n=0}^{\infty}a_n^2<\infty$$

第一条保证算法有无限累计移动能力，不会过早冻结；第二条使平方可积噪声的累计方差保持可控。

常见选择为：

$$a_n=\frac{a}{(n+n_0)^{\alpha}},\qquad \frac{1}{2}<\alpha\leq 1$$

若使用常数步长：

$$a_n\equiv a>0$$

算法通常不会精确收敛到一个点，而是在稳定点附近形成稳态波动。常数步长适合持续跟踪非平稳目标，但不能套用衰减步长下的几乎必然点收敛结论。

## 四、噪声分解

令 $\mathcal F_n$ 表示第 $n$ 步之前的信息。典型鞅差条件为：

$$\mathbb E[M_{n+1}\mid\mathcal F_n]=0$$

常用二阶矩条件为：

$$\mathbb E[\lVert M_{n+1}\rVert^2\mid\mathcal F_n]\leq C\left(1+\lVert\theta_n\rVert^2\right)$$

偏差项常要求满足可求和条件：

$$\sum_na_n\lVert\varepsilon_{n+1}\rVert<\infty$$

或者至少满足在稳定轨迹上的渐近消失条件。

强化学习样本通常来自 Markov 链而非独立同分布序列。此时噪声不一定逐步是简单鞅差，需要通过遍历性、Poisson 方程、混合速度或受控 Markov 噪声理论处理。

## 五、投影随机逼近

如果参数必须位于闭凸集 $K$，可以使用：

$$\theta_{n+1}=\Pi_K\left(\theta_n+a_n\left[h(\theta_n)+M_{n+1}\right]\right)$$

投影能强制有界，但极限动力学不再是简单的 $\dot\theta=h(\theta)$，而是投影 ODE 或法锥微分包含：

$$\dot\theta\in h(\theta)-N_K(\theta)$$

不能在投影频繁激活时仍用无约束 ODE 的稳定点解释结果。

## 六、ODE Method

考虑递推：

$$\theta_{n+1}=\theta_n+a_n\left[h(\theta_n)+M_{n+1}+\varepsilon_{n+1}\right]$$

定义算法时间：

$$t_n=\sum_{k=0}^{n-1}a_k$$

在区间 $[t_n,t_{n+1}]$ 上对离散点做分段线性插值，得到连续轨迹 $\bar\theta(t)$。

对应的平均 ODE 为：

$$\dot\theta(t)=h(\theta(t))$$

如果步长趋于零、噪声在算法时间尺度上消失、偏差可控且迭代有界，则插值轨迹会渐近跟随该 ODE。

## 七、Asymptotic Pseudo-Trajectory

ODE method 的严格表达通常不是“随机迭代逐点等于 ODE 解”，而是插值轨迹构成 asymptotic pseudo-trajectory。

设 $\phi_s(x)$ 是 ODE 从 $x$ 出发运行时间 $s$ 的流。对任意固定窗口 $T>0$，典型性质为：

$$\lim_{t\rightarrow\infty}\sup_{0\leq s\leq T}\lVert\bar\theta(t+s)-\phi_s(\bar\theta(t))\rVert=0$$

这表示在任意固定未来窗口内，足够晚的随机轨迹都接近 ODE 轨迹。

如果 ODE 有唯一全局渐近稳定平衡点 $\theta^*$，并且随机迭代有界，则通常可以推出：

$$\theta_n\rightarrow\theta^*\quad\text{a.s.}$$

若 ODE 有多个平衡点、极限环或更复杂不变集，随机逼近一般只能保证极限集落在相应的 internally chain transitive set 中，不能声称收敛到唯一点。

## 八、Lyapunov 分析

若存在连续可微函数 $V$，满足：

$$V(\theta)\geq 0$$

并且沿 ODE 轨迹：

$$\frac{\mathrm d}{\mathrm dt}V(\theta(t))=\langle\nabla V(\theta),h(\theta)\rangle\leq 0$$

则 $V$ 是 Lyapunov 函数。

若在 $\theta\neq\theta^*$ 时严格有：

$$\langle\nabla V(\theta),h(\theta)\rangle<0$$

可以用 LaSalle 不变性原理或直接稳定性论证识别极限集合。

在优化中常取目标差或距离平方；在 actor–critic 中，actor 的平均 ODE 未必是精确梯度流，因此必须验证实际漂移对应的 Lyapunov 结构。

## 九、非光滑 ODE 与微分包含

如果平均漂移不连续、使用 max 运算、投影、次梯度或集合值策略，则极限对象可能是微分包含：

$$\dot\theta(t)\in H(\theta(t))$$

例如非光滑目标的随机次梯度法可能对应：

$$\dot\theta(t)\in-\partial f(\theta(t))$$

普通光滑 ODE 结论不能直接用于这些情况，需要使用 differential inclusion 和集合值动力系统工具。

## 十、Two-Timescale Stochastic Approximation

考虑两个变量：慢变量 $\theta_n$ 和快变量 $w_n$。递推为：

$$w_{n+1}=w_n+b_n\left[G(\theta_n,w_n)+M_{n+1}^{w}+\varepsilon_{n+1}^{w}\right]$$

$$\theta_{n+1}=\theta_n+a_n\left[H(\theta_n,w_n)+M_{n+1}^{\theta}+\varepsilon_{n+1}^{\theta}\right]$$

两组步长分别满足随机逼近条件，并要求：

$$\frac{a_n}{b_n}\rightarrow 0$$

这意味着在快变量看来，$\theta_n$ 几乎冻结；在慢变量看来，$w_n$ 已经接近当前 $\theta_n$ 对应的平衡。

## 十一、快慢 ODE 分解

### 1. 快时间尺度

固定 $\theta$ 后，分析：

$$\dot w=G(\theta,w)$$

假设它有渐近稳定平衡：

$$w=\lambda(\theta)$$

并且 $w_n$ 能跟踪这个平衡映射。

### 2. 慢时间尺度

把快变量替换为准稳态 $\lambda(\theta)$，得到约化 ODE：

$$\dot\theta=H(\theta,\lambda(\theta))$$

如果快 ODE 对每个冻结的 $\theta$ 稳定，平衡映射足够规则，慢 ODE 也稳定，并且联合迭代有界，则可以建立双时间尺度收敛。

### 3. 不能只看步长比

$a_n/b_n\rightarrow 0$ 只是时间尺度分离的一部分。还需要：

- 快子系统在冻结慢变量下稳定；
- 平衡映射 $\lambda(\theta)$ 存在并具有适当连续性；
- 噪声和偏差满足条件；
- 联合迭代有界；
- 数据生成 Markov 链在策略变化下保持足够遍历。

## 十二、Two-Timescale Actor–Critic

在 actor–critic 中，critic 参数 $w_n$ 通常使用快步长 $b_n$，actor 参数 $\theta_n$ 使用慢步长 $a_n$。

策略写成：

$$\pi_{\theta}(a\mid s)$$

价值近似写成：

$$V_w(s)$$

一步 TD error 为：

$$\delta_n=R_{n+1}+\gamma V_{w_n}(S_{n+1})-V_{w_n}(S_n)$$

线性 critic 的典型更新为：

$$w_{n+1}=w_n+b_n\delta_n\phi(S_n)$$

actor 的典型策略梯度更新为：

$$\theta_{n+1}=\theta_n+a_n\delta_n\nabla_{\theta}\log\pi_{\theta_n}(A_n\mid S_n)$$

若使用成本最小化、优势函数、自然梯度、熵正则化或约束乘子，符号和更新结构会相应变化。

## 十三、Actor–Critic 的 ODE 解释

对冻结策略参数 $\theta$，critic 试图收敛到：

$$w=\lambda(\theta)$$

这个点可能是真实价值函数参数，也可能只是投影 Bellman 方程的解。

慢 actor 的极限 ODE 为：

$$\dot\theta=\bar H(\theta,\lambda(\theta))$$

只有当 critic 结构、采样分布和 actor 更新满足相应策略梯度条件时，才可以进一步写成：

$$\dot\theta=\nabla J(\theta)$$

函数逼近偏差、off-policy 采样、截断重要性权重和不兼容特征都可能使 $\bar H$ 偏离真实策略梯度。

## 十四、Markov 噪声

actor–critic 数据由当前策略控制的 Markov 链产生。平均漂移常写为：

$$h(\theta)=\int H(\theta,z)\,\nu_{\theta}(\mathrm dz)$$

其中 $\nu_{\theta}$ 是策略 $\pi_{\theta}$ 下的平稳分布。

要使用该平均漂移，通常需要对每个相关 $\theta$ 保证遍历性，并控制 $\nu_{\theta}$ 随 $\theta$ 的变化。若策略接近确定性后使部分状态永远不可达，统一混合条件可能失效。

Poisson 方程可用于把相关 Markov 噪声分解为鞅差、望远镜项和小偏差。实现中不能把连续帧简单当成独立样本来估计方差。

## 十五、Off-Policy 与函数逼近风险

线性 on-policy TD 在适当条件下具有稳定理论，但 off-policy、bootstrapping 与函数逼近组合可能发散。

重要性权重为：

$$\rho_n=\frac{\pi_{\theta_n}(A_n\mid S_n)}{\mu(A_n\mid S_n)}$$

若行为策略概率 $\mu(A_n\mid S_n)$ 很小，权重会产生高方差。裁剪权重降低方差但引入偏差。

双时间尺度本身不能修复错误的 critic 固定点。应根据 on-policy、off-policy、线性或非线性函数逼近选择相应稳定算法。

## 十六、Borkar–Meyn 稳定性问题

ODE method 通常先假设：

$$\sup_n\lVert\theta_n\rVert<\infty\quad\text{a.s.}$$

但这正是许多随机逼近算法最难证明的部分。Borkar–Meyn 思路通过分析漂移在无穷远处的缩放极限，给出迭代有界性的充分条件。

考虑：

$$\theta_{n+1}=\theta_n+a_n\left[h(\theta_n)+M_{n+1}\right]$$

定义缩放漂移：

$$h_c(x)=\frac{h(cx)}{c}$$

若当 $c\rightarrow\infty$ 时，$h_c$ 在紧集上一致收敛到：

$$h_{\infty}(x)=\lim_{c\rightarrow\infty}\frac{h(cx)}{c}$$

则分析无穷远 ODE：

$$\dot x=h_{\infty}(x)$$

## 十七、Borkar–Meyn 核心条件

一个常用版本要求无穷远 ODE 的原点是全局渐近稳定平衡：

$$x(t)\rightarrow 0,\qquad \forall x(0)$$

直观上，如果参数尺度很大，归一化漂移仍把轨迹拉回原点，那么随机迭代不容易持续逃向无穷远。

结合 Lipschitz 漂移、Robbins–Monro 步长、鞅差噪声和二阶矩控制等条件，可以推出迭代几乎必然有界。随后才能使用原始 ODE：

$$\dot\theta=h(\theta)$$

分析最终极限集合。

Borkar–Meyn 条件主要解决稳定性，不自动证明原始 ODE 只有一个目标平衡点。完整点收敛通常还要证明原始 ODE 的相应吸引性质。

## 十八、无穷远缩放的线性例子

设：

$$h(x)=Ax+b+o(\lVert x\rVert)$$

则：

$$h_{\infty}(x)=Ax$$

无穷远 ODE 为：

$$\dot x=Ax$$

若矩阵 $A$ 的所有特征值实部都严格为负，则原点全局指数稳定，这为有界性提供一个清晰诊断。

若 $A$ 有正实部特征值，参数在大尺度上可能被向外推；若存在纯虚特征值，则还需要更细致分析，不能仅凭数值模拟声称稳定。

## 十九、径向漂移诊断

选择 Lyapunov 函数：

$$V(x)=\frac{1}{2}\lVert x\rVert^2$$

沿无穷远 ODE：

$$\dot V(x)=\langle x,h_{\infty}(x)\rangle$$

若存在 $c>0$，使得在所有非零方向上：

$$\langle x,h_{\infty}(x)\rangle\leq-c\lVert x\rVert^2$$

则无穷远动力学具有明确的向内漂移。

在神经网络中，$h_{\infty}$ 可能不存在或高度依赖方向。对若干随机射线做经验测试只能发现反例，不能证明全局 Borkar–Meyn 条件。

## 二十、双时间尺度的稳定性

双时间尺度系统需要同时控制快变量和慢变量。仅分别裁剪参数并不能证明无投影算法稳定。

常见分析顺序为：

1. 固定慢变量，证明快 ODE 的平衡 $\lambda(\theta)$ 稳定；
2. 控制 $\lambda(\theta)$ 的增长与连续性；
3. 把快变量替换为 $\lambda(\theta)$，分析慢 ODE；
4. 对联合缩放系统或分层缩放系统建立无穷远稳定性；
5. 最后证明联合迭代有界。

Actor 和 critic 使用不同网络、归一化层和优化器时，理论上的快慢比例未必等于配置文件里的 learning rate 比值。自适应优化器会改变有效步长。

## 二十一、Polyak–Ruppert Averaging

给定随机逼近迭代 $\theta_1,\ldots,\theta_n$，Polyak–Ruppert 平均定义为：

$$\bar\theta_n=\frac{1}{n}\sum_{k=1}^{n}\theta_k$$

实际中常在 burn-in 后做尾部平均：

$$\bar\theta_{m:n}=\frac{1}{n-m+1}\sum_{k=m}^{n}\theta_k$$

它不是对多个独立模型做集成，而是对同一随机逼近轨迹的后期迭代进行平均。

## 二十二、渐近正态性

考虑根附近线性化：

$$g(\theta)\approx A(\theta-\theta^*)$$

设根处噪声的长期协方差为 $S$。在经典正则条件下，Polyak–Ruppert 平均满足：

$$\sqrt n(\bar\theta_n-\theta^*)\Rightarrow\mathcal N\left(0,A^{-1}SA^{-\mathsf T}\right)$$

这里的 $S$ 对独立噪声是单步协方差；对 Markov 噪声则应使用包含自相关的长期协方差，而不是简单样本方差。

在适当设置下，平均估计可以达到经典随机逼近的有效渐近协方差，并降低对步长常数的敏感性。

## 二十三、为什么平均有效

后期迭代通常围绕稳定点随机波动：

$$\theta_n=\theta^*+\text{系统偏差}+\text{随机波动}$$

若随机波动具有足够混合性，平均可以抵消一部分零均值噪声。使用：

$$a_n=\frac{a}{n^{\alpha}},\qquad \frac{1}{2}<\alpha<1$$

时，原始迭代可能不是最优尺度，但适当平均后仍可获得 $\sqrt n$ 级渐近行为。

平均不会消除模型偏差、critic 投影误差、off-policy 偏差或错误奖励函数。

## 二十四、加权与尾部平均

一般加权平均为：

$$\bar\theta_n^{w}=\frac{\sum_{k=1}^{n}w_k\theta_k}{\sum_{k=1}^{n}w_k}$$

后期权重更大可以减少早期偏差，但会降低有效样本量。burn-in 过短会混入瞬态偏差，过长则浪费数据。

对于策略网络，参数平均不一定等于策略分布平均：

$$\pi_{\bar\theta}(a\mid s)\neq\frac{1}{n}\sum_{k=1}^{n}\pi_{\theta_k}(a\mid s)$$

神经网络存在参数置换对称性时，跨越不同吸引域直接平均参数甚至可能破坏策略。

## 二十五、Actor–Critic 中的平均

### 1. Critic averaging

对线性或局部稳定 critic，尾部平均通常能降低价值参数方差。应同时报告原始参数与平均参数的 Bellman residual。

### 2. Actor averaging

若 actor 在同一个局部吸引域内缓慢波动，参数尾部平均可能有益；若策略经历模式切换，则应考虑 occupancy 或动作概率空间平均，而不是盲目平均网络权重。

### 3. 分别设置 burn-in

快 critic 和慢 actor 的稳定时间不同，平均窗口不应机械地使用同一个起点。

### 4. 在线部署

部署平均参数前，应在独立回放和仿真种子上重新评估。训练轨迹上的低方差不等于样本外性能更高。

## 二十六、5v5 游戏中的应用

### 1. 在线对手参数估计

用 Robbins–Monro 更新对手进攻倾向、换线概率或技能命中率。目标分布发生变点时，应由 BOCPD 或其他检测器触发重置、增大步长或切换模型。

### 2. 快速价值评估与慢速策略更新

critic 在大量帧级数据上快速更新，actor 只在较慢时间尺度改变开团、撤退和资源交换策略，减少策略变化对数据分布的破坏。

### 3. 团队共享 critic

多个英雄可以共享公共状态价值，同时保留角色特定 actor。必须明确共享信息是否在执行时可获得，避免中心化 critic 的隐藏特征泄漏到 actor。

### 4. 安全乘子

若有风险约束：

$$J_c(\theta)\leq d$$

可以引入乘子 $\lambda\geq 0$，形成额外时间尺度：

$$\lambda_{n+1}=\left[\lambda_n+c_n(J_c(\theta_n)-d)\right]_+$$

三时间尺度的快慢顺序必须按具体算法证明，不能默认 critic、actor、乘子采用任意三个学习率就会收敛。

### 5. 持续版本漂移

衰减步长适合近似平稳环境，常数或周期重启步长适合跟踪版本变化。二者解决的统计目标不同，应分别报告稳态误差与跟踪延迟。

## 二十七、与现有游戏数学层的组合

推荐接入流程：

1. P23 的 BOCPD 与 HSMM 判断数据是否仍来自同一阶段或版本；
2. P24 的 belief planner 提供隐藏状态和对手类型后验；
3. critic 在快时间尺度估计价值、优势或 occupancy value；
4. actor 在慢时间尺度更新高层混合策略；
5. Borkar–Meyn 型缩放分析或显式投影控制参数稳定性；
6. Polyak–Ruppert averaging 对进入稳定区间后的轨迹降方差；
7. P27 处理资源与风险约束，P30 给性能估计附加置信序列；
8. 输出仍需通过动作掩码、技能冷却、资源、碰撞、联合规划和 MAPF 检查。

## 二十八、工程诊断

### 1. 步长诊断

记录：

$$\sum_{k=0}^{n}a_k$$

以及：

$$\sum_{k=0}^{n}a_k^2$$

双时间尺度还应记录有效比率：

$$\rho_n=\frac{a_n}{b_n}$$

### 2. 稳定性诊断

记录参数范数、梯度范数、更新范数、投影激活频率和无穷远径向漂移：

$$d_c(v)=\left\langle v,\frac{h(cv)}{c}\right\rangle$$

### 3. Critic 诊断

记录 TD error 均值、方差、自相关、Bellman residual、特征协方差条件数与状态覆盖。

### 4. Actor 诊断

记录策略熵、KL 变化、梯度范数、最佳响应 gap、最后迭代与平均策略的独立评估。

### 5. Averaging 诊断

记录 burn-in、平均窗口、原始与平均参数性能、长期协方差估计和跨种子误差条。

### 6. ODE 诊断

用冻结参数的大批量模拟估计平均漂移 $h(\theta)$，检查候选平衡附近 Jacobian 特征值，而不是只看单条随机轨迹是否平滑。

## 二十九、常见误区

### 1. 只验证步长条件就声称收敛

还需要稳定性、噪声、连续性、遍历性和 ODE 吸引结构。

### 2. 把有界性当成自然成立

神经网络 actor–critic 可以参数爆炸。投影、正则化和 Borkar–Meyn 条件解决的是不同层面的稳定问题。

### 3. 把学习率大小直接等同于时间尺度

Adam、RMSProp、梯度裁剪、更新频率和批量大小都会改变有效时间尺度。

### 4. 把 critic 收敛当成真实价值无偏

critic 可能只收敛到投影 Bellman 方程或带有 off-policy 偏差的固定点。

### 5. 把连续帧当作 IID 样本

Markov 自相关会影响噪声协方差、置信区间和 Polyak–Ruppert 渐近方差。

### 6. 在环境变点后继续使用旧的衰减步长

步长已经很小时，算法可能无法跟踪新版本。需要变化检测、重启或常数步长机制。

### 7. 跨多个吸引域平均参数

平均可能落在任何一个有效策略都不对应的区域。应先诊断轨迹是否处于同一局部稳定分支。

### 8. 让在线学习绕过游戏规则

actor 输出仍是候选策略。非法动作、安全约束和路径冲突必须由执行层拒绝。

## 三十、选择建议

若目标是从逐步噪声观测求解固定期望方程，使用 Robbins–Monro 框架，并首先确认符号、步长和噪声分解。

若需要解释长期行为，用 ODE method 分析平均漂移的稳定点、极限环和吸引域；非光滑或投影问题改用微分包含。

若一个模块必须跟踪另一个模块的准稳态，使用 two-timescale stochastic approximation，并验证快子系统稳定与步长比趋零。

若有界性无法直接证明，检查 Borkar–Meyn 无穷远缩放条件，或明确使用投影与正则化形成不同的稳定机制。

若后期迭代围绕同一稳定点高方差波动，使用 Polyak–Ruppert 尾部平均；若环境持续漂移或轨迹跨越多个吸引域，则不应机械平均。

## 三十一、结论

Robbins–Monro 给出随机逼近的基本递推，ODE method 把它的长期行为连接到确定性动力系统，Two-timescale actor–critic 利用快慢分离把价值跟踪和策略改进组合起来，Borkar–Meyn 条件补上经常被忽略的有界性证明，Polyak–Ruppert averaging 则改善稳定区域内的统计效率。

这些方法的理论链条具有明确顺序：先定义正确的平均漂移，再控制噪声与偏差；先证明迭代稳定，再讨论 ODE 极限；先证明 critic 对冻结 actor 的跟踪，再讨论 actor 的约化动力学；最后才使用平均降低方差。

在游戏在线学习中，任何一个环节缺失都可能产生“训练曲线看似平稳、实际策略却不可信”的结果。可靠实现必须同时保存步长、时间尺度比、稳定性诊断、Markov 自相关、平均窗口、跨种子评估和原生规则验收结果。
