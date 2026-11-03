from pathlib import Path

import onnxruntime as ort
import torch

from rl.export_happo_mobile import (
    export_onnx,
    load_policy,
    sample_inputs,
    validate_and_benchmark,
)
from rl.happo import ROLE_NAMES
from rl.happo import HAPPO


def test_mobile_export_matches_pytorch(tmp_path: Path) -> None:
    checkpoint = tmp_path / "happo.pt"
    output = tmp_path / "happo-mobile.onnx"
    HAPPO(516, seed=2026).save(checkpoint)

    policy = load_policy(checkpoint)
    export_onnx(policy, output, max_candidates=32)
    validation = validate_and_benchmark(policy, output, 32, runs=3)

    assert output.is_file()
    assert validation["argmax_matches_all_roles"] is True
    assert float(validation["max_abs_error"]) < 1.0e-4
    assert ort.InferenceSession(str(output)).get_inputs()[1].shape == [1, 32, 34]


def test_untrained_roles_use_first_legal_action(tmp_path: Path) -> None:
    checkpoint = tmp_path / "untrained.pt"
    model = HAPPO(516, seed=2026)
    model.save(checkpoint)
    policy = load_policy(checkpoint)
    local, candidates, legal, role = sample_inputs(8)
    legal.zero_()
    legal[:, 3:6] = 1.0

    with torch.inference_mode():
        for role_index in range(len(ROLE_NAMES)):
            role.zero_()
            role[:, role_index] = 1.0
            logits = policy(local, candidates, legal, role)[0]
            assert int(torch.argmax(logits)) == 3
            assert torch.all(logits[3:6] == 0.0)
