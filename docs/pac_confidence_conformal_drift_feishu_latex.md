# 有限样本可信决策：PAC-MDP、PAC-Bayes、Empirical Bernstein、Anytime Confidence Sequence 与共形风险控制

## 摘要

强化学习和游戏策略评估不能只报告训练均值或单次胜率。PAC-MDP 研究在线学习算法需要多少次非近优决策；PAC-Bayes 用先验、后验与 KL 复杂度控制策略分布的样本外风险；Empirical Bernstein 界根据实际样本方差收紧固定样本置信区间；Anytime Confidence Sequence 在持续监控和可选停止下保持覆盖；Conformal Risk Control 将共形校准从集合覆盖扩展到一般有界损失；加权共形预测则在协变量漂移下利用密度比恢复目标分布覆盖。

本文给出六类方法的数学定义、典型界、成立假设、算法流程、诊断方法，以及它们在 5v5、战棋和策略模型中的使用边界。所有有限样本保证都必须连同概率空间、数据依赖、损失范围和漂移假设解释。

## 一、概率保证的基本语言

设数据为：

$$D_n=(Z_1,\ldots,Z_n)$$

模型或策略由数据生成，记为：

$$\widehat\pi=\mathcal A(D_n)$$

一个典型的 PAC 陈述是：以至少 $1-\delta$ 的概率，输出对象的误差不超过 $\varepsilon$：

$$\Pr\left(\mathcal E(\widehat\pi)>\varepsilon\right)\le\delta$$

$\varepsilon$ 控制精度，$\delta$ 控制保证失败概率。这个概率通常针对训练数据、环境随机性或算法随机性，而不是说每一条未来轨迹都安全。

## 二、MDP 与价值差

有限折扣 MDP 写成：

$$\mathcal M=(\mathcal S,\mathcal A,P,r,\gamma)$$

策略价值为：

$$V^\pi(s)=\mathbb E_s^\pi\left[\sum_{t=0}^{\infty}\gamma^t r(s_t,a_t)\right]$$

最优价值为：

$$V^\star(s)=\sup_\pi V^\pi(s)$$

策略在状态 $s$ 的次优差距为：

$$\Delta^\pi(s)=V^\star(s)-V^\pi(s)$$

如果奖励位于 $[0,1]$，价值范围满足：

$$0\le V^\pi(s)\le\frac{1}{1-\gamma}$$

因此折扣因子接近一时，微小模型误差也可能被长时域放大。

## 三、PAC-MDP 的定义

PAC-MDP 关注在线算法在交互过程中有多少时刻采取明显非近优策略。令学习算法在时刻 $t$ 的当前策略为 $\pi_t$，访问状态为 $s_t$。定义坏时刻：

$$V^{\pi_t}(s_t)<V^\star(s_t)-\varepsilon$$

坏时刻总数为：

$$N_\varepsilon=\sum_{t=0}^{\infty}\mathbf 1\left\{V^{\pi_t}(s_t)\lt V^\star(s_t)-\varepsilon\right\}$$

若存在关于以下量的多项式 $p$：

$$|\mathcal S|,\ |\mathcal A|,\ \frac{1}{\varepsilon},\ \frac{1}{\delta},\ \frac{1}{1-\gamma}$$

使得：

$$\Pr\left(N_\varepsilon\le p\right)\ge1-\delta$$

则算法具有 PAC-MDP 样本复杂度保证。

PAC-MDP 限制的是非近优时间步数量，不等同于累计遗憾界，也不直接等同于最后输出策略的离线泛化界。

## 四、PAC-MDP 的典型机制

### 4.1 乐观面对不确定性

模型型算法维护转移和奖励估计，并构造置信集合：

$$\mathcal M_t=\left\{M:\left|r_M(s,a)-\widehat r_t(s,a)\right|\le b^r_t(s,a),\ \left\|P_M(\cdot\mid s,a)-\widehat P_t(\cdot\mid s,a)\right\|_1\le b^P_t(s,a)\right\}$$

