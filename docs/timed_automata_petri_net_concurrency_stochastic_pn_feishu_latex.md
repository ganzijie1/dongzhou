# Timed Automata、Petri Net 与并发系统：时间、同步、死锁与随机演化

## 摘要

并发系统由多个能够同时推进、竞争资源、互相同步并发生因果依赖的组件组成。单一顺序状态机可以描述“先做什么、后做什么”，但难以自然表达多个英雄同时移动和施法、共享控制权、等待队友、争夺同一目标、技能冷却、网络时延和随机事件。

Timed Automata，简称时间自动机，在有限状态机上增加连续时钟、守卫、重置和位置不变量，适合验证严格时间窗、超时、同步和最坏时延。Petri Net，简称 Petri 网，用库所、变迁和令牌直接表达并发、资源、冲突、同步与因果关系。Time Petri Net 给变迁增加确定性发射区间；Stochastic Petri Net 给变迁增加随机发射时间，可进一步映射到连续时间 Markov 链，分析吞吐、等待、失败概率和稳态占用。

本文系统介绍并发语义、偏序、时间自动机、区域与 Zone 抽象、Petri 网结构性质、时间 Petri 网、随机 Petri 网、广义随机 Petri 网、CTMC 分析、模型检测、仿真与参数估计，并以 5v5 MOBA 的技能冷却、控制链、团战同步、资源互斥、塔仇恨、死锁和活锁为贯穿案例。

## 一、并发系统的统一视角

设系统由 $n$ 个组件组成：

$$\mathcal S=\mathcal S_1\parallel\mathcal S_2\parallel\cdots\parallel\mathcal S_n$$

组件 $i$ 的局部状态为 $s_i$，全局状态为：

$$s=(s_1,s_2,\ldots,s_n)$$

若局部状态数为 $m_i$，朴素全局状态数为：

$$\lvert S\rvert=\prod_{i=1}^{n}m_i$$

这说明并发建模的主要困难不是单个组件复杂，而是全局笛卡尔积造成的状态爆炸。

## 二、交错语义

交错语义把同时发生的动作解释为某种顺序：

$$a\parallel b\rightsquigarrow ab\ \vee\ ba$$

若动作 $a$ 和 $b$ 相互独立，则：

$$ab\sim ba$$

两条执行序列代表同一偏序行为。模型检测若枚举两种顺序，会产生冗余状态。

MOBA 中两名英雄在不同区域独立移动通常可以交换顺序；两个技能争夺同一控制权或同一目标时则不能交换。

## 三、真正并发与偏序

事件集合为 $E$，因果关系为：

$$\prec\ \subseteq E\times E$$

若：

$$e_i\prec e_j$$

表示事件 $e_j$ 必须等待 $e_i$。若两事件既无因果关系又无冲突，则可以并发。

一次执行可以表示为偏序：

$$\rho=(E,\prec)$$

而不必强行选择唯一线性顺序。Petri 网天然保留这种并发结构。

## 四、同步、冲突与资源竞争

同步要求多个组件共同完成一个事件：

$$a_1\otimes a_2\otimes\cdots\otimes a_k$$

冲突表示多个动作竞争同一资源：

$$a\# b$$

互斥资源容量为一时：

$$m(r)\le1$$

MOBA 中的共享移动控制权、同一技能槽、同一召唤物、唯一目标锁和团队指挥令牌都可以视为资源。

## 五、安全性与活性

安全性表达“坏事永远不发生”：

$$\Box\neg\mathrm{Bad}$$

活性表达“好事最终会发生”：

$$\Box(\mathrm{Request}\Rightarrow\Diamond\mathrm{Response})$$

有界响应要求：

$$\Box(\mathrm{Request}\Rightarrow\Diamond^{\le T}\mathrm{Response})$$

死锁主要破坏活性；越塔、重复施法和非法控制权则通常是安全性问题。

## 六、死锁、活锁与饥饿

死锁状态满足：

$$A(s)=\varnothing$$

活锁轨迹持续执行动作，但进度不增加：

$$\sum_{k=t-W+1}^{t}\lVert a_k-a_{k-1}\rVert\gt\epsilon_a$$

$$P_t-P_{t-W}\le\epsilon_P$$

饥饿表示某个持续可用的动作永远没有被调度：

$$\Diamond\Box\mathrm{Enabled}(a)\ \wedge\ \Box\Diamond\neg\mathrm{Fired}(a)$$

公平性假设决定“持续可用是否最终执行”，必须在模型中明确声明。

## 七、Timed Automata 的定义

一个时间自动机写为：

$$\mathcal A=(L,\ell_0,C,\Sigma,E,I)$$

其中：

- $L$ 是有限位置集合。
- $\ell_0$ 是初始位置。
- $C$ 是实值时钟集合。
- $\Sigma$ 是动作标签集合。
- $E$ 是带守卫和重置的边。
- $I$ 是位置不变量。

一条边表示为：

