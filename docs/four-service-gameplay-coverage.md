# 东周四服务玩法覆盖矩阵

本矩阵记录 2026-11-13 本机完整联网版的当前边界。范围是四个仓库中与东周玩家流程直接相关的能力，不把通用管理后台、监控和其他游戏协议误列为东周玩法。

## 覆盖结果

| 来源 | 东周服务契约 | 玩家入口 | 权威结果 | 真实证据 |
| --- | --- | --- | --- | --- |
| knowledge-jizhan | 全文检索、按关卡读取已发布 AKU、战役路线、玩家简册、知识竞赛 | 查阅、本回史料、选定出处、已得简册、行军路线、史官问对 | 只接收 `dongzhou_stage_*`；出处和检索回执进入军议与军令；相邻关卡路线必须同时通过战役推进、定点和 NPC 对话三种图谱查询；问对题目从当前已发布 AKU 人物录生成，30 秒内答中记 10 分；本回 10 分封存结果可作为史识凭据进入派差 | `test-live-knowledge-browser.js`、`test-live-fulltext-browser.js`、`test-live-campaign-route-acceptance.js`、`test-live-knowledge-quiz.js`、`verify-live-knowledge-campaign.py`、`campaign-routes-desktop-live.png`、`campaign-routes-mobile-live.png`、`knowledge-quiz-live.png` |
| AINPC | NPC 注册与上线、主动来信偏好、状态/人格/动机/稳定品质/关系、双向私聊、AI Helper 问答与评价、90 天日程、关卡当值、主副手双向协同、自主念头、军议裁断、已签军令临时插程、玩家本人领差/响应/复命、复命裁决后的玩家关系、急报评估、参战结果与长期经历 | 官署状态、品质与品行、府中书问、军师问策、来信开关、拟定日程、本关当值、协办副手、请其进言、军议裁断、签发后下达、我的差事、官署战报 | 稳定 NPC/玩家身份；问策先绑定知识仓已发布的本关 AKU，再由 AINPC 异步生成答案并经游戏服回调按玩家隔离落账；进度提示与最终答案分离，重复回调不重复写入，三维带路不在战棋中伪执行；orgFlow 终态以稳定效果号沉淀品质并影响下一次任职；主办与副手的双向好感/关系形成有正有负的协同因子；成功、部分完成或失败复命被玩家接纳后分别形成不同幅度的感激或敬重，申斥形成恼怒；已签军令分别进入两人的日程 owner 并形成独立防篡改回执；实际参战属官收到幂等的重要事件、长期系统消息和官署可读的短期记忆归档，其中已验签行军路线、路线回执和两端 AKU 随战果进入人物经历 | `test-live-adviser.js`、`verify-live-roster-npcs.py`、`test-live-office-npc-state.js`、`test-live-quality-loop.js`、`test-live-spontaneous-thought.js`、`test-live-correspondence-acceptance.js`、`test-live-interaction-preference.js`、`test-live-schedule-browser.js`、`test-live-player-career-browser.js`、`test-live-kernel-mandate-acceptance.js`、`test-live-battle-memory.js`、`test-live-battle-emotion.js` |
| orgFlowEngine | 权威名册、玩家入仕/辞仕、组织谱系、贡献账、公共库藏、虚拟任务、玩家本人任务申请、月例定时派差、任务终态、人工复命审核 | 个人仕籍、我的差事、直属主管、贡献收支、库藏、军需调拨、颁差、推进月令、月例察访、收纳复命/申斥 | 岗位候选、任务候选、责任人响应、直属审核、贡献、功绩和结案凭据均以 orgFlow 为准；月令命中同类在办差事时跳过重复派发，并返回阻止派发的权威任务供官署显示标题、状态与结果；验收奖励进入 `task.execution` 实账，玩家可按 20 点一批调拨为 12 军粮；12 席均进入可操作官员集合，负责人不可向自己派单 | `test-live-membership-browser.js`、`test-live-player-career-browser.js`、`live-player-career-browser.json`、`test-live-roster-ledger.js`、`test-live-office-roster-browser.js`、`test-live-office-inventory.js`、`test-live-inventory-requisition.js`、`test-live-settlement-acceptance.js`、`test_scheduled_duties.py` |
| NexusKernel | 运行模块健康、规范军令、主副手协同证据、确认动作、恢复签发、终态复命裁决、公共资源支出裁可、行军路线、问对结果与人物四项归档封存 | 内核军令草案、签发/驳回、复命待裁、军需调拨待裁、军令簿、行军择路、史官问对、官署任务簿 | 史料、军议、AINPC 进言、书问、主副手双向关系、两人当值、急报、适岗证据、史识凭据和军需支出统一 SHA-256 封存；确认动作可恢复，重放不重复计分；事件、长期记忆、品质和动机全部送达后才生成人物归档封印 | `test-live-kernel-mandate-acceptance.js`、`test-live-spontaneous-thought.js`、`test-live-settlement-acceptance.js`、`test-live-campaign-route-acceptance.js`、`test-live-knowledge-quiz.js`、`test-live-motivation-loop.js` |

