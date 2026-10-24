# 连续时间马尔可夫决策过程：CTMDP 与 Uniformization

## 摘要

连续时间马尔可夫决策过程，简称 CTMDP，用转移速率而不是固定步长转移概率描述随机系统。系统在状态中停留一段随机时间，再发生跳变；动作同时影响停留时间、下一状态分布和收益率。Uniformization，也称一致化或均匀化，通过选择一个支配所有退出速率的统一泊松速率，把 CTMDP 转换为带虚拟自环的离散时间 MDP，从而复用值迭代、策略迭代、线性规划和仿真工具。

本文介绍 CTMDP 的生成元、停留时间、跳链、折扣与平均回报最优性方程、uniformization 的严格构造、奖励和折扣换算、有限时域泊松展开、策略语义、数值算法、仿真验证，以及它们在 5v5、战棋和战略游戏中的应用边界。

## 一、为什么需要连续时间模型

普通离散时间 MDP 假设所有决策都发生在统一步长上。但许多游戏和控制过程具有异步事件：

- 不同技能的冷却和施法时间不同；
- 单位移动、攻击、受伤和增援在不同时刻发生；
- 城池失守、补给到达和外交事件没有统一回合边界；
- 某些状态只持续很短时间，另一些状态可能长时间不变。

若强行使用很小固定步长，会产生大量无事件步骤；步长过大又会掩盖事件顺序。CTMDP 直接用事件速率描述时间。

## 二、有限 CTMDP

一个有限、时间齐次 CTMDP 可写为：

$$\mathcal C=(\mathcal S,\{\mathcal A(s)\}_{s\in\mathcal S},q,r,\mu_0)$$

其中：

- $\mathcal S$ 是有限状态集合；
- $\mathcal A(s)$ 是状态 $s$ 的合法动作集合；
- $q(j\mid s,a)$ 是从状态 $s$ 跳到状态 $j$ 的转移速率；
- $r(s,a)$ 是单位时间收益率；
- $\mu_0$ 是初始状态分布。

对 $j\ne s$，要求：

$$q(j\mid s,a)\ge0$$

状态 $s$ 的退出速率为：

$$\lambda(s,a)=\sum_{j\ne s}q(j\mid s,a)$$

生成元的对角项定义为：

$$q(s\mid s,a)=-\lambda(s,a)$$

因此每一行满足：

$$\sum_j q(j\mid s,a)=0$$

这里 $q$ 的单位是每单位时间的事件率，不是一步转移概率。

## 三、停留时间与嵌入跳链

在状态 $s$ 选择动作 $a$ 后，若 $\lambda(s,a)>0$，停留时间 $\tau$ 服从指数分布：

$$\Pr(\tau>t\mid s,a)=\exp[-\lambda(s,a)t]$$

其期望为：

$$\mathbb E[\tau\mid s,a]=\frac{1}{\lambda(s,a)}$$

条件于发生真实跳变，下一状态分布为：

$$p(j\mid s,a,\mathrm{jump})=\frac{q(j\mid s,a)}{\lambda(s,a)},\quad j\ne s$$

因此 CTMDP 同时包含两个部分：动作控制等待多久，以及事件发生后跳到哪里。只保留嵌入跳链会丢失停留时间信息，也会错误计算单位时间收益。

若 $\lambda(s,a)=0$，在该动作下状态是吸收的。此时不存在上述跳链分母，应单独处理。

## 四、策略语义

平稳确定性 Markov 策略写成：

$$a=\pi(s)$$

平稳随机策略写成：

$$\pi(a\mid s)=\Pr(a_t=a\mid X_t=s)$$

连续时间控制还必须明确动作何时允许改变。常见语义包括：

- 只在真实状态跳变时选择动作，并保持到下一次真实跳变；
- 在任意时刻根据当前状态重新选择动作；
- 在外部决策时钟到达时重新选择动作；
- 使用依赖停留时间或完整历史的策略。

Uniformization 是否保持策略等价，取决于采用哪一种语义。文档和实现必须显式声明决策时机。

## 五、固定策略下的生成元

对确定性策略 $\pi$，诱导生成元为：

$$Q^\pi_{sj}=q(j\mid s,\pi(s))$$

对平稳随机策略，可按动作概率混合：

$$Q^\pi_{sj}=\sum_a\pi(a\mid s)q(j\mid s,a)$$

