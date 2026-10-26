# 序贯因果推断与因果 OPE：从 g-formula、Doubly Robust 到 Proximal Learning 和隐藏混杂敏感性

## 摘要

序贯决策数据同时包含时间变化的状态、动作、奖励和后续反馈。动作会改变未来状态，未来状态又影响后续动作，因此普通回归、静态倾向得分或只比较“采取过某动作”和“未采取某动作”的样本，通常无法回答动态策略的因果价值。

序贯因果推断首先定义动态干预和潜在结果，再依靠一致性、正值性、序贯可交换性和无干扰等条件，用 sequential g-formula、逆概率加权或递归回归识别策略价值。Doubly Robust（DR）估计把结果模型与行为策略模型结合：在标准条件下，其中一类模型正确即可保持一致性，但它不能自动修复隐藏混杂、严重缺乏重叠或错误的因果时间顺序。

因果 Off-Policy Evaluation（OPE）把上述方法用于评估日志策略之外的目标策略。若存在未观测混杂，可使用负对照和 proximal causal learning，通过结果桥或处理桥恢复识别；若代理变量、完备性或桥方程条件不可信，则应转向 Rosenbaum、marginal sensitivity model、混杂函数或分布鲁棒界，报告策略价值区间。

本文采用有限时域、奖励越大越好的约定，系统介绍 dynamic treatment regime、sequential g-formula、IPW、MSM、AIPW、序贯 DR、efficient influence function、交叉拟合、因果 OPE、边缘重要性采样、proximal bridge、隐藏混杂敏感性，以及 5v5 游戏回放中的策略评估。

## 一、序贯数据结构

考虑长度为 $T+1$ 的轨迹：

$$O=(L_0,A_0,R_0,L_1,A_1,R_1,\ldots,L_T,A_T,R_T,L_{T+1})$$

$L_t$ 表示动作前可见的状态或协变量，$A_t$ 是动作，$R_t$ 是即时奖励。动作前历史定义为：

$$H_t=(L_0,A_0,R_0,\ldots,L_t)$$

动作后历史可写成：

$$H_t^+=(H_t,A_t,R_t)$$

时间顺序必须按真实决策过程定义。把动作之后产生的变量误放入动作前状态，会制造后处理偏差和信息泄漏。

## 二、动态策略

随机目标策略 $\pi$ 在历史 $H_t$ 上给出动作分布：

$$\pi_t(a\mid H_t)=\mathbb P_{\pi}(A_t=a\mid H_t)$$

确定性动态规则是特殊情形：

$$A_t=d_t(H_t)$$

行为策略记为 $\mu_t(a\mid H_t)$。离线评估的目标是仅使用 $\mu$ 生成的日志，估计目标策略 $\pi$ 的因果价值。

## 三、潜在轨迹与动态干预

对动作序列 $\bar a_t=(a_0,\ldots,a_t)$，定义潜在状态和奖励：

$$L_{t+1}^{\bar a_t},\qquad R_t^{\bar a_t}$$

在动态策略 $\pi$ 下，动作按照 $\pi_t(\cdot\mid H_t^{\pi})$ 生成，对应潜在轨迹记为：

$$O^{\pi}=(L_0,A_0^{\pi},R_0^{\pi},\ldots,L_{T+1}^{\pi})$$

策略价值为：

$$V(\pi)=\mathbb E\left[\sum_{t=0}^T\gamma^tR_t^{\pi}\right],\qquad 0\lt\gamma\leq1$$

策略差异可定义为：

$$\Delta(\pi,\pi_0)=V(\pi)-V(\pi_0)$$

## 四、一致性

一致性要求：若个体实际动作历史等于 $\bar a_t$，则观察结果等于相应潜在结果：

$$\bar A_t=\bar a_t\quad\Longrightarrow\quad L_{t+1}=L_{t+1}^{\bar a_t},\quad R_t=R_t^{\bar a_t}$$

一致性隐含动作版本明确。若“支援中路”包含完全不同的路径、到达时机和技能承诺，却只记录成一个动作标签，一致性就可能失败。

## 五、序贯可交换性

标准无未观测混杂条件为：

$$A_t\perp\!\!\!\perp \left\{L_{s}^{\bar a},R_s^{\bar a}:s\geq t\right\}\mid H_t$$

它表示给定日志中的完整决策历史后，当前动作与未来潜在结果独立。该条件不能仅从观察数据检验，必须结合日志生成机制、领域知识和负对照诊断。

