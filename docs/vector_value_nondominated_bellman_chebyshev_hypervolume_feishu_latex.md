# 向量价值函数、非支配 Bellman 算子、Chebyshev 标量化与超体积指标

## 摘要

多目标决策同时考虑多个相互冲突的指标，例如胜率、经济、存活、资源控制、阵型完整、动作风险与计算延迟。单一标量奖励必须预先固定这些目标的交换比例，而真实系统中的偏好可能随状态、玩家风格、比赛阶段或安全约束变化。多目标 Markov 决策过程保留向量奖励，以 Pareto 偏序比较策略，并用一个非支配价值集合代替单个最优价值。

非支配 Bellman 算子把动态规划推广到集合值递推：对每个动作组合后继状态的价值集合，再删除被其他向量支配的候选。加权和标量化只保证找到受支撑的凸前沿点；Chebyshev 标量化通过最小化相对理想点的最大加权缺口，可以发现非凸 Pareto 前沿。超体积指标计算非支配集合相对参考点支配的体积，同时反映收敛性与多样性。

本文系统介绍向量价值、Pareto 偏序、可达回报集、Pareto Coverage Set、Convex Coverage Set、集合值 Bellman 递推、Minkowski 和、剪枝、随机策略、Chebyshev 与增强 Chebyshev 标量化、时间一致性、超体积计算与贡献、偏好条件策略、档案维护、误差指标及 5v5 MOBA 应用。

## 一、多目标决策问题

设目标维数为 $m$，即时奖励为向量：

