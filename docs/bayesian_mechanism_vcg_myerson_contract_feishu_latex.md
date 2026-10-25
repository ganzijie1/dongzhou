# Bayesian Mechanism Design、VCG、Myerson Auction、Revelation Principle、IR/IC 与 Principal–Agent

## 摘要

机制设计研究如何在参与者拥有私人信息并会策略性行动时，通过规则、分配和支付实现某个社会目标。贝叶斯机制设计把参与者类型视为随机变量；revelation principle 说明可以把许多复杂交互转化为直接报告类型的机制；individual rationality（IR）保证参与者愿意参加；incentive compatibility（IC）保证如实报告或执行约定行为符合自身利益；VCG 机制以社会福利最大化和外部性支付实现占优策略激励相容；Myerson 拍卖用虚拟价值刻画单物品最优收益；contract theory 与 principal–agent 模型则研究隐藏类型和隐藏行动下的合同设计。

这些工具依赖明确假设：准线性效用、私人价值、风险态度、类型分布、承诺能力、可观察结果、可执行支付和反串谋条件。离开这些假设后，公式可能仍能计算，但激励结论不再自动成立。

本文统一介绍上述理论、关键公式、求解方法、不可兼得结果，以及它们在 5v5 游戏匹配、角色分配、团队奖励和 AI 行为激励中的应用边界。

## 一、机制设计的基本元素

参与者集合为：

$$N=\{1,\ldots,n\}$$

参与者 $i$ 的私人类型为：

$$\theta_i\in\Theta_i$$

联合类型为：

$$\theta=(\theta_1,\ldots,\theta_n)\in\Theta$$

类型先验为：

$$F(\theta)$$

可行分配集合为 $X$。直接机制由分配规则和支付规则组成：

$$x:\Theta\rightarrow X$$

$$p_i:\Theta\rightarrow\mathbb R$$

本文采用“$p_i>0$ 表示参与者向机制支付”的约定。准线性效用为：

$$u_i(\theta_i;\hat\theta)=v_i(x(\hat\theta),\theta_i)-p_i(\hat\theta)$$

其中 $\hat\theta$ 是报告类型，$\theta_i$ 是真实类型。

## 二、社会选择目标

常见社会福利目标为：

$$W(x,\theta)=\sum_{i=1}^{n}v_i(x,\theta_i)$$

有效分配规则选择：

$$x^*(\theta)\in\arg\max_{x\in X}\sum_i v_i(x,\theta_i)$$

卖方收益目标为：

$$\operatorname{Rev}(p)=\mathbb E_{\theta}\left[\sum_i p_i(\theta)\right]$$

还可以加入公平、风险、容量、预算和安全目标。不同目标通常不可同时达到最优，必须明确优先级与约束。

## 三、Dominant-Strategy Incentive Compatibility

直接机制满足占优策略激励相容，简称 DSIC，如果对任意参与者、真实类型、虚假报告和其他人报告都有：

$$v_i(x(\theta_i,\theta_{-i}),\theta_i)-p_i(\theta_i,\theta_{-i})\geq v_i(x(\hat\theta_i,\theta_{-i}),\theta_i)-p_i(\hat\theta_i,\theta_{-i})$$

DSIC 表示无论其他参与者报告什么，如实报告都是最优响应。

它是较强的稳健激励概念，不需要参与者知道其他人的类型分布。但它仍不自动防止多人串谋、虚假身份和机制外转移支付。

## 四、Bayesian Incentive Compatibility

贝叶斯激励相容，简称 BIC，要求在给定自己的类型并对其他类型取条件期望后，如实报告最优：

$$\mathbb E_{\theta_{-i}\mid\theta_i}\left[u_i(\theta_i;\theta_i,\theta_{-i})\right]\geq\mathbb E_{\theta_{-i}\mid\theta_i}\left[u_i(\theta_i;\hat\theta_i,\theta_{-i})\right]$$

对所有 $i$、$\theta_i$ 和 $\hat\theta_i$ 都要求成立。

