# 极端风险建模：GEV、Peaks-over-Threshold、广义 Pareto、尾相关 Copula 与 Cross-Entropy Importance Sampling

## 摘要

平均损失、普通方差和常规蒙特卡洛往往无法可靠描述极低概率但后果严重的事件。极值理论从分块最大值或高阈值超越量出发，对尾部进行专门建模；Copula 将各变量的边缘尾部分布与相依结构分离，描述多种风险是否会共同进入极端区域；重要抽样通过改变采样分布提高失败样本出现频率；Cross-Entropy 方法则迭代学习更接近稀有事件条件分布的提议分布。

本文系统介绍广义极值分布 GEV、Peaks-over-Threshold 方法、广义 Pareto 分布 GPD、尾相关 Copula、Cross-Entropy Importance Sampling，以及阈值选择、去簇、参数估计、回归水平、尾相关诊断、似然比、有效样本量、无偏评估与游戏中的稀有失败分析。

## 一、极端风险问题

设损失随机变量为 $X$，关心超过高阈值 $x$ 的概率：

$$p_x=\Pr(X>x)$$

或者关心多个损失共同超限：

$$p_{x,y}=\Pr(X>x,Y>y)$$

若 $p_x$ 极小，直接蒙特卡洛使用 $N$ 个独立样本时，失败计数近似服从二项分布。朴素估计量为：

$$\widehat p_{\mathrm{MC}}=\frac{1}{N}\sum_{i=1}^N\mathbf 1\{X_i>x\}$$

其方差为：

$$\operatorname{Var}(\widehat p_{\mathrm{MC}})=\frac{p_x(1-p_x)}{N}$$

相对标准误差约为：

$$\frac{\sqrt{\operatorname{Var}(\widehat p_{\mathrm{MC}})}}{p_x}\approx\frac{1}{\sqrt{Np_x}}$$

当 $Np_x$ 很小时，样本中可能一个失败都没有。零次观测不等于真实概率为零。

## 二、两条极值理论路线

经典极值理论有两条互补路线。

第一条是 Block Maxima。把时间序列分成多个区块，在每个区块取最大值：

$$M_k=\max\{X_t:t\in B_k\}$$

经过适当标准化，区块最大值的极限分布属于广义极值分布 GEV。

第二条是 Peaks-over-Threshold，简称 POT。选择高阈值 $u$，保留全部超阈值观测，并研究超越量：

$$Y=X-u\mid X>u$$

在适当条件下，高阈值超越量近似服从广义 Pareto 分布 GPD。

GEV 使用每个区块一个最大值，结构简单但会丢弃其他高值；POT 通常能更有效利用尾部样本，但更依赖阈值和时间相关处理。

## 三、广义极值分布 GEV

### 3.1 分布函数

GEV 分布的参数为位置 $\mu$、尺度 $\sigma>0$ 和形状 $\xi$。当 $\xi\ne0$ 时：

$$G(z)=\exp\left\{-\left[1+\xi\frac{z-\mu}{\sigma}\right]^{-1/\xi}\right\}$$

定义域必须满足：

$$1+\xi\frac{z-\mu}{\sigma}>0$$

当 $\xi=0$ 时取连续极限，得到 Gumbel 分布：

$$G(z)=\exp\left\{-\exp\left[-\frac{z-\mu}{\sigma}\right]\right\}$$

### 3.2 形状参数的含义

- $\xi>0$：Frechet 型重尾，尾部无有限上界；
- $\xi=0$：Gumbel 型轻尾；
- $\xi<0$：Weibull 型有限上端点。

当 $\xi<0$ 时，上端点为：

$$z_{\max}=\mu-\frac{\sigma}{\xi}$$

形状参数决定远尾外推速度，通常也是最难稳定估计的参数。小样本下，$\xi$ 的轻微变化可能大幅改变高回归水平。

### 3.3 回归水平

设 $p=G(z_p)$，则当 $\xi\ne0$：

$$z_p=\mu+\frac{\sigma}{\xi}\left[(-\log p)^{-\xi}-1\right]$$

当 $\xi=0$：

$$z_p=\mu-\sigma\log(-\log p)$$

如果每个区块代表固定时段，$p$ 可以转化为“每若干区块超过一次”的回归期。回归期是长期频率解释，不保证事件会按固定间隔发生。

## 四、Block Maxima 的建模流程

