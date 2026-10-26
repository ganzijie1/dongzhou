# 非线性与鲁棒状态估计：EKF、UKF、粒子滤波、IMM 与 H-infinity 滤波

## 摘要

状态估计解决“真实状态不可直接观测”这一核心问题。传感器只提供带噪声、延迟、遮挡或不完整的观测，而控制器需要位置、速度、加速度、意图、阶段和模式等隐变量。滤波器利用动力学预测未来，再用新观测修正预测，并同时维护不确定性。

扩展 Kalman 滤波器，简称 EKF，通过一阶线性化处理非线性模型；无迹 Kalman 滤波器，简称 UKF，通过确定性 Sigma 点传播均值和协方差；粒子滤波使用带权样本表示任意非高斯、非线性后验；交互多模型滤波，简称 IMM，在多个动力学模式间做概率混合；H-infinity 滤波把未知扰动视为最坏情况能量输入，追求估计误差对扰动的受控增益。

这些方法不是简单的精度等级关系。EKF、UKF 主要依赖单峰高斯近似；粒子滤波适合多峰和强非线性，但计算成本较高；IMM 解决模式切换；H-infinity 解决模型和噪声统计不可信时的鲁棒性。实际系统常把它们组合，例如 IMM-EKF、IMM-UKF、Rao-Blackwellized 粒子滤波或 H-infinity 增强的模式滤波器。

## 一、离散时间状态空间模型

考虑非线性系统：

$$x_k=f_{k-1}(x_{k-1},u_{k-1})+w_{k-1}$$

观测模型为：

$$y_k=h_k(x_k)+v_k$$

其中：

$$x_k\in\mathbb R^n,\qquad y_k\in\mathbb R^m$$

$u_k$ 是已知控制，$w_k$ 是过程噪声，$v_k$ 是观测噪声。高斯滤波通常假设：

$$w_k\sim\mathcal N(0,Q_k)$$

$$v_k\sim\mathcal N(0,R_k)$$

且二者彼此独立，并与初始状态独立。若存在相关噪声、偏置或未知输入，需要扩展状态或使用相应的广义公式。

## 二、滤波目标

给定截至时刻 $k$ 的观测和控制历史：

$$y_{1:k}=(y_1,\ldots,y_k)$$

$$u_{0:k-1}=(u_0,\ldots,u_{k-1})$$

目标是估计过滤后验：

$$p(x_k\mid y_{1:k},u_{0:k-1})$$

预测后验为：

$$p(x_k\mid y_{1:k-1},u_{0:k-1})$$

滤波只使用当前和过去观测；平滑还会使用未来观测：

$$p(x_k\mid y_{1:T}),\qquad T>k$$

二者不能混用。离线回放平滑得到的精度通常高于在线滤波，但不能直接声称在线系统也拥有未来信息。

## 三、贝叶斯预测

Chapman-Kolmogorov 预测为：

$$p(x_k\mid y_{1:k-1})=\int p(x_k\mid x_{k-1},u_{k-1})p(x_{k-1}\mid y_{1:k-1})dx_{k-1}$$

它把上一时刻后验通过状态转移传播到当前时刻。

## 四、贝叶斯更新

观测到 $y_k$ 后，Bayes 更新为：

$$p(x_k\mid y_{1:k})=\frac{p(y_k\mid x_k)p(x_k\mid y_{1:k-1})}{p(y_k\mid y_{1:k-1})}$$

归一化常数为预测似然：

$$p(y_k\mid y_{1:k-1})=\int p(y_k\mid x_k)p(x_k\mid y_{1:k-1})dx_k$$

线性高斯模型中，这两个积分有闭式解；EKF、UKF 和粒子滤波分别使用不同近似计算它们。

## 五、线性 Kalman 滤波基线

线性系统为：

$$x_k=F_{k-1}x_{k-1}+B_{k-1}u_{k-1}+w_{k-1}$$

$$y_k=H_kx_k+v_k$$

若后验为高斯：

$$x_{k-1}\mid y_{1:k-1}\sim\mathcal N(\widehat x_{k-1\mid k-1},P_{k-1\mid k-1})$$

则预测均值为：

$$\widehat x_{k\mid k-1}=F_{k-1}\widehat x_{k-1\mid k-1}+B_{k-1}u_{k-1}$$

预测协方差为：

$$P_{k\mid k-1}=F_{k-1}P_{k-1\mid k-1}F_{k-1}^{\mathsf T}+Q_{k-1}$$

创新为：

$$\nu_k=y_k-H_k\widehat x_{k\mid k-1}$$

创新协方差为：

$$S_k=H_kP_{k\mid k-1}H_k^{\mathsf T}+R_k$$

Kalman 增益为：

$$K_k=P_{k\mid k-1}H_k^{\mathsf T}S_k^{-1}$$

状态更新为：

$$\widehat x_{k\mid k}=\widehat x_{k\mid k-1}+K_k\nu_k$$

## 六、Joseph 协方差更新

简单协方差更新为：

$$P_{k\mid k}=(I-K_kH_k)P_{k\mid k-1}$$

