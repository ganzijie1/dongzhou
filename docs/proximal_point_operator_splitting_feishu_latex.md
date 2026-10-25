# Proximal Point 与 Operator Splitting

## 摘要

Proximal Point（近端点法）和 Operator Splitting（算子分裂）是现代凸优化、变分不等式、单调包含、分布式优化和博弈均衡求解的共同基础。

近端点法通过隐式更新稳定地求解单调算子的零点；算子分裂则把难以直接求逆的算子和拆成多个容易处理的子算子，分别使用梯度、投影、近端映射或线性求解器。Forward–Backward、Douglas–Rachford、Peaceman–Rachford、ADMM、Three-Operator Splitting 和原始–对偶算法都可以放进这个统一框架。

本文介绍基本定义、resolvent 与 proximal operator、主要算法、收敛条件、算法之间的关系、数值残差，以及它们在 5v5 游戏策略、资源约束、团队共识和均衡计算中的应用。

## 一、统一问题：单调包含

设 $\mathcal H$ 是有限维欧氏空间，算子 $A$ 可以是多值映射：

$$A:\mathcal H\rightrightarrows\mathcal H$$

基本目标是寻找 $x^*$，使得：

$$0\in A(x^*)$$

更常见的是两个或多个算子的和：

$$0\in A(x^*)+B(x^*)$$

或者：

$$0\in A(x^*)+B(x^*)+C(x^*)$$

直接求解 $(A+B)^{-1}$ 往往困难，但 $A$ 和 $B$ 各自的 resolvent、梯度或投影可能很容易计算。算子分裂的目标就是在不直接求逆算子和的情况下找到共同零点。

## 二、单调算子

算子 $A$ 称为单调算子，如果对任意 $u\in A(x)$ 和 $v\in A(y)$ 都有：

$$\langle u-v,x-y\rangle\geq 0$$

若不存在图像严格包含 $\operatorname{gra}(A)$ 的其他单调算子，则称 $A$ 为极大单调算子。

极大单调性不是“数值最大”，而是说算子的单调图像不能再添加新的点而保持单调。这个条件保证 resolvent 在整个空间上具有良好定义。

### 1. 强单调性

若存在 $\mu>0$，使得：

$$\langle u-v,x-y\rangle\geq\mu\lVert x-y\rVert^2$$

则称 $A$ 为 $\mu$-强单调算子。强单调性通常带来零点唯一性和更快的收敛。

### 2. 余强单调性

单值算子 $B$ 称为 $\beta$-cocoercive，如果：

$$\langle Bx-By,x-y\rangle\geq\beta\lVert Bx-By\rVert^2$$

若 $f$ 是凸函数且梯度为 $L$-Lipschitz，则在标准有限维条件下：

$$\nabla f\text{ 是 }\frac{1}{L}\text{-cocoercive}$$

这正是 Forward–Backward 中显式梯度步的典型条件。

## 三、Resolvent 与反射算子

给定步长 $\lambda>0$，算子 $A$ 的 resolvent 定义为：

$$J_{\lambda A}=(I+\lambda A)^{-1}$$

若 $z=J_{\lambda A}(x)$，则：

$$x\in z+\lambda A(z)$$

等价地：

$$\frac{x-z}{\lambda}\in A(z)$$

当 $A$ 极大单调时，$J_{\lambda A}$ 是单值、全域且 firmly nonexpansive：

$$\lVert Jx-Jy\rVert^2\leq\langle Jx-Jy,x-y\rangle$$

反射 resolvent 定义为：

$$R_{\lambda A}=2J_{\lambda A}-I$$

Douglas–Rachford 和 Peaceman–Rachford 正是由这些反射算子组成。

## 四、Proximal Operator

若 $f$ 是正常、下半连续、凸函数，并令：

$$A=\partial f$$

则 resolvent 就是 proximal operator：

$$J_{\lambda\partial f}=\operatorname{prox}_{\lambda f}$$

其定义为：

