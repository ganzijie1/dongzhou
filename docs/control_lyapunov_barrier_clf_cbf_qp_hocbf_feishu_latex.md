# Control Lyapunov / Barrier Function：CLF、CBF、CLF-CBF-QP 与高阶障碍函数

## 摘要

Control Lyapunov Function，简称 CLF，用一个标量函数把稳定目标转化为控制不等式；Control Barrier Function，简称 CBF，用另一个标量函数把安全集合的前向不变性转化为控制不等式。二者都可以在控制仿射系统中形成关于控制输入的线性约束，再通过二次规划组合为 CLF-CBF-QP。

CLF 负责“趋向哪里”，CBF 负责“不能进入哪里”。在工程实现中，CLF 通常允许通过松弛变量暂时违背，以保持优化问题可行；安全 CBF 一般应保持为硬约束，只有在系统已经不可恢复时才进入明确标记的最小违规模式。

当安全函数对控制输入的相对阶大于一时，普通一阶 CBF 不能直接约束控制，需要使用 High-Order Control Barrier Function，简称 HOCBF，或者 Exponential CBF。本文从连续控制仿射系统出发，系统介绍 CLF、CBF、CLF-CBF-QP、HOCBF、鲁棒和离散版本、可行性、数值实现及 5v5 游戏应用。

全文统一使用：

$$\mathcal C=\{x:h(x)\geq0\}$$

表示安全集合，$h(x)=0$ 表示安全边界，$h(x)<0$ 表示违反安全约束。

## 一、控制仿射系统

考虑控制仿射系统：

$$\dot x=f(x)+g(x)u$$

其中：

$$x\in\mathbb R^n,\qquad u\in\mathcal U\subseteq\mathbb R^m$$

$f(x)$ 是自然漂移，$g(x)$ 描述控制输入如何作用于状态。常见输入约束为：

$$u_{\min}\leq u\leq u_{\max}$$

对可微函数 $q(x)$，沿系统轨迹的导数为：

$$\dot q(x)=\nabla q(x)^{\mathsf T}f(x)+\nabla q(x)^{\mathsf T}g(x)u$$

定义 Lie 导数：

$$L_fq(x)=\nabla q(x)^{\mathsf T}f(x)$$

$$L_gq(x)=\nabla q(x)^{\mathsf T}g(x)$$

因此：

$$\dot q(x)=L_fq(x)+L_gq(x)u$$

CLF 与一阶 CBF 的关键优势是：虽然动力学可以非线性，但对当前控制 $u$ 的约束通常是仿射的。

## 二、稳定性问题

设期望平衡点为 $x^{\star}$。稳定控制希望：

$$x(t)\rightarrow x^{\star}$$

Lyapunov 方法不直接求完整轨迹，而是构造能量函数 $V(x)$。典型要求为：

$$V(x^{\star})=0$$

$$V(x)>0,\qquad x\neq x^{\star}$$

并希望沿闭环轨迹：

$$\dot V(x)<0$$

直观上，$V$ 像一座以目标点为谷底的地形；控制器不断选择使能量下降的动作。

## 三、Control Lyapunov Function

若存在类 $\mathcal K$ 函数 $\alpha$，使对每个非目标状态都有：

$$\inf_{u\in\mathcal U}\left[L_fV(x)+L_gV(x)u\right]\leq-\alpha(V(x))$$

则 $V$ 可作为 CLF。

常用指数型条件为：

$$L_fV(x)+L_gV(x)u\leq-cV(x)$$

其中：

$$c>0$$

若该约束始终满足，则：

$$V(x(t))\leq e^{-ct}V(x(0))$$

这给出指数收敛速率。

## 四、类 K 函数

连续函数 $\alpha:[0,a)\rightarrow[0,\infty)$ 若满足：

$$\alpha(0)=0$$

且严格单调递增，则称为类 $\mathcal K$ 函数。若定义域和值域均扩展到非负实数且无界，则称为扩展类 $\mathcal K_{\infty}$ 函数。

常见选择为：

$$\alpha(s)=cs$$

也可以使用：

$$\alpha(s)=c_1s+c_2s^3$$

函数形状决定离目标不同距离处的收敛强度。

## 五、二次型 CLF