$$e=(\ell,g,a,R,\ell')$$

$g$ 是时钟守卫，$R\subseteq C$ 是重置时钟集合。

## 八、时钟赋值

时钟赋值为：

$$\nu:C\rightarrow\mathbb R_{\ge0}$$

时间经过 $d$ 后：

$$(\nu+d)(x)=\nu(x)+d$$

将集合 $R$ 中的时钟重置为零：

$$\nu[R:=0](x)=0,\qquad x\in R$$

未被重置的时钟保持原值：

$$\nu[R:=0](x)=\nu(x),\qquad x\notin R$$

## 九、时钟约束

基本守卫可以写为：

$$x\le c$$

$$x\ge c$$

差分时钟约束为：

$$x-y\le c$$

守卫由这些原子命题的合取构成。位置不变量限制在当前位置最多可以停留多久，例如：

$$I(\ell):x\le5$$

它表示进入位置 $\ell$ 后，必须在五个时间单位内离开。

## 十、时间迁移语义

时间自动机状态为：

$$q=(\ell,\nu)$$

延时迁移写为：

$$(\ell,\nu)\xrightarrow{d}(\ell,\nu+d)$$

它要求延时期间始终满足位置不变量：

$$\forall d'\in[0,d],\quad \nu+d'\models I(\ell)$$

离散迁移写为：

$$(\ell,\nu)\xrightarrow{a}(\ell',\nu')$$

并要求：

$$\nu\models g$$

$$\nu'=\nu[R:=0]$$

$$\nu'\models I(\ell')$$

## 十一、技能冷却时间自动机

单个技能可设位置：

$$L=\{\mathrm{Ready},\mathrm{Casting},\mathrm{Cooldown}\}$$

时钟 $x$ 记录施法或冷却时间。施法完成条件为：

$$x\ge\tau_{\mathrm{cast}}$$

冷却完成条件为：

$$x\ge\tau_{\mathrm{cd}}$$

若施法期间必须在上限前结束：

$$I(\mathrm{Casting}):x\le\tau_{\mathrm{cast}}^{\max}$$

被打断、取消和死亡可以建成额外边，并按规则选择是否重置冷却。

## 十二、控制链时间窗

设第一个控制技能命中时重置时钟 $x$。后续技能必须在控制结束前命中：

$$x\le\tau_{\mathrm{cc}}$$

若第二个技能过早释放会浪费重叠控制，可以加入下界：

$$x\ge\tau_{\mathrm{cc}}-\delta$$

可行接续窗口为：

$$\tau_{\mathrm{cc}}-\delta\le x\le\tau_{\mathrm{cc}}$$

时间自动机可以验证是否存在满足网络时延、前摇和弹道时间的合法控制链。

## 十三、超时与看门狗

等待队友、等待寻路和等待技能都应有超时。等待位置的不变量为：

$$I(\mathrm{Wait}):x\le\tau_{\mathrm{wait}}$$

成功同步边守卫为：

$$\mathrm{ready}=1$$

超时边守卫为：

$$x\ge\tau_{\mathrm{wait}}$$

这样模型不会永久停留在 Wait 状态，运行时也能生成明确的恢复动作。

## 十四、时间自动机的同步

两个自动机可通过通道同步。发送动作记为：

$$a!$$

接收动作记为：

$$a?$$

只有发送端和接收端都启用时，联合动作才发生：

$$a!\parallel a?\rightarrow a$$

这适合描述“开团者发出 engage，队友进入响应状态”“技能控制命中后爆发模块接管”等协议。

## 十五、广播同步

广播发送端执行：

$$b!$$

所有当前能接收 $b?$ 的组件同步响应，不能接收的组件不阻止广播。

MOBA 中团队撤退、目标重置和全队安全否决更适合广播；必须全员到齐的集合行动则更适合握手或 barrier 同步。

## 十六、紧迫位置与承诺位置

紧迫位置禁止时间流逝：

$$d=0$$

承诺位置不仅禁止时间流逝，还要求下一步由承诺组件执行。

紧迫机制适合原子化控制权交接或立即安全否决，但滥用会制造人为死锁。只有确实要求零延迟的逻辑才应使用。

## 十七、时间自动机网络

多个自动机组成网络：

$$\mathcal N=\mathcal A_1\parallel\cdots\parallel\mathcal A_n$$

全局位置为：

$$\ell=(\ell_1,\ldots,\ell_n)$$

时钟集合为：

$$C=\bigcup_{i=1}^{n}C_i$$

共享变量和同步通道带来耦合。若每个组件位置数为 $m_i$，全局离散位置数仍可能达到 $\prod_i m_i$。

## 十八、区域抽象

虽然时钟取连续实数，若最大常数为 $M$，可以按整数部分、是否超过 $M$、小数部分是否为零及小数排序建立有限区域等价类。

区域等价记为：

$$\nu\sim_M\nu'$$

若两个赋值位于同一区域，则它们满足相同的相关时钟约束，并具有等价的离散可达行为。

