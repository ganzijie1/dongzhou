# 生产入口和内部游戏服回调隔离

当前提供的是可审阅的 Nginx 配置参考，未配置实际域名、TLS 证书、私网网卡或防火墙，也没有修改或重启现有服务。不能把配置存在等同于生产部署完成。

`config/nginx-dongzhou-production.conf.example` 使用两个监听入口：公开 HTTPS 入口仅向浏览器开放静态资源和 `/api/dongzhou/v1/`；私网入口仅允许可信服务网段访问 `/api/v1/`、`/api/v2/` 和健康检查。已有游戏服回调没有独立鉴权，必须隔离，尤其 `NDLLMAllAILogin` 会清理登录状态并触发重登，`ainpc/login-ready` 会更新登录状态。CORS 不能阻止直接 HTTP 请求。

## 部署条件

1. 替换示例域名、证书路径、`10.0.0.10` 和 `10.0.0.0/24`。可信网段应尽量精确，且不得包含普通访客设备。若服务与 Nginx 同机，可使用仅回环可达的内部监听。
2. `DONGZHOU_ENV=production`、`DONGZHOU_PUBLIC_ORIGIN` 使用真实 HTTPS 域名；浏览器持有 Secure Cookie。后端监听地址或 Docker 映射须限制到回环/服务私网，防火墙禁止从公网直接访问 `8780`、验证入口 `8781` 和内部监听 `8782`。只在反代拦截而让原端口公开并不安全。
3. AINPC 游戏服回调和 orgFlow 组织时钟查询指向内部入口；H5 使用公开入口。不要把内部 URL 下发给浏览器。内部网络须可信；跨不可信网络时增加 mTLS 或受控隧道，不能直接使用本示例的明文 HTTP。
4. 先用目标机器实际 Nginx 执行 `nginx -t`。证书和网络未准备好时停止发布，不绕过 TLS 或改用开发配置。
5. 外部客户端运行下方只读检查，确认回调路径均为 `403`，并从允许的服务网段验证内部健康检查可达。从禁止的网段验证内部入口不可达或 `403`。

```powershell
integration-service/.venv/Scripts/python.exe tools/verify-public-ingress.py --url https://实际域名
```

检查工具只发送 GET，不触发派差、登录、复命、存档写入。它检查页面可达、公开存档 API 未登录返回 401、内部路径及编码/归一化变体返回 403，并拒绝跟随重定向。结果中的 `backendPortIsolationVerified=false` 表示未验证后端原端口封锁，不能替代网络防火墙验收、证书更新演练或内部服务完整联调。当前尚未对真实生产入口运行此检查。

## 可重复的隔离验证

运行 `tools/test-production-ingress-contract.py` 可检查参考配置结构及检查器失败处理；它不是 Nginx 解析器。运行 `tools/test-production-ingress-nginx.py` 使用 Docker 内部临时网络、模拟上游和临时自签测试证书，实际执行 `nginx -t` 并检查公开/私有路由和可信来源 ACL，不发布宿主端口。脚本需要 Docker、OpenSSL 及官方 Nginx/Python 镜像，结束后清理本次测试容器和网络。

已实测通过：7 项离线合同测试、42 项真实 Nginx 路由检查。该结果只证明参考配置的隔离行为；`publicProductionAcceptance=false` 和 `testOnlyCertificate=true` 不得改写为真实公网部署已验收。

## 超时和军议结果

网关请求预算按 `DONGZHOU_UPSTREAM_TIMEOUT_SECONDS * 4 + 15` 秒计算，默认 135 秒；Nginx 参考读超时为 510 秒，覆盖上游配置允许的最大 120 秒时的网关 495 秒预算。外层负载均衡器也应覆盖这一预算。

AINPC 军议选择必须同时满足业务 `code=200`、存在结果对象、返回索引和类型属于本次候选。HTTP 200 内的业务失败不再记为完成，客户端可使用原请求 ID 重试。此规则不表示模型每次都可用；上游故障仍应显示为可重试错误。
