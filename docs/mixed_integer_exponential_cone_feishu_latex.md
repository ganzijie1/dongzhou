# 混合整数指数锥规划：理论、建模与求解实践

## 摘要

混合整数指数锥规划把整数决策、线性约束和指数锥约束放在同一个优化模型中。它能够精确表达指数函数、对数函数、相对熵、熵、log-sum-exp、softplus，以及带离散选择的几何规划结构。

这类模型常被简称为 MIECP，也可归入混合整数锥优化或 MICO。不同软件的术语并不完全统一，因此工程上应检查求解器是否真正支持“整数变量与指数锥同时存在”，不能仅凭其支持连续指数锥就作出推断。

本文介绍指数锥定义、常见函数的锥化、规范形式、分支定界、外逼近、Perspective 强化、Big-M、稀疏逻辑回归、支持集受限熵优化、KL 散度、MOSEK Fusion 与 CVXPY 示例、数值稳定性和结果验证。公式采用飞书稳定支持的 LaTeX 子集。

---

## 一、为什么需要指数锥

线性规划只能直接表达线性关系，二阶锥适合欧氏范数和平方和，而指数锥负责一类包含指数、对数与熵的凸关系。

例如，指数函数的上图集合为：

$$
t\geq e^x
$$

对数函数的下图集合为：

$$
t\leq\log x
$$

相对熵为：

$$
D(x,y)=x\log\frac{x}{y}
$$

这些关系不是一般的线性约束或二阶锥约束，但可以使用三维指数锥精确表示。

## 二、指数锥的定义

令三维向量为 $(u,v,w)$。原始指数锥可定义为：

$$
K_{\exp}=\{(u,v,w):u\geq ve^{w/v},\ v>0\}
$$

并加入闭包边界：

$$
\{(u,0,w):u\geq0,\ w\leq0\}
$$

因此，当 $v>0$ 时，锥成员关系：

$$
(u,v,w)\in K_{\exp}
$$

等价于：

$$
u\geq ve^{w/v}
$$

指数锥是凸锥。连续指数锥规划可以使用内点法求解；加入整数变量后，整体可行域不再凸，但固定整数变量后的连续子问题仍可保持凸性。

## 三、基本函数的指数锥表达

### 3.1 指数函数

约束：

$$
t\geq e^x
$$

等价于：

$$
(t,1,x)\in K_{\exp}
$$

### 3.2 对数函数

约束：

$$
t\leq\log x
$$

等价于：

$$
(x,1,t)\in K_{\exp}
$$

该形式自动要求 $x$ 位于对数的有效定义域。

### 3.3 熵

熵项为：

$$
H(x)=-x\log x
$$

其下图可以表示为：

$$
t\leq-x\log x
$$

$$
(1,x,t)\in K_{\exp}
$$

闭包使 $x=0$ 时的极限值能够得到一致处理。

### 3.4 相对熵

相对熵上界：

$$
t\geq x\log\frac{x}{y}
$$

可写为：

$$
(y,x,-t)\in K_{\exp}
$$

当 $x$ 和 $y$ 表示概率质量时，这一结构可用于 KL 散度、分布鲁棒优化和信息投影。

## 四、log-sum-exp 与 softplus

### 4.1 log-sum-exp

设：

$$
t\geq\log\left(\sum_{i=1}^{n}e^{x_i}\right)
$$

等价于：

$$
\sum_{i=1}^{n}u_i\leq1
$$

以及：

$$
(u_i,1,x_i-t)\in K_{\exp},\quad i=1,\ldots,n
$$

这一表示避免直接计算可能溢出的巨大指数值。

### 4.2 softplus

softplus 函数为：

$$
f(x)=\log(1+e^x)
$$

其上界：

$$
t\geq\log(1+e^x)
$$

可以使用两个辅助变量：

$$
u+v\leq1
$$

$$
(u,1,x-t)\in K_{\exp}
$$

$$
(v,1,-t)\in K_{\exp}
$$

softplus 是逻辑回归损失和某些平滑风险函数的核心构件。

