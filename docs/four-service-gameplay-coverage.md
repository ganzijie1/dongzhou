# 东周四服务玩法覆盖矩阵

本矩阵记录 2026-11-17 本机完整联网版的当前边界。范围是四个仓库中与东周玩家流程直接相关的能力，不把通用管理后台、监控和其他游戏协议误列为东周玩法。

## 覆盖结果

| 来源 | 东周服务契约 | 玩家入口 | 权威结果 | 真实证据 |
| --- | --- | --- | --- | --- |
| knowledge-jizhan | 全文检索、按关卡读取已发布 AKU、战役路线、玩家简册、知识竞赛 | 查阅、本回史料、选定出处、据史慰勉、据史问忆、已得简册、行军路线、史官问对、战后论功复盘、内核验印 | 只接收 `dongzhou_stage_*`；出处和检索回执进入军议与军令；相邻关卡路线必须同时通过战役推进、定点和 NPC 对话三种图谱查询；问对题目从当前已发布 AKU 人物录生成，30 秒内答中记 10 分；本回 10 分封存结果可作为史识凭据进入派差；玩家可要求服务端从原始问答记录重算封印；慰勉、问忆和战后复盘只能引用当前关卡再次核验为已发布的 AKU | `test-live-knowledge-browser.js`、`test-live-fulltext-browser.js`、`test-live-campaign-route-acceptance.js`、`test-live-knowledge-quiz.js`、`test-live-history-commendation.js`、`test-live-history-recollection.js`、`test-live-kernel-mandate-acceptance.js`、`test-battle-debrief-browser.js`、`verify-live-knowledge-campaign.py`、`campaign-routes-desktop-live.png`、`campaign-routes-mobile-live.png`、`knowledge-quiz-live.png`、`battle-debrief-desktop.png`、`battle-debrief-mobile.png` |
| AINPC | NPC 注册与上线、主动来信偏好、状态/人格/动机/稳定品质/关系、当前执行器状态、今日运行队列、双向私聊、事件公聊、AI Helper 问答与评价、90 天日程、关卡当值、主副手双向协同、自主念头、军议裁断、据史慰勉、据史问忆、已签军令临时插程、玩家本人领差/响应/改令/复命/补呈、复命裁决后的玩家关系、急报评估、参战结果与长期经历 | 官署状态、当前执行进度、今日实况与稍后待办、品质与品行、府中书问、官署告示、军师问策、来信开关、拟定日程、本关当值、协办副手、请其进言、据史慰勉、据史问忆、军议裁断、签发后下达、我的差事、官署战报 | 稳定 NPC/玩家身份；官署当前执行状态严格复核游戏服与 NPC 复合身份，只投影是否运行/暂停/等待回报、当前事务、阶段和动作进度；今日运行队列另外投影在线状态、值守时窗、当前/待办/挂起事务和数量，不下放登录轮次、会话、终端事件、调试开关、数据源、内部代理、LoongMemory 活动、错误、恢复或扩展参数；玩家改令会把修改前后参数、变更路径及原/拟议总时长交给直属 NPC，NPC 只能依据真实差异裁定；玩家补呈使用 orgFlow 原补件私聊锚点，不把补件误作新的首次复命；事件公聊必须携带当前登录轮次，由东周游戏服幂等落账并经 NexusKernel 封印，页面只展示 orgFlow 当前在职属官的公告；问策先绑定知识仓已发布的本关 AKU，再由 AINPC 异步生成答案并经游戏服回调按玩家隔离落账；据史慰勉以稳定效果号写入 `appreciation +2`，重试不重复结算；据史问忆只读取正式短期记忆，优先匹配含当前 AKU 的军议，缺失时回退最近系统战报，不伪造回忆；orgFlow 终态以稳定效果号沉淀品质并影响下一次任职；主办与副手的双向好感/关系形成有正有负的协同因子；成功、部分完成或失败复命被玩家接纳后分别形成不同幅度的感激或敬重，申斥形成恼怒；已签军令分别进入两人的日程 owner 并形成独立防篡改回执；实际参战属官收到幂等的重要事件、长期系统消息和官署可读的短期记忆归档，其中已验签行军路线、路线回执和两端 AKU 随战果进入人物经历 | `test-live-player-task-response-browser.js`、`live-player-task-response-browser.json`、`test-live-adviser.js`、`test-live-history-commendation.js`、`test-live-history-recollection.js`、`verify-live-roster-npcs.py`、`test-live-office-npc-state.js`、`npc-runtime-schedule-live.png`、`npc-runtime-schedule-mobile-live.png`、`test-live-quality-loop.js`、`test-live-spontaneous-thought.js`、`test-live-correspondence-acceptance.js`、`test-live-interaction-preference.js`、`test-live-schedule-browser.js`、`test-live-player-career-browser.js`、`test-organization-browser.js`、`test-live-kernel-mandate-acceptance.js`、`test-live-battle-memory.js`、`test-live-battle-emotion.js` |
| orgFlowEngine | 权威名册、玩家入仕/辞仕、组织谱系、贡献账、公共库藏、虚拟任务、玩家本人任务申请与参数改令、月例定时派差及启停、任务终态、人工复命审核与退回补件 | 个人仕籍、我的差事、直属主管、贡献收支、库藏、军需调拨、颁差、推进月令、月例察访、停办/恢复月例、收纳复命/补呈/申斥 | 岗位候选、任务候选、责任人响应、参数修订、直属审核、补件确认、贡献、功绩和结案凭据均以 orgFlow 为准；页面只有在活动确认是 `TASK_SUPPLEMENT_REQUEST`、面向玩家且允许 `submit_supplement` 时才开放补呈；未送达的玩家改令审核可由真实私聊建立收悉锚点，审核通过后原子应用参数修订并进入 `IN_PROGRESS`；月令命中同类在办差事时跳过重复派发，并返回阻止派发的权威任务供官署显示标题、状态与结果；玩家启停月例必须携带当前规则版本，由 orgFlow 原子递增，停办只阻止未来派发，不取消已派任务；验收奖励进入 `task.execution` 实账，玩家可按 20 点一批调拨为 12 军粮；正式模板为统领 1 席、巡卫 4 席，当前 4 人在册并保留 1 席供玩家申请，负责人不可向自己派单 | `test-live-player-task-response-browser.js`、`live-player-task-response-browser.json`、`test-live-membership-browser.js`、`test-live-player-career-browser.js`、`live-player-career-browser.json`、`test-organization-browser.js`、`test-live-roster-ledger.js`、`test-live-office-roster-browser.js`、`test-live-office-inventory.js`、`test-live-inventory-requisition.js`、`test-live-settlement-acceptance.js`、`test_scheduled_duties.py` |
| NexusKernel | 运行模块健康、规范军令、主副手协同证据、确认动作、恢复签发、终态复命裁决、公共资源支出裁可、月例规则启停、行军路线、问对结果、贡献卷宗、慰勉、问忆、战后四服务复盘与人物四项归档封存 | 内核军令草案、签发/驳回、复命待裁、军需调拨待裁、月例启停封印、军令簿、行军择路、史官问对、主动验印、玩家与属官功绩卷宗验印、据史慰勉、据史问忆、官署任务簿、论功复盘 | 史料、军议、AINPC 进言、书问、主副手双向关系、两人当值、急报、适岗证据、史识凭据和军需支出统一 SHA-256 封存；`dongzhou_organization_scheduled_duty` 绑定玩家请求、稳定规则号、组织、主办、执行者、任务码及变更前后版本，拒绝跳版或身份错配；`dongzhou_battle_debrief` 只接受已封战报号，由服务端重读本关已发布 AKU、参战者正式记忆和 orgFlow 权威任务行迹后重建复盘，不信任浏览器摘要；慰勉必须等 AINPC 关系事件送达后才由 `dongzhou_npc_commendation` 封印；问忆由 `dongzhou_npc_recollection` 绑定 AKU、人物、记忆号、原文摘要、时间、来源类型和匹配方式；确认动作可恢复，重放不重复计分；问对验印从玩家隔离的服务端原始记录重算题印和答卷封印，浏览器摘要不参与判真；功绩卷宗验印重新读取 orgFlow 权威贡献与原始任务行迹，由 NexusKernel 重建卷宗并核对身份、贡献摘要、模块与封印，不使用页面缓存自证；事件、长期记忆、品质和动机全部送达后才生成人物归档封印 | `test-live-kernel-mandate-acceptance.js`、`test-battle-debrief-browser.js`、`test-live-history-commendation.js`、`test-live-history-recollection.js`、`test-live-spontaneous-thought.js`、`test-live-settlement-acceptance.js`、`test-live-campaign-route-acceptance.js`、`test-live-knowledge-quiz.js`、`test-live-contribution-dossier.js`、`test-live-motivation-loop.js`、`test_scheduled_duties.py` |

