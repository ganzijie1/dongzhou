# 5v5 MOBA 中的死锁、活锁与无谓行为检测

## 摘要

MOBA 智能体的“卡墙、绕塔转圈、发呆、反复横跳、送塔”并不是同一种故障。卡墙通常是连续控制或局部导航无法产生有效位移；绕塔常是目标吸引、危险排斥与寻路重规划形成极限环；发呆可能是真死锁，也可能是条件等待、行为树无可执行叶节点或控制权冲突；送塔则往往仍在正常执行动作，只是安全约束、目标价值或撤退逻辑失效。

因此，检测系统不能只问“英雄有没有动”，而要同时判断：动作是否可执行、状态是否取得任务进展、是否在有限状态集合内循环、是否持续暴露于危险、多个控制层是否互相覆盖，以及是否存在可行退出动作。

本文建立统一转移系统，区分死锁、活锁、振荡、饥饿、导航卡滞和策略性自毁；给出滑动窗口进度、碰撞接触、路径势能、环绕角、状态循环、强连通分量、等待图、时序逻辑和 Petri 网等检测方法，并给出运行时监视、分级恢复、回放挖掘、测试与指标体系。

## 一、问题分类

设智能体状态为 $s_t$，动作命令为 $a_t$，实际执行结果为 $y_t$，高层目标为 $g_t$。常见异常可分为：

1. 死锁：没有任何可执行动作，或者多个模块互相等待。
2. 活锁：动作持续变化，但任务进度长期为零。
3. 振荡：在少数状态、目标或动作间反复切换。
4. 饥饿：某个必要行为一直得不到执行机会。
5. 导航卡滞：持续发出移动命令，但位置几乎不变。
6. 策略性自毁：动作合法且有位移，却持续降低生存与任务价值。

这六类故障可以同时发生。例如，寻路器在墙边振荡属于导航卡滞与活锁的组合。

## 二、统一转移系统

把运行时建模为：

$$s_{t+1}=F(s_t,a_t,\xi_t)$$

其中 $\xi_t$ 包含敌方动作、碰撞、网络延迟、技能结果和环境事件。

候选动作集合为：

$$A(s_t)=\{a\mid g_a(s_t)=1\}$$

$g_a$ 是动作守卫条件。控制器选择：

$$a_t=\pi(s_t,g_t)$$

检测器观察窗口：

$$H_t=(s_{t-W+1},a_{t-W+1},\ldots,s_t,a_t)$$

并输出异常类别与置信度：

$$D(H_t)=(c_t,q_t)$$

其中 $c_t$ 是类别，$q_t\in[0,1]$ 是置信度。

## 三、死锁的形式化定义

最严格的动作死锁定义为：

$$A(s_t)=\varnothing$$

但游戏工程中更常见的是“有效动作集合为空”。设能推进当前目标的动作集合为：

$$A^+(s,g)=\{a\in A(s)\mid \Delta P(s,a,g)\gt0\}$$

若：

$$A^+(s_t,g_t)=\varnothing$$

即使仍能播放待机、转向或无效移动，也属于目标相关死锁。

持续时间超过阈值才报警：

$$T_{\mathrm{dead}}\ge\tau_{\mathrm{dead}}$$

## 四、活锁的形式化定义

活锁中动作并非停止：

$$\sum_{k=t-W+1}^{t}\lVert a_k-a_{k-1}\rVert\gt\epsilon_a$$

但任务进度不足：

$$P_t-P_{t-W}\le\epsilon_P$$

若状态反复落在有限集合 $C$ 中：

$$s_k\in C,\qquad t-W\le k\le t$$

且没有到达目标集合 $G$，则可判定候选活锁。

## 五、振荡与活锁的区别

振荡强调反复切换，活锁强调无进展。目标选择振荡可写为：

$$g_{t-2}=g_t,\qquad g_{t-1}\neq g_t$$

动作振荡可写为：

$$a_{t-2}=a_t,\qquad a_{t-1}\neq a_t$$

如果振荡同时推动任务前进，例如走位躲技能，则不应视为活锁。只有当：

$$\Delta P_W\le\epsilon_P$$

且振荡次数超过阈值时，才触发恢复。

## 六、任务进度变量

检测的关键是定义进度。对目标位置 $x_g$，距离进度可取：

$$P_t^{\mathrm{dist}}=-d(x_t,x_g)$$

对推塔任务，可取：