在强化学习语言中，它要求 $H_t$ 已包含行为策略选择动作时使用的全部共同原因。只满足马尔可夫性并不自动等于无隐藏混杂。

## 六、序贯正值性

若目标策略可能选择动作 $a$，行为策略在相同历史上必须有正概率选择它：

$$\pi_t(a\mid h)\gt0\quad\Longrightarrow\quad \mu_t(a\mid h)\gt0$$

理论上的正值性不等于实践中有足够重叠。当 $\mu_t(a\mid h)$ 极小时，重要性权重会爆炸，估计方差和模型外推风险显著增加。

确定性规则、硬安全屏蔽和版本限定动作常导致结构性不重叠，此时不能只靠增加样本量解决。

## 七、无干扰与单位定义

标准潜在结果假设通常要求一个单位的结果不受其他单位处理影响。但多人游戏、社交网络和集群系统存在明显干扰：

$$Y_i(\bar a_i,\bar a_{-i})\neq Y_i(\bar a_i)$$

解决方法包括把整局、整队或交互群组定义为单位，显式建立网络干扰模型，或只估计特定暴露映射下的效应。若单位定义错误，后续再精细的 DR 估计也无法恢复目标因果量。

## 八、Sequential g-formula

在一致性、序贯可交换性和正值性成立时，目标策略下的联合分布由 g-formula 识别：

$$p^{\pi}(\bar l_{T+1},\bar a_T,\bar r_T)=p(l_0)\prod_{t=0}^T\pi_t(a_t\mid h_t)p(r_t,l_{t+1}\mid h_t,a_t)$$

因此：

$$V(\pi)=\int\sum_{\bar a_T}\left(\sum_{t=0}^T\gamma^tr_t\right)p(l_0)\prod_{t=0}^T\pi_t(a_t\mid h_t)p(r_t,l_{t+1}\mid h_t,a_t)\,d\nu$$

$d\nu$ 表示对连续变量积分、对离散变量求和。该公式直接展示了策略机制和环境机制的分离。

## 九、递归 g-computation

定义终端条件价值：

$$Q_T(h_T,a_T)=\mathbb E[R_T\mid H_T=h_T,A_T=a_T]$$

策略条件价值为：

$$V_T(h_T)=\sum_a\pi_T(a\mid h_T)Q_T(h_T,a)$$

向后递归：

$$Q_t(h_t,a_t)=\mathbb E\left[R_t+\gamma V_{t+1}(H_{t+1})\mid H_t=h_t,A_t=a_t\right]$$

$$V_t(h_t)=\sum_a\pi_t(a\mid h_t)Q_t(h_t,a)$$

最终：

$$V(\pi)=\mathbb E[V_0(H_0)]$$

## 十、Monte Carlo g-computation

若已估计条件生成模型：

$$\widehat p(r_t,l_{t+1}\mid h_t,a_t)$$

可从基线分布采样，按目标策略选择动作，再从环境模型滚动生成反事实轨迹。模拟回报均值估计 $V(\pi)$。

该方法直观且支持复杂随机策略，但需要每个时间点的条件转移模型在目标策略访问区域内可靠。长时域模型误差会递归累积。

## 十一、时间变化混杂

$L_t$ 可能同时满足：

1. 受过去动作 $A_{t-1}$ 影响；
2. 影响当前动作 $A_t$；
3. 影响未来结果。

若在普通结果回归中直接调整这类变量，可能阻断过去动作的部分因果路径；若不调整，又会留下当前动作的混杂。g-formula、Marginal Structural Model 和结构嵌套模型正是为这种反馈结构设计的。

## 十二、轨迹重要性权重

单步密度比为：

$$\rho_t=\frac{\pi_t(A_t\mid H_t)}{\mu_t(A_t\mid H_t)}$$

截至时刻 $t$ 的累计权重为：

$$\rho_{0:t}=\prod_{k=0}^t\rho_k$$

普通轨迹 IS 估计量为：

$$\widehat V_{\mathrm{IS}}=\frac{1}{n}\sum_{i=1}^n\rho_{0:T}^{(i)}\sum_{t=0}^T\gamma^tR_t^{(i)}$$

当时域长或策略差异大时，累计乘积会造成极高方差。

## 十三、Per-Decision Importance Sampling

每个时刻的奖励只需校正此前的动作分布：

