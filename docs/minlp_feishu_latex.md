# 混合整数非线性规划：理论、算法与工程实践

## 摘要

混合整数非线性规划（Mixed-Integer Nonlinear Programming，MINLP）同时包含连续变量、整数变量和非线性目标或约束。它可以表达设备启停、工艺设计、能源调度、网络设计、投资选择、非线性风险、离散控制和复杂资源配置。

MINLP 不是单一难度等级。凸 MINLP 可以利用凸性构造可靠的全局界；非凸 MINLP 还需要空间分支定界、凸包络、区间传播和全局下界。只调用一个局部 NLP 求解器，通常不能证明非凸 MINLP 的全局最优性。

本文介绍 MINLP 的规范形式、凸性判定、NLP 分支定界、外逼近、LP/NLP Branch-and-Bound、广义 Benders、空间分支定界、McCormick 包络、Perspective、可行性泵、求解器选择、Pyomo/SCIP 与 MindtPy 示例、数值稳定性和独立验证。公式采用飞书稳定支持的 LaTeX 子集。

---

## 一、MINLP 的定义

一个常见 MINLP 可以写为：

$$
\min f(x,y)
$$

满足非线性约束：

$$
g_i(x,y)\leq0,\quad i=1,\ldots,m
$$

线性约束：

$$
Ax+By\leq d
$$

连续变量：

$$
l\leq x\leq u
$$

整数变量：

$$
y_j\in Z,\quad j\in I
$$

其中 $x$ 表示连续决策，$y$ 表示整数或二元决策。函数 $f$ 或 $g_i$ 中只要存在不能归入线性、二次或已知锥结构的一般非线性关系，模型通常就被称为 MINLP。

## 二、MINLP 与其他模型的区别

| 模型 | 目标与约束结构 | 整数变量 |
|---|---|---|
| LP | 线性 | 无 |
| MILP | 线性 | 有 |
| NLP | 一般非线性 | 无 |
| MIQP/MIQCP | 二次结构 | 有 |
| MISOCP | 二阶锥结构 | 有 |
| MIECP | 指数锥结构 | 有 |
| MINLP | 一般非线性结构 | 有 |

如果非线性可以精确改写成二阶锥、指数锥、幂锥或线性约束，优先使用更专门的模型类别。结构化模型通常更容易获得稳定松弛、全局界和高性能实现。

## 三、凸 MINLP 与非凸 MINLP

### 3.1 凸 MINLP

对于最小化问题，如果：

- 目标函数 $f$ 对连续变量是凸函数；
- 小于等于约束中的 $g_i$ 是凸函数；
- 非线性等式是仿射等式；
- 连续变量定义域是凸集；

则固定整数变量后得到凸 NLP 子问题。

凸性的重要意义是：连续子问题的局部最优解也是全局最优解，切平面可以提供全局有效的外逼近。

### 3.2 非凸 MINLP

下列结构常导致非凸性：

$$
xy
$$

$$
\frac{x}{y}
$$

$$
\sin x
$$

$$
x^3-xy
$$

以及一般非线性等式：

$$
h(x,y)=0
$$

非凸模型可能有多个局部最优点。局部 NLP 求解器从不同初值出发可能返回不同结果，因此需要区分局部可行解、局部最优解和经过全局界证明的解。

## 四、局部最优与全局最优

设可行域为 $S$。局部最优解 $x^{L}$ 只要求在某个邻域内满足：

$$
f(x^{L})\leq f(x)
$$

全局最优解 $x^{G}$ 要求对所有可行点满足：

$$
f(x^{G})\leq f(x),\quad x\in S
$$

对于凸问题，两者一致。对于非凸问题，KKT 条件通常只提供局部必要条件，不能自动证明全局最优。

工程报告中必须说明：

- 使用的是局部还是全局算法；
- 是否获得有效全局界；
- 当前 gap 是全局 gap 还是局部停止指标；
- 非凸函数是否全部处于求解器支持范围内。

## 五、连续松弛

把整数变量放宽为连续变量：

$$
y_j\in[l_j,u_j]
$$

得到连续 NLP 松弛。

对于最小化问题，若松弛被全局求解，则：

$$
z_{relax}\leq z_{MINLP}
$$

如果连续松弛只求到局部最优，其目标值不一定是全局有效下界。这是非凸 MINLP 中非常关键的区别。