$$P_t^{\mathrm{tower}}=-H_t^{\mathrm{tower}}$$

对撤退任务，可取安全裕度：

$$P_t^{\mathrm{safe}}=d(x_t,\mathcal U_t)$$

其中 $\mathcal U_t$ 是危险集合。

综合进度可写为：

$$P_t=w_1P_t^{\mathrm{dist}}+w_2P_t^{\mathrm{objective}}+w_3P_t^{\mathrm{safe}}+w_4P_t^{\mathrm{team}}$$

不同任务必须使用不同进度定义，不能用“离目标更近”统一评价所有行为。

## 七、滑动窗口进度检测

位置净位移为：

$$\Delta x_W=\lVert x_t-x_{t-W}\rVert_2$$

窗口内累计路程为：

$$L_W=\sum_{k=t-W+1}^{t}\lVert x_k-x_{k-1}\rVert_2$$

目标进展为：

$$\Delta d_W=d(x_{t-W},x_g)-d(x_t,x_g)$$

卡住通常表现为 $\Delta x_W$ 和 $L_W$ 都很小；绕圈则可能有较大的 $L_W$，但 $\Delta x_W$ 与 $\Delta d_W$ 很小。

## 八、墙边卡滞检测

设移动命令强度为：

$$U_W=\sum_{k=t-W+1}^{t}\lVert u_k^{\mathrm{move}}\rVert_2$$

若同时满足：

$$U_W\ge u_{\min}$$

$$L_W\le\epsilon_x$$

$$T_{\mathrm{contact}}\ge\tau_c$$

则是强卡墙信号。$T_{\mathrm{contact}}$ 是与不可通行边界持续接触的时间。

还可计算期望速度与实际速度差：

$$e_v=\frac{1}{W}\sum_{k=t-W+1}^{t}\lVert v_k^{\mathrm{cmd}}-v_k^{\mathrm{actual}}\rVert_2$$

当 $e_v$ 长期过大时，应检查碰撞、路径点、速度控制和位移技能状态。

## 九、墙角法向冲突

设最近两面墙的外法向为 $n_1,n_2$，期望移动方向为 $u$。若：

$$u^\top n_1\lt0$$

且：

$$u^\top n_2\lt0$$

则控制器正在持续把英雄推向墙角。

墙角夹角为：

$$\phi=\arccos\left(\frac{n_1^\top n_2}{\lVert n_1\rVert\lVert n_2\rVert}\right)$$

当 $\phi$ 较小且命令方向落入不可行锥时，单纯重复原路径不会脱困，必须改变局部航点或投影控制方向。

## 十、路径点不可见与不可达

设当前路径点为 $p_j$。射线或导航可见性为：

$$\chi_{\mathrm{vis}}(x_t,p_j)\in\{0,1\}$$

若路径点持续不可见：

$$\chi_{\mathrm{vis}}(x_t,p_j)=0$$

且局部规划器仍反复追踪 $p_j$，则是路径缓存失效。

进一步检查导航图可达性：

$$x_t\leadsto p_j$$

若不可达，应立即丢弃路径，而不是等待位置误差自行消失。

## 十一、绕塔转圈的环绕角检测

设塔中心为 $c$，英雄相对向量为：

$$r_t=x_t-c$$

连续角度增量为：

$$\Delta\theta_t=\mathrm{wrap}\left(\mathrm{atan2}(r_t)-\mathrm{atan2}(r_{t-1})\right)$$

窗口累计环绕角为：

$$\Theta_W=\sum_{k=t-W+1}^{t}\Delta\theta_k$$

环绕数为：

$$N_{\mathrm{wind}}=\frac{\lvert\Theta_W\rvert}{2\pi}$$

若 $N_{\mathrm{wind}}$ 较大、半径变化很小且任务进度接近零，就可识别“绕塔转圈”。

## 十二、环形极限环的附加条件

平均半径为：

$$\bar r=\frac{1}{W}\sum_{k=t-W+1}^{t}\lVert x_k-c\rVert_2$$

半径方差为：

$$\sigma_r^2=\frac{1}{W}\sum_{k=t-W+1}^{t}(\lVert x_k-c\rVert_2-\bar r)^2$$

极限环候选条件为：

$$N_{\mathrm{wind}}\ge n_0$$

$$\sigma_r^2\le\epsilon_r$$

$$\Delta P_W\le\epsilon_P$$

还要排除正常走 A、规避技能和等待兵线等有价值行为。

