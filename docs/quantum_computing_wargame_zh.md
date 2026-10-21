# 量子计算战棋优化层实现说明

本实现把联合动作选择编译为一个共享的二元动作模型，并绑定到所有使用
`RuntimeBattlePolicy` 的关卡。CP-SAT、MILP 和 QUBO 使用相同的变量、唯一动作组和时空冲突。它不把经典模拟称为量子加速：真实 QAOA、量子线路模拟器和量子退火器只能通过显式采样接口接入。

## 1. 运行链路

```text
原生规则生成合法动作
  -> HAPPO/CQL + 格点 MFG + 量子格点场评分
  -> 每单位保留有限候选
  -> 编译 one-hot、顶点冲突和时空换位冲突
  -> CP-SAT / MILP / QUBO 求解器组合
  -> 原生动作索引解码
  -> MAPF 预约表再次验证
  -> 执行一个动作后滚动重规划
```

优化器只组合现有合法动作，不能生成移动、攻击或技能。地形、射程、行动点、剧情条件和伤害结算仍由原生规则层掌握。

## 2. QUBO 模型

候选动作 `a` 对应二元变量 `x_a`。对每个单位 `i` 加入唯一动作项：

```text
A * (1 - sum_{a in A_i} x_a)^2
```

路径在同一时刻占据同一格、交换边或最终落点相同时，加入冲突项：

```text
B * x_a * x_b
```

战术评分作为线性收益：

```text
-u_a * x_a
```

惩罚系数由所有单位的效用上界自动确定，并严格大于违反约束可能获得的收益。最终解还要经过 `SpaceTimeGrid` 复核，因此错误的量子样本不能绕过合法性检查。

实现位于：

- `rl/quantum_optimization.py`：QUBO 编译、能量计算、可行性验证和求解器。
- `rl/classical_optimization.py`：真实 OR-Tools CP-SAT、SciPy/HiGHS MILP 与后端组合。
- `rl/joint_turn_planner.py`：联合动作评分后调用优化层，再用 MAPF 预约表复核。
- `rl/runtime_policy.py`：默认对所有关卡启用，并在后端状态中显示实际求解器。

## 3. 默认求解器组合

- `cp-sat-optimal` / `cp-sat-feasible`：OR-Tools CP-SAT，直接处理唯一动作和互斥约束。
- `milp-optimal` / `milp-feasible`：SciPy/HiGHS MILP，使用二元变量和显式线性约束。
- `qubo-exact`：变量数和组合数在安全上限内时，枚举每单位一个动作的笛卡尔积，得到可复核的全局最优解。
- `qubo-bounded`：问题较大时执行确定性的有界分支搜索，限制节点数量，避免阻塞回合。
- `qubo-mapf-fallback`：QUBO 编译、外部采样或解码异常时，回退到原联合 MAPF 贪心流程。

默认自动顺序是：

```text
CP-SAT -> MILP -> QUBO -> MAPF
```

前一个后端缺失、超时、无可行解或验证失败时才会进入下一个后端。`used_fallback` 和 `backend_error` 会记录降级原因。

运行时的 `policy.backend` 会显示实际链路，例如：

```text
joint-mapf+happo+mfg+quantum+cp-sat-optimal
```

可以固定后端进行消融：

```python
cp_sat = RuntimeBattlePolicy(optimization_backend="cp-sat")
milp = RuntimeBattlePolicy(optimization_backend="milp")
qubo = RuntimeBattlePolicy(optimization_backend="qubo")
```

## 4. 接入 QAOA 或量子退火器

外部后端只需接收 `TacticalQUBO` 并返回变量到 0/1 的映射。下面的示例只说明接口，不假定具体 SDK：

```python
from rl.quantum_optimization import SampledQUBOSolver, TacticalQUBOOptimizer
from rl.runtime_policy import RuntimeBattlePolicy

def sample_with_backend(model):
    # model.linear、model.quadratic 和 model.offset 可转交给
    # QAOA、量子线路模拟器或量子退火 SDK。
    # 返回一个样本，或按质量排序的多个样本。
    return [{0: 1, 1: 0, 2: 1}]

solver = SampledQUBOSolver(sample_with_backend, name="qaoa")
optimizer = TacticalQUBOOptimizer(external_solver=solver)
policy = RuntimeBattlePolicy(qubo_optimizer=optimizer)
```

外部样本必须满足：

- 每个参与单位恰好选择一个动作；
- 不包含顶点、落点或换位冲突；
- 变量编号属于当前 QUBO；
- 解码后仍能通过现有 MAPF 预约表。

若所有样本都无效、后端抛出异常或返回空结果，系统自动使用经典求解器。可通过
`policy.planner.last_optimizer_solution.used_fallback` 和 `backend_error` 检查是否发生后端回退。

## 5. 全关卡绑定与关闭方式

`RuntimeBattlePolicy` 默认启用自动求解器组合，因此使用该策略的旧关卡和新关卡不需要复制配置。地图和剧本只负责提供原生单位与动作。

调试或消融时可以关闭：

```python
policy = RuntimeBattlePolicy(enable_qubo_optimizer=False)
```

关闭后恢复原联合 MAPF 选择逻辑，后端名称不追加优化器名称。参数名保留 `enable_qubo_optimizer` 是为了兼容已经存在的调用。

## 6. 与现有量子模块的关系

- `quantum_tactics.py` 表达局部量子态、测量、退相干和格点 Hamiltonian。
- `quantum_lattice_field.py` 表达局部 Bose-Hubbard 场及其与格点 MFG 的耦合。
- `quantum_optimization.py` 负责多单位联合动作的 QUBO 组合优化。

三者职责不同。量子态和量子格点场给动作提供先验，QUBO 层组合动作，原生规则和 MAPF 保证可执行性。

Grover 搜索、量子振幅估计和参数化量子策略尚未直接放进逐帧运行时。当前引擎没有低成本可逆 oracle 或状态制备线路，硬接入只会把经典工作隐藏在量子接口后面。后续只有在实现可计量的 oracle、门数、shots、端到端延迟和经典基线后才应启用。

## 7. 验证

```powershell
python -m pytest rl/quantum_optimization_test.py `
  rl/classical_optimization_test.py `
  rl/joint_turn_planner_test.py `
  rl/lattice_field_runtime_test.py `
  rl/quantum_tactics_test.py `
  rl/quantum_lattice_field_test.py -q
```

覆盖：

- one-hot、落点、顶点和换位冲突编码；
- 全局最优非冲突动作组合；
- 非法 QAOA 样本拒绝和经典回退；
- 合法外部量子样本解码；
- 大问题自动切换有界后端；
- CP-SAT、MILP 和 QUBO 在同一实例上的最优解一致性；
- CP-SAT 失败后真实转入 MILP 的降级链；
- 所有关卡的默认运行时绑定；
- 既有 MAPF、MFG、量子战术和量子格点场回归。
