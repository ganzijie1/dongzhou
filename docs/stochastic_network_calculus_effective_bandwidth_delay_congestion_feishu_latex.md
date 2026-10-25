# 随机网络演算：Network Calculus、有效带宽、延迟与拥塞概率界

## 摘要

Network Calculus 用累计到达过程、累计离开过程和服务曲线分析队列系统，为 backlog、延迟和端到端服务质量提供可组合上界。确定性网络演算适合硬实时与最坏情形分析；随机网络演算允许到达和服务违反曲线约束，但要求给出明确的违约概率函数。有效带宽通过指数矩把突发流量压缩成与风险参数相关的等效速率，有效容量则描述随机服务在指数风险尺度下能够稳定支持的速率。二者结合 Chernoff 方法，可以构造队列积压、延迟和拥塞概率的指数界。

本文统一介绍 min-plus 代数、到达曲线、服务曲线、串联系统、剩余服务、随机包络、有效带宽、有效容量、鞅与 Chernoff 界，并说明有限时间界、稳态界和大偏差近似之间的区别。最后给出它们在 5v5 游戏网络、推理服务、帧同步、命令队列和多阶段实时处理链中的应用方法。

## 一、累计过程

设 $A(t)$ 表示区间 $[0,t]$ 内累计到达量，$D(t)$ 表示累计离开量。对 $0\leq s\leq t$，定义区间增量：

$$A(s,t)=A(t)-A(s)$$

$$D(s,t)=D(t)-D(s)$$

累计过程通常满足非负、右连续且单调不减。单位可以是 bit、packet、request、frame 或计算任务，但同一公式中的到达与服务必须使用一致单位。

## 二、Backlog 与虚拟延迟

时刻 $t$ 的 backlog 为：

$$B(t)=A(t)-D(t)$$

虚拟延迟定义为当前已到达数据全部离开所需的最短等待时间：

$$W(t)=\inf\{d\geq0:A(t)\leq D(t+d)\}$$

在 FIFO 流体系统中，$W(t)$ 对应队首虚拟等待；在非 FIFO、分片或优先级系统中，单流实际包延迟与聚合虚拟延迟需要另外建立关系。

## 三、min-plus 卷积

对两个非负函数 $f$ 与 $g$，min-plus 卷积定义为：

$$\left(f\otimes g\right)(t)=\inf_{0\leq s\leq t}\{f(s)+g(t-s)\}$$

min-plus 去卷积定义为：

$$\left(f\oslash g\right)(t)=\sup_{u\geq0}\{f(t+u)-g(u)\}$$

网络演算把普通线性系统中的加法和卷积替换为 min-plus 运算，使到达、服务和离开关系可以组合计算。

## 四、确定性到达曲线

若对任意 $0\leq s\leq t$ 都有：

$$A(s,t)\leq\alpha(t-s)$$

则称 $\alpha$ 是到达过程 $A$ 的到达曲线。常见 token-bucket 曲线为：

$$\alpha(t)=b+rt\quad(t\gt0)$$

其中 $b$ 是允许的最大突发量，$r$ 是长期速率。若需要严格处理 $t=0$，应根据累计过程约定设置 $\alpha(0)$。

## 五、确定性服务曲线

若系统对任意 $t\geq0$ 保证：

$$D(t)\geq(A\otimes\beta)(t)$$

则称 $\beta$ 是系统的最小服务曲线。常见 rate-latency 服务曲线为：

$$\beta(t)=R(t-T)_+$$

其中：

$$x_+=\max\{x,0\}$$

$R$ 是保证服务率，$T$ 是固定处理或调度延迟。

## 六、最大服务曲线与输出约束

最小服务曲线给出至少能提供多少服务。若还存在最大服务曲线 $\gamma$，可写为：

$$D(s,t)\leq(A\otimes\gamma)(s,t)$$

在常见时不变表示中，输出到达曲线可由去卷积得到：

$$\alpha_{\mathrm{out}}=\alpha\oslash\beta$$

输出包络对于串联系统逐节点分析很重要，但去卷积上界可能逐跳变松。

## 七、Backlog 确定性界

到达曲线为 $\alpha$、服务曲线为 $\beta$ 时，最大垂直偏差定义为：

$$v(\alpha,\beta)=\sup_{t\geq0}\{\alpha(t)-\beta(t)\}$$

在标准因果和零初始 backlog 条件下：

$$B(t)\leq v(\alpha,\beta)$$

若 $v(\alpha,\beta)=+\infty$，说明所选到达与服务曲线无法给出有限 backlog 保证，通常是长期到达速率不小于保证服务率。