$$r(s,a,s')\in\mathbb R^m$$

例如：

$$r=(r_{\mathrm{win}},r_{\mathrm{gold}},r_{\mathrm{survival}},r_{\mathrm{objective}},r_{\mathrm{coordination}})$$

每个分量应统一为“越大越好”。若原指标是代价 $c_i$，可转换为：

$$r_i=-c_i$$

混用最大化收益与最小化代价会使支配关系产生歧义。

## 二、向量累计回报

折扣向量回报为：

$$G_t=\sum_{k=0}^{\infty}\gamma^kr_{t+k}$$

其中：

$$0\le\gamma\lt1$$

策略 $\pi$ 的向量价值函数为：

$$V^{\pi}(s)=\mathbb E_{\pi}\left[G_t\mid s_t=s\right]\in\mathbb R^m$$

动作价值函数为：

$$Q^{\pi}(s,a)=\mathbb E_{\pi}\left[G_t\mid s_t=s,a_t=a\right]$$

## 三、分量 Bellman 期望方程

固定策略下：

$$V^{\pi}(s)=\sum_a\pi(a\mid s)\sum_{s'}P(s'\mid s,a)\left[r(s,a,s')+\gamma V^{\pi}(s')\right]$$

向量等式按分量成立：

$$V_i^{\pi}(s)=\sum_a\pi(a\mid s)\sum_{s'}P(s'\mid s,a)\left[r_i(s,a,s')+\gamma V_i^{\pi}(s')\right]$$

困难不在策略评价，而在不同目标之间不存在天然的全序“最大值”。

## 四、Pareto 弱支配

对两个向量 $u,v\in\mathbb R^m$，若：

$$u_i\ge v_i,\qquad i=1,\ldots,m$$

则称 $u$ 弱支配 $v$，记为：

$$u\succeq v$$

若同时：

$$u\neq v$$

则称 $u$ Pareto 支配 $v$，记为：

$$u\succ v$$

## 五、强支配与严格支配

若每个分量都严格更好：

$$u_i\gt v_i,\qquad i=1,\ldots,m$$

可称 $u$ 严格或强支配 $v$。

文献对“weak、strict、strong”的命名并不完全统一，因此实现中应直接写出分量条件，而不是只保存名称。

## 六、不可比关系

若存在目标 $i,j$ 满足：

$$u_i\gt v_i$$

$$u_j\lt v_j$$

则 $u$ 与 $v$ 不可比。一个策略更安全，另一个策略更高收益，Pareto 偏序不会替用户替换这种价值判断。

多目标方法的输出通常是一组不可比方案，而不是唯一策略。

## 七、非支配算子

对有限或紧致集合 $X\subseteq\mathbb R^m$，非支配子集定义为：

$$\mathrm{ND}(X)=\{x\in X\mid\nexists y\in X,\ y\succ x\}$$

被支配向量可以安全删除，因为它对所有单调偏好都不优于其支配者。

但如果估计存在噪声，过早删除可能永久丢失真实非支配解。

## 八、Pareto 前沿

可达价值集合为 $\mathcal V$，Pareto 前沿为：

$$\mathcal P=\mathrm{ND}(\mathcal V)$$

若关心对应策略，则策略前沿为：

$$\Pi_{\mathcal P}=\{\pi\mid V^{\pi}\in\mathcal P\}$$

多个不同策略可能产生同一价值向量。系统若需要解释或执行，必须保存价值向量到策略的映射。

## 九、状态相关价值集合

从状态 $s$ 可实现的价值集合为：

$$\mathcal V(s)=\{V^{\pi}(s)\mid\pi\in\Pi\}$$

非支配价值集合为：

$$\mathcal P(s)=\mathrm{ND}(\mathcal V(s))$$

所以多目标最优价值不是单个向量，而是集合值函数：

$$s\mapsto\mathcal P(s)$$

## 十、策略类别

策略可以是：

- 确定性或随机性。
- 平稳或非平稳。
- Markov 或历史依赖。

允许随机策略通常会凸化期望回报集合。允许哪类策略会改变 Pareto 前沿，因此必须在算法和报告中明确。

## 十一、折扣占用测度

固定初始分布 $\mu_0$，折扣占用测度为：

$$d^{\pi}(s,a)=(1-\gamma)\mathbb E_{\pi}\left[\sum_{t=0}^{\infty}\gamma^t\mathbf 1_{\{s_t=s,a_t=a\}}\right]$$

它满足流量约束：

$$\sum_ad(s,a)=(1-\gamma)\mu_0(s)+\gamma\sum_{s',a'}d(s',a')P(s\mid s',a')$$

期望向量回报为：

$$J(\pi)=\frac{1}{1-\gamma}\sum_{s,a}d^{\pi}(s,a)\bar r(s,a)$$

## 十二、随机策略与凸化

占用测度可行域是凸多面体。对两个可行占用测度：

$$d_{\alpha}=\alpha d_1+(1-\alpha)d_2$$

其中：

$$\alpha\in[0,1]$$

对应回报为：

$$J_{\alpha}=\alpha J_1+(1-\alpha)J_2$$

因此允许适当随机策略时，期望回报集合具有凸结构。每回合随机选择整套策略与每状态随机动作并非总有相同的风险和轨迹语义。

## 十三、Pareto Coverage Set

Pareto Coverage Set，简称 PCS，是一组策略，使每个 Pareto 最优价值都由其中至少一个策略实现：

$$\forall v\in\mathcal P,\quad\exists\pi\in\mathrm{PCS}:V^{\pi}=v$$

连续问题的 PCS 可能无限，实际算法只能近似覆盖。

## 十四、Convex Coverage Set

对线性权重：

$$w\in\Delta^{m-1}$$

其中：

$$\Delta^{m-1}=\{w\in\mathbb R_+^m\mid\sum_iw_i=1\}$$

Convex Coverage Set，简称 CCS，要求对任意 $w$，集合中至少有一个策略最大化：

$$w^\top V^{\pi}$$

CCS 只需覆盖受支撑的凸前沿点，通常小于完整 PCS。

## 十五、线性标量化

加权和效用为：

$$g_w(v)=w^\top v$$

固定权重后，标量奖励为：

$$r_w=w^\top r$$

可以使用普通 Bellman 最优算子：

$$V_w^*(s)=\max_a\sum_{s'}P(s'\mid s,a)\left[w^\top r(s,a,s')+\gamma V_w^*(s')\right]$$

## 十六、加权和的局限

线性标量化只能找到存在支撑超平面的 Pareto 点。

若前沿非凸，某些非支配向量 $v$ 对所有 $w\ge0$ 都不是：

$$\mathop{\arg\max}_{u\in\mathcal V}w^\top u$$

这些点虽然 Pareto 最优，却会被所有加权和训练漏掉。

## 十七、有限时域集合值动态规划

设剩余时域为 $h$，终端集合为：

$$\mathcal V_0(s)=\{0\}$$

对动作 $a$，后继价值集合为：

$$\mathcal Q_{h+1}(s,a)=\bigoplus_{s'}P(s'\mid s,a)\left(r(s,a,s')+\gamma\mathcal V_h(s')\right)$$

状态价值集合为：

$$\mathcal V_{h+1}(s)=\mathrm{ND}\left(\bigcup_a\mathcal Q_{h+1}(s,a)\right)$$

## 十八、加权 Minkowski 和

集合缩放定义为：

$$\alpha X=\{\alpha x\mid x\in X\}$$

Minkowski 和为：

$$X\oplus Y=\{x+y\mid x\in X,\ y\in Y\}$$

因此：

$$\bigoplus_{s'}P(s'\mid s,a)X_{s'}$$

表示对每个可能后继状态选择一个后续策略向量，再按转移概率求期望。

## 十九、非支配 Bellman 算子

对集合值函数 $\mathcal V$，定义：

$$\mathcal B_{\mathrm{ND}}\mathcal V(s)=\mathrm{ND}\left(\bigcup_a\bigoplus_{s'}P(s'\mid s,a)\left(r(s,a,s')+\gamma\mathcal V(s')\right)\right)$$

固定点形式为：

$$\mathcal V^*=\mathcal B_{\mathrm{ND}}\mathcal V^*$$

它是集合值 Bellman 方程，而不是对向量逐分量取最大值。

## 二十、为什么不能逐分量最大

错误做法是：

$$V_i^*(s)=\max_{\pi}V_i^{\pi}(s)$$

然后组合：

$$v_{\mathrm{ideal}}=(V_1^*,\ldots,V_m^*)$$

不同分量最大值可能来自不同策略，因此 $v_{\mathrm{ideal}}$ 通常不可实现。它是理想点，不是实际价值向量。

## 二十一、理想点与 Nadir 点

理想点定义为：

$$z_i^*=\sup_{v\in\mathcal V}v_i$$

Pareto 前沿上的 Nadir 点形式上为：

$$z_i^{\mathrm{nad}}=\inf_{v\in\mathcal P}v_i$$

理想点通常不可达，Nadir 点又难以精确估计。两者常用于归一化与标量化。

## 二十二、集合爆炸

若每个后继状态有 $K$ 个候选，分支数为 $b$，朴素 Minkowski 组合数可达到：

$$K^b$$

每次 Bellman 备份还要跨动作取并集并执行非支配筛选。

目标维数、时域和状态分支都会导致集合快速膨胀。

## 二十三、增量剪枝

不必先构造完整 Cartesian 组合。可以逐个后继集合合并：

$$X_1=P_1\mathcal V(s_1)$$

$$X_{k+1}=\mathrm{ND}(X_k\oplus P_{k+1}\mathcal V(s_{k+1}))$$

中间每一步删除被支配向量，能够显著减少候选数。

但浮点误差会使几乎相同的向量互不支配，需要容差与去重。

## 二十四、epsilon 支配

对最大化目标，可定义乘法或加法 epsilon 支配。加法形式为：

$$u_i+\epsilon_i\ge v_i,\qquad i=1,\ldots,m$$

使用 epsilon 网格可压缩档案：

$$b_i(v)=\left\lfloor\frac{v_i}{\epsilon_i}\right\rfloor$$

同一网格箱只保留代表向量，以精度换取计算与存储。

## 二十五、误差传播

若每次 Bellman 备份引入集合近似误差 $\epsilon$，折扣系统中的累计误差通常具有：

$$O\left(\frac{\epsilon}{1-\gamma}\right)$$

的放大结构。

精确常数依赖集合距离、剪枝方式和算子性质。$\gamma$ 接近一时，局部剪枝误差会长期积累。

## 二十六、集合距离

有向集合距离为：

$$d_{\rightarrow}(A,B)=\sup_{a\in A}\inf_{b\in B}\lVert a-b\rVert$$

Hausdorff 距离为：

$$d_H(A,B)=\max\{d_{\rightarrow}(A,B),d_{\rightarrow}(B,A)\}$$

它可衡量两次价值集合迭代差异，但对离群点敏感，也不直接反映偏好加权后的性能。

## 二十七、随机动作混合

若状态 $s$ 下以概率 $\alpha_a$ 选择动作：

$$\alpha_a\ge0,\qquad\sum_a\alpha_a=1$$

动作集合的期望回报可形成凸组合。

若算法只对动作集合取并集，它对应当前状态确定性动作；若允许随机动作，应进一步取适当凸包：

$$\mathrm{co}\left(\bigcup_a\mathcal Q(s,a)\right)$$

是否取凸包取决于策略类与执行语义。

## 二十八、非支配 Bellman 的策略恢复

每个价值向量都应保存 backpointer：

$$b(v)=(a,\{v_{s'}\}_{s'})$$

它记录当前动作和每个后继状态选择的后续价值向量。

没有 backpointer，算法只能给出前沿形状，无法构造实现该向量的策略。

## 二十九、固定偏好与动态偏好

若偏好权重 $w$ 在整条轨迹固定，可以训练：

$$\pi(a\mid s,w)$$

如果 $w$ 随时间变化：

$$w_t\neq w_{t+1}$$

原策略的长期最优性可能失效。应把偏好状态纳入 Markov 状态或在变化时重新规划。

## 三十、单调效用函数

决策者最终可以用单调效用：

$$u:\mathbb R^m\rightarrow\mathbb R$$

选择：

$$\pi^*=\mathop{\arg\max}_{\pi}u(V^{\pi})$$

若 $u$ 对每个目标严格递增，则最优解一定位于 Pareto 前沿。

多目标动态规划保留前沿，使偏好可以在规划后决定。

## 三十一、Chebyshev 标量化

对最大化问题，给定理想或 utopian 参考点 $z^*$，定义加权最大缺口：

$$L_{\mathrm{Tch}}(v;w,z^*)=\max_{1\le i\le m}w_i(z_i^*-v_i)$$

选择：

$$v^*=\mathop{\arg\min}_{v\in\mathcal V}L_{\mathrm{Tch}}(v;w,z^*)$$

它最小化最差目标的加权不足。

## 三十二、Utopian 参考点

为避免参考点恰好落在可达边界，可设置：

$$z_i^{u}=z_i^*+\eta_i$$

其中：

$$\eta_i\gt0$$

对最大化问题，$z^u$ 比理想点略好，因此所有可达向量都位于其下方。

## 三十三、Chebyshev 几何

对固定损失水平 $\tau$：

$$L_{\mathrm{Tch}}(v;w,z^*)\le\tau$$

等价于：

$$v_i\ge z_i^*-\frac{\tau}{w_i},\qquad i=1,\ldots,m$$

其等值面是轴对齐盒的边界。权重控制每个目标允许的缺口。

## 三十四、Chebyshev 能找到非凸前沿

加权和使用超平面接触可达集合，而 Chebyshev 使用相对理想点的最大加权距离。

在适当正权重与参考点条件下，Chebyshev 标量化能够恢复非凸前沿上的 Pareto 解。

这不意味着任意权重网格都能均匀覆盖前沿；目标尺度和前沿形状仍会造成采样不均。

## 三十五、增强 Chebyshev 标量化

为减少弱 Pareto 解和并列，定义：

$$L_{\mathrm{aug}}(v)=\max_iw_i(z_i^u-v_i)+\rho\sum_iw_i(z_i^u-v_i)$$

其中：

$$\rho\gt0$$

第一项控制最差缺口，第二项在最大缺口相同的候选中偏好总体更优者。

## 三十六、Chebyshev 效用形式

也可写成最大化效用：

$$g_{\mathrm{Tch}}(v)=-\max_iw_i(z_i^u-v_i)$$

增强形式为：

$$g_{\mathrm{aug}}(v)=-L_{\mathrm{aug}}(v)$$

代码中必须统一最小化损失或最大化效用，避免符号翻转错误。

## 三十七、目标归一化

若不同目标尺度差异大，权重会失去直观意义。可归一化：

$$\widetilde v_i=\frac{v_i-z_i^{\mathrm{low}}}{z_i^{\mathrm{high}}-z_i^{\mathrm{low}}}$$

Chebyshev 损失使用：

$$\widetilde z_i^u-\widetilde v_i$$

上下界应来自可信范围或滚动估计，不能被少数异常值任意改变。

## 三十八、零权重问题

若：

$$w_i=0$$

目标 $i$ 不参与最大缺口，可能允许该目标任意恶化。

若要保证 Pareto 性，常要求：

$$w_i\gt0,\qquad i=1,\ldots,m$$

或设置最小权重：

$$w_i\ge\epsilon_w$$

## 三十九、成就标量化函数

Achievement Scalarizing Function 可以写为：

$$S(v)=\max_iw_i(z_i^u-v_i)+\rho\sum_iw_i(z_i^u-v_i)$$

参考点不必只是真正理想点，也可以是用户期望水平。

若期望点不可达，算法返回最均衡接近方案；若可达，则可进一步寻找超过期望的非支配方案。

## 四十、Chebyshev 与约束

若某些目标是硬约束，更合适的形式是：

$$\max_{\pi}V_1^{\pi}$$

满足：

$$V_i^{\pi}\ge b_i,\qquad i=2,\ldots,m$$

Chebyshev 只能表达软权衡，不能保证绝不违反安全阈值。安全、合法性和生存底线应使用 CMDP、屏障或硬过滤。

## 四十一、非线性标量化的时间不一致

线性期望满足：

$$w^\top\mathbb E[G]=\mathbb E[w^\top G]$$

但一般非线性效用不满足：

$$u(\mathbb E[G])\neq\mathbb E[u(G)]$$

Chebyshev 作用于整条轨迹的期望向量时，不能简单把每步奖励先做同样非线性标量化再运行普通 Bellman 递推。

## 四十二、局部标量化的错误

错误替代是：

$$r_t^{\mathrm{scalar}}=-\max_iw_i(z_i^*-r_{t,i})$$

然后累加：

$$\sum_t\gamma^tr_t^{\mathrm{scalar}}$$

通常：

$$-\max_iw_i\left(z_i^*-\sum_t\gamma^tr_{t,i}\right)\neq\sum_t\gamma^t\left[-\max_iw_i(z_i^*-r_{t,i})\right]$$

两者优化的是不同问题。

## 四十三、保持时间一致的方法

可选方法包括：

1. 先用集合值 Bellman 得到回报前沿，再在根状态 Chebyshev 选择。
2. 把累计向量回报或剩余目标预算纳入扩展状态。
3. 使用占用测度优化整个期望回报向量。
4. 对固定线性权重使用标量 Bellman，对非线性偏好做外层搜索。

扩展状态会增加维度，但能保留正确目标语义。

## 四十四、Chebyshev 与学习

偏好条件价值网络可写为：

$$Q_{\theta}(s,a,w)\in\mathbb R^m$$

训练目标仍可保持向量形式：

$$y=r+\gamma Q_{\bar\theta}(s',a',w)$$

动作选择使用：

$$a'=\mathop{\arg\min}_aL_{\mathrm{Tch}}(Q_{\bar\theta}(s',a,w);w,z^*)$$

这种方法是近似控制方法，非线性偏好的 Bellman 一致性仍需按具体算法证明或验证。

## 四十五、偏好采样

可从 simplex 采样权重：

$$w\sim\mathrm{Dirichlet}(\alpha)$$

若：

$$\alpha_i=1$$

得到 simplex 上的均匀分布。

小 $\alpha_i$ 更常采到角点偏好，大 $\alpha_i$ 更集中于均衡偏好。均匀采权重不等于均匀覆盖 Pareto 前沿。

## 四十六、偏好不确定性

若真实权重属于集合：

$$w\in\mathcal W$$

可做鲁棒选择：

$$\max_{v\in\mathcal V}\min_{w\in\mathcal W}u(v;w)$$

也可维护权重后验：

$$p(w\mid\mathcal D)$$

选择最大期望效用或最大信息价值的策略。

## 四十七、超体积指标

对最大化问题，参考点 $r$ 应被所有候选非支配点弱支配：

$$v\succeq r,\qquad v\in A$$

单点 $v$ 支配的盒为：

$$[r,v]=\prod_{i=1}^{m}[r_i,v_i]$$

集合 $A$ 的超体积为：

$$\mathrm{HV}(A;r)=\lambda_m\left(\bigcup_{v\in A}[r,v]\right)$$

$\lambda_m$ 是 $m$ 维 Lebesgue 体积。

## 四十八、超体积的单调性

若集合 $A$ 弱支配集合 $B$，则在相同有效参考点下：

$$\mathrm{HV}(A;r)\ge\mathrm{HV}(B;r)$$

加入一个被现有集合支配的点不会增加超体积。

加入一个扩展支配区域的非支配点会使超体积增加。

## 四十九、二维超体积

设二维非支配点按第一目标递增排序：

$$x_1\lt x_2\lt\cdots\lt x_n$$

对应第二目标递减：

$$y_1\gt y_2\gt\cdots\gt y_n$$

令 $x_0=r_1$，则：

$$\mathrm{HV}(A;r)=\sum_{i=1}^{n}(x_i-x_{i-1})(y_i-r_2)$$

前提是所有点都支配参考点。

## 五十、三维与高维超体积

三维可通过切片、递归分解或扫描计算。目标维数增加后，精确计算成本快速上升。

超体积计算复杂度不仅取决于点数 $n$，也强烈依赖目标维数 $m$。

当 $m$ 较大时，Monte Carlo、FPRAS 或近似贡献算法通常更实用。

## 五十一、超体积贡献

点 $v\in A$ 的独立超体积贡献为：

$$\Delta\mathrm{HV}(v\mid A)=\mathrm{HV}(A;r)-\mathrm{HV}(A\setminus\{v\};r)$$

贡献小的点通常位于拥挤区域或几乎被其他点覆盖。

档案超过容量时，可以删除最小贡献点，但要避免每次重算全部超体积造成高成本。

## 五十二、超体积改进

候选点 $v$ 相对当前档案 $A$ 的超体积改进为：

$$\mathrm{HVI}(v;A,r)=\mathrm{HV}(A\cup\{v\};r)-\mathrm{HV}(A;r)$$

若 $v$ 被 $A$ 支配：

$$\mathrm{HVI}(v;A,r)=0$$

Expected Hypervolume Improvement 对预测不确定性取期望，常用于多目标 Bayesian Optimization。

## 五十三、参考点选择

参考点应略差于所有感兴趣方案：

$$r_i\le\inf_{v\in A_{\mathrm{relevant}}}v_i$$

如果参考点过远，超体积主要由大矩形基线决定，前沿差异被稀释。

如果参考点被某些候选点支配关系违反，指标可能忽略这些点或产生不一致实现。

## 五十四、参考点敏感性

两个集合的超体积排序可能随参考点变化：

$$\mathrm{HV}(A;r)\gt\mathrm{HV}(B;r)$$

但对另一参考点 $r'$：

$$\mathrm{HV}(A;r')\lt\mathrm{HV}(B;r')$$

报告超体积必须同时报告归一化方式和参考点，不能只给一个数字。

## 五十五、目标缩放与超体积

若目标 $i$ 乘以常数 $c_i\gt0$，超体积按：

$$\mathrm{HV}'=\left(\prod_{i=1}^{m}c_i\right)\mathrm{HV}$$

因此不同目标量纲会强烈影响指标。

通常先归一化到：

$$\widetilde v_i\in[0,1]$$

再使用固定参考点，例如略低于零的向量。

## 五十六、Monte Carlo 超体积

选择包含支配区域的边界盒 $B$，均匀采样：

$$X_k\sim\mathrm{Uniform}(B)$$

估计：

$$\widehat{\mathrm{HV}}=\mathrm{Vol}(B)\frac{1}{N}\sum_{k=1}^{N}\mathbf 1_{\{\exists v\in A:v\succeq X_k\succeq r\}}$$

标准误差按：

$$O(N^{-1/2})$$

下降，与维数无关的速率并不意味着高维常数小。

## 五十七、超体积梯度

当点是非支配且不在组合结构切换边界上，超体积对点坐标可分段求导：

$$\nabla_v\mathrm{HV}(A;r)$$

梯度指向扩大独占支配区域的方向。

在点互相交换排序、重合或被支配时，超体积不可微或梯度不连续，需要次梯度、平滑近似或无梯度优化。

## 五十八、超体积不是全部

超体积同时反映收敛与覆盖，但不能直接说明：

- 某个具体偏好下的策略价值。
- 策略是否安全或可执行。
- 前沿估计是否校准。
- 不同状态下策略是否一致。
- 轨迹风险与方差。

应结合支配率、epsilon 指标、IGD、偏好后悔和策略级评测。

## 五十九、加性 epsilon 指标

集合 $A$ 相对参考集合 $B$ 的加性 epsilon 指标为最小 $\epsilon$，使：

$$\forall b\in B,\quad\exists a\in A:\ a_i+\epsilon\ge b_i,\ \forall i$$

记为：

$$I_{\epsilon+}(A,B)$$

它衡量 $A$ 需要整体平移多少才能弱支配参考前沿。

## 六十、IGD

给定参考前沿样本 $R$，Inverted Generational Distance 为：

$$\mathrm{IGD}(A,R)=\frac{1}{\lvert R\rvert}\sum_{r\in R}\min_{a\in A}\lVert r-a\rVert$$

IGD 同时受到参考集密度与尺度影响。

若真实前沿未知，使用算法自身合并前沿作为参考会产生评测偏差。

## 六十一、Pareto 后悔

给定真实偏好效用 $u_w$，档案 $A$ 的后悔为：

$$\mathrm{Regret}(A,w)=\max_{v\in\mathcal V}u_w(v)-\max_{a\in A}u_w(a)$$

平均后悔为：

$$\mathbb E_{w\sim p(w)}[\mathrm{Regret}(A,w)]$$

它比无偏好超体积更直接反映目标用户分布下的决策损失。

## 六十二、档案维护

候选向量 $v$ 到达时：

1. 若被档案中任一点支配，则丢弃。
2. 删除所有被 $v$ 支配的档案点。
3. 若容量未满，插入 $v$。
4. 若容量超限，按超体积贡献、拥挤距离或 epsilon 网格剪枝。

档案应同时保存策略标识、评估方差、样本量和生成版本。

## 六十三、噪声下的支配

估计价值为：

$$\widehat v_i\pm c_i$$

保守支配可以要求：

$$\widehat u_i-c_i^u\ge\widehat v_i+c_i^v,\qquad\forall i$$

这比点估计支配更难触发，但减少误删。

也可计算支配概率：

$$\mathbb P(u\succeq v\mid\mathcal D)$$

并只在概率超过阈值时剪枝。

## 六十四、统计评估

对策略 $\pi$，第 $n$ 条回放向量回报为：

$$G^{(n)}\in\mathbb R^m$$

均值估计为：

$$\widehat V^{\pi}=\frac{1}{N}\sum_{n=1}^{N}G^{(n)}$$

协方差为：

$$\widehat\Sigma^{\pi}=\frac{1}{N-1}\sum_{n=1}^{N}(G^{(n)}-\widehat V^{\pi})(G^{(n)}-\widehat V^{\pi})^\top$$

目标之间通常相关，不能只独立报告每个分量方差。

## 六十五、风险敏感向量价值

期望相同的策略可能具有不同风险。可扩展目标：

$$v=(\mathbb E[G_1],\ldots,\mathbb E[G_m],-\mathrm{CVaR}_{\alpha}(L))$$

或者把安全风险设为约束：

$$\mathrm{CVaR}_{\alpha}(L)\le b$$

把风险当普通软目标会允许极端偏好牺牲安全，硬约束更适合不可接受事件。

## 六十六、词典序偏好

若目标有严格优先级，可使用 lexicographic order。先最大化 $v_1$，在近最优集合内最大化 $v_2$：

$$v_1\ge v_1^*-\epsilon_1$$

再继续后续目标。

词典序不是 Chebyshev 的特殊权重极限在所有数值实现中的可靠替代；显式分层约束更稳定。

## 六十七、MOBA 目标向量

一个战术动作的价值可定义为：

$$v=(p_{\mathrm{win}},\Delta g,p_{\mathrm{survive}},\Delta o,-r_{\mathrm{exposure}},-c_{\mathrm{coord}})$$

其中：

- $p_{\mathrm{win}}$ 是后续胜率估计。
- $\Delta g$ 是经济变化。
- $p_{\mathrm{survive}}$ 是生存概率。
- $\Delta o$ 是地图目标收益。
- $r_{\mathrm{exposure}}$ 是危险暴露。
- $c_{\mathrm{coord}}$ 是团队失配代价。

目标必须定义共同时间窗，否则短期收益与长期胜率无法直接比较。

## 六十八、越塔决策

候选动作包括进攻、等待和撤退，其向量可写为：

$$v_a=(p_{\mathrm{kill}},p_{\mathrm{survive}},\Delta g,\Delta o,-T_{\mathrm{cooldown}})$$

Pareto 集保留“高击杀低生存”和“低击杀高生存”等不可比方案。

安全底线应先约束：

$$p_{\mathrm{survive}}\ge p_{\min}$$

再在可行集合上使用 Chebyshev 或超体积选择，而不是让偏好权重决定是否送塔。

## 六十九、资源争夺

打龙、接团、推塔和分带的回报向量可以是：

$$v=(p_{\mathrm{objective}},p_{\mathrm{teamfight}},\Delta g,-T_{\mathrm{arrival}},-R_{\mathrm{ambush}})$$

状态相关偏好 $w(s)$ 可以在资源即将刷新时提高目标权重，在己方低血时提高生存权重。

若偏好在规划期间变化，应把阶段变量加入状态并重新求解。

## 七十、团队角色差异

不同角色可以有不同局部偏好：

$$w^{\mathrm{tank}}\neq w^{\mathrm{carry}}\neq w^{\mathrm{support}}$$

但团队目标不是五个局部效用简单相加。可定义团队向量：

$$V^{\mathrm{team}}=\sum_{i=1}^{5}\alpha_iV^i+\Phi(V^1,\ldots,V^5)$$

$\Phi$ 表示阵型、同步和互补收益。

## 七十一、偏好条件策略

统一网络接收偏好：

$$\pi_{\theta}(a\mid s,w)$$

目标是覆盖：

$$w\in\mathcal W$$

训练时应覆盖角点、均衡区和业务常用偏好，而不是只均匀采样。

上线时必须记录实际 $w$，否则无法解释同一状态下为何选择不同动作。

## 七十二、非支配动作筛选

对状态 $s$ 的动作向量估计：

$$\widehat Q(s,a)\in\mathbb R^m$$

先计算：

$$A_{\mathrm{ND}}(s)=\{a\mid\nexists a':\widehat Q(s,a')\succ\widehat Q(s,a)\}$$

