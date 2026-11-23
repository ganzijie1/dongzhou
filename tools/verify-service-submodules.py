from __future__ import annotations

import configparser
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "services/knowledge-jizhan": {
        "mirror_url": "https://github.com/ganzijie1/knowledge-jizhan.git",
        "source_path": Path("E:/game/knowledge-jizhan"),
        "source_url": "ssh://git@git.nd.com.cn:10022/AIGames/knowledge-jizhan.git",
        "source_branch": "main",
        "source_commit": "45afa2ffe77faea0622e8d3ed3f2b69c0cab9c56",
    },
    "services/ainpc": {
        "mirror_url": "https://github.com/ganzijie1/ainpc.git",
        "source_path": Path("E:/game/ainpc"),
        "source_url": "ssh://git@git.nd.com.cn:10022/AIGames/ainpc.git",
        "source_branch": "develop",
        "source_commit": "8a7b673c6ddb93c5ac64d96a270b35619e5bcc1c",
    },
    "services/orgFlowEngine": {
        "mirror_url": "https://github.com/ganzijie1/orgFlowEngine.git",
        "source_path": Path("E:/game/orgFlowEngine"),
        "source_url": "ssh://git@git.nd.com.cn:10022/AIGames/orgFlowEngine.git",
        "source_branch": "develop",
        "source_commit": "8b1049e965719d31c51772dde799737e9b92e918",
    },
    "services/NexusKernel": {
        "mirror_url": "https://github.com/ganzijie1/NexusKernel.git",
        "source_path": Path("E:/game/NexusKernel"),
        "source_url": "ssh://git@git.nd.com.cn:10022/AIGames/NexusKernel.git",
        "source_branch": "develop",
        "source_commit": "190abb1fa889e40aa08dbc6efaaba6fe4940ca6d",
    },
}


def git(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def git_succeeds(*args: str, cwd: Path = ROOT) -> bool:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        check=False,
    )
    return result.returncode == 0


def main() -> None:
    modules = configparser.ConfigParser()
    modules.read(ROOT / ".gitmodules", encoding="utf-8")
    failures: list[str] = []

    for relative_path, expected in EXPECTED.items():
        expected_url = str(expected["mirror_url"])
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
        if git(
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            cwd=directory,
        ):
            failures.append(
                f"{relative_path}: contains uncommitted changes; the parent gitlink "
                "does not reproduce this workspace"
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
            if branch_commit != pinned_commit and not git_succeeds(
                "merge-base",
                "--is-ancestor",
                branch_commit,
                pinned_commit,
                cwd=directory,
            ):
                failures.append(
                    f"{relative_path}: pinned {pinned_commit[:12]} does not include "
                    f"origin/dev-gzj ({branch_commit[:12]})"
                )

        source_commit = str(expected["source_commit"])
        if not git_succeeds("cat-file", "-e", f"{source_commit}^{{commit}}", cwd=directory):
            failures.append(f"{relative_path}: GitLab source commit {source_commit[:12]} is missing")
        elif not git_succeeds(
            "merge-base", "--is-ancestor", source_commit, pinned_commit, cwd=directory
        ):
            failures.append(
                f"{relative_path}: pinned {pinned_commit[:12]} does not include "
                f"GitLab source {source_commit[:12]}"
            )

        source_path = Path(expected["source_path"])
        if source_path.is_dir():
            source_url = git("remote", "get-url", "origin", cwd=source_path)
            if source_url != expected["source_url"]:
                failures.append(f"{relative_path}: local source has an unexpected GitLab URL")
            source_branch = git("branch", "--show-current", cwd=source_path)
            if source_branch != expected["source_branch"]:
                failures.append(
                    f"{relative_path}: local source branch is {source_branch}, "
                    f"expected {expected['source_branch']}"
                )
            source_head = git("rev-parse", "HEAD", cwd=source_path)
            if source_head != source_commit:
                failures.append(
                    f"{relative_path}: local GitLab source is {source_head[:12]}, "
                    f"expected {source_commit[:12]}"
                )

    if failures:
        raise SystemExit("Service submodule verification failed:\n- " + "\n- ".join(failures))
    print(f"PASS: {len(EXPECTED)} service submodules are initialized and pinned")


if __name__ == "__main__":
    main()
