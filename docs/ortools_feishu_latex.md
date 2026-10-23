# OR-Tools：从数学建模到组合优化工程

## 摘要

OR-Tools 是 Google 开源的组合优化工具集，适合处理排程、指派、车辆路径、装箱、网络流、线性规划和整数规划等问题。它的核心价值不是提供一个“万能算法”，而是把业务问题转换为变量、约束与目标，并为不同结构选择合适的求解器。

本文系统介绍 OR-Tools 的求解器体系、数学模型、CP-SAT 建模方法、Python 使用流程、性能调优、结果解释及常见误区。文中的公式采用飞书可渲染的 LaTeX 子集。

---

## 一、OR-Tools 解决什么问题

组合优化的基本形式是：在满足约束的可行解集合中，找到目标值最优的解。

$$
\min_{x \in X} f(x)
$$

其中，$x$ 是待决定的变量，$X$ 是可行解集合，$f(x)$ 是成本、时间、距离、风险或其他目标。

典型问题包括：

- 把员工分配到班次，同时满足技能、休息和覆盖需求；
- 把任务安排到机器，同时满足工序先后和资源互斥；
- 为车辆规划路线，同时满足容量与时间窗；
- 把物品装入有限数量的箱子；
- 在网络中计算最大流、最小费用流或匹配；
- 在资源限制下选择收益最大的项目组合。

OR-Tools 使用 C++ 实现核心能力，并提供 Python、Java、C# 和 C++ 接口。

## 二、求解器体系

OR-Tools 不是单一求解器，而是一组针对不同问题结构的接口和算法。

### 2.1 CP-SAT

CP-SAT 是 OR-Tools 的主要整数约束求解器。它结合约束传播、SAT 搜索、整数规划切割、冲突学习和启发式搜索，适合整数变量、逻辑条件、互斥关系、先后顺序、可选任务和离散资源。

CP-SAT 只接受整数变量和整数系数。含小数的模型需要先进行可靠的整数缩放。

### 2.2 MPSolver

MPSolver 是线性规划和混合整数规划的统一接口。线性规划的标准形式可写为：

$$
\min c^{T}x
$$

约束为：

$$
Ax \leq b
$$

$$
l \leq x \leq u
$$

若所有变量都可连续取值，就是 LP；若部分变量必须为整数，就是 MIP。OR-Tools 自带 GLOP 线性规划求解器，也可以通过相应构建方式连接其他受支持的求解器。纯整数且逻辑约束较多时，通常优先考虑 CP-SAT。

### 2.3 Routing Solver

Routing Solver 面向旅行商问题和车辆路径问题，支持多车路径、车辆容量、访问时间窗、取货与送货、可放弃节点以及车辆资源限制。

它通常返回高质量可行解，但大规模车辆路径问题未必能在给定时间内证明全局最优。

### 2.4 图算法

OR-Tools 还提供最大流、最小费用流和线性和指派等专用算法。当问题严格符合专用结构时，专用算法通常比通用 MIP 或 CP-SAT 更快。

## 三、如何选择求解器

| 问题特征 | 优先选择 |
|---|---|
| 连续变量、线性目标、线性约束 | GLOP 或其他 LP 求解器 |
| 整数变量、线性模型 | CP-SAT 或 MIP |
| 大量条件、互斥、排程约束 | CP-SAT |
| 车辆、站点、容量、时间窗 | Routing Solver |
| 纯最大流或最小费用流 | 图算法 |
| 简单一对一指派 | Linear Sum Assignment |
| 复杂指派并带额外业务约束 | CP-SAT 或 MIP |

选择原则是：先识别问题结构，再选择求解器，不要因为熟悉某个 API 就把所有问题都强行写成同一种模型。

## 四、CP-SAT 的数学建模

### 4.1 决策变量

布尔变量：

$$
x_i \in \{0,1\}
$$

它可以表示是否选择项目、是否分配任务、是否使用路线或某个条件是否成立。

整数变量：

$$
l_i \leq x_i \leq u_i
$$

它可以表示开始时间、人员数量、库存、位置编号或离散资源用量。

### 4.2 常见线性约束

容量约束：

$$
\sum_i a_i x_i \leq C
$$

覆盖约束：

$$
\sum_i x_i \geq d
$$

恰好选择一个：

$$
\sum_i x_i = 1
$$

### 4.3 指派模型

设 $x_{ij}=1$ 表示工人 $i$ 被分配到任务 $j$，成本为 $c_{ij}$。目标为：

$$
\min \sum_i \sum_j c_{ij}x_{ij}
$$

每个工人最多承担一个任务：

$$
\sum_j x_{ij} \leq 1
$$

每个任务恰好由一个工人完成：