状态分布行向量 $p(t)$ 满足 Kolmogorov 前向方程：

$$\frac{d}{dt}p(t)=p(t)Q^\pi$$

初始分布为 $p(0)=\mu_0$ 时：

$$p(t)=\mu_0\exp(tQ^\pi)$$

生成元矩阵指数描述固定策略下任意时间点的状态分布。

## 六、连续时间折扣回报

设连续时间折扣率为 $\alpha>0$。策略价值定义为：

$$V^\pi(s)=\mathbb E_s^\pi\left[\int_0^\infty e^{-\alpha t}r(X_t,A_t)\,dt\right]$$

对固定平稳策略，价值满足：

$$\alpha V^\pi=r^\pi+Q^\pi V^\pi$$

因此：

$$V^\pi=(\alpha I-Q^\pi)^{-1}r^\pi$$

有限状态、有限速率且 $\alpha>0$ 时，该线性系统通常良定义。数值实现仍应检查矩阵条件数和方程残差。

## 七、折扣最优性方程

收益最大化 CTMDP 的 Hamilton-Jacobi-Bellman 方程为：

$$\alpha V(s)=\max_{a\in\mathcal A(s)}\left[r(s,a)+\sum_j q(j\mid s,a)V(j)\right]$$

利用对角项可改写为：

$$V(s)=\max_a\frac{r(s,a)+\sum_{j\ne s}q(j\mid s,a)V(j)}{\alpha+\lambda(s,a)}$$

第二种形式直接反映等待时间折扣与下一真实跳变，但其分母依赖动作。Uniformization 会把所有动作转换到统一事件速率。

## 八、Uniformization 的构造

### 8.1 选择统一速率

选择常数 $\Lambda$，满足：

$$\Lambda\ge\max_{s,a}\lambda(s,a)$$

对有限状态和有限动作、且退出速率有界的模型，总能选择有限 $\Lambda$。若退出速率无界，全局 uniformization 可能不可用，需要截断、状态依赖一致化或其他方法。

### 8.2 构造离散转移核

对 $j\ne s$，定义：

$$P_\Lambda(j\mid s,a)=\frac{q(j\mid s,a)}{\Lambda}$$

自环概率为：

$$P_\Lambda(s\mid s,a)=1-\frac{\lambda(s,a)}{\Lambda}$$

因为 $\Lambda$ 支配所有退出速率，所有概率均非负，并满足：

$$\sum_jP_\Lambda(j\mid s,a)=1$$

矩阵形式为：

$$P_\Lambda^a=I+\frac{Q^a}{\Lambda}$$

统一速率 $\Lambda$ 的泊松时钟每次响起时，系统根据 $P_\Lambda$ 更新。若抽到自环，则这是一个虚拟事件，物理状态没有发生真实跳变。

## 九、为什么虚拟自环是必要的

原模型中不同状态—动作对具有不同退出速率。Uniformization 使用更快的统一泊松时钟，再以自环补足差额：

$$\Lambda-\lambda(s,a)$$

是真实事件之外的虚拟事件率。真实跳往 $j$ 的总速率仍为：

$$\Lambda P_\Lambda(j\mid s,a)=q(j\mid s,a)$$

因此虚拟事件不会改变连续时间状态过程的真实跳变速率。删除自环会把所有状态的退出速率错误地改成 $\Lambda$。

## 十、折扣率和奖励的换算

设 uniformization 事件间隔 $T$ 服从参数为 $\Lambda$ 的指数分布。连续折扣在一个事件间隔后的期望因子为：

$$\beta=\mathbb E[e^{-\alpha T}]=\frac{\Lambda}{\Lambda+\alpha}$$

在一个事件间隔内，以速率 $r(s,a)$ 累积收益，其期望折扣收益为：

$$\bar r(s,a)=\mathbb E\left[\int_0^T e^{-\alpha t}r(s,a)\,dt\right]=\frac{r(s,a)}{\Lambda+\alpha}$$

因此 uniformized 离散 MDP 的 Bellman 方程为：

$$V(s)=\max_a\left[\bar r(s,a)+\beta\sum_jP_\Lambda(j\mid s,a)V(j)\right]$$

代入 $\bar r$、$\beta$ 和 $P_\Lambda$ 后，正好恢复连续时间方程：

$$\alpha V(s)=\max_a\left[r(s,a)+\sum_jq(j\mid s,a)V(j)\right]$$

