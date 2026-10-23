# 混合整数二次规划：理论、建模与求解实践

## 摘要

混合整数二次规划（Mixed-Integer Quadratic Programming，MIQP）同时包含离散决策和二次目标。它可以描述“是否选择”与“选择多少”之间的联合关系，也可以表达平方偏差、波动、风险、平滑成本和变量之间的交互作用。

MIQP 广泛用于投资组合、设施选址、生产计划、能源调度、控制、机器学习特征选择、排程和游戏资源分配。它比线性规划和混合整数线性规划更有表达力，但凸性、松弛质量、变量边界和数值尺度会显著影响求解难度。

本文介绍 MIQP 的严格定义、凸与非凸结构、MIQP 与 MIQCP 的区别、分支定界、凸松弛、乘积线性化、McCormick 包络、Perspective 强化、Gurobi 与 CPLEX 建模、数值诊断和工程验证。公式采用飞书稳定支持的 LaTeX 子集。

---

## 一、MIQP 的数学定义

MIQP 的常见形式是：

$$
\min \frac{1}{2}x^{T}Qx+c^{T}x
$$

满足线性约束：

$$
Ax \leq b
$$

变量边界：

$$
l \leq x \leq u
$$

以及部分变量的整数要求：

$$
x_j \in Z, \quad j \in I
$$

其中：

- $x$ 是决策变量向量；
- $Q$ 是二次目标矩阵；
- $c$ 是线性目标系数；
- $A$ 和 $b$ 定义线性约束；
- $I$ 是整数变量下标集合。

二元变量是最常见的整数变量：

$$
x_j \in \{0,1\}
$$

它可以表示是否启用设备、是否选择资产、是否分配任务或某项逻辑条件是否成立。

## 二、MIQP、QP、MILP 与 MIQCP 的区别

| 模型 | 目标 | 约束 | 变量 |
|---|---|---|---|
| LP | 线性 | 线性 | 连续 |
| QP | 二次 | 线性 | 连续 |
| MILP | 线性 | 线性 | 连续加整数 |
| MIQP | 二次 | 线性 | 连续加整数 |
| QCP | 线性或二次 | 含二次约束 | 连续 |
| MIQCP | 线性或二次 | 含二次约束 | 连续加整数 |

关键区别是：**MIQP 的约束仍然是线性的，二次项只出现在目标函数中。**

如果模型含有：

$$
x^{T}Rx+a^{T}x \leq d
$$

这样的二次约束，它就属于 QCP 或 MIQCP，而不是严格意义上的 MIQP。

## 三、二次目标的展开

矩阵形式：

$$
\frac{1}{2}x^{T}Qx+c^{T}x
$$

展开后为：

$$
\frac{1}{2}\sum_i Q_{ii}x_i^2
+\frac{1}{2}\sum_i\sum_{j\neq i}Q_{ij}x_ix_j
+\sum_i c_ix_i
$$

若 $Q$ 对称，则交叉项可以合并。建模时必须确认求解器 API 对二次矩阵系数与代数表达式系数的约定，特别是目标前是否包含 $1/2$。

常见二次项含义包括：

- $x_i^2$：平方惩罚或平滑成本；
- $(x_i-r_i)^2$：偏离目标值的代价；
- $x_ix_j$：两个决策之间的相互作用；
- $x^{T}\Sigma x$：投资组合方差；
- $\|Hx-y\|_2^2$：最小二乘误差。

## 四、凸性决定问题性质

对于最小化问题，如果：

$$
Q \succeq 0
$$

即 $Q$ 是半正定矩阵，那么连续二次目标是凸函数。可以通过特征值判断：

$$
\lambda_{min}(Q) \geq 0
$$

此时称为凸 MIQP。固定整数变量后，每个节点的连续子问题是凸 QP，可以获得可靠的全局下界。

如果 $Q$ 存在负特征值：

$$
\lambda_{min}(Q) < 0
$$

则目标是非凸的。非凸 MIQP 需要全局优化技术，例如空间分支定界、凸包络和额外松弛，通常比同规模凸 MIQP 困难得多。

需要注意：即使 $Q$ 半正定，整数变量仍会使问题成为组合优化问题，一般不能按连续凸优化的复杂度理解。

## 五、三个典型应用

### 5.1 带固定成本的投资组合

设 $w_i$ 是资产权重，$y_i$ 表示是否持有资产，$\Sigma$ 是协方差矩阵，$\mu_i$ 是期望收益。

风险与收益目标可以写为：

$$
\min \gamma w^{T}\Sigma w-\sum_i\mu_iw_i
$$

预算约束：

$$
\sum_i w_i=1
$$

持仓与选择变量联动：

$$
0\leq w_i\leq U_i y_i
$$

限制最多持有 $K$ 个资产：

