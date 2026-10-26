# 动态机制设计与信息 Elicitation：动态拍卖、承诺约束、Peer Prediction 与 Proper Scoring Rule

## 摘要

动态机制设计研究私人信息、公共状态和资源配置随时间变化时，如何设计分配与支付规则，使参与者愿意持续报告信息并采取期望行动。与静态机制不同，当前报告不仅影响当前分配，还会改变未来信念、资格、价格和承诺，因此激励相容必须在每个历史和每个延续博弈中成立。

信息 elicitation 关注如何付费获取概率、信号、判断和预测。当未来结果可验证时，proper scoring rule 可以使风险中性报告者最大化期望得分的唯一方式是真实报告信念；当没有客观真值时，peer prediction 利用不同参与者信号之间的统计相关性，用同伴报告替代结果验证，但会引入非诚实均衡、置换均衡、低努力均衡和串谋风险。

本文系统介绍动态直接机制、动态 revelation principle、Bayesian 与 ex post 动态激励相容、promised utility、动态参与约束、动态 pivot 机制、重复与序贯拍卖、库存和学习、完全承诺、有限承诺、无承诺、棘轮效应、重新谈判、proper scoring rule、Bregman divergence、均值与分位数 elicitation、peer prediction、无先验机制、努力激励、动态声誉，以及 5v5 游戏中的资源配置与战争迷雾信息汇报。

## 一、动态环境

时间为：

$$t=0,1,\ldots,T$$

参与者集合为：

$$\mathcal N=\{1,\ldots,n\}$$

公共状态记为 $z_t$，参与者 $i$ 的私人类型或信号为 $\theta_{i,t}$。完整状态为：

$$s_t=(z_t,\theta_{1,t},\ldots,\theta_{n,t})$$

类型可能由 Markov 转移产生，并受过去分配影响。

## 二、动态历史

时刻 $t$ 的公共历史可写为：

$$h_t=(z_0,\hat\theta_0,x_0,p_0,\ldots,z_t)$$

$\hat\theta_t$ 是报告，$x_t$ 是分配，$p_t$ 是支付。参与者还可能拥有私人历史：

$$h_{i,t}^{\mathrm{priv}}=(h_t,\theta_{i,0:t})$$

机制规则必须说明依赖公共历史、当前报告还是全部私人历史。

## 三、分配与支付

动态机制在每个历史上指定分配规则：

$$x_t=x_t(h_t,\hat\theta_t)$$

以及向机制支付的金额：

$$p_{i,t}=p_{i,t}(h_t,\hat\theta_t)$$

参与者 $i$ 的单期准线性效用为：

$$u_{i,t}=v_i(s_t,x_t)-p_{i,t}$$

折扣总效用为：

$$U_i=\mathbb E\left[\sum_{t=0}^T\delta_i^tu_{i,t}\right]$$

## 四、动态直接机制

直接机制要求参与者每期报告当前私人类型：

$$\hat\theta_{i,t}\in\Theta_{i,t}$$

诚实策略为：

$$\hat\theta_{i,t}=\theta_{i,t}$$

但动态诚实性必须比较所有历史依赖的偏离策略，而不只是当前一次谎报。

报告会影响未来状态或机制信念时，单期 truthfulness 不足。

## 五、动态 Revelation Principle

在给定承诺能力、信息结构和均衡概念下，许多间接机制的均衡结果可由一个诚实直接机制复制。

动态 revelation principle 不是无条件的。若设计者不能承诺未来规则、私人历史不可压缩、参与者可在未来退出，或机制允许重新谈判，直接机制还必须满足相应的序贯可执行约束。

“可以直接报告”不代表“报告每期独立”。

## 六、动态 Bayesian IC

令 $\sigma_i$ 为报告策略，$\sigma_i^{\mathrm{tr}}$ 为诚实策略。动态 Bayesian incentive compatibility 要求对所有参与者和可达私人历史：