## 跨服务闭环

联网授命必须依次取得已发布史料、当前属官裁断、AINPC 当值与状态、NexusKernel 军令，再由 orgFlowEngine 受理。任务终态先形成 orgFlow 结案实账，再由 NexusKernel 生成玩家裁决，随后将结果写回 AINPC 重要事件和长期经历，最后作为战前助益进入战斗。缺少任一服务确认时不会在浏览器本地伪造成功。

官署人物页现在同时读取 AINPC 日程执行器的实时状态，用于区分“计划做什么”和“此刻是否正在执行”。网关仅接受与请求中的游戏服、NPC 完全一致的正式响应；接口未部署、执行器尚无记录或短暂不可用时只把这一行降级为不可用，不拖垮情绪、关系、人格、动机、品质和记忆。实时状态不进入 NexusKernel，因为它是会变化的观察值而不是需要永久封印的裁决事实。

日程页进一步区分“今日实况”和“90 日计划”。前者来自 AINPC 正式日程 Web 总览，逐项复核游戏服与 NPC 身份，只展示当前值守时窗、正在执行及最多五项待办/挂起事务；后者继续来自长期计划 owner。总览不可用时只降级今日实况，90 日计划仍可读取。调试控制、持久库来源、内部代理、LoongMemory 活动、错误类型和 `extra_data` 均不会进入浏览器；这个运行队列同样是易变观察值，不由 NexusKernel 永久封印。