$$
\sum_i y_i\leq K
$$

其中：

$$
y_i\in\{0,1\}
$$

二次项表示组合方差，整数变量表示持仓数量、固定交易成本或最小交易批量。

### 5.2 生产平滑与设备启停

设 $x_t$ 是时段 $t$ 的产量，$y_t$ 表示设备是否开启。生产变化惩罚为：

$$
\sum_{t=2}^{T}(x_t-x_{t-1})^2
$$

设备联动约束为：

$$
L_ty_t\leq x_t\leq U_ty_t
$$

模型可以同时考虑固定启机成本、线性生产成本和二次平滑成本。

### 5.3 稀疏回归与特征选择

设 $\beta_j$ 是回归系数，$z_j$ 表示是否选择特征。目标为：

$$
\min \|X\beta-y\|_2^2
$$

稀疏约束为：

$$
-M_jz_j\leq\beta_j\leq M_jz_j
$$

$$
\sum_j z_j\leq K
$$

整数变量实现精确的特征数量限制，二次目标表示残差平方和。

## 六、连续松弛与节点下界

把整数约束临时改成连续区间，例如：

$$
y_i\in[0,1]
$$

就得到连续松弛。对于凸最小化 MIQP：

$$
z_{relax}\leq z_{MIQP}
$$

连续松弛为整数问题提供下界。下界越接近真实整数最优值，分支定界通常越快。

一个模型即使变量和约束数量不多，如果松弛很弱，也可能产生巨大的搜索树。因此，求解性能常常更取决于建模强度，而不是表面规模。

## 七、分支定界与分支切割

若松弛解中的整数变量出现：

$$
x_k=2.4
$$

可以建立两个子问题：

$$
x_k\leq2
$$

以及：

$$
x_k\geq3
$$

求解器在树中维护：

- incumbent：当前最好的整数可行解；
- best bound：所有未排除节点的最好理论界；
- gap：当前解与理论界之间的差距。

对于最小化问题，常见相对差距定义为：

$$
g=\frac{|z_P-z_D|}{\max(1,|z_P|)}
$$

其中 $z_P$ 是当前可行解目标值，$z_D$ 是理论下界。

切割平面是所有整数可行解都满足、但能排除部分松弛解的不等式：

$$
\alpha^{T}x\leq\beta
$$

切割改善理论界，启发式改善 incumbent，两者共同缩小 gap。

## 八、二元乘积的精确线性化

若：

$$
z=x_1x_2
$$

且：

$$
x_1,x_2\in\{0,1\}
$$

可以用以下线性约束精确替代：

$$
z\leq x_1
$$

$$
z\leq x_2
$$

$$
z\geq x_1+x_2-1
$$

$$
z\geq0
$$

因此，含二元乘积的 MIQP 有时可以完全转化为 MILP。转化后是否更快取决于模型规模、松弛质量和求解器实现，不能仅凭“线性模型更简单”作判断。

## 九、二元变量与连续变量的乘积

设：

$$
z=xy
$$

其中：

$$
y\in\{0,1\}
$$

$$
L\leq x\leq U
$$

可以使用以下精确线性化：

$$
z\leq Uy
$$

$$
z\geq Ly
$$

$$
z\leq x-L(1-y)
$$

$$
z\geq x-U(1-y)
$$

边界 $L$ 和 $U$ 必须有效且尽可能紧。宽松边界会直接削弱线性化后的松弛。

## 十、McCormick 包络

设：

$$
z=xy
$$

并且：

$$
L_x\leq x\leq U_x
$$

$$
L_y\leq y\leq U_y
$$

双线性项的 McCormick 凸包络由四个不等式构成：

$$
z\geq L_xy+L_yx-L_xL_y
$$

$$
z\geq U_xy+U_yx-U_xU_y
$$

$$
z\leq U_xy+L_yx-U_xL_y
$$

$$
z\leq L_xy+U_yx-L_xU_y
$$

对于一般连续变量，这是一种松弛而不一定是精确等价。空间分支定界通过不断缩小变量区间，使包络逐渐变紧。

## 十一、Perspective 强化

考虑带开关变量的二次成本：只有当 $y=1$ 时，连续变量 $x$ 才能非零。

$$
Ly\leq x\leq Uy
$$

若目标含：

$$
qx^2+fy
$$

简单连续松弛可能很弱。可引入变量 $t$ 并使用 Perspective 结构：

$$
x^2\leq ty
$$

$$
t\geq0
$$

再在目标中使用：

$$
qt+fy
$$

该结构在适用条件下可以显著加强松弛。具体实现可使用旋转锥、二次约束或求解器能够识别的等价形式。

## 十二、Big-M 与 Indicator Constraint

条件约束常被写成：

$$
a^{T}x\leq b+M(1-y)
$$