再在非支配动作中使用偏好选择。

这减少明显劣势动作，但模型误差可能使真实优质动作被误删，应配合不确定性边界。

## 七十三、安全过滤与多目标选择

先定义硬可行动作集合：

$$A_{\mathrm{safe}}(s)=\{a\in A(s)\mid g_{\mathrm{legal}}(s,a)=1,\ g_{\mathrm{safety}}(s,a)=1\}$$

再计算：

$$A_{\mathrm{Pareto}}(s)=\mathrm{ND}\{\widehat Q(s,a)\mid a\in A_{\mathrm{safe}}(s)\}$$

最后用 Chebyshev、线性偏好或规则选择。顺序不能颠倒，否则标量高分可能覆盖非法或不可接受动作。

## 七十四、超体积用于策略集训练

若一个批次产生策略价值集合：

$$A_{\theta}=\{V^{\pi_{\theta,w_j}}\}_{j=1}^{K}$$

可以最大化：

$$J_{\mathrm{HV}}(\theta)=\mathrm{HV}(A_{\theta};r)$$

它鼓励策略覆盖不同权衡区域。

但超体积梯度会把训练重点放在边界和独占区域，可能忽略常用偏好附近的精细性能，应与偏好分布损失组合。

## 七十五、动态参考点

训练早期前沿较差，固定严格参考点可能使所有点都无有效支配盒。动态参考点可设为：

