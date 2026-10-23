# Gurobi：从数学模型到高性能优化求解

## 摘要

Gurobi Optimizer 是商业数学优化求解器，用于求解线性规划、混合整数规划、二次规划、二次约束规划以及相应的混合整数模型。当前官方文档还覆盖非凸二次与非线性模型、多目标、Solution Pool、场景分析、不可行诊断和分布式部署等能力。

Gurobi 采用“建模—求解—查询”工作流：开发者先把业务问题表达为变量、约束和目标，再调用求解器，最后读取可行解、最优界、对偶信息和诊断结果。

本文介绍 Gurobi 的模型类型、核心算法、Python API、最优性证明、IIS 与可行性松弛、数值稳定性、性能调优以及工程应用边界。公式采用飞书稳定支持的 LaTeX 子集。

---

## 一、Gurobi 解决什么问题

优化问题的基本形式是：

$$
\min_{x \in X} f(x)
$$

其中 $x$ 是决策变量，$X$ 是满足约束的可行域，$f(x)$ 是成本、风险、时间或负收益。

典型应用包括：

- 生产计划与供应链配置；
- 车辆、仓库和订单分配；
- 航班、员工、机器和能源排程；
- 设施选址与网络设计；
- 投资组合与风险控制；
- 广告、定价和资源预算；
- 大规模组合选择与任务指派。

Gurobi 不负责理解自然语言业务规则。它负责高效求解已经被准确表达为数学模型的问题。

## 二、支持的主要模型

### 2.1 线性规划 LP

线性规划可以写为：

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

变量可以连续取值。Gurobi 可使用单纯形法、Barrier 方法和并发优化方法求解 LP。

### 2.2 混合整数线性规划 MILP

若部分变量必须取整数值，则形成 MILP：

$$
\min c^{T}x
$$

$$
Ax \leq b
$$

$$
x_j \in Z, \quad j \in I
$$

二元变量满足：

$$
x_j \in \{0,1\}
$$

它可以表示是否选择项目、是否启用设施、是否分配任务或某项逻辑条件是否成立。

### 2.3 二次规划 QP

二次目标模型可写为：

$$
\min \frac{1}{2}x^{T}Qx+c^{T}x
$$

满足线性约束：

$$
Ax \leq b
$$

若 $Q$ 为半正定矩阵，则最小化目标是凸的。二次项适合表示平方偏差、平滑成本、波动和风险。

### 2.4 二次约束规划 QCP

二次约束示例为：

$$
x^{T}Qx+a^{T}x \leq r
$$

二阶锥约束可以表示为：

$$
x_1^2+x_2^2 \leq t^2
$$

当模型含整数变量时，会形成 MIQP 或 MIQCP。

### 2.5 非凸二次与非线性模型

Gurobi 可以处理一定范围的非凸二次模型和非线性表达式。非凸模型通常比凸模型困难得多，需要空间分支、松弛和界估计。

如果一个理论上应当凸的模型被识别为非凸，应先检查数据、符号和矩阵，而不是直接接受更昂贵的非凸求解流程。

## 三、Python API：gurobipy

Gurobi 的 Python 包是 `gurobipy`。核心对象包括：

- `Env`：授权、日志和运行环境；
- `Model`：优化模型；
- `Var` 与 `MVar`：标量和矩阵变量；
- `Constr` 与 `QConstr`：线性与二次约束；
- `LinExpr` 与 `QuadExpr`：线性与二次表达式；
- `tupledict`：按业务索引管理变量；
- attributes：读取状态、解、界和统计信息；
- parameters：控制算法、停止条件和搜索策略。

Gurobi 还提供 C、C++、Java、.NET、MATLAB 和 R 等接口。不同语言接口共享大部分参数、属性和状态码。

## 四、第一个 gurobipy 模型

下面建立一个整数生产计划。产品 A 和 B 的单位收益分别为 30 和 20，两类资源容量分别为 40 和 36。

```python
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("production_plan")

x_a = model.addVar(vtype=GRB.INTEGER, lb=0, name="product_a")
x_b = model.addVar(vtype=GRB.INTEGER, lb=0, name="product_b")

model.addConstr(2 * x_a + x_b <= 40, name="resource_1")
model.addConstr(x_a + 2 * x_b <= 36, name="resource_2")
model.setObjective(30 * x_a + 20 * x_b, GRB.MAXIMIZE)

model.Params.TimeLimit = 10
model.optimize()

if model.SolCount > 0:
    print("objective =", model.ObjVal)
    print("product_a =", x_a.X)
    print("product_b =", x_b.X)
else:
    print("No feasible solution available")
```