$$\widehat V_{\mathrm{PDIS}}=\frac{1}{n}\sum_{i=1}^n\sum_{t=0}^T\gamma^t\rho_{0:t}^{(i)}R_t^{(i)}$$

PDIS 通常比整轨迹 IS 方差更小，但仍依赖正确的行为策略概率和充分重叠。若日志只保存最终动作而没有动作候选、屏蔽规则和随机化概率，则权重模型可能无法还原。

## 十四、稳定化与自归一化权重

Marginal Structural Model 常使用稳定化权重：

$$SW_i=\prod_{t=0}^T\frac{p(A_{i,t}\mid \bar A_{i,t-1},L_{i,0})}{p(A_{i,t}\mid H_{i,t})}$$

自归一化 PDIS 可写成：

$$\widehat V_{\mathrm{WPDIS}}=\sum_{t=0}^T\gamma^t\frac{\sum_i\rho_{0:t}^{(i)}R_t^{(i)}}{\sum_i\rho_{0:t}^{(i)}}$$

自归一化通常降低方差，但在有限样本中引入偏差。它不是重叠失败的根治方法。

## 十五、Marginal Structural Model

MSM 直接对干预历史下的边缘均值建模：

$$\mathbb E[Y^{\bar a}]=m(\bar a;\beta)$$

通过逆概率权重创建伪总体，使处理历史近似与时间变化混杂独立，再估计 $\beta$。例如：

$$m(\bar a;\beta)=\beta_0+\sum_{t=0}^T\beta_{t+1}a_t$$

MSM 适合解释累计处理效应，但模型形式错误仍会造成偏差，且高维动作历史需要结构化参数化。

## 十六、单阶段 AIPW

先看单阶段策略价值。令：

$$q(x,a)=\mathbb E[Y\mid X=x,A=a],\qquad \mu(a\mid x)=\mathbb P(A=a\mid X=x)$$

随机目标策略 $\pi$ 的 AIPW 得分为：

$$\phi_{\mathrm{AIPW}}=\sum_a\pi(a\mid X)q(X,a)+\frac{\pi(A\mid X)}{\mu(A\mid X)}\left[Y-q(X,A)\right]$$

价值估计为样本均值：

$$\widehat V_{\mathrm{AIPW}}=\frac{1}{n}\sum_{i=1}^n\widehat\phi_{\mathrm{AIPW},i}$$

## 十七、Doubly Robust 的含义

标准 AIPW 在以下任一条件下保持一致：

1. 结果模型 $q$ 正确；
2. 倾向模型 $\mu$ 正确。

其偏差通常具有乘积结构：

$$\operatorname{Bias}(\widehat V_{\mathrm{DR}})\approx \mathbb E\left[(\widehat q-q)(\widehat w-w)\right]$$

因此两个 nuisance 模型都以足够速度收敛时，价值估计可达到根号样本率。

“双重稳健”不表示对任意两个错误模型仍稳健，也不表示对未观测混杂、正值性违反、数据泄漏或目标定义错误稳健。

## 十八、序贯 Direct Method

用递归回归估计 $\widehat Q_t$ 和 $\widehat V_t$ 后，Direct Method 为：

$$\widehat V_{\mathrm{DM}}=\frac{1}{n}\sum_{i=1}^n\widehat V_0(H_{i,0})$$

DM 不使用重要性权重，方差较低，但完全依赖序贯结果模型。在目标策略访问而行为策略很少访问的历史上，它本质上依赖外推。

## 十九、序贯 Doubly Robust OPE

定义估计的时序差分残差：

$$\widehat\delta_t=R_t+\gamma\widehat V_{t+1}(H_{t+1})-\widehat Q_t(H_t,A_t)$$

令 $\widehat V_{T+1}=0$。标准序贯 DR 估计量为：

$$\widehat V_{\mathrm{DR}}=\frac{1}{n}\sum_{i=1}^n\left[\widehat V_0(H_{i,0})+\sum_{t=0}^T\gamma^t\widehat\rho_{0:t}^{(i)}\widehat\delta_t^{(i)}\right]$$

第一项是模型预测，第二项用重要性加权残差校正模型偏差。

## 二十、序贯双重稳健条件

在标准纵向模型中，如果所有阶段的结果递归模型正确，或所有阶段的处理机制正确，DR 估计可保持一致。某些专门构造的 sequentially doubly robust 或 multiply robust 估计器允许不同阶段由不同 nuisance 组件正确。

