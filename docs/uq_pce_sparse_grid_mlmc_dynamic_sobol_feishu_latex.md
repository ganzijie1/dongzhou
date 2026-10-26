# 不确定性量化：Polynomial Chaos、Sparse Grid、Multilevel Monte Carlo 与 Sobol 动态扩展

## 摘要

不确定性量化（Uncertainty Quantification，UQ）研究输入不确定性如何传播到模型输出，以及哪些不确定因素主导输出波动。Polynomial Chaos Expansion（PCE）用正交多项式在随机空间中展开模型响应；Sparse Grid 用 Smolyak 组合替代高维张量网格；Multilevel Monte Carlo（MLMC）通过粗细模型差分和跨层耦合降低期望估计成本；Sobol 指数则把输出方差分解到输入和交互作用，并可扩展到时间轨迹、时间窗口、向量输出和随机过程输入。

四类方法解决的问题不同。PCE 是随机空间代理和谱表示；Sparse Grid 是插值与积分节点组织方法；MLMC 是多层采样估计器；Sobol 是全局敏感度指标。它们可以组合，但不能互相替代。例如 Sparse Grid 可以计算 PCE 系数，PCE 可以快速生成 Sobol 指数，MLMC 可以估计高保真动态统计量，但 MLMC 本身不是敏感度分解。

本文系统介绍不确定性分类、随机输入表示、PCE 基、截断、投影、回归、稀疏 PCE、相关输入、动态 PCE、Smolyak 构造、自适应稀疏网格、MLMC 望远镜恒等式、最优样本分配、复杂度定理、静态与动态 Sobol、路径空间敏感度、PCE–Sobol 连接，以及 5v5 游戏仿真中的版本参数、玩家行为和事件随机性分析。

## 一、不确定性的两类来源

Aleatoric uncertainty 表示系统固有随机性，例如命中、暴击、到达和测量噪声。Epistemic uncertainty 表示知识不足，例如参数估计误差、模型结构误差和数据覆盖不足。

可把输入写成：

$$\Xi=(\Xi^{\mathrm{aleatoric}},\Xi^{\mathrm{epistemic}})$$

二者应分别报告，因为增加数据可能降低 epistemic uncertainty，却不能消除真实随机性。

## 二、前向 UQ

给定随机输入：

$$\Xi\sim\rho(\xi)$$

模型输出为：

$$Y=\mathcal G(\Xi)$$

动态输出写为：

$$Y(t)=\mathcal G_t(\Xi),\qquad t\in[0,T]$$

前向 UQ 计算均值、方差、分位数、超越概率、置信带和敏感度。

## 三、逆向 UQ

若模型依赖未知参数 $\theta$，观测为 $D$，贝叶斯校准目标为：

$$p(\theta\mid D)\propto p(D\mid\theta)p(\theta)$$

得到后验后，再计算 posterior predictive：

$$p(Y_{\mathrm{new}}\mid D)=\int p(Y_{\mathrm{new}}\mid\theta)p(\theta\mid D)d\theta$$

PCE、Sparse Grid 和 MLMC 都可用于加速似然、证据或后验预测，但必须把校准不确定性继续传播到最终输出。

## 四、模型输出统计量

均值和方差为：

$$\mu_Y=\mathbb E[Y]$$

$$\sigma_Y^2=\mathbb E[(Y-\mu_Y)^2]$$

失效概率为：

$$p_f=\mathbb P(Y\in\mathcal F)$$

风险量还可包括分位数、VaR 和 CVaR。不同统计量对代理误差的敏感性不同：均值准确不代表尾部概率准确。

## 五、随机输入标准化

将原始输入 $X$ 映射到标准随机变量 $\Xi$：

$$X=T(\Xi)$$

例如高斯输入可标准化为：

$$X=\mu+\sigma\Xi,\qquad \Xi\sim\mathcal N(0,1)$$

均匀输入可映射到 $[-1,1]$。标准化有利于选择匹配分布的正交多项式并改善数值条件。

## 六、Polynomial Chaos Expansion

若：

$$Y\in L^2(\rho)$$

则可在正交多项式基上展开：

$$Y(\Xi)=\sum_{\alpha\in\mathbb N^d}c_{\alpha}\Psi_{\alpha}(\Xi)$$

其中 $\alpha$ 是多重指标，$\Psi_{\alpha}$ 是与输入分布匹配的多元正交多项式。

实际计算必须截断为有限项。

## 七、正交基

若基已归一化：