BIC 通常比 DSIC 弱，因为它只要求在先验条件期望下不偏离。若先验错误、类型相关性被忽略或参与者拥有额外信息，BIC 结论可能失效。

## 五、Individual Rationality

设参与者 $i$ 的外部选择效用为：

$$\bar u_i(\theta_i)$$

### 1. Ex-post IR

对每个完整类型组合都满足：

$$v_i(x(\theta),\theta_i)-p_i(\theta)\geq\bar u_i(\theta_i)$$

### 2. Interim IR

参与者知道自己的类型后，在其他类型条件分布下满足：

$$\mathbb E_{\theta_{-i}\mid\theta_i}\left[v_i(x(\theta),\theta_i)-p_i(\theta)\right]\geq\bar u_i(\theta_i)$$

### 3. Ex-ante IR

在参与者尚未知道自身类型前满足：

$$\mathbb E_{\theta}\left[v_i(x(\theta),\theta_i)-p_i(\theta)\right]\geq\mathbb E_{\theta_i}[\bar u_i(\theta_i)]$$

在通常设置中，ex-post IR 强于 interim IR，interim IR 又强于 ex-ante IR。具体比较仍依赖外部选择和信息到达时点。

## 六、预算平衡

机制的总收入为：

$$B(\theta)=\sum_i p_i(\theta)$$

强预算平衡要求：

$$B(\theta)=0$$

弱预算平衡通常要求机制不补贴：

$$B(\theta)\geq 0$$

预算平衡与效率、IR、IC 经常冲突。一个机制可以激励相容并有效，却产生盈余或赤字。

## 七、Revelation Principle

Revelation principle 的核心陈述是：如果某个间接机制存在一个均衡并实现某个结果分布，那么通常可以构造一个直接机制，让参与者报告类型，并使如实报告在对应均衡概念下实现同样结果。

设原机制中的均衡策略为：

$$s_i^*(\theta_i)$$

直接机制收到报告 $\hat\theta$ 后，模拟原机制消息：

$$m_i=s_i^*(\hat\theta_i)$$

然后执行原机制的分配和支付。因此虚报类型等价于在原机制中采用另一个类型的均衡消息。

## 八、Revelation Principle 不代表什么

Revelation principle 不表示：

- 所有机制都天然 truthful；
- BIC 可以自动升级为 DSIC；
- 直接机制一定更容易计算或沟通；
- 机制可以忽略串谋、有限理性和错误先验；
- 设计者可以观察真实类型；
- 动态机制只需检查单步偏离。

它主要缩小理论搜索空间：研究可实现结果时，可以优先研究直接且 truthful 的机制。

## 九、VCG 机制

VCG 适用于准线性私人价值环境。首先选择社会福利最大化分配：

$$x^*(\theta)\in\arg\max_{x\in X}\sum_jv_j(x,\theta_j)$$

参与者 $i$ 的支付为：

$$p_i(\theta)=h_i(\theta_{-i})-\sum_{j\neq i}v_j(x^*(\theta),\theta_j)$$

其中 $h_i$ 可以是任意只依赖其他参与者报告的函数。

参与者 $i$ 的效用为：

$$u_i(\theta)=\sum_jv_j(x^*(\theta),\theta_j)-h_i(\theta_{-i})$$

因为第二项不依赖 $i$ 的报告，参与者通过如实报告使总福利最大，因此 VCG 满足 DSIC。

## 十、Clarke Pivot Payment

常用选择是 Clarke pivot：

$$h_i(\theta_{-i})=\max_{x\in X_{-i}}\sum_{j\neq i}v_j(x,\theta_j)$$

因此：

$$p_i=\max_{x\in X_{-i}}\sum_{j\neq i}v_j(x,\theta_j)-\sum_{j\neq i}v_j(x^*(\theta),\theta_j)$$

支付等于参与者 $i$ 给其他人造成的外部性。

在单物品拍卖中，最高估值者获胜并支付第二高估值，这就是 Vickrey 二价拍卖，也是 VCG 的特例。