区域图将无限状态时间自动机转化为有限图，但区域数量随时钟数快速增长。

## 十九、Zone 与差分约束

Zone 是由差分约束定义的凸时钟集合：

$$x_i-x_j\le c_{ij}$$

引入零时钟 $x_0=0$ 后，上下界都可以写成差分形式：

$$x_i-x_0\le u_i$$

$$x_0-x_i\le-l_i$$

Difference Bound Matrix，简称 DBM，用矩阵元素保存 $c_{ij}$，通常比显式区域图更高效。

## 二十、Zone 后继运算

对 Zone $Z$，执行延时闭包：

$$Z^{\uparrow}=\{\nu+d\mid\nu\in Z,\ d\ge0\}$$

与守卫相交：

$$Z_g=Z^{\uparrow}\cap\llbracket g\rrbracket$$

重置后：

$$Z_R=\{\nu[R:=0]\mid\nu\in Z_g\}$$

再与目标位置不变量相交：

$$Z'=Z_R\cap\llbracket I(\ell')\rrbracket$$

若 $Z'$ 非空，则该符号迁移可达。

## 二十一、时间可达性

目标位置集合为 $F$。可达问题问：

$$\exists\rho:\ \mathrm{Last}(\rho)\in F$$

最短到达时间为：

$$T^*=\inf_{\rho:\mathrm{Last}(\rho)\in F}\mathrm{Time}(\rho)$$

最坏响应时间为：

$$T_{\max}=\sup_{\rho:\mathrm{Request}\leadsto\mathrm{Response}}\Delta t(\rho)$$

它可用于验证技能链最短完成时间、队伍最晚集结时间和安全撤退上界。

## 二十二、Zeno 行为

若无限多个离散动作在有限时间内发生，则是 Zeno 行为：

$$\sum_{k=1}^{\infty}d_k\lt\infty$$

例如两个零时延内部动作无限互相触发。真实游戏不可能执行无限事件，因此验证时应要求时间发散：

$$\sum_{k=1}^{\infty}d_k=\infty$$

每个循环加入正时间下界或公平调度，可以排除多数 Zeno 伪路径。

## 二十三、时间博弈自动机

在时间博弈中，可控动作属于智能体：

$$\Sigma_c$$

不可控动作属于环境或敌方：

$$\Sigma_u$$

控制器要选择动作和等待时间，使目标在任何环境响应下仍满足：

$$\Box\neg\mathrm{Unsafe}$$

或：

$$\Diamond\mathrm{Target}$$

它适合验证敌方可能打断、延迟或先手时，我方控制链和撤退协议是否仍有必胜时间策略。

## 二十四、Petri 网的定义

一个普通 Petri 网写为：

$$N=(P,T,\mathrm{Pre},\mathrm{Post},M_0)$$

其中：

- $P$ 是库所集合。
- $T$ 是变迁集合。
- $\mathrm{Pre}$ 是输入弧权。
- $\mathrm{Post}$ 是输出弧权。
- $M_0$ 是初始标识。

标识为：

$$M\in\mathbb N^{\lvert P\rvert}$$

$M(p)$ 表示库所 $p$ 中的令牌数。

## 二十五、变迁使能与发射

变迁 $t$ 使能的条件为：

$$M\ge\mathrm{Pre}(:,t)$$

发射后：

$$M'=M-\mathrm{Pre}(:,t)+\mathrm{Post}(:,t)$$

定义关联矩阵：

$$C=\mathrm{Post}-\mathrm{Pre}$$

则：

$$M'=M+C(:,t)$$

对发射计数向量 $\sigma$：

$$M=M_0+C\sigma$$

状态方程是可达性的必要条件，但通常不是充分条件。

## 二十六、并发变迁

变迁集合 $U\subseteq T$ 可以并发发射，当：

$$M\ge\sum_{t\in U}\mathrm{Pre}(:,t)$$

若两个变迁不竞争输入令牌，则它们可以独立发生。若：

$$\mathrm{Pre}(:,t_1)+\mathrm{Pre}(:,t_2)\not\le M$$

则它们发生结构冲突或标识冲突。

Petri 网用令牌消费直接表达资源竞争，不必枚举所有组件状态组合。

## 二十七、技能资源 Petri 网

可以设置库所：

$$P=\{\mathrm{Ready},\mathrm{Mana},\mathrm{Target},\mathrm{ControlToken},\mathrm{Cooldown}\}$$

施法变迁需要同时消费技能可用、足够资源、合法目标和控制权令牌。施法完成后生成冷却令牌和效果令牌。

若导航与战斗都需要唯一 ControlToken，则同一时刻只有一个模块能提交最终移动命令，从结构上避免控制器并发写入。

## 二十八、团队同步 Petri 网

每名英雄到位后向库所 $p_i^{\mathrm{ready}}$ 放入令牌。开团变迁的输入要求：

$$M(p_i^{\mathrm{ready}})\ge1,\qquad i\in\mathcal I$$