不能把“每个阶段任意挑一个模型正确”直接套到所有 DR 公式。稳健性集合取决于具体估计方程和递归构造。

## 二十一、有效影响函数

在非参数纵向模型下，策略价值的影响函数具有“初始预测加加权残差”的结构：

$$\varphi(O)=V_0(H_0)-V(\pi)+\sum_{t=0}^T\gamma^t\rho_{0:t}\left[R_t+\gamma V_{t+1}(H_{t+1})-Q_t(H_t,A_t)\right]$$

在正则条件下：

$$\mathbb E[\varphi(O)]=0$$

以有效影响函数构造的一步估计或 TMLE 可兼顾灵活机器学习和渐近推断。

## 二十二、交叉拟合

若 $Q_t$ 和 $\mu_t$ 由高容量模型估计，在同一数据上训练并计算影响函数会产生过拟合偏差。交叉拟合把样本分成 $K$ 折：

$$\mathcal I=\mathcal I_1\cup\cdots\cup\mathcal I_K$$

对第 $k$ 折的得分，nuisance 模型只用 $\mathcal I\setminus\mathcal I_k$ 训练。最后合并所有折的得分。

对于轨迹数据，划分单位应是整条独立轨迹、玩家簇或比赛簇，不能把同一轨迹的时间点随机拆到训练和验证两侧。

## 二十三、置信区间

若轨迹相互独立且正则条件成立，可用影响函数方差：

$$\widehat{\operatorname{SE}}(\widehat V)=\sqrt{\frac{1}{n(n-1)}\sum_{i=1}^n(\widehat\varphi_i-\bar\varphi)^2}$$

近似置信区间为：

$$\widehat V\pm z_{1-\alpha/2}\widehat{\operatorname{SE}}(\widehat V)$$

若数据按玩家、队伍、服务器或版本聚类，应使用聚类稳健方差或按簇 bootstrap。普通逐行 bootstrap 会低估相关性。

## 二十四、重叠诊断

有效样本量可定义为：

$$\operatorname{ESS}_t=\frac{\left(\sum_i\rho_{0:t}^{(i)}\right)^2}{\sum_i\left(\rho_{0:t}^{(i)}\right)^2}$$

还应检查权重分位数、最大权重、动作覆盖、目标策略质量落在哪些行为策略低密度区域，以及不同时间点的 ESS 衰减。

截断权重：

$$\widetilde\rho_{0:t}=\min\{\rho_{0:t},c\}$$

可降低方差，但会引入偏差；应同时报告不同截断阈值下的敏感性。

## 二十五、因果 OPE 与普通预测

预测问题估计：

$$\mathbb E[Y\mid H_t,A_t=a]$$

因果 OPE 需要：

$$\mathbb E[Y^{\pi}]$$

若动作由风险、玩家意图或隐藏战术驱动，条件均值可能主要反映“为什么选择该动作”，而不是“该动作造成什么结果”。高预测精度不保证策略价值具有因果解释。

## 二十六、Markov OPE 与历史 OPE

若观察状态 $S_t$ 满足充分状态条件，可写：

$$Q^{\pi}(s,a)=\mathbb E[R_t+\gamma V^{\pi}(S_{t+1})\mid S_t=s,A_t=a]$$

若 $S_t$ 丢失行为策略使用的信息，则应使用更完整的 $H_t$，或承认存在隐藏混杂。仅因为模型是 MDP，就把压缩特征当作充分状态，是因果 OPE 的常见错误。

## 二十七、边缘密度比

轨迹权重乘积方差很高，可直接估计目标策略与行为策略的状态动作占用测度比：

$$w_t(s,a)=\frac{d_t^{\pi}(s,a)}{d_t^{\mu}(s,a)}$$

价值可写成：

$$V(\pi)=\sum_{t=0}^T\gamma^t\mathbb E_{(S_t,A_t)\sim d_t^{\mu}}\left[w_t(S_t,A_t)R_t\right]$$

DICE 类方法通过 Bellman 流平衡估计密度比。它降低了显式轨迹乘积，但仍依赖状态充分性、覆盖和估计方程可识别。

## 二十八、策略依赖的目标总体

策略价值可能针对不同总体：

$$V_{\mathcal P}(\pi)=\mathbb E_{L_0\sim\mathcal P}[Y^{\pi}]$$

