# PDMP：分段确定性马尔可夫过程的理论、仿真、控制与游戏应用

## 摘要

Piecewise-Deterministic Markov Process（PDMP，分段确定性马尔可夫过程）描述一类混合随机系统：两次事件之间，状态按照常微分方程或确定性流连续演化；事件在状态相关的随机时刻发生；事件发生后，状态依据转移核瞬间跳变。它把 ODE、连续时间 Markov 链、更新过程和混合自动机统一在一个事件驱动框架中。

PDMP 适合刻画设备老化与故障、排队网络、神经元放电、流行病干预、保险风险、通信系统、Hawkes 强度状态，以及游戏中位置、冷却、持续伤害与击杀、刷新、传送、死亡等离散事件的组合。

本文系统介绍 PDMP 的状态空间、确定性流、跳跃强度、转移核、强制边界跳跃、路径构造、非爆炸性、生成元、Dynkin 公式、Kolmogorov 方程、鞅表示、精确仿真、参数估计、受控 PDMP、HJB、脉冲控制 QVI、部分可观测 PDMP、稀有事件算法和 5v5 游戏建模。

核心边界是：PDMP 的随机性主要来自跳跃时间和跳后状态，跳跃之间通常没有 Brownian 连续噪声；若连续轨迹本身受扩散噪声驱动，则应使用 jump diffusion、switching diffusion 或更一般的随机混合系统。

## 一、基本直觉

PDMP 的样本路径由连续段和跳点拼接而成。若当前状态为 $x$，系统先沿确定性轨迹：

$$X_{t+s}=\phi_s(x)$$

随后在随机时刻 $\tau$ 跳到新状态：

$$X_{\tau}\sim Q(\cdot\mid X_{\tau^-})$$

其中 $X_{\tau^-}$ 表示跳跃前的左极限。跳跃后以新状态为起点重复同一过程。

## 二、状态空间

常见状态由离散模式和连续变量组成：

$$X_t=(M_t,Z_t)\in E$$

其中：

$$E=\bigcup_{m\in\mathcal M}\{m\}\times E_m$$

$M_t$ 可以表示运行、故障、维修、死亡、复活或技能阶段；$Z_t$ 可以表示位置、血量、温度、库存、冷却或年龄。

不同离散模式允许拥有不同维度的连续状态域，但工程实现通常使用统一维度加掩码，以便数值计算和批处理。

## 三、确定性流

在无跳跃区间内，连续状态满足：

$$\frac{dZ_t}{dt}=F(M_t,Z_t)$$

其流映射记为：

$$\phi_t(m,z)=(m,\Phi_m(t,z))$$

流应满足半群性质：

$$\phi_0(x)=x,\qquad \phi_{t+s}(x)=\phi_t(\phi_s(x))$$

若动力学显式依赖日历时间，可把时间加入状态，使扩充后的系统重新成为齐次 Markov 过程。

## 四、跳跃强度

跳跃强度或 hazard rate 为：

$$\lambda:E\rightarrow[0,\infty)$$

给定尚未跳跃且当前状态为 $X_t=x$，短时间内发生跳跃的概率近似为：

$$\mathbb P(N_{t+\Delta t}-N_t=1\mid X_t=x)=\lambda(x)\Delta t+o(\Delta t)$$

状态相关强度允许风险随着温度、损耗、血量或敌人距离变化。

## 五、转移核

事件发生后，新状态按照 Markov 核 $Q$ 采样：

$$Q(x,B)=\mathbb P(X_{\tau}\in B\mid X_{\tau^-}=x)$$

通常要求排除无效自跳：

$$Q(x,\{x\})=0$$

但这不是所有定义都必须满足。若有多种事件类型 $k$，可写成：

$$\lambda(x)=\sum_k\lambda_k(x)$$

$$Q(x,dy)=\sum_k\frac{\lambda_k(x)}{\lambda(x)}Q_k(x,dy)$$

