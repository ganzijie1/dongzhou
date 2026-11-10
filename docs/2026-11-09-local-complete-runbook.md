# 东周本机完整版本运行手册

## 入口与交付包

- 游戏入口：`http://127.0.0.1:8780/`
- 东周网关镜像：`dongzhou-integration:20261111-local-complete35`
- AINPC 八角色镜像：`ainpc-app:v20261111-dongzhou-local-complete18`
- orgFlow API/Worker 镜像：`org-flow-engine:dongzhou-local-complete23`
- H5 完整包：`output/2026-11-11-dongzhou-integrated-h5-complete35.zip`
- H5 SHA256：`D0B95636DC057C1C25799612A68EC1781B2841451B329A615A7D8A069BD57C54`

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
- 官署可调阅所选属官参与的真实 AINPC 私聊作为“府中耳报”。取用的消息摘要会进入军议，NexusKernel 签令时重新核验原消息、参与者和摘要并封存证据；情报/外交任务据此增加 8 点成功率，其他任务增加 4 点。该入口不提供虚构的玩家回复功能。
- 每类官署任务会从真实 AINPC 日程选取与当前关卡最近的当值事务；军令签发前会重新校验计划号和事件号，并把角色状态、事件、日期及关卡范围封入 NexusKernel 摘要。orgFlow 任务简报会持久化同一当值事件，前端可直接查看“本关当值”。
- 无 API 拦截的真实浏览器已完成同一任务的签发、领命、成功复命、云存档重载和战斗承接；恢复过程没有创建重复任务。证据为 `live-kernel-mandate-complete12.json`、`live-kernel-mandate-complete12.png` 与 `live-kernel-mandate-complete12-mobile.png`。
- AINPC 八角色使用 `complete18` 镜像且健康；LoongEQ 与 LoongMemory 从容器内返回 `ready`，真实左儒决策返回 `COMPLETED`。
- orgFlow API/Worker 使用 `complete22` 镜像，通知意图无 `PENDING` 积压；真实晚到送达回执会以原通知 ID 对账，不会重复发私聊。
- 全文检索和已发布史料通过真实浏览器验收，没有 API 模拟。
- 正式外交链已通过无拦截真实浏览器验收：knowledge-jizhan 史料、AINPC 军议、NexusKernel 外交军令、orgFlow 任务、云端游说结果和盟约门禁完整贯通；本次真实结果为 `FAILURE`，页面正确拒绝结盟，云存档重载后仍一致。证据为 `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json` 与同名 PNG。
- NPC 日程会在派单和每次月令推进时刷新；执行期、结果确认期不会因经理或执行人的旧日程停在 `WAITING_ACTIVE`。AINPC 复命和网关 `CHAT_START / CHAT_TURN / DELIVERY_RESULT` outbox 均已 `DELIVERED`。
- `ainpc-duty-complete22` 真实验收已证明史料、军议、当值校验、NexusKernel 签令及 orgFlow 建单成功；任务 `d4496a8e-7de8-504a-ba90-ad35bcd243e4` 的简报含当值计划与事件。该任务当前仍停在 `MEMBER_RESPONSE_PENDING`，原因是现有 AINPC 消息持久化队列超时，因此本轮不将 NPC 自动回应和任务终态记为通过。
- NPC 当值状态现会计算为 `25-95` 的胜任度，并随 NexusKernel 授命摘要封存到 orgFlow 差事；月令结算使用封存分数调整成功概率，旧授命按中性 `65` 兼容。前端同时显示分数、档位、情绪和关系支持。
- `complete34` 增加“性格适岗”：网关只读调用 AINPC 正式人格档案并固定传入 `auto_initialize=false`，按军粮、整训、巡察、军情、外交五类差事计算不同适岗分。适岗因子进入胜任度，原始档案、信号和分数由 NexusKernel 封入军令并传给 orgFlowEngine；旧军令及未建档角色按中性因子兼容。真实部署读取左儒已有 `stubborn / smooth` 档案，整训适岗为 `56/100 (steady)`、人格因子为 `+1.2`、最终胜任为 `76/100`，未触发自动建档。
- `complete35` 增加“任务意愿”：AINPC Global 以只读接口返回已持久化动机，网关按军粮、整训、巡察、军情、外交五类差事做关键词归属，仅相关动机影响胜任度。动机快照、匹配信号、意愿分和因子由 NexusKernel 封入军令并写入 orgFlowEngine 摘要；旧军令、缺失快照和无关动机均按中性因子兼容。真实部署读取左儒已有“情报核验 35”，情报差事意愿为 `64/100 (willing)`、动机因子为 `+2.1`、最终胜任为 `75/100`；不存在的 NPC 返回空快照，不创建状态。
- `ainpc-readiness-complete23` 真实验收创建了 NexusKernel 授命及 orgFlow 任务 `cc47d078-f232-5d9a-a24f-afebf5269039`；任务简报已封存 `Readiness 72/100 (watch)`。任务仍为 `MEMBER_RESPONSE_PENDING`；浏览器随后因 Docker Desktop 引擎失联报 `Failed to fetch`，因此本轮只确认真实建单和胜任度传递，不将异步任务终态记为通过。
- 官署终态现增加第二个 NexusKernel 人在回路：orgFlowEngine 的贡献、功绩和终态先生成不可改写的封存凭据，玩家必须在官署选择“收纳复命”或“申斥”后才能推进月令。收纳才发放战前助益；申斥仍照录上游贡献与功绩，但取消战前助益或外交成功并扣减属官信任、关系。裁决按任务、玩家、结案摘要幂等保存，刷新和重试不会重复领奖或更换决定。
- 东周网关冷重启后，原存档、任务身份、失败终态和浏览器显示保持一致。
- H5 包含 172 个关卡、4038 个文件、2520 条角色语音和 1126 个情境音乐 cue；发布校验无错误。

验收记录位于 `output/integration-validation/`，其中最终只读检查为 `local-delivery-latest.json`，真实任务恢复验收为 `live-task-recovery-complete15.json`，正式外交链验收为 `live-diplomacy-acceptance-20261110-formal-diplomacy-complete17.json`。