当 $y=1$ 时约束生效。$M$ 必须足够大，但过大会造成：

- 连续松弛过弱；
- 数值误差放大；
- 分支树增大；
- 可行性容差与逻辑语义发生冲突。

应从变量边界推导最小有效 $M$，或使用求解器的 indicator constraint。Indicator 的语义更清楚，但性能仍取决于内部重构和变量边界。

## 十三、Gurobi 建模示例

下面建立一个带固定选择成本和二次偏差成本的生产模型。

```python
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("miqp_production")

x = model.addVars(3, lb=0.0, name="production")
y = model.addVars(3, vtype=GRB.BINARY, name="enabled")

capacity = [8.0, 10.0, 7.0]
target = [5.0, 6.0, 4.0]
fixed_cost = [3.0, 4.0, 2.0]

for i in range(3):
    model.addConstr(x[i] <= capacity[i] * y[i])

model.addConstr(gp.quicksum(x[i] for i in range(3)) >= 12.0)

quadratic_cost = gp.quicksum(
    (x[i] - target[i]) * (x[i] - target[i])
    for i in range(3)
)
selection_cost = gp.quicksum(fixed_cost[i] * y[i] for i in range(3))

model.setObjective(quadratic_cost + selection_cost, GRB.MINIMIZE)
model.Params.TimeLimit = 30
model.optimize()

if model.SolCount > 0:
    print("objective =", model.ObjVal)
    print("bound =", model.ObjBound)
    for i in range(3):
        print(i, x[i].X, y[i].X)
```

读取变量解之前应确认 `SolCount > 0`。达到时间限制时，模型可能有可行解但尚未证明最优。

## 十四、DOcplex 建模示例

相同结构可以使用 DOcplex 表达：

```python
from docplex.mp.model import Model

model = Model(name="miqp_production")

capacity = [8.0, 10.0, 7.0]
target = [5.0, 6.0, 4.0]
fixed_cost = [3.0, 4.0, 2.0]

x = model.continuous_var_list(3, lb=0, name="production")
y = model.binary_var_list(3, name="enabled")

for i in range(3):
    model.add_constraint(x[i] <= capacity[i] * y[i])

model.add_constraint(model.sum(x) >= 12.0)

quadratic_cost = model.sum(
    (x[i] - target[i]) * (x[i] - target[i])
    for i in range(3)
)
selection_cost = model.sum(fixed_cost[i] * y[i] for i in range(3))

model.minimize(quadratic_cost + selection_cost)
solution = model.solve(log_output=True)

if solution is not None:
    print("objective =", solution.objective_value)
```

DOcplex 是建模层，本地求解需要兼容的 CPLEX 运行时和有效授权。

## 十五、凸 MIQP 与非凸 MIQP 的求解差异

### 15.1 凸 MIQP

凸 MIQP 的节点松弛是凸 QP。求解器可以获得可信下界，并使用分支定界、切割、启发式和预处理证明全局最优。

### 15.2 非凸 MIQP

非凸 MIQP 需要对连续变量和整数变量同时进行全局搜索。典型方法包括：

- 空间分支定界；
- McCormick 包络；
- Reformulation Linearization Technique；
- 局部可行解启发式；
- 凸下界与变量区间收缩。

非凸模型可能比同规模凸模型慢多个数量级。提交求解前应先检查 $Q$ 的特征值和建模符号，确认非凸性确实来自业务，而不是数据错误。

## 十六、数值稳定性

MIQP 同时受到整数搜索和二次数值计算影响。常见风险包括：

- 系数跨越过多数量级；
- $Q$ 接近半正定边界；
- 变量上界极宽；
- Big-M 过大；
- 原始数据含无意义的高精度小数；
- 二次矩阵非对称或构造重复；
- 目标各项量纲不一致。

### 16.1 对称化二次矩阵

二次型只由矩阵的对称部分决定：

$$
x^{T}Qx=x^{T}\left(\frac{Q+Q^{T}}{2}\right)x
$$

因此可先对 $Q$ 做对称化，再检查特征值和尺度。

### 16.2 变量缩放

如果变量 $x_i$ 的典型值是百万，而 $x_j$ 的典型值是千分之一，二次项会产生更大的尺度差异。可定义缩放变量：

$$
x_i=s_i\hat{x}_i
$$

使 $\hat{x}_i$ 的典型量级接近 1，再相应变换目标与约束。

## 十七、性能改进顺序

遇到求解慢，应按以下顺序处理：

1. 验证模型和数据正确性；
2. 判断 $Q$ 是否半正定；
3. 缩紧所有连续与整数变量边界；
4. 减少 Big-M，改用 indicator 或更强重构；
5. 检查能否精确线性化二元乘积；
6. 加入有效不等式和对称性破除约束；
7. 提供高质量初始解；
8. 设置业务可接受的时间与 gap；
9. 最后才进行参数调优。

