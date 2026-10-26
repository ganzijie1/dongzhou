# 动态风险度量、Nested CVaR 与 BSDE：时间一致风险控制的统一框架

## 摘要

静态风险指标把一个随机损失映射为单个数值，但多阶段决策还要回答：今天制定的风险排序，明天获得新信息后是否仍然认可？动态风险度量用条件风险算子描述随信息更新的风险评价；时间一致性要求未来风险判断与当前递归评价不矛盾；Nested CVaR 把单步条件 CVaR 沿决策树逐层复合，从而得到可以动态规划的尾部风险目标；Backward Stochastic Differential Equation（BSDE）则在连续时间中用向后随机方程定义非线性条件期望和动态风险。

本文采用“损失越大越差”的约定，系统介绍条件风险度量、公理、强时间一致性、风险包络、CVaR 对偶、Nested CVaR Bellman 方程、Markov 风险转移映射、策略优化、BSDE 与 $g$-expectation、二次和相干驱动、风险敏感 HJB，以及情景树、回归 Monte Carlo 和深度 BSDE 数值方法。最后给出其在 5v5 游戏多阶段团战、资源争夺、复活窗口和版本风险控制中的应用。

关键边界是：静态 CVaR、总累计损失 CVaR、逐阶段 Nested CVaR 和各阶段 CVaR 之和通常不同；Nested CVaR 虽具有递归时间一致性，但会改变风险含义，并可能对每个分支重复放大尾部事件。

## 一、概率空间与信息流

设过滤概率空间为：

$$\left(\Omega,\mathcal F,(\mathcal F_t)_{t=0}^T,\mathbb P\right)$$

$\mathcal F_t$ 表示时刻 $t$ 已知的信息，并满足：

$$\mathcal F_0\subseteq\mathcal F_1\subseteq\cdots\subseteq\mathcal F_T$$

终端随机损失记为：

$$X\in L^p(\mathcal F_T)$$

动态风险度量在每个时刻给出一个条件风险评价：

$$\rho_t(X)\in L^p(\mathcal F_t)$$

因此 $\rho_t(X)$ 本身是依赖当前信息的随机变量，而不是固定常数。

## 二、静态风险度量

静态风险度量是映射：

$$\rho:L^p(\mathcal F_T)\rightarrow\mathbb R$$

风险中性评价为：

$$\rho(X)=\mathbb E[X]$$

最坏情形评价为：

$$\rho(X)=\operatorname*{ess\,sup}X$$

风险度量的选择决定优化目标。它不是随机变量分布的唯一“真实风险”，而是决策者偏好和保证要求的数学编码。

## 三、单调性与现金平移不变性

若损失逐点不更大，则风险不应更高。单调性为：

$$X\leq Y\Longrightarrow\rho(X)\leq\rho(Y)$$

现金平移不变性为：

$$\rho(X+c)=\rho(X)+c$$

动态条件版本要求对任意 $m\in L^p(\mathcal F_t)$：

$$\rho_t(X+m)=\rho_t(X)+m$$

这里 $m$ 在时刻 $t$ 已知，因此可以逐状态从未来风险中分离出来。

## 四、凸风险度量

凸性为：

$$\rho(\lambda X+(1-\lambda)Y)\leq\lambda\rho(X)+(1-\lambda)\rho(Y)$$

其中：

$$0\leq\lambda\leq1$$

它表达分散化不应增加风险。若还满足正齐次性：

$$\rho(cX)=c\rho(X)\quad(c\geq0)$$

以及次可加性：

$$\rho(X+Y)\leq\rho(X)+\rho(Y)$$

则属于相干风险度量。

## 五、条件风险度量

条件风险算子写为：

$$\rho_t:L^p(\mathcal F_T)\rightarrow L^p(\mathcal F_t)$$

条件单调性为：

$$X\leq Y\Longrightarrow\rho_t(X)\leq\rho_t(Y)$$

条件凸性允许权重 $\lambda$ 是 $\mathcal F_t$ 可测随机变量：

$$\rho_t(\lambda X+(1-\lambda)Y)\leq\lambda\rho_t(X)+(1-\lambda)\rho_t(Y)$$