AINPC 好感与关系中的目标身份也由网关做当前会话映射。当前玩家的稳定 AINPC 身份显示为“你”，orgFlow 当前名册中的 12 名 NPC 通过稳定 NPC 号还原正式姓名；无法归属到当前玩家或在职 NPC 的历史目标不会以下放 ID 或重复“未具名人物”的方式占据人情簿，但 AINPC 返回的牵挂与人际总数仍照实显示。

官署“内核在线”状态以 NexusKernel 当前注册的全部必需玩法模块为准，不再只抽查军令、问对、路线、任务轨迹和军需模块。19 个模块中任一项离开 `ready/degraded` 可运行状态，集成状态立即返回离线、完整模块状态与不可用名单；官署状态条同时显示实际可运行数量，例如 `内核 19/19`。

完成性审计以正式玩家边界而不是仓库中的全部 HTTP 路由为准。knowledge-jizhan 的玩家检索、玩家 AKU 批量读取、已发布关卡知识和地图迁移查询均有东周调用与玩家入口；AINPC 的注册/上线、行为目录、人物状态、私聊/公聊、AI Helper、日程规划/执行/中断、组织事务、短期记忆、急报、自主念头和战报均进入对应闭环，`fact` 只是 `short_term_memory` 的兼容 HTTP 门面，不重复计算为新玩法；orgFlowEngine 的正式岗位、名册、贡献、库存、定时规则和虚拟任务由 AINPC tools 或签名管理接口承接，默认关闭的旧任务冲突选择、旧审核/申诉、组织治理后台、导入和调试路由不冒充玩家能力；AINPC 的监控、日志、EQ 管理、缓存、用量分析和影子知识维护同样属于运维面。NexusKernel 门禁逐项覆盖 `dongzhou_runtime`、`dongzhou_mandate_workflow`、`dongzhou_knowledge_tournament`、`dongzhou_npc_commendation`、`dongzhou_npc_recollection`、`dongzhou_npc_public_notice`、`dongzhou_organization_contribution_ledger`、`dongzhou_campaign_route`、`dongzhou_npc_settlement`、`dongzhou_npc_review_relationship`、`dongzhou_npc_collaboration_relationship`、`dongzhou_organization_task_trace`、`dongzhou_organization_contribution_dossier`、`dongzhou_npc_merit_commendation`、`dongzhou_adviser_guide`、`dongzhou_organization_task_topology`、`dongzhou_logistics_briefing`、`dongzhou_organization_scheduled_duty` 和 `dongzhou_battle_debrief`，不能以其中任意子集通过代替全量健康。

“论功复盘”只对同时拥有已认证参战者和 orgFlow 权威支援差事的已封战报开放。请求只携带战报号；服务端重新读取玩家云存档并复核战报摘要，随后从 knowledge-jizhan 读取本关已发布 AKU、从 AINPC 读取每名参战者与本战匹配的正式记忆、从 orgFlowEngine 读取每项支援差事的完整行迹，最后由 NexusKernel `dongzhou_battle_debrief 1.0.0` 合卷。参战者记忆尚未异步送达时返回可重试状态，页面不会用浏览器战报文本补造回忆；展示层只显示人物、史证与行迹计数，不泄漏 AKU key、NPC 数字号或任务 UUID。