## 六、PDMP 的特征三元组

一个基本 PDMP 由三元组确定：

$$\left(\phi,\lambda,Q\right)$$

若状态域存在边界，还需指定首次到达边界的时间和边界跳转规则。三元组决定：

1. 跳跃之间如何运动；
2. 何时发生随机事件；
3. 事件发生后跳到哪里。

这三类对象必须使用同一状态定义，否则过程不一定满足 Markov 性。

## 七、边界与强制跳跃

从状态 $x$ 出发，沿流首次到达边界的时间为：

$$t^{\star}(x)=\inf\{t\gt0:\phi_t(x)\in\partial E\}$$

在 $t^{\star}(x)$ 之前可能发生随机跳跃；若没有，则边界可触发强制跳跃。实际跳跃时间为：

$$T_1=\min\{T_{\lambda},t^{\star}(x)\}$$

例如冷却归零、资源耗尽、角色到达传送终点或设备温度达到安全上限，都可建成边界事件。

## 八、首次跳跃时间分布

在 $0\leq t\lt t^{\star}(x)$ 时，首次随机跳跃的生存函数为：

$$\mathbb P_x(T_{\lambda}\gt t)=\exp\left[-\int_0^t\lambda(\phi_s(x))\,ds\right]$$

定义累计风险：

$$\Lambda_x(t)=\int_0^t\lambda(\phi_s(x))\,ds$$

则：

$$\mathbb P_x(T_{\lambda}\gt t)=e^{-\Lambda_x(t)}$$

当 $\lambda$ 为常数时，等待时间退化为指数分布。

## 九、路径递归构造

令跳跃时刻为：

$$0=T_0\lt T_1\lt T_2\lt\cdots$$

若跳后状态为 $Z_n=X_{T_n}$，则在：

$$T_n\leq t\lt T_{n+1}$$

有：

$$X_t=\phi_{t-T_n}(Z_n)$$

到达 $T_{n+1}$ 后，根据：

$$Z_{n+1}\sim Q(\cdot\mid X_{T_{n+1}^-})$$

采样下一状态。嵌入链 $(Z_n,T_n)$ 保存了事件级动态。

## 十、非爆炸性

PDMP 必须避免有限时间内发生无限多次跳跃：

$$T_n\rightarrow\infty\quad\text{几乎必然}$$

若强度有界：

$$\lambda(x)\leq\overline\lambda\lt\infty$$

且强制边界跳跃之间存在正的最小驻留时间，通常容易保证非爆炸。若跳跃会把状态推向更高强度区域，则需使用 Lyapunov 条件或事件计数矩估计进行证明。

## 十一、Markov 性

在状态包含所有决定未来流、强度和跳核的信息时：

$$\mathbb P(X_{t+s}\in B\mid\mathcal F_t)=\mathbb P(X_{t+s}\in B\mid X_t)$$

若事件概率依赖“上次事件后经过多久”，应把年龄变量加入状态：

$$A_t=t-T_{N_t}$$

遗漏年龄、冷却、阶段或历史累计量会使表面上的 PDMP 失去 Markov 性。

## 十二、强 Markov 性

在适当可测性和流正则条件下，PDMP 对停止时间 $\tau$ 满足强 Markov 性：

$$\mathbb E_x[f(X_{\tau+t})\mid\mathcal F_{\tau}]=P_tf(X_{\tau})$$

其中转移半群为：

$$P_tf(x)=\mathbb E_x[f(X_t)]$$

强 Markov 性使动态规划可以在随机事件时刻重新启动。

## 十三、无穷小生成元

若流由向量场 $F$ 生成，对足够光滑的函数 $f$，PDMP 生成元为：

$$\mathcal Lf(x)=\nabla f(x)^{\mathsf T}F(x)+\lambda(x)\int_E\left[f(y)-f(x)\right]Q(x,dy)$$

