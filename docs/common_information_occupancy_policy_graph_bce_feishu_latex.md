# Common-Information、Occupancy-State、Dec-POMDP Policy Graph 与 Bayesian Correlated Equilibrium

## 摘要

多智能体部分可观测决策的困难不只是“看不见真实状态”，还包括每个智能体拥有不同信息、无法直接观察队友的观察，以及策略本身会改变未来信息分布。

Common-information approach（公共信息方法）把共享历史交给一个虚拟协调者，由协调者为各智能体选择依赖私人信息的 prescription；Occupancy-state game（占用状态博弈）把真实状态与私人历史的联合分布作为规划状态；Dec-POMDP policy graph（策略图）把长历史压缩成有限控制器节点；Bayesian correlated equilibrium（贝叶斯相关均衡）则用服从约束描述具有私人类型的智能体为何愿意遵守相关建议。

四者可以形成一条完整链路：公共信息定义合法协调边界，占用状态提供动态充分统计，策略图提供可部署的有限记忆实现，贝叶斯相关均衡负责审计推荐是否激励相容。

## 一、多智能体部分可观测模型

考虑 $n$ 个智能体。环境状态为：

$$X_t\in\mathcal X$$

联合动作为：

$$A_t=(A_t^1,\ldots,A_t^n)\in\mathcal A_1\times\cdots\times\mathcal A_n$$

状态转移为：

$$P(x'\mid x,a)=\Pr(X_{t+1}=x'\mid X_t=x,A_t=a)$$

智能体 $i$ 获得局部观察：

$$O_{t+1}^i\sim Z_i(\cdot\mid X_{t+1},A_t)$$

联合即时收益为团队共享收益或玩家特定收益：

$$r_i(x,a)$$

若所有智能体共享同一收益，就是 Dec-POMDP；若收益不同，则属于一般和 POSG 或其他动态贝叶斯博弈。

智能体 $i$ 的策略只能依赖自身可用信息：

$$\pi_t^i(a_i\mid I_t^i)$$

不能在算法里悄悄使用该智能体本来无法看到的敌方状态、队友私有观察或未来事件。

## 二、信息结构：公共信息与私人信息

把智能体 $i$ 在时刻 $t$ 的信息分解为：

$$I_t^i=(C_t,P_t^i)$$

其中：

- $C_t$ 是所有智能体都知道、并且知道其他人也知道的公共信息；
- $P_t^i$ 是只有智能体 $i$ 掌握的私人信息。

公共信息可以包括共享地图视野、全队播报、公共计时器、已经广播的信号和共同动作历史。私人信息可以包括局部观察、未广播的意图、本地估计或个体类型。

关键要求不是“数据在服务器上可获得”，而是“执行策略的智能体是否被允许使用”。服务器内部知道隐藏状态，并不意味着它可以被当作玩家公共信息。

## 三、Common-Information Approach

公共信息方法引入一个虚拟的 common agent，也称 coordinator。协调者只观察公共信息 $C_t$，不直接观察各智能体的私人信息。

协调者在每个时刻选择一组 prescription：

$$\Gamma_t=(\Gamma_t^1,\ldots,\Gamma_t^n)$$

其中：

$$\Gamma_t^i:\mathcal P_t^i\rightarrow\Delta(\mathcal A_i)$$

智能体 $i$ 收到 prescription 后，把自己的私人信息代入：

$$A_t^i\sim\Gamma_t^i(\cdot\mid P_t^i)$$

因此协调者不需要知道 $P_t^i$ 的真实值，只需要决定“每种可能私人信息应如何行动”。

### 1. 公共信念

协调者的状态通常是公共信念：

$$\Pi_t(x,p^1,\ldots,p^n)=\Pr(X_t=x,P_t^1=p^1,\ldots,P_t^n=p^n\mid C_t)$$

它是环境状态与所有私人信息的条件联合分布。

### 2. 公共信息增量

设下一时刻新增的公共信息为：

$$Z_{t+1}^{\mathrm c}=C_{t+1}\setminus C_t$$

则公共信念可以写成受 prescription 控制的贝叶斯更新：

$$\Pi_{t+1}=\Phi_t(\Pi_t,\Gamma_t,Z_{t+1}^{\mathrm c})$$

映射 $\Phi_t$ 由状态转移、观察模型、私人记忆更新和公共信号机制共同决定。

### 3. 协调者动态规划

对于团队共享收益，有限时域 Bellman 递推可以写为：