选择置信集合中价值最乐观的模型和策略：

$$\widetilde M_t,\pi_t\in\arg\max_{M\in\mathcal M_t,\pi}V_M^\pi(s_t)$$

乐观性使算法主动访问仍可能有高价值的未知状态—动作对。

### 4.2 已知与未知状态—动作对

令访问次数为 $N_t(s,a)$。当：

$$N_t(s,a)\ge m_{\mathrm{known}}$$

就把该状态—动作对视为已充分估计。PAC-MDP 证明通常把误差分成：

- 当前处于已知区域时，模型误差足够小；
- 当前进入未知区域时，访问会增加并最终减少不确定性；
- 未知区域能被访问的总次数受到计数上界控制。

### 4.3 模拟引理

若两个 MDP 的奖励和转移核接近，则固定策略价值也接近。一个典型量级为：

$$\left\|V_M^\pi-V_{\widehat M}^\pi\right\|_\infty\lesssim\frac{\varepsilon_r}{1-\gamma}+\frac{\gamma\varepsilon_P}{(1-\gamma)^2}$$

常数依赖奖励范围和所用转移距离。该式用于说明为什么高折扣问题需要更精确的模型估计。

## 五、PAC-MDP 与其他指标

PAC-MDP、遗憾和 best-policy identification 回答不同问题。

累计遗憾为：

$$\operatorname{Regret}(T)=\sum_{t=0}^{T-1}\left[V^\star(s_t)-V^{\pi_t}(s_t)\right]$$

PAC-MDP 允许少量任意大的坏时刻，并控制其数量；遗憾界累加所有时间步的性能差。一个算法可能具有好的 PAC-MDP 界，但有限时域遗憾常数仍较大。

纯探索方法则希望用有限数据输出策略 $\widehat\pi$，满足：

$$V^{\widehat\pi}(s_0)\ge V^\star(s_0)-\varepsilon$$

其概率至少为 $1-\delta$。这又不同于在线交互期间的 PAC-MDP 保证。

## 六、PAC-Bayes 的策略分布视角

设策略类为 $\Pi$。在观察数据之前选择先验分布 $P$，观察数据后得到后验分布 $Q$。PAC-Bayes 评估 Gibbs 策略：先从 $Q$ 抽取策略 $\pi$，再执行该策略。

对有界损失 $\ell(\pi,Z)\in[0,1]$，真实风险为：

$$L(Q)=\mathbb E_{\pi\sim Q}\mathbb E_{Z\sim\mathcal D}[\ell(\pi,Z)]$$

经验风险为：

$$\widehat L_n(Q)=\mathbb E_{\pi\sim Q}\left[\frac{1}{n}\sum_{i=1}^n\ell(\pi,Z_i)\right]$$

后验相对先验的复杂度由 KL 散度衡量：

$$\operatorname{KL}(Q\|P)=\mathbb E_{\pi\sim Q}\left[\log\frac{dQ}{dP}(\pi)\right]$$

若 $Q$ 把质量集中到先验认为极不可能的策略上，复杂度惩罚会变大。

## 七、PAC-Bayes kl 界

定义 Bernoulli 相对熵：

$$\operatorname{kl}(\widehat p\|p)=\widehat p\log\frac{\widehat p}{p}+(1-\widehat p)\log\frac{1-\widehat p}{1-p}$$

对独立同分布样本和数据独立先验，一类经典 PAC-Bayes 界说明：以至少 $1-\delta$ 的概率，对所有后验 $Q$ 同时有：

$$\operatorname{kl}\left(\widehat L_n(Q)\|L(Q)\right)\le\frac{\operatorname{KL}(Q\|P)+\log(2\sqrt n/\delta)}{n}$$

通过数值反演二元 kl，可以得到 $L(Q)$ 的上界。一个较宽松但直观的平方根形式为：

$$L(Q)\le\widehat L_n(Q)+\sqrt{\frac{\operatorname{KL}(Q\|P)+\log(2\sqrt n/\delta)}{2n}}$$

