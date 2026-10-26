# Cox 与 Determinantal Point Process：覆盖概率、最近邻距离与空间建模

## 摘要

空间点过程研究随机对象在平面或更高维空间中的分布。对象可以是资源点、出生点、敌人、传感器、基站、障碍、事件位置或地图兴趣点。与只保存平均密度的模型不同，空间点过程同时描述点数波动、聚集、排斥、空洞、最近邻和覆盖等几何结构。

Poisson Point Process，简称 PPP，是完全随机空间分布的基线。Cox Process 在给定随机强度场后条件地服从 Poisson 过程，因此自然表达热点、簇集和环境异质性。Determinantal Point Process，简称 DPP，用核矩阵行列式定义联合强度，天然表达点间排斥和较均匀的空间铺开。

覆盖概率可以通过空洞概率或概率生成泛函统一计算；最近邻问题必须区分“从任意位置到最近点的接触距离”和“从一个典型点到其他点的最近邻距离”。对 PPP，二者分布相同；对 Cox 和 DPP，它们一般不同。

本文系统介绍 PPP、Cox、Log-Gaussian Cox、Thomas 簇过程、DPP、核条件、Palm 分布、Ripley K、pair correlation、随机覆盖、重复覆盖、最近邻距离、仿真、估计、边界修正及 5v5 游戏空间建模。

## 一、空间点配置

在区域 $W\subseteq\mathbb R^d$ 中，一个局部有限点过程写为：

$$\Phi=\{X_1,X_2,\ldots\}$$

对有界可测集合 $B\subseteq W$，计数变量为：

$$N(B)=\sum_{X_i\in\Phi}\mathbf 1_{\{X_i\in B\}}$$

局部有限要求：

$$N(B)\lt\infty$$

几乎必然成立。空间点过程的随机性同时包括点数和点的位置。

## 二、简单点过程

简单点过程不允许两个点完全重合：

$$\mathbb P(X_i=X_j)=0,\qquad i\neq j$$

连续空间 PPP、常见 Cox 和连续 DPP 通常是简单的。若业务允许同一格点堆叠多个对象，应使用计数测度、带重数点过程或离散多项计数模型，而不是强行使用简单点过程。

## 三、强度测度

强度测度定义为：

$$\Lambda(B)=\mathbb E[N(B)]$$

若存在强度函数 $\lambda(x)$，则：

$$\Lambda(B)=\int_B\lambda(x)dx$$

齐次过程满足：

$$\lambda(x)=\lambda$$

于是：

$$\mathbb E[N(B)]=\lambda\lvert B\rvert$$

$\lambda$ 的单位是每单位面积或每单位体积的期望点数。

## 四、平稳性与各向同性

平稳过程对平移不变：

$$\Phi+a\sim\Phi$$

各向同性过程对旋转不变：

$$R\Phi\sim\Phi$$

地图边界、道路、河流、出生区域和地形会破坏这些假设。平稳各向同性公式可作为局部基线，但不能不经检验地用于整张非均匀地图。

## 五、Poisson Point Process

强度函数为 $\lambda(x)$ 的 PPP 满足：

$$N(B)\sim\mathrm{Poisson}(\Lambda(B))$$

并且对互不相交区域 $B_1,\ldots,B_r$，计数：

$$N(B_1),\ldots,N(B_r)$$

相互独立。

齐次 PPP 是“完全空间随机性”的标准基线，没有额外聚集，也没有点间排斥。

## 六、PPP 的空洞概率

区域 $B$ 中没有任何点的概率为：

$$\mathbb P(N(B)=0)=e^{-\Lambda(B)}$$

齐次情况下：

$$\mathbb P(N(B)=0)=e^{-\lambda\lvert B\rvert}$$

空洞概率是覆盖概率和最近点距离的基础。

## 七、概率生成泛函

对取值在 $[0,1]$ 的函数 $v(x)$，点过程的概率生成泛函为：

$$G_{\Phi}[v]=\mathbb E\left[\prod_{X_i\in\Phi}v(X_i)\right]$$

PPP 的生成泛函为：

$$G_{\mathrm{PPP}}[v]=\exp\left[-\int_W(1-v(x))\lambda(x)dx\right]$$

生成泛函统一编码空洞、独立稀疏化和随机覆盖概率。

