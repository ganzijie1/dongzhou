# 多项式优化、SOS 与矩松弛：从非负证书到全局优化层级

## 摘要

多项式优化研究以多项式为目标和约束的全局优化问题。它能够表达二次规划、0–1 优化、几何约束、鲁棒控制、参数辨识、博弈均衡条件和经过多项式近似的非线性规划，但一般是 NP-hard。困难不在于求一个局部驻点，而在于证明没有更好的可行点。

Sum of Squares（SOS，平方和）方法把“某个多项式在可行集上非负”替换为可由半正定矩阵验证的代数证书。Moment Relaxation（矩松弛）从对偶角度把点优化提升为概率测度优化，并以矩矩阵和局部化矩阵的半正定性刻画候选矩序列。二者构成 Lasserre 层级：松弛阶数增加时，下界单调提高；在 Archimedean 等条件下渐近收敛到全局最优值；满足 flat extension 时还可提取有限个全局最优解。

本文系统介绍多重指标、多项式非负性、SOS Gram 矩阵、半正定规划、Positivstellensatz、Putinar 证书、矩与局部化矩阵、原始–对偶层级、收敛、强对偶、解提取、稀疏与对称化、DSOS/SDSOS、SONC、数值缩放，以及在 5v5 游戏模型中的安全证书、策略代理和组合优化应用。

## 一、标准多项式优化问题

考虑：

$$p^{\star}=\inf_{x\in\mathbb R^n}f(x)$$

约束为：

$$g_i(x)\geq0,\qquad i=1,\ldots,m$$

$$h_j(x)=0,\qquad j=1,\ldots,\ell$$

其中 $f,g_i,h_j$ 都是实系数多项式。可行集为基本半代数集合：

$$K=\{x\in\mathbb R^n:g_i(x)\geq0,\ h_j(x)=0\}$$

## 二、多重指标

对多重指标：

$$\alpha=(\alpha_1,\ldots,\alpha_n)\in\mathbb N^n$$

定义：

$$|\alpha|=\sum_{i=1}^n\alpha_i,\qquad x^{\alpha}=\prod_{i=1}^nx_i^{\alpha_i}$$

任意次数不超过 $d$ 的多项式可写为：

$$p(x)=\sum_{|\alpha|\leq d}p_{\alpha}x^{\alpha}$$

次数不超过 $d$ 的单项式数量为：

$$s(n,d)=\binom{n+d}{d}$$

## 三、为什么全局优化困难

即使目标只有四次且没有复杂约束，也可能存在大量局部极小点。0–1 约束可写成：

$$x_i^2-x_i=0$$

因此许多组合优化问题都可嵌入多项式优化。一般多项式全局优化是 NP-hard，不能期望存在对所有实例都高效且精确的有限算法。

SOS 层级的价值是提供可计算下界、可验证证书和逐阶收敛，而不是消除最坏情形复杂度。

## 四、全局下界作为非负性

一个数 $\gamma$ 是无约束问题的合法下界，当且仅当：

$$f(x)-\gamma\geq0,\qquad \forall x\in\mathbb R^n$$

因此：

$$p^{\star}=\sup\{\gamma:f-\gamma\text{ 在 }\mathbb R^n\text{ 上非负}\}$$

约束情形则要求：

$$f(x)-\gamma\geq0,\qquad \forall x\in K$$

全局优化由此转化为寻找可计算的非负性证书。

## 五、SOS 多项式

若存在多项式 $q_1,\ldots,q_r$，使：

$$p(x)=\sum_{k=1}^rq_k(x)^2$$

则称 $p$ 为 SOS，多项式集合记为：

$$\Sigma[x]$$

显然：

$$p\in\Sigma[x]\quad\Longrightarrow\quad p(x)\geq0$$

SOS 是非负性的充分条件，但在一般维数和次数下不是必要条件。

## 六、非负但非 SOS

Motzkin 多项式为：

$$M(x,y)=x^4y^2+x^2y^4+1-3x^2y^2$$

由算术–几何平均不等式：

$$x^4y^2+x^2y^4+1\geq3x^2y^2$$

所以 $M(x,y)\geq0$，但它不是 SOS。