## 跨服务闭环

联网授命必须依次取得已发布史料、当前属官裁断、AINPC 当值与状态、NexusKernel 军令，再由 orgFlowEngine 受理。任务终态先形成 orgFlow 结案实账，再由 NexusKernel 生成玩家裁决，随后将结果写回 AINPC 重要事件和长期经历，最后作为战前助益进入战斗。缺少任一服务确认时不会在浏览器本地伪造成功。

推进月令会由 AINPC 协调 orgFlow 的月例察访规则。若左儒已有同类非终态任务，orgFlow 以确定顺序选出权威任务并把任务号写入 `SKIPPED / duplicate_active_task` 触发记录；东周再通过签名管理接口反查组织、任务类型和责任人，官署直接展示任务标题、当前状态与最终结果。历史触发在迁移时只按同一严格条件回填，无法追溯的记录明确标为引用不可用，不会猜测绑定。

月例察访在登记规则前会先核验司马与司徒的 AINPC 日程。排班服务暂不可用时，网关返回可重试的 `503 / ainpc_schedule_unavailable`，契约响应损坏时返回 `502 / ainpc_schedule_contract_invalid`，不再泄漏为无语义的服务器 `500`；服务恢复后同一入口可正常返回 `ACTIVE` 规则并继续派差。

无可执行待办时，AINPC 现在无论生成快照是否位于核心地图，都直接采用固定 `SleepTree`，不再退回模型并因旧目录中的运行态 `Reborn` 被过滤而形成空链。东周网关严格实现 `ValidateBTParams / ExecuteBehavior`：仅接受参数合法且网关已确认就绪的 `SleepTree` 与 `Reborn`，休息按声明时长持有同一物理 UID，结束后才回调。回调复合身份、物理 UID 与到期时间进入 SQLite outbox，网关重启不丢失；同 UID 同载荷只复用，冲突载荷返回 409。真实干净重启验收中 12 名 NPC 各生成并下发一条休息链，验收窗口内预检失败、空链、模型配置失败和提前完成均为 0。

玩家现在可为差事指定一名协办副手。网关先用 orgFlow 权威名册确认主办与副手均在职，再读取 AINPC 两个方向的好感和关系，生成 `-8` 至 `+10` 的协同因子并计入任务成功率。NexusKernel `dongzhou_mandate_workflow 1.11.0` 同时封存两人身份、关系证据、协同分和各自当值；军令下达时两人分别获得稳定事件号和日程中断回执。任务终态为双方分别写入事件、长期记忆、品行与履职意愿，并由 `dongzhou_npc_settlement 1.1.0` 各自封印；战后两人也都进入权威参战者名单。任何一方未真正入程都不会形成可用的完整协办军令。

协办不再只是成功率参数。联合军令会在 orgFlow 原子生成汇总父任务以及主办、协办两个关键子任务，双方独立执行并保留各自的异常、补件、确认与结案行迹；任一方未终态时不会提前结算。NexusKernel `dongzhou_organization_task_topology 1.0.0` 封存父子拓扑和双方权威状态，官署军务账簿直接显示联合进度。

任务终态还会以独立 outbox 写入 AINPC 稳定品质。每个任务的效果号固定，重试、刷新和重启不会重复加点；升级只补齐已有权威结果，绝不重算成败。下一次任职读取正式品质档案，按军需、整训、巡防、情报或外交的价值要求计算品行适配，随后由 NexusKernel 连同胜任度一起封存并交给 orgFlowEngine。当前累积实账中左儒担当为 `100`，军需品行 `60/100`、胜任度品质因子 `+2`；测试从权威档案动态取值并验证官署展示与下一次任职使用同一数值，不再依赖历史快照常量。