推进月令会由 AINPC 协调 orgFlow 的月例察访规则。若左儒已有同类非终态任务，orgFlow 以确定顺序选出权威任务并把任务号写入 `SKIPPED / duplicate_active_task` 触发记录；东周再通过签名管理接口反查组织、任务类型和责任人，官署直接展示任务标题、当前状态与最终结果。历史触发在迁移时只按同一严格条件回填，无法追溯的记录明确标为引用不可用，不会猜测绑定。

玩家可在官署主动停办或恢复月例察访。浏览器为未确认请求保留同一请求号，断线重试不会重复改版；网关每次重新读取稳定规则号、组织、游戏服、杜伯/左儒的成员号与 NPC 号、任务码、频率、关卡参数和当前版本，orgFlow 只接受期望版本一致的状态变化。NexusKernel `dongzhou_organization_scheduled_duty 1.0.0` 封存变更前后状态和版本；状态未变化时封存同版无操作，真实变化必须严格递增一版。官署标题取自同一权威规则的 `stage_title`，不泄漏通用模板的英文内部标题。停办不撤销已经派出的权威任务，页面继续显示其标题和办理状态。月例任务已归属其他玩家时，新会话只读显示并标记为不可收养，不抢占原所有者，也不再把正常的多会话查看误报为 502。

月例察访的权威任务会登记到当前玩家的官署任务簿；成功或部分完成后生成一次性的“下一场战事”侦察支援。战后存档不信任浏览器的跨关卡标记或加成数值，而是重新核对 orgFlow 任务所有权、月例规则号、左儒责任人、`court-monthly-intelligence` 权威范围、结案结果与 NexusKernel 封印，并按权威任务类型和成功/部分完成状态重算军粮、士气、攻防或侦察效果，随后在战报回执中封存合计值并标记 `scope=next_battle`。同一支援一经某份已封战报消费，后续战报再次引用会被服务端拒绝；把侦察 `+1` 篡改为其他数值也无法取得战报封印。

月例察访在登记规则前会先核验司马与司徒的 AINPC 日程。排班服务暂不可用时，网关返回可重试的 `503 / ainpc_schedule_unavailable`，契约响应损坏时返回 `502 / ainpc_schedule_contract_invalid`，不再泄漏为无语义的服务器 `500`；服务恢复后同一入口可正常返回 `ACTIVE` 规则并继续派差。

AINPC 事件公聊现由东周正式实现 `NDLLMSendPublicMessage` 游戏服契约。回调必须匹配 NPC 当前 `loginRequestId`，旧轮次不会落账；NPC 还必须存在于东周注册目录。正文、人物和登录轮次摘要以稳定消息号幂等写入 SQLite，再由 NexusKernel `dongzhou_npc_public_notice 1.0.0` 封印。官署“官署告示”查询会重新读取 orgFlow 权威名册与 AINPC 当前登录轮次，仅展示当前在职且轮次摘要仍有效的属官公告；离职、未知、离线或已重登录属官的旧号令不能进入页面。玩家可把当前属官的告示“取为公议”：AINPC 军议前重新核对消息摘要、登录轮次与在职身份，NexusKernel `dongzhou_mandate_workflow 1.13.0` 签令前再次读取同一告示、当前轮次与 orgFlow 名册，并把告示回执同时封入军议、军令和后续组织差事；页面打开后若 NPC 重登录，旧公议也不能继续签令，切换官员、告示或史证后旧军议不会复用。

无可执行待办时，AINPC 现在无论生成快照是否位于核心地图，都直接采用固定 `SleepTree`，不再退回模型并因旧目录中的运行态 `Reborn` 被过滤而形成空链。东周网关严格实现 `ValidateBTParams / ExecuteBehavior`：只接受参数合法且网关已确认就绪的 `SleepTree`、`Reborn` 与东周专用 `DongzhouDutyTree`；其中当值树还必须通过下一段所述的事务编号与名称复合身份校验。休息和当值按声明时长持有同一物理 UID，结束后才回调。回调复合身份、物理 UID 与到期时间进入 SQLite outbox，网关重启不丢失；同 UID 同载荷只复用，冲突载荷返回 409。真实干净重启验收中 12 名 NPC 各生成并下发一条休息链，验收窗口内预检失败、空链、模型配置失败和提前完成均为 0。

