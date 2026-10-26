# Blackwell Approachability 与对抗 Bandit：EXP3、Swap Regret、Partial Monitoring 和校准学习

## 摘要

在线决策研究在环境持续变化、反馈不完整且可能具有对抗性时如何学习。Blackwell Approachability 把目标写成向量收益空间中的集合，并要求长期平均向量逐渐接近该集合；外部遗憾、内部遗憾、公平约束和多指标安全都可转化为 approachability。对抗多臂老虎机只观察被选动作的损失，EXP3 通过重要性加权构造无偏损失估计，在最坏环境中获得次线性外部遗憾。

Swap regret 允许把每次实际选择的动作按一个映射替换为另一个动作，比外部遗憾更强；多玩家都具有 vanishing swap/internal regret 时，经验分布接近相关均衡。Partial Monitoring 进一步允许玩家只观察与动作和环境结果共同决定的信号，甚至看不到所选动作损失；其可学性由损失差能否从信号分布识别决定，并出现 $\sqrt T$、$T^{2/3}$ 和线性遗憾等不同难度等级。

校准学习要求长期预测频率与实际频率一致。它可以通过 Blackwell 向量逼近构造，并与内部遗憾、相关均衡和对抗预测相连接。本文系统介绍以上理论、算法、界、适用条件和 5v5 游戏中的不完全反馈决策应用。

## 一、在线决策协议

动作集合为：

$$\mathcal A=\{1,\ldots,K\}$$

每一轮 $t=1,\ldots,T$：

1. 学习者选择动作 $I_t$；
2. 环境产生损失向量 $\ell_t\in[0,1]^K$；
3. 学习者承担 $\ell_t(I_t)$；
4. 学习者只获得反馈模型允许的信息。

累积损失为：

$$L_T=\sum_{t=1}^T\ell_t(I_t)$$

## 二、对抗环境

Oblivious adversary 在游戏开始前固定整个损失序列。Non-anticipating adaptive adversary 可以依赖历史，但不能在看到当前随机动作 $I_t$ 后再选择 $\ell_t$。

形式上要求：

$$\ell_t\perp\!\!\!\perp I_t\mid\mathcal F_{t-1}$$

若环境先观察当前动作再指定损失，它可以总让所选动作损失最高，标准 bandit regret 一般无法保证次线性。

## 三、外部遗憾

与事后最佳固定动作比较：

$$R_T^{\mathrm{ext}}=\sum_{t=1}^T\ell_t(I_t)-\min_{i\in\mathcal A}\sum_{t=1}^T\ell_t(i)$$

无外部遗憾要求：

$$\frac{R_T^{\mathrm{ext}}}{T}\rightarrow0$$

这并不表示每轮选择最优，也不比较随时间切换的动态策略。

## 四、反馈模型

Full information 每轮观察整个 $\ell_t$。Bandit feedback 只观察：

$$\ell_t(I_t)$$

Semi-bandit 在选择组合动作时观察被选资源的分量损失。Partial monitoring 只观察信号：

$$S_t=H(I_t,J_t)$$

其中 $J_t$ 是环境结果，信号不一定能直接给出损失。

## 五、Full Information 的 Hedge

指数权重算法维护：

$$w_{t+1,i}=w_{t,i}\exp\{-\eta\ell_t(i)\}$$

选择分布为：

$$p_{t,i}=\frac{w_{t,i}}{\sum_jw_{t,j}}$$

对损失在 $[0,1]$ 的情形，适当选择学习率可得：

$$R_T^{\mathrm{ext}}=O\left(\sqrt{T\log K}\right)$$

Bandit 情形看不到全部 $\ell_t(i)$，因此不能直接使用该更新。

## 六、重要性加权估计

若：

$$I_t\sim p_t$$

定义：

$$\widehat\ell_{t,i}=\frac{\ell_t(I_t)\mathbf 1\{I_t=i\}}{p_{t,i}}$$

条件期望满足：

$$\mathbb E[\widehat\ell_{t,i}\mid\mathcal F_{t-1}]=\ell_t(i)$$

因此这是无偏反事实损失估计。代价是当 $p_{t,i}$ 很小时方差很大。

## 七、EXP3

EXP3 维护权重：

$$w_{1,i}=1$$