条件风险评价随当前状态、历史、观察和信念变化。

## 六、动态风险度量

动态风险度量是一族条件算子：

$$\boldsymbol\rho=(\rho_0,\rho_1,\ldots,\rho_T)$$

通常归一化为：

$$\rho_t(0)=0$$

在终端时刻，若损失已经完全可知：

$$\rho_T(X)=X$$

不同时间的风险算子必须满足某种一致性，才能支持可靠的序贯决策。

## 七、时间一致性

强时间一致性的一种排序定义是：若在时刻 $t+1$ 判断 $X$ 不比 $Y$ 更危险，则时刻 $t$ 也应保持该排序：

$$\rho_{t+1}(X)\leq\rho_{t+1}(Y)\Longrightarrow\rho_t(X)\leq\rho_t(Y)$$

在正规、现金平移不变等条件下，它通常等价于递归关系：

$$\rho_t(X)=\rho_t(\rho_{t+1}(X))$$

若使用奖励而非损失，或把风险定义成资本需求的负号，递归式符号会相应变化。

## 八、动态不一致的来源

在时刻零直接最小化终端总损失的静态 CVaR：

$$\min_\pi\operatorname{CVaR}_\alpha\left(\sum_{t=0}^{T-1}C_t^\pi+C_T^\pi\right)$$

通常不满足强时间一致性。进入某个低概率分支后，条件分布和尾部样本集合会改变，原计划的后续动作可能不再最优。

这种重新优化不是计算错误，而是静态非线性风险函数与信息更新不兼容的结果。

## 九、VaR

对损失 $X$，置信水平 $\alpha\in(0,1)$ 的 Value-at-Risk 定义为：

$$\operatorname{VaR}_\alpha(X)=\inf\{z:\mathbb P(X\leq z)\geq\alpha\}$$

VaR 给出分位点，但不描述超过分位点后的损失大小，并且一般不具凸性或次可加性。

离散分布存在原子时，分位点可能不唯一或出现跳跃，必须采用明确的左、右分位数约定。

## 十、CVaR 的优化表示

Conditional Value-at-Risk 又称 Expected Shortfall。对损失 $X$：

$$\operatorname{CVaR}_\alpha(X)=\inf_{\eta\in\mathbb R}\left\{\eta+\frac{1}{1-\alpha}\mathbb E[(X-\eta)_+]\right\}$$

其中：

$$x_+=\max\{x,0\}$$

在连续分布下，最优 $\eta$ 可取 $\operatorname{VaR}_\alpha(X)$。离散分布中必须正确处理分位点原子的分数质量。

## 十一、CVaR 的风险包络

CVaR 是相干风险度量，并有对偶表示：

$$\operatorname{CVaR}_\alpha(X)=\sup_{\xi\in\mathcal U_\alpha}\mathbb E[\xi X]$$

风险包络为：

$$\mathcal U_\alpha=\left\{\xi:0\leq\xi\leq\frac{1}{1-\alpha},\ \mathbb E[\xi]=1\right\}$$

对手可以重新加权概率，但任一样本权重放大倍数不超过 $1/(1-\alpha)$。这给出 CVaR 的分布鲁棒解释。

## 十二、条件 CVaR

给定时刻 $t$ 信息，条件 CVaR 可写为：

$$\operatorname{CVaR}_{\alpha,t}(X)=\operatorname*{ess\,inf}_{\eta\in L^p(\mathcal F_t)}\left\{\eta+\frac{1}{1-\alpha}\mathbb E[(X-\eta)_+\mid\mathcal F_t]\right\}$$

这里阈值 $\eta$ 可以依赖当前信息。它的条件风险包络满足：

$$0\leq\xi\leq\frac{1}{1-\alpha}$$

$$\mathbb E[\xi\mid\mathcal F_t]=1$$

## 十三、一步风险映射

多阶段模型常定义从 $t+1$ 风险变量映射到 $t$ 的一步条件风险算子：

$$\mathcal R_t:L^p(\mathcal F_{t+1})\rightarrow L^p(\mathcal F_t)$$

期望风险映射为：