其余 11 类日常当值不再落入旧游戏原子动作。AINPC 通过东周专用 `transaction2actions` 与默认链目录，把朝会、军阵、军粮、巡营、军情、外交、史策、军令、城防、募兵和祭告统一下发为无可伪造参数的 `DongzhouDutyTree`；事务编号、名称、计划号与行为链号由不可变执行上下文携带。网关启动后用 SQLite outbox 调用正式目录同步接口，追加该动作但不清理其他游戏目录；执行时严格复核 `9100101..9100111` 的编号和名称，按计划时长到期才回调。真实合同验收中 `9100104 / 巡察营垒` 在 3 秒后形成 `DELIVERED` 记录且回调一次，故意改名为“转运军粮”则返回 `422 / dongzhou_duty_identity_invalid`。

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

玩家本人仕途是独立的权威闭环：先由 orgFlow 写入 `officer_12` 仕籍，再通过 AINPC 与直属杜伯查询本人岗位目录、按名称申请、调阅待办、接受、申请改令、拒绝和复命；回应按钮会先自动同步 AINPC 待办，再用所选任务名绑定写操作，避免页面已读到 orgFlow 新任务但 AINPC 尚未建立会话上下文的竞态。改令提交后，页面会自动请杜伯裁定；orgFlow 向 AINPC 提供修改前后参数与原/拟议总时长，杜伯的决定再由 orgFlow 原子落账。浏览器只展示 AINPC 回信和 orgFlow 名册回读，不自行创建任务、改变状态或增加贡献。2026-11-15 真实验收中，`演练阵法`（`0e67784b...7446`）把总时长改为三日后经杜伯 `approve` 进入 `IN_PROGRESS`，封印摘要为 `d6b1db85...514e`；独立的 `巡察营垒`（`a0d18e35...6bdd`）拒绝后进入 `REJECTED`，封印摘要为 `59f2d420...3018`。

复命被直属主管退回时，官署不再沿用含糊的“复命”按钮。页面必须从 NexusKernel 已封存的 orgFlow 任务行迹中同时核对补件确认、玩家收件人和 `submit_supplement` 权限，才显示“提交补呈”；退回原因只从已接受的 `return_for_supplement` 回覆投影六种白名单原因码及最长 500 字的 `OTHER` 说明，连同成果确认号和补件确认号进入封印，私聊正文及额外动作参数不会下放。玩家刷新或隔日返回仍可直接看到主管要求，提交文案明确绑定原差事和补呈内容，并继续沿用原私聊锚点进入 orgFlow 的下一轮成果审核。确认缺失或尚未封存时只允许刷新，不能由浏览器自行推进状态。`test_core.py` 和 `test-organization-browser.js` 已覆盖字段防泄漏、首次复命、退回补件、补呈复核、贡献结算以及 390px 移动端布局。

请仕入口现在只使用 orgFlow 权威空缺返回的正式职位名。`officer_12` 仍是服务端内部席位键，但页面、玩家申请和杜伯回信统一显示“军府属官·第12席”，不会把内部键暴露给玩家。按钮会发送带正式职位名的明确交易命令，AINPC V2 将该句式路由到加入申请而不是只查询空缺，最终成员身份仍以 orgFlow 名册回读为准。真实无拦截 Chromium 已完成申请、入仕、显示直属杜伯、辞仕和席位释放，测试结束后权威空缺恢复为“军府属官·第12席”。

史官问对把 knowledge-jizhan 的知识竞赛规则落入当前战役。网关从本回已发布 AKU 的结构化人物录选取正确项，从其他关卡人物录选择三个干扰项；题面经 NexusKernel 生成稳定动作号和 SHA-256 题印，正确索引只保存在玩家隔离的服务端请求账本。题目限时 30 秒，答中 10 分，逾时或答错为 0 分；刷新可恢复未答题，同一题重复交卷只回放原结果，换答案或跨玩家交卷均拒绝。

答中后的问对结果会成为下一次同关军议的“史识凭据”。网关在签令前重新核验玩家、关卡、AKU、10 分结果摘要与 NexusKernel `SEALED` 回执，并要求 AINPC 军议问题携带同一史识印记；通过后由 `dongzhou_mandate_workflow 1.11.0` 封存并传给 orgFlowEngine，任务成功率增加 `3` 点。答错、跨玩家、跨关卡、错配史料、摘要篡改或只在前端构造字段均为零加成并拒绝伪造凭据；旧存档和未参加问对的军令保持兼容。

答题后还可在史官问对面板主动“验印”。网关只按当前玩家读取原始题目与权威答卷，重新调用 `dongzhou_knowledge_tournament` 生成题印和结果封印，并逐项比对状态、选项、正解、分数和回执；未答题返回冲突，换玩家查询返回不存在，浏览器本地篡改摘要不能改变验印结果。真实 Chromium 已在刷新恢复答题后取得同一 64 位摘要，并在桌面与 320px 视口显示模块、版本和验真结果。

