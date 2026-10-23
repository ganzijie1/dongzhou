# COPT 求解器：从数学模型到 Python 工程实践

## 摘要

COPT（Cardinal Optimizer，杉数求解器）是一套高性能数学规划求解器，用于求解大规模连续优化、离散优化、锥优化和部分非线性优化问题。它提供 C、C++、C#、Java、Python 等原生接口，也能通过 AMPL、Pyomo、PuLP、CVXPY 等建模层调用。

本文依据 COPT 8.0 官方用户手册，介绍 COPT 的问题类型、算法体系、安装与授权、`coptpy` 建模流程、LP/MILP/SOCP 示例、求解状态、参数、GPU 能力、不可行性诊断、性能调优和工程验证。

---

## 一、COPT 是什么

COPT 的核心职责是：接收数学模型，利用数值优化算法寻找满足约束的最优解，并给出可行性、最优性和求解进度信息。

一个典型优化模型包含：

- 决策变量；
- 目标函数；
- 约束条件；
- 变量边界；
- 连续、整数或二元变量类型。

例如，线性规划的标准形式可写为：

$$
\min c^{T}x
$$

满足：

$$
Ax\leq b
$$

$$
l\leq x\leq u
$$

如果部分变量必须取整数，则模型进入混合整数规划范畴。

## 二、COPT 支持的问题类型

根据 COPT 8.0 官方手册，主要支持下列模型。

| 类别 | 数学结构 | 官方列出的主要算法 |
|---|---|---|
| LP | 线性目标与线性约束 | 单纯形法、Barrier、PDLP |
| SOCP | 二阶锥约束 | Barrier |
| ExpCone | 指数锥约束 | Barrier |
| 凸 QP | 凸二次目标 | Barrier |
| 凸 QCP | 凸二次约束 | Barrier |
| SDP | 半正定锥约束 | Barrier、ADMM |
| 非凸 QP/QCP | 非凸二次结构 | 空间分支定界或局部 Barrier |
| NLP | 一般非线性结构 | 局部 Barrier |
| MILP | 线性模型加整数变量 | Branch-and-Cut |
| MISOCP | 二阶锥模型加整数变量 | Branch-and-Cut |
| MIQP/MIQCP | 二次模型加整数变量 | Branch-and-Cut |

### 2.1 线性规划

线性规划可写为：

$$
\max c^{T}x
$$

$$
Ax\leq b
$$

$$
x\geq0
$$

常见应用包括配料、运输、生产计划、流量分配和连续资源配置。

### 2.2 混合整数线性规划

MILP 在 LP 基础上增加整数集合：

$$
x_j\in Z,\quad j\in I
$$

二元变量满足：

$$
y_j\in\{0,1\}
$$

它适合表达开关、选择、分配、批量、路径和排程决策。

### 2.3 二次规划与二次约束规划

凸 QP 的目标通常为：

$$
\min \frac{1}{2}x^{T}Qx+c^{T}x
$$

当矩阵 $Q$ 半正定时，目标函数为凸函数。

QCP 还允许二次约束：

$$
x^{T}Q_kx+a_k^{T}x\leq b_k
$$

使用非凸二次模型时，必须区分求解器返回的是全局最优解、局部最优解还是仅有一个可行解。

### 2.4 二阶锥规划

标准二阶锥约束为：

$$
\|x\|_2\leq t
$$

仿射形式为：

$$
\|Fx+g\|_2\leq a^{T}x+b
$$

它可以表达欧氏距离、组合风险、鲁棒半径和平方和约束。加入整数变量后即形成 MISOCP。

### 2.5 半正定规划

半正定规划包含矩阵约束：

$$
X\succeq0
$$

更一般的线性矩阵不等式为：

$$
F_0+\sum_i x_iF_i\succeq0
$$

它常见于控制、矩阵补全、组合优化松弛和多项式优化。

## 三、求解器与建模层的区别