不能仅把 $q/\Lambda$ 当作转移概率，却继续沿用原来的每步奖励和离散折扣因子。这样会改变价值尺度和最优策略。

## 十一、带跳变奖励的模型

除单位时间收益率 $r(s,a)$ 外，若从 $s$ 跳到 $j$ 时还获得一次性奖励 $g(s,a,j)$，其期望奖励率贡献为：

$$r_{\mathrm{jump}}(s,a)=\sum_{j\ne s}q(j\mid s,a)g(s,a,j)$$

可以把总有效收益率写成：

$$r_{\mathrm{eff}}(s,a)=r(s,a)+r_{\mathrm{jump}}(s,a)$$

再代入折扣 HJB 与 uniformization。若跳变奖励与事件时刻、目标状态或控制切换有更复杂关系，应从原始随机积分重新推导，不能机械并入收益率。

## 十二、固定策略的 Uniformization

对固定策略 $\pi$，令：

$$P_\Lambda^\pi=I+\frac{Q^\pi}{\Lambda}$$

连续时间转移矩阵可以展开为泊松混合：

$$\exp(tQ^\pi)=e^{-\Lambda t}\sum_{n=0}^{\infty}\frac{(\Lambda t)^n}{n!}(P_\Lambda^\pi)^n$$

该公式的含义是：时间区间 $[0,t]$ 内 uniformization 时钟的事件数服从均值为 $\Lambda t$ 的泊松分布；条件于事件数为 $n$，状态按离散核 $P_\Lambda^\pi$ 演化 $n$ 步。

这为瞬态概率、有限时域收益和仿真提供了稳定计算方法。

## 十三、泊松级数截断

实际计算只能保留有限项。若截断到 $N$，遗漏概率质量为：

$$\varepsilon_N=\Pr\left(\operatorname{Poisson}(\Lambda t)>N\right)$$

选择 $N$ 使：

$$\varepsilon_N\le\varepsilon$$

即可控制由于泊松尾截断引入的概率误差。对有界函数 $f$，截断误差还可以用尾概率乘以函数范围进行界定。

$\Lambda t$ 很大时，应使用稳定的泊松概率递推、分段时间推进或专门数值库，避免直接计算阶乘和高次幂。

## 十四、折扣值迭代

Uniformization 后可直接执行离散值迭代：

$$V_{k+1}(s)=\max_a\left[\frac{r(s,a)}{\Lambda+\alpha}+\frac{\Lambda}{\Lambda+\alpha}\sum_jP_\Lambda(j\mid s,a)V_k(j)\right]$$

因为：

$$0<\beta=\frac{\Lambda}{\Lambda+\alpha}<1$$

Bellman 算子在无穷范数下是 $\beta$ 收缩。可以报告 Bellman 残差：

$$\delta_k=\|\mathcal TV_k-V_k\|_\infty$$

当 $\Lambda$ 远大于实际退出速率时，$\beta$ 非常接近一且自环概率很大，值迭代会变慢。因此应选择刚好足以支配速率并留有数值容差的 $\Lambda$，而不是任意取极大值。

## 十五、策略迭代

给定策略 $\pi_k$，先求解：

$$\alpha V^{\pi_k}=r^{\pi_k}+Q^{\pi_k}V^{\pi_k}$$

再逐状态改进：

$$\pi_{k+1}(s)\in\arg\max_a\left[r(s,a)+\sum_jq(j\mid s,a)V^{\pi_k}(j)\right]$$

也可以在 uniformized 离散模型上执行完全等价的策略评估和改进。破同分规则应固定，否则策略可能在等价值动作间反复切换。

## 十六、平均回报 CTMDP

长期平均收益率定义为：

$$\rho^\pi(s)=\liminf_{T\rightarrow\infty}\frac{1}{T}\mathbb E_s^\pi\left[\int_0^T r(X_t,A_t)\,dt\right]$$

在适当的不可约、遍历或单链条件下，最优增益 $\rho$ 和偏置函数 $h$ 满足：

$$\rho=\max_a\left[r(s,a)+\sum_jq(j\mid s,a)h(j)\right]$$

偏置只在加常数意义下确定，可固定：

$$h(s_{\mathrm{ref}})=0$$

uniformized 离散模型使用每个泊松步奖励：

$$\bar r_{\mathrm{avg}}(s,a)=\frac{r(s,a)}{\Lambda}$$

