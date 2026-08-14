"""Offline-capable Google ADK terrain labeling workflow.

The workflow uses ADK for orchestration and local deterministic tools for
evidence collection. It never needs an LLM key to enforce the review policy.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import AsyncGenerator

import numpy as np
import torch
from google.adk.agents import BaseAgent, InvocationContext, ParallelAgent, SequentialAgent
from google.adk.events import Event, EventActions


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.terrain_semantic_dinov3 import cached_cells
from tools.train_terrain_trusted_adapter import (
    CLASSES, CosineAdapter, prototype_probabilities,
)


def _event(author: str, key: str, value) -> Event:
    return Event(author=author, actions=EventActions(state_delta={key: value}))


def _manifest(ctx: InvocationContext) -> tuple[Path, dict]:
    relative = str(ctx.session.state["manifest_path"])
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents:
        raise ValueError("manifest must stay inside the Mengde workspace")
    return path, json.loads(path.read_text(encoding="utf-8"))


class EvidenceAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        path, manifest = _manifest(ctx)
        image_path = (ROOT / str(manifest["map"])).resolve()
        width, height = map(int, manifest["grid"])
        rows = manifest.get("terrain_rows", [])
        actual_hash = hashlib.sha256(image_path.read_bytes()).hexdigest()
        declared_hash = str(manifest.get("image_sha256", "")).lower()
        aligned = (
            image_path.is_file() and len(rows) == height
            and all(len(row) == width for row in rows)
        )
        review = manifest.get("review", {})
        verified_source = bool(
            aligned and declared_hash == actual_hash
            and review.get("status") == "fully_reviewed"
            and review.get("source_matrix_matches_stage")
            and review.get("source_matrix_drives_renderer")
        )
        yield _event(self.name, "evidence", {
            "manifest": str(path.relative_to(ROOT)), "image": str(image_path.relative_to(ROOT)),
            "grid": [width, height], "aligned": aligned,
            "declared_hash": declared_hash, "actual_hash": actual_hash,
            "verified_source_matrix": verified_source,
            "reviewed_cells": int(review.get("reviewed_cells", 0)),
        })


class VisionProposalAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        _, manifest = _manifest(ctx)
        image_path = ROOT / str(manifest["map"])
        width, height = map(int, manifest["grid"])
        bundle = torch.load(
            ROOT / "output/terrain_model/terrain_trusted_adapter.pt",
            map_location="cpu", weights_only=False,
        )
        model = CosineAdapter(int(bundle["feature_count"]), int(bundle["hidden"]))
        model.load_state_dict(bundle["state_dict"])
        model.eval()
        features = cached_cells(image_path, width, height)
        scaled = ((features - bundle["mean"]) / bundle["scale"]).astype(np.float32)
        with torch.inference_mode():
            tensor = torch.from_numpy(scaled)
            probability = torch.softmax(model(tensor), dim=1).numpy()
            embedding = model.embed(tensor).numpy()
        metric = prototype_probabilities(
            embedding, bundle["prototypes"], bundle["prototype_owners"]
        )
        ensemble = 0.55 * probability + 0.45 * metric
        head_agreement = probability.argmax(1) == metric.argmax(1)
        ordered = np.sort(ensemble, axis=1)
        accepted = (
            head_agreement
            & (ordered[:, -1] >= float(bundle["confidence_threshold"]))
            & (ordered[:, -1] - ordered[:, -2] >= float(bundle["margin_threshold"]))
        )
        prediction = CLASSES[ensemble.argmax(1)]
        yield _event(self.name, "vision_proposal", {
            "classes": CLASSES.tolist(),
            "rows": [
                "".join(prediction[y * width:(y + 1) * width]) for y in range(height)
            ],
            "accepted": accepted.tolist(),
            "accepted_cells": int(accepted.sum()),
            "coverage": float(accepted.mean()),
            "mean_confidence": float(ensemble.max(axis=1).mean()),
            "requires_review": int((~accepted).sum()),
        })


class StructureAuditAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        _, manifest = _manifest(ctx)
        rows = manifest.get("terrain_rows", [])
        width, height = map(int, manifest["grid"])
        flat = "".join(rows)
        cells = lambda char: {
            (index % width, index // width) for index, value in enumerate(flat) if value == char
        }
        fences = {tuple(map(int, point)) for point in manifest.get("fence_cells", [])}
        camps = {tuple(map(int, point)) for point in manifest.get("camp_cells", [])}
        icons = {tuple(map(int, point)) for point in manifest.get("camp_icon_cells", [])}
        supplies = {tuple(map(int, point)) for point in manifest.get("supply_sites", [])}
        errors = []
        if cells("P") != fences:
            errors.append("fence_cells do not match P terrain cells")
        if cells("e") != camps or camps != icons:
            errors.append("camp cells/icons do not match e terrain cells")
        if not camps <= supplies:
            errors.append("camp supply site is missing")
        if len(rows) != height or any(len(row) != width for row in rows):
            errors.append("terrain grid is not aligned")
        yield _event(self.name, "structure_audit", {
            "passed": not errors, "errors": errors,
            "fence_cells": len(fences), "camp_cells": len(camps),
            "water_cells": len(cells("~")),
        })


class ArbitrationAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        _, manifest = _manifest(ctx)
        evidence = ctx.session.state["evidence"]
        vision = ctx.session.state["vision_proposal"]
        structure = ctx.session.state["structure_audit"]
        source_wins = bool(evidence["verified_source_matrix"] and structure["passed"])
        if source_wins:
            rows = manifest["terrain_rows"]
            decision = "accept_verified_source_matrix"
            review_required = []
        else:
            rows = vision["rows"]
            decision = "vision_proposal_review_only"
            width = int(manifest["grid"][0])
            review_required = [
                [index % width, index // width]
                for index, accepted in enumerate(vision["accepted"]) if not accepted
            ]
        yield _event(self.name, "terrain_decision", {
            "decision": decision, "rows": rows,
            "review_required": review_required,
            "structure_audit_passed": structure["passed"],
            "production_write_allowed": source_wins,
            "auto_apply": False,
        })


root_agent = SequentialAgent(
    name="mengde_terrain_supervisor",
    description="Evidence-aware terrain labeling and promotion workflow",
    sub_agents=[
        EvidenceAgent(name="evidence_agent", description="Validate source and image evidence"),
        ParallelAgent(
            name="proposal_and_audit",
            sub_agents=[
                VisionProposalAgent(name="vision_agent", description="DINOv3 proposal only"),
                StructureAuditAgent(name="structure_agent", description="Audit hard terrain rules"),
            ],
        ),
        ArbitrationAgent(name="arbitration_agent", description="Select evidence or require review"),
    ],
)