同一终态还会以独立、幂等的动机结算写入 AINPC：成功、部分完成、失败分别增加 `8 / 18 / 30` 点对应差事意愿。东周事件认知携带外部权威动机策略，AINPC 仍处理事件、情绪、关系和记忆，但不再用模型候选覆盖已经结算的意愿；刷新、事件异步完成和八角色容器重启均不会重复加点或回退。下一次派任会读取该意愿作为匹配信号，并把动机因子计入胜任度；事件、长期记忆、品质和动机四项全部送达后，NexusKernel 才封存完整人物归档。

玩家对复命的裁决也会进入人物关系，而不再只有申斥能改变好感。成功、部分完成和失败但如实接纳分别写入 `appreciation +6 / +3` 或 `respect +1`；申斥继续写入 `annoyance +5.8`。重要事件、长期记忆和好感三项使用稳定事件号异步送达 AINPC，全部完成后由 NexusKernel `dongzhou_npc_review_relationship 1.0.0` 绑定任务号、裁决摘要、NPC、玩家和三项送达次数生成封印；重放裁决不会重复加点。官署任务簿持续轮询已结案但关系尚在回写的任务，最终展示关系变化与封印摘要。

“军师问策”使用 AINPC 正式 AI Helper，而不是把普通 NPC 对话改名。网关先读取知识仓当前关卡已发布 AKU，把史料号、摘要、目标、人物与出处作为权威玩家状态提交；AINPC 同步受理后异步回调 `/api/v2/NDLLMSendLittleElfMessage`。加载提示和最终答案在回调前都经过 AIFirewall HMAC 敏感词接口，容器通过宿主机 `8090` 桥接访问；过滤服务异常时才会显式标记降级。回调按稳定玩家号与请求号双重校验，加载提示只更新进度，最终答案才结案，重复内容返回同一 `talkId`，不同内容冲突拒绝；浏览器刷新后继续轮询同一请求，并可提交一次“准确/不准确”评价。AI Helper 的三维带路会被明确忽略，不在战棋地图中伪造寻路成功。

军令由玩家确认签发后，网关先调用 AINPC 正式 `POST /api/v1/schedule-interrupts/temp/generate`。请求绑定军令号、摘要、属官、当前当值、急报分、游戏时钟和稳定事件号；AINPC 的日程 owner 负责保护休息日程、插入今日临时事项或写入未来计划。只有通过事件号和返回结构复核的结果才封成 `scheduleInterruption` 回执并随军令、组织差事和云存档保留；断线重试复用同一请求号和事件号，不会重复插程。orgFlow 派差接口会在服务端反查该玩家同一军令摘要的已完成入程记录，未入程、入程失败、跨玩家或摘要不符均无法绕过前端直接派差。

玩家可在裁断前请求当前属官自主进言。网关把当前关卡、已选出处、任务类型、AINPC 当值、人格、动机和游戏时钟交给正式 `spontaneous-thought` 能力；请求号同时作为动机操作号，重试不会重复累计。完整进言与一条稳定军议提案共同形成 SHA-256 回执并写入云存档，只有 AINPC 军议实际选中该签名提案时才允许随 NexusKernel 军令封存，跨玩家、跨属官、跨关卡、跨任务或摘要篡改均拒绝。

复命被接纳后，组织贡献同时以 `TASK_SETTLEMENT_ACCEPTED` 原因进入 orgFlow 公共库藏。玩家申请调拨 20 点 `task.execution` 时，NexusKernel 先封存支出草案；玩家签发后 orgFlow 才以 `CAMPAIGN_REQUISITION_APPROVED` 权威扣账，东周再依据已验证收据补入 12 军粮，驳回则零支出。内核动作、请求号、扣账和云存档均可回放，页面刷新或中断恢复不会替玩家自动签发，也不会重复扣领或重复加粮。

组织层级后续调整不会让已结案差事从人物经历中消失。AINPC 可按原任务号只读回看终态快照，但 orgFlow 会用当前名册重新核验组织、主管、岗位、责任人和直属关系；只有已终态任务的 `snapshot` 获得兼容，旧层级上的领命、复命及其他写操作仍被拒绝。