当所需角色全部到位时，开团变迁才使能。

若只要求至少 $k$ 人到位，可使用聚合库所：

$$M(p_{\mathrm{team}})\ge k$$

必须同时提供超时或降级变迁，否则缺席英雄可能让全队永久等待。

## 二十九、可达图与覆盖图

从 $M_0$ 出发，所有可达标识组成：

$$R(N,M_0)=\{M\mid M_0\xrightarrow{\sigma}M\}$$

若令牌数无界，可达图可能无限。覆盖图使用符号 $\omega$ 表示任意大的令牌数：

$$n\lt\omega$$

Karp-Miller 树通过加速增长序列构造有限覆盖表示，可用于判断库所是否可能无界。

## 三十、有界性与安全性

库所 $p$ 是 $k$ 有界的，如果：

$$\forall M\in R(N,M_0),\quad M(p)\le k$$

若 $k=1$，称为安全库所。

整个网有界，当所有库所都存在有限上界。控制权、唯一技能槽和目标锁通常应建成安全库所；事件队列和任务积压则可能需要更大容量。

## 三十一、Petri 网活性

变迁 $t$ 从标识 $M$ 最终可使能，如果：

$$\exists M'\in R(N,M),\quad t\ \mathrm{enabled\ at}\ M'$$

若对所有可达标识都可以最终重新使能 $t$，则 $t$ 具有强活性。

团队撤退、控制权释放和路径重规划应保持活性；否则系统可能进入无法再触发恢复的结构性陷阱。

## 三十二、Petri 网死锁

死锁标识满足：

$$\forall t\in T,\quad M\not\ge\mathrm{Pre}(:,t)$$

正常终止标识也可能没有使能变迁，因此需要定义合法终止集合 $F$。真正死锁集合为：

$$D=\{M\mid\mathrm{Enabled}(M)=\varnothing,\ M\notin F\}$$

运行时“所有模块都在等待令牌”可以映射到这一结构。

## 三十三、P 不变量

若向量 $y$ 满足：

$$y^\top C=0$$

则：

$$y^\top M=y^\top M_0$$

称为 P 不变量。它表达令牌守恒。

例如唯一控制权令牌应满足：

$$M(p_{\mathrm{free}})+M(p_{\mathrm{nav}})+M(p_{\mathrm{fight}})+M(p_{\mathrm{safety}})=1$$

如果运行日志违反该式，说明控制权丢失或重复创建。

## 三十四、T 不变量

若非零向量 $x\ge0$ 满足：

$$Cx=0$$

则 $x$ 是 T 不变量候选，表示一组变迁按计数 $x$ 发射后回到原标识。

T 不变量可以发现循环行为，例如“选目标、靠近、撤退、重新选同一目标”形成状态闭环。结构上存在循环不等于一定活锁，还要检查循环是否带来任务进度。

## 三十五、Siphon 与 Trap

库所集合 $S$ 是 siphon，当进入 $S$ 的每个变迁也从 $S$ 取令牌：

$$\mathop{\bullet}S\subseteq S^{\mathop{\bullet}}$$

一旦 siphon 变空，外部变迁无法重新为其生成令牌。

库所集合 $Q$ 是 trap，当从 $Q$ 取令牌的每个变迁也向 $Q$ 放令牌：

$$Q^{\mathop{\bullet}}\subseteq\mathop{\bullet}Q$$

一旦 trap 含有令牌，它不会完全变空。Siphon 分析常用于发现资源耗尽导致的死锁。

## 三十六、抑制弧、读弧与重置弧

抑制弧要求某库所令牌数低于阈值：

$$M(p)\lt w$$

读弧检查令牌但不消费。重置弧将库所令牌清零。

这些扩展能简洁表达“技能未被禁用”“读取队友就绪但不消耗其状态”“死亡后清除所有临时效果”。但扩展弧会提高分析复杂度，应只在普通结构难以表达时使用。

## 三十七、Colored Petri Net

Colored Petri Net 让令牌携带类型和值：

$$\kappa=(\mathrm{hero},\mathrm{role},\mathrm{hp},\mathrm{cooldown})$$

变迁守卫依据颜色决定是否使能：

$$g_t(\kappa_1,\ldots,\kappa_m)=1$$

这样无需为每名英雄复制整套库所，但状态空间并不会自动消失；颜色展开后仍可能很大。

## 三十八、层次 Petri 网

复杂模型可把子网封装为页面或模块：

$$N=N_{\mathrm{macro}}[N_{\mathrm{skill}},N_{\mathrm{navigation}},N_{\mathrm{fight}},N_{\mathrm{safety}}]$$

替代变迁代表一个子网，入口和出口通过接口库所连接。

层次化提高可读性与复用性，但必须保证接口令牌语义一致，尤其是异常、取消和超时路径。

## 三十九、Time Petri Net

Time Petri Net 给每个变迁定义发射区间：

$$I_t=[\alpha_t,\beta_t]$$

