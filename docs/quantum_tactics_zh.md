# 量子战术层接入说明

本实现把量子力学作为局部、可选、可验证的战术子系统。原生规则引擎仍负责合法行动、占位、伤害和回合结算；量子层只在观测前保存位置叠加与相干性，并向联合回合规划器提供 Born 概率先验。未配置量子状态的单位与旧关卡行为不变。

## 已实现机制

- `QuantumState`：以密度矩阵统一表示纯叠加和经典混合，并校验厄米性、半正定性与单位迹。
- 幺正演化：接受任意有限维幺正算子，或由厄米 Hamiltonian 自动计算时间演化。
- 格点 Hamiltonian：将四邻接移动写成 tight-binding 耦合，地形势垒写入对角势能。
- 相位与干涉：相位操作不会立即改变位置概率，但会改变后续合流结果。
- 测量与坍缩：使用固定随机种子抽样，完整记录抽样值、前后概率和结果。
- 退相干：相位阻尼保留位置概率，同时衰减密度矩阵非对角元。
- 合法投影：测量前可投影到原生规则给出的合法格，零概率投影会显式失败。
- 隧穿估计：提供有限势垒的 WKB 透射概率，供技能数值设计使用。
- 规划器接入：量子先验只重排现有合法行动，不能生成原生引擎未提供的行动。

## 最小接入方式

```python
from rl.quantum_tactics import QuantumTacticalSystem, lattice_hamiltonian

quantum = QuantumTacticalSystem(seed=2026)
quantum.prepare(unit_id=7, amplitudes={(4, 3): 1.0, (5, 3): 1.0j})

cells = ((4, 3), (5, 3), (6, 3))
hamiltonian = lattice_hamiltonian(
    cells,
    coupling=0.8,
    potentials={(5, 3): 2.0},
)
quantum.evolve(7, hamiltonian, delta_time=0.5)
priors = quantum.action_priors(native_legal_actions)
choice = planner.choose(
    native_legal_actions,
    units,
    width,
    height,
    quantum_priors=priors,
)
```

若运行时环境暴露 `quantum_action_priors(actions)`，`RuntimeBattlePolicy` 会自动读取并叠加该先验，后端名称追加 `+quantum`。环境不提供此方法时不产生额外开销。

## 推荐回合语义

1. 准备：技能创建不超过 8 个格点的局部叠加。
2. 演化：地形势能、道路耦合和相位技能共同作用。
3. 环境：回合末调用 `end_turn(dephasing)`，火焰、侦察区等环境可提高退相干强度。
4. 规划：`action_priors` 依据合法目的格的 Born 概率生成中心化对数先验。
5. 观测：攻击、占点或主动侦察前调用 `observe(unit_id, legal_cells)`。
6. 经典结算：坍缩后的唯一格点交还原生规则引擎处理占位与战斗。

## 设计边界

- 不把全场所有单位放入单一全局波函数。状态维度仅随启用量子技能的局部格点增长。
- 不把量子概率当作新的合法性来源。地图阻挡、友军占位和行动点仍由原生引擎决定。
- 不在观测后保留多个经典实体副本。叠加态是一个单位的一份状态，而不是复制单位。
- 不宣称经典模拟带来量子计算加速。本模块的目标是提供新的战术规则。
- 联机和回放必须同步种子与 `QuantumReplayEvent`；不得使用未记录的随机源。

## 验证

运行：

```powershell
python -m pytest rl/quantum_tactics_test.py rl/joint_turn_planner_test.py
```

测试覆盖归一化、Born 概率、相位干涉、退相干、Hamiltonian 演化、合法投影、固定种子坍缩、隧穿边界、规划器排序和运行时可选接入。
