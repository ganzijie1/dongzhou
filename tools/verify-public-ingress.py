"""只读验证公开入口屏蔽内部回调，不发送任何业务写请求。"""
from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="真实公开 HTTPS 根地址")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ("", "/")):
        parser.error("--url 必须为不含凭据、路径或查询参数的 HTTPS 根地址")
    checks = [("/", 200), ("/api/dongzhou/v1/save", 401)] + [(path, 403) for path in (
        "/api/v1/NDLLMAllAILogin", "/api/v1/ainpc/login-ready",
        "/api/v2/NDLLMSendPrivateMessage", "/api/v1", "/api/v2",
        "/internal/v1/organization-tasks/dialogues/report",
        "/api", "/internal", "/redoc", "/openapi.json", "/docs", "/health/ready", "/metrics",
        "/api/dongzhou/v10/save", "/api/dongzhou/v1",
        "/api%2Fv1/NDLLMAllAILogin",
        "/api/dongzhou/v1/../../v1/NDLLMAllAILogin",
        "/api/dongzhou/v1/..%2f..%2fv1/NDLLMAllAILogin",
        "//api//v1//NDLLMAllAILogin",
    )]
    opener = build_opener(NoRedirect())
    results = []
    for path, expected in checks:
        try:
            with opener.open(Request(args.url.rstrip("/") + path, method="GET"), timeout=args.timeout) as response:
                status = response.status
        except HTTPError as error:
            status = error.code
            error.close()
        except (URLError, TimeoutError):
            status = "connection_failed"
        results.append({"path": path, "expected": expected, "actual": status, "passed": status == expected})
    passed = all(item["passed"] for item in results)
    print(json.dumps({"passed": passed, "scope": "read_only_public_route_checks",
                      "backendPortIsolationVerified": False, "checks": results}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
