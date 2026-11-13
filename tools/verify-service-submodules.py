from __future__ import annotations

import configparser
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "services/knowledge-jizhan": "https://github.com/ganzijie1/knowledge-jizhan.git",
    "services/ainpc": "https://github.com/ganzijie1/ainpc.git",
    "services/orgFlowEngine": "https://github.com/ganzijie1/orgFlowEngine.git",
    "services/NexusKernel": "https://github.com/ganzijie1/NexusKernel.git",
}


def git(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def main() -> None:
    modules = configparser.ConfigParser()
    modules.read(ROOT / ".gitmodules", encoding="utf-8")
    failures: list[str] = []

    for relative_path, expected_url in EXPECTED.items():
        section = f'submodule "{relative_path}"'
        directory = ROOT / relative_path
        if not modules.has_section(section):
            failures.append(f"{relative_path}: missing .gitmodules entry")
            continue
        if modules.get(section, "url", fallback="") != expected_url:
            failures.append(f"{relative_path}: unexpected GitHub URL")
        if modules.get(section, "branch", fallback="") != "dev-gzj":
            failures.append(f"{relative_path}: branch must be dev-gzj")
        if not directory.is_dir():
            failures.append(f"{relative_path}: directory is not initialized")
            continue

        stage = git("ls-files", "--stage", "--", relative_path).split()
        if len(stage) < 2 or stage[0] != "160000":
            failures.append(f"{relative_path}: parent does not record a gitlink")
            continue
        pinned_commit = stage[1]
        actual_commit = git("rev-parse", "HEAD", cwd=directory)
        if actual_commit != pinned_commit:
            failures.append(
                f"{relative_path}: checked out {actual_commit[:12]}, expected {pinned_commit[:12]}"
            )
        origin = git("remote", "get-url", "origin", cwd=directory)
        if origin != expected_url:
            failures.append(f"{relative_path}: origin is not the sanitized GitHub repository")
        try:
            branch_commit = git(
                "rev-parse",
                "refs/remotes/origin/dev-gzj",
                cwd=directory,
            )
        except RuntimeError:
            failures.append(f"{relative_path}: origin/dev-gzj is not available")
        else:
            if branch_commit != pinned_commit:
                failures.append(
                    f"{relative_path}: pinned {pinned_commit[:12]}, "
                    f"origin/dev-gzj is {branch_commit[:12]}"
                )

    if failures:
        raise SystemExit("Service submodule verification failed:\n- " + "\n- ".join(failures))
    print(f"PASS: {len(EXPECTED)} service submodules are initialized and pinned")


if __name__ == "__main__":
    main()