对线性系统：

$$\dot x=Ax+Bu$$

选择：

$$V(x)=x^{\mathsf T}Px$$

其中：

$$P=P^{\mathsf T}>0$$

则：

$$\dot V=x^{\mathsf T}(A^{\mathsf T}P+PA)x+2x^{\mathsf T}PBu$$

若已有稳定反馈：

$$u=Kx$$

可以通过 Lyapunov 方程选择 $P$：

$$(A+BK)^{\mathsf T}P+P(A+BK)=-Q$$

其中 $Q>0$。CLF-QP 可以在名义反馈外加入约束，同时尽量保留该稳定趋势。

## 六、有限时间 CLF

若希望在有限时间内到达目标，可使用：

$$\dot V\leq-cV^{\gamma}$$

其中：

$$c>0,\qquad0<\gamma<1$$

由此得到到达时间上界：

$$T\leq\frac{V(x(0))^{1-\gamma}}{c(1-\gamma)}$$

该结论要求不等式在到达前持续成立。输入饱和、离散采样和建模误差都会改变实际时间界。

## 七、安全集合

给定连续可微函数 $h(x)$，定义：

$$\mathcal C=\{x:h(x)\geq0\}$$

内部为：

$$\mathrm{Int}(\mathcal C)=\{x:h(x)>0\}$$

边界为：

$$\partial\mathcal C=\{x:h(x)=0\}$$

安全目标是前向不变性：

$$x(0)\in\mathcal C\quad\Longrightarrow\quad x(t)\in\mathcal C,\ \forall t\geq0$$

前向不变性比“当前没有碰撞”更强，因为它要求未来闭环轨迹持续留在安全集合内。

## 八、Nagumo 边界条件

在光滑边界上，一个基本切向条件是：

$$\dot h(x)\geq0,\qquad h(x)=0$$

即系统到达安全边界时，速度不能指向集合外部。对控制系统，这要求边界上存在可行控制满足：

$$L_fh(x)+L_gh(x)u\geq0$$

CBF 把这一边界条件扩展到安全集合内部，并形成可直接优化的约束。

## 九、Zeroing Control Barrier Function

若存在扩展类 $\mathcal K$ 函数 $\alpha$，使：

$$\sup_{u\in\mathcal U}\left[L_fh(x)+L_gh(x)u\right]\geq-\alpha(h(x))$$

则 $h$ 可作为 Zeroing CBF 的候选。

相应的安全控制集合为：

$$K_{\mathrm{CBF}}(x)=\{u\in\mathcal U:L_fh(x)+L_gh(x)u+\alpha(h(x))\geq0\}$$

常用线性选择为：

$$\alpha(h)=\kappa h$$

其中 $\kappa>0$。于是：

$$L_fh+L_ghu\geq-\kappa h$$

当状态靠近边界时，允许的负向变化逐渐变小；在边界上恢复为 $\dot h\geq0$。

## 十、CBF 前向不变性

若初始状态满足：

$$x(0)\in\mathcal C$$

并且局部 Lipschitz 控制器对所有时刻选择：

$$u(x)\in K_{\mathrm{CBF}}(x)$$

则在适当正则条件下：

$$x(t)\in\mathcal C,\qquad\forall t\geq0$$

这一定理依赖连续时间动力学和持续满足约束。数字控制器只在离散时刻更新时，还需要采样保持误差分析。

## 十一、Reciprocal Barrier Function

另一类障碍函数在接近边界时发散。若安全集合内部定义：

$$B(x)>0$$

且：

$$B(x)\rightarrow\infty,\qquad h(x)\rightarrow0^+$$

典型选择为：

$$B(x)=\frac{1}{h(x)}$$

可以要求：

$$\inf_{u\in\mathcal U}\left[L_fB(x)+L_gB(x)u\right]\leq\alpha\left(\frac{1}{B(x)}\right)$$

Zeroing CBF 在边界附近通常数值更温和；Reciprocal Barrier 更直接表达接近边界的代价发散。二者的符号和不等式方向不能混用。

## 十二、CLF 与 CBF 的逻辑差异

CLF 条件回答：

$$\exists u:\dot V\leq-\alpha(V)$$

CBF 条件回答：