变迁使能后至少等待 $\alpha_t$ 才能发射，并且若持续使能，最迟应在 $\beta_t$ 前发射。

若：

$$\beta_t=\infty$$

则不存在强制最晚发射时间。

时间 Petri 网适合表达确定性或区间型前摇、冷却、同步等待和超时。

## 四十、Time Petri Net 的时钟

对每个已使能变迁 $t$ 维护年龄：

$$x_t\ge0$$

可发射条件为：

$$\alpha_t\le x_t\le\beta_t$$

时间流逝必须保证所有持续使能变迁不会超过其最晚时间：

$$x_t+d\le\beta_t$$

变迁被禁用后，其年龄通常丢弃；重新使能时从零开始，除非采用持久时间语义。

## 四十一、原子语义与持久语义

在原子语义中，变迁一旦失去使能，其计时器被重置。再次使能后重新计时。

在持久语义中，某些暂停可以保留已等待时间。设暂停前年龄为 $x_t^-$，恢复后：

$$x_t^+=x_t^-$$

技能施法被硬打断通常应重置；服务器暂停、短暂控制权转移是否保留进度则由具体规则决定。

## 四十二、Timed Automata 与 Time Petri Net 的关系

有界 Time Petri Net 可以转换为时间自动机网络。每个已使能变迁对应一个时钟，标识对应离散位置。

反向转换也存在受限构造，但并非所有时间自动机结构都能自然映射为紧凑 Petri 网。

选择原则是：严格控制流程和复杂时钟守卫优先 Timed Automata；并发、资源和同步结构优先 Petri Net；两者结合时可让 Petri 网负责使能结构，时间自动机负责局部协议。

## 四十三、Stochastic Petri Net

随机 Petri 网给每个使能变迁随机发射时间。最常见模型使用指数分布：

$$T_t\sim\mathrm{Exp}(\lambda_t)$$

生存函数为：

$$\mathbb P(T_t\gt u)=e^{-\lambda_tu}$$

期望发射时间为：

$$\mathbb E[T_t]=\frac{1}{\lambda_t}$$

指数分布的无记忆性使标识过程可以映射为 CTMC。

## 四十四、竞争时钟与 Race Policy

若当前使能变迁集合为 $E(M)$，总速率为：

$$\Lambda(M)=\sum_{t\in E(M)}\lambda_t(M)$$

下一次事件等待时间为：

$$\Delta\tau\sim\mathrm{Exp}(\Lambda(M))$$

变迁 $t$ 最先发射的概率为：

$$\mathbb P(t\ \mathrm{fires\ next}\mid M)=\frac{\lambda_t(M)}{\Lambda(M)}$$

这就是竞争时钟语义。

## 四十五、标识相关发射率

发射率可以依赖当前标识：

$$\lambda_t=\lambda_t(M)$$

例如越多人集火，目标死亡事件速率越高；敌方控制越多，撤退成功事件速率越低。

多服务器语义可写为：

$$\lambda_t(M)=e_t(M)\lambda_t^0$$

$e_t(M)$ 是当前可并行启动的实例数。

## 四十六、从随机 Petri 网到 CTMC

每个可达标识对应 CTMC 状态。若变迁 $t$ 把 $M_i$ 变为 $M_j$，生成矩阵非对角元素为：

$$q_{ij}=\sum_{t:M_i\xrightarrow{t}M_j}\lambda_t(M_i)$$

对角元素为：

$$q_{ii}=-\sum_{j\neq i}q_{ij}$$

生成矩阵满足：

$$Q\mathbf 1=0$$

概率行向量 $p(t)$ 满足 Kolmogorov 前向方程：

$$\frac{dp(t)}{dt}=p(t)Q$$

## 四十七、瞬态概率

给定初始分布 $p(0)$：

$$p(t)=p(0)e^{Qt}$$

瞬态分析可回答：“未来三秒内处于控制链完成状态的概率是多少”“五秒内撤退成功的概率是多少”“团战同步等待超过阈值的概率是多少”。

对于大状态空间，可以使用 uniformization、Krylov 方法或统计模型检测近似。

## 四十八、稳态分布

稳态分布 $\pi$ 满足：

$$\pi Q=0$$

$$\sum_i\pi_i=1$$

长期处于状态集合 $B$ 的比例为：

$$\pi(B)=\sum_{i\in B}\pi_i$$

MOBA 单局是明显非平稳过程，因此稳态分析只适合局部重复子系统或固定阶段，不能把整局比赛强行视为稳态。

## 四十九、随机奖励

为标识 $M$ 定义状态奖励率：

$$r(M)$$

有限时域累计期望奖励为：

$$J(T)=\mathbb E\left[\int_0^T r(M_t)dt+\sum_{k:\tau_k\le T}r_{t_k}^{\mathrm{jump}}\right]$$

稳态奖励为：

$$J_{\infty}=\sum_M\pi(M)r(M)$$

奖励可以表示伤害、危险暴露、控制覆盖、等待成本、资源消耗和任务收益。