$$V_t(\pi)=\max_{\gamma}\left\{\bar r_t(\pi,\gamma)+\mathbb E\left[V_{t+1}(\Phi_t(\pi,\gamma,Z_{t+1}^{\mathrm c}))\right]\right\}$$

其中：

$$\bar r_t(\pi,\gamma)=\mathbb E[r(X_t,A_t)\mid\Pi_t=\pi,\Gamma_t=\gamma]$$

这个转换把分散决策改写成协调者面对的 belief-state 控制问题，但动作不再是普通动作，而是函数空间中的 prescriptions。

### 4. 方法价值

- 明确区分公共信息与私人信息；
- 避免中心化训练时的信息泄漏到分散执行；
- 把动态团队问题转化为公共信念上的规划；
- 为动态机制设计和相关建议提供合法的信息基础。

### 5. 主要限制

prescription 的数量随私人信息空间指数增长，公共信念维度也可能极大。公共信息方法提供的是结构化等价表示，不自动解决维数灾难。

## 四、策略依赖信念问题

在分散控制中，观察到的公共历史对私人状态的含义可能依赖过去策略。相同的公共事件，在不同 prescription 下可以对应不同后验。

公共信念的更新必须显式条件于已选 prescription：

$$\Pr(X_{t+1},P_{t+1}\mid C_{t+1},\Gamma_{0:t})$$

若更新器忽略策略对动作和信号分布的影响，就会产生 signaling bias：模型把由策略选择导致的观察差异错误解释成环境状态差异。

在某些信息结构下，可以构造 strategy-independent belief；但这需要专门条件，不能默认成立。

## 五、Occupancy State

Occupancy state 把状态和信息历史的概率质量统一记录。对于有限时域 Dec-POMDP，可令智能体 $i$ 的动作–观察历史为：

$$\theta_t^i=(o_0^i,a_0^i,o_1^i,\ldots,a_{t-1}^i,o_t^i)$$

联合历史为：

$$\theta_t=(\theta_t^1,\ldots,\theta_t^n)$$

计划时 occupancy state 定义为：

$$\eta_t(x,\theta_t)=\Pr(X_t=x,\Theta_t=\theta_t\mid\delta_{0:t-1})$$

其中 $\delta_{0:t-1}$ 是此前采用的联合 decision rules。

它不是单局运行时某个玩家直接观察到的变量，而是规划器对所有可能真实状态和联合私人历史的概率分布。

## 六、Occupancy-State Transition

时刻 $t$ 的联合 decision rule 为：

$$\delta_t(a\mid\theta_t)=\prod_{i=1}^n\delta_t^i(a_i\mid\theta_t^i)$$

给定 occupancy state 和 decision rule，下一 occupancy state 由模型确定：

$$\eta_{t+1}=T_t(\eta_t,\delta_t)$$

展开后可写为：

