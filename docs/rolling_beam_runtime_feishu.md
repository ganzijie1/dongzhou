# 东周战斗中的滚动 Beam 规划器

> 实现与实验日期：2026-09-06
>
> 适用代码：`D:\dongzhou`
>
> 运行链：Rolling Beam 主策略 -> HAPPO 回退 -> CQL 回退 -> 安全待机

## 1. 结论

当前原生战斗引擎没有毫秒级的 `clone/undo`。用真实进程为 MCTS 的每个节点重放历史，会使后半局的代价随历史长度增长。项目因此采用轻量、可复制的数值状态和滚动 Beam Search：搜索若干个短动作序列，只把首个原生合法动作交给游戏执行，下一决策点重新读取权威状态。

这不是“用手写规则替换学习模型”。Rolling Beam 是当前无需训练数据的主策略；已有 HAPPO 和 CQL 仍作为规划器异常或输入不兼容时的回退。原生引擎继续负责合法动作枚举和实际结算。

## 2. 为什么选择 Rolling Beam

设动作分支数为 \(A\)，时域为 \(H\)，随机场景数为 \(K\)，Beam 宽度为 \(B\)。完整 Expectimax 的展开量近似为

```latex
O\!\left(KA^H\right),
```

而滚动 Beam 的展开量约为

```latex
O\!\left(KHBA\right).
```

当前发布配置为

```latex
H=2,\qquad B=6,\qquad A_{\max}=10,\qquad K=3.
```

它保留两名连续行动单位之间的短期组合，又避免完整树搜索。MCTS 更适合拥有快速内存快照、廉价转移和大量模拟预算的环境；当前引擎的进程级恢复不满足这个条件。Beam Search 还能直接利用原生合法动作排序、动作支配剪枝和确定性的风险场景，行为更容易复现。

## 3. 权威边界

规划器不自行发明动作。每次决策读取原生进程返回的集合

```latex
\mathcal A_t=\operatorname{NativeLegalActions}(s_t),
```

并保证最终动作满足

```latex
a_t^*\in\mathcal A_t.
```

原生动作元数据现包含：

- 基础攻击和技能的伤害、治疗、命中率及 MP 消耗；
- 基础攻击的暴击、连击、反击伤害和反击命中率；
- 技能是否针对敌方、是否属于纯属性效果；
- 移动后所处地形对应的攻击伤害，而不是错误沿用移动前地形。

真实命中、伤害、脚本事件、地形和胜负仍由 C++ 引擎结算。轻量模型只用于比较候选，不替代权威规则。

## 4. 轻量随机模型

每个候选序列复制 \(K\) 个纯数据状态。对命中、暴击和连击使用确定性的分层分位点，而不是每次搜索重新抽随机数。第 \(k\) 个场景的基础分位点为

```latex
q_k=\frac{k+1/2}{K},\qquad k=0,\ldots,K-1.
```

不同随机事件使用互异的固定偏移，既覆盖有利和不利结果，又保证相同输入得到相同计划。

单步近似奖励与原生训练环境一致：

```latex
r_t=-0.01
+2\Delta N_{\mathrm{enemy-dead}}
-2\Delta N_{\mathrm{own-dead}}
+\frac12\left(\Delta HP_{\mathrm{enemy}}-\Delta HP_{\mathrm{own}}\right)
+r_{\mathrm{terminal}}.
```

对手响应由可替换接口提供。当前默认模型计算敌方下一回合内可达的基础攻击，并选择其最有威胁的目标。它是显式近似，不读取未来信息，也不声称等价于完整对手策略。

## 5. 风险选择

对场景回报 \(R_1,\ldots,R_K\)，规划器计算均值和下尾 CVaR。令升序统计量为 \(R_{(i)}\)，则

```latex
\operatorname{CVaR}_{\alpha}(R)
=\frac{1}{m}\sum_{i=1}^{m}R_{(i)},
\qquad
m=\max\left(1,\left\lceil\alpha K\right\rceil\right).
```

当前 \(\alpha=0.25\)。候选先比较己方全灭概率和击败敌方概率，再比较 CVaR、均值、位置改善和资源保留。这样不会用平均高收益掩盖明显的暴毙分支。

## 6. 剪枝

搜索依次执行：

1. 删除单位已死亡、已行动、目标死亡或目的格被占用的动作。
2. 按“动作类型、技能、目的格、目标”合并完全重复动作。
3. 每个单位至少保留不同动作类型和技能的代表，避免纯按即时伤害剪掉治疗或移动。
4. 使用轻量状态键合并位置、HP、MP、行动和死亡状态相同的节点。
5. 每层只保留前 \(B\) 个节点。

搜索完成后只执行序列首项：

```latex
(a_t^*,a_{t+1},\ldots)
\longmapsto
\operatorname{ExecuteNative}(a_t^*).
```

其余项只是当前预测，不会机械排队执行。

## 7. 运行时回退

运行顺序是：

```text
Rolling Beam
  -> 输入或模型不兼容：HAPPO
  -> HAPPO 模型缺失/损坏：CQL
  -> CQL 也不可用：当前单位安全待机
```

规划器异常被记录在 `planner_error`，不会导致前端战斗直接退出。HAPPO/CQL 的既有代码和模型格式没有被删除。

## 8. 同种子基准

基准使用 `example` 战场、10 个完全相同的初始随机种子、相同的 80 动作上限；己方使用既有稳定脚本，对比完整 Rolling Beam 与单步、单场景、无对手响应的规划基线。

| 策略 | 敌方胜率 | 敌方平均回报 | 平均动作数 | 敌方攻击率 | 平均规划耗时 | P95 耗时 |
|---|---:|---:|---:|---:|---:|---:|
| Rolling Beam | 0% | -21.4882 | 31.3 | 14.01% | 33.47 ms | 51.97 ms |
| 单步基线 | 0% | -22.1780 | 32.2 | 6.00% | 1.70 ms | 2.23 ms |

Rolling Beam 在这组种子上提高了攻击率并改善了平均回报，但没有取得胜局。因此当前证据只支持“搜索链路有效且比单步基线更积极”，不能支持“已经超过训练好的 HAPPO”或“已经达到最优策略”。后续若要做部署优劣结论，必须补齐同一批多关卡种子下的 HAPPO/CQL 检查点对比。

原始结果保存在 `docs/rolling_beam_benchmark.json`。

## 9. 复现命令

```powershell
cmake -S . -B build\rl-vcpkg -G "Visual Studio 18 2026" -A x64 `
  "-DCMAKE_POLICY_VERSION_MINIMUM=3.5" `
  "-DCMAKE_TOOLCHAIN_FILE=C:/Program Files (x86)/Microsoft Visual Studio/18/BuildTools/VC/vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build\rl-vcpkg --config Release --target mengde_rl -j 4
python -m rl.rolling_beam_test
python -m rl.runtime_policy_test
python -m rl.runtime_frontend_policy_test
python -m rl.compare_rolling_beam --episodes 10 --max-episode-actions 80 `
  --output docs\rolling_beam_benchmark.json
```

## 10. 后续边界

- 当前前向模型只覆盖公开动作元数据和常规击杀目标；特殊关卡脚本目标仍由真实执行后的滚动反馈纠正。
- 当前对手模型只做一步可达基础攻击，不等同于 Expectimax 的完整敌方策略树。
- 属性类技能已显式标记，规划器不会再把高 `power` 的纯减益技能误当成直接伤害。
- 若未来原生引擎提供廉价内存 `clone/undo`，可在相同接口下加入 MCTS/Expectimax，并用同种子协议重新比较。
