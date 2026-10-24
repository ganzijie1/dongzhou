# 图模型与分布式优化：Sum-product、Max-product、Loopy BP、Junction Tree、Max-Sum/DCOP 与 ADMM

## 摘要

许多多智能体决策问题都可以写成“局部因子之和或乘积构成全局目标”。概率图模型关心边缘概率、条件概率和最大后验解释；分布式约束优化关心多个智能体如何只交换局部消息，求得高质量联合动作；ADMM 则通过交替局部优化与共识更新，处理可分解的连续凸优化问题。

本文统一介绍 Sum-product、Max-product、Loopy Belief Propagation、Junction Tree、Max-Sum 与 DCOP、ADMM 分布式优化。重点讨论消息方程、精确性条件、复杂度、收敛诊断、工程接口，以及它们在 5v5、战棋和战略游戏中的应用边界。

## 一、统一的因子图表示

设变量集合为 $x=(x_1,\ldots,x_n)$，因子图由变量节点和因子节点组成。一个未归一化的概率模型写成：

$$\widetilde p(x)=\prod_{a\in\mathcal F}\psi_a(x_a)$$

其中 $x_a$ 是因子 $a$ 涉及的变量子集，$\psi_a(x_a)\ge 0$ 是局部势函数。归一化分布为：

$$p(x)=\frac{1}{Z}\prod_{a\in\mathcal F}\psi_a(x_a)$$

配分函数为：

$$Z=\sum_x\prod_{a\in\mathcal F}\psi_a(x_a)$$

若使用能量表示：

$$p(x)=\frac{1}{Z}\exp\left[-E(x)\right]$$

并令局部能量满足：

$$E(x)=\sum_{a\in\mathcal F}E_a(x_a)$$

概率推断常见目标有两类。第一类是边缘概率：

$$p(x_i)=\sum_{x_{-i}}p(x)$$

第二类是最大后验配置：

$$x^{\mathrm{MAP}}\in\arg\max_x p(x)$$

Sum-product 主要计算边缘量，Max-product 主要计算 MAP 配置。两者使用相同图结构，但采用不同的代数运算。

## 二、Sum-product 算法

### 2.1 变量到因子的消息

变量节点 $i$ 向相邻因子 $a$ 发送：

$$m_{i\rightarrow a}(x_i)=\prod_{b\in\mathcal N(i)\setminus\{a\}}m_{b\rightarrow i}(x_i)$$

这里 $\mathcal N(i)$ 表示与变量 $i$ 相邻的因子集合。直观上，该消息汇总了除目标因子 $a$ 以外的全部局部证据。

### 2.2 因子到变量的消息

因子节点 $a$ 向变量 $i$ 发送：

$$m_{a\rightarrow i}(x_i)=\sum_{x_a\setminus x_i}\psi_a(x_a)\prod_{j\in\mathcal N(a)\setminus\{i\}}m_{j\rightarrow a}(x_j)$$

该消息对因子中的其他变量求和，保留 $x_i$ 的函数形式。

### 2.3 变量边缘与因子边缘

变量节点的未归一化 belief 为：

$$\widetilde b_i(x_i)=\prod_{a\in\mathcal N(i)}m_{a\rightarrow i}(x_i)$$

归一化后：

$$b_i(x_i)=\frac{\widetilde b_i(x_i)}{\sum_{\bar x_i}\widetilde b_i(\bar x_i)}$$

因子 belief 为：

$$b_a(x_a)\propto\psi_a(x_a)\prod_{i\in\mathcal N(a)}m_{i\rightarrow a}(x_i)$$

在无环因子图上，只要消息完成一次由叶到根、再由根到叶的传递，所得 belief 就是精确边缘分布。

### 2.4 数值稳定性

多个小概率连续相乘容易下溢。工程实现应周期性归一化消息，或在对数域计算。归一化不会改变最终边缘，因为消息本身只在正比例意义下确定。

若某条消息全部为零，通常意味着证据与模型约束不相容、势函数存在错误，或浮点下溢。不能简单用均匀分布掩盖，应记录冲突并执行明确的回退策略。

## 三、Max-product 与对数域 Max-sum

### 3.1 Max-product 消息

变量到因子的公式与 Sum-product 相同：

$$m_{i\rightarrow a}(x_i)=\prod_{b\in\mathcal N(i)\setminus\{a\}}m_{b\rightarrow i}(x_i)$$

因子到变量的求和被最大化替代：