使用带显式探索的分布：

$$p_{t,i}=(1-\gamma)\frac{w_{t,i}}{\sum_jw_{t,j}}+\frac{\gamma}{K}$$

采样 $I_t$，构造 $\widehat\ell_{t,i}$，再更新：

$$w_{t+1,i}=w_{t,i}\exp\{-\eta\widehat\ell_{t,i}\}$$

探索保证：

$$p_{t,i}\geq\frac{\gamma}{K}$$

## 八、EXP3 的遗憾界

标准指数势分析给出形如：

$$\mathbb E[R_T^{\mathrm{ext}}]\leq\frac{\log K}{\eta}+\frac{\eta}{2}\sum_{t=1}^T\mathbb E\left[\sum_ip_{t,i}\widehat\ell_{t,i}^2\right]+\gamma T$$

重要性估计满足：

$$\mathbb E\left[\sum_ip_{t,i}\widehat\ell_{t,i}^2\mid\mathcal F_{t-1}\right]=\sum_i\ell_t(i)^2\leq K$$

适当选择 $\eta$ 和 $\gamma$ 后：

$$\mathbb E[R_T^{\mathrm{ext}}]=O\left(\sqrt{TK\log K}\right)$$

## 九、探索与方差

重要性估计的条件二阶矩为：

$$\mathbb E[\widehat\ell_{t,i}^2\mid\mathcal F_{t-1}]=\frac{\ell_t(i)^2}{p_{t,i}}$$

小概率动作导致高方差。显式探索降低方差，却会产生探索损失。

探索率过小会使估计不稳定；过大则长期频繁选择低质量动作。理论参数通常依赖 $T$，未知时域可使用 doubling trick 或自适应学习率。

## 十、EXP3.P 与高概率界

原始 EXP3 主要给出期望遗憾界。EXP3.P 通过偏置奖励估计和显式探索控制尾部，获得高概率保证：

$$R_T^{\mathrm{ext}}=O\left(\sqrt{TK\log\frac{K}{\delta}}\right)$$

以至少 $1-\delta$ 的概率成立，忽略不同版本中的低阶项。

高概率算法的更新公式和常数依实现而异，不能只把期望界机械替换成概率界。

## 十一、Implicit Exploration

EXP3-IX 使用：

$$\widetilde\ell_{t,i}=\frac{\ell_t(I_t)\mathbf 1\{I_t=i\}}{p_{t,i}+\gamma}$$

分母中的 $\gamma$ 产生受控偏差，却改善浓缩性质。它可减少显式均匀探索造成的性能损失。

无偏性不是唯一目标；在对抗在线学习中，适当偏置可能换来更好的高概率方差控制。

## 十二、对抗与随机 Bandit

随机 bandit 假设每个动作从固定或结构化分布产生奖励，常用 UCB 或 Thompson Sampling，并获得依赖 gap 的对数遗憾。

对抗 bandit 不假设固定均值，EXP3 提供最坏情形：

$$\widetilde O(\sqrt{KT})$$

保证。若环境实际上随机，纯 EXP3 可能比利用随机结构的算法保守；可使用 best-of-both-worlds 算法兼顾两类环境。

## 十三、动态比较器

若比较器允许切换，定义最多 $S$ 次切换的遗憾：

$$R_T^{(S)}=\sum_t\ell_t(I_t)-\min_{i_{1:T}:\operatorname{switch}(i_{1:T})\leq S}\sum_t\ell_t(i_t)$$

固定动作无遗憾不能保证动态遗憾。需要 EXP3.S、固定份额更新、变化预算或重启机制。

若环境任意快速变化且比较器不受限制，次线性动态遗憾通常不可能。

## 十四、延迟反馈

若第 $t$ 轮反馈在 $t+d_t$ 才到达，算法只能使用已到达信息。总延迟为：

$$D=\sum_{t=1}^Td_t$$

适当延迟 bandit 算法可获得依赖 $T+D$ 的遗憾界。若延迟由动作和未观测损失共同决定，还可能产生选择偏差，不能只把反馈简单排队。

## 十五、睡眠与受限动作

每轮可行动作集合为：

$$\mathcal A_t\subseteq\mathcal A$$

