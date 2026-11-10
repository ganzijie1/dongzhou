# 东周四服务生产接入

> 本文保留四服务接入设计背景；本机最终镜像、端口、哈希和恢复命令以 `docs/2026-11-09-local-complete-runbook.md` 为准。

浏览器只访问 `dongzhou-integration-service`。该服务基于 NexusKernel，持有服务端存档、玩家会话、幂等记录和上游凭据；H5 不直接访问 AINPC、orgFlowEngine 或 knowledge-jizhan。

本次交付范围已由用户确认为这台电脑长期运行的完整联网版本，入口为 `http://127.0.0.1:8780/`；最新部署后真实服务验收 9/9 PASS，“查史料—NPC军议—NexusKernel签发军令—orgFlow派差—真实复命—战斗反馈—军令结案”已通过无拦截浏览器验收。当前网关镜像为 `dongzhou-integration:20261110-local-complete14`，AINPC 八角色为 `ainpc-app:v20261110-dongzhou-local-complete14`，orgFlow API/Worker 为 `org-flow-engine:dongzhou-local-complete22`。运行与恢复边界见 `docs/2026-11-09-local-complete-runbook.md`。下述公网发布条件供未来公开部署使用，不阻塞当前本机交付。宿主冷启动尚未实际演练，运行依赖 Docker 引擎就绪，上游模型故障仍须按真实失败处理。

## 发布顺序

1. 发布 knowledge-jizhan 数据镜像，确认镜像包含 `AI使用的知识库/V3/dongzhou` 的 172 份 AKU。
2. 在 knowledge-jizhan 工作台登记新来源，执行 schema/内容一致性校验，发布并同步检索索引。管理模式不会自动导入。
3. 在 orgFlowEngine 运行 `python scripts/publish_dongzhou_catalog.py --publish`，发布 `config/organizations/dongzhou_court_v2.json`，用 `dongzhou_court` 模板建立官署并导入武将；把每个稳定武将 ID 与其实际占用的岗位 UUID 写入 `DONGZHOU_ORGFLOW_HERO_SLOTS`。未映射武将会拒绝派单，不会错派给其他成员。
4. 将 AINPC 的 `ORGANIZATION_TASK_SERVICE_BEARER_TOKEN` 以同值注入 `DONGZHOU_AINPC_TASK_TOKEN`。该令牌只用于服务端到期复命出站队列，禁止进入 H5、日志或存档。
5. 用 AINPC 仓库的 `docker/v2/docker-compose-dongzhou.yml` 叠加环境。日程事务目录唯一 owner 是 Gateway；Business 通过 typed proxy 读取 Gateway，必须给 Gateway 配置 `AINPC_CONST_CSV_SCHEDULE_TRANSACTIONS`，指向东周专用 12 类官署事务，不替换通用 CSV。当前本机 Gateway、Global、Business 固定为 `ainpc-app:v20261110-dongzhou-local-complete14`，由 `docker/v2/docker-compose-dongzhou-local-complete.yml` 统一覆盖。保留基础配置的 entrypoint、网络、挂载、端口和托管凭据；更新现有实例前按 Docker 标签保留每个服务原 Compose 项目归属，不能把不同项目的现有容器统一当作新项目创建。目录升级不会自动迁移已提交日程，必须通过正式重拟接口并回读验收。
6. 启动 AINPC V2 的 gateway、global、business 实例及其 NATS/Mongo/Redis 依赖，确认目标 NPC 已注册且 Actor 可用。Windows 宿主执行 Compose 时必须把 `AINPC_DATA_ROOT` 设为实际宿主目录（当前环境为 `E:/game/.runtime/ainpc/v2`）；容器内路径沿基础配置挂载，不因宿主路径不同而直接改容器目录。
7. 部署 integration gateway，执行 `/health/live`、`/health/ready` 和 `/api/dongzhou/v1/integration/status` 探测，再开放入口流量。

## 身份与真值