因此用 SOS 替代全局非负会产生保守性；提高层级或使用约束集合上的乘子可以减少这种保守性。

## 七、单项式向量

令 $v_d(x)$ 收集所有次数不超过 $d$ 的单项式：

$$v_d(x)=(x^{\alpha})_{|\alpha|\leq d}$$

其维数为：

$$\dim v_d=s(n,d)=\binom{n+d}{d}$$

若 $\deg p\leq2d$，则 SOS 表示可写为 Gram 形式：

$$p(x)=v_d(x)^{\mathsf T}Qv_d(x)$$

## 八、Gram 矩阵判据

多项式 $p$ 是 SOS，当且仅当存在半正定矩阵：

$$Q\succeq0$$

使：

$$p(x)=v_d(x)^{\mathsf T}Qv_d(x)$$

若：

$$Q=R^{\mathsf T}R$$

则：

$$p(x)=\|Rv_d(x)\|_2^2$$

Gram 矩阵一般不唯一，因为不同矩阵可能产生相同的多项式系数。

## 九、系数匹配

展开 Gram 表达式：

$$v_d(x)^{\mathsf T}Qv_d(x)=\sum_{\alpha}\left(\sum_{\beta+\gamma=\alpha}Q_{\beta,\gamma}\right)x^{\alpha}$$

与：

$$p(x)=\sum_{\alpha}p_{\alpha}x^{\alpha}$$

逐项匹配得到关于 $Q$ 的线性方程：

$$\sum_{\beta+\gamma=\alpha}Q_{\beta,\gamma}=p_{\alpha}$$

因此 SOS 检验是线性等式加半正定约束，即半正定规划。

## 十、无约束 SOS 下界

次数选择满足 $2d\geq\deg f$。SOS 下界问题为：

$$p_d^{\mathrm{SOS}}=\sup_{\gamma,Q}\ \gamma$$

约束为：

$$f(x)-\gamma=v_d(x)^{\mathsf T}Qv_d(x)$$

$$Q\succeq0$$

若最优得到 $\gamma$，则 $f(x)\geq\gamma$ 对所有 $x$ 成立。

## 十一、二次优化与 Shor 松弛

二次多项式可写成：

$$f(x)=x^{\mathsf T}Ax+2b^{\mathsf T}x+c$$

提升矩阵：

$$X=\begin{bmatrix}1\\x\end{bmatrix}\begin{bmatrix}1\\x\end{bmatrix}^{\mathsf T}$$

满足：

$$X\succeq0,\qquad \operatorname{rank}(X)=1$$

删除秩一约束得到 Shor SDP 松弛。它正是低阶矩/SOS 松弛的一个特例。

## 十二、约束集合上的证书

在：

$$K=\{x:g_i(x)\geq0,\ h_j(x)=0\}$$

上证明 $p\geq0$，可寻找：

$$p=\sigma_0+\sum_{i=1}^m\sigma_i g_i+\sum_{j=1}^{\ell}\tau_j h_j$$

其中：

$$\sigma_i\in\Sigma[x]$$

$\tau_j$ 是任意多项式。因为可行点上 $g_i\geq0$ 且 $h_j=0$，右侧必非负。

## 十三、二次模与理想

由不等式生成的二次模为：

$$M(g)=\left\{\sigma_0+\sum_i\sigma_i g_i:\sigma_i\in\Sigma[x]\right\}$$

由等式生成的理想为：

$$I(h)=\left\{\sum_j\tau_jh_j:\tau_j\in\mathbb R[x]\right\}$$

证书可简写为：

$$p\in M(g)+I(h)$$

有限阶计算需要限制每个乘积的次数。

## 十四、Archimedean 条件

若存在 $R\gt0$，使：

$$R-\|x\|_2^2\in M(g)+I(h)$$

则称相应二次模满足 Archimedean 条件。它蕴含可行集有界。

工程上常显式加入冗余球约束：

$$R-\|x\|_2^2\geq0$$

这不会改变已知有界的可行集，却使 Putinar 收敛理论可用。

## 十五、Putinar Positivstellensatz

在 Archimedean 条件下，若多项式 $p$ 在 $K$ 上严格为正：

$$p(x)\gt0,\qquad \forall x\in K$$