## 五、MIECP 的规范形式

一个混合整数指数锥模型可以写为：

$$
\min c^{T}x
$$

满足线性关系：

$$
Ax=b
$$

若干指数锥关系：

$$
(a_k^{T}x+\alpha_k,b_k^{T}x+\beta_k,d_k^{T}x+\delta_k)\in K_{\exp}
$$

以及整数条件：

$$
x_j\in Z,\quad j\in I
$$

二元变量满足：

$$
x_j\in\{0,1\}
$$

其中仿射表达式进入指数锥，目标函数保持线性。非线性关系已经被封装在锥域中。

## 六、与其他模型的区别

| 模型 | 非线性结构 | 整数变量 |
|---|---|---|
| MILP | 无，或已线性化 | 有 |
| MISOCP | 二阶锥、范数、平方和 | 有 |
| MIQP/MIQCP | 二次目标或二次约束 | 有 |
| MIECP | 指数锥、对数、熵、相对熵 | 有 |
| MINLP | 一般非线性结构 | 有 |

MIECP 是结构化的混合整数凸优化。它比一般 MINLP 更明确地暴露凸性，但通常比 MILP 和 MISOCP 更难求解。

指数锥通常不能精确替换为有限个二阶锥。若使用分段线性近似，应明确它是近似模型，并验证误差方向和误差上界。

## 七、连续松弛与分支定界

把二元变量放宽为：

$$
0\leq y_i\leq1
$$

得到连续指数锥松弛。对于最小化问题：

$$
z_{relax}\leq z_{integer}
$$

求解器通常执行以下流程：

1. 求解连续指数锥松弛；
2. 选择非整数变量分支；
3. 在子节点重新求解连续锥问题；
4. 使用可行解更新上界；
5. 使用松弛值更新下界；
6. 按不可行性或界进行剪枝。

最小化问题的相对 gap 常写为：

$$
g=\frac{|z_P-z_D|}{\max(1,|z_P|)}
$$

其中 $z_P$ 是当前整数可行解，$z_D$ 是全局下界。具体定义与停止条件应以所用求解器文档为准。

## 八、外逼近

指数函数：

$$
f(x)=e^x
$$

在点 $\bar x$ 的一阶支撑线为：

$$
e^x\geq e^{\bar x}+e^{\bar x}(x-\bar x)
$$

因此，若要求：

$$
t\geq e^x
$$

可以加入线性有效不等式：

$$
t\geq e^{\bar x}+e^{\bar x}(x-\bar x)
$$

外逼近算法在发现违反点后添加新的支撑平面。有限个切平面只构成松弛，不等于完整指数锥。

当指数变量缺少有效上下界时，外逼近可能需要大量切割。应先缩紧定义域，再比较原生锥算法和外逼近方法。

## 九、Perspective 强化

设二元变量 $y$ 表示某项功能是否启用，连续变量 $x$ 表示启用后的强度，$z$ 表示指数成本。

Perspective 形式为：

$$
z\geq ye^{x/y}
$$

它可以直接写成：

$$
(z,y,x)\in K_{\exp}
$$

并加入联动边界：

$$
Ly\leq x\leq Uy
$$

当 $y=1$ 时：

$$
z\geq e^x
$$

当 $y=0$ 时，闭包与联动边界允许关闭该项并令 $x=0$。在满足相应建模条件时，这种形式通常比宽松 Big-M 提供更强的连续松弛。

## 十、Big-M 条件指数约束

若只在 $y=1$ 时要求：

$$
t\geq e^x
$$

一种条件表达为：

$$
t\geq e^x-M(1-y)
$$

必须根据 $x$ 与 $t$ 的有效边界推导 $M$。如果：

$$
L\leq x\leq U
$$

则 $e^x$ 的范围跨越：

$$
e^L\leq e^x\leq e^U
$$

即使 $U$ 只增加少量，所需 $M$ 也可能快速增大。没有紧边界时，Big-M 会造成弱松弛和严重数值问题。

优先顺序通常是：原生 Perspective、原生 indicator 与锥结构、推导出的紧 Big-M，最后才是经验性大常数。