$$
\sum_i x_{ij} = 1
$$

### 4.4 条件约束

如果选择方案 A，就必须启用资源 B。设 $x_A$ 和 $x_B$ 为布尔变量，则可写为：

$$
x_A \leq x_B
$$

OR-Tools 也支持只在某个布尔条件成立时启用约束。条件约束比随意使用很大的 Big-M 更清晰，也通常更利于传播。

### 4.5 排程模型

任务 $i$ 的开始时间、持续时间和结束时间满足：

$$
s_i + p_i = e_i
$$

同一机器上的任务 $i$ 与 $j$ 不能重叠，因此至少满足一个顺序：

$$
e_i \leq s_j
$$

或：

$$
e_j \leq s_i
$$

在 CP-SAT 中，IntervalVar、NoOverlap 和 Cumulative 等原生约束比手写成对 Big-M 约束更适合排程。

工期目标通常是最小化最大完工时间：

$$
\min C_{max}
$$

且：

$$
C_{max} \geq e_i
$$

## 五、安装与第一个 Python 模型

官方推荐在虚拟环境中安装 Python 包：

```powershell
python -m pip install ortools
```

下面用 CP-SAT 解决一个简单的资源选择问题。三个项目的成本分别为 4、3、2，收益分别为 9、6、4，总预算不超过 6，目标是最大化总收益。

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

x0 = model.new_bool_var("project_0")
x1 = model.new_bool_var("project_1")
x2 = model.new_bool_var("project_2")

model.add(4 * x0 + 3 * x1 + 2 * x2 <= 6)
model.maximize(9 * x0 + 6 * x1 + 4 * x2)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10.0
status = solver.solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("objective =", solver.objective_value)
    print("selected =", [
        solver.value(x0),
        solver.value(x1),
        solver.value(x2),
    ])
else:
    print("No feasible solution found.")
