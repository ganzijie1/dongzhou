# 混合整数二阶锥规划：理论、建模与求解实践

## 摘要

混合整数二阶锥规划（Mixed-Integer Second-Order Cone Programming，MISOCP）把整数决策、线性约束和二阶锥约束统一在同一个优化模型中。它能够表达欧氏范数、平方和、风险半径、椭球不确定性、透视结构和某些凸二次关系。

MISOCP 广泛用于鲁棒优化、机会约束、投资组合、设施选址、无线网络、能源系统、物流、控制和具有固定启用成本的凸优化问题。它比 MILP 更自然地保留范数结构，也比一般非线性整数规划更容易获得可靠的凸松弛和全局最优界。

本文介绍标准二阶锥、旋转二阶锥、MISOCP 的规范形式、与 MIQCP 的关系、分支定界、外逼近、Perspective 强化、Big-M、Gurobi 与 CPLEX 建模、数值稳定性和工程验证。公式采用飞书稳定支持的 LaTeX 子集。

---

## 一、什么是二阶锥

### 1.1 标准二阶锥

$n$ 维标准二阶锥定义为：

$$
K_n=\{(t,x):\|x\|_2\leq t\}
$$

其中：

$$
\|x\|_2=\sqrt{\sum_{i=1}^{n-1}x_i^2}
$$

约束：

$$
\|x\|_2\leq t
$$

自动隐含：

$$
t\geq0
$$

三维时，边界形状类似圆锥，因此也称 Lorentz cone 或 quadratic cone。

### 1.2 仿射二阶锥约束

工程中更常见的形式是：

$$
\|Fx+g\|_2\leq a^{T}x+b
$$

它要求右端：

$$
a^{T}x+b\geq0
$$

左侧是凸函数，右侧是仿射函数，因此可行域是凸集。

### 1.3 旋转二阶锥

旋转二阶锥定义为：

$$
2uv\geq\|w\|_2^2
$$

$$
u\geq0,\quad v\geq0
$$

它与标准二阶锥等价：

$$
\|(2w,u-v)\|_2\leq u+v
$$

旋转锥特别适合表达平方上界、二次透视和均方误差。

## 二、MISOCP 的规范形式

一个常见 MISOCP 可以写为：

$$
\min c^{T}x
$$

满足线性等式：

$$
Ax=b
$$

若干二阶锥约束：

$$
\|F_kx+g_k\|_2\leq a_k^{T}x+b_k
$$

以及整数条件：

$$
x_j\in Z,\quad j\in I
$$

二元变量满足：

$$
x_j\in\{0,1\}
$$

若去掉整数条件，模型就是连续 SOCP；加入整数变量后，可行域不再凸，但固定整数变量后得到的节点子问题仍可保持为凸 SOCP。

## 三、MISOCP 与其他模型的区别

| 模型 | 目标 | 约束 | 离散变量 |
|---|---|---|---|
| LP | 线性 | 线性 | 无 |
| MILP | 线性 | 线性 | 有 |
| SOCP | 线性或可锥化凸目标 | 线性加二阶锥 | 无 |
| MISOCP | 线性或可锥化凸目标 | 线性加二阶锥 | 有 |
| MIQP | 二次 | 线性 | 有 |
| MIQCP | 线性或二次 | 含二次约束 | 有 |

MISOCP 可以视为混合整数锥优化的一种。许多凸 MIQCP 可以转换为 MISOCP，但不是所有二次约束都能表示成凸二阶锥。

## 四、二阶锥与二次约束的等价关系

标准锥约束：

$$
\|Fx+g\|_2\leq t
$$

在 $t\geq0$ 条件下等价于：

$$
(Fx+g)^{T}(Fx+g)\leq t^2
$$

必须保留：

$$
t\geq0
$$

如果只写平方不等式而漏掉右端非负条件，那么负的 $t$ 也可能满足平方关系，模型将不再与原二阶锥等价。

更一般地，若 $Q$ 半正定并且：

$$
Q=R^{T}R
$$

则约束：

$$
x^{T}Qx\leq t^2
$$

可以写成：

$$
\|Rx\|_2\leq t
$$

因此，求解器可能把识别出的凸二次约束转换成二阶锥形式。

## 五、为什么锥形式重要

同一个数学关系可以写成范数约束或平方后的二次约束，但锥形式通常更直接地暴露凸结构。

潜在好处包括：

- 凸性更明确；
- 避免不必要的展开和抵消；
- 便于内点法利用锥结构；
- 便于构造对偶界和不可行证书；
- 便于使用旋转锥表达 Perspective 结构；
- 对数值尺度和模型审查更友好。