## 十三、反复横跳检测

沿局部主方向 $q$ 投影位置：

$$z_t=q^\top x_t$$

速度符号翻转次数为：

$$N_{\mathrm{flip}}=\sum_{k=t-W+2}^{t}\mathbf 1_{\{\dot z_k\dot z_{k-1}\lt0\}}$$

若：

$$N_{\mathrm{flip}}\ge n_{\mathrm{flip}}$$

且净进度很小，则可能是两个势场、两个目标或两个控制器竞争造成的振荡。

## 十四、发呆检测

发呆不能仅用速度为零定义。候选条件为：

$$\lVert v_t\rVert\le\epsilon_v$$

$$\lVert a_t^{\mathrm{effective}}\rVert\le\epsilon_a$$

$$T_{\mathrm{idle}}\ge\tau_{\mathrm{idle}}$$

同时要求当前存在有价值可执行动作：

$$A^+(s_t,g_t)\neq\varnothing$$

否则在出生等待复活、合法回城、蓄力、隐蔽埋伏或等待同步窗口时可能被误报。

## 十五、合法等待白名单

定义等待谓词：

$$W_{\mathrm{legal}}(s_t)\in\{0,1\}$$

它可以包含回城、复活、受控、引导技能、不可选中、等待关键队友、等待资源刷新和明确战术埋伏。

最终发呆告警为：

$$D_{\mathrm{idle}}=\mathbf 1_{\{T_{\mathrm{idle}}\ge\tau_{\mathrm{idle}}\}}\left(1-W_{\mathrm{legal}}(s_t)\right)$$

白名单必须带最大持续时间，防止某个等待标志没有清除而永久屏蔽异常。

## 十六、送塔不是死锁

送塔通常具有持续动作和明显位移，因此不是传统死锁。应把它建模为安全约束违例或价值单调下降。

定义塔伤害危险集合：

$$\mathcal U_{\mathrm{tower}}=\{s\mid \mathrm{TargetedByTower}(s)=1\}$$

生存裕度可写为：

$$m_t=H_t+S_t-\widehat D_{\mathrm{in}}(t,t+\Delta)$$

若：

$$m_t\lt0$$

且没有足够击杀、拆塔或换资源收益，则继续深入属于无谓风险行为。

## 十七、塔下行动价值

塔下动作价值可写为：

$$Q_{\mathrm{dive}}=p_kV_k+p_oV_o-p_dC_d-p_fC_f-p_rC_r$$

其中 $p_k$ 是击杀概率，$V_k$ 是击杀价值，$p_oV_o$ 是目标收益，$p_dC_d$ 是死亡代价，$p_fC_f$ 是失败后节奏损失，$p_rC_r$ 是资源消耗。

安全否决条件可取：

$$Q_{\mathrm{dive}}\lt Q_{\mathrm{retreat}}-\delta_Q$$

若控制器仍连续选择深入，则应归类为策略循环或安全层失效，而不是导航卡滞。

## 十八、危险暴露积分

瞬时危险分数为 $R(s_t)$。窗口累计暴露为：

$$E_W=\sum_{k=t-W+1}^{t}R(s_k)\Delta t$$

无进展危险循环判据为：

$$E_W\ge E_{\max}$$

$$\Delta P_W\le\epsilon_P$$

这能识别“在塔下走来走去”“在敌方火力区反复选目标”以及“血量不足仍试图贴近”等合法但无价值的动作。

## 十九、等待图检测模块死锁

把模块、资源和控制权表示为等待图：

$$G_W=(V_W,E_W)$$

若模块 $i$ 等待模块 $j$，建立边：

$$i\rightarrow j$$

例如导航等待目标选择，目标选择等待团战状态，团战状态又等待导航到位，就形成环：

$$i_1\rightarrow i_2\rightarrow\cdots\rightarrow i_k\rightarrow i_1$$

等待图中存在有向环是资源或控制依赖死锁的重要证据。

## 二十、团队协调死锁

五名英雄可能互相等待“别人先开”。设英雄 $i$ 的开团条件为：

$$g_i=\mathbf 1_{\{\sum_{j\neq i}z_{ij}\ge m_i\}}$$

$z_{ij}$ 表示队友 $j$ 是否已进入接应状态。若所有英雄都要求至少一名其他英雄先进入，但当前无人进入，就出现协调死锁。

可检查：

$$\sum_{i=1}^{5}g_i=0$$

同时：