若离散模型的最优平均每步收益为 $g$，则连续时间平均收益率为：

$$\rho=\Lambda g$$

缺少单链或遍历条件时，平均收益可能依赖初始状态，不能直接套用单一标量 $\rho$ 的方程。

## 十七、有限时域 CTMDP

设终止时刻为 $T$，终端收益为 $g(s)$。令 $V(t,s)$ 表示时刻 $t$ 的最优剩余价值，则后向方程为：

$$-\frac{\partial V(t,s)}{\partial t}=\max_a\left[r(t,s,a)+\sum_jq(j\mid t,s,a)V(t,j)\right]$$

终端条件为：

$$V(T,s)=g(s)$$

有限时域策略通常依赖剩余时间。即使模型时间齐次，最优策略也未必平稳。Uniformization 后可以结合泊松事件数和时间状态做动态规划，但不能简单把无限时域平稳策略当作有限时域最优策略。

## 十八、策略等价与虚拟事件陷阱

如果原 CTMDP 允许控制器持续观察当前状态并在 uniformization 时钟上重新选择动作，那么虚拟自环处重新决策可以与该控制语义一致。

如果原模型规定动作只能在真实跳变时选择并保持到下一个真实跳变，则虚拟事件不应提供新的动作选择机会。可采用以下处理：

- 在扩展状态中保存当前承诺动作；
- 虚拟自环时强制继续原动作；
- 只在真实跳变标记出现时开放决策；
- 使用与跳变时刻控制语义匹配的半马尔可夫模型。

忽略这一点会扩大策略集合，使 uniformized 模型获得原系统不存在的控制能力。

## 十九、非爆炸性

一个过程若能在有限时间内发生无限次真实跳变，就称为爆炸。有限状态且退出速率统一有界时：

$$\sup_{s,a}\lambda(s,a)<\infty$$

全局 uniformization 提供一个支配泊松过程，从而排除有限时间内无限事件。

对可数无限状态或无界速率模型，必须另行证明非爆炸性。仅仅写出生成元并不保证过程合法。

## 二十、Uniformization 与时间离散化的区别

固定小步长 Euler 离散常写为：

$$P_{\Delta t}\approx I+Q\Delta t$$

为保证非负概率，需要 $\Delta t$ 足够小，并存在离散化误差。Uniformization 选择：

$$\Delta t\ \mathrm{不是固定时间步，而是均值为}\ 1/\Lambda\ \mathrm{的随机事件间隔}$$

对时间齐次有限 CTMC，完整泊松级数是精确表示；误差只来自数值截断。两者不能混为同一种近似。

## 二十一、仿真方法

### 21.1 直接事件仿真

在状态 $s$ 选择动作 $a$：

1. 采样 $\tau\sim\operatorname{Exp}(\lambda(s,a))$；
2. 在停留期间累计收益；
3. 按 $q(j\mid s,a)/\lambda(s,a)$ 采样真实下一状态；
4. 到达新状态后重新决策。

### 21.2 Uniformization 仿真

1. 采样统一事件间隔 $T\sim\operatorname{Exp}(\Lambda)$；
2. 按 $P_\Lambda(\cdot\mid s,a)$ 采样下一状态；
3. 若状态不变，则记录虚拟事件；
4. 按既定策略语义决定是否允许重新选动作。

两种仿真在策略语义一致时，应产生相同的真实状态过程统计。可以用停留时间分布、状态占有率和累计收益进行交叉验证。

## 二十二、5v5 游戏应用

### 22.1 状态与事件率

宏观状态可以包含地图阶段、人数差、关键技能状态、资源目标和队伍阵型。动作是推进、撤退、集结、分推或争夺目标。转移率可描述：

- 遭遇团战的到达率；
- 击杀、阵亡和撤退事件率；
- 防御塔或中立目标被攻破的速率；
- 增援到达和技能恢复的速率。

事件率必须从明确规则、计时器或回放统计估计，并按版本和段位分层校准。不能把离散发生概率直接当作连续时间速率。

### 22.2 收益率

单位时间收益可表示经济增长、地图控制和生存优势；击杀、失塔等离散事件可作为跳变奖励。Uniformization 后，可使用统一离散规划器比较不同宏策略，同时保持真实事件时间尺度。

## 二十三、战棋与战略游戏应用

