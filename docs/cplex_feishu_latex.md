# CPLEX：从数学规划到工业级优化应用

## 摘要

IBM ILOG CPLEX Optimization Studio 是面向运筹优化建模、求解和部署的工具体系。它通常用于生产计划、供应链、运输、排程、能源、金融、资源配置和组合决策等问题。

日常语境中的“CPLEX”可能指三个不同层次：

- CPLEX Optimizer：求解 LP、MIP、QP 和相关数学规划模型；
- CP Optimizer：面向约束满足与复杂排程的约束规划引擎；
- Optimization Studio：包含 OPL、IDE、两个求解引擎和开发接口的完整产品。

本文介绍 CPLEX 的数学基础、产品结构、算法体系、DOcplex 建模、求解状态、最优性证明、不可行诊断、性能调优及工程接入边界。公式采用飞书稳定支持的 LaTeX 子集。

---

## 一、CPLEX 解决什么问题

优化问题的基本目标是在可行域中寻找最优决策：

$$
\min_{x \in X} f(x)
$$

其中 $x$ 是决策变量，$X$ 是满足全部约束的可行域，$f(x)$ 是成本、时间、风险或负收益。

典型应用包括：

- 决定工厂生产多少产品以及如何分配原料；
- 把订单、机器、人员和班次组合成可执行计划；
- 在仓库、车辆和路线之间分配配送任务；
- 选择投资组合并控制预算与风险；
- 优化电力系统、通信网络和供应网络；
- 在大量离散方案中选择满足规则的最优组合。

CPLEX 的优势不在于理解业务语义，而在于高效求解已经被准确表达为变量、约束和目标的模型。

## 二、CPLEX Optimization Studio 的组成

### 2.1 CPLEX Optimizer

CPLEX Optimizer 是数学规划引擎，主要处理：

- 线性规划 LP；
- 混合整数线性规划 MILP；
- 二次规划 QP；
- 混合整数二次规划 MIQP；
- 二次约束规划 QCP；
- 混合整数二次约束规划 MIQCP。

它包含单纯形法、Barrier 内点法、分支定界、分支切割、预处理、启发式搜索和并行搜索等能力。

### 2.2 CP Optimizer

CP Optimizer 是独立的约束规划引擎，适合：

- 作业车间排程；
- 可选任务；
- 资源互斥；
- 累积资源容量；
- 复杂日历；
- 任务先后和时间关系；
- 逻辑结构密集的组合问题。

它通过约束传播缩减变量域，再通过搜索寻找可行解或最优解。CP Optimizer 与 CPLEX Optimizer 是互补关系，不应把两者当成同一个求解算法。

### 2.3 OPL 与 IDE

OPL 是 IBM 的优化建模语言。模型、数据和求解设置可以分离：

- `.mod` 文件描述变量、约束和目标；
- `.dat` 文件保存问题实例数据；
- `.ops` 文件保存求解参数；
- Run Configuration 组合一次具体运行。

IDE 支持执行模型、查看表格结果、分析运行时间、调整参数、查找约束冲突和调试脚本。

### 2.4 Python 接口

Python 中有两类常见接口：

- `cplex`：较低层的 CPLEX Python API，接近底层矩阵和求解器功能；
- `docplex.mp`：面向数学规划的对象化建模接口；
- `docplex.cp`：面向 CP Optimizer 的建模接口。

DOcplex 负责构建模型。仅安装 `docplex` 并不等于已经具备本地 CPLEX 求解能力，本地求解还需要兼容的 CPLEX 运行时与有效授权。

## 三、线性规划 LP

线性规划的标准形式可写为：

$$
\min c^{T}x
$$

满足：

$$
Ax \leq b
$$

$$
l \leq x \leq u
$$

若变量可以连续取值，问题就是 LP。可行域由线性不等式构成，是一个凸多面体；线性目标的最优解若存在，至少有一个最优解位于可行域的极点或最优面上。

### 3.1 原始问题与对偶问题

考虑原始问题：

$$
\min c^{T}x
$$

$$
Ax \geq b
$$

$$
x \geq 0
$$

对应的一种对偶形式是：

$$
\max b^{T}y
$$

$$
A^{T}y \leq c
$$

$$
y \geq 0
$$

对偶变量可以解释资源约束的边际价值。若强对偶条件成立，原始最优值与对偶最优值相等。

### 3.2 LP 算法

CPLEX Optimizer 支持的主要 LP 算法包括：

- Primal Simplex：沿可行域顶点迭代；
- Dual Simplex：在对偶侧保持可行并恢复原始可行性；
- Barrier：从可行域内部逼近最优解；
- Network 方法：利用网络结构处理特定模型。

