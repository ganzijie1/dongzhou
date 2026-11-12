# AINPC 军议旧事闭环

complete98 把东周军议选择从“已归档”继续推进到 AINPC 正式短期记忆。任务对话归档成功后，网关用同一稳定来源号写入 `short-term-memory` owner；重试复用冻结裁断，事实幂等键保证不会形成重复旧事。

官署人物页显示最近旧事，玩家可选一条作为下一轮军议依据。旧事引用包含稳定幂等键和 SHA-256 印记，不采用浏览器自报内容。

验证链分为两层：

1. AINPC 作出新裁断前，网关反查该 NPC 最近记忆，核验幂等键、完整印记和议题中的印记标记。
2. NexusKernel 签发军令前再次反查当前记忆，同时核验本轮对话自身已经进入记忆库；通过后将选用旧事写入 `dongzhou_mandate_workflow 1.7.0` 军令印记。

任务对话先成功、记忆写入暂时失败时，请求进入 `RETRYABLE`；再次提交不会重新选择方案。

验证结果：

- 集成服务全量测试：108 passed，21 subtests passed。
- 网页状态机：`test-game-systems.js`、`test-organization-play.js`、`test-integration-client.js` 全部通过。
- 完整用例覆盖首轮军议形成旧事、属官状态返回印记、次轮军议引用旧事、NexusKernel 军令再次核验并封存。