1. 选择与业务周期匹配的区块长度；
2. 每个区块提取一个最大值；
3. 检查区块最大值之间的独立性或弱依赖；
4. 使用极大似然、概率加权矩或贝叶斯方法估计 GEV 参数；
5. 通过 QQ 图、概率图和回归水平图检查拟合；
6. 使用剖面似然、Bootstrap 或后验区间量化不确定性；
7. 对区块长度和非平稳趋势做敏感性分析。

区块过短时，最大值可能尚未进入渐近极值区；区块过长时，可用最大值数量太少。不能只根据拟合优度自动选择而忽略时间语义。

## 五、Peaks-over-Threshold

### 5.1 超越量

选定高阈值 $u$，定义超越量：

$$Y=X-u\quad\mathrm{given}\quad X>u$$

POT 不仅保留每个区块最大值，而是利用所有满足 $X>u$ 的高值。若原始序列存在连续多帧高值，同一次极端事件可能贡献大量相关样本，需要去簇或显式建模依赖。

### 5.2 Pickands-Balkema-de Haan 近似

对广泛分布类别，当阈值足够高时，条件超越分布近似 GPD：

$$\Pr(X-u\le y\mid X>u)\approx H_{\xi,\beta}(y)$$

$\beta>0$ 是阈值处的尺度参数，$\xi$ 与相应 GEV 的尾形状参数一致。

“足够高”不是固定百分位，也不能从定理中直接得到。实际工作必须通过阈值稳定性和样本量权衡选择。

## 六、广义 Pareto 分布 GPD

### 6.1 分布函数

当 $\xi\ne0$ 时：

$$H_{\xi,\beta}(y)=1-\left(1+\xi\frac{y}{\beta}\right)^{-1/\xi}$$

其支持集满足：

$$y\ge0\quad\mathrm{and}\quad1+\xi\frac{y}{\beta}>0$$

当 $\xi=0$ 时，GPD 退化为指数分布：

$$H_{0,\beta}(y)=1-\exp\left(-\frac{y}{\beta}\right)$$

当 $\xi<0$ 时，超越量具有有限上界：

$$0\le y\le-\frac{\beta}{\xi}$$

### 6.2 密度

当 $\xi\ne0$ 时，GPD 密度为：

$$h_{\xi,\beta}(y)=\frac{1}{\beta}\left(1+\xi\frac{y}{\beta}\right)^{-1/\xi-1}$$

当 $\xi=0$ 时：

$$h_{0,\beta}(y)=\frac{1}{\beta}\exp\left(-\frac{y}{\beta}\right)$$

## 七、POT 的尾概率与回归水平

记阈值超越概率为：

$$\zeta_u=\Pr(X>u)$$

对 $x>u$，尾概率近似为：

$$\Pr(X>x)\approx\zeta_u\left[1+\xi\frac{x-u}{\beta}\right]^{-1/\xi}$$

当 $\xi=0$ 时：

$$\Pr(X>x)\approx\zeta_u\exp\left[-\frac{x-u}{\beta}\right]$$

若希望尾概率约为 $1/T$，且目标水平位于阈值以上，即 $T\zeta_u>1$，当 $\xi\ne0$ 时对应回归水平为：

$$x_T=u+\frac{\beta}{\xi}\left[(T\zeta_u)^\xi-1\right]$$

当 $\xi=0$：

$$x_T=u+\beta\log(T\zeta_u)$$

这里 $T$ 的单位必须与观测频率一致。若数据经过去簇，$\zeta_u$ 和回归期解释还要考虑簇到达率。

## 八、阈值选择

阈值过低会产生渐近偏差，阈值过高会造成方差增大。常用诊断包括：

### 8.1 平均超越函数

理论平均超越函数为：

$$e(u)=\mathbb E[X-u\mid X>u]$$

GPD 在适当参数范围内具有近似线性平均超越函数。经验图在一段高阈值区间中接近直线，可以作为候选依据，但不是充分证明。

### 8.2 参数稳定图

在一系列候选阈值上重复拟合，观察形状参数 $\widehat\xi(u)$ 和经过阈值调整的尺度参数是否稳定。

GPD 的阈值稳定性给出：

$$\beta(v)=\beta(u)+\xi(v-u),\quad v>u$$

若参数随阈值剧烈变化，说明阈值过低、样本过少、存在非平稳性或模型不合适。

### 8.3 自动选择的限制

自动阈值程序仍需结合时间相关、业务损失尺度和样本外检验。只选择使似然最大的阈值会偏向保留过多数据，并不自动保证尾部近似成立。

## 九、时间相关与去簇

