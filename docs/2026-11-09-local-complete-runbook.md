# 东周本机完整版本运行手册

## 入口与交付包

- 游戏入口：`http://127.0.0.1:8780/`
- 东周网关镜像：`dongzhou-integration:20261112-local-complete82`
- AINPC 八角色镜像：`ainpc-app:v20261112-dongzhou-local-complete61`
- orgFlow API/Worker 镜像：`org-flow-engine:dongzhou-local-complete27`
- H5 完整包：`output/2026-11-11-dongzhou-integrated-h5-complete69.zip`
- H5 SHA256：`8776541A490913DDEE6C180693E5DFE834D73E2706B61C5792D2056F162D1766`

东周入口、AINPC 网关和 AINPC Mongo 分别只监听 `127.0.0.1:8780`、`127.0.0.1:9130` 和 `127.0.0.1:27117`。Docker Desktop 已登记为当前 Windows 用户登录后自动启动；各长期容器使用 `unless-stopped`。

## 日常检查

```powershell
cd E:\game\dongzhou
python tools\check-local-delivery.py --output output\integration-validation\local-delivery-latest.json
```

检查成功时 `passed` 为 `true`。它只做健康、镜像、端口、交付包和既有验收报告核对，不登录、不下令、不创建任务。

## 东周网关重建

```powershell
cd E:\game\dongzhou\integration-service
docker compose --env-file .env -f compose.yaml up -d --force-recreate gateway
```

本机 HTTP 入口必须使用 `DONGZHOU_ENV=development` 和 `DONGZHOU_PUBLIC_ORIGIN=http://127.0.0.1:8780`。`production` 模式要求 HTTPS，不适用于当前回环入口。`.env` 含凭据并已由 Git 忽略，不得提交或复制到报告。

东周存档位于具名卷 `dongzhou-diplomacy-candidate-data-20261109`。不要运行 `docker compose down -v`、`docker volume prune`，也不要改动 `.env` 中的数据卷名。部署前 SQLite 在线备份为：

`backups/2026-11-09-dongzhou-integration-predeployment.sqlite3`

## AINPC 最终镜像

最终覆盖文件：

`E:\game\ainpc\docker\v2\docker-compose-dongzhou-local-complete.yml`

AINPC 状态根必须保持为 `E:/game/.runtime/ainpc/v2`。八个角色分属两个既有 Compose 项目，不要用单一项目执行全栈 `down/up`，也不要运行 `down -v`、setup 或 finalize。Mongo 回环收敛前备份为：

`E:\game\ainpc\backups\2026-11-09-mongo-pre-loopback-v2`

AINPC 容器通过宿主回环代理访问 LoongEQ、LoongMemory、输入预检、敏感词、RAGFlow 和精确检索。计划任务 `Dongzhou-LoongEQ-Loopback-Proxy` 在当前用户登录时自动启动，监听仅限 `127.0.0.1` 的 `8000`、`8040`、`8041`、`8090`、`8230`、`8231`、`10010`。代理脚本位于 `tools/loongeq-loopback-proxy.py`，启动脚本位于 `tools/start-loongeq-loopback-proxy.ps1`；不得将监听地址改为公网网卡。

## 已验收内容