$$\operatorname{prox}_{\lambda f}(x)=\arg\min_z\left\{f(z)+\frac{1}{2\lambda}\lVert z-x\rVert^2\right\}$$

近端映射不是简单地对目标函数加一个固定正则项；它在每一步使用当前迭代点作为二次中心，求一个隐式、局部稳定的子问题。

### 1. 指示函数与投影

闭凸集 $K$ 的指示函数定义为：

$$\iota_K(x)=0\text{ 当 }x\in K,\qquad \iota_K(x)=+\infty\text{ 当 }x\notin K$$

它的近端映射就是投影：

$$\operatorname{prox}_{\iota_K}(x)=\Pi_K(x)$$

### 2. 一范数与软阈值

对于 $f(x)=\tau\lVert x\rVert_1$，近端映射为逐分量软阈值：

$$\operatorname{prox}_{\lambda f}(x)_i=\operatorname{sign}(x_i)\max\left(|x_i|-\lambda\tau,0\right)$$

### 3. Moreau envelope

Moreau envelope 定义为：

$$e_{\lambda f}(x)=\min_z\left\{f(z)+\frac{1}{2\lambda}\lVert z-x\rVert^2\right\}$$

在凸情形下，它是原函数的光滑化，并满足：

$$\nabla e_{\lambda f}(x)=\frac{1}{\lambda}\left(x-\operatorname{prox}_{\lambda f}(x)\right)$$

## 五、Proximal Point Algorithm

近端点法求解：

$$0\in A(x^*)$$

其精确迭代为：

$$x_{k+1}=J_{\lambda_k A}(x_k)$$

等价地：

$$0\in A(x_{k+1})+\frac{1}{\lambda_k}(x_{k+1}-x_k)$$

这是一个隐式更新，因为算子在新点 $x_{k+1}$ 处评价。与显式梯度步相比，它通常更稳定。

### 1. 凸优化形式

当 $A=\partial f$ 时：

$$x_{k+1}=\arg\min_x\left\{f(x)+\frac{1}{2\lambda_k}\lVert x-x_k\rVert^2\right\}$$

### 2. 固定点解释

零点 $x^*$ 满足：

$$x^*=J_{\lambda A}(x^*)$$

所以近端点法是 resolvent 的固定点迭代。

### 3. 基本收敛性质

对极大单调算子，在零点存在且步长保持正值等标准条件下，近端点迭代收敛到一个零点。在有限维空间中，弱收敛与强收敛的区别消失，但无限维结论需要单独说明。

若 $A$ 为 $\mu$-强单调，则 resolvent 是压缩映射：

$$\lVert J_{\lambda A}(x)-J_{\lambda A}(y)\rVert\leq\frac{1}{1+\lambda\mu}\lVert x-y\rVert$$

因此可以得到线性收敛。

### 4. 非精确近端点法

实际子问题通常只近似求解，可写为：

$$x_{k+1}\approx J_{\lambda_k A}(x_k)$$

经典理论通常要求误差可求和或满足相对误差准则。若内层误差长期不衰减，外层的近端稳定性不能保证最终精度。

## 六、为什么需要 Operator Splitting

考虑复合凸优化：

$$\min_x f(x)+g(x)$$

一阶条件为：

$$0\in\partial f(x)+\partial g(x)$$

即使 $\operatorname{prox}_f$ 和 $\operatorname{prox}_g$ 都容易计算，$\operatorname{prox}_{f+g}$ 通常没有闭式表达。

算子分裂构造只使用 $A$、$B$ 各自的 resolvent 或显式评价的迭代。它的价值在于保留子问题结构：

- 光滑项用梯度；
- 非光滑项用 proximal operator；
- 硬约束用投影；
- 线性耦合用原始–对偶更新；
- 多智能体局部项用并行子问题；
- 共识约束用对偶变量协调。

## 七、Forward–Backward Splitting

考虑：

$$0\in A(x)+B(x)$$

其中 $A$ 极大单调并适合隐式 resolvent，$B$ 单值且适合显式前向步。迭代为：

