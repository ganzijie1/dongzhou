# 东周四服务玩法覆盖矩阵

本矩阵记录 2026-11-12 本机完整联网版的当前边界。范围是四个仓库中与东周玩家流程直接相关的能力，不把通用管理后台、监控和其他游戏协议误列为东周玩法。

## 覆盖结果

| 来源 | 东周服务契约 | 玩家入口 | 权威结果 | 真实证据 |
| --- | --- | --- | --- | --- |
| knowledge-jizhan | 全文检索、按关卡读取已发布 AKU、战役路线、玩家简册、知识竞赛 | 查阅、本回史料、选定出处、已得简册、行军路线、史官问对 | 只接收 `dongzhou_stage_*`；出处和检索回执进入军议与军令；相邻关卡路线必须同时通过战役推进、定点和 NPC 对话三种图谱查询；问对题目从当前已发布 AKU 人物录生成，30 秒内答中记 10 分 | `test-live-knowledge-browser.js`、`test-live-fulltext-browser.js`、`test-live-campaign-route-acceptance.js`、`test-live-knowledge-quiz.js`、`verify-live-knowledge-campaign.py`、`campaign-routes-desktop-live.png`、`campaign-routes-mobile-live.png`、`knowledge-quiz-live.png` |
| AINPC | NPC 注册与上线、主动来信偏好、状态/人格/动机/稳定品质/关系、双向私聊、90 天日程、关卡当值、自主念头、军议裁断、已签军令临时插程、玩家本人领差/响应/复命、急报评估、参战结果与长期经历 | 官署状态、品质与品行、府中书问、来信开关、拟定日程、本关当值、请其进言、军议裁断、签发后下达、我的差事、官署战报 | 稳定 NPC/玩家身份；orgFlow 终态以稳定效果号沉淀品质并影响下一次任职；进言读取当前当值、动机与史料并真实触发动机路由；已签军令经日程 owner 裁定为今日插程、后续排程或拒绝，并形成独立防篡改回执；实际参战属官收到幂等的重要事件和长期系统消息，战果以服务器权威标准语义驱动即时情绪 | `verify-live-roster-npcs.py`、`test-live-office-npc-state.js`、`test-live-quality-loop.js`、`test-live-spontaneous-thought.js`、`test-live-correspondence-acceptance.js`、`test-live-interaction-preference.js`、`test-live-schedule-browser.js`、`test-live-player-career-browser.js`、`test-live-kernel-mandate-acceptance.js`、`test-live-battle-memory.js`、`test-live-battle-emotion.js` |
| orgFlowEngine | 权威名册、玩家入仕/辞仕、组织谱系、贡献账、公共库藏、虚拟任务、玩家本人任务申请、任务终态、人工复命审核 | 个人仕籍、我的差事、直属主管、贡献收支、库藏、军需调拨、颁差、推进月令、收纳复命/申斥 | 岗位候选、任务候选、责任人响应、直属审核、贡献、功绩和结案凭据均以 orgFlow 为准；验收奖励进入 `task.execution` 实账，玩家可按 20 点一批调拨为 12 军粮；12 席均进入可操作官员集合，负责人不可向自己派单 | `test-live-membership-browser.js`、`test-live-player-career-browser.js`、`live-player-career-browser.json`、`test-live-roster-ledger.js`、`test-live-office-roster-browser.js`、`test-live-office-inventory.js`、`test-live-inventory-requisition.js`、`test-live-office-acceptance.js`、`test-live-settlement-acceptance.js` |
| NexusKernel | 运行模块健康、规范军令、确认动作、恢复签发、终态复命裁决、公共资源支出裁可、行军路线与问对结果封存 | 内核军令草案、签发/驳回、复命待裁、军需调拨待裁、军令簿、行军择路、史官问对 | 史料、军议、AINPC 进言、书问、当值、急报、适岗证据和军需支出统一 SHA-256 封存；开战前由 `dongzhou_campaign_route` 模块封存最终路线、地图、粮草与士气；问对正确项仅留在服务端请求账本，交卷后才由 `dongzhou_knowledge_tournament` 模块揭示并封存结果；确认动作可恢复，重放不重复计分 | `test-live-kernel-mandate-acceptance.js`、`test-live-spontaneous-thought.js`、`test-live-mandate-mobile.js`、`test-live-settlement-acceptance.js`、`test-live-inventory-requisition.js`、`test-live-campaign-route-acceptance.js`、`test-live-knowledge-quiz.js` |