## 五十、GSPN

Generalized Stochastic Petri Net，简称 GSPN，同时包含：

- Immediate Transition：零时间立即变迁。
- Timed Transition：指数分布定时变迁。

若立即变迁使能，定时变迁不能发射。多个立即变迁通过权重选择：

$$\mathbb P(t\mid M)=\frac{w_t}{\sum_{u\in I(M)}w_u}$$

含立即变迁的标识称为 vanishing marking；只含定时竞争的标识称为 tangible marking。

## 五十一、消除瞬时状态

构建 CTMC 前，需要消除 vanishing marking。设瞬时子链转移矩阵为 $P_{vv}$，从瞬时到稳定标识为 $P_{vt}$。

吸收到稳定标识的概率为：

$$B=(I-P_{vv})^{-1}P_{vt}$$

如果 $I-P_{vv}$ 不可逆，可能存在立即变迁构成的零时间循环，需要修正模型。

## 五十二、非指数随机时间

技能前摇、网络延迟和人类反应时间未必服从指数分布。一般分布可写为：

$$T_t\sim F_t$$

此时无记忆性通常不成立：

$$\mathbb P(T_t\gt s+u\mid T_t\gt s)\neq\mathbb P(T_t\gt u)$$

模型可能成为 GSMP、半 Markov 过程或补充年龄变量后的扩展状态过程。为方便求解而强行使用指数分布会扭曲尾部和超时概率。

## 五十三、相位型分布

相位型分布用有限 CTMC 的吸收时间逼近一般正值分布：

$$T\sim\mathrm{PH}(\alpha,S)$$

生存函数为：

$$\mathbb P(T\gt t)=\alpha e^{St}\mathbf 1$$

它可以逼近 Erlang、超指数和多峰延迟，同时保留 Markov 分析结构，但会增加状态数量。

## 五十四、随机技能命中示例

设施法完成后，命中概率为 $p_h$。用两个立即变迁表达：

$$\mathbb P(t_{\mathrm{hit}})=p_h$$

$$\mathbb P(t_{\mathrm{miss}})=1-p_h$$

命中后生成控制令牌，未命中则进入重规划。冷却恢复可由速率 $\lambda_{\mathrm{cd}}$ 的定时变迁表达。

若冷却是确定秒数，应使用 Time Petri Net 或确定性延迟，而不是指数近似。

## 五十五、团战同步随机模型

第 $i$ 名英雄到位时间为：

$$T_i\sim F_i$$

全员到位时间为：

$$T_{\max}=\max_iT_i$$

若相互独立：

$$\mathbb P(T_{\max}\le t)=\prod_iF_i(t)$$

实际到位时间受共享道路、敌方阻挡和共同决策影响，通常不独立。随机 Petri 网可以通过共享库所和共同变迁表示相关性。

## 五十六、塔仇恨并发模型

库所可表示塔空闲、当前目标、攻击节拍和目标脱离。英雄攻击敌方英雄触发仇恨切换变迁。

塔攻击间隔可设为确定时间区间：

$$T_{\mathrm{shot}}\in[\tau_{\min},\tau_{\max}]$$

也可根据实测抖动拟合随机分布。越塔安全性质可写为：

$$\mathbb P(\Diamond^{\le T}\mathrm{Death})\le\delta$$

模型必须区分规则确定性与数据不确定性，不能把固定服务器机制误当随机过程。

## 五十七、死锁检测组合

时间自动机检测“超时仍未响应”：

$$x\ge\tau_{\mathrm{wait}}\wedge\neg\mathrm{Response}$$

Petri 网检测“所有变迁均未使能”：

$$\mathrm{Enabled}(M)=\varnothing$$

随机 Petri 网检测“虽有出口但期望等待过长”：

$$\mathbb E[T_{\mathrm{exit}}\mid M]\ge\tau_{\max}$$

三者分别识别时间违约、结构死锁和性能性软死锁。

## 五十八、活锁检测组合

Petri 网 T 不变量给出结构循环候选：

$$Cx=0$$

时间自动机检查循环是否时间发散：

$$\sum_kd_k=\infty$$

随机模型估计逃逸概率：

$$p_{\mathrm{exit}}(C)\le\epsilon$$

若循环不产生任务进度、时间持续流逝且逃逸概率很小，就可以判定实际活锁。

## 五十九、TCTL 性质

时间计算树逻辑可表达存在或所有路径上的时间性质。安全性示例：

$$A\Box\neg\mathrm{Deadlock}$$

存在快速完成路径：

$$E\Diamond^{\le T}\mathrm{ObjectiveDone}$$

所有路径都及时撤退：

$$A\Diamond^{\le T}\mathrm{SafeZone}$$

存在路径与所有路径的区别对应“有一种操作能成功”和“无论环境如何都能保证成功”。

## 六十、CSL 性质

对 CTMC，可用 Continuous Stochastic Logic 表达概率与时间。有限时域到达性质为：

