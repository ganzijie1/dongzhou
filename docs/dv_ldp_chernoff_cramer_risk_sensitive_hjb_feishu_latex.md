# Donsker–Varadhan 变分公式、大偏差原理、Chernoff–Cramér 理论与 Risk-sensitive HJB

## 摘要

许多概率、学习和控制问题都在研究同一件事：低概率但高损失的事件如何被指数尺度放大，以及为了让这种事件发生，概率分布或系统轨迹必须付出多大“信息代价”。Donsker–Varadhan 变分公式把对数矩母函数写成“期望收益减 KL 散度”的优化；Large Deviation Principle（LDP）用速率函数描述稀有事件概率的指数衰减；Chernoff bound 给出有限样本指数尾界，Cramér transform 给出独立样本均值的大偏差速率；Risk-sensitive HJB 则把指数效用引入动态控制，并产生一个与梯度平方有关的非线性项。

本文统一这些理论的符号、条件、推导和数值方法，并说明它们在 5v5 游戏 AI 的团战风险、灾难事件、策略鲁棒性和安全控制中的应用。所有概率结论都依赖相应的矩存在性、正则性或遍历性条件；有限样本上界不能被当成精确概率，渐近速率也不能替代真实样本校准。

## 一、指数尺度为何重要

设随机损失为 $L$，普通风险中性准则只关注：

$$\mathbb E[L]$$

风险敏感准则关注指数矩：

$$\mathbb E[\exp(\theta L)]$$

其确定性等价值常写为：

$$\rho_\theta(L)=\frac{1}{\theta}\log\mathbb E[\exp(\theta L)]$$

当 $\theta>0$ 且 $L$ 表示损失时，大损失会被指数放大；当 $\theta<0$ 时，准则偏向另一侧尾部。若采用“奖励最大化”而不是“损失最小化”，风险厌恶对应的符号可能相反，必须先声明约定。

若指数矩在零附近有限，则：

$$\rho_\theta(L)=\mathbb E[L]+\frac{\theta}{2}\operatorname{Var}(L)+O(\theta^2)$$

因此小 $\theta$ 下，风险敏感目标近似为均值加方差惩罚，但有限或较大 $\theta$ 时不能只用均值—方差代替。

## 二、相对熵与测度变换

设 $P$ 是参考概率测度，$Q$ 是候选概率测度。若 $Q$ 对 $P$ 绝对连续，记 Radon–Nikodym 导数为：

$$\frac{dQ}{dP}$$

KL 散度定义为：

$$D_{\mathrm{KL}}(Q\Vert P)=\mathbb E_Q\left[\log\frac{dQ}{dP}\right]$$

若 $Q$ 不对 $P$ 绝对连续，则通常约定：

$$D_{\mathrm{KL}}(Q\Vert P)=+\infty$$

相对熵不是对称距离，但它精确量化了把参考分布 $P$ 扭曲成 $Q$ 所需的信息代价。

## 三、Donsker–Varadhan 变分公式

设可测函数 $f$ 满足 $\mathbb E_P[e^f]<\infty$。Donsker–Varadhan 变分公式为：

$$\log\mathbb E_P[e^f]=\sup_{Q\ll P}\left\{\mathbb E_Q[f]-D_{\mathrm{KL}}(Q\Vert P)\right\}$$

左边是对数指数矩，右边是在所有绝对连续的分布上，以期望收益补偿分布偏离成本。这个公式也称 Gibbs 变分原理或相对熵的凸对偶公式。

若把 $f$ 换成 $\theta L$，则：

$$\frac{1}{\theta}\log\mathbb E_P[e^{\theta L}]=\sup_{Q\ll P}\left\{\mathbb E_Q[L]-\frac{1}{\theta}D_{\mathrm{KL}}(Q\Vert P)\right\}$$

该式适用于 $\theta>0$。它说明风险敏感损失等于一个分布鲁棒问题：对手可以改变分布，但要支付 KL 惩罚。