$$\exists u:\dot h\geq-\alpha(h)$$

CLF 关注渐近或有限时间性能；短时间内放慢收敛通常可以接受。CBF 关注集合不变性；一旦越过硬安全边界，之后再补偿也不能恢复“从未违规”的保证。

因此，在联合优化中常把 CLF 设为软约束，把核心 CBF 保持为硬约束。

## 十三、名义控制器

设已有行为树、强化学习策略、轨迹跟踪器或人工规则给出名义控制：

$$u_{\mathrm{nom}}(x)$$

安全过滤器希望在满足 CBF 的同时尽量少改动名义动作：

$$u^{\star}=\arg\min_{u\in K_{\mathrm{CBF}}(x)}\frac{1}{2}\lVert u-u_{\mathrm{nom}}\rVert^2$$

这形成最简单的 CBF-QP。若名义动作本来安全，最优解通常保持不变；只有接近约束边界时才介入。

## 十四、CLF-QP

只使用 CLF 时，可以求：

$$\min_{u,\delta}\frac{1}{2}(u-u_{\mathrm{nom}})^{\mathsf T}H(u-u_{\mathrm{nom}})+p\delta^2$$

满足：

$$L_fV+L_gVu\leq-cV+\delta$$

$$\delta\geq0$$

矩阵 $H>0$ 控制动作修改代价，$p>0$ 惩罚稳定性松弛。$\delta$ 使 QP 在输入受限时仍可能可行，但它也意味着所要求的 CLF 收敛速率可能暂时无法实现。

## 十五、CLF-CBF-QP

联合优化的标准形式为：

$$\min_{u,\delta}\frac{1}{2}(u-u_{\mathrm{nom}})^{\mathsf T}H(u-u_{\mathrm{nom}})+p\delta^2$$

满足 CLF 约束：

$$L_fV+L_gVu\leq-cV+\delta$$

满足 CBF 约束：

$$L_fh+L_ghu\geq-\alpha(h)$$

以及输入约束：

$$u_{\min}\leq u\leq u_{\max}$$

和：

$$\delta\geq0$$

CLF 决定期望收敛，CBF 截断不安全动作，QP 在每个控制周期选择距离名义控制最近的合法输入。

## 十六、标准 QP 矩阵形式

令优化变量为：

$$z=(u,\delta)$$

目标写成：

$$\min_z\frac{1}{2}z^{\mathsf T}Pz+q^{\mathsf T}z$$

所有约束整理为：

$$Az\leq b$$

例如 CBF 约束可改写为：

$$-L_gh\,u\leq L_fh+\alpha(h)$$

工程实现必须统一求解器的不等式方向。如果求解器使用 $Az\geq b$，需要整体转换，不能只改变右端符号。

## 十七、松弛变量的设计

CLF 松弛通常取：

$$\delta_{\mathrm{CLF}}\geq0$$

核心安全 CBF 默认不设置松弛。若多个安全约束在物理上无法同时满足，可引入带优先级的违规变量：

$$L_fh_i+L_gh_i u+\alpha_i(h_i)\geq-\epsilon_i$$

$$\epsilon_i\geq0$$

并使用：

$$\sum_iw_i\epsilon_i^2$$

作为高代价。此时输出必须明确标记为“最小违规控制”，不能继续声称严格前向不变性。

## 十八、多个 CBF

若存在 $M$ 个安全约束：

$$\mathcal C=\bigcap_{i=1}^M\{x:h_i(x)\geq0\}$$

则需要同时满足：

$$L_fh_i+L_gh_i u+\alpha_i(h_i)\geq0,\qquad i=1,\ldots,M$$

每个约束单独可行不意味着它们联合可行。两个避碰约束可能要求角色同时向相反方向移动，因此必须检查联合控制集合：

$$K(x)=\bigcap_{i=1}^MK_{\mathrm{CBF},i}(x)$$

## 十九、相对阶

安全函数 $h(x)$ 的相对阶是控制输入首次显式出现在其第几阶时间导数中。

若：

$$L_gh(x)\neq0$$

则相对阶为一，普通 CBF 可直接约束 $u$。

若：

$$L_gh(x)=0$$

但：

$$L_gL_fh(x)\neq0$$