## 跨服务闭环

联网授命必须依次取得已发布史料、当前属官裁断、AINPC 当值与状态、NexusKernel 军令，再由 orgFlowEngine 受理。任务终态先形成 orgFlow 结案实账，再由 NexusKernel 生成玩家裁决，随后将结果写回 AINPC 重要事件和长期经历，最后作为战前助益进入战斗。缺少任一服务确认时不会在浏览器本地伪造成功。

任务终态还会以独立 outbox 写入 AINPC 稳定品质。每个任务的效果号固定，重试、刷新和重启不会重复加点；升级只补齐已有权威结果，绝不重算成败。下一次任职读取正式品质档案，按军需、整训、巡防、情报或外交的价值要求计算品行适配，随后由 NexusKernel 连同胜任度一起封存并交给 orgFlowEngine。真实回填将左儒担当从 `85` 精确变为 `94`，重启保持不变；军需品行 `59/100`、胜任度品质因子 `+1.8` 已由无拦截浏览器回读。

同一终态还会以独立、幂等的动机结算写入 AINPC：成功、部分完成、失败分别增加 `8 / 18 / 30` 点对应差事意愿。东周事件认知携带外部权威动机策略，AINPC 仍处理事件、情绪、关系和记忆，但不再用模型候选覆盖已经结算的意愿；刷新、事件异步完成和八角色容器重启均不会重复加点或回退。

军令由玩家确认签发后，网关先调用 AINPC 正式 `POST /api/v1/schedule-interrupts/temp/generate`。请求绑定军令号、摘要、属官、当前当值、急报分、游戏时钟和稳定事件号；AINPC 的日程 owner 负责保护休息日程、插入今日临时事项或写入未来计划。只有通过事件号和返回结构复核的结果才封成 `scheduleInterruption` 回执并随军令、组织差事和云存档保留；断线重试复用同一请求号和事件号，不会重复插程。orgFlow 派差接口会在服务端反查该玩家同一军令摘要的已完成入程记录，未入程、入程失败、跨玩家或摘要不符均无法绕过前端直接派差。

玩家可在裁断前请求当前属官自主进言。网关把当前关卡、已选出处、任务类型、AINPC 当值、人格、动机和游戏时钟交给正式 `spontaneous-thought` 能力；请求号同时作为动机操作号，重试不会重复累计。完整进言与一条稳定军议提案共同形成 SHA-256 回执并写入云存档，只有 AINPC 军议实际选中该签名提案时才允许随 NexusKernel 军令封存，跨玩家、跨属官、跨关卡、跨任务或摘要篡改均拒绝。

复命被接纳后，组织贡献同时以 `TASK_SETTLEMENT_ACCEPTED` 原因进入 orgFlow 公共库藏。玩家申请调拨 20 点 `task.execution` 时，NexusKernel 先封存支出草案；玩家签发后 orgFlow 才以 `CAMPAIGN_REQUISITION_APPROVED` 权威扣账，东周再依据已验证收据补入 12 军粮，驳回则零支出。内核动作、请求号、扣账和云存档均可回放，页面刷新或中断恢复不会替玩家自动签发，也不会重复扣领或重复加粮。

组织层级后续调整不会让已结案差事从人物经历中消失。AINPC 可按原任务号只读回看终态快照，但 orgFlow 会用当前名册重新核验组织、主管、岗位、责任人和直属关系；只有已终态任务的 `snapshot` 获得兼容，旧层级上的领命、复命及其他写操作仍被拒绝。

战斗结算同样进入人物经历。网关只从战报中的军议、军令和筹备指令提取当前权威名册内的实际参与者，为每人生成稳定的重要事件和长期系统消息；存档与事件原子提交、相同重试不会重复，未知或未参与角色不受影响。同一事件号若携带不同结果会使整个存档事务回滚，防止云档与 NPC 经历分叉。

