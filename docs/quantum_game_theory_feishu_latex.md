# 量子博弈：从量子策略、EWL 协议到非局域博弈与量子均衡

## 摘要

量子博弈把博弈论的玩家、策略、信息和收益嵌入量子力学框架。策略可以是局部幺正操作、量子信道或测量；共享资源可以是可分离态、纠缠态或经典—量子相关态；裁判通过 POVM 测量产生结果，并依据结果支付收益。量子博弈并不是简单地给经典混合策略换一种随机数发生器，而是允许叠加、相位、纠缠、测量扰动和上下文性改变可实现的相关分布。

本文介绍量子态、密度矩阵、CPTP 策略、测量与收益的一般模型，分析 Meyer 量子硬币、Eisert–Wilkens–Lewenstein（EWL）量子囚徒困境、CHSH 非局域博弈、量子 Bayesian 博弈、量子 Nash 与量子相关均衡，并讨论半正定规划、噪声、可实现性和实验估计。最后说明量子博弈在 5v5 游戏和多智能体建模中的合理用途与边界。

关键限制是：量子优势依赖协议、信息结构、允许策略集、共享纠缠、测量和噪声；它不自动意味着更高社会福利，也不意味着可以超光速通信，更不能把量子形式直接当成当前经典游戏服务器的性能提升方案。

## 一、经典有限博弈

经典有限博弈可写为：

$$G=(N,(A_i)_{i\in N},(u_i)_{i\in N})$$

玩家 $i$ 的纯策略为 $a_i\in A_i$，联合策略为：

$$a=(a_1,\ldots,a_n)$$

收益为：

$$u_i(a_1,\ldots,a_n)$$

经典混合策略是动作集合上的概率分布：

$$p_i\in\Delta(A_i)$$

独立混合策略下的期望收益为：

$$U_i(p_1,\ldots,p_n)=\sum_a u_i(a)\prod_jp_j(a_j)$$

## 二、量子博弈的三种含义

第一类是经典博弈的量子化：保留经典收益表，但允许玩家作用于量子态。第二类是非局域博弈：裁判向空间分离玩家发送问题，玩家使用共享纠缠生成答案。第三类是原生量子博弈：策略、信息或收益本身涉及量子态、量子信道、测量和量子系统控制。

这三类问题使用相似数学语言，但研究目的不同。对经典博弈的某一种量子化不是唯一的；初态、纠缠门、反纠缠门、测量基和策略集合都会改变结果。

## 三、纯态与 Hilbert 空间

量子系统状态位于复 Hilbert 空间 $\mathcal H$。纯态用单位向量表示：

$$|\psi\rangle\in\mathcal H$$

$$\langle\psi|\psi\rangle=1$$

单量子比特一般态为：

$$|\psi\rangle=\alpha|0\rangle+\beta|1\rangle$$

归一化要求：

$$|\alpha|^2+|\beta|^2=1$$

整体相位 $e^{i\phi}$ 不改变物理状态，但相对相位会影响干涉与最终测量概率。

## 四、复合系统与纠缠

两个玩家的联合空间为：

$$\mathcal H_{AB}=\mathcal H_A\otimes\mathcal H_B$$

乘积纯态可写为：

$$|\psi\rangle_{AB}=|\phi\rangle_A\otimes|\chi\rangle_B$$

Bell 态：

$$|\Phi^+\rangle=\frac{|00\rangle+|11\rangle}{\sqrt2}$$

不能分解为两个局部纯态的张量积，因此是纠缠态。纠缠允许经典共享随机性无法实现的相关性，但局部测量结果仍服从无信号约束。

## 五、密度矩阵

一般量子态由密度矩阵表示：

$$\rho\succeq0$$

$$\operatorname{Tr}(\rho)=1$$

纯态对应：

$$\rho=|\psi\rangle\langle\psi|$$

且满足：

$$\operatorname{Tr}(\rho^2)=1$$

混合态满足：

$$\operatorname{Tr}(\rho^2)\lt1$$

密度矩阵同时表示经典随机混合和量子相干，是量子博弈最通用的状态语言。

## 六、约化态与部分迹

联合态为 $\rho_{AB}$ 时，玩家 A 的局部状态为：

$$\rho_A=\operatorname{Tr}_B(\rho_{AB})$$