COPT 是求解器，`coptpy` 是其 Python 接口。Pyomo、PuLP、CVXPY 和 AMPL 属于更高层的建模工具。

一个典型调用链为：

1. 用户在建模层定义变量、目标和约束；
2. 建模层把模型转换为 COPT 能接收的结构；
3. COPT 执行预处理和优化算法；
4. 接口返回状态、解、界、gap 和诊断信息。

仅安装 `coptpy` 并不等于已经具备完整求解环境。通常还需要安装匹配版本的 COPT 本体并正确配置许可证。

## 四、安装与许可证

### 4.1 安装 Python 接口

官方推荐通过 pip 安装：

```powershell
pip install coptpy
```

升级接口：

```powershell
pip install --upgrade coptpy
```

官方手册说明，当前 Python 接口支持 Python 3.7 至 3.14；矩阵建模功能建议使用 Python 3.8 或更高版本。矩阵建模还应满足官方文档给出的 NumPy 版本要求。

### 4.2 许可证类型

官方手册列出四类许可证：

- Personal License：绑定个人计算机和用户名；
- Server License：绑定服务器硬件；
- Floating License：通过浮动许可服务分配令牌；
- Cluster License：本地建模，提交到计算集群求解。

许可证是否可用、可用线程数和部署方式应以实际授权文件及合同为准。

### 4.3 最小验证

安装后可先检查导入：

```python
import coptpy as cp
from coptpy import COPT

with cp.Envr() as env:
    with env.createModel("smoke_test") as model:
        x = model.addVar(lb=0.0, ub=1.0, name="x")
        model.setObjective(x, COPT.MAXIMIZE)
        model.solve()
        print(model.status, model.objval)
```

能够导入包并不代表许可证一定有效；应以成功创建环境、完成求解并返回状态为准。

## 五、`coptpy` 的基本对象

Python 建模通常涉及以下对象：

- `Envr`：求解环境；
- `Model`：模型；
- `Var`、`MVar`：标量变量和矩阵变量；
- `Constraint`：线性约束；
- `QConstraint`：二次约束；
- `Cone`：锥约束；
- `PsdVar`、`PsdConstraint`：半正定变量与约束；
- `COPT`：变量类型、方向、状态和参数常量。

推荐使用上下文管理器释放原生资源：

```python
import coptpy as cp

with cp.Envr() as env:
    with env.createModel("demo") as model:
        # Build and solve the model here.
        model.solve()
```

模型应先于环境释放。长时间运行、反复建模或使用回调时，显式管理资源尤其重要。

## 六、完整 LP 示例

考虑模型：

$$
\max 1.2x+1.8y+2.1z
$$

满足：

$$
1.5x+1.2y+1.8z\leq2.6
$$

$$
0.8x+0.6y+0.9z\geq1.2
$$

变量边界为：

$$
0.1\leq x\leq0.6
$$

$$
0.2\leq y\leq1.5
$$

$$
0.3\leq z\leq2.8
$$

对应代码：

```python
import coptpy as cp
from coptpy import COPT

with cp.Envr() as env:
    with env.createModel("lp_example") as model:
        x = model.addVar(lb=0.1, ub=0.6, name="x")
        y = model.addVar(lb=0.2, ub=1.5, name="y")
        z = model.addVar(lb=0.3, ub=2.8, name="z")

        model.addConstr(1.5*x + 1.2*y + 1.8*z <= 2.6)
        model.addConstr(0.8*x + 0.6*y + 0.9*z >= 1.2)

        model.setObjective(
            1.2*x + 1.8*y + 2.1*z,
            sense=COPT.MAXIMIZE,
        )
        model.setParam(COPT.Param.TimeLimit, 10.0)
        model.solve()

        if model.status == COPT.OPTIMAL:
            print("objective =", model.objval)
            print("x, y, z =", x.x, y.x, z.x)

        model.write("lp_example.mps")
        model.write("lp_example.sol")
```