Sleeping bandit 只在 $\mathcal A_t$ 上分配概率。比较器也必须明确是最佳始终可行动作，还是按可用性条件定义的策略。

在游戏中，冷却、距离、资源和安全规则会让动作临时不可用；把不可行动作仍放进归一化分布会破坏概率和遗憾定义。

## 十六、组合与 Semi-Bandit

若动作是资源子集 $S_t\subseteq[d]$，损失为：

$$\ell_t(S_t)=\sum_{j\in S_t}\ell_{t,j}$$

Semi-bandit 反馈观察所有被选分量 $\ell_{t,j}$。可以对每个资源构造重要性估计，并结合在线线性优化。

若只观察总和而看不到分量，就变成更困难的 bandit linear optimization。

## 十七、Blackwell 向量收益

设玩家动作 $a\in\mathcal A$、对手动作或环境结果 $b\in\mathcal B$，向量收益为：

$$g(a,b)\in\mathbb R^d$$

时间平均为：

$$\bar g_T=\frac1T\sum_{t=1}^Tg(a_t,b_t)$$

给定闭凸目标集 $C\subseteq\mathbb R^d$，approachability 要求：

$$\operatorname{dist}(\bar g_T,C)\rightarrow0$$

## 十八、Blackwell 条件

对混合动作 $x\in\Delta(\mathcal A)$ 和 $y\in\Delta(\mathcal B)$，记双线性延拓为 $g(x,y)$。闭凸集 $C$ 可逼近的经典条件为：

$$\forall y\in\Delta(\mathcal B),\ \exists x\in\Delta(\mathcal A):g(x,y)\in C$$

它表示无论对手采用何种混合分布，玩家都有一个混合动作把单轮期望向量放入目标集。

对非凸集合、受限信息或非双线性模型，需要更一般条件。

## 十九、投影策略

令：

$$c_t=\Pi_C(\bar g_{t-1})$$

若 $\bar g_{t-1}\notin C$，选择 $x_t$ 使：

$$\max_{y\in\Delta(\mathcal B)}\left\langle\bar g_{t-1}-c_t,\ g(x_t,y)-c_t\right\rangle\leq0$$

几何上，玩家选择动作，使下一步期望向量不越过投影点处的分离超平面。

## 二十、逼近速率

若：

$$\|g(a,b)-c\|_2\leq G$$

对相关状态成立，则经典分析给出：

$$\mathbb E[\operatorname{dist}(\bar g_T,C)]=O\left(\frac{G}{\sqrt T}\right)$$

高概率界可由鞅浓缩得到。速率常数取决于向量范数、目标几何和反馈噪声。

## 二十一、外部遗憾作为 Approachability

定义遗憾向量第 $i$ 个分量：

$$g_i(I_t,\ell_t)=\ell_t(I_t)-\ell_t(i)$$

目标集取负正交象限：

$$C=\mathbb R_-^K$$

若：

$$\operatorname{dist}\left(\frac1T\sum_tg_t,C\right)\rightarrow0$$

则每个固定动作的平均外部遗憾非正，从而：

$$\frac{R_T^{\mathrm{ext}}}{T}\rightarrow0$$

## 二十二、多目标约束

若每轮产生收益、风险、公平和资源向量：

$$g_t=(r_t,-q_t,-c_t,f_t)$$

目标集合可写为：

$$C=\{z:z_1\geq r_{\min},\ z_2\geq-q_{\max},\ z_3\geq-c_{\max},\ |z_4|\leq\varepsilon\}$$

Approachability 可以直接控制长期向量约束，而不必先把所有指标压成单一加权和。

目标集必须可行；若 Blackwell 条件失败，任何算法都不能保证逼近。

## 二十三、Bandit Approachability

若只观察所选动作反馈，可构造向量收益估计：

$$\widehat g_t(a)=\frac{\mathbf 1\{I_t=a\}}{p_t(a)}g_t(a)$$

再用估计平均向量执行投影策略。重要性估计需要所有可能影响目标的动作拥有正概率。

维数、最小动作概率和向量范围会进入逼近速率。若信号不足以识别向量收益，则问题属于 partial monitoring，而非普通 bandit approachability。

## 二十四、内部遗憾

把每次选择 $i$ 的轮次统一替换为 $j$，对应 pairwise internal regret：