Bell 态的任一局部约化态为：

$$\rho_A=\rho_B=\frac{I}{2}$$

因此单个玩家局部看见完全混合态，但联合测量具有强相关性。不能从局部约化态单独恢复全部联合信息。

## 七、可分离态与纠缠态

双边混合态若能写成：

$$\rho_{AB}=\sum_kp_k\rho_A^k\otimes\rho_B^k$$

其中：

$$p_k\geq0,\qquad\sum_kp_k=1$$

则称其可分离。不能这样表示的状态为纠缠态。可分离态可由经典共享随机变量协调；纠缠态可能在非局域博弈中产生更高胜率。

## 八、幺正策略

封闭量子系统的可逆策略由幺正算子表示：

$$U^\dagger U=UU^\dagger=I$$

单量子比特的一般 $SU(2)$ 操作可参数化为：

$$U(\theta,\phi,\lambda)=\begin{pmatrix}\cos(\theta/2)&-e^{i\lambda}\sin(\theta/2)\\e^{i\phi}\sin(\theta/2)&e^{i(\phi+\lambda)}\cos(\theta/2)\end{pmatrix}$$

只允许某个低维子集与允许完整 $SU(2)$ 会得到不同均衡，因此策略空间必须作为协议的一部分明确给出。

## 九、一般量子信道策略

带噪声、测量、辅助系统或随机化的策略应使用完全正迹保持映射（CPTP map）：

$$\mathcal E(\rho)=\sum_kK_k\rho K_k^\dagger$$

Kraus 算子满足：

$$\sum_kK_k^\dagger K_k=I$$

局部玩家策略为 $\mathcal E_i$。若玩家不能通信，联合策略通常限制为局部操作：

$$\mathcal E=\mathcal E_1\otimes\cdots\otimes\mathcal E_n$$

允许通信、共享辅助态或序贯操作会扩展可实现策略集合。

## 十、测量与结果概率

一般测量由 POVM 元素 $\{M_o\}_o$ 表示：

$$M_o\succeq0$$

$$\sum_oM_o=I$$

在状态 $\rho$ 上观察到结果 $o$ 的概率为：

$$p(o)=\operatorname{Tr}(M_o\rho)$$

投影测量是 POVM 的特殊情况。测量基决定相位和纠缠如何转化为经典结果分布。

## 十一、一般量子博弈协议

一个静态量子博弈可以由初态 $\rho_0$、玩家信道 $\mathcal E_i$、裁判信道 $\mathcal R$、POVM $M_o$ 和收益 $u_i(o)$ 定义。终态为：

$$\rho_f=\mathcal R\circ(\mathcal E_1\otimes\cdots\otimes\mathcal E_n)(\rho_0)$$

玩家 $i$ 的期望收益为：

$$U_i(\mathcal E_1,\ldots,\mathcal E_n)=\sum_ou_i(o)\operatorname{Tr}(M_o\rho_f)$$

初态、操作顺序、通信限制和测量规则共同决定博弈，不能只给一个经典收益矩阵就声称量子化已唯一确定。

## 十二、经典博弈的嵌入

经典分布 $p(a)$ 可以表示为对角密度矩阵：

$$\rho_p=\sum_ap(a)|a\rangle\langle a|$$

经典随机策略对应只改变计算基概率且不利用相干的量子信道。若量子协议不能把所有经典纯策略和混合策略作为特例嵌入，则它比较的并不是原经典博弈的严格扩展。

合理的经典一致性要求是：当纠缠参数或相干资源关闭时，量子协议恢复经典收益分布。

## 十三、量子纯策略 Nash 均衡

若策略集合是允许的量子操作 $\mathcal S_i$，策略组合 $\mathcal E^*$ 是 Nash 均衡，当且仅当对所有玩家和单方偏离都有：

$$U_i(\mathcal E_i^*,\mathcal E_{-i}^*)\geq U_i(\mathcal E_i,\mathcal E_{-i}^*)$$

其中：

$$\mathcal E_i\in\mathcal S_i$$

均衡结论总是相对于指定策略集合。一个策略在两参数幺正集合中是均衡，并不保证在完整 CPTP 策略集合中仍是均衡。

## 十四、量子混合策略

玩家可以按经典概率选择不同量子操作：