第一项描述确定性漂移，第二项描述随机跳跃。若状态包含离散模式，应在各模式域内分别计算梯度。

## 十四、多事件生成元

若事件类型为 $k=1,\ldots,K$，强度为 $\lambda_k$，跳核为 $Q_k$，则：

$$\mathcal Lf(x)=\nabla f(x)^{\mathsf T}F(x)+\sum_{k=1}^K\lambda_k(x)\int_E\left[f(y)-f(x)\right]Q_k(x,dy)$$

若第 $k$ 类事件采用确定性重置映射 $R_k(x)$：

$$Q_k(x,dy)=\delta_{R_k(x)}(dy)$$

对应项简化为：

$$\lambda_k(x)\left[f(R_k(x))-f(x)\right]$$

## 十五、Dynkin 公式

对生成元定义域内的 $f$：

$$\mathbb E_x[f(X_t)]=f(x)+\mathbb E_x\left[\int_0^t\mathcal Lf(X_s)\,ds\right]$$

因此：

$$M_t^f=f(X_t)-f(X_0)-\int_0^t\mathcal Lf(X_s)\,ds$$

是局部鞅；在适当可积条件下是鞅。Dynkin 公式可用于推导矩方程、稳定性条件和参数估计方程。

## 十六、事件计数鞅

令 $N_t$ 为随机跳跃计数，则其补偿过程为：

$$A_t=\int_0^t\lambda(X_{s^-})\,ds$$

于是：

$$M_t=N_t-A_t$$

是鞅。多事件情形下：

$$M_t^k=N_t^k-\int_0^t\lambda_k(X_{s^-})\,ds$$

可用事件计数与累计暴露时间估计强度参数。

## 十七、Kolmogorov 后向方程

定义：

$$u(t,x)=\mathbb E_x[f(X_t)]$$

在适当正则条件下：

$$\frac{\partial u}{\partial t}(t,x)=\mathcal Lu(t,x)$$

初值为：

$$u(0,x)=f(x)$$

后向方程适合计算从当前状态出发的未来期望、到达概率和价值函数。

## 十八、Kolmogorov 前向方程

若状态在单一连续域中且跳核有密度 $q(y,x)$，密度 $p(t,x)$ 满足：

$$\frac{\partial p}{\partial t}+\nabla\cdot\left(F(x)p(t,x)\right)=-\lambda(x)p(t,x)+\int_E\lambda(y)q(y,x)p(t,y)\,dy$$

左侧是确定性输运，右侧第一项是跳出损失，积分项是从其他状态跳入的概率流。

存在模式、边界重置或奇异跳核时，前向方程还需加入模式耦合与边界通量条件。

## 十九、不变分布

不变分布 $\pi$ 满足：

$$\int_E\mathcal Lf(x)\pi(dx)=0$$

对所有合适的测试函数 $f$ 成立。若存在 Lyapunov 函数 $V$，使：

$$\mathcal LV(x)\leq-cV(x)+b\mathbf 1_C(x)$$

并满足不可约性与小集条件，可建立正 Harris recurrence、唯一不变分布和遍历收敛。

## 二十、与连续时间 Markov 链的关系

连续时间 Markov 链在跳跃之间通常保持状态不变，对应：

$$F(x)=0$$

因此 CTMC 是 PDMP 的特殊情形，其生成元为：

$$\mathcal Lf(x)=\sum_yq(x,y)\left[f(y)-f(x)\right]$$

PDMP 则允许跳跃间状态沿非平凡 ODE 运动，强度也随连续状态变化。

## 二十一、与 ODE 和混合自动机的关系

当：

$$\lambda(x)=0$$

且不存在边界随机重置时，PDMP 退化为确定性 ODE。确定性混合自动机具有模式切换与重置，但切换通常由守卫条件完全决定；PDMP 进一步允许随机 hazard 和随机跳核。