玩家还可选定本回已发布 AKU 的具体出处，对当前在职属官执行“据史慰勉”。网关每次都重新读取 knowledge-jizhan 与 orgFlow 权威名册，不接受旧缓存中的史料或离职属官；以玩家、关卡和属官生成稳定事件号，通过 SQLite outbox 把 `appreciation +2` 送入 AINPC。同一玩家、关卡、属官即使刷新或换请求也只结算一次，换史料重放会被冲突保护拒绝。只有 AINPC 确认送达后，NexusKernel `dongzhou_npc_commendation 1.0.0` 才封存玩家、属官、AKU、出处与关系效果，浏览器写入官署存档并回读人物状态。

“据史问忆”把已存在的人物经历变成可操作玩法。网关重新核验当前已发布 AKU 与 orgFlow 在职名册，再通过 AINPC 正式短期记忆查询读取当前属官的权威记录：优先选择正文含 AKU 号、标题或出处的 `dialogue_choice`，没有匹配军议时才回退最近的 `system_message`，两类记录都不存在则明确返回 404。NexusKernel `dongzhou_npc_recollection 1.1.0` 同时封存记忆号、原文摘要、时间、来源、匹配方式和可供军议复核的 AINPC 原始回执；浏览器按稳定问忆号去重保存并自动取为当前军议旧事。后续军议会从 AINPC 再查同一记忆号与摘要，Nexus 军令继续封存该回执并交给 orgFlow 派差，不能凭本地文本构造或替换回忆。

相邻关卡行军不再只有固定耗粮。网关按同一对 knowledge-jizhan 地图节点分别核验 `campaign_progression`、`fixed_point` 和 `npc_dialog` 路线，并拒绝地图号、落点或向导对话结构不完整的结果。玩家可选奉诏直进（军粮 2）、官道驿行（军粮 3、士气 +6）或向导引路（军粮 1、士气 -4）；偏好随云档保存，但开战不会信任展示缓存，而是把最终方法重新交给服务端查询并由 NexusKernel `dongzhou_campaign_route` 模块封存。联网结果缺少 `SEALED` 回执时拒绝开战；通过后才一次结算，路线及双史料见证随战果进入正式战报。回执除 64 位摘要外还包含服务端 HMAC 证明，云档入库时会重新验签并核对目标关卡，删除路线或篡改耗粮、士气、知识见证都会被拒绝。验签后的路线名、路线号、回执和两端 AKU 继续进入实际参战属官的 AINPC 重要事件与长期记忆，官署战报同步展示路线和双史料封印。桌面端和 390px 移动端均已通过真实接口验收。

当前无拦截完整任务证据为：

- `live-kernel-mandate-complete44-evidence.json`：史证适配、签令、派差、复命和战斗承接。
- `live-authoritative-settlement.png`：贡献、功绩、结案摘要、NPC 事件和长期经历一致。
- `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json`：知识、军议、外交军令、游说、盟约门禁和云档恢复。
- `live-player-career-browser.json`：玩家请仕、可领目录、按名称领差、待办、受命、复命、直属审核和贡献 `0 -> 100`。
- `live-membership-browser.json`、`live-membership-joined.png`、`live-membership-released.png`：玩家以正式职位名申请“军府属官·第12席”，orgFlow 权威名册确认入仕与直属杜伯，随后辞仕并释放同一席位。
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
- `history-recollection-live.png`、`history-recollection-mobile-live.png`：真实 Chromium 选定第一回 AKU 后向左儒问忆，命中 AINPC 正式 `dialogue_choice`，由 NexusKernel 封印、自动取为军议旧事并写入云档；随后实际提交的 AINPC 军议保存了与问忆完全一致的记忆摘要，重复问忆仍保留一条稳定回执，桌面端与 320px 移动端无横向溢出。
- `npc-public-notice-live.png`、`npc-public-notice-council-live.png`、`npc-public-notice-mobile-live.png`：左儒使用当前真实登录轮次调用 AINPC 公聊游戏服契约，东周幂等落账并由 NexusKernel 封印；新访客经 orgFlow 在职名册与 AINPC 当前轮次双重过滤后只回读仍有效的正文与印记，并将该稳定消息号选入 AINPC 公议，保存的军议账本保留同一告示摘要；桌面端和 320px 移动端无横向溢出。
- `live-route-battle-memory129.json`：真实向导路线及第一、第二回 AKU 经 NexusKernel 验签后进入第二回战报，实际参战属官的 AINPC 记忆和官署战报均回读到同一路线与双史料封印。

## 当前验证基线

