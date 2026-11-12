# 官署结果到 NPC 动机闭环

## 目标

orgFlowEngine 的权威任务终态不再只形成经历和品质，也会形成下一次任职可读取的任务意愿。成功、部分完成、失败分别增加 `8 / 18 / 30` 点；失败增量更高，表示未竟事项的紧迫驱动力，不代表奖励。

## 所有权与顺序

- 东周网关以稳定操作号 `dongzhou-org-motivation:<task_id>:v1` 调用 AINPC 正式动机接口。
- `NPC_TASK_OUTCOME` 仍进入 AINPC 的情绪、关系、认知和记忆流水线，但携带 `motivation_policy=external_authoritative`，其异步认知不得再次改写本次权威动机。
- AINPC 仍为该认知建立独立持久操作和完成记录，只是动机更新列表为空；其他认知效果不受影响。
- 如果 orgFlow 已先于本地月令给出终态，网关读取 `pendingSettlement.result`、`pendingReview.review.finalResult` 或 NexusKernel 封印的 `review.finalResult`，立即进入复命，不再要求任务仍为 `active` 或等到到期月。
- 普通未终态任务仍受原到期月约束；历史任务不批量回填动机，避免升级时触发意外自主行为。

## 真实验收

- 第一笔任务 `7f37db10-d85b-5aea-8cb3-5c9e049750ad` 暴露了异步认知覆盖问题：显式 `+8` 后，旧认知操作将同名动机调回 `0`，据此补上所有权契约。
- 修复后任务 `78bd9bb3-5cfd-571a-8359-30c20cc8a33f` 权威结果为 `SUCCESS`。五条 outbox 均一次送达；显式操作把“再办军粮转运”从 `0` 写为 `8`。
- 12 秒后，AINPC 的 `event_report:dongzhou-org-outcome:<task_id>` 认知操作正常完成，整张动机表保持不变。
- 重建全部 8 个 AINPC 容器后，同一任务重放前后仍为 `8`。全局动机修订号可被其他合法操作推进，不作为本结算的幂等判据。
- 浏览器证据：`output/integration-validation/live-motivation-authority-complete94-motivation.json` 和同名 PNG。

## 验证

- 东周集成服务：`104 passed, 21 subtests passed`。
- 网页玩法：`test-game-systems.js`、`test-organization-play.js`、`test-integration-client.js` 全部通过。
- AINPC 新增权威动机测试通过；完整动机目录为 `184 passed, 18 skipped, 3 failed`。三个失败均为现有测试桩未跟随 cognition repository 和 recovery handler 参数变化，与本次策略无关。