$$\mathbb E[U_i(\sigma_i^{\mathrm{tr}},\sigma_{-i}^{\mathrm{tr}})\mid h_{i,t}^{\mathrm{priv}}]\geq\mathbb E[U_i(\sigma_i',\sigma_{-i}^{\mathrm{tr}})\mid h_{i,t}^{\mathrm{priv}}]$$

对所有可行偏离 $\sigma_i'$ 成立。

期望基于参与者对其他类型和未来状态的条件信念。

## 七、动态 Ex Post IC

更强的 ex post IC 要求给定其他参与者实际类型路径，诚实报告仍最优：

$$U_i(\theta_i,\theta_{-i};\mathrm{truth})\geq U_i(\theta_i,\theta_{-i};\sigma_i')$$

它不依赖正确共同先验，因此更稳健，但可实现集合通常更小。

Dominant-strategy IC 是进一步要求对其他人的所有报告策略都成立。

## 八、One-Shot Deviation Principle

在有限时域、完美回忆和适当连续性条件下，验证序贯激励相容可简化为：在任意历史，只偏离当前报告或动作一次，之后恢复诚实，也不能获利。

形式上比较：

$$U_i^{\mathrm{truth}}(h_t)\geq U_i^{\mathrm{dev\ at\ }t}(h_t)$$

该原则依赖动态博弈条件。存在不完美回忆、非标准策略空间或无限时域技术问题时，不能直接使用。

## 九、Promised Utility

机制可把参与者延续效用作为状态：

$$w_{i,t}=\mathbb E\left[\sum_{\tau=t}^T\delta_i^{\tau-t}u_{i,\tau}\mid h_t\right]$$

Promise-keeping 条件为：

$$w_{i,t}=\mathbb E\left[v_i(s_t,x_t)-p_{i,t}+\delta_iw_{i,t+1}\mid h_t\right]$$

动态机制设计可在公共状态和 promised utility 空间上递归求解。

## 十、动态参与约束

Ex ante participation 要求：

$$\mathbb E[U_i]\geq0$$

Interim participation 要求给定当前私人信息：

$$\mathbb E[U_i\mid\theta_{i,t}]\geq0$$

若参与者可以随时退出，则每个历史都需满足：

$$w_{i,t}(h_t)\geq U_{i,t}^{\mathrm{outside}}(h_t)$$

动态退出权会显著限制可提取收益。

## 十一、预算与可行性

分配必须满足：

$$x_t\in\mathcal X(s_t)$$

弱预算平衡要求机制不产生预期赤字：

$$\mathbb E\left[\sum_i p_{i,t}\right]\geq0$$

逐期预算平衡比跨期预算平衡更强。动态机制还可能需要流动性、信用额度和支付上限约束。

## 十二、社会福利 Bellman 方程

设公共状态和真实类型合并为 $s$，最优社会福利满足：

$$W_t(s)=\max_{x\in\mathcal X(s)}\left\{\sum_i v_i(s,x)+\delta\mathbb E[W_{t+1}(S_{t+1})\mid s,x]\right\}$$

终端条件为：

$$W_{T+1}(s)=0$$

动态有效机制希望在激励约束下实现该递归分配。

## 十三、动态 Pivot 思想

动态 VCG 或 pivot 机制让参与者支付其对其他人造成的折扣外部性。令没有参与者 $i$ 时的最优福利为 $W_{-i}$，其总支付可写成概念形式：

$$P_i=W_{-i}(s_{-i,0})-\mathbb E_{\pi^{\star}}\left[\sum_{t=0}^T\delta^t\sum_{j\neq i}v_j(s_t,x_t^{\star})\right]$$

参与者的期望效用因而等于“有自己时的总福利减去没有自己时的基准福利”。

精确逐期支付还取决于状态转移、类型独立性和是否允许跨期结算。

## 十四、动态 Pivot 的条件

动态 pivot truthfulness 常依赖：

- 准线性效用；
- 机制能承诺未来分配与支付；
- 私人类型转移满足相应独立性或受控 Markov 条件；
- 报告不会通过未建模渠道改变他人类型；
- 机制能观察并执行状态转移与支付。

若类型相关或行动存在隐藏道德风险，标准动态 VCG 需要修改。

## 十五、单参数动态 Envelope

在单参数环境中，令 $Q_i(\theta)$ 表示报告类型 $\theta$ 对应的期望折扣分配量。激励相容通常要求单调性：

$$Q_i(\theta')\geq Q_i(\theta),\qquad \theta'\geq\theta$$

延续效用满足 envelope：

$$U_i(\theta)=U_i(\underline\theta)+\int_{\underline\theta}^{\theta}Q_i(z)\,dz$$

总支付由：

$$P_i(\theta)=\theta Q_i(\theta)-U_i(\theta)$$

恢复。动态环境中 $Q_i$ 必须包含未来分配和状态效应。

## 十六、重复拍卖

重复拍卖每期出售一个或多个对象。即使每期采用二价拍卖，当前出价也可能影响：

- 未来保留价；
- 信誉或资格；
- 平台对价值的估计；
- 竞争者未来行为；
- 剩余库存。

因此“每期二价”不自动推出整个动态机制的诚实性。

## 十七、序贯拍卖

多个互补或替代对象依次出售时，当前估值取决于已获对象集合：

$$v_i(S_t\cup\{j\})-v_i(S_t)$$

参与者会策略性地考虑未来供给和预算。序贯单品拍卖通常不能复制一次性组合 VCG 的结果。

需要把剩余物品、预算和已获集合纳入状态。

## 十八、库存约束拍卖

若剩余库存为 $q_t$，分配 $x_t$ 后：

$$q_{t+1}=q_t-\sum_i x_{i,t}$$

卖方 Bellman 方程为：

$$V_t(q,h)=\max_{\mathcal M_t}\mathbb E\left[\sum_i p_{i,t}+\delta V_{t+1}(q_{t+1},h_{t+1})\right]$$

当前卖出会减少未来选择权，最优保留价通常随库存、剩余时间和需求信念变化。

## 十九、学习型动态拍卖

卖方可能不知道需求参数 $\theta$，需要从出价和成交中学习。机制同时面临探索和收益：

$$\max_{\pi}\mathbb E\left[\sum_t\delta^t\operatorname{Revenue}_t\right]$$

参与者知道当前报告会影响未来价格时，可能操纵平台学习，这称为 strategic experimentation 或 strategic data manipulation。

将买方当作被动 stochastic bandit 臂通常会遗漏该激励效应。

## 二十、广告与长期价值

广告分配的即时价值可能为点击收益，长期状态还包括用户疲劳、广告主预算和转化信念：

$$s_t=(\text{belief},\text{budget},\text{fatigue},\text{inventory})$$

动态机制需要区分广告主私人价值和平台对长期外部性的估计。若当前点击改变未来曝光机会，单期 GSP 或 VCG 不一定动态激励相容。

## 二十一、完全承诺

完全承诺表示设计者在时刻零承诺整个历史依赖规则：

$$\mathcal M=\{x_t(h_t,\hat\theta_t),p_t(h_t,\hat\theta_t)\}_{t=0}^T$$

未来即使出现更有利的重新定价机会，也按原规则执行。

这使 revelation principle 和跨期支付更容易成立，但在现实平台、监管或长期合同中未必可信。

## 二十二、有限承诺

有限承诺允许设计者只承诺某些部分，例如：

- 当前支付不可追溯修改；
- 未来规则只能在预先声明的菜单中调整；
- 一段锁定期内价格不变；
- 状态转移规则可承诺，但未来保留价不可承诺。

必须把可承诺集合写入机制状态和序贯理性约束，而不是在求解后口头假设。

## 二十三、无承诺

无承诺时，设计者每个历史都会重新优化未来机制。参与者预见这一点，均衡必须满足设计者和参与者双方的序贯理性。

设计者不能可信承诺未来采取届时并非最优的行动。最优机制因而是一个动态博弈均衡，而不是单纯的 ex ante 最优合同。

## 二十四、棘轮效应

高类型参与者若当前诚实展示高价值，设计者未来可能提高价格或任务要求。于是高类型会压低当前报告，以保护未来信息租。

设未来价格依赖当前报告：

$$p_{t+1}=p_{t+1}(\hat\theta_t)$$

若：

$$\frac{\partial p_{t+1}}{\partial\hat\theta_t}\gt0$$

就可能产生 ratchet effect。承诺限制越弱，该问题通常越严重。

## 二十五、耐用品与 Coase 问题

垄断者出售耐用品且不能承诺未来价格时，未购买者预期未来降价，从而推迟购买。随着报价间隔缩短，均衡价格可能快速下降。

该现象说明动态定价不仅取决于当前需求，还取决于卖方未来自我竞争。有限时域、折旧、容量、消费者异质性和承诺技术会改变结论。

## 二十六、重新谈判

一个 ex ante 最优合同可能在未来历史上不再 Pareto 有效，双方因而希望重新谈判。Renegotiation-proof 机制要求不存在双方都愿意接受的可行延续替代。

重新谈判约束通常削弱惩罚威胁和跨期激励。若模型允许重新谈判，就不能依赖永远不会真正执行的离轨惩罚。

## 二十七、自生成承诺集合

有限承诺问题可用 promised utility 集合递归。令 $\mathcal W(s)$ 为状态 $s$ 下可持续的延续效用集合。

一个 promised utility $w$ 可行，当存在当前分配、支付和下一状态承诺 $w'$，满足：

$$w_i=\mathbb E[u_i+\delta_iw_i']$$

并且：

$$w'(s')\in\mathcal W(s')$$

同时满足参与者 IC 和设计者不偏离约束。

## 二十八、信息 Elicitation

Elicitation 的目标是诱导参与者报告私人信念、信号或统计量。若未来结果 $Y$ 可验证，可支付：

$$S(q,Y)$$

其中 $q$ 是报告的概率分布。设计目标是使真实信念 $p$ 最大化期望得分。

评分方向必须明确：本文约定分数越高越好。

## 二十九、Proper Scoring Rule

评分规则 $S(q,y)$ 是 proper，若对任意真实分布 $p$：

$$\mathbb E_{Y\sim p}[S(p,Y)]\geq\mathbb E_{Y\sim p}[S(q,Y)],\qquad \forall q$$

若仅在 $q=p$ 时取等，则为 strictly proper：

$$q\neq p\quad\Longrightarrow\quad \mathbb E_p[S(p,Y)]\gt\mathbb E_p[S(q,Y)]$$

该结论通常假设报告者风险中性且只关心得分期望。

## 三十、Logarithmic Score

离散结果下：

$$S_{\log}(q,y)=\log q_y$$

真实分布 $p$ 下的期望差为：

$$\mathbb E_p[S_{\log}(p,Y)-S_{\log}(q,Y)]=D_{\mathrm{KL}}(p\|q)\geq0$$

因此 log score 严格 proper。它对接近零的错误概率惩罚无界，实际支付常需截断或限制报告域。

## 三十一、Brier Score

使用“分数越高越好”的形式：

$$S_{\mathrm B}(q,y)=2q_y-\|q\|_2^2$$

期望差为：

$$\mathbb E_p[S_{\mathrm B}(p,Y)-S_{\mathrm B}(q,Y)]=\|p-q\|_2^2$$

因此 Brier score 严格 proper 且有界，适合有限结果。

等价的负平方损失形式只差与结果有关的常数。

## 三十二、Bregman 表示

设 $G$ 是定义在概率单纯形上的严格凸函数。可构造：

$$S_G(q,y)=G(q)+\langle\nabla G(q),e_y-q\rangle$$

真实分布为 $p$ 时：

$$\mathbb E_p[S_G(p,Y)-S_G(q,Y)]=D_G(p,q)\geq0$$

其中：

$$D_G(p,q)=G(p)-G(q)-\langle\nabla G(q),p-q\rangle$$

严格凸性给出严格 proper。

## 三十三、Elicitable Property

并非总要报告完整分布。统计量 $T(P)$ 可 elicitable，若存在损失 $L(r,y)$，使：

$$T(P)\in\operatorname*{arg\,min}_r\mathbb E_{Y\sim P}[L(r,Y)]$$

均值由平方损失 elicitation：

$$L(r,y)=(r-y)^2$$

$\alpha$ 分位数由 pinball loss：

$$L_{\alpha}(r,y)=(\alpha-\mathbf 1\{y\leq r\})(y-r)$$

## 三十四、联合 Elicitation

某些统计量不能单独 elicitation，却可与其他统计量联合 elicitation。方差通常与均值一起报告：

$$T(P)=(\mathbb E[Y],\operatorname{Var}(Y))$$

风险管理中 VaR 与 Expected Shortfall 也存在联合 elicitation 结构。

设计评分前应先确认目标性质是否 elicitable，而不是随意发明一个看似合理的误差函数。

## 三十五、风险厌恶

Proper scoring rule 的标准结论基于期望得分最大化。若参与者效用为：

$$\mathbb E[u(S(q,Y))]$$

且 $u$ 非线性，真实报告可能不再最优。

可使用小额支付近似风险中性，或把分数映射为赢得固定奖品的概率，构造 binary lottery，使期望效用对报告保持线性。

## 三十六、动态 Scoring Rule

参与者在多个时刻更新预测 $q_t$。可支付增量分数：

$$\Delta S_t=S(q_t,Y)-S(q_{t-1},Y)$$

总支付望远镜化：

$$\sum_{t=1}^T\Delta S_t=S(q_T,Y)-S(q_0,Y)$$

若参与者可随时更新并且结果最终可验证，market scoring rule 用增量支付奖励信息改进。

## 三十七、Market Scoring Rule

对有限结果，可使用凸成本函数：

$$C(q)=b\log\sum_{y=1}^me^{q_y/b}$$

即时价格为：

$$p_y(q)=\frac{e^{q_y/b}}{\sum_ze^{q_z/b}}$$

交易者通过改变状态 $q$ 获得状态相关支付。参数 $b$ 控制流动性和做市商最坏损失。

预测市场仍需处理操纵、预算、相关头寸和参与者外部利益。

## 三十八、没有真值时的问题

若报告的是主观质量、隐蔽状态或无法验证的判断，机制不能直接用 $Y$ 评分。简单按多数票付费会奖励协调一致，而不一定奖励真实信息。

Peer prediction 的思路是：若参与者信号因共同潜在状态而相关，一个人的报告可以预测另一个人的报告。

## 三十九、Peer Prediction 基本模型

潜在状态为 $\omega$，参与者观察私人信号：

$$S_i\sim P(\cdot\mid\omega)$$

条件独立模型常写为：

$$S_i\perp\!\!\!\perp S_j\mid\omega$$

但边缘上 $S_i$ 与 $S_j$ 相关。共同先验和信号模型诱导后验预测：

$$P(S_j\mid S_i)$$

## 四十、基本 Peer Prediction 支付

参与者 $i$ 报告 $r_i$ 后，机制把它映射为对同伴报告的预测：

$$q_i(\cdot)=P(S_j=\cdot\mid S_i=r_i)$$

支付：

$$p_i=S(q_i,r_j)$$

若评分规则严格 proper、报告对应不同后验且其他人诚实，则诚实报告是一个 Bayesian Nash 均衡。

这只证明诚实是均衡之一，不证明它唯一或最优。

## 四十一、Stochastic Relevance

若不同私人信号诱导不同的同伴后验：

$$s\neq s'\quad\Longrightarrow\quad P(S_j\mid S_i=s)\neq P(S_j\mid S_i=s')$$

则称信号具有 stochastic relevance。

若两个信号对同伴报告的预测完全相同，任何只基于同伴报告的机制都难以区分它们，严格诚实 elicitation 会失败。

## 四十二、Peer Prediction 的多均衡

常见非诚实均衡包括：

- 所有人总报告同一标签；
- 对信号做共同置换；
- 忽略信息并按公共随机数协调；
- 选择低努力但高度一致的信号源；
- 形成串谋报告规则。

因此评估机制不能只验证 truth-telling equilibrium，还要比较 equilibrium payoff、可达性和对串谋的鲁棒性。

## 四十三、Bayesian Truth Serum

Bayesian Truth Serum 同时要求参与者报告自己的答案和对群体答案分布的预测。信息分数奖励“实际频率比群体预测更常见”的答案，预测分数用 proper scoring rule 评价概率预测。

其目标是在没有客观真值时奖励“意外地常见”信息。具体保证依赖大样本、共同先验和信号条件，不能视为无假设的真值发现器。

## 四十四、Detail-Free Peer Prediction

若机制不知道共同先验，可从多任务数据估计相关结构，或使用 correlated agreement、disagreement mechanism 和互信息型支付。

多任务使机制能够区分同任务相关性和跨任务基线相关性。典型思想是奖励：

$$\text{同任务一致性}-\text{跨任务偶然一致性}$$

但任务必须近似同分布，且参与者不能控制匹配方式。

## 四十五、努力与信息获取

参与者可选择努力 $e_i$，产生不同质量信号，并承担成本 $c_i(e_i)$。机制不仅要诱导诚实，还要诱导高努力：

$$\mathbb E[p_i\mid e_i^{\star}]-c_i(e_i^{\star})\geq\mathbb E[p_i\mid e_i]-c_i(e_i)$$

如果低努力公共信号带来更高一致性，普通 peer agreement 反而可能奖励偷懒。

支付尺度必须覆盖边际信息成本，同时防止无意义刷分。

## 四十六、动态 Peer Prediction

在重复任务中，当前报告影响未来匹配、信誉和支付。延续效用为：

$$W_i(h_t)=\mathbb E\left[p_{i,t}-c_i(e_{i,t})+\delta_iW_i(h_{t+1})\mid h_t\right]$$

动态机制可以用声誉提高长期诚实和努力激励，也可能产生棘轮效应：高质量报告者担心未来被分配更难任务。

承诺未来信誉规则和审计概率是动态真诚性的关键。

## 四十七、串谋与 Sybil

串谋者可协调报告以操纵同伴分数；Sybil 攻击者还可创建多个身份互相验证。防护包括：

- 随机且不可预测的同伴匹配；
- 多任务交叉检查；
- 偶发 ground-truth audit；
- 身份成本与速率限制；
- 串谋图检测；
- 报告置换与复制检测；
- 将支付分散到多个独立信息源。

没有身份和匹配安全，评分公式本身无法阻止联合操纵。

## 四十八、5v5 游戏中的动态机制

稀缺资源包括野区、兵线、视野、传送机会和大型目标优先权。参与者或 AI 模块拥有局部私人信息：

$$\theta_{i,t}=(\text{技能状态},\text{风险判断},\text{敌方线索},\text{局部收益})$$

机制根据报告分配任务：

$$x_t=(\text{分路、支援、控图、开团角色})$$

支付可替换为训练奖励、资源优先级、信誉或未来任务选择权。

## 四十九、战争迷雾下的信息 Elicitation

若敌方位置最终被视野、回放或服务器日志验证，可使用 proper scoring rule 奖励概率报告：

$$q_{i,t}=\mathbb P(\text{敌方在区域 }i\mid\mathcal I_t)$$

若短期内没有可靠真值，可让不同英雄或感知模块进行 peer prediction，但要防止共同复制同一个错误模型。

推荐流程是：

1. 有延迟真值时优先使用 proper scoring；
2. 无真值时才使用 peer prediction；
3. 混合偶发审计和同伴评分；
4. 单独验证诚实、努力、串谋和动态承诺；
5. 不把高一致性直接解释为高准确率。

## 五十、结论

动态机制设计的核心是让当前报告、当前分配和未来延续价值共同满足激励相容、参与约束和可执行承诺。动态拍卖不能简单重复静态拍卖；当前出价会影响未来价格、库存、信念和资格。Promised utility 提供了递归状态，动态 pivot 用跨期外部性解释支付，而有限承诺和棘轮效应决定理论机制是否可信。

Proper scoring rule 适用于结果最终可验证的概率和统计量 elicitation；严格 proper 的期望优势可由 KL、平方距离或一般 Bregman divergence 表示。风险厌恶、预算和结果可验证性必须单独处理。

Peer prediction 在没有客观真值时利用信号相关性，但诚实通常只是多个均衡之一，并面临置换、低努力、串谋和 Sybil 问题。在 5v5 游戏中，应优先使用服务器延迟真值配合 scoring rule；确实无真值时，再用多任务 peer prediction、随机匹配和审计，并把未来信誉规则纳入动态承诺分析。
