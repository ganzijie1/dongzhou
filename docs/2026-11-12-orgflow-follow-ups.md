# orgFlow 权威追办与补救任务（complete86）

## 玩家闭环

组织差事结案后不再停在一次性奖励。orgFlowEngine 的东周目录 v4 根据原任务类型和权威终局生成下一项工作：成功生成 `FOLLOW_UP` 追办，部分完成生成 `FOLLOW_UP`，失败生成 `REMEDIATION` 补救。外交、操练、谍报、巡察和军需五类差事都有明确的跨类型去向，且不会把任务重新派给自身类型。

派生任务只允许一层。orgFlowEngine 持久化规则号、触发结果、前序任务、根任务、代数、计划任务号和实际任务号；东周网关逐项复核这些字段、岗位和目标默认值，不能由浏览器伪造派生关系。

## 东周承接

网关将已创建的派生任务登记到原玩家名下，继承原章节和岗位席位，成本为 0，不重复签发军令，也不重复扣除资源。若同一席位的实际责任人在执行期间调整，网关按 orgFlow 当前 `responsible_member_id` 反查并同步东周人物，结算不沿用过期的父任务执行人。浏览器任务簿显示“追办”或“补救”，按普通 orgFlow 任务继续轮询、结案和发奖。存在待创建的派生意图时，推进月令会被阻止，避免跨月丢失追办。

NexusKernel 模块版本提升为 `dongzhou_mandate_workflow@1.5.0`，用于标识包含派生任务承接的集成契约；complete85 的战果封存仍保持其历史 `1.4.0` 记录。

## 真实服务验收

- 父任务：`c294a867-8ab1-5b63-9787-3d3e0a8419a0`，终局 `SUCCESS`。
- 派生意图：`5d2f2480-cc9e-5adc-b333-26f01ddab540`，规则 `dongzhou_supply_success_follow_up`。
- 子任务：`3a5c0216-1a98-5bd7-9b5a-eaf5176b2712`，类型 `patrol`，代数 1；验收期间从 `IN_PROGRESS` 进入权威终局 `FAILURE`。
- 浏览器回读确认子任务与父任务处于同一章节、同一岗位席位，成本为 0，并保留前序任务和规则号；责任人变化后按 orgFlow 实际责任人显示和校验。
- 证据：`output/integration-validation/live-orgflow-followup-complete86.json`、`live-orgflow-followup-lineage-complete86.json` 和同名 PNG。

验收期间发现 AINPC 当值窗口和同一对话双方的私聊租约会正确阻止派差。测试仅对指定 NPC 临时启用当值调试并通过正式运行时接口清理该精确会话租约；验收后已移除调试规则并用原编排重建服务，没有把调试覆盖写入仓库。

## 回归入口

- orgFlow 目录：`tests/scripts/test_publish_dongzhou_catalog.py`
- 网关所有权与路由：`integration-service/tests/test_core.py`、`integration-service/tests/test_court_mandates.py`
- 浏览器状态机：`tools/test-organization-play.js`
- 真实服务与浏览器：`tools/test-live-orgflow-followup.js`