```

标准流程是：创建模型、创建变量、添加约束、设置目标、设置资源边界、求解并根据状态读取结果。

## 六、理解求解状态

CP-SAT 常见状态包括：

- `OPTIMAL`：找到可行解，并证明不存在更优解；
- `FEASIBLE`：找到可行解，但尚未证明最优；
- `INFEASIBLE`：证明模型无可行解；
- `MODEL_INVALID`：模型定义无效；
- `UNKNOWN`：在得到确定结论前停止。

必须区分“找到一个好解”和“证明这是最优解”。

对于最小化问题，若当前可行解目标值为 $z$，有效下界为 $b$，可定义相对差距：

$$
g = \frac{z-b}{\max(1,|z|)}
$$

工程系统应同时记录状态、目标值、最优界、运行时间和停止原因，而不是只保存最终变量。

## 七、Routing Solver 的核心结构

设 $x_{ijk}=1$ 表示车辆 $k$ 从节点 $i$ 行驶到节点 $j$，距离或成本为 $d_{ij}$。基本目标是：

$$
\min \sum_k \sum_i \sum_j d_{ij}x_{ijk}
$$

每个客户通常要求被访问一次：

$$
\sum_k \sum_j x_{ijk} = 1
$$

车辆容量约束为：

$$
\sum_i q_i y_{ik} \leq Q_k
$$

时间窗约束为：

$$
a_i \leq t_i \leq b_i
$$

Routing API 使用 Dimension 表示沿路径累积的量，例如时间、距离、载重和能量。常见搜索配置包括第一解策略、Guided Local Search、Tabu Search、Simulated Annealing，以及时间和解数量限制。

## 八、模型质量比参数调优更重要

### 8.1 缩紧变量边界

如果任务最早开始时间和最晚结束时间已知，应直接使用紧边界：

$$
r_i \leq s_i \leq d_i-p_i
$$

边界越紧，传播与搜索通常越有效。

### 8.2 避免不必要的 Big-M

典型 Big-M 约束为：

$$
a^{T}x \leq b + M(1-y)
$$

过大的 $M$ 会削弱线性松弛并引入数值问题。CP-SAT 中应优先考虑条件约束和原生全局约束。

### 8.3 消除对称性

多个完全相同的机器、车辆或班次会产生等价解。可加入稳定排序或固定一个代表变量，减少重复搜索。

### 8.4 使用原生约束

排程优先使用 NoOverlap、Cumulative 和可选 IntervalVar；一对一关系可使用 AllDifferent；乘积、最大值和绝对值尽量使用相应建模接口。

### 8.5 设置求解边界

生产系统应设置最大求解时间、可接受最优差距、随机种子、并行工作数和解回调，并把这些参数写入实验与回放记录。

## 九、CP-SAT 的整数缩放

CP-SAT 只处理整数。若金额精确到分，可以把元缩放为分：

$$
12.35 \rightarrow 1235
$$

一般形式为：

$$
\hat{x} = \operatorname{round}(sx)
$$

其中 $s$ 是缩放因子。缩放时必须明确原始精度、四舍五入规则、最大系数和可能的溢出风险。不要为了保留无意义的小数位而使用过大的缩放因子。

## 十、不可行模型如何排查

`INFEASIBLE` 通常意味着业务规则之间存在冲突。推荐方法是：

1. 验证数据范围和单位；
2. 暂时去掉目标，仅检查可行性；
3. 按约束组逐步启用；
4. 为软约束增加松弛变量；
5. 检查恰好一次、最多一次和至少一次是否写反；
6. 检查时间单位、容量单位和整数缩放；
7. 使用假设变量与不可满足核心定位冲突规则。

例如把需求约束改为：

$$
\sum_i x_i + s \geq d
$$

其中 $s \geq 0$ 是缺口变量，再最小化：

$$
\min Ms
$$

就可以把“完全无解”转化为“最少需要放宽多少”。

## 十一、在战棋与游戏 AI 中的用途

### 11.1 多单位联合行动

设 $x_{ua}=1$ 表示单位 $u$ 选择动作 $a$。每个单位恰好选择一个动作：

$$
\sum_a x_{ua}=1
$$

多个单位不能占据同一目标格 $g$：

$$
\sum_u \sum_{a \in A(u,g)} x_{ua} \leq 1
$$

目标可以组合伤害、风险、阵型和补给：

$$
\max \sum_u \sum_a v_{ua}x_{ua}
$$

OR-Tools 负责联合选择，底层规则引擎仍应负责验证动作合法性和执行结果。

### 11.2 编队、生产与任务排程

单位到阵型槽位的分配，本质上是带兵种、距离、互斥和领导覆盖约束的指派问题。游戏中的建造、训练、技能冷却、运输和工序链也可以使用 IntervalVar 与资源约束表示。

### 11.3 路径规划的边界

OR-Tools 可以优化任务与路线，但不是所有实时移动问题的替代品。高频连续避障、物理控制和单个单位的局部移动通常更适合 A*、RRT、MPC 或专门的 MAPF 算法。

常见架构是：OR-Tools 决定谁执行什么任务、去哪个目标；路径规划器生成合法路径；规则引擎执行；状态变化后滚动重求解。

## 十二、OR-Tools 不是什么

OR-Tools 不是：

- 自动理解自然语言业务规则的系统；
- 保证所有大规模困难问题都能迅速得到最优解的工具；
- 连续非线性优化器；
- 自动修复错误模型的数据清洗工具；
- 物理仿真器或实时控制器；
- 用一个求解器覆盖所有问题结构的平台。

求解器只能严格执行已经表达出来的模型。错误的变量、遗漏的约束或失真的目标，会得到数学上正确但业务上错误的答案。

## 十三、上线前检查清单

### 模型

- 变量含义、单位和上下界是否明确；
- 硬约束与软约束是否区分；
- 目标函数是否真实反映业务优先级；
- 是否存在对称变量或冗余约束；
- CP-SAT 的全部系数是否为整数。

### 求解

- 是否设置时间和内存边界；
- 是否区分 `FEASIBLE` 与 `OPTIMAL`；
- 是否记录目标界与最优差距；
- 无解时是否有诊断与降级策略；
- 是否保存求解器参数和随机种子。

### 验证

- 是否用独立规则检查器复核解；
- 是否覆盖边界数据和不可行数据；
- 是否对历史实例做回放；
- 是否与贪心、人工规则或旧系统比较；
- 是否监控求解时间、可行率与目标质量。

## 十四、结论

OR-Tools 最适合规则能够明确表达、选择是离散的、约束彼此交织、候选组合又多到无法穷举的问题。

正确的使用方式包括四步：

1. 把业务对象定义为变量；
2. 把不可违反的规则定义为约束；
3. 把偏好与代价定义为目标；
4. 根据结构选择 CP-SAT、LP/MIP、Routing 或图算法。

模型决定问题是否正确，求解器决定如何搜索，独立验证决定结果能否进入生产系统。三者缺一不可。

## 参考资料

- [OR-Tools 官方首页](https://developers.google.com/optimization)
- [OR-Tools 简介](https://developers.google.com/optimization/introduction)
- [安装 OR-Tools](https://developers.google.com/optimization/install)
- [CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver)
- [MPSolver Interface](https://developers.google.com/optimization/lp/mpsolver)
- [Vehicle Routing](https://developers.google.com/optimization/routing)
- [Scheduling Overview](https://developers.google.com/optimization/scheduling)
- [Network Flows](https://developers.google.com/optimization/flow)