## 十一、VCG 的 IR 与预算问题

在允许不参与、估值非负、可行集合满足适当删除参与者条件时，Clarke pivot 常能给出 ex-post IR。但这不是所有 VCG 环境中的无条件结论。

VCG 一般不保证强预算平衡。在公共项目、双边交易和某些组合分配中，机制可能产生盈余或赤字。

VCG 也未必抗串谋。多个参与者联合虚报、拆分身份或进行机制外补偿，可能破坏预期性质。

## 十二、Groves 机制

Groves 机制使用有效分配并令支付满足：

$$p_i(\theta)=h_i(\theta_{-i})-\sum_{j\neq i}v_j(x^*(\theta),\theta_j)$$

所有 Groves 机制在标准准线性私人价值环境下都满足 DSIC。VCG 通常指这类机制，Clarke pivot 是其中一个具体支付选择。

$h_i$ 的选择会影响预算、参与效用和收入，但不改变占优策略激励相容性，因为它不依赖 $i$ 的报告。

## 十三、单参数机制

设参与者 $i$ 的类型是标量 $v_i$，分配概率为：

$$q_i(v_i)=\mathbb E_{v_{-i}}[x_i(v_i,v_{-i})]$$

中期效用为：

$$U_i(v_i)=v_iq_i(v_i)-P_i(v_i)$$

在标准单参数贝叶斯环境中，BIC 要求分配规则 $q_i(v_i)$ 单调不减，并满足 envelope 关系：

$$U_i(v_i)=U_i(\underline v_i)+\int_{\underline v_i}^{v_i}q_i(t)\,\mathrm dt$$

因此期望支付为：

$$P_i(v_i)=v_iq_i(v_i)-U_i(\underline v_i)-\int_{\underline v_i}^{v_i}q_i(t)\,\mathrm dt$$

若最低类型的 IR 约束绑定，则：

$$U_i(\underline v_i)=0$$

这个 payment identity 是 Myerson 拍卖推导的基础。

## 十四、Myerson Auction

考虑单物品拍卖。买家 $i$ 的私人价值为：

$$v_i\sim F_i$$

若存在密度，则记为：

$$f_i(v)=F_i'(v)$$

假设价值独立、风险中性、准线性，并满足相应正则条件。Myerson 虚拟价值定义为：

$$\phi_i(v)=v-\frac{1-F_i(v)}{f_i(v)}$$

卖方期望收入可以表示为期望虚拟剩余：

$$\mathbb E\left[\sum_ip_i(v)\right]=\mathbb E\left[\sum_i\phi_i(v_i)x_i(v)\right]$$

该等式依赖 BIC、支付恒等式、边界效用和可积性等条件。

## 十五、Regular Distribution

若虚拟价值 $\phi_i(v)$ 单调不减，则称分布 regular。

在 regular 单物品环境中，Myerson 最优机制把物品分配给具有最高非负虚拟价值的参与者：

$$i^*\in\arg\max_i\phi_i(v_i)$$

只有当：

$$\phi_{i^*}(v_{i^*})\geq 0$$

时才分配。支付是使获胜者刚好仍会获胜的临界类型。

## 十六、保留价

对独立同分布 regular 买家，保留价 $r$ 常由：

$$\phi(r)=0$$

确定，也就是：

$$r-\frac{1-F(r)}{f(r)}=0$$

若所有出价低于保留价，卖方不出售物品。

保留价依赖估计的价值分布。有限样本、分布漂移和参与者策略性响应会使经验保留价不稳定。

## 十七、Irregular Distribution 与 Ironing

若 $\phi(v)$ 非单调，直接按虚拟价值分配可能违反分配单调性，从而破坏 BIC。

Myerson ironing 在分位数或收益曲线上做适当凸化或凹化，得到单调的 ironed virtual value：

$$\bar\phi(v)$$

再按 ironed virtual surplus 最大化分配。被 ironing 合并的类型区间可能获得相同分配概率。

不能简单地对非单调 $\phi$ 做逐点排序后称其为 Myerson 最优拍卖。