## 四、最优指数倾斜分布

若归一化常数有限，变分问题的最优测度满足：

$$\frac{dQ^*}{dP}=\frac{e^f}{\mathbb E_P[e^f]}$$

对 $f=\theta L$，得到指数倾斜：

$$\frac{dQ_\theta}{dP}=\exp\left(\theta L-\log\mathbb E_P[e^{\theta L}]\right)$$

在 $Q_\theta$ 下，高损失样本获得更大权重。重要性采样、大偏差最可能路径和风险敏感控制都可借助这种倾斜构造。

## 五、DV 公式的基本证明

定义指数倾斜测度 $P_f$：

$$\frac{dP_f}{dP}=\frac{e^f}{\mathbb E_P[e^f]}$$

对任意 $Q\ll P$，相对熵非负给出：

$$D_{\mathrm{KL}}(Q\Vert P_f)\geq0$$

展开可得：

$$D_{\mathrm{KL}}(Q\Vert P_f)=D_{\mathrm{KL}}(Q\Vert P)-\mathbb E_Q[f]+\log\mathbb E_P[e^f]$$

因此：

$$\mathbb E_Q[f]-D_{\mathrm{KL}}(Q\Vert P)\leq\log\mathbb E_P[e^f]$$

取 $Q=P_f$ 时等号成立，从而得到变分公式。

## 六、KL 散度的对偶表达

在适当可积条件下，DV 公式还可重排为：

$$D_{\mathrm{KL}}(Q\Vert P)=\sup_f\left\{\mathbb E_Q[f]-\log\mathbb E_P[e^f]\right\}$$

这给出了从样本估计 KL 散度的判别式思路，也是互信息神经估计、分布鲁棒优化和生成模型中的基础工具。若函数类被限制为 $\mathcal F$，只能得到下界：

$$D_{\mathrm{KL}}(Q\Vert P)\geq\sup_{f\in\mathcal F}\left\{\mathbb E_Q[f]-\log\mathbb E_P[e^f]\right\}$$

函数逼近误差、指数项方差和有限样本偏差必须单独评估。

## 七、大偏差原理的定义

设随机变量族 $Z_n$ 取值于拓扑空间 $\mathcal X$，速度为 $a_n\to\infty$，速率函数为 $I:\mathcal X\to[0,\infty]$。LDP 要求对任意可测集合 $A$，有内外界：

$$-\inf_{x\in A^\circ}I(x)\leq\liminf_{n\to\infty}\frac{1}{a_n}\log\mathbb P(Z_n\in A)$$

$$\limsup_{n\to\infty}\frac{1}{a_n}\log\mathbb P(Z_n\in A)\leq-\inf_{x\in\overline A}I(x)$$

直观上：

$$\mathbb P(Z_n\in A)\asymp\exp\left(-a_n\inf_{x\in A}I(x)\right)$$

符号 $\asymp$ 在这里只表示对数尺度上的渐近等价，不表示普通比值趋于一。

## 八、良速率函数与指数紧性

速率函数满足下半连续性：

$$I(x)\leq\liminf_{k\to\infty}I(x_k)\quad\text{when }x_k\to x$$

若每个次水平集：

$$\{x:I(x)\leq c\}$$

都是紧集，则称 $I$ 为良速率函数。无限维空间中，经常需要指数紧性把局部大偏差界提升为完整 LDP；不能仅凭点态概率近似宣布已证明 LDP。

## 九、Laplace 原理与 Varadhan 引理

Laplace 原理把 LDP 转化为指数积分的极限。对适当连续函数 $h$：

$$\lim_{n\to\infty}\frac{1}{a_n}\log\mathbb E\left[e^{a_n h(Z_n)}\right]=\sup_{x\in\mathcal X}\{h(x)-I(x)\}$$

这就是 Varadhan 型积分引理的核心形式。右侧是收益 $h$ 与大偏差代价 $I$ 的竞争。它与 DV 公式具有相同的熵正则化和凸对偶结构。