不同 PAC-Bayes 定理的常数、损失条件和先验要求不同。正式报告应注明使用的具体版本，而不是混合多篇定理的常数。

## 八、PAC-Bayes 策略后验

一种常见后验形式是 Gibbs 后验：

$$Q_\eta(d\pi)=\frac{\exp[-\eta n\widehat L_n(\pi)]P(d\pi)}{\int\exp[-\eta n\widehat L_n(\bar\pi)]P(d\bar\pi)}$$

$\eta>0$ 控制经验性能与先验复杂度之间的权衡。$\eta$ 很大时，后验更集中于低经验损失策略，也可能增大 KL 项。

在游戏策略评估中，$Q$ 可以表示：

- 不同策略网络检查点的分布；
- 策略库上的混合权重；
- 参数空间中的随机后验；
- 不同战术模板的 Gibbs 分布。

分布上的保证不自动转化为后验均值参数或单一 MAP 策略的保证。若部署时只选一个策略，需要单独分析或验证。

## 九、PAC-Bayes 在强化学习中的限制

经典界通常假设 $Z_i$ 独立同分布。强化学习轨迹具有时间依赖，同一策略生成的数据还可能依赖环境初始状态和策略本身。

可采用以下方式满足或替代假设：

- 把独立重置的完整 episode 视为样本；
- 使用独立环境种子和初始状态；
- 对 Markov 依赖使用专门的 PAC-Bayes 或混合过程界；
- 对在线数据使用 martingale PAC-Bayes；
- 对离线策略评估使用有界重要权重或稳健估计。

若策略使用生成该数据的同一回放进行选择，不能再把该回放当成独立测试集。

## 十、Empirical Bernstein 界

Hoeffding 界只使用变量范围。Empirical Bernstein 界还利用样本方差，在观测波动较小时可以更紧。

设独立样本 $X_i\in[0,1]$，样本均值为：

$$\bar X_n=\frac{1}{n}\sum_{i=1}^nX_i$$

无偏样本方差为：

$$S_n^2=\frac{1}{n-1}\sum_{i=1}^n(X_i-\bar X_n)^2$$

对 $n\ge2$，一个常用的单侧经验 Bernstein 界为：以至少 $1-\delta$ 的概率，

$$\mathbb E[X]\le\bar X_n+\sqrt{\frac{2S_n^2\log(2/\delta)}{n}}+\frac{7\log(2/\delta)}{3(n-1)}$$

若原变量位于 $[a,b]$，可先归一化到 $[0,1]$，或把右侧误差项乘以范围 $b-a$。

## 十一、Empirical Bernstein 的解释

当样本方差接近零时，平方根项显著缩小，但线性修正项仍防止小样本下过度自信。当方差较大时，该界可能与 Hoeffding 界相当甚至更宽。

用同一批数据在大量策略、指标和切片中挑选最优者后，不能对最终选中项继续使用未经校正的单个置信界。应使用联合界、数据拆分、PAC-Bayes 或其他选择后有效方法。

对 Bernoulli 胜负数据，精确二项区间、Wilson 区间或 beta-binomial 模型有时更合适。Empirical Bernstein 的优势在于能处理一般有界回报。

## 十二、固定时刻置信区间的陷阱

固定样本量区间保证：

$$\Pr(\mu\in C_n)\ge1-\delta$$

它不自动保证：

$$\Pr(\mu\in C_t\ \mathrm{for\ all}\ t)\ge1-\delta$$

如果每看一次数据就计算一个 95% 区间，并在首次显著时停止，整体误覆盖概率会超过 5%。持续监控需要 Anytime Confidence Sequence 或显式 alpha-spending。

## 十三、Anytime Confidence Sequence

置信序列是一组随时间更新的集合 $C_t$，满足：

$$\Pr\left(\forall t\ge1:\mu\in C_t\right)\ge1-\delta$$

因此对任意停时 $\tau$：

