"""Verify every published Dongzhou stage and campaign route through the live gateway."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from urllib.parse import quote
from uuid import uuid4

import httpx


def unwrap(response: httpx.Response) -> dict:
    response.raise_for_status()
    body = response.json()
    if body.get("success") is True:
        return body.get("data", body)
    return body


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8780")
    parser.add_argument(
        "--campaign",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "web-game/scenario/campaign.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    campaign = json.loads(args.campaign.read_text(encoding="utf-8"))
    stages = campaign.get("stages")
    assert isinstance(stages, list) and stages, "campaign has no stages"
    assert campaign.get("stageCount") == len(stages), "campaign stage count is inconsistent"
    stage_ids = [str(stage.get("id")) for stage in stages]
    assert len(stage_ids) == len(set(stage_ids)), "campaign contains duplicate stage IDs"
    assert [stage.get("index") for stage in stages] == list(range(1, len(stages) + 1)), (
        "campaign indexes are not consecutive"
    )

    knowledge_ids: set[str] = set()
    route_ids: set[str] = set()
    provision_costs: Counter[int] = Counter()

    with httpx.Client(base_url=args.url, timeout=45) as client:
        session = unwrap(
            client.post(
                "/api/dongzhou/v1/sessions/guest",
                json={"installation_id": str(uuid4())},
            )
        )
        assert session.get("playerId"), "guest session has no player identity"

        save = unwrap(client.get("/api/dongzhou/v1/save"))
        unwrap(
            client.put(
                "/api/dongzhou/v1/save",
                json={
                    "expected_version": save["version"],
                    "payload": {"completed": stage_ids, "validationOnly": True},
                },
            )
        )

        for stage_id in stage_ids:
            body = unwrap(
                client.get(f"/api/dongzhou/v1/knowledge/stages/{quote(stage_id, safe='')}")
            )
            assert body.get("mode") == "connected", f"stage {stage_id} is not connected"
            items = body.get("results")
            assert isinstance(items, list) and len(items) == 1, (
                f"stage {stage_id} must have exactly one published knowledge entry"
            )
            item = items[0]
            assert item.get("stageId") == stage_id, f"stage {stage_id} crossed stage boundary"
            knowledge_id = item.get("id")
            assert isinstance(knowledge_id, str) and knowledge_id.startswith("dongzhou_stage_"), (
                f"stage {stage_id} crossed game boundary"
            )
            assert item.get("is_valid") is True, f"stage {stage_id} knowledge is not published"
            for field in ("name", "summary", "content"):
                assert isinstance(item.get(field), str) and item[field].strip(), (
                    f"stage {stage_id} has no {field}"
                )
            sources = item.get("sourceDetails")
            assert isinstance(sources, list) and sources, f"stage {stage_id} has no source details"
            assert knowledge_id not in knowledge_ids, f"duplicate knowledge ID {knowledge_id}"
            knowledge_ids.add(knowledge_id)

        for previous, current in zip(stages, stages[1:]):
            request = {
                "from_stage_id": str(previous["id"]),
                "from_stage_index": previous["index"],
                "to_stage_id": str(current["id"]),
                "to_stage_index": current["index"],
            }
            route = unwrap(client.post("/api/dongzhou/v1/knowledge/routes", json=request))
            from_map_id = 900000 + previous["index"]
            to_map_id = 900000 + current["index"]
            expected_id = f"campaign_progression_{from_map_id}_{to_map_id}"
            assert route.get("mode") == "connected" and route.get("found") is True, (
                f"route {previous['id']} -> {current['id']} is not published"
            )
            assert route.get("fromStageId") == previous["id"], "route source stage mismatch"
            assert route.get("toStageId") == current["id"], "route target stage mismatch"
            assert route.get("fromMapId") == from_map_id, "route source map mismatch"
            assert route.get("toMapId") == to_map_id, "route target map mismatch"
            assert route.get("routeId") == expected_id, "route identity mismatch"
            provision_cost = route.get("provisionCost")
            assert type(provision_cost) is int and 0 <= provision_cost <= 20, (
                "route provision cost is invalid"
            )
            assert expected_id not in route_ids, f"duplicate route ID {expected_id}"
            route_ids.add(expected_id)
            provision_costs[provision_cost] += 1

    report = {
        "result": "PASS",
        "at": datetime.now(timezone.utc).isoformat(),
        "url": args.url,
        "playerIsolation": True,
        "sharedClockAdvanced": False,
        "organizationTaskCreated": False,
        "campaignStages": len(stages),
        "publishedKnowledgeEntries": len(knowledge_ids),
        "campaignRoutes": len(route_ids),
        "provisionCostHistogram": dict(sorted(provision_costs.items())),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