## 十、收缩原理

若 $Z_n$ 满足速率函数为 $I$ 的 LDP，且 $Y_n=g(Z_n)$，其中 $g$ 连续，则 $Y_n$ 的速率函数为：

$$J(y)=\inf_{x:g(x)=y}I(x)$$

收缩原理允许先在轨迹、经验分布或高维状态上建立 LDP，再投影到失败率、资源差额或胜率等指标。

## 十一、Sanov 定理

设 $X_1,\ldots,X_n$ 独立同分布于 $P$，经验测度为：

$$\widehat P_n=\frac{1}{n}\sum_{i=1}^n\delta_{X_i}$$

在适当拓扑和正则条件下，$\widehat P_n$ 以速度 $n$ 满足 LDP，速率函数为：

$$I(Q)=D_{\mathrm{KL}}(Q\Vert P)$$

因此某个异常经验分布出现的指数代价就是它相对真实分布的 KL 散度。这是 DV 公式、统计假设检验和分布鲁棒优化之间的重要桥梁。

## 十二、Chernoff bound 的基本推导

对任意随机变量 $X$、阈值 $a$ 和 $\lambda>0$，Markov 不等式给出：

$$\mathbb P(X\geq a)=\mathbb P(e^{\lambda X}\geq e^{\lambda a})\leq e^{-\lambda a}\mathbb E[e^{\lambda X}]$$

对 $\lambda$ 优化得到 Chernoff bound：

$$\mathbb P(X\geq a)\leq\inf_{\lambda>0}\exp\left(-\lambda a+\log\mathbb E[e^{\lambda X}]\right)$$

该界在指数矩有限的范围内成立。若矩母函数不存在，直接套用 Chernoff 方法可能得到无意义结果。

## 十三、累积量生成函数

定义累积量生成函数：

$$\Lambda(\lambda)=\log\mathbb E[e^{\lambda X}]$$

若在零附近可微，则：

$$\Lambda'(0)=\mathbb E[X]$$

$$\Lambda''(0)=\operatorname{Var}(X)$$

在指数倾斜分布下：

$$\Lambda'(\lambda)=\mathbb E_{Q_\lambda}[X]$$

$$\Lambda''(\lambda)=\operatorname{Var}_{Q_\lambda}(X)\geq0$$

所以 $\Lambda$ 是凸函数，斜率选择目标尾部位置，曲率反映倾斜后的方差。

## 十四、Cramér transform

Cramér transform 是 $\Lambda$ 的 Legendre–Fenchel 共轭：

$$I(x)=\sup_{\lambda\in\mathbb R}\{\lambda x-\Lambda(\lambda)\}$$

对右尾，若只允许 $\lambda\geq0$，则得到相应单侧速率。若最优点位于内部且 $\Lambda$ 可微，则：

$$\Lambda'(\lambda^*)=x$$

并且：

$$I(x)=\lambda^*x-\Lambda(\lambda^*)$$

这不是把概率直接取负对数，而是对所有指数倾斜参数做最优选择。

## 十五、Cramér 定理

设 $X_1,X_2,\ldots$ 独立同分布，且累积量生成函数在零的邻域有限。样本均值为：

$$\overline X_n=\frac{1}{n}\sum_{i=1}^nX_i$$

Cramér 定理说明 $\overline X_n$ 以速度 $n$ 满足 LDP，速率函数为：

$$I(x)=\sup_{\lambda\in\mathbb R}\{\lambda x-\Lambda(\lambda)\}$$

对适当右尾集合，可得对数渐近：

$$\lim_{n\to\infty}\frac{1}{n}\log\mathbb P(\overline X_n\geq a)=-\inf_{x\geq a}I(x)$$

Chernoff bound 是有限 $n$ 的上界，Cramér 定理则描述 $n\to\infty$ 时指数衰减率，二者不能直接画等号。

## 十六、Bernoulli 示例