## 八、二阶乘积密度

二阶乘积密度 $\rho^{(2)}(x,y)$ 描述在 $x$ 和 $y$ 附近同时出现两个不同点的局部强度。

pair correlation function 定义为：

$$g(x,y)=\frac{\rho^{(2)}(x,y)}{\lambda(x)\lambda(y)}$$

平稳各向同性时只依赖距离：

$$g(x,y)=g(\lVert x-y\rVert)$$

PPP 满足：

$$g(r)=1$$

## 九、聚集与排斥

若某距离尺度上：

$$g(r)\gt1$$

表示相对于 PPP 更容易同时出现点，体现聚集。

若：

$$g(r)\lt1$$

表示点间排斥。

$g(r)=1$ 只描述该距离尺度的二阶结构，不足以证明整个过程就是 PPP。

## 十、Ripley K 函数

对平稳过程，Ripley K 函数可解释为：给定原点存在一个典型点，半径 $r$ 内其他点数的期望除以强度。

各向同性 $d$ 维形式为：

$$K(r)=d v_d\int_0^r s^{d-1}g(s)ds$$

其中单位球体积为：

$$v_d=\frac{\pi^{d/2}}{\Gamma(1+d/2)}$$

PPP 满足：

$$K_{mathrm{PPP}}(r)=v_dr^d$$

二维时：

$$K_{mathrm{PPP}}(r)=\pi r^2$$

## 十一、Cox Process

令 $\Lambda(x)$ 是非负随机强度场。给定整个强度场后：

$$\Phi\mid\Lambda\sim\mathrm{PPP}(\Lambda(x))$$

则边缘过程称为 Cox Process，也称双随机 Poisson 过程。

随机强度高的区域产生更多点，低强度区域产生空洞，因此 Cox 过程自然呈现过度离散和空间聚集。

## 十二、Cox 计数矩

定义区域随机积分强度：

$$M_B=\int_B\Lambda(x)dx$$

条件于 $\Lambda$：

$$N(B)\mid\Lambda\sim\mathrm{Poisson}(M_B)$$

无条件均值为：

$$\mathbb E[N(B)]=\mathbb E[M_B]$$

方差为：

$$\mathrm{Var}[N(B)]=\mathbb E[M_B]+\mathrm{Var}[M_B]$$

因此：

$$\mathrm{Var}[N(B)]\geq\mathbb E[N(B)]$$

随机强度带来超过 Poisson 的计数波动。

## 十三、Cox 二阶相关

Cox 过程的二阶乘积密度为：

$$\rho^{(2)}(x,y)=\mathbb E[\Lambda(x)\Lambda(y)]$$

因此：

$$g(x,y)=1+\frac{\mathrm{Cov}(\Lambda(x),\Lambda(y))}{\mathbb E[\Lambda(x)]\mathbb E[\Lambda(y)]}$$

当强度场在附近正相关时：

$$g(x,y)\gt1$$

说明点产生聚集。

## 十四、Cox 生成泛函

条件于随机强度场，使用 PPP 生成泛函，再对强度场取期望：

$$G_{\mathrm{Cox}}[v]=\mathbb E_{\Lambda}\left[\exp\left(-\int_W(1-v(x))\Lambda(x)dx\right)\right]$$

与使用平均强度替代随机强度不同：

$$\mathbb E[e^{-M_B}]\neq e^{-\mathbb E[M_B]}$$

因此仅知道平均密度不足以确定 Cox 空洞概率。

## 十五、Log-Gaussian Cox Process

令高斯随机场为：

$$Z(x)\sim\mathrm{GP}(m(x),C(x,y))$$

定义随机强度：

$$\Lambda(x)=e^{Z(x)}$$

得到 Log-Gaussian Cox Process，简称 LGCP。

平均强度为：

$$\lambda(x)=\exp\left[m(x)+\frac{1}{2}C(x,x)\right]$$

平稳情况下 pair correlation 为：

$$g(r)=e^{C(r)}$$

正相关高斯场产生空间聚集。

## 十六、LGCP 协变量

可以写：

$$Z(x)=\beta^{\mathsf T}z(x)+Y(x)$$

$z(x)$ 是地形、道路、资源、人口或地图特征，$Y(x)$ 是剩余空间随机场。