具体求解器可能在预处理阶段自动转换 MIQCP 与 MISOCP，也可能提供参数控制保留二次形式、转换为标准锥或转换为分解的旋转锥形式。

## 六、连续 SOCP 的凸性

约束：

$$
\|Fx+g\|_2\leq a^{T}x+b
$$

定义的是凸可行域。若目标也是线性或凸且可锥化，连续模型是凸优化问题。

凸性意味着局部最优解也是全局最优解。在适当正则条件下，原始问题与对偶问题具有相同最优值，并可以使用原始—对偶内点法求解。

MISOCP 本身因整数变量而非凸，但节点连续松弛仍能提供全局有效界。

## 七、分支定界与锥松弛

把二元变量暂时放宽为：

$$
y_i\in[0,1]
$$

就得到连续 SOCP 松弛。对于最小化问题：

$$
z_{SOCP}\leq z_{MISOCP}
$$

如果松弛解中整数变量为：

$$
y_k=0.4
$$

可建立两个分支：

$$
y_k=0
$$

以及：

$$
y_k=1
$$

求解器反复求解节点锥松弛、更新理论界、寻找整数可行解并剪枝。

对于最小化问题，常见相对 gap 为：

$$
g=\frac{|z_P-z_D|}{\max(1,|z_P|)}
$$

其中 $z_P$ 是当前可行解目标值，$z_D$ 是全局下界。

## 八、外逼近

标准二阶锥：

$$
\|u\|_2\leq t
$$

可以用一系列线性支撑不等式进行外逼近。对任意满足 $\|d\|_2\leq1$ 的方向 $d$，都有：

$$
d^{T}u\leq t
$$

有限方向集合只给出多面体松弛。若当前解违反真实锥约束，可以在违反方向添加新的支撑平面，逐步收紧模型。

外逼近允许使用 MILP 框架处理锥结构，但所需切割数量可能很大。原生锥求解与外逼近哪种更好，取决于维度、整数结构、求解器和实例。

## 九、Perspective 强化

设二元变量 $y$ 控制连续变量 $x$ 是否启用：

$$
Ly\leq x\leq Uy
$$

如果启用时产生平方成本，可以引入 $t$：

$$
x^2\leq ty
$$

$$
t\geq0,\quad y\geq0
$$

它是旋转二阶锥结构。与弱的 Big-M 表达相比，Perspective Reformulation 往往给出更紧的连续松弛。

多个连续变量时可写为：

$$
\|Rx\|_2^2\leq ty
$$

该结构适合固定启用成本、机组启停、稀疏回归、设施开关与组合风险控制。

## 十、Big-M 与条件锥约束

若只有在 $y=1$ 时才要求：

$$
\|Fx+g\|_2\leq r
$$

一种 Big-M 表达是：

$$
\|Fx+g\|_2\leq r+M(1-y)
$$

但过大的 $M$ 会削弱松弛并放大数值风险。应从变量边界推导最小有效 $M$，或使用求解器支持的 indicator、原生逻辑结构和 Perspective 重构。

没有有限变量边界时，通常无法得到有效而紧的 Big-M。此时应重新审查模型结构，而不是随意放入极大常数。

## 十一、鲁棒线性约束

考虑不确定系数：

$$
a=\bar a+Fz
$$

其中扰动满足：

$$
\|z\|_2\leq\rho
$$

要求对所有允许扰动都满足：

$$
a^{T}x\leq b
$$

其鲁棒对应形式为：

$$
\bar a^{T}x+\rho\|F^{T}x\|_2\leq b
$$

这是一条二阶锥约束。如果模型中还存在设施选择、路径选择或资源启用变量，就形成 MISOCP。

鲁棒半径 $\rho$ 越大，方案越保守。它必须通过历史误差、统计置信或明确的风险政策校准。

## 十二、高斯机会约束

设随机向量的均值为 $\mu$，协方差为 $\Sigma$。线性随机约束为：

$$
a^{T}x\leq b
$$

在高斯假设和给定置信水平下，确定性等价形式常具有结构：

$$
\mu^{T}x+\kappa\|\Sigma^{1/2}x\|_2\leq b
$$

其中 $\kappa$ 是由允许违反概率决定的分位系数。

这说明机会约束在特定分布假设下可以转化为 SOCP。若分布假设错误或协方差估计不稳定，数学上的可行概率保证可能不成立，因此必须做样本外验证。

## 十三、投资组合中的 MISOCP