则：

$$p\in M(g)+I(h)$$

即存在 SOS 乘子证书。定理要求严格正；对仅非负的多项式，有限次数证书可能不存在。

在优化中可对 $f-p^{\star}+\varepsilon$ 使用定理，并令 $\varepsilon\downarrow0$，得到层级渐近收敛。

## 十六、其他 Positivstellensatz

Stengle Positivstellensatz 可处理更一般半代数集合，但证书包含约束乘积和更复杂代数结构。Schmüdgen 证书使用 preordering：

$$\sum_{\nu\in\{0,1\}^m}\sigma_{\nu}(x)\prod_i g_i(x)^{\nu_i}$$

Putinar 证书通常规模更小，因此在满足 Archimedean 条件时更常用于计算。

## 十七、截断 SOS 证书

在松弛阶数 $d$，要求：

$$f-\gamma=\sigma_0+\sum_i\sigma_i g_i+\sum_j\tau_j h_j$$

并满足：

$$\deg\sigma_0\leq2d$$

$$\deg(\sigma_i g_i)\leq2d,\qquad \deg(\tau_jh_j)\leq2d$$

得到有限维 SDP。阶数越高，允许的证书越丰富。

## 十八、Lasserre SOS 层级

第 $d$ 阶对偶 SOS 松弛为：

$$p_d=\sup_{\gamma}\ \gamma$$

约束为：

$$f-\gamma\in M_d(g)+I_{2d}(h)$$

其中 $M_d$ 和 $I_{2d}$ 表示相应次数截断。合法下界满足：

$$p_d\leq p^{\star}$$

并且：

$$p_d\leq p_{d+1}$$

## 十九、概率测度提升

点优化可等价写成测度优化：

$$p^{\star}=\inf_{\mu}\int_K f(x)\,d\mu(x)$$

约束：

$$\mu\geq0,\qquad \mu(K)=1$$

最优测度可取为全局最优点上的 Dirac 测度：

$$\mu=\delta_{x^{\star}}$$

矩松弛把未知测度替换为有限阶矩序列。

## 二十、矩序列

测度 $\mu$ 的矩定义为：

$$y_{\alpha}=\int_Kx^{\alpha}\,d\mu(x)$$

定义 Riesz 线性泛函：

$$L_y(p)=\sum_{\alpha}p_{\alpha}y_{\alpha}$$

于是：

$$L_y(f)=\int_Kf(x)\,d\mu(x)$$

概率归一化对应：

$$y_0=1$$

## 二十一、矩矩阵

阶数 $d$ 的矩矩阵定义为：

$$[M_d(y)]_{\alpha,\beta}=y_{\alpha+\beta},\qquad |\alpha|,|\beta|\leq d$$

对任意：

$$q(x)=c^{\mathsf T}v_d(x)$$

有：

$$c^{\mathsf T}M_d(y)c=L_y(q^2)=\int q(x)^2d\mu(x)\geq0$$

因此真实矩序列必须满足：

$$M_d(y)\succeq0$$

## 二十二、局部化矩阵

对约束多项式：

$$g(x)=\sum_{\gamma}g_{\gamma}x^{\gamma}$$

局部化矩阵定义为：

$$[M_r(gy)]_{\alpha,\beta}=\sum_{\gamma}g_{\gamma}y_{\alpha+\beta+\gamma}$$

若测度支撑在 $g(x)\geq0$ 上，则：

$$c^{\mathsf T}M_r(gy)c=\int q(x)^2g(x)d\mu(x)\geq0$$

所以：

$$M_r(gy)\succeq0$$

## 二十三、等式约束的矩条件

若测度支撑在：

$$h_j(x)=0$$

上，则对允许次数的任意单项式 $x^{\alpha}$：

$$L_y(x^{\alpha}h_j)=0$$

等价地可写成局部化矩阵：

$$M_r(h_jy)=0$$

等式条件是线性约束，不需要把 $h_j$ 和 $-h_j$ 都作为不等式处理。

## 二十四、矩松弛

令：

$$d_i=\left\lceil\frac{\deg g_i}{2}\right\rceil,\qquad e_j=\left\lceil\frac{\deg h_j}{2}\right\rceil$$