协变量解释确定性空间趋势，随机场解释未观测的局部热点。若遗漏重要协变量，随机场相关长度和方差可能吸收其结构。

## 十七、Shot-Noise Cox Process

令父点过程为：

$$\Phi_p=\{C_j\}$$

随机强度为多个热点核的叠加：

$$\Lambda(x)=\sum_{C_j\in\Phi_p}W_jk(x-C_j)$$

$C_j$ 是热点中心，$W_j$ 是热点权重，$k$ 是空间扩散核。

该模型适合资源围绕营地、事件围绕战斗中心或玩家围绕目标点聚集的场景。

## 十八、Neyman-Scott 簇过程

父点按 PPP 产生，每个父点独立产生随机数量的子点，子点位置围绕父点分布。最终只观测子点。

若父点强度为 $\kappa$，每个父点平均产生 $\mu$ 个子点，则子点强度为：

$$\lambda=\kappa\mu$$

Neyman-Scott 过程是常见的 Poisson cluster process，也可看作特定 Cox 过程。

## 十九、Thomas Process

二维 Thomas 过程令子点相对父点服从：

$$X-C\sim\mathcal N(0,\sigma^2I)$$

若每簇子点数服从 Poisson 分布，则 pair correlation 为：

$$g(r)=1+\frac{1}{4\pi\kappa\sigma^2}\exp\left(-\frac{r^2}{4\sigma^2}\right)$$

$\sigma$ 控制簇宽度，$\kappa$ 控制簇中心密度。

## 二十、Determinantal Point Process

DPP 用核函数：

$$K(x,y)$$

定义各阶乘积密度：

$$\rho^{(n)}(x_1,\ldots,x_n)=\det\left[K(x_i,x_j)\right]_{i,j=1}^n$$

当两个点靠近且核行向量相似时，行列式变小，因此联合出现概率下降，形成软排斥。

## 二十一、DPP 强度

一阶乘积密度为：

$$\lambda(x)=\rho^{(1)}(x)=K(x,x)$$

平稳 DPP 通常满足：

$$K(x,y)=K_0(x-y)$$

于是：

$$\lambda=K_0(0)$$

核的对角控制密度，非对角控制点间相关和排斥尺度。

## 二十二、DPP pair correlation

DPP 的二阶乘积密度为：

$$\rho^{(2)}(x,y)=K(x,x)K(y,y)-\lvert K(x,y)\rvert^2$$

因此：

$$g(x,y)=1-\frac{\lvert K(x,y)\rvert^2}{K(x,x)K(y,y)}$$

所以：

$$0\leq g(x,y)\leq1$$

标准 DPP 表达排斥或无相关，不能直接表达 $g(r)\gt1$ 的聚集。

## 二十三、DPP 核的合法性

在有界区域 $W$ 上，积分算子：

$$(\mathcal Kf)(x)=\int_WK(x,y)f(y)dy$$

需要是 Hermitian、局部迹类且半正定，其特征值满足：

$$0\leq\lambda_j(\mathcal K)\leq1$$

不是任意相似度函数都能作为 DPP 核。密度和排斥尺度过大时可能违反谱约束。

## 二十四、DPP 计数矩

限制在区域 $B$ 的核算子记为 $K_B$。点数均值为：

$$\mathbb E[N(B)]=\mathrm{tr}(K_B)$$

方差为：

$$\mathrm{Var}[N(B)]=\mathrm{tr}(K_B-K_B^2)$$

因此：

$$\mathrm{Var}[N(B)]\leq\mathbb E[N(B)]$$

DPP 计数通常比 Poisson 更均匀，体现欠离散。

## 二十五、DPP 空洞概率

区域 $B$ 中没有点的概率为 Fredholm 行列式：

$$\mathbb P(N(B)=0)=\det(I-K_B)$$

若 $K_B$ 的特征值为 $\lambda_j^{(B)}$，则：

$$\det(I-K_B)=\prod_j(1-\lambda_j^{(B)})$$

实际计算需要离散化、谱展开或专用 Fredholm determinant 数值方法。

## 二十六、离散 DPP 的 L-ensemble

对有限候选集合 $\mathcal Y=\{1,\ldots,M\}$，给定半正定矩阵 $L$，子集 $Y$ 的概率为：

$$\mathbb P(\mathbf Y=Y)=\frac{\det(L_Y)}{\det(I+L)}$$