$$\mathbb E[\Psi_{\alpha}(\Xi)\Psi_{\beta}(\Xi)]=\delta_{\alpha\beta}$$

常见对应关系为：

| 输入分布 | 常用正交多项式 |
| --- | --- |
| Gaussian | Hermite |
| Uniform | Legendre |
| Gamma | Laguerre |
| Beta | Jacobi |

“分布匹配”提高谱逼近效率，但不是说不匹配的多项式完全不能使用。

## 八、多元张量基

若输入独立：

$$\rho(\xi)=\prod_{i=1}^d\rho_i(\xi_i)$$

可构造：

$$\Psi_{\alpha}(\xi)=\prod_{i=1}^d\psi_{\alpha_i}^{(i)}(\xi_i)$$

并保持正交性：

$$\mathbb E[\Psi_{\alpha}\Psi_{\beta}]=\prod_i\delta_{\alpha_i\beta_i}$$

输入相关时，简单张量正交结构通常失效。

## 九、总次数截断

总次数集合为：

$$\mathcal A_p=\{\alpha\in\mathbb N^d:|\alpha|_1\leq p\}$$

项数为：

$$P=\binom{d+p}{p}$$

截断 PCE 为：

$$Y_p(\Xi)=\sum_{\alpha\in\mathcal A_p}c_{\alpha}\Psi_{\alpha}(\Xi)$$

$P$ 随维数和次数组合增长，是 PCE 的主要维数瓶颈。

## 十、超曲面与各向异性截断

Hyperbolic truncation 可定义为：

$$\mathcal A_{p,q}=\left\{\alpha:\left(\sum_i\alpha_i^q\right)^{1/q}\leq p\right\},\qquad 0\lt q\leq1$$

$q\lt1$ 会抑制高阶交互项。各向异性截断可使用权重：

$$\sum_iw_i\alpha_i\leq p$$

对不重要变量设置更大 $w_i$，减少相关高次项。

## 十一、PCE 系数投影

正交基下：

$$c_{\alpha}=\mathbb E[Y\Psi_{\alpha}]$$

若基未归一化：

$$c_{\alpha}=\frac{\mathbb E[Y\Psi_{\alpha}]}{\mathbb E[\Psi_{\alpha}^2]}$$

积分可用 Monte Carlo、张量求积或 Sparse Grid。投影法要求积分规则能解析模型响应与基函数的乘积。

## 十二、均值与方差

正交归一基中，常数项为：

$$\mathbb E[Y_p]=c_{\mathbf0}$$

方差为：

$$\operatorname{Var}(Y_p)=\sum_{\alpha\neq\mathbf0}c_{\alpha}^2$$

因此 PCE 一旦建立，低阶矩和 Sobol 指数几乎不再需要额外模型调用。

## 十三、Intrusive Galerkin

若原模型写成：

$$\mathcal R(u,\Xi)=0$$

将：

$$u(\Xi)=\sum_{\alpha}u_{\alpha}\Psi_{\alpha}(\Xi)$$

代入并要求残差对每个基正交：

$$\mathbb E[\mathcal R(u,\Xi)\Psi_{\beta}]=0$$

得到耦合的确定性方程组。Intrusive 方法高效但需要修改求解器，并可能产生大规模耦合系统。

## 十四、Non-Intrusive PCE

Non-intrusive 方法把原模型视为黑箱，仅在样本点运行：

$$y^{(n)}=\mathcal G(\xi^{(n)})$$

再通过投影、回归或压缩感知求系数。它不改原求解器，适合现有仿真系统。

代价是需要合理实验设计，并独立验证代理在目标分布和尾部区域的精度。

## 十五、最小二乘 PCE

设计矩阵为：

$$\Phi_{n,\alpha}=\Psi_{\alpha}(\xi^{(n)})$$

普通最小二乘求解：

$$\widehat c=\operatorname*{arg\,min}_c\|\Phi c-y\|_2^2$$

稳定性取决于样本数、节点分布和矩阵条件数。样本数只略大于基数时，可能严重过拟合。

应使用独立验证集、交叉验证或 leave-one-out 误差。

## 十六、Sparse PCE

若只有少数系数显著，可使用：

$$\widehat c=\operatorname*{arg\,min}_c\frac12\|\Phi c-y\|_2^2+\lambda\|c\|_1$$

也可使用 LARS、OMP、basis pursuit 或 reweighted $\ell_1$。稀疏 PCE 的有效性依赖系数可压缩性和设计矩阵的可恢复性。

稀疏正则不会自动修复错误的输入分布、截断集合或模型不连续。

