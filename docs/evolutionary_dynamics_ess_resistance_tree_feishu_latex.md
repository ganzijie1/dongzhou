# Replicator Dynamics、Logit Dynamics、ESS、Mutation–Selection 与 Resistance Tree

## 摘要

演化博弈研究策略如何在选择、学习、试错和突变作用下改变。Replicator Dynamics 让收益高于群体平均值的策略扩大份额；Logit Dynamics 用带噪最佳回应描述有限理性和随机探索；Evolutionarily Stable Strategy（ESS）要求一个常驻策略不仅是对称 Nash 均衡，还能抵抗少量突变者入侵；Mutation–Selection Dynamics 同时刻画收益选择和策略创新；Resistance Tree 则利用小噪声 Markov 链的最小阻力生成树，识别长期随机稳定状态。

这五类工具处于不同层级。Replicator 和 mutation–selection 通常是总体份额的确定性动力系统；logit 可表示总体平滑回应，也可表示有限玩家异步更新；ESS 是静态抗入侵概念；resistance tree 分析有限状态随机过程在噪声趋零时的平稳分布。它们可以连接，但不能不加条件地互相替代。

本文从对称矩阵博弈和策略单纯形出发，系统介绍复制子方程、对数比率、势函数、离散复制子、多群体扩展、logit response、QRE、log-linear learning、ESS 判据、复制子–突变方程、准物种、有限群体随机漂变、正则扰动、Markov Chain Tree Theorem、随机势与最小阻力树，并给出在 5v5 游戏阵容、出装、分路和版本生态中的建模方法。

## 一、策略总体

设有 $n$ 个纯策略，群体状态为：

$$x=(x_1,\ldots,x_n)\in\Delta_n$$

其中单纯形为：

$$\Delta_n=\left\{x\in\mathbb R_+^n:\sum_{i=1}^n x_i=1\right\}$$

$x_i$ 表示采用策略 $i$ 的群体比例。动力学必须保持非负性和总量为一。

## 二、对称矩阵博弈

收益矩阵记为：

$$A\in\mathbb R^{n\times n}$$

策略 $i$ 面对群体状态 $x$ 的期望收益为：

$$u_i(x)=(Ax)_i$$

群体平均收益为：

$$\bar u(x)=x^{\mathsf T}Ax=\sum_i x_i u_i(x)$$

收益可以表示繁殖率、学习成功率、策略采用者增长率或多局比赛中的相对表现。

## 三、Replicator Dynamics

连续时间复制子方程为：

$$\dot x_i=x_i\left[u_i(x)-\bar u(x)\right]$$

高于平均收益的策略份额增加，低于平均收益的策略份额减少。增长率满足：

$$\frac{\dot x_i}{x_i}=u_i(x)-\bar u(x)$$

复制子动力学比较的是相对收益，而不是收益的绝对大小。

## 四、单纯形不变性

总份额的导数为：

$$\sum_i\dot x_i=\sum_i x_i u_i(x)-\bar u(x)\sum_i x_i=0$$

因此：

$$\sum_i x_i(t)=1$$

若初始状态 $x_i(0)\geq0$，则 $x_i(t)\geq0$。若某策略初始份额为零：

$$x_i(0)=0\quad\Longrightarrow\quad x_i(t)=0$$

标准复制子动力学无法自行创造完全缺失的策略。

## 五、对数份额比

对两个正份额策略 $i$ 和 $j$：

$$\frac{d}{dt}\log\frac{x_i}{x_j}=u_i(x)-u_j(x)$$

因此累计收益差决定相对份额：

$$\frac{x_i(t)}{x_j(t)}=\frac{x_i(0)}{x_j(0)}\exp\left[\int_0^t(u_i(x_s)-u_j(x_s))ds\right]$$

该公式把复制子动力学与指数权重、乘法权重更新联系起来。

## 六、收益变换

若所有策略同时增加同一状态相关常数 $c(x)$：

$$u_i'(x)=u_i(x)+c(x)$$

则：

$$u_i'(x)-\bar u'(x)=u_i(x)-\bar u(x)$$

连续复制子轨迹不变。若把全部收益乘以正数，只会改变时间尺度。

## 七、静止点

复制子静止点满足：

$$x_i\left[u_i(x)-\bar u(x)\right]=0,\qquad i=1,\ldots,n$$

因此所有正份额策略必须具有相同收益：

$$x_i\gt0\quad\Longrightarrow\quad u_i(x)=\bar u(x)$$