第 $d$ 阶矩松弛为：

$$p_d^{\mathrm{mom}}=\inf_yL_y(f)$$

约束：

$$y_0=1,\qquad M_d(y)\succeq0$$

$$M_{d-d_i}(g_iy)\succeq0,\qquad i=1,\ldots,m$$

$$M_{d-e_j}(h_jy)=0,\qquad j=1,\ldots,\ell$$

## 二十五、SOS 与矩的对偶

矩松弛是原始 SDP，SOS 证书是其对偶。直观对应关系为：

| 矩侧 | SOS 侧 |
| --- | --- |
| 未知矩 $y$ | 未知 Gram 矩阵与乘子 |
| 矩矩阵半正定 | 平方和多项式 |
| 局部化矩阵 | SOS 乘以约束 |
| 目标 $L_y(f)$ | 最大化下界 $\gamma$ |
| 原子测度 | 最优点与证书接触 |

在适当 Slater 条件下，两侧最优值相同。

## 二十六、层级收敛

在 Archimedean 条件和可行性等标准假设下：

$$p_d^{\mathrm{mom}}=p_d^{\mathrm{SOS}}\leq p^{\star}$$

且：

$$p_d\uparrow p^{\star}\qquad\text{当 }d\rightarrow\infty$$

这是渐近结论，不保证所有问题在低阶或某个统一有限阶达到精确。

若最优差多项式具有有限次数 Putinar 证书，则相应阶数会有限收敛。

## 二十七、Flat Extension

设：

$$r_K=\max_i\left\lceil\frac{\deg g_i}{2}\right\rceil$$

若最优矩序列满足秩稳定：

$$\operatorname{rank}M_d(y)=\operatorname{rank}M_{d-r_K}(y)=r$$

在相应技术条件下，存在一个由 $r$ 个原子组成的表示测度：

$$\mu=\sum_{k=1}^rw_k\delta_{x^{(k)}}$$

这说明松弛已经精确，并可提取全局最优点。

## 二十八、秩一提取

若：

$$\operatorname{rank}M_d(y)=1$$

则测度为单个 Dirac：

$$\mu=\delta_{x^{\star}}$$

一阶矩直接给出：

$$x_i^{\star}=y_{e_i}$$

随后应把提取点代回原约束和目标，检查可行性与最优值残差。

## 二十九、多原子提取

当平坦秩为 $r\gt1$，可在矩矩阵的列空间中构造乘法算子：

$$\mathcal X_i:q(x)\mapsto x_iq(x)$$

这些算子的联合特征值给出原子坐标 $x^{(k)}$，权重由矩匹配求得。

数值上需要选择稳定基、进行秩判定并处理近重复特征值。仅观察到若干小特征值还不足以证明严格 flatness。

## 三十、单位圆盘示例

考虑：

$$\min_{x,y}\ x$$

约束：

$$1-x^2-y^2\geq0$$

显然最优值为 $-1$，最优点为 $(-1,0)$。可构造证书：

$$x+1=\frac12\left[(x+1)^2+y^2\right]+\frac12(1-x^2-y^2)$$

第一项是 SOS，第二项是非负常数乘约束，因此证明：

$$x\geq-1\qquad\text{在单位圆盘上}$$

该问题在低阶松弛中即可精确。

## 三十一、0–1 多项式优化

二元变量可用：

$$x_i^2-x_i=0$$

或符号变量：

$$z_i^2-1=0$$

编码。任意伪布尔函数都可写成多项式。矩松弛使用这些等式减少高阶矩，并产生组合优化 SDP 层级。

阶数增加最终可达到精确，但矩阵尺寸随变量数和阶数快速增长。

## 三十二、Max-Cut 示例

对无向图权重 $w_{ij}\geq0$，令 $z_i\in\{-1,1\}$。割权重为：

$$\operatorname{Cut}(z)=\frac12\sum_{(i,j)\in E}w_{ij}(1-z_iz_j)$$

约束：

$$z_i^2=1$$

一阶矩松弛引入：

$$X_{ij}\approx z_iz_j$$

并要求：

$$X\succeq0,\qquad X_{ii}=1$$

得到经典 Max-Cut SDP 松弛。

## 三十三、强对偶