$$m_{a\rightarrow i}(x_i)=\max_{x_a\setminus x_i}\psi_a(x_a)\prod_{j\in\mathcal N(a)\setminus\{i\}}m_{j\rightarrow a}(x_j)$$

根节点可选择：

$$x_r^\star\in\arg\max_{x_r}\prod_{a\in\mathcal N(r)}m_{a\rightarrow r}(x_r)$$

在树上，仅逐变量取最大 belief 不一定得到一致的联合 MAP。应保存每次最大化的回溯指针，从根的最优取值沿树反向恢复其他变量。

### 3.2 对数域 Max-sum

令：

$$M_{a\rightarrow i}(x_i)=\log m_{a\rightarrow i}(x_i)$$

以及：

$$\theta_a(x_a)=\log\psi_a(x_a)$$

则因子消息变成：

$$M_{a\rightarrow i}(x_i)=\max_{x_a\setminus x_i}\left[\theta_a(x_a)+\sum_{j\in\mathcal N(a)\setminus\{i\}}M_{j\rightarrow a}(x_j)\right]$$

变量消息为：

$$M_{i\rightarrow a}(x_i)=\sum_{b\in\mathcal N(i)\setminus\{a\}}M_{b\rightarrow i}(x_i)$$

对数域把乘法转换为加法，避免概率下溢。这一形式也与 DCOP 的 Max-Sum 算法直接对应。

### 3.3 零温极限

若概率模型写成：

$$p_\tau(x)\propto\exp\left[\frac{U(x)}{\tau}\right]$$

当温度 $\tau$ 趋近于零时，log-sum-exp 逐渐接近最大值：

$$\lim_{\tau\downarrow0}\tau\log\sum_x\exp\left[\frac{U(x)}{\tau}\right]=\max_x U(x)$$

这说明 Sum-product 与 Max-product 可以放在同一半环视角下理解，但二者输出的统计含义不同：一个求和聚合概率质量，一个选择最高得分配置。

## 四、Loopy Belief Propagation

### 4.1 为什么需要环图消息传递

真实系统常含闭环关系，例如多个单位共享目标、互相避碰，同时受区域资源约束。因子图出现环后，继续重复相同消息方程就得到 Loopy Belief Propagation，简称 LBP。

LBP 在树上是精确算法，在一般环图上通常是近似算法。它可能收敛到有用的固定点，也可能振荡、收敛到错误边缘，或依赖初始化和更新顺序。

### 4.2 同步与异步调度

同步更新在每轮使用上一轮全部消息计算新消息。异步更新则立即使用最新消息。残差调度优先更新变化最大的消息，其残差可定义为：

$$R_{a\rightarrow i}^{(t)}=\max_{x_i}\left|\log m_{a\rightarrow i}^{(t)}(x_i)-\log m_{a\rightarrow i}^{(t-1)}(x_i)\right|$$

异步或残差调度常能加快收敛，但执行顺序必须可记录和可复现。

### 4.3 阻尼

为减少振荡，可对归一化后的消息使用阻尼：

$$\widehat m^{(t+1)}=(1-\lambda)m^{(t)}+\lambda m_{\mathrm{new}}^{(t+1)}$$

其中 $0<\lambda\le1$。在对数域中也可以对规范化后的 log-message 做线性混合。阻尼只能改善数值行为，不会把环图近似变成精确推断。

### 4.4 Bethe 自由能解释

LBP 的固定点与 Bethe 自由能的驻点相关。Bethe 近似使用局部 belief 构造：

$$F_{\mathrm B}(b)=\sum_a\sum_{x_a}b_a(x_a)\log\frac{b_a(x_a)}{\psi_a(x_a)}+\sum_i(1-d_i)\sum_{x_i}b_i(x_i)\log b_i(x_i)$$

这里 $d_i$ 是变量节点度数。belief 还必须满足归一化与局部一致性：

$$\sum_{x_a\setminus x_i}b_a(x_a)=b_i(x_i)$$

Bethe 自由能一般非凸，可能存在多个驻点。因此 LBP 的不同初始化可能得到不同结果。

### 4.5 必须报告的诊断

LBP 至少应报告：

- 最大消息残差；
- 迭代轮数和停止原因；
- 阻尼系数与更新调度；
- belief 归一化误差；
- 相邻因子与变量 belief 的局部一致性残差；
- 不同初始化下的解差异；
- 小型子图上与精确枚举或 Junction Tree 的误差。