## 八、延迟确定性界

最大水平偏差定义为：

$$h(\alpha,\beta)=\sup_{s\geq0}\inf\{\tau\geq0:\alpha(s)\leq\beta(s+\tau)\}$$

在 FIFO 等相应条件下：

$$W(t)\leq h(\alpha,\beta)$$

垂直偏差控制缓存需求，水平偏差控制延迟。二者的几何意义不同，不能简单用同一个数值替换。

## 九、Token-bucket 与 Rate-latency 示例

设：

$$\alpha(t)=b+rt$$

$$\beta(t)=R(t-T)_+$$

若 $r\leq R$，backlog 界为：

$$B_{\max}\leq b+rT$$

延迟界为：

$$W_{\max}\leq T+\frac{b}{R}$$

如果 $r\gt R$，长期 backlog 无界。平均速率条件 $r\lt R$ 是获得有限界的基础，但实际界还由突发量 $b$ 和固定延迟 $T$ 决定。

## 十、串联系统

若数据依次经过服务曲线为 $\beta_1,\ldots,\beta_n$ 的节点，则端到端服务曲线为：

$$\beta_{\mathrm{net}}=\beta_1\otimes\beta_2\otimes\cdots\otimes\beta_n$$

对 rate-latency 节点：

$$\beta_i(t)=R_i(t-T_i)_+$$

可得到保守端到端曲线：

$$\beta_{\mathrm{net}}(t)=R_{\min}(t-T_{\mathrm{sum}})_+$$

其中：

$$R_{\min}=\min_iR_i$$

$$T_{\mathrm{sum}}=\sum_iT_i$$

这体现“速率取瓶颈、延迟相加”。

## 十一、Pay Bursts Only Once

若直接逐跳重新套用同一个输入突发上界，可能在每一跳都重复支付 burst，造成极松延迟界。端到端 min-plus 卷积在适当条件下只支付一次初始突发：

$$D_n\geq A\otimes\beta_1\otimes\cdots\otimes\beta_n$$

但交叉流、重整形、非 FIFO 调度和节点相关性会破坏简单形式，需要显式分析每跳输出包络与剩余服务。

## 十二、多路复用与剩余服务

设总服务曲线为 $\beta$，交叉流到达曲线为 $\alpha_c$。在任意复用的常见保守模型下，目标流可获得剩余服务：

$$\beta_{\mathrm{lo}}(t)=\left[\beta(t)-\alpha_c(t)\right]_+$$

严格优先级、加权公平队列和轮询调度可推导更精确的剩余服务曲线。必须说明调度策略，不能只从链路总容量推出单流时延保证。

## 十三、确定性界的局限

硬到达曲线必须覆盖所有合法轨迹。对突发随机流量，它可能由极端样本决定，导致容量与缓存估计过度保守。确定性界也不会自动利用统计复用收益。

随机网络演算允许：

$$\mathbb P(\mathrm{bound\ violation})\leq\varepsilon$$

代价是必须明确随机假设、时间范围、依赖结构和违约函数，且结果不再是零失败保证。

## 十四、随机到达包络

一种逐区间随机到达约束为：

$$\mathbb P\left(A(s,t)-\alpha(t-s)\gt x\right)\leq f(x)$$

其中 $f(x)$ 随 $x$ 下降。更强的虚 backlog 中心包络可写为：

$$\mathbb P\left(\sup_{0\leq s\leq t}\{A(s,t)-\alpha(t-s)\}\gt x\right)\leq f(x)$$

第二种形式已经控制同一终点 $t$ 的所有起点，因此更适合直接推导 backlog 界。不同随机包络定义不能不加转换地混用。

## 十五、随机服务曲线

一种随机最小服务曲线定义为：

$$\mathbb P\left((A\otimes\beta)(t)-D(t)\gt x\right)\leq g(x)$$

$g(x)$ 是服务违约函数。无线衰落、共享计算资源、抢占调度和随机故障都可以造成服务随机性。

若到达与服务共享环境状态，则违约事件可能强相关。只使用边际 $f$ 和 $g$ 时，通常只能得到不依赖独立性的保守组合界。

## 十六、随机 Backlog 界

设确定性几何偏差为：

$$b_0=v(\alpha,\beta)$$

若到达和服务分别具有违约函数 $f$ 与 $g$，常见的独立性无关分裂界为：

$$\mathbb P(B(t)\gt b_0+x)\leq\inf_{0\leq y\leq x}\{f(y)+g(x-y)\}$$