但静止点不一定是 Nash 均衡，因为零份额策略可能具有更高收益，却无法从边界自行出现。

## 八、Nash 均衡与复制子静止点

对称 Nash 均衡 $x^{\star}$ 满足：

$$y^{\mathsf T}Ax^{\star}\leq {x^{\star}}^{\mathsf T}Ax^{\star},\qquad \forall y\in\Delta_n$$

每个对称 Nash 均衡都是复制子静止点。反向命题一般不成立。

如果内部静止点满足所有纯策略收益相同，它是候选 Nash 均衡；还需检查边界和不可行方向上的最佳回应条件。

## 九、线性稳定性

令复制子向量场为：

$$F_i(x)=x_i\left[(Ax)_i-x^{\mathsf T}Ax\right]$$

在静止点 $x^{\star}$ 附近线性化：

$$\dot \xi=DF(x^{\star})\xi$$

稳定性只需在单纯形切空间：

$$T\Delta_n=\left\{\xi:\sum_i\xi_i=0\right\}$$

上分析。若相关特征值实部均为负，则该静止点局部渐近稳定。

## 十、对称势与平均收益

若 $A=A^{\mathsf T}$，平均收益沿复制子轨迹满足：

$$\frac{d}{dt}\left(x^{\mathsf T}Ax\right)=2\sum_i x_i\left[(Ax)_i-x^{\mathsf T}Ax\right]^2\geq0$$

因此平均收益是 Lyapunov 函数。该结论依赖矩阵对称性；一般非对称对称博弈中，平均收益不一定单调增加。

这也是“自然选择总会提高平均适应度”需要附加条件的原因。

## 十一、势博弈中的复制子动力学

若存在光滑势函数 $\Phi(x)$，使收益差与势梯度差一致，则复制子动力学可写成 Shahshahani 几何下的梯度流：

$$\dot x_i=x_i\left[\frac{\partial\Phi}{\partial x_i}-\sum_jx_j\frac{\partial\Phi}{\partial x_j}\right]$$

沿轨迹：

$$\frac{d\Phi}{dt}=\sum_i x_i\left(\frac{\partial\Phi}{\partial x_i}-\sum_jx_j\frac{\partial\Phi}{\partial x_j}\right)^2\geq0$$

势函数把长期收敛与局部极值联系起来。

## 十二、零和博弈与循环

在反对称零和结构中，复制子动力学可能围绕内部 Nash 均衡循环，而不收敛。例如 Rock–Paper–Scissors 可出现闭轨或异宿循环。

若内部均衡为 $x^{\star}$，某些零和模型具有守恒量：

$$D_{\mathrm{KL}}(x^{\star}\|x)=\sum_i x_i^{\star}\log\frac{x_i^{\star}}{x_i}$$

因此时间平均可能收敛到均衡，但瞬时策略份额持续振荡。

## 十三、离散时间复制子

常见离散更新为：

$$x_i^{+}=\frac{x_i f_i(x)}{\sum_jx_j f_j(x)}$$

要求适应度 $f_i(x)$ 非负且分母为正。若原始收益可能为负，可使用正的适应度映射：

$$f_i(x)=e^{\eta u_i(x)}$$

离散复制子对收益平移的性质与连续模型不同，步长过大也可能导致振荡或复杂动力学。

## 十四、多群体复制子

设玩家群体或角色类型为 $p=1,\ldots,P$，群体 $p$ 的策略份额为 $x^p$。动力学为：

$$\dot x_i^p=x_i^p\left[u_i^p(x^1,\ldots,x^P)-\bar u^p(x)\right]$$

其中：

$$\bar u^p(x)=\sum_i x_i^p u_i^p(x)$$

多群体模型适合刻画不同位置、阵营、职业或生态物种的策略演化。

## 十五、复制子与在线学习

连续时间指数权重满足：

$$x_i(t)=\frac{x_i(0)\exp\left(\eta\int_0^tu_i(x_s)ds\right)}{\sum_jx_j(0)\exp\left(\eta\int_0^tu_j(x_s)ds\right)}$$

对时间求导可得到复制子形式：

$$\dot x_i=\eta x_i(u_i-\bar u)$$

因此复制子动力学也可解释为群体中的 multiplicative weights 或 entropy mirror descent。

## 十六、Logit Response

给定收益向量 $u(x)$，logit 回应为：

$$L_i^{\beta}(x)=\frac{\exp\{\beta u_i(x)\}}{\sum_j\exp\{\beta u_j(x)\}}$$