仅报告“算法收敛”不足以证明边缘概率准确。

## 五、Junction Tree 精确推断

### 5.1 从原图到团树

Junction Tree 把有环图转化为满足运行交集性质的团树。在无向图上，主要步骤是：

1. 若输入为贝叶斯网络，先把有向图道德化；
2. 对无向图进行三角化，使其成为弦图；
3. 提取弦图的极大团；
4. 以团交集为权重构造最大权生成树；
5. 把原始因子分配到覆盖其变量的团中。

若变量 $x_i$ 同时出现在两个团 $C_u$ 和 $C_v$ 中，则它必须出现在两团之间路径上的每一个团中。这就是运行交集性质。

### 5.2 团势与分隔集消息

团 $C$ 的初始势记为 $\Psi_C(x_C)$。相邻团 $C$ 和 $D$ 的分隔集为：

$$S_{CD}=C\cap D$$

Sum-product 团消息为：

$$m_{C\rightarrow D}(x_{S_{CD}})=\sum_{x_{C\setminus S_{CD}}}\Psi_C(x_C)\prod_{B\in\mathcal N(C)\setminus\{D\}}m_{B\rightarrow C}(x_{S_{BC}})$$

校准后的团 belief 为：

$$b_C(x_C)\propto\Psi_C(x_C)\prod_{B\in\mathcal N(C)}m_{B\rightarrow C}(x_{S_{BC}})$$

相邻团在分隔集上的边缘必须一致：

$$\sum_{x_{C\setminus S_{CD}}}b_C(x_C)=\sum_{x_{D\setminus S_{CD}}}b_D(x_D)$$

将求和替换为最大化，并保存回溯指针，可以进行精确 MAP 推断。

### 5.3 树宽决定复杂度

若最大团大小为 $w+1$，则 $w$ 是相应消元顺序的树宽。离散变量每个有至多 $K$ 个取值时，时间和空间复杂度通常含有：

$$O(K^{w+1})$$

因此 Junction Tree 对低树宽图很有效，但三角化造成的大团会迅速耗尽内存。寻找最小树宽本身是困难问题，工程上常使用 min-fill 或 min-degree 等启发式消元顺序。

## 六、DCOP：分布式约束优化问题

一个离散 DCOP 可以写为：

$$\max_{x_1,\ldots,x_n}\sum_{a\in\mathcal F}f_a(x_a)$$

变量由不同智能体持有，每个因子只涉及局部变量。智能体通过消息交换协调取值，而不需要把完整全局问题集中到一个节点。

DCOP 模型通常包含：

- 智能体集合；
- 每个智能体控制的变量；
- 每个变量的有限取值域；
- 局部效用或代价函数；
- 通信图与消息协议；
- 隐私、时延和失联假设。

把所有约束违反设为一个极大负数虽然简单，但可能造成数值问题。更稳妥的做法是显式移除非法配置，或使用具有明确上界的惩罚并验证其足以排除违规解。

## 七、Max-Sum 与 DCOP

### 7.1 消息方程

DCOP 的 Max-Sum 直接在效用域工作。变量到因子的消息为：

$$q_{i\rightarrow a}(x_i)=\sum_{b\in\mathcal N(i)\setminus\{a\}}r_{b\rightarrow i}(x_i)$$

因子到变量的消息为：

$$r_{a\rightarrow i}(x_i)=\max_{x_a\setminus x_i}\left[f_a(x_a)+\sum_{j\in\mathcal N(a)\setminus\{i\}}q_{j\rightarrow a}(x_j)\right]$$

变量的局部聚合得分为：

$$z_i(x_i)=\sum_{a\in\mathcal N(i)}r_{a\rightarrow i}(x_i)$$

在树形因子图上，可选择根变量并使用回溯指针恢复全局最优配置。若每个变量独立执行：

$$x_i^\star\in\arg\max_{x_i}z_i(x_i)$$

而不进行一致的回溯或破同分协调，即使在树上也可能因并列最大值产生不一致联合动作。

### 7.2 消息规范化

给一条 Max-Sum 消息加常数不会改变最优配置。因此可做规范化：

$$\bar r_{a\rightarrow i}(x_i)=r_{a\rightarrow i}(x_i)-\max_{\bar x_i}r_{a\rightarrow i}(\bar x_i)$$

这可以防止消息绝对值不断漂移，并改善浮点稳定性。

### 7.3 环图上的 Max-Sum