右侧是对误差预算 $x$ 的最优分配。若有额外独立性或鞅结构，可以获得更紧的乘积、卷积或指数界。

## 十七、随机延迟界

设确定性水平偏差为：

$$d_0=h(\alpha,\beta)$$

在 FIFO 和所用随机曲线定义支持样本路径控制的条件下，可以得到形式为：

$$\mathbb P(W(t)\gt d_0+d)\leq\varepsilon_W(d)$$

$\varepsilon_W$ 由到达和服务违约函数组合而成。具体横向偏移需要考虑服务曲线逆映射，不能把 backlog 阈值 $x$ 直接当成时间阈值 $d$。

## 十八、指数矩与 Chernoff 界

对任意随机变量 $X$ 和 $\theta\gt0$：

$$\mathbb P(X\geq x)\leq e^{-\theta x}\mathbb E[e^{\theta X}]$$

优化 $\theta$ 得到：

$$\mathbb P(X\geq x)\leq\inf_{\theta\gt0}\exp\left(-\theta x+\log\mathbb E[e^{\theta X}]\right)$$

随机网络演算常用这一方法把流量与服务的矩母函数转换成指数违约函数。

## 十九、有效带宽

对时间区间长度 $t$，到达过程的有限时域有效带宽定义为：

$$a(\theta,t)=\frac{1}{\theta t}\log\mathbb E[e^{\theta A(0,t)}]$$

长期有效带宽定义为：

$$a(\theta)=\limsup_{t\to\infty}\frac{1}{\theta t}\log\mathbb E[e^{\theta A(0,t)}]$$

$\theta$ 是 QoS 风险参数。若二阶矩存在，小 $\theta$ 下有：

$$a(\theta,t)=\frac{\mathbb E[A(0,t)]}{t}+\frac{\theta}{2t}\operatorname{Var}(A(0,t))+O(\theta^2)$$

因此有效带宽同时反映平均速率与突发方差。

## 二十、有效带宽的概率意义

由 Chernoff 界：

$$\mathbb P(A(0,t)\geq ct)\leq\exp\left[-\theta t(c-a(\theta,t))\right]$$

只要：

$$c\gt a(\theta,t)$$

右侧就随 $t$ 指数下降。对给定容量 $c$，可对 $\theta$ 优化：

$$I(c)=\sup_{\theta\geq0}\theta(c-a(\theta))$$

$I(c)$ 是相应的大偏差候选速率，但严格极限还需要 Gärtner–Ellis 等条件。

## 二十一、独立流的聚合

若 $n$ 个到达流在所考察时间尺度上相互独立，则聚合到达量为：

$$A_{\mathrm{agg}}(0,t)=\sum_{i=1}^nA_i(0,t)$$

指数矩可分解：

$$\mathbb E[e^{\theta A_{\mathrm{agg}}}]=\prod_{i=1}^n\mathbb E[e^{\theta A_i}]$$

因此有效带宽相加：

$$a_{\mathrm{agg}}(\theta,t)=\sum_{i=1}^na_i(\theta,t)$$

若流量因同一比赛阶段、广播事件或公共网络状态而相关，直接相加会低估尾部风险。

## 二十二、有效容量

对随机服务过程 $S(0,t)$，有效容量定义为：

$$c_{\mathrm{eff}}(\theta,t)=-\frac{1}{\theta t}\log\mathbb E[e^{-\theta S(0,t)}]$$

长期形式为：

$$c_{\mathrm{eff}}(\theta)=\liminf_{t\to\infty}-\frac{1}{\theta t}\log\mathbb E[e^{-\theta S(0,t)}]$$

平均意义稳定通常只需平均到达小于平均服务；指数 QoS 条件更强，典型要求存在 $\theta\gt0$ 使：

$$a(\theta)\lt c_{\mathrm{eff}}(\theta)$$

## 二十三、常数服务下的 Backlog 指数界

考虑离散时间、平稳独立增量到达和每时隙常数服务 $C$。定义单时隙对数矩母函数：

$$\Lambda_A(\theta)=\log\mathbb E[e^{\theta A_1}]$$

若存在 $\theta\gt0$ 满足：

$$\rho_\theta=\exp(\Lambda_A(\theta)-\theta C)\lt1$$

用并集界可得稳态 backlog 的一个几何级数上界：

$$\mathbb P(B\gt b)\leq\frac{e^{-\theta b}}{1-\rho_\theta}$$

该式是便于解释的保守界；更精确的鞅方法可以消除或减小前置常数。

## 二十四、常数服务下的延迟界

对 FIFO 流体队列和常数服务率 $C$，虚拟延迟与 backlog 满足：