## 十一、带固定费用的指数资源模型

设 $y_i$ 表示是否启用资源 $i$，$x_i$ 是投入强度，$z_i$ 是指数成本，固定费用为 $f_i$。

目标：

$$
\min\sum_i f_iy_i+\sum_i z_i
$$

联动边界：

$$
0\leq x_i\leq U_iy_i
$$

Perspective 指数成本：

$$
(z_i,y_i,x_i)\in K_{\exp}
$$

整数条件：

$$
y_i\in\{0,1\}
$$

该模型可表示启用设备、服务器、生产线或策略后的非线性能耗和拥塞成本。

## 十二、支持集受限的最大熵模型

设 $p_i$ 是概率，$y_i$ 表示第 $i$ 个状态是否允许出现在支持集中，最多选择 $K$ 个状态。

概率约束：

$$
\sum_i p_i=1
$$

支持集联动：

$$
0\leq p_i\leq y_i
$$

$$
\sum_i y_i\leq K
$$

熵辅助变量满足：

$$
(1,p_i,t_i)\in K_{\exp}
$$

目标为：

$$
\max\sum_i t_i
$$

这在选择有限情景、压缩离散分布和构造受限随机策略时有用。

## 十三、KL 散度与离散选择

设 $p$ 是待优化分布，$q$ 是参考分布。KL 散度为：

$$
D(p,q)=\sum_i p_i\log\frac{p_i}{q_i}
$$

引入 $d_i$：

$$
(q_i,p_i,-d_i)\in K_{\exp}
$$

散度半径约束为：

$$
\sum_i d_i\leq\rho
$$

若只允许选择部分情景：

$$
p_i\leq U_iy_i
$$

$$
y_i\in\{0,1\}
$$

就得到带支持选择的混合整数相对熵模型。参考概率 $q_i$ 若为零，需要单独处理定义域，不能直接代入对数比值。

## 十四、稀疏逻辑回归

给定样本特征 $a_i$ 和标签 $s_i\in\{-1,1\}$，线性打分为：

$$
r_i=a_i^{T}\beta+\beta_0
$$

逻辑损失为：

$$
\ell_i=\log(1+e^{-s_ir_i})
$$

使用 softplus 的两个指数锥可表达其上界。

令 $y_j$ 表示特征 $j$ 是否被选中：

$$
-M_jy_j\leq\beta_j\leq M_jy_j
$$

限制特征数：

$$
\sum_j y_j\leq K
$$

目标可以写为：

$$
\min\sum_i\ell_i+\lambda\sum_j y_j
$$

这比先训练连续模型再截断系数更直接地控制支持集，但计算难度显著增加。$M_j$ 必须通过数据缩放、正则化和系数边界推导。

## 十五、离散几何规划

几何规划中的单项式为：

$$
g(x)=c\prod_{i=1}^{n}x_i^{a_i}
$$

令：

$$
y_i=\log x_i
$$

则：

$$
\log g(x)=\log c+\sum_i a_iy_i
$$

多个单项式之和经过对数变换后形成 log-sum-exp 约束，因此可用指数锥表示。

当设备型号、拓扑、公式项或设计模块由整数变量选择时，就形成离散几何规划或混合整数指数锥模型。变量必须满足正值域，原变量与对数变量之间的解释也应保持一致。

## 十六、MOSEK Fusion 示例

下面的示例来自 MOSEK 官方混合整数锥教程的结构。模型为：

$$
\min t
$$

$$
t\geq\sqrt{x^2+y^2}
$$

$$
x\geq e^y+3.8
$$

$$
x,y\in Z
$$

对应 Fusion 代码：