$$\Pr(\mu\in C_\tau)\ge1-\delta$$

这里停时可以由此前观测决定，例如“当新策略胜率下界超过旧策略时停止测试”。

## 十四、一个简单的 Anytime 构造

设 $X_t\in[0,1]$ 独立且均值为常数 $\mu$。给每个时间点分配：

$$\delta_t=\frac{6\delta}{\pi^2t^2}$$

因为：

$$\sum_{t=1}^{\infty}\delta_t=\delta$$

在每个时刻使用 Hoeffding 半径：

$$r_t=\sqrt{\frac{\log(2/\delta_t)}{2t}}$$

并定义：

$$C_t=[\bar X_t-r_t,\bar X_t+r_t]\cap[0,1]$$

由并合界可得同时覆盖。这个构造简单但较保守；mixture boundary、stitching 和 empirical-Bernstein confidence sequence 通常更紧。

## 十五、E-process 与 Ville 不等式

在零假设下，若非负过程 $E_t$ 满足：

$$\mathbb E[E_t\mid\mathcal F_{t-1}]\le E_{t-1}$$

且 $E_0=1$，则它是一个 e-process 或非负超鞅。Ville 不等式给出：

$$\Pr\left(\sup_{t\ge0}E_t\ge\frac{1}{\delta}\right)\le\delta$$

因此可以在任意时刻观察 $E_t$，并在 $E_t\ge1/\delta$ 时拒绝零假设，而不因可选停止破坏一类错误控制。

对条件次高斯增量 $X_t-\mu$，固定 $\lambda$ 的指数超鞅可写为：

$$M_t(\lambda)=\exp\left[\lambda\sum_{i=1}^t(X_i-\mu)-\frac{\lambda^2\sigma^2t}{2}\right]$$

对 $\lambda$ 做混合或分段优化，可以反演得到置信序列。

## 十六、Confidence Sequence 的适用边界

Anytime-valid 不代表可以任意改变数据生成机制。保证依赖以下条件之一：

- 条件均值稳定；
- martingale difference 条件成立；
- 使用的方差代理有效；
- 自适应分配概率已进入估计量；
- 缺失、延迟和删失机制已正确处理。

若游戏版本、匹配池或玩家分布发生变化，常数均值置信序列可能失去目标意义。此时应转向变化检测、分段模型或漂移鲁棒推断。

## 十七、Conformal Risk Control

普通共形预测常控制预测集合误覆盖率。Conformal Risk Control，简称 CRC，把目标扩展到一般有界损失。

设预测对象族为 $C_\lambda(x)$，参数 $\lambda$ 越大时集合通常越保守。定义损失：

$$\ell_i(\lambda)=\ell(Y_i,C_\lambda(X_i))$$

并假设：

$$0\le\ell_i(\lambda)\le B$$

经验风险为：

$$\widehat R_n(\lambda)=\frac{1}{n}\sum_{i=1}^n\ell_i(\lambda)$$

在交换性和损失随 $\lambda$ 单调不增等条件下，可选择：

$$\widehat\lambda=\inf\left\{\lambda:\frac{n}{n+1}\widehat R_n(\lambda)+\frac{B}{n+1}\le\alpha\right\}$$

相应程序可控制新样本的边际期望风险：

$$\mathbb E[\ell_{n+1}(\widehat\lambda)]\le\alpha$$

## 十八、CRC 能控制哪些损失

CRC 不限于零一误覆盖损失。只要损失有界并满足相应单调结构，可以考虑：

- 预测集合未覆盖关键敌情的损失；
- 集合过大带来的行动成本；
- 多标签漏检比例；
- 超过安全阈值的截断损失；
- 分组加权的关键目标漏报；
- 风险集合与真实危险区域的不匹配。

边际期望风险保证不是“每个状态、每个英雄或每个群体都满足风险上限”。若需要组条件或状态条件保证，必须为相关切片提供足够校准数据并使用相应方法。

## 十九、高概率风险控制