有限精度下，更稳定的 Joseph 形式为：

$$P_{k\mid k}=(I-K_kH_k)P_{k\mid k-1}(I-K_kH_k)^{\mathsf T}+K_kR_kK_k^{\mathsf T}$$

Joseph 形式更容易保持对称半正定。实现后还可做数值对称化：

$$P\leftarrow\frac{1}{2}(P+P^{\mathsf T})$$

但对称化不能修复错误模型、负特征值或严重条件数问题。

## 七、扩展 Kalman 滤波器

EKF 用当前估计附近的一阶 Taylor 展开近似非线性动力学。预测均值为：

$$\widehat x_{k\mid k-1}=f_{k-1}(\widehat x_{k-1\mid k-1},u_{k-1})$$

状态转移 Jacobian 为：

$$F_{k-1}=\left.\frac{\partial f_{k-1}}{\partial x}\right|_{\widehat x_{k-1\mid k-1},u_{k-1}}$$

预测协方差为：

$$P_{k\mid k-1}=F_{k-1}P_{k-1\mid k-1}F_{k-1}^{\mathsf T}+Q_{k-1}$$

## 八、EKF 观测更新

预测观测为：

$$\widehat y_{k\mid k-1}=h_k(\widehat x_{k\mid k-1})$$

观测 Jacobian 为：

$$H_k=\left.\frac{\partial h_k}{\partial x}\right|_{\widehat x_{k\mid k-1}}$$

创新为：

$$\nu_k=y_k-\widehat y_{k\mid k-1}$$

创新协方差为：

$$S_k=H_kP_{k\mid k-1}H_k^{\mathsf T}+R_k$$

Kalman 增益为：

$$K_k=P_{k\mid k-1}H_k^{\mathsf T}S_k^{-1}$$

状态更新为：

$$\widehat x_{k\mid k}=\widehat x_{k\mid k-1}+K_k\nu_k$$

协方差推荐使用 Joseph 形式，其中 $H_k$ 为当前线性化 Jacobian。

## 九、EKF 的一阶近似误差

非线性函数的 Taylor 展开为：

$$f(x)\approx f(\widehat x)+F(x-\widehat x)$$

EKF 忽略二阶及更高阶项。若后验协方差较大、模型曲率较强或均值远离真实状态，线性化误差可能导致：

1. 协方差低估；
2. 创新长期带偏；
3. 增益方向错误；
4. 滤波发散；
5. 角度跨越分支切口时出现跳变。

EKF 的“扩展”不代表对任意非线性都可靠。

## 十、迭代 EKF

当观测模型强非线性时，可以在同一观测上重复线性化。第 $j$ 次迭代的线性化点为：

$$\widehat x_k^{(j)}$$

更新可写为：

$$\widehat x_k^{(j+1)}=\widehat x_{k\mid k-1}+K_k^{(j)}\left[y_k-h_k(\widehat x_k^{(j)})+H_k^{(j)}(\widehat x_k^{(j)}-\widehat x_{k\mid k-1})\right]$$

迭代 EKF 类似一次局部 Gauss-Newton 求解。它可以改善观测更新，但不能消除预测阶段的非高斯误差，也可能因初值差而收敛到错误局部点。

## 十一、误差状态 EKF

姿态、角度或流形状态常使用名义状态与小误差分离：

$$x=\Phi(\widehat x,\delta x)$$

滤波器估计局部误差：

$$\delta x\sim\mathcal N(0,P)$$

观测更新后，把误差注入名义状态：

$$\widehat x\leftarrow\Phi(\widehat x,\delta\widehat x)$$

再重置误差坐标。误差状态方法能避免直接对旋转角做不一致的欧氏加法，但需要正确的注入 Jacobian 和协方差重置。

## 十二、无迹变换

UKF 的基础是 Unscented Transform。若：

$$x\sim\mathcal N(\widehat x,P)$$

希望近似：

$$z=g(x)$$

UKF 不计算 $g$ 的 Jacobian，而是选择一组确定性 Sigma 点，使它们的加权均值和协方差与原高斯分布一致，再将每个点通过非线性函数传播。

## 十三、UKF 参数

状态维数为 $n$，选择参数：

$$\alpha>0,\qquad\beta\geq0,\qquad\kappa\in\mathbb R$$

定义：

$$\lambda=\alpha^2(n+\kappa)-n$$

以及：

$$c=n+\lambda$$

必须满足：

$$c>0$$

$\alpha$ 控制 Sigma 点扩张范围；对高斯先验常取 $\beta=2$；$\kappa$ 用于进一步调整点集。

## 十四、Sigma 点

令矩阵平方根满足：

$$AA^{\mathsf T}=P$$

则 $2n+1$ 个 Sigma 点为：

$$\chi_0=\widehat x$$

$$\chi_i=\widehat x+\sqrt{c}\,A_i,\qquad i=1,\ldots,n$$

$$\chi_{i+n}=\widehat x-\sqrt{c}\,A_i,\qquad i=1,\ldots,n$$

$A_i$ 表示矩阵平方根第 $i$ 列。数值实现通常使用 Cholesky 分解，不应直接对协方差逐元素开平方。