$$\exists a_i^{\mathrm{probe}}\in A_i(s)$$

系统应指定显式发起者、超时探测动作或随机打破对称。

## 二十一、控制权死锁与饥饿

设控制层集合为：

$$\mathcal C=\{\mathrm{strategy},\mathrm{fight},\mathrm{navigation},\mathrm{safety},\mathrm{script}\}$$

控制权变量为 $o_t$。若多个层都认为其他层拥有控制权：

$$o_t=\varnothing$$

则表现为发呆。

若某层持续抢占控制权，使低层动作永远无法完成，则形成饥饿。设动作 $a$ 等待执行时间为：

$$T_a=t-t_a^{\mathrm{ready}}$$

若 $T_a$ 超过上限且守卫持续成立，应记录抢占来源并触发仲裁。

## 二十二、强连通分量检测活锁

将抽象状态和转移构成图：

$$G=(V,E)$$

对强连通分量 $C\subseteq V$，若：

$$\forall u,v\in C,\quad u\leadsto v$$

且执行轨迹长期停留在 $C$，则它是循环候选。

若目标集合不在其中：

$$C\cap G=\varnothing$$

并且控制策略几乎不选择离开 $C$ 的边，则该分量是活锁陷阱。

## 二十三、闭合循环与逃逸概率

分量的策略逃逸概率为：

$$p_{\mathrm{exit}}(C)=\sum_{s\in C}\mu_C(s)\sum_a\pi(a\mid s)\sum_{s'\notin C}P(s'\mid s,a)$$

$\mu_C$ 是轨迹在分量内的经验占用分布。

若：

$$p_{\mathrm{exit}}(C)\le\epsilon_{\mathrm{exit}}$$

则即使图上存在出口，当前策略也几乎不会使用它。这比仅检查拓扑闭合更适合发现学习策略的软活锁。

## 二十四、状态哈希与重复轨迹

定义抽象状态哈希：

$$h_t=H(\alpha(s_t),\alpha(g_t),\alpha(a_t))$$

窗口重复率为：

$$R_W=\frac{W-\lvert\{h_{t-W+1},\ldots,h_t\}\rvert}{W}$$

当 $R_W$ 高且进度低时，表明状态动作对反复出现。

哈希必须忽略无关微小数值，否则相同循环会因坐标抖动、浮点误差或计时器变化被误认为不同状态。

## 二十五、周期检测

对离散哈希序列，可搜索最小周期 $p$：

$$h_k=h_{k-p}$$

在窗口内的周期一致率为：

$$C_p=\frac{1}{W-p}\sum_{k=t-W+p+1}^{t}\mathbf 1_{\{h_k=h_{k-p}\}}$$

若：

$$\max_{1\le p\le p_{\max}}C_p\ge c_0$$

且没有任务进展，就触发周期活锁。

也可以用 Floyd 快慢指针检测确定性状态机中的环，但随机游戏轨迹更适合容错哈希和重复率。

## 二十六、时序逻辑性质

“收到移动目标后最终取得位移”可写为：

$$\Box\left(\mathrm{MoveGoal}\Rightarrow\Diamond^{\le H}\mathrm{Moved}\right)$$

“进入塔区后必须在有限时间内完成有效目标或退出”可写为：

$$\Box\left(\mathrm{TowerZone}\Rightarrow\Diamond^{\le H}(\mathrm{ValueGain}\vee\mathrm{Exit})\right)$$

“不能永远在重规划状态”可写为：

$$\Box\Diamond\neg\mathrm{Replanning}$$

这些性质可离线用于模型检测，也可编译为轻量运行时监视器。

## 二十七、Büchi 视角下的活性

设接受状态集合为 $F$，活性要求轨迹无限次访问 $F$：

$$\mathrm{Inf}(\rho)\cap F\neq\varnothing$$

在 MOBA 中，$F$ 可以表示“取得可度量任务进展”“完成控制权交接”或“离开危险循环”。

若轨迹最终永远停留在某个不含 $F$ 的强连通分量中，就违反 Büchi 接受条件，可解释为长期活锁。

## 二十八、Petri 网死锁检测

行为并发、资源令牌和同步条件可用 Petri 网表示。标识为：

$$M\in\mathbb N^n$$

变迁 $t$ 可激活的条件为：

$$M\ge\mathrm{Pre}(:,t)$$

死锁标识满足：

$$\forall t,\quad M\not\ge\mathrm{Pre}(:,t)$$

