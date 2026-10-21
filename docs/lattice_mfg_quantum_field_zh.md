# 格点 MFG 与量子格点场实现说明

本实现增加两个彼此独立、也可双向耦合的战术层：

- `rl/lattice_mfg.py`：有限图上的离散时间平均场博弈。
- `rl/quantum_lattice_field.py`：小型局部战区上的截断玻色 Fock 场。

两层都只为原生合法动作生成先验。地形、占位、攻击、回合顺序和 MAPF 仍由现有规则处理。

## 1. 格点 MFG

`LatticeMFG` 求解熵正则的反向 Bellman 方程和前向 Kolmogorov 方程：

```text
预测密度 -> 反向价值/策略 -> 前向密度 -> 松弛更新 -> 自洽残差
```

已实现：

- 任意有限有向图和矩形格点构造；
- 不可通行格、方向边和地形移动成本；
- 等待动作、局域容量、幂次拥堵成本；
- 零温确定性策略与有限温 softmax 策略；
- 质量非负性、质量守恒和策略行归一化检查；
- 密度、价值、边通量和自洽残差输出；
- 非对称多兵种外层固定点；
- 将下一时刻 continuation value 转换为逐单位、中心化的合法动作先验，支持单回合跨越多条格点边的原生移动。

最小示例：

```python
from rl.lattice_mfg import LatticeMFG, LatticeMFGConfig

model = LatticeMFG.from_grid(
    12,
    8,
    movement_costs=costs,
    config=LatticeMFGConfig(horizon=8, congestion_weight=2.0),
)
result = model.solve(initial_density, terminal_cost)
priors = result.action_priors(native_actions, units)
```

`result.converged` 只在固定点残差达到容差时为真。生产环境不得忽略未收敛状态；可降低松弛系数、增加熵正则或缩短滚动时域。

## 2. 量子格点场

`BosonicLatticeField` 构造每格最大占据数有限的 Fock 空间。其 Hamiltonian 是带 Peierls 相位的 Bose-Hubbard 模型：

```text
跃迁 + 局域相互作用 + 地形势能 + MFG 密度势能
```

已实现：

- 截断玻色占据基底；
- 局域产生、湮灭和数算符；
- Bose-Hubbard 跃迁与局域相互作用；
- 有向边规范相位，Hamiltonian 保持厄米；
- 精确有限维幺正演化；
- Fock 数基底退相干；
- 期望占据数、总粒子数、归一化场强；
- 量子场强到合法动作先验的转换；
- 在分配内存前检查 Fock 维度上限。

维度为：

```text
(max_occupancy + 1) ** cell_count
```

因此它只适合局部精确战区。默认上限是 4096。大地图应使用复平均场或经典格点场，不能提高上限来掩盖指数增长。

最小示例：

```python
from rl.quantum_lattice_field import BosonicLatticeConfig, BosonicLatticeField

field = BosonicLatticeField(
    cells=((4, 3), (5, 3), (6, 3)),
    amplitudes={(1, 0, 0): 1.0},
    config=BosonicLatticeConfig(max_occupancy=2, hopping=0.8),
)
field.evolve(0.2, gauge_phases={((4, 3), (5, 3)): 0.5})
```

## 3. 双向耦合

`LatticeMFGQuantumCoupler` 实现：

```text
MFG 密度 -> 量子局域势 -> 量子占据 -> MFG 外部成本 -> 新 MFG 密度
```

`density_to_potential` 控制人群对量子场的势能作用；`quantum_to_cost` 控制量子占据对群体决策的吸引或排斥。正值表示排斥成本，负值表示吸引收益。

```python
from rl.quantum_lattice_field import LatticeMFGQuantumCoupler

coupled = LatticeMFGQuantumCoupler(
    model,
    field,
    density_to_potential=0.5,
    quantum_to_cost=0.75,
)
solution = coupled.solve(initial_density, terminal_cost)
```

输出同时包含 MFG 解、逐时刻量子占据、最终量子场、自洽残差与收敛标记。

## 4. 运行时接入

`LatticeFieldPolicyAdapter` 包装现有环境，不修改环境对象：

```python
from rl.quantum_lattice_field import LatticeFieldPolicyAdapter

runtime_env = LatticeFieldPolicyAdapter(
    env,
    mfg_result=solution.mfg,
    quantum_field=solution.final_field,
)
choice = runtime_policy.choose(runtime_env, actions, observation, width, height)
```

运行时策略按顺序组合：

```text
HAPPO/CQL 模型先验 + MFG 先验 + 量子场先验
-> CP-SAT / MILP / QUBO 联合动作优化 -> MAPF 合法性复核
```

后端状态会显示 `+mfg`、`+quantum` 和实际优化后端。若提供器返回非法动作编号、非有限数或非映射，运行时会禁用该提供器，并继续使用原有规划器。CP-SAT、MILP、QUBO、外部 QAOA/退火采样器和回退规则见 `docs/quantum_computing_wargame_zh.md`。

## 5. 验证

```powershell
python -m pytest rl/lattice_mfg_test.py rl/quantum_lattice_field_test.py rl/quantum_tactics_test.py rl/quantum_optimization_test.py rl/joint_turn_planner_test.py -q
```

覆盖内容包括：

- HJB–Kolmogorov 质量守恒与固定点残差；
- 障碍、确定性极限、多兵种和动作先验；
- Fock 维度、产生/湮灭、粒子数守恒和厄米性；
- 规范相位、退相干和指数维度防护；
- MFG—量子场双向耦合；
- 联合规划器与运行时适配器；
- QUBO 编译、全局动作组合、外部采样验证与经典回退；
- 既有量子战术和 MAPF 回归。