## 十七、谱收敛与失效情形

当响应对随机输入足够光滑或解析时，PCE 误差可能随次数快速下降：

$$\|Y-Y_p\|_{L^2(\rho)}\leq Ce^{-ap}$$

若响应存在跳跃、分岔、接触、模式切换或稀有失效边界，系数衰减变慢并可能出现 Gibbs 现象。

可使用 multi-element PCE、局部分区、适应基或混合代理。

## 十八、相关输入

经典 Sobol 分解和张量 PCE 通常要求输入独立。相关输入可通过 Rosenblatt 或 Nataf 变换映射到独立变量：

$$X=T(\Xi)$$

也可直接对联合分布做 Gram–Schmidt 正交化或使用 arbitrary PCE。

变换会改变“某个物理输入的敏感度”解释，不能把独立潜变量指数直接无条件当作原变量指数。

## 十九、动态 PCE

对时间响应：

$$Y(t,\Xi)=\sum_{\alpha}c_{\alpha}(t)\Psi_{\alpha}(\Xi)$$

均值轨迹为：

$$\mu_Y(t)=c_{\mathbf0}(t)$$

方差轨迹为：

$$\sigma_Y^2(t)=\sum_{\alpha\neq\mathbf0}c_{\alpha}(t)^2$$

系数函数可由每个时间点回归，也可通过 intrusive Galerkin 得到系数 ODE。

## 二十、长时间动态 PCE

非线性动力系统中，相位误差、混沌和分布形变会使固定全局基在长时间失效。常用方法包括：

- 时间窗口 PCE；
- restart PCE；
- flow-map PCE；
- 动态正交分解；
- multi-element PCE；
- 局部重新标准化随机变量。

短时间谱收敛不能自动保证长期轨迹代理可靠。

## 二十一、张量求积

若每个维度使用 $m$ 个节点，$d$ 维张量节点数为：

$$N_{\mathrm{tensor}}=m^d$$

即使一维规则高效，张量积仍遭受维数灾难。Sparse Grid 通过组合不同维度的低阶规则，删去大量高阶张量节点。

## 二十二、一维层级规则

令 $U_i$ 为第 $i$ 层一维插值或求积算子，并定义增量：

$$\Delta_i=U_i-U_{i-1},\qquad U_0=0$$

若节点嵌套：

$$\mathcal X_{i-1}\subseteq\mathcal X_i$$

新增层只需计算新节点。Clenshaw–Curtis 和某些 Gauss–Patterson 规则具有嵌套性。

## 二十三、Smolyak Sparse Grid

对 $d$ 维和总层级 $q$，Smolyak 算子可写为：

$$\mathcal A(q,d)=\sum_{|\mathbf i|_1\leq q+d-1}\Delta_{i_1}\otimes\cdots\otimes\Delta_{i_d}$$

其中 $i_k\geq1$。它保留低总层级张量增量，避免完整高阶张量积。

节点数通常远小于 $m^d$，但仍会随有效维数增长。

## 二十四、Sparse Grid 求积

稀疏网格求积写成：

$$\mathbb E[f(\Xi)]\approx\sum_{n=1}^Nw_nf(\xi^{(n)})$$

因此 PCE 系数可近似为：

$$c_{\alpha}\approx\sum_{n=1}^Nw_nY(\xi^{(n)})\Psi_{\alpha}(\xi^{(n)})$$

Smolyak 组合权重可能为负；这不妨碍高阶积分精度，但不应把所有权重解释为概率。

## 二十五、分层剩余

Sparse Grid 插值的层级剩余可写为：

$$\Delta_{\mathbf i}f=(\Delta_{i_1}\otimes\cdots\otimes\Delta_{i_d})f$$

若其范数或对目标积分的贡献较大，就继续细化相邻多重指标；若很小，则停止该方向。

分层剩余同时提供适应性指标和误差代理，但不是所有非光滑问题的严格误差上界。

## 二十六、各向异性 Sparse Grid

若不同输入重要性不同，可限制：

$$\sum_{k=1}^d\omega_ki_k\leq q$$

重要维度使用较小 $\omega_k$，获得更多节点；不重要维度使用较大权重。

权重可由先验、导数敏感度、低阶 PCE 或自适应剩余学习。错误各向异性可能漏掉弱主效应但强交互的变量。

## 二十七、Sparse Grid 的局限

Sparse Grid 适合中等维度和较光滑响应。以下情况会削弱优势：

