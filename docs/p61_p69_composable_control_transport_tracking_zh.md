# P61-P69：多智能体协同、跟踪、控制、概率流与可组合验证

本文记录 P61-P69 在游戏模型中的数学语义、接口边界和联合接入方式。所有模块均为分析、候选生成或安全诊断工具，不会扩大游戏原生动作集合，也不能绕过技能冷却、资源、碰撞、视野和规则检查。

## P61：多智能体路径冲突

`rl/p61_multi_agent_path_conflict_math.py` 提供顶点冲突、对向换边冲突、预约表、ECBS focal 集和连续时间最近接近检测。连续线段冲突使用相对运动

$$
r(t)=r_0+v_rt,\qquad t^*=\operatorname{clip}\left(-\frac{r_0^Tv_r}{v_r^Tv_r},0,T\right).
$$

适用于英雄集结、狭窄通道让行、追击包夹和编队移动。CBS/ECBS 仍需由上层搜索器生成约束树，本模块只提供冲突与节点筛选原语。

## P62：随机有限集与多目标跟踪

`rl/p62_random_finite_set_tracking_math.py` 提供小规模精确 JPDA 边缘化、PHD 生存/出生预测、单观测 PHD 更新和多假设剪枝。JPDA 会排除多个目标占用同一观测的非法联合关联；PHD 权重和表示期望目标数，不是单目标后验概率。

游戏中用于视野断续时的敌方目标关联、分身/召唤物区分和草丛进出后的多假设保留。输入似然必须来自感知模型，不能把缺失观测直接当作目标消失。

## P63：鲁棒与随机 MPC

`rl/p63_robust_stochastic_mpc_math.py` 用区间传播求闭环系统的最小鲁棒正不变盒近似：

$$
r_{k+1}=|A_{cl}|r_k+w.
$$

模块还支持约束收紧、盒不变性复核、场景违反率和经验机会约束裕量。可用于走位控制、技能释放窗口和网络延迟下的轨迹修正。经验覆盖率不是分布外保证；正式场景 MPC 还需说明样本独立性、置信度和样本复杂度。

## P64：混杂与切换系统

`rl/p64_hybrid_switching_system_math.py` 提供 Saltation Matrix、平均驻留时间、切换 Lyapunov 上界、模式轨迹验证和 Zeno 候选检测。无显式时变重置时，盐跃矩阵为

$$
S=D R+\frac{(f^+-D R f^-)n^T}{n^T f^-+g_t}.
$$

它适合描述移动、施法、受控、击退、死亡和复活等离散模式与连续状态的耦合。Zeno 检测仅根据连续短间隔报警，最终原因需结合状态机日志确认。

## P65：各向异性代价场与动态势场

`rl/p65_anisotropic_dynamic_field_math.py` 支持 SPD 度量的各向异性比、Randers 有向代价、预测最近接近势能和限速向量融合。Randers 代价采用

$$
F(v)=\sqrt{v^TMv}+b^Tv,\qquad b^TM^{-1}b<1.
$$

该模块可以表达坡度、草丛、塔火力、单向追逃优势和移动敌人的时变风险。动态势场只作为局部代价，必须与 P55 可达图或 P61 冲突规划结合，以避免局部极小和绕圈。

## P66：事件触发与网络化控制

`rl/p66_event_network_control_math.py` 提供 AoI 跟踪、饱和均匀量化、相对/绝对事件触发、丢包零阶保持和离散数据率下界。Age of Information 定义为

$$
\Delta(t)=t-u(t),
$$

其中 $u(t)$ 是当前已接收最新信息的生成时刻。游戏中可根据队友状态的新鲜度衰减协同权重，并在误差超阈值时发送更新。数据率下界是稳定化的必要诊断，不等于实际协议吞吐预算。

## P67：Benamou-Brenier 与概率流桥接

`rl/p67_benamou_brenier_bridge_math.py` 提供离散连续性残差、动态最优传输作用量、熵正则 Sinkhorn 耦合、概率流 ODE 速度和线性 flow-matching 目标：

$$
\partial_t\rho+\nabla\cdot m=0,\qquad
\mathcal A=\int_0^1\int\frac{\|m\|^2}{\rho}\,dx\,dt.
$$

可用于把当前编队分布平滑输运到目标阵型、重放轨迹分布插值和生成候选路径。熵正则耦合与线性插值不是障碍物可行轨迹，输出仍需经过地图和碰撞过滤。

## P68：Ramadge-Wonham 监督控制

`rl/p68_supervisory_control_math.py` 在有限语言上提供前缀闭包、自然投影、可控性、可观测性、最大可控子语言和监督器使能事件。不可控事件必须满足

$$
\overline K\Sigma_{uc}\cap L\subseteq\overline K.
$$

可把击退、硬控、被动触发等建模为不可控事件，把移动、施法和回城建模为可禁用事件，从而生成不阻塞的安全行为语言。当前实现面向有限枚举语言，大型系统应转为自动机上的不动点算法。

## P69：Assume-Guarantee、Barrier 与可组合概率界

`rl/p69_contract_barrier_composition_math.py` 提供有限行为集上的假设-保证契约、饱和保证与精化关系、样本化 barrier 条件，以及 union bound、独立失效界、条件失效组合和风险预算分配。契约条件失效组合为

$$
P(F)\leq P(\neg A)+\bigl(1-P(\neg A)\bigr)P(F\mid A).
$$

Barrier 样本检查只能验证给定样本上的符号条件，不构成连续状态空间的全局证书；全局证明需要 SOS、区间验证或形式化模型检测。

## 联合接入顺序

1. P62 维护带关联不确定性的敌我目标 belief，P66 根据 AoI、丢包和量化误差给 belief 降权。
2. P65 构造有向时变代价，P67 生成群体分布或阵型迁移候选。
3. P61 消解离散和连续时间路径冲突，P63 对候选轨迹做扰动管束与机会约束复核。
4. P64 检查移动、受控、施法等混杂模式切换，P68 禁用会把行为语言带出安全规范的可控事件。
5. P69 为子系统声明假设、保证与风险预算，并与 P51 barrier、P55 可达图、P56 死锁/活锁监控联合验收。
6. 最终动作仍必须通过原生合法动作、资源、地图、技能、战斗规则和回放测试。

## 定向回归

```powershell
python -m pytest rl/p61_multi_agent_path_conflict_math_test.py rl/p62_random_finite_set_tracking_math_test.py rl/p63_robust_stochastic_mpc_math_test.py rl/p64_hybrid_switching_system_math_test.py rl/p65_anisotropic_dynamic_field_math_test.py rl/p66_event_network_control_math_test.py rl/p67_benamou_brenier_bridge_math_test.py rl/p68_supervisory_control_math_test.py rl/p69_contract_barrier_composition_math_test.py -q
```