若 $X\sim\operatorname{Bernoulli}(p)$，则：

$$\Lambda(\lambda)=\log(1-p+pe^\lambda)$$

其 Cramér 速率函数为：

$$I(x)=x\log\frac{x}{p}+(1-x)\log\frac{1-x}{1-p}$$

其中 $x\in[0,1]$。这正是两个 Bernoulli 分布之间的 KL 散度：

$$I(x)=D_{\mathrm{KL}}(\operatorname{Bern}(x)\Vert\operatorname{Bern}(p))$$

因此观测到异常成功率 $x$ 的指数代价，是经验参数相对真实参数的信息偏离。

## 十七、Gaussian 示例

若 $X\sim\mathcal N(\mu,\sigma^2)$，则：

$$\Lambda(\lambda)=\mu\lambda+\frac{\sigma^2\lambda^2}{2}$$

Cramér transform 为：

$$I(x)=\frac{(x-\mu)^2}{2\sigma^2}$$

于是对 $a>\mu$：

$$\mathbb P(\overline X_n\geq a)\leq\exp\left(-n\frac{(a-\mu)^2}{2\sigma^2}\right)$$

高斯情形的二次速率函数解释了许多次高斯浓缩界。

## 十八、Gärtner–Ellis 方法

对非独立同分布序列，定义缩放对数矩母函数：

$$\Lambda(\lambda)=\lim_{n\to\infty}\frac{1}{a_n}\log\mathbb E[e^{a_n\langle\lambda,Z_n\rangle}]$$

在存在性、下半连续性、适当光滑性和指数紧性等条件下，可由 Gärtner–Ellis 定理得到候选速率函数：

$$I(x)=\sup_\lambda\{\langle\lambda,x\rangle-\Lambda(\lambda)\}$$

若 $\Lambda$ 不可微或定义域边界不满足本质光滑性，直接做共轭可能只能得到部分上下界，必须检查定理条件。

## 十九、路径空间大偏差

考虑小噪声扩散：

$$dX_t^\varepsilon=b(X_t^\varepsilon)dt+\sqrt\varepsilon\,\sigma(X_t^\varepsilon)dW_t$$

在适当条件下，Freidlin–Wentzell 作用量可写为：

$$S_{0T}(\phi)=\frac{1}{2}\int_0^T\left\|\dot\phi_t-b(\phi_t)\right\|_{a(\phi_t)^{-1}}^2dt$$

其中：

$$a(x)=\sigma(x)\sigma(x)^\top$$

路径概率在对数尺度上满足：

$$\mathbb P(X^\varepsilon\approx\phi)\asymp\exp\left(-\frac{S_{0T}(\phi)}{\varepsilon}\right)$$

最小作用量路径刻画系统从稳定区逃逸到失败区的最可能稀有轨迹。

## 二十、风险敏感随机控制

考虑受控扩散：

$$dX_s=b(X_s,u_s)ds+\sigma(X_s,u_s)dW_s$$

运行损失为 $c(x,u)$，终端损失为 $g(x)$。有限时域风险敏感价值函数定义为：

$$V(t,x)=\inf_u\frac{1}{\theta}\log\mathbb E_{t,x}^u\left[\exp\left(\theta\left(g(X_T)+\int_t^Tc(X_s,u_s)ds\right)\right)\right]$$

本文采用损失最小化且 $\theta>0$ 表示风险厌恶的约定。

## 二十一、指数价值函数与动态规划

定义指数价值函数：

$$\Psi(t,x)=e^{\theta V(t,x)}$$

则：

$$\Psi(t,x)=\inf_u\mathbb E_{t,x}^u\left[\exp\left(\theta\left(g(X_T)+\int_t^Tc(X_s,u_s)ds\right)\right)\right]$$

它满足乘法型动态规划，而普通期望控制满足加法型动态规划。终端条件为：

$$V(T,x)=g(x)$$

$$\Psi(T,x)=e^{\theta g(x)}$$