$$x_{k+1}=J_{\gamma A}\left(x_k-\gamma B(x_k)\right)$$

“Forward” 指显式计算 $x_k-\gamma B(x_k)$，“Backward” 指使用隐式 resolvent $J_{\gamma A}$。

### 1. Proximal Gradient

对于：

$$\min_x f(x)+g(x)$$

若 $f$ 光滑凸、$g$ 闭凸，则取：

$$A=\partial g,\qquad B=\nabla f$$

得到：

$$x_{k+1}=\operatorname{prox}_{\gamma g}\left(x_k-\gamma\nabla f(x_k)\right)$$

### 2. 步长条件

若 $B$ 为 $\beta$-cocoercive，标准固定步长范围为：

$$0<\gamma<2\beta$$

若 $B=\nabla f$ 且 $\nabla f$ 为 $L$-Lipschitz，则常写为：

$$0<\gamma<\frac{2}{L}$$

实际实现常选择更保守的步长或使用回溯线搜索。

### 3. 局限

仅有单调 Lipschitz 而没有 cocoercivity 时，简单 Forward–Backward 可能不收敛。旋转型博弈伪梯度就是典型例子。

## 八、Forward–Backward–Forward

Tseng 的 Forward–Backward–Forward 适合 $A$ 极大单调、$B$ 单调且 Lipschitz，但不一定 cocoercive 的问题。

第一步：

$$y_k=J_{\gamma A}\left(x_k-\gamma B(x_k)\right)$$

第二步：

$$x_{k+1}=y_k-\gamma\left(B(y_k)-B(x_k)\right)$$

它比简单 Forward–Backward 多一次算子评价，用校正项处理旋转和非余强单调结构。它与 Extragradient 思想相近，但对约束和非光滑项的分工不同。

## 九、Douglas–Rachford Splitting

考虑两个极大单调算子：

$$0\in A(x)+B(x)$$

令：

$$x_k=J_{\gamma A}(z_k)$$

再计算：

$$y_k=J_{\gamma B}(2x_k-z_k)$$

标准松弛更新为：

$$z_{k+1}=z_k+\theta_k(y_k-x_k)$$

其中典型范围是 $0<\theta_k<2$，具体结论取决于假设与参数序列。

使用反射算子时，可写成：

$$z_{k+1}=\left(1-\frac{\theta_k}{2}\right)z_k+\frac{\theta_k}{2}R_{\gamma B}R_{\gamma A}z_k$$

需要注意：收敛到的是辅助变量 $z_k$ 的固定点，原问题解通常由 shadow sequence 提取：

$$x_k=J_{\gamma A}(z_k)$$

不能直接把 $z_k$ 当成原始解。

## 十、Peaceman–Rachford Splitting

Peaceman–Rachford 使用完整的两次反射：

$$z_{k+1}=R_{\gamma B}R_{\gamma A}z_k$$

它可以视为 Douglas–Rachford 取最大松弛的边界形式。它在某些强单调、线性或结构良好的问题上很快，但一般稳定性弱于标准 Douglas–Rachford。不能仅因为单次迭代更激进就默认它更优。

## 十一、ADMM

考虑带线性耦合的凸问题：

$$\min_{x,z}f(x)+g(z)\quad\text{subject to}\quad Ax+Bz=c$$

缩放形式 ADMM 的 $x$ 更新为：

$$x_{k+1}=\arg\min_x\left\{f(x)+\frac{\rho}{2}\lVert Ax+Bz_k-c+u_k\rVert^2\right\}$$

$z$ 更新为：

$$z_{k+1}=\arg\min_z\left\{g(z)+\frac{\rho}{2}\lVert Ax_{k+1}+Bz-c+u_k\rVert^2\right\}$$

缩放对偶变量更新为：

$$u_{k+1}=u_k+Ax_{k+1}+Bz_{k+1}-c$$