若希望以概率至少 $1-\delta$ 保证真实风险不超过 $\alpha$，可以为每个 $\lambda$ 构造风险上置信界 $U_n(\lambda,\delta)$，并选择：

$$\widehat\lambda=\inf\{\lambda:U_n(\lambda,\delta)\le\alpha\}$$

这类方法常称为 risk-controlling prediction sets。若同时搜索多个 $\lambda$，上置信界必须对选择过程有效，例如使用单调性、统一界、校准拆分或多重检验校正。

不能把 CRC 的期望风险保证和高概率风险上界混写成同一个结论。

## 二十、共形预测的交换性基础

设校准分数为：

$$S_i=S(X_i,Y_i)$$

在校准样本和测试样本交换时，测试分数的秩近似均匀。Split conformal 使用有限样本修正后的分位数：

$$k=\left\lceil(n+1)(1-\alpha)\right\rceil$$

并取第 $k$ 个校准分数作为阈值；若 $k>n$，阈值取正无穷，从而返回保守全集。

普通交换性在明显分布漂移下不成立。加权共形针对的是特定漂移结构，而不是任意变化。

## 二十一、协变量漂移

设校准分布为 $P$，目标测试分布为 $Q$。协变量漂移假设为：

$$P(Y\mid X)=Q(Y\mid X)$$

但边缘特征分布可以不同：

$$P_X\ne Q_X$$

定义密度比：

$$w(x)=\frac{dQ_X}{dP_X}(x)$$

只要 $Q_X$ 对 $P_X$ 绝对连续，且密度比可用，就可以通过加权校准让训练域样本代表目标域。

如果条件分布 $Y\mid X$ 也发生变化，仅估计 $w(x)$ 不能恢复覆盖保证。

## 二十二、加权共形分位数

对测试特征 $x$，校准权重和测试权重为：

$$w_i=w(X_i),\quad w_{n+1}=w(x)$$

归一化权重为：

$$p_i(x)=\frac{w_i}{\sum_{j=1}^nw_j+w_{n+1}}$$

测试点权重为：

$$p_{n+1}(x)=\frac{w_{n+1}}{\sum_{j=1}^nw_j+w_{n+1}}$$

构造带权离散分布：

$$\sum_{i=1}^np_i(x)\delta_{S_i}+p_{n+1}(x)\delta_{\infty}$$

令 $q_{1-\alpha}^w(x)$ 为该分布的 $1-\alpha$ 分位数，则预测集合为：

$$C(x)=\{y:S(x,y)\le q_{1-\alpha}^w(x)\}$$

正无穷原子是有限样本修正的一部分。当测试点权重很大时，集合可能变得非常保守甚至成为全集，这正确反映了目标点在校准数据中缺乏支持。

## 二十三、密度比估计

密度比可以通过概率分类估计。把校准域标记为 $D=0$，目标域标记为 $D=1$。若分类器给出：

$$\eta(x)=\Pr(D=1\mid X=x)$$

设两个域在分类训练样本中的先验比例为：

$$\pi_D=\Pr(D=1)$$

则密度比为：

$$w(x)=\frac{\eta(x)}{1-\eta(x)}\frac{1-\pi_D}{\pi_D}$$

分类器需要概率校准。过拟合分类器会产生极端权重，使有效样本量下降并导致预测集合不稳定。

## 二十四、权重诊断与裁剪

加权样本的有效样本量为：

$$\operatorname{ESS}=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}$$

应报告最大权重、权重分位数、ESS 和目标样本在校准支持中的位置。

权重裁剪可写为：

$$\widetilde w_i=\min(w_i,w_{\max})$$

裁剪能降低方差，但改变了目标分布，一般会引入偏差并失去原始精确覆盖结论。应把它作为偏差—方差折中，并通过敏感性分析报告。

## 二十五、时间漂移与在线加权

若较新的校准样本更接近当前测试分布，可使用时间衰减权重：