算法选择应根据模型结构、热启动需求、数值条件和重复求解方式决定。默认自动选择通常是可靠起点。

## 四、混合整数规划 MIP

若部分变量必须取整数值，模型成为混合整数规划：

$$
\min c^{T}x
$$

$$
Ax \leq b
$$

$$
x_j \in Z, \quad j \in I
$$

其中 $I$ 是整数变量下标集合。二元变量满足：

$$
x_j \in \{0,1\}
$$

它可以表示是否建设工厂、是否选择订单、是否启用路线或某个逻辑条件是否成立。

### 4.1 LP 松弛

暂时去掉整数约束可得到 LP 松弛。对于最小化问题，LP 松弛最优值是整数问题的下界：

$$
z_{LP} \leq z_{MIP}
$$

界越紧，证明最优所需的搜索通常越少。

### 4.2 分支定界

若 LP 松弛解中的整数变量出现分数值，例如：

$$
x_k = 2.4
$$

可以分成两个子问题：

$$
x_k \leq 2
$$

以及：

$$
x_k \geq 3
$$

CPLEX 在搜索树中维护：

- incumbent：当前最好的整数可行解；
- best bound：尚未排除节点能达到的最好理论界；
- MIP gap：当前解与理论界之间的差距。

### 4.3 分支切割

CPLEX 会加入对所有整数可行解都成立、但能排除部分分数解的有效不等式：

$$
\alpha^{T}x \leq \beta
$$

这些切割平面可以收紧 LP 松弛，减少分支搜索。切割并非越多越好，过多无效切割也会增加节点 LP 的规模。

## 五、二次模型

凸二次规划可以写为：

$$
\min \frac{1}{2}x^{T}Qx + c^{T}x
$$

满足线性约束：

$$
Ax \leq b
$$

当 $Q$ 为半正定矩阵时，目标是凸的。二次项适合表示平方偏差、波动、平滑成本和风险。

二次约束示例：

$$
x^{T}Qx \leq r
$$

如果再加入整数变量，就形成 MIQP 或 MIQCP。此类模型通常比纯 LP 或 MILP 更难，应先确认二次项确实必要，并检查凸性与数值尺度。

## 六、常见建模模式

### 6.1 指派

设 $x_{ij}=1$ 表示资源 $i$ 分配给任务 $j$，成本为 $c_{ij}$：

$$
\min \sum_i \sum_j c_{ij}x_{ij}
$$

每个任务恰好分配一次：

$$
\sum_i x_{ij}=1
$$

每个资源最多承担一个任务：

$$
\sum_j x_{ij}\leq1
$$

### 6.2 设施选址

设 $y_j=1$ 表示开启设施 $j$，$x_{ij}=1$ 表示客户 $i$ 由设施 $j$ 服务：

$$
x_{ij} \leq y_j
$$

容量约束为：

$$
\sum_i d_i x_{ij} \leq C_j y_j
$$

目标可以同时考虑固定成本和运输成本：

$$
\min \sum_j f_j y_j + \sum_i \sum_j c_{ij}x_{ij}
$$

### 6.3 软约束

若需求允许少量缺口，可以加入松弛变量 $s_i$：

$$
\sum_j a_{ij}x_j + s_i \geq d_i
$$

$$
s_i \geq 0
$$

再在目标中加入惩罚：

$$
\min c^{T}x + M\sum_i s_i
$$

惩罚系数 $M$ 应反映真实业务代价，不应只为了“让约束看起来更硬”而随意设成极大值。

### 6.4 条件约束

如果方案 A 被选中，就必须启用资源 B，可写为：

$$
x_A \leq x_B
$$

更复杂的条件关系可以使用 indicator constraint。相比手写 Big-M，它通常具有更清晰的语义，也便于求解器利用结构。

## 七、使用 DOcplex 建立第一个模型

DOcplex 建模层可以通过 Python 包管理器安装：

```powershell
python -m pip install docplex
```

下面解决一个简单的生产计划。产品 A 和 B 的单位收益分别为 30 和 20；两类资源容量分别为 40 和 36。

```python
from docplex.mp.model import Model

model = Model(name="production_plan")

x_a = model.integer_var(lb=0, name="product_a")
x_b = model.integer_var(lb=0, name="product_b")

model.add_constraint(2 * x_a + x_b <= 40, "resource_1")
model.add_constraint(x_a + 2 * x_b <= 36, "resource_2")
model.maximize(30 * x_a + 20 * x_b)

solution = model.solve(log_output=True)

if solution is None:
    print("No solution available")
else:
    print("objective =", solution.objective_value)
    print("product_a =", solution[x_a])
    print("product_b =", solution[x_b])
```