随机混合系统是更宽泛的概念，PDMP 是其中具有确定性连续流和 Markov 跳跃机制的一类。

## 二十二、与 SDE 和 Jump Diffusion 的关系

扩散过程满足：

$$dX_t=b(X_t)dt+\sigma(X_t)dW_t$$

即使没有离散跳跃，连续路径也受 Brownian 噪声扰动。PDMP 的连续段通常满足：

$$dX_t=F(X_t)dt$$

随机性集中在跳时和跳后状态。若模型同时包含扩散与跳跃：

$$dX_t=b(X_t)dt+\sigma(X_t)dW_t+dJ_t$$

则属于 jump diffusion，而不是纯 PDMP。

## 二十三、与半 Markov 过程的关系

半 Markov 过程允许等待时间分布依赖当前状态和下一状态。PDMP 的等待时间通过沿流累计 hazard 生成：

$$\Lambda_x(t)=\int_0^t\lambda(\phi_s(x))\,ds$$

观察跳点序列时可得到 Markov renewal 或半 Markov 结构，但 PDMP 还保留跳跃之间的完整连续轨迹。

## 二十四、精确逆变换仿真

采样：

$$E\sim\operatorname{Exp}(1)$$

然后求解：

$$\int_0^{\tau}\lambda(\phi_s(x))\,ds=E$$

若解 $\tau\lt t^{\star}(x)$，则在 $\tau$ 发生随机跳跃；否则先到达边界并执行强制跳跃。跳前状态为 $\phi_{\tau}(x)$，跳后状态从 $Q$ 采样。

当累计 hazard 可解析积分或可稳定求根时，这是自然的事件驱动精确方法。

## 二十五、Thinning 仿真

若沿轨迹存在可计算上界：

$$\lambda(\phi_s(x))\leq\overline\lambda(s)$$

先根据 $\overline\lambda$ 生成候选事件，在候选时刻 $t$ 以概率：

$$\frac{\lambda(\phi_t(x))}{\overline\lambda(t)}$$

接受。被拒绝的候选不会改变系统状态。

常数上界过大时会产生大量拒绝；可使用分段上界、自适应上界或局部 Lipschitz 界提高效率。

## 二十六、数值 ODE 与事件定位

当流没有闭式解时，需要数值积分：

$$\dot z=F(m,z)$$

同时积分累计 hazard：

$$\dot h=\lambda(m,z),\qquad h(0)=0$$

事件发生于 $h=E$ 或守卫函数 $g(z)=0$ 的首次根。求解器必须支持 event detection，避免固定大步长跨过边界或漏掉高强度区间。

## 二十七、仿真伪流程

单条轨迹的基本流程为：

1. 初始化状态、时间和终止时刻；
2. 采样单位指数随机变量；
3. 联立积分状态与累计 hazard；
4. 比较随机事件时间和边界到达时间；
5. 确定事件类型并从跳核采样；
6. 更新状态并重复；
7. 记录跳前、跳后状态和事件累计风险。

固定时间网格只用于输出或控制刷新，不应替代真正的事件定位。

## 二十八、似然函数

若完整观察跳跃时刻和状态，且跳核有密度 $q$，忽略与参数无关项时：

$$\log L(\theta)=\sum_{n:T_n\leq T}\log\lambda_{\theta}(X_{T_n^-})+\sum_{n:T_n\leq T}\log q_{\theta}(X_{T_n^-},X_{T_n})-\int_0^T\lambda_{\theta}(X_s)\,ds$$

若有多事件类型，应使用对应 $\lambda_{k,\theta}$ 和 $q_{k,\theta}$。强制边界跳跃不能误计为随机 hazard 事件。

## 二十九、参数估计

最大似然估计为：

$$\widehat\theta\in\operatorname*{arg\,max}_{\theta}\log L(\theta)$$

还可利用鞅估计方程：

$$\sum_k\int_0^T\psi_k(X_{t^-};\theta)\left[dN_t^k-\lambda_k(X_{t^-};\theta)dt\right]=0$$