$$w_i=\exp[-\lambda(t_{\mathrm{now}}-t_i)]$$

这种启发式权重不自动等于真实密度比，因此通常没有协变量漂移下的精确有限样本保证。

更可靠的流程是：

1. 定义目标时间窗和目标分布；
2. 使用特征区分历史窗与目标窗；
3. 估计并校准密度比；
4. 检查条件分布稳定性；
5. 使用加权共形；
6. 持续监控覆盖并在变化点后重新校准。

Adaptive conformal 可以在线调整名义误覆盖率，但它的长期平均性质和静态交换性覆盖保证不同，不能混为一谈。

## 二十六、六类方法的关系

| 方法 | 核心对象 | 典型保证 | 主要限制 |
|---|---|---|---|
| PAC-MDP | 在线探索策略 | 非近优时间步数量 | 有限 MDP、模型与算法假设 |
| PAC-Bayes | 策略后验分布 | 样本外平均风险 | 先验、数据依赖与损失条件 |
| Empirical Bernstein | 固定样本均值 | 方差自适应置信界 | 固定时刻、多重选择问题 |
| Confidence Sequence | 序贯均值或参数 | 所有时刻同时覆盖 | 条件均值与鞅假设 |
| Conformal Risk Control | 预测集合族 | 边际期望或高概率风险 | 交换性、单调性、损失有界 |
| 加权共形 | 漂移下预测集合 | 协变量漂移目标覆盖 | 密度比与条件分布稳定 |

这些方法可以组合，但保证不会自动叠加。例如，用置信序列选择停止时间后再用未经序贯校正的 PAC-Bayes 测试集，会重新引入选择偏差。

## 二十七、5v5 游戏应用

### 27.1 PAC-MDP

在小型抽象宏观状态上，PAC-MDP 可以评估探索算法需要多少次明显次优团战或目标决策，才会掌握转移和收益。真实大型游戏不满足小型表格假设时，不能直接引用多项式样本复杂度。

### 27.2 PAC-Bayes

把多个策略检查点、阵容策略或战术模板组成先验和后验。使用独立对局估计 Gibbs 策略的失败率，并用 KL 项惩罚过度集中于少量训练胜者。

### 27.3 Confidence Sequence

持续 A/B 测试新策略时，可以随对局到达更新胜率差置信序列，在下界超过零时停止，而不破坏预设错误率。

### 27.4 共形方法

为敌方位置、伤害或团战结果构造预测集合，并用 CRC 控制漏掉危险状态的平均损失。版本、段位或匹配池变化时，可在协变量漂移假设近似成立的情况下使用加权共形。

## 二十八、战棋与战略游戏应用

PAC-MDP 适合小规模敌情与资源状态抽象；PAC-Bayes 可对不同战役策略库建立复杂度感知的泛化界；Empirical Bernstein 可给伤亡和补给均值提供方差自适应上界；Confidence Sequence 可持续监控新章节或新 AI 的失败率。

CRC 可控制“真实敌军行动不在候选集合中”的平均代价，加权共形可适配不同章节、地图或难度导致的特征分布变化。若历史规律本身改变，例如同一特征下敌方策略发生变化，则需要变化检测和重新校准。

## 二十九、统一验证流程

### 29.1 数据审计

- 明确训练、校准、验证和测试数据的边界；
- 记录 episode、玩家、地图、版本和随机种子；
- 检查样本独立单位是帧、回合还是完整对局；
- 防止同一轨迹片段跨数据集泄漏；
- 说明自适应收集和停止规则。

### 29.2 PAC-MDP

- 明确状态和动作是否有限；
- 验证奖励范围和折扣因子；
- 记录访问计数与置信半径；
- 在小模型上比较真实最优价值；
- 统计非近优时间步，而不仅是最终胜率；
- 不把函数逼近实验冒充表格 PAC 定理。

### 29.3 PAC-Bayes

