# Minty 与 Stampacchia 变分不等式

## 摘要

变分不等式把约束优化、互补问题、Nash 均衡、交通均衡和网络资源分配统一为一个算子求零问题。Stampacchia 形式在候选解处评价算子，表达“从当前解出发不存在可行下降方向”；Minty 形式则在所有比较点处评价算子，表达“任意比较点的算子都指向候选解之外”。

在连续单调算子下，两种形式等价；离开连续性、单调性或伪单调性以后，它们的解集可能不同。这个区别决定了均衡证书是否可靠，也决定了投影法、Extragradient、Mirror-Prox 等算法的收敛结论能否使用。

本文介绍两种变分不等式的定义、几何含义、解集关系、等价条件、反例、gap 函数、求解方法，以及它们在 5v5 游戏均衡与约束策略学习中的应用。

## 一、基本设置

设 $K$ 是非空闭凸集：

$$K\subseteq\mathbb{R}^d$$

设算子为：

$$F:K\rightarrow\mathbb{R}^d$$

内积记为 $\langle \cdot,\cdot\rangle$。变分不等式的目标不是简单求解 $F(x)=0$，而是允许约束边界上的法向力抵消算子。

当候选点位于 $K$ 的内部时，若所有方向都可行，变分不等式通常退化为：

$$F(x^*)=0$$

当候选点位于边界时，$F(x^*)$ 可以不为零，但它不能产生指向可行域内部的改进方向。

## 二、Stampacchia 变分不等式

Stampacchia 变分不等式记为 $\operatorname{SVI}(F,K)$。它要求寻找 $x^*\in K$，使得：

$$\langle F(x^*),y-x^*\rangle\geq 0,\qquad \forall y\in K$$

其关键特征是：算子始终在候选解 $x^*$ 处计算。

### 1. 一阶最优性解释

若 $F=\nabla f$，且 $f$ 是可微凸函数，则约束优化问题：

$$\min_{x\in K}f(x)$$

的一阶最优性条件为：

$$\langle \nabla f(x^*),y-x^*\rangle\geq 0,\qquad \forall y\in K$$

因此凸优化的一阶条件就是 Stampacchia 变分不等式。

### 2. 法锥包含形式

闭凸集 $K$ 在 $x$ 处的法锥定义为：

$$N_K(x)=\left\{v:\langle v,y-x\rangle\leq 0,\ \forall y\in K\right\}$$

Stampacchia 形式等价于单调包含：

$$0\in F(x^*)+N_K(x^*)$$

这说明变分不等式是“算子加约束法锥”的求零问题。

### 3. 投影不动点形式

对于任意 $\eta>0$，Stampacchia 解满足：

$$x^*=\Pi_K\left(x^*-\eta F(x^*)\right)$$

其中 $\Pi_K$ 是到 $K$ 的欧氏投影。这个等价关系是投影梯度法、Extragradient 和残差诊断的基础。

## 三、Minty 变分不等式

Minty 变分不等式记为 $\operatorname{MVI}(F,K)$。它要求寻找 $x^*\in K$，使得：

$$\langle F(y),y-x^*\rangle\geq 0,\qquad \forall y\in K$$

它与 Stampacchia 形式的差别只有算子评价点：

- Stampacchia 在 $x^*$ 处计算 $F(x^*)$；
- Minty 在每个比较点 $y$ 处计算 $F(y)$。

这个看似很小的差异会改变解集和理论要求。

### 1. 几何解释

Minty 条件要求任意 $y$ 处的算子 $F(y)$ 与从候选解 $x^*$ 指向 $y$ 的方向具有非负内积。换言之，从全局看，算子场不能系统性地把点推向远离 $x^*$ 的反方向。

### 2. 稳定性解释

若考虑动力系统：

$$\dot{x}=-F(x)$$

则 Minty 条件可被理解为一种全局方向一致性证书。它比只检查 $F(x^*)$ 的局部条件包含更多算子场信息，但在非单调问题中也可能过强。

## 四、两种形式的解集关系

分别记解集为：

$$\operatorname{SOL}_S(F,K)=\left\{x^*\in K:x^*\text{ 满足 SVI}\right\}$$

$$\operatorname{SOL}_M(F,K)=\left\{x^*\in K:x^*\text{ 满足 MVI}\right\}$$

### 1. 单调性使 Stampacchia 推出 Minty

若 $F$ 单调，即：

$$\langle F(y)-F(x),y-x\rangle\geq 0,\qquad \forall x,y\in K$$

并且 $x^*$ 满足 Stampacchia 条件，则：

$$\langle F(x^*),y-x^*\rangle\geq 0$$

由单调性还有：

$$\langle F(y)-F(x^*),y-x^*\rangle\geq 0$$

两式相加得到：

$$\langle F(y),y-x^*\rangle\geq 0$$