## 十八、Myerson 与 VCG 的区别

| 机制 | 主要目标 | 使用分布 | 典型分配原则 |
|---|---|---|---|
| VCG | 社会福利最大化 | 通常不需要类型先验 | 最大化真实报告总价值 |
| Myerson | 卖方期望收益最大化 | 需要价值分布 | 最大化非负虚拟价值 |

VCG 可能把物品给最高真实价值者；Myerson 可能因保留价不出售，也可能在非对称分布下不按最高原始价值排序。

## 十九、有限类型贝叶斯机制设计

若类型集合和分配集合有限，可以直接把机制写成线性规划。

决策变量包括：

$$x(a\mid\theta)$$

以及：

$$p_i(\theta)$$

概率约束为：

$$x(a\mid\theta)\geq 0,\qquad\sum_ax(a\mid\theta)=1$$

BIC 约束为：

$$\mathbb E_{\theta_{-i}\mid\theta_i}\left[u_i(\theta_i;\theta_i,\theta_{-i})-u_i(\theta_i;\hat\theta_i,\theta_{-i})\right]\geq 0$$

再加入 interim IR、预算、容量和公平约束，即可最大化期望福利或收益。

类型相关时必须使用正确的条件分布 $F(\theta_{-i}\mid\theta_i)$，不能错误地分解成独立边缘分布。

## 二十、Bayesian Correlated Mechanism

如果机制不仅收集报告，还向参与者发送相关行动建议，可以使用联合分布：

$$\mu(\theta,a)$$

它应满足 Bayes plausibility：

$$\sum_a\mu(\theta,a)=F(\theta)$$

以及 obedience 约束。机制设计可以进一步在 BCE 多面体中选择最大福利、最大收益或满足公平风险约束的结果。

这比标准直接分配机制更一般，但必须明确推荐者能够观察什么信息以及建议是否可执行。

## 二十一、Contract Theory

合同理论研究 principal（委托人）如何设计支付或任务规则，引导 agent（代理人）选择委托人希望的行为。

委托人效用记为：

$$U_P$$

代理人效用记为：

$$U_A$$

两类核心信息问题是：

- hidden information 或 adverse selection：签约前代理人知道自己的类型，委托人不知道；
- hidden action 或 moral hazard：签约后代理人选择不可直接观察的行动或努力。

## 二十二、Observable Action：First Best

若努力 $e$ 可观察且可写入合同，结果 $Y$ 的分布为：

$$Y\sim P(\cdot\mid e)$$

工资为 $w$，代理人成本为 $c(e)$。风险中性代理人的期望效用为：

$$U_A=w-c(e)$$

委托人的期望效用为：

$$U_P=\mathbb E[Y\mid e]-w$$

委托人可选择 $(e,w)$ 最大化 $U_P$，只需满足 participation constraint：

$$w-c(e)\geq\bar U$$

这称为 first-best 基准。

## 二十三、Hidden Action：Moral Hazard

若努力不可观察，合同只能依赖可观察结果 $Y$：

$$w=w(Y)$$

代理人选择努力：

$$e^*\in\arg\max_e\mathbb E[u(w(Y))\mid e]-c(e)$$

因此合同必须满足 incentive compatibility：

$$\mathbb E[u(w(Y))\mid e^*]-c(e^*)\geq\mathbb E[u(w(Y))\mid e]-c(e),\qquad\forall e$$

还要满足 participation：

$$\mathbb E[u(w(Y))\mid e^*]-c(e^*)\geq\bar U$$

委托人求解：

$$\max_{w(\cdot),e^*}\mathbb E[Y-w(Y)\mid e^*]$$

并受上述 IC 与 IR 约束。

## 二十四、风险分担与激励

若代理人风险厌恶，$u$ 为凹函数。更依赖结果的工资提供更强激励，但也把更多结果风险转移给代理人。

在线性合同中：

$$w(Y)=s+bY$$