战斗结算同样进入人物经历。网关只从战报中的军议、军令和筹备指令提取当前权威名册内的实际参与者，为每人生成稳定的重要事件和长期系统消息，并把同一战果通过 AINPC 正式短期记忆接口归档为官署可读经历；存档与事件原子提交、相同重试不会重复，未知或未参与角色不受影响。同一事件号若携带不同结果会使整个存档事务回滚，防止云档与 NPC 经历分叉。

玩家本人仕途是独立的权威闭环：先由 orgFlow 写入 `officer_12` 仕籍，再通过 AINPC 与直属杜伯查询本人岗位目录、按名称申请、调阅待办、接受和复命；orgFlow 校验每一步并在杜伯审核通过后结算贡献。浏览器只展示 AINPC 回信和 orgFlow 名册回读，不自行创建任务或增加贡献。

史官问对把 knowledge-jizhan 的知识竞赛规则落入当前战役。网关从本回已发布 AKU 的结构化人物录选取正确项，从其他关卡人物录选择三个干扰项；题面经 NexusKernel 生成稳定动作号和 SHA-256 题印，正确索引只保存在玩家隔离的服务端请求账本。题目限时 30 秒，答中 10 分，逾时或答错为 0 分；刷新可恢复未答题，同一题重复交卷只回放原结果，换答案或跨玩家交卷均拒绝。

答中后的问对结果会成为下一次同关军议的“史识凭据”。网关在签令前重新核验玩家、关卡、AKU、10 分结果摘要与 NexusKernel `SEALED` 回执，并要求 AINPC 军议问题携带同一史识印记；通过后由 `dongzhou_mandate_workflow 1.11.0` 封存并传给 orgFlowEngine，任务成功率增加 `3` 点。答错、跨玩家、跨关卡、错配史料、摘要篡改或只在前端构造字段均为零加成并拒绝伪造凭据；旧存档和未参加问对的军令保持兼容。

相邻关卡行军不再只有固定耗粮。网关按同一对 knowledge-jizhan 地图节点分别核验 `campaign_progression`、`fixed_point` 和 `npc_dialog` 路线，并拒绝地图号、落点或向导对话结构不完整的结果。玩家可选奉诏直进（军粮 2）、官道驿行（军粮 3、士气 +6）或向导引路（军粮 1、士气 -4）；偏好随云档保存，但开战不会信任展示缓存，而是把最终方法重新交给服务端查询并由 NexusKernel `dongzhou_campaign_route` 模块封存。联网结果缺少 `SEALED` 回执时拒绝开战；通过后才一次结算，路线及双史料见证随战果进入正式战报。回执除 64 位摘要外还包含服务端 HMAC 证明，云档入库时会重新验签并核对目标关卡，删除路线或篡改耗粮、士气、知识见证都会被拒绝。验签后的路线名、路线号、回执和两端 AKU 继续进入实际参战属官的 AINPC 重要事件与长期记忆，官署战报同步展示路线和双史料封印。桌面端和 390px 移动端均已通过真实接口验收。

当前无拦截完整任务证据为：