因此：

$$F\text{ 单调}\quad\Longrightarrow\quad \operatorname{SOL}_S(F,K)\subseteq\operatorname{SOL}_M(F,K)$$

### 2. 连续性使 Minty 推出 Stampacchia

设 $x^*$ 满足 Minty 条件。对任意 $y\in K$ 和 $t\in(0,1]$，令：

$$y_t=x^*+t(y-x^*)$$

由于 $K$ 为凸集，所以 $y_t\in K$。Minty 条件给出：

$$\langle F(y_t),y_t-x^*\rangle\geq 0$$

除以 $t$ 后得到：

$$\langle F(y_t),y-x^*\rangle\geq 0$$

若 $F$ 在 $x^*$ 连续，令 $t\downarrow 0$，便有：

$$\langle F(x^*),y-x^*\rangle\geq 0$$

因此在凸域和连续算子下：

$$F\text{ 连续}\quad\Longrightarrow\quad \operatorname{SOL}_M(F,K)\subseteq\operatorname{SOL}_S(F,K)$$

更弱的径向连续或适当半连续条件也可支持类似结论，但必须明确所采用的拓扑与方向极限。

### 3. 连续单调时等价

综合上述两个方向：

$$F\text{ 连续且单调}\quad\Longrightarrow\quad \operatorname{SOL}_S(F,K)=\operatorname{SOL}_M(F,K)$$

这是最常使用的 Minty–Stampacchia 等价结论。

## 五、伪单调与更弱结构

算子 $F$ 称为伪单调，如果：

$$\langle F(x),y-x\rangle\geq 0\quad\Longrightarrow\quad\langle F(y),y-x\rangle\geq 0$$

对所有 $x,y\in K$ 都成立。

若 $x^*$ 是 Stampacchia 解，则前件对任意 $y$ 成立，因此伪单调性直接推出：

$$\operatorname{SOL}_S(F,K)\subseteq\operatorname{SOL}_M(F,K)$$

反方向仍通常需要连续性、半连续性或径向条件。伪单调性弱于单调性，适用于部分非凸优化的一阶条件与某些一般和博弈，但不能自动保证算法像单调问题一样稳定。

### 严格伪单调与唯一性

严格伪单调可以排除部分多解情形，但唯一性结论依赖定义和可行域。工程上更常使用强单调性给出清晰唯一性保证。

## 六、强单调性、Lipschitz 性与唯一解

若存在 $\mu>0$，使得：

$$\langle F(x)-F(y),x-y\rangle\geq \mu\lVert x-y\rVert^2$$

则称 $F$ 为 $\mu$-强单调算子。

若存在 $L>0$，使得：

$$\lVert F(x)-F(y)\rVert\leq L\lVert x-y\rVert$$

则称 $F$ 为 $L$-Lipschitz 连续算子。

在适当存在性条件下，强单调性可保证 Stampacchia 解唯一。若 $x_1$ 和 $x_2$ 都是解，则由两组变分不等式可得：

$$\langle F(x_1)-F(x_2),x_1-x_2\rangle\leq 0$$

而强单调性要求：

$$\langle F(x_1)-F(x_2),x_1-x_2\rangle\geq \mu\lVert x_1-x_2\rVert^2$$

因此只能有：

$$x_1=x_2$$

## 七、两类不等式不等价的反例

### 1. 非单调算子：Stampacchia 解未必是 Minty 解

取：

$$K=[-1,1],\qquad F(x)=-x$$

点 $x^*=0$ 满足 Stampacchia 条件，因为：

$$F(0)=0$$

但 Minty 条件要求：

$$-y(y-0)=-y^2\geq 0,\qquad \forall y\in[-1,1]$$

这显然不成立。因此非单调时，Stampacchia 解不必属于 Minty 解集。

### 2. 不连续算子：Minty 解未必是 Stampacchia 解

取 $K=[-1,1]$，并定义：

$$F(y)=-1\text{ 当 }y<0,\qquad F(y)=1\text{ 当 }y\geq 0$$

对 $x^*=0$，任意 $y$ 都满足：

$$F(y)(y-0)\geq 0$$

所以 $0$ 是 Minty 解。但 Stampacchia 条件使用 $F(0)=1$，它要求：

$$y\geq 0,\qquad \forall y\in[-1,1]$$

该条件不成立。因此缺少连续性时，Minty 解不必是 Stampacchia 解。

这些反例说明，不能在未验证假设时把两种形式互换。

## 八、与凸优化的关系

设 $F=\nabla f$。

### 1. 可微凸函数

若 $f$ 可微且凸，则：

$$f(y)\geq f(x)+\langle \nabla f(x),y-x\rangle$$

因此 $x^*$ 是全局最小点，当且仅当它满足 Stampacchia 变分不等式。在梯度连续时，它也满足 Minty 形式。

