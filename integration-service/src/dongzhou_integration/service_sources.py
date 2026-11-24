from __future__ import annotations

from typing import Any

SERVICE_NAMES = ("knowledge", "aiNpc", "orgFlow", "nexusKernel")

SERVICE_SOURCES: dict[str, dict[str, str]] = {
    "knowledge": {
        "submodulePath": "services/knowledge-jizhan",
        "mirrorUrl": "https://github.com/ganzijie1/knowledge-jizhan.git",
        "sourcePath": "E:/game/knowledge-jizhan",
        "sourceUrl": "ssh://git@git.nd.com.cn:10022/AIGames/knowledge-jizhan.git",
        "sourceBranch": "main",
        "sourceRevision": "45afa2ffe77faea0622e8d3ed3f2b69c0cab9c56",
        "integrationRevision": "660d65b2b5f1ab667812ebb1d73c91aadcdc5a03",
    },
    "aiNpc": {
        "submodulePath": "services/ainpc",
        "mirrorUrl": "https://github.com/ganzijie1/ainpc.git",
        "sourcePath": "E:/game/ainpc",
        "sourceUrl": "ssh://git@git.nd.com.cn:10022/AIGames/ainpc.git",
        "sourceBranch": "develop",
        "sourceRevision": "82b7a7e02bccceb283563cee9929e29610d6ebf5",
        "integrationRevision": "808edf68f20b012d5c17bfad7aa130b6a1f884ed",
    },
    "orgFlow": {
        "submodulePath": "services/orgFlowEngine",
        "mirrorUrl": "https://github.com/ganzijie1/orgFlowEngine.git",
        "sourcePath": "E:/game/orgFlowEngine",
        "sourceUrl": "ssh://git@git.nd.com.cn:10022/AIGames/orgFlowEngine.git",
        "sourceBranch": "develop",
        "sourceRevision": "8b1049e965719d31c51772dde799737e9b92e918",
        "integrationRevision": "fbfc803b264c2c1e1dffe80c8da1bb5caa676cc3",
    },
    "nexusKernel": {
        "submodulePath": "services/NexusKernel",
        "mirrorUrl": "https://github.com/ganzijie1/NexusKernel.git",
        "sourcePath": "E:/game/NexusKernel",
        "sourceUrl": "ssh://git@git.nd.com.cn:10022/AIGames/NexusKernel.git",
        "sourceBranch": "develop",
        "sourceRevision": "190abb1fa889e40aa08dbc6efaaba6fe4940ca6d",
        "integrationRevision": "4f1915b45eadf8608308f7131173d1d60f6c5270",
    },
}

if tuple(SERVICE_SOURCES) != SERVICE_NAMES:
    raise RuntimeError("service source manifest order does not match SERVICE_NAMES")


def public_service_source(service: str) -> dict[str, str]:
    source = SERVICE_SOURCES[service]
    return {
        "sourceBranch": source["sourceBranch"],
        "sourceRevision": source["sourceRevision"],
        "integrationRevision": source["integrationRevision"],
    }


def public_service_sources() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "services": {
            service: public_service_source(service)
            for service in SERVICE_NAMES
        },
    }