运行前需要安装与目标平台兼容的 Gurobi 软件和 Python 包，并配置有效授权。具体安装方式、平台支持和授权类型应以当前官方文档为准。

## 五、常见建模模式

### 5.1 指派问题

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

Python 中可以使用 `addVars` 创建索引变量，并用 `quicksum` 构造大规模求和表达式。

### 5.2 设施选址

设 $y_j=1$ 表示开启设施 $j$，$x_{ij}=1$ 表示客户 $i$ 由设施 $j$ 服务：

$$
x_{ij} \leq y_j
$$

设施容量约束为：

$$
\sum_i d_i x_{ij} \leq C_j y_j
$$

目标为固定成本与服务成本之和：

$$
\min \sum_j f_jy_j+\sum_i\sum_j c_{ij}x_{ij}
$$

### 5.3 条件约束

如果选择方案 A，就必须启用资源 B：

$$
x_A \leq x_B
$$

更复杂的逻辑可以使用 indicator constraint。与手写 Big-M 相比，它的语义更明确，也允许求解器使用模型结构。

### 5.4 分段线性成本

分段线性函数可以描述阶梯价格、加班成本、库存罚金和服务水平。若成本在断点 $q_k$ 上取值 $v_k$，求解器可以使用分段线性目标或约束表达。

### 5.5 一般约束

Gurobi API 提供最大值、最小值、绝对值、逻辑关系和其他一般约束。原生一般约束通常比自行展开成大量辅助变量和 Big-M 更易读。

## 六、LP 的原始与对偶

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

对偶变量可以解释资源约束的边际价值。在线性模型中，Gurobi 可以提供对偶值、约束松弛量、约化成本和基状态等信息。

这些信息依赖模型类型和算法状态。整数模型的离散决策通常不能直接沿用 LP 影子价格解释。

## 七、MIP 如何证明最优

### 7.1 LP 松弛

去掉整数条件后得到 LP 松弛。对于最小化问题：

$$
z_{LP} \leq z_{MIP}
$$

LP 松弛提供理论下界。高质量模型应尽量让这个下界靠近真正整数最优值。

### 7.2 分支定界

若松弛解中整数变量出现：

$$
x_k=2.4
$$

可以分成两个分支：

$$
x_k\leq2
$$

以及：

$$
x_k\geq3
$$

搜索过程中有两个关键量：

- incumbent：当前最好的整数可行解；
- best bound：所有尚未排除节点所能达到的最好理论界。

对于最小化问题，可定义相对 MIP gap：

$$
g=\frac{|z_P-z_D|}{\max(1,|z_P|)}
$$

其中 $z_P$ 是当前可行解目标值，$z_D$ 是理论界。当 gap 达到设定阈值时，可以在没有零 gap 证明的情况下停止。

### 7.3 切割与启发式

切割平面是所有整数可行解都满足、但能排除部分分数解的不等式：

$$
\alpha^{T}x\leq\beta
$$

启发式则尝试从松弛解、节点信息和已有解中快速构造新的整数可行解。切割改善 best bound，启发式改善 incumbent，两者共同缩小 gap。

## 八、理解状态、属性与停止原因

常见结果包括：

- `OPTIMAL`：已找到并证明最优解；
- `INFEASIBLE`：模型被证明不可行；
- `UNBOUNDED`：目标可以无限改善；
- `INF_OR_UNBD`：当前预处理结果无法区分不可行与无界；
- `TIME_LIMIT`：达到时间限制；
- `NODE_LIMIT`：达到节点限制；
- `SOLUTION_LIMIT`：达到解数量限制；
- `INTERRUPTED`：被用户或外部过程终止。

即使状态不是 `OPTIMAL`，模型也可能已有可用解。读取 `ObjVal` 或变量的 `X` 属性前，应先确认 `SolCount > 0`。

生产系统至少应记录：

- Status；
- SolCount；
- ObjVal；
- ObjBound；
- MIPGap；
- Runtime；
- NodeCount；
- 参数和模型版本。

## 九、Solution Pool 与多目标

### 9.1 Solution Pool

离散模型可能有多个质量相近但业务含义不同的方案。Solution Pool 可以保存多组可行解，并允许按池中的解编号读取变量值。

