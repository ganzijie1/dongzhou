# Wasserstein 梯度流与 Fokker–Planck 方程：JKO 格式、连续性方程与熵耗散

## 摘要

经典梯度下降让有限维变量沿函数最陡下降方向运动。Wasserstein 梯度流把这一思想推广到概率分布空间：变量不再是向量，而是随时间演化的概率测度；距离不再是 Euclidean 距离，而是最优输运给出的 Wasserstein 距离。概率质量通过连续性方程移动，自由能沿最陡下降方向耗散。

Fokker–Planck 方程描述随机微分方程的概率密度演化。在线性漂移扩散情形，它恰好是由势能与 Boltzmann 熵组成的自由能在二阶 Wasserstein 空间中的梯度流。Jordan、Kinderlehrer 与 Otto 提出的 JKO 格式用一系列“输运代价加自由能”的隐式最小化问题离散这一演化，是 minimizing movement 方法在概率测度空间中的典型实现。

本文从概率测度、最优输运、Benamou-Brenier 动力学公式和连续性方程出发，推导 Wasserstein 梯度流、热方程、Fokker–Planck 方程、JKO 迭代、熵耗散、Fisher 信息、相对熵、位移凸性、EVI、指数收敛及数值方法，并讨论它们在 5v5 MOBA 群体位置分布、战争迷雾信念、风险势场和多智能体宏观流动中的使用边界。

## 一、从点状态到概率分布

有限维状态写为：

$$x(t)\in\mathbb R^d$$

分布状态写为概率测度：

$$\rho_t\in\mathcal P(\mathbb R^d)$$

若 $\rho_t$ 关于 Lebesgue 测度有密度，仍用 $\rho_t(x)$ 表示，并满足：

$$\rho_t(x)\ge0$$

$$\int_{\mathbb R^d}\rho_t(x)dx=1$$

分布演化既要改变形状，也必须保持非负性与总质量。

## 二、二阶矩空间

二阶 Wasserstein 空间定义为：

$$\mathcal P_2(\mathbb R^d)=\left\{\rho\in\mathcal P(\mathbb R^d)\mid\int_{\mathbb R^d}\lVert x\rVert^2d\rho(x)\lt\infty\right\}$$

有限二阶矩保证二次输运代价有限。

分布均值为：

$$m(\rho)=\int_{\mathbb R^d}x\,d\rho(x)$$

二阶矩为：

$$M_2(\rho)=\int_{\mathbb R^d}\lVert x\rVert^2d\rho(x)$$

## 三、推前测度

给定可测映射：

$$T:\mathbb R^d\rightarrow\mathbb R^d$$

推前测度记为：