玩家本人仕途是独立的权威闭环：先由 orgFlow 写入 `officer_12` 仕籍，再通过 AINPC 与直属杜伯查询本人岗位目录、按名称申请、调阅待办、接受和复命；orgFlow 校验每一步并在杜伯审核通过后结算贡献。浏览器只展示 AINPC 回信和 orgFlow 名册回读，不自行创建任务或增加贡献。

史官问对把 knowledge-jizhan 的知识竞赛规则落入当前战役。网关从本回已发布 AKU 的结构化人物录选取正确项，从其他关卡人物录选择三个干扰项；题面经 NexusKernel 生成稳定动作号和 SHA-256 题印，正确索引只保存在玩家隔离的服务端请求账本。题目限时 30 秒，答中 10 分，逾时或答错为 0 分；刷新可恢复未答题，同一题重复交卷只回放原结果，换答案或跨玩家交卷均拒绝。

相邻关卡行军不再只有固定耗粮。网关按同一对 knowledge-jizhan 地图节点分别核验 `campaign_progression`、`fixed_point` 和 `npc_dialog` 路线，并拒绝地图号、落点或向导对话结构不完整的结果。玩家可选奉诏直进（军粮 2）、官道驿行（军粮 3、士气 +6）或向导引路（军粮 1、士气 -4）；偏好随云档保存，但开战不会信任展示缓存，而是把最终方法重新交给服务端查询并由 NexusKernel `dongzhou_campaign_route` 模块封存。联网结果缺少 `SEALED` 回执时拒绝开战；通过后才一次结算并把 64 位摘要写入战斗存档。桌面端和 390px 移动端均已通过真实接口验收。

当前无拦截完整任务证据为：

- `live-kernel-mandate-complete44-evidence.json`：史证适配、签令、派差、复命和战斗承接。
- `live-authoritative-settlement.png`：贡献、功绩、结案摘要、NPC 事件和长期经历一致。
- `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json`：知识、军议、外交军令、游说、盟约门禁和云档恢复。
- `live-player-career-browser.json`：玩家请仕、可领目录、按名称领差、待办、受命、复命、直属审核和贡献 `0 -> 100`。
- `live-mandate-schedule-complete77.png`：真实史料、军议、Nexus 签发、AINPC 日程中断、orgFlow 派差、复命审核、库存奖励、云档与战斗承接。
- `live-office-npc-state-complete80.png`：层级升级后真实人物状态、关系与 90 日当值均恢复为可读，最终状态和日程请求为 `200`，页面无“暂不可用”。
- `live-battle-memory-complete81.json`：独立玩家的繻葛之战战报经云档重载仍在官署可见；公子吕两条 AINPC 事件一次送达，周幽王两条在短暂不可用后由 outbox 第 7 次重试送达。
- `live-battle-emotion-complete82.json`：独立玩家胜报以服务器权威语义进入 AINPC；周幽王状态关联同一事件号并精确落为 `joy 78 / strong`，规则理由和官署页面展示均通过。
- `live-quality-loop-complete92.png`：历史 orgFlow 结果幂等沉淀为 AINPC 品质，品质进入下一次任职胜任度并由官署展示。
- `live-motivation-authority-complete94-motivation.json`：真实 orgFlow 成功终态把军粮转运意愿从 `0 -> 8`；异步事件认知和 AINPC 八角色重启后仍保持 8，稳定操作未重复执行。

## 当前验证基线