在有环 DCOP 上，Max-Sum 与 LBP 一样不保证收敛或最优。常用工程措施包括：

- 阻尼；
- 异步或残差调度；
- 固定迭代预算；
- 对部分边进行剪枝或形成生成树；
- 使用 bounded Max-Sum 给出结构化损失界；
- 在最终执行前集中检查冲突并修复非法联合动作。

必须把“消息固定点”“可行联合动作”和“全局最优解”区分开。

### 7.4 DCOP 的游戏用途

每个英雄或单位可以控制一个宏动作变量，例如进攻、掩护、撤退、侦察或占点。局部因子表示：

- 两名单位的协同或冲突；
- 区域容量与碰撞；
- 治疗、控制和输出链；
- 共享目标收益；
- 阵型、距离与通信约束；
- 局部风险和资源消耗。

Max-Sum 适合快速协调有限宏动作，但地图通行、技能合法性和硬资源约束仍应由原生规则或精确约束求解器复核。

## 八、ADMM 分布式优化

### 8.1 可分共识模型

考虑多个节点共同求解：

$$\min_{x_1,\ldots,x_N,z}\sum_{i=1}^N f_i(x_i)\quad\mathrm{s.t.}\quad x_i=z$$

其中 $x_i$ 是节点 $i$ 的局部变量，$z$ 是全局共识变量。增广拉格朗日为：

$$L_\rho(x,z,y)=\sum_i\left[f_i(x_i)+y_i^\mathsf{T}(x_i-z)+\frac{\rho}{2}\|x_i-z\|_2^2\right]$$

令缩放对偶变量 $u_i=y_i/\rho$，ADMM 迭代为：

$$x_i^{k+1}=\arg\min_{x_i}\left[f_i(x_i)+\frac{\rho}{2}\|x_i-z^k+u_i^k\|_2^2\right]$$

$$z^{k+1}=\frac{1}{N}\sum_{i=1}^N\left(x_i^{k+1}+u_i^k\right)$$

$$u_i^{k+1}=u_i^k+x_i^{k+1}-z^{k+1}$$

如果全局变量还受集合约束 $z\in\mathcal C$，则 $z$ 更新变为对平均量在 $\mathcal C$ 上的投影。

### 8.2 图共识形式

在通信图 $G=(V,E)$ 上，也可对每条边施加：

$$x_i=x_j\quad\forall(i,j)\in E$$

若通信图连通，所有边共识会推出全局共识。图断开时，每个连通分量只能形成自己的局部共识，不能报告为全局一致。

### 8.3 原始与对偶残差

共识原始残差为：

$$r^{k+1}=\left(x_1^{k+1}-z^{k+1},\ldots,x_N^{k+1}-z^{k+1}\right)$$

缩放后的对偶残差可写为：

$$s^{k+1}=\rho\left(z^{k+1}-z^k\right)$$

停止条件应同时检查：

$$\|r^{k+1}\|_2\le\varepsilon_{\mathrm{pri}}$$

$$\|s^{k+1}\|_2\le\varepsilon_{\mathrm{dual}}$$

只检查目标函数变化可能在节点仍未达成共识时过早停止。

### 8.4 惩罚参数与自适应调整

$\rho$ 太小会使共识建立缓慢，太大则可能让局部优化过度服从共识并降低数值效率。残差平衡策略可按以下三种情况调整。

当原始残差显著较大时：

$$\|r^k\|_2>\mu\|s^k\|_2\quad\Rightarrow\quad\rho^{k+1}=\tau\rho^k$$

当对偶残差显著较大时：

$$\|s^k\|_2>\mu\|r^k\|_2\quad\Rightarrow\quad\rho^{k+1}=\rho^k/\tau$$

其他情况下保持：

$$\rho^{k+1}=\rho^k$$

改变 $\rho$ 时要相应缩放对偶变量，保持未缩放乘子一致。参数 $\mu$ 和 $\tau$ 是算法设置，应通过问题尺度与回放验证，而不是视为通用常数。

### 8.5 收敛边界

在闭、真、凸函数和适当鞍点存在条件下，标准两块 ADMM 具有可靠的收敛理论。非凸局部规划、整数变量、异步通信、多块直接扩展和丢包环境需要额外条件或专门算法。

把离散 DCOP 变量直接放入 ADMM 会形成非凸或混合整数子问题，标准凸 ADMM 的全局收敛保证不再成立。此时 ADMM 可以作为启发式协调器，但最终结果必须检查可行性和最优性差距。