则相对阶为二。此时一阶约束：

$$L_fh+\alpha(h)\geq0$$

与控制 $u$ 无关，不能通过当前控制直接修正，必须使用高阶障碍函数。

## 二十、避碰问题为什么常是相对阶二

考虑双积分器：

$$\dot p=v$$

$$\dot v=u$$

避碰函数为：

$$h(p)=\lVert p-p_o\rVert^2-d_{\min}^2$$

一阶导数：

$$\dot h=2(p-p_o)^{\mathsf T}(v-v_o)$$

其中没有 $u$。二阶导数为：

$$\ddot h=2\lVert v-v_o\rVert^2+2(p-p_o)^{\mathsf T}(u-u_o)$$

控制首次出现在二阶导数中，因此该安全函数对加速度控制的相对阶为二。

## 二十一、High-Order Control Barrier Function

令：

$$\psi_0(x)=h(x)$$

递归定义：

$$\psi_i(x)=\dot\psi_{i-1}(x)+\alpha_i(\psi_{i-1}(x))$$

其中：

$$i=1,\ldots,r$$

$r$ 是相对阶。HOCBF 约束为：

$$\psi_r(x,u)\geq0$$

并要求初始状态满足：

$$\psi_i(x(0))\geq0,\qquad i=0,\ldots,r-1$$

在适当正则条件下，这一递归保证各层集合连续保持可行，从而维持原始安全约束 $h(x)\geq0$。

## 二十二、二阶 HOCBF

对相对阶二的 $h$，选择：

$$\psi_0=h$$

$$\psi_1=\dot h+\alpha_1(h)$$

最终约束为：

$$\dot\psi_1+\alpha_2(\psi_1)\geq0$$

展开得到：

$$\ddot h+\alpha_1'(h)\dot h+\alpha_2(\dot h+\alpha_1(h))\geq0$$

若选择线性函数：

$$\alpha_1(s)=k_1s,\qquad\alpha_2(s)=k_2s$$

则：

$$\ddot h+(k_1+k_2)\dot h+k_1k_2h\geq0$$

该不等式对双积分器控制 $u$ 是仿射的，可以直接放入 QP。

## 二十三、一般相对阶 HOCBF

若 $h$ 的相对阶为 $r$，则最高阶导数具有结构：

$$h^{(r)}=L_f^rh+L_gL_f^{r-1}h\,u$$

HOCBF 递归会加入所有低阶项，最终可写为：

$$L_f^rh+L_gL_f^{r-1}h\,u+S(h,L_fh,\ldots,L_f^{r-1}h)\geq0$$

$S$ 汇总由 $\alpha_i$ 和低阶 Lie 导数产生的项。实现时应通过自动微分、符号微分或经过测试的解析表达式生成，避免遗漏链式法则项。

## 二十四、Exponential Control Barrier Function

定义导数状态：

$$\eta_b=(h,L_fh,\ldots,L_f^{r-1}h)$$

选择增益向量 $K$，施加：

$$L_f^rh+L_gL_f^{r-1}h\,u\geq-K\eta_b$$

若对应伴随矩阵的闭环动态稳定，并且初始导数状态满足所需可行条件，则可以得到指数型障碍约束。

ECBF 是 HOCBF 的线性增益特例。HOCBF 允许每层使用一般类 $\mathcal K$ 函数，设计自由度更大。

## 二十五、HOCBF 参数的含义

增益过小会使控制器太晚介入，离散采样和执行延迟可能导致越界；增益过大则会产生激烈动作、频繁饱和和数值病态。

参数选择应结合：

1. 最大控制能力；
2. 最大接近速度；
3. 控制周期与通信延迟；
4. 状态估计误差；
5. 动力学残差；
6. 可接受的控制抖动。

不能只在静止初始状态上调参，因为高速接近状态决定真正的制动需求。

## 二十六、输入到状态安全

考虑带扰动系统：

$$\dot x=f(x)+g(x)u+p(x)d$$

其中：

$$d\in\mathcal D$$

鲁棒 CBF 约束为：

$$L_fh+L_ghu+\min_{d\in\mathcal D}L_ph\,d+\alpha(h)\geq0$$

若扰动满足：