- 先验必须在查看评估数据前确定，或使用合法的数据依赖先验定理；
- 报告经验风险、KL、样本量和 $\delta$；
- 对 kl 界执行数值反演而不是随意使用正态近似；
- 区分 Gibbs 策略与单一部署策略；
- 使用独立 episode 或满足所用依赖界的样本。

### 29.4 置信界与置信序列

- 固定时刻界不得用于反复查看后的可选停止；
- Confidence Sequence 记录每一步边界和停时；
- 检查收益范围或方差代理；
- 多指标监控需要联合错误控制；
- 漂移后重新定义估计目标。

### 29.5 共形与漂移

- 校准分数与模型训练数据分离；
- 检查损失有界和单调性；
- 区分边际风险、条件风险和高概率风险；
- 验证密度比分类器校准；
- 报告权重 ESS 和极端权重；
- 检查 $P(Y\mid X)=Q(Y\mid X)$ 是否合理；
- 在目标时间段做独立覆盖回测。

## 三十、常见误区

第一，PAC 不表示 probably always correct。它是在明确概率空间中，以高概率给出近似正确结论。

第二，PAC-MDP 的样本复杂度不是训练需要的固定 episode 数，也不是任意神经强化学习算法的自动保证。

第三，PAC-Bayes 约束的是后验分布的 Gibbs 风险，不自动约束后验均值参数或挑出的单一策略。

第四，Empirical Bernstein 是固定样本界。持续查看并按结果停止需要 Confidence Sequence。

第五，Anytime-valid 允许可选停止，但不允许无视环境分布变化或任意篡改估计量。

第六，CRC 的边际期望风险不等于每个状态的条件风险，也不等于逐轨迹硬安全。

第七，加权共形只在明确的漂移结构下恢复保证。若 $Y\mid X$ 改变，仅重加权 $X$ 不足。

第八，估计密度比和裁剪权重会引入额外误差。使用估计权重时应把精确保证改写为近似或稳健结论。

第九，同一数据同时用于模型选择、停止、校准和最终报告，会破坏多数标准有限样本结论。

## 三十一、结论

PAC-MDP 从在线探索角度限制明显次优决策的数量；PAC-Bayes 通过策略后验相对先验的 KL 复杂度控制样本外风险；Empirical Bernstein 使用观测方差收紧固定时刻均值界；Anytime Confidence Sequence 在持续监控和可选停止下保持同时覆盖；Conformal Risk Control 把共形校准扩展到一般有界风险；加权共形预测在协变量漂移且密度比可靠时适配目标分布。

在实际游戏模型中，应先确定需要的是探索效率、策略泛化、固定样本评估、持续监控、预测风险还是漂移覆盖，再选择相应工具。最终报告必须同时给出假设、样本单位、置信参数、选择过程、权重诊断和独立验证结果，不能只展示一个看似严格的上界。

## 参考文献

1. Kearns, M. and Singh, S. Near-Optimal Reinforcement Learning in Polynomial Time.
2. Strehl, A. L., Li, L. and Littman, M. L. Reinforcement Learning in Finite MDPs: PAC Analysis.
3. McAllester, D. A. Some PAC-Bayesian Theorems.
4. Seeger, M. PAC-Bayesian Generalisation Error Bounds for Gaussian Process Classification.
5. Maurer, A. A Note on the PAC Bayesian Theorem.
6. Maurer, A. and Pontil, M. Empirical Bernstein Bounds and Sample Variance Penalization.
7. Howard, S. R., Ramdas, A., McAuliffe, J. and Sekhon, J. Time-Uniform, Nonparametric, Nonasymptotic Confidence Sequences.
8. Angelopoulos, A. N., Bates, S., Jordan, M. I. and Malik, J. Conformal Risk Control.
9. Bates, S., Angelopoulos, A. N., Lei, L., Malik, J. and Jordan, M. I. Distribution-Free, Risk-Controlling Prediction Sets.
10. Tibshirani, R. J., Barber, R. F., Candes, E. J. and Ramdas, A. Conformal Prediction Under Covariate Shift.