## 六、NLP 分支定界

NLP-based Branch-and-Bound 在每个节点固定或收紧部分整数变量边界，然后求解连续 NLP 子问题。

若松弛解中：

$$
y_k=2.4
$$

可以建立两个分支：

$$
y_k\leq2
$$

以及：

$$
y_k\geq3
$$

对于凸 MINLP，节点 NLP 的全局最优值可作为可靠下界。对于非凸 MINLP，如果节点只由局部 NLP 求解器处理，该值可能不是有效全局下界。

## 七、外逼近

外逼近（Outer Approximation，OA）在 NLP 子问题与 MILP 主问题之间交替。

对凸函数 $g(x)$，在点 $\bar x$ 的一阶线性化为：

$$
g(x)\geq g(\bar x)+\nabla g(\bar x)^{T}(x-\bar x)
$$

因此，约束：

$$
g(x)\leq0
$$

产生全局有效的必要条件：

$$
g(\bar x)+\nabla g(\bar x)^{T}(x-\bar x)\leq0
$$

对于凸目标，引入目标上图变量 $\eta$：

$$
\eta\geq f(x)
$$

并加入目标切平面：

$$
\eta\geq f(\bar x)+\nabla f(\bar x)^{T}(x-\bar x)
$$

OA 主问题是 MILP，负责选择整数方案并给出下界；固定整数变量后的 NLP 子问题负责恢复非线性可行性和更新可行解。

对非凸函数，切线不一定是全局下界，因此普通 OA 不能直接提供全局保证。

## 八、LP/NLP Branch-and-Bound

LP/NLP Branch-and-Bound 把 OA 切平面放入单棵分支定界树中。每当得到新的整数候选点，就求解 NLP 子问题并动态加入线性化切割。

与多轮 OA 相比，它可以复用一棵 MILP 搜索树，但需要支持惰性约束或持久化求解器接口。Pyomo MindtPy 官方文档说明，其单树实现目前依赖特定的 CPLEX 或 Gurobi persistent 接口。

## 九、广义 Benders 分解

广义 Benders 分解把整数决策留在主问题，把连续非线性变量放入子问题。

给定整数方案 $y^k$，求解：

$$
\min_x f(x,y^k)
$$

满足：

$$
g_i(x,y^k)\leq0
$$

子问题的对偶信息用于生成关于 $y$ 的最优性割或可行性割。

这种方法适合整数变量数量相对较少、固定整数后连续子问题结构良好的模型。若子问题非凸或对偶不可靠，经典 Benders 割可能失去全局有效性。

## 十、空间分支定界

非凸全局求解器通常使用空间分支定界。它不仅对整数变量分支，也可能对连续变量的定义域分支。

若：

$$
l_x\leq x\leq u_x
$$

可在中点 $m$ 处分成：

$$
l_x\leq x\leq m
$$

以及：

$$
m\leq x\leq u_x
$$

定义域缩小时，非凸函数的凸包络通常会变紧，从而改善全局下界。

Gurobi 当前官方文档说明，其受支持的非线性模型使用空间分支定界和动态线性外逼近。SCIP 官方文档说明，其独立求解器对 MINLP 使用基于 LP 的空间 branch-and-cut。

## 十一、McCormick 包络

考虑双线性项：

$$
w=xy
$$

已知边界：

$$
l_x\leq x\leq u_x
$$

$$
l_y\leq y\leq u_y
$$

McCormick 包络由四个线性不等式组成：

$$
w\geq l_xy+l_yx-l_xl_y
$$

$$
w\geq u_xy+u_yx-u_xu_y
$$

$$
w\leq u_xy+l_yx-u_xl_y
$$

$$
w\leq l_xy+u_yx-l_xu_y
$$

边界越紧，包络越强。空间分支通过不断缩小 $x$ 或 $y$ 的区间来收紧这些不等式。

## 十二、区间传播与范围缩减

全局求解器会利用约束收紧变量范围。例如：

$$
x^2+y^2\leq R^2
$$

可以推出：

$$
-R\leq x\leq R
$$

$$
-R\leq y\leq R
$$

范围缩减的作用包括：

- 收紧 McCormick 包络；
- 降低 Big-M；
- 减少无效搜索区域；
- 改善非线性函数的数值尺度；
- 更快发现不可行节点。