## 九、Max-Sum 与 ADMM 的关系和区别

两者都利用目标可分解性并交换局部消息，但数学对象不同。

| 维度 | Max-Sum / DCOP | ADMM |
|---|---|---|
| 主要变量 | 有限离散变量 | 通常是连续变量 |
| 全局目标 | 局部效用之和最大化 | 可分函数之和最小化 |
| 协调机制 | 因子图最大化消息 | 增广拉格朗日与对偶变量 |
| 树上性质 | 树形因子图可精确 | 与树形无直接等价关系 |
| 环图性质 | 通常为近似启发式 | 凸两块形式下可收敛 |
| 主要输出 | 联合离散配置 | 连续共识解与对偶量 |
| 典型用途 | 角色分工、任务分配、宏动作 | 资源预算、轨迹、参数共识 |

离散角色选择适合 Max-Sum；连续资源、位置参考量或模型参数共享适合 ADMM。混合问题可以分层求解，但不能假设两个近似层组合后自动保持全局最优。

## 十、Junction Tree 与 Loopy BP 的选择

当图树宽较小且需要可信精确边缘时，应优先考虑 Junction Tree。若树宽很大但局部因子稀疏、实时性更重要，可以使用 LBP，并提供收敛和误差诊断。

选择流程可以概括为：

1. 先估计消元顺序和最大团规模；
2. 若团表可承受，使用 Junction Tree；
3. 若团表不可承受，考虑 LBP、变分法、采样或结构裁剪；
4. 在可精确求解的小型切片上校验近似误差；
5. 对关键安全约束保留独立精确检查。

## 十一、统一的游戏分层架构

可以把五类技术组合为以下层次：

1. Sum-product 根据视野、战报和传感信息更新敌情边缘；
2. Max-product 从概率模型中恢复最可能的联合隐藏状态；
3. Junction Tree 负责低树宽关键子图的精确推断；
4. LBP 负责大规模环图的近似实时推断；
5. Max-Sum/DCOP 为单位分配离散宏动作和目标；
6. ADMM 协调连续资源、轨迹参考或共享参数；
7. 原生规则、碰撞检测、CP-SAT/MILP 与 MAPF 负责最终可行性。

推断层输出信念或候选，优化层输出建议联合动作；任何一层都不应绕过游戏合法动作系统。

## 十二、5v5 应用示例

### 12.1 敌方意图推断

变量可以表示敌方五名英雄的意图、目标区域和技能状态。局部因子表示视野证据、英雄组合、距离关系和目标刷新时间。Sum-product 计算各英雄意图边缘，Max-product 给出联合最可能解释。

### 12.2 团战角色分配

每名英雄的变量取值为开团、跟进、保护、侧翼、撤退等宏动作。局部因子表示技能衔接、距离、输出窗口和生存风险。Max-Sum 产生联合角色方案，规则层再检查技能冷却、可达性和目标合法性。

### 12.3 连续资源协调

节点可以分别优化路线压力、视野预算和目标区域驻留比例。ADMM 让各节点保留局部目标，同时对团队总预算或共享变量达成共识。实时执行时需要设置固定迭代预算和超时回退。

## 十三、战棋与战略游戏应用

在战棋中，因子图可以表达相邻单位掩护、补给覆盖、区域容量和敌情证据；DCOP 可以把攻击、防守、护送和侦察任务分配给不同单位；ADMM 可以协调各战区的连续补给份额、风险预算和兵力松弛变量。

在战略层，Junction Tree 适合对低树宽外交网络做精确推断，LBP 适合更大规模的联盟和情报关系图。若关系图中的环很多且作用强，必须把 LBP 的多固定点和误差纳入决策风险，而不能把 belief 当作真实概率。

## 十四、工程实现建议

### 14.1 数据结构

- 为变量定义稳定编号、取值域和所有者；
- 为因子定义作用域、张量维度和合法配置；
- 消息携带来源、目标、迭代号、规范化常数和时间戳；
- 明确同步、异步、延迟和丢包语义；
- 所有破同分规则使用确定性次序或显式公共随机种子。

### 14.2 计算缓存

因子消息的主要成本是对其他变量求和或最大化。可以缓存局部张量切片、使用向量化缩并，并对不变因子预计算。优化不能改变变量轴顺序或回溯指针语义。

### 14.3 超时与降级

实时系统应设置：