ADMM 可以解释为对适当对偶单调包含应用 Douglas–Rachford splitting。这解释了它为什么同时具有近端分裂与乘子法的特征。

### 1. 原始残差

$$r_k=Ax_k+Bz_k-c$$

### 2. 对偶残差

常见两块标准形式下，对偶残差可写为：

$$s_k=\rho A^{\mathsf T}B(z_k-z_{k-1})$$

符号和矩阵形式会随约束写法变化，工程实现应从所使用的增广拉格朗日推导，而不是机械照搬。

### 3. 罚参数

$\rho$ 太小会导致原始可行性恢复缓慢，太大则可能使对偶进展缓慢或子问题病态。自适应 $\rho$ 时必须同步缩放相应的对偶变量。

## 十二、Three-Operator Splitting

考虑：

$$0\in A(x)+B(x)+C(x)$$

其中 $A$ 和 $B$ 适合 resolvent，$C$ 单值且 cocoercive。Davis–Yin 三算子分裂的一种标准形式为：

$$x_k=J_{\gamma A}(z_k)$$

$$y_k=J_{\gamma B}\left(2x_k-z_k-\gamma C(x_k)\right)$$

$$z_{k+1}=z_k+y_k-x_k$$

它适合“一个光滑项、两个非光滑或约束项”的问题。例如：

$$\min_x f(x)+g(x)+h(x)$$

其中 $f$ 光滑，$g$ 和 $h$ 的近端映射容易计算。

## 十三、原始–对偶分裂

考虑：

$$\min_x f(x)+g(Kx)$$

其鞍点形式为：

$$\min_x\max_y f(x)+\langle Kx,y\rangle-g^*(y)$$

Chambolle–Pock 型更新可写为：

$$y_{k+1}=\operatorname{prox}_{\sigma g^*}\left(y_k+\sigma K\bar{x}_k\right)$$

$$x_{k+1}=\operatorname{prox}_{\tau f}\left(x_k-\tau K^{\mathsf T}y_{k+1}\right)$$

$$\bar{x}_{k+1}=x_{k+1}+\theta(x_{k+1}-x_k)$$

经典步长条件之一是：

$$\tau\sigma\lVert K\rVert^2<1$$

不同变体可以使用预条件、线搜索、强凸加速或随机块更新，条件也会相应变化。

## 十四、Consensus Splitting

多智能体共识问题为：

$$\min_{x_1,\ldots,x_n,z}\sum_{i=1}^n f_i(x_i)\quad\text{subject to}\quad x_i=z$$

每个智能体独立更新局部变量：

$$x_i^{k+1}=\operatorname{prox}_{f_i/\rho}(z_k-u_i^k)$$

全局共识变量更新为：

$$z_{k+1}=\frac{1}{n}\sum_{i=1}^n(x_i^{k+1}+u_i^k)$$

对偶变量更新为：

$$u_i^{k+1}=u_i^k+x_i^{k+1}-z_{k+1}$$

若智能体权重、通信图或局部约束不同，共识更新需要相应修改。通信丢包、延迟和异步更新也需要专门的收敛条件。

## 十五、算法之间的关系

| 问题结构 | 推荐分裂 | 每轮主要操作 | 关键条件 |
|---|---|---|---|
| 单个极大单调算子 | Proximal Point | 一次 resolvent | 零点存在、步长合适 |
| 非光滑项加光滑项 | Forward–Backward | 一次 prox、一次梯度 | 梯度 cocoercive |
| 非光滑项加单调 Lipschitz 项 | Forward–Backward–Forward | 一次 prox、两次算子评价 | 单调与 Lipschitz |
| 两个非光滑项 | Douglas–Rachford | 两次 resolvent | 两算子极大单调 |
| 线性耦合两块优化 | ADMM | 两个子问题、一次对偶更新 | 凸性与鞍点存在等 |
| 两个 prox 项加一个光滑项 | Three-Operator | 两次 prox、一次梯度 | 光滑项 cocoercive |
| 线性算子复合 | 原始–对偶分裂 | 原始 prox、对偶 prox | 步长乘积受算子范数控制 |