非凸 MINLP 中，有限且紧的变量边界往往是能否获得全局证明的关键。

## 十三、可行性泵

MINLP 可行性泵在两类点之间迭代：

- 满足整数条件但可能违反非线性约束的点；
- 满足非线性约束但整数变量可能分数化的点。

一种距离目标为：

$$
\min\|y-\bar y\|_1
$$

其中 $\bar y$ 是当前整数候选。可行性泵主要用于尽快寻找可行解，不等同于全局最优证明。

Pyomo MindtPy 提供 FP 策略，也可把它用于 OA 初始化。

## 十四、Big-M 与条件非线性约束

若只在 $y=1$ 时启用：

$$
g(x)\leq0
$$

常见 Big-M 表达为：

$$
g(x)\leq M(1-y)
$$

其中：

$$
y\in\{0,1\}
$$

$M$ 必须覆盖 $y=0$ 时 $g(x)$ 的最大可能值。若边界不足，无法得到可靠的有限 $M$。

过大的 $M$ 会导致：

- 连续松弛很弱；
- 分支树巨大；
- 数值误差放大；
- 整数容差与约束违反相互作用；
- 非线性子问题更难初始化。

应优先考虑 indicator、凸包重构、Perspective 或显式析取建模。

## 十五、二元变量与连续变量乘积的精确线性化

若：

$$
w=xy
$$

$$
y\in\{0,1\}
$$

$$
L\leq x\leq U
$$

则可使用四个线性约束精确表达：

$$
w\leq Uy
$$

$$
w\geq Ly
$$

$$
w\leq x-L(1-y)
$$

$$
w\geq x-U(1-y)
$$

这类结构不必保留为一般 MINLP。识别并线性化它，通常能显著提高性能。

## 十六、Perspective 强化

设 $y$ 控制连续变量 $x$ 是否启用，凸成本为 $f(x)$。Perspective 函数为：

$$
yf(x/y)
$$

平方成本的典型形式为：

$$
x^2\leq ty
$$

$$
t\geq0,\quad y\geq0
$$

这可以表示为旋转二阶锥。若模型的非线性主要来自此类结构，重构后可能从 MINLP 降为更容易处理的 MISOCP。

## 十七、分段线性近似

对单变量非线性函数 $f(x)$，可以在节点：

$$
x_0<x_1<\cdots<x_K
$$

上建立分段线性近似。

近似误差应定义为：

$$
E=\max_{x\in[l,u]}|f(x)-\hat f(x)|
$$

必须明确近似是外逼近、内逼近还是双边近似。若约束可行性依赖近似方向，错误方向可能产生原模型不可行的解。

分段线性化可以把部分 MINLP 转为 MILP，但维度、分段数和离散变量数量可能迅速增加。

## 十八、典型建模场景

### 18.1 设备启停与非线性能耗

设 $y_i$ 表示设备是否启用，$q_i$ 表示负载：

$$
0\leq q_i\leq U_iy_i
$$

非线性能耗可写为：

$$
c_i(q_i)=a_iq_i^2+b_iq_i+f_iy_i
$$

如果二次项是凸的，模型可能进一步转为 MIQP 或 MISOCP。

### 18.2 工艺流程设计

整数变量选择设备或反应路径，连续变量表示流量、温度和压力，非线性约束来自质量守恒、热力学和反应动力学。

### 18.3 Pooling 与混合

浓度与流量乘积常形成双线性项：

$$
w_{ij}=q_{ij}c_i
$$

这通常是非凸 MINLP，需要 McCormick 包络、范围缩减或专门的 pooling 重构。

### 18.4 选址与连续设计

整数变量决定是否建设设施，连续变量决定容量、位置和服务水平，成本或可靠性可能是非线性函数。

### 18.5 离散控制

开关模式由整数变量表示，状态和控制满足非线性动力学。时间离散后可形成大型 MINLP，但实时求解通常十分困难。

## 十九、Pyomo 与 SCIP 示例

下面建立一个凸 MINLP。二元变量 $y$ 决定是否启用连续决策 $x$。

目标：

$$
\min (x-4)^2+3y
$$

联动约束：

$$
0\leq x\leq6y
$$