代码中的 `docplex.mp` 负责建模，实际求解需要本机或目标环境存在可用的 CPLEX 引擎。生产部署前应核对 IBM 当前版本的系统要求、Python 兼容性和授权条件。

## 八、OPL 模型示例

同一生产计划可以用 OPL 表示：

```opl
dvar int+ productA;
dvar int+ productB;

maximize 30 * productA + 20 * productB;

subject to {
  resource1: 2 * productA + productB <= 40;
  resource2: productA + 2 * productB <= 36;
}
```

OPL 的优势是模型接近数学表达，数据可以与模型分离，适合优化专家快速原型、实验与业务规则审查。应用服务则常使用 Python、Java、C++ 或 .NET API 集成。

## 九、理解求解结果

对于 MIP，必须同时关注可行解与最优性证明。若当前可行解目标值为 $z_P$，理论界为 $z_D$，可定义相对差距：

$$
g = \frac{|z_P-z_D|}{\max(1,|z_P|)}
$$

常见结果含义包括：

- optimal：已找到并证明全局最优解；
- feasible：有可行解，但未完成最优性证明；
- infeasible：证明不存在满足全部约束的解；
- unbounded：目标可以无限改善；
- infeasible or unbounded：预处理后暂时无法区分两种情形；
- stopped：因时间、节点、内存或用户条件停止。

上线系统应记录：

- 求解状态；
- 可行解目标值；
- 最优界；
- 相对与绝对 gap；
- 运行时间和节点数；
- 停止原因；
- 参数、线程数和随机种子；
- 模型版本与输入数据版本。

## 十、不可行诊断

模型不可行通常意味着约束或数据之间存在冲突。CPLEX 的 Conflict Refiner 可以从约束和变量边界中提取一个相互矛盾的子集，帮助定位原因。

需要注意：

- 一个模型可能有多个独立冲突；
- 修复一个冲突后，可能暴露下一个冲突；
- 最小冲突表示删除其中任意一个成员可破坏该冲突，但不保证整个模型立即可行；
- 冲突偏好可以引导诊断方向，但不保证找到用户主观上最想要的冲突。

实用排查顺序是：

1. 检查单位、索引、上下界和数据缺失；
2. 暂时移除目标，只做可行性检查；
3. 按业务模块分组启用约束；
4. 将可放宽规则改成带代价的软约束；
5. 运行 Conflict Refiner；
6. 将冲突映射回业务规则，而不是只报告内部行号。

## 十一、性能调优

### 11.1 先改模型，再改参数

求解慢时应先检查：

- 变量上下界是否过宽；
- Big-M 是否远大于必要值；
- 是否存在重复或弱约束；
- 是否存在大量对称解；
- 数据尺度是否相差过大；
- 是否能加入有效不等式；
- 是否能分解成主问题与子问题。

参数调优无法挽救结构错误的模型。

### 11.2 Big-M 的风险

典型约束为：

$$
a^{T}x \leq b + M(1-y)
$$

$M$ 必须足以关闭约束，但过大会导致松弛弱化和数值不稳定。应尽量从变量上下界推导最小有效 $M$，或使用 indicator constraint。

### 11.3 缩紧边界

若变量满足更紧的业务范围：

$$
l'_i \leq x_i \leq u'_i
$$

且：

$$
l_i \leq l'_i \leq u'_i \leq u_i
$$

就应使用紧边界。它能改善预处理、松弛质量和分支效率。

### 11.4 热启动

重复求解相似实例时，可以向 MIP 提供已有可行解。高质量 MIP start 有助于提前获得 incumbent，但无效或严重不一致的初始解也可能被拒绝。CPLEX 还可以对被拒绝的 MIP start 做冲突分析。

### 11.5 时间与 gap

真实系统常在有限时间内运行。应同时设置时间预算和可接受 gap。例如，当相对差距低于业务阈值时停止，而不是一味追求数学上的零 gap。

## 十二、CPLEX Optimizer 与 CP Optimizer 如何选择

| 问题特征 | 优先方向 |
|---|---|
| 线性成本与线性资源约束 | CPLEX Optimizer |
| 需要 LP 对偶、影子价格或松弛分析 | CPLEX Optimizer |
| 复杂固定成本、选址、投资组合 | CPLEX Optimizer |
| 时间区间、可选任务、资源日历 | CP Optimizer |
| 大量任务先后、互斥与排程关系 | CP Optimizer |
| 同时含总体规划和详细排程 | 分层或混合架构 |