$$R_{i\rightarrow j}(T)=\sum_{t=1}^T\mathbf 1\{I_t=i\}\left[\ell_t(i)-\ell_t(j)\right]$$

无内部遗憾要求：

$$\max_{i,j}R_{i\rightarrow j}(T)=o(T)$$

它比外部遗憾更强，因为它允许比较依赖于实际所选动作的条件偏离。

## 二十五、Swap Regret

对任意映射：

$$\phi:\mathcal A\rightarrow\mathcal A$$

swap regret 为：

$$R_T^{\mathrm{swap}}=\max_{\phi}\sum_{t=1}^T\left[\ell_t(I_t)-\ell_t(\phi(I_t))\right]$$

由于每个源动作可独立选择替代动作：

$$R_T^{\mathrm{swap}}=\sum_i\max_jR_{i\rightarrow j}(T)$$

若平均 swap regret 消失，则所有条件替换规则都不能持续改进。

## 二十六、外部与 Swap Regret

常数映射：

$$\phi(i)=j,\qquad \forall i$$

是 swap 映射的特例，因此：

$$R_T^{\mathrm{swap}}\geq R_T^{\mathrm{ext}}$$

无 swap regret 蕴含无外部遗憾，反向一般不成立。

外部遗憾只问“始终改用哪个动作更好”，swap regret 还问“当我用了动作 $i$ 时，是否应该改成 $j$”。

## 二十七、Regret Matching

维护正的内部累积遗憾：

$$R_{i\rightarrow j}^+(t)=\max\{R_{i\rightarrow j}(t),0\}$$

当当前动作为 $i$ 时，可按：

$$P_{i\rightarrow j}\propto R_{i\rightarrow j}^+(t)$$

分配下一步转移动作，并把剩余概率留在 $i$。

Regret matching 可解释为逼近负正交象限，并产生 vanishing internal regret。

## 二十八、Swap Regret 的外部学习归约

可为每个源动作运行一个外部无遗憾子算法，输出替代动作分布。把这些分布组成转移矩阵：

$$Q_t(i,j)=q_t^i(j)$$

主算法选择其平稳分布：

$$p_t^{\mathsf T}Q_t=p_t^{\mathsf T}$$

适当向各子算法分配条件损失，可把外部遗憾界转化为 swap regret 界。

## 二十九、外部遗憾与 CCE

多玩家重复博弈中，若每个玩家外部遗憾消失，经验联合分布：

$$\widehat\sigma_T(a)=\frac1T\sum_{t=1}^T\mathbf 1\{a_t=a\}$$

趋近粗相关均衡集合。粗相关均衡只禁止玩家在看到推荐前统一改用某个固定动作。

这不保证动作序列或每个玩家的边际策略收敛。

## 三十、Swap Regret 与 CE

若每个玩家 swap 或 internal regret 消失，经验分布趋近相关均衡。相关均衡要求对所有动作替换映射 $\phi_i$：

$$\mathbb E_{a\sim\sigma}[u_i(a)]\geq\mathbb E_{a\sim\sigma}[u_i(\phi_i(a_i),a_{-i})]$$

该条件允许玩家根据收到的推荐动作决定是否偏离，因此比 CCE 更强。

## 三十一、Partial Monitoring 模型

环境结果集合为：

$$\mathcal J=\{1,\ldots,M\}$$

损失矩阵为：

$$L\in\mathbb R^{K\times M}$$

信号映射为：

$$H:\mathcal A\times\mathcal J\rightarrow\Sigma$$

第 $t$ 轮环境选择 $J_t$，玩家承担 $L(I_t,J_t)$，但只观察：

$$H(I_t,J_t)$$

## 三十二、Bandit 是 Partial Monitoring 特例

在 bandit feedback 中，信号就是所选动作损失：

$$H(i,j)=L(i,j)$$

因此玩家可观察 $L(I_t,J_t)$，并通过动作概率做重要性加权。

在一般 partial monitoring 中，不同结果可能产生相同信号，却对应不同损失。此时单纯的 inverse propensity weighting 无法恢复损失。

## 三十三、信号矩阵

对动作 $i$，把可能信号编号为 $\sigma_1,\ldots,\sigma_{m_i}$，定义信号矩阵：