这段代码展示了标准工作流：创建环境、创建模型、添加变量、添加约束、设置目标、设置参数、求解、检查状态和导出结果。

## 七、完整 MILP 示例

设有 $n$ 个候选任务，收益为 $p_i$，资源消耗为 $a_i$，总容量为 $B$。是否选择任务由二元变量 $x_i$ 表示。

目标为：

$$
\max \sum_{i=1}^{n}p_ix_i
$$

容量约束为：

$$
\sum_{i=1}^{n}a_ix_i\leq B
$$

$$
x_i\in\{0,1\}
$$

对应代码：

```python
import coptpy as cp
from coptpy import COPT

profit = [9, 7, 12, 8, 10]
resource = [4, 3, 6, 5, 4]
capacity = 13
n = len(profit)

with cp.Envr() as env:
    with env.createModel("task_selection") as model:
        x = model.addVars(
            range(n),
            vtype=COPT.BINARY,
            nameprefix="select",
        )

        model.addConstr(
            cp.quicksum(resource[i] * x[i] for i in range(n))
            <= capacity
        )

        model.setObjective(
            cp.quicksum(profit[i] * x[i] for i in range(n)),
            COPT.MAXIMIZE,
        )

        model.setParam(COPT.Param.TimeLimit, 30.0)
        model.setParam(COPT.Param.RelGap, 1e-4)
        model.solve()

        if model.status == COPT.OPTIMAL:
            chosen = [i for i in range(n) if x[i].x > 0.5]
            print("objective =", model.objval)
            print("chosen =", chosen)
```

大规模表达式建议使用 `cp.quicksum()`，避免反复使用普通 Python 加法产生大量临时对象。

## 八、SOCP 与 MISOCP 建模

COPT Python API 支持直接添加标准二阶锥和旋转二阶锥。

标准锥：

$$
\sqrt{x_1^2+x_2^2}\leq t
$$

可以把变量按 $[t,x_1,x_2]$ 的顺序加入锥：

```python
import coptpy as cp
from coptpy import COPT

with cp.Envr() as env:
    with env.createModel("socp_example") as model:
        t = model.addVar(lb=0.0, name="t")
        x1 = model.addVar(lb=-COPT.INFINITY, name="x1")
        x2 = model.addVar(lb=-COPT.INFINITY, name="x2")

        model.addConstr(x1 + x2 >= 1.0)
        model.addCone([t, x1, x2], COPT.CONE_QUAD)
        model.setObjective(t, COPT.MINIMIZE)
        model.solve()

        if model.status == COPT.OPTIMAL:
            print(t.x, x1.x, x2.x)
```

旋转锥通常表达：

$$
2uv\geq\sum_i w_i^2
$$

$$
u\geq0,\quad v\geq0
$$

可使用 `COPT.CONE_RQUAD`。如果锥中加入整数或二元变量，或者锥约束与整数选择变量共同存在，模型成为 MISOCP。

## 九、矩阵建模

矩阵接口使用 `MVar` 和 NumPy 风格运算，适合大批量变量与约束。

线性约束可以写为：

$$
Ax\leq b
$$

二次目标可以写为：

$$
x^{T}Qx+c^{T}x
$$

矩阵建模的优势是代码更接近数学形式，但应关注：

- 数组维度和广播规则；
- 稀疏矩阵格式；
- Python 与 NumPy 版本；
- 模型构建阶段的内存占用；
- 输入矩阵是否对称及半正定。

官方常见问题说明，矩阵建模至少需要 Python 3.8 和 NumPy 1.23。

## 十、通过 CVXPY、Pyomo 和 PuLP 调用

### 10.1 CVXPY

CVXPY 1.3 及以上版本可以直接指定 COPT：

```python
import cvxpy as cp

x = cp.Variable(3, nonneg=True)
objective = cp.Minimize(cp.sum(x))
constraints = [x[0] + 2*x[1] + x[2] >= 1]
problem = cp.Problem(objective, constraints)
problem.solve(solver="COPT")
```