它适合分析“目标令牌、移动控制权、技能许可和安全许可互相等待”的情况。需要把正常终止标识从死锁集合中排除。

## 二十九、行为树中的死锁

行为树常见故障包括：

- 所有条件节点都失败，没有兜底动作。
- Parallel 节点等待一个永远不会成功的子节点。
- Decorator 无限重试同一失败动作。
- 高优先级分支持续 Running，使低优先级恢复分支饥饿。
- 黑板键值由不同模块反复覆盖。

设节点 $n$ 连续处于 Running 的时间为：

$$T_n=t-t_n^{\mathrm{enter}}$$

若超过节点级预算：

$$T_n\ge\tau_n$$

且进度为零，就应中断该节点并把失败原因传给上层，而不是永久返回 Running。

## 三十、控制器冲突检测

设导航输出为 $u_t^{\mathrm{nav}}$，战斗走位输出为 $u_t^{\mathrm{fight}}$，安全层输出为 $u_t^{\mathrm{safe}}$。

方向冲突可用余弦相似度衡量：

$$c_{ij}=\frac{(u_t^i)^\top u_t^j}{\lVert u_t^i\rVert\lVert u_t^j\rVert}$$

当：

$$c_{ij}\le-\gamma$$

且控制权高频切换时，英雄容易左右横跳或原地抵消。

应记录最终生效动作，而不能只记录各模块的提议动作。

## 三十一、多证据融合

单一检测器容易误报。定义特征：

$$z_t=(z_{\mathrm{motion}},z_{\mathrm{progress}},z_{\mathrm{cycle}},z_{\mathrm{contact}},z_{\mathrm{risk}},z_{\mathrm{control}})$$

线性风险分数为：

$$q_t=\sigma(w^\top z_t+b)$$

也可以使用规则融合：

$$D_{\mathrm{stuck}}=D_{\mathrm{move}}\wedge(D_{\mathrm{contact}}\vee D_{\mathrm{path}})$$

$$D_{\mathrm{livelock}}=D_{\mathrm{cycle}}\wedge D_{\mathrm{no\ progress}}$$

$$D_{\mathrm{suicide}}=D_{\mathrm{risk}}\wedge D_{\mathrm{no\ value}}$$

规则型融合更容易解释，学习型融合更容易适应不同英雄和地图，但必须保证跨版本校准。

## 三十二、滞回与去抖

进入异常状态使用高阈值，退出使用低阈值：

$$\theta_{\mathrm{enter}}\gt\theta_{\mathrm{exit}}$$

进入需要连续满足：

$$N_{\mathrm{bad}}\ge n_{\mathrm{enter}}$$

退出需要连续恢复：

$$N_{\mathrm{good}}\ge n_{\mathrm{exit}}$$

这样可以避免一帧碰撞、一秒等待或正常走位触发反复报警和恢复动作。

## 三十三、异常状态机

推荐状态集合：

$$Q=\{\mathrm{normal},\mathrm{suspect},\mathrm{confirmed},\mathrm{recovering},\mathrm{cooldown}\}$$

典型转移为：

$$\mathrm{normal}\rightarrow\mathrm{suspect}\rightarrow\mathrm{confirmed}\rightarrow\mathrm{recovering}\rightarrow\mathrm{cooldown}\rightarrow\mathrm{normal}$$

恢复后设置冷却期，防止同一检测器立即重新触发。若恢复失败次数超过上限，应升级到更强恢复层级。

## 三十四、分级恢复策略

恢复等级可按破坏性从低到高排列：

1. 刷新局部路径与当前路径点。
2. 临时提高障碍膨胀或改变局部代价。
3. 选择侧向逃逸点并短时锁定。
4. 禁用最近使用的失败边或目标。
5. 切换到安全撤退目标。
6. 重置行为树当前分支和控制权。
7. 重新初始化局部规划器状态。

恢复函数为：

$$a_t^{\mathrm{recover}}=R(c_t,s_t,H_t)$$

它必须受游戏合法动作和安全约束限制，不能用瞬移或穿墙掩盖问题。

## 三十五、卡墙脱困方向

设障碍法向为 $n$，原期望方向为 $u$。切向投影为：

$$u_{\mathrm{tan}}=u-(u^\top n)n$$

若切向仍过小，可选择左右两个候选方向：

$$u_{\pm}=\frac{u_{\mathrm{tan}}\pm\lambda R_{\pi/2}n}{\lVert u_{\mathrm{tan}}\pm\lambda R_{\pi/2}n\rVert}$$