模型改进通常比盲目增加线程和运行时间更有效。

## 十八、结果与停止条件

生产系统应至少记录：

- 求解状态；
- 当前可行解目标值；
- 最优界；
- 相对与绝对 gap；
- 运行时间；
- 分支节点数；
- 根节点松弛值；
- 参数、线程数与随机种子；
- 模型和输入数据版本。

必须区分：

- 找到一个可行解；
- 找到一个高质量解；
- 在给定容差内证明最优；
- 证明模型无解。

时间限制到达并不等于失败。如果已有可行解且 gap 满足业务要求，结果可能仍可部署。

## 十九、验证与测试

### 19.1 独立可行性检查

不要只信任求解器返回的变量值。应使用独立规则检查器验证：

$$
Ax\leq b+\varepsilon
$$

整数变量应接近某个整数 $n_j$：

$$
|x_j-n_j|\leq\varepsilon, \quad n_j\in Z
$$

### 19.2 目标重算

使用原始业务数据重新计算：

$$
z=\frac{1}{2}x^{T}Qx+c^{T}x
$$

并与求解器报告目标比较。

### 19.3 基线比较

至少与以下方法比较：

- 连续 QP 松弛；
- 忽略二次项的 MILP；
- 贪心或人工规则；
- 小规模穷举；
- 历史生产方案。

小规模穷举尤其适合验证整数逻辑和目标系数。

## 二十、在战棋与游戏 AI 中的用途

### 20.1 多单位联合行动

设 $x_{ua}=1$ 表示单位 $u$ 选择动作 $a$。每个单位选择一个动作：

$$
\sum_a x_{ua}=1
$$

同一目标格最多容纳一个单位：

$$
\sum_u\sum_{a\in A(u,g)}x_{ua}\leq1
$$

如果希望惩罚单位动作之间的冲突或奖励协同，可以加入二次交互项：

$$
\max \sum_u\sum_a v_{ua}x_{ua}
+\sum_{u<v}\sum_a\sum_b q_{uvab}x_{ua}x_{vb}
$$

正系数可以表示协同，负系数可以表示冲突。若变量全为二元变量，也可以考虑精确线性化为 MILP。

### 20.2 阵型偏差

设单位最终位置为 $p_u$，目标槽位为 $r_u$，可以最小化平方偏差：

$$
\min \sum_u \|p_u-r_u\|_2^2
$$

整数变量负责槽位选择和互斥，二次项负责平滑地惩罚偏离程度。

### 20.3 工程边界

MIQP 适合低频联合决策、资源分配和滚动规划，不应直接承担每帧物理控制、碰撞响应或动画执行。最终动作仍应由路径规划器和原生规则引擎验证。

## 二十一、何时不应使用 MIQP

以下情况可能更适合其他方法：

- 目标和约束全部线性：优先 MILP；
- 二次项只来自二元乘积且可轻易线性化：比较 MILP 与 MIQP；
- 没有整数变量：使用 QP 或 QCP；
- 存在复杂时间区间和资源日历：考虑约束规划；
- 问题是连续非线性且不可微：考虑专门非线性或无导数算法；
- 决策频率极高：考虑预计算、近似策略或模型预测控制。

选择模型应以结构和验证结果为依据，而不是追求公式复杂度。

## 二十二、结论

MIQP 的核心是把离散选择、连续数量与二次交互统一到同一模型中。

它的求解质量取决于四个方面：

1. 二次结构是否正确且凸性明确；
2. 连续松弛是否足够强；
3. 变量边界、线性化和数值尺度是否合理；
4. 可行解、最优界与最终结果是否经过独立验证。

凸 MIQP 已有成熟的工业求解流程；非凸 MIQP 则需要更谨慎的全局优化、边界设计和计算预算。一个表达更复杂的模型不一定更准确，只有经过数据校准、基线比较和回放验证的二次项才值得保留。

## 参考资料

- [Gurobi：Objectives and Quadratic Models](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/objectives.html)
- [Gurobi Optimizer Reference Manual](https://docs.gurobi.com/projects/optimizer/en/current/)
- [IBM：Solving MIP Problems with Quadratic Terms](https://www.ibm.com/docs/en/icos/22.1.2?topic=optimization-solving-mixed-integer-programming-problems-quadratic-terms)
- [IBM：Solving Problems with a Quadratic Objective](https://www.ibm.com/docs/en/icos/22.1.2?topic=optimization-solving-problems-quadraticobjective-qp)
- [IBM：What Does CPLEX Solve?](https://www.ibm.com/docs/en/icos/22.1.1?topic=optimizer-what-does-cplex-solve)
- [IBM：Quadratic Programming](https://www.ibm.com/docs/en/icos/22.1.1?topic=areas-quadratic-programming)
