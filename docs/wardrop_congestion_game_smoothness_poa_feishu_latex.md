# Wardrop 均衡、拥塞博弈与 Smoothness PoA：网络资源竞争的统一框架

## 摘要

交通网络、通信路由、云计算、排队系统和多人游戏都存在相同结构：许多决策者共享有限资源，某项资源的使用成本随负载增加。Wardrop 均衡用连续流量描述大量可忽略个体的自私路由；原子拥塞博弈保留有限玩家对资源负载的离散影响；Price of Anarchy（PoA）比较最坏均衡与社会最优；Smoothness 方法则通过一个局部偏离不等式，为纯 Nash、混合 Nash、相关均衡、粗相关均衡和无悔学习结果提供统一效率保证。

本文系统介绍多商品网络流、Wardrop 第一原则、变分不等式、Beckmann 势、存在唯一性、社会最优、边际成本、Pigou 与 Braess 例子、Rosenthal 势、原子与加权拥塞博弈、PoA 与 Price of Stability、非原子和原子 smoothness、不完全信息与学习鲁棒性、收费设计、Stackelberg 路由，以及 5v5 游戏中的分路、野区、目标点和路线拥塞。

关键边界是：Wardrop 模型假设单个决策者对总流量影响可忽略；有限玩家对负载有显著影响时，应使用原子模型。Smoothness 给出的是均衡效率上界，不自动证明均衡存在、界的紧性或某个学习算法收敛到单一点。

## 一、网络与资源

设有向网络为：

$$G=(V,E)$$

每条边 $e\in E$ 的流量为 $x_e\geq0$，延迟或成本函数为：

$$\ell_e:\mathbb R_+\rightarrow\mathbb R_+$$

通常假设 $\ell_e$ 连续且非递减。总边成本为：

$$C_e(x_e)=x_e\ell_e(x_e)$$

网络社会成本为所有使用者承担成本之和。

## 二、多商品需求

商品或玩家类型记为 $k\in\mathcal K$，其起终点为 $(s_k,t_k)$，需求为 $d_k$。可行路径集合为 $\mathcal P_k$。

路径流满足：

$$f_p^k\geq0,\qquad \sum_{p\in\mathcal P_k}f_p^k=d_k$$

边流由路径流聚合：

$$x_e=\sum_{k\in\mathcal K}\sum_{p\in\mathcal P_k:e\in p}f_p^k$$

所有满足需求守恒的路径流构成可行集 $\mathcal F$。

## 三、路径成本

在可分离边延迟模型中，路径 $p$ 的成本为：

$$c_p(x)=\sum_{e\in p}\ell_e(x_e)$$

同一路径上的各边成本相加。若资源间存在交互：

$$\ell_e=\ell_e(x_1,\ldots,x_{|E|})$$

则仍可构造一般网络博弈，但 Beckmann 势和标准边级 smoothness 结论可能不再成立。

## 四、Wardrop 第一原则

Wardrop 均衡 $f^{\mathrm W}$ 满足：对每个商品 $k$，所有正流量路径都具有最小成本：

$$f_p^{k,\mathrm W}\gt0\quad\Longrightarrow\quad c_p(x^{\mathrm W})=\min_{q\in\mathcal P_k}c_q(x^{\mathrm W})$$

等价地：

$$f_p^{k,\mathrm W}\gt0\quad\Longrightarrow\quad c_p(x^{\mathrm W})\leq c_q(x^{\mathrm W}),\qquad \forall q\in\mathcal P_k$$

没有一个无穷小用户能通过单方面换路严格降低成本。

## 五、非原子假设

Wardrop 用户的质量连续且单个用户影响为零。某个用户从路径 $p$ 切换到 $q$ 时，不改变边流 $x$，因此比较的是当前成本。

若一个玩家的流量为 $w_i\gt0$，其换路会改变资源负载和所有相关延迟，应使用原子或可分流原子拥塞博弈。

非原子并不表示用户数量真的无限，而是单个用户相对于总需求足够小的近似。

## 六、Wardrop 的变分不等式

边流 $x^{\mathrm W}$ 是 Wardrop 均衡，当且仅当：

$$\sum_{e\in E}\ell_e(x_e^{\mathrm W})(y_e-x_e^{\mathrm W})\geq0,\qquad \forall y\in\mathcal F$$

记成本算子为：