游戏回放中的极端伤亡、延迟或资源崩溃往往持续多个连续帧。直接把每一帧当作独立超越会低估不确定性。

Run declustering 可把相隔少于 $r$ 个非超越观测的高值合并为一簇，每簇保留峰值。极值指数 $\theta$ 可用于描述有效独立极端簇比例：

$$0<\theta\le1$$

$\theta$ 越小，极端事件聚集越强。去簇参数会影响样本量和回归期，应进行敏感性分析。

若保留完整时间依赖，可使用点过程、Markov 链尾模型或时间变化参数模型，而不是强行独立化。

## 十、非平稳极值模型

地图版本、赛季、玩家水平和战局阶段可能改变极值分布。可令 GEV 参数依赖协变量 $z$：

$$\mu(z)=\beta_0+\beta^\mathsf Tz$$

为保证尺度为正，可写：

$$\log\sigma(z)=\gamma_0+\gamma^\mathsf Tz$$

形状参数也可变化，但通常很难稳定估计。复杂度应由样本外预测、正则化和不确定性分析支持，不能仅靠训练似然增加参数。

## 十一、Copula 与 Sklar 定理

设随机变量 $X$ 和 $Y$ 的边缘分布为 $F_X$ 和 $F_Y$。联合分布可写成：

$$F_{X,Y}(x,y)=C\left(F_X(x),F_Y(y)\right)$$

$C$ 是 Copula。令：

$$U=F_X(X),\quad V=F_Y(Y)$$

在连续边缘下，$U$ 和 $V$ 都服从 $[0,1]$ 上均匀分布。Copula 单独描述依赖结构，从而允许边缘尾部分布与共同极端关系分别建模。

## 十二、尾相关系数

### 12.1 上尾相关

上尾相关系数定义为：

$$\lambda_U=\lim_{q\uparrow1}\Pr(V>q\mid U>q)$$

也可写为：

$$\lambda_U=\lim_{q\uparrow1}\frac{1-2q+C(q,q)}{1-q}$$

### 12.2 下尾相关

下尾相关系数定义为：

$$\lambda_L=\lim_{q\downarrow0}\Pr(V\le q\mid U\le q)$$

等价表达为：

$$\lambda_L=\lim_{q\downarrow0}\frac{C(q,q)}{q}$$

$\lambda_U>0$ 表示当一个变量进入极高分位时，另一个变量仍有非消失概率同时进入极高分位。线性相关系数无法充分描述这种尾部共同极端。

## 十三、常见 Copula 的尾行为

### 13.1 Gaussian Copula

对于相关系数满足 $|\rho|<1$ 的 Gaussian Copula：

$$\lambda_U=\lambda_L=0$$

它可以具有较强的中部相关，却仍是渐近尾独立。因此仅使用 Gaussian Copula 可能低估共同极端。

### 13.2 Student-t Copula

自由度为 $\nu$、相关参数为 $\rho$ 的二维 Student-t Copula 具有对称尾相关：

$$\lambda_U=\lambda_L=2t_{\nu+1}\left[-\sqrt{\frac{(\nu+1)(1-\rho)}{1+\rho}}\right]$$

这里 $t_{\nu+1}$ 是自由度为 $\nu+1$ 的 Student-t 分布函数。较小自由度通常对应更强尾相关。

### 13.3 Gumbel Copula

参数 $\theta\ge1$ 的 Gumbel Copula 具有：

$$\lambda_U=2-2^{1/\theta}$$

并且：

$$\lambda_L=0$$

它适合表达上尾共同极端。

### 13.4 Clayton Copula

参数 $\theta>0$ 的 Clayton Copula 具有：

$$\lambda_L=2^{-1/\theta}$$

并且：

$$\lambda_U=0$$

它适合表达下尾共同极端。旋转 Copula 可以改变尾部方向。

## 十四、尾独立不等于没有极端依赖

当 $\lambda_U=0$ 时，变量仍可能以比完全独立更慢的速度趋于联合尾零概率。可使用残余尾依赖参数或有限阈值条件概率进行诊断。

经验上可计算：

$$\widehat\lambda_U(q)=\frac{\sum_{i=1}^N\mathbf 1\{U_i>q,V_i>q\}}{\sum_{i=1}^N\mathbf 1\{U_i>q\}}$$

但当 $q$ 很高时样本数极少，估计方差很大。应报告分母中的超越次数和置信区间，而不是只给出一条平滑曲线。

## 十五、边缘分布与 Copula 的联合建模

一个实用流程是：