官方列出的 CVXPY-COPT 接口覆盖 LP、MIP、QP、SOCP、SDP、MIQP 和 MISOCP。

### 10.2 Pyomo

Pyomo 可以通过 COPT 的 AMPL、Direct 或 Persistent 方式连接。实际接口名称、插件文件位置和兼容版本应以当前安装包文档为准。

### 10.3 PuLP

PuLP 2.8 及以上版本可通过 `COPT()` 调用，其动态库方式依赖正确安装 `coptpy` 和 COPT 本体。

高层建模工具便于迁移求解器，但原生 `coptpy` 往往能更直接地访问回调、参数、锥对象、IIS 和高级属性。

## 十一、算法体系

### 11.1 LP

单纯形法沿多面体顶点移动，适合需要基解、热启动或重复修改模型的场景。Barrier 从可行域内部迭代，适合大型稀疏连续模型。PDLP 属于一阶方法，适合特定大规模线性规划。

### 11.2 MIP

混合整数规划通常采用 Branch-and-Cut。把整数条件暂时放宽后得到连续松弛：

$$
0\leq y_i\leq1
$$

求解器通过分支、割平面、启发式、预处理和节点选择逐步缩小最优性 gap。

对于最小化问题，设当前可行解为 $z_P$，全局下界为 $z_D$，常见相对 gap 可表示为：

$$
g=\frac{|z_P-z_D|}{\max(|z_P|,|z_D|)}
$$

实际停止准则应以 COPT 参数定义和日志显示为准，尤其要处理两侧都接近零的情形。

### 11.3 锥与 SDP

SOCP、指数锥和凸 QCP 主要使用 Barrier。SDP 还可以使用 ADMM。算法选择应根据规模、精度要求、稀疏性和硬件条件决定。

## 十二、常用参数

| 参数 | 作用 |
|---|---|
| `TimeLimit` | 总求解时间限制 |
| `SolTimeLimit` | 找到可行解后的时间限制 |
| `NodeLimit` | MIP 节点数限制 |
| `MemLimit` | 内存限制 |
| `RelGap` | 相对最优性 gap |
| `AbsGap` | 绝对最优性 gap |
| `FeasTol` | 可行性容差 |
| `IntTol` | 整数容差 |
| `Threads` | 线程数量 |
| `Logging` | 是否输出日志 |
| `LogLevel` | 日志详细程度 |

示例：

```python
model.setParam(COPT.Param.TimeLimit, 120.0)
model.setParam(COPT.Param.RelGap, 1e-4)
model.setParam(COPT.Param.Threads, 8)
```

不要在没有基准测试的情况下同时修改大量参数。应固定实例集、随机种子、时间限制和评价指标，然后一次改变少量因素。

## 十三、状态、界与结果解释

调用 `model.solve()` 后，应先检查状态，再读取解。

常见结果语义包括：

- 最优；
- 不可行；
- 无界；
- 不可行或无界；
- 达到时间限制；
- 达到节点或迭代限制；
- 数值困难；
- 被用户中断；
- 非凸问题的局部最优。

达到时间限制不等于没有结果。MIP 可能已经找到可行解，但尚未证明其最优。此时应同时报告：

- 当前目标值；
- 最好对偶界；
- 相对和绝对 gap；
- 求解时间；
- 节点数量；
- 是否存在可行解。

不要只保存目标值而忽略求解状态。

## 十四、不可行性诊断

若模型不可行，可使用 IIS 和可行性松弛。

IIS 是一个不可行子系统：其中约束共同导致不可行，移除其中某些元素后可能恢复可行。它适合定位冲突约束，但不一定对应唯一的业务根因。

可行性松弛通过允许约束或边界发生带代价的偏移，寻找最小修改。例如：

$$
Ax\leq b+s
$$

$$
s\geq0
$$

目标中惩罚松弛：