$$F(x)=(\ell_e(x_e))_{e\in E}$$

则可写成：

$$\langle F(x^{\mathrm W}),y-x^{\mathrm W}\rangle\geq0,\qquad \forall y\in\mathcal F$$

## 七、互补条件

对商品 $k$ 引入最小路径成本 $\pi_k$。Wardrop 条件可写为：

$$c_p(x)-\pi_k\geq0$$

$$f_p^k\geq0$$

$$f_p^k\left[c_p(x)-\pi_k\right]=0$$

再加上需求守恒。这是一组非线性互补条件，可用 MPEC、VI 或专门交通分配算法求解。

## 八、Beckmann 势

当边成本可分离且连续非递减时，Wardrop 均衡等价于凸优化：

$$\min_{x\in\mathcal F}\Phi(x)$$

其中：

$$\Phi(x)=\sum_{e\in E}\int_0^{x_e}\ell_e(z)\,dz$$

因为：

$$\frac{\partial\Phi}{\partial x_e}=\ell_e(x_e)$$

该优化的 KKT 条件正是 Wardrop 变分不等式。

## 九、存在性

若可行集 $\mathcal F$ 非空、紧且凸，成本算子连续，则 VI 存在解。因此连续非递减边成本下，Wardrop 均衡通常存在。

若路径集合无限、需求无界、容量约束导致可行集开口，或成本在容量处不连续，需要额外紧性与下半连续性条件。

势函数方法提供存在性，也提供可计算性。

## 十、唯一性

若每个边延迟严格递增，则 Wardrop 的边流通常唯一。更一般地，若成本算子严格单调：

$$\langle F(x)-F(y),x-y\rangle\gt0,\qquad x\neq y$$

则 VI 解唯一。

路径流分解不一定唯一：多个路径可诱导相同边流和相同成本。报告“均衡唯一”时必须说明是边流、路径流还是成本唯一。

## 十一、社会成本

网络总成本为：

$$C(x)=\sum_{e\in E}x_e\ell_e(x_e)$$

系统最优流定义为：

$$x^{\mathrm{OPT}}\in\operatorname*{arg\,min}_{x\in\mathcal F}C(x)$$

Wardrop 用户最小化个人延迟，系统规划者最小化所有用户总延迟。两者通常不同。

## 十二、边际社会成本

若 $\ell_e$ 可微：

$$\frac{d}{dx_e}\left[x_e\ell_e(x_e)\right]=\ell_e(x_e)+x_e\ell_e'(x_e)$$

第一项是新增用户自身成本，第二项是该用户施加给既有用户的拥塞外部性。

系统最优可看作以边际社会成本：

$$m_e(x_e)=\ell_e(x_e)+x_e\ell_e'(x_e)$$

为感知成本的 Wardrop 均衡。

## 十三、Pigouvian Toll

边际拥塞收费为：

$$\tau_e(x_e)=x_e\ell_e'(x_e)$$

用户感知成本变成：

$$\widetilde\ell_e(x_e)=\ell_e(x_e)+\tau_e(x_e)$$

在标准可分离模型中，该收费可把系统最优实现为 Wardrop 均衡。现实中还需处理预算、可观测性、公平性和需求弹性。

## 十四、Price of Anarchy

PoA 定义为最坏均衡社会成本与最优成本之比：

$$\operatorname{PoA}=\sup_{x\in\mathrm{Eq}}\frac{C(x)}{C(x^{\mathrm{OPT}})}$$

若均衡唯一，可直接比较该均衡。PoA 越接近一，去中心化行为越有效。

PoA 是给定博弈类别的最坏情形指标，不等于某个具体实例的实际损失。

## 十五、Price of Stability

Price of Stability（PoS）比较最好均衡与社会最优：

$$\operatorname{PoS}=\inf_{x\in\mathrm{Eq}}\frac{C(x)}{C(x^{\mathrm{OPT}})}$$

总有：

$$1\leq\operatorname{PoS}\leq\operatorname{PoA}$$

PoS 适合分析均衡选择机制可以达到的最佳效果；PoA 则对最坏均衡提供保证。

## 十六、Pigou 网络

考虑单位需求和两条平行边：

$$\ell_1(x)=x,\qquad \ell_2(x)=1$$

Wardrop 均衡把全部流量放在第一条边：

$$x_1^{\mathrm W}=1,\qquad C(x^{\mathrm W})=1$$