1. 分别拟合每个变量的主体分布和尾部分布；
2. 用概率积分变换得到近似均匀变量；
3. 在变换数据上拟合候选 Copula；
4. 检查上尾和下尾诊断；
5. 比较样本外联合超限概率；
6. 用参数 Bootstrap 传播边缘和 Copula 不确定性。

若边缘模型错误，伪观测不会真正均匀，Copula 参数也会受到污染。不能把边缘拟合和依赖拟合完全割裂地验证。

## 十六、重要抽样

设原始密度为 $f(x)$，稀有事件集合为 $\mathcal F$。目标概率为：

$$p=\Pr_f(X\in\mathcal F)=\int\mathbf 1_{\mathcal F}(x)f(x)\,dx$$

选择提议密度 $q(x)$，只要在失败区域满足 $q(x)>0$，就有：

$$p=\mathbb E_q\left[\mathbf 1_{\mathcal F}(X)\frac{f(X)}{q(X)}\right]$$

定义似然比：

$$w(x)=\frac{f(x)}{q(x)}$$

重要抽样估计量为：

$$\widehat p_{\mathrm{IS}}=\frac{1}{N}\sum_{i=1}^N\mathbf 1_{\mathcal F}(X_i)w(X_i),\quad X_i\sim q$$

如果 $q$ 固定且支持条件成立，该估计量无偏。其方差为：

$$\operatorname{Var}_q(\widehat p_{\mathrm{IS}})=\frac{1}{N}\left[\mathbb E_q\left(\mathbf 1_{\mathcal F}(X)w(X)^2\right)-p^2\right]$$

## 十七、零方差提议分布

理论上的最优提议分布是原分布在失败事件上的条件分布：

$$q^\star(x)=\frac{\mathbf 1_{\mathcal F}(x)f(x)}{p}$$

在 $q^\star$ 下：

$$\mathbf 1_{\mathcal F}(X)\frac{f(X)}{q^\star(X)}=p$$

所以估计方差为零。但 $q^\star$ 依赖未知的 $p$，无法直接使用。Cross-Entropy 方法的目标是从参数族中寻找接近 $q^\star$ 的提议分布。

## 十八、Cross-Entropy 方法

设提议分布属于参数族 $q_\theta$。通过最小化：

$$D_{\mathrm{KL}}(q^\star\|q_\theta)$$

可得到等价优化目标：

$$\theta^\star\in\arg\max_\theta\mathbb E_f\left[\mathbf 1_{\mathcal F}(X)\log q_\theta(X)\right]$$

因为真正失败太少，算法使用逐步升高的中间阈值。设性能函数为 $S(x)$，目标事件为：

$$\mathcal F=\{x:S(x)\ge\gamma^\star\}$$

在第 $t$ 轮，从 $q_{\theta_t}$ 采样，并把中间阈值设为高分位：

$$\gamma_t=\min\left(\gamma^\star,\operatorname{Quantile}_{1-\rho}\{S(X_i)\}_{i=1}^N\right)$$

其中 $\rho$ 是 elite 比例。阈值逐轮接近最终失败阈值。

## 十九、加权 CE 参数更新

由于样本来自当前提议 $q_{\theta_t}$ 而不是原分布 $f$，更新应使用重要权重：

$$w_i^{(t)}=\frac{f(X_i)}{q_{\theta_t}(X_i)}$$

新的参数估计为：

$$\widehat\theta_{t+1}\in\arg\max_\theta\sum_{i=1}^Nw_i^{(t)}\mathbf 1\{S(X_i)\ge\gamma_t\}\log q_\theta(X_i)$$

为减少参数振荡，可使用平滑更新：

$$\theta_{t+1}=\alpha\widehat\theta_{t+1}+(1-\alpha)\theta_t$$

其中 $0<\alpha\le1$。不同文献也使用未加权的经典 CE 更新或基于当前提议的变体；实现必须明确目标测度和权重约定，不能混合公式。

## 二十、Gaussian 提议的更新

若 $q_\theta$ 是多元 Gaussian，参数为均值 $\mu$ 和协方差 $\Sigma$，定义 elite 权重：

$$\omega_i=w_i\mathbf 1\{S(X_i)\ge\gamma_t\}$$

加权均值更新为：

$$\widehat\mu=\frac{\sum_i\omega_iX_i}{\sum_i\omega_i}$$

加权协方差更新为：

$$\widehat\Sigma=\frac{\sum_i\omega_i(X_i-\widehat\mu)(X_i-\widehat\mu)^\mathsf T}{\sum_i\omega_i}$$