- 维数很高且各维同等重要；
- 输出有跳跃或窄失效边界；
- 有效维数随区域变化；
- 单次模型成本极不均匀；
- 节点无法并行或复用。

高维时可结合稀疏 PCE、active subspace、低秩张量或 MLMC。

## 二十八、Monte Carlo 基线

普通 Monte Carlo 估计：

$$\widehat\mu_N=\frac1N\sum_{n=1}^NY^{(n)}$$

方差为：

$$\operatorname{Var}(\widehat\mu_N)=\frac{\operatorname{Var}(Y)}{N}$$

均方根误差按 $N^{-1/2}$ 下降，与维数无关，但不利用模型层级和光滑性。

## 二十九、多层模型

设 $P_{\ell}$ 是第 $\ell$ 层近似，层级越高越精确也越昂贵。可能的层级包括：

- 时间步长；
- 空间网格；
- 仿真保真度；
- AI 推理精度；
- 战斗模型复杂度；
- 样本或粒子数量。

目标是估计高层期望：

$$\mathbb E[P_L]$$

## 三十、MLMC 望远镜恒等式

利用：

$$\mathbb E[P_L]=\mathbb E[P_0]+\sum_{\ell=1}^L\mathbb E[P_{\ell}-P_{\ell-1}]$$

定义：

$$Y_0=P_0,\qquad Y_{\ell}=P_{\ell}-P_{\ell-1}$$

MLMC 估计量为：

$$\widehat P_{\mathrm{ML}}=\sum_{\ell=0}^L\frac1{N_{\ell}}\sum_{n=1}^{N_{\ell}}Y_{\ell}^{(n)}$$

## 三十一、跨层耦合

$P_{\ell}^{(n)}$ 与 $P_{\ell-1}^{(n)}$ 必须使用相同底层随机输入或尽可能强的 coupling：

$$Y_{\ell}^{(n)}=P_{\ell}^{(n)}-P_{\ell-1}^{(n)}$$

如果粗细层独立采样：

$$\operatorname{Var}(P_{\ell}-P_{\ell-1})$$

通常不会随层级快速下降，MLMC 优势会消失。

离散事件模型还需耦合事件时间、随机数和路径分支。

## 三十二、MLMC 方差

令：

$$V_{\ell}=\operatorname{Var}(Y_{\ell})$$

各层样本独立时：

$$\operatorname{Var}(\widehat P_{\mathrm{ML}})=\sum_{\ell=0}^L\frac{V_{\ell}}{N_{\ell}}$$

粗层方差大但成本低，可使用大量样本；细层差分方差小但成本高，只需少量样本。

## 三十三、最优样本分配

令单个层差分样本成本为 $C_{\ell}$。给定目标方差 $\varepsilon^2/2$，最优样本数满足：

$$N_{\ell}\propto\sqrt{\frac{V_{\ell}}{C_{\ell}}}$$

更具体地：

$$N_{\ell}\approx\frac{2}{\varepsilon^2}\sqrt{\frac{V_{\ell}}{C_{\ell}}}\sum_{k=0}^L\sqrt{V_kC_k}$$

实际算法先用 pilot samples 估计 $V_{\ell}$ 和 $C_{\ell}$，再自适应分配。

## 三十四、偏差控制

MLMC 仍估计的是 $\mathbb E[P_L]$，与真实目标 $\mathbb E[P]$ 存在离散偏差：

$$|\mathbb E[P-P_L]|\leq c_12^{-\alpha L}$$

通常选择 $L$ 使：

$$|\mathbb E[P-P_L]|\leq\frac{\varepsilon}{\sqrt2}$$

再把采样方差控制在 $\varepsilon^2/2$，使均方误差不超过 $\varepsilon^2$。

## 三十五、MLMC 复杂度

假设：

$$|\mathbb E[P-P_{\ell}]|=O(2^{-\alpha\ell})$$

$$V_{\ell}=O(2^{-\beta\ell})$$

$$C_{\ell}=O(2^{\gamma\ell})$$

则达到 RMSE $\varepsilon$ 的总成本典型为：

$$\operatorname{Cost}=\begin{cases}O(\varepsilon^{-2}),&\beta\gt\gamma\\O(\varepsilon^{-2}\log^2(\varepsilon^{-1})),&\beta=\gamma\\O(\varepsilon^{-2-(\gamma-\beta)/\alpha}),&\beta\lt\gamma\end{cases}$$

严格常数和对数写法依层级参数化而异。

## 三十六、MLMC 变体

常见扩展包括：