若连续状态只在离散时刻带噪观测，则需要粒子滤波、EM、数据增广或模拟似然。

## 三十、模型诊断

若模型正确，每个随机事件的累计 hazard 增量：

$$E_n=\int_{T_{n-1}}^{T_n}\lambda(X_s)\,ds$$

在适当条件下应近似独立同分布为 $\operatorname{Exp}(1)$。可进一步变换：

$$U_n=1-e^{-E_n}$$

其应近似服从 $\operatorname{Uniform}(0,1)$。这就是 time-rescaling 诊断。

还应分别检查事件类型概率、跳后状态分布、边界事件比例和连续流残差。

## 三十一、受控 PDMP

控制 $a_t$ 可影响流、强度和跳核：

$$\dot X_t=F(X_t,a_t)$$

$$\lambda=\lambda(X_t,a_t)$$

$$Q=Q(\cdot\mid X_t,a_t)$$

折扣成本目标为：

$$V(x)=\inf_{\pi}\mathbb E_x^{\pi}\left[\int_0^{\infty}e^{-\beta t}c(X_t,A_t)\,dt+\sum_n e^{-\beta T_n}k(X_{T_n^-},X_{T_n})\right]$$

控制可在连续时间调整，也可限制为只在事件时刻或固定决策时刻更新。

## 三十二、受控生成元

固定动作 $a$ 下：

$$\mathcal L^af(x)=\nabla f(x)^{\mathsf T}F(x,a)+\lambda(x,a)\int_E\left[f(y)-f(x)\right]Q(dy\mid x,a)$$

动作可改变：

1. 连续移动和资源变化速度；
2. 事件到达概率；
3. 事件发生后的结果分布；
4. 即时运行成本与跳跃成本。

必须避免把同一动作效应同时重复计入流和跳核。

## 三十三、无限时域 HJB

对折扣成本最小化，形式 HJB 方程为：

$$\beta V(x)=\inf_{a\in\mathcal A(x)}\left\{c(x,a)+\nabla V(x)^{\mathsf T}F(x,a)+\lambda(x,a)\int_E[V(y)-V(x)]Q(dy\mid x,a)\right\}$$

最优反馈动作满足：

$$a^{\star}(x)\in\operatorname*{arg\,min}_{a\in\mathcal A(x)}\left\{c(x,a)+\mathcal L^aV(x)\right\}$$

由于跳跃积分项是非局部的，该方程是非局部一阶 HJB。

## 三十四、有限时域 HJB

设终端成本为 $g$，则：

$$V(T,x)=g(x)$$

在终端前：

$$-\frac{\partial V}{\partial t}(t,x)=\inf_a\left\{c(t,x,a)+\mathcal L_t^aV(t,x)\right\}$$

边界强制跳跃要求价值满足：

$$V(t,x)=\int_E\left[k(x,y)+V(t,y)\right]Q_{\partial}(x,dy),\qquad x\in\partial E$$

## 三十五、事件时刻动态规划

也可把问题嵌入跳跃时刻。对当前状态 $x$ 和等待期间控制 $a(\cdot)$，比较下一事件前的运行成本、事件成本和跳后价值：

$$V(x)=\inf_{a(\cdot)}\mathbb E_x\left[\int_0^{T_1}e^{-\beta t}c(X_t,a_t)\,dt+e^{-\beta T_1}\{k(X_{T_1^-},X_{T_1})+V(X_{T_1})\}\right]$$

这种写法将连续时间控制转化为事件间的确定性最优控制加跳点递归。

## 三十六、脉冲控制

若决策者可主动在任意时刻把状态从 $x$ 重置到 $\Gamma(x,\xi)$，定义干预算子：

$$\mathcal MV(x)=\inf_{\xi\in\Xi(x)}\left\{K(x,\xi)+V(\Gamma(x,\xi))\right\}$$

