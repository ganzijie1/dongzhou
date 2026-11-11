"""Verify every authoritative organization member through the live Dongzhou API."""
from __future__ import annotations

import argparse
from datetime import date, timedelta
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


def business_ok(component: object) -> bool:
    return isinstance(component, dict) and component.get("code") in (0, 200, "0", "200")


def validate_schedule(hero_id: str, npc_id: str, body: dict) -> dict:
    assert body.get("heroId") == hero_id, "schedule hero identity mismatch"
    assert body.get("npcId") == npc_id, "schedule NPC identity mismatch"
    schedule = body.get("schedule", {})
    assert business_ok(schedule), "schedule business request failed"
    plan = schedule.get("data", {})
    assert plan.get("npc_id") == npc_id, "plan NPC identity mismatch"
    days = plan.get("schedules")
    assert isinstance(days, list) and len(days) == 90, "plan must contain 90 days"
    assert [item.get("day") for item in days] == list(range(1, 91)), "plan day sequence is invalid"
    start = date.fromisoformat(plan["start_date"])
    expected_dates = [(start + timedelta(days=offset)).isoformat() for offset in range(90)]
    assert [item.get("date") for item in days] == expected_dates, "plan dates are not consecutive"
    assert plan.get("end_date") == expected_dates[-1], "plan end date is invalid"
    return {"days": len(days), "startDate": plan["start_date"], "endDate": plan["end_date"]}


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8780")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    results = []
    with httpx.Client(base_url=args.url, timeout=45) as client:
        unwrap(client.post("/api/dongzhou/v1/sessions/guest", json={"installation_id": str(uuid4())}))
        roster = unwrap(client.get("/api/dongzhou/v1/organization/roster"))
        members = roster.get("members")
        assert isinstance(members, list) and members, "organization roster is empty"
        hero_ids = [member.get("heroId") for member in members]
        assert all(isinstance(hero_id, str) and hero_id for hero_id in hero_ids), "roster has an invalid hero ID"
        assert len(hero_ids) == len(set(hero_ids)), "roster contains duplicate heroes"

        for hero_id in hero_ids:
            encoded = quote(hero_id, safe="")
            state = unwrap(client.get(f"/api/dongzhou/v1/npcs/{encoded}/state"))
            assert state.get("heroId") == hero_id, "state hero identity mismatch"
            npc_id = state.get("npcId")
            assert isinstance(npc_id, str) and npc_id, "state has no NPC identity"
            assert state.get("knownNpcIds", {}).get(hero_id) == npc_id, "known NPC mapping mismatch"
            assert state.get("runtime", {}).get("state") == "READY", "NPC actor is not ready"
            for component in ("emotion", "affection", "relationships"):
                assert business_ok(state.get(component)), f"{component} business request failed"
            schedule = validate_schedule(
                hero_id,
                npc_id,
                unwrap(client.get(f"/api/dongzhou/v1/npcs/{encoded}/schedule")),
            )
            results.append({"heroId": hero_id, "npcId": npc_id, **schedule})

    report = {
        "result": "PASS",
        "url": args.url,
        "organization": roster.get("organization", {}).get("name"),
        "memberCount": len(results),
        "members": results,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