$$\mathbb P_{\ge p_0}(\Diamond^{\le T}F)$$

有限时域安全性质为：

$$\mathbb P_{\ge1-\delta}(\Box^{\le T}\neg U)$$

稳态性质为：

$$\mathbb S_{\le\eta}(\mathrm{Deadlock})$$

实际使用前必须确认过程满足 CTMC 假设，尤其是指数等待和当前状态充分性。

## 六十一、统计模型检测

当精确状态空间过大时，可独立仿真 $N$ 条轨迹。性质满足指示变量为 $Y_i$：

$$Y_i\in\{0,1\}$$

概率估计为：

$$\widehat p=\frac{1}{N}\sum_{i=1}^{N}Y_i$$

Hoeffding 界给出：

$$\mathbb P(\lvert\widehat p-p\rvert\ge\epsilon)\le2e^{-2N\epsilon^2}$$

因此样本数可取：

$$N\ge\frac{\log(2/\alpha)}{2\epsilon^2}$$

## 六十二、Gillespie 仿真

对指数竞争变迁，总速率为 $\Lambda(M)$。生成均匀随机数 $u_1,u_2$：

$$\Delta\tau=-\frac{\log u_1}{\Lambda(M)}$$

选择最小索引 $j$ 满足：

$$\sum_{k=1}^{j}\lambda_k(M)\ge u_2\Lambda(M)$$

然后发射变迁 $j$。每次仿真应记录随机种子、参数版本和完整事件轨迹。

## 六十三、参数估计

若变迁 $t$ 的指数等待样本为 $d_1,\ldots,d_n$，极大似然估计为：

$$\widehat\lambda_t=\frac{n}{\sum_{i=1}^{n}d_i}$$

若存在右删失，总暴露时间为 $E_t$，观测发射次数为 $N_t$：

$$\widehat\lambda_t=\frac{N_t}{E_t}$$

拟合后应检查生存曲线和危险率；如果危险率明显随时间变化，应改用相位型或半 Markov 模型。

## 六十四、从回放构建模型

回放事件先映射为：

$$e_k=(t_k,\mathrm{actor}_k,\mathrm{type}_k,\mathrm{resource}_k,\mathrm{state}_k)$$

因果关系可由时间、资源读写和规则约束推断。若两个事件共享写资源，则不能默认独立：

$$W(e_i)\cap W(e_j)\neq\varnothing$$

构建后需要把未观测边分成“规则禁止”和“数据不足”，不能把零计数直接解释为不可能。

## 六十五、偏序约简

若动作 $a$ 与 $b$ 独立：

$$a\mathrel{I}b$$

则只需探索一个代表顺序。独立性通常要求：

$$W(a)\cap(R(b)\cup W(b))=\varnothing$$

$$W(b)\cap(R(a)\cup W(a))=\varnothing$$

偏序约简能够大幅减少并发交错，但错误声明独立会漏掉真实竞争和死锁。

## 六十六、对称约简

若多个单位在模型中行为完全对称，可按置换群 $G$ 合并状态：

$$s\sim s'\iff\exists g\in G,\quad g(s)=s'$$

使用代表元：

$$[s]=\{g(s)\mid g\in G\}$$

兵线单位、同类召唤物和等价任务工作者适合对称约简；英雄技能与角色差异通常会破坏完全对称。

## 六十七、抽象与细化

抽象映射为：

$$\alpha:S\rightarrow\widehat S$$

若抽象模型发现反例，需要判断是否存在对应具体轨迹。伪反例出现时，细分相关状态或时钟区间：

$$\widehat S_{k+1}=\mathrm{Refine}(\widehat S_k,\rho_{\mathrm{spurious}})$$

这种 CEGAR 流程适合逐步解决状态爆炸，而不是一开始把所有连续数值离散得极细。

## 六十八、三类模型如何选择

Timed Automata 适合：

- 严格时间窗、超时和最坏响应时间。
- 控制协议、握手、抢占和同步。
- 时钟之间的差分约束。

Petri Net 适合：

- 并发、资源、令牌守恒与结构死锁。
- 多模块协同、共享控制权和条件汇合。
- 因果关系与偏序。

Stochastic Petri Net 适合：

- 随机延迟、失败、竞争与性能概率。
- 等待时间、吞吐、稳态和有限时域风险。
- 大量重复仿真和概率模型检测。

## 六十九、混合建模方案

推荐分层模型：

$$\mathcal M=\mathcal N_{\mathrm{PN}}\otimes\mathcal A_{\mathrm{TA}}\otimes\mathcal P_{\mathrm{stoch}}$$

Petri 网决定资源和并发使能，时间自动机约束关键协议与硬时限，随机层描述命中、延迟、敌方响应和非确定结果。

不能直接求解完整乘积时，可按接口变量协同：

$$z_{k+1}=F_{\mathrm{PN}}(z_k,e_k)$$

$$e_k=F_{\mathrm{TA}}(q_k,\nu_k)$$