$b$ 是绩效敏感度，$s$ 是固定支付。增大 $b$ 往往增强努力激励，也增加代理人收入波动。

最优合同在保险与激励之间权衡。若结果噪声大、努力对结果影响弱，高绩效敏感度可能成本很高。

## 二十五、Limited Liability

若代理人不能向委托人支付超过某个下限，可加入：

$$w(y)\geq\underline w$$

常见有限责任约束为：

$$w(y)\geq 0$$

有限责任会限制惩罚，改变最优合同，并可能使部分努力水平无法实现。

## 二十六、Hidden Type：Adverse Selection

代理人知道类型 $\theta$，委托人提供合同菜单：

$$\{x(\hat\theta),t(\hat\theta)\}_{\hat\theta\in\Theta}$$

代理人真实类型为 $\theta$ 时的效用为：

$$u(x(\hat\theta),\theta)-t(\hat\theta)$$

IC 要求：

$$u(x(\theta),\theta)-t(\theta)\geq u(x(\hat\theta),\theta)-t(\hat\theta)$$

IR 要求：

$$u(x(\theta),\theta)-t(\theta)\geq\bar u(\theta)$$

这与直接贝叶斯机制设计本质相同：合同菜单诱导代理人自我选择。

## 二十七、Single Crossing 与单调分配

若类型越高，边际质量价值越高，可以使用 single-crossing 条件。例如：

$$\frac{\partial^2u(x,\theta)}{\partial x\partial\theta}>0$$

在一维规则条件下，IC 通常要求分配 $x(\theta)$ 随类型单调，并通过 envelope 公式确定信息租金。

高类型通常获得信息租金：

$$U(\theta)=U(\underline\theta)+\int_{\underline\theta}^{\theta}\frac{\partial u(x(t),t)}{\partial t}\,\mathrm dt$$

最优合同可能扭曲低类型分配，以减少高类型模仿低类型合同的收益。

## 二十八、多任务与可操纵指标

若代理人同时执行多个任务，合同只奖励容易观测的指标，代理人可能把努力从难测但重要的任务转移到被奖励指标。

设努力向量为：

$$e=(e_1,\ldots,e_m)$$

绩效信号为：

$$Y=Be+\varepsilon$$

若工资只依赖某些分量，最优响应可能牺牲未计价任务。这是 Goodhart 效应与多任务代理问题的机制基础。

## 二十九、动态合同

动态 principal–agent 问题中，当前行动影响未来状态、信念和承诺。合同可以依赖公共历史：

$$w_t=w_t(H_t^{\mathrm{public}})$$

代理人的 continuation utility 是关键状态变量：

$$U_{t}^{\mathrm{cont}}=\mathbb E\left[\sum_{k=t}^{T}\beta^{k-t}u_k\mid H_t^{\mathrm{public}}\right]$$

逐期静态 IC 不一定保证动态 IC，因为当前偏离会改变未来信息和合同状态。

## 三十、不可兼得结果

### 1. Green–Laffont 类型张力

在一般公共决策环境中，效率、DSIC 与严格预算平衡通常无法同时无条件实现。VCG 保证效率和 DSIC，但预算平衡可能失败。

### 2. Myerson–Satterthwaite

在买卖双方独立私人价值、支持区间重叠的双边交易中，通常不存在同时满足 Bayesian IC、interim IR、预算平衡与事后效率的机制。

这些结果说明“设计更聪明的支付公式”不能消除所有制度冲突，设计者必须明确牺牲哪一个目标或引入额外信息、补贴和重复互动。

## 三十一、鲁棒性与失效边界

### 1. 相关类型

类型相关时，独立先验下的 Myerson 公式和 BIC 计算不能直接使用。

### 2. Interdependent Values

如果玩家价值依赖他人的私人信号，私人价值 VCG 与标准 Myerson 分析需要修改。

### 3. 风险厌恶

准线性风险中性支付恒等式可能失效，最优拍卖和合同会改变。

### 4. 有限理性

玩家可能不会精确最佳响应。QRE、认知层级或行为模型可用于描述偏差，但不能继续声称经典 DSIC 的行为预测完全成立。