它适合：

- 给计划员提供多个备选计划；
- 比较近优解的结构稳定性；
- 检查多个等价最优解；
- 在后处理阶段加入难以直接建模的偏好。

Solution Pool 中存在多个解，不代表已经枚举所有可行解；具体含义取决于 PoolSearchMode、PoolSolutions 和 PoolGap 等参数。

### 9.2 多目标

多目标模型可以按优先级分层，也可以在同层使用权重。词典序思想是：先优化高优先级目标，再在允许的退化范围内优化次级目标。

例如先最小化未满足需求：

$$
f_1(x)=\sum_i s_i
$$

再最小化总成本：

$$
f_2(x)=c^{T}x
$$

这通常比随意把两个目标乘上巨大权重后相加更容易解释。

## 十、不可行诊断：IIS

如果模型不可行，Gurobi 可以计算 IIS，即不可约不一致子系统。IIS 是一组相互矛盾的约束和变量边界；移除其中任意一个成员，就会破坏这一组特定冲突的不可约性。

Python 示例：

```python
model.optimize()

if model.Status == GRB.INFEASIBLE:
    model.computeIIS()
    model.write("model_iis.ilp")
```

需要注意：

- 一个模型可能存在多个 IIS；
- 一个 IIS 不一定覆盖所有不可行原因；
- 修复一个 IIS 后可能出现另一个冲突；
- MIP 的 IIS 计算可能较昂贵；
- 应给约束稳定命名，才能把诊断结果映射回业务规则。

## 十一、可行性松弛 FeasRelax

如果模型无解，但某些规则允许有代价地放宽，可以引入松弛变量。原约束：

$$
a_i^{T}x \leq b_i
$$

放宽后：

$$
a_i^{T}x \leq b_i+s_i
$$

$$
s_i \geq 0
$$

再最小化加权违反量：

$$
\min \sum_i p_i s_i
$$

FeasRelax 可以构造相应的放宽模型，并按设置最小化违反数量、违反总量或平方违反量。

惩罚 $p_i$ 必须表达真实业务代价。没有业务依据的统一惩罚，可能给出数学上最小但业务上不可接受的修复方案。

## 十二、数值稳定性

优化模型使用有限精度浮点数。以下问题会损害稳定性：

- 系数尺度相差过大；
- 变量边界极宽；
- Big-M 远大于必要值；
- 数据含不必要的小数精度；
- 约束近似线性相关；
- 单位混用，例如元与万元、秒与小时混在同一模型。

### 12.1 Big-M

典型 Big-M 约束是：

$$
a^{T}x \leq b+M(1-y)
$$

$M$ 必须足够大以关闭约束，但越大越会削弱松弛并放大数值风险。应利用变量上下界推导最小有效 $M$，或改用 indicator constraint。

### 12.2 尺度检查

如果最小非零系数约为 $10^{-6}$，最大系数约为 $10^9$，模型跨越了过多数量级。更好的做法是重新选择单位、缩放数据，并检查这些极端值是否源于录入错误。

Gurobi 提供最大最小系数、边界和右端项等模型属性，也提供基矩阵条件数相关属性用于诊断部分连续模型。

## 十三、性能调优

### 13.1 先改模型

求解慢时首先检查：

- 是否能缩紧变量上下界；
- 是否存在过大的 Big-M；
- 是否存在对称解；
- 是否遗漏有效不等式；
- 是否有重复、弱或无效约束；
- 能否按时间、场景或网络结构分解；
- 是否真的需要每一个整数变量。

### 13.2 关键 MIP 参数

- `TimeLimit`：最大求解时间；
- `MIPGap`：相对最优差距阈值；
- `MIPGapAbs`：绝对最优差距阈值；
- `Threads`：并行线程数；
- `MIPFocus`：平衡可行解搜索、最优性证明和界改善；
- `Heuristics`：启发式投入；
- `Cuts`：切割总体强度；
- `Seed`：部分随机选择的种子。

默认参数通常是可靠起点。应在有代表性的实例集上调参，而不是只优化一个样例。

### 13.3 自动调参

Gurobi 提供 Parameter Tuning Tool，可在一组模型和给定时间预算上搜索参数组合。调参结果仍需在独立测试集上验证，避免只对训练实例有效。

### 13.4 热启动

MIP start 可以提供已知可行解。重复求解相似模型时，Gurobi 也可能复用已有 basis、incumbent 或其他可用信息，前提是模型修改没有使这些信息失效。