$$r_i^{(k)}=\min_{v\in A_k}v_i-\delta_i$$

但动态参考点会使跨迭代超体积不可直接比较。

训练监控应另保留一个固定评测参考点。

## 七十六、Bellman 备份伪代码逻辑

每次状态备份可按以下逻辑：

1. 对每个动作收集所有后继状态集合。
2. 逐个执行加权 Minkowski 和。
3. 每合并一个后继就做 epsilon 非支配剪枝。
4. 跨动作取并集。
5. 若允许动作随机化，计算或近似凸包。
6. 保存价值、动作和后继 backpointer。
7. 达到容量上限时按误差保证或超体积贡献压缩。

输出不是一个最大值，而是带策略来源的非支配档案。

## 七十七、复杂度控制

可采用：

- 自适应 epsilon 网格。
- 增量非支配排序。
- 近邻索引与正交范围查询。
- 分目标上下界剪枝。
- 权重集驱动的 CCS 搜索。
- 只在访问状态维护局部前沿。
- 分层目标与硬约束降维。

当目标维数增大时，大量点会互不支配，Pareto 方法的区分能力下降。

## 七十八、评测协议

至少报告：

1. 每目标均值、方差和置信区间。
2. 非支配策略数量与重复率。
3. 固定参考点下的归一化超体积。
4. epsilon 指标与 IGD。
5. 业务偏好分布下的平均与最坏后悔。
6. 安全约束违例率。
7. 不同权重下策略切换稳定性。
8. 计算耗时、档案大小和 Bellman 剪枝误差。