对应代码：

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.x = pyo.Var(bounds=(0.0, 6.0), initialize=2.0)
model.y = pyo.Var(domain=pyo.Binary)

model.link = pyo.Constraint(expr=model.x <= 6.0 * model.y)
model.objective = pyo.Objective(
    expr=(model.x - 4.0) ** 2 + 3.0 * model.y,
    sense=pyo.minimize,
)

solver = pyo.SolverFactory("scip")
results = solver.solve(model, tee=True)

print("termination =", results.solver.termination_condition)
print("objective =", pyo.value(model.objective))
print("x =", pyo.value(model.x))
print("y =", pyo.value(model.y))
```

运行前需要正确安装 SCIP，并确保 Pyomo 能找到其可执行程序或接口。

## 二十、Pyomo MindtPy 示例

MindtPy 是 Pyomo 中的 MINLP 分解工具箱，需要一个 MILP 求解器和一个 NLP 求解器。

下面的模型结构与官方文档示例一致：

```python
import pyomo.environ as pyo

model = pyo.ConcreteModel()
model.x = pyo.Var(bounds=(1.0, 10.0), initialize=5.0)
model.y = pyo.Var(domain=pyo.Binary)

model.c1 = pyo.Constraint(
    expr=(model.x - 4.0) ** 2 - model.x
    <= 50.0 * (1.0 - model.y)
)
model.c2 = pyo.Constraint(
    expr=model.x * pyo.log(model.x) + 5.0
    <= 50.0 * model.y
)
model.objective = pyo.Objective(
    expr=model.x,
    sense=pyo.minimize,
)

results = pyo.SolverFactory("mindtpy").solve(
    model,
    strategy="OA",
    mip_solver="glpk",
    nlp_solver="ipopt",
    time_limit=600,
    tee=True,
)