### 2. 非凸函数

对于非凸 $f$，Stampacchia 条件通常只是约束一阶驻点条件，不保证全局最优。Minty 条件可能更强，但也不能在没有额外结构时自动解释为全局最优证书。

### 3. 复合优化

问题：

$$\min_x f(x)+g(x)$$

其中 $f$ 光滑、$g$ 凸但可能不可微，可以写成：

$$0\in \nabla f(x^*)+\partial g(x^*)$$

这属于单调包含，并可视为变分不等式的推广。

## 九、与 Nash 均衡的关系

考虑 $n$ 个玩家。玩家 $i$ 的决策为 $x_i\in K_i$，成本为 $J_i(x_i,x_{-i})$。令：

$$K=K_1\times\cdots\times K_n$$

定义伪梯度算子：

$$F(x)=\operatorname{col}\left(\nabla_{x_1}J_1(x),\ldots,\nabla_{x_n}J_n(x)\right)$$

如果每个玩家的成本关于自身决策是凸的，则 Nash 均衡满足：

$$\langle F(x^*),x-x^*\rangle\geq 0,\qquad \forall x\in K$$

也就是 Stampacchia 变分不等式。

若伪梯度连续且单调，则 Nash 均衡也满足 Minty 形式。若伪梯度强单调，均衡通常唯一。若一般和博弈的伪梯度非单调，Minty 解可能不存在，普通梯度、Extragradient 和乐观方法也可能出现循环或收敛到不同局部对象。

## 十、互补问题

当可行域为非负正交锥：

$$K=\mathbb{R}_+^d$$

Stampacchia 变分不等式等价于非线性互补条件：

$$x^*\geq 0,\qquad F(x^*)\geq 0,\qquad \langle x^*,F(x^*)\rangle=0$$

这可以描述容量价格、资源稀缺影子价格、市场清算和网络拥塞均衡。

## 十一、Gap 函数与数值证书

### 1. Stampacchia primal gap

定义：

$$g_S(x)=\sup_{y\in K}\langle F(x),x-y\rangle$$

由于可以选择 $y=x$，所以：

$$g_S(x)\geq 0$$

并且：

$$g_S(x)=0\quad\Longleftrightarrow\quad x\in\operatorname{SOL}_S(F,K)$$

当 $K$ 无界时，这个上确界可能为无穷大，工程上常使用正则化 gap 或投影残差。

### 2. Minty dual gap

定义：

$$g_M(x)=\sup_{y\in K}\langle F(y),x-y\rangle$$

同样有：

$$g_M(x)\geq 0$$

并且：

$$g_M(x)=0\quad\Longleftrightarrow\quad x\in\operatorname{SOL}_M(F,K)$$

Minty gap 需要在所有比较点计算 $F(y)$，通常比 primal gap 更难求。

### 3. 投影残差

定义自然残差：

$$r_{\eta}(x)=\frac{1}{\eta}\left[x-\Pi_K(x-\eta F(x))\right]$$

Stampacchia 解满足：

$$r_{\eta}(x^*)=0$$

残差小只表示接近一阶变分不等式解；在病态、非单调或近退化问题中，仍需结合最佳响应 gap、条件数和多初值验证。

## 十二、求解算法

### 1. 投影法

基本迭代为：

$$x_{t+1}=\Pi_K\left(x_t-\eta_t F(x_t)\right)$$

它适合强单调且 Lipschitz 的问题。在仅单调的旋转型博弈中，最后迭代可能不收敛。

### 2. Extragradient

预测步为：

$$\widetilde{x}_t=\Pi_K\left(x_t-\eta F(x_t)\right)$$

校正步为：

$$x_{t+1}=\Pi_K\left(x_t-\eta F(\widetilde{x}_t)\right)$$

它针对光滑单调变分不等式，可抑制双线性博弈中的旋转。

### 3. Mirror-Prox

Mirror-Prox 将 Extragradient 与 Bregman 几何结合，适合概率单纯形、正定锥和其他非欧几里得可行域。对概率策略常使用负熵镜像函数。

### 4. 近端点法

近端点迭代求解：

$$0\in F(x_{t+1})+N_K(x_{t+1})+\frac{1}{\lambda_t}(x_{t+1}-x_t)$$

其隐式步通常更稳定，但每轮需要解一个正则化子问题。

### 5. 乐观方法

Optimistic Gradient 或 Optimistic Mirror Descent 使用历史算子预测下一方向，例如：

$$m_t=2F(x_t)-F(x_{t-1})$$

它可以在可预测重复博弈中降低滞后，但环境变点后应重置历史预测。

## 十三、存在性条件

一个常用的有限维存在性结论是：若 $K$ 非空、紧、凸，且 $F$ 连续，则 Stampacchia 变分不等式至少有一个解。