- 网关完整回归：`157 passed`；新增玩家路由门禁从 FastAPI 源码提取 49 个正式玩家端点，与浏览器客户端调用双向集合相等，并要求客户端导出的每个玩法方法都在 `game.js` 中实际调用，防止新增服务能力只停留在网关或形成前端幽灵入口。执行器与今日队列覆盖复合身份串线拒绝、旧部署降级和内部会话/终端/调试/数据源/LoongMemory/错误字段防泄漏；史识凭据覆盖正确封存、主动验印、据史慰勉、据史问忆、摘要篡改、跨玩家/关卡/史料隔离和 orgFlow 参数传递；公聊覆盖当前/过期登录轮次、重登录后旧告示隐藏、幂等落账、内核封印、在职过滤，以及告示进入公议后若轮次变化则拒绝签令。真实页面同时拒绝暴露 AINPC 情绪/记忆枚举、日程计划主键与 knowledge 内部关卡键；这些字段仍保留在 NexusKernel 验签和军令请求中。
- 上游源码回归：四个服务当前均为已提交、无已跟踪改动的 GitHub 精确提交；父仓库 gitlink、本地 HEAD 与远端 `dev-gzj` 分支由 `tools/verify-github-service-pins.py` 同时校验。源码回归只证明契约实现，不替代 live 验收。
- 前端：集成客户端、组织玩法、战斗系统、顾问、官署、军议、外交、战后复盘和战前资源事务浏览器测试全部通过；模拟器覆盖新版未完成军令恢复接口，新玩家启动不会因该必读接口被误判失败。
- 真实冒烟：四项能力在线；独立访客存档往返、版本冲突和玩家隔离通过；抽查第一、第四和第一百七十一关均返回已发布史料；左儒计划为连续 90 天、368 项东周事务，其中正式临时战报事务仅在携带东周事件绑定时通过校验。长期计划按 AINPC 契约只列可执行待办，休息由非活跃时段的运行时强制休息机制接管。
- 权威名册：12/12 NPC 状态与 90 天计划通过；真实浏览器显示心境、关系、性情、动机、当前执行事务、今日值守时窗和后续待办，当前玩家身份可映射为“你”，未知历史玩家不会泄漏到人情簿，杜伯可调阅但不可向自己派单。运行日程桌面和 390px 移动端均无溢出，证据为 `npc-runtime-schedule-live.png` 与 `npc-runtime-schedule-mobile-live.png`。
- 玩家仕途：真实浏览器无拦截确认正式岗位名和五个权威任务名均以完整中文显示；请仕申请发送“军府属官·第12席”而非内部 `officer_12`，并完成权威入仕、直属杜伯回读、辞仕和席位释放。后续完成 `输送粮秣` 受命、重大受阻登记、杜伯裁定恢复、复命审核、贡献档案封存，贡献余额从 `0` 增至 `100`。另一独立玩家真实完成 `演练阵法` 三日总时长改令，杜伯读取真实修改上下文并审核通过，任务进入 `IN_PROGRESS`；同一玩家随后拒绝 `巡察营垒`，任务进入 `REJECTED`。两项均取得 NexusKernel 封印，桌面及 390px 移动端无溢出。测试结束均辞仕并释放席位，证据为 `live-membership-browser.json`、`live-player-career-exception-browser.json`、`live-player-task-response-browser.json`、`live-player-task-response-browser.png` 与 `live-player-task-response-mobile.png`。
- 军需调拨：真实浏览器无拦截证明草案阶段零扣款、NexusKernel 签发后公共库藏 `60 -> 40`、军粮 `100 -> 112`、驳回零扣款；云档重载保持一致，同一请求回放不重复扣领。
- 属官进言：真实左儒进言返回 `COMPLETED / hasThought=true`，重要度多次实测为 `72-78`，动机路由为 `delayed`；真实 Chromium 完成进言、军议选中、Nexus 草案封存同一摘要和玩家驳回，未派发 orgFlow 差事；320px 长文自动换行且无横向溢出，证据为 `live-spontaneous-thought-mobile.png`。
- 军令入程：真实 Chromium 无拦截只发出 1 次日程中断请求，AINPC 正式日程 owner 返回并落下可校验回执，随后 orgFlow 任务 `SUCCESS`、玩家收纳复命、公共库藏 `40 -> 140`、军粮奖励、云档重载和战斗承接全部通过；证据为 `live-mandate-schedule-complete77.png`。
- 战后经历：真实 Chromium 无拦截通过 AINPC 军议取得参战凭证，由 NexusKernel 返回 `SEALED` 战报，再同时写入 AINPC 重要事件、长期系统消息和短期记忆归档；轮询读到唯一“繻葛之战告捷”记忆后，云档重载仍在官署人物经历与战报档案中可见。
- 战后情绪：真实 Chromium 无拦截写入新的繻葛之战胜报，v2 事件一次送达；AINPC 忽略冲突的模型状态候选，按 `protect/support/success` 规则持久化 `joy 78 / strong`，关联事件号与东周确定性计算一致，官署页面已回读显示。
- 史官问对：真实 Chromium 从第一回已发布 AKU 开题，公开题面不含正确索引；刷新后恢复同一题并答中，NexusKernel 返回 `SEALED` 结果，云档累计 10 分；随后主动验印从服务端原始记录重算并核对同一摘要，证据为 `knowledge-quiz-live.png` 与 `knowledge-quiz-mobile-live.png`。
- 行军择路：真实 Chromium 在桌面端选择向导引路，军粮 `100 -> 99`、士气 `70 -> 66`；390px 移动端选择官道驿行，军粮 `100 -> 97`、士气 `70 -> 76`。两次开战均重新读取真实 knowledge-jizhan 图谱并得到 `dongzhou_campaign_route 1.2.0 / SEALED` 回执和服务端证明；第二回真实战报还把向导路线及 `dongzhou_stage_001/002` 写入实际参战属官的 AINPC 长期记忆，证据为 `campaign-routes-desktop-live.png`、`campaign-routes-mobile-live.png` 与 `live-route-battle-memory129.json`。
- 本地交付：当前开发验收拓扑由本机网关/AINPC 进程和 orgFlow 容器组成，不使用 `config/local-delivery-manifest.json` 中 2026-11-15 的不可变发布包快照冒充当前交付。当前完成性证据是实时健康、现场浏览器验收、源码回归和 GitHub 精确指针；正式发布包仍须按其独立清单重新构建后验收。
- 版本交付：父仓库只记录 GitHub `ganzijie1` 下四个 `dev-gzj` 精确提交：AINPC `b119b1a1b6926dbd2978555594cba96bfcda7e10`、orgFlowEngine `2424605740160a9a3971be3ddc691dcc3aa17461`、knowledge-jizhan `0103bc4900091ed39c87abdbb1bceb2a5b583933`、NexusKernel `dfaa58ed1fd99e758812025c390cd9a5d9f363d6`。`tools/verify-github-service-pins.py` 拒绝内网 URL、非 GitHub `ganzijie1` remote、脏的已跟踪工作区，以及父 gitlink、本地 HEAD、远端分支三者不一致。