$$\xi_k\sim P_{\theta}(\cdot\mid z_k,q_k)$$

## 七十、运行时监视器

离线模型验证结构，在线监视器检查实际轨迹。运行时状态可写为：

$$m_t=(M_t,\ell_t,\nu_t,\widehat p_t)$$

监视器输出：

$$D_t=(\mathrm{deadlock},\mathrm{timeout},\mathrm{livelock},\mathrm{risk})$$

在线检测必须使用最终生效动作、真实碰撞和真实服务器事件，不能只观察规划器的候选动作。

## 七十一、工程日志

每个并发事件应记录：

- 单调时间戳与帧号。
- 组件、线程或行为节点。
- 读写资源和令牌变化。
- 使能、禁用、开始、完成、取消与超时。
- 时钟守卫与不变量判定。
- 随机分支概率、样本和随机种子。
- 控制权拥有者与最终生效动作。

事件日志为：

$$e_k=(t_k,c_k,\tau_k,R_k,W_k,M_k,\nu_k,o_k)$$

这些字段足以重建多数等待图、Petri 标识和时间自动机轨迹。

## 七十二、测试策略

至少验证：

1. 技能冷却到期前绝不能再次施法。
2. 施法被打断后按规则进入正确冷却。
3. 团队同步缺一人时能按时超时降级。
4. 控制权令牌始终守恒且唯一。
5. 两模块互等时能够检测结构死锁。
6. 零时间内部动作不存在无限循环。
7. 塔下行为在风险阈值前触发撤退。
8. 随机命中率与配置概率在置信区间内一致。
9. CTMC 概率与 Monte Carlo 结果在误差范围内一致。
10. 正常等待、埋伏与冷却不会被误判为死锁。

## 七十三、验证指标

死锁检测精确率为：

$$\mathrm{Precision}_D=\frac{N_{\mathrm{TP}}}{N_{\mathrm{TP}}+N_{\mathrm{FP}}}$$

召回率为：

$$\mathrm{Recall}_D=\frac{N_{\mathrm{TP}}}{N_{\mathrm{TP}}+N_{\mathrm{FN}}}$$

平均检测延迟为：

$$\bar T_D=\frac{1}{N}\sum_{i=1}^{N}(t_i^{\mathrm{detect}}-t_i^{\mathrm{start}})$$

概率校准可使用 Brier 分数：

$$\mathrm{BS}=\frac{1}{N}\sum_{i=1}^{N}(\widehat p_i-y_i)^2$$

## 七十四、常见建模错误

1. 把并发事件强行写成固定顺序，丢失竞争和同步。
2. 把所有等待时间设为指数分布，只为方便求解。
3. 忽略 Zeno 循环，得到物理上不可能的无限动作轨迹。
4. 把正常终止标识误报为 Petri 网死锁。
5. 忘记超时和取消边，使等待状态永久存在。
6. 使用共享变量却没有记录原子性和写入冲突。
7. 把存在成功路径误解为所有敌方响应下都能成功。
8. 只验证模型，不核对运行时代码与模型的一致性。
9. 参数更新后不重新验证时间窗和概率性质。

## 七十五、MOBA 最小可行落地

第一阶段只建三个子模型：

1. 技能时间自动机：Ready、Casting、Cooldown、Interrupted。
2. 控制权 Petri 网：Strategy、Fight、Navigation、Safety 竞争唯一令牌。
3. 团战同步随机 Petri 网：队友到位、开团、超时、撤退和失败分支。

先验证四条性质：

$$A\Box\neg\mathrm{DoubleCast}$$

$$A\Box\neg\mathrm{LostControlToken}$$

$$A\Diamond^{\le T}\mathrm{SyncOrAbort}$$

$$\mathbb P_{\le\delta}(\Diamond^{\le T}\mathrm{UnsafeDive})$$

这三个模型已经能够覆盖技能非法重复、模块互锁、全队互等和高风险越塔等高价值问题。

## 七十六、结论

Timed Automata、Petri Net 和 Stochastic Petri Net 分别提供三种互补视角。时间自动机回答“是否在规定时间内发生”，Petri 网回答“哪些事件能并发、同步或因资源而阻塞”，随机 Petri 网回答“等待多久、以多大概率成功或失败”。

在 MOBA 中，技能冷却和控制链适合时间自动机，控制权、团队同步和资源守恒适合 Petri 网，随机命中、网络时延、敌方响应和等待性能适合随机 Petri 网。死锁检测应结合结构无使能、超时未响应和随机出口等待，而活锁检测应结合 T 不变量、时间发散、任务进度与逃逸概率。

工程上应先建小而可验证的子模型，再通过同步通道、接口令牌和事件日志连接。不要一开始构造十名英雄、全部技能和完整地图的巨大乘积。每个模型都必须对应运行时可观测字段、可执行恢复动作和版本化参数，才能从数学描述变成真正可调试、可回放和可持续维护的并发控制系统。