$\beta\geq0$ 是逆温度。$\beta=0$ 时均匀随机；$\beta\rightarrow\infty$ 时质量集中于最佳回应。

温度常记为：

$$\tau=\frac{1}{\beta}$$

温度越高，选择越分散。

## 十七、连续时间 Logit Dynamics

平滑最佳回应动力学可写为：

$$\dot x_i=L_i^{\beta}(x)-x_i$$

它表示个体以单位修正率重新选择策略，新选择服从 logit 回应。

与复制子不同，即使 $x_i=0$，只要温度有限：

$$L_i^{\beta}(x)\gt0$$

策略 $i$ 也会重新出现，因此 logit dynamics 通常保持内部状态。

## 十八、Logit Equilibrium 与 QRE

logit dynamics 的静止点满足：

$$x_i^{\star}=L_i^{\beta}(x^{\star})$$

这就是 logit quantal response equilibrium 的固定点条件。有限 $\beta$ 下，低收益动作仍有正概率。

当 $\beta\rightarrow\infty$ 时，QRE 的极限点通常是 Nash 均衡候选，但不同延拓分支可能趋向不同均衡，且会发生分岔。

## 十九、熵正则化解释

logit 回应是以下问题的解：

$$L^{\beta}(x)\in\operatorname*{arg\,max}_{y\in\Delta_n}\left\{y^{\mathsf T}u(x)+\frac{1}{\beta}H(y)\right\}$$

其中熵为：

$$H(y)=-\sum_i y_i\log y_i$$

熵项奖励混合与探索。$\beta$ 增大时，收益项相对更重要。

## 二十、有限玩家 Logit Dynamics

在有限玩家博弈中，可随机选择一个玩家 $k$ 更新动作。给定其他玩家动作 $a_{-k}$，其选择 $b$ 的概率为：

$$\mathbb P(a_k^{+}=b\mid a_{-k})=\frac{\exp\{\beta u_k(b,a_{-k})\}}{\sum_{c\in A_k}\exp\{\beta u_k(c,a_{-k})\}}$$

这形成有限状态、通常不可约的 Markov 链。它与连续总体 logit ODE 有关，但不是同一个对象。

## 二十一、Log-Linear Learning

异步 logit 更新也称 log-linear learning。若每次只有一个玩家更新，且更新机会覆盖全部玩家，则有限温度下通常存在唯一平稳分布。

在 exact potential game 中，若势函数为 $\Phi(a)$，平稳分布为 Gibbs 形式：

$$\mu_{\beta}(a)=\frac{\exp\{\beta\Phi(a)\}}{\sum_{a'}\exp\{\beta\Phi(a')\}}$$

当 $\beta\rightarrow\infty$ 时，平稳质量集中于全局势最大状态，而不只是任意局部 Nash 均衡。

## 二十二、Replicator 与 Logit 的区别

Replicator 使用相对收益驱动已有策略的增长，边界面不变；logit 使用带噪最佳回应，有限温度下会重新引入零份额策略。

复制子方程为：

$$\dot x_i=x_i(u_i-\bar u)$$

logit 方程为：

$$\dot x_i=L_i^{\beta}(x)-x_i$$

前者强调选择复制，后者强调个体修正和有限理性。二者的稳定点和长期分布通常不同。

## 二十三、ESS 的定义

策略 $x^{\star}$ 是 Evolutionarily Stable Strategy，若对所有充分接近且不同于 $x^{\star}$ 的突变策略 $y$，存在足够小的 $\varepsilon\gt0$，使：

$$u\left(x^{\star},(1-\varepsilon)x^{\star}+\varepsilon y\right)\gt u\left(y,(1-\varepsilon)x^{\star}+\varepsilon y\right)$$

其中：

$$u(x,y)=x^{\mathsf T}Ay$$

该不等式表示少量突变者进入后，常驻策略仍有更高适应度。

## 二十四、ESS 的两阶段判据

对称矩阵博弈中，$x^{\star}$ 为 ESS，当且仅当对所有 $y\neq x^{\star}$：

$$u(x^{\star},x^{\star})\geq u(y,x^{\star})$$

并且在第一项取等时：

$$u(x^{\star},y)\gt u(y,y)$$

第一条件说明 $x^{\star}$ 是对称 Nash 均衡；第二条件在突变者面对常驻者不吃亏时，要求常驻者在突变群体中表现更好。

## 二十五、严格 Nash 与 ESS

若纯策略 $i$ 是严格对称 Nash 均衡：