$$T_{\#}\mu$$

其定义满足：

$$T_{\#}\mu(B)=\mu(T^{-1}(B))$$

对任意测试函数 $\varphi$：

$$\int\varphi(y)d(T_{\#}\mu)(y)=\int\varphi(T(x))d\mu(x)$$

推前描述质量粒子经过映射 $T$ 后形成的新分布。

## 四、输运计划

给定边缘分布 $\mu$ 与 $\nu$，耦合集合为：

$$\Pi(\mu,\nu)=\{\gamma\in\mathcal P(\mathbb R^d\times\mathbb R^d)\mid\pi^1_{\#}\gamma=\mu,\ \pi^2_{\#}\gamma=\nu\}$$

$\gamma(x,y)$ 描述从位置 $x$ 运往位置 $y$ 的联合质量。

Monge 形式要求存在确定映射 $T$：

$$T_{\#}\mu=\nu$$

Kantorovich 形式允许质量分裂，因此可解性更好。

## 五、二阶 Wasserstein 距离

二阶 Wasserstein 距离定义为：

$$W_2^2(\mu,\nu)=\inf_{\gamma\in\Pi(\mu,\nu)}\int_{\mathbb R^d\times\mathbb R^d}\lVert x-y\rVert^2d\gamma(x,y)$$

它衡量把分布 $\mu$ 搬运成 $\nu$ 所需的最小二次功。

若最优映射 $T$ 存在：

$$W_2^2(\mu,\nu)=\int_{\mathbb R^d}\lVert x-T(x)\rVert^2d\mu(x)$$

## 六、一维 Wasserstein 距离

在一维中，使用分位数函数可以显式计算：

$$W_2^2(\mu,\nu)=\int_0^1\lvert F_{\mu}^{-1}(u)-F_{\nu}^{-1}(u)\rvert^2du$$

这说明一维最优输运按分位数单调匹配。

对调试数值算法，一维公式是非常重要的基准测试。

## 七、最优映射与 Brenier 定理

若源测度 $\mu$ 关于 Lebesgue 测度绝对连续，二次代价下最优映射可写为凸函数的梯度：

$$T=\nabla\phi$$

并满足：

$$T_{\#}\mu=\nu$$

若密度足够光滑，Jacobian 关系为：

$$\mu(x)=\nu(T(x))\det(\nabla T(x))$$

这与 Monge-Ampere 方程密切相关。

## 八、位移插值

设 $T$ 是从 $\mu_0$ 到 $\mu_1$ 的最优映射。Wasserstein 测地线为：

$$\mu_t=((1-t)\mathrm{Id}+tT)_{\#}\mu_0$$

其中：

$$t\in[0,1]$$

沿这条曲线：

$$W_2(\mu_s,\mu_t)=\lvert t-s\rvert W_2(\mu_0,\mu_1)$$

这种插值移动质量，而不是逐点线性混合密度。

## 九、线性混合与位移插值

普通线性混合为：

$$\rho_t=(1-t)\rho_0+t\rho_1$$

它把两份密度叠加，可能在中间同时出现两个峰。

位移插值则把峰从起点连续移动到终点。对位置分布、资源流和群体迁移，位移插值通常更符合物理直觉。

## 十、连续性方程

质量密度 $\rho_t$ 在速度场 $v_t$ 下演化：

$$\partial_t\rho_t+\nabla\cdot(\rho_tv_t)=0$$

该方程表达局部质量守恒。

若区域 $\Omega$ 有边界并要求无通量：

$$\rho_tv_t\cdot n=0,\qquad x\in\partial\Omega$$

则总质量保持：

$$\frac{d}{dt}\int_{\Omega}\rho_tdx=0$$

## 十一、连续性方程的弱形式

对光滑紧支撑测试函数 $\varphi$：

$$\frac{d}{dt}\int_{\Omega}\varphi(x)\rho_t(x)dx=\int_{\Omega}\nabla\varphi(x)\cdot v_t(x)\rho_t(x)dx$$

弱形式不要求密度和速度都经典光滑，适合测度解。

若 $\varphi=1$，右端为零，从而得到质量守恒。

## 十二、Benamou-Brenier 公式

Wasserstein 距离具有动力学表示：

$$W_2^2(\rho_0,\rho_1)=\inf_{\rho_t,v_t}\int_0^1\int_{\mathbb R^d}\rho_t(x)\lVert v_t(x)\rVert^2dxdt$$

约束为：

$$\partial_t\rho_t+\nabla\cdot(\rho_tv_t)=0$$

$$\rho_{t=0}=\rho_0,\qquad\rho_{t=1}=\rho_1$$

因此 $W_2^2$ 是最小动能。

## 十三、动量变量

令：

$$m_t=\rho_tv_t$$

连续性方程变为：

$$\partial_t\rho_t+\nabla\cdot m_t=0$$

作用量写为：

$$\int_0^1\int\frac{\lVert m_t\rVert^2}{\rho_t}dxdt$$

函数 $\lVert m\rVert^2/\rho$ 对 $(\rho,m)$ 是凸的，这为数值优化提供便利。

## 十四、绝对连续曲线

若曲线 $\rho_t$ 在 $W_2$ 中绝对连续，则存在速度场 $v_t$，满足连续性方程，并且：

$$\lVert\dot\rho_t\rVert_{W_2}^2=\inf_{v_t}\int\rho_t\lVert v_t\rVert^2dx$$

最小范数速度通常位于梯度场闭包中：

$$v_t=\nabla\psi_t$$

这构成 Otto 形式微分几何的切空间直觉。

## 十五、Euclidean 梯度流

有限维能量 $E(x)$ 的梯度流为：

$$\dot x_t=-\nabla E(x_t)$$

能量耗散：

$$\frac{d}{dt}E(x_t)=-\lVert\nabla E(x_t)\rVert^2$$

隐式 Euler 格式为：

$$x_{k+1}=\mathop{\arg\min}_x\left\{\frac{\lVert x-x_k\rVert^2}{2\tau}+E(x)\right\}$$

JKO 格式正是把 Euclidean 距离换成 $W_2$。

## 十六、概率测度上的自由能

设自由能泛函：

$$\mathcal F:\mathcal P_2(\mathbb R^d)\rightarrow(-\infty,\infty]$$

沿扰动 $\rho_\epsilon$ 的一阶变化定义第一变分：

$$\left.\frac{d}{d\epsilon}\mathcal F(\rho_\epsilon)\right|_{\epsilon=0}=\int\frac{\delta\mathcal F}{\delta\rho}(x)\left.\frac{d\rho_\epsilon}{d\epsilon}\right|_{\epsilon=0}dx$$

第一变分：

$$\frac{\delta\mathcal F}{\delta\rho}$$

对应有限维中的梯度势。

## 十七、Wasserstein 梯度

自由能的 Wasserstein 最陡下降速度为：

$$v_t=-\nabla\frac{\delta\mathcal F}{\delta\rho}(\rho_t)$$

代入连续性方程：

$$\partial_t\rho_t=\nabla\cdot\left(\rho_t\nabla\frac{\delta\mathcal F}{\delta\rho}(\rho_t)\right)$$

这就是形式上的 Wasserstein 梯度流方程。

符号中的正散度来自速度场带有负梯度。

## 十八、势能

外部势能为：

$$\mathcal V(\rho)=\int_{\mathbb R^d}V(x)\rho(x)dx$$

第一变分为：

$$\frac{\delta\mathcal V}{\delta\rho}=V$$

对应梯度流：

$$\partial_t\rho=\nabla\cdot(\rho\nabla V)$$

其速度场为：

$$v=-\nabla V$$

质量沿势能下降方向输运。

## 十九、Boltzmann 熵

本文采用数学文献中的熵泛函约定：

$$\mathcal H(\rho)=\int_{\mathbb R^d}\rho\log\rho\,dx$$

它是物理 Shannon 熵的负值。第一变分为：

$$\frac{\delta\mathcal H}{\delta\rho}=\log\rho+1$$

因此：

$$\nabla\frac{\delta\mathcal H}{\delta\rho}=\frac{\nabla\rho}{\rho}$$

## 二十、热方程是熵的梯度流

把 $\mathcal F=\mathcal H$ 代入 Wasserstein 梯度流：

$$\partial_t\rho=\nabla\cdot\left(\rho\nabla(\log\rho+1)\right)$$

利用：

$$\rho\nabla\log\rho=\nabla\rho$$

得到：

$$\partial_t\rho=\Delta\rho$$

因此热方程是 Boltzmann 熵在 $W_2$ 几何下的最陡下降流。

## 二十一、自由能

温度或扩散参数为 $\beta^{-1}$。自由能定义为：

$$\mathcal F(\rho)=\frac{1}{\beta}\int\rho\log\rho\,dx+\int V\rho\,dx$$

第一变分为：

$$\frac{\delta\mathcal F}{\delta\rho}=\frac{1}{\beta}(\log\rho+1)+V$$

对应梯度流：

$$\partial_t\rho=\frac{1}{\beta}\Delta\rho+\nabla\cdot(\rho\nabla V)$$

这就是过阻尼 Fokker–Planck 方程。

## 二十二、随机微分方程

考虑 Langevin 随机微分方程：

$$dX_t=-\nabla V(X_t)dt+\sqrt{\frac{2}{\beta}}dB_t$$

$B_t$ 是标准 Brownian 运动。

若 $X_t$ 的密度为 $\rho_t$，则其前向 Kolmogorov 方程为：

$$\partial_t\rho_t=\nabla\cdot(\rho_t\nabla V)+\frac{1}{\beta}\Delta\rho_t$$

粒子随机动力学与分布梯度流给出同一个密度演化。

## 二十三、一般 Fokker–Planck 方程

对 Itô 扩散：

$$dX_t=b(X_t,t)dt+\sigma(X_t,t)dB_t$$

扩散矩阵为：

$$a=\sigma\sigma^\top$$

密度满足：

$$\partial_t\rho=-\sum_i\partial_i(b_i\rho)+\frac{1}{2}\sum_{i,j}\partial_{ij}(a_{ij}\rho)$$

只有在漂移与扩散满足适当结构时，它才是标准 $W_2$ 梯度流。

## 二十四、非梯度漂移

若：

$$b=-\nabla V+c$$

且 $c$ 不是某个势的梯度，则 Fokker–Planck 方程包含旋转或非可逆部分。

可以形式上分解为：

$$\partial_t\rho=\nabla\cdot\left(\rho\nabla\frac{\delta\mathcal F}{\delta\rho}\right)-\nabla\cdot(\rho c)$$

第一项耗散自由能，第二项是输运。非可逆动力学一般不能完全解释为纯 Wasserstein 梯度流。

## 二十五、平衡 Gibbs 分布

稳态零通量条件为：

$$\frac{1}{\beta}\nabla\rho_\infty+\rho_\infty\nabla V=0$$

因此：

$$\nabla\log\rho_\infty=-\beta\nabla V$$

得到：

$$\rho_\infty(x)=\frac{1}{Z}e^{-\beta V(x)}$$

归一化常数为：

$$Z=\int_{\mathbb R^d}e^{-\beta V(x)}dx$$

## 二十六、相对熵表示

对 Gibbs 分布 $\rho_\infty$，相对熵为：

$$\mathrm{KL}(\rho\Vert\rho_\infty)=\int\rho\log\frac{\rho}{\rho_\infty}dx$$

自由能与相对熵关系为：

$$\mathcal F(\rho)-\mathcal F(\rho_\infty)=\frac{1}{\beta}\mathrm{KL}(\rho\Vert\rho_\infty)$$

因此自由能下降等价于向平衡分布的相对熵下降。

## 二十七、自由能耗散

沿 Wasserstein 梯度流：

$$\frac{d}{dt}\mathcal F(\rho_t)=\int\frac{\delta\mathcal F}{\delta\rho}\partial_t\rho_tdx$$

代入方程并分部积分：

$$\frac{d}{dt}\mathcal F(\rho_t)=-\int\rho_t\left\lVert\nabla\frac{\delta\mathcal F}{\delta\rho}\right\rVert^2dx$$

所以：

$$\frac{d}{dt}\mathcal F(\rho_t)\le0$$

右端是自由能耗散率。

## 二十八、Fisher 信息

相对于 $\rho_\infty$ 的相对 Fisher 信息定义为：

$$\mathcal I(\rho\Vert\rho_\infty)=\int\rho\left\lVert\nabla\log\frac{\rho}{\rho_\infty}\right\rVert^2dx$$

Fokker–Planck 自由能耗散为：

$$\frac{d}{dt}\mathrm{KL}(\rho_t\Vert\rho_\infty)=-\frac{1}{\beta}\mathcal I(\rho_t\Vert\rho_\infty)$$

具体系数取决于扩散参数约定，使用时必须保持 SDE、自由能和 PDE 的系数一致。

## 二十九、热方程的熵耗散

对：

$$\partial_t\rho=\Delta\rho$$

Boltzmann 熵满足：

$$\frac{d}{dt}\mathcal H(\rho_t)=-\int\frac{\lVert\nabla\rho_t\rVert^2}{\rho_t}dx$$

也可写为：

$$\frac{d}{dt}\mathcal H(\rho_t)=-4\int\lVert\nabla\sqrt{\rho_t}\rVert^2dx$$

耗散项就是 Fisher 信息的一种形式。

## 三十、熵与方差的直觉

Boltzmann 熵泛函 $\mathcal H=\int\rho\log\rho$ 在扩散中下降，而物理 Shannon 熵：

$$S(\rho)=-\int\rho\log\rho\,dx$$

上升。

两种约定只差符号。讨论“熵增加”或“熵耗散”时，必须先说明采用哪一种定义。

## 三十一、对数 Sobolev 不等式

若平衡测度满足对数 Sobolev 不等式：

$$\mathrm{KL}(\rho\Vert\rho_\infty)\le\frac{1}{2\lambda}\mathcal I(\rho\Vert\rho_\infty)$$

结合熵耗散可得：

$$\frac{d}{dt}\mathrm{KL}(\rho_t\Vert\rho_\infty)\le-\frac{2\lambda}{\beta}\mathrm{KL}(\rho_t\Vert\rho_\infty)$$

因此：

$$\mathrm{KL}(\rho_t\Vert\rho_\infty)\le e^{-2\lambda t/\beta}\mathrm{KL}(\rho_0\Vert\rho_\infty)$$

## 三十二、Talagrand 不等式

适当条件下：

$$W_2^2(\rho,\rho_\infty)\le\frac{2}{\beta\kappa}\mathrm{KL}(\rho\Vert\rho_\infty)$$

结合相对熵指数衰减，可得到 Wasserstein 距离收敛。

对强凸势：

$$\nabla^2V\succeq\kappa I$$

通常能够获得良好的收敛与泛函不等式。

## 三十三、JKO 格式

给定时间步长 $\tau$ 和初始分布 $\rho^0$，JKO 迭代为：

$$\rho^{k+1}=\mathop{\arg\min}_{\rho\in\mathcal P_2}\left\{\frac{1}{2\tau}W_2^2(\rho,\rho^k)+\mathcal F(\rho)\right\}$$

第一项惩罚单步搬运距离，第二项推动自由能下降。

它是 Wasserstein 空间中的隐式 Euler 或 proximal step。

## 三十四、JKO 的物理解释

每一步在两种需求之间折中：

$$\mathrm{MovementCost}=\frac{1}{2\tau}W_2^2(\rho,\rho^k)$$

$$\mathrm{EnergyCost}=\mathcal F(\rho)$$

$\tau$ 小时不允许分布单步移动过远；自由能又促使质量向低势能、高扩散平衡的方向调整。

JKO 不是把 Fokker–Planck 方程普通显式离散，而是每一步求一个全局变分问题。

## 三十五、JKO 能量下降

由于 $\rho=\rho^k$ 是可行解：

$$\frac{1}{2\tau}W_2^2(\rho^{k+1},\rho^k)+\mathcal F(\rho^{k+1})\le\mathcal F(\rho^k)$$

因此：

$$\mathcal F(\rho^{k+1})\le\mathcal F(\rho^k)$$

并且：

$$\sum_{k=0}^{N-1}W_2^2(\rho^{k+1},\rho^k)\le2\tau\left(\mathcal F(\rho^0)-\inf\mathcal F\right)$$

## 三十六、JKO 最优性条件

设 $T_{k+1\rightarrow k}$ 是从 $\rho^{k+1}$ 到 $\rho^k$ 的最优映射。形式最优性条件为：

$$\frac{T_{k+1\rightarrow k}(x)-x}{\tau}=\nabla\frac{\delta\mathcal F}{\delta\rho}(\rho^{k+1})(x)$$

因此，从新分布看向旧分布的位移对应自由能上升方向；正向演化则沿自由能下降方向。

这与隐式 Euler 条件一致。

## 三十七、Fokker–Planck 的 JKO 步

对自由能：

$$\mathcal F(\rho)=\frac{1}{\beta}\int\rho\log\rho\,dx+\int V\rho\,dx$$

JKO 步为：

$$\rho^{k+1}=\mathop{\arg\min}_{\rho}\left\{\frac{1}{2\tau}W_2^2(\rho,\rho^k)+\frac{1}{\beta}\int\rho\log\rho\,dx+\int V\rho\,dx\right\}$$

当 $\tau\rightarrow0$ 时，适当插值的离散解收敛到 Fokker–Planck 方程的弱解。

## 三十八、离散速度

由最优映射定义离散速度：

$$v^{k+1}(x)=\frac{x-T_{k+1\rightarrow k}(x)}{\tau}$$

根据最优性条件：

$$v^{k+1}=-\nabla\frac{\delta\mathcal F}{\delta\rho}(\rho^{k+1})$$

离散连续性方程在弱意义上逼近：

$$\frac{\rho^{k+1}-\rho^k}{\tau}+\nabla\cdot(\rho^{k+1}v^{k+1})=0$$

## 三十九、Minimizing Movement

定义分段常数插值：

$$\rho_\tau(t)=\rho^k,\qquad t\in[k\tau,(k+1)\tau)$$

利用能量下降、二阶矩控制和离散动作量估计，可以提取子序列：

$$\rho_{\tau_j}\rightarrow\rho$$

极限曲线称为 generalized minimizing movement，并在适当条件下满足目标梯度流。

## 四十、测地凸性

泛函 $\mathcal F$ 沿 Wasserstein 测地线 $\rho_t$ 为 $\lambda$ 位移凸，如果：

$$\mathcal F(\rho_t)\le(1-t)\mathcal F(\rho_0)+t\mathcal F(\rho_1)-\frac{\lambda}{2}t(1-t)W_2^2(\rho_0,\rho_1)$$

位移凸性不同于对密度线性混合的普通凸性。

它提供解的唯一性、稳定性和收敛率。

## 四十一、EVI

Evolution Variational Inequality 形式为：

$$\frac{1}{2}\frac{d}{dt}W_2^2(\rho_t,\sigma)+\frac{\lambda}{2}W_2^2(\rho_t,\sigma)\le\mathcal F(\sigma)-\mathcal F(\rho_t)$$

对任意比较分布 $\sigma$ 成立。

EVI 比形式 PDE 更稳健，并能推出收缩性：

$$W_2(\rho_t,\widetilde\rho_t)\le e^{-\lambda t}W_2(\rho_0,\widetilde\rho_0)$$

## 四十二、曲线最大斜率

度量斜率定义为：

$$\lvert\partial\mathcal F\rvert(\rho)=\limsup_{\nu\rightarrow\rho}\frac{(\mathcal F(\rho)-\mathcal F(\nu))_+}{W_2(\rho,\nu)}$$

梯度流满足能量耗散不等式：

$$\mathcal F(\rho_T)+\frac{1}{2}\int_0^T\lVert\dot\rho_t\rVert_{W_2}^2dt+\frac{1}{2}\int_0^T\lvert\partial\mathcal F\rvert^2(\rho_t)dt\le\mathcal F(\rho_0)$$

在规则条件下可取等号。

## 四十三、一般内能

内能泛函为：

$$\mathcal U(\rho)=\int U(\rho(x))dx$$

第一变分为：

$$\frac{\delta\mathcal U}{\delta\rho}=U'(\rho)$$

梯度流为：

$$\partial_t\rho=\nabla\cdot(\rho\nabla U'(\rho))$$

可定义压力：

$$P(\rho)=\rho U'(\rho)-U(\rho)$$

于是：

$$\partial_t\rho=\Delta P(\rho)$$

## 四十四、多孔介质方程

取：

$$U(\rho)=\frac{\rho^m}{m-1}$$

则：

$$P(\rho)=\rho^m$$

得到多孔介质方程：

$$\partial_t\rho=\Delta(\rho^m)$$

当 $m\gt1$ 时，扩散随密度增强，并可能具有有限传播速度。

## 四十五、快速扩散

当：

$$0\lt m\lt1$$

方程：

$$\partial_t\rho=\Delta(\rho^m)$$

属于快速扩散型。低密度区域扩散更强，可能出现与多孔介质方程不同的消失、尾部和正则性行为。

不是所有 $m$ 都保证质量守恒和良好解，维数与指数条件必须单独检查。

## 四十六、相互作用能

成对相互作用能为：

$$\mathcal W(\rho)=\frac{1}{2}\int\int W(x-y)\rho(x)\rho(y)dxdy$$

第一变分为：

$$\frac{\delta\mathcal W}{\delta\rho}=W*\rho$$

梯度流贡献为：

$$\nabla\cdot(\rho\nabla(W*\rho))$$

吸引核可产生聚集，排斥核可保持分散。

## 四十七、聚集扩散方程

组合内能、外势和相互作用：

$$\mathcal F(\rho)=\int U(\rho)dx+\int V\rho dx+\frac{1}{2}\int\int W(x-y)\rho(x)\rho(y)dxdy$$

梯度流为：

$$\partial_t\rho=\nabla\cdot\left(\rho\nabla(U'(\rho)+V+W*\rho)\right)$$

该模型统一表达扩散、环境吸引和群体相互作用。

## 四十八、McKean–Vlasov 动力学

粒子系统可写为：

$$dX_t^i=-\nabla V(X_t^i)dt-\frac{1}{N}\sum_{j=1}^{N}\nabla W(X_t^i-X_t^j)dt+\sqrt{\frac{2}{\beta}}dB_t^i$$

经验测度为：

$$\mu_t^N=\frac{1}{N}\sum_{i=1}^{N}\delta_{X_t^i}$$

当 $N$ 很大且满足适当条件时，经验测度趋向 McKean–Vlasov Fokker–Planck 方程。

## 四十九、传播混沌

传播混沌描述有限多个粒子在大系统极限中渐近独立：

$$\mathcal L(X_t^1,\ldots,X_t^k)\rightarrow\rho_t^{\otimes k}$$

这为平均场 PDE 提供粒子基础。

在 5v5 MOBA 中英雄数只有十个，不能自动使用大粒子极限；平均场更适合大量兵线单位、粒子信念或多局统计分布。

## 五十、各向异性扩散

若扩散矩阵为 $D(x)$，方程可能写为：

$$\partial_t\rho=\nabla\cdot(D\nabla\rho+\rho b_D)$$

只有在选择合适的度量、参考测度和漂移修正后，才可能解释为对应几何下的梯度流。

标准 $W_2$ 对应 isotropic mobility $\rho I$。地形速度和方向性明显时，应使用加权输运度量或 Riemannian 结构。

## 五十一、有界区域与反射边界

在区域 $\Omega$ 上，无通量边界条件为：

$$\left(\frac{1}{\beta}\nabla\rho+\rho\nabla V\right)\cdot n=0$$

它对应粒子在边界反射，不会离开区域。

吸收边界则允许质量流失：

$$\rho=0,\qquad x\in\partial\Omega$$

吸收情形下 $\rho$ 可能不再是概率密度，需要跟踪剩余质量或加入墓地状态。

## 五十二、障碍与不可通行区域

地图障碍可通过定义可行域 $\Omega$ 和无通量边界处理。

也可用高势垒：

$$V_{\kappa}(x)=\kappa\phi_{\mathrm{obstacle}}(x)$$

并让：

$$\kappa\rightarrow\infty$$

高势垒近似实现简单，但数值刚性强，并可能出现少量穿透。硬边界更忠实，网格与输运计算更复杂。

## 五十三、非平衡稳态

若存在非梯度循环流，稳态可能满足：

$$\nabla\cdot J_\infty=0$$

但：

$$J_\infty\neq0$$

这称为非平衡稳态。此时详细平衡不成立，系统有持续概率环流。

纯自由能梯度流在平衡时通量为零，因此不能完整描述这类循环动力学。

## 五十四、详细平衡

Fokker–Planck 概率通量为：

$$J=-\rho\nabla V-\frac{1}{\beta}\nabla\rho$$

详细平衡要求：

$$J_\infty=0$$

这导出 Gibbs 分布。若系统有旋转驱动、持续策略循环或外部能量注入，详细平衡可能不成立。

## 五十五、熵产生

自由能耗散率可写为：

$$\mathcal D(\rho)=\int\rho\left\lVert\nabla\frac{\delta\mathcal F}{\delta\rho}\right\rVert^2dx$$

于是：

$$\frac{d}{dt}\mathcal F(\rho_t)=-\mathcal D(\rho_t)$$

若 $\mathcal D=0$，在适当连通性条件下，系统达到临界或平衡分布。

## 五十六、De Bruijn 恒等式

设：

$$X_t=X+\sqrt{2t}Z$$

$Z$ 是标准 Gaussian 随机变量，$\rho_t$ 满足热方程。

Shannon 熵的导数与 Fisher 信息相关：

$$\frac{d}{dt}S(\rho_t)=\mathcal I(\rho_t)$$

具体常数依赖噪声参数化。它连接扩散、熵增长和信息论。

## 五十七、JKO 的存在性

JKO 单步存在通常需要：

- 自由能下半连续。
- 自由能有适当下界。
- 二阶矩得到控制。
- 极小化序列具有紧性。

直接法的核心是从极小化序列提取弱收敛子序列，并利用：

$$W_2^2(\cdot,\rho^k)$$

与 $\mathcal F$ 的下半连续性传递到极限。

## 五十八、唯一性

若自由能沿 Wasserstein 测地线严格凸或 $\lambda$ 凸，JKO 单步通常具有唯一极小值。

若相互作用势非凸，可能存在多个局部极小值：

$$\rho^{k+1}\in\mathop{\arg\min}_{\rho}\left\{\frac{1}{2\tau}W_2^2(\rho,\rho^k)+\mathcal F(\rho)\right\}$$

数值算法可能选择不同分支，解的稳定性与初值、时间步和优化误差有关。

## 五十九、时间步误差

JKO 是一阶时间离散。形式上：

$$W_2(\rho_\tau(t),\rho(t))=O(\tau^{1/2})$$

或在更强正则条件下获得更好误差率。

具体误差依赖自由能凸性、解的光滑性、空间离散和单步优化精度，不能把一个通用阶数用于所有非线性方程。

## 六十、离散梯度流

数值方法应尽量保持：

$$\rho_i^k\ge0$$

$$\sum_i\rho_i^k=1$$

$$\mathcal F(\rho^{k+1})\le\mathcal F(\rho^k)$$

普通高阶离散若破坏非负性或能量下降，可能产生负密度和虚假振荡。

结构保持比单纯局部截断误差更重要。

## 六十一、有限体积方法

把区域划分为控制体 $K$。质量更新为：

$$\rho_K^{n+1}=\rho_K^n-\frac{\Delta t}{\lvert K\rvert}\sum_{L\sim K}F_{KL}^n$$

保守通量满足：

$$F_{KL}^n=-F_{LK}^n$$

因此总质量守恒。使用上风、Scharfetter-Gummel 或离散自由能通量可以改善非负性与稳态保持。

## 六十二、Scharfetter-Gummel 通量

对漂移扩散，可在网格边上解析局部常系数问题。Bernoulli 函数为：

$$B(z)=\frac{z}{e^z-1}$$

离散通量可写成相邻密度的指数拟合组合。

该方法在强漂移下比中心差分稳定，并能较好保持 Gibbs 平衡，但在复杂非结构网格上实现更困难。

## 六十三、直接离散 JKO

可把密度表示为网格向量：

$$\rho\in\mathbb R_+^n$$

单步求解：

$$\min_{\rho}\ \frac{1}{2\tau}W_{2,h}^2(\rho,\rho^k)+\mathcal F_h(\rho)$$

约束：

$$\mathbf 1^\top\rho=1$$

难点在于离散 $W_2$ 计算和每个时间步的非线性优化。

## 六十四、熵正则最优输运

离散输运计划 $\Gamma$ 的熵正则问题为：

$$\min_{\Gamma\in\Pi(\mu,\nu)}\sum_{i,j}C_{ij}\Gamma_{ij}+\varepsilon\sum_{i,j}\Gamma_{ij}(\log\Gamma_{ij}-1)$$

Sinkhorn 迭代可高效求解，但 $\varepsilon$ 会引入平滑偏差。

在 JKO 内部使用熵正则时，必须区分物理自由能中的熵与数值输运正则熵，它们不是同一个参数。

## 六十五、Benamou-Brenier 数值法

在时空网格上优化密度与动量：

$$\min_{\rho,m}\int_0^1\int\frac{\lVert m\rVert^2}{2\rho}dxdt$$

约束：

$$\partial_t\rho+\nabla\cdot m=0$$

这可转化为凸优化，并自然处理连续性方程。

计算维度增加一个时间轴，对高维状态空间成本很高。

## 六十六、粒子方法

用粒子近似分布：

$$\rho_t^N=\frac{1}{N}\sum_{i=1}^{N}\delta_{X_t^i}$$

粒子按 SDE 或相互作用 ODE 演化。

优点是适合高维采样和个体轨迹；缺点是密度、熵和 Fisher 信息对原子测度可能不直接有限，需要核平滑、blob 方法或变分粒子近似。

## 六十七、Normalizing Flow 参数化

设基础分布为 $\rho_0$，可逆映射为 $T_\theta$：

$$\rho_\theta=(T_\theta)_{\#}\rho_0$$

优化参数化 JKO 目标：

$$\min_\theta\ \frac{1}{2\tau}W_2^2(\rho_\theta,\rho^k)+\mathcal F(\rho_\theta)$$

参数化限制可能使真实极小值不在模型族内，需同时评估表达误差与优化误差。

## 六十八、维数灾难

网格在 $d$ 维每维取 $n$ 个点时，总网格数为：

$$n^d$$

高维 Wasserstein 估计也具有较慢统计收敛。不能把二维地图上的成功方法直接扩展到包含十名英雄全部状态的高维联合密度。

常见处理包括因子化、低维潜变量、粒子法、切片 Wasserstein 和局部交互近似。

## 六十九、Wasserstein 与 KL 的区别

KL 散度为：

$$\mathrm{KL}(\rho\Vert\nu)=\int\rho\log\frac{\rho}{\nu}dx$$

它不编码底层空间距离，且支撑不重叠时可能无穷大。

$W_2$ 关注质量移动的几何距离，即使支撑分离仍可有限。两者在自由能与 JKO 中扮演不同角色：$W_2$ 是时间步的几何代价，KL 常是能量或收敛度量。

## 七十、Wasserstein 与总变差

总变差距离为：

$$\lVert\rho-\nu\rVert_{\mathrm{TV}}=\frac{1}{2}\int\lvert\rho-\nu\rvert dx$$

它衡量概率质量差异，但不关心差异发生的位置。

移动一个窄峰少量距离时，$W_2$ 会随移动距离连续变化，而总变差可能变化很大。空间运动问题通常更适合 Wasserstein 几何。

## 七十一、非质量守恒扩展

标准 $W_2$ 只比较总质量相等的测度。

若存在出生、死亡、生成和消失，可使用带源项连续性方程：

$$\partial_t\rho+\nabla\cdot(\rho v)=g$$

并采用 unbalanced optimal transport、Wasserstein-Fisher-Rao 或 Hellinger-Kantorovich 类度量。

英雄死亡、复活和兵线生成若直接作为密度质量变化，需要这类扩展或显式状态切换。

## 七十二、MOBA 群体位置密度

把大量单位或多局统计中的位置分布记为：

$$\rho_t(x)$$

外部势可组合目标吸引、塔区危险和地形：

$$V(x,t)=V_{\mathrm{objective}}(x,t)+V_{\mathrm{tower}}(x,t)+V_{\mathrm{terrain}}(x)$$

相互作用核 $W$ 描述聚集、分散或阵型间距。

宏观演化可写为：

$$\partial_t\rho=\frac{1}{\beta}\Delta\rho+\nabla\cdot(\rho\nabla(V+W*\rho))$$

## 七十三、风险势场

设敌方威胁强度为 $R(x,t)$，目标收益为 $G(x,t)$。势函数可设为：

$$V(x,t)=\alpha R(x,t)-\gamma G(x,t)$$

密度速度为：

$$v=-\nabla V-\nabla(W*\rho)$$

这给出宏观流动方向，但不能替代碰撞、技能守卫、路径连通性和离散战术状态。

## 七十四、战争迷雾信念

不可见敌人的位置信念为：

$$b_t(x)$$

无新观测时，可以用漂移扩散传播：

$$\partial_tb=-\nabla\cdot(bu)+D\Delta b$$

收到观测后再做 Bayes 更新：

$$b^+(x)=\frac{Z(o\mid x)b^-(x)}{\int Z(o\mid y)b^-(y)dy}$$

预测 PDE 与观测更新共同构成连续状态滤波，而不是单一纯梯度流。

## 七十五、兵线与群体流

大量小兵可用密度近似。道路方向形成漂移 $u(x,t)$：

$$\partial_t\rho+\nabla\cdot(\rho u)=D\Delta\rho$$

若拥挤降低速度，可令：

$$u(\rho)=u_0(1-\rho/\rho_{\max})$$

这会产生非线性守恒律与扩散耦合。标准 Wasserstein 梯度流结构是否保留，需要根据 mobility 和能量重新推导。

## 七十六、阵型形成

吸引与排斥核可表达阵型：

$$W(z)=W_{\mathrm{rep}}(z)+W_{\mathrm{att}}(z)$$

短程排斥防止重叠，较长程吸引保持队伍聚集。

稳定阵型对应自由能局部极小值，但非凸相互作用会产生多稳态、合并和模式选择。局部最小不一定具有最佳战术价值。

## 七十七、与平均场博弈的区别

Wasserstein 梯度流通常描述给定自由能下的耗散演化。

平均场博弈同时包含个体最优响应和群体分布一致性，典型耦合为 HJB 与 Fokker–Planck：

$$-\partial_tu+H(x,\nabla u)=f(x,\rho)$$

$$\partial_t\rho-\nabla\cdot(\rho D_pH(x,\nabla u))=0$$

只有特殊势博弈结构下，整体系统才可化为单一变分或梯度流。

## 七十八、与 Schrödinger Bridge 的区别

Schrödinger Bridge 在随机扩散参考过程下寻找连接给定端点分布的最可能路径。

其动态优化含有相对熵或控制能量，而 JKO 是自由能梯度流的局部隐式时间步。

两者都与最优输运和 Fokker–Planck 有关，但一个是端点约束的路径推断或控制问题，一个是耗散动力学离散。

## 七十九、参数估计

从轨迹增量：

$$\Delta X_k=X_{t_{k+1}}-X_{t_k}$$

估计局部漂移：

$$\widehat b(x)=\frac{1}{\Delta t}\mathbb E[\Delta X_k\mid X_{t_k}\approx x]$$

估计扩散：

$$\widehat a(x)=\frac{1}{\Delta t}\mathbb E[\Delta X_k\Delta X_k^\top\mid X_{t_k}\approx x]$$

离散帧、控制策略和观测噪声会共同影响估计，不能把行为策略造成的漂移误认为环境物理力。

## 八十、模型校验

质量误差为：

$$e_{\mathrm{mass}}(t)=\left\lvert\int\rho_tdx-1\right\rvert$$

非负性违例为：

$$e_{\mathrm{neg}}(t)=\int(\rho_t)_-dx$$

能量上升量为：

$$e_{\mathcal F}^k=(\mathcal F(\rho^{k+1})-\mathcal F(\rho^k))_+$$

还应检查 Wasserstein 距离、边界通量、稳态误差与 PDE 残差。

## 八十一、JKO 数值校验

单步最优性残差可写为：

$$r_k=\left\lVert\frac{T_{k+1\rightarrow k}-\mathrm{Id}}{\tau}-\nabla\frac{\delta\mathcal F}{\delta\rho}(\rho^{k+1})\right\rVert_{L^2(\rho^{k+1})}$$

离散能量不等式残差为：

$$r_{\mathcal E}^k=\left(\frac{1}{2\tau}W_2^2(\rho^{k+1},\rho^k)+\mathcal F(\rho^{k+1})-\mathcal F(\rho^k)\right)_+$$

优化器停止条件应同时控制目标下降、约束误差和这些结构残差。

## 八十二、基准问题

推荐至少验证：

1. 热方程 Gaussian 初值的解析扩散。
2. 二次势下 Ornstein-Uhlenbeck 过程。
3. 一维分位数公式与数值 $W_2$。
4. Gibbs 稳态保持。
5. 无通量边界质量守恒。
6. 多孔介质方程的 Barenblatt 型解。
7. 相互作用模型的聚集与排斥。
8. JKO 能量单调下降。

## 八十三、Ornstein-Uhlenbeck 示例

取二次势：

$$V(x)=\frac{\kappa}{2}\lVert x\rVert^2$$

Fokker–Planck 方程为：

$$\partial_t\rho=\kappa\nabla\cdot(x\rho)+\frac{1}{\beta}\Delta\rho$$

平衡分布为 Gaussian：

$$\rho_\infty(x)\propto e^{-\beta\kappa\lVert x\rVert^2/2}$$

均值指数衰减：

$$m_t=e^{-\kappa t}m_0$$

## 八十四、稳定性与扰动

若自由能是 $\lambda$ 位移凸，两个解满足：

$$W_2(\rho_t,\widetilde\rho_t)\le e^{-\lambda t}W_2(\rho_0,\widetilde\rho_0)$$

这表示初始分布误差不会放大。

若 $\lambda\lt0$，只能得到可能增长的上界。非凸多势阱系统可能对初值和噪声非常敏感。

## 八十五、常见错误

1. 把 Shannon 熵与 $\int\rho\log\rho$ 的符号混淆。
2. 忽略连续性方程中的质量守恒。
3. 把任意 Fokker–Planck 方程都称为标准 Wasserstein 梯度流。
4. 混淆物理自由能熵与 Sinkhorn 数值正则熵。
5. 把 JKO 当作普通显式 Euler。
6. 使用吸收边界却仍假设总质量为一。
7. 在非凸能量下默认解与 JKO 极小值唯一。
8. 在十英雄联合状态上直接使用高维网格。
9. 用平均场密度替代游戏规则、个体技能和离散目标状态。
10. 只看 PDE 残差，不检查非负性、质量和能量耗散。

## 八十六、最小可行落地

第一阶段只在二维地图上建模一种密度：

$$\rho_t(x,y)$$

选择：

$$\mathcal F(\rho)=D\int\rho\log\rho\,dx+\int V(x,t)\rho(x)dx$$

$V$ 只包含静态障碍近似、塔区风险和一个目标吸引项。使用无通量边界和保守有限体积法。

先验证质量、非负性、自由能和已知稳态，再加入时变敌方威胁、相互作用核与观测 Bayes 更新。

## 八十七、工程分层

推荐分层：

- 密度层：传播位置分布、威胁场或群体宏观流。
- 图规划层：处理道路连通、技能条件和离散战术阶段。
- 个体控制层：处理碰撞、施法和短时反馈。
- 安全层：处理塔区、障碍和不可接受风险。

信息流可写为：

$$o_t\rightarrow\rho_t\rightarrow(V_t,W_t)\rightarrow v_t\rightarrow g_t\rightarrow a_t^{\mathrm{safe}}$$

密度模型提供软引导和不确定性，不应绕过图可达性与游戏合法性。

## 八十八、结论

Wasserstein 梯度流把概率分布的演化解释为自由能在最优输运几何下的最陡下降。连续性方程保证质量守恒，速度场由自由能第一变分的负梯度产生。热方程是 Boltzmann 熵的梯度流，过阻尼 Fokker–Planck 方程是熵与外部势能组成的自由能梯度流。

JKO 格式用“单步输运代价加新分布自由能”的最小化问题实现隐式时间离散。它天然给出自由能单调下降和离散动作量控制，并通过 minimizing movement 极限连接到 PDE。熵耗散、Fisher 信息、对数 Sobolev 不等式、位移凸性和 EVI 则提供趋向平衡、唯一性、稳定性与收敛速度。

在 MOBA 中，这套理论适合描述大量单位、多局统计密度、位置不确定性和宏观风险流动，而不适合直接替代十名英雄的离散技能、对抗博弈和路径连通逻辑。可靠实践应从二维、质量守恒、结构保持的最小模型开始，用解析基准与能量耗散校验，再逐步连接信念更新、图规划和个体安全控制。
