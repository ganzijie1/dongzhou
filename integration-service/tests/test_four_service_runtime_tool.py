from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import verify_four_service_runtime as verifier  # noqa: E402


def _bundle() -> dict:
    path = (
        ROOT
        / "services"
        / "orgFlowEngine"
        / "config"
        / "organizations"
        / "dongzhou_court_v7.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _status() -> dict:
    seal = verifier.expected_source_seal()
    services = {}
    for name, source in verifier.SERVICE_SOURCES.items():
        services[name] = {
            "online": True,
            "sourceBranch": source["sourceBranch"],
            "sourceRevision": source["sourceRevision"],
            "integrationRevision": source["integrationRevision"],
            "reportedSourceBranch": source["sourceBranch"],
            "reportedSourceRevision": source["sourceRevision"],
            "sourceSealDigest": seal,
        }
    services["nexusKernel"].update(
        {
            "requiredModuleCount": 22,
            "operationalModuleCount": 22,
            "sourceBoundModuleCount": len(verifier.EXPECTED_SOURCE_BOUND_MODULES),
            "sourceBoundModules": sorted(verifier.EXPECTED_SOURCE_BOUND_MODULES),
            "unavailableModules": [],
            "serviceProvenanceState": "ready",
            "sourceProvenance": {"kernel": {"state": "SEALED"}},
        }
    )
    services["knowledge"]["sourceAttested"] = True
    services["aiNpc"]["sourceAttested"] = True
    services["orgFlow"]["sourceAttested"] = True
    services["nexusKernel"]["sourceAttested"] = True
    return {"mode": "connected", "services": services}


def test_source_seal_matches_the_frozen_runtime_manifest() -> None:
    assert verifier.expected_source_seal() == (
        "2ee936f94c275651d6284387d88ef92ecca659b4ec9eedb87225c404e080607b"
    )


def _source_receipt() -> dict:
    trace = verifier.public_service_sources()
    return {
        **trace,
        "digest": verifier.canonical_digest(trace),
        "kernel": {
            "module": "dongzhou_service_provenance",
            "moduleVersion": "1.0.0",
            "nexusKernelVersion": "0.2.0",
            "state": "SEALED",
        },
    }


def test_source_provenance_receipt_requires_exact_services_digest_and_kernel() -> None:
    assert verifier.validate_source_provenance_receipt(_source_receipt()) == {
        "services": 4,
        "sourceSealDigest": verifier.expected_source_seal(),
    }

    for mutation in ("service", "digest", "kernel", "extra"):
        receipt = deepcopy(_source_receipt())
        if mutation == "service":
            receipt["services"]["aiNpc"]["sourceRevision"] = "0" * 40
        elif mutation == "digest":
            receipt["digest"] = "0" * 64
        elif mutation == "kernel":
            receipt["kernel"]["state"] = "UNSEALED"
        else:
            receipt["unexpected"] = True
        with pytest.raises(ValueError, match="source provenance"):
            verifier.validate_source_provenance_receipt(receipt)


def test_orgflow_bundle_contract_accepts_the_tracked_v7_asset() -> None:
    assert verifier.validate_orgflow_bundle(_bundle()) == {
        "releaseTier": "FORMAL",
        "templateVersion": 7,
        "slots": 13,
        "tasks": 5,
    }


@pytest.mark.parametrize("mutation", ["slot", "task", "capacity"])
def test_orgflow_bundle_contract_rejects_dongzhou_drift(mutation: str) -> None:
    bundle = _bundle()
    template = bundle["templates"][0]["payload"]
    if mutation == "slot":
        template["slots"].pop()
    elif mutation == "task":
        bundle["task_catalogs"][0]["payload"]["tasks"].pop()
    else:
        template["capacity_tiers"][0]["member_capacity"] = 5
    with pytest.raises(ValueError):
        verifier.validate_orgflow_bundle(bundle)


def test_bundle_comparison_is_structural_not_line_ending_sensitive() -> None:
    bundle = _bundle()
    equivalent = json.loads(json.dumps(bundle, ensure_ascii=False))
    verifier.compare_bundles(bundle, equivalent)
    changed = deepcopy(bundle)
    changed["templates"][0]["version"] = 8
    with pytest.raises(ValueError, match="differs"):
        verifier.compare_bundles(bundle, changed)


def test_live_status_requires_all_pinned_services_and_modules() -> None:
    seal = verifier.expected_source_seal()
    detail = verifier.validate_live_status(_status(), seal)
    assert detail["onlineServices"] == 4
    assert detail["nexusModules"] == 22
    assert detail["sourceBoundModules"] == 20

    offline = _status()
    offline["services"]["aiNpc"]["online"] = False
    with pytest.raises(ValueError, match="aiNpc is offline"):
        verifier.validate_live_status(offline, seal)

    drifted = _status()
    drifted["services"]["knowledge"]["sourceRevision"] = "0" * 40
    with pytest.raises(ValueError, match="sourceRevision"):
        verifier.validate_live_status(drifted, seal)

    unattested = _status()
    unattested["services"]["knowledge"]["sourceAttested"] = False
    with pytest.raises(ValueError, match="did not attest"):
        verifier.validate_live_status(unattested, seal)

    unattested_ainpc = _status()
    unattested_ainpc["services"]["aiNpc"]["sourceAttested"] = False
    with pytest.raises(ValueError, match="aiNpc runtime did not attest"):
        verifier.validate_live_status(unattested_ainpc, seal)

    unattested_orgflow = _status()
    unattested_orgflow["services"]["orgFlow"]["sourceAttested"] = False
    with pytest.raises(ValueError, match="orgFlow runtime did not attest"):
        verifier.validate_live_status(unattested_orgflow, seal)

    unattested_nexus = _status()
    unattested_nexus["services"]["nexusKernel"]["sourceAttested"] = False
    with pytest.raises(ValueError, match="NexusKernel runtime did not attest"):
        verifier.validate_live_status(unattested_nexus, seal)

    misreported = _status()
    misreported["services"]["orgFlow"]["reportedSourceRevision"] = "0" * 40
    with pytest.raises(ValueError, match="reportedSourceRevision"):
        verifier.validate_live_status(misreported, seal)

    incomplete = _status()
    incomplete["services"]["nexusKernel"]["operationalModuleCount"] = 21
    with pytest.raises(ValueError, match="not fully operational"):
        verifier.validate_live_status(incomplete, seal)

    source_unbound = _status()
    source_unbound["services"]["nexusKernel"]["sourceBoundModules"].pop()
    source_unbound["services"]["nexusKernel"]["sourceBoundModuleCount"] = 17
    with pytest.raises(ValueError, match="not fully source-bound"):
        verifier.validate_live_status(source_unbound, seal)


def test_gateway_readiness_requires_all_four_attested_services() -> None:
    ready = {
        "status": "healthy",
        "requiredServices": ["knowledge", "aiNpc", "orgFlow", "nexusKernel"],
        "unavailableServices": [],
        "sourceDriftServices": [],
    }
    verifier.validate_gateway_readiness(ready)

    drifted = deepcopy(ready)
    drifted["status"] = "degraded"
    drifted["unavailableServices"] = ["nexusKernel"]
    drifted["sourceDriftServices"] = ["nexusKernel"]
    with pytest.raises(ValueError, match="readiness is not healthy"):
        verifier.validate_gateway_readiness(drifted)


def test_cli_has_no_publish_or_write_mode() -> None:
    source = (ROOT / "tools" / "verify_four_service_runtime.py").read_text(
        encoding="utf-8"
    )
    assert '"--publish"' not in source
    assert '"--write"' not in source
    assert '"--execute"' not in source