设 $w_i$ 是资产权重，$y_i$ 表示是否持有资产，$\Sigma$ 是协方差矩阵。

预算约束：

$$
\sum_i w_i=1
$$

持仓与选择联动：

$$
0\leq w_i\leq U_i y_i
$$

持仓数量限制：

$$
\sum_i y_i\leq K
$$

风险约束：

$$
\|Rw\|_2\leq\sigma
$$

其中：

$$
\Sigma=R^{T}R
$$

目标可以最大化期望收益：

$$
\max \sum_i\mu_iw_i
$$

风险锥负责组合波动，整数变量负责持仓数量、固定交易成本和最小批量。

## 十四、空间覆盖与网络设计

设 $p_j$ 是发射器或设施位置，$d_i$ 是需求点位置，$z_{ij}=1$ 表示设施 $j$ 覆盖需求点 $i$。

覆盖约束可以写为：

$$
\|p_j-d_i\|_2\leq r_j+M(1-z_{ij})
$$

每个需求点至少被一个设施覆盖：

$$
\sum_j z_{ij}\geq1
$$

若位置也是变量，该模型把欧氏距离、覆盖分配和设施选择结合在一起。Big-M 必须由位置区域直径和最大半径推导。

## 十五、Gurobi 建模示例

下面建立一个带持仓数量约束的组合模型。为保持示例清晰，使用对角风险矩阵。

```python
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("misocp_portfolio")

returns = [0.08, 0.11, 0.07, 0.10]
volatility = [0.20, 0.30, 0.15, 0.25]
n = len(returns)

w = model.addVars(n, lb=0.0, ub=1.0, name="weight")
y = model.addVars(n, vtype=GRB.BINARY, name="selected")
risk = model.addVar(lb=0.0, name="risk")

model.addConstr(gp.quicksum(w[i] for i in range(n)) == 1.0)
model.addConstr(gp.quicksum(y[i] for i in range(n)) <= 3)

for i in range(n):
    model.addConstr(w[i] <= 0.7 * y[i])

variance = gp.quicksum(
    volatility[i] * volatility[i] * w[i] * w[i]
    for i in range(n)
)
model.addQConstr(variance <= risk * risk)

expected_return = gp.quicksum(returns[i] * w[i] for i in range(n))
model.setObjective(expected_return - 0.5 * risk, GRB.MAXIMIZE)

model.Params.TimeLimit = 30
model.optimize()

if model.SolCount > 0:
    print("objective =", model.ObjVal)
    print("risk =", risk.X)
    for i in range(n):
        print(i, w[i].X, y[i].X)
```

约束 `variance <= risk * risk` 只有在 `risk >= 0` 时才与标准二阶锥语义一致。示例已通过变量下界显式保证这一点。

## 十六、DOcplex 建模示例

```python
from docplex.mp.model import Model

model = Model(name="misocp_portfolio")

returns = [0.08, 0.11, 0.07, 0.10]
volatility = [0.20, 0.30, 0.15, 0.25]
n = len(returns)

w = model.continuous_var_list(n, lb=0, ub=1, name="weight")
y = model.binary_var_list(n, name="selected")
risk = model.continuous_var(lb=0, name="risk")

model.add_constraint(model.sum(w) == 1)
model.add_constraint(model.sum(y) <= 3)

for i in range(n):
    model.add_constraint(w[i] <= 0.7 * y[i])

variance = model.sum(
    volatility[i] * volatility[i] * w[i] * w[i]
    for i in range(n)
)
model.add_constraint(variance <= risk * risk)

expected_return = model.sum(returns[i] * w[i] for i in range(n))
model.maximize(expected_return - 0.5 * risk)

solution = model.solve(log_output=True)

if solution is not None:
    print("objective =", solution.objective_value)
```

DOcplex 是建模层，本地求解需要兼容的 CPLEX 运行时和有效授权。

## 十七、数值稳定性

MISOCP 对变量尺度和锥边界较敏感。常见风险包括：

- 锥两侧的量级相差过大；
- 协方差或二次矩阵接近奇异；
- Big-M 远大于必要值；
- 变量缺少有效上下界；
- 平方形式引入巨大系数；
- 单位混用，例如元与万元、秒与小时；
- 把接近零的右端误当作严格正数。

### 17.1 变量缩放

可以定义：

$$
x_i=s_i\hat{x}_i
$$

使缩放变量 $\hat{x}_i$ 的典型量级接近 1，再变换线性和锥约束。

### 17.2 分解协方差矩阵

若风险矩阵 $\Sigma$ 半正定，可以使用：

$$
\Sigma=R^{T}R
$$