若训练日志来自高段位玩家，而目标部署在全体玩家，基线分布也发生变化。应明确是评估日志总体、部署总体还是版本迁移后的总体，并对基线协变量漂移做重加权或运输性分析。

## 二十九、隐藏混杂为何破坏 OPE

设 $U_t$ 同时影响动作和未来结果：

$$U_t\rightarrow A_t,\qquad U_t\rightarrow R_t,L_{t+1}$$

若 $U_t$ 未包含在 $H_t$ 中，则：

$$A_t\not\!\perp\!\!\!\perp Y^{\pi}\mid H_t$$

普通 g-formula、IPW 和 DR 都可能有偏。DR 只在观察到足以控制混杂的变量后，针对结果模型或倾向模型的错设提供保护。

## 三十、负对照变量

负对照暴露 $Z$ 应与隐藏混杂有关，但在给定真实混杂和处理后不直接影响结果。负对照结果 $W$ 应受隐藏混杂影响，但不受当前处理直接影响。

理想化代理条件可写成：

$$Y\perp\!\!\!\perp Z\mid A,U,X$$

$$W\perp\!\!\!\perp (A,Z)\mid U,X$$

观察到负对照与结果或处理之间的异常关联，可揭示残余混杂；在更强完备性条件下，它们还可用于 proximal identification。

## 三十一、Proximal Causal Learning

Proximal causal learning 不要求直接观测隐藏混杂 $U$，而是使用两类代理：

- treatment-inducing proxy $Z$；
- outcome-inducing proxy $W$。

核心不是简单把 $Z$ 和 $W$ 都放入回归，而是求解一个条件矩方程。代理相关性过弱、排除条件失败或完备性不成立时，桥函数可能不存在、不可唯一识别或极不稳定。

## 三十二、结果混杂桥

结果桥函数 $h$ 满足：

$$\mathbb E[Y\mid Z,A=a,X]=\mathbb E[h(W,a,X)\mid Z,A=a,X]$$

在代理条件和完备性等假设下：

$$\mathbb E[Y(a)]=\mathbb E[h(W,a,X)]$$

$h(W,a,X)$ 不是普通的 $\mathbb E[Y\mid W,A=a,X]$。它是由条件积分方程定义的桥函数，求解常具有病态逆问题性质。

## 三十三、处理混杂桥

处理桥 $q$ 可由：

$$\mathbb E[q(Z,a,X)\mid W,A=a,X]=\frac{1}{\mathbb P(A=a\mid W,X)}$$

定义。在相应条件下：

$$\mathbb E[Y(a)]=\mathbb E\left[\mathbf 1\{A=a\}q(Z,a,X)Y\right]$$

结果桥和处理桥分别类似结果回归与逆概率权重，但它们针对的是代理变量诱导的积分方程，而不是直接观测混杂下的标准 nuisance 模型。

## 三十四、Proximal Doubly Robust 得分

对固定动作 $a$，proximal DR 得分为：

$$\phi_a^{\mathrm{PDR}}=h(W,a,X)+\mathbf 1\{A=a\}q(Z,a,X)\left[Y-h(W,a,X)\right]$$

对只依赖 $X$ 的随机目标策略：

$$\phi_{\pi}^{\mathrm{PDR}}=\sum_a\pi(a\mid X)h(W,a,X)+\pi(A\mid X)q(Z,A,X)\left[Y-h(W,A,X)\right]$$

在合适的 proximal 模型中，结果桥或处理桥正确可提供双重稳健性。但代理结构、桥存在性和完备性仍是额外且不可省略的识别条件。

## 三十五、完备性

一种典型完备性条件是：若平方可积函数 $g$ 满足：

$$\mathbb E[g(U)\mid Z,A,X]=0$$

则：

$$g(U)=0\quad\text{几乎处处}$$

直观上，代理 $Z$ 必须包含足够丰富的关于 $U$ 的变化，使条件期望算子没有非平凡零空间。完备性比普通相关性强，通常不能直接由有限样本验证。

## 三十六、桥函数的数值求解

离散代理可把桥方程写成线性系统：

$$m_{z,a,x}=\sum_w h(w,a,x)p(w\mid z,a,x)$$

连续高维代理可使用 sieve、核方法、正则化最小二乘、GMM、minimax 学习或神经网络。一个常见正则目标为：

$$\min_h\left\|\widehat{\mathbb E}[Y-h(W,A,X)\mid Z,A,X]\right\|^2+\lambda\|h\|_{\mathcal H}^2$$