### 5. 串谋和虚假身份

单人 IC 不等于 group strategy-proof。团队联合报告、账号拆分和机制外交易需要单独建模。

### 6. 无承诺能力

若设计者不能承诺未来支付或分配规则，revelation principle 和动态合同结论可能不适用。

## 三十二、5v5 游戏中的应用

### 1. 角色与位置分配

玩家对打野、辅助、输出等位置有私人偏好。机制可以收集偏好并分配角色，同时用虚拟积分、优先权或未来匹配权补偿承担低偏好位置的玩家。

### 2. 稀缺资源分配

红蓝 buff、经济、装备升级、复活资源和地图目标可视为稀缺资源。VCG 式外部性价格可以用于离线分析每名英雄占用资源对团队其他成员的机会成本。

### 3. 匹配与组队

类型可以包括位置偏好、英雄池、风险风格和沟通意愿。机制目标可以组合等待时间、实力平衡、偏好满足和队伍稳定性。

### 4. 团队奖励

若只奖励击杀，玩家可能抢人头而忽视视野和保护。合同理论提示应对多任务贡献、结果噪声和可操纵指标进行联合设计。

### 5. AI 队友激励

若所有 AI 完全由同一个中央控制器控制，它们并非真正战略参与者，通常不需要 IC。只有当模块拥有不同局部目标、信息或自主更新规则时，机制设计才用于防止局部目标破坏团队目标。

### 6. 玩家拍卖机制

真实货币、概率付费和未成年人场景受法律、平台和伦理约束。数学收益最优不等于产品上可接受，正式应用需要独立合规审查。

## 三十三、MOBA 角色分配示例

设玩家 $i$ 对角色 $j$ 的报告价值为：

$$v_{ij}$$

二元分配变量为：

$$x_{ij}\in\{0,1\}$$

每名玩家只能分配一个角色：

$$\sum_jx_{ij}=1$$

每个角色只能分配给一名玩家：

$$\sum_ix_{ij}=1$$

有效分配求解：

$$\max_x\sum_{i,j}v_{ij}x_{ij}$$

可以用匹配算法求解，再用 VCG 外部性支付计算每名玩家的机会成本。若使用的补偿是不可转让的排队优先权，准线性效用假设需要重新验证。

## 三十四、团队贡献合同示例

设可观察指标为：

$$Y=(Y_{\mathrm{damage}},Y_{\mathrm{vision}},Y_{\mathrm{protect}},Y_{\mathrm{objective}})$$

线性奖励为：

$$w(Y)=s+\beta^{\mathsf T}Y$$

若指标相关且含噪，$\beta$ 不应只按与胜率的表面相关性设置。玩家行为会响应奖励规则，从而改变指标分布。

应加入反操纵约束、团队结果、角色条件基线和异常检测，避免奖励 farming、无效伤害或故意延长对局。

## 三十五、与现有游戏数学层的组合

1. 匹配博弈与赋值模型生成可行角色、玩家和资源分配；
2. Bayesian mechanism design 描述私人类型、报告与支付；
3. VCG 用于福利最大化及外部性审计；
4. Myerson 用于有限、合规的收益目标研究；
5. BCE 允许基于私人类型发送相关团队建议；
6. Contract theory 处理不可观察努力和可操纵绩效指标；
7. P27 的 CMDP 与预算模型加入资源和风险约束；
8. P30 的 PAC-Bayes、confidence sequence 和 conformal risk control 评估机制样本外风险；
9. 所有建议仍需通过游戏规则、公平性、隐私、安全与合规审查。

## 三十六、有限类型机制的求解流程

1. 枚举类型、分配和合法支付范围；
2. 指定先验或条件类型分布；
3. 选择福利、收益、公平或风险目标；
4. 写出 feasibility 约束；
5. 写出 DSIC 或 BIC 约束；
6. 写出 ex-post、interim 或 ex-ante IR；
7. 加入预算、容量、隐私和公平限制；
8. 用 LP、MILP、凸优化或双层优化求解；
9. 检查所有偏离约束的最小余量；
10. 用未参与训练的行为数据和仿真代理做压力测试。