## 二十二、Risk-sensitive HJB

设受控生成算子为：

$$\mathcal L^u\varphi=b(x,u)^\top\nabla\varphi+\frac{1}{2}\operatorname{tr}\left(a(x,u)\nabla^2\varphi\right)$$

指数价值函数满足：

$$-\partial_t\Psi=\inf_u\left\{\mathcal L^u\Psi+\theta c(x,u)\Psi\right\}$$

令 $V=\theta^{-1}\log\Psi$，可得风险敏感 HJB：

$$-\partial_tV=\inf_u\left\{c+b^\top\nabla V+\frac{1}{2}\operatorname{tr}(a\nabla^2V)+\frac{\theta}{2}\nabla V^\top a\nabla V\right\}$$

相较风险中性 HJB，多出的项为：

$$\frac{\theta}{2}\|\sigma^\top\nabla V\|^2$$

它惩罚价值对噪声方向的高敏感度。

## 二十三、风险中性极限

当 $\theta\to0$ 且可交换极限、微分与期望时：

$$V_\theta(t,x)\to V_0(t,x)$$

风险敏感 HJB 退化为普通 HJB：

$$-\partial_tV_0=\inf_u\left\{c+b^\top\nabla V_0+\frac{1}{2}\operatorname{tr}(a\nabla^2V_0)\right\}$$

因此 $\theta$ 是风险中性控制和尾部敏感控制之间的连续参数，但数值上过大的 $|\theta|$ 会导致指数溢出和估计方差爆炸。

## 二十四、长期平均风险敏感控制

长期平均指数增长率可定义为：

$$\rho(\theta)=\inf_u\limsup_{T\to\infty}\frac{1}{\theta T}\log\mathbb E_x^u\left[\exp\left(\theta\int_0^Tc(X_s,u_s)ds\right)\right]$$

若令正特征函数 $\psi=e^{\theta h}$，相应乘法 Poisson 方程或特征值 HJB 为：

$$\theta\rho\,\psi=\inf_u\left\{\mathcal L^u\psi+\theta c(x,u)\psi\right\}$$

对数变换后得到：

$$\rho=\inf_u\left\{c+b^\top\nabla h+\frac{1}{2}\operatorname{tr}(a\nabla^2h)+\frac{\theta}{2}\nabla h^\top a\nabla h\right\}$$

该结论需要稳定性、遍历性和主特征值存在等条件，不能只凭有限时域方程直接外推。

## 二十五、KL 鲁棒控制解释

DV 公式说明，在固定控制策略下，指数风险可以写成对替代路径分布 $Q$ 的最坏情形优化：

$$\frac{1}{\theta}\log\mathbb E_P[e^{\theta L}]=\sup_{Q\ll P}\left\{\mathbb E_Q[L]-\frac{1}{\theta}D_{\mathrm{KL}}(Q\Vert P)\right\}$$

因此风险敏感控制可解释为控制器与“自然扰动对手”的零和博弈。对手把路径分布推向高损失区域，同时承担 KL 代价。这里的 KL 是路径测度之间的散度，不应未经推导替换成单步转移 KL。

## 二十六、小噪声、HJB 与最小作用量

小噪声大偏差把罕见轨迹概率转化为作用量最小化；动态规划把作用量最小化转化为 Hamilton–Jacobi 方程。若控制形式的作用量为：

$$\dot\phi=b(\phi)+\sigma(\phi)v$$

$$S_{0T}(\phi)=\inf_v\frac{1}{2}\int_0^T\|v_t\|^2dt$$

则到达目标集 $B$ 的最小代价可写为：

$$W(x)=\inf_{T,\phi:\phi_0=x,\phi_T\in B}S_{0T}(\phi)$$

对应的 Hamiltonian 为：

$$H(x,p)=b(x)^\top p+\frac{1}{2}p^\top a(x)p$$

这与风险敏感 HJB 中的梯度二次项具有同一结构来源。

## 二十七、离散时间风险敏感 Bellman 方程