$$W\leq\frac{B}{C}$$

因此：

$$\mathbb P(W\gt d)\leq\mathbb P(B\gt Cd)$$

结合上一节得到：

$$\mathbb P(W\gt d)\leq\frac{e^{-\theta Cd}}{1-\rho_\theta}$$

包化、非抢占服务和固定传播时间需要加入 packetizer 与 latency 修正。

## 二十五、鞅方法

若净输入增量为：

$$Y_k=A_k-S_k$$

且可找到 $\theta\gt0$ 使指数过程满足超鞅条件，则可以构造：

$$M_n=\exp\left(\theta\sum_{k=1}^nY_k-n\kappa(\theta)\right)$$

利用最大不等式直接控制随机游走上确界：

$$\mathbb P\left(\sup_{n\geq0}\sum_{k=1}^nY_k\geq b\right)\leq Ce^{-\theta b}$$

鞅界能够避免对所有时间点简单做并集导致的松弛，但要求验证条件期望和适应性结构。

## 二十六、Markov 调制流量

设环境状态 $Z_k$ 是 Markov 链，转移矩阵为 $P$，状态相关到达为 $a_j$。指数倾斜矩阵可写为：

$$M_\theta=P\operatorname{diag}(e^{\theta a_1},\ldots,e^{\theta a_m})$$

长期对数矩增长率由谱半径决定：

$$\Lambda_A(\theta)=\log\rho(M_\theta)$$

有效带宽为：

$$a(\theta)=\frac{1}{\theta}\log\rho(M_\theta)$$

这能描述活跃/空闲、战斗/非战斗等突发阶段之间的时间相关性。

## 二十七、M/M/1 基准

对到达率 $\lambda$、服务率 $\mu$ 的 M/M/1 队列，稳定条件为：

$$\rho=\frac{\lambda}{\mu}\lt1$$

稳态系统内任务数满足：

$$\mathbb P(N\geq n)=\rho^n$$

排队等待时间的尾部为：

$$\mathbb P(W_q\gt d)=\rho e^{-(\mu-\lambda)d}$$

该精确结果可用于校验实现，但真实网络通常不满足 Poisson 到达、指数服务和独立性。

## 二十八、拥塞概率界

若缓存容量为 $K$，拥塞或溢出事件为：

$$\mathcal C_K=\{B\gt K\}$$

指数界通常具有形式：

$$\mathbb P(\mathcal C_K)\leq C_0e^{-\theta^*K}$$

$\theta^*$ 可由到达与服务的对数矩平衡条件确定：

$$\Lambda_A(\theta^*)+\Lambda_{-S}(\theta^*)=0$$

该根存在性要求负平均漂移和指数矩有限。若只使用长期极限，则常得到对数渐近而非有限 $K$ 的严格上界。

## 二十九、有限时间与稳态的区别

有限时间违约概率应写明观察窗口：

$$\mathbb P\left(\sup_{0\leq t\leq T}B(t)\gt K\right)$$

稳态尾概率则是：

$$\limsup_{t\to\infty}\mathbb P(B(t)\gt K)$$

有限窗口界、任意时间界和稳态界使用的初始条件与证明工具不同。冷启动队列、非平稳流量和版本切换期间不能直接套用稳态结果。

## 三十、重尾流量

若到达量缺少正指数矩：

$$\mathbb E[e^{\theta A}]=+\infty\quad\text{for all }\theta\gt0$$

有效带宽和 Chernoff 指数界失效。此时可使用次指数分布、正则变化、截断矩、分位数包络或极值理论。

对重尾流量，拥塞往往由一次极大 burst 主导，而不是许多小偏差累积，因此指数衰减模型会严重低估尾部概率。

## 三十一、统计估计误差

样本有效带宽估计为：

$$\widehat a(\theta,t)=\frac{1}{\theta t}\log\left(\frac{1}{n}\sum_{i=1}^ne^{\theta A_i(0,t)}\right)$$

当 $\theta$ 较大时，少数极端样本会支配估计。应报告 bootstrap 或其他置信区间、样本最大值敏感性、不同 block 长度、有效样本量和分布漂移测试。

若在同一数据上选择最优 $\theta$ 并报告概率界，还要控制调参产生的选择偏差。

## 三十二、参数优化

对给定阈值 $x$，Chernoff 界需要求解：

$$\inf_{\theta\in\Theta}\exp\{-\theta x+\Lambda(\theta)\}$$

等价于：

$$\sup_{\theta\in\Theta}\{\theta x-\Lambda(\theta)\}$$