正则化缓解病态性，但会引入偏差；应报告正则路径、弱代理诊断和样本外矩条件残差。

## 三十七、序贯 Proximal g-formula

在纵向隐藏混杂中，需要每个时刻的处理代理 $Z_t$、结果代理 $W_t$ 和递归桥。概念上，末期桥先吸收终端结果，再向前构造：

$$\mathbb E[Y_{t+1}^{\mathrm{bridge}}\mid Z_t,H_t,A_t]=\mathbb E[h_t(W_t,H_t,A_t)\mid Z_t,H_t,A_t]$$

目标策略随后对动作做积分：

$$V_t^{\pi}(H_t,W_t)=\sum_a\pi_t(a\mid H_t)h_t(W_t,H_t,a)$$

完整识别需要逐期代理排除条件、序贯完备性和正值性。不能把单阶段 proximal 公式逐行复制就默认纵向识别成立。

## 三十八、Proximal Causal OPE

在策略评估中，代理变量应对应行为决策时的隐藏信息。例如：

- $Z_t$：影响动作但不直接影响后续收益的决策侧代理；
- $W_t$：反映潜在局势但不受当前动作直接影响的结果侧代理。

可构造序贯桥或 proximal Bellman 方程，再对目标策略动作分布积分。若目标策略使用了桥建模中未允许的信息，估计目标也会改变。

## 三十九、工具变量与 Proximal 方法的区别

工具变量 $Z$ 通常需要影响处理、排除对结果的直接路径，并满足独立性；它常识别局部效应或结构参数。Proximal 方法使用成对代理和桥方程，目标是恢复更一般的因果均值。

两者都不是“找到一个与动作相关的变量”即可。排除限制、相关性、单调性、完备性和目标效应类型应分别陈述。

## 四十、隐藏混杂敏感性分析

当无混杂和 proximal 识别都不足以令人信服时，应把隐藏混杂强度作为参数，计算：

$$V^{-}(\pi;\Gamma)\leq V(\pi)\leq V^{+}(\pi;\Gamma)$$

$\Gamma=1$ 通常对应无额外隐藏偏差；$\Gamma$ 增大允许更强混杂。关键结果是策略排序在多大 $\Gamma$ 下发生反转，而不是只报告一个任意参数点。

## 四十一、Rosenbaum 敏感性模型

对具有相同观察协变量的两个单位，隐藏混杂可使处理赔率相差至多 $\Gamma$：

$$\frac{1}{\Gamma}\leq\frac{e_i/(1-e_i)}{e_j/(1-e_j)}\leq\Gamma$$

其中 $e_i=\mathbb P(A_i=1\mid X_i,U_i)$。该模型常用于匹配观察研究的显著性界和效应界。

在序贯环境中，需要说明 $\Gamma$ 是逐时刻限制还是整条轨迹限制；逐时刻小偏差也可能随时间累积。

## 四十二、Marginal Sensitivity Model

设名义倾向得分为：

$$e(x)=\mathbb P(A=1\mid X=x)$$

真实倾向得分允许依赖隐藏变量：

$$e_0(x,u)=\mathbb P(A=1\mid X=x,U=u)$$

赔率比敏感性模型约束：

$$\frac{1}{\Lambda}\leq\frac{e_0(x,u)/(1-e_0(x,u))}{e(x)/(1-e(x))}\leq\Lambda$$

在该约束下优化加权结果，可得到最坏与最好情形价值界。

## 四十三、序贯敏感性模型

逐期真实行为概率记为：

$$\mu_{0,t}(a\mid H_t,U_t)$$

名义日志模型为 $\mu_t(a\mid H_t)$。可限制每期赔率偏离：

$$\frac{1}{\Lambda_t}\leq\frac{\operatorname{odds}\{\mu_{0,t}(1\mid H_t,U_t)\}}{\operatorname{odds}\{\mu_t(1\mid H_t)\}}\leq\Lambda_t$$

目标是对所有满足约束的隐藏行为机制求策略价值上下界。由于权重跨期相乘，必须保持概率归一化和动态一致性，不能独立把每行权重推到极端。

## 四十四、混杂函数

二元动作下可定义：

$$c_a(x)=\mathbb E[Y(a)\mid A=a,X=x]-\mathbb E[Y(a)\mid A=1-a,X=x]$$

则：

