"""Verify the pinned four-service Dongzhou runtime without changing service state."""

from __future__ import annotations

import argparse
from http.cookiejar import CookieJar
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import urllib.request
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_SRC = ROOT / "integration-service" / "src"
sys.path.insert(0, str(INTEGRATION_SRC))

from dongzhou_integration.service_sources import (  # noqa: E402
    SERVICE_SOURCES,
    public_service_sources,
)


EXPECTED_SLOT_KEYS = {"commander", *(f"patrol_{index}" for index in range(1, 13))}
EXPECTED_TASK_CODES = {
    "dongzhou.diplomacy",
    "dongzhou.drill",
    "dongzhou.intelligence",
    "dongzhou.patrol",
    "dongzhou.supply",
}


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def expected_source_seal() -> str:
    return canonical_digest(public_service_sources())


def validate_orgflow_bundle(bundle: dict) -> dict:
    if bundle.get("schema_version") != 1 or bundle.get("release_tier") != "FORMAL":
        raise ValueError("orgFlow bundle must be schema 1 and FORMAL")

    templates = bundle.get("templates")
    catalogs = bundle.get("task_catalogs")
    if not isinstance(templates, list) or not isinstance(catalogs, list):
        raise ValueError("orgFlow bundle is missing templates or task catalogs")

    template = next(
        (item for item in templates if item.get("template_id") == "dongzhou_court"),
        None,
    )
    catalog = next(
        (item for item in catalogs if item.get("catalog_id") == "dongzhou_court_tasks"),
        None,
    )
    if not isinstance(template, dict) or template.get("version") != 7:
        raise ValueError("Dongzhou court template v7 is missing")
    if not isinstance(catalog, dict) or catalog.get("version") != 7:
        raise ValueError("Dongzhou court task catalog v7 is missing")

    payload = template.get("payload")
    catalog_payload = catalog.get("payload")
    if not isinstance(payload, dict) or not isinstance(catalog_payload, dict):
        raise ValueError("Dongzhou court payload is invalid")

    slots = payload.get("slots")
    slot_keys = {
        item.get("slot_key") for item in slots or [] if isinstance(item, dict)
    }
    if slot_keys != EXPECTED_SLOT_KEYS or len(slots or []) != len(EXPECTED_SLOT_KEYS):
        raise ValueError("Dongzhou court must contain commander plus patrol_1..patrol_12")

    tiers = payload.get("capacity_tiers")
    if not isinstance(tiers, list) or len(tiers) != 1:
        raise ValueError("Dongzhou court must define one initial capacity tier")
    tier = tiers[0]
    if (
        tier.get("member_capacity") != 13
        or set(tier.get("enabled_slot_keys") or []) != EXPECTED_SLOT_KEYS
        or tier.get("required_slot_keys") != ["commander"]
        or payload.get("final_member_upper_bound") != 13
    ):
        raise ValueError("Dongzhou court capacity contract is invalid")

    tasks = catalog_payload.get("tasks")
    task_codes = {
        item.get("task_code") for item in tasks or [] if isinstance(item, dict)
    }
    if task_codes != EXPECTED_TASK_CODES or len(tasks or []) != len(EXPECTED_TASK_CODES):
        raise ValueError("Dongzhou court must contain exactly five task definitions")
    if set(payload.get("allowed_task_codes") or []) != EXPECTED_TASK_CODES:
        raise ValueError("Dongzhou court allowed task codes do not match its catalog")

    reference = template.get("task_catalog_ref") or {}
    if (
        reference.get("catalog_id") != "dongzhou_court_tasks"
        or reference.get("version") != 7
        or not isinstance(reference.get("checksum"), str)
        or len(reference["checksum"]) != 64
    ):
        raise ValueError("Dongzhou court task catalog reference is invalid")

    return {
        "releaseTier": "FORMAL",
        "templateVersion": 7,
        "slots": len(slot_keys),
        "tasks": len(task_codes),
    }


def compare_bundles(rendered: dict, tracked: dict) -> None:
    if rendered != tracked:
        raise ValueError("rendered orgFlow bundle differs from the tracked v7 bundle")


