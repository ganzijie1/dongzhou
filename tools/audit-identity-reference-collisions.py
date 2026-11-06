#!/usr/bin/env python3
"""Find duplicate or suspiciously similar character identity references."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
OUTPUT_PATH = ROOT / "output" / "voice-production" / "identity-reference-collision-audit.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--review-threshold", type=float, default=0.88)
    parser.add_argument("--top-pairs", type=int, default=200)
    return parser.parse_args()


def load_helpers():
    path = ROOT / "tools" / "evaluate-contextual-voice-candidates.py"
    spec = importlib.util.spec_from_file_location("dongzhou_voice_evaluator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load voice evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_speaker_encoder, module.encode_speaker


def main() -> None:
    args = parse_args()
    import numpy as np

    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    load_speaker_encoder, encode_speaker = load_helpers()
    encoder = load_speaker_encoder(args.device)
    rows = []
    embeddings = []
    hashes: dict[str, list[str]] = {}
    cache_root = ROOT / "output" / "voice-production" / "embeddings" / "identity-collision-audit"
    cache_root.mkdir(parents=True, exist_ok=True)
    for index, card in enumerate(cards, start=1):
        path = ROOT / card["referenceFile"]
        if not path.is_file():
            rows.append({"voiceCardId": card["id"], "speaker": card["speaker"], "status": "missing"})
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(card["id"])
        cache = cache_root / f"{card['id']}.npy"
        if cache.is_file() and cache.stat().st_mtime >= path.stat().st_mtime:
            embedding = np.load(cache).astype(np.float32)
        else:
            embedding = encode_speaker(encoder, path)
            np.save(cache, embedding)
        embedding /= max(float(np.linalg.norm(embedding)), 1e-8)
        rows.append({
            "voiceCardId": card["id"], "speaker": card["speaker"], "file": card["referenceFile"],
            "sha256": digest, "status": "present",
        })
        embeddings.append((len(rows) - 1, embedding))
        print(f"[{index}/{len(cards)}] {card['speaker']}", flush=True)

    pairs = []
    if embeddings:
        matrix = np.vstack([item[1] for item in embeddings])
        similarity = matrix @ matrix.T
        np.fill_diagonal(similarity, -1.0)
        for local_index, (row_index, _) in enumerate(embeddings):
            nearest_local = int(np.argmax(similarity[local_index]))
            nearest_row = embeddings[nearest_local][0]
            score = float(similarity[local_index, nearest_local])
            rows[row_index]["nearestVoiceCardId"] = rows[nearest_row]["voiceCardId"]
            rows[row_index]["nearestSpeaker"] = rows[nearest_row]["speaker"]
            rows[row_index]["nearestSimilarity"] = round(score, 5)
            rows[row_index]["collisionReviewRequired"] = score >= args.review_threshold
        for left in range(len(embeddings)):
            for right in range(left + 1, len(embeddings)):
                score = float(similarity[left, right])
                if score < args.review_threshold:
                    continue
                left_row = rows[embeddings[left][0]]
                right_row = rows[embeddings[right][0]]
                pairs.append({
                    "leftVoiceCardId": left_row["voiceCardId"], "leftSpeaker": left_row["speaker"],
                    "rightVoiceCardId": right_row["voiceCardId"], "rightSpeaker": right_row["speaker"],
                    "similarity": round(score, 5),
                })
        pairs.sort(key=lambda item: item["similarity"], reverse=True)

    exact_groups = [ids for ids in hashes.values() if len(ids) > 1]
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "model": "SpeechBrain ECAPA-TDNN speaker embedding",
        "policy": {
            "exactDuplicates": "Byte-identical identity references are automatic failures.",
            "nearCollisions": "Embedding similarity is an uncalibrated review screen, not proof that two speakers are identical.",
            "reviewThreshold": args.review_threshold,
        },
        "summary": {
            "cards": len(cards),
            "present": sum(row["status"] == "present" for row in rows),
            "missing": sum(row["status"] == "missing" for row in rows),
            "exactDuplicateGroups": len(exact_groups),
            "nearCollisionPairs": len(pairs),
        },
        "exactDuplicateGroups": exact_groups,
        "topNearCollisionPairs": pairs[: max(0, args.top_pairs)],
        "entries": rows,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
