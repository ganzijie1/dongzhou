"""Verify that the four gameplay services are reproducibly pinned to GitHub."""

from __future__ import annotations

import configparser
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVICES = {
    "services/ainpc": "ainpc",
    "services/knowledge-jizhan": "knowledge-jizhan",
    "services/NexusKernel": "NexusKernel",
    "services/orgFlowEngine": "orgFlowEngine",
}
BRANCH = "dev-gzj"


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise RuntimeError(detail)
    return result.stdout.strip()


def gitmodules() -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".gitmodules", encoding="utf-8")
    records: dict[str, dict[str, str]] = {}
    for section in parser.sections():
        if not section.startswith('submodule "'):
            continue
        path = parser.get(section, "path", fallback="")
        records[path] = {
            "url": parser.get(section, "url", fallback=""),
            "branch": parser.get(section, "branch", fallback=""),
        }
    return records


def parent_gitlink(path: str) -> str:
    row = git(ROOT, "ls-tree", "HEAD", "--", path)
    fields = row.split(None, 3)
    if len(fields) != 4 or fields[0] != "160000" or fields[1] != "commit":
        raise RuntimeError(f"{path} is not a gitlink")
    return fields[2]


def remote_urls(repo: Path) -> dict[str, set[str]]:
    records: dict[str, set[str]] = {}
    for line in git(repo, "remote", "-v").splitlines():
        fields = line.split()
        if len(fields) >= 2:
            records.setdefault(fields[0], set()).add(fields[1])
    return records


def verify() -> dict:
    modules = gitmodules()
    checks = []
    for path, repository in SERVICES.items():
        expected_url = f"https://github.com/ganzijie1/{repository}.git"
        module = modules.get(path, {})
        repo = ROOT / path
        link = parent_gitlink(path)
        local = git(repo, "rev-parse", "HEAD")
        tracked_changes = git(repo, "status", "--porcelain=v1", "--untracked-files=no")
        remotes = remote_urls(repo)
        origin_urls = remotes.get("origin", set())
        all_urls = {url for urls in remotes.values() for url in urls}
        remote_line = git(repo, "ls-remote", "origin", f"refs/heads/{BRANCH}")
        remote = remote_line.split()[0] if remote_line else ""
        passed = all(
            (
                module.get("url") == expected_url,
                module.get("branch") == BRANCH,
                link == local == remote,
                not tracked_changes,
                origin_urls == {expected_url},
                bool(all_urls) and all_urls == {expected_url},
            )
        )
        checks.append(
            {
                "path": path,
                "url": expected_url,
                "branch": BRANCH,
                "gitlink": link,
                "localHead": local,
                "remoteHead": remote,
                "trackedClean": not tracked_changes,
                "remoteNames": sorted(remotes),
                "passed": passed,
            }
        )
    return {
        "result": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "githubOwner": "ganzijie1",
        "branch": BRANCH,
        "services": checks,
    }


def main() -> int:
    try:
        report = verify()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        report = {"result": "FAIL", "error": str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