$$A_{ii}\gt A_{ji},\qquad \forall j\neq i$$

则 $e_i$ 是 ESS。反之，ESS 不一定是严格 Nash，因为混合 ESS 可以依靠第二阶段条件抵抗入侵。

Nash 均衡只要求单个偏离者没有更高收益；ESS 还比较突变者与自身相遇时的表现。

## 二十六、混合 ESS

若 $x^{\star}$ 是内部 ESS，则其支持中的纯策略收益相同：

$$Ax^{\star}=\bar u(x^{\star})\mathbf 1$$

但收益相同只给出 Nash 候选。还需验证二阶侵入条件。

对所有满足 $\mathbf 1^{\mathsf T}z=0$ 的非零切向扰动，常见充分条件为：

$$z^{\mathsf T}Az\lt0$$

在相应支撑子空间上，这表示均衡附近的突变混合受到严格抑制。

## 二十七、ESS 与复制子稳定性

对称博弈中的 ESS 通常是复制子动力学的局部渐近稳定状态，并可使用：

$$V(x)=D_{\mathrm{KL}}(x^{\star}\|x)$$

作为局部 Lyapunov 函数。沿轨迹：

$$\dot V(x)=-\left[u(x^{\star},x)-u(x,x)\right]$$

在 ESS 邻域内右侧为负。

反向关系需要额外条件；复制子局部稳定、Nash 稳定和 ESS 不能在所有博弈中无条件视为同义词。

## 二十八、ESS 与有限群体

ESS 是无限群体、稀有突变极限中的抗入侵概念。在有限群体中，即使突变策略期望收益较低，也可能因随机漂变固定。

有限群体更常分析固定概率：

$$\rho_{i\rightarrow j}=\mathbb P(\text{单个 }j\text{ 突变者最终占据全体}\mid\text{初始常驻 }i)$$

因此有限群体稳定性还依赖群体规模、选择强度和更新规则。

## 二十九、Mutation–Selection Dynamics

令 $Q_{ji}$ 表示策略 $j$ 的后代或学习更新变成策略 $i$ 的概率：

$$Q_{ji}\geq0,\qquad \sum_iQ_{ji}=1$$

复制子–突变方程为：

$$\dot x_i=\sum_jx_j f_j(x)Q_{ji}-x_i\bar f(x)$$

其中：

$$\bar f(x)=\sum_jx_j f_j(x)$$

第一项包含选择后的复制和突变流入，第二项保持总份额归一化。

## 三十、均匀突变模型

一种常见参数化为：

$$Q=(1-\mu)I+\mu M$$

$\mu\in[0,1]$ 是突变率，$M$ 是行随机矩阵。$\mu=0$ 时恢复标准复制子；$\mu\gt0$ 且 $M$ 不可约时，边界通常不再不变。

突变使消失策略重新出现，并将边界均衡推向单纯形内部。

## 三十一、选择–突变平衡

平衡状态满足：

$$\sum_jx_j^{\star}f_j(x^{\star})Q_{ji}=x_i^{\star}\bar f(x^{\star})$$

高收益策略得到选择放大，突变则把质量扩散到其他策略。平衡不是简单的最大收益策略，而是适应度与可达突变网络的共同结果。

当 $\mu\rightarrow0$ 时，极限可能选择某些 Nash 或演化稳定状态，但选择结果取决于动力学和突变结构。

## 三十二、常适应度与 Perron–Frobenius

若适应度 $f_j\gt0$ 与群体状态无关，定义：

$$B_{ij}=f_jQ_{ji}$$

平衡满足特征向量方程：

$$Bx^{\star}=\bar f^{\star}x^{\star}$$

若 $B$ 不可约且非负，Perron–Frobenius 定理给出唯一正的主特征向量，归一化后得到 mutation–selection 平衡。

## 三十三、Quasispecies 与误差阈值

在序列复制模型中，高适应度主序列周围会形成突变云，称为 quasispecies。主序列的长期占比取决于复制优势和复制保真度。

当突变率增大时，群体可能从集中于主序列转向分散分布。这类误差阈值在有限维平滑模型中可能表现为快速交叉，而不一定是真正的相变。

## 三十四、突变与 Logit 噪声

Mutation–selection 和 logit 都可使零份额策略重新出现，但机制不同：

- mutation–selection 在复制过程中通过 $Q$ 产生策略转换；
- logit dynamics 在决策修正时按平滑最佳回应重新选择；
- uniform exploration 通常与收益无关；
- logit exploration 仍偏向高收益动作。