分别短程模拟并选择预期进度更大的方向。脱困期间应锁定选择数百毫秒，避免左右方向每帧翻转。

## 三十六、绕塔恢复

检测到塔周极限环后，不应只重新请求同一个终点。可执行：

1. 把塔危险区扩大为临时禁行区域。
2. 在环外选择可见且可达的逃逸锚点。
3. 禁止短时间内重新选择导致环绕的边。
4. 若任务仍有价值，从不同入口重新规划。
5. 若生存裕度不足，强制撤退并屏蔽攻击追踪。

临时禁忌边集合为：

$$E_{\mathrm{tabu}}(t)=\{e\mid t-t_e^{\mathrm{fail}}\le\tau_{\mathrm{tabu}}\}$$

新路径不得使用该集合中的边。

## 三十七、目标切换滞回

设当前目标价值为 $V(g_t)$，候选目标为 $g'$. 只有当：

$$V(g')\ge V(g_t)+\Delta_V$$

并持续：

$$T_{\mathrm{better}}\ge\tau_{\mathrm{switch}}$$

才允许切换。紧急安全事件可以绕过滞回，但必须有明确优先级。

这能减少“追人、撤退、再追人”的目标抖动。

## 三十八、塔区硬安全约束

定义允许越塔谓词：

$$G_{\mathrm{dive}}(s)=G_{\mathrm{wave}}G_{\mathrm{kill}}G_{\mathrm{escape}}G_{\mathrm{team}}G_{\mathrm{health}}$$

其中每一项都取零或一。只有：

$$G_{\mathrm{dive}}(s)=1$$

才允许进入高风险塔区。

一旦生存裕度低于退出阈值：

$$m_t\le m_{\mathrm{exit}}$$

安全层应锁定撤退目标一段最小时间，避免攻击目标重新夺回控制权。

## 三十九、误报控制

需要显式排除以下正常行为：

- 补刀前的短时站位。
- 草丛埋伏和视野外等待。
- 等待兵线、队友或关键技能。
- 规避指向技能时的短周期横移。
- 走 A 形成的攻击移动循环。
- 有目的地拉塔仇恨与换抗。
- 回城、蓄力、复活和控制状态。

误报代价与漏报代价不同。可定义：

$$L=\lambda_{\mathrm{FP}}N_{\mathrm{FP}}+\lambda_{\mathrm{FN}}N_{\mathrm{FN}}+\lambda_{\mathrm{late}}T_{\mathrm{delay}}$$

塔下送死的漏报代价通常高于短暂误报，因此安全检测器应采用更敏感的阈值。

## 四十、运行时日志

每次异常至少记录：

- 时间、英雄、地图位置和当前任务。
- 当前路径、路径点、目标和目标切换历史。
- 所有控制层候选动作与最终生效动作。
- 速度、碰撞法向、导航可达性和局部代价。
- 血量、塔仇恨、敌我威胁和技能冷却。
- 检测特征、触发规则、置信度和恢复等级。
- 恢复前后数秒的状态窗口。

事件记录可抽象为：

$$e_t=(t,s_t,g_t,a_t,z_t,c_t,q_t,r_t)$$

$r_t$ 表示采取的恢复动作。

## 四十一、离线回放挖掘

对每段回放计算低进度窗口：

$$\mathcal W_{\mathrm{low}}=\{[t-W,t]\mid\Delta P_W\le\epsilon_P\}$$

再按运动、风险和周期特征聚类。高频模式通常会暴露固定墙角、特定塔区、特定英雄位移技能或特定行为树分支。

可构建异常转移图：

$$G_A=(V_A,E_A)$$

节点是抽象异常状态，边是恢复动作及结果。这样可以统计哪种恢复对哪类卡滞最有效。

## 四十二、单元测试与场景测试

至少构造以下确定性测试：

1. 英雄正对不可通行墙持续移动。
2. 英雄卡在两墙夹角。
3. 路径点位于墙后且不可见。
4. 塔周势场形成稳定圆周轨迹。
5. 追击与撤退目标每帧切换。
6. 行为树叶节点永久 Running。
7. 两个模块互相等待控制权。
8. 英雄在塔下无击杀收益仍继续深入。
9. 正常草丛埋伏不应报警。
10. 正常走 A 和技能躲避不应报警。

对每个场景验证检测延迟、类别、恢复动作和恢复后的任务进度。

## 四十三、性质测试

可定义必须保持的性质：

$$D_{\mathrm{stuck}}=1\Rightarrow T_{\mathrm{recover}}\le\tau_R$$

$$D_{\mathrm{tower}}=1\Rightarrow a_{\mathrm{advance}}\notin A_{\mathrm{safe}}$$

$$W_{\mathrm{legal}}=1\Rightarrow D_{\mathrm{idle}}=0$$

$$N_{\mathrm{recover}}\ge N_{\max}\Rightarrow g_t=\mathrm{safe\ retreat}$$

随机生成墙体、路径点、目标切换和控制器延迟，可以检查监视器是否在边界条件下失效。

## 四十四、核心指标

检测精确率为：

$$\mathrm{Precision}=\frac{N_{\mathrm{TP}}}{N_{\mathrm{TP}}+N_{\mathrm{FP}}}$$

检测召回率为：

$$\mathrm{Recall}=\frac{N_{\mathrm{TP}}}{N_{\mathrm{TP}}+N_{\mathrm{FN}}}$$

平均检测延迟为：

$$\bar T_D=\frac{1}{N}\sum_{i=1}^{N}(t_i^{\mathrm{detect}}-t_i^{\mathrm{start}})$$

恢复成功率为：

$$p_R=\frac{N_{\mathrm{progress\ after\ recovery}}}{N_{\mathrm{recovery}}}$$

还应统计重复恢复率、错误强制撤退率、塔下死亡率、单位时间低进度占比和不同地图区域的异常热力图。

## 四十五、阈值如何设定

阈值不应对所有英雄固定。设英雄移动速度、攻击节奏和技能机制参数为 $\theta_h$，阈值为：

$$\tau=\tau(\theta_h,\mathrm{task},\mathrm{map},\mathrm{latency})$$

可以先用规则给出保守范围，再通过标注回放最小化验证损失：

$$\theta^*=\mathop{\arg\min}_{\theta}L_{\mathrm{val}}(\theta)$$

阈值更新必须按版本和地图分层验证，不能用总体平均掩盖特定英雄的严重误报。

## 四十六、推荐实时架构

推荐把检测分为四层：

1. 每帧采集层：记录命令、实际运动、碰撞、目标和控制权。
2. 短窗口监视层：检测卡墙、发呆、目标抖动和塔区危险。
3. 中窗口循环层：检测环绕角、重复轨迹、强连通分量和软活锁。
4. 恢复仲裁层：选择最小破坏性的恢复动作并验证恢复效果。

信息流为：

$$o_t\rightarrow z_t\rightarrow D_t\rightarrow R_t\rightarrow a_t^{\mathrm{safe}}\rightarrow o_{t+1}$$

检测器只能提出异常与恢复建议；最终动作仍需经过游戏规则、安全约束和控制权仲裁。

## 四十七、最小可行版本

第一版可以只实现六个监视器：

1. 有移动命令但低位移的卡墙监视器。
2. 高累计路程但低净进度的绕圈监视器。
3. 环绕塔中心的 winding number 监视器。
4. 合法等待白名单后的发呆监视器。
5. 两周期目标和动作振荡监视器。
6. 塔伤害裕度与撤退可达性的送塔监视器。

恢复只做三档：刷新路径、选择侧向逃逸点、强制安全撤退。先把触发证据和结果完整记录，再逐步加入等待图、SCC、Petri 网和时序逻辑验证。

## 四十八、结论

在 MOBA 中，死锁检测解决“无动作可走或模块互相等待”，活锁检测解决“动作很多但没有进展”，导航卡滞检测解决“命令与实际运动不一致”，安全监视解决“动作合法却持续送死”。把所有问题都归结为速度为零，会漏掉绕塔、反复横跳和送塔，也会误伤埋伏、回城和等待兵线。

可靠方案需要三类信号共同工作：进度信号判断任务是否前进，循环信号判断状态和动作是否重复，安全信号判断是否在用生命和资源换取有效价值。检测后必须采用分级恢复，优先局部重规划和侧向脱困，失败后才升级为目标重置与强制撤退。

最终原则是：每个长期 Running 的行为都要有进度证明、超时预算和退出路径；每个高风险动作都要有价值证据和安全回退；每次恢复都要记录原因、动作和结果。这样才能把“偶尔看起来很蠢”转化为可定位、可回放、可测试和可持续修复的工程问题。