$$\lVert d\rVert\leq\bar d$$

则：

$$\min_{\lVert d\rVert\leq\bar d}L_ph\,d=-\bar d\lVert L_ph\rVert$$

于是可用确定性裕量构造鲁棒约束：

$$L_fh+L_ghu-\bar d\lVert L_ph\rVert+\alpha(h)\geq0$$

## 二十七、模型不确定性

若动力学估计为：

$$\dot x=\widehat f(x)+\widehat g(x)u+e(x,u)$$

且已知：

$$\lvert\nabla h^{\mathsf T}e(x,u)\rvert\leq\varepsilon_h(x,u)$$

则保守 CBF 可写为：

$$L_{\widehat f}h+L_{\widehat g}h\,u-\varepsilon_h(x,u)+\alpha(h)\geq0$$

误差界必须来自覆盖关注区域的数据或可信物理上界。只用训练误差均值不能支撑最坏情况安全保证。

## 二十八、随机 CBF

考虑 Itô 扩散：

$$dX_t=b(X_t,u_t)dt+\sigma(X_t)dW_t$$

函数 $h$ 的生成元为：

$$\mathcal Ah=\nabla h^{\mathsf T}b+\frac{1}{2}\mathrm{tr}\left(\sigma\sigma^{\mathsf T}\nabla^2h\right)$$

可以构造期望安全、概率安全或超鞅型障碍条件。但当扩散在边界法向上非零时，Brownian 路径可能瞬间穿越边界，因此简单要求：

$$\mathcal Ah+\alpha(h)\geq0$$

一般不等价于确定性的逐路径前向不变性。文档和代码必须标明保证是期望、概率还是几乎必然意义。

## 二十九、离散时间 CBF

对离散系统：

$$x_{k+1}=F(x_k,u_k)$$

一种离散 CBF 条件为：

$$h(x_{k+1})-h(x_k)\geq-\gamma h(x_k)$$

其中：

$$0<\gamma\leq1$$

等价地：

$$h(F(x_k,u_k))\geq(1-\gamma)h(x_k)$$

该约束通常对 $u$ 非线性。可以直接做非线性优化，也可以在名义动作附近线性化，但线性化版本需要可信域和余项界。

## 三十、采样数据 CBF

连续时间 CBF 只在采样时刻成立，不自动保证两个采样点之间安全。若控制周期为 $\Delta t$，需要估计采样间最坏变化：

$$h(x(t+\Delta t))\geq h(x(t))-M\Delta t$$

可以收紧安全约束：

$$h(x_k)\geq M\Delta t+\rho$$

$\rho$ 用于覆盖状态估计和执行误差。更精确的方法是使用 sampled-data CBF、区间可达性或短时 BRT 计算采样间安全裕量。

## 三十一、执行延迟

若从观测到动作生效存在延迟 $\tau$，控制器实际作用于未来状态。简单的一阶预测为：

$$\widehat x(t+\tau)=x(t)+\tau\left[f(x(t))+g(x(t))u_{\mathrm{old}}\right]$$

CBF-QP 应在预测状态上评估，或使用延迟系统的扩展状态。直接在过期状态上求解会在高速接近边界时产生虚假安全。

## 三十二、QP 可行性

CLF-CBF-QP 可能因以下原因不可行：

1. 已经处于安全集合外；
2. 控制输入不足以阻止越界；
3. 多个 CBF 相互冲突；
4. CLF 与硬 CBF 冲突且 CLF 没有松弛；
5. HOCBF 初始低阶条件已经违反；
6. 模型、延迟或状态估计错误。

应显式记录可行性状态：

$$s_{\mathrm{QP}}\in\{\mathrm{optimal},\mathrm{infeasible},\mathrm{numerical\ failure}\}$$

求解失败不能静默回退到未经检查的名义动作。

## 三十三、优先级与分层 QP

当约束过多时，可以使用词典序优先级：

1. 首先最小化核心安全违规；
2. 在核心安全最优值固定后最小化次级安全违规；
3. 再优化 CLF 性能；
4. 最后最小化对名义动作的修改。

相比把所有目标混成一个巨大权重和，分层 QP 更容易解释，也避免权重尺度不当让性能目标压过安全目标。