## 七十九、测试用例

应包含：

1. 两目标凸前沿，加权和可以覆盖受支撑点。
2. 两目标非凸前沿，加权和漏点而 Chebyshev 找到。
3. 被支配点加入后超体积不变。
4. 新极端点加入后超体积增加。
5. 改变参考点时验证指标敏感性。
6. 逐分量理想点不可达的反例。
7. 非线性逐步标量化与整体标量化不等价的反例。
8. 随机策略凸化回报集合。
9. epsilon 剪枝误差界。
10. backpointer 恢复策略与价值一致。

## 八十、一个三策略示例

设三种策略价值为：

$$v^A=(9,3)$$

$$v^B=(6,6)$$

$$v^C=(3,9)$$

三者互不支配。若参考点：

$$r=(0,0)$$

超体积同时奖励两个极端点和中间均衡点的覆盖。

如果存在：

$$v^D=(5,5)$$

则 $v^B\succ v^D$，加入 $v^D$ 不增加超体积。

## 八十一、Chebyshev 示例

理想点为：

$$z^*=(9,9)$$

均衡权重为：

$$w=(1/2,1/2)$$

三种策略的最大加权缺口分别为：

$$L_{\mathrm{Tch}}(v^A)=3$$

$$L_{\mathrm{Tch}}(v^B)=3/2$$