## 十五、UKF 权重

均值权重为：

$$W_0^{(m)}=\frac{\lambda}{c}$$

协方差权重为：

$$W_0^{(c)}=\frac{\lambda}{c}+1-\alpha^2+\beta$$

其余权重为：

$$W_i^{(m)}=W_i^{(c)}=\frac{1}{2c},\qquad i=1,\ldots,2n$$

部分参数设置会产生负的中心权重。负权重并非自动错误，但会增加协方差失去正定性的数值风险。

## 十六、UKF 预测

传播 Sigma 点：

$$\chi_{i,k\mid k-1}=f_{k-1}(\chi_{i,k-1\mid k-1},u_{k-1})$$

预测均值为：

$$\widehat x_{k\mid k-1}=\sum_{i=0}^{2n}W_i^{(m)}\chi_{i,k\mid k-1}$$

预测协方差为：

$$P_{k\mid k-1}=\sum_{i=0}^{2n}W_i^{(c)}e_i^xe_i^{x\mathsf T}+Q_{k-1}$$

其中：

$$e_i^x=\chi_{i,k\mid k-1}-\widehat x_{k\mid k-1}$$

该写法假设过程噪声为加性。非加性噪声可以通过增广状态 UKF 处理。

## 十七、UKF 观测更新

将预测 Sigma 点映射到观测空间：

$$\zeta_{i,k}=h_k(\chi_{i,k\mid k-1})$$

预测观测均值为：

$$\widehat y_{k\mid k-1}=\sum_{i=0}^{2n}W_i^{(m)}\zeta_{i,k}$$

观测创新协方差为：

$$S_k=\sum_{i=0}^{2n}W_i^{(c)}e_i^ye_i^{y\mathsf T}+R_k$$

其中：

$$e_i^y=\zeta_{i,k}-\widehat y_{k\mid k-1}$$

状态与观测的互协方差为：

$$P_k^{xy}=\sum_{i=0}^{2n}W_i^{(c)}e_i^xe_i^{y\mathsf T}$$

增益为：

$$K_k=P_k^{xy}S_k^{-1}$$

状态和协方差更新为：

$$\widehat x_{k\mid k}=\widehat x_{k\mid k-1}+K_k(y_k-\widehat y_{k\mid k-1})$$

$$P_{k\mid k}=P_{k\mid k-1}-K_kS_kK_k^{\mathsf T}$$

## 十八、Square-Root UKF

Square-Root UKF 直接维护协方差平方根：

$$P=SS^{\mathsf T}$$

它使用 QR 分解和 Cholesky 更新避免反复构造完整协方差，通常具有更好的正定性和数值稳定性。

当维数较高、权重含负值或协方差条件数较差时，优先考虑 Square-Root 实现。

## 十九、角度与流形均值

角度不能直接用普通加权平均。例如接近 $-\pi$ 和 $\pi$ 的两个方向实际上接近，但算术平均可能落在零附近。

圆周均值可使用：

$$\overline\theta=\mathrm{atan2}\left(\sum_iw_i\sin\theta_i,\sum_iw_i\cos\theta_i\right)$$

角度残差应归一化到统一区间。姿态位于更一般流形时，应使用适当的群运算、切空间误差和流形 Sigma 点。

## 二十、粒子滤波表示

粒子滤波用带权经验分布近似后验：

$$p(x_k\mid y_{1:k})\approx\sum_{i=1}^Nw_k^{(i)}\delta(x_k-x_k^{(i)})$$

满足：

$$w_k^{(i)}\geq0$$

$$\sum_{i=1}^Nw_k^{(i)}=1$$

粒子集合可以表达偏斜、多峰、截断和离散连续混合分布，这是单高斯 EKF/UKF 无法完整表达的。

## 二十一、序贯重要性采样

对每个粒子，从提议分布采样：

$$x_k^{(i)}\sim q(x_k\mid x_{k-1}^{(i)},y_k)$$

未归一化权重更新为：

$$\widetilde w_k^{(i)}=w_{k-1}^{(i)}\frac{p(y_k\mid x_k^{(i)})p(x_k^{(i)}\mid x_{k-1}^{(i)})}{q(x_k^{(i)}\mid x_{k-1}^{(i)},y_k)}$$

归一化为：

$$w_k^{(i)}=\frac{\widetilde w_k^{(i)}}{\sum_{j=1}^N\widetilde w_k^{(j)}}$$

提议分布越接近当前最优后验，权重方差通常越小。

## 二十二、Bootstrap 粒子滤波

Bootstrap 或 SIR 粒子滤波选择状态转移作为提议：

$$q(x_k\mid x_{k-1}^{(i)},y_k)=p(x_k\mid x_{k-1}^{(i)})$$

于是：

$$x_k^{(i)}\sim p(x_k\mid x_{k-1}^{(i)})$$

权重简化为：

$$\widetilde w_k^{(i)}=w_{k-1}^{(i)}p(y_k\mid x_k^{(i)})$$

SIR 实现简单，但观测很精确或模型维数较高时，大多数预测粒子可能落在低似然区域。

