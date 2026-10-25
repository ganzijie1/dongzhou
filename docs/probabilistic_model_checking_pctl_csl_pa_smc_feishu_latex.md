# 概率模型检测：PCTL、CSL、概率自动机与统计模型检测

## 摘要

概率模型检测研究带随机性系统是否满足安全、可达、时限、长期稳定和收益约束。它把系统表示为离散时间 Markov 链、连续时间 Markov 链、Markov 决策过程或概率自动机，再用 PCTL、CSL 等时序逻辑描述性质，最后通过精确数值算法、状态空间抽象或统计采样计算满足概率。

精确模型检测可以在有限模型上给出数值解或形式化界，但容易遭遇状态爆炸；统计模型检测只需要可执行模拟器，适合大型黑盒系统，但输出是带统计误差的估计或假设检验结论。二者不是互相替代，而是可以通过抽象、置信界和反例回放组合使用。

本文统一介绍 PCTL、CSL、概率自动机、数值概率模型检测和 Statistical Model Checking（SMC），并给出它们在 5v5 游戏 AI 的团战安全、目标争夺、响应时限、长期稳定和版本回归测试中的应用方法。

## 一、概率模型检测的目标

设系统执行产生随机路径：

$$\omega=s_0s_1s_2\cdots$$

性质 $\varphi$ 对一条路径或一个初始状态给出真假判断。概率模型检测关注：

$$\mathbb P_s(\omega\models\varphi)$$

典型问题包括：

$$\mathbb P_s(\Diamond\mathrm{goal})\geq0.99$$

$$\mathbb P_s(\Box\neg\mathrm{failure})\geq0.999$$

$$\mathbb P_s(\Diamond_{\leq T}\mathrm{response})\geq0.95$$

这些表达分别对应最终可达、安全保持和有时限响应。

## 二、原子命题与状态标记

设原子命题集合为 $AP$，状态标记函数为：

$$L:S\rightarrow2^{AP}$$

若 $a\in L(s)$，则状态 $s$ 满足原子命题 $a$：

$$s\models a\Longleftrightarrow a\in L(s)$$

在游戏中，原子命题可以是 `low_hp`、`objective_alive`、`team_grouped`、`enemy_visible` 或 `base_under_attack`。命题必须由可复现的状态谓词定义，不能只依赖人工主观标签。

## 三、离散时间 Markov 链

离散时间 Markov 链（DTMC）可写为：

$$\mathcal D=(S,P,L)$$

其中 $S$ 是状态集合，转移矩阵满足：