$$L_{\mathrm{Tch}}(v^C)=3$$

因此均衡偏好选择 $v^B$。

## 八十二、常见错误

1. 对向量价值逐分量取最大并声称得到可实现策略。
2. 不说明允许确定性还是随机策略。
3. 用加权和声称覆盖了所有非凸 Pareto 前沿。
4. 不归一化目标就解释 Chebyshev 权重。
5. 把非线性标量化逐步施加到即时奖励。
6. 让软权重代替不可违反的安全约束。
7. 使用没有被全部候选支配的超体积参考点。
8. 不报告参考点和目标尺度就比较超体积。
9. 在有噪声价值上做激进确定性支配剪枝。
10. 只保存价值点，不保存可恢复策略。

## 八十三、最小可行落地

第一阶段只选择三个目标：

$$v=(p_{\mathrm{win}},p_{\mathrm{survive}},\Delta g)$$

先用离线回放和仿真产生有限候选策略，计算置信区间并建立非支配档案。

安全条件固定为：

$$p_{\mathrm{survive}}\ge p_{\min}$$

在可行档案上使用归一化增强 Chebyshev 选择，并用固定参考点超体积监控覆盖质量。

## 八十四、工程架构

推荐流程：

$$\mathrm{State}\rightarrow\mathrm{VectorValue}\rightarrow\mathrm{Uncertainty}\rightarrow\mathrm{SafetyFilter}\rightarrow\mathrm{NDArchive}\rightarrow\mathrm{Preference}\rightarrow\mathrm{Action}$$