若矩 SDP 或 SOS SDP 满足严格可行性，通常有：

$$p_d^{\mathrm{mom}}=p_d^{\mathrm{SOS}}$$

且最优值可达到。若可行集位于低维代数簇上，严格可行性可能失败，导致数值对偶间隙。

可通过消除等式、使用商环基、面约化或更精确的约束预处理改善。

## 三十四、规模增长

矩矩阵维数为：

$$s(n,d)=\binom{n+d}{d}$$

半正定矩阵的条目规模近似为：

$$O\left(s(n,d)^2\right)$$

因此维数和阶数稍大时，稠密 Lasserre 层级迅速不可承受。实际应用必须利用稀疏性、对称性、低阶结构或替代锥。

## 三十五、相关稀疏性

若每个多项式只涉及少量变量，可构建变量交互图。把共同出现于同一项或约束中的变量连边，再做弦图扩展，得到最大团：

$$I_1,\ldots,I_q$$

每个团建立较小矩矩阵：

$$M_d^{I_k}(y)\succeq0$$

在 running intersection property 等条件下，稀疏层级仍可保持渐近收敛。

## 三十六、项稀疏性

Term sparsity 利用实际出现的单项式支撑，而不只看变量共现。可根据指数集合构建支撑图，并把 Gram 矩阵分解为更小块。

项稀疏方法可显著降低高维低项数问题的规模，但不同分解规则可能影响界的强度和收敛保证。

## 三十七、对称性约化

若有限群 $G$ 作用于变量，且：

$$f(gx)=f(x),\qquad K=gK$$

则可把多项式空间分解为群表示的不变子空间，使 Gram 和矩矩阵块对角化。

还可加入对称矩约束。对称化既减少计算，也避免求解器在等价解之间产生不必要的不稳定。

## 三十八、DSOS 与 SDSOS

DSOS 要求 Gram 矩阵对角占优，可转化为线性规划；SDSOS 要求 Gram 矩阵缩放对角占优，可转化为二阶锥规划：

$$\operatorname{DSOS}\subseteq\operatorname{SDSOS}\subseteq\operatorname{SOS}$$

它们通常更快但更保守。得到的下界仍合法，但可能比 SDP SOS 下界弱。

可使用 basis pursuit 或迭代换基逐步增强。

## 三十九、SONC 与其他证书

Sums of Nonnegative Circuit Polynomials（SONC）利用多项式支撑的凸几何构造非负证书。它与 SOS 不互相包含，在稀疏高次多项式中可能更有优势。

其他方法包括：

- Handelman 证书；
- Bernstein 基证书；
- SAGE；
- 区间算术；
- 分支定界；
- McCormick 松弛。

证书选择应匹配可行集和单项式结构。

## 四十、数值缩放

高次单项式会造成严重条件数问题。例如 $x^{20}$ 与常数项在不同尺度上可能相差巨大。应把变量缩放到：

$$x_i\in[-1,1]$$

并缩放目标与约束系数。

Chebyshev 或正交多项式基有时比原始单项式基稳定。求解后必须在原始坐标中重新验证证书残差。

## 四十一、证书后处理

浮点 SDP 解只给出近似 Gram 矩阵。应检查：

$$\|p-v_d^{\mathsf T}Qv_d\|_{\mathrm{coef}}$$

以及：

$$\lambda_{\min}(Q)$$

若需要机器可验证证明，可用高精度求解、有理重构和区间算术，把近似证书转换为精确或严格认证证书。

## 四十二、松弛阶数选择

最小可行阶数至少满足：

$$2d\geq\max\{\deg f,\deg g_i,\deg h_j\}$$

建议流程是：

1. 从最低合法阶开始；
2. 记录下界和对偶残差；
3. 检查 flatness 和候选点；
4. 若未收敛再提高一阶；
5. 同时考虑稀疏分解和变量缩放。

盲目一次提高很多阶，通常会先遇到内存和数值问题。

## 四十三、鲁棒优化

若不确定参数 $u$ 位于半代数集合：

$$U=\{u:g_i(u)\geq0\}$$

鲁棒约束：

$$p(x,u)\geq0,\qquad \forall u\in U$$