系统最优令 $x_1=1/2$：

$$C(x^{\mathrm{OPT}})=\left(\frac12\right)^2+\frac12=\frac34$$

因此：

$$\operatorname{PoA}=\frac{1}{3/4}=\frac43$$

## 十七、Braess Paradox

在 Braess 网络中，新增一条零延迟捷径可能使 Wardrop 总成本上升。一个标准实例中，删去捷径时流量均分，总成本为：

$$C_{\mathrm{without}}=\frac32$$

加入捷径后，自私用户全部选择看似更短的组合路径，均衡总成本变为：

$$C_{\mathrm{with}}=2$$

悖论来自均衡反馈，不是因为新增边本身具有正成本。容量增加也可能改变策略激励并产生类似现象。

## 十八、弹性需求

若需求取决于最小出行成本，可使用逆需求函数 $B_k(q_k)$。用户只在收益不低于成本时进入：

$$B_k(q_k)=\pi_k$$

社会福利为：

$$W(q,x)=\sum_k\int_0^{q_k}B_k(z)\,dz-\sum_ex_e\ell_e(x_e)$$

弹性需求下应分析福利 PoA，而不是只比较总延迟。

## 十九、容量约束

若边容量为 $u_e$：

$$0\leq x_e\leq u_e$$

可把容量作为硬可行性约束，或使用趋于无穷的延迟函数。硬容量会引入影子价格，均衡条件包含容量乘子。

当需求超过网络可行容量时，必须允许拒绝、排队、溢出或弹性需求，否则模型无解。

## 二十、随机用户均衡

若用户感知成本带有随机误差，可使用 logit route choice：

$$P_k(p\mid x)=\frac{\exp\{-\theta c_p(x)\}}{\sum_{q\in\mathcal P_k}\exp\{-\theta c_q(x)\}}$$

随机用户均衡满足：

$$f_p^k=d_kP_k(p\mid x)$$

$\theta$ 越大，选择越接近确定性最短路；有限 $\theta$ 下所有可行路径可能有正流量。

## 二十一、动态交通分配

静态 Wardrop 忽略出发时间、排队传播和时变容量。动态均衡使用路径–出发时间流 $f_p(t)$，并要求使用中的选择具有相同最小广义成本。

动态模型需要满足流守恒、先进先出和队列演化。静态 PoA 结论不能自动转移到动态排队网络。

## 二十二、原子拥塞博弈

有限玩家集合为 $\mathcal N$，资源集合为 $\mathcal E$。玩家 $i$ 选择资源子集：

$$s_i\in\mathcal S_i\subseteq2^{\mathcal E}$$

资源负载为：

$$n_e(s)=|\{i:e\in s_i\}|$$

玩家成本为：

$$C_i(s)=\sum_{e\in s_i}\ell_e(n_e(s))$$

## 二十三、纯 Nash 均衡

策略组合 $s$ 是纯 Nash 均衡，若：