算法名称相近不代表更新可以任意互换。选择方法时应先识别每个算子的单调性、Lipschitz 性、cocoercivity、是否可求 resolvent，以及耦合结构。

## 十六、变分不等式与博弈均衡

约束变分不等式：

$$\langle F(x^*),x-x^*\rangle\geq 0,\qquad \forall x\in K$$

等价于：

$$0\in F(x^*)+N_K(x^*)$$

因此可取：

$$A=N_K,\qquad B=F$$

若 $F$ 强单调且 Lipschitz，可使用投影或近端方法；若 $F$ 单调 Lipschitz 但不是 cocoercive，可使用 Extragradient 或 Forward–Backward–Forward；若约束与非光滑正则项需要分别处理，可使用 Douglas–Rachford 或 Three-Operator Splitting。

对于一般和博弈，伪梯度可能非单调。此时标准单调分裂理论不再自动成立，可能出现多均衡、极限环和初始化依赖。近端正则化可以改善局部条件，但不能把非单调博弈自动变成全局单调问题。

## 十七、5v5 游戏中的应用

### 1. 高层混合策略近端更新

设团队策略为概率向量 $\pi$。使用 KL 或欧氏近端项可以限制策略单次变化：

$$\pi_{k+1}=\arg\min_{\pi\in\Delta}\left\{\langle g_k,\pi\rangle+\frac{1}{\eta}D(\pi,\pi_k)\right\}$$

这可以避免版本更新或单局异常导致策略突然坍缩。

### 2. 团队资源分配

每名英雄有局部收益和资源需求，同时共享金币、视野、路线与地图目标。可以写成：

$$\min_{x_1,\ldots,x_5}\sum_{i=1}^5 f_i(x_i)\quad\text{subject to}\quad\sum_{i=1}^5 C_i x_i\leq b$$

ADMM 或原始–对偶分裂允许局部计算与共享价格协调。

### 3. 任务共识

不同英雄根据局部视野提出开团时间、目标位置和撤退阈值。Consensus ADMM 可协调为共享高层计划，同时保留角色差异。

### 4. 非光滑规则

稀疏集火、路线切换惩罚、硬安全区、技能互斥和容量约束都可能产生非光滑项。算子分裂可以让每类规则由独立 prox 或投影处理。

### 5. 均衡计算

红蓝双方伪梯度与合法策略法锥形成单调包含。光滑单调时可用 Extragradient、Forward–Backward–Forward 或原始–对偶方法；存在复杂非光滑约束时可使用近端与分裂结构。

## 十八、与现有游戏数学层的组合

推荐流程：

1. P24 信念规划生成对隐藏状态和对手类型的分布；
2. P25 随机博弈构造收益、Shapley 算子或一般和伪梯度；
3. P26 因子图分解局部相互作用，ADMM 处理共识变量；
4. P27 CMDP 和 Budgeted MDP 提供资源、风险与硬预算约束；
5. 将光滑收益、非光滑规则、硬约束和线性耦合分配给不同算子；
6. 根据单调性和可计算结构选择 PPA、Forward–Backward、DRS、ADMM 或原始–对偶分裂；
7. P30 使用置信界和共形风险控制审计离线估计误差；
8. 输出仍需通过原生动作合法性、技能冷却、资源、碰撞、联合规划和 MAPF 检查。

## 十九、收敛诊断

### 1. 固定点残差

对于一般迭代 $x_{k+1}=T(x_k)$，记录：

$$r_k^{\mathrm{fp}}=\lVert x_k-T(x_k)\rVert$$

### 2. 单调包含残差

若能选取 $a_k\in A(x_k)$ 和 $b_k\in B(x_k)$，记录：

$$r_k^{\mathrm{inc}}=\lVert a_k+b_k\rVert$$

### 3. 近端残差

$$r_{\lambda}(x)=\frac{1}{\lambda}\left[x-J_{\lambda A}(x)\right]$$