- `live-kernel-mandate-complete44-evidence.json`：史证适配、签令、派差、复命和战斗承接。
- `live-authoritative-settlement.png`：贡献、功绩、结案摘要、NPC 事件和长期经历一致。
- `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json`：知识、军议、外交军令、游说、盟约门禁和云档恢复。
- `live-player-career-browser.json`：玩家请仕、可领目录、按名称领差、待办、受命、复命、直属审核和贡献 `0 -> 100`。
- `live-mandate-schedule-complete77.png`：真实史料、军议、Nexus 签发、AINPC 日程中断、orgFlow 派差、复命审核、库存奖励、云档与战斗承接。
- `live-office-npc-state-complete80.png`：层级升级后真实人物状态、关系与 90 日当值均恢复为可读，最终状态和日程请求为 `200`，页面无“暂不可用”。
- `live-battle-memory-complete81.json`：独立玩家的真实军议经 NexusKernel 封存后形成繻葛之战胜报；AINPC 重要事件、长期系统消息和短期记忆归档均完成，云档重载后官署战报及周幽王的“告捷”经历同时可见。
- `live-battle-receipt-complete85.json`：独立玩家胜报以服务器权威语义进入 AINPC；周幽王状态关联同一事件号并精确落为 `joy 78 / strong`，NexusKernel 参战者封印和官署页面展示均通过。
- `live-quality-loop-complete92.png`：历史 orgFlow 结果幂等沉淀为 AINPC 品质，品质进入下一次任职胜任度并由官署展示。
- `live-motivation-authority-complete94-motivation.json`：真实 orgFlow 成功终态把军粮转运意愿从 `0 -> 8`；异步事件认知和 AINPC 八角色重启后仍保持 8；下一次军需派任读到该信号，动机适配分 `53`、胜任度因子 `+0.4`；四项归档由 `dongzhou_npc_settlement` 生成 64 位稳定封印。
- `live-collaboration-complete101.json`：真实双人军令中左儒主办、秦襄公协办；副将事件、长期记忆、品行、履职意愿四项均送达并独立封印。筹备奖励已进入战场并从待用列表消耗后，战报仍通过服务端军议、军令和 orgFlow 结案认证，权威参战者为两人。
- `live-knowledge-mastery-v5-complete105.json`：真实问对答中后进入 AINPC 军议，NexusKernel 军令封存 `10/10` 与成功率 `+3`；orgFlow 模板 5 实账保存同一题号、分数和加成。
- `live-terminal-gate-complete89.json`：真实 orgFlow 执行尚未终态时不会提前生成 AINPC 复命提示；执行进入 `SUCCESS` 后才允许主管审核，公共库藏 `task.execution` 从 `940 -> 1040`，云档恢复与战报回读均通过。
- `live-relationship-growth-complete107.json`：真实玩家接纳左儒成功复命后，AINPC 重要事件、长期记忆和 `appreciation +6` 三项均送达；NexusKernel 生成关系封印 `ca9f6793...74249`，重放不重复加点，官署任务簿显示“感激+6”和封印摘要。
- `live-adviser-complete108.json`：真实 Chromium 提交“本关史料中的关键人物是谁”，知识仓已发布 AKU 随玩家状态进入 AINPC；加载提示和最终答案经 AIFirewall 过滤后由游戏服回调，两次均为 `filter_degraded=false`，页面显示周宣王、杜伯、左儒及史事情由，并成功提交“准确”评价。最近一次完整复验任务为 `1fcce851-19f7-4b8b-bc1f-7b45e4742607`。
- `live-route-battle-memory129.json`：真实向导路线及第一、第二回 AKU 经 NexusKernel 验签后进入第二回战报，实际参战属官的 AINPC 记忆和官署战报均回读到同一路线与双史料封印。

## 当前验证基线

