# 平均场博弈深化：Master Equation、有限玩家误差与 Mean-field Control

## 摘要

平均场博弈（Mean-field Game，MFG）研究大量弱相互作用理性玩家的 Nash 均衡。典型 MFG 由一个向后的 Hamilton–Jacobi–Bellman 方程和一个向前的 Fokker–Planck 方程耦合而成。Master Equation 进一步把均衡价值写成当前状态与总体分布的函数，从而同时描述所有初始分布、有限玩家修正、共同噪声和均衡稳定性。Mean-field control（MFC）则不是分散玩家的 Nash 问题，而是社会规划者控制整体分布的优化问题；规划者会内生化单个决策对总体分布造成的外部性。

本文统一介绍 MFG PDE 系统、Lions 导数、Master Equation、有限 $N$ 玩家 Nash 系统、近似误差与传播混沌、共同噪声、MFC 的测度空间动态规划和最优性系统，并讨论它们在 5v5 游戏 AI 的大规模单位控制、匹配生态、阵容分布、资源拥塞和群体策略调节中的应用。

为固定符号，本文采用损失最小化，并令个体扩散系数为 $\sqrt{2\nu}$。不同文献若用收益最大化或相反的 Hamiltonian 定义，漂移项和测度导数项的符号会相应变化。

## 一、从有限玩家到平均场

考虑 $N$ 个玩家，玩家 $i$ 的状态为 $X_t^{i,N}$，经验分布为：

$$m_t^N=\frac{1}{N}\sum_{j=1}^N\delta_{X_t^{j,N}}$$

玩家动力学可写为：

$$dX_t^{i,N}=b(X_t^{i,N},m_t^N,\alpha_t^{i,N})dt+\sqrt{2\nu}\,dW_t^i$$

当 $N$ 很大且交互具有交换对称性时，单个玩家对经验分布的影响为 $1/N$ 量级，经验分布可能收敛到确定性或条件随机的极限分布 $m_t$。

## 二、代表性玩家问题

给定一条外生分布流 $(m_t)_{0\leq t\leq T}$，代表性玩家选择控制 $\alpha$，最小化：

$$J(t,x;\alpha,m)=\mathbb E\left[\int_t^Tf(X_s,m_s,\alpha_s)ds+g(X_T,m_T)\right]$$

状态满足：

$$dX_s=b(X_s,m_s,\alpha_s)ds+\sqrt{2\nu}\,dW_s$$

MFG 均衡要求个体控制对给定 $m$ 最优，同时最优控制产生的状态分布仍然等于 $m$。

## 三、Hamiltonian 约定

定义损失最小化 Hamiltonian：

$$H(x,m,p)=\inf_{a\in A}\left\{b(x,m,a)\cdot p+f(x,m,a)\right\}$$

若最优动作唯一，记为：

$$a^*(x,m,p)\in\arg\min_{a\in A}\left\{b(x,m,a)\cdot p+f(x,m,a)\right\}$$

在可微条件下，最优漂移满足：

$$b^*(x,m,p)=D_pH(x,m,p)$$

若文献定义 $H=\sup_a\{-b\cdot p-f\}$，则 $D_pH$ 与最优漂移之间会多一个负号。

## 四、MFG 的 HJB 方程

给定分布流 $m_t$，价值函数 $u(t,x)$ 满足：

$$-\partial_tu(t,x)-\nu\Delta u(t,x)+H(x,m_t,D_xu(t,x))=0$$

终端条件为：

$$u(T,x)=g(x,m_T)$$

最优反馈控制为：

$$\alpha_t^*=a^*(X_t,m_t,D_xu(t,X_t))$$

## 五、Fokker–Planck 方程

在最优反馈下，群体分布满足：

$$\partial_tm_t-\nu\Delta m_t+\operatorname{div}\left(m_tD_pH(x,m_t,D_xu(t,x))\right)=0$$

初始条件为：

$$m_0=\mu_0$$

该方程向前传播分布，而 HJB 从终端条件向后传播价值，因此 MFG 是典型的前向—后向耦合系统。

## 六、MFG 固定点

给定候选分布流 $m$，先解 HJB 得到最优反馈，再用 Fokker–Planck 方程得到新分布流 $\Gamma(m)$。均衡满足：

$$m=\Gamma(m)$$

最简单的 Picard 迭代为：

$$m^{k+1}=\Gamma(m^k)$$

为改善稳定性，可加入松弛：