若 $\Lambda$ 光滑且最优点位于内部，则：

$$\Lambda'(\theta^*)=x$$

数值优化必须限制在矩母函数有限的定义域内，并使用 log-sum-exp 避免指数溢出。

## 三十三、5v5 游戏实时链路

一条游戏控制链可分为：网络收包、状态解码、特征构建、模型推理、动作仲裁和网络发包。每阶段提供服务曲线：

$$\beta_{\mathrm{e2e}}=\beta_{\mathrm{rx}}\otimes\beta_{\mathrm{decode}}\otimes\beta_{\mathrm{infer}}\otimes\beta_{\mathrm{act}}\otimes\beta_{\mathrm{tx}}$$

端到端延迟目标可写为：

$$\mathbb P(W_{\mathrm{e2e}}\gt d_{\max})\leq\varepsilon$$

应同时计入固定传播时间、排队时间、批处理等待和超时重试。

## 三十四、帧同步与突发到达

团战阶段事件密度会显著上升，可用 Markov 调制到达描述普通态与战斗态：

$$Z_t\in\{\mathrm{normal},\mathrm{fight}\}$$

不同状态具有不同到达强度：

$$\lambda_{\mathrm{fight}}\gt\lambda_{\mathrm{normal}}$$

只按整局平均包速率配容量会掩盖团战 burst。有效带宽或随机到达包络应按短时间尺度估计，并对战斗态驻留时间进行建模。

## 三十五、推理服务与动态批处理

动态批处理提高吞吐但引入等待时间。若最大组批时间为 $T_b$，推理节点可用近似 rate-latency 曲线：

$$\beta_{\mathrm{infer}}(t)=R_b(t-T_b-T_c)_+$$

$T_c$ 是固定计算启动延迟，$R_b$ 是批处理后的保证吞吐。过大的 batch 可能提高 $R_b$ 却同时增加 $T_b$，应以延迟违约概率而不是平均吞吐单独优化。

## 三十六、接纳控制与容量规划

若独立业务流 $i$ 的有效带宽为 $a_i(\theta)$，一种保守接纳条件为：

$$\sum_{i=1}^na_i(\theta)\leq C_{\mathrm{reserved}}$$

若服务随机，则更合理的条件为：

$$\sum_{i=1}^na_i(\theta)\lt c_{\mathrm{eff}}(\theta)$$

选择 $\theta$ 时应由目标延迟、缓存阈值和违约概率反推，而不是把 $\theta$ 当作任意调参常数。

## 三十七、验证流程

第一步统一 bit、packet、request 和时间单位。第二步从日志构建累计到达、服务和离开过程。第三步验证工作守恒、FIFO、调度和初始 backlog 假设。第四步分别拟合确定性曲线和随机包络。第五步估计有效带宽、有效容量与依赖结构。第六步计算 backlog、延迟和拥塞界。第七步用独立高峰期回放检查实际违约率。第八步对不同版本、地区、网络和团战阶段做分层验证。

经验违约率为：

$$\widehat p=\frac{1}{n}\sum_{i=1}^n\mathbf1\{W_i\gt d_{\max}\}$$

必须同时报告置信上界，而不只报告点估计。

## 三十八、常见误区

第一，把平均到达率小于平均服务率当作低延迟保证。稳定并不意味着尾延迟小。

第二，把确定性曲线拟合到大多数样本后仍称为硬上界。遗漏的样本必须进入随机违约函数。

第三，假设聚合流独立，却忽略共同赛事阶段和公共网络拥塞。

第四，用长期有效带宽回答毫秒级有限窗口问题，而不检查收敛时间尺度。

第五，把大偏差近似写成有限样本严格概率界。

第六，在重尾数据上使用不存在的指数矩。

第七，串联节点逐跳重复支付同一 burst，产生无法使用的过松界。

第八，只验证平均延迟，不验证 backlog、丢包、超时和高分位延迟。

## 三十九、结论

确定性 Network Calculus 用到达曲线、服务曲线和 min-plus 代数构造可组合的 backlog 与延迟硬界；随机网络演算用违约函数放宽硬约束，提供带概率保证的服务质量分析；有效带宽和有效容量把随机到达与随机服务映射到指数风险尺度；Chernoff、鞅和大偏差方法进一步给出延迟和拥塞尾界。

可靠应用这些工具必须明确曲线定义、观察窗口、FIFO 与调度假设、随机依赖、指数矩存在性以及有限时间和稳态之间的区别。最终界还必须用独立高峰期数据验证，否则数学上正确的上界也可能建立在错误的流量与服务模型上。