$$\overline{\mathcal E}_i=\sum_kq_k\mathcal E_i^k$$

其中：

$$q_k\geq0,\qquad\sum_kq_k=1$$

CPTP 映射集合本身是凸集，因此这种随机混合仍是合法量子信道。在紧致凸策略集和连续收益等条件下，可使用经典不动点工具研究混合量子均衡存在性。

## 十五、Meyer 量子硬币博弈

经典硬币初态为 $|0\rangle$。经典玩家只能选择翻转或不翻转：

$$F=X=\begin{pmatrix}0&1\\1&0\end{pmatrix}$$

$$N=I$$

量子玩家先施加 Hadamard 门：

$$H=\frac{1}{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}$$

得到：

$$H|0\rangle=|+\rangle=\frac{|0\rangle+|1\rangle}{\sqrt2}$$

因为：

$$X|+\rangle=|+\rangle$$

无论经典玩家翻转还是不翻转，量子玩家最后再施加 $H$ 都恢复 $|0\rangle$。优势来自策略集合不对称，而不是量子玩家在相同资源条件下普遍战胜经典玩家。

## 十六、经典囚徒困境

经典动作是合作 $C$ 与背叛 $D$。收益通常满足：

$$T\gt R\gt P\gt S$$

并要求：

$$2R\gt T+S$$

典型收益为：

$$u(C,C)=(R,R)$$

$$u(C,D)=(S,T)$$

$$u(D,C)=(T,S)$$

$$u(D,D)=(P,P)$$

经典博弈中 $(D,D)$ 是 Nash 均衡，但双方收益低于 $(C,C)$。

## 十七、EWL 量子化协议

Eisert–Wilkens–Lewenstein 协议从 $|00\rangle$ 开始，先施加纠缠门：

$$J(\gamma)=\exp\left(i\frac{\gamma}{2}X\otimes X\right)$$

玩家分别施加局部策略 $U_A$ 和 $U_B$，随后裁判施加 $J^\dagger$：

$$|\psi_f\rangle=J^\dagger(U_A\otimes U_B)J|00\rangle$$

最终在计算基测量。结果 $00,01,10,11$ 分别映射到 $CC,CD,DC,DD$ 的经典收益。

纠缠参数范围通常取：

$$0\leq\gamma\leq\frac{\pi}{2}$$

## 十八、EWL 中的经典策略

可选经典合作策略为：

$$C=I$$

经典背叛策略可表示为：

$$D=iX$$

协议设计要求在限制到 $\{C,D\}$ 及其经典随机混合时，恢复经典囚徒困境概率与收益。

一种常见量子策略为：

$$Q=iZ$$

在最大纠缠和特定两参数策略集合中，$(Q,Q)$ 可以成为 Nash 均衡，并得到合作收益 $R$。

## 十九、EWL 结论的边界

EWL 的合作型结果依赖三项选择：纠缠门、末端反纠缠测量、允许的局部策略子集。若把策略扩展到完整 $SU(2)$ 或更一般 CPTP 映射，玩家可能出现新的最佳响应，原均衡可能消失、退化或变成混合均衡。

因此不能从：

$$U_i(Q,Q)=R$$

直接推出“量子力学解决了所有囚徒困境”。正确结论是：特定量子协议改变了可实现的策略与相关性，从而改变了该扩展博弈的均衡结构。

## 二十、纠缠参数与相变

收益可写为纠缠强度的函数：

$$U_i=U_i(\gamma,U_A,U_B)$$

随着 $\gamma$ 增大，最佳响应和均衡可能在某些阈值处变化：

$$\gamma_c=\inf\{\gamma:\text{equilibrium structure changes}\}$$

阈值取决于收益参数和策略集合。实际分析应画出最佳响应对应、均衡收益与稳定性，而不只比较最大纠缠和零纠缠两个端点。

## 二十一、非局域博弈

在双玩家非局域博弈中，裁判从分布 $\pi(x,y)$ 抽取问题 $x,y$，分别发送给 Alice 和 Bob。玩家不通信，输出 $a,b$，胜负由谓词 $V(a,b\mid x,y)$ 决定。

策略胜率为：

$$\omega=\sum_{x,y,a,b}\pi(x,y)V(a,b\mid x,y)p(a,b\mid x,y)$$

经典值为：

