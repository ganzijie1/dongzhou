from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config" / "gameplay-evidence.json"


def test_current_gameplay_evidence_is_present_and_tracked() -> None:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert document["schemaVersion"] == 1
    assert document["scope"] == "current-executable-gameplay-evidence"
    groups = document["evidence"]
    assert set(groups) == {
        "crossServiceContracts",
        "browserWorkflows",
        "liveWorkflows",
        "readOnlyAcceptance",
    }

    entries = [item for values in groups.values() for item in values]
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