## 三十七、诊断指标

### 1. IC violation

定义最大激励违反量：

$$\varepsilon_{\mathrm{IC}}=\max_{i,\theta_i,\hat\theta_i}\left[U_i(\hat\theta_i\mid\theta_i)-U_i(\theta_i\mid\theta_i)\right]_+$$

### 2. IR violation

$$\varepsilon_{\mathrm{IR}}=\max_{i,\theta_i}\left[\bar u_i(\theta_i)-U_i(\theta_i)\right]_+$$

### 3. Budget deficit

$$\varepsilon_{\mathrm{budget}}=\left[-\sum_ip_i\right]_+$$

### 4. Welfare loss

$$\Delta W=W(x^*,\theta)-W(x,\theta)$$

### 5. Regret under learned behavior

如果参与者不完全理性，应训练偏离策略并测量经验收益，而不是只检查解析约束。

### 6. 分布漂移

分别报告不同版本、段位、地区、角色和队伍结构上的 IC、IR、预算与公平指标。

## 三十八、常见误区

### 1. 把 BIC 写成 DSIC

BIC 只在类型条件期望下成立，DSIC 对任意其他报告都成立。

### 2. 不说明 IR 的时点

ex-ante、interim 和 ex-post IR 的强度和含义不同。

### 3. 认为 revelation principle 证明所有人都会说真话

它是可实现性等价工具，仍需要构造满足相应 IC 的直接机制。

### 4. 认为 VCG 总是预算平衡

VCG 的效率和 DSIC 不保证强预算平衡。

### 5. 对 irregular 分布直接使用原始虚拟价值

需要 ironing 才能恢复分配单调性。

### 6. 忽略类型分布估计误差

Myerson 最优机制可能对尾部分布和样本选择高度敏感。

### 7. 把 noisy outcome 当成 effort

隐藏行动合同必须处理结果噪声与风险分担。

### 8. 只奖励容易测量的指标

会诱导多任务努力错配和 Goodhart 行为。

### 9. 对中央控制 AI 强行加入支付

没有独立目标和战略选择时，机制设计可能只增加复杂度。

### 10. 把数学最优当作产品可用

真实货币、隐私、公平、成瘾与未成年人保护需要独立制度约束。

## 三十九、选择建议

若目标是有效分配且参与者具有准线性私人价值，优先研究 VCG/Groves，并单独审计预算与串谋。

若目标是单物品期望收益最大化，且价值独立、分布可信、参与者风险中性，使用 Myerson；非 regular 分布需要 ironing。

若问题是一般贝叶斯类型与有限分配，用 revelation principle 转为直接机制，再通过 BIC、IR 与 feasibility 线性规划求解。

若问题涉及不可观察努力，使用 moral-hazard principal–agent 模型；若涉及签约前私人类型，使用 adverse-selection 合同菜单。

若参与者是有限理性、可串谋、类型相关或机制缺乏承诺能力，应改用更鲁棒的机制概念，而不是继续引用标准 DSIC/BIC 结论。

## 四十、结论

Bayesian mechanism design 用类型、分配和支付系统地处理私人信息；revelation principle 把复杂机制的可实现性问题压缩到直接 truthful 机制；IR 决定参与者是否愿意参加，IC 决定是否愿意如实报告或遵守建议；VCG 用外部性支付实现福利最大化和 DSIC；Myerson 用虚拟价值实现特定假设下的收益最优；contract theory 则把机制设计扩展到隐藏行动、风险分担和动态承诺。

在游戏系统中，这些方法可以用于角色分配、资源优先权、组队匹配、团队奖励和自主模块协调，但必须先判断参与者是否真正具有私人信息和战略自主性。任何机制结论都应连同信息结构、效用模型、先验、风险态度、预算、串谋、合规和行为实验结果一起报告，不能只展示一个数学上最优的支付公式。