## 三十四、控制抖动

CBF 活跃集频繁切换可能导致动作抖动。可在目标中加入控制变化：

$$\lVert u-u_{\mathrm{prev}}\rVert_R^2$$

也可以限制控制变化率：

$$-\Delta u_{\max}\leq u-u_{\mathrm{prev}}\leq\Delta u_{\max}$$

但变化率约束会进一步缩小可行集。若安全需要瞬时大动作而变化率不允许，必须在更早位置介入或增大安全裕量。

## 三十五、CLF-CBF 与 MPC

CLF-CBF-QP 通常只优化当前控制，速度快且易于审计；MPC 显式预测多步轨迹，能处理未来约束和复杂代价。

组合方式包括：

1. MPC 生成 $u_{\mathrm{nom}}$，CBF 作为最后安全过滤器；
2. 把 CBF 约束加入 MPC 每个预测步；
3. 用 CLF 作为 MPC 终端代价或终端约束；
4. 用 BRT 价值函数构造终端安全集合。

只在第一个预测步加入 CBF 不能自动保证后续预测轨迹安全。

## 三十六、CLF-CBF 与 BRT

BRT 价值函数可以构造安全函数：

$$h(t,x)=V_{\mathrm{BRT}}(t,x)$$

采用 $V_{\mathrm{BRT}}>0$ 为安全时，HJI 最优安全控制与 CBF 边界条件密切相关。BRT 提供全局、有限时域、最坏对手信息；CBF-QP 提供局部、在线、低成本的动作过滤。

推荐组合是：

1. 离线用 BRT 计算不可恢复区域；
2. 在线用 BRT 价值或其保守近似作为 CBF；
3. CLF 表达当前任务目标；
4. QP 在安全前提下尽量执行名义策略。

若使用神经网络近似 BRT，必须把近似误差加入 CBF 收紧量。

## 三十七、单机器人避障示例

单积分器动力学：

$$\dot p=u$$

圆形障碍中心为 $p_o$，安全半径为 $R$。定义：

$$h(p)=\lVert p-p_o\rVert^2-R^2$$

则：

$$\dot h=2(p-p_o)^{\mathsf T}u$$

一阶 CBF 为：

$$2(p-p_o)^{\mathsf T}u+\kappa\left(\lVert p-p_o\rVert^2-R^2\right)\geq0$$

它是关于速度控制 $u$ 的线性不等式。

## 三十八、双积分器避障示例

双积分器使用相对阶二 HOCBF：

$$h=\lVert p-p_o\rVert^2-R^2$$

$$\dot h=2(p-p_o)^{\mathsf T}(v-v_o)$$

$$\ddot h=2\lVert v-v_o\rVert^2+2(p-p_o)^{\mathsf T}(u-u_o)$$

线性 HOCBF 约束为：

$$\ddot h+(k_1+k_2)\dot h+k_1k_2h\geq0$$

若障碍加速度 $u_o$ 未知但有界，应把最坏 $u_o$ 纳入鲁棒项。

## 三十九、编队 CLF

设角色期望保持相对位移 $r^{\star}$，误差为：

$$e=(p_i-p_j)-r^{\star}$$

可选 CLF：

$$V(e)=\frac{1}{2}e^{\mathsf T}e$$

CLF 约束推动角色恢复编队；角色间最小距离 CBF 则防止编队收缩时发生碰撞。两者联合后形成“尽量维持阵型，但不以碰撞为代价”的控制器。

## 四十、5v5 游戏中的安全函数

可构造以下 CBF 或 HOCBF：

1. 英雄间避碰：$h_{ij}=\lVert p_i-p_j\rVert^2-d_{ij}^2$；
2. 危险区域：$h_{\mathrm{zone}}$ 为到防御塔、毒圈或技能区域的带符号距离；
3. 地图边界：$h_{\mathrm{map}}$ 为可通行区域带符号距离；
4. 资源下界：$h_{\mathrm{hp}}=\mathrm{HP}-\mathrm{HP}_{\min}$；
5. 到达时限：把剩余时间加入状态构造时变 CBF；
6. 视野和掩体：用几何可见性裕量构造任务型软约束；
7. 技能前摇：把技能阶段作为混合模式，针对每个模式使用不同障碍约束。