## 二十三、对数权重

连续相乘的似然容易下溢。应维护：

$$\ell_k^{(i)}=\log w_{k-1}^{(i)}+\log p(y_k\mid x_k^{(i)})$$

使用稳定归一化：

$$a=\max_i\ell_k^{(i)}$$

$$w_k^{(i)}=\frac{\exp(\ell_k^{(i)}-a)}{\sum_j\exp(\ell_k^{(j)}-a)}$$

若所有粒子似然都为数值零，应触发观测异常或重初始化逻辑，而不是保留无效的全零权重。

## 二十四、有效样本量

权重退化可用有效样本量诊断：

$$N_{\mathrm{eff}}=\frac{1}{\sum_{i=1}^N(w_k^{(i)})^2}$$

范围为：

$$1\leq N_{\mathrm{eff}}\leq N$$

当：

$$N_{\mathrm{eff}}<\tau N$$

时触发重采样，$\tau$ 常作为可调阈值。每一步都重采样可能加剧样本贫化。

## 二十五、重采样

重采样按照权重复制高权粒子并删除低权粒子。常见方法包括：

1. Multinomial resampling；
2. Residual resampling；
3. Stratified resampling；
4. Systematic resampling。

重采样后通常设置：

$$w_k^{(i)}=\frac{1}{N}$$

Systematic resampling 只需要一个随机起点，方差通常低于朴素多项式重采样，但不同重采样器的相关结构并不完全相同。

## 二十六、样本贫化

频繁重采样会使许多粒子拥有相同祖先，导致多样性下降。可使用：

1. 增加过程噪声或 roughening；
2. 重采样后执行 MCMC move；
3. 使用依赖观测的提议分布；
4. 对条件线性子结构做 Rao-Blackwellization；
5. 保留多个模式或假设簇；
6. 增加粒子数并改善状态降维。

盲目增大随机扰动会使后验过宽，不能代替正确的提议设计。

## 二十七、粒子滤波估计量

后验均值近似为：

$$\widehat x_k=\sum_{i=1}^Nw_k^{(i)}x_k^{(i)}$$

协方差近似为：

$$P_k=\sum_{i=1}^Nw_k^{(i)}(x_k^{(i)}-\widehat x_k)(x_k^{(i)}-\widehat x_k)^{\mathsf T}$$

多峰后验中，均值可能位于所有高概率模式之间的低概率区域。此时应同时输出 MAP 粒子、聚类模式、分位区间或完整粒子集合。

## 二十八、Rao-Blackwellized 粒子滤波

若状态可分为：

$$x_k=(r_k,z_k)$$

且给定 $r_{0:k}$ 后，$z_k$ 条件线性高斯，则只对 $r_k$ 采样，并为每个粒子维护一个 Kalman 滤波器：

$$p(x_{0:k}\mid y_{1:k})=p(r_{0:k}\mid y_{1:k})p(z_{0:k}\mid r_{0:k},y_{1:k})$$

解析积分掉 $z_k$ 可以显著降低 Monte Carlo 方差，但实现复杂度和每粒子计算成本会上升。

## 二十九、模式切换系统

很多目标不是始终遵循同一种动力学。引入离散模式：

$$m_k\in\{1,\ldots,M\}$$

模式转移矩阵定义为：

$$p_{ij}=\mathbb P(m_k=j\mid m_{k-1}=i)$$

满足：

$$p_{ij}\geq0,\qquad\sum_{j=1}^Mp_{ij}=1$$

每个模式拥有独立动力学和噪声：

$$x_k=f^{(m_k)}(x_{k-1},u_{k-1})+w_k^{(m_k)}$$

## 三十、IMM 的目的

精确混合滤波会随着时间产生指数增长的模式历史。IMM 用每个当前模式一个滤波器近似全部历史，并在每一步执行：

1. 模式概率预测；
2. 条件初值混合；
3. 各模型独立滤波；
4. 模型似然计算；
5. 模式概率更新；
6. 总体状态融合。

IMM 以线性数量的滤波器近似指数数量的模式路径。

## 三十一、IMM 模式概率预测

设上一时刻模式概率为：

$$\mu_{k-1}^{(i)}=\mathbb P(m_{k-1}=i\mid y_{1:k-1})$$

当前模式 $j$ 的预测概率为：

$$c_j=\sum_{i=1}^Mp_{ij}\mu_{k-1}^{(i)}$$

这里 $c_j$ 也称为归一化常数或混合概率分母。

## 三十二、IMM 交互概率

给定当前模式为 $j$，上一模式为 $i$ 的条件概率为：

$$\mu_{k-1}^{(i\mid j)}=\frac{p_{ij}\mu_{k-1}^{(i)}}{c_j}$$

满足：

$$\sum_{i=1}^M\mu_{k-1}^{(i\mid j)}=1$$

若 $c_j$ 极小，应使用概率下界或对数域处理，不能直接除以接近零的数。

## 三十三、IMM 初值混合

模式 $j$ 的混合初始均值为：