有限时域成本最小化的 QVI 可写为：

$$\min\left\{-\frac{\partial V}{\partial t}-\inf_a[c+\mathcal L^aV],\ \mathcal MV-V\right\}=0$$

继续区满足 HJB，干预区满足：

$$V=\mathcal MV$$

## 三十七、最优停止

若可选择停止并支付终止成本 $g(x)$，价值满足障碍问题：

$$V(x)\leq g(x)$$

折扣无限时域的 QVI 为：

$$\min\left\{\beta V-\inf_a[c+\mathcal L^aV],\ g-V\right\}=0$$

停止区满足 $V=g$，继续区满足 HJB。设备更换、撤退、终止任务和退出市场都可用该结构。

## 三十八、部分可观测 PDMP

若真实状态 $X_t$ 不完全可见，观测历史生成信念：

$$b_t(dx)=\mathbb P(X_t\in dx\mid\mathcal Y_t)$$

两次观测或事件之间，信念按流、存活信息和观测模型连续更新；事件到达和标记会触发 Bayes 跳跃。扩充后的信念过程可作为完全可观测控制状态。

“某段时间没有发生事件”本身也包含信息，因为它改变对高强度状态的后验概率。

## 三十九、过滤中的存活更新

若初始状态不确定且尚未观察到跳跃，未归一化信念为：

$$\widetilde b_t(dx)\propto b_0(dx_0)\mathbf 1\{x=\phi_t(x_0)\}\exp\left[-\int_0^t\lambda(\phi_s(x_0))ds\right]$$

归一化后得到条件于“截至 $t$ 无事件”的后验。高 hazard 初始状态因为长期未发生事件而获得更低后验权重。

## 四十、Hawkes 过程的 PDMP 表示

对指数核 Hawkes 过程，强度可写成状态：

$$d\lambda_t=-\beta(\lambda_t-\mu)dt+\alpha dN_t$$

两次事件之间：

$$\frac{d\lambda_t}{dt}=-\beta(\lambda_t-\mu)$$

事件发生时：

$$\lambda_t=\lambda_{t^-}+\alpha$$

因此 $(N_t,\lambda_t)$ 是 PDMP。一般非指数记忆核可能需要无限维状态或近似展开。

## 四十一、神经元放电模型

Integrate-and-Fire 神经元的膜电位满足：

$$\frac{dV_t}{dt}=F(V_t,I_t)$$

放电强度可为 $\lambda(V_t)$，或在电位到达阈值时强制放电。放电后重置：

$$V_t=V_{\mathrm{reset}}$$

神经网络耦合时，一个神经元放电还会使其他神经元电位跳变，形成高维交互 PDMP。

## 四十二、可靠性与维护

设备健康状态 $H_t$ 随时间退化：

$$\dot H_t=-d(H_t)$$

故障强度随着健康下降而增加：

$$\lambda_{\mathrm{fail}}(H_t)=\lambda_0e^{\alpha(1-H_t)}$$

故障后进入维修模式，维修完成后跳回健康状态。控制可以选择检查、降载、预防维修或更换，并通过 HJB 或 QVI 优化总成本。

## 四十三、排队和通信系统

队列工作量在无到达时按服务速率下降：

$$\dot W_t=-c\mathbf 1\{W_t\gt0\}$$

到达事件使工作量跳增：

$$W_t=W_{t^-}+S_n$$

若到达强度依赖拥塞状态，系统构成 PDMP。路由、服务率和准入控制可改变流或跳跃机制。

## 四十四、稀有事件估计

目标可能是估计在时域 $T$ 内进入失效集 $B$ 的概率：

$$p_B=\mathbb P_x(\tau_B\leq T)$$

当 $p_B$ 很小时，普通 Monte Carlo 需要大量样本。可使用重要性采样、Adaptive Multilevel Splitting、Subset Simulation 或 change of measure。

