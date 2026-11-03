"""Export Dongzhou's role-conditioned HAPPO actors for mobile inference."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

from rl.happo import HAPPO_ACTION_FEATURES, HAPPOActor, ROLE_NAMES
from rl.mappo import LOCAL_FEATURES


DEFAULT_MAX_CANDIDATES = 256
ONNX_OPSET = 15


class MobileHAPPOPolicy(nn.Module):
    """Select one actor with a float one-hot role input and mask padded actions."""

    def __init__(self, trained_roles: tuple[str, ...] = ROLE_NAMES) -> None:
        super().__init__()
        self.actors = nn.ModuleList(HAPPOActor() for _ in ROLE_NAMES)
        trained = set(trained_roles)
        self._trained = tuple(role in trained for role in ROLE_NAMES)
        self.register_buffer(
            "trained_role_mask",
            torch.tensor(
                [float(role in trained) for role in ROLE_NAMES], dtype=torch.float32
            ),
        )

    def forward(
        self,
        local: torch.Tensor,
        candidates: torch.Tensor,
        legal_mask: torch.Tensor,
        role_one_hot: torch.Tensor,
    ) -> torch.Tensor:
        # Keep all four ONNX inputs in the graph even for a checkpoint with no
        # trained roles, while producing exact zero logits for safe fallback.
        zero_logits = candidates[:, :, 0] * 0.0 + local[:, :1] * 0.0
        role_logits = torch.stack(
            [
                actor(local, candidates) if self._trained[index] else zero_logits
                for index, actor in enumerate(self.actors)
            ],
            dim=1,
        )
        selected = torch.sum(role_logits * role_one_hot.unsqueeze(-1), dim=1)
        role_is_trained = torch.sum(
            role_one_hot * self.trained_role_mask.unsqueeze(0), dim=1, keepdim=True
        )
        selected = torch.where(
            role_is_trained > 0.5, selected, torch.zeros_like(selected)
        )
        invalid = torch.full_like(selected, -1.0e4)
        return torch.where(legal_mask > 0.5, selected, invalid)


def load_policy(checkpoint: Path) -> MobileHAPPOPolicy:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if "actors" not in payload:
        raise ValueError(f"checkpoint has no actors state: {checkpoint}")
    if int(payload.get("action_features", HAPPO_ACTION_FEATURES)) != HAPPO_ACTION_FEATURES:
        raise ValueError("checkpoint action feature schema does not match runtime")

    raw_trained_roles = payload.get("trained_roles", ())
    trained_roles = tuple(str(role) for role in raw_trained_roles)
    unknown_roles = set(trained_roles) - set(ROLE_NAMES)
    if unknown_roles:
        raise ValueError(f"checkpoint contains unknown trained roles: {unknown_roles}")
    policy = MobileHAPPOPolicy(trained_roles)
    actor_state = payload["actors"]
    for index, role in enumerate(ROLE_NAMES):
        prefix = f"{role}."
        state = {
            key[len(prefix) :]: value
            for key, value in actor_state.items()
            if key.startswith(prefix)
        }
        if not state:
            raise ValueError(f"checkpoint has no actor for role {role}")
        policy.actors[index].load_state_dict(state)
    policy.eval()
    return policy


def sample_inputs(max_candidates: int, seed: int = 2026) -> tuple[torch.Tensor, ...]:
    generator = torch.Generator().manual_seed(seed)
    local = torch.randn((1, LOCAL_FEATURES), generator=generator)
    candidates = torch.randn(
        (1, max_candidates, HAPPO_ACTION_FEATURES), generator=generator
    )
    legal_mask = torch.zeros((1, max_candidates), dtype=torch.float32)
    legal_mask[:, : min(37, max_candidates)] = 1.0
    role_one_hot = torch.zeros((1, len(ROLE_NAMES)), dtype=torch.float32)
    role_one_hot[:, 0] = 1.0
    return local, candidates, legal_mask, role_one_hot


def export_onnx(
    policy: MobileHAPPOPolicy, output: Path, max_candidates: int
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    inputs = sample_inputs(max_candidates)
    with torch.inference_mode():
        torch.onnx.export(
            policy,
            inputs,
            output,
            input_names=("local", "candidates", "legal_mask", "role_one_hot"),
            output_names=("logits",),
            opset_version=ONNX_OPSET,
            do_constant_folding=True,
            dynamo=False,
        )


def validate_and_benchmark(
    policy: MobileHAPPOPolicy,
    output: Path,
    max_candidates: int,
    runs: int,
) -> dict[str, object]:
    import onnxruntime as ort

    session = ort.InferenceSession(
        str(output), providers=["CPUExecutionProvider"]
    )
    local, candidates, mask, role = sample_inputs(max_candidates)
    inputs = {
        "local": local.numpy(),
        "candidates": candidates.numpy(),
        "legal_mask": mask.numpy(),
        "role_one_hot": role.numpy(),
    }
    max_error = 0.0
    argmax_matches = True
    with torch.inference_mode():
        for role_index in range(len(ROLE_NAMES)):
            role.zero_()
            role[:, role_index] = 1.0
            inputs["role_one_hot"] = role.numpy()
            expected = policy(local, candidates, mask, role).numpy()
            actual = session.run(("logits",), inputs)[0]
            max_error = max(max_error, float(np.max(np.abs(expected - actual))))
            argmax_matches &= int(np.argmax(expected)) == int(np.argmax(actual))

    for _ in range(10):
        session.run(("logits",), inputs)
    timings = []
    for _ in range(max(1, runs)):
        started = time.perf_counter_ns()
        session.run(("logits",), inputs)
        timings.append((time.perf_counter_ns() - started) / 1_000_000.0)
    values = np.asarray(timings, dtype=np.float64)
    return {
        "provider": session.get_providers()[0],
        "runs": len(timings),
        "host_only": True,
        "p50_ms": float(np.percentile(values, 50)),
        "p95_ms": float(np.percentile(values, 95)),
        "p99_ms": float(np.percentile(values, 99)),
        "max_abs_error": max_error,
        "argmax_matches_all_roles": bool(argmax_matches),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_metadata(
    policy: MobileHAPPOPolicy,
    output: Path,
    checkpoint: Path,
    metadata_path: Path,
    max_candidates: int,
    validation: dict[str, object],
    release_report: Path | None,
) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "format": "onnx",
        "opset": ONNX_OPSET,
        "model": output.name,
        "model_bytes": output.stat().st_size,
        "model_sha256": sha256(output),
        "source_checkpoint": str(checkpoint),
        "source_checkpoint_sha256": sha256(checkpoint),
        "local_features": LOCAL_FEATURES,
        "candidate_features": HAPPO_ACTION_FEATURES,
        "max_candidates": max_candidates,
        "roles": list(ROLE_NAMES),
        "trained_roles": [
            role
            for role, trained in zip(ROLE_NAMES, policy.trained_role_mask.tolist())
            if trained > 0.5
        ],
        "untrained_role_behavior": "equal legal logits; deterministic first legal action",
        "inputs": ["local", "candidates", "legal_mask", "role_one_hot"],
        "output": "logits",
        "selection": "argmax over legal candidates",
        "invalid_logit": -1.0e4,
        "validation": validation,
    }
    if release_report is not None:
        report = json.loads(release_report.read_text(encoding="utf-8"))
        metadata["release_evaluation"] = {
            "scope": report.get("scope"),
            "battle_stages": report.get("battle_stages"),
            "episodes_per_stage": report.get("episodes_per_stage"),
            "scripted_baseline": report.get("scripted_baseline"),
            "happo": report.get("happo"),
            "delta": report.get("delta"),
            "release_gate": report.get("release_gate"),
        }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--release-report", type=Path)
    parser.add_argument("--max-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    parser.add_argument("--benchmark-runs", type=int, default=200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_candidates < 1:
        raise ValueError("max candidates must be positive")
    policy = load_policy(args.checkpoint)
    export_onnx(policy, args.output, args.max_candidates)
    validation = validate_and_benchmark(
        policy, args.output, args.max_candidates, args.benchmark_runs
    )
    if not validation["argmax_matches_all_roles"]:
        raise RuntimeError("ONNX argmax differs from PyTorch")
    if float(validation["max_abs_error"]) > 1.0e-4:
        raise RuntimeError(f"ONNX parity error too large: {validation['max_abs_error']}")
    metadata_path = args.metadata or args.output.with_suffix(".json")
    write_metadata(
        policy,
        args.output,
        args.checkpoint,
        metadata_path,
        args.max_candidates,
        validation,
        args.release_report,
    )
    print(metadata_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