相同的内部平衡分布不代表两种微观机制相同，政策含义和瞬态响应也可能不同。

## 三十五、有限群体出生–死亡过程

设群体大小为 $N$，策略 $i$ 的个体数为 $n_i$。Moran 型过程中，每步选择一个个体繁殖、一个个体死亡，并允许突变。

状态空间为：

$$\mathcal X_N=\left\{n\in\mathbb Z_+^n:\sum_i n_i=N\right\}$$

当 $N$ 很大且噪声适当缩放时，其平均场极限可接近 replicator–mutator ODE；有限 $N$ 下仍存在随机漂变和稀有跃迁。

## 三十六、正则扰动 Markov 链

设无扰动链为 $P^0$，带小噪声参数 $\varepsilon$ 的链为 $P^{\varepsilon}$。正则扰动通常要求：

1. 每个 $\varepsilon\gt0$ 时链不可约；
2. $P^{\varepsilon}\rightarrow P^0$；
3. 正概率转移具有幂阶：

$$0\lt\lim_{\varepsilon\rightarrow0}\frac{P^{\varepsilon}(x,y)}{\varepsilon^{r(x,y)}}\lt\infty$$

$r(x,y)\geq0$ 称为从 $x$ 到 $y$ 的 resistance。

## 三十七、Resistance 的含义

阻力衡量低噪声下某次转移需要多少“不利偏差”或错误。若：

$$P^{\varepsilon}(x,y)\asymp c(x,y)\varepsilon^{r(x,y)}$$

则 $r$ 越大，转移越罕见。

零阻力边描述无扰动最优响应或自然动力学；正阻力边描述错误、实验、突变或暂时接受较低收益。

## 三十八、Log-Linear Learning 的阻力

令：

$$\varepsilon=e^{-\beta}$$

玩家 $k$ 在状态 $a$ 更新为动作 $b$ 的 logit 概率，其低温阻力为：