- antithetic MLMC；
- multi-index Monte Carlo；
- randomized quasi-Monte Carlo MLMC；
- unbiased MLMC；
- continuation MLMC；
- multifidelity control variates。

变体的核心仍是用强相关低成本模型减少高成本估计的方差。

## 三十七、Sobol 方差分解

对独立输入：

$$Y=f(X_1,\ldots,X_d)$$

ANOVA 分解为：

$$f=f_0+\sum_if_i+\sum_{i\lt j}f_{ij}+\cdots+f_{1\cdots d}$$

各项正交，因此：

$$\operatorname{Var}(Y)=\sum_{\varnothing\neq u\subseteq\{1,\ldots,d\}}V_u$$

其中：

$$V_u=\operatorname{Var}(f_u(X_u))$$

## 三十八、一阶与总效应 Sobol

一阶指数为：

$$S_i=\frac{\operatorname{Var}(\mathbb E[Y\mid X_i])}{\operatorname{Var}(Y)}$$

总效应指数为：

$$S_i^{\mathrm T}=1-\frac{\operatorname{Var}(\mathbb E[Y\mid X_{-i}])}{\operatorname{Var}(Y)}$$

$S_i$ 只包含主效应，$S_i^{\mathrm T}$ 包含所有涉及 $X_i$ 的交互。

两者之差衡量输入参与交互的程度。

## 三十九、Pick–Freeze 估计

生成独立样本矩阵 $A$ 与 $B$，构造 $A_B^{(i)}$：除第 $i$ 列来自 $B$ 外，其余列来自 $A$。

通过：

$$f(A),\qquad f(B),\qquad f(A_B^{(i)})$$

的交叉乘积可估计一阶和总效应指数。

不同 Saltelli、Jansen 和 Martinez 估计器具有不同有限样本偏差与方差，应报告具体公式而不是只写“Monte Carlo Sobol”。

## 四十、PCE 直接计算 Sobol

定义多重指标支撑：

$$\operatorname{supp}(\alpha)=\{i:\alpha_i\gt0\}$$

对应子集 $u$ 的部分方差为：

$$V_u=\sum_{\operatorname{supp}(\alpha)=u}c_{\alpha}^2$$

因此：

$$S_i=\frac{\sum_{\operatorname{supp}(\alpha)=\{i\}}c_{\alpha}^2}{\sum_{\alpha\neq0}c_{\alpha}^2}$$

$$S_i^{\mathrm T}=\frac{\sum_{\alpha:\alpha_i\gt0}c_{\alpha}^2}{\sum_{\alpha\neq0}c_{\alpha}^2}$$

## 四十一、点时刻动态 Sobol

对动态输出 $Y(t)$：

$$S_i(t)=\frac{\operatorname{Var}(\mathbb E[Y(t)\mid X_i])}{\operatorname{Var}(Y(t))}$$

$$S_i^{\mathrm T}(t)=1-\frac{\operatorname{Var}(\mathbb E[Y(t)\mid X_{-i}])}{\operatorname{Var}(Y(t))}$$

它们描述每个时刻的敏感度。若 $\operatorname{Var}(Y(t))$ 接近零，点时刻指数会数值不稳定。

## 四十二、PCE 的动态 Sobol

若：

$$Y(t,\Xi)=\sum_{\alpha}c_{\alpha}(t)\Psi_{\alpha}(\Xi)$$

则：

$$S_i(t)=\frac{\sum_{\operatorname{supp}(\alpha)=\{i\}}c_{\alpha}(t)^2}{\sum_{\alpha\neq0}c_{\alpha}(t)^2}$$

$$S_i^{\mathrm T}(t)=\frac{\sum_{\alpha:\alpha_i\gt0}c_{\alpha}(t)^2}{\sum_{\alpha\neq0}c_{\alpha}(t)^2}$$

一次动态 PCE 即可生成整条敏感度曲线。

## 四十三、积分型动态 Sobol

点时刻指数的简单时间平均并不等于轨迹总体敏感度。给定权重 $w(t)\geq0$，定义：

$$S_i^{[0,T]}=\frac{\int_0^Tw(t)\operatorname{Var}(\mathbb E[Y(t)\mid X_i])dt}{\int_0^Tw(t)\operatorname{Var}(Y(t))dt}$$

总效应为：

$$S_i^{\mathrm T,[0,T]}=\frac{\int_0^Tw(t)\mathbb E[\operatorname{Var}(Y(t)\mid X_{-i})]dt}{\int_0^Tw(t)\operatorname{Var}(Y(t))dt}$$