$$
\min c^{T}x+\lambda\sum_i s_i
$$

惩罚权重必须反映业务严重程度，否则求解器可能放松不应违反的约束。

## 十五、热启动、回调和调参工具

### 15.1 MIP Start

如果已有历史方案、贪心解或上一滚动窗口的解，可以作为 MIP Start 提交。高质量初始解有机会改善上界，但错误或质量过差的初值也可能没有帮助。

### 15.2 回调

回调可用于读取进度、提前中止、添加惰性约束或实现特定分离逻辑。回调会增加生命周期和线程管理复杂度，应避免在回调中执行耗时 I/O。

### 15.3 Tuner

COPT 提供参数调优工具。调参结果应在独立验证实例上复测，避免只对训练实例过拟合。

## 十六、GPU 能力的正确理解

官方 8.0 文档说明：

- GPU 可用于 LP；
- GPU 可用于整数规划的根节点松弛；
- LP 使用 GPU 时需要选择 PDLP 或 Barrier 等兼容方法；
- SOCP、Q(C)P、指数锥和 SDP 可在 Barrier 模式下使用 GPU。

这不等于整个 MIP 搜索树都会在 GPU 上完成。实际收益取决于模型规模、稀疏性、数据传输成本、显卡架构、CUDA 环境和求解算法。

启用 GPU 前应建立 CPU 基线，并比较：

$$
S=\frac{T_{CPU}}{T_{GPU}}
$$

其中 $T_{CPU}$ 和 $T_{GPU}$ 必须来自同一模型、同一容差和同一硬件环境下的可重复测试。

## 十七、建模与性能优化

### 17.1 缩紧变量边界

与其使用宽泛边界：

$$
0\leq x\leq10^9
$$

不如从业务上推导紧边界：

$$
0\leq x\leq U
$$

紧边界能改善预处理、Big-M、连续松弛和数值稳定性。

### 17.2 控制 Big-M

条件约束常写成：

$$
a^{T}x\leq b+M(1-y)
$$

过大的 $M$ 会削弱松弛并带来数值风险。应根据变量边界推导最小有效值，或使用 indicator 和更强的重构。

### 17.3 统一尺度

如果系数从 $10^{-8}$ 跨越到 $10^{10}$，数值条件可能恶化。可通过单位转换和变量缩放，使主要变量与约束处于相近量级。

定义：

$$
x_i=s_i\hat{x}_i
$$

并在变换后重写目标与约束。

### 17.4 批量构建模型

大模型应优先使用 `addVars()`、`addMVar()`、矩阵接口和 `quicksum()`，减少 Python 层循环与临时表达式。

### 17.5 消除对称性

若多个设施或单位完全同质，求解器可能反复搜索等价解。可加入排序或对称破除约束，例如：

$$
y_1\geq y_2\geq\cdots\geq y_n
$$

但必须确认该约束不会删除真正不同的可行方案。

## 十八、工程验证

求解器返回成功并不意味着业务结果一定正确。至少应独立检查以下内容。

### 18.1 线性约束残差

$$
r_i=a_i^{T}x-b_i
$$

对于小于等于约束，应满足：

$$
r_i\leq\varepsilon
$$

### 18.2 整数性

$$
|x_j-n_j|\leq\varepsilon,\quad n_j\in Z
$$

### 18.3 锥约束

$$
\|F_kx+g_k\|_2-a_k^{T}x-b_k\leq\varepsilon
$$

同时检查锥右端没有违反非负条件。

### 18.4 目标重算

使用原始输入数据重新计算：

$$
z=c^{T}x
$$

不要只信任导出的显示值或经过四舍五入的变量。

### 18.5 回归测试

固定小规模实例，并验证：

- 已知最优值；
- 可行性与整数性；
- 不可行实例状态；
- 时间限制下是否正确处理 incumbent；
- 模型导入导出前后目标是否一致。

## 十九、COPT 与 OR-Tools、Gurobi、CPLEX 的关系