边缘核为：

$$K=L(I+L)^{-1}$$

反之，在 $I-K$ 可逆时：

$$L=K(I-K)^{-1}$$

L-ensemble 常用于从有限候选点中选择多样且高质量的子集。

## 二十七、质量与相似性分解

离散 DPP 常写为：

$$L_{ij}=q_iS_{ij}q_j$$

$q_i\geq0$ 表示候选点质量，$S_{ij}$ 表示相似性。高质量提高入选概率，高相似性降低两个候选同时入选的概率。

若 $S$ 不是半正定矩阵，则 $L$ 可能不是合法 DPP 核。

## 二十八、DPP 不是硬核过程

DPP 通常产生软排斥：近距离点概率降低，但不一定严格为零。

硬核过程则要求：

$$\mathbb P(\exists X_i,X_j:\lVert X_i-X_j\rVert\lt r_0)=0$$

如果游戏规则要求资源点之间绝不小于固定距离，应使用硬核采样、Poisson disk sampling 或在 DPP 后增加合法性检查，不能只依赖软排斥。

## 二十九、PPP 的接触距离

从空间中一个固定位置到最近点的距离定义为：

$$R=\inf_{X_i\in\Phi}\lVert X_i\rVert$$

事件 $R\gt r$ 等价于半径 $r$ 球内没有点：

$$\mathbb P(R\gt r)=\mathbb P(N(B(0,r))=0)$$

齐次 PPP 下：

$$\mathbb P(R\gt r)=e^{-\lambda v_dr^d}$$

因此分布函数为：

$$F_R(r)=1-e^{-\lambda v_dr^d}$$

## 三十、PPP 最近距离密度

接触距离密度为：

$$f_R(r)=d\lambda v_dr^{d-1}e^{-\lambda v_dr^d}$$

均值为：

$$\mathbb E[R]=\frac{\Gamma(1+1/d)}{(\lambda v_d)^{1/d}}$$

二维时：

$$F_R(r)=1-e^{-\lambda\pi r^2}$$

$$f_R(r)=2\pi\lambda r e^{-\lambda\pi r^2}$$

$$\mathbb E[R]=\frac{1}{2\sqrt{\lambda}}$$

## 三十一、第 k 近邻距离

令 $R_k$ 为从固定位置到第 $k$ 个最近点的距离。事件 $R_k\leq r$ 等价于球内至少有 $k$ 个点。

PPP 下，令：

$$m(r)=\lambda v_dr^d$$

则：

$$\mathbb P(R_k\leq r)=1-\sum_{j=0}^{k-1}e^{-m(r)}\frac{m(r)^j}{j!}$$

密度为：

$$f_{R_k}(r)=\frac{d(\lambda v_d)^k}{(k-1)!}r^{dk-1}e^{-\lambda v_dr^d}$$

## 三十二、接触分布与最近邻分布

接触分布从任意空间位置出发：

$$F(r)=\mathbb P(\Phi\cap B(0,r)\neq\varnothing)$$

最近邻分布从一个典型过程点出发，并排除该点本身：

$$G(r)=\mathbb P^{!0}(\Phi\cap B(0,r)\neq\varnothing)$$

$\mathbb P^{!0}$ 是 reduced Palm 分布。

PPP 根据 Slivnyak 定理满足：

$$F(r)=G(r)$$

一般 Cox 和 DPP 不满足这一等式。

## 三十三、J 函数

空间相互作用可用：

$$J(r)=\frac{1-G(r)}{1-F(r)}$$

PPP 满足：

$$J(r)=1$$

聚集过程通常表现为：

$$J(r)\lt1$$

排斥过程通常表现为：

$$J(r)\gt1$$

这些解释依赖估计尺度、边界修正和分母不接近零。

## 三十四、Cox 接触距离

Cox 过程半径 $r$ 球的空洞概率为：

$$1-F(r)=\mathbb E\left[\exp\left(-\int_{B(0,r)}\Lambda(x)dx\right)\right]$$

因此：

$$F(r)=1-\mathbb E\left[\exp\left(-\int_{B(0,r)}\Lambda(x)dx\right)\right]$$

由于随机强度积分在指数内部，不能只把它替换为平均强度。LGCP 通常需要数值积分、Laplace 近似或 Monte Carlo。