- 网关完整回归：`125 passed`，另有 `21 subtests passed`；史识凭据覆盖正确封存、摘要篡改、跨玩家/关卡/史料隔离和 orgFlow 参数传递，月例排班上游不可用的可重试错误映射亦有回归保护。
- 前端：集成客户端、组织玩法、战斗系统、官署浏览器、军议浏览器和外交浏览器全部通过。
- 真实冒烟：四项能力在线；独立访客存档往返、版本冲突和玩家隔离通过；172/172 关已发布史料且每关在线返回明确标注的《东周列国志》文学底本边界，171/171 组连续行军均具备战役推进、定点和 NPC 对话三种路线；左儒计划为 90 天、450 项东周事务。长期计划按 AINPC 契约只列可执行待办，休息由非活跃时段的运行时强制休息机制接管。
- 权威名册：12/12 NPC 状态与 90 天计划通过；真实浏览器逐席显示心境、关系、性情、动机与日程，杜伯可调阅但不可向自己派单。
- 玩家仕途：真实浏览器无拦截完成 `officer_12` 入仕、`Intelligence mission` 受命与复命，杜伯审核通过后贡献余额从 `0` 增至 `100`，测试结束辞仕并释放席位。
- 军需调拨：真实浏览器无拦截证明草案阶段零扣款、NexusKernel 签发后公共库藏 `60 -> 40`、军粮 `100 -> 112`、驳回零扣款；云档重载保持一致，同一请求回放不重复扣领。
- 属官进言：真实左儒进言返回 `COMPLETED / hasThought=true`，重要度多次实测为 `72-78`，动机路由为 `delayed`；真实 Chromium 完成进言、军议选中、Nexus 草案封存同一摘要和玩家驳回，未派发 orgFlow 差事；320px 长文自动换行且无横向溢出，证据为 `live-spontaneous-thought-mobile.png`。
- 军令入程：真实 Chromium 无拦截只发出 1 次日程中断请求，AINPC 正式日程 owner 返回并落下可校验回执，随后 orgFlow 任务 `SUCCESS`、玩家收纳复命、公共库藏 `40 -> 140`、军粮奖励、云档重载和战斗承接全部通过；证据为 `live-mandate-schedule-complete77.png`。
- 战后经历：真实 Chromium 无拦截通过 AINPC 军议取得参战凭证，由 NexusKernel 返回 `SEALED` 战报，再同时写入 AINPC 重要事件、长期系统消息和短期记忆归档；轮询读到唯一“繻葛之战告捷”记忆后，云档重载仍在官署人物经历与战报档案中可见。
- 战后情绪：真实 Chromium 无拦截写入新的繻葛之战胜报，v2 事件一次送达；AINPC 忽略冲突的模型状态候选，按 `protect/support/success` 规则持久化 `joy 78 / strong`，关联事件号与东周确定性计算一致，官署页面已回读显示。
- 史官问对：真实 Chromium 从第一回已发布 AKU 开题，公开题面不含正确索引；刷新后恢复同一题并答中伯阳父，NexusKernel 返回 `SEALED` 结果，云档累计 10 分，证据为 `knowledge-quiz-live.png`。
- 行军择路：真实 Chromium 在桌面端选择向导引路，军粮 `100 -> 99`、士气 `70 -> 66`；390px 移动端选择官道驿行，军粮 `100 -> 97`、士气 `70 -> 76`。两次开战均重新读取真实 knowledge-jizhan 图谱并得到 `dongzhou_campaign_route 1.2.0 / SEALED` 回执和服务端证明；第二回真实战报还把向导路线及 `dongzhou_stage_001/002` 写入实际参战属官的 AINPC 长期记忆，证据为 `campaign-routes-desktop-live.png`、`campaign-routes-mobile-live.png` 与 `live-route-battle-memory129.json`。
- 本地交付：网关、AINPC、orgFlow 和九个依赖容器均符合镜像、健康与 `unless-stopped` 约束；完整 H5 包哈希通过；检查过程业务写入为 0。
- 版本交付：东周父仓库只固定 `ganzijie1` GitHub 上四个精确提交：knowledge-jizhan `7b8b0378`、AINPC `031bc4af6`、orgFlowEngine `bdd432c`、NexusKernel `beda977d`；内网 GitLab 不作为推送目标。AINPC 的生产私聊已切换到 LoongEQ `guidance/v1` 与 `eq-abilities-v2`，并在画像缺失时调用正式幂等 `/ensure`，不再把永久缺档当正常状态。真实书问任务 `playerchat-4643eac3374c36fe422a4c2b4bc3020a` 完成回信且 API、Worker 和网关健康；当时 LoongEQ 外部画像存储返回 `503 guidance_profile_storage_unavailable`，因此该次验收只证明显式降级和聊天连续性，不能宣称 EQ 策略已应用。

## orgFlow 追办与补救

orgFlow 东周目录 v4 已为外交、操练、谍报、巡察和军需五类差事配置权威派生规则。成功结案生成追办，部分完成生成追办，失败生成补救；派生深度限定为一层。东周服务端复核前序任务、根任务、触发结果、规则号、岗位与确定性任务号，再把已创建子任务登记给原玩家。子任务继承章节和岗位席位、成本为 0；席位责任人变化时按 orgFlow 当前实账同步，并按普通差事继续结案。真实父任务到子任务链路见 `test-live-orgflow-followup.js`、`live-orgflow-followup-complete86.json`、`live-orgflow-followup-lineage-complete86.json` 和同名 PNG。

## 非玩法边界

公网 TLS、可信回调网络和 Windows 宿主冷启动属于部署验收，不由浏览器玩法测试代替。公共库藏只接受 orgFlow 的结案奖励与签名调拨，不人工播种资源；余额不足时明确拒绝。模型或上游服务不可用时保持明确失败，不静默切换本地伪结果。