$$\omega_c=\sup_{\mathrm{classical}}\omega$$

量子值为：

$$\omega_q=\sup_{\mathrm{quantum}}\omega$$

## 二十二、量子非局域策略

玩家共享纠缠态 $\rho_{AB}$，并根据问题选择局部 POVM：

$$\{M_a^x\}_a,\qquad\{N_b^y\}_b$$

联合输出概率为：

$$p(a,b\mid x,y)=\operatorname{Tr}\left[(M_a^x\otimes N_b^y)\rho_{AB}\right]$$

无信号条件要求 Alice 的边际不依赖 Bob 的问题：

$$\sum_bp(a,b\mid x,y)=\sum_bp(a,b\mid x,y')$$

Bob 一侧同理。量子相关严格强于经典局部相关，但弱于全部无信号相关。

## 二十三、CHSH 博弈

CHSH 中问题与答案都是 bit，问题均匀分布。获胜条件为：

$$a\oplus b=x\land y$$

最佳经典策略胜率为：

$$\omega_c=\frac{3}{4}$$

共享 Bell 态并选择适当测量方向时，量子胜率为：

$$\omega_q=\cos^2\left(\frac{\pi}{8}\right)=\frac{2+\sqrt2}{4}$$

数值约为：

$$\omega_q\approx0.8536$$

该优势受 Tsirelson 界限制，仍低于一般无信号盒可达到的胜率 $1$。

## 二十四、Bell 不等式与博弈

令二元输出编码为 $A_x,B_y\in\{-1,1\}$。CHSH 表达式为：

$$S=\mathbb E[A_0B_0]+\mathbb E[A_0B_1]+\mathbb E[A_1B_0]-\mathbb E[A_1B_1]$$

经典局部策略满足：

$$|S|\leq2$$

量子策略满足 Tsirelson 界：

$$|S|\leq2\sqrt2$$

非局域博弈把 Bell 不等式的违反转化为具有明确收益的决策任务。

## 二十五、量子 Bayesian 博弈

Bayesian 博弈中，玩家类型 $t_i$ 是私人信息。量子版本可让玩家根据类型选择测量或信道。期望收益为：

$$U_i=\sum_{\boldsymbol t,\boldsymbol a}p(\boldsymbol t)u_i(\boldsymbol a,\boldsymbol t)p(\boldsymbol a\mid\boldsymbol t)$$

量子相关分布可写为：

$$p(\boldsymbol a\mid\boldsymbol t)=\operatorname{Tr}\left[\left(\bigotimes_iM_{a_i}^{t_i}\right)\rho\right]$$

若某些 Bayesian 博弈对应 Bell 场景，纠缠可以扩大可实现相关集合并提高均衡收益，但结果依赖先验和收益结构。

## 二十六、经典相关均衡

经典相关均衡由相关装置抽取动作建议 $a$。对每个玩家、建议动作和偏离动作，服从建议应满足：

$$\sum_{a_{-i}}\mu(a_i,a_{-i})\left[u_i(a_i,a_{-i})-u_i(a_i',a_{-i})\right]\geq0$$

共享经典随机性可以实现 $\mu$，但不能产生违反 Bell 不等式的相关分布。

## 二十七、量子相关均衡

量子相关装置向玩家分发共享态 $\rho$，玩家通过规定局部测量输出动作。若任何玩家单独替换自己的局部 CPTP 映射都不能提高收益，则该协议构成量子相关均衡。

形式上，对所有局部偏离 $\mathcal F_i$：

$$U_i(\mathcal E_i^*,\mathcal E_{-i}^*)\geq U_i(\mathcal F_i\circ\mathcal E_i^*,\mathcal E_{-i}^*)$$

量子相关均衡的定义取决于玩家能否保留辅助系统、进行一般测量、获得经典建议或与裁判交互。

## 二十八、零和量子博弈与 Minimax

在双玩家零和量子博弈中，可令玩家选择密度矩阵 $\rho$ 与 $\sigma$，收益为双线性形式：

$$U(\rho,\sigma)=\operatorname{Tr}[R(\rho\otimes\sigma)]$$

在有限维紧致凸策略集合和连续双线性收益下，有 minimax 关系：

$$\max_\rho\min_\sigma U(\rho,\sigma)=\min_\sigma\max_\rho U(\rho,\sigma)$$

若策略集合包含非凸秩约束、有限电路深度或离散门集，标准 minimax 条件可能不成立。

## 二十九、半正定规划

密度矩阵与 POVM 的正半定约束使许多量子策略优化具有 SDP 结构。标准形式为：

$$\max_X\operatorname{Tr}(CX)$$

约束为：

$$\operatorname{Tr}(A_kX)=b_k$$

$$X\succeq0$$

固定其他玩家测量时，单个玩家最佳响应常可写成 SDP。多玩家联合优化通常仍是非凸的，可使用交替优化获得下界，但不能保证全局最优。

## 三十、NPA 层级

非局域相关的量子集合难以直接刻画。Navascués–Pironio–Acín 层级通过测量算子矩矩阵构造一系列 SDP 外逼近：

$$\mathcal Q\subseteq\cdots\subseteq\mathcal Q_2\subseteq\mathcal Q_1$$

每一级给出量子值上界：

$$\omega_q\leq\omega_k$$

随着层级提高，上界通常收紧，但矩阵规模迅速增长。一个可实现量子策略提供下界，NPA 提供上界；两者接近时才能认证近似最优性。

## 三十一、动态量子博弈

多阶段量子博弈中，状态通过量子信道演化：

$$\rho_{t+1}=\mathcal T_t^{a_t^1,\ldots,a_t^n}(\rho_t)$$

若每阶段测量，测量会改变后续状态。策略需要依赖玩家可观察的经典历史和保留的量子记忆：

$$\pi_i:(h_t^{\mathrm{classical}},\rho_t^i)\mapsto\mathcal E_{i,t}$$

动态量子博弈与量子控制、量子 comb、过程矩阵和量子随机博弈相连，其均衡存在和计算通常比静态模型更困难。

## 三十二、退相干与噪声

退极化信道可写为：

$$\mathcal D_p(\rho)=(1-p)\rho+p\frac{I}{d}$$

相位阻尼会削弱非对角相干项。经过噪声后，收益变为：

$$U_i(p)=\sum_ou_i(o)\operatorname{Tr}[M_o\mathcal N_p(\rho_f)]$$

随着噪声增大，量子优势可能低于经典基线。应计算优势消失阈值：

$$p_c=\inf\{p:U_i^{\mathrm{quantum}}(p)\leq U_i^{\mathrm{classical}}\}$$

## 三十三、有限测量与统计误差

若收益观测 $Y_k$ 有界于 $[u_{\min},u_{\max}]$，用 $n$ 次 shots 估计：

$$\widehat U_i=\frac{1}{n}\sum_{k=1}^nY_k$$

Hoeffding 界给出：

$$\mathbb P(|\widehat U_i-U_i|\geq\varepsilon)\leq2\exp\left(-\frac{2n\varepsilon^2}{(u_{\max}-u_{\min})^2}\right)$$

验证 Nash 均衡还要同时估计多个偏离收益，因此需要多重比较校正或统一置信界。

## 三十四、量子策略梯度

参数化量子电路策略记为 $U(\theta)$，期望收益为：

$$J(\theta)=\langle\psi(\theta)|R|\psi(\theta)\rangle$$

对满足相应生成元条件的旋转门，参数移位规则可写为：

$$\frac{\partial J}{\partial\theta}=\frac{1}{2}\left[J\left(\theta+\frac{\pi}{2}\right)-J\left(\theta-\frac{\pi}{2}\right)\right]$$

多玩家可交替做梯度响应，但一般和博弈可能循环或发散；收敛到驻点也不等于收敛到 Nash 均衡。

## 三十五、量子优势的认证

声称量子优势至少需要明确经典比较集合 $\mathcal C$ 与量子集合 $\mathcal Q$。优势可写为：

$$\Delta=\sup_{q\in\mathcal Q}U(q)-\sup_{c\in\mathcal C}U(c)$$

还应扣除统计与实现误差：

$$\Delta_{\mathrm{cert}}=\Delta-\varepsilon_{\mathrm{stat}}-\varepsilon_{\mathrm{noise}}-\varepsilon_{\mathrm{model}}$$

若经典基线未充分优化、允许的信息不同或通信预算不同，则比较不公平。

## 三十六、量子启发式模型

即使没有量子硬件，也可使用复振幅、密度矩阵和非交换投影构造“量子概率”认知模型，用于表示上下文依赖、顺序效应和不相容观测。例如事件投影 $P_A$ 与 $P_B$ 可能不交换：

$$P_AP_B\neq P_BP_A$$

顺序概率因此不同：

$$\|P_BP_A|\psi\rangle\|^2\neq\|P_AP_B|\psi\rangle\|^2$$

这是经典计算机上的量子启发式概率模型，不等于实现了物理纠缠或量子计算加速。

## 三十七、5v5 游戏中的合理应用

量子博弈可以作为研究共享相关性和策略上下文的理论工具。例如，两名智能体不能实时通信但共享预先协调资源时，可比较经典共享随机策略与更一般相关策略的收益上界。

团队结果分布可写为：

$$p(a_1,\ldots,a_5\mid o_1,\ldots,o_5)$$

实际经典服务器应先使用相关均衡、共享潜变量、Dec-POMDP 或通信策略作为基线。只有当协议真的使用量子设备并满足空间分离、测量和无通信条件时，才应称为物理量子策略。

## 三十八、5v5 战术的量子启发式表示

可以把“进攻”和“撤退”作为二基态，把尚未决策的上下文状态表示为：

$$|\psi\rangle=\alpha|\mathrm{attack}\rangle+\beta|\mathrm{retreat}\rangle$$

不同信息到达顺序对应不同测量算子，从而表达观察顺序效应。团队耦合可用张量网络压缩高阶相关：

$$\Psi(a_1,\ldots,a_n)=\sum_{z_1,\ldots,z_{n-1}}T_1^{a_1z_1}T_2^{z_1a_2z_2}\cdots T_n^{z_{n-1}a_n}$$

这类模型可以在经典硬件上训练，但必须与普通概率图模型、注意力网络和相关策略做同预算对比。

## 三十九、何时量子化没有帮助

若最终可实现分布已经属于经典相关集合、纠缠被噪声完全破坏、测量成本超过收益、策略集合被限制到对角操作、经典通信本来就允许，或所谓优势仅来自给量子玩家更多动作，那么量子化没有可信优势。

对于可完全通信的中心化 5v5 控制器，经典联合策略已经能直接生成任意动作相关性，非局域量子优势通常没有相同任务意义。

## 四十、建模与验证流程

第一步写出经典博弈、信息结构和最佳经典基线。第二步明确 Hilbert 空间、初态、纠缠资源、玩家局部系统和通信约束。第三步指定允许的幺正或 CPTP 策略集合。第四步固定操作顺序、裁判信道、测量和收益映射。第五步检查关闭量子资源时能否恢复经典博弈。第六步求最佳响应和均衡。第七步加入噪声与有限 shots。第八步用 SDP 上下界或穷举小模型验证最优性。

经典恢复条件可写为：

$$\lim_{\gamma\to0}U_i^{\mathrm{quantum}}(\gamma,C,D)=U_i^{\mathrm{classical}}(C,D)$$

## 四十一、常见误区

第一，把叠加解释为玩家同时执行多个经典动作。测量最终只产生一个结果，干涉发生在振幅层。

第二，把纠缠解释为可传递信息。纠缠相关不允许超光速信号。

第三，只改变策略集合，却把收益改善归因于量子计算速度。

第四，在受限策略子集中找到均衡后，声称对所有量子操作稳定。

第五，比较优化充分的量子策略与未经优化的经典基线。

第六，忽略制备、门、读出和退相干噪声。

第七，把经典计算机上的复数概率模型称为真实量子部署。

第八，只报告最高收益，不报告均衡、单方偏离收益和统计置信区间。

## 四十二、结论

量子博弈用量子态、局部操作和测量扩展经典策略与相关结构。EWL 协议展示纠缠和相位如何改变特定囚徒困境扩展的均衡；CHSH 展示共享纠缠在无通信非局域任务中产生可认证优势；量子 Nash、量子相关均衡和 SDP 则提供更一般的分析语言。

严谨的量子博弈结论必须同时给出协议、经典嵌入、策略集合、信息限制、噪声模型和验证方法。量子资源可以改变某些博弈的可实现相关性，但不会自动消除利益冲突、社会困境、计算复杂性或工程成本。