$$\mathcal R_t(Z)=\mathbb E[Z\mid\mathcal F_t]$$

CVaR 风险映射为：

$$\mathcal R_t(Z)=\operatorname{CVaR}_{\alpha,t}(Z)$$

一步映射是构造时间一致动态风险度量的基本组件。

## 十四、递归动态风险

给定阶段损失 $C_t$，递归风险到成本定义为：

$$V_T=C_T$$

$$V_t=C_t+\mathcal R_t(V_{t+1})$$

展开得到：

$$V_0=C_0+\mathcal R_0\left(C_1+\mathcal R_1\left(\cdots+C_{T-1}+\mathcal R_{T-1}(C_T)\right)\right)$$

这种嵌套结构满足与所选一步算子相对应的递归时间一致性。

## 十五、Nested CVaR

若每一步都选择条件 CVaR，则：

$$V_t=C_t+\operatorname{CVaR}_{\alpha_t,t}(V_{t+1})$$

完整目标为：

$$C_0+\operatorname{CVaR}_{\alpha_0,0}\left(C_1+\operatorname{CVaR}_{\alpha_1,1}\left(\cdots+C_T\right)\right)$$

风险水平可以随时间和状态变化：

$$\alpha_t=\alpha(t,S_t)$$

但状态依赖风险水平必须在策略设计前固定，或作为扩展状态的一部分处理。

## 十六、三种 CVaR 目标并不相同

总累计损失的静态 CVaR 为：

$$\operatorname{CVaR}_\alpha\left(\sum_tC_t\right)$$

逐阶段 CVaR 之和为：

$$\sum_t\operatorname{CVaR}_\alpha(C_t)$$

Nested CVaR 为：

$$C_0+\operatorname{CVaR}_{\alpha,0}\left(C_1+\operatorname{CVaR}_{\alpha,1}(\cdots)\right)$$

除特殊独立性或退化条件外，三者数值、最优策略和风险解释都不同。

## 十七、Nested CVaR 的风险包络树

每个节点的一步条件 CVaR 都允许局部概率扭曲。沿一条路径，联合似然比是各阶段扭曲的乘积：

$$\Xi_T=\prod_{t=0}^{T-1}\xi_{t+1}$$

其中：

$$0\leq\xi_{t+1}\leq\frac{1}{1-\alpha_t}$$

$$\mathbb E[\xi_{t+1}\mid\mathcal F_t]=1$$

因此 Nested CVaR 对应一个 rectangular 的动态风险包络，允许对手在每个信息节点重新选择局部概率扭曲。

## 十八、Rectangularity 与时间一致性

动态风险包络若能按历史逐阶段拼接，则称具有 rectangularity。直观上，对手在一个分支选择的条件分布，不限制其在其他分支选择合法条件分布。

Rectangularity 使最坏分布优化可以递归分解：

$$\sup_{Q\in\mathcal Q}\mathbb E_Q[X]=\sup_{q_0}\mathbb E_{q_0}\left[\sup_{q_1}\mathbb E_{q_1}[\cdots X]\right]$$

非 rectangular 模糊集合一般会破坏 Bellman 原理，需要保留额外历史或全局分布约束。

## 十九、Markov 风险转移映射