- NexusKernel 以嵌入式运行内核接入并处于 `ready`；真实 `orgFlow / AINPC / knowledge-jizhan` 上游均在线。
- 官署玩法现已形成强制四服务闭环：knowledge-jizhan 提供本回史料和可选出处，玩家必须选定出处后才能召集 AINPC 属官据证军议；NexusKernel 将所选书目、史料层级、适用范围、原文链接与 SHA-256 摘要一并封存进军令，orgFlowEngine 仅受理携带匹配军令号、摘要和出处的任务；复命结果随战备进入战斗，战后军令结案。
- 官署可调阅所选属官参与的真实 AINPC 私聊作为“府中书问”。玩家也可直接传话给已上线属官：网关以稳定玩家身份、幂等请求号和已登记会话调用 AINPC 正式入站私聊接口，AINPC 的回复仍经游戏服回调落库后显示。每位玩家只能读取发给自己的回复；取用的消息摘要会进入军议，NexusKernel 签令时重新核验原消息、参与者和摘要并封存证据；情报/外交任务据此增加 8 点成功率，其他任务增加 4 点。
- 每类官署任务会从真实 AINPC 日程选取与当前关卡最近的当值事务；军令签发前会重新校验计划号和事件号，并把角色状态、事件、日期及关卡范围封入 NexusKernel 摘要。orgFlow 任务简报会持久化同一当值事件，前端可直接查看“本关当值”。
- 无 API 拦截的真实浏览器已在同一任务 `cd9d873a-9264-53d1-bfc0-90048f909f11` 上完成签发、领命、成功复命、玩家收纳复命、云存档重载和战斗承接；断点恢复没有创建重复任务。证据为 `live-kernel-mandate-complete38-race-fixed.json` 与 `live-kernel-mandate-complete40-final.png`。
- AINPC 八角色使用 `complete54` 镜像且健康；LoongEQ 与 LoongMemory 从容器内返回 `ready`，真实左儒决策返回 `COMPLETED`，府中书问可从 Business 角色调用 orgFlowEngine 只读组织知识；过期持久日程会在重试前丢弃旧状态，避免恢复循环。
- orgFlow API/Worker 使用 `complete24` 镜像；真实晚到送达回执会以原通知 ID 对账，不会重复发私聊，公共库藏和组织名册使用独立只读权限回读。
- 全文检索和已发布史料通过真实浏览器验收，没有 API 模拟。
- 正式外交链已通过无拦截真实浏览器验收：knowledge-jizhan 史料、AINPC 军议、NexusKernel 外交军令、orgFlow 任务、云端游说结果和盟约门禁完整贯通；本次真实结果为 `FAILURE`，页面正确拒绝结盟，云存档重载后仍一致。证据为 `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json` 与同名 PNG。
- NPC 日程会在派单和每次月令推进时刷新；若 90 天计划生成超过网关 30 秒响应预算，页面会继续轮询计划号，只有主管和属官的新计划都已持久化才推进月令。执行期、结果确认期不会因过期日程停在 `WAITING_ACTIVE`。本次真实任务的 AINPC 复命和网关 `ORG_REPORT_START / CHAT_START / CHAT_TURN / DELIVERY_RESULT` outbox 均已 `DELIVERED`。
- `ainpc-duty-complete22` 曾记录任务 `d4496a8e-7de8-504a-ba90-ad35bcd243e4` 停在 `MEMBER_RESPONSE_PENDING` 的历史故障；`complete20` 已修复长通知触发的内容策略上游失败，且 `complete38-race-fixed` 真实验收已证明 NPC 自动领命、复命、审核和终态完整通过。
- NPC 当值状态现会计算为 `25-95` 的胜任度，并随 NexusKernel 授命摘要封存到 orgFlow 差事；月令结算使用封存分数调整成功概率，旧授命按中性 `65` 兼容。前端同时显示分数、档位、情绪和关系支持。
- `complete34` 增加“性格适岗”：网关只读调用 AINPC 正式人格档案并固定传入 `auto_initialize=false`，按军粮、整训、巡察、军情、外交五类差事计算不同适岗分。适岗因子进入胜任度，原始档案、信号和分数由 NexusKernel 封入军令并传给 orgFlowEngine；旧军令及未建档角色按中性因子兼容。真实部署读取左儒已有 `stubborn / smooth` 档案，整训适岗为 `56/100 (steady)`、人格因子为 `+1.2`、最终胜任为 `76/100`，未触发自动建档。
- `complete35` 增加“任务意愿”：AINPC Global 以只读接口返回已持久化动机，网关按军粮、整训、巡察、军情、外交五类差事做关键词归属，仅相关动机影响胜任度。动机快照、匹配信号、意愿分和因子由 NexusKernel 封入军令并写入 orgFlowEngine 摘要；旧军令、缺失快照和无关动机均按中性因子兼容。真实部署读取左儒已有“情报核验 35”，情报差事意愿为 `64/100 (willing)`、动机因子为 `+2.1`、最终胜任为 `75/100`；不存在的 NPC 返回空快照，不创建状态。
- `complete37` 将“府中书问”补成双向玩法。`POST /api/dongzhou/v1/npcs/{hero_id}/messages` 接收玩家传话，登记 PLAYER/NPC 会话后转发 AINPC；回调未重复携带 `playerInfo` 时，网关从同任务的封存参与者恢复目标身份，避免回复已落库但列表不可见。真实部署已验证左儒回复、回调入库、玩家隔离与 H5 读取完整闭环。
- AINPC `complete19` 将 Business 组织模块已有的只读知识服务纳入公开 typed contract。玩家询问组织任务或贡献时，私聊流水线会调用 orgFlowEngine、校验响应身份并按权限表达结果；不再因 `ModuleCallStub` 缺少 `open_knowledge` 无条件降级。真实验证中知识视图返回 `ok`，贡献视图按当前玩家权限返回 `denied`，两者均保持服务端授权边界。
- AINPC `complete20` 将长组织通知按最多 800 字、64 字重叠的片段逐段送入 AIFirewall；任一片段被替换即整体拦截，任一调用失败仍整体不可用，保持 fail-closed。原 1038 字通知已从上游 `502` 恢复为正式策略判定，orgFlow 随后自动重试并完成同一任务。
- `ainpc-readiness-complete23` 曾因 Docker Desktop 引擎失联只确认胜任度传递；其异步终态缺口已由后续 `complete38-race-fixed` 同任务全链验收覆盖。
- 官署终态现增加第二个 NexusKernel 人在回路：orgFlowEngine 的贡献、功绩和终态先生成不可改写的封存凭据，玩家必须在官署选择“收纳复命”或“申斥”后才能推进月令。收纳才发放战前助益；申斥仍照录上游贡献与功绩，但取消战前助益或外交成功并扣减属官信任、关系。裁决按任务、玩家、结案摘要幂等保存，刷新和重试不会重复领奖或更换决定。
- `complete42` 将 orgFlowEngine 的权威任务终态同时回写 AINPC 重要事件和长期系统消息。两条事件使用独立 outbox 重试，只有两者均送达时簿书才显示“经历已形成”；网关升级时会按已封存结果幂等补齐旧任务缺失的长期记忆，不重算成败或奖励。真实任务 `b2b66b37-732c-507b-970d-fb0ff7511698` 与 `cd9d873a-9264-53d1-bfc0-90048f909f11` 已在 AINPC `ops_reports` 持久化为左儒的可读经历，稳定消息号均为 `dongzhou-org-outcome:<task_id>`。
- `complete43` 将 AINPC 协同加成收紧为属官到当前主管的具体关系：正向好感与有效上下级关系加分，厌恶或仇恨扣分，其他人物的关系不再误入胜任度。主管 ID、好感、有效关系和最终因子随 NexusKernel 军令封存，任务簿显示 `协同+N/-N`。真实只读验收确认左儒当前对主管杜伯无关系记录，因此军粮当值为 `协同+0`，没有人工补造状态。
- `complete44` 让史料选择和 AINPC 军议结论真正进入结算：来源层级、出处范围、军议与差事类型的匹配、检索回执分别形成信号，合计封存为 `0-9` 的史证适配度。新差事按封存分数替代旧的固定知识加成，旧军令仍按中性 `6` 兼容；NexusKernel 军令、orgFlow 简报和官署簿书共同显示同一值。
- `complete75` 将公共库藏军需调拨纳入 NexusKernel `1.2.0` 确认工作流：草案阶段不扣账，签发后才调用 orgFlow 权威负数调整并凭收据增加军粮，驳回零支出；签发动作、上游幂等键和云档效果可跨刷新恢复且不可重复落账。
- `complete76` 将 AINPC 自主念头接入军议：当前属官会依据本回史料、出处、当值、人格和动机形成真实进言并触发动机路由；完整进言与稳定提案按请求幂等封存，只有提案被军议选中才由 NexusKernel 封入军令。真实 Chromium 已完成 `COMPLETED -> 军议选中 -> REQUIRES_ACTION -> REJECTED`，没有派发 orgFlow 差事；320px 页面无横向溢出，证据为 `live-spontaneous-thought-mobile.png`。
- `complete78` 将已签军令接入 AINPC 正式日程中断：签发后先由 `schedule-interrupts` owner 按急报、当前当值和游戏时钟裁定并实际插入今日或未来日程，再派发 orgFlow 差事。日程事件号从军令摘要稳定派生，客户端请求与服务端回执均可重放且不重复插程；回执随军令簿、差事和云档保存。真实无拦截 Chromium 只发出 1 次日程请求，随后完成任务 `SUCCESS`、收纳复命、库存 `40 -> 140`、战前军粮奖励、云档重载及战斗承接，证据为 `live-mandate-schedule-complete77.png`。
- `complete79` 将 AINPC 入程从浏览器流程约定提升为网关硬门禁：任何携带 NexusKernel 军令的 orgFlow 派差，必须先反查到同一玩家、军令号和摘要的已完成日程裁定记录；直接调用派差 API、入程失败、跨玩家或篡改摘要均不能绕过。真实无拦截 Chromium 已在原任务 `3c859b7e-6c76-5531-90ee-bfa41a84fd17` 上续跑完成知识检索、军议、急报裁定、NexusKernel 签令、AINPC 入程、orgFlow 执行与直属审核、战斗支援和云档重载，终态为 `SUCCESS`，库存 `140 -> 240`，证据为 `live-mandate-schedule-gate-complete79b.json` 与同名 PNG。
- `complete80` 将层级升级后的历史终态任务恢复为严格只读：AINPC 可继续查询已结案差事的 `snapshot`，orgFlow 会按当前名册复核组织、主管、岗位、责任人与直属关系；领命、复命等写操作和所有未终态任务仍要求原层级版本完全一致。真实历史任务 `2b8be328-e06a-5d53-9d36-1d288d1cf3e0` 的层级版本为 `1`、当前组织版本为 `8`，部署 `complete27` 后同一次轮询由 `503` 恢复为 `200`，AINPC 随即停止重复轮询，没有重开任务或产生业务写入。真实无拦截 Chromium 随后同时验证人物状态与日程最终响应为 `200`，页面没有“正在恢复”或“暂不可用”文案，证据为 `live-office-npc-state-complete80.png`。
- `complete81` 将战后回报写入实际参战属官的 AINPC 认知链：军议、军令或筹备中的权威属官各获得一条 `NPC_BATTLE_OUTCOME` 重要事件和一条 `NPC_BATTLE_MEMORY` 长期系统消息，未参与或未知角色不会收到。战报、云存档和两类事件在同一 SQLite 事务提交，稳定事件号支持跨月重放去重；同号异文会冲突并整体回滚。真实无拦截 Chromium 完成繻葛之战回报、云档重载和官署档案回读；公子吕两条 outbox 一次送达，周幽王两条在 AINPC 短暂不可用后于第 7 次自动重试送达，最终四条均为 `DELIVERED` 且错误清空。证据为 `live-battle-memory-complete81.json` 与同名 PNG。`DELIVERED` 表示 AINPC 正式回调已接收，不替代其下游异步记忆整理状态。
- `complete82` 为战后重要事件补齐服务器权威标准语义。胜利以 `protect/support/success`、失败以 `system/battle_loss/failure` 进入 AINPC，服务端强度与确认状态优先于模型候选；旧 `complete81` 战报通过 v2 稳定事件号补投递，不重复长期消息。真实无拦截 Chromium 以独立玩家写入繻葛之战胜报，AINPC 最终状态精确为 `joy 78 / strong`，关联事件号 `1635409062`、理由 `standard event protect/support: success`，云档重载后官署页面可见。证据为 `live-battle-emotion-complete82.json` 与同名 PNG。
- `complete62` 已将当前四服务结果补成玩家可读界面：府中书问以稳定访客隔离并显示正式人物名，orgFlow 名册显示 12 席谱系、贡献余额、累计收支与直属主管，AINPC 主动来信偏好显示真实同步状态，90 天当值计划显示起止日期、首日事项和计划印记。对应无拦截验收为 `live-correspondence-acceptance.png`、`live-roster-ledger.png`、`live-interaction-preference.png` 与 `live-schedule-browser.png`。
- `complete64` 将 orgFlow 权威名册的 12 席全部合并进可操作官员集合，不再只显示当前关卡的两名角色。新增成员使用游戏正式中文名并将内部岗位编号映射为可派差官职；既有忠诚、疲劳与关系状态保留。真实无拦截浏览器已逐席确认 12/12 AINPC 均为 `READY`，可调阅性情、动机和 90 日当值，证据为 `live-office-roster-browser.json` 与同名 PNG。
- `complete67` 开放玩家申请 `officer_12` 军府属官席位，并显示直属杜伯与 orgFlow 权威贡献账户。入仕只以权威名册回写为成功，最长等待 180 秒；辞仕需要界面二次确认后才发送明确退出请求。真实无拦截浏览器已完成入仕、名册回读、辞仕和席位释放，证据为 `live-membership-browser.json`、`live-membership-joined.png` 与 `live-membership-released.png`。
- `complete69` 补全玩家作为属官的仕途闭环：入仕后可向杜伯查询本人岗位的可领目录，按具体名称申请任务，调阅待办，接受任务并提交口头复命。AINPC `complete57` 将这些固定界面命令确定性路由到既有组织事务，orgFlow 继续负责候选校验、任务状态、直属审核和贡献结算。真实无拦截玩家从 `officer_12` 领取并完成 `Intelligence mission`，杜伯审核通过，贡献余额由 `0` 增至 `100`，随后辞仕释放席位；证据为 `live-player-career-browser.json` 与 `live-player-career-browser.png`。
- 东周网关冷重启后，原存档、任务身份、失败终态和浏览器显示保持一致。
- H5 包含 172 个关卡、4038 个文件、2520 条角色语音和 1126 个情境音乐 cue；发布校验无错误。

验收记录位于 `output/integration-validation/`。当前史证适配四服务闭环为 `live-kernel-mandate-complete44-evidence.json`，任务 `2b8be328-e06a-5d53-9d36-1d288d1cf3e0` 以 `史证 2/9（弱）` 进入 NexusKernel、orgFlow、复命裁决与战斗承接并最终 `SUCCESS`；正式外交链验收为 `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json`。