数学规划擅长全局资源权衡、线性结构和界证明；约束规划擅长离散时间关系与强传播。遇到规划加排程问题，可以让 CPLEX Optimizer 决定产量、设施或批次，再由 CP Optimizer 生成详细日程。

## 十三、与 OR-Tools 的区别

二者都能处理整数优化和约束问题，但定位不同：

- CPLEX Optimization Studio 是商业优化产品体系，包含成熟的数学规划引擎、CP Optimizer、OPL、IDE 与企业开发接口；
- OR-Tools 是 Google 开源组合优化工具集，CP-SAT、Routing 和图算法是其主要特色；
- CPLEX Optimizer 在 LP、MIP、QP、QCP、对偶分析、灵敏度和数学规划工作流方面更完整；
- OR-Tools 的 CP-SAT 对纯整数、逻辑密集模型很有竞争力，并且易于开源项目集成；
- 具体性能取决于模型结构与数据，不能只根据产品名称判断。

可靠的选型方法是建立代表性基准实例，统一时间预算、线程数、停止条件和验证器，再比较可行率、目标值、最优界、稳定性与部署成本。

## 十四、在战棋与游戏 AI 中的用途

### 14.1 多单位联合行动

设 $x_{ua}=1$ 表示单位 $u$ 选择动作 $a$。每个单位选择一个动作：

$$
\sum_a x_{ua}=1
$$

同一目标格 $g$ 最多容纳一个单位：

$$
\sum_u \sum_{a \in A(u,g)}x_{ua}\leq1
$$

目标可以组合伤害、存活、补给和阵型收益：

$$
\max \sum_u \sum_a v_{ua}x_{ua}
$$

CPLEX 负责联合选择，原生规则引擎仍应独立验证动作合法性。

### 14.2 生产与资源规划

兵种训练、装备制造、补给运输和任务组合可以建模为 MILP。若进一步涉及精确开始时间、资源日历和不可中断任务，可由 CP Optimizer 处理详细排程。

### 14.3 不适合直接处理的层次

CPLEX 不替代实时碰撞、连续物理控制、动画状态机或高频局部避障。常见工程分层是：

- 优化器决定任务、目标和资源分配；
- 路径规划器生成时空路径；
- 行为树或控制器执行；
- 规则引擎验证状态变化；
- 环境改变后滚动重求解。

## 十五、上线前检查清单

### 模型正确性

- 变量、单位、索引和上下界是否明确；
- 硬约束与软约束是否区分；
- 目标函数是否反映真实业务偏好；
- 是否存在过大的 Big-M；
- 是否使用独立验证器复核解。

### 求解可靠性

- 是否设置时间、节点和内存边界；
- 是否记录 incumbent、best bound 和 gap；
- 是否区分可行与已证明最优；
- 不可行时是否运行冲突诊断；
- 是否保存参数和求解日志。

### 部署与治理

- 是否核对目标平台、API 和 Python 版本兼容性；
- 是否确认开发、测试与生产环境的授权条件；
- 是否对历史实例做回放；
- 是否与人工规则或旧方案做基线比较；
- 是否监控求解时间、可行率、目标质量和失败降级。

## 十六、结论

CPLEX 的核心能力可以概括为：用成熟的数学规划算法和约束规划技术，把复杂决策问题变成可求解、可证明、可诊断的模型。

正确使用 CPLEX 需要分清三个层次：

1. 业务问题是否被正确抽象；
2. CPLEX Optimizer、CP Optimizer 或分层架构是否选对；
3. 求解结果是否经过独立验证并满足部署约束。

模型决定求解器在解决什么问题，算法决定如何搜索，最优界说明结论有多强，验证器决定结果能否真正进入生产系统。

## 参考资料

- [IBM ILOG CPLEX Optimization Studio 产品介绍](https://www.ibm.com/products/ilog-cplex-optimization-studio)
- [Discovering CPLEX Optimization Studio](https://www.ibm.com/docs/en/icos/22.1.2?topic=guide-discovering-cplex-optimization-studio)
- [CPLEX Python API](https://www.ibm.com/docs/en/icos/22.1.2?topic=SSSA5P_22.1.2/ilog.odms.cplex.help/refpythoncplex/html/help.htm)
- [Setting up the Python API of CPLEX](https://www.ibm.com/docs/en/icos/22.1.1?topic=cplex-setting-up-python-api)
- [CP Optimizer Overview](https://www.ibm.com/docs/en/icos/22.1.2?topic=cpco-overview)
- [How to invoke the Conflict Refiner](https://www.ibm.com/docs/en/icos/22.1.1?topic=conflicts-how-invoke-conflict-refiner)