图谱路径增量把 knowledge-jizhan 的 graph 召回从“只有命中分数”补成可核验的最短路径证据。知识服务现在返回确定性选择的起点、完整节点、关系类型和跳数，并为路径节点批量补全 AKU 名称；东周只接受节点数等于跳数加一、关系数等于跳数且起点一致的路径。合格路径随六路召回进入 SHA-256 搜索回执、玩家简册、选证和后续军议/军令证据，页面以“牵连路径”直接展示史料之间的归属、前置、层级或上下级关联。真实查询返回 10/10 条带路径的 graph 结果；真实 Chromium 搜索“郑伯克段 周郑交质”取得 6 条已发布东周史料并展示一跳 `DEPENDS_ON` 路径，桌面和 390px 视口均通过，证据为 `graph-path-live.png`、`graph-path-mobile-live.png` 与 `fulltext-browser-restored.json`。

## orgFlow 追办与补救

orgFlow 东周目录 v4 已为外交、操练、谍报、巡察和军需五类差事配置权威派生规则。成功结案生成追办，部分完成生成追办，失败生成补救；派生深度限定为一层。东周服务端复核前序任务、根任务、触发结果、规则号、岗位与确定性任务号，再把已创建子任务登记给原玩家。子任务继承章节和岗位席位、成本为 0；席位责任人变化时按 orgFlow 当前实账同步，并按普通差事继续结案。真实父任务到子任务链路见 `test-live-orgflow-followup.js`、`live-orgflow-followup-complete86.json`、`live-orgflow-followup-lineage-complete86.json` 和同名 PNG。

## 非玩法边界

公网 TLS、可信回调网络和 Windows 宿主冷启动属于部署验收，不由浏览器玩法测试代替。生产公共库藏只接受 orgFlow 的结案奖励与签名调拨，余额不足时明确拒绝；本机验收环境可使用带审计原因和幂等键的签名额度来验证首次调拨，不能把该额度记作玩家产出。模型或上游服务不可用时保持明确失败，不静默切换本地伪结果。
