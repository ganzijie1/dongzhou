import json
from pathlib import Path

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]


def test_trusted_adapter_is_selective_and_not_promoted():
    report = json.loads(
        (ROOT / "output/terrain_model/terrain_trusted_adapter_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["supervision"].startswith("two fully reviewed maps")
    assert report["trusted_maps"] == ["m008-large-v2.png", "m058.png"]
    assert report["validation"]["macro_f1"] >= 0.90
    assert report["validation"]["accepted_accuracy"] >= 0.98
    assert report["selection"]["requires_head_agreement"] is True
    assert report["production_promotion"] is False
    assert report["auto_apply"] is False


def test_second_reviewed_map_and_lomo_gate():
    # The review contract is validated through get() to keep malformed data explicit.
    reviewed = json.loads((ROOT / "output/terrain_model/m058_fully_reviewed_manifest.json").read_text(encoding="utf-8"))
    source = json.loads((ROOT / "assets/lzc/map_sources/m058_ch35_manifest.json").read_text(encoding="utf-8"))
    review = reviewed.get("review", {})
    assert review.get("status") == "fully_reviewed"
    assert review.get("reviewed_cells") == 23 * 16
    assert reviewed["terrain_rows"] == source["terrain_rows"]
    assert reviewed["class_counts"] == {"f": 107, "g": 98, "F": 104, "m": 43, "~": 16}
    assert reviewed["camp_cells"] == reviewed["fence_cells"] == reviewed["supply_sites"] == []
    lomo = json.loads((ROOT / "output/terrain_model/terrain_trusted_lomo_report.json").read_text(encoding="utf-8"))
    assert lomo["evaluation"] == "leave-one-fully-reviewed-map-out"
    assert lomo["trusted_maps"] == ["m008-large-v2.png", "m058.png"]
    assert len(lomo["folds"]) == 2
    assert lomo["production_promotion"] is False
    assert lomo["auto_apply"] is False
    assert lomo["promotion_checks"]["selective_coverage"] is True
    assert not all(lomo["promotion_checks"].values())


def test_adapter_artifact_contract():
    bundle = torch.load(
        ROOT / "output/terrain_model/terrain_trusted_adapter.pt",
        map_location="cpu",
        weights_only=False,
    )
    assert bundle["classes"] == ["f", "g", "F", "m"]
    assert bundle["auto_apply"] is False
    assert np.asarray(bundle["prototype_owners"]).dtype == np.int64
    assert set(np.asarray(bundle["prototype_owners"]).tolist()) == {0, 1, 2, 3}
    assert 0.55 <= bundle["confidence_threshold"] <= 0.95
    assert 0.05 <= bundle["margin_threshold"] <= 0.35