$$\widehat x_{k-1}^{(0,j)}=\sum_{i=1}^M\mu_{k-1}^{(i\mid j)}\widehat x_{k-1}^{(i)}$$

混合协方差必须包含模式间均值差：

$$P_{k-1}^{(0,j)}=\sum_{i=1}^M\mu_{k-1}^{(i\mid j)}\left[P_{k-1}^{(i)}+e_{ij}e_{ij}^{\mathsf T}\right]$$

其中：

$$e_{ij}=\widehat x_{k-1}^{(i)}-\widehat x_{k-1}^{(0,j)}$$

遗漏外积项会系统性低估模式混合产生的不确定性。

## 三十四、IMM 模型条件滤波

每个模式从混合初值出发运行自己的滤波器：

$$\left(\widehat x_k^{(j)},P_k^{(j)},\nu_k^{(j)},S_k^{(j)}\right)=\mathcal F_j\left(\widehat x_{k-1}^{(0,j)},P_{k-1}^{(0,j)},y_k\right)$$

$\mathcal F_j$ 可以是 KF、EKF、UKF 或其他滤波器。不同模式也可以拥有不同过程噪声、观测模型和控制响应。

## 三十五、IMM 模型似然

高斯创新下，模型似然为：

$$\Lambda_k^{(j)}=\frac{\exp\left[-\frac{1}{2}\nu_k^{(j)\mathsf T}\left(S_k^{(j)}\right)^{-1}\nu_k^{(j)}\right]}{\sqrt{(2\pi)^m\det S_k^{(j)}}}$$

数值实现应使用对数似然：

$$\log\Lambda_k^{(j)}=-\frac{1}{2}\left[m\log(2\pi)+\log\det S_k^{(j)}+\nu_k^{(j)\mathsf T}\left(S_k^{(j)}\right)^{-1}\nu_k^{(j)}\right]$$

不应显式计算矩阵逆和行列式；应使用 Cholesky 分解求解二次型与对数行列式。

## 三十六、IMM 模式概率更新

后验模式概率为：

$$\mu_k^{(j)}=\frac{\Lambda_k^{(j)}c_j}{\sum_{\ell=1}^M\Lambda_k^{(\ell)}c_{\ell}}$$

对数域中先计算：

$$a_j=\log\Lambda_k^{(j)}+\log c_j$$

再使用 log-sum-exp 归一化，避免某一模式似然下溢到零。

## 三十七、IMM 总体融合

总体均值为：

$$\widehat x_k=\sum_{j=1}^M\mu_k^{(j)}\widehat x_k^{(j)}$$

总体协方差为：

$$P_k=\sum_{j=1}^M\mu_k^{(j)}\left[P_k^{(j)}+e_je_j^{\mathsf T}\right]$$

其中：

$$e_j=\widehat x_k^{(j)}-\widehat x_k$$

总体协方差同样必须包含模式均值离散度。

## 三十八、IMM 模型设计

典型运动模型包括：

1. 静止或低速模型；
2. 匀速模型；
3. 匀加速模型；
4. 协调转弯模型；
5. 冲刺模型；
6. 撤退模型；
7. 传送或跳变模型。

模型过少会漏掉真实运动，模型过多且高度相似会导致概率难以区分、计算增加和参数不可辨识。

## 三十九、不同状态坐标的 IMM

标准 IMM 假设各模式状态维度和语义一致。若模式使用不同坐标，需要定义映射：

$$x^{(j)}=T_{ij}(x^{(i)})$$

协方差近似映射为：

$$P^{(j)}=J_{ij}P^{(i)}J_{ij}^{\mathsf T}+Q_{ij}$$

$J_{ij}$ 是映射 Jacobian，$Q_{ij}$ 表示降维、增维或模式切换引入的不确定性。没有明确映射时，直接混合不同状态向量没有数学意义。

## 四十、H-infinity 滤波的动机

Kalman 滤波依赖准确的噪声协方差和概率模型。若扰动是非平稳、重尾、对抗性或统计参数未知，可以把估计设计为最坏情况博弈。

考虑线性系统：

$$x_{k+1}=F_kx_k+G_kw_k$$

$$y_k=H_kx_k+v_k$$

关注输出为：

$$z_k=L_kx_k$$

H-infinity 滤波要求估计误差能量相对于初值误差、过程扰动和观测扰动能量的增益受控。

## 四十一、H-infinity 性能指标

一个典型有限时域要求为：

$$\frac{\sum_{k=0}^T\lVert z_k-\widehat z_k\rVert^2}{\lVert x_0-\widehat x_0\rVert_{P_0^{-1}}^2+\sum_{k=0}^{T-1}\lVert w_k\rVert_{Q_k^{-1}}^2+\sum_{k=0}^T\lVert v_k\rVert_{R_k^{-1}}^2}<\gamma^2$$

其中：

$$\lVert a\rVert_M^2=a^{\mathsf T}Ma$$

$\gamma$ 是允许的最坏能量增益。$\gamma$ 越小，鲁棒要求越强，但滤波 Riccati 不等式越可能不可行。

## 四十二、最小极限与可行性

H-infinity 设计不是任意选择很小的 $\gamma$。存在问题相关的下界：