改变跳跃强度和跳核后，必须使用完整似然比校正，不能只修改事件概率而忽略等待时间密度。

## 四十五、数值方法

受控 PDMP 常用方法包括：

1. 半拉格朗日离散化；
2. 有限体积求解前向方程；
3. 事件时刻动态规划；
4. 值迭代和策略迭代；
5. 基函数或神经网络价值逼近；
6. Monte Carlo 与回归；
7. 粒子滤波和 belief-space control。

数值网格必须解析边界、重置面和高 hazard 区域，否则误差会集中在最重要的事件附近。

## 四十六、5v5 游戏状态模型

可将游戏状态写为：

$$X_t=(M_t,Z_t)$$

离散模式 $M_t$ 包含存活、死亡、回城、施法、控制、复活和目标阶段；连续状态 $Z_t$ 包含位置、朝向、血量、法力、冷却、持续效果和资源。

两次关键事件之间，移动、回复、持续伤害和冷却按确定性或近似确定性动力学演化。

## 四十七、游戏事件与强度

事件类型可包括：

- 技能命中或落空；
- 暴击与被动触发；
- 击杀、死亡与复活；
- 野怪和大型目标刷新；
- 视野发现与丢失；
- 传送完成或被打断；
- 装备购买和等级提升。

第 $k$ 类事件强度可写为：

$$\lambda_k(x,a)=\lambda_k^{0}(x)\exp\{\theta_k^{\mathsf T}\psi(x,a)\}$$

但确定倒计时事件应建成边界触发，不应强行拟合成随机指数等待时间。

## 四十八、游戏控制与价值

动作可改变移动流、技能命中强度和事件结果：

$$F=F(x,a),\qquad \lambda_k=\lambda_k(x,a),\qquad Q_k=Q_k(\cdot\mid x,a)$$

游戏价值可以组合持续收益和事件收益：

$$J^{\pi}(x)=\mathbb E_x^{\pi}\left[\int_0^Te^{-\beta t}r_c(X_t,A_t)dt+\sum_{k:T_k\leq T}e^{-\beta T_k}r_k(X_{T_k^-},X_{T_k})+e^{-\beta T}g(X_T)\right]$$

持续收益包括占位、视野和资源控制；跳跃收益包括击杀、推塔和目标获取。

## 四十九、工程验收清单

一个可信的 PDMP 实现至少应检查：

1. 状态是否包含所有决定流、hazard 和跳核的变量；
2. 流是否满足半群或正确的非齐次扩充；
3. 随机事件与强制边界事件是否分开；
4. 累计 hazard 是否单调并正确定位根；
5. 跳后状态是否始终落在合法状态空间；
6. 是否排除了有限时间事件爆炸；
7. time-rescaling 后的事件残差是否合理；
8. 仿真步长变化是否不改变事件统计；
9. HJB、边界条件和跳跃积分是否一致；
10. 游戏回放中的动作前后时间戳是否没有信息泄漏。

还应使用可解析特例验证等待时间、状态分布、生成元矩和价值函数。

## 五十、结论

PDMP 用确定性流描述事件之间的连续演化，用状态相关强度描述随机事件何时发生，用转移核描述事件带来的状态重置。它既保留连续时间物理结构，又避免在每个微小时间步人为注入随机噪声。

生成元把输运和跳跃统一在一个算子中，由此得到 Dynkin 公式、Kolmogorov 方程、似然和 HJB。精确仿真应基于累计 hazard 或 thinning，并显式处理边界事件；受控系统还可结合最优停止、脉冲控制和部分可观测过滤。

在 5v5 游戏中，PDMP 适合作为事件驱动世界模型：位置、冷却和持续效果沿流变化，命中、击杀、刷新、传送和死亡通过跳跃处理。它可以连接高频局部控制、事件级策略评估和长期资源规划，但必须把确定倒计时、随机事件、隐藏信息和玩家控制分别建模。