```python
import sys
from mosek.fusion import Model, Domain, Expr, ObjectiveSense
import mosek.fusion.pythonic

with Model("mixed_integer_exp_cone") as model:
    x = model.variable("x", Domain.integral(Domain.unbounded()))
    y = model.variable("y", Domain.integral(Domain.unbounded()))
    t = model.variable("t")

    model.constraint(
        Expr.vstack(t, x, y),
        Domain.inQCone(),
    )

    model.constraint(
        Expr.vstack(x - 3.8, 1.0, y),
        Domain.inPExpCone(),
    )

    model.objective(ObjectiveSense.Minimize, t)
    model.setSolverParam("mioMaxTime", 60.0)
    model.setSolverParam("mioTolRelGap", 1e-4)
    model.setLogHandler(sys.stdout)
    model.solve()

    print("x =", x.level()[0])
    print("y =", y.level()[0])
    print("t =", t.level()[0])
```

生产代码还应检查求解状态和可行解状态，再读取 `level()`。达到时间限制时不能直接声称已证明最优。

## 十七、CVXPY 示例

CVXPY 可以把符合 DCP 规则的指数表达式规范化为指数锥。需要选择同时支持指数锥和整数变量的后端求解器。

```python
import cvxpy as cp

x = cp.Variable(integer=True, name="x")
y = cp.Variable(integer=True, name="y")
t = cp.Variable(name="t")

constraints = [
    cp.norm(cp.hstack([x, y]), 2) <= t,
    cp.exp(y) + 3.8 <= x,
]

problem = cp.Problem(cp.Minimize(t), constraints)
problem.solve(
    solver=cp.MOSEK,
    mosek_params={"MSK_DPAR_MIO_MAX_TIME": 60.0},
)

print("status =", problem.status)
print("objective =", problem.value)
print("x, y =", x.value, y.value)
```

如果后端只支持连续指数锥或只支持 MILP，该模型不会因为 CVXPY 能解析表达式就自动变得可解。

## 十八、求解器支持范围

判断求解器是否适用时，应分别核对：

1. 是否支持原始或对偶指数锥；
2. 是否支持整数变量；
3. 是否允许二者出现在同一模型；
4. 是否提供全局界和 MIP gap；
5. 是否支持所需 API 与授权方式。

MOSEK 官方 Fusion 文档明确给出了整数变量与指数锥同时存在的 MICO 示例。

COPT 8.0 官方概览明确列出连续指数锥规划，也列出多类混合整数模型，但没有在该概览表中单独列出 MIECP。使用前应根据当前版本 API、支持矩阵和厂商说明进一步确认，不能把连续 ExpCone 支持自动外推为混合整数 ExpCone 支持。

其他求解器可能通过一般凸非线性、外逼近或分段线性化处理类似模型，但算法语义和全局保证可能不同。

## 十九、数值稳定性

### 19.1 指数增长

指数函数增长极快：

$$
e^{30}\approx10^{13}
$$

指数自变量出现较大的正负范围时，微小扰动也会引起巨大绝对变化。应尽量通过变量中心化、单位转换和边界缩紧控制范围。

### 19.2 对数定义域

使用：

$$
t\leq\log x
$$

时必须保证 $x$ 的定义域。若业务要求严格正值，可设置有数据依据的下界：

$$
x\geq\varepsilon
$$

不要随意选择极小的 $\varepsilon$，因为它会影响数值尺度和业务语义。

### 19.3 概率零值

熵中的 $0\log0$ 可通过闭包按极限处理，但相对熵中参考概率为零时需要特殊规则。不能简单把零替换为任意小数而不做敏感性分析。

### 19.4 尺度统一

定义缩放变量：

$$
x_i=s_i\hat{x}_i
$$

使主要变量和仿射表达式保持合理量级。目标系数、固定费用和指数成本也应避免跨越过多数量级。

## 二十、性能改进顺序

求解困难时建议按以下顺序处理：

1. 检查每个指数锥的坐标顺序；
2. 检查对数、熵和相对熵的定义域；
3. 缩紧整数变量和指数自变量边界；
4. 使用 Perspective 替代弱 Big-M；
5. 从数据推导最小有效 Big-M；
6. 添加对称破除和有效不等式；
7. 提供高质量整数初始解；
8. 为重复结构批量生成锥约束；
9. 设置业务可接受的时间和 gap；
10. 在代表性实例集上比较原生锥与外逼近。