$$\eta_{t+1}(x',\theta_{t+1})=\sum_{x,\theta_t,a}\eta_t(x,\theta_t)\delta_t(a\mid\theta_t)P(x'\mid x,a)Z(o_{t+1}\mid x',a)$$

这里 $\theta_{t+1}$ 必须与 $\theta_t$、$a$ 和新观察 $o_{t+1}$ 一致，不一致的项概率为零。

### 1. Occupancy reward

给定 $\eta$ 与联合 decision rule $\delta$，期望即时收益为：

$$R(\eta,\delta)=\sum_{x,\theta,a}\eta(x,\theta)\delta(a\mid\theta)r(x,a)$$

### 2. Occupancy Bellman equation

团队问题可写为：

$$V_t(\eta)=\max_{\delta_t}\left\{R(\eta,\delta_t)+\gamma V_{t+1}(T_t(\eta,\delta_t))\right\}$$

occupancy transition 对给定模型和 decision rule 是确定的，因此 Dec-POMDP 可以在连续 occupancy 空间上改写为确定性控制问题。

## 七、Occupancy-State Game

当玩家收益不同，occupancy state 不再只对应单个控制者的价值最大化，而会形成 occupancy-state game。

公共 occupancy 可以定义为：

$$\eta_t(x,p^1,\ldots,p^n)=\Pr(X_t=x,P_t^1=p^1,\ldots,P_t^n=p^n\mid C_t)$$

每个玩家或协调机制选择 prescription，收益和下一 occupancy 由：

$$r_i(\eta,\gamma)=\mathbb E[r_i(X,A)\mid\eta,\gamma]$$

以及：

$$\eta'=T(\eta,\gamma,z^{\mathrm c})$$

共同决定。

在零和 POSG 中，可以在 occupancy 空间定义 min–max Bellman 或 Shapley 算子；在一般和 POSG 中，需要定义 occupancy-state Markov equilibrium、相关建议或其他均衡概念。

### 主要难点

- occupancy 维度随联合历史指数增长；
- 可达 occupancy 集是高维连续集合；
- 一般和情形可能有多均衡和分支选择；
- 信息结构变化会改变 occupancy 的定义；
- 用神经网络近似 occupancy 时必须保留归一化和信息可实现性。

## 八、Common Belief 与 Occupancy State 的区别

| 对象 | 条件信息 | 主要用途 | 执行时是否直接可见 |
|---|---|---|---|
| 局部 belief | 单个智能体历史 | 个体 POMDP 决策 | 由个体估计 |
| common belief | 公共历史 | 协调者 prescription 规划 | 可由共享更新器维护 |
| plan-time occupancy | 已选联合决策规则 | 离线 Dec-POMDP 动态规划 | 通常不是玩家观察量 |
| occupancy-state game | 公共历史或规划历史 | POSG 动态均衡 | 取决于信息结构 |

二者经常形式相似，但条件事件和用途不同。实现时必须在数据结构中记录 conditioning set，不能只存一个未注明语义的概率张量。

## 九、Dec-POMDP Policy Graph

完整历史策略树随时域指数增长。Policy graph，也称 finite-state controller，用有限节点压缩历史。

对智能体 $i$，定义有限节点集合：

$$Q_i=\{1,\ldots,m_i\}$$

节点可以表示“搜索敌方”“准备开团”“撤退冷却”“控制地图目标”等内部记忆模式。

### 1. 动作选择

在节点 $q_i$ 上，动作分布为：

$$\psi_i(a_i\mid q_i)$$

确定性 policy graph 是其特殊情形：每个节点只选择一个动作。

### 2. 节点转移

执行动作并获得新观察后，节点转移为：

$$\tau_i(q_i'\mid q_i,a_i,o_i')$$

若节点转移是确定的，则 $\tau_i$ 在每个输入上只有一个输出节点概率为一。

### 3. 初始节点

初始节点分布为：

$$\rho_i(q_i)$$

完整有限状态控制器写成：

$$\mathcal C_i=(Q_i,\rho_i,\psi_i,\tau_i)$$

## 十、联合 Policy Graph 的价值评估

令联合节点为：

$$q=(q_1,\ldots,q_n)$$

状态–节点对 $(x,q)$ 构成扩展 Markov 链。折扣价值满足：

$$V(x,q)=\bar r(x,q)+\gamma\sum_{x',q'}\bar P(x',q'\mid x,q)V(x',q')$$

联合节点下的期望收益为：

$$\bar r(x,q)=\sum_a\left[\prod_i\psi_i(a_i\mid q_i)\right]r(x,a)$$

扩展转移核为：

$$\bar P(x',q'\mid x,q)=\sum_{a,o'}\left[\prod_i\psi_i(a_i\mid q_i)\tau_i(q_i'\mid q_i,a_i,o_i')\right]P(x'\mid x,a)Z(o'\mid x',a)$$

因此固定 policy graph 的价值可以通过线性方程求解：

$$V=(I-\gamma\bar P)^{-1}\bar r$$

只有在 $\gamma<1$ 或相应随机最短路条件成立时，这个无限时域表达才有良好定义。

## 十一、Policy Graph 的构造方法

### 1. 有限时域分层图

每一层对应一个剩余时域，边按照观察连接下一层节点。它等价于压缩后的策略树，适合短时域精确或近似规划。

### 2. 有限状态控制器搜索

固定节点数后，可交替优化动作分布与节点转移，也可以使用 nonlinear programming、MILP、policy iteration 或梯度方法。

### 3. 节点扩展与合并

若某些观察历史需要不同响应，可拆分节点；若两个节点产生近似相同的动作和未来价值，可合并节点。

### 4. Bounded Policy Iteration

在固定控制器规模下改进局部节点，并用线性规划或优势证书判断是否存在改进。固定节点数会限制最优性，但能控制部署内存与延迟。

## 十二、Policy Graph 的工程价值与风险

### 价值

- 把无限或指数历史压缩成有限记忆；
- 可直接部署为事件驱动状态机；
- 节点含义可以解释和调试；
- 可限制运行时内存与决策耗时；
- 可以与行为树、战术阶段机和技能状态机连接。

### 风险

- 节点太少会产生记忆混叠；
- 节点标签不等于真实隐状态；
- 离线最优节点转移可能在分布漂移下失效；
- 随机控制器的复现需要保存随机种子；
- 策略图不能绕过底层动作合法性。

## 十三、Bayesian Game

静态贝叶斯博弈中，玩家 $i$ 有私人类型：

$$\Theta_i\in\mathcal T_i$$

联合类型为：

$$\theta=(\theta_1,\ldots,\theta_n)$$

共同先验为：

$$p(\theta)$$

玩家 $i$ 知道自己的类型 $\theta_i$，但不一定知道其他玩家的类型。收益为：

$$u_i(a,\theta)$$

类型可以表示角色、目标偏好、局部观察摘要、风险容忍度、技能状态类别或对手行为模式。

## 十四、Bayesian Correlated Equilibrium

Bayesian correlated equilibrium（BCE）用联合分布描述类型与行动建议：

$$\mu(\theta,a)$$

它需要满足两个核心条件：Bayes plausibility 和 obedience。

### 1. Bayes plausibility

类型边缘分布必须等于给定先验：

$$\sum_a\mu(\theta,a)=p(\theta),\qquad \forall\theta$$

还需要：

$$\mu(\theta,a)\geq 0$$

以及：

$$\sum_{\theta,a}\mu(\theta,a)=1$$

### 2. Obedience constraints

对每个玩家 $i$、类型 $\theta_i$、被推荐动作 $a_i$ 和偏离动作 $a_i'$，要求：

$$\sum_{\theta_{-i},a_{-i}}\mu(\theta_i,\theta_{-i},a_i,a_{-i})\left[u_i(a_i,a_{-i},\theta)-u_i(a_i',a_{-i},\theta)\right]\geq 0$$

这意味着在知道自己的类型并收到动作建议后，玩家没有动力单方面偏离。

如果某个类型–建议事件概率为零，相应约束自然为零，不应从零概率事件推导行为结论。

## 十五、BCE 线性规划

在有限类型和有限动作下，BCE 集由线性等式与不等式定义，是一个凸多面体。

若设计目标是最大化加权社会福利：

$$W(\mu)=\sum_{\theta,a}\mu(\theta,a)\sum_i w_i u_i(a,\theta)$$

则可以求解线性规划：

$$\max_{\mu}W(\mu)$$

约束包括：

- Bayes plausibility；
- obedience；
- 非负性；
- 可选的安全、公平、预算和容量约束。

线性规划返回的是满足指定信息与服从条件的最优结果分布，不一定给出唯一机制。要部署还需要实现能够生成该联合分布的合法信号或推荐机制。

## 十六、BCE、CE 与 Bayes–Nash 的区别

| 概念 | 私人类型 | 相关建议 | 主要约束 |
|---|---|---|---|
| Nash equilibrium | 否或视为固定 | 否 | 对固定他方策略最佳响应 |
| Correlated equilibrium | 否 | 是 | 收到建议后不愿偏离 |
| Bayes–Nash equilibrium | 是 | 条件独立策略 | 每个类型下最佳响应 |
| Bayesian correlated equilibrium | 是 | 是 | Bayes plausibility 与类型条件服从 |

Bayes–Nash 可以嵌入 BCE，但 BCE 允许由信号机制产生额外相关性，因此结果集合通常更大。

BCE 也不等于“协调器知道真实状态后随意下命令”。协调器能使用哪些类型或信号，取决于合法信息结构。若推荐机制使用了执行者无法获得、且机制本身也无权观察的信息，所谓 obedience 没有可实现意义。

## 十七、动态 BCE 与公共信息

在动态游戏中，可以把每个公共历史上的推荐机制写成：

$$\sigma_t(a_t\mid C_t,P_t)$$

但动态激励相容不仅要求当前不偏离，还要考虑偏离对未来信念、信号和收益的影响。

一个动态服从约束通常比较“遵守当前建议并继续遵守”与“当前偏离后采用允许的后续策略”的条件价值：

$$V_i^{\mathrm{obey}}(I_t^i,a_t^i)\geq V_i^{\mathrm{dev}}(I_t^i,a_t^i\rightarrow\hat a_t^i)$$

逐阶段静态 BCE 约束通常不足以证明动态激励相容。动态模型需要明确偏离可观察性、未来推荐规则、完美回忆和承诺能力。

## 十八、四个方法如何组合

### 第一步：定义信息边界

把每个智能体的信息拆成：

$$I_t^i=(C_t,P_t^i)$$

明确哪些信号可以共享、何时共享、共享是否有延迟，以及协调器有权看到什么。

### 第二步：维护公共信念或 occupancy

根据公共历史和 prescription 更新：

$$\Pi_{t+1}=\Phi_t(\Pi_t,\Gamma_t,Z_{t+1}^{\mathrm c})$$

离线规划器可维护更完整的 occupancy state，用于评估所有可能私人历史的概率质量。

### 第三步：求解 prescription 或 decision rule

在公共信念或 occupancy 状态上求高层联合规则：

$$\Gamma_t^i:P_t^i\rightarrow\Delta(\mathcal A_i)$$

### 第四步：压缩为 policy graph

把历史依赖规则压缩成有限节点、动作分布和观察驱动节点转移：

$$\mathcal C_i=(Q_i,\rho_i,\psi_i,\tau_i)$$

### 第五步：检查 BCE obedience

若智能体收益不同，或者建议可能与个体目标冲突，应计算所有类型–建议–偏离组合的服从余量：

$$m_{i,\theta_i,a_i,a_i'}=\sum_{\theta_{-i},a_{-i}}\mu(\theta,a)\left[u_i(a,\theta)-u_i(a_i',a_{-i},\theta)\right]$$

只有当：

$$m_{i,\theta_i,a_i,a_i'}\geq 0$$

对全部相关组合成立时，才满足静态 BCE 服从要求。

## 十九、5v5 战争迷雾示例

### 1. 公共信息

- 已共享的敌方位置；
- 防御塔、龙和兵线等公共地图状态；
- 全队可见的击杀与资源计时器；
- 已广播的开团、撤退与集火信号；
- 所有人都能确认的技能事件。

### 2. 私人信息

- 某英雄局部视野中的短暂敌方动作；
- 未广播的路线意图；
- 本地对对手类型的估计；
- 只在本地模型中维护的置信度；
- 通信延迟造成的暂时信息差。

### 3. Common-information coordinator

协调者根据公共信念输出 prescriptions，例如：

- 若打野私有观察确认敌方核心位远离，则尝试开龙；
- 若辅助私有观察发现伏击，则转为撤退和保护；
- 若两条私人证据互相矛盾，则先侦察而非强制开团。

### 4. Occupancy state

occupancy 同时保留真实敌方位置、各英雄私人观察历史和当前策略图节点的概率质量，用于离线比较“立即开团”“继续侦察”和“换资源”的期望长期收益。

### 5. Policy graph

可设计有限节点：

- 搜索；
- 集结；
- 试探；
- 开团；
- 追击；
- 撤退；
- 重置。

观察和公共信号驱动节点转移，底层控制器再把高层动作翻译成合法移动、技能与目标选择。

### 6. BCE 推荐

若不同角色有不同局部目标，可让相关装置推荐“坦克先手、输出等待、辅助封路”。服从约束检查每种角色类型收到建议后，是否更愿意私自抢资源、提前追击或拒绝承担风险。

## 二十、求解与近似方法

### 1. 精确动态规划

短时域、小状态、小观察问题可以在 occupancy 空间做动态规划或枚举 prescriptions。复杂度通常随玩家数、历史长度和观察数快速增长。

### 2. Point-based occupancy planning

只在回放和仿真中可达的 occupancy 点上备份价值，类似 POMDP 的 PBVI。它降低计算量，但不提供全 occupancy 空间的精确保证。

### 3. Monte Carlo tree search

使用粒子近似公共信念或 occupancy，并在 prescription 或高层联合动作上搜索。渐进扩宽可控制巨大动作和观察分支。

### 4. Policy graph optimization

固定节点预算后，使用局部搜索、梯度、MILP 或 bounded policy iteration 优化动作和节点转移。

### 5. BCE linear programming

有限类型与动作下，直接对 $\mu(\theta,a)$ 求线性规划。大规模时可使用约束生成，只加入当前最严重的偏离约束。

### 6. Function approximation

神经网络可以近似公共 belief encoder、occupancy value 或 prescription，但必须用概率归一化、信息掩码和可实现性测试防止信息泄漏。

## 二十一、验证指标

### 1. Belief calibration

按预测概率分箱，比较事件真实频率。公共信念不仅要归一化，还要在未见回放上校准。

### 2. Occupancy conservation

每一步检查：

$$\sum_{x,\theta}\eta_t(x,\theta)=1$$

以及：

$$\eta_t(x,\theta)\geq 0$$

### 3. 信息泄漏测试

遮蔽非公共特征后，协调器输出不得变化。个体策略遮蔽其他玩家私人信息后也应保持一致。

### 4. Policy graph 覆盖

记录节点访问率、节点熵、转移覆盖、死节点和观察冲突。很少访问的节点不能仅凭训练集价值保留。

### 5. BCE violation

定义最大服从违反量：

$$\varepsilon_{\mathrm{BCE}}=\max_{i,\theta_i,a_i,a_i'}\left[-m_{i,\theta_i,a_i,a_i'}\right]_+$$

精确 BCE 要求：

$$\varepsilon_{\mathrm{BCE}}=0$$

数值求解和采样估计只能声称在容差或置信区间内近似满足。

### 6. Exploitability

对每个类型训练或求解最佳偏离策略，测量遵守建议与最优偏离之间的价值差。动态问题必须允许偏离策略影响未来历史，而不只是改单步动作。

## 二十二、与现有游戏数学层的组合

推荐接入顺序：

1. P23 的 BOCPD 与 HSMM 识别版本变点和战斗阶段；
2. P24 的 POMDP、POMCPOW、DESPOT 与 I-POMDP 提供单体信念规划和对手类型模型；
3. Common-information approach 明确公共与私人信息边界；
4. occupancy-state game 把公共信念、私人历史和动态收益统一为规划状态；
5. policy graph 将求得的历史策略压缩成有限状态控制器；
6. P25 的随机博弈与 P31 类变分不等式方法求局部均衡；
7. BCE 约束检查相关建议在异质收益下是否可服从；
8. P27 施加资源与风险预算，P30 给估计结果附加置信界；
9. 所有输出仍需通过动作掩码、技能冷却、资源、碰撞、联合规划与 MAPF 检查。

## 二十三、常见误区

### 1. 把服务器信息当作公共信息

公共信息必须由信息结构定义，不能因为训练服务器能访问就默认执行者可用。

### 2. 把 occupancy 当作单个玩家 belief

occupancy 通常覆盖真实状态与所有联合私人历史，条件事件和用途都不同。

### 3. 忽略策略依赖信念

动作本身会传递信息。后验更新必须考虑生成动作的 prescription。

### 4. 把 policy graph 节点当作真实状态

节点只是有限记忆，多个隐藏状态可能映射到同一节点。

### 5. 用逐阶段 BCE 代替动态激励相容

动态偏离会改变未来信息与推荐，必须比较完整后续价值。

### 6. 只检查推荐动作的平均收益

BCE 需要对每个玩家、类型、建议和偏离动作分别检查 obedience。

### 7. 忽略零概率建议

零概率事件上的条件行为未被数据识别，不能据此声称策略稳定。

### 8. 绕过底层游戏规则

协调 prescription、occupancy 策略和 policy graph 都只是高层决策。非法动作仍应由原生执行层拒绝。

## 二十四、选择建议

若问题的核心是分散执行与信息边界，先使用 Common-information approach；它能明确协调器到底可以依赖什么。

若需要对完整联合历史分布做离线动态规划，使用 occupancy state；若玩家收益不同，则使用 occupancy-state game，并明确均衡概念。

若部署内存与实时延迟受限，使用 Dec-POMDP policy graph 将历史策略压缩为有限状态控制器，同时检查记忆混叠与节点覆盖。

若协调建议面对私人类型与异质激励，使用 Bayesian correlated equilibrium 的 Bayes plausibility 和 obedience 约束；动态环境还要补充跨期偏离分析。

四种方法不是互相替代，而是分别解决信息、状态、实现和激励四个层面的问题。

## 二十五、结论

Common-information approach 用 prescriptions 把分散策略改写为公共信念上的协调问题；occupancy state 用真实状态与联合私人历史的分布提供动态充分统计；Dec-POMDP policy graph 把指数历史压缩为可部署的有限记忆控制器；Bayesian correlated equilibrium 用 Bayes plausibility 和 obedience 保证相关建议与私人类型相容。

在 5v5 战争迷雾场景中，最重要的不是建立一个能看到一切的中央策略，而是保持信息可实现性：协调器只使用合法公共信息，个体动作只依赖自己的私人信息和收到的 prescription，策略图不偷偷编码未来事件，BCE 推荐也不能依赖机制无权观察的类型。

只有同时通过信息泄漏测试、occupancy 守恒、policy graph 覆盖、动态偏离评估和原生动作合法性检查，这套模型才能从数学规划结果转化为可信的游戏策略。
