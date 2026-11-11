# 东周四服务玩法覆盖矩阵

本矩阵记录 2026-11-12 本机完整联网版的当前边界。范围是四个仓库中与东周玩家流程直接相关的能力，不把通用管理后台、监控和其他游戏协议误列为东周玩法。

## 覆盖结果

| 来源 | 东周服务契约 | 玩家入口 | 权威结果 | 真实证据 |
| --- | --- | --- | --- | --- |
| knowledge-jizhan | 全文检索、按关卡读取已发布 AKU、战役路线、玩家简册 | 查阅、本回史料、选定出处、已得简册、行军路线 | 只接收 `dongzhou_stage_*`；出处和检索回执进入军议与军令 | `test-live-knowledge-browser.js`、`test-live-fulltext-browser.js`、`test-live-campaign-route-acceptance.js`、`verify-live-knowledge-campaign.py`、`live-integration-complete62.json` |
| AINPC | NPC 注册与上线、主动来信偏好、状态/人格/动机/关系、双向私聊、90 天日程、关卡当值、军议裁断、玩家本人领差/响应/复命、急报评估 | 官署状态、府中书问、来信开关、拟定日程、本关当值、军议裁断、我的差事 | 稳定 NPC/玩家身份；固定事务命令进入组织 Actor；回复回调落库后展示；计划、事件、人格、意愿、关系和急报封入军令 | `verify-live-roster-npcs.py`、`test-live-office-npc-state.js`、`test-live-correspondence-acceptance.js`、`test-live-interaction-preference.js`、`test-live-schedule-browser.js`、`test-live-player-career-browser.js`、`test-live-kernel-mandate-acceptance.js` |
| orgFlowEngine | 权威名册、玩家入仕/辞仕、组织谱系、贡献账、公共库藏、虚拟任务、玩家本人任务申请、任务终态、人工复命审核 | 个人仕籍、我的差事、直属主管、贡献收支、库藏、军需调拨、颁差、推进月令、收纳复命/申斥 | 岗位候选、任务候选、责任人响应、直属审核、贡献、功绩和结案凭据均以 orgFlow 为准；验收奖励进入 `task.execution` 实账，玩家可按 20 点一批调拨为 12 军粮；12 席均进入可操作官员集合，负责人不可向自己派单 | `test-live-membership-browser.js`、`test-live-player-career-browser.js`、`live-player-career-browser.json`、`test-live-roster-ledger.js`、`test-live-office-roster-browser.js`、`test-live-office-inventory.js`、`test-live-inventory-requisition.js`、`test-live-office-acceptance.js`、`test-live-settlement-acceptance.js` |
| NexusKernel | 运行模块健康、规范军令、确认动作、恢复签发、终态复命裁决、公共资源支出裁可 | 内核军令草案、签发/驳回、复命待裁、军需调拨待裁、军令簿 | 史料、军议、书问、当值、急报、适岗证据和军需支出统一 SHA-256 封存；确认动作可恢复，未签发或驳回的调拨不扣库 | `test-live-kernel-mandate-acceptance.js`、`resume-live-kernel-mandate-acceptance.js`、`test-live-mandate-mobile.js`、`test-live-settlement-acceptance.js`、`test-live-inventory-requisition.js` |

## 跨服务闭环

联网授命必须依次取得已发布史料、当前属官裁断、AINPC 当值与状态、NexusKernel 军令，再由 orgFlowEngine 受理。任务终态先形成 orgFlow 结案实账，再由 NexusKernel 生成玩家裁决，随后将结果写回 AINPC 重要事件和长期经历，最后作为战前助益进入战斗。缺少任一服务确认时不会在浏览器本地伪造成功。

复命被接纳后，组织贡献同时以 `TASK_SETTLEMENT_ACCEPTED` 原因进入 orgFlow 公共库藏。玩家申请调拨 20 点 `task.execution` 时，NexusKernel 先封存支出草案；玩家签发后 orgFlow 才以 `CAMPAIGN_REQUISITION_APPROVED` 权威扣账，东周再依据已验证收据补入 12 军粮，驳回则零支出。内核动作、请求号、扣账和云存档均可回放，页面刷新或中断恢复不会替玩家自动签发，也不会重复扣领或重复加粮。

玩家本人仕途是独立的权威闭环：先由 orgFlow 写入 `officer_12` 仕籍，再通过 AINPC 与直属杜伯查询本人岗位目录、按名称申请、调阅待办、接受和复命；orgFlow 校验每一步并在杜伯审核通过后结算贡献。浏览器只展示 AINPC 回信和 orgFlow 名册回读，不自行创建任务或增加贡献。

当前无拦截完整任务证据为：

- `live-kernel-mandate-complete44-evidence.json`：史证适配、签令、派差、复命和战斗承接。
- `live-authoritative-settlement.png`：贡献、功绩、结案摘要、NPC 事件和长期经历一致。
- `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json`：知识、军议、外交军令、游说、盟约门禁和云档恢复。
- `live-player-career-browser.json`：玩家请仕、可领目录、按名称领差、待办、受命、复命、直属审核和贡献 `0 -> 100`。

## 当前验证基线

- 网关：`87 passed`，另有 `21 subtests passed`。
- 前端：集成客户端、组织玩法、战斗系统、官署浏览器、军议浏览器和外交浏览器全部通过。
- 真实冒烟：四项能力在线；独立访客存档往返、版本冲突和玩家隔离通过；172/172 关已发布史料、171/171 条连续行军路线通过；172 关共有 184 条分层出处，其中 160 关使用明确标注的《东周列国志》文学底本边界；左儒计划为 90 天、436 项东周事务。
- 权威名册：12/12 NPC 状态与 90 天计划通过；真实浏览器逐席显示心境、关系、性情、动机与日程，杜伯可调阅但不可向自己派单。
- 玩家仕途：真实浏览器无拦截完成 `officer_12` 入仕、`Intelligence mission` 受命与复命，杜伯审核通过后贡献余额从 `0` 增至 `100`，测试结束辞仕并释放席位。
- 军需调拨：真实浏览器无拦截证明草案阶段零扣款、NexusKernel 签发后公共库藏 `60 -> 40`、军粮 `100 -> 112`、驳回零扣款；云档重载保持一致，同一请求回放不重复扣领。
- 本地交付：网关、AINPC、orgFlow 和九个依赖容器均符合镜像、健康与 `unless-stopped` 约束；完整 H5 包哈希通过；检查过程业务写入为 0。

## 非玩法边界

公网 TLS、可信回调网络和 Windows 宿主冷启动属于部署验收，不由浏览器玩法测试代替。公共库藏只接受 orgFlow 的结案奖励与签名调拨，不人工播种资源；余额不足时明确拒绝。模型或上游服务不可用时保持明确失败，不静默切换本地伪结果。