$$m^{k+1}=(1-\eta_k)m^k+\eta_k\Gamma(m^k)$$

强耦合或多均衡问题中，直接固定点迭代可能振荡或收敛到依赖初值的均衡。

## 七、单调性与唯一性

Lasry–Lions 单调性是 MFG 唯一性和稳定性的常见条件。对耦合函数 $F(x,m)$，典型条件为：

$$\int_{\mathbb R^d}\left(F(x,m)-F(x,m')\right)(m-m')(dx)\geq0$$

终端耦合 $G$ 可采用类似条件。直观上，单调性抑制正反馈拥挤：某处玩家增多时，继续进入该处不会变得更有利。

单调性是充分条件而非必要条件；缺少单调性时可能存在多个均衡、分岔和均衡选择问题。

## 八、分布上的函数导数

设 $V(m)$ 是概率测度上的泛函。线性函数导数可由扰动定义：

$$V(m')-V(m)=\int_0^1\int\frac{\delta V}{\delta m}((1-s)m+sm',y)(m'-m)(dy)ds$$

$\delta V/\delta m$ 只在加上与 $y$ 无关的常数意义下唯一，常用归一化为：

$$\int\frac{\delta V}{\delta m}(m,y)m(dy)=0$$

Lions 导数通常记为：

$$D_mV(m,y)=D_y\frac{\delta V}{\delta m}(m,y)$$

它通过把随机变量分布的泛函提升到 $L^2$ 空间来定义可微性。

## 九、测度链式法则

若 $m_t$ 满足：

$$\partial_tm_t=\nu\Delta m_t-\operatorname{div}(m_tb_t)$$

则在适当光滑和可积条件下：

$$\frac{d}{dt}V(m_t)=\int\frac{\delta V}{\delta m}(m_t,y)\partial_tm_t(dy)$$

积分分部后：

$$\frac{d}{dt}V(m_t)=\int\left[\nu\operatorname{div}_yD_mV(m_t,y)+D_mV(m_t,y)\cdot b_t(y)\right]m_t(dy)$$

Master Equation 和 MFC 的测度空间 HJB 都来自这条链式法则。

## 十、Decoupling Field

若对任意时刻 $t$、位置 $x$ 和分布 $m$，MFG 系统都有足够规则的解，可以定义：

$$U(t,x,m)=u^{t,m}(t,x)$$

其中 $u^{t,m}$ 是从时刻 $t$、初始分布 $m$ 启动的 MFG 价值函数。沿均衡分布流：

$$u(t,x)=U(t,x,m_t)$$

$U$ 称为 decoupling field。它把整个前向—后向系统压缩为状态和分布上的统一价值映射。

## 十一、无共同噪声的 Master Equation

定义均衡漂移：

$$b^*(y,m)=D_pH(y,m,D_yU(t,y,m))$$

分布生成算子的伴随作用为：

$$\mathcal K_{U,m}^*m=\nu\Delta m-\operatorname{div}(mb^*)$$

Master Equation 的链式法则形式为：

$$-\partial_tU-\nu\Delta_xU+H(x,m,D_xU)-\int\frac{\delta U}{\delta m}(t,x,m,y)(\mathcal K_{U,m}^*m)(dy)=0$$

终端条件为：

$$U(T,x,m)=g(x,m)$$

这种写法直接显示测度流对价值变化的贡献，并减少不同 Hamiltonian 符号约定造成的混淆。

## 十二、Master Equation 的展开形式

对测度项积分分部，可得：

$$-\partial_tU-\nu\Delta_xU+H(x,m,D_xU)-\nu\int\operatorname{div}_yD_mU(t,x,m,y)m(dy)-\int D_mU(t,x,m,y)\cdot b^*(y,m)m(dy)=0$$

其中 $D_mU(t,x,m,y)$ 表示 $U$ 对分布变量在位置 $y$ 的 Lions 导数。

该方程定义在：

$$[0,T]\times\mathbb R^d\times\mathcal P_2(\mathbb R^d)$$

测度空间是无限维的，因此经典解存在性通常需要较强光滑性、单调性和非退化扩散条件。

## 十三、Master Equation 的作用

Master Equation 同时完成四件事：给出任意初始分布下的均衡价值；描述价值对分布扰动的敏感性；构造有限玩家 Nash 系统的近似解；在共同噪声存在时刻画条件分布的随机演化。

对小分布扰动 $m'$，一阶展开为：

$$U(t,x,m')-U(t,x,m)\approx\int\frac{\delta U}{\delta m}(t,x,m,y)(m'-m)(dy)$$

该导数可以衡量某类单位或玩家密度变化对个体价值的边际影响。

## 十四、共同噪声

若所有玩家还受到共同 Brownian 运动 $W_t^0$：

$$dX_t^i=b(X_t^i,m_t,\alpha_t^i)dt+\sqrt{2\nu}\,dW_t^i+\sqrt{2\nu_0}\,dW_t^0$$

平均场不再是无条件分布，而是共同噪声条件下的随机分布：

$$m_t=\mathcal L(X_t^i\mid\mathcal F_t^0)$$

共同噪声 Master Equation 会出现 $x$ 与测度变量的交叉二阶项，以及对测度的二阶导数项。其抽象形式可写为：

$$-\partial_tU+\mathcal H(U,m)+\nu_0\mathcal M_2U=0$$

$\mathcal M_2$ 汇总共同噪声诱导的二阶测度算子。具体展开依赖 Lions 二阶导数约定，不应在未固定符号与协方差结构时机械套用。

## 十五、有限玩家 Nash 系统

令 $v_i^N(t,x_1,\ldots,x_N)$ 是玩家 $i$ 的均衡价值，排除自身的经验分布为：

$$m_{\boldsymbol x}^{N,i}=\frac{1}{N-1}\sum_{j\neq i}\delta_{x_j}$$

对无共同噪声且独立扩散的对称博弈，Nash PDE 系统可写为：

$$-\partial_tv_i^N-\nu\sum_{j=1}^N\Delta_{x_j}v_i^N+H(x_i,m_{\boldsymbol x}^{N,i},D_{x_i}v_i^N)+\sum_{j\neq i}D_{x_j}v_i^N\cdot D_pH(x_j,m_{\boldsymbol x}^{N,j},D_{x_j}v_j^N)=0$$

终端条件为：

$$v_i^N(T,\boldsymbol x)=g(x_i,m_{\boldsymbol x}^{N,i})$$

该系统维数随 $N$ 线性增长，但未知函数有 $N$ 个，直接求解很快遭遇维数灾难。

## 十六、由 Master Equation 构造有限玩家近似

自然近似为：

$$u_i^N(t,\boldsymbol x)=U(t,x_i,m_{\boldsymbol x}^{N,i})$$

对 $j\neq i$，经验测度链式法则给出：

$$D_{x_j}u_i^N\approx\frac{1}{N-1}D_mU(t,x_i,m_{\boldsymbol x}^{N,i},x_j)$$

二阶导数还会产生 $1/(N-1)^2$ 量级的测度二阶导数项。把 $u_i^N$ 代入 Nash 系统，Master Equation 会抵消主阶项，剩余项决定有限玩家残差。

## 十七、有限玩家价值误差

在经典解足够光滑、系数有界且单调性等稳定条件成立时，常见结果具有形式：

$$\max_i\|v_i^N-u_i^N\|\leq\frac{C}{N}$$

具体范数、常数和速率取决于模型、是否有共同噪声、扩散退化性、终端数据光滑性及经验测度采用 $1/N$ 还是 $1/(N-1)$。

若只能得到弱解或较低正则性，误差可能低于 $O(N^{-1})$，甚至只能证明收敛而无显式速率。

## 十八、近似 Nash 均衡误差

把 MFG 反馈策略部署到有限 $N$ 玩家系统中，若任意玩家单独偏离的收益改善至多 $\varepsilon_N$，则构成 $\varepsilon_N$-Nash 均衡：

$$J_i^N(\alpha^{1,*},\ldots,\alpha^{N,*})\leq J_i^N(\beta^i,\alpha^{-i,*})+\varepsilon_N$$

损失最小化下，上式表示单方偏离不能把损失降低超过 $\varepsilon_N$。在较强正则条件下可能有：

$$\varepsilon_N\leq\frac{C}{N}$$

在只使用传播混沌和 Lipschitz 稳定性的证明中，更常见的是 $N^{-1/2}$ 或带维数依赖的经验测度速率。

## 十九、传播混沌

传播混沌表示有限玩家在极限下变得渐近独立，每个玩家服从同一个 McKean–Vlasov 极限。若 $\overline X_t^i$ 是使用极限分布流驱动的独立副本，可研究耦合误差：

$$\mathbb E\left[\sup_{0\leq t\leq T}|X_t^{i,N}-\overline X_t^i|^2\right]$$

在 Lipschitz 条件下，常见均方耦合界为：

$$\mathbb E\left[\sup_{0\leq t\leq T}|X_t^{i,N}-\overline X_t^i|^2\right]\leq\frac{C}{N}$$

这对应单个状态的均方根误差 $O(N^{-1/2})$。它与价值函数的 $O(N^{-1})$ 展开不是同一个结论。

## 二十、经验测度误差与维数

经验测度的 Wasserstein 收敛速度依赖状态维数和矩条件。一个基本分解为：

$$W_2(m_t^N,m_t)\leq W_2\left(m_t^N,\frac{1}{N}\sum_{i=1}^N\delta_{\overline X_t^i}\right)+W_2\left(\frac{1}{N}\sum_{i=1}^N\delta_{\overline X_t^i},m_t\right)$$

第一项是交互系统与独立副本的耦合误差，第二项是独立经验分布的统计误差。高维下第二项可能明显慢于 $N^{-1/2}$，因此不能普遍声称：

$$\mathbb E[W_2(m_t^N,m_t)]=O(N^{-1/2})$$

应根据维数、距离阶数和分布矩条件使用相应经验测度定理。

## 二十一、中央极限定理修正

大数极限只给出 $m_t^N\to m_t$。进一步定义涨落场：

$$\eta_t^N=\sqrt N(m_t^N-m_t)$$

在适当条件下，$\eta_t^N$ 可收敛到高斯测度值过程。于是有限玩家指标可做二阶近似：

$$\mathbb E[F(m_t^N)]\approx F(m_t)+\frac{1}{2N}\mathbb E[D_{mm}^2F(m_t)[\eta_t,\eta_t]]$$

该展开需要二阶测度可微性；若存在边界、碰撞、离散动作或多均衡，Gaussian 修正可能失效。

## 二十二、Mean-field Control 的定义

Mean-field control 又称 McKean–Vlasov control 或社会规划问题。规划者选择统一反馈控制总体分布，最小化：

$$J^{\mathrm{MFC}}(\alpha)=\mathbb E\left[\int_0^Tf(X_t,m_t,\alpha_t)dt+g(X_T,m_T)\right]$$

其中：

$$m_t=\mathcal L(X_t)$$

与 MFG 不同，规划者知道改变控制会改变整个分布，因此对 $m$ 的影响进入一阶最优条件。

## 二十三、测度空间 Bellman 方程

设社会价值泛函为：

$$V(t,m)=\inf_\alpha J_{t,m}^{\mathrm{MFC}}(\alpha)$$

在无共同噪声且足够光滑时，其 Bellman 方程可写成：

$$-\partial_tV(t,m)+\int\left[H(x,m,D_mV(t,m,x))-\nu\operatorname{div}_xD_mV(t,m,x)\right]m(dx)=0$$

终端条件为：

$$V(T,m)=\int g(x,m)m(dx)$$

若 $b$ 或扩散也非局部依赖分布，Hamiltonian 和二阶项需按具体模型扩展。

## 二十四、MFC 的最优性系统

令：

$$u(t,x)=\frac{\delta V}{\delta m}(t,m_t,x)$$

对含分布耦合的 Hamiltonian，规划者的向后方程会出现外部性修正：

$$-\partial_tu-\nu\Delta u+H(x,m_t,D_xu)+\int\frac{\delta H}{\delta m}(y,m_t,D_yu)(x)m_t(dy)=0$$

前向方程仍由最优漂移推动：

$$\partial_tm_t-\nu\Delta m_t+\operatorname{div}\left(m_tD_pH(x,m_t,D_xu)\right)=0$$

终端条件也包含总体终端成本对分布的边际影响。

## 二十五、MFG 与 MFC 的核心差别

MFG 中单个无穷小玩家把 $m$ 当作给定，向后方程为：

$$-\partial_tu-\nu\Delta u+H(x,m,D_xu)=0$$

MFC 中规划者内生化分布外部性，因此多出：

$$\int\frac{\delta H}{\delta m}(y,m,D_yu)(x)m(dy)$$

若耦合完全没有分布外部性，或模型具有特殊势结构，两者可能一致；一般情况下，分散均衡并不等于社会最优。

## 二十六、势平均场博弈

若耦合来自某个势泛函 $\mathcal F(m)$：

$$F(x,m)=\frac{\delta\mathcal F}{\delta m}(m,x)$$

则 MFG 均衡可能转化为分布流上的全局变分问题。典型目标形式为：

$$\inf_{m,v}\left\{\int_0^T\int L(x,m_t,v_t(x))m_t(dx)dt+\mathcal G(m_T)\right\}$$

约束为 Fokker–Planck 方程：

$$\partial_tm-\nu\Delta m+\operatorname{div}(mv)=0$$

势结构有利于使用凸优化、原始—对偶算法和全局能量下降方法。

## 二十七、社会代价与 Price of Anarchy

设分散 MFG 均衡的社会成本为 $C_{\mathrm{MFG}}$，规划者最优成本为 $C_{\mathrm{MFC}}$。损失最小化下可定义：

$$\operatorname{PoA}=\frac{C_{\mathrm{MFG}}}{C_{\mathrm{MFC}}}$$

当成本非负且分母为正时，通常有：

$$\operatorname{PoA}\geq1$$

可通过拥塞费、奖励塑形或机制设计加入边际外部性，使分散行为更接近 MFC 解。

## 二十八、离散状态 MFG

有限状态空间中，分布位于概率单纯形：

$$\Delta_K=\left\{m\in\mathbb R_+^K:\sum_{k=1}^Km_k=1\right\}$$

个体采用转移率 $q_{ij}(a,m)$。分布演化为：

$$\dot m_j=\sum_i m_iq_{ij}(a_i^*,m)$$

HJB 变成常微分方程组：

$$-\dot u_i=\min_a\left\{f_i(a,m)+\sum_jq_{ij}(a,m)(u_j-u_i)\right\}$$

离散模型更适合角色、路线、战术模式等有限类别，但单纯形边界处仍可能出现非光滑性。

## 二十九、数值求解 Master Equation

直接离散 $m$ 会遭遇测度维数灾难。常见方法包括：有限状态单纯形网格、粒子近似、基函数投影、神经网络 $U_\theta(t,x,m)$、DeepSets 或注意力编码经验测度、基于 FBSDE 的求解器，以及利用单调性结构的迭代。

粒子输入可表示为：

$$U_\theta\left(t,x,\frac{1}{M}\sum_{j=1}^M\delta_{y_j}\right)$$

网络必须对粒子排列不变，并在不同粒子数、初始分布和时间切片上验证泛化。

## 三十、数值残差与验证

对近似解 $U_\theta$，可构造 Master Equation 残差：

$$\mathcal R_\theta(t,x,m)=\mathcal M[U_\theta](t,x,m)$$

训练目标可以包含：

$$\mathcal L(\theta)=\mathbb E[|\mathcal R_\theta|^2]+\lambda_T\mathbb E[|U_\theta(T,x,m)-g(x,m)|^2]$$

小残差只说明采样点附近近似满足所写方程，不证明解唯一，也不保证测度导数、有限玩家策略或分布外推正确。

## 三十一、有限玩家误差的实证验证

对多个 $N$ 运行有限玩家模拟，比较 MFG 策略与有限玩家最优响应。可估计单方偏离收益：

$$\widehat\varepsilon_N=\max_i\left[J_i^N(\alpha^*)-\inf_{\beta^i}J_i^N(\beta^i,\alpha^{-i,*})\right]_+$$

再拟合幂律：

$$\widehat\varepsilon_N\approx cN^{-\gamma}$$

拟合指数 $\gamma$ 只是有限范围经验规律；必须给出置信区间，并分别检查数值离散误差、有限回放误差和真实有限玩家误差。

## 三十二、5v5 游戏：单位与局部分布

若每个英雄、召唤物或兵线单位视为弱交互个体，可用位置—血量—角色状态构造分布：

$$m_t(x,h,r)=\frac{1}{N}\sum_{i=1}^N\delta_{(X_t^i,H_t^i,R_t^i)}(x,h,r)$$

个体损失可包含死亡、拥塞、脱节、资源暴露和技能覆盖：

$$f_i=c_{\mathrm{death}}+c_{\mathrm{spacing}}+c_{\mathrm{objective}}+c_{\mathrm{role}}$$

标准平均场近似更适合大量同质或分类型单位；只有十名高度异质英雄时，应使用多总体 MFG、主从博弈或有限玩家模型，而不是假装 $N$ 已足够大。

## 三十三、5v5 游戏：多总体平均场

把坦克、战士、法师、射手和辅助视为不同总体，记第 $k$ 类分布为 $m_t^k$。价值函数满足耦合系统：

$$-\partial_tu^k-\nu_k\Delta u^k+H^k(x,m^1,\ldots,m^K,D_xu^k)=0$$

各总体分布满足：

$$\partial_tm^k-\nu_k\Delta m^k+\operatorname{div}\left(m^kD_pH^k(x,\boldsymbol m,D_xu^k)\right)=0$$

该模型可以表达前排密度、后排安全区、支援覆盖和路线拥塞之间的相互作用。

## 三十四、5v5 游戏：MFG 与团队控制

若每个智能体只优化自身生存和收益，MFG 可以预测分散行为与拥塞均衡。若中央战术控制器直接优化全队胜率、资源和伤亡，则更接近 MFC。

可把团队社会损失写为：

$$C(m,\alpha)=\int f(x,m,\alpha(x))m(dx)+\lambda\Phi(m)$$

$\Phi(m)$ 可惩罚阵型断裂、火力重叠不足或路线过度集中。MFC 的外部性项促使控制器考虑“一个单位移动会怎样改变全队分布”，而不只看该单位的局部最优。

## 三十五、匹配生态与长期分布

在大规模玩家匹配、英雄选择和策略流行度层面，平均场状态可以表示段位—角色—英雄分布。个体根据胜率、等待时间和偏好选择队列或英雄，平台则调节匹配和奖励。

MFG 用于预测玩家对平台规则的均衡响应；MFC 用于计算平台理想的总体分布。二者差异可识别激励缺口，并指导奖励或等待时间定价。

平台改变规则会改变玩家分布，离线固定分布评估通常不足：

$$m_{t+1}=\Gamma(m_t;\mathrm{rule})$$

## 三十六、何时不应使用平均场

以下情形应谨慎：玩家数很少且个体影响不可忽略；存在关键领袖或 Boss；交互由稀疏固定网络而非总体分布决定；玩家高度异质且类型不可聚合；存在强联盟、通信和身份记忆；策略不连续导致 Master Equation 缺乏光滑性；多均衡使训练结果严重依赖初始化。

可替代为有限玩家动态博弈、图上平均场博弈、主从平均场博弈、Mean-field type game、群体博弈或基于网络的局部交互模型。

## 三十七、实施路线

第一步验证交换对称性和单个体影响是否随 $N$ 减弱。第二步确定状态、总体类型、噪声、成本和 Hamiltonian 符号。第三步先解 MFG 前向—后向系统并检查质量守恒、非负性和单调性。第四步用多个有限 $N$ 仿真测量传播混沌和单方偏离收益。第五步需要跨初始分布泛化或有限玩家一阶修正时，再求 Master Equation。第六步若目标是中央团队最优，则改建 MFC，而不是误用 MFG。第七步用真实回放校准并进行版本外验证。

质量守恒应满足：

$$\int m_t(dx)=1$$

分布非负性应满足：

$$m_t\geq0$$

## 三十八、常见误区

第一，把 MFG 和 MFC 当成同一个问题。前者是分散 Nash 均衡，后者是总体最优控制。

第二，看到 $N$ 很大就默认误差为 $O(1/N)$。价值展开、状态耦合、经验测度和近似 Nash 的速率可能不同。

第三，只证明经验分布收敛，就声称有限玩家策略是近似 Nash。还需要控制单方偏离收益。

第四，在存在共同噪声时仍使用确定性 $m_t$。正确对象通常是条件分布。

第五，用有限样本网格残差代替 Master Equation 的经典解证明。

第六，在十名高度异质英雄上直接套用单总体极限，而不检查类型结构与个体影响。

第七，混用不同 Hamiltonian 符号约定，导致 Fokker–Planck 漂移和 Master Equation 测度项符号相反。

## 三十九、结论

MFG 用 HJB–Fokker–Planck 固定点描述大量分散玩家的 Nash 均衡；Master Equation 把均衡价值提升为状态与分布的统一函数，并为分布敏感性、共同噪声和有限玩家展开提供核心工具；有限玩家误差必须区分价值误差、近似 Nash 误差、轨迹耦合误差和经验测度误差；MFC 则通过测度空间 Bellman 方程内生化总体分布外部性，刻画社会规划者的最优控制。

实际应用中，最重要的不是把所有系统都改写成平均场形式，而是先验证弱交互、交换对称性、玩家规模和分布正则性。只有在这些条件与业务结构匹配时，Master Equation 和 Mean-field control 才能给出可信的近似、可解释的外部性和可验证的群体策略。