## 三十五、DPP 接触距离

DPP 的接触分布为：

$$F(r)=1-\det(I-K_{B(0,r)})$$

这直接来自 DPP 空洞概率。若过程平稳，结果只依赖半径；非平稳 DPP 还依赖查询位置。

## 三十六、DPP Palm 核

给定位置 $x$ 存在一个 DPP 点并删除该点后，reduced Palm 过程仍是 DPP，其核为：

$$K^x(y,z)=K(y,z)-\frac{K(y,x)K(x,z)}{K(x,x)}$$

对平稳过程的典型点可取 $x=0$。最近邻分布为：

$$G(r)=1-\det(I-K_{B(0,r)}^0)$$

由于 Palm 核体现典型点周围的排斥，DPP 的 $G(r)$ 通常与接触分布 $F(r)$ 明显不同。

## 三十七、随机球覆盖模型

给每个点 $X_i$ 附加独立随机覆盖半径 $R_i$，覆盖集合为：

$$\mathcal U=\bigcup_{X_i\in\Phi}B(X_i,R_i)$$

原点被覆盖的概率为：

$$p_{\mathrm{cov}}=\mathbb P(0\in\mathcal U)$$

这称为 Boolean germ-grain model。点是 germ，覆盖球是 grain。

## 三十八、PPP 覆盖概率

齐次 PPP 且半径独立同分布时，覆盖原点的点数服从 Poisson 分布，其均值为：

$$m_{\mathrm{cov}}=\lambda v_d\mathbb E[R^d]$$

因此：

$$p_{\mathrm{cov}}=1-\exp\left[-\lambda v_d\mathbb E[R^d]\right]$$

二维固定半径 $R$ 时：

$$p_{\mathrm{cov}}=1-e^{-\lambda\pi R^2}$$

## 三十九、k 重覆盖

原点被至少 $k$ 个 PPP 覆盖球覆盖的概率为：

$$p_{\mathrm{cov}}^{(k)}=1-\sum_{j=0}^{k-1}e^{-m_{\mathrm{cov}}}\frac{m_{\mathrm{cov}}^j}{j!}$$

重复覆盖适合描述多传感器冗余、多个治疗区叠加或同时受到多个威胁区域影响。

“至少一次覆盖”和“覆盖次数期望”不同：

$$\mathbb E[C(0)]=m_{\mathrm{cov}}$$

而覆盖概率为 $1-e^{-m_{\mathrm{cov}}}$。

## 四十、一般点过程的覆盖

若位置 $x$ 的点独立地以概率 $q(x)$ 覆盖原点，则未覆盖概率为：

$$1-p_{\mathrm{cov}}=G_{\Phi}[1-q]$$

因此：

$$p_{\mathrm{cov}}=1-G_{\Phi}[1-q]$$

这将覆盖问题统一为概率生成泛函计算。

## 四十一、Cox 覆盖概率

条件于随机强度场，覆盖点是独立稀疏化的 PPP。因此：

$$p_{\mathrm{cov}}=1-\mathbb E_{\Lambda}\left[\exp\left(-\int_Wq(x)\Lambda(x)dx\right)\right]$$

聚集会同时产生热点和大空洞。即使平均覆盖点数与 PPP 相同，覆盖概率也可能更低，因为更多点浪费在已经密集覆盖的热点中。

## 四十二、DPP 覆盖概率

定义加权核：

$$K_q(x,y)=\sqrt{q(x)}K(x,y)\sqrt{q(y)}$$

则独立覆盖稀疏化后的空洞概率为：

$$1-p_{\mathrm{cov}}=\det(I-K_q)$$

因此：

$$p_{\mathrm{cov}}=1-\det(I-K_q)$$

DPP 的排斥通常减少重叠浪费并改善空间均匀性，但具体覆盖优劣取决于核、密度、边界和覆盖半径。

## 四十三、有限区域边界

查询点 $x$ 靠近地图边界时，覆盖球与可部署区域的交集变小。PPP 固定半径覆盖概率应使用：

$$p_{\mathrm{cov}}(x)=1-\exp\left[-\lambda\lvert B(x,R)\cap W\rvert\right]$$

不能直接使用无限平面公式 $1-e^{-\lambda\pi R^2}$。