$$[S_i]_{r,j}=\mathbf 1\{H(i,j)=\sigma_r\}$$

若结果分布为 $q\in\Delta_M$，则动作 $i$ 的信号分布为：

$$S_iq$$

Partial monitoring 的识别问题是：能否从各动作的信号分布恢复相关损失差。

## 三十四、Global Observability

记动作 $i$ 的损失行向量为 $L_i$。若对所有动作对 $i,j$：

$$L_i-L_j\in\operatorname{span}\left(S_1^{\mathsf T},\ldots,S_K^{\mathsf T}\right)$$

则称游戏 globally observable。

这表示任意动作损失差可以表示为所有动作信号统计的线性组合，因此通过探索所有动作能够估计比较所需信息。

## 三十五、Local Observability

每个动作在结果分布单纯形上有一个最优区域。相邻 Pareto-optimal 动作若其损失差能由局部邻域动作的信号恢复，则称 locally observable。

Local observability 比 global observability 更强，因为它要求无需广泛探索远离当前候选的动作，就能区分局部竞争者。

精确定义依赖 cell decomposition 和邻接结构。

## 三十六、Partial Monitoring 难度分类

有限非退化 partial monitoring 游戏的 minimax regret 典型分为：

1. trivial：零或常数级；
2. easy：$\widetilde\Theta(\sqrt T)$；
3. hard：$\Theta(T^{2/3})$，忽略对数项；
4. hopeless：$\Theta(T)$。

通常 locally observable 对应 easy，global 但非 local 对应 hard，非 global observable 对应 hopeless。

这是问题结构分类，不是任意算法自动达到的界。

## 三十七、为什么出现 T 的 2/3 次方

Hard partial monitoring 必须在“选择可能高损失的信息动作”和“利用当前最佳动作”之间权衡。若探索轮数约为 $m$：

$$R_T\approx m+\frac{T}{\sqrt m}$$

平衡两项：

$$m\asymp T^{2/3}$$

得到：

$$R_T\asymp T^{2/3}$$

该启发式反映辨识损失差需要额外信息成本。

## 三十八、Partial Monitoring 算法

典型方法包括：

- FeedExp3；
- AppleTree；
- CBP；
- PM-DMED；
- 信息比率和镜像下降方法；
- 基于全局或局部观察算子的损失估计。

算法必须使用 $L$ 与 $H$ 的结构构造观察向量。直接套用 EXP3，若信号不是所选损失，通常不会得到正确遗憾保证。

## 三十九、校准预测

设每轮预测：

$$p_t\in\Delta_m$$

随后观察类别：

$$Y_t\in\{1,\ldots,m\}$$

若预测值为 $q$ 的轮次中，实际类别频率接近 $q$，则预测是校准的。

校准关注概率频率一致性，不等同于对数损失、Brier 分数或分类准确率最优。

## 四十、有限网格校准误差

给定预测网格 $\mathcal G\subset\Delta_m$，定义：

$$N_T(q)=\sum_{t=1}^T\mathbf 1\{p_t=q\}$$

经验结果分布为：

$$\widehat q_T=\frac{1}{N_T(q)}\sum_{t:p_t=q}e_{Y_t}$$

校准误差可写为：

$$\operatorname{Cal}_T=\sum_{q\in\mathcal G}\frac{N_T(q)}{T}\|\widehat q_T-q\|_1$$

目标是 $\operatorname{Cal}_T\rightarrow0$。

## 四十一、校准作为 Approachability

对每个网格点 $q$ 定义偏差块：

$$g_q(p_t,Y_t)=\mathbf 1\{p_t=q\}(e_{Y_t}-q)$$

把所有块拼成向量 $g_t$。校准要求频繁使用的预测块平均偏差趋零。

通过对适当凸目标集应用 Blackwell approachability，可构造随机校准预测器。随机化很重要，因为确定性预测器可被对抗序列系统性破坏。

## 四十二、连续校准

精确预测值位于连续单纯形时，通常定义弱校准或核校准。对连续测试函数 $w$，要求：

$$\frac1T\sum_{t=1}^Tw(p_t)(e_{Y_t}-p_t)\rightarrow0$$

实践中可使用有限网格逼近、核特征或在线校准映射。

