# Mirror Descent、Extragradient 与 Optimistic Mirror Descent

## 摘要

Mirror Descent（镜像下降）、Extragradient（外梯度）和 Optimistic Mirror Descent（乐观镜像下降）是约束优化、在线学习、鞍点问题与博弈均衡求解中的三类基础算法。

- Mirror Descent 根据变量空间选择合适的几何结构；
- Extragradient 先预测、再校正，用于抑制对抗博弈中的旋转；
- Optimistic Mirror Descent 利用历史梯度预测下一步方向，在可预测的重复博弈中减少震荡。

本文统一介绍三种方法的数学基础、更新公式、收敛条件、算法流程、数值诊断和 5v5 游戏应用。

## 一、统一框架：优化与变分不等式

设可行域为闭凸集：

$$X \subseteq \mathbb{R}^d$$

普通凸优化问题为：

$$\min_{x \in X} f(x)$$

对应算子为：

$$F(x)=\nabla f(x)$$

零和博弈通常写成：

$$\min_{x \in X}\max_{y \in Y} L(x,y)$$

令联合变量为 $z=(x,y)$，鞍点算子为：

$$F(z)=\begin{bmatrix}\nabla_x L(x,y) \\ -\nabla_y L(x,y)\end{bmatrix}$$

一般变分不等式要求寻找 $z^* \in Z$，使得：

$$\langle F(z^*),z-z^*\rangle \geq 0,\qquad \forall z\in Z$$

Nash 均衡、约束优化的一阶条件、网络流均衡和部分市场均衡都可以写成这种形式。

如果：

$$\langle F(x)-F(y),x-y\rangle \geq 0$$

则称 $F$ 为单调算子。Extragradient 和 Optimistic Mirror Descent 的主要理论优势通常建立在单调性与 Lipschitz 连续性上。

## 二、Bregman 散度与镜像几何

选择可微、严格凸的镜像函数 $\psi$。对应的 Bregman 散度为：

$$D_{\psi}(x,y)=\psi(x)-\psi(y)-\langle \nabla\psi(y),x-y\rangle$$

它不一定是对称距离，但可以描述变量空间的自然几何。

### 1. 欧几里得几何

取：

$$\psi(x)=\frac{1}{2}\lVert x\rVert_2^2$$

则：

$$D_{\psi}(x,y)=\frac{1}{2}\lVert x-y\rVert_2^2$$

此时 Mirror Descent 退化为投影梯度下降。

### 2. 概率单纯形几何

若变量是概率分布：

$$\Delta_n=\left\{x\in\mathbb{R}^n:x_i\geq 0,\sum_i x_i=1\right\}$$

可选择负熵：

$$\psi(x)=\sum_i x_i\log x_i$$

对应的 Bregman 散度是 KL 散度：

$$D_{\psi}(x,y)=\sum_i x_i\log\frac{x_i}{y_i}$$

这种几何天然保持概率非负和归一化，适合混合策略、资源比例和任务分配。

## 三、Mirror Descent

给定当前点 $x_t$ 和算子值 $g_t$，Mirror Descent 更新为：

$$x_{t+1}=\arg\min_{x\in X}\left[\eta_t\langle g_t,x\rangle+D_{\psi}(x,x_t)\right]$$

其中 $\eta_t>0$ 是步长。在无约束对偶空间中，可写成：

$$\nabla\psi(x_{t+1})=\nabla\psi(x_t)-\eta_t g_t$$

随后通过镜像映射回到原空间。

### 概率策略更新

在概率单纯形和负熵几何下，更新变为指数权重：

$$x_{t+1,i}=\frac{x_{t,i}\exp(-\eta_t g_{t,i})}{\sum_j x_{t,j}\exp(-\eta_t g_{t,j})}$$

它不会产生负概率，也不需要先走出单纯形再做欧氏投影。

### 优点

- 匹配概率、非负权重和其他约束空间的自然几何；
- 每轮通常只需要一次梯度或算子计算；
- 适合在线学习和无悔学习；
- 可与熵正则化、KL Control 和混合策略直接结合。

### 局限

- 在双线性博弈中，最后一次迭代可能围绕均衡持续旋转；
- 一般需要对时间平均策略给出收敛结论；
- 步长与镜像函数选择不当会造成过慢更新或数值退化。

## 四、为什么普通梯度会在博弈中旋转

考虑双线性鞍点问题：

$$\min_x\max_y xy$$

其算子为：

$$F(x,y)=\begin{bmatrix}y \\ -x\end{bmatrix}$$

连续动力学为：

$$\dot{x}=-y,\qquad \dot{y}=x$$

因此：