生命值通常受离散伤害和事件跳变影响，不能只用连续一阶 CBF。需要使用混合系统、PDMP、离散 CBF 或最坏伤害包络。

## 四十一、5v5 游戏中的 CLF

可构造以下 CLF：

1. 追踪移动目标；
2. 回到阵型锚点；
3. 缩短到补给点或撤退点的距离；
4. 调整到期望射程环；
5. 让速度和朝向恢复到战术参考；
6. 让资源分配误差或团队覆盖误差下降。

一个简单位置 CLF 为：

$$V(p)=\frac{1}{2}\lVert p-p_{\mathrm{ref}}\rVert^2$$

但移动目标、障碍和敌方控制会使单一距离 CLF 不足，需要时变 CLF、追踪误差动力学或上层规划器更新参考点。

## 四十二、动作离散化

许多游戏只允许有限动作：

$$\mathcal A=\{a_1,\ldots,a_K\}$$

此时可以对每个动作预测短时状态：

$$x_k^+=F(x,a_k)$$

保留满足离散 CBF 的动作：

$$\mathcal A_{\mathrm{safe}}(x)=\{a_k:h(F(x,a_k))\geq(1-\gamma)h(x)\}$$

再从安全动作中选择最小 CLF 或最大策略分数的动作。若安全集合为空，应报告不可行并进入预定义降级逻辑，而不是随意选择一个动作。

## 四十三、技能选择与混合控制

连续移动和离散技能可以组合为混合决策：

$$a=(m,u)$$

$m$ 表示技能或模式，$u$ 表示连续方向。可以先枚举少量合法技能模式，再对每个模式求一个 CLF-CBF-QP，最后比较可行模式的目标值。

模式切换必须遵守冷却、资源和前摇规则。QP 只能在调用方给出的合法模式内优化，不能生成引擎不存在的技能状态。

## 四十四、状态估计误差

若观测状态为 $\widehat x$，误差满足：

$$\lVert x-\widehat x\rVert\leq\varepsilon_x$$

可以使用 Lipschitz 常数收紧：

$$h(\widehat x)\geq L_h\varepsilon_x+\rho$$

或直接对状态不确定集求最坏 CBF：

$$\min_{x\in\mathcal X(\widehat x)}\left[L_fh(x)+L_gh(x)u+\alpha(h(x))\right]\geq0$$

均值状态安全不代表真实状态安全，尤其在敌方位置和速度估计存在长尾误差时。

## 四十五、数值缩放

CLF、CBF、控制输入和松弛变量可能具有不同数量级。应进行无量纲化或显式缩放：

$$\widetilde x_i=\frac{x_i-x_i^{\mathrm{ref}}}{s_i}$$

$$\widetilde u_j=\frac{u_j}{r_j}$$

条件数差会导致 QP 求解器错误报告不可行、活跃集抖动或产生很大的对偶变量。缩放后仍需把输出正确映射回物理单位。

## 四十六、可微 QP 与训练

当活跃集局部不变且 KKT 系统非奇异时，QP 解对参数可做隐式微分。设 KKT 残差为：

$$F(z,\lambda,\theta)=0$$

则：

$$\frac{d(z,\lambda)}{d\theta}=-\left(\frac{\partial F}{\partial(z,\lambda)}\right)^{-1}\frac{\partial F}{\partial\theta}$$

这允许训练名义策略时考虑安全过滤器。但在活跃集切换、互补退化和不可行点附近，梯度可能不连续或不稳定，必须监控条件数和梯度裁剪。

## 四十七、验证指标

应同时报告安全、性能和数值指标：

1. 最小安全裕量：

$$h_{\min}=\min_t h(x(t))$$

2. CBF 最小残差：

$$r_{\mathrm{CBF}}=\min_t\left[L_fh+L_ghu+\alpha(h)\right]$$

3. CLF 违规量：

$$r_{\mathrm{CLF}}=\max_t\left[L_fV+L_gVu+cV-\delta\right]$$

4. QP 不可行率；
5. 松弛变量分布；
6. 控制修改幅度；
7. 控制变化率；
8. 求解时间的均值、分位数与最大值；
9. 模型扰动和观测噪声下的安全违规率。