训练阶段维护策略级前沿；运行阶段只在安全候选中进行快速偏好选择。

所有决策日志应记录向量估计、置信区间、支配关系、归一化参数、权重、参考点与最终动作。

## 八十五、结论

向量价值函数保留多个目标的期望累计回报，Pareto 偏序把“全面不差且至少一项更好”与不可比权衡区分开。非支配 Bellman 算子通过后继价值集合的加权 Minkowski 和、跨动作并集与非支配剪枝，构造状态相关 Pareto 前沿；它的核心对象是集合与策略来源，而不是逐分量最大值。

线性加权和计算简单并与普通 Bellman 递推兼容，但只能覆盖受支撑的凸前沿点。Chebyshev 标量化以理想点的最大加权缺口表达均衡改进，能够访问非凸前沿；增强项可减少弱 Pareto 与并列问题。由于它是非线性效用，必须区分“对累计期望向量标量化”和“逐步标量化即时奖励”，避免时间不一致。

超体积用一个参考点衡量非支配集合覆盖的支配区域，同时奖励逼近前沿和保持多样性。它对尺度与参考点敏感，高维计算昂贵，也不能替代安全、偏好后悔和统计不确定性。MOBA 落地时应先做硬安全过滤，再维护带置信度和策略 backpointer 的非支配档案，最后按可解释偏好选择动作。
