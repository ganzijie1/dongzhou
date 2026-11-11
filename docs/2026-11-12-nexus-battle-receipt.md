# NexusKernel 战果封存（complete83）

## 目标

战斗结果不能再仅凭浏览器战报直接改变 AINPC 权威状态。`complete83` 在云存档提交阶段增加 NexusKernel 战果封存：服务端先核对战前已提交的议事、军令、组织任务和待用支援，再生成不可由本次请求覆盖的战果印记。

## 数据流

1. 战前存档保存 `councils`、`mandates`、`tasks` 与 `pendingSupport`。
2. 战后存档提交新战报，服务端只接受能回溯到上一版本存档的支援引用。
3. NexusKernel `dongzhou_mandate_workflow@1.3.0` 生成 `kernelReceipt`，其中包含战报摘要、已验证参战者、已验证支援、内核版本和 SHA-256 摘要。
4. AINPC 战果事件只读取 `kernelReceipt.verifiedParticipants`，不再读取浏览器原始 councils、mandates 或 orders 来确定参战 NPC。
5. 同一战报再次保存时必须保持战果和支援引用不变，否则返回 `409 battle_report_changed_after_seal`。
6. 云端返回印记后，H5 立即合并回本地存档，并在官署历史档案显示“内核战果印记”。

## 安全边界

印记证明战果经过服务端校验并与上一版已提交存档中的支援链一致，可阻止单次伪造战报、替换参战者和封存后篡改。它不等同于对所有更早客户端数据的密码学背书；需要更强对抗安全时，应继续把议事和组织任务凭据改为仅由相应服务端接口签发并在数据库中独立核验。

## 验证

- 集成服务：`93 passed, 21 subtests passed`。
- 客户端：集成客户端、组织玩法和 JavaScript 语法检查通过。
- 真实浏览器：无 API 拦截，完成战前支援存档、战后封存、AINPC 情绪更新和官署印记显示。
- 证据：`output/integration-validation/live-battle-receipt-complete83.json` 与同名 PNG。
- 部署镜像：`dongzhou-integration:20261112-local-complete83`。
