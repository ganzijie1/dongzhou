# AINPC 策士回答投递恢复

东周“问策士”通过 AINPC AI Helper 生成回答，再由游戏服回调写入东周网关。此前如果回答已经生成，但 `/api/v2/NDLLMSendLittleElfMessage` 临时失败，AINPC 只留下失败日志，不会再次投递；东周问题会一直停在 `PROCESSING`。

AINPC `c94119d4f` 补齐了最终回答的持久恢复：

- 首次投递失败时，在 `ai_helper_call_logs` 保存 `chatId`、首次敏感词过滤后的冻结回答和重试状态。
- Global 实例按 Mongo 原子租约领取到期记录，多实例不会同时领取同一回答。
- 重试只发送冻结回答，不重复知识检索、模型生成或敏感词过滤，因此不会产生第二份内容，也不会与东周的回答幂等校验冲突。
- 失败采用指数退避，最长间隔 300 秒，累计 12 次仍失败后进入 `FAILED`，留给人工核查，不会无限制造回调流量。
- 进程退出时停止领取；已领取但未提交的租约到期后可由新实例继续恢复。

## 验收

- repository 生成一致性：114 个 repository 全部通过 `--check`。
- AINPC 定向回归：69 项全部通过。
- AI Helper 全套：177 项通过、13 项跳过；唯一既有失败是冒烟脚本把 ask task ID 固定为 `ai-helper-smoke-ask-1`，而旧测试仍期待时间戳 ID，与本次文件无交集。
- 新 Global 镜像 `ainpc-app:v20261113-dongzhou-local-ai-helper-retry77` 已健康运行，容器内生成代码包含 `delivery_retry_due_1` 复合索引。
- 无 API 拦截 Chromium 从东周页面完成问策士、回调、显示和“准确”反馈。问题号为 `e49f3c1a-30b5-484b-8f02-a333f2d19d3b`，回答已进入 `ANSWERED`。

旧问题 `9cd889f7-f75b-4c9e-9dd2-2e5615bc9464` 在升级前已经生成回答但回调失败；本次通过相同正式回调恢复为 `ANSWERED`，没有直接改写网关数据库。旧日志缺少 `chatId`，因此不会被新循环猜测性重放；自动恢复只适用于升级后保存了完整投递身份的记录。