$$\frac{\mathrm d}{\mathrm dt}\left(x^2+y^2\right)=0$$

轨迹会围绕原点旋转，而不是自动收敛到均衡 $(0,0)$。在对抗问题中，沿当前梯度前进可能只是在追逐对方上一时刻的位置。

## 五、Extragradient

Extragradient 每轮执行预测和校正两步。

预测步：

$$\widetilde{x}_t=\Pi_X\left(x_t-\eta_t F(x_t)\right)$$

校正步：

$$x_{t+1}=\Pi_X\left(x_t-\eta_t F(\widetilde{x}_t)\right)$$

第二步使用预测点的算子值，但仍然从原点 $x_t$ 出发。

镜像形式为：

$$\widetilde{x}_t=\arg\min_{x\in X}\left[\eta_t\langle F(x_t),x\rangle+D_{\psi}(x,x_t)\right]$$

$$x_{t+1}=\arg\min_{x\in X}\left[\eta_t\langle F(\widetilde{x}_t),x\rangle+D_{\psi}(x,x_t)\right]$$

预测步估计“如果按当前方向移动，对手与约束将如何响应”；校正步根据预测位置的局部结构决定真实移动方向。

### 收敛特点

对于光滑单调变分不等式，在适当步长下，Extragradient 的平均间隙通常满足：

$$\mathrm{Gap}(\bar{x}_T)=O\left(\frac{1}{T}\right)$$

普通 Mirror Descent 在一般有界单调问题上的典型平均间隙为：

$$\mathrm{Gap}(\bar{x}_T)=O\left(\frac{1}{\sqrt{T}}\right)$$

具体速率仍取决于光滑性、强单调性、噪声和步长假设。

### 代价与边界

- 每轮通常需要两次算子计算；
- 若算子来自昂贵仿真，两次评估可能成为主要成本；
- 随机梯度版本必须控制两次估计之间的偏差和方差；
- 非单调一般和博弈不能直接套用单调变分不等式结论。

## 六、Optimistic Mirror Descent

Optimistic Mirror Descent 使用可预测序列 $m_t$ 估计下一轮算子：

$$x_{t+1}=\arg\min_{x\in X}\left[\eta_t\langle m_t,x\rangle+D_{\psi}(x,x_t)\right]$$

常用的一阶外推是：

$$m_t=2g_t-g_{t-1}$$

其中：

$$g_t=F(x_t)$$

因此更新使用 $2F(x_t)-F(x_{t-1})$，而不是只使用当前算子值。

在概率单纯形上：

$$x_{t+1,i}=\frac{x_{t,i}\exp\left[-\eta_t(2g_{t,i}-g_{t-1,i})\right]}{\sum_j x_{t,j}\exp\left[-\eta_t(2g_{t,j}-g_{t-1,j})\right]}$$

若梯度变化平稳，则：

$$g_{t+1}\approx 2g_t-g_{t-1}$$

算法相当于提前估计对手的下一次响应，而不是永远落后一拍。

### 与动量法的区别

动量法通常累计历史下降方向：

$$v_t=\beta v_{t-1}+g_t$$

OMD 的目标是预测下一梯度：

- 动量主要用于加速单目标优化；
- OMD 主要利用在线序列的可预测性；
- 在博弈中，OMD 可以抵消旋转，而普通动量可能放大旋转。

在光滑单调博弈和可预测在线学习中，OMD 可以取得与 Extragradient 类似的快速间隙收敛；部分双线性博弈还能得到最后迭代收敛。结论依赖具体更新形式、步长和算子结构。

## 七、三种方法的比较

| 方法 | 每轮典型算子计算 | 核心机制 | 主要优势 | 主要风险 |
|---|---:|---|---|---|
| Mirror Descent | 1 次 | 使用 Bregman 几何 | 约束自然，适合概率策略 | 对抗博弈中可能旋转 |
| Extragradient | 2 次 | 预测后校正 | 单调博弈中稳定 | 算子计算成本较高 |
| Optimistic Mirror Descent | 约 1 次 | 预测下一梯度 | 利用可预测性，减少滞后 | 预测错误时可能过冲 |

## 八、算法流程

### Mirror Descent

1. 初始化 $x_1$、步长 $\eta_t$ 和镜像函数 $\psi$；
2. 计算 $g_t=F(x_t)$；
3. 求解一次镜像近端问题；
4. 输出最后迭代或加权平均。

### Extragradient

1. 在 $x_t$ 计算 $F(x_t)$；
2. 做一次镜像预测，得到 $\widetilde{x}_t$；
3. 在预测点计算 $F(\widetilde{x}_t)$；
4. 从 $x_t$ 出发做校正；
5. 输出最后迭代或加权平均。

