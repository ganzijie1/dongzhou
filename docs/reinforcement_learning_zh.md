# 将 Mirror Mode 强化学习移植到 mengde

本目录实现了论文《Mirror Mode in Fire Emblem》中使用的主要方法：玩家示范、行为克隆（BC）、生成对抗模仿学习（GAIL）、PPO、非法动作掩码，以及游戏内奖励。

## 架构

训练不会模拟鼠标或读取画面，而是直接复用 `mengde` 的 C++ 规则引擎：

1. `core::RLEnvironment` 从当前 `Game` 枚举合法单位、移动格和攻击目标。
2. 每个完整的“单位 + 落点 + 行为 + 目标”被展平为一个离散动作。与论文的三个独立动作分支相比，这能避免选择出彼此不兼容的落点和目标。
3. `mengde_rl` 通过标准输入输出提供 `RESET`、`STEP` 和 `ACTIONS` 命令。
4. `rl.MengdeEnv` 将协议包装为 Gymnasium 环境，并向 MaskablePPO 提供动作掩码。
5. 训练先用玩家示范做 BC，再用 GAIL 和 masked PPO 联合训练；GAIL 奖励权重为 `1.0`，原始游戏奖励权重为 `0.5`。

观测是固定长度向量。开头包含回合、当前阵营和地图尺寸；之后最多 32 个单位各占 16 项，包括阵营、存活/行动状态、坐标、HP/MP、五维属性和移动力。所有数值归一化到 `[0, 1]`。

奖励沿用论文的主体设计：合法动作 `+0.3`，击杀 `+1`，己方死亡 `-1`，胜负额外 `+1/-1`，20 次己方动作未结束则截断并 `-1`。由于曹操传地图比论文的 `6x8` 地图大，另加入权重为 `0.1` 的双方 HP 差变化，减少长地图的稀疏奖励问题。

## 构建

先按项目原有说明安装 CMake、C++11 编译器、SDL2、SDL2_ttf、Lua 5.2 和 Boost，然后配置并构建。新增目标名为 `mengde_rl`。

```powershell
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target mengde_rl
```

可执行文件的具体位置取决于 CMake 生成器。后续命令用实际路径替换 `<mengde_rl>`。

## Python 环境

使用 Python 3.10 至 3.12。仓库当前机器上的 Python 3.14 不适合论文对应的 PyTorch/imitation 版本。

```powershell
py -3.10 -m venv .venv-rl
.\.venv-rl\Scripts\Activate.ps1
python -m pip install -r rl\requirements.txt
```

## 快速启动验证

当前 Windows 构建可直接运行以下命令，不需要示范或模型：

```powershell
cd C:\mengde
.\.venv-rl\Scripts\python.exe -m rl.smoke_test
```

它会真实启动 `mengde_rl`，检查 516 维观测、合法动作掩码，并连续执行三个动作。看到
`mengde RL smoke test passed` 表示 C++ 规则引擎、进程协议和 Gymnasium 封装已经连通。

## 收集玩家示范

下面的交互式采集器会列出规则引擎给出的完整合法动作。论文每位玩家使用五局示范，因此默认也是五局。

```powershell
python -m rl.record_demo --executable <mengde_rl> --episodes 5 --output rl\demonstrations\player01.npz
```

每步选择一个动作编号。输入 `q` 可以提前结束并保存已经收集的数据。

## 训练

```powershell
python -m rl.train --executable <mengde_rl> --demonstrations rl\demonstrations\player01.npz --output rl\models\player01 --steps 1000000
```

主要超参数对齐论文最终模型：学习率 `3e-4`、两层 256 单元网络、batch size 256、PPO clip 0.2、GAIL 两层 128 单元网络、GAIL 强度 1.0、外部奖励强度 0.5。TensorBoard 日志写入 `rl/models/tensorboard`。

快速连通性验证可先用 `--steps 4096 --bc-epochs 1`。这只能验证管线，不能产生可用战术模型。

## 运行模型

```powershell
python -m rl.play --executable <mengde_rl> --model rl\models\player01.zip --episodes 5
```

当前入口为 headless 对局，用于训练、评估和批量实验。若要在 SDL 图形界面中让敌军使用模型，需要再选择一种部署方式：随游戏分发 Python sidecar，或将策略导出 ONNX 并在 C++ 中加入推理运行时。训练与数据接口不依赖该部署选择。

## 图形化观察策略

打开可交互战斗窗口：

```powershell
.\.venv-rl\Scripts\python.exe -m rl.play_gui
```

默认从 `D:\Downloads\LZC传（Li自成）\LZC传（Li自成）` 读取
`map/m000.jpg` 的 19x16 原版战场、`Hexzmap.e5` 第 0 关地形数据和
从原版战斗窗口提取的透明人物动作形象。`E5/Face.e5` 头像只在选中人物后显示于
右侧情报栏。`Mmap.e5` 是过场/R 场景资源，不用于战斗。可用
`--map m001.jpg` 选择其他原版战场，或通过 `--assets-root` 指向素材的其他副本。

窗口默认加载 `rl/models/enemy_ppo.zip` 控制敌方。也可以指定其他 MaskablePPO 模型：

```powershell
.\.venv-rl\Scripts\python.exe -m rl.play_gui --enemy-model rl\models\player01.zip
```

窗口会明确显示 PPO 模型是否加载。敌方推理会把阵营观测转换为训练时的我方视角，
并在 PPO 概率上应用攻击优先、禁止无意义待命等战术约束。

我方回合用鼠标选择单位和落点，再点击“攻击”选择敌军，或点击“待命”。蓝色范围来自
C++ 地形寻路、兵种移动代价和控制区规则。单位会沿避开城墙的四方向路径逐格走动，
行走期间切换腿部帧，静止时不播放抖动动画。敌方回合由模型逐单位决策。`R` 重开，`Esc` 退出。

不需要示范数据时，可训练一个 MaskablePPO 基线：

```powershell
.\.venv-rl\Scripts\python.exe -m rl.train_ppo --steps 30000
```

批量转换 MOD 的 EEX 剧本：

```powershell
.\.venv-rl\Scripts\python.exe tools\eex_converter.py `
  "D:\Downloads\LZC传（Li自成）\LZC传（Li自成）\RS" `
  --style assets_work\eex_editor\style.txt `
  --output game\sce\lzc\generated
```

`manifest.json` 汇总已识别指令、对白和 12 关部署表。无法识别的新引擎扩展 Section 会带
`parse_error` 和 `raw_bytes`，不会被静默丢弃或错误转换。

## 协议调试

`mengde_rl` 每次响应都以 `RL` 加制表符开头，后接一行 JSON。引擎日志写到标准错误，不会污染协议。

```text
RESET
STEP 0
ACTIONS
QUIT
```

若某个 MOD 关卡需要玩家手动部署武将，headless 初始化会明确报错。该关卡需要先在 Lua 中提供自动部署配置，或扩展协议加入部署动作。
