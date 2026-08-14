"""Run the offline Google ADK terrain workflow and save its event trajectory."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from google.adk.runners import InMemoryRunner
from google.genai import types

from terrain_adk_agent import root_agent


ROOT = Path(__file__).resolve().parents[1]


async def run(manifest: str, output: Path):
    runner = InMemoryRunner(agent=root_agent, app_name="mengde_terrain")
    session = await runner.session_service.create_session(
        app_name="mengde_terrain", user_id="local-reviewer",
        state={"manifest_path": manifest},
    )
    trajectory = []
    async for event in runner.run_async(
        user_id="local-reviewer", session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part()]),
    ):
        trajectory.append({
            "author": event.author,
            "state_delta": dict(event.actions.state_delta),
        })
    final = await runner.session_service.get_session(
        app_name="mengde_terrain", user_id="local-reviewer", session_id=session.id,
    )
    payload = {
        "framework": "google-adk", "agent": root_agent.name,
        "manifest": manifest, "trajectory": trajectory,
        "evidence": final.state.get("evidence"),
        "vision_proposal": final.state.get("vision_proposal"),
        "structure_audit": final.state.get("structure_audit"),
        "decision": final.state.get("terrain_decision"),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    await runner.close()
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "output/terrain_model/terrain_adk_agent_report.json",
    )
    args = parser.parse_args()
    payload = asyncio.run(run(args.manifest, args.output))
    print(json.dumps({
        "framework": payload["framework"],
        "trajectory": [item["author"] for item in payload["trajectory"]],
        "decision": payload["decision"], "output": str(args.output),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