在 Markov 决策过程中，给定状态 $s$、动作 $a$ 和下一状态价值 $V(s')$，风险转移映射记为：

$$\sigma(V,s,a)=\rho_{P(\cdot\mid s,a)}(V(S'))$$

期望映射为：

$$\sigma(V,s,a)=\sum_{s'}P(s'\mid s,a)V(s')$$

CVaR 映射为：

$$\sigma_\alpha(V,s,a)=\operatorname{CVaR}_{\alpha,P(\cdot\mid s,a)}(V(S'))$$

它把动态风险问题压缩到当前状态、动作和下一状态价值。

## 二十、Nested CVaR Bellman 方程

有限时域损失最小化满足：

$$V_T(s)=g(s)$$

$$V_t(s)=\min_{a\in A(s)}\left\{c_t(s,a)+\sigma_{\alpha_t}(V_{t+1},s,a)\right\}$$

最优策略为：

$$\pi_t^*(s)\in\arg\min_{a\in A(s)}\left\{c_t(s,a)+\sigma_{\alpha_t}(V_{t+1},s,a)\right\}$$

该递推依赖 Markov 风险映射和 rectangular 条件风险包络。

## 二十一、离散 CVaR 的线性规划

若下一状态取值为 $v_j$，概率为 $p_j$，CVaR 可写成：

$$\min_{\eta,z}\ \eta+\frac{1}{1-\alpha}\sum_jp_jz_j$$

约束为：

$$z_j\geq v_j-\eta$$

$$z_j\geq0$$

也可用风险包络求对偶 LP：

$$\max_q\sum_jq_jv_j$$

$$0\leq q_j\leq\frac{p_j}{1-\alpha},\qquad\sum_jq_j=1$$

## 二十二、策略依赖风险

若策略是随机策略：

$$\pi_t(a\mid s)$$

需要先明确风险是在动作随机化之前还是之后评价。若随机种子是控制器已知信息，动作条件风险与外部观察者的混合风险不同。

一种常见建模是把随机动作和下一状态一起纳入一步结果：

$$Z=c(s,A)+V(S')$$

再对联合分布计算条件风险。风险度量的非线性使“先对动作求期望再算风险”和“先算各动作风险再混合”通常不同。

## 二十三、折扣无限时域

对折扣因子 $\gamma\in(0,1)$，Markov 动态风险 Bellman 算子可写为：

$$\mathcal TV(s)=\min_a\left\{c(s,a)+\gamma\sigma(V,s,a)\right\}$$

若风险转移映射在上确界范数下非扩张，则：

$$\|\mathcal TV-\mathcal TW\|_\infty\leq\gamma\|V-W\|_\infty$$

从而获得唯一不动点和价值迭代收敛。缺少单调性、平移性质或有界成本时，需要另行分析。

## 二十四、风险预算与状态扩展

若希望全局控制尾部概率或 CVaR 阈值，可以把剩余风险预算加入状态：

$$\widetilde S_t=(S_t,B_t)$$

预算按决策与观察更新：

$$B_{t+1}=\Psi(B_t,S_t,A_t,S_{t+1})$$

状态扩展可以恢复动态规划，但会增加维度。仅在终点检查预算通常不能保证所有历史分支都可行。

## 二十五、动态风险约束

风险约束可写为：

$$\rho_t\left(\sum_{k=t}^TC_k\right)\leq b_t$$

若约束要求在每个历史节点成立，则是条件风险约束；若只在时刻零成立，则是预承诺约束。两者可行策略集不同。

对条件约束，预算 $b_t$ 必须是 $\mathcal F_t$ 可测，并与后续策略共同设计。

## 二十六、BSDE 的基本形式

连续时间 BSDE 由终端条件 $\xi$ 和驱动函数 $g$ 定义：

$$Y_t=\xi+\int_t^Tg(s,Y_s,Z_s)ds-\int_t^TZ_s\,dW_s$$

微分形式为：

$$dY_t=-g(t,Y_t,Z_t)dt+Z_t\,dW_t$$

终端条件为：

$$Y_T=\xi$$

未知过程 $(Y,Z)$ 从终端向前求解；$Z$ 同时描述鞅表示和对 Brownian 风险的敏感度。

## 二十七、线性 BSDE 与条件期望

当驱动为零：

$$g(t,y,z)=0$$

BSDE 解为：

$$Y_t=\mathbb E[\xi\mid\mathcal F_t]$$

因此 BSDE 是条件期望的非线性推广。非零驱动会引入风险厌恶、模型不确定性、贴现或控制成本。

## 二十八、g-expectation

由 BSDE 定义非线性条件期望：

$$\mathcal E_{t,T}^g[\xi]=Y_t$$

若把 $\xi$ 视为未来损失，可定义动态风险：

$$\rho_t^g(\xi)=\mathcal E_{t,T}^g[\xi]$$

在适当驱动条件下，$g$-expectation 满足单调性、时间一致性和塔式性质：

$$\mathcal E_{s,T}^g[\xi]=\mathcal E_{s,t}^g\left[\mathcal E_{t,T}^g[\xi]\right]$$

## 二十九、BSDE 比较定理

若终端条件和驱动满足适当 Lipschitz、可积和偏序条件，并且：

$$\xi^1\leq\xi^2$$

$$g_1(t,y,z)\leq g_2(t,y,z)$$

则对应解通常满足：

$$Y_t^1\leq Y_t^2$$

比较定理是 BSDE 动态风险单调性的基础。多维 BSDE 中比较原理更受限制，不能直接沿用一维结论。

## 三十、凸 BSDE 风险度量

若驱动 $g(t,z)$ 对 $z$ 凸、与 $y$ 无关并满足：

$$g(t,0)=0$$

则可得到平移不变的凸动态风险度量。若 $g$ 对 $z$ 还是正齐次的，则风险度量可能具有相干性。

驱动的凸共轭为：

$$g^*(t,q)=\sup_z\{q\cdot z-g(t,z)\}$$

它将 BSDE 风险解释为对替代漂移测度的惩罚最坏情形期望。

## 三十一、熵风险与二次 BSDE

熵风险度量为：

$$\rho_t^{\theta}(X)=\frac{1}{\theta}\log\mathbb E[e^{\theta X}\mid\mathcal F_t]$$

对应二次驱动：

$$g(z)=\frac{\theta}{2}\|z\|^2$$

风险参数 $\theta\gt0$ 时，大损失被指数放大。二次 BSDE 的存在唯一性需要比普通 Lipschitz BSDE 更强的终端可积性或有界性条件。

## 三十二、相干驱动与最坏漂移

若不确定漂移集合为 $\Theta_t$，可取支持函数驱动：

$$g(t,z)=\sup_{q\in\Theta_t}q\cdot z$$

对应动态风险可解释为一族等价概率测度上的最坏条件期望：

$$\rho_t(X)=\operatorname*{ess\,sup}_{Q\in\mathcal Q_t}\mathbb E_Q[X\mid\mathcal F_t]$$

动态集合 $\mathcal Q_t$ 的稳定拼接性质对应离散时间的 rectangularity。

## 三十三、受控扩散与 BSDE

设受控状态满足：

$$dX_t=b(t,X_t,a_t)dt+\sigma(t,X_t,a_t)dW_t$$

给定控制 $a$，风险价值可由 BSDE 表示：

$$Y_t=h(X_T)+\int_t^T\left[c(s,X_s,a_s)+g(s,Z_s)\right]ds-\int_t^TZ_s\,dW_s$$

控制问题为：

$$V(t,x)=\inf_aY_t^{t,x,a}$$

这把运行损失、终端损失和动态风险驱动统一到一个向后递推中。

## 三十四、BSDE 与风险敏感 HJB

若 Markov 解满足：

$$Y_t=V(t,X_t)$$

则通常有：

$$Z_t=\sigma(t,X_t,a_t)^\top D_xV(t,X_t)$$

对应 HJB 为：

$$-\partial_tV=\inf_a\left\{c+b\cdot D_xV+\frac{1}{2}\operatorname{tr}(\sigma\sigma^\top D_x^2V)+g(\sigma^\top D_xV)\right\}$$

对熵驱动 $g(z)=\theta\|z\|^2/2$，得到风险敏感 HJB 的梯度平方项。

## 三十五、FBSDE

当状态向前、价值向后耦合时形成 Forward-Backward SDE：

$$dX_t=b(t,X_t,Y_t,Z_t)dt+\sigma(t,X_t,Y_t,Z_t)dW_t$$

$$dY_t=-g(t,X_t,Y_t,Z_t)dt+Z_t\,dW_t$$

$$Y_T=h(X_T)$$

FBSDE 可表示随机控制、均衡、均值场博弈和随机最大值原理。强耦合系统可能只在短时间或单调性条件下有唯一解。

## 三十六、反射 BSDE

若风险价值必须保持在障碍 $L_t$ 之上，可使用反射 BSDE：

$$Y_t=\xi+\int_t^Tg(s,Y_s,Z_s)ds+K_T-K_t-\int_t^TZ_s\,dW_s$$

约束为：

$$Y_t\geq L_t$$

最小反射条件为：

$$\int_0^T(Y_t-L_t)dK_t=0$$

它与最优停止、Snell 包络和带安全边界的风险控制相连。

## 三十七、离散情景树算法

在有限情景树上，从叶节点向根节点递推。对节点 $n$ 的子节点损失 $V_m$ 和条件概率 $p_{m\mid n}$，求：

$$V_n=c_n+\min_\eta\left\{\eta+\frac{1}{1-\alpha_n}\sum_{m\in\operatorname{child}(n)}p_{m\mid n}(V_m-\eta)_+\right\}$$

若节点含动作，则对每个动作先计算风险，再选最小值。该算法对树规模线性，但情景树本身随时间指数增长。

## 三十八、Nested CVaR 的线性规划展开

在每个节点引入阈值 $\eta_n$ 和超额变量 $z_{nm}$：

$$z_{nm}\geq V_m-\eta_n$$

$$z_{nm}\geq0$$

节点风险为：

$$R_n=\eta_n+\frac{1}{1-\alpha_n}\sum_mp_{m\mid n}z_{nm}$$

若动态和成本都是线性的，可以把整个有限情景树问题展开为大型 LP 或 MILP。

## 三十九、回归 Monte Carlo BSDE

时间离散步长为 $\Delta t$。一个基本向后格式为：

$$Z_k\approx\frac{1}{\Delta t}\mathbb E[Y_{k+1}\Delta W_k\mid\mathcal F_k]$$

$$Y_k\approx\mathbb E[Y_{k+1}+g(t_k,Y_{k+1},Z_k)\Delta t\mid\mathcal F_k]$$

条件期望可用线性基函数、树模型或神经网络回归。回归误差会逐步向后传播，应使用独立验证路径和多时间网格检查。

## 四十、Deep BSDE 方法

Deep BSDE 将初始 $Y_0$ 和过程 $Z_t$ 参数化，通过向前模拟最小化终端误差：

$$\mathcal L(\theta)=\mathbb E\left[|Y_T^\theta-h(X_T)|^2\right]$$

离散传播为：

$$Y_{k+1}=Y_k-g(t_k,Y_k,Z_k)\Delta t+Z_k\Delta W_k$$

小终端损失不自动保证策略最优或风险估计校准，还需检查 PDE/BSDE 残差、跨步长稳定性和独立样本表现。

## 四十一、Nested CVaR 的保守性

当每一阶段都对最坏尾部重新加权时，路径权重上界可能随时间相乘：

$$\Xi_T\leq\prod_{t=0}^{T-1}\frac{1}{1-\alpha_t}$$

长时域和高 $\alpha$ 会导致极端保守、价值梯度集中和策略冻结。可以使用随时域调整的风险水平、风险预算、混合期望—CVaR 或其他动态风险映射。

## 四十二、混合动态风险

期望与 CVaR 的凸组合为：

$$\mathcal R_t(Z)=(1-\lambda_t)\mathbb E[Z\mid\mathcal F_t]+\lambda_t\operatorname{CVaR}_{\alpha_t,t}(Z)$$

其中：

$$0\leq\lambda_t\leq1$$

只要每一步算子满足相应条件并按嵌套方式组合，仍可保持递归时间一致性。

## 四十三、风险偏好的校准

$\alpha$ 不是“越大越安全”的免费参数。提高 $\alpha$ 会减少有效尾部样本并增大估计方差。经验尾部样本量约为：

$$n_{\mathrm{tail}}\approx n(1-\alpha)$$

应同时报告：

$$\mathbb E[X],\quad\operatorname{VaR}_\alpha(X),\quad\operatorname{CVaR}_\alpha(X),\quad\rho_0^{\mathrm{nested}}(X)$$

参数应通过独立回放、压力场景和策略性能权衡选择。

## 四十四、5v5 游戏的多阶段风险

一场团战可分为集结、试探、开团、集火、追击和撤退阶段。阶段损失可定义为：

$$C_t=w_1D_t+w_2H_t+w_3O_t+w_4P_t$$

$D_t$ 表示伤亡，$H_t$ 表示血量或技能资源损失，$O_t$ 表示地图目标损失，$P_t$ 表示阵型破坏。

Nested CVaR 目标为：

$$V_t(s)=\min_a\left\{C_t(s,a)+\operatorname{CVaR}_{\alpha_t}\left(V_{t+1}(S')\mid s,a\right)\right\}$$

它会优先规避在每个阶段条件下都可能造成严重后果的行动。

## 四十五、资源争夺与条件风险

主宰或关键据点决策具有分支结构：成功、被抢、换资源、遭埋伏。静态终局 CVaR 可能在进入某个分支后改变原计划；Nested CVaR 会在每个已知分支重新评价后续损失。

可把风险水平与复活时间和经济差关联：

$$\alpha_t=\operatorname{clip}(\alpha_0+k_1\Delta\mathrm{gold}_t+k_2\Delta\mathrm{respawn}_t,\alpha_{\min},\alpha_{\max})$$

该规则必须预先声明并做回放外验证，否则会产生数据驱动的风险口径漂移。

## 四十六、团队风险与个体风险

团队风险不等于各英雄风险之和：

$$\operatorname{CVaR}_\alpha\left(\sum_iL_i\right)\neq\sum_i\operatorname{CVaR}_\alpha(L_i)$$

共同控制链、范围伤害和阵型崩溃会产生强尾部依赖。应直接建模联合损失或使用包含尾相关的情景树。

若只优化单个英雄 CVaR，可能得到每人局部保守但团队目标失败的策略。

## 四十七、与现有游戏模型的组合

P35 的熵风险和风险敏感 DP 适合指数尾部；P29 的 EVT 和重要性采样用于估计极端场景；P36 的概率模型检测验证阈值性质；本模块的 Nested CVaR 负责时间一致的多阶段尾部控制；BSDE 负责连续时间非线性风险传播。

推荐流程是：先用回放建立阶段模型，再用 EVT/重要性采样补充尾部情景，随后训练 Nested CVaR 或 BSDE 策略，最后用概率模型检测和独立回放验证。

## 四十八、实现检查

至少检查：损失和奖励符号是否统一；$\alpha$ 是置信水平还是尾部质量；离散原子是否正确分割；风险算子是否条件化于正确过滤；风险包络是否 rectangular；随机策略的风险评价顺序是否明确；情景树概率是否归一化；BSDE 驱动是否满足存在唯一性条件；训练与验证路径是否独立。

Bellman 残差可写为：

$$r_t(s)=\left|V_t(s)-\min_a\{c_t(s,a)+\sigma(V_{t+1},s,a)\}\right|$$

残差小只说明近似解与所写模型一致，不证明情景模型与真实游戏一致。

## 四十九、常见误区

第一，把静态累计损失 CVaR 称为时间一致动态风险。

第二，把每阶段 CVaR 相加当成 Nested CVaR。

第三，忽略离散分位点原子的分数质量。

第四，把更高 $\alpha$ 直接解释为更好的安全性，而不报告性能损失和尾部样本量。

第五，在随机策略中混淆“风险后混合”与“混合后算风险”。

第六，把 BSDE 的 $Z_t$ 简单解释为控制动作；它首先是鞅表示和风险敏感度过程。

第七，在二次 BSDE 中忽略终端损失的指数可积性。

第八，用训练情景树上的低风险替代真实版本和真实玩家分布下的外部验证。

## 五十、结论

动态风险度量把风险评价变成随信息流更新的条件算子；时间一致性通过递归结构保证当前和未来风险排序协调；Nested CVaR 用逐节点条件尾部风险建立可动态规划的离散时间控制；BSDE 和 $g$-expectation 则在连续时间提供非线性条件期望、凸或相干风险以及风险敏感 HJB 的统一表示。

实际应用必须明确风险对象、信息过滤、嵌套顺序和对偶风险包络。Nested CVaR 解决了静态 CVaR 的预承诺问题，但会改变风险语义并可能过度保守；BSDE 提供强大连续时间工具，但依赖驱动正则性、终端可积性和可靠数值求解。二者都应与均值、分位数、失败概率和独立压力回放共同报告。
