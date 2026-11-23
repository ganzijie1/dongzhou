from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "tools" / "verify-service-submodules.py"
SPEC = spec_from_file_location("verify_service_submodules", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VERIFIER = module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def test_remote_branch_commit_accepts_one_exact_branch(monkeypatch) -> None:
    revision = "a" * 40
    monkeypatch.setattr(
        VERIFIER,
        "git",
        lambda *args: f"{revision}\trefs/heads/develop",
    )

    assert VERIFIER.remote_branch_commit("ssh://git.example/repo.git", "develop") == revision


@pytest.mark.parametrize(
    "output",
    [
        "",
        f"{'a' * 40}\trefs/heads/develop\n{'b' * 40}\trefs/heads/main",
        f"{'a' * 40}\trefs/tags/develop",
        "short\trefs/heads/develop",
    ],
)
def test_remote_branch_commit_rejects_ambiguous_or_invalid_output(
    monkeypatch, output: str
) -> None:
    monkeypatch.setattr(VERIFIER, "git", lambda *args: output)

    with pytest.raises(RuntimeError, match="invalid"):
        VERIFIER.remote_branch_commit("ssh://git.example/repo.git", "develop")