若地图有墙体或不可穿透区域，应使用可见区域、路径球或传播核，而不是纯欧氏圆。

## 四十四、网络 SINR 覆盖

无线网络中的覆盖常定义为：

$$\mathrm{SINR}=\frac{PH_0R_0^{-\alpha}}{\sigma^2+\sum_{X_i\neq X_0}PH_i\lVert X_i\rVert^{-\alpha}}$$

覆盖概率为：

$$p_c(\theta)=\mathbb P(\mathrm{SINR}\gt\theta)$$

它与几何圆盘覆盖不同，因为干扰点越多可能降低覆盖。不能把 $1-e^{-\lambda\pi R^2}$ 当作 SINR 覆盖公式。

## 四十五、PPP Rayleigh SINR 基线

在二维齐次 PPP、最近基站关联、Rayleigh 衰落、相同发射功率、无热噪声且路径损耗指数 $\alpha\gt2$ 的经典模型中：

$$p_c(\theta)=\frac{1}{1+\rho(\theta,\alpha)}$$

其中：

$$\rho(\theta,\alpha)=\theta^{2/\alpha}\int_{\theta^{-2/\alpha}}^{\infty}\frac{1}{1+u^{\alpha/2}}du$$

这是高度特定的闭式基线。有限区域、阴影、功率控制、噪声、Cox 或 DPP 部署都会改变结果。

## 四十六、覆盖半径的反问题

PPP 二维固定半径模型中，若目标覆盖概率为 $p_0$，所需半径满足：

$$R\geq\sqrt{\frac{-\log(1-p_0)}{\lambda\pi}}$$

若半径固定，所需密度满足：

$$\lambda\geq\frac{-\log(1-p_0)}{\pi R^2}$$

这些公式只适用于无限平面 PPP 几何覆盖，不能直接用于排斥、聚集或有边界地图。

## 四十七、Monte Carlo 覆盖估计

给定 $M$ 个均匀查询点 $U_j$，覆盖概率估计为：

$$\widehat p_{\mathrm{cov}}=\frac{1}{M}\sum_{j=1}^M\mathbf 1_{\{U_j\in\mathcal U\}}$$

若查询点独立，近似标准误为：

$$\mathrm{SE}(\widehat p_{\mathrm{cov}})\approx\sqrt{\frac{\widehat p_{\mathrm{cov}}(1-\widehat p_{\mathrm{cov}})}{M}}$$

对于同一随机地图中的密集网格点，查询结果具有空间相关，普通二项标准误会偏小，应按独立地图重复或空间区块估计不确定性。

## 四十八、PPP 仿真

在有限区域 $W$ 中模拟齐次 PPP：

1. 采样点数：

$$N\sim\mathrm{Poisson}(\lambda\lvert W\rvert)$$

2. 条件于 $N$，独立均匀采样：

$$X_i\sim\mathrm{Uniform}(W)$$

非齐次 PPP 可以使用 thinning、逆变换或按强度分块采样。

## 四十九、Cox 仿真

先模拟随机强度场：

$$\Lambda(x)$$

再条件地模拟非齐次 PPP。LGCP 常在网格上模拟高斯场，指数变换后在每个像素内采样 Poisson 点。

网格过粗会抹去短程相关，指数变换还会放大高斯场插值误差。仿真分辨率必须小于关注的最短空间尺度。

## 五十、DPP 谱仿真

有界区域 DPP 可通过核算子的特征分解模拟。若特征值为 $\lambda_j$，先独立采样：

$$B_j\sim\mathrm{Bernoulli}(\lambda_j)$$

保留 $B_j=1$ 的特征函数，得到 projection DPP，再逐点采样位置并更新子空间。

离散 DPP 也可对有限核矩阵做特征分解。大规模问题需要低秩、Nyström、随机特征或专门的近似采样算法。

## 五十一、PPP 强度估计

齐次 PPP 的极大似然估计为：

$$\widehat\lambda=\frac{N(W)}{\lvert W\rvert}$$

非齐次 log-linear 强度可写为：

$$\lambda(x)=\exp(\beta^{\mathsf T}z(x))$$

对数似然为：

$$\ell(\beta)=\sum_{X_i\in\Phi}\beta^{\mathsf T}z(X_i)-\int_W\exp(\beta^{\mathsf T}z(x))dx$$