若 $K$ 不紧，则需要强制性条件控制解不会逃向无穷远。例如存在 $x_0\in K$，使得：

$$\frac{\langle F(x),x-x_0\rangle}{\lVert x\rVert}\rightarrow +\infty$$

当 $\lVert x\rVert\rightarrow\infty$ 时，这类 coercivity 条件可帮助恢复存在性。实际使用时必须核对具体定理采用的连续性、紧性和强制性版本。

## 十四、5v5 游戏中的建模

令每个英雄的高层混合策略为：

$$\pi_i\in\Delta(\mathcal A_i)$$

联合策略为：

$$\pi=(\pi_1,\ldots,\pi_n)$$

如果使用成本最小化约定，可定义伪梯度：

$$F_i(\pi)=\nabla_{\pi_i}J_i(\pi)$$

其中成本可组合死亡风险、资源损失、距离、技能冲突和地图目标损失。

### Stampacchia 解释

在候选策略 $\pi^*$ 处，每名玩家沿任意合法单边偏移都没有一阶成本下降方向。它对应局部均衡和 KKT 型执行条件。

### Minty 解释

从任意比较策略 $\pi$ 处观察，伪梯度场都与从候选均衡指向该策略的方向一致。单调游戏中，这提供与 Stampacchia 相同的均衡证书；非单调游戏中，它可能过强或为空。

### 可建模对象

- 开团、撤退、集火和换线的混合策略；
- 多英雄共享走廊、目标点和技能窗口的拥塞价格；
- 资源预算、风险约束和容量限制下的广义 Nash 均衡；
- 红蓝双方零和或近零和团战子博弈；
- 队内局部收益与全队目标不完全一致的一般和博弈。

## 十五、与现有游戏数学层的组合

推荐流程：

1. P24 信念规划给出隐藏状态和对手类型分布；
2. P25 随机博弈生成状态相关收益与转移；
3. 构造伪梯度算子 $F$ 和合法策略集 $K$；
4. 先检查经验单调性、对称 Jacobian 特征值与 Lipschitz 上界；
5. 单调问题使用 Extragradient 或 Mirror-Prox；
6. 强单调问题可使用投影法并监控线性收敛；
7. 非单调问题报告多初值、多分支、最佳响应 gap 和局部稳定性；
8. P27 施加资源与风险约束，P30 给离线评估附加有限样本置信界；
9. 输出仍须通过原生动作合法性、技能冷却、资源、碰撞、联合规划和 MAPF 检查。

## 十六、工程诊断清单

至少记录以下量：

- Stampacchia primal gap；
- Minty dual gap；
- 投影残差 $\lVert r_\eta(x_t)\rVert$；
- 最佳响应 gap；
- 相邻迭代距离；
- 算子范数与经验 Lipschitz 比率；
- Jacobian 对称部分的最小特征值；
- 最后迭代与平均迭代结果；
- 多初值是否收敛到同一解；
- 约束违反量、随机种子、模型版本和回放版本。

经验单调性可通过样本对粗略检查：

$$m(x,y)=\langle F(x)-F(y),x-y\rangle$$

若频繁出现显著负值，就不能声称算子单调。有限样本未发现负值也不是全局单调性的数学证明。

## 十七、常见误区

### 1. 把 Minty 与 Stampacchia 当作无条件等价

等价通常需要连续性与单调性，或者相应的弱化假设。

### 2. 把小投影残差当作全局最优

非凸优化和非单调博弈中，小残差只说明接近一阶驻点或局部均衡候选。

### 3. 忽略解集可能为空或多值

非单调问题的 Minty 解可能不存在，Stampacchia 解也可能有多个分支。

### 4. 把收益梯度和成本梯度符号混用

成本最小化通常使用 $F_i=\nabla J_i$；收益最大化通常使用 $F_i=-\nabla u_i$。符号错误会把稳定方向完全反转。

### 5. 只看时间平均策略

平均策略 gap 下降不代表最后迭代稳定。部署时必须说明使用最后策略、平均策略还是经过选择的历史策略。

### 6. 让均衡求解器绕过游戏规则

变分不等式只生成高层候选策略。动作可执行性仍由原生规则和安全控制层决定。

## 十八、结论

Stampacchia 变分不等式是约束一阶最优性与 Nash 均衡的直接表达；Minty 变分不等式从整个算子场评价候选解。单调性负责从 Stampacchia 推向 Minty，连续性负责从 Minty 推回 Stampacchia，因此连续单调是两者等价的核心组合。

在游戏模型中，先验证算子结构，再选择算法比直接套用某个均衡求解器更重要。强单调问题适合投影法，光滑单调问题适合 Extragradient 或 Mirror-Prox，非单调一般和博弈则必须保留多分支、局部稳定性和失败诊断，不能把一个低残差点包装成唯一全局均衡。