有限样本下协方差可能奇异或过度收缩。可加入正则项：

$$\widehat\Sigma_\varepsilon=\widehat\Sigma+\varepsilon I$$

若失败区域具有多个分离模式，单个 Gaussian 可能只覆盖一个模式，应使用混合分布、分层 CE 或多起点运行。

## 二十一、最终概率估计

自适应阶段结束后，冻结最终提议 $q_{\widehat\theta}$，使用一批独立新样本进行最终估计：

$$\widehat p=\frac{1}{N_{\mathrm{eval}}}\sum_{i=1}^{N_{\mathrm{eval}}}\mathbf 1_{\mathcal F}(X_i)\frac{f(X_i)}{q_{\widehat\theta}(X_i)}$$

样本方差估计为：

$$\widehat{\operatorname{Var}}(\widehat p)=\frac{1}{N_{\mathrm{eval}}(N_{\mathrm{eval}}-1)}\sum_i\left(Y_i-\bar Y\right)^2$$

其中：

$$Y_i=\mathbf 1_{\mathcal F}(X_i)\frac{f(X_i)}{q_{\widehat\theta}(X_i)}$$

最终评估样本应独立于 CE 适配样本。直接复用自适应训练样本并套用普通独立同分布标准误差，可能产生偏差或错误置信区间。

## 二十二、权重诊断

对非负权重 $w_i$，常用有效样本量诊断为：

$$\operatorname{ESS}=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}$$

对稀有事件概率估计，更应检查失败加权贡献：

$$Y_i=\mathbf 1_{\mathcal F}(X_i)w_i$$

需要报告：

- 失败样本数；
- 最大权重及权重分位数；
- ESS 和失败贡献 ESS；
- 估计方差与变异系数；
- 多个独立 CE 运行间的稳定性；
- 是否存在单一样本支配估计。

提议分布产生很多失败样本并不自动表示估计准确。若似然比极端不稳定，方差仍可能很大。

## 二十三、支持覆盖与防御混合

若某个失败区域满足 $f(x)>0$ 但 $q(x)=0$，重要抽样估计会遗漏该区域。可使用防御混合：

$$q_\varepsilon(x)=(1-\varepsilon)q_{\widehat\theta}(x)+\varepsilon f(x)$$

其中 $0<\varepsilon<1$。这样只要原分布覆盖失败区域，混合提议也保持支持覆盖。

防御混合通常牺牲一部分效率，但减少模式遗漏和无限权重风险。$\varepsilon$ 应通过独立实验选择并报告。

## 二十四、轨迹型重要抽样

对随机动力学轨迹：

$$\tau=(s_0,a_0,s_1,\ldots,s_T)$$

原轨迹密度记为 $f(\tau)$，提议轨迹密度为 $q(\tau)$。若只改变转移核，似然比可分解为：

$$w(\tau)=\prod_{t=0}^{T-1}\frac{P(s_{t+1}\mid s_t,a_t)}{Q(s_{t+1}\mid s_t,a_t)}$$

应在对数域累计：

$$\log w(\tau)=\sum_{t=0}^{T-1}\left[\log P(s_{t+1}\mid s_t,a_t)-\log Q(s_{t+1}\mid s_t,a_t)\right]$$

若策略、初始分布或外生噪声分布也被修改，似然比必须包含所有改变的概率因子。遗漏任何一项都会使估计错误。

## 二十五、四类方法如何协同

四类方法解决不同问题：

| 方法 | 主要输入 | 主要输出 | 核心用途 |
|---|---|---|---|
| GEV | 分块最大值 | 极值分布与回归水平 | 区块级最大损失 |
| POT/GPD | 阈值以上样本 | 尾概率与超越量模型 | 更充分利用高值数据 |
| 尾相关 Copula | 多变量边缘变换 | 联合尾依赖 | 共同极端与风险叠加 |
| CE Importance Sampling | 可采样概率模型与失败函数 | 高效稀有事件概率估计 | 仿真中的失败加速 |

GEV 和 GPD 是统计尾部模型；Copula 是多变量依赖模型；CE-IS 是改变仿真采样分布的计算方法。它们可以互相校验，但不能互相替代。

## 二十六、5v5 游戏应用

可以研究以下极端量：

- 单次团战最大经济损失；
- 连续时间窗内最大死亡数；
- 极端网络延迟与操作失败；
- 大龙团同时出现视野丢失和关键技能空窗；
- 策略在极罕见阵容和资源差下的崩溃概率。