### Optimistic Mirror Descent

1. 计算当前算子 $g_t$；
2. 构造预测量 $m_t=2g_t-g_{t-1}$；
3. 使用 $m_t$ 做镜像更新；
4. 保存 $g_t$ 供下一轮使用；
5. 检测到环境变点时清空历史预测。

## 九、5v5 游戏中的建模方式

设每名英雄的高层动作包括开团、拉扯、集火、撤退、转线和控制地图资源。玩家 $i$ 的混合策略为：

$$\pi_i\in\Delta(\mathcal A_i)$$

联合策略为：

$$\pi=(\pi_1,\ldots,\pi_n)$$

收益可组合战斗、经济、地图控制和风险：

$$u_i(\pi)=w_1 U_{\mathrm{combat}}+w_2 U_{\mathrm{economy}}+w_3 U_{\mathrm{map}}-w_4 U_{\mathrm{risk}}$$

每个玩家对应的博弈算子为：

$$F_i(\pi)=-\nabla_{\pi_i}u_i(\pi)$$

### Mirror Descent 的用途

- 更新开团、撤退等混合策略；
- 保持策略始终位于概率单纯形；
- 使用 KL 几何限制策略相对旧版本变化过快；
- 与无悔学习、CE 和 CCE 模块结合。

### Extragradient 的用途

- 处理红蓝双方相互针对造成的策略循环；
- 求解零和或近零和团战子博弈；
- 求解 Nash、QRE 或约束博弈对应的变分不等式；
- 在版本平衡分析中减少策略交替震荡。

### OMD 的用途

- 根据连续多轮交战预测对手下一次响应；
- 预测换线、集火和撤退倾向；
- 在重复博弈中利用对方策略变化的可预测性；
- 与 BOCPD 结合，在变点发生后重置历史梯度。

## 十、与现有游戏模型的组合

推荐流程：

1. P24 信念规划估计隐藏状态与对手类型；
2. P25 随机博弈构造 Shapley 或一般和算子；
3. 使用 Mirror Descent、Extragradient 或 OMD 求混合策略；
4. P27 CMDP 对经济、血量和风险预算施加约束；
5. P30 置信序列和共形风险控制审计策略表现；
6. 最终动作通过原生合法动作、资源、碰撞、联合规划和 MAPF 检查。

这些算法更新的是高层策略分布，不应直接绕过游戏规则生成底层动作。

## 十一、工程诊断

每次求解至少记录：

- 变分不等式 gap；
- 最佳响应 gap；
- 算子范数；
- 相邻策略 KL 散度；
- 最后迭代与平均迭代的性能；
- 步长与策略熵；
- 约束违反量；
- 随机种子和回放版本。

OMD 还应记录预测误差：

$$e_t=\lVert g_t-m_t\rVert_*$$

Extragradient 应记录预测点与正式点的差异：

$$d_t=D_{\psi}(\widetilde{x}_t,x_t)$$

如果 gap 下降但实战指标恶化，通常说明收益函数、状态抽象或对手分布发生偏差，而不是求解器已经证明策略有效。

## 十二、常见误区

### 1. 把训练损失下降当成 Nash 收敛

单方收益增加不代表双方最佳响应 gap 已趋近于零。

### 2. 只报告平均策略

平均策略可能收敛，但最后迭代仍持续震荡。部署使用哪一种必须明确。

### 3. 把 OMD 当成普通动量

OMD 的预测项针对下一轮算子，而不是无条件累计历史梯度。

### 4. 在非单调一般和博弈中套用单调收敛结论

一般和博弈可能存在极限环、多重均衡和局部不稳定点，需要额外结构或局部分析。

### 5. 忽略接近零概率的数值问题

负熵镜像更新应使用 log-sum-exp 稳定计算，并设置受控支持集。

### 6. 让数学求解器绕过原生规则

均衡策略只是高层候选。非法移动、技能冷却、资源不足和路径冲突仍应由游戏运行层拒绝。

## 十三、选择建议

若变量是概率策略、资源比例或非负权重，优先从 Mirror Descent 开始。

若问题是光滑单调的 Nash、鞍点或变分不等式，并能承担两次算子计算，优先使用 Extragradient。

若对手响应连续、历史梯度具有预测性，或者一次算子计算成本较高，可使用 Optimistic Mirror Descent，同时监控预测误差，并在检测到环境变点后重置预测状态。

工程上可以统一使用负熵镜像几何保持策略合法，再根据博弈是否出现旋转、算子计算成本以及梯度是否可预测，选择普通、外梯度或乐观更新。