- 网关：`103 passed`，另有 `21 subtests passed`；AINPC 动机定向回归通过，完整动机模块 `184 passed, 18 skipped`，另有 3 个既存启动夹具失配。
- 前端：集成客户端、组织玩法、战斗系统、官署浏览器、军议浏览器和外交浏览器全部通过。
- 真实冒烟：四项能力在线；独立访客存档往返、版本冲突和玩家隔离通过；172/172 关已发布史料、171/171 组连续行军均具备战役推进、定点和 NPC 对话三种路线；172 关共有 184 条分层出处，其中 160 关使用明确标注的《东周列国志》文学底本边界；左儒计划为 90 天、436 项东周事务。
- 权威名册：12/12 NPC 状态与 90 天计划通过；真实浏览器逐席显示心境、关系、性情、动机与日程，杜伯可调阅但不可向自己派单。
- 玩家仕途：真实浏览器无拦截完成 `officer_12` 入仕、`Intelligence mission` 受命与复命，杜伯审核通过后贡献余额从 `0` 增至 `100`，测试结束辞仕并释放席位。
- 军需调拨：真实浏览器无拦截证明草案阶段零扣款、NexusKernel 签发后公共库藏 `60 -> 40`、军粮 `100 -> 112`、驳回零扣款；云档重载保持一致，同一请求回放不重复扣领。
- 属官进言：真实左儒进言返回 `COMPLETED / hasThought=true`，重要度多次实测为 `72-78`，动机路由为 `delayed`；真实 Chromium 完成进言、军议选中、Nexus 草案封存同一摘要和玩家驳回，未派发 orgFlow 差事；320px 长文自动换行且无横向溢出，证据为 `live-spontaneous-thought-mobile.png`。
- 军令入程：真实 Chromium 无拦截只发出 1 次日程中断请求，AINPC 正式日程 owner 返回并落下可校验回执，随后 orgFlow 任务 `SUCCESS`、玩家收纳复命、公共库藏 `40 -> 140`、军粮奖励、云档重载和战斗承接全部通过；证据为 `live-mandate-schedule-complete77.png`。
- 战后经历：真实 Chromium 无拦截写入繻葛之战战报并从云档重载官署档案；两名实际参与属官共四条重要事件/长期系统消息最终均为 `DELIVERED`。公子吕两条一次送达，周幽王两条在上游短暂不可用后由 outbox 第 7 次重试送达，最终错误为空。该状态证明 AINPC 正式回调接收成功，不替代下游异步记忆整理状态。
- 战后情绪：真实 Chromium 无拦截写入新的繻葛之战胜报，v2 事件一次送达；AINPC 忽略冲突的模型状态候选，按 `protect/support/success` 规则持久化 `joy 78 / strong`，关联事件号与东周确定性计算一致，官署页面已回读显示。
- 史官问对：真实 Chromium 从第一回已发布 AKU 开题，公开题面不含正确索引；刷新后恢复同一题并答中伯阳父，NexusKernel 返回 `SEALED` 结果，云档累计 10 分，证据为 `knowledge-quiz-live.png`。
- 行军择路：真实 Chromium 在桌面端选择向导引路，军粮 `100 -> 99`、士气 `70 -> 66`，内核摘要为 `5c95d290...40658`；390px 移动端选择官道驿行，军粮 `100 -> 97`、士气 `70 -> 76`，摘要为 `866ade76...822b`。两次开战均重新读取真实 knowledge-jizhan 图谱并得到 `dongzhou_campaign_route / SEALED` 回执，证据为 `campaign-routes-desktop-live.png` 与 `campaign-routes-mobile-live.png`。
- 本地交付：网关、AINPC、orgFlow 和九个依赖容器均符合镜像、健康与 `unless-stopped` 约束；完整 H5 包哈希通过；检查过程业务写入为 0。

## orgFlow 追办与补救

orgFlow 东周目录 v4 已为外交、操练、谍报、巡察和军需五类差事配置权威派生规则。成功结案生成追办，部分完成生成追办，失败生成补救；派生深度限定为一层。东周服务端复核前序任务、根任务、触发结果、规则号、岗位与确定性任务号，再把已创建子任务登记给原玩家。子任务继承章节和岗位席位、成本为 0；席位责任人变化时按 orgFlow 当前实账同步，并按普通差事继续结案。真实父任务到子任务链路见 `test-live-orgflow-followup.js`、`live-orgflow-followup-complete86.json`、`live-orgflow-followup-lineage-complete86.json` 和同名 PNG。

## 非玩法边界

公网 TLS、可信回调网络和 Windows 宿主冷启动属于部署验收，不由浏览器玩法测试代替。公共库藏只接受 orgFlow 的结案奖励与签名调拨，不人工播种资源；余额不足时明确拒绝。模型或上游服务不可用时保持明确失败，不静默切换本地伪结果。
