# Fitted Q Evaluation、Fitted Q Iteration、Conservative Q-Learning、Bellman Completeness、Concentrability 与 DICE

## 摘要

离线强化学习只使用已经收集的固定数据集学习或评估策略，不能在训练过程中主动探索环境。它的核心困难不是普通监督学习误差，而是策略会查询数据分布之外的状态–动作，Bellman 备份又会把这种外推误差逐步放大。

Fitted Q Evaluation（FQE）评估一个固定目标策略；Fitted Q Iteration（FQI）通过最优 Bellman 备份学习控制策略；Conservative Q-Learning（CQL）主动压低数据外动作的价值，减少过度乐观；Bellman completeness 描述函数类能否容纳反复 Bellman 备份；concentrability coefficient 描述目标策略分布相对数据分布的覆盖程度；marginalized importance sampling 与 DICE 则通过估计占用测度密度比进行离线策略评估。

本文统一说明这些方法的目标、公式、成立条件、误差来源、诊断指标，以及它们在 5v5 游戏回放学习中的应用边界。

## 一、离线强化学习设置

考虑折扣 MDP：

$$\mathcal M=(\mathcal S,\mathcal A,P,r,\gamma,d_0)$$

其中 $0\leq\gamma<1$。固定数据集为：

$$\mathcal D=\{(S_i,A_i,R_i,S_i',D_i)\}_{i=1}^N$$

$D_i$ 表示终止标记。数据由未知或部分已知的行为策略 $\mu$ 产生，目标策略为 $\pi$。

目标策略的动作价值函数为：

$$Q^{\pi}(s,a)=\mathbb E^{\pi}\left[\sum_{t=0}^{\infty}\gamma^tR_t\mid S_0=s,A_0=a\right]$$

状态价值为：

$$V^{\pi}(s)=\mathbb E_{a\sim\pi(\cdot\mid s)}[Q^{\pi}(s,a)]$$

初始分布下的策略价值为：

$$J(\pi)=\mathbb E_{S_0\sim d_0}[V^{\pi}(S_0)]$$

## 二、离线学习为何困难

普通监督学习只需要在训练分布上拟合标签。离线强化学习的标签由当前价值函数自己生成：

$$Y=R+\gamma\mathcal BQ(S')$$

其中 $\mathcal B$ 可能是目标策略期望或最大化操作。如果 $S'$ 上选择的数据外动作具有虚高价值，错误就会进入标签并在多轮备份中传播。

离线问题通常同时包含：

- 有限样本误差；
- 函数逼近误差；
- Bellman 备份误差；
- 分布偏移；
- 行为策略未知；
- 长时域重要性权重高方差；
- 策略选择重复使用评估数据造成的偏差。

## 三、策略 Bellman 算子

固定策略 $\pi$ 的 Bellman 算子为：

$$\left(T^{\pi}Q\right)(s,a)=r(s,a)+\gamma\mathbb E_{s'\sim P(\cdot\mid s,a),a'\sim\pi(\cdot\mid s')}[Q(s',a')]$$

目标价值满足固定点方程：

$$Q^{\pi}=T^{\pi}Q^{\pi}$$

最优 Bellman 算子为：

$$\left(T^*Q\right)(s,a)=r(s,a)+\gamma\mathbb E_{s'\sim P(\cdot\mid s,a)}\left[\max_{a'}Q(s',a')\right]$$

最优动作价值满足：

$$Q^*=T^*Q^*$$

FQE 近似 $T^{\pi}$ 的固定点；FQI 近似 $T^*$ 的固定点。两者不能混为同一个算法。

## 四、Fitted Q Evaluation

FQE 用固定离线数据评估给定策略 $\pi$。初始化 $Q_0$ 后，第 $k$ 轮构造目标：

$$Y_i^{(k)}=R_i+\gamma(1-D_i)\mathbb E_{a'\sim\pi(\cdot\mid S_i')}[Q_k(S_i',a')]$$

然后做监督回归：

$$Q_{k+1}=\arg\min_{f\in\mathcal F}\frac{1}{N}\sum_{i=1}^{N}\left(f(S_i,A_i)-Y_i^{(k)}\right)^2$$

最终价值估计为：

$$\widehat J_{\mathrm{FQE}}(\pi)=\frac{1}{N_0}\sum_{j=1}^{N_0}\mathbb E_{a\sim\pi(\cdot\mid S_{0,j})}[\widehat Q(S_{0,j},a)]$$

其中 $S_{0,j}$ 应来自目标初始分布，而不是任意回放中间状态。

## 五、FQE 的实现要点

### 1. 目标策略必须固定

FQE 的每轮备份都使用同一个 $\pi$。如果一边评估一边根据 $Q_k$ 改策略，算法已经变成控制方法，不再是固定策略评估。

### 2. 终止与截断必须区分

真正终止状态通常不 bootstrap；仅因日志窗口结束造成的截断可能仍需 bootstrap。把两者都设为 $D=1$ 会系统性低估长时域价值。

### 3. Target network

回归目标应在一轮内冻结，神经网络实现通常使用 target network 或完整 fitted iteration，减少 moving-target 不稳定。

### 4. Cross-fitting

用同一数据同时拟合 $Q$ 和报告误差会产生乐观偏差。可按完整轨迹切分数据，在训练折拟合 FQE，在验证折估计 Bellman residual 或 doubly robust 修正。

### 5. FQE 不是天然保守估计

FQE 可能高估也可能低估。若目标策略访问数据稀疏动作，FQE 的回归误差同样可能严重外推。

## 六、Fitted Q Iteration

FQI 用最优 Bellman 备份学习控制价值。第 $k$ 轮目标为：

$$Y_i^{(k)}=R_i+\gamma(1-D_i)\max_{a'}Q_k(S_i',a')$$

回归步骤为：

$$Q_{k+1}=\arg\min_{f\in\mathcal F}\frac{1}{N}\sum_{i=1}^{N}\left(f(S_i,A_i)-Y_i^{(k)}\right)^2$$

学习到的贪心策略为：

$$\pi_{k+1}(s)\in\arg\max_aQ_{k+1}(s,a)$$

对于连续动作，可用 actor、采样优化或结构化优化器近似 $\max$，但近似误差必须计入结果。

## 七、FQI 的外推误差

最大化操作会偏好估计误差较大的动作。若：

$$\widehat Q(s,a)=Q(s,a)+\epsilon(s,a)$$

则通常有：

$$\mathbb E\left[\max_a\widehat Q(s,a)\right]\geq\max_aQ(s,a)$$

在离线数据中，未充分覆盖动作的 $\epsilon(s,a)$ 往往更大，因此 FQI 可能把策略推向数据几乎没有支持的动作。

常见缓解方法包括：

- 限制候选动作靠近行为策略；
- 使用不确定性惩罚；
- 使用 ensemble 的下置信估计；
- 使用 CQL 等保守价值正则；
- 使用行为克隆或 advantage-weighted policy improvement；
- 对每次策略改进做独立 OPE。

## 八、FQE 与 FQI 的区别

| 方法 | Bellman 算子 | 目标 | 输出 |
|---|---|---|---|
| FQE | $T^{\pi}$ | 评估固定策略 | $\widehat Q^{\pi}$ 与 $\widehat J(\pi)$ |
| FQI | $T^*$ | 学习改进策略 | $\widehat Q^*$ 与近似贪心策略 |

FQI 生成候选策略后，通常应使用独立 FQE、DICE、重要性采样或在线安全试验评估，不能直接把 FQI 的训练价值当作可信策略价值。

## 九、Conservative Q-Learning

CQL 的核心思想是：在拟合 Bellman 方程的同时，提高数据动作价值与广泛候选动作价值之间的差距，使数据外动作不容易因函数逼近误差获得虚高价值。

离散动作的一种典型 CQL 正则项为：

$$\mathcal R_{\mathrm{CQL}}(Q)=\mathbb E_{s\sim\mathcal D}\left[\log\sum_a\exp Q(s,a)-\mathbb E_{a\sim\mathcal D(\cdot\mid s)}Q(s,a)\right]$$

总目标为：

$$\min_Q\mathcal L_{\mathrm{Bellman}}(Q)+\alpha\mathcal R_{\mathrm{CQL}}(Q)$$

其中：

$$\mathcal L_{\mathrm{Bellman}}(Q)=\mathbb E_{(s,a,r,s')\sim\mathcal D}\left[Q(s,a)-\widehat{\mathcal B}Q(s,a)\right]^2$$

$\widehat{\mathcal B}$ 可以对应 Q-learning、actor–critic 或其他目标备份。

## 十、CQL 正则的作用

第一项：

$$\log\sum_a\exp Q(s,a)$$

会关注所有候选动作，尤其是高价值动作；第二项：

$$\mathbb E_{a\sim\mathcal D(\cdot\mid s)}Q(s,a)$$

抬高数据动作相对地位。最小化两者之差会压低未被数据支持但价值虚高的动作。

当 $\alpha$ 太小，保守性不足；当 $\alpha$ 太大，策略可能退化为近似行为克隆，忽略数据中能够支持的真实改进。

## 十一、连续动作 CQL

连续动作下无法直接计算所有动作的 log-sum-exp，通常从多个分布采样动作，例如当前策略、均匀提议或行为策略近似：

$$a^{(j)}\sim q(\cdot\mid s)$$

并用重要性修正近似：

$$\log\int\exp Q(s,a)\,\mathrm da\approx\log\frac{1}{M}\sum_{j=1}^{M}\frac{\exp Q(s,a^{(j)})}{q(a^{(j)}\mid s)}$$

若提议分布没有覆盖高价值区域，近似仍可能失真。数值实现必须使用 log-sum-exp 稳定化。

## 十二、CQL 的保证边界

CQL 在特定有限样本、函数类、优化精度和分布假设下可以导出保守价值或策略改进结论，但不能无条件保证每个状态动作都低估真实价值。

实际报告应明确：

- 使用哪一种 CQL 目标；
- 正则系数 $\alpha$ 如何选择；
- 候选动作如何采样；
- 行为策略是否估计；
- Bellman 目标与 actor 如何更新；
- 保守性是在数据分布、策略分布还是逐点意义下讨论。

## 十三、Bellman Realizability

函数类记为 $\mathcal F$。Realizability 假设目标价值位于函数类中：

$$Q^{\pi}\in\mathcal F$$

控制问题中可能要求：

$$Q^*\in\mathcal F$$

Realizability 只说明最终目标可表达，不保证中间 Bellman 备份仍可表达。

## 十四、Bellman Completeness

策略评估的 Bellman completeness 要求：

$$T^{\pi}f\in\mathcal F,\qquad \forall f\in\mathcal F$$

控制问题的 Bellman completeness 要求：

$$T^*f\in\mathcal F,\qquad \forall f\in\mathcal F$$

近似 completeness 可写为：

$$\sup_{f\in\mathcal F}\inf_{g\in\mathcal F}\lVert g-Tf\rVert_{\nu}\leq\varepsilon_{\mathrm{comp}}$$

其中 $\nu$ 是指定参考分布。

FQE 和 FQI 反复执行“Bellman 备份后投影回函数类”。如果函数类不 complete，每一轮都会产生结构性投影误差，即使 $Q^{\pi}$ 或 $Q^*$ 本身碰巧位于函数类中也可能如此。

## 十五、Completeness 为什么很强

神经网络函数类容量很大，但“容量大”不等于对 Bellman 算子闭合。Bellman 备份包含：

- 转移期望；
- 目标策略积分；
- 最大化或 actor 优化；
- 终止与奖励结构。

这些运算可能把一个简单函数映射成函数类无法准确表示的形状。

工程上可以用 holdout Bellman error、不同网络宽度、不同 target 更新与多步备份比较近似 completeness，但有限实验不能证明全局闭合。

## 十六、Discounted Occupancy Measure

目标策略的归一化折扣状态占用为：

$$d_{\gamma}^{\pi}(s)=(1-\gamma)\sum_{t=0}^{\infty}\gamma^t\Pr_{\pi}(S_t=s)$$

状态–动作占用为：

$$d_{\gamma}^{\pi}(s,a)=d_{\gamma}^{\pi}(s)\pi(a\mid s)$$

它满足归一化：

$$\sum_{s,a}d_{\gamma}^{\pi}(s,a)=1$$

策略价值可以写成：

$$J(\pi)=\frac{1}{1-\gamma}\mathbb E_{(s,a)\sim d_{\gamma}^{\pi}}[r(s,a)]$$

## 十七、Concentrability Coefficient

设离线数据的参考状态–动作分布为 $\nu(s,a)$。最直接的逐点 concentrability 为：

$$C_{\infty}(\pi,\nu)=\left\lVert\frac{d_{\gamma}^{\pi}}{\nu}\right\rVert_{\infty}$$

二阶版本为：

$$C_2(\pi,\nu)=\mathbb E_{(s,a)\sim\nu}\left[\left(\frac{d_{\gamma}^{\pi}(s,a)}{\nu(s,a)}\right)^2\right]$$

如果存在目标策略访问但数据从不覆盖的状态动作：

$$d_{\gamma}^{\pi}(s,a)>0,\qquad \nu(s,a)=0$$

则相应密度比和 concentrability 为无穷大，单凭该离线数据无法非参数识别该部分策略价值。

## 十八、逐时刻 Concentrability

有些理论使用第 $t$ 步状态–动作分布 $d_t^{\pi}$：

$$c_t(\pi,\nu)=\left\lVert\frac{d_t^{\pi}}{\nu}\right\rVert_{\infty}$$

再构造折扣加权系数，例如：

$$C^{(1)}=(1-\gamma)\sum_{t=0}^{\infty}\gamma^tc_t$$

不同论文对 concentrability 的定义、范数、策略集合和时间加权不同。引用误差界时必须同时给出所采用的定义，不能只报告一个没有语义的 $C$。

## 十九、Concentrability 与误差传播

Bellman 回归误差通常在数据分布 $\nu$ 下测量，而最终价值关心目标策略分布 $d_{\gamma}^{\pi}$。密度比把两者连接：

$$\mathbb E_{d_{\gamma}^{\pi}}[f]=\mathbb E_{\nu}\left[\frac{d_{\gamma}^{\pi}}{\nu}f\right]$$

由 Cauchy–Schwarz 可得：

$$\lVert f\rVert_{d_{\gamma}^{\pi}}\leq\sqrt{C_2(\pi,\nu)}\lVert f\rVert_{\nu}$$

因此即使数据分布上的 Bellman error 很小，若 concentrability 很大，目标策略误差仍可能巨大。

具体 FQE 或 FQI 误差界还包含折扣因子、函数类复杂度、迭代次数和 approximation error；不能把上式单独当作完整性能定理。

## 二十、Trajectory Importance Sampling

若行为策略 $\mu$ 已知，单步重要性比为：

$$\rho_t=\frac{\pi(A_t\mid S_t)}{\mu(A_t\mid S_t)}$$

截至时刻 $t$ 的累积比为：

$$\rho_{0:t}=\prod_{k=0}^{t}\rho_k$$

整条轨迹重要性采样可以写成：

$$\widehat J_{\mathrm{IS}}=\frac{1}{N}\sum_{i=1}^{N}\rho_{0:T_i}^{(i)}G_i$$

其中 $G_i$ 是轨迹折扣回报。随着时域增加，乘积权重的方差通常急剧增长。

## 二十一、Per-Decision Importance Sampling

Per-decision IS 在每个奖励时刻只使用截至该时刻的权重：

$$\widehat J_{\mathrm{PDIS}}=\frac{1}{N}\sum_{i=1}^{N}\sum_{t=0}^{T_i}\gamma^t\rho_{0:t}^{(i)}R_t^{(i)}$$

它通常比整轨迹 IS 方差低，但仍包含随时域增长的概率比乘积。

Self-normalized IS 用权重和归一化，可以降低方差：

$$\widehat J_{\mathrm{SNIS}}=\frac{\sum_iw_iG_i}{\sum_iw_i}$$

但有限样本下通常引入偏差。权重裁剪也产生偏差–方差权衡。

## 二十二、Marginalized Importance Sampling

边缘重要性采样不使用完整轨迹概率比，而直接估计目标占用与数据占用的密度比：

$$w(s,a)=\frac{d_{\gamma}^{\pi}(s,a)}{d_{\gamma}^{\mu}(s,a)}$$

于是：

$$J(\pi)=\frac{1}{1-\gamma}\mathbb E_{(s,a)\sim d_{\gamma}^{\mu}}[w(s,a)r(s,a)]$$

若分解为状态比和动作比：

$$w(s,a)=\frac{d_{\gamma}^{\pi}(s)}{d_{\gamma}^{\mu}(s)}\frac{\pi(a\mid s)}{\mu(a\mid s)}$$

边缘化避免显式乘积整个历史的重要性比，但把难题转化为高维密度比估计。

## 二十三、Occupancy Flow Identity

目标折扣占用满足流守恒。对任意测试函数 $f(s,a)$：

$$\mathbb E_{d_{\gamma}^{\pi}}\left[f(S,A)-\gamma\mathbb E_{A'\sim\pi(\cdot\mid S')}f(S',A')\right]=(1-\gamma)\mathbb E_{S_0\sim d_0,A_0\sim\pi}f(S_0,A_0)$$

代入：

$$d_{\gamma}^{\pi}(s,a)=w(s,a)d_{\gamma}^{\mu}(s,a)$$

得到密度比矩条件：

$$\mathbb E_{d_{\gamma}^{\mu}}\left[w(S,A)\left(f(S,A)-\gamma\mathbb E_{A'\sim\pi}f(S',A')\right)\right]=(1-\gamma)\mathbb E_{d_0,\pi}f(S_0,A_0)$$

DICE 方法的核心就是在不显式估计行为策略概率的情况下，用这些流守恒矩条件估计 $w$。

## 二十四、DICE 方法族

DICE 不是单一固定公式，而是一类通过 stationary distribution correction 或 occupancy ratio 求解离线策略评估的方法。常见变体包括 DualDICE、GenDICE、GradientDICE 与 BestDICE 等。

一个典型的二次 saddle objective 可以写成：

$$\min_{\nu}\max_{w}\ \mathbb E_{d^{\mu}}\left[w(S,A)\left(\nu(S,A)-\gamma\mathbb E_{A'\sim\pi}\nu(S',A')\right)-\frac{1}{2}w(S,A)^2\right]-(1-\gamma)\mathbb E_{d_0,\pi}\nu(S_0,A_0)$$

在理想函数类和优化条件下，对偶变量 $w$ 对应目标占用与数据占用的密度比。

不同 DICE 变体会改变：

- 使用状态比还是状态–动作比；
- 正则函数及其凸共轭；
- 是否显式施加归一化；
- 是否处理平均回报而非折扣回报；
- 是否加入非负约束；
- 如何稳定 saddle-point 优化。

## 二十五、DICE 的归一化与非负性

真实密度比满足：

$$w(s,a)\geq 0$$

以及：

$$\mathbb E_{d_{\gamma}^{\mu}}[w(S,A)]=1$$

神经网络 saddle-point 求解可能产生负值或归一化漂移。可以使用正值参数化、约束优化或显式校准，但每种处理都会改变优化与统计性质。

若估计权重集中在少数样本上，应报告有效样本量：

$$\mathrm{ESS}=\frac{\left(\sum_iw_i\right)^2}{\sum_iw_i^2}$$

很小的 ESS 表示目标策略主要依赖数据集中极少数样本，即使点估计有限也不可靠。

## 二十六、DICE 与行为策略估计

普通 IS 需要动作概率比 $\pi/\mu$，行为策略未知时必须先估计 $\mu$。DICE 通过 occupancy flow moment 避免显式构造完整行为策略概率。

这不意味着 DICE 消除了覆盖要求。如果目标 occupancy 不绝对连续于数据 occupancy，真实密度比不存在或为无穷大，DICE 也无法恢复缺失信息。

## 二十七、Doubly Robust 组合

可以把 FQE 的 $\widehat Q$ 与 DICE 的密度比 $\widehat w$ 组合。定义：

$$\widehat V(s)=\mathbb E_{a\sim\pi(\cdot\mid s)}[\widehat Q(s,a)]$$

Bellman residual 为：

$$\widehat\delta=R+\gamma(1-D)\widehat V(S')-\widehat Q(S,A)$$

一种折扣 doubly robust 估计为：

$$\widehat J_{\mathrm{DR}}=\mathbb E_{S_0\sim d_0}[\widehat V(S_0)]+\frac{1}{1-\gamma}\mathbb E_{(S,A,R,S')\sim\mathcal D}[\widehat w(S,A)\widehat\delta]$$

在相应正则条件、样本拆分和正确 nuisance 模型下，如果价值模型或密度比模型中至少一个正确，可以消除一部分一阶偏差。

“Doubly robust” 不意味着任意一个神经网络训练失败时结果仍可靠，也不消除覆盖失败。

## 二十八、置信区间

回放中的 transition 具有轨迹相关性，bootstrap 应以完整对局、玩家或匹配组为单位，而不是随机重采样单帧。

若估计器写成轨迹贡献 $\widehat\psi_i$，标准误可以基于：

$$\widehat{\mathrm{SE}}=\sqrt{\frac{1}{N(N-1)}\sum_{i=1}^{N}(\widehat\psi_i-\bar\psi)^2}$$

对复杂 FQE、DICE 和策略选择流程，应在每个 bootstrap 重样本中重新拟合全部 nuisance 模型，否则会低估训练不确定性。

## 二十九、策略选择偏差

若在同一验证集上评估大量候选策略并选择最大值：

$$\widehat\pi=\arg\max_{\pi\in\Pi}\widehat J(\pi)$$

则：

$$\widehat J(\widehat\pi)$$

通常对最终选择策略存在乐观偏差。应使用嵌套数据切分、独立最终测试集、置信下界选择或多重比较修正。

## 三十、5v5 回放数据建模

### 1. 状态

状态可以包含双方存活、血量、经济、等级、技能状态、兵线、视野、地图目标与阶段摘要。不能把未来事件或执行时不可见信息直接输入 actor。

### 2. 动作

高层动作可以是开团、撤退、集火、转线、控龙、推塔和换资源。动作粒度必须与日志能够可靠识别的决策时刻一致。

### 3. 行为策略混合

数据可能来自不同玩家、段位、补丁版本和推荐系统：

$$d^{\mathcal D}=\sum_k\omega_kd^{\mu_k}$$

把它假设成单一平稳行为策略可能导致错误密度比。应保存来源、版本、角色和匹配条件，并进行分层建模。

### 4. 奖励

击杀、经济和胜负等密集或稀疏奖励必须与评估目标一致。训练后重新改变奖励权重，相当于评估不同 MDP。

## 三十一、5v5 中的 FQE 与 FQI

### FQE

评估固定高层策略在历史地图、阵容和对手分布上的折扣回报。应按完整对局切分，并报告不同版本、阵容和角色上的最坏误差。

### FQI

从回放中学习策略改进，但贪心动作必须受合法动作掩码、地图通行、技能冷却和资源规则约束。未在数据中充分出现的高层联合动作不能仅凭高 Q 值进入部署。

### CQL

压低罕见开团时机、罕见阵容组合或极端位置动作的虚高价值。保守系数应通过独立 OPE 和回放覆盖共同选择。

## 三十二、覆盖诊断

### 1. 动作支持率

统计目标策略动作在相似状态邻域内是否有数据支持。

### 2. 密度比尾部

报告 $\widehat w$ 的最大值、分位数、ESS 和被裁剪质量。

### 3. 表征距离

计算目标策略访问表示与离线数据表示之间的最近邻距离或核密度，但不能把表示距离自动解释为真实 concentrability。

### 4. 分层覆盖

分别检查英雄、位置、阵容、地图区域、比赛阶段、版本和玩家水平。总体覆盖可能掩盖某个关键子群完全缺失。

### 5. 反事实动作检查

对目标策略偏好的动作，检索最相似回放片段并人工或规则验证其合法性与后果。

## 三十三、联合工作流

推荐流程：

1. 按完整对局与版本切分训练、调参和最终测试集；
2. 建立状态、动作、终止和奖励语义；
3. 用行为克隆诊断动作覆盖，而不是只追求行为策略精度；
4. 用 FQI 或 CQL 产生候选策略；
5. 用独立 FQE 评估候选策略；
6. 用 marginalized IS 或 DICE 估计 occupancy ratio；
7. 用 doubly robust 估计交叉检查 FQE 与密度比结果；
8. 报告 concentrability proxy、权重 ESS、Bellman residual 和跨版本误差；
9. 只在下置信界和安全规则通过后进行小流量在线验证；
10. 在线执行仍需经过原生动作合法性、资源、碰撞、联合规划和 MAPF 检查。

## 三十四、与现有游戏数学层的组合

1. P23 的 BOCPD 与 HSMM 识别版本变化和战斗阶段，避免混合不兼容数据；
2. P24 的 belief planning 为部分可观测状态构造 belief 特征；
3. Common-information 与 occupancy-state 模型明确多人信息边界；
4. FQI 或 CQL 从固定回放学习候选高层策略；
5. FQE、DICE 和 doubly robust OPE 评估候选策略；
6. P27 施加资源和风险预算；
7. P30 的经验 Bernstein、confidence sequence 与 conformal risk control 提供有限样本风险控制；
8. 用真实仿真和回放复核离线模型无法识别的状态动作。

## 三十五、工程诊断清单

至少记录：

- FQE holdout Bellman residual；
- FQI 每轮目标值与策略动作分布；
- CQL 正则项、Bellman loss 与拉格朗日参数；
- 数据动作与目标动作的价值差；
- 目标策略相对行为数据的动作支持率；
- DICE 密度比归一化误差、负权重比例和 ESS；
- trajectory IS、PDIS、MIS、DICE、FQE 与 DR 的估计差异；
- 完整对局 bootstrap 置信区间；
- 不同版本、角色、阵容与阶段的子群结果；
- 最终测试集只使用一次的策略选择记录。

## 三十六、常见误区

### 1. 把 FQI 训练 Q 值当作策略评估

最大化和分布外动作会造成明显乐观偏差，应使用独立 OPE。

### 2. 把 FQE 当作无偏估计器

FQE 仍依赖函数类、覆盖、优化和 Bellman completeness。

### 3. 认为 CQL 一定逐点低估

保守性结论依赖具体目标和假设，实际网络可能在某些状态仍高估。

### 4. 把 realizability 当作 completeness

$Q^{\pi}\in\mathcal F$ 不代表 $T^{\pi}f\in\mathcal F$ 对所有 $f$ 成立。

### 5. 只看平均覆盖

关键阵容或极端团战阶段可能完全没有数据支持。

### 6. 认为 DICE 不需要覆盖

DICE 避免显式行为策略估计，但不能从零数据恢复目标 occupancy。

### 7. 按 transition 随机切分

相邻帧泄漏会让训练和测试高度相关。应按完整对局、玩家或匹配组切分。

### 8. 裁剪权重后仍声称无偏

裁剪、自归一化和正则化都会改变偏差–方差权衡。

### 9. 用同一测试集选择并报告策略

这会产生选择偏差，尤其在候选策略很多时。

### 10. 绕过原生游戏规则

离线策略只生成候选高层动作，不具有执行合法性的最终决定权。

## 三十七、选择建议

若只需要评估一个固定策略，优先使用 FQE，并以 MIS、DICE 或 DR 结果交叉验证。

若要从固定数据中学习新策略，FQI 是基础方法，但应在覆盖差时加入行为约束、不确定性或 CQL 保守正则。

若函数逼近误差是主要风险，检查 Bellman realizability 与 approximate completeness，而不是只增加网络规模。

若目标策略与数据分布明显不同，报告 concentrability proxy、密度比尾部和 ESS；覆盖为零时应拒绝离线结论。

若行为策略未知或轨迹 IS 方差过高，可使用 marginalized IS 或 DICE 估计 occupancy ratio，再与 FQE 组成 doubly robust 估计。

## 三十八、结论

FQE 解决固定策略评估，FQI 解决离线控制，CQL 用保守正则抑制数据外动作过度乐观。Bellman completeness 决定函数类能否承受反复 Bellman 备份，concentrability 决定数据分布上的误差会被目标策略放大多少。Trajectory IS 直接修正整条路径分布，marginalized IS 和 DICE 则通过占用测度密度比降低长时域乘积权重问题。

这些方法不能绕过离线强化学习的基本识别边界：目标策略访问而数据完全没有覆盖的状态动作，无法仅靠更复杂的神经网络或更先进的 OPE 恢复。可信的游戏离线学习必须同时报告 Bellman 误差、函数类假设、覆盖、密度比尾部、有效样本量、策略选择偏差和跨版本稳定性，并以独立仿真或小流量在线试验完成最后验证。