网格越细，离散化偏差越小，但维数和有限样本误差越大。

## 四十三、校准与内部遗憾

校准预测与内部无遗憾存在紧密归约。直观上，若在预测为 $q$ 的轮次中，结果频率确实接近 $q$，则对 $q$ 做最佳回应不会被另一个条件动作系统性击败。

反过来，可把每个预测桶的条件替换误差写成内部遗憾。由此可以从校准算法构造 correlated equilibrium 学习，也可用内部遗憾算法构造校准器。

具体归约取决于损失函数和预测离散化。

## 四十四、校准与 Proper Scoring Rule

Brier 分数为：

$$S(p,y)=\|p-e_y\|_2^2$$

对数损失为：

$$S(p,y)=-\log p_y$$

Proper scoring rule 激励报告真实条件概率，但低平均 proper loss 不自动保证对任意对抗序列的所有校准条件。

校准与 sharpness、resolution 和 scoring-rule regret 应分别报告。

## 四十五、部分反馈下的校准

若真实结果 $Y_t$ 不可见，只观察信号 $H(I_t,Y_t)$，校准能否实现取决于结果频率或所需函数能否从信号识别。

若两个结果分布对所有动作产生相同信号分布，却要求不同校准预测，则精确校准不可识别。此时只能校准可观察等价类、使用额外审计标签或报告部分识别集合。

## 四十六、5v5 游戏中的对抗 Bandit

可把宏观动作定义为：

- 开团；
- 撤退；
- 控制大型目标；
- 推进边线；
- 入侵野区；
- 防守高地；
- 交换资源。

每次只观察所执行动作的实际结果，未执行动作的反事实损失不可见。若日志保存选择概率，可用 EXP3 型估计做在线稳健选择。

## 四十七、游戏中的向量 Approachability

单轮向量可包含：

$$g_t=(\text{经济收益},\text{死亡风险},\text{目标控制},\text{资源消耗},\text{角色公平})$$

目标集合可以要求长期死亡风险不超过阈值、资源消耗受限，同时经济和目标控制达到最低水平。

与固定加权和相比，approachability 更直接地表达“所有约束同时满足”，但必须确认目标集合在对手最坏回应下可逼近。

## 四十八、游戏中的 Swap Regret

外部遗憾只判断“整段时间都改用撤退是否更好”。Swap regret 可以判断：

- 当系统选择开团时，是否应改成拉扯；
- 当系统选择控龙时，是否应改成逼塔；
- 当系统选择追击时，是否应改成撤退。

这适合发现条件化策略替换规则。多智能体都降低 swap regret 时，经验联合行为可接近相关均衡，但不保证形成单一确定战术。

## 四十九、战争迷雾与 Partial Monitoring

战争迷雾下，系统看到击杀、血量变化、视野提示和目标状态等信号，却看不到敌方完整位置、技能意图和所有反事实损失。这比普通 bandit 更接近 partial monitoring。

上线前应建立损失矩阵近似和信号映射，检查关键动作损失差是否 globally 或 locally observable。若不可观察，就不能声称 EXP3 能从现有日志恢复全部动作价值。

敌人到达概率、技能命中概率和目标刷新判断还应做在线校准，并按地图区域、版本和对局阶段分桶诊断。

## 五十、结论

Blackwell Approachability 用向量目标集合统一描述遗憾、公平、风险和资源约束；外部遗憾是逼近负正交象限的特例。EXP3 通过动作随机化和重要性加权，在只观察所选损失的对抗 bandit 中取得 $\widetilde O(\sqrt{KT})$ 遗憾。

Swap regret 比外部遗憾更强，它允许按实际动作做条件替换，并在重复博弈中对应相关均衡；外部遗憾只保证粗相关均衡。Partial monitoring 的反馈甚至不一定包含所选损失，能否学习取决于损失差对信号的可观察性，并产生 easy、hard 和 hopeless 等不同遗憾阶。

校准学习要求概率预测与长期经验频率一致，可通过 approachability 和内部遗憾归约构造。在 5v5 游戏中，应把可观察的执行损失交给 bandit 方法，把不可识别的战争迷雾反馈建成 partial monitoring，把多指标安全建成 approachability，并保存动作概率和反馈信号，才能进行可验证的在线学习。