只报告平均任务收益会掩盖少量但严重的安全失败。

## 四十八、测试矩阵

至少覆盖以下测试：

1. 名义动作安全时，过滤器保持动作不变；
2. 接近边界时，CBF 约束成为活跃约束；
3. 边界上最坏扰动下仍满足不向外条件；
4. CLF 与 CBF 冲突时，只松弛 CLF；
5. 输入饱和时正确报告不可行或降低收敛性能；
6. HOCBF 在高速接近状态下提前制动；
7. 多障碍夹角中检测联合不可行；
8. 延迟、噪声和动力学误差消融；
9. 离散动作集合为空时触发明确降级；
10. 求解器失败时禁止静默使用不安全动作。

## 四十九、常见错误

### 1. 把 CLF 当成安全保证

CLF 保证趋向目标，不保证途中避开障碍。

### 2. 给硬 CBF 随意加小权重松弛

一旦允许松弛，严格前向不变性结论不再成立。

### 3. 忽略相对阶

当 $L_gh=0$ 时，一阶 CBF 不能控制 $\dot h$，必须检查更高阶导数。

### 4. 只检查采样时刻

离散控制周期内仍可能穿越边界，需要 sampled-data 裕量或短时可达分析。

### 5. 使用错误符号

本文约定 $h\geq0$ 为安全。如果代码使用 $h\leq0$ 为安全，所有不等式必须整体重新推导。

### 6. 忽略 QP 状态

返回一个数值向量不代表求解成功，必须检查状态、原始残差和对偶残差。

### 7. 把模型内保证当成现实保证

未建模的技能跳变、碰撞响应、网络延迟和状态估计误差都可能破坏 CBF 假设。

## 五十、推荐接入架构

建议使用以下分层：

1. 上层策略产生任务目标和名义动作；
2. CLF 把任务目标转成收敛约束；
3. CBF/HOCBF 把碰撞、区域、资源和时序限制转成安全约束；
4. QP 在合法连续控制域内求最小修正；
5. 动作适配器映射到游戏原生动作；
6. 原生规则再次检查冷却、资源、碰撞和技能合法性；
7. 回放记录 $V$、$h$、约束残差、活跃集、松弛量和求解状态。

CBF 是安全过滤层，不应直接绕过原生动作掩码、联合规划、MAPF 或游戏规则。

## 五十一、最小实现路线

第一阶段实现二维单积分器避障 CBF-QP，使用解析几何测试安全边界。

第二阶段实现双积分器相对阶二 HOCBF，加入速度、加速度和制动距离测试。

第三阶段加入 CLF、输入约束、CLF 松弛和多个 CBF，建立可行性诊断。

第四阶段加入离散动作筛选、执行延迟和状态误差收紧。

第五阶段把 BRT 价值近似接为 CBF，并用回放对照无过滤、普通 CBF、HOCBF 和 BRT shield。

## 五十二、结论

CLF、CBF、CLF-CBF-QP 与 HOCBF 构成一套从稳定目标到安全控制的连续优化框架。CLF 描述期望下降方向，CBF 描述安全集合的前向不变性，QP 在每个控制周期解决二者与输入约束之间的冲突，HOCBF 则处理控制需要经过多阶动力学才能影响安全函数的问题。

这套方法的价值在于约束清晰、可在线求解、能与现有策略组合，并能通过残差和活跃集审计。但其保证始终依赖动力学、控制边界、状态估计、采样周期和求解器状态。实际游戏接入必须保留不可行分支、误差收紧和原生规则复核，不能把一个形式正确的 QP 自动等同于真实系统安全。

## 附录：符号表

- $x$：系统状态；
- $u$：控制输入；
- $f$：无控制漂移；
- $g$：控制作用矩阵；
- $V$：Control Lyapunov Function；
- $h$：Control Barrier Function；
- $\mathcal C$：安全集合；
- $L_f$、$L_g$：Lie 导数；
- $\alpha$：类 $\mathcal K$ 函数；
- $\delta$：CLF 松弛变量；
- $\psi_i$：HOCBF 递归变量；
- $u_{\mathrm{nom}}$：名义控制；
- $u^{\star}$：QP 输出控制。