这种定义按每个时刻的实际输出方差加权。

## 四十四、窗口与时滞敏感度

局部时间窗口 $[a,b]$ 的指数为：

$$S_i^{[a,b]}=\frac{\int_a^bw(t)V_i(t)dt}{\int_a^bw(t)V(t)dt}$$

滚动窗口可观察某个参数何时开始主导。还可研究输入在时刻 $s$ 对输出时刻 $t$ 的影响：

$$S_i(s\rightarrow t)$$

时滞指数需要明确输入是静态参数、控制历史还是随机过程，不能只复用静态条件期望。

## 四十五、向量与场输出

若输出为向量 $Y(t)\in\mathbb R^m$，可使用协方差迹：

$$S_i^{\mathrm{trace}}(t)=\frac{\operatorname{tr}\{\operatorname{Cov}(\mathbb E[Y(t)\mid X_i])\}}{\operatorname{tr}\{\operatorname{Cov}(Y(t))\}}$$

也可先做 PCA 或 Karhunen–Loève 展开，对主要模态计算 Sobol。

不同分量量纲不同时，应先标准化或指定物理权重。

## 四十六、随机过程输入

时间随机输入可做 Karhunen–Loève 展开：

$$X(t,\omega)=\mu(t)+\sum_{k=1}^{\infty}\sqrt{\lambda_k}\phi_k(t)\xi_k(\omega)$$

截断后，把 $\xi_k$ 作为 PCE 或 Sobol 输入。物理过程的敏感度应把其所有 KL 模态作为一组：

$$S_X^{\mathrm T}=S_{\{\xi_1,\ldots,\xi_r\}}^{\mathrm T}$$

否则单个模态指数难以解释为原始过程的重要性。

## 四十七、相关输入与 Shapley Effects

输入相关时，经典 ANOVA 正交分解不唯一，主效应与相关性贡献纠缠。令 $\mathcal D=\{1,\ldots,d\}$，可使用 Shapley effect：

$$\operatorname{Sh}_i=\sum_{u\subseteq\mathcal D\setminus\{i\}}\frac{|u|!(d-|u|-1)!}{d!}\left[v(u\cup\{i\})-v(u)\right]$$

其中 $v(u)$ 是基于条件方差的联盟价值。

Shapley effects 在变量间公平分配解释方差，但计算成本通常高于独立输入 Sobol。

## 四十八、代理模型验证

UQ 结果必须附带代理误差。建议检查：

1. 独立测试误差；
2. 均值和方差误差；
3. 分位数与失效概率误差；
4. PCE 系数衰减；
5. Sparse Grid 分层剩余；
6. MLMC 层差偏差和方差率；
7. Sobol 置信区间和排序稳定性；
8. 输入分布与相关结构敏感性。

若代理误差与目标不确定性同量级，敏感度排名没有可信解释。

## 四十九、5v5 游戏中的 UQ

可把不确定输入分为：

- 版本参数：英雄数值、装备收益、目标奖励；
- 玩家参数：反应时间、命中率、风险偏好；
- 战术参数：支援延迟、视野覆盖、资源分配；
- 随机事件：暴击、技能命中、敌方路径；
- 模型误差：行为模型和伤害代理偏差。

动态输出可取：

$$Y(t)=(\text{经济差},\text{存活概率},\text{地图控制},\text{团战胜率})$$

PCE 和 Sparse Grid 适合中低维平滑参数扫描；MLMC 可把简化战斗模型、低帧率仿真和完整引擎组成多层；动态 Sobol 可判断不同时段由装备、操作、视野还是支援延迟主导。

## 五十、结论

Polynomial Chaos 用正交多项式压缩随机响应，适合平滑、中低有效维问题；Sparse Grid 用 Smolyak 结构减少非侵入投影和插值节点；MLMC 通过强耦合的粗细层差分，把大量预算放在廉价层；Sobol 指数则把输出方差分配给输入主效应和交互作用。

动态 UQ 不能只在若干时刻重复静态分析。应区分点时刻指数、方差加权的时间积分指数、滚动窗口指数、向量输出指数和随机过程组指数。输入相关时，应改用相关敏感度或 Shapley effects。

在 5v5 游戏仿真中，建议先建立输入分布与层级模型，再用低阶 PCE 或 Sparse Grid 做结构探索，用 MLMC 估计高保真动态统计量，最后用动态 Sobol 定位不同比赛阶段的主导不确定因素。所有敏感度结论都应同时报告代理误差、采样误差和输入分布假设。
