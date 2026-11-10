"""Offline reference-config and checker contracts; NOT nginx or firewall acceptance."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import posixpath
import re
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def parse_reference(text):
    # Deliberately reject syntax outside this simple reviewed reference; this is
    # not an nginx parser and must not be used as a replacement for nginx -t.
    tokens = re.findall(r"#[^\n]*|[{};]|[^\s{};]+", text)
    tokens = iter(token for token in tokens if not token.startswith("#"))

    def block(nested=False):
        result, head = [], []
        for token in tokens:
            if token == "}":
                if head or not nested:
                    raise ValueError("Unexpected closing brace")
                return result
            if token == "{":
                if not head:
                    raise ValueError("Unnamed block")
                result.append((tuple(head), block(True)))
                head = []
            elif token == ";":
                result.append((tuple(head), None))
                head = []
            else:
                head.append(token)
        if nested or head:
            raise ValueError("Unclosed directive or block")
        return result

    return block()


class ReferenceContract(unittest.TestCase):
    def setUp(self):
        self.tree = parse_reference((ROOT / "config/nginx-dongzhou-production.conf.example").read_text(encoding="utf-8"))
        servers = [children for head, children in self.tree if head == ("server",)]
        self.assertEqual(len(servers), 2)
        self.public, self.private = servers

    def directives(self, body):
        return [head for head, children in body if children is None]

    def route(self, body, request_path):
        # Only exact/prefix locations are supported by the reference. Percent and
        # dot normalization cases below are structural expectations, not an nginx run.
        normalized = posixpath.normpath("/" + unquote(request_path).lstrip("/"))
        if request_path.endswith("/") and normalized != "/":
            normalized += "/"
        candidates = []
        for head, children in body:
            if not head or head[0] != "location":
                continue
            self.assertIn(len(head), (2, 3))
            modifier = head[1] if len(head) == 3 else ""
            self.assertIn(modifier, ("", "=", "^~"))
            prefix = head[-1]
            if modifier == "=" and normalized == prefix:
                return self.directives(children)
            if modifier != "=" and normalized.startswith(prefix):
                candidates.append((len(prefix), self.directives(children)))
        return max(candidates)[1] if candidates else []

    def test_public_denies_sensitive_prefixes_and_normalized_paths(self):
        for path in ("/api", "/api/v1", "/api/v2/NDLLMSendPrivateMessage",
                     "/internal", "/internal/v1/organization-tasks/dialogues/report",
                     "/docs", "/redoc", "/openapi.json", "/health", "/metrics",
                     "/api%2Fv1/NDLLMAllAILogin", "/api/dongzhou/v1/../../v1/NDLLMAllAILogin"):
            with self.subTest(path=path):
                self.assertIn(("return", "403"), self.route(self.public, path))

    def test_only_browser_api_prefix_is_forwarded(self):
        self.assertIn(("proxy_pass", "http://dongzhou_gateway"), self.route(self.public, "/api/dongzhou/v1/save"))
        self.assertIn(("return", "403"), self.route(self.public, "/api/dongzhou/v10/save"))
        self.assertIn(("return", "403"), self.route(self.public, "/api/dongzhou/v1"))

    def test_tls_private_acl_and_loopback_upstream(self):
        self.assertIn(("listen", "443", "ssl"), self.directives(self.public))
        self.assertIn(("ssl_protocols", "TLSv1.2", "TLSv1.3"), self.directives(self.public))
        self.assertIn(("listen", "10.0.0.10:8782"), self.directives(self.private))
        acl = [head for head in self.directives(self.private) if head[0] in ("allow", "deny")]
        self.assertEqual(acl, [("allow", "10.0.0.0/24"), ("deny", "all")])
        upstream = next(body for head, body in self.tree if head == ("upstream", "dongzhou_gateway"))
        self.assertIn(("server", "127.0.0.1:8780"), self.directives(upstream))
        self.assertIn(("return", "404"), self.route(self.private, "/api/dongzhou/v1/save"))


class CheckerContract(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("public_ingress_checker", ROOT / "tools/verify-public-ingress.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def run_checker(self, status):
        seen = []

        class Opener:
            def open(self, request, timeout):
                seen.append((request.full_url, request.get_method()))
                code = 200 if request.full_url.endswith("/") else 401 if request.full_url.endswith("/api/dongzhou/v1/save") else status
                if code == 200:
                    class Response:
                        status = 200
                        def __enter__(self): return self
                        def __exit__(self, *args): return False
                    return Response()
                if code is None:
                    raise URLError("offline synthetic failure")
                raise HTTPError(request.full_url, code, "synthetic", {}, None)

        stdout = io.StringIO()
        with patch.object(sys, "argv", ["verify-public-ingress.py", "--url", "https://test.invalid"]), patch.object(self.module, "build_opener", return_value=Opener()), contextlib.redirect_stdout(stdout):
            result = self.module.main()
        return result, json.loads(stdout.getvalue()), seen

    def test_all_probes_are_read_only(self):
        code, body, seen = self.run_checker(403)
        self.assertEqual(code, 0)
        self.assertTrue(body["passed"])
        self.assertTrue(all(method == "GET" for _, method in seen))
        self.assertFalse(body["backendPortIsolationVerified"])
        self.assertIn(("https://test.invalid/api/dongzhou/v1/save", "GET"), seen)

    def test_redirect_exposure_and_connection_failure_fail_closed(self):
        for status in (200, 301, 307, 404, 405, None):
            with self.subTest(status=status):
                code, body, _ = self.run_checker(status)
                self.assertEqual(code, 1)
                self.assertFalse(body["passed"])

    def test_redirect_handler_does_not_follow(self):
        self.assertIsNone(self.module.NoRedirect().redirect_request(None, None, 302, "", {}, "https://elsewhere.invalid"))

    def test_http_credentials_and_path_urls_are_rejected_before_network(self):
        for url in ("http://test.invalid", "https://a:b@test.invalid", "https://test.invalid/private", "https://test.invalid/?x=1"):
            with self.subTest(url=url), patch.object(sys, "argv", ["verify-public-ingress.py", "--url", url]), patch.object(self.module, "build_opener") as network, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.module.main()
                network.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