$$\gamma>\gamma_{\min}$$

若 $\gamma$ 过小，要求超过系统可实现能力，Riccati 递推会失去正定性或滤波器不存在。

实际实现应通过二分搜索、Riccati 可行性和闭环仿真寻找可行 $\gamma$，不能把矩阵分解失败简单归因于数值误差。

## 四十三、信息形式 H-infinity 更新

在一种常见离散线性 H-infinity 估计形式中，定义鲁棒后验信息矩阵：

$$\Omega_k=P_{k\mid k-1}^{-1}+H_k^{\mathsf T}R_k^{-1}H_k-\gamma^{-2}L_k^{\mathsf T}L_k$$

要求：

$$\Omega_k>0$$

后验误差矩阵取为：

$$P_{k\mid k}=\Omega_k^{-1}$$

状态更新可写为：

$$\widehat x_{k\mid k}=\widehat x_{k\mid k-1}+P_{k\mid k}H_k^{\mathsf T}R_k^{-1}(y_k-H_k\widehat x_{k\mid k-1})$$

预测为：

$$P_{k+1\mid k}=F_kP_{k\mid k}F_k^{\mathsf T}+G_kQ_kG_k^{\mathsf T}$$

具体 H-infinity 递推会随性能输出、时序约定和扰动权重而变化。实现时必须从同一性能指标推导全部矩阵，不能从不同文献拼接公式。

## 四十四、H-infinity 与 Kalman 的关系

当：

$$\gamma\rightarrow\infty$$

有：

$$\gamma^{-2}L_k^{\mathsf T}L_k\rightarrow0$$

上述信息更新退化为标准信息形式 Kalman 更新。有限 $\gamma$ 引入最坏情况性能项，通常使滤波器更保守。

H-infinity 并不自动优于 Kalman。当高斯统计模型准确时，Kalman 在均方误差意义下具有最优性；H-infinity 的优势在于对统计失配和未知能量扰动的鲁棒性。

## 四十五、非线性 H-infinity 滤波

非线性系统可以结合 EKF 式线性化：

$$F_k=\left.\frac{\partial f_k}{\partial x}\right|_{\widehat x_k}$$

$$H_k=\left.\frac{\partial h_k}{\partial x}\right|_{\widehat x_{k\mid k-1}}$$

再运行局部 H-infinity Riccati 递推。也可以使用无迹 H-infinity 或粒子化鲁棒滤波。

这些方法同时承担非线性近似和最坏情况设计两类误差，必须分别验证线性化残差与鲁棒增益，不能只报告一个状态 RMSE。

## 四十六、观测门控

异常观测不应无条件进入滤波器。归一化创新平方为：

$$\mathrm{NIS}_k=\nu_k^{\mathsf T}S_k^{-1}\nu_k$$

高斯假设下：

$$\mathrm{NIS}_k\sim\chi_m^2$$

可以用卡方分位数做门控：

$$\mathrm{NIS}_k\leq\chi_{m,1-\alpha}^2$$

超门观测可能是遮挡、错误匹配或模型切换，也可能说明滤波协方差低估。不能长期简单丢弃而不记录。

## 四十七、NEES 一致性

若仿真或标注提供真实状态，归一化估计误差平方为：

$$\mathrm{NEES}_k=(x_k-\widehat x_k)^{\mathsf T}P_k^{-1}(x_k-\widehat x_k)$$

理想高斯一致滤波器满足：

$$\mathbb E[\mathrm{NEES}_k]\approx n$$

NEES 长期过大表示协方差过度自信或模型失配；长期过小表示协方差过于保守。RMSE 小但 NEES 很大仍不是可信滤波器。

## 四十八、创新白化

正确建模时，创新序列应近似零均值且时间不相关：

$$\mathbb E[\nu_k]\approx0$$

$$\mathbb E[\nu_k\nu_{k-\ell}^{\mathsf T}]\approx0,\qquad\ell>0$$

持续偏差提示观测偏置、动力学漏项或错误模式；持续自相关提示过程噪声、延迟或状态维度设置不当。

## 四十九、缺失观测

若时刻 $k$ 没有有效观测，只执行预测：

$$\widehat x_{k\mid k}=\widehat x_{k\mid k-1}$$

$$P_{k\mid k}=P_{k\mid k-1}$$

连续遮挡期间协方差应随过程噪声增长。冻结协方差会产生虚假确定性；无限增长则需要重捕获、地图约束或模式先验控制。

## 五十、异步和延迟观测

观测时间戳为 $t_y$，到达时间为 $t_a$，若：

$$t_y\lt t_a$$

则属于乱序或延迟观测。处理方法包括：

1. 保存有限状态历史并回滚更新；
2. 使用 out-of-sequence measurement 公式；
3. 在因子图或滑动窗口中统一优化；
4. 延迟较小时做近似前向补偿。

直接把旧观测当作当前观测会在高速目标上产生系统性滞后。

## 五十一、数值稳定性

协方差必须满足：

$$P=P^{\mathsf T}$$

$$P\geq0$$

推荐做法包括：