## 十四、回调与滚动优化

回调可以在求解过程中读取进度、记录 incumbent、实现特定终止条件，或在允许的位置添加 lazy constraint 和 user cut。

回调中的逻辑必须轻量、确定且线程安全。错误的 lazy constraint 会改变可行域，可能使最终答案错误，因此必须由独立规则验证。

滚动优化通常按以下流程运行：

1. 使用当前状态建立模型；
2. 在固定时间预算内求解；
3. 执行决策的一部分；
4. 接收新订单、状态或预测；
5. 修改模型并再次求解。

这种方式适合动态排程、库存补货、车队调度和游戏回合决策。

## 十五、与 CPLEX 和 OR-Tools 的区别

| 工具 | 主要定位 |
|---|---|
| Gurobi | 商业数学优化求解器，突出 LP/MIP/QP/QCP、非凸与非线性、API 和高性能求解 |
| CPLEX Optimization Studio | 商业优化产品体系，包含 CPLEX Optimizer、CP Optimizer、OPL 和 IDE |
| OR-Tools | 开源组合优化工具集，包含 CP-SAT、Routing 和图算法 |

Gurobi 与 CPLEX 在数学规划领域有大量重叠；CPLEX 还提供独立 CP Optimizer 与 OPL 工作流。OR-Tools 的 CP-SAT 对整数和逻辑密集模型很有竞争力，并便于开源项目使用。

不能脱离模型结构宣布某个求解器永远更快。可靠选型应使用代表性实例，统一时间、线程、gap 和验证规则，再比较可行率、目标值、最优界、稳定性、接口与部署成本。

## 十六、在战棋与游戏 AI 中的用途

### 16.1 多单位联合行动

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

Gurobi 负责联合选择，原生规则引擎仍应独立验证动作合法性。

### 16.2 资源与任务规划

兵种训练、装备制造、补给运输、编队槽位和任务组合都可以建模为 MIP。Solution Pool 可以生成多个质量接近的备选方案，再由上层策略或玩家偏好选择。

### 16.3 工程边界

Gurobi 不替代实时碰撞、连续物理控制、动画状态机和高频局部避障。常见分层是：

- 优化器选择任务、资源与目标；
- 路径规划器生成合法路径；
- 行为树或控制器执行；
- 规则引擎验证结果；
- 状态改变后滚动重求解。

## 十七、上线前检查清单

### 模型

- 变量、索引、单位和上下界是否明确；
- 硬约束与软约束是否区分；
- 目标函数是否反映真实业务优先级；
- 是否存在过大的 Big-M 或尺度问题；
- 是否有独立解验证器。

### 求解

- 是否设置时间、节点和内存边界；
- 是否记录 ObjVal、ObjBound 与 MIPGap；
- 是否检查 SolCount 后再读取解；
- 不可行时是否使用 IIS 或 FeasRelax；
- 是否保留日志、参数与模型文件。

### 部署

- 是否核对当前版本的平台与 API 兼容性；
- 是否确认开发、测试和生产授权；
- 是否在历史与极端实例上回放；
- 是否设计无解、超时和引擎不可用时的降级策略；
- 是否监控求解时间、可行率、gap 和目标质量。

## 十八、结论

Gurobi 的核心价值，是把大规模数学规划模型转化为可求解、可证明和可诊断的决策过程。

正确使用它需要分清四件事：

1. 业务问题是否被准确建模；
2. 模型是否具有足够强的边界和松弛；
3. 求解状态、可行解和最优界是否被正确解释；
4. 结果是否经过独立验证并满足部署要求。

求解器性能不能弥补错误模型，零 gap 也不能证明业务定义正确。模型、算法、诊断和验证必须共同构成完整的优化工程。

## 参考资料

- [Gurobi Optimizer 官方产品页](https://www.gurobi.com/product)
- [Gurobi Optimizer Reference Manual](https://docs.gurobi.com/projects/optimizer/en/current/)
- [Objectives](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/objectives.html)
- [Python Model Class](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html)
- [Infeasibility Analysis](https://docs.gurobi.com/projects/optimizer/en/current/features/infeasibility.html)
- [Parameter Guidelines](https://docs.gurobi.com/projects/optimizer/en/current/concepts/parameters/guidelines.html)
- [Gurobi Example Tour](https://docs.gurobi.com/projects/examples/en/current/)