对离散状态动作 MDP，折扣型指数目标并不总能写成普通平稳 Bellman 方程；更自然的是有限时域乘法递推。设：

$$\Psi_T(s)=e^{\theta g(s)}$$

则向后递推为：

$$\Psi_t(s)=\min_a\left\{e^{\theta c_t(s,a)}\sum_{s'}P(s'\mid s,a)\Psi_{t+1}(s')\right\}$$

在对数域中：

$$V_t(s)=\min_a\left\{c_t(s,a)+\frac{1}{\theta}\log\sum_{s'}P(s'\mid s,a)e^{\theta V_{t+1}(s')}\right\}$$

实现时应使用 log-sum-exp 技巧，避免直接计算大指数。

## 二十八、数值计算方法

DV 变分问题可用参数化函数 $f_\omega$ 做随机梯度优化；Cramér transform 可对一维 $\lambda$ 做凸优化；路径大偏差可用最小作用量法、字符串法或射击法；风险敏感 HJB 可用单调有限差分、有限体积、半拉格朗日方法或神经 PDE 方法。

对 Cramér transform，数值目标为：

$$\max_\lambda\;\lambda x-\widehat\Lambda(\lambda)$$

样本估计为：

$$\widehat\Lambda(\lambda)=\log\left(\frac{1}{n}\sum_{i=1}^ne^{\lambda X_i}\right)$$

直接估计极端指数矩可能由极少数样本支配，应配合对数域计算、置信区间、截断敏感性检查和独立回放验证。

## 二十九、重要性采样与最优倾斜

为了估计稀有事件 $A$，可从倾斜分布 $Q$ 采样，并使用似然比：

$$\mathbb P_P(A)=\mathbb E_Q\left[\mathbf1_A\frac{dP}{dQ}\right]$$

若用指数倾斜：

$$\frac{dQ_\lambda}{dP}=e^{\lambda X-\Lambda(\lambda)}$$

则：

$$\mathbb P_P(A)=\mathbb E_{Q_\lambda}\left[\mathbf1_Ae^{-\lambda X+\Lambda(\lambda)}\right]$$

选择使倾斜后均值靠近稀有阈值的 $\lambda$，通常能显著降低方差，但仍需报告有效样本量和权重退化。

## 三十、5v5 游戏中的稀有事件建模

可把以下事件视为高损失稀有事件：关键资源团战团灭、连续控制链导致核心英雄零输出、主宰争夺时同步失误、优势局被翻盘、网络抖动触发集体错误动作。

设一场回放的灾难损失为：

$$L=w_1N_{\mathrm{death}}+w_2R_{\mathrm{lost}}+w_3D_{\mathrm{objective}}+w_4T_{\mathrm{stun}}$$

可用风险敏感指标比较策略：

$$J_\theta(\pi)=\frac{1}{\theta}\log\mathbb E_\pi[e^{\theta L}]$$

它会比平均损失更重视少数灾难回放，但不能代替单独报告胜率、均值、分位数和最坏场景。

## 三十一、团战失败的 Chernoff 监控

设窗口内每场是否出现严重团灭为 $Y_i\in\{0,1\}$，经验比例为：

$$\overline Y_n=\frac{1}{n}\sum_{i=1}^nY_i$$

若基线概率为 $p$ 且近似独立，则对 $a>p$：

$$\mathbb P(\overline Y_n\geq a)\leq\exp\left(-nD_{\mathrm{KL}}(\operatorname{Bern}(a)\Vert\operatorname{Bern}(p))\right)$$

实际回放往往存在版本、段位、阵容和时间相关性，因此应按环境分层，并使用混合过程界、块自助法或序贯检验校准，而不是把独立同分布假设当成事实。

## 三十二、风险敏感战术控制

设状态包含血量、技能冷却、阵型、视野和资源计时，动作是集结、开团、撤退或换资源。连续近似下，可令运行损失包括：

$$c(x,u)=c_{\mathrm{death}}+c_{\mathrm{position}}+c_{\mathrm{objective}}+c_{\mathrm{coordination}}$$

风险敏感 HJB 的二次梯度项会惩罚那些对状态估计噪声极为敏感的决策边界。例如，当“立即开团”只在极窄状态区域内占优时，风险敏感策略可能提前集结或延后进场。

风险参数应通过回放外验证选择，而不应仅凭主观设定：

$$\theta^*=\arg\min_{\theta\in\Theta}\operatorname{ValidationRisk}(\pi_\theta)$$

## 三十三、模型与数据诊断

至少检查以下内容：指数矩是否有限；样本是否存在强依赖和分布漂移；速率函数是否凸且在典型值处为零；数值共轭是否落在矩母函数定义域内；重要性权重是否退化；HJB 离散是否满足稳定性和单调性；策略是否在风险中性极限下恢复基线。

可验证：

$$I(\mathbb E[X])=0$$

以及在光滑严格凸情形下：

$$I''(\mathbb E[X])=\frac{1}{\operatorname{Var}(X)}$$

这些是局部诊断，不是完整正确性证明。

## 三十四、常见误区

第一，把 Chernoff 上界当作真实尾概率。它只保证不超过某个值，界可能很松。

第二，把 $\asymp$ 解释为普通数值近似。LDP 通常只控制对数主阶。

第三，在矩母函数不存在的重尾数据上强行使用 Cramér 理论。此时应考虑次指数尾、正则变化或极值理论。

第四，忽略风险参数和损失/奖励符号。相同 $\theta$ 在不同约定下可能代表相反风险偏好。

第五，把状态边际 KL 当作完整路径测度 KL。动态系统中的熵代价通常需要链式分解。

第六，用训练样本估计极端指数矩后直接部署。指数变换会放大离群点、建模误差和分布漂移。

## 三十五、统一关系图

四组理论可概括为：

$$\text{DV 对偶}\Longrightarrow\text{指数矩与 KL 鲁棒性}$$

$$\text{Chernoff 优化}\Longrightarrow\text{有限样本指数上界}$$

$$\mathrm{Cramer\ transform}\Longrightarrow\mathrm{sample\ mean\ LDP\ rate}$$

$$\text{路径 LDP 与动态规划}\Longrightarrow\text{Risk-sensitive HJB}$$

共同核心是凸对偶：对指数倾斜的收益进行优化，同时支付熵或作用量代价。

## 三十六、实施建议

第一阶段先定义真实业务损失和尾部事件，不要先选公式。第二阶段以风险中性策略、经验分位数和简单浓缩界建立基线。第三阶段估计累积量生成函数与速率函数，并检查定义域和样本稳定性。第四阶段用指数倾斜提高稀有事件仿真效率。第五阶段才训练风险敏感控制器，并对不同 $\theta$ 做消融。第六阶段在版本、段位、阵容和网络条件变化下做外部验证。

最终报告应同时给出：

$$\mathbb E[L],\quad\operatorname{VaR}_\alpha(L),\quad\operatorname{CVaR}_\alpha(L),\quad\rho_\theta(L),\quad\mathbb P(L\geq\ell)$$

任何单一风险指标都不应垄断上线决策。

## 三十七、结论

Donsker–Varadhan 公式把指数风险解释为期望损失与 KL 分布偏离的对抗；LDP 用速率函数揭示稀有事件的指数尺度；Chernoff bound 提供有限样本尾界，Cramér transform 给出独立样本均值的渐近代价；Risk-sensitive HJB 把同一指数结构带入动态控制，并通过梯度平方项惩罚对噪声高度敏感的策略。

这些理论最适合回答“极少发生但代价巨大的失败怎样形成、怎样估计、怎样主动规避”。可靠使用它们的关键不是增加公式数量，而是明确测度、符号、矩存在性、独立性、渐近尺度和动态正则条件，并以真实回放对尾部结论做持续校准。
