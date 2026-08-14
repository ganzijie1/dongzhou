"""Compare ADK evidence arbitration with the standalone vision proposal."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, f1_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from run_terrain_adk_agent import run


CLASSES = np.asarray(["f", "g", "F", "m"])


def metrics(truth_rows: list[str], predicted_rows: list[str]):
    truth = np.asarray(list("".join(truth_rows)))
    predicted = np.asarray(list("".join(predicted_rows)))
    eligible = np.isin(truth, CLASSES)
    truth, predicted = truth[eligible], predicted[eligible]
    report = classification_report(
        truth, predicted, labels=CLASSES.tolist(), output_dict=True, zero_division=0,
    )
    return {
        "accuracy": float((truth == predicted).mean()),
        "macro_f1": float(f1_score(truth, predicted, labels=CLASSES, average="macro")),
        "minimum_class_recall": float(min(report[label]["recall"] for label in CLASSES)),
        "classes": {label: report[label] for label in CLASSES},
    }


async def main_async(manifest_path: str, output: Path):
    agent_report = await run(
        manifest_path, ROOT / "output/terrain_model/terrain_adk_agent_report.json"
    )
    truth = json.loads((ROOT / manifest_path).read_text(encoding="utf-8"))["terrain_rows"]
    payload = {
        "manifest": manifest_path,
        "standalone_vision": metrics(truth, agent_report["vision_proposal"]["rows"]),
        "adk_arbitration": metrics(truth, agent_report["decision"]["rows"]),
        "adk_decision": agent_report["decision"]["decision"],
        "comparison_scope": "terrain labeling; HAPPO is not a vision baseline",
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", default="output/terrain_model/m058_fully_reviewed_manifest.json"
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "output/terrain_model/terrain_adk_vs_model_report.json",
    )
    args = parser.parse_args()
    print(json.dumps(
        asyncio.run(main_async(args.manifest, args.output)), ensure_ascii=False, indent=2
    ))


if __name__ == "__main__":
    main()