传统回合制战棋不一定需要 CTMDP。但若模型包含连续到达的增援、补给中断、疾病、叛乱、外交事件或围城失守，就可以用事件率描述异步演化。

战略层的状态可包含城池控制、兵力区间、粮草和联盟结构；动作包括驻防、进军、征粮、谈判和封锁。平均回报适合长期边境治理，有限时域模型适合指定日期前的战役目标。

## 二十四、参数估计

若在状态—动作对 $(s,a)$ 下观察总暴露时间 $T_{s,a}$ 和跳往 $j$ 的次数 $N_{saj}$，齐次泊松假设下的速率极大似然估计为：

$$\widehat q(j\mid s,a)=\frac{N_{saj}}{T_{s,a}},\quad j\ne s$$

退出速率估计为：

$$\widehat\lambda(s,a)=\frac{\sum_{j\ne s}N_{saj}}{T_{s,a}}$$

需要同时报告暴露时间、事件计数和置信区间。罕见状态的点估计可能极不稳定，可以使用分层模型、Gamma 先验或状态聚合，但不能虚构未观察到的事件。

## 二十五、数值验证

### 25.1 生成元检查

- 非对角速率非负；
- 对角项等于负退出速率；
- 每行和为零；
- 所有合法状态—动作对速率有限；
- 吸收状态单独处理。

### 25.2 Uniformization 检查

- $\Lambda$ 不小于任何退出速率；
- $P_\Lambda$ 每个元素非负；
- 每行概率和为一；
- 由 $\Lambda(P_\Lambda-I)$ 恢复原生成元；
- 自环概率与速率差一致；
- 不同可行 $\Lambda$ 下的连续时间价值和策略一致。

### 25.3 价值检查

- CTMDP HJB 残差低于容差；
- uniformized Bellman 残差低于容差；
- 两种方程得到的价值一致；
- 固定策略线性系统与蒙特卡洛估计相容；
- 泊松尾截断质量低于目标误差；
- 平均回报模型明确验证单链或遍历条件。

## 二十六、常见误区

第一，速率不是概率。$q(j\mid s,a)$ 可以大于一，其单位是每单位时间事件数。

第二，只把速率除以 $\Lambda$ 还不够，必须加入虚拟自环，使转移概率归一化并保持真实退出速率。

第三，连续时间折扣率 $\alpha$ 不能直接当作离散折扣因子。uniformized 折扣应为 $\Lambda/(\Lambda+\alpha)$。

第四，单位时间收益率不能原样作为每个 uniformization 步的奖励。折扣问题中的一步收益是 $r/(\Lambda+\alpha)$，平均回报问题中常用 $r/\Lambda$。

第五，$\Lambda$ 不是越大越好。过大的 $\Lambda$ 会造成大量虚拟自环，并使离散折扣因子接近一，降低迭代效率。

第六，在虚拟事件处重新选择动作可能改变策略空间。必须匹配原 CTMDP 的动作承诺和决策时机。

第七，有限时域最优策略一般依赖时间，不能直接复用无限时域平稳策略。

第八，平均回报方程需要结构条件。多链模型中，单一增益和偏置方程可能不足。

## 二十七、结论

CTMDP 用生成元和指数停留时间刻画异步随机事件，能够同时描述动作对事件频率、跳转方向和单位时间收益的影响。Uniformization 选择统一泊松速率，通过虚拟自环构造离散转移核；正确换算奖励和折扣后，离散 Bellman 方程与连续时间 HJB 完全一致。

在工程应用中，应明确动作何时可改变、收益是速率还是跳变奖励、目标是折扣还是平均回报，并验证非爆炸性、生成元合法性、uniformization 概率核、Bellman 残差和泊松截断误差。Uniformization 的价值不是粗略时间离散，而是在适用条件下把连续时间问题精确映射到成熟的离散 MDP 工具链。

## 参考文献

1. Guo, X. and Hernandez-Lerma, O. Continuous-Time Markov Decision Processes.
2. Puterman, M. L. Markov Decision Processes: Discrete Stochastic Dynamic Programming.
3. Serfozo, R. F. An Equivalence Between Continuous and Discrete Time Markov Decision Processes.
4. Lippman, S. A. Applying a New Device in the Optimization of Exponential Queuing Systems.
5. Jensen, A. Markoff Chains as an Aid in the Study of Markoff Processes.
6. Norris, J. R. Markov Chains.
7. Ross, S. M. Introduction to Probability Models.