1. 使用 Cholesky 分解求线性系统，不显式求逆；
2. 使用 Joseph 更新或平方根滤波；
3. 对角线设置合理下界；
4. 监控条件数和最小特征值；
5. 对角度和流形状态使用正确残差；
6. 对极小概率使用对数域；
7. 固定随机种子复现粒子滤波测试。

## 五十二、滤波器选型

| 条件 | 推荐方法 | 主要风险 |
|---|---|---|
| 轻度非线性、需要低延迟 | EKF | Jacobian 错误与线性化发散 |
| 中等非线性、单峰高斯近似合理 | UKF | Sigma 点参数与正定性 |
| 强非线性、非高斯或多峰 | 粒子滤波 | 权重退化与计算成本 |
| 明显运动模式切换 | IMM-EKF 或 IMM-UKF | 模式集和转移矩阵失配 |
| 噪声统计不可信、关注最坏扰动 | H-infinity | 保守性与 Riccati 可行性 |
| 离散模式加连续非高斯状态 | IMM-PF 或 Rao-Blackwellized PF | 实现复杂度 |

选择依据应是后验形状、模式结构、实时预算和鲁棒目标，而不是简单按算法名称新旧排序。

## 五十三、战争迷雾中的状态

5v5 游戏可定义目标状态：

$$x_k=(p_x,p_y,v_x,v_y,a_x,a_y,\theta,\omega,c,m)$$

其中 $p$ 是位置，$v$ 是速度，$a$ 是加速度，$\theta$ 是朝向，$\omega$ 是转向率，$c$ 是冷却或资源状态，$m$ 是行为模式。

并非所有分量都应放入同一个高斯向量。离散模式适合 IMM，非负计时器需要合适变换，地图区域可作为离散变量，技能跳跃可能需要混合系统或粒子表示。

## 五十四、游戏观测模型

可能的观测包括：

1. 视野内位置和速度；
2. 小地图中的离散位置；
3. 技能特效和受击事件；
4. 最后可见时间；
5. 地图路径和可通行区域；
6. 队友共享的异步观测；
7. 推断得到的目标选择或战术模式。

若观测是距离和方位：

$$y_k=(r_k,\phi_k)$$

则：

$$r_k=\sqrt{(p_x-s_x)^2+(p_y-s_y)^2}$$

$$\phi_k=\mathrm{atan2}(p_y-s_y,p_x-s_x)$$

这是典型非线性观测，且方位残差需要角度归一化。

## 五十五、IMM 游戏模式

模式可以定义为：

$$m_k\in\{\mathrm{lane},\mathrm{engage},\mathrm{retreat},\mathrm{rotate},\mathrm{recall}\}$$

每个模式具有不同的参考速度、过程噪声和地图约束。模式转移矩阵可依赖局势：

$$p_{ij,k}=p_{ij}(\mathrm{HP},\mathrm{distance},\mathrm{objective},\mathrm{cooldown})$$

标准固定转移矩阵 IMM 可作为基线；状态依赖转移需要额外校准，避免把当前观测重复计入转移先验和模型似然。

## 五十六、多峰位置后验

敌方消失在视野后，可能经过多个岔路。后验可以写成：

$$p(x_k\mid y_{1:k})=\sum_{j=1}^J\pi_jp_j(x_k)$$

单个 EKF 或 UKF 会把多个路线平均成一条可能穿过墙体的虚假路径。此时可使用：

1. 粒子滤波保留多条路径；
2. Gaussian Sum Filter；
3. 地图拓扑上的离散 belief；
4. IMM 加路线模式；
5. 粒子与局部 EKF 的混合。

## 五十七、地图约束

粒子传播后应处理不可通行区域。简单删除越界粒子会改变归一化并可能造成所有粒子死亡。可使用：

1. 沿导航图传播；
2. 反射或投影到可行区域；
3. 在转移密度中显式加入地图约束；
4. 对无有效粒子的情况重新初始化。

选择哪一种取决于真实运动规则。投影不是通用物理模型，可能人为增加墙边概率。

## 五十八、与控制器的接口

滤波器不应只输出点估计。推荐接口返回：

$$\left(\widehat x_k,P_k,\nu_k,S_k,q_k,\mathrm{status}\right)$$

$q_k$ 可以表示 IMM 模式概率或粒子簇概率。控制器可利用协方差做：

1. 风险收紧；
2. 概率避碰；
3. 信息价值规划；
4. 目标重捕获；
5. 安全动作降级。

点估计进入 CLF、CBF 或 BRT 前，应把位置和速度不确定性转换为鲁棒裕量或情景集合。

## 五十九、滤波器与因果边界

滤波器估计隐藏状态，但不自动识别因果关系。一个模式概率升高只表示该模式更能解释观测，不证明某个技能、队友动作或地图事件导致了模式切换。

若要回答干预问题，需要另外使用因果模型、序贯 g-formula、逆强化学习或反事实模拟。

## 六十、参数标定

过程噪声 $Q$ 表示模型无法解释的状态变化，观测噪声 $R$ 表示传感器误差。它们不应只作为让曲线“看起来平滑”的旋钮。