def validate_live_status(status: dict, expected_seal: str) -> dict:
    if status.get("mode") != "connected":
        raise ValueError("integration gateway is not connected")
    services = status.get("services")
    if not isinstance(services, dict):
        raise ValueError("integration status has no service map")

    for service_name, source in SERVICE_SOURCES.items():
        service = services.get(service_name)
        if not isinstance(service, dict) or service.get("online") is not True:
            raise ValueError(f"{service_name} is offline")
        for field in ("sourceBranch", "sourceRevision", "integrationRevision"):
            if service.get(field) != source[field]:
                raise ValueError(f"{service_name} {field} does not match the pinned source")
        if service.get("sourceSealDigest") != expected_seal:
            raise ValueError(f"{service_name} source seal does not match the pinned manifest")

    if services["knowledge"].get("sourceAttested") is not True:
        raise ValueError("knowledge runtime did not attest its pinned GitLab source")
    if services["aiNpc"].get("sourceAttested") is not True:
        raise ValueError("aiNpc runtime did not attest its pinned GitLab source")
    if services["orgFlow"].get("sourceAttested") is not True:
        raise ValueError("orgFlow runtime did not attest its pinned GitLab source")
    if services["nexusKernel"].get("sourceAttested") is not True:
        raise ValueError("NexusKernel runtime did not attest its pinned GitLab source")

    nexus = services["nexusKernel"]
    if nexus.get("serviceProvenanceState") != "ready":
        raise ValueError("Nexus service provenance module is not ready")
    if (nexus.get("sourceProvenance") or {}).get("kernel", {}).get("state") != "SEALED":
        raise ValueError("Nexus source provenance is not sealed")
    required = nexus.get("requiredModuleCount")
    operational = nexus.get("operationalModuleCount")
    if not isinstance(required, int) or required < 20 or operational != required:
        raise ValueError("Nexus required modules are not fully operational")
    if nexus.get("unavailableModules") != []:
        raise ValueError("Nexus reports unavailable required modules")

    return {
        "mode": "connected",
        "onlineServices": len(SERVICE_SOURCES),
        "nexusModules": operational,
        "sourceSealDigest": expected_seal,
    }


def _python_executable() -> Path:
    candidate = ROOT / "integration-service" / ".venv" / "Scripts" / "python.exe"
    return candidate if candidate.is_file() else Path(sys.executable)


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def verify_source_pins(python: Path) -> dict:
    output = _run(
        [str(python), str(ROOT / "tools" / "verify-service-submodules.py")],
        cwd=ROOT,
    )
    return {"services": len(SERVICE_SOURCES), "detail": output}


def render_and_verify_orgflow(python: Path) -> dict:
    orgflow = ROOT / SERVICE_SOURCES["orgFlow"]["submodulePath"]
    tracked_path = orgflow / "config" / "organizations" / "dongzhou_court_v7.json"
    with TemporaryDirectory(prefix="dongzhou-orgflow-verify-") as directory:
        output = Path(directory) / "dongzhou_court_v7.json"
        env = dict(os.environ)
        existing_path = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(orgflow) + (os.pathsep + existing_path if existing_path else "")
        _run(
            [
                str(python),
                "scripts/publish_dongzhou_catalog.py",
                "--output",
                str(output),
            ],
            cwd=orgflow,
            env=env,
        )
        rendered = json.loads(output.read_text(encoding="utf-8"))
    tracked = json.loads(tracked_path.read_text(encoding="utf-8"))
    detail = validate_orgflow_bundle(rendered)
    compare_bundles(rendered, tracked)
    return {**detail, "trackedBundle": str(tracked_path.relative_to(ROOT)).replace("\\", "/")}


def _json_request(opener, method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with opener.open(request, timeout=45) as response:
        body = json.loads(response.read().decode("utf-8"))
    if body.get("success") is True and isinstance(body.get("data"), dict):
        return body["data"]
    return body


def verify_live(base_url: str, expected_seal: str) -> dict:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    base = base_url.rstrip("/")
    guest = _json_request(
        opener,
        "POST",
        f"{base}/api/dongzhou/v1/sessions/guest",
        {"installation_id": str(uuid4())},
    )
    if not guest.get("playerId"):
        raise ValueError("guest session has no player identity")
    status = _json_request(opener, "GET", f"{base}/api/dongzhou/v1/integration/status")
    return validate_live_status(status, expected_seal)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8766")
    parser.add_argument(
        "--skip-live",
        action="store_true",
        help="verify pinned source and generated assets without contacting the gateway",
    )
    args = parser.parse_args()
    python = _python_executable()
    seal = expected_source_seal()
    checks = {
        "sourcePins": verify_source_pins(python),
        "orgFlowBundle": render_and_verify_orgflow(python),
        "sourceProvenance": {
            "schemaVersion": 1,
            "services": len(SERVICE_SOURCES),
            "sourceSealDigest": seal,
        },
    }
    if not args.skip_live:
        checks["liveRuntime"] = verify_live(args.url, seal)
    report = {
        "result": "PASS",
        "mode": "read-only",
        "url": None if args.skip_live else args.url,
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
