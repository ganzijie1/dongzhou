from __future__ import annotations

import json
from pathlib import Path
import subprocess

from dongzhou_integration.service_sources import public_service_sources


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config" / "gameplay-evidence.json"
COVERAGE = ROOT / "docs" / "four-service-gameplay-coverage.md"
LOCAL_SERVICE_SOURCES = ROOT / "web-game" / "scenario" / "service-sources.json"


def test_local_service_source_manifest_matches_runtime_pins() -> None:
    assert json.loads(LOCAL_SERVICE_SOURCES.read_text(encoding="utf-8")) == (
        public_service_sources()
    )


def test_current_gameplay_evidence_is_present_and_tracked() -> None:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert document["schemaVersion"] == 1
    assert document["scope"] == "current-executable-gameplay-evidence"
    groups = document["evidence"]
    assert set(groups) == {
        "crossServiceContracts",
        "browserWorkflows",
        "simulationWorkflows",
        "liveWorkflows",
        "externalInputWorkflows",
        "readOnlyAcceptance",
    }

    external = groups["externalInputWorkflows"]
    assert isinstance(external, dict) and external
    assert all(isinstance(reason, str) and reason for reason in external.values())
    entries = [
        item
        for name, values in groups.items()
        if name != "externalInputWorkflows"
        for item in values
    ] + list(external)
    assert len(entries) == len(set(entries))
    assert all((ROOT / item).is_file() for item in entries)

    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *entries],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert tracked.returncode == 0, tracked.stderr

    live_scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tools").glob("test-live-*.js")
    }
    browser_scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tools").glob("test-*-browser.js")
        if not path.name.startswith("test-live-")
    } | {"tools/test-organization-battle-transaction.js"}
    simulation_scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tools").glob("test-*.js")
    } - live_scripts - browser_scripts

    external_scripts = set(external)
    assert set(groups["liveWorkflows"]) | (external_scripts & live_scripts) == live_scripts
    assert set(groups["browserWorkflows"]) == browser_scripts
    assert (
        set(groups["simulationWorkflows"])
        | (external_scripts & simulation_scripts)
        == simulation_scripts
    )
    assert external_scripts <= live_scripts | simulation_scripts

    for item in live_scripts:
        source = (ROOT / item).read_text(encoding="utf-8")
        assert "DONGZHOU_TEST_URL" in source, f"{item} cannot target the active live deployment"

    expected_counts = (
        f"{len(groups['crossServiceContracts'])} 个跨服务契约、"
        f"{len(groups['browserWorkflows'])} 个浏览器流程、"
        f"{len(groups['simulationWorkflows'])} 个可直接运行模拟器、"
        f"{len(groups['liveWorkflows'])} 个可直接运行现场流程、"
        f"{len(groups['externalInputWorkflows'])} 个依赖外部输入的受限流程和 "
        f"{len(groups['readOnlyAcceptance'])} 个只读验收"
    )
    assert expected_counts in COVERAGE.read_text(encoding="utf-8")