并写成：

$$
\|Rx\|_2\leq t
$$

如果估计矩阵存在微小负特征值，应先判断是采样误差、舍入误差还是模型本身非凸，不要直接忽略。

## 十八、性能改进顺序

求解慢时建议按以下顺序处理：

1. 检查锥约束方向和右端非负条件；
2. 缩紧整数与连续变量边界；
3. 从几何或业务范围推导最小 Big-M；
4. 使用原生锥或求解器可识别的凸二次形式；
5. 加入 Perspective 强化和有效不等式；
6. 消除对称性；
7. 提供高质量初始解；
8. 设置业务可接受的时间与 gap；
9. 在代表性实例集上调参。

模型结构通常比盲目增加线程和求解时间更重要。

## 十九、验证与测试

### 19.1 线性约束

独立验证：

$$
Ax\leq b+\varepsilon
$$

### 19.2 整数变量

整数变量应接近某个整数 $n_j$：

$$
|x_j-n_j|\leq\varepsilon,\quad n_j\in Z
$$

### 19.3 锥约束

对每个锥独立重算：

$$
\|F_kx+g_k\|_2-a_k^{T}x-b_k\leq\varepsilon
$$

并检查右端：

$$
a_k^{T}x+b_k\geq-\varepsilon
$$

### 19.4 基线与样本外测试

至少比较：

- 连续 SOCP 松弛；
- 外逼近 MILP；
- 去掉风险项的 MILP；
- 贪心或历史方案；
- 小规模穷举；
- 鲁棒与机会约束的样本外违反率。

## 二十、在战棋与游戏 AI 中的用途

### 20.1 鲁棒行动选择

设动作收益估计误差位于椭球集合中，可把最坏情形限制写成二阶锥约束。整数变量负责选动作和单位，锥约束负责限制不确定损失。

### 20.2 阵型半径与覆盖

设单位位置为 $p_u$，编队中心为 $c$，是否进入编队由 $y_u$ 控制：

$$
\|p_u-c\|_2\leq R+M(1-y_u)
$$

这可以表达编队覆盖、治疗范围、指挥范围和无线通信半径。

### 20.3 风险预算

若多个伤害或资源误差具有协方差结构，可使用：

$$
\|Rx\|_2\leq B
$$

控制联合风险，而不是简单相加各项最坏值。

### 20.4 工程边界

MISOCP 适合低频资源配置、任务选择与滚动规划，不替代每帧物理控制、碰撞响应和局部避障。最终动作仍应由路径规划器和原生规则验证。

## 二十一、何时不应使用 MISOCP

以下情况可能更适合其他模型：

- 只有线性约束和线性目标：使用 MILP；
- 没有整数变量：使用 SOCP；
- 只有二次目标且约束线性：使用 MIQP；
- 二次约束无法转换为凸锥：考虑非凸 MIQCP 或全局优化；
- 存在复杂时间区间和资源日历：考虑约束规划；
- 高频在线控制且时间预算极小：考虑预计算、近似策略或 MPC。

模型选择应依据结构、求解性能和验证结果，而不是追求更复杂的数学形式。

## 二十二、结论

MISOCP 把离散选择与凸范数约束结合起来。它的核心优势是保留风险、距离、鲁棒性和平方关系的锥结构，同时利用整数变量表达启用、分配和组合规则。

可靠的 MISOCP 工程需要做到：

1. 明确标准锥和旋转锥的定义；
2. 在平方转换中保留右端非负条件；
3. 为 Big-M、变量边界和不确定半径提供数据依据；
4. 使用连续锥松弛、最优界和独立验证判断结果质量；
5. 对鲁棒与机会约束做样本外校准。

锥模型不是把平方项换一种写法，而是把可利用的凸结构明确交给求解器。

## 参考资料

- [MOSEK Modeling Cookbook：Conic Quadratic Optimization](https://docs.mosek.com/modeling-cookbook/cqo.html)
- [MOSEK Modeling Cookbook：Mixed Integer Optimization](https://docs.mosek.com/modeling-cookbook/mio.html)
- [Gurobi：Constraints and Second-Order Cone Forms](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/constraints.html)
- [Gurobi：PreMIQCPForm Parameter](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
- [IBM：Second-Order Cone Programming](https://www.ibm.com/docs/en/icos/22.1.2?topic=qcp-second-order-cone-programming-socp-non-psd)
- [IBM：Solving MIP Problems with Quadratic Terms](https://www.ibm.com/docs/en/icos/22.1.2?topic=optimization-solving-mixed-integer-programming-problems-quadratic-terms)