print("termination =", results.solver.termination_condition)
print("objective =", pyo.value(model.objective))
print("x =", pyo.value(model.x))
print("y =", pyo.value(model.y))
```

OA 依赖凸性假设。对非凸 MINLP，不能仅把 `strategy="OA"` 保持不变并宣称获得全局最优。

MindtPy 的 GOA 需要有效的全局松弛，并要求 NLP 子问题由全局 NLP 求解器处理。官方示例使用 BARON；SCIP 也被列为可用于全局 NLP 子问题的求解器。

## 二十一、求解器选择

| 工具 | 主要定位 | 全局性说明 |
|---|---|---|
| SCIP | MIP 与 MINLP 框架 | 对受支持且有界的 MINLP 使用空间 branch-and-cut |
| Gurobi | 通用数学规划与受支持的非线性模型 | 当前版本对受支持表达式使用空间分支定界和动态外逼近 |
| BARON | 代数 NLP/MINLP 全局优化 | 在文档所述条件下进行确定性全局优化 |
| Bonmin | 凸 MINLP 算法集合 | 凸情形可作为精确算法；非凸情形仅作为启发式 |
| MindtPy | Pyomo 分解框架 | OA 主要面向凸 MINLP；GOA 需要全局子求解器与有效包络 |
| Ipopt | 连续 NLP 局部求解器 | 不处理整数变量，非凸时只寻求局部解 |

实际支持的函数、许可证、接口和版本会变化，必须查看当前官方文档并用小模型验证。

## 二十二、数值稳定性

### 22.1 变量尺度

若变量量级差异过大，可以定义：

$$
x_i=s_i\hat{x}_i
$$

使缩放后的变量典型量级接近 1。

### 22.2 有效定义域

对数要求：

$$
x>0
$$

除法要求分母远离零：

$$
|y|\geq\varepsilon
$$

平方根要求：

$$
x\geq0
$$

不应依赖求解器在非法点自动恢复。应通过变量边界和约束明确给出有效域。

### 22.3 导数质量

梯度或 Hessian 错误会破坏 NLP 子问题。可用有限差分检查解析导数：

$$
\frac{f(x+he_i)-f(x-he_i)}{2h}
$$

并与解析梯度第 $i$ 个分量比较。

### 22.4 原表达式残差

现代求解器可能把复杂表达式拆成辅助变量链。辅助模型满足容差，不保证原始聚合表达式的误差同样小。应使用最终变量值重新计算原始函数。

## 二十三、性能改进顺序

求解慢时建议按以下顺序处理：

1. 判断模型究竟是凸还是非凸；
2. 把可线性化的二元乘积改写成 MILP；
3. 把二次、范数、指数结构改写成专门模型；
4. 为所有非线性变量设置紧的有限边界；
5. 缩小 Big-M；
6. 使用 Perspective、McCormick 和有效不等式；
7. 统一尺度并检查定义域；
8. 提供高质量初始解；
9. 利用问题分解和对称破除；
10. 在代表性实例集上选择算法与参数。

模型重构通常比单纯增加求解时间更有效。

## 二十四、结果验证

### 24.1 线性约束

检查：

$$
Ax+By-d\leq\varepsilon
$$

### 24.2 非线性约束

对每条约束独立重算：

$$
g_i(x,y)\leq\varepsilon
$$

### 24.3 整数性

$$
|y_j-n_j|\leq\varepsilon,\quad n_j\in Z
$$

### 24.4 目标函数

使用原始数据重算：

$$
z=f(x,y)
$$

### 24.5 全局证明

对于最小化问题，应同时记录可行解上界 $z_P$ 和全局下界 $z_D$：

$$
z_D\leq z^*\leq z_P
$$

若没有有效 $z_D$，就不能报告经过证明的全局 gap。

### 24.6 多起点测试

局部算法应使用多个初值：

$$
x^{(1)},x^{(2)},\ldots,x^{(K)}
$$

若结果明显不同，说明模型存在局部结构或数值敏感性。多起点可以改善解质量，但不能替代全局证明。

## 二十五、在游戏 AI 与仿真中的用途

### 25.1 离散战术与连续控制

整数变量选择战术模式、目标或技能，连续变量决定速度、角度、资源分配和时间。非线性约束可以表达命中率、能耗或运动学。

### 25.2 编队与非线性风险

离散变量决定单位归属，连续变量决定位置。碰撞、视野、火力和风险可能形成非线性耦合。

### 25.3 资源启用与收益饱和

收益函数可能具有边际递减：

$$
r(x)=a(1-e^{-bx})
$$

整数变量决定是否启用资源，连续变量决定投入强度。

### 25.4 工程边界

MINLP 适合低频战略规划、离线设计和滚动决策，不适合直接承担每帧碰撞处理或毫秒级动作控制。实时系统应准备时间限制、可行初始解、降级策略和结果验证器。

## 二十六、何时不应使用 MINLP

以下情况应优先选择更简单的形式：

- 非线性可精确线性化：使用 MILP；
- 只有凸二次结构：使用 MIQP/MIQCP；
- 只有范数结构：使用 MISOCP；
- 只有指数与熵结构：使用混合整数指数锥；
- 没有整数变量：使用 NLP 或凸锥优化；
- 只需近似且误差可控：使用分段线性 MILP；
- 高频在线控制：使用 MPC、近似策略或预计算方案。

## 二十七、结论

MINLP 是表达能力很强、但计算与验证成本也很高的模型类别。可靠实践的核心是先识别结构，再选择算法。

需要做到：

1. 明确凸性与全局性；
2. 区分局部 NLP 解和全局有效界；
3. 为非线性变量提供紧边界；
4. 使用 McCormick、Perspective 和范围缩减强化松弛；
5. 尽可能转为 MILP、MIQP、MISOCP 或指数锥模型；
6. 根据模型结构选择 SCIP、Gurobi、BARON、Bonmin 或 MindtPy；
7. 独立重算原始非线性约束和目标。

## 参考资料

- [SCIP Documentation：Supported Optimization Problems](https://www.scipopt.org/doc/html/WHATPROBLEMS.php)
- [SCIP Documentation：Overview](https://scipopt.org/doc/html/)
- [Gurobi Documentation：Nonlinear Constraints](https://docs.gurobi.com/projects/optimizer/en/current/features/nonlinear.html)
- [Pyomo Documentation：MindtPy Solver](https://pyomo.readthedocs.io/en/stable/explanation/solvers/mindtpy.html)
- [COIN-OR Documentation：Bonmin User Manual](https://www.coin-or.org/Bonmin/Intro.html)
- [COIN-OR Documentation：Ipopt](https://coin-or.github.io/Ipopt/)
- [BARON User Manual](https://minlp.com/baron-user-manual)
