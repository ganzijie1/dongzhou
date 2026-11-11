# NexusKernel 战果封存（complete85）

## 目标

战斗结果不能仅凭浏览器战报改变 AINPC 权威状态。`complete85` 在云存档版本链校验之外，继续回查集成服务数据库里的真实议事、军令和 orgFlow 终局任务记录，再生成不可由本次请求覆盖的战果印记。

## 数据流

1. H5 发起议事时把 `stage_id` 写入真实 `npc_decision` 请求，使议事人和关卡同时受服务端记录约束。
2. 战前存档保存 `councils`、`mandates`、`tasks` 与 `pendingSupport`；orgFlow 任务终局读取时，服务端缓存权威 settlement 与 closure receipt。
3. 战后存档提交新战报，服务端先校验上一版本存档引用，再分别回查 `npc_decision`、`court_mandate` 和 `organization_task` 服务端记录。
4. NexusKernel `dongzhou_mandate_workflow@1.4.0` 生成 `kernelReceipt`，其中包含战报摘要、已验证参战者、已验证支援、未认证引用、内核版本和 SHA-256 摘要。
5. AINPC 战果事件只读取 `kernelReceipt.verifiedParticipants`，不再读取浏览器原始 councils、mandates 或 orders 来确定参战 NPC。
6. 没有服务端凭据的引用进入 `rejectedSupport`，不阻断战斗存档，但不能触发 NPC 权威事件。
7. 同一战报再次保存时必须保持战果和支援引用不变，否则返回 `409 battle_report_changed_after_seal`。
8. 云端返回印记后，H5 立即合并回本地存档，并在官署历史档案显示认证人数与未认证数量。

## 安全边界

印记现在同时证明引用存在于上一版存档，并对应当前玩家的服务端接口记录。议事必须为当前英雄、当前关卡的已完成 AINPC 决策；军令必须为已签发且摘要一致的 NexusKernel 军令；参战任务必须对应 orgFlow 成功或部分成功的权威 settlement 和一致的 closure receipt。纯客户端预埋数据会被排除。

## 验证

- 集成服务：`96 passed, 21 subtests passed`。
- 客户端：集成客户端、组织玩法和 JavaScript 语法检查通过。
- 真实浏览器：无 API 拦截，完成战前支援存档、战后封存、AINPC 情绪更新和官署印记显示。
- 证据：`output/integration-validation/live-battle-receipt-complete85.json` 与同名 PNG。
- 部署镜像：`dongzhou-integration:20261112-local-complete85`。
