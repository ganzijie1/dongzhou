from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_SOURCE = ROOT / "integration-service" / "src" / "dongzhou_integration" / "app.py"
CLIENT_SOURCE = ROOT / "web-game" / "integration-client.js"
GAME_SOURCE = ROOT / "web-game" / "game.js"
UPSTREAM_SOURCE = (
    ROOT / "integration-service" / "src" / "dongzhou_integration" / "upstreams.py"
)
UPSTREAM_CONTRACT_TEST = (
    ROOT / "integration-service" / "tests" / "test_upstream_contracts.py"
)

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
REQUEST_CALL = re.compile(
    r"request(?:WithTransientRetry)?\(\s*([`\"'])(.+?)\1",
    re.DOTALL,
)
TEMPLATE_EXPRESSION = re.compile(r"\$\{.*?\}")
PATH_PARAMETER = re.compile(r"\{[^{}]+\}")
REQUEST_METHOD = re.compile(
    r'^\s*,\s*\{\s*method\s*:\s*["\']([A-Z]+)["\']',
    re.DOTALL,
)
CONTRACT_ONLY_UPSTREAM_METHODS = {"request_npc_relogin"}


def _shape(path: str) -> str:
    path = path.split("?", 1)[0]
    path = TEMPLATE_EXPRESSION.sub("{}", path)
    return PATH_PARAMETER.sub("{}", path)


def _gateway_player_routes() -> set[tuple[str, str]]:
    tree = ast.parse(APP_SOURCE.read_text(encoding="utf-8"), filename=str(APP_SOURCE))
    routes: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not decorator.args:
                continue
            function = decorator.func
            if not (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "router"
                and function.attr in HTTP_METHODS
            ):
                continue
            path = decorator.args[0]
            if isinstance(path, ast.Constant) and isinstance(path.value, str):
                routes.add((function.attr.upper(), _shape(path.value)))
    return routes


def _client_routes(source: str) -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for match in REQUEST_CALL.finditer(source):
        path = match.group(2)
        if not path.startswith("/"):
            continue
        options = source[match.end() : match.end() + 256]
        declared = REQUEST_METHOD.match(options)
        method = declared.group(1) if declared else "GET"
        routes.add((method, _shape(path)))
    return routes


def _exported_client_methods(source: str) -> set[str]:
    matches = re.findall(r"^  return \{(.+?)\};$", source, flags=re.MULTILINE)
    assert matches, "integration client export object is missing"
    return {
        item.split(":", 1)[0].strip()
        for item in matches[-1].split(",")
        if item.strip() and not item.strip().startswith("isOffline:")
    }


def _public_upstream_methods() -> set[str]:
    tree = ast.parse(
        UPSTREAM_SOURCE.read_text(encoding="utf-8"), filename=str(UPSTREAM_SOURCE)
    )
    upstreams = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Upstreams"
    )
    return {
        node.name
        for node in upstreams.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }


def _called_attribute_names(*sources: Path) -> set[str]:
    called: set[str] = set()
    for source in sources:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        called.update(
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        )
    return called


def test_every_gateway_player_route_has_a_matching_browser_http_call() -> None:
    client = CLIENT_SOURCE.read_text(encoding="utf-8")
    gateway_routes = _gateway_player_routes()
    client_routes = _client_routes(client)

    assert len(gateway_routes) >= 45
    assert gateway_routes == client_routes


def test_every_exported_browser_client_method_is_used_by_the_game() -> None:
    client = CLIENT_SOURCE.read_text(encoding="utf-8")
    game = GAME_SOURCE.read_text(encoding="utf-8")
    exported = _exported_client_methods(client)
    unused = {
        method
        for method in exported
        if re.search(rf"\.{re.escape(method)}\s*\(", game) is None
    }

    assert len(exported) >= 50
    assert unused == set()


def test_career_reply_matcher_accepts_authoritative_task_action_phrases() -> None:
    game = GAME_SOURCE.read_text(encoding="utf-8")

    assert r"\u4ea4\u7ed9\u4f60|\u5b8c\u6210\u540e" in game
    assert r"\u4e0d\u63a5|\u91cd\u65b0\u5b89\u6392" in game
    assert (
        r"^\u3010\u4efb\u52a1\u4e8b\u9879(?:\u5f00\u59cb|\u7ed3\u675f)\u3011"
        in game
    )


def test_every_public_upstream_method_is_used_or_an_explicit_contract_probe() -> None:
    app_source = ROOT / "integration-service" / "src" / "dongzhou_integration" / "app.py"
    public = _public_upstream_methods()
    called = _called_attribute_names(app_source, UPSTREAM_SOURCE)

    assert len(public) >= 50
    assert public - called == CONTRACT_ONLY_UPSTREAM_METHODS
    contract_test = UPSTREAM_CONTRACT_TEST.read_text(encoding="utf-8")
    assert all(
        f"upstreams.{method}(" in contract_test
        for method in CONTRACT_ONLY_UPSTREAM_METHODS
    )