### 4. ADMM 残差

同时记录原始残差、对偶残差、绝对与相对停止阈值、罚参数历史和子问题误差。

### 5. 博弈诊断

除了算子残差，还应记录最佳响应 gap、变分不等式 gap、策略 KL 变化、最后迭代与平均迭代性能，以及多初值是否收敛到同一分支。

残差小不等于模型正确。若收益函数、转移模型或对手分布有偏差，算法可以非常精确地求出错误模型的解。

## 二十、数值实现要点

### 1. 变量尺度

不同变量量纲差异过大会导致固定步长失效。可以使用对角预条件或变量归一化，但必须保持原始约束语义。

### 2. 近端子问题精度

外层残差下降到与内层误差同量级后会停滞。应保存每次内层迭代次数和最优性残差。

### 3. 自适应步长

回溯线搜索和残差平衡可以减少人工调参，但每次参数变化都要符合对应算法的理论要求。

### 4. 概率变量

概率接近零时，熵近端与 KL 计算应使用 log-sum-exp，并避免直接计算 $\log 0$。

### 5. 异步与随机更新

随机块、延迟通信和异步 ADMM 需要额外的有界延迟、采样覆盖或方差条件。不能把同步收敛定理直接用于任意异步实现。

## 二十一、常见误区

### 1. 把 proximal step 当作普通梯度正则化

近端点法是隐式 resolvent 更新，不只是给原目标永久增加二次惩罚。

### 2. 把 Douglas–Rachford 的辅助变量当作原始解

通常应输出 shadow sequence $J_{\gamma A}(z_k)$。

### 3. 在单调 Lipschitz 问题中盲用 Forward–Backward

缺少 cocoercivity 时应考虑 Extragradient、Forward–Backward–Forward 或其他适用方法。

### 4. 只看 ADMM 原始残差

原始可行性很好但对偶残差很大时，目标和乘子可能尚未稳定。

### 5. 认为更大的罚参数一定更快

过大的 $\rho$ 会使子问题病态，并拖慢对偶进展。

### 6. 把非凸或非单调问题包装成凸单调问题

算法仍可能运行，但标准全局收敛结论已经失效。应明确报告局部解、初始化和失败模式。

### 7. 绕过游戏原生规则

分裂算法输出的是高层候选策略或资源计划。动作能否执行仍由游戏规则、安全层和路径规划决定。

## 二十二、选择建议

如果整个算子的 resolvent 可以有效求解，优先考虑 Proximal Point；它稳定、概念简单，但每轮子问题可能较重。

如果问题由光滑项与一个非光滑项组成，优先考虑 Forward–Backward。若显式算子只有单调 Lipschitz 而非 cocoercive，考虑 Forward–Backward–Forward 或 Extragradient。

如果有两个容易分别求 prox 的非光滑项，考虑 Douglas–Rachford。若问题天然是线性耦合的两块结构，考虑 ADMM。若有两个 prox 项和一个光滑项，考虑 Three-Operator Splitting。若存在明显线性算子复合，考虑原始–对偶分裂。

最终选择应由算子结构、单调性、每次梯度与 prox 成本、通信方式、所需精度和可验证残差共同决定，而不是只根据算法流行程度。

## 二十三、结论

Proximal Point 用隐式 resolvent 把单调算子零点变成稳定的固定点问题；Operator Splitting 则进一步把复杂算子和拆成可分别计算的梯度、投影、prox 和对偶更新。

Forward–Backward 适合光滑与非光滑复合结构，Forward–Backward–Forward 处理更一般的单调 Lipschitz 算子，Douglas–Rachford 与 ADMM 适合多块非光滑和线性耦合问题，Three-Operator 与原始–对偶方法则覆盖更复杂的组合结构。

在游戏模型中，这些方法最适合处理策略稳定化、共享资源、团队共识、硬约束和均衡计算。它们提供的是可审计的数学候选解，不替代原生动作合法性、实时安全控制和回放验证。