$$C_i(s)\leq C_i(s_i',s_{-i}),\qquad \forall i,\ \forall s_i'\in\mathcal S_i$$

与 Wardrop 不同，原子玩家偏离会改变资源负载，因此偏离成本要在新负载下计算。

社会成本为：

$$C(s)=\sum_iC_i(s)=\sum_en_e(s)\ell_e(n_e(s))$$

## 二十四、Rosenthal Potential

无权原子拥塞博弈具有精确势函数：

$$\Phi(s)=\sum_{e\in\mathcal E}\sum_{k=1}^{n_e(s)}\ell_e(k)$$

玩家 $i$ 单方面偏离时：

$$\Phi(s_i',s_{-i})-\Phi(s)=C_i(s_i',s_{-i})-C_i(s)$$

因此势函数的局部极小点是纯 Nash 均衡，有限改进路径必然终止。

## 二十五、势函数与社会成本

Rosenthal 势通常不等于社会成本：

$$\Phi(s)\neq C(s)$$

势最小化选择的是均衡，不一定是社会最优。势函数证明均衡存在和最佳回应收敛，却不能单独给出 PoA。

在某些成本类别中，可比较 $\Phi$ 与 $C$ 来分析 Price of Stability。

## 二十六、加权拥塞博弈

玩家 $i$ 的权重为 $w_i$，资源负载为：

$$x_e(s)=\sum_{i:e\in s_i}w_i$$

玩家成本可写为：

$$C_i(s)=w_i\sum_{e\in s_i}\ell_e(x_e(s))$$

一般加权拥塞博弈未必拥有 Rosenthal 精确势，也未必存在纯 Nash 均衡。应改用近似势、混合均衡、smoothness 或特定延迟结构。

## 二十七、可分流原子博弈

原子玩家可把需求 $d_i$ 分配到多条路径：

$$\sum_{p\in\mathcal P_i}f_p^i=d_i$$

其成本为：

$$C_i(f)=\sum_e f_e^i\ell_e(x_e)$$

玩家在优化时考虑自身流量改变对延迟的影响。其一阶条件不同于非原子 Wardrop，也不同于不可分流拥塞博弈。

## 二十八、Smoothness 的成本形式

成本博弈若对所有策略组合 $s,s^{\star}$ 满足：

$$\sum_iC_i(s_i^{\star},s_{-i})\leq\lambda C(s^{\star})+\mu C(s)$$

其中：

$$\lambda\gt0,\qquad \mu\lt1$$

则称博弈为 $(\lambda,\mu)$-smooth。左侧把每个玩家分别偏离到比较策略，但其他玩家保持在原策略。

## 二十九、Smoothness PoA

若 $s$ 是纯 Nash 均衡，逐个使用偏离不增成本：

$$C(s)\leq\sum_iC_i(s_i^{\star},s_{-i})$$

结合 smoothness：

$$C(s)\leq\lambda C(s^{\star})+\mu C(s)$$

因此：

$$\frac{C(s)}{C(s^{\star})}\leq\frac{\lambda}{1-\mu}$$

对所有有效参数取最优可得最紧 smoothness 上界。

## 三十、为什么 Smoothness 鲁棒

Smoothness 证明只使用单玩家偏离不等式和线性期望，因此同一界通常可扩展到：

- 混合 Nash 均衡；
- 相关均衡；
- 粗相关均衡；
- 无悔学习的时间平均；
- 某些不完全信息 Bayesian 博弈。

这称为 robust PoA。但扩展需要社会成本与玩家成本一致、偏离可测且类型模型满足相应独立性或信息条件。

## 三十一、粗相关均衡

分布 $\sigma$ 是粗相关均衡，若对每个玩家和固定偏离 $s_i'$：

$$\mathbb E_{s\sim\sigma}[C_i(s)]\leq\mathbb E_{s\sim\sigma}[C_i(s_i',s_{-i})]$$

对 smoothness 不等式取期望可得：

$$\mathbb E_{\sigma}[C(s)]\leq\frac{\lambda}{1-\mu}C(s^{\star})$$

因此玩家通过 no-regret learning 产生的经验分布也受同一效率界控制。

## 三十二、非原子 Smoothness

对延迟函数类 $\mathcal L$，若对所有 $\ell\in\mathcal L$ 和 $x,y\geq0$：

$$y\ell(x)\leq\lambda y\ell(y)+\mu x\ell(x)$$

则 Wardrop 均衡满足：

$$C(x^{\mathrm W})\leq\frac{\lambda}{1-\mu}C(x^{\mathrm{OPT}})$$

其中 $x$ 是均衡负载，$y$ 是比较负载。

## 三十三、非原子 PoA 推导

Wardrop VI 取 $y=x^{\mathrm{OPT}}$：

$$C(x^{\mathrm W})=\sum_ex_e^{\mathrm W}\ell_e(x_e^{\mathrm W})\leq\sum_ex_e^{\mathrm{OPT}}\ell_e(x_e^{\mathrm W})$$

逐边应用 smoothness：

$$x_e^{\mathrm{OPT}}\ell_e(x_e^{\mathrm W})\leq\lambda x_e^{\mathrm{OPT}}\ell_e(x_e^{\mathrm{OPT}})+\mu x_e^{\mathrm W}\ell_e(x_e^{\mathrm W})$$

求和并移项得到 $\lambda/(1-\mu)$ 界。

## 三十四、仿射延迟的 4/3 界

设：

$$\ell(x)=ax+b,\qquad a,b\geq0$$

利用：

$$xy\leq y^2+\frac14x^2$$

可得：

$$y\ell(x)\leq y\ell(y)+\frac14x\ell(x)$$

因此参数为：

$$\lambda=1,\qquad \mu=\frac14$$

非原子仿射拥塞网络满足：

$$\operatorname{PoA}\leq\frac{1}{1-1/4}=\frac43$$

Pigou 网络达到该界。

## 三十五、Pigou 参数

对延迟函数类 $\mathcal L$，定义：

$$\beta(\mathcal L)=\sup_{\ell\in\mathcal L}\sup_{x\gt0,\ 0\leq y\leq x}\frac{y[\ell(x)-\ell(y)]}{x\ell(x)}$$

则在标准非原子可分离模型中：

$$\operatorname{PoA}\leq\frac{1}{1-\beta(\mathcal L)}$$

该参数衡量高负载成本相对低负载成本增长所造成的外部性。

## 三十六、多项式延迟

对单项式：

$$\ell(x)=x^d$$

令 $t=y/x$，Pigou 项为：

$$t(1-t^d)$$

最大值在：

$$t=(d+1)^{-1/d}$$

取得，因此：

$$\beta_d=\frac{d}{(d+1)^{1+1/d}}$$

相应 smoothness 界为：

$$\operatorname{PoA}\leq\frac{1}{1-\beta_d}$$

次数越高，拥塞外部性和最坏效率损失通常越大。

## 三十七、原子资源 Smoothness

在无权原子拥塞博弈中，若比较状态有 $y$ 个玩家使用资源，而当前状态有 $x$ 个，则分别偏离最多产生：

$$y\ell(x+1)$$

因此可寻找参数满足：

$$y\ell(x+1)\leq\lambda y\ell(y)+\mu x\ell(x)$$

再对资源求和得到博弈 smoothness。与非原子不等式相比，多出的 $+1$ 正是单个原子玩家对负载的影响。

## 三十八、原子仿射 PoA

对非负仿射延迟，无权不可分流原子拥塞博弈可使用：

$$\lambda=\frac53,\qquad \mu=\frac13$$

得到：

$$\operatorname{PoA}\leq\frac{5/3}{1-1/3}=\frac52$$

该常数不同于非原子仿射网络的 $4/3$。选择 PoA 结论前必须先确认玩家是否原子、是否带权和是否可分流。

## 三十九、Smoothness 的局限

Smoothness 上界可能不紧，因为它要求同一局部不等式对所有状态和比较状态成立。某个具体网络的实际 PoA 可能远低于类别上界。

若社会目标包含最大延迟、公平性、风险或非可加耦合项，标准 smoothness 需要扩展。若成本可能为负，很多成本比值也失去意义。

## 四十、无悔学习

玩家 $i$ 的外部遗憾为：

$$R_i(T)=\sum_{t=1}^TC_i(s^t)-\min_{s_i'}\sum_{t=1}^TC_i(s_i',s_{-i}^t)$$

若：

$$\frac{R_i(T)}{T}\rightarrow0$$

经验分布趋近粗相关均衡集合。对 smooth 博弈：

$$\limsup_{T\rightarrow\infty}\frac{\frac1T\sum_{t=1}^TC(s^t)}{C(s^{\star})}\leq\frac{\lambda}{1-\mu}$$

即使动作本身不收敛，长期平均效率仍可受控。

## 四十一、Bayesian Smoothness

若玩家类型 $\theta_i$ 决定需求、可行路径或成本，可定义类型依赖策略。对每个类型轮廓建立 smoothness 偏离，并对先验取期望，可得到 Bayesian PoA。

但若类型高度相关、玩家只观察部分公共信号或偏离依赖未知类型，标准独立类型扩展可能失效，需要信息结构感知的 smoothness。

## 四十二、网络设计

可通过容量扩展、删边、收费和信号设计改善均衡。设计变量记为 $z$：

$$\min_z C(x^{\mathrm W}(z))+\kappa(z)$$

这是一个含均衡约束的双层问题。下层 Wardrop 可由 VI、KKT 或 Beckmann 优化替代。

Braess paradox 表明“增加资源”不一定改善无收费均衡，因此网络设计必须考虑行为响应。

## 四十三、Stackelberg Routing

系统可直接控制部分流量 $\alpha d$，其余用户对控制后网络形成 Wardrop 均衡。领导者问题为：

$$\min_{x^{\mathrm L}}C(x^{\mathrm L}+x^{\mathrm F})$$

约束为：

$$x^{\mathrm F}\in\operatorname{Wardrop}(x^{\mathrm L})$$

受控流可用于预加载路线、诱导剩余用户或保证关键资源，但求解通常是双层优化。

## 四十四、算法：Frank–Wolfe

Beckmann 问题可用 Frank–Wolfe。给定 $x^k$，先在线性化成本下做全有或全无最短路分配：

$$y^k\in\operatorname*{arg\,min}_{y\in\mathcal F}\sum_e\ell_e(x_e^k)y_e$$

再更新：

$$x^{k+1}=x^k+\eta_k(y^k-x^k)$$

线搜索可最小化 $\Phi(x^k+\eta(y^k-x^k))$。其 Frank–Wolfe gap 也是 Wardrop VI 残差。

## 四十五、算法：投影与 Mirror Descent

一般 VI 可用投影梯度：

$$x^{k+1}=\Pi_{\mathcal F}\left[x^k-\eta_kF(x^k)\right]$$

若算子仅单调而非强单调，extragradient 更稳健：

$$y^k=\Pi_{\mathcal F}[x^k-\eta F(x^k)]$$

$$x^{k+1}=\Pi_{\mathcal F}[x^k-\eta F(y^k)]$$

路径概率还可用 entropy mirror descent，避免每步欧氏投影到高维单纯形。

## 四十六、5v5 游戏中的拥塞资源

可把下列对象视为共享资源：

- 兵线经济与经验；
- 野区营地；
- 狭窄河道和入口；
- 防御塔攻击范围；
- 大型目标周围安全位置；
- 回城、传送和支援通道；
- 团战中的输出空间与保护位。

多人同时选择同一资源可能造成经济稀释、路径碰撞、技能重叠、视野暴露和其他区域失守。

## 四十七、游戏路径与延迟

英雄 $i$ 的路线成本可写为：

$$c_i(p,x)=t_i^{\mathrm{travel}}(p)+r_i^{\mathrm{exposure}}(p,x)+\sum_{e\in p}\ell_e(x_e)-g_i^{\mathrm{resource}}(p,x)$$

$x_e$ 可表示同一路段或任务点上的己方人数。延迟函数不只代表移动时间，也可表示资源稀释和战术机会成本。

若英雄角色差异显著，应使用玩家特定成本或加权拥塞模型，而不是假设同质非原子用户。

## 四十八、单局原子模型与跨局 Wardrop 模型

单局只有五名英雄，每名英雄的路线选择都会显著改变局势，因此更接近原子拥塞博弈。

跨大量对局分析某段位玩家的路线比例时，单个玩家对总体分布影响很小，可使用 Wardrop 或人口博弈近似。

同一游戏问题在不同统计层级上可能对应不同模型，PoA 常数不能跨层级直接复用。

## 四十九、游戏中的 PoA 与协调

定义团队成本：

$$C(s)=C^{\mathrm{travel}}+C^{\mathrm{resource\ loss}}+C^{\mathrm{risk}}+C^{\mathrm{timing}}$$

PoA 比较自利或局部决策均衡与中央团队规划：

$$\operatorname{PoA}=\frac{\max_{s\in\mathrm{Eq}}C(s)}{\min_{s}C(s)}$$

信号、ping、角色责任、软收费和队长指令相当于改变感知成本或控制部分流量。Smoothness 可判断在玩家使用 no-regret 更新时，长期团队损失是否仍有统一上界。

## 五十、结论

Wardrop 均衡用变分不等式和 Beckmann 势刻画连续自私流量；原子拥塞博弈通过 Rosenthal 势解释有限玩家最佳回应；社会最优使用边际成本而非个人成本；PoA 衡量去中心化行为的最坏效率损失。

Smoothness 的价值在于它不依赖某个特定均衡选择，并可把纯 Nash 的效率界扩展到混合、相关、粗相关和无悔学习结果。非原子仿射延迟的经典界为 $4/3$，无权原子不可分流仿射拥塞博弈的经典界为 $5/2$，二者不可混用。

在 5v5 游戏中，应把单局路线与资源竞争建成原子、异质和可能带协同的拥塞博弈；跨大量对局的元分布才适合 Wardrop 近似。实际系统可用指数或学习算法产生候选动作，再通过匹配、收费、信号或集中规划减少拥塞外部性，并用实例 PoA 与 smoothness 上界共同评估协调价值。