日程目录配置检查可运行 `integration-service/.venv/Scripts/python.exe tools/test-dongzhou-schedule-owner.py`。它仅解析合并配置、在无网络临时容器读取所选镜像目录，不启动 AINPC 服务或修改计划。已有计划的真值在 AINPC Mongo `schedule_plans`，按游戏服与 NPC 复合身份保存；`current` 直接返回已提交计划，非强制生成会复用当日可执行的旧计划，重启和更换目录不会自动迁移。先验收 Gateway 实际目录，再经授权对明确 NPC 调用正式重拟接口；`force_regenerate=true` 会产生真实规划并覆盖当前计划，不能在健康检查或修复验证中偷偷调用。迁移验收须核对完整 90 天的事务 ID 均为 `9100101..9100112`、无异游戏内容，并确认持久计划版本变化及重启读取一致。

- 玩家会话是 HttpOnly、SameSite=Strict 的签名 Cookie；原生客户端可用同一签名 Bearer。
- `hero_id` 通过固定 BLAKE2 映射为 AINPC 63 位正整数，重启和扩容后不变。
- 联网存档以服务端版本号为准，并发旧版本写入返回 `409`。
- 存档、到期复命出站事件及游戏时钟在同一 SQLite 事务提交，任何写入失败全部回滚。首次入队冻结复命结果，后续保存不覆盖结果，也不重新投递已完成事件；旧版本遗漏的复命在下一次保存时补入。
- 颁令请求在浏览器持久记录，受理回执确认写入云档后才清除。断线恢复重用原请求号，按远端任务号去重扣粮；云档冲突会阻止后续排队写入。
- 在线颁令必须先读取本回已发布史料并取得当前属官的 AINPC 军议。网关随后调用 NexusKernel 真实运行模块状态，签发包含关卡、属官、差事、史料、军议和内核版本的规范军令；摘要使用规范 JSON 的 SHA-256，orgFlowEngine 任务参数中的军令号或摘要不匹配时直接拒绝。
- 军令状态随任务从 `ISSUED` 进入 `ORDERED`，复命后进入 `FULFILLED`、`PARTIAL` 或 `FAILED`，战斗报告落档后进入 `RESOLVED`。军令、军议和史料证据随战备跨页面及云存档恢复，不以浏览器提示文字代替持久记录。
- 官署任务以 orgFlowEngine 正式虚拟任务终态为准。联网模式不会再用浏览器随机数结算。
- 到期复命出队前重新读取真实任务：只有 `IN_PROGRESS` 才创建 AINPC 复命；尚未领命等非终态保留队列，已终态直接结束该队列事件。旧版本提前创建的失败复命不能靠重复 POST 恢复，需核实 AINPC 的恢复轮次和管理接口，不能换新操作号绕过幂等。
- 颁令只有收到 `ACCEPTED` 和远端任务号后才扣粮、写入本地差事；拒单的幂等回放不会显示领命成功。提交期间禁用重复颁令，远端任务号与本地差事一并存档。
- 官署台账最多保留最近 40 条已结束差事，所有未复命差事继续保留；未投入战斗的筹备不随台账裁剪。持久序号独立于台账长度，旧存档从现有差事编号迁移。
- 战斗完整初始化成功后才提交战备消费，部署与开场脚本异常均回滚；消费日志在云保存失败后恢复，按战备业务 ID 去重，跨页面重叠消费只补云档中真实剩余份额。恢复无法写回云档时暂停进入游戏，避免沿用未消费的旧档。
- 官署差事的复命结果按任务基础难度、官职匹配、忠诚、疲劳和已查阅史料统一计算；相同存档与任务输入可重放，浏览器与服务端不再各算一套。
- knowledge-jizhan 不可用时返回 `503`；只有显式 `?offline=1` 才使用本地演算。
- 在线知识结果只接受 `dongzhou_stage_*` AKU。网关扩大候选召回后再做领域过滤，共享知识库中的其他游戏记录不会进入东周 H5。
- 官署“本回史料”通过 `/api/dongzhou/v1/knowledge/stages/{stage_id}` 按当前战役精确读取已发布 AKU，并加入玩家简册用于筹备。此入口不依赖 LLM 查询解析；本地目录仅映射关卡和 AKU 编号，在线正文仍来自 knowledge-jizhan。全文搜索故障时继续明确报错，不自动切换本地资料。
- 关卡编号使用目录映射，不能从 AKU 编号推算；例如 `dongzhou_stage_004` 对应 `03b`，并非关卡 `04`。

## 发布门禁