积分通常使用数值网格或 quadrature 近似。

## 五十二、Cox 估计

LGCP 的似然需要对潜在高斯场积分，常用方法包括：

1. Laplace 近似；
2. MCMC；
3. INLA 型近似；
4. 变分推断；
5. 最小对比拟合 K 函数；
6. pairwise composite likelihood。

只拟合一阶强度无法识别随机场协方差；需要二阶统计或完整潜变量推断。

## 五十三、DPP 估计

离散 L-ensemble 的对数似然为：

$$\ell(L)=\log\det(L_Y)-\log\det(I+L)$$

连续 DPP 可使用谱似然、近似 Fredholm determinant、最小对比或复合似然。

估计时必须同时满足核合法性的谱约束。忽略约束可能得到高似然但不存在的 DPP。

## 五十四、边界修正

有限观察窗中，靠近边界的点有一部分邻域不可见，会低估邻居数。常见修正包括：

1. Translation correction；
2. Isotropic correction；
3. Border correction；
4. Toroidal correction；
5. 仿真包络使用相同窗口。

环面修正只在地图确实周期或边界影响可忽略时合理。

## 五十五、模型诊断

应比较：

1. 计数均值与方差；
2. 空洞概率；
3. pair correlation $g(r)$；
4. Ripley $K(r)$ 或 $L(r)$；
5. 接触分布 $F(r)$；
6. 最近邻分布 $G(r)$；
7. $J(r)$；
8. 覆盖率与重复覆盖；
9. 独立测试窗口的似然；
10. 模型仿真包络。

只匹配点数或平均最近距离不足以区分 PPP、Cox 与 DPP。

## 五十六、游戏资源分布

不同机制适合不同点过程：

1. 独立随机小资源可用 PPP；
2. 资源围绕营地、地形热点聚集可用 Cox；
3. 出生点或战略资源需要均匀分散可用 DPP；
4. 严格最小距离应使用硬核或 Poisson disk；
5. 固定规则点加随机扰动应使用结构化生成模型，而非纯平稳过程。

模型选择应来自关卡规则，而不是只看某个统计量拟合更好。

## 五十七、视野与技能覆盖

每个视野点、守卫或技能中心作为 germ，视野区域作为 grain。覆盖概率衡量随机位置被至少一个区域覆盖的概率。

若覆盖区域受墙体阻挡，可定义：

$$C_i=\{x:d_{\mathrm{path}}(x,X_i)\leq R_i,\ \mathrm{visible}(x,X_i)=1\}$$

覆盖集合为：

$$\mathcal U=\bigcup_iC_i$$

此时通常需要地图几何算法或 Monte Carlo，圆盘闭式公式不再适用。

## 五十八、最近目标距离

最近邻距离可用于：

1. 最近资源点；
2. 最近敌人或队友；
3. 最近安全区；
4. 最近出生点；
5. 最近视野盲区；
6. 最近障碍或掩体。

若查询位置是任意地图位置，使用接触分布 $F$；若查询位置本身是一个过程点，例如“从典型资源点到下一个资源点”，使用 Palm 最近邻分布 $G$。

## 五十九、DPP 关卡布点

对有限候选格点 $i$，定义质量：

$$q_i=\exp(\beta^{\mathsf T}z_i)$$

定义相似性：

$$S_{ij}=\exp\left(-\frac{d_{ij}^2}{2\sigma^2}\right)$$

构造：

$$L_{ij}=q_iS_{ij}q_j$$

DPP 在偏好高质量位置的同时避免选择过于相似的点。若要求恰好选择 $k$ 个点，应使用 $k$-DPP。

## 六十、Cox 热点建模

可把地图环境特征放入 LGCP：

$$\log\Lambda(x)=\beta_0+\beta_1\mathrm{terrain}(x)+\beta_2\mathrm{objective}(x)+Y(x)$$

$Y(x)$ 表示无法由已知地图特征解释的热点。

若热点随时间移动，应使用时空 Cox 过程：

$$\Lambda(t,x)=\exp(Z(t,x))$$

并显式建模时间相关，而不是把所有时刻叠加为静态热点。

## 六十一、公平性与可玩性

高覆盖率不一定意味着良好关卡。过度均匀可能缺乏战术差异，过度聚集则可能造成资源滚雪球。

可以联合评估：