$$r(a,a')=\max_{c\in A_k}u_k(c,a_{-k})-u_k(b,a_{-k})$$

其中 $a'=(b,a_{-k})$。选择最佳回应时阻力为零；相对最佳收益损失越大，阻力越高。

具体阻力还取决于更新协议、并发规则和噪声参数化。

## 三十九、Markov Chain Tree Theorem

对有限不可约 Markov 链，令 $\mathcal T_z$ 为所有有向生成树，且每个节点沿边最终指向根 $z$。根 $z$ 的树权重为：

$$\tau(z)=\sum_{T\in\mathcal T_z}\prod_{(x\rightarrow y)\in T}P(x,y)$$

平稳分布满足：

$$\mu(z)=\frac{\tau(z)}{\sum_{z'}\tau(z')}$$

该定理把长期平稳概率转化为所有入根生成树的权重之和。

## 四十、Resistance Tree

在小噪声极限中，一棵入根树 $T$ 的总阻力为：

$$R(T)=\sum_{(x\rightarrow y)\in T}r(x,y)$$

状态 $z$ 的 stochastic potential 为：

$$\gamma(z)=\min_{T\in\mathcal T_z}R(T)$$

随机稳定状态是 stochastic potential 最小的状态或无扰动常返类。它们在 $\varepsilon\rightarrow0$ 时保持正的平稳概率。

## 四十一、随机稳定性

若 $\mu^{\varepsilon}$ 是扰动链的唯一平稳分布，则状态 $z$ 随机稳定，当：

$$\liminf_{\varepsilon\rightarrow0}\mu^{\varepsilon}(z)\gt0$$

随机稳定性是长期、小噪声和先取平稳分布后的概念。有限时间内最常见的状态、确定性动力学吸引子和随机稳定状态可能不同。

极限次序很重要：先令时间趋于无穷，再令噪声趋于零。

## 四十二、常返类之间的压缩树

若无扰动链有多个常返类 $C_1,\ldots,C_m$，可先计算从类 $C_i$ 到 $C_j$ 的最小路径阻力：

$$r(C_i,C_j)=\min_{\omega:C_i\leadsto C_j}\sum_{e\in\omega}r(e)$$

再在常返类构成的压缩图上求最小入根树。这样避免在巨大微观状态空间上枚举全部生成树。

进入某个均衡容易并不意味着它随机稳定；还必须比较从其他类进入和从该类逃出的总阻力结构。

## 四十三、势博弈中的随机稳定状态

在 exact potential game 的标准 log-linear learning 下：

$$\mu_{\beta}(a)\propto e^{\beta\Phi(a)}$$

因此低温极限选择：

$$a^{\star}\in\operatorname*{arg\,max}_a\Phi(a)$$

Resistance tree 给出同一结论的路径解释。但在非势博弈、异步规则改变、状态约束或非对称噪声下，随机稳定状态未必最大化一个简单势函数。

## 四十四、数值模拟

复制子和 mutation–selection 可用保持单纯形的积分器。显式 Euler 更新：

$$x_i^{k+1}=x_i^k+\Delta t\,F_i(x^k)$$

在步长过大时可能产生负份额。可使用自适应 ODE 求解器、对数坐标、镜像更新或投影修正。

有限玩家 logit 和 resistance 模型应直接模拟 Markov 链，并区分 burn-in、混合时间和真正的低噪声跃迁时间。

## 四十五、参数估计

若观察群体份额时间序列，可通过：

$$\widehat{\dot x}_i(t)\approx x_i(t)\left[u_i(x_t;\theta)-\bar u(x_t;\theta)\right]$$

估计收益参数。也可使用状态空间模型处理观测噪声。

若观察个体修正动作，logit 参数可由条件选择似然估计：

$$\log L(\beta)=\sum_m\left[\beta u_{a_m}(x_m)-\log\sum_j e^{\beta u_j(x_m)}\right]$$

策略内生匹配、未观测异质性和版本变化会使简单估计产生偏差。

## 四十六、5v5 游戏的元策略总体

可把策略定义为阵容体系、分路方案、资源分配、出装路线或团战协议。版本 $v$ 下的对局收益矩阵为：

$$A_{ij}^{(v)}=\mathbb E[\text{策略 }i\text{ 对策略 }j\text{ 的相对收益}]$$

元策略份额 $x_i$ 可表示玩家、战队或 AI 群体采用该体系的比例。复制子动力学描述高胜率策略在版本生态中的扩张。

## 四十七、角色与多群体模型

不同位置可作为不同群体：

$$x^{\mathrm{top}},x^{\mathrm{jungle}},x^{\mathrm{mid}},x^{\mathrm{carry}},x^{\mathrm{support}}$$

某个位置的策略收益依赖全部位置的联合分布：

$$u_i^p=u_i^p(x^{\mathrm{top}},x^{\mathrm{jungle}},x^{\mathrm{mid}},x^{\mathrm{carry}},x^{\mathrm{support}})$$

这比把五个位置混成单一策略总体更能表达角色互补和阵容协同。

## 四十八、版本、探索与创新

版本改动使收益矩阵随时间变化：

$$A=A(t)$$

Mutation–selection 中的 $Q$ 可表示玩家学习新出装、模仿职业战队或尝试冷门英雄。Logit 温度表示有限理性与探索强度。

版本突变后，旧 ESS 可能失去稳定性；有限突变率可防止生态永久卡在旧边界，但过强探索会稀释高质量策略。

## 四十九、游戏中的 Resistance Tree

把纯策略组合、团队规范或元环境吸引子视为有限状态。无扰动边表示最佳回应和常规模仿，正阻力边表示暂时采用低收益策略、协同试验或罕见创新。

对每个候选元环境计算最小入根树：

$$\gamma(z)=\min_{T\in\mathcal T_z}\sum_{e\in T}r(e)$$

最小 $\gamma(z)$ 的状态是小噪声长期随机稳定候选。它不一定具有最高瞬时胜率，而可能是最容易由其他生态进入、同时最难被协调偏差推翻的规范。

## 五十、结论

Replicator Dynamics 用相对收益解释已有策略份额的选择增长；Logit Dynamics 通过熵正则和随机最佳回应引入有限理性；ESS 检查常驻策略能否抵抗稀有突变；Mutation–Selection 同时描述选择和持续创新；Resistance Tree 则分析有限状态随机演化在小噪声长期极限下选择哪些状态。

五者不能简单混同。ESS 是局部入侵判据，不等于全局吸引子；复制子静止点不一定是 Nash；logit QRE 不等于 ESS；mutation–selection 内部平衡依赖突变网络；随机稳定状态取决于整个状态图的进入和逃逸阻力。

在 5v5 游戏中，可用多群体复制子分析角色元策略，用 logit 表示玩家有限理性，用 ESS 检查阵容体系抗反制能力，用 mutation–selection 模拟版本创新，并用 resistance tree 判断长期可持续的策略规范。模型必须按版本、段位和匹配机制分别校准，并用真实转移路径验证阻力定义。