当前验收记录（2026-11-10）：全文检索已恢复；真实网关 9 项检查通过，AINPC 八角色健康且重启次数为零，LoongEQ 与 LoongMemory 从容器内返回 `ready`。无 API 拦截浏览器已验证属官状态、日程和真实决策，证据见 `output/integration-validation/live-integration-complete19.json` 与 `live-office-npc-state-complete19.png`。此前 503 保留为历史故障，不再作为当前阻塞项。这是本次功能恢复证据，实际公网 TLS、后端端口隔离、可信回调网络及宿主重启恢复仍需独立验收。

运行 `integration-service/.venv/Scripts/python.exe tools/verify-live-integration.py --url <网关地址> --output output/integration-validation/live-smoke.json` 验证真实健康、独立访客存档及冲突隔离、首中末关卡已发布史料、AI 检索、NPC 状态和 90 天日程。任一项失败则退出码非零；此检查不会派差或推进共享游戏时钟，不能代替任务复命与发布验收。

设置 `DONGZHOU_TEST_URL=<网关地址>` 后运行 `node tools/test-live-knowledge-browser.js`，直接从浏览器验证联网史料读取、展示和筹备记录；该测试不拦截或模拟 API。

- knowledge AKU schema 必须 `172/172` 通过，且工作台发布后用代表性人物、战役、军令各做召回验收。
- orgFlowEngine 必须覆盖重复 `source_event_id`、服务重试、部分完成、失败和终态回读。
- AINPC 必须覆盖 NPC 注册、情绪/关系读取、日程生成与读取、对话裁断的同一复合身份。
- AINPC 日程验收必须确认事务 ID 全部位于 `9100101..9100112`，且抽查结果不含“机体、银河币、天关、飞船”等其他游戏词汇。首次强制重拟可能由 Actor 异步完成；随后用非强制生成接口读取已提交计划，并用 current 接口确认完整 90 天日程。
- AINPC 私聊必须覆盖 `NDLLMChatWithPlayer`、`NDLLMSendPrivateMessage`、`QueryPrivateChatRuntimeState` 和 `ResetPrivateChatRuntimeState`。游戏服持久化消息并回调后才算送达；仅收到聊天请求不算成功。
- 网关必须覆盖 Cookie 失效恢复、存档版本冲突、跨玩家任务读取拒绝、上游超时和重启后的幂等重放。
- 普通私聊依赖 aiproxy 的投递/回调闭环；未提供并验收该外部服务前，不把“聊天已受理”显示为 NPC 回复。

## 本机运行核对与恢复边界

当前本机访问入口为 `http://127.0.0.1:8780/`。可运行以下只读检查，不创建会话、不调用模型、不派单、不写存档，也不推进游戏时钟：

```powershell
integration-service/.venv/Scripts/python.exe tools/check-local-delivery.py --output output/integration-validation/local-delivery-readonly-20261109.json
```

此工具核对本次交付的 11 个应用容器镜像标签，以及这 11 个应用和 9 个存储/知识依赖的运行、已有健康检查与 `unless-stopped` 重启策略；还检查页面/健康 HTTP、匿名存档拒绝访问及交付包 SHA256。依赖镜像版本不由此工具固定。没有健康检查的容器，其 running 不等同业务健康；本工具不覆盖宿主冷启动。版本变更后须同步工具中的期望发布版本和包哈希。

东周 orgFlow Compose 叠加层为 API 和 Worker 显式设置 `restart: unless-stopped`。该策略依赖 Docker 引擎已启动；手工停止的容器不会因此自动恢复。当前尚未进行宿主重启演练，也未证明 Windows 登录前 Docker Desktop 可用。不要为了检查恢复随意重启共享服务或重放已完成任务。公网 TLS 与全文检索的验收边界见上文发布门禁和 `production-ingress-isolation.md`。

## 镜像回退

回退 integration gateway 镜像不会回滚服务端存档或上游任务。先停止新流量，保留 `/data` 卷，再回退镜像。知识版本通过工作台建立新发布回退；orgFlow/AINPC 已受理的任务不得通过删除本地记录撤销。

AINPC 回退时同时回退东周派生镜像和 compose 叠加层；Mongo 中已生成的东周日程可继续读取。若回退到通用事务目录，必须先停止新日程生成，不能让同一游戏服并存两套事务 ID。
