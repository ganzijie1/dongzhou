# AINPC 稳定品质闭环

本次增量把 orgFlowEngine 的权威任务结果接入 AINPC 已有的稳定品质系统，并使品质影响下一次东周任职。结果不由 H5 计算或写入。

## 权威链路

1. orgFlowEngine 产生最终 `SUCCESS / PARTIAL / FAILURE`。
2. 东周网关沿独立 outbox 生成 `NPC_QUALITY_SETTLEMENT`，效果号为 `dongzhou-org-quality:<task_id>:v1`。
3. AINPC canonical `POST /api/v1/quality/event-settlement` 由 actor-optional owner 持久结算；同效果号同载荷只返回原结果，不重复加点，异载荷冲突。
4. 下一次拟定任职时，网关读取正式品质档案，按差事计算品行适配并计入胜任度。
5. NexusKernel `dongzhou_mandate_workflow 1.6.0` 将完整档案、适配分和因子封入军令；orgFlow 简报与 H5 官署展示同一值。

## 规则

- 成功 `+2`，部分完成 `+0.5`，失败 `-1`。
- 军需、整训、巡防沉淀担当；情报沉淀信义；外交沉淀公正。
- 不同差事使用不同品质权重。军需重担当、操守、信义并防贪欲与自私；外交重公正、宽容、信义并防虚伪、刻薄与酷烈。
- 品行因子限制为 `-6..+6`，只是胜任度的一部分，不覆盖日程、情绪、人格、动机或主管协同。
- 升级时只扫描已送达且缺少对应品质事件的历史任务，不重新判定任务结果。

## 真实验收

- 上线前左儒担当为 `85`。
- 9 条历史权威结果为 6 次成功、3 次失败，净变化 `+9`；回填后担当为 `94`。
- 网关强制重建后担当仍为 `94`，`updated_at` 未变化，证明回填与 AINPC 效果回执均幂等。
- 无拦截 Chromium 回读军需品行 `59/100 (steady)`、品质因子 `+1.8`、当前胜任度 `67/100`；人物面板显示 `担当 94 · 酷烈 54`。
- 证据：`output/integration-validation/live-quality-loop-complete92.png`。
- 回归：东周 `103 passed, 21 subtests passed`；AINPC 品质模块 `62 passed`；前端系统、组织玩法和集成客户端测试通过。