1. 两队出生区的覆盖差；
2. 最近资源距离分布差；
3. 高价值点的路径成本；
4. 重复覆盖和浪费；
5. 热点拥塞；
6. 多次随机生成之间的方差；
7. 极端空洞概率。

## 六十二、与优化的组合

点过程可以生成候选或概率先验，再由优化器满足硬约束：

1. DPP 生成多样候选子集；
2. MILP 处理容量、阵营和路径约束；
3. 次模优化最大化覆盖；
4. CVT 或 Lloyd 方法改善均匀性；
5. BRT/CBF 检查动态安全；
6. 回放仿真评估实际可玩性。

随机几何模型不应绕过地图合法性、碰撞和任务规则。

## 六十三、与图模型的连接

从点配置构造半径图：

$$A_{ij}=\mathbf 1_{\{\lVert X_i-X_j\rVert\leq r\}}$$

可研究连通性、孤立点和覆盖网络。PPP、Cox 与 DPP 的空间结构会改变图度分布和连通阈值。

平均覆盖不保证图连通；即使每个位置接近某个点，点之间也可能无法形成通信链。

## 六十四、常见错误

### 1. 把 Cox 当作普通非齐次 PPP

Cox 强度本身随机，因此计数方差和空洞概率不能只用平均强度计算。

### 2. 把 DPP 当作严格最小距离采样

DPP 通常是软排斥，不自动保证硬间距。

### 3. 混淆 F 与 G

任意位置到最近点和典型点到最近其他点属于不同 Palm 条件。

### 4. 忽略有限地图边界

无限平面覆盖和最近距离公式在地图边缘会产生偏差。

### 5. 只比较平均密度

PPP、Cox 与 DPP 可以拥有相同强度，却具有完全不同的空洞和邻距结构。

### 6. 把几何覆盖当作 SINR 覆盖

干扰可能使更多发射点降低通信覆盖。

### 7. 使用非法 DPP 核

核必须满足半正定和谱特征值约束。

### 8. 把欧氏距离当作地图路径距离

墙体、河流和不可通行区域会改变真实邻近关系。

## 六十五、最小实现路线

第一阶段实现有限矩形区域 PPP，验证点数、空洞概率、最近距离和固定圆覆盖闭式公式。

第二阶段实现 Thomas 过程和 LGCP，比较计数过度离散、$g(r)$、$K(r)$ 与空洞分布。

第三阶段实现离散 DPP 和 $k$-DPP，验证核特征值、子集概率、排斥和最近邻分布。

第四阶段实现边界修正、接触分布 $F$、最近邻分布 $G$ 和 $J$ 函数。

第五阶段接入地图可见性、路径距离和随机覆盖 Monte Carlo，比较 PPP、Cox、DPP 与硬核布点。

第六阶段将 DPP 候选、覆盖优化和游戏规则求解器串联，并用多局回放验证可玩性。

## 六十六、结论

PPP、Cox 和 DPP 分别代表完全随机、聚集和排斥三类重要空间结构。Cox 通过随机强度场表达热点和环境异质性；DPP 通过核行列式表达点间排斥和多样性。它们即使具有相同平均密度，也会产生不同的空洞概率、最近邻距离和覆盖效率。

覆盖概率可以通过生成泛函统一理解，最近距离则需要区分普通空间位置和 Palm 典型点。实际游戏和工程应用必须同时考虑有限边界、地图障碍、路径距离、硬约束和统计诊断，不能把无限平面闭式公式直接当作完整关卡保证。

## 附录：符号表

- $\Phi$：空间点过程；
- $N(B)$：区域 $B$ 内点数；
- $\lambda(x)$：一阶强度；
- $\Lambda(B)$：强度测度；
- $g(r)$：pair correlation function；
- $K(r)$：Ripley K 函数；
- $\Lambda(x)$：Cox 随机强度场；
- $K(x,y)$：DPP 核；
- $L$：离散 DPP 的 L-ensemble 核；
- $F(r)$：接触距离分布；
- $G(r)$：Palm 最近邻分布；
- $J(r)$：基于 $F$ 与 $G$ 的相互作用诊断；
- $v_d$：$d$ 维单位球体积；
- $p_{\mathrm{cov}}$：覆盖概率；
- $R_k$：第 $k$ 近邻距离。