可对 $u$ 构造 SOS 证书：

$$p(x,u)=\sigma_0(u)+\sum_i\sigma_i(u)g_i(u)$$

若 $x$ 也是决策变量，系数匹配会产生关于 $x$ 和 Gram 矩阵的联合约束；是否保持凸性取决于参数化方式。

## 四十四、Lyapunov 稳定性

对多项式系统：

$$\dot x=F(x)$$

可寻找多项式 Lyapunov 函数 $V$，满足：

$$V(x)-\varepsilon\|x\|_2^2\in\Sigma[x]$$

$$-\nabla V(x)^{\mathsf T}F(x)-\varepsilon\|x\|_2^2\in\Sigma[x]$$

这给出原点渐近稳定的可验证充分条件。区域稳定性可加入半代数集合乘子。

## 四十五、Barrier Certificate

设初始集为 $X_0$，危险集为 $X_u$。可寻找屏障 $B$，使：

$$B(x)\leq0,\qquad x\in X_0$$

$$B(x)\gt0,\qquad x\in X_u$$

并在边界上满足：

$$\nabla B(x)^{\mathsf T}F(x)\leq0$$

这些集合条件可通过 SOS 乘子编码，为连续系统安全性提供形式证书。

## 四十六、最优控制与占用测度

多项式动力系统的最优控制可提升为占用测度线性规划。其矩松弛把 Liouville 方程转换为矩等式，并用半正定约束保证测度非负。

状态–控制占用测度 $\mu$ 满足弱动力学约束：

$$\int\nabla v(x)^{\mathsf T}F(x,u)d\mu=\int v\,d\mu_T-\int v\,d\mu_0$$

对测试多项式 $v$ 截断后得到有限阶矩 SDP。

## 四十七、博弈与均衡计算

多项式博弈的 Nash 条件可写为最佳回应不等式、KKT 条件或互补多项式系统。有限博弈的混合策略满足：

$$x_i\geq0,\qquad \sum_ix_i=1$$

支持策略满足收益无差异，非支持策略收益不高于均衡收益。这些条件可编码为半代数集合，并用矩方法枚举或优化均衡属性。

但 KKT 条件可能包含非最优驻点，需结合全局最佳回应证书。

## 四十八、5v5 游戏中的多项式代理

可把局部战斗收益、命中概率、资源转换和风险指标拟合为多项式代理：

$$\widehat J(x,a)=\sum_{|\alpha|+|\beta|\leq d}c_{\alpha,\beta}x^{\alpha}a^{\beta}$$

约束可包含：

$$a_i\in[0,1],\qquad \sum_ia_i\leq B$$

以及冷却、距离和安全边界的多项式近似。SOS 松弛可给出代理模型下的全局下界或上界。

## 四十九、游戏中的安全与组合优化

应用包括：

- 证明某个控制区域内血量不会跌破安全线；
- 验证追击策略不会进入不可恢复区域；
- 优化连续技能参数和资源分配；
- 处理英雄选择、目标选择等 0–1 决策；
- 为神经策略的局部多项式近似构造安全屏障；
- 给小规模战术子问题提供全局最优基线。

若原游戏动力学含离散事件、不可微碰撞和复杂网络输出，应分段建模或采用混合整数、PDMP 与分支定界；不能把低阶多项式代理的证书直接解释为原引擎的全局证明。

## 五十、结论

多项式优化把全局最优问题转化为可行集上的多项式非负性。SOS 用半正定 Gram 矩阵提供可计算的充分证书；矩松弛通过矩矩阵和局部化矩阵描述候选概率测度；两者是同一 SDP 层级的对偶视角。

在 Archimedean 条件下，Lasserre 下界单调收敛到全局最优值；出现 flat extension 时，可以从矩序列提取有限个全局最优点。低阶不精确不表示方法错误，而是证书次数不足或问题结构尚未被利用。

实际应用的核心是控制规模和数值误差：优先缩放变量、消除等式、利用相关稀疏性与对称性，从最低合法阶逐步提升，并在原坐标中验证证书与提取解。对于 5v5 游戏，SOS 最适合小规模连续战术、鲁棒安全验证和多项式代理基线，而不是直接替代整个离散事件游戏引擎。