模型结构通常比单纯增加线程和时间更重要。

## 二十一、结果验证

### 21.1 线性约束

独立重算：

$$
Ax-b
$$

并按约束方向检查残差。

### 21.2 整数变量

对整数变量检查：

$$
|x_j-n_j|\leq\varepsilon,\quad n_j\in Z
$$

### 21.3 指数锥

当 $v>\varepsilon$ 时，检查：

$$
u-ve^{w/v}\geq-\varepsilon
$$

当 $|v|\leq\varepsilon$ 时，检查闭包边界：

$$
u\geq-\varepsilon
$$

$$
w\leq\varepsilon
$$

### 21.4 业务指标

至少报告：

- 当前整数可行解目标值；
- 全局界与 gap；
- 时间和节点数；
- 最大线性残差；
- 最大指数锥残差；
- 定义域最小余量；
- 与基线或近似模型的差异。

整数问题最终解通常不能像纯连续凸问题那样直接解释为具有完整全局对偶乘子。需要对固定整数方案的连续子问题另行分析。

## 二十二、在游戏 AI 与工程系统中的用途

### 22.1 风险敏感规划

指数效用或指数风险可以放大尾部损失。整数变量负责选择任务、路线或单位，指数锥负责精确表达非线性风险。

### 22.2 稀疏策略选择

熵用于控制策略分布的随机性，整数变量限制可用动作数量，可以得到支持集受限的随机策略。

### 22.3 服务器与能耗调度

服务器是否启动由二元变量决定，负载与温度或能耗之间的指数关系由 Perspective 指数锥表达。

### 22.4 通信与容量设计

无线网络中的功率、容量、误码率或可靠性模型常含指数和对数。设备选择、频段分配与拓扑决策引入整数变量。

### 22.5 工程边界

MIECP 适合低频规划、设计和资源配置，不适合直接承担每帧物理控制。若实时预算严格，可以离线求解策略模板，在线使用近似模型、查表或滚动优化。

## 二十三、何时不应使用 MIECP

以下情况可能有更简单的模型：

- 只有线性关系：使用 MILP；
- 只有范数和平方和：使用 MISOCP；
- 没有整数变量：使用连续指数锥规划；
- 指数关系只需粗略近似：考虑有误差保证的分段线性模型；
- 非线性不满足凸性：考虑全局 MINLP 或重新建模；
- 高频在线决策：考虑预计算和近似策略。

不能仅因为公式中出现指数就使用指数锥。关键是约束方向必须形成凸上图或凹下图等可锥化结构。

## 二十四、结论

混合整数指数锥规划把离散选择与指数、对数和熵结构统一起来。它特别适合固定启用成本、支持集选择、稀疏统计模型、相对熵约束、几何设计和风险敏感规划。

可靠建模需要做到：

1. 统一指数锥坐标顺序；
2. 正确处理闭包和定义域；
3. 优先使用 Perspective 强化；
4. 对 Big-M 提供边界依据；
5. 核实求解器对整数加指数锥的联合支持；
6. 同时报告可行解、全局界和 gap；
7. 独立验证指数锥残差和业务指标。

## 参考资料

- [MOSEK Modeling Cookbook：Exponential Cone Optimization](https://docs.mosek.com/modeling-cookbook/expo.html)
- [MOSEK Modeling Cookbook：Mixed Integer Optimization](https://docs.mosek.com/modeling-cookbook/mio.html)
- [MOSEK Modeling Cookbook：Practical Optimization](https://docs.mosek.com/modeling-cookbook/practical.html)
- [MOSEK Fusion API：Integer Optimization](https://docs.mosek.com/latest/pythonfusion/tutorial-mio-shared.html)
- [MOSEK Fusion API：Conic Modeling](https://docs.mosek.com/latest/pythonfusion/modeling.html)
- [MOSEK Fusion API：Supported Domains](https://docs.mosek.com/latest/pythonfusion/list-of-domains.html)
- [COPT 8.0 User Guide：Supported Problem Types](https://guide.coap.online/copt/en-doc/intro.html)