$$\mathbb E[Y(a)\mid X=x]=\mathbb E[Y\mid A=a,X=x]-\{1-e_a(x)\}c_a(x)$$

其中 $e_a(x)=\mathbb P(A=a\mid X=x)$。由领域专家给定 $c_a(x)$ 的范围或分布，可以直接观察隐藏选择偏差对策略价值的影响。

纵向情形需要时间相关的混杂函数，并明确它影响即时奖励、后续状态还是二者。

## 四十五、部分识别与鲁棒策略比较

若策略价值只能识别为区间：

$$\mathcal V(\pi)=[V^{-}(\pi),V^{+}(\pi)]$$

当：

$$V^{-}(\pi_1)\gt V^{+}(\pi_0)$$

可在给定敏感性模型下稳健断言 $\pi_1$ 优于 $\pi_0$。若区间重叠，则数据和假设不足以确定排序。

部署决策可最大化最坏情形价值：

$$\pi^{\star}\in\operatorname*{arg\,max}_{\pi}V^{-}(\pi)$$

## 四十六、删失、掉线与缺失

若轨迹在时刻 $t$ 被删失，令 $C_t=1$ 表示仍可观测。逆删失权重为：

$$\omega_t^C=\prod_{k=0}^t\frac{1}{\mathbb P(C_k=1\mid H_k,A_k,C_{k-1}=1)}$$

可与动作权重组合。若掉线由未记录的挫败感、设备状态或队内冲突驱动，则删失也可能存在隐藏混杂，需要额外代理或敏感性分析。

## 四十七、5v5 回放中的因果问题

设每个决策窗口记录：

$$H_t=(\text{经济、等级、血量、位置、兵线、视野、冷却、目标计时、历史动作})$$

$A_t$ 可以是开团、撤退、推进、控龙、换线或回城，奖励为后续一段时间的经济差、目标收益、生存和胜率变化。

行为策略受到未记录的语音指挥、玩家意图、对手推断和操作信心影响。这些变量同时影响动作与结果，是典型隐藏混杂来源。

## 四十八、游戏日志设计

为了支持因果 OPE，日志应保存：

1. 动作发生前的完整特征快照；
2. 候选动作集合和安全屏蔽结果；
3. 行为策略对每个候选动作的概率；
4. 模型版本、地图版本和匹配分段；
5. 队伍级标识以处理干扰与聚类；
6. 视野内外信息的权限边界；
7. 动作延迟、取消和执行失败；
8. 删失、掉线与异常结束原因。

只有最终动作标签而没有候选概率，会显著削弱 IPW 和 DR OPE 的可信度。

## 四十九、端到端验收清单

一个可信的序贯因果 OPE 系统至少应检查：

1. 时间顺序、单位和干预版本是否明确；
2. 目标策略是否只使用部署时可得信息；
3. 序贯可交换性由哪些日志字段支撑；
4. 各时刻重叠、权重和 ESS 是否可接受；
5. DM、IS、PDIS、DR 和边缘比方法是否一致；
6. nuisance 模型是否按整轨迹交叉拟合；
7. 置信区间是否处理聚类与版本漂移；
8. 负对照是否提示残余混杂；
9. proximal 代理、桥残差和完备性论证是否充分；
10. 策略结论在多组敏感性参数下是否稳定。

还应使用已知生成机制的半合成数据验证覆盖、混杂和桥估计失败时，系统能否给出正确警报。

## 五十、结论

Sequential g-formula 给出了动态策略价值的基本识别公式；递归 g-computation、IPW 和 MSM 分别从环境建模、处理机制重加权和边缘结构建模实现该公式。Doubly Robust 方法把结果模型与行为策略模型结合，并通过影响函数支持高效估计和统计推断。

因果 OPE 的核心不是选择一个更复杂的估计器，而是确认目标策略、时间顺序、历史充分性、正值性和干扰结构。DR 可以缓解观察混杂已充分控制后的模型错设，却不能自动消除隐藏混杂。

当合格的处理代理和结果代理存在时，proximal causal learning 可通过桥方程在未直接观测混杂的情况下恢复识别；当这些强条件也无法成立时，隐藏混杂敏感性分析和部分识别区间是更诚实的答案。

在 5v5 游戏回放中，应把整局或队伍作为相关单位，完整记录候选动作概率和决策前信息，使用交叉拟合的序贯 DR 作为主估计，并以负对照、proximal bridge 和敏感性区间审计未记录意图、沟通和对手认知造成的偏差。