推荐流程：

1. 用高质量轨迹拟合动力学残差；
2. 按观测来源估计误差分布；
3. 用 NIS、NEES 和创新自相关检查一致性；
4. 在不同地图、角色和延迟条件下交叉验证；
5. 对非平稳条件使用分段、模式或在线噪声估计；
6. 保留独立压力测试集。

## 六十一、评估指标

位置 RMSE 为：

$$\mathrm{RMSE}=\sqrt{\frac{1}{T}\sum_{k=1}^T\lVert p_k-\widehat p_k\rVert^2}$$

还应报告：

1. 速度和朝向误差；
2. NIS 与 NEES 覆盖率；
3. 创新均值和自相关；
4. 模式识别延迟；
5. 遮挡期间误差增长；
6. 重捕获时间；
7. 粒子 ESS 与谱系多样性；
8. 协方差正定失败次数；
9. 每帧耗时和尾延迟；
10. 下游控制任务收益与安全违规。

## 六十二、消融实验

至少比较：

1. 恒速外推；
2. 线性 KF；
3. EKF；
4. UKF；
5. 粒子滤波；
6. IMM-EKF 或 IMM-UKF；
7. H-infinity；
8. 无地图约束与有地图约束；
9. 固定噪声与自适应噪声；
10. 无延迟处理与时间戳对齐。

所有方法应使用相同观测、相同测试片段和相同在线信息，避免让某个方法获得未来状态或额外标签。

## 六十三、常见错误

### 1. 把协方差当作真实误差

$P_k$ 是模型条件下的内部不确定性。模型失配时，它可能与真实误差严重不一致。

### 2. 显式求矩阵逆

直接计算 $S^{-1}$ 会降低稳定性。应求解线性方程或使用 Cholesky 分解。

### 3. UKF 逐元素开平方

Sigma 点必须使用矩阵平方根，不能对 $P$ 每个元素独立开方。

### 4. 粒子滤波每帧无条件重采样

这会加速样本贫化，应根据 ESS 或其他退化指标触发。

### 5. IMM 协方差遗漏模式均值差

只平均各模式协方差会低估模式不确定性。

### 6. H-infinity 的公式混搭

不同性能指标和时序约定对应不同 Riccati 递推，不能拼接使用。

### 7. 把平滑结果当成在线结果

使用未来观测的平滑器不能直接用于实时决策性能报告。

### 8. 忽略角度和地图拓扑

普通欧氏均值可能产生穿墙位置或错误朝向。

## 六十四、推荐工程架构

建议将估计系统分为：

1. 时间戳和坐标统一层；
2. 观测关联与门控层；
3. 动力学预测层；
4. EKF、UKF、PF 或 IMM 核心；
5. 地图与规则约束层；
6. 一致性与故障检测层；
7. belief 输出层；
8. 回放记录与离线重算层。

每次更新应记录观测来源、创新、协方差、门控结果、模式概率、ESS、重采样标记和求解状态。

## 六十五、最小实现路线

第一阶段实现二维匀速 KF 与 EKF，建立 Joseph 更新、NIS 门控和缺失观测测试。

第二阶段实现 UKF 和 Square-Root 版本，使用强非线性方位观测对比 EKF。

第三阶段实现 SIR 粒子滤波、对数权重、ESS 和 systematic resampling，验证多峰路线。

第四阶段实现三模式 IMM-EKF 或 IMM-UKF，测试静止、匀速和转弯切换。

第五阶段实现线性 H-infinity 基线，扫描 $\gamma$ 可行区间，并在重尾噪声、协方差失配和对抗扰动下比较 Kalman。

第六阶段接入地图约束、异步观测和下游安全控制，进行完整回放消融。

## 六十六、结论

EKF、UKF、粒子滤波、IMM 和 H-infinity 滤波分别解决非线性、高斯近似、多峰后验、模式切换和统计失配问题。它们共享“预测加更新”的贝叶斯或对抗估计结构，但对后验形状、噪声模型和计算预算作出不同假设。

可靠状态估计不仅要降低 RMSE，还要让不确定性与真实误差一致，正确处理角度、遮挡、延迟、异常观测、模式切换和数值正定性。在游戏模型中，滤波结果应以 belief、协方差和模式概率进入规划与安全控制，而不是把一个平滑点估计当作确定真相。

## 附录：符号表

- $x_k$：隐状态；
- $y_k$：观测；
- $u_k$：已知控制；
- $w_k$：过程噪声；
- $v_k$：观测噪声；
- $Q_k$：过程噪声协方差或能量权重；
- $R_k$：观测噪声协方差或能量权重；
- $P_k$：估计误差协方差或 Riccati 矩阵；
- $\nu_k$：创新；
- $S_k$：创新协方差；
- $K_k$：滤波增益；
- $\chi_i$：UKF Sigma 点；
- $w_k^{(i)}$：粒子权重；
- $N_{\mathrm{eff}}$：有效样本量；
- $\mu_k^{(j)}$：IMM 模式概率；
- $\gamma$：H-infinity 最坏能量增益界。