$$P(s,s')\geq0$$

$$\sum_{s'\in S}P(s,s')=1$$

Markov 性为：

$$\mathbb P(X_{k+1}=s'\mid X_0,\ldots,X_k)=P(X_k,s')$$

给定初始分布和转移矩阵后，DTMC 在无限路径空间上诱导唯一概率测度。

## 四、连续时间 Markov 链

连续时间 Markov 链（CTMC）可写为：

$$\mathcal C=(S,Q,L)$$

生成矩阵 $Q$ 满足：

$$Q(s,s')\geq0\quad(s\neq s')$$

$$Q(s,s)=-\sum_{s'\neq s}Q(s,s')$$

状态 $s$ 的离开率为：

$$q(s)=-Q(s,s)$$

若 $q(s)>0$，停留时间服从参数为 $q(s)$ 的指数分布：

$$\mathbb P(T_s>t)=e^{-q(s)t}$$

瞬态分布满足 Kolmogorov 前向方程：

$$\frac{d}{dt}p(t)=p(t)Q$$

形式解为：

$$p(t)=p(0)e^{Qt}$$

## 五、Markov 决策过程

Markov 决策过程（MDP）可写为：

$$\mathcal M=(S,A,P,L)$$

在状态 $s$ 选择动作 $a$ 后，下一状态服从：

$$P(s'\mid s,a)$$

策略或调度器记为 $\pi$。固定 $\pi$ 后，MDP 诱导一个 Markov 链。性质的满足概率依赖策略：

$$\mathbb P_s^\pi(\varphi)$$

因此通常计算最小和最大概率：

$$P_{\min}(s,\varphi)=\inf_\pi\mathbb P_s^\pi(\varphi)$$

$$P_{\max}(s,\varphi)=\sup_\pi\mathbb P_s^\pi(\varphi)$$

最小值表达对所有策略的稳健保证，最大值表达存在某个策略可以达到的能力上界。

## 六、概率自动机

概率自动机可以同时包含动作标签、概率分支和非确定性。一个常见表示为：

$$\mathcal A=(S,A,\rightarrow,L)$$

转移关系为：

$$s\xrightarrow{a}\mu$$

其中 $\mu\in\operatorname{Dist}(S)$ 是下一状态分布。同一状态和动作可能存在多个候选分布，调度器负责消解非确定性，随后再由概率选择具体后继。

若把并发模块组合，动作可通过同步产生联合转移。需要明确同步规则、隐藏动作、公平性假设，以及调度器能够观察多少历史信息。

## 七、概率与非确定性的区别

概率分支描述环境或系统的随机性，例如技能命中或网络延迟；非确定分支描述尚未指定的控制选择、并发交错或抽象误差。二者不能混成一个经验概率。

对概率分支可以求期望；对非确定分支通常求上下界：

$$\inf_\pi\mathbb P_s^\pi(\varphi)\leq\mathbb P_s^\pi(\varphi)\leq\sup_\pi\mathbb P_s^\pi(\varphi)$$

若调度器被允许观察未来随机结果，会产生不现实的预知能力，因此调度器类必须满足非预见性。

## 八、PCTL 的状态公式

PCTL 是 Probability Computation Tree Logic，常用于 DTMC 和 MDP。状态公式可递归写为：

$$\Phi::=\mathrm{true}\mid a\mid\neg\Phi\mid\Phi_1\land\Phi_2\mid\mathsf P_{\bowtie p}[\psi]$$

其中：

$$\bowtie\in\{<,\leq,>,\geq\}$$

$$p\in[0,1]$$

$\mathsf P_{\bowtie p}[\psi]$ 表示从当前状态出发，满足路径公式 $\psi$ 的路径概率与阈值 $p$ 比较后成立。

## 九、PCTL 的路径公式

常见路径公式为：

$$\psi::=\mathsf X\Phi\mid\Phi_1\,\mathsf U\,\Phi_2\mid\Phi_1\,\mathsf U^{\leq k}\,\Phi_2$$

$\mathsf X\Phi$ 表示下一步满足 $\Phi$；$\Phi_1\mathsf U\Phi_2$ 表示最终到达 $\Phi_2$，且此前一直满足 $\Phi_1$；有界 until 要求在至多 $k$ 步内完成。

最终可达可定义为：

$$\mathsf F\Phi\equiv\mathrm{true}\,\mathsf U\,\Phi$$

安全保持可通过对偶表达：

$$\mathsf G\Phi\equiv\neg\mathsf F\neg\Phi$$

## 十、PCTL 语义示例

性质：

$$\mathsf P_{\geq0.99}[\mathsf F\,\mathrm{goal}]$$

表示最终到达目标状态的概率至少为 $0.99$。

性质：

$$\mathsf P_{\leq0.01}[\mathsf F^{\leq20}\,\mathrm{failure}]$$

表示未来 20 步内进入失败状态的概率至多为 $0.01$。

性质：

$$\mathsf P_{\geq0.95}[\mathrm{safe}\,\mathsf U\,\mathrm{complete}]$$

表示在保持安全的前提下最终完成任务的概率至少为 $0.95$。

## 十一、DTMC 可达概率计算

设目标状态集合为 $T$，可达概率为：

$$x_s=\mathbb P_s(\Diamond T)$$

边界条件为：

$$x_s=1\quad(s\in T)$$

对其余可到达状态：

$$x_s=\sum_{s'}P(s,s')x_{s'}$$

于是可达概率可通过线性方程组、值迭代或图分解求解。必须先识别不能到达 $T$ 的状态并将其值设为零，避免奇异方程组。

## 十二、MDP 可达概率计算

MDP 中最大可达概率满足 Bellman 最优方程：

$$x_s^{\max}=\max_{a\in A(s)}\sum_{s'}P(s'\mid s,a)x_{s'}^{\max}$$

最小可达概率满足：

$$x_s^{\min}=\min_{a\in A(s)}\sum_{s'}P(s'\mid s,a)x_{s'}^{\min}$$

有限 MDP 的无界可达问题通常存在确定性无记忆最优策略，但更复杂的多目标、部分可观测或历史约束问题未必具有这一性质。

## 十三、有界 Until 的动态规划

设：

$$x_s^{(k)}=\mathbb P_s(\Phi_1\,\mathsf U^{\leq k}\,\Phi_2)$$

初始化为：

$$x_s^{(0)}=\mathbf1_{\Phi_2}(s)$$

对 $k\geq1$：

$$x_s^{(k)}=\mathbf1_{\Phi_2}(s)+\mathbf1_{\Phi_1\land\neg\Phi_2}(s)\sum_{s'}P(s,s')x_{s'}^{(k-1)}$$

MDP 情形把求和外层换成对动作的最大或最小运算。

## 十四、CSL 的作用

CSL 是 Continuous Stochastic Logic，面向 CTMC。它不仅能表达最终可达，还能表达真实时间区间内的转移和长期稳定概率。

CSL 状态公式可写为：

$$\Phi::=\mathrm{true}\mid a\mid\neg\Phi\mid\Phi_1\land\Phi_2\mid\mathsf P_{\bowtie p}[\psi]\mid\mathsf S_{\bowtie p}[\Phi]$$

路径公式包括带时间区间的 next 与 until：

$$\psi::=\mathsf X^I\Phi\mid\Phi_1\,\mathsf U^I\,\Phi_2$$

其中 $I\subseteq\mathbb R_{\geq0}$ 是时间区间。

## 十五、CSL 时间有界性质

性质：

$$\mathsf P_{\geq0.999}[\mathsf F^{[0,2]}\,\mathrm{response}]$$

表示两秒内响应的概率至少为 $0.999$。

性质：

$$\mathsf P_{\leq0.005}[\mathrm{operational}\,\mathsf U^{[0,10]}\,\mathrm{failure}]$$

表示十秒内在持续运行期间进入失败状态的概率至多为 $0.005$。

时间区间的开闭端点会影响边界时刻语义，工具实现和需求文档必须采用一致约定。

## 十六、CSL 稳态算子

稳态性质：

$$\mathsf S_{\geq p}[\Phi]$$

表示长期稳态下处于满足 $\Phi$ 的状态的概率至少为 $p$。若 CTMC 不可约，长期极限可能依赖初始状态和底部强连通分量。

平稳分布 $\pi$ 满足：

$$\pi Q=0$$

$$\sum_s\pi_s=1$$

仅求出某个平稳分布不自动证明从给定初态收敛到它，仍需检查不可约性、正常返和周期相关条件。

## 十七、CTMC Uniformization

Uniformization 把 CTMC 的瞬态分析转化为 Poisson 加权的 DTMC 计算。选择：

$$\lambda\geq\max_s q(s)$$

定义统一化转移矩阵：

$$P=I+\frac{Q}{\lambda}$$

则：

$$p(t)=\sum_{k=0}^{\infty}e^{-\lambda t}\frac{(\lambda t)^k}{k!}p(0)P^k$$

数值实现需要截断 Poisson 和，并控制上下尾截断误差。$\lambda$ 过大会增加需要计算的步数。

## 十八、奖励扩展

概率模型常配合状态奖励和转移奖励。累计奖励可写为：

$$R_T=\int_0^Tr(X_t)dt+\sum_{0\lt t\leq T}r_e(X_{t^-},X_t)$$

离散时间版本为：

$$R_k=\sum_{t=0}^{k-1}r(S_t,A_t)$$

工具通常提供 PCTL/CSL 的奖励扩展，用于验证期望死亡数、资源损失、延迟、能耗或收益。概率阈值与期望奖励阈值表达不同风险信息，不能互相替代。

## 十九、调度器与公平性

概率自动机和 MDP 的性质取决于调度器类。历史依赖随机调度器可表示为：

$$\pi(a\mid s_0a_0s_1\cdots s_t)$$

无记忆策略只依赖当前状态：

$$\pi(a\mid s_t)$$

若并发系统要求某个持续可用动作最终被选择，需要加入公平性约束。没有公平性时，调度器可能通过永久拖延使活性性质失败；加入过强公平性又可能排除真实故障执行。

## 二十、概率反例与证据

普通模型检测的反例是一条路径；概率性质的反例通常是一组路径或子系统，其总概率质量超过阈值。例如对：

$$\mathsf P_{\leq p}[\Diamond T]$$

若找到路径集合 $C$ 满足：

$$\sum_{\omega\in C}\mathbb P(\omega)>p$$

则 $C$ 构成违反性质的概率证据。实际工具常用最可能路径、k-shortest paths 或关键子系统生成可解释反例。

## 二十一、状态空间爆炸

若第 $i$ 个组件有 $n_i$ 个局部状态，同步乘积的最坏状态数为：

$$|S|=\prod_{i=1}^mn_i$$

应对方法包括符号表示、稀疏矩阵、强连通分量分解、偏序约简、对称约简、双模拟商、抽象解释和组合式验证。约简必须保持待验证逻辑所需的等价关系。

## 二十二、概率双模拟

概率双模拟把行为等价状态合并。对等价关系 $\sim$，若 $s\sim t$，则应有相同标记，并对每个等价类 $C$ 满足：

$$P(s,C)=P(t,C)$$

其中：

$$P(s,C)=\sum_{s'\in C}P(s,s')$$

在适当定义下，双模拟商保持 PCTL 或 CSL 性质。近似双模拟则需要额外误差界，不能把近似商的结论直接当成精确结论。

## 二十三、抽象与区间概率

当真实转移概率未知或状态聚合产生误差时，可使用区间 Markov 链：

$$P(s,s')\in[\underline P(s,s'),\overline P(s,s')]$$

性质验证变成对所有合法转移矩阵求上下界：

$$\underline p=\inf_{P\in\mathcal P}\mathbb P_P(\varphi)$$

$$\overline p=\sup_{P\in\mathcal P}\mathbb P_P(\varphi)$$

若阈值位于 $[\underline p,\overline p]$ 内，当前抽象无法判定，应细化状态或收集更多数据。

## 二十四、统计模型检测

统计模型检测通过独立模拟轨迹估计性质满足概率。对第 $i$ 条轨迹定义：

$$Y_i=\mathbf1\{\omega_i\models\varphi\}$$

若轨迹独立同分布，则：

$$Y_i\sim\operatorname{Bernoulli}(p)$$

Monte Carlo 估计为：

$$\widehat p_n=\frac{1}{n}\sum_{i=1}^nY_i$$

它不需要显式枚举状态空间，但要求模拟器、性质监视器和随机种子管理正确。

## 二十五、固定样本置信保证

Hoeffding 不等式给出：

$$\mathbb P(|\widehat p_n-p|\geq\varepsilon)\leq2e^{-2n\varepsilon^2}$$

若要求误差至多 $\varepsilon$、失败概率至多 $\delta$，可选：

$$n\geq\frac{1}{2\varepsilon^2}\log\frac{2}{\delta}$$

该界分布无关但可能保守。Wilson、Clopper–Pearson 或经验 Bernstein 区间可提供不同宽度和覆盖性质；选择方法应在实验前固定。

## 二十六、序贯概率比检验

要判断：

$$H_0:p\geq p_0$$

$$H_1:p\leq p_1$$

其中 $p_1<p_0$ 形成无差异区间。累计对数似然比可写为：

$$L_n=\sum_{i=1}^n\log\frac{p_1^{Y_i}(1-p_1)^{1-Y_i}}{p_0^{Y_i}(1-p_0)^{1-Y_i}}$$

给定第一类错误上限 $\alpha$ 和第二类错误上限 $\beta$，近似停止阈值为：

$$A=\log\frac{\beta}{1-\alpha}$$

$$B=\log\frac{1-\beta}{\alpha}$$

当 $L_n\leq A$ 时接受 $H_0$，当 $L_n\geq B$ 时接受 $H_1$，否则继续采样。可选停止规则必须与所用置信保证相匹配。

## 二十七、统计模型检测的依赖问题

一条轨迹内部允许有 Markov 依赖，因为 $Y_i$ 是整条轨迹的性质结果；但不同轨迹之间通常要求独立。若复用同一长轨迹切片、共享环境随机数或策略状态未重置，则 Bernoulli 独立假设可能失效。

有效样本量可粗略表示为：

$$n_{\mathrm{eff}}\approx\frac{n}{1+2\sum_{k\geq1}\rho_k}$$

其中 $\rho_k$ 是序列相关系数。该近似不能替代严格的混合条件分析，但能暴露严重相关性。

## 二十八、稀有事件统计验证

若失败概率极小，朴素 Monte Carlo 需要大量样本。重要性采样从替代分布 $Q$ 采样，并使用似然比：

$$p=\mathbb E_Q\left[\mathbf1_{\varphi}\frac{dP}{dQ}\right]$$

估计量为：

$$\widehat p_n=\frac{1}{n}\sum_{i=1}^n\mathbf1_{\varphi}(\omega_i)\frac{dP}{dQ}(\omega_i)$$

还可使用 splitting、subset simulation 或 cross-entropy 方法。改变采样分布后必须保留完整路径似然比，否则估计会有偏。

## 二十九、多性质与自适应测试

若同时验证 $m$ 个性质，每个性质都使用显著性水平 $\alpha$，整体误报率会膨胀。Bonferroni 控制可使用：

$$\alpha_i=\frac{\alpha}{m}$$

若测试过程中反复查看结果、调整阈值或挑选性质，固定时点置信区间不再保持原覆盖率。应使用预注册测试、独立验证集、anytime confidence sequence 或显式多重检验校正。

## 三十、精确检测与统计检测的组合

可先在抽象模型上做精确模型检测，得到候选危险状态和最坏调度器，再在真实模拟器中用统计模型检测验证抽象误差。若抽象给出：

$$P_{\max}^{\mathrm{abstract}}(\varphi)\leq p$$

且抽象关系确实是保守上界，则可以形式化证明安全阈值。若保守关系尚未证明，统计结果只能提供经验支持。

另一种流程是用 SMC 找到失败回放，再提取有限子模型做精确反例分析。

## 三十一、5v5 游戏的 PCTL 性质

离散决策周期下，可定义：

$$\mathsf P_{\geq0.95}[\mathrm{grouped}\,\mathsf U^{\leq8}\,\mathrm{engage}]$$

表示在保持集结状态的前提下，八个决策步内进入有效开团的概率至少为 $0.95$。

撤退安全性质可写为：

$$\mathsf P_{\leq0.02}[\mathsf F^{\leq12}\,\mathrm{teamwipe}]$$

资源交换性质可写为：

$$\mathsf P_{\geq0.9}[\mathrm{safe}\,\mathsf U\,\mathrm{objective\_secured}]$$

状态谓词应由血量、距离、技能冷却、视野和人数差等可观测量确定。

## 三十二、5v5 游戏的 CSL 性质

连续事件仿真可验证真实时间响应：

$$\mathsf P_{\geq0.99}[\mathsf F^{[0,1.5]}\,\mathrm{reinforcement\_arrives}]$$

控制链风险可写为：

$$\mathsf P_{\leq0.01}[\mathsf F^{[0,3]}\,\mathrm{carry\_disabled}]$$

长期失配率可写为：

$$\mathsf S_{\leq0.05}[\mathrm{role\_conflict}]$$

如果事件持续时间并非指数分布，普通 CTMC 可能不合适，可考虑相位型近似、广义半 Markov 模型或显式时钟模型。

## 三十三、调度器在游戏 AI 中的解释

在游戏模型中，调度器可以代表战术控制器、队伍指挥策略或未解析的并发决策。计算：

$$P_{\min}(\mathrm{win\ without\ teamwipe})$$

可以评估所有允许策略中的最坏保证；计算：

$$P_{\max}(\mathrm{objective\ secured})$$

可以判断模型内是否存在高成功率策略。若调度器拥有真实 AI 不可见的信息，该上界会虚高，所以观察结构必须与部署条件一致。

## 三十四、版本回归与统计门禁

设旧版本满足概率为 $p_A$，新版本为 $p_B$，关注差值：

$$\Delta=p_B-p_A$$

可以使用配对随机种子降低环境方差，但分析时必须使用配对差值方法。上线门禁可规定：

$$\operatorname{LCB}_{1-\alpha}(\Delta)>-\varepsilon$$

其中 $\varepsilon$ 是允许退化幅度，$\operatorname{LCB}$ 是单侧置信下界。门禁阈值、样本量和停止规则应在运行测试前确定。

## 三十五、模型构建与验证流程

第一步定义原子命题和时间单位。第二步判断系统是 DTMC、CTMC、MDP、概率自动机还是黑盒模拟器。第三步明确随机性、控制选择和并发非确定性的来源。第四步把需求写成 PCTL、CSL 或监视器。第五步进行模型结构检查，包括概率归一化、不可达状态、死锁和时钟单位。第六步选择精确求解、抽象上下界或 SMC。第七步生成反例和回放。第八步用独立场景与版本验证结果。

## 三十六、质量检查清单

至少检查：转移概率是否归一化；CTMC 生成矩阵行和是否为零；状态标记是否互相矛盾；调度器是否获得未来信息；时间边界的开闭区间是否一致；吸收状态和死锁语义是否明确；数值迭代残差是否达标；统计轨迹是否独立；随机种子是否可复现；多重检验是否校正；稀有事件权重是否退化。

数值残差可检查：

$$r_s=\left|x_s-\sum_{s'}P(s,s')x_{s'}\right|$$

但残差小不等于模型正确，它只说明数值解与所建方程一致。

## 三十七、常见误区

第一，把模拟中没有观察到失败解释为失败概率为零。零次失败只能产生上置信界。

第二，把最大满足概率当成当前策略的实际满足概率。最大值通常对应重新合成的最优调度器。

第三，在 CTMC 中忽略事件持续时间分布，仅用平均持续时间替代全过程。

第四，用训练回放估计转移概率，再在同一回放上报告验证置信度，导致双重使用数据。

第五，把统计模型检测称为数学证明。它提供的是受假设约束的统计保证。

第六，验证形式化性质本身写错的模型。模型检测证明的是模型满足公式，不自动证明公式等价于真实业务需求。

## 三十八、工具选择

有限状态 DTMC、CTMC、MDP 和概率自动机可使用 PRISM、Storm 等概率模型检测器；带时钟的随机系统可考虑统计扩展工具；已有仿真器则可实现独立的轨迹监视器和 SMC 管线。选择工具时应检查支持的模型语义、逻辑片段、策略类型、奖励结构、精确或浮点求解方式，以及反例导出能力。

工具输出的 `true`、`false` 或数值概率必须连同模型版本、初始状态、性质文本、容差和求解器配置一起存档。

## 三十九、结论

PCTL 为离散时间概率系统提供下一步、可达、until 和步数约束；CSL 把性质扩展到 CTMC 的真实时间区间与稳态行为；概率自动机统一表示概率分支和非确定选择；统计模型检测则通过模拟为大型或黑盒系统提供带误差控制的概率估计与判定。

可靠的概率模型检测必须同时回答四个问题：系统模型是否忠实，逻辑性质是否真正表达需求，调度器与时间语义是否符合部署环境，数值或统计保证是否满足其前提。只有这四层一致，概率阈值才具有工程意义。
