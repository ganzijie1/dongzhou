import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_adk_agent_uses_verified_evidence_without_auto_apply():
    report = json.loads(
        (ROOT / "output/terrain_model/m058_adk_agent_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["framework"] == "google-adk"
    assert [event["author"] for event in report["trajectory"]] == [
        "evidence_agent", "vision_agent", "structure_agent", "arbitration_agent"
    ]
    assert report["evidence"]["verified_source_matrix"] is True
    assert report["structure_audit"]["passed"] is True
    assert report["decision"]["decision"] == "accept_verified_source_matrix"
    assert report["decision"]["production_write_allowed"] is True
    assert report["decision"]["auto_apply"] is False
    rejected = json.loads((ROOT / "output/terrain_model/m058_adk_unverified_report.json").read_text(encoding="utf-8"))
    evidence = rejected.get("evidence", {})
    decision = rejected.get("decision", {})
    assert evidence.get("verified_source_matrix") is False
    assert decision.get("decision") == "vision_proposal_review_only"
    assert decision.get("production_write_allowed") is False
    assert len(decision.get("review_required", [])) == 20


def test_adk_beats_untrusted_vision_on_reviewed_map():
    comparison = json.loads(
        (ROOT / "output/terrain_model/terrain_adk_vs_model_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert comparison["adk_arbitration"]["macro_f1"] == 1.0
    assert comparison["adk_arbitration"]["minimum_class_recall"] == 1.0
    vision_f1 = comparison.get("standalone_vision", {}).get("macro_f1")
    agent_f1 = comparison.get("adk_arbitration", {}).get("macro_f1")
    assert vision_f1 < agent_f1
    assert comparison.get("comparison_scope", "").startswith("terrain labeling")