- 最大消息轮数；
- 单次推断时间上限；
- 残差未收敛时的可信度标记；
- 通信断开时的局部策略；
- 非法联合动作的集中修复；
- 上一次可行解或保守规则策略作为回退。

## 十五、验证方案

### 15.1 Sum-product 与 Max-product

- 在小图上与完整枚举边缘比较；
- 检查每个 belief 非负且归一化；
- 树图上验证消息结果与变量消元一致；
- MAP 使用回溯恢复，并与暴力最优配置比较；
- 零势与不相容证据必须产生明确诊断。

### 15.2 LBP

- 报告最大消息残差和局部一致性残差；
- 从多种初始化运行；
- 比较同步、异步和阻尼调度；
- 在小规模精确子图上测量边缘误差；
- 未收敛时不得标记为精确概率。

### 15.3 Junction Tree

- 验证团树的运行交集性质；
- 检查每个原始因子恰当分配到覆盖团；
- 校准后检查分隔集边缘一致性；
- 记录最大团规模、树宽估计和峰值内存；
- 与完整枚举结果比较。

### 15.4 Max-Sum/DCOP

- 树图上与集中式枚举最优解比较；
- 检查消息规范化不改变最终配置；
- 保存最大化回溯指针；
- 环图上报告残差、迭代预算与全局效用；
- 最终联合动作执行硬约束复核。

### 15.5 ADMM

- 同时报告原始残差和对偶残差；
- 与集中式凸求解结果比较目标值和解；
- 检查通信图连通性；
- 记录 $\rho$ 调整和对偶变量缩放；
- 非凸或整数版本明确标记为启发式结果。

## 十六、常见误区

第一，Sum-product 的最大边缘取值组合不一定等于联合 MAP。联合 MAP 应使用 Max-product 或其他 MAP 求解方法，并保持回溯一致性。

第二，LBP 消息残差趋近于零不代表边缘一定准确。它只表明算法接近某个固定点。

第三，Junction Tree 并非把任何图都廉价地变成树。复杂度转移到了可能很大的团，关键参数是树宽。

第四，DCOP 中各智能体独立选择局部最大动作可能产生不一致。树上需要回溯，环图上需要破同分协调和最终冲突检查。

第五，Max-Sum 的名字既可指 Max-product 的对数域形式，也可指 DCOP 消息算法。两者代数相近，但模型语义与执行协议不同。

第六，ADMM 不是任意非凸、多块、整数或异步问题的通用收敛保证。使用这些扩展时必须说明额外假设并验证可行性。

第七，概率推断和决策优化不能混为一谈。高概率状态不一定对应高效用动作，最优动作还依赖收益、风险和约束。

## 十七、结论

Sum-product 在树形因子图上精确计算边缘，Max-product 通过最大化和回溯恢复 MAP 配置；LBP 把相同消息方程扩展到环图，以精确性换取可扩展性；Junction Tree 通过三角化和团树提供精确推断，但复杂度受树宽支配；Max-Sum 将局部效用因子用于离散 DCOP 协同；ADMM 则通过增广拉格朗日、局部子问题和共识变量解决可分连续优化。

在游戏模型中，推荐让图推断方法负责不确定性和隐藏状态，让 Max-Sum/DCOP 负责离散协同，让 ADMM 负责连续资源共识，并由原生规则与精确约束层验证最终动作。每一种方法都应输出残差、停止原因和适用条件，而不是只返回一个看似确定的答案。

## 参考文献

1. Kschischang, F. R., Frey, B. J. and Loeliger, H.-A. Factor Graphs and the Sum-Product Algorithm.
2. Pearl, J. Probabilistic Reasoning in Intelligent Systems.
3. Yedidia, J. S., Freeman, W. T. and Weiss, Y. Understanding Belief Propagation and Its Generalizations.
4. Lauritzen, S. L. and Spiegelhalter, D. J. Local Computations with Probabilities on Graphical Structures and Their Application to Expert Systems.
5. Wainwright, M. J. and Jordan, M. I. Graphical Models, Exponential Families, and Variational Inference.
6. Farinelli, A., Rogers, A., Petcu, A. and Jennings, N. R. Decentralised Coordination of Low-Power Embedded Devices Using the Max-Sum Algorithm.
7. Fioretto, F., Pontelli, E. and Yeoh, W. Distributed Constraint Optimization Problems and Applications: A Survey.
8. Boyd, S., Parikh, N., Chu, E., Peleato, B. and Eckstein, J. Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers.