GEV 可建模每局或每个时间窗的最大损失；POT/GPD 可利用所有高损失团战；尾相关 Copula 可评估经济落后、视野不足和技能真空是否共同极端；CE-IS 可主动偏置出生点、命中结果、敌方策略或环境噪声，寻找罕见失败轨迹。

任何偏置仿真都必须保存完整似然比，最终策略比较应使用冻结提议和独立评估样本。

## 二十七、战棋与战略游戏应用

极端事件可以包括补给链整体中断、关键将领同时阵亡、多城连锁失守、极端天气与叛乱共振、兵力恢复时间异常延长等。

区块可按章节、季度或战役划分；POT 阈值应由损失尺度和样本稳定性共同确定；Copula 可描述多个战区共同崩溃；CE-IS 可偏置敌军行动、天气和补给故障，使灾难路径更频繁出现，再用轨迹似然比恢复真实概率。

## 二十八、验证流程

### 28.1 GEV 与 GPD

- 检查支持条件；
- 报告阈值或区块选择；
- 绘制概率图、QQ 图和回归水平图；
- 使用剖面似然或 Bootstrap 给出参数区间；
- 检查形状参数和尺度参数稳定性；
- 对时间趋势、去簇参数和阈值做敏感性分析；
- 使用留出时间段进行样本外尾部检验。

### 28.2 Copula

- 检查边缘概率积分变换近似均匀；
- 比较多种具有不同尾部结构的 Copula；
- 报告有限阈值尾条件概率；
- 使用样本外联合超限频率验证；
- 传播边缘参数和 Copula 参数不确定性；
- 检查高维模型的正定性与可辨识性。

### 28.3 CE-IS

- 每轮记录阈值、elite 数和参数；
- 检查提议分布对所有失败模式的支持；
- 使用独立最终样本估计概率；
- 报告权重、ESS、方差和置信区间；
- 从多个初始化运行；
- 在较不稀有阈值上与朴素蒙特卡洛比较；
- 对轨迹似然比逐项做单元测试。

## 二十九、常见误区

第一，GEV 主要对应分块最大值，POT 对应阈值超越量；不能把全部原始观测直接当作 GEV 样本。

第二，阈值越高不一定越好。偏差会下降，但有效样本量和参数稳定性可能恶化。

第三，$\xi$ 的点估计不能单独支撑遥远外推。必须给出区间和阈值敏感性。

第四，线性相关很高不等于尾相关非零，线性相关不高也不代表没有共同极端。

第五，Gaussian Copula 在非退化相关下渐近尾独立，不能自动表达强共同尾风险。

第六，CE 适配阶段产生大量失败不等于最终概率估计无偏。必须冻结提议并使用正确似然比和独立评估样本。

第七，单峰提议可能遗漏多个分离失败模式。应考虑防御混合、多起点或混合提议。

第八，重要抽样只能纠正已知的采样分布变化，不能纠正错误的环境模型或遗漏的失败机制。

## 三十、结论

GEV 通过分块最大值描述极值极限，POT 和 GPD 使用高阈值以上数据建立尾概率模型；尾相关 Copula 将边缘尾部与共同极端依赖分开；Cross-Entropy Importance Sampling 通过逐轮学习稀有事件条件区域，提高失败采样效率，并以似然比恢复原分布概率。

可靠的极端风险分析不能只给出一个极小概率。它必须同时说明区块或阈值如何选择、时间相关如何处理、形状参数有多不确定、Copula 是否具有正确尾行为、提议分布是否覆盖全部失败模式、权重是否稳定，以及最终估计是否来自独立评估样本。

## 参考文献

1. Fisher, R. A. and Tippett, L. H. C. Limiting Forms of the Frequency Distribution of the Largest or Smallest Member of a Sample.
2. Gnedenko, B. V. Sur la Distribution Limite du Terme Maximum d'une Serie Aleatoire.
3. Pickands, J. Statistical Inference Using Extreme Order Statistics.
4. Balkema, A. A. and de Haan, L. Residual Life Time at Great Age.
5. Coles, S. An Introduction to Statistical Modeling of Extreme Values.
6. Embrechts, P., Kluppelberg, C. and Mikosch, T. Modelling Extremal Events.
7. Nelsen, R. B. An Introduction to Copulas.
8. Joe, H. Dependence Modeling with Copulas.
9. Rubinstein, R. Y. and Kroese, D. P. The Cross-Entropy Method.
10. Bucklew, J. A. Introduction to Rare Event Simulation.