COPT、Gurobi 和 CPLEX 都属于通用数学规划求解器，覆盖 LP、MIP、二次或锥类模型，但具体算法、接口、许可证、部署和性能不同。

OR-Tools 更像一个优化工具箱，包含 CP-SAT、路由和图算法，也可连接部分外部求解器。若问题以布尔逻辑、排程和整数约束为主，CP-SAT 可能很合适；若模型包含连续变量、对偶信息、锥约束或高精度数值结构，数学规划求解器通常更自然。

求解器选择不应只看单个公开榜单。建议使用自己的代表性实例比较：

- 达到同一 gap 所需时间；
- 固定时间内的可行解质量；
- 峰值内存；
- 模型构建时间；
- 许可证与部署成本；
- API 和诊断能力；
- 结果可重复性。

## 二十、在游戏 AI 与运筹系统中的用途

### 20.1 任务选择

二元变量表示是否执行任务：

$$
y_i\in\{0,1\}
$$

在资源和时间限制下最大化综合收益。

### 20.2 编队与单位分配

变量 $x_{ij}$ 表示单位 $i$ 是否分配给小队 $j$：

$$
\sum_j x_{ij}=1
$$

可加入角色、距离、战力、协同和容量约束。

### 20.3 路径与网络流

流守恒可写为：

$$
\sum_{j}x_{ij}-\sum_{j}x_{ji}=b_i
$$

适合战略层运输、补给和任务网络。高频局部避障仍应交给专门的路径规划与运动控制算法。

### 20.4 鲁棒资源配置

椭球不确定性可导出二阶锥：

$$
\bar a^{T}x+\rho\|F^{T}x\|_2\leq b
$$

加入离散选择后可以使用 MISOCP 表达风险受控的任务规划。

## 二十一、常见错误

1. 只安装 `coptpy`，没有安装或配置 COPT 本体和许可证；
2. 忘记检查求解状态，直接读取目标值；
3. 把达到时间限制误写成已证明最优；
4. 使用过大的 Big-M；
5. 默认变量下界为零，却实际需要负数；
6. 对非凸模型把局部最优误认为全局最优；
7. 在代码中逐项普通求和，导致建模阶段缓慢；
8. 只调线程数，不先改善边界和模型结构；
9. 只看求解日志，不独立验证约束残差；
10. 升级 COPT 本体后忘记同步接口和许可证要求。

## 二十二、结论

COPT 是覆盖连续、整数、二次、锥、半正定和部分非线性模型的通用数学规划求解器。它的 Python 接口与主流数学建模 API 相似，同时提供矩阵建模、IIS、可行性松弛、回调、调参、GPU 和集群部署能力。

可靠使用 COPT 的关键不是只会调用 `solve()`，而是：

1. 选择与业务结构一致的模型类别；
2. 正确安装本体、接口和许可证；
3. 检查状态、可行解、界和 gap；
4. 缩紧边界，控制尺度和 Big-M；
5. 独立重算约束与目标；
6. 使用代表性实例进行基准测试。

## 参考资料

- [COPT 8.0 User Guide：Introduction and Supported Problems](https://guide.coap.online/copt/en-doc/intro.html)
- [COPT 8.0 User Guide：Python Interface](https://guide.coap.online/copt/en-doc/pythoninterface.html)
- [COPT 8.0 User Guide：Python API Reference](https://guide.coap.online/copt/en-doc/pyapiref.html)
- [COPT 8.0 User Guide：Parameters](https://guide.coap.online/copt/en-doc/parameter.html)
- [COPT 8.0 User Guide：Modeling and Solving Optimization Problems](https://guide.coap.online/copt/en-doc/modeling.html)
- [COPT 8.0 User Guide：CVXPY Interface](https://guide.coap.online/copt/en-doc/cvxpyinterface.html)
- [COPT 8.0 User Guide：FAQ](https://guide.coap.online/copt/en-doc/faq.html)
