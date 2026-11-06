#!/usr/bin/env python3
"""Fuse target identity embeddings with contextual source acoustic codes using Qwen Base."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
SOURCE_ROOT = ROOT / "output" / "voice-production" / "custom-voice-contextual-candidates"
MODEL_PATH = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-Base"
OUTPUT_ROOT = ROOT / "output" / "voice-production" / "hybrid-contextual-clones"
INDEX_PATH = ROOT / "output" / "voice-production" / "hybrid-contextual-clone-index.json"
IDENTITY_OUTPUT_ROOT = ROOT / "output" / "voice-production" / "identity-contextual-clones"
IDENTITY_INDEX_PATH = ROOT / "output" / "voice-production" / "identity-contextual-clone-index.json"
ANCHORED_OUTPUT_ROOT = ROOT / "output" / "voice-production" / "anchored-contextual-clones"
ANCHORED_INDEX_PATH = ROOT / "output" / "voice-production" / "anchored-contextual-clone-index.json"
ANCHOR_ROOT = ROOT / "output" / "voice-production" / "identity-style-anchors"

PERFORMANCE_TEXT_OVERRIDES = {
    "市井孩童唱的是何等妖言？速召百官入朝解说！": "市井孩童唱的，是何等妖言？……速召百官，入朝解说！",
    "传旨天下：严禁制造贩卖檿弧箕箙，见者即拿；并搜捕宫中弃女。": "传旨天下：严禁制造贩卖檿弧箕箙；见者即拿。并搜捕，宫中弃女。",
    "那弃女至今无踪，司市官杜伯办事不力，推出斩首！": "那弃女至今无踪。司市官杜伯，办事不力。……推出，斩首！",
    "君叫臣死，臣不得不死。再敢多言，与杜伯同罪！": "君叫臣死，臣不得不死。……再敢多言，与杜伯同罪！",
    "今日围猎，众卿随寡人尽兴而归！": "今日围猎。众卿，随寡人尽兴而归！",
}

PRONUNCIATION_OVERRIDES = {
    "魏犨": "魏抽",
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="01")
    parser.add_argument("--speakers", default="")
    parser.add_argument("--entry-ids", default="")
    parser.add_argument("--entry-id-file", type=Path)
    parser.add_argument("--identity-only-entry-ids", default="")
    parser.add_argument("--identity-only-entry-file", type=Path)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-anchors", action="store_true")
    parser.add_argument("--attempt", type=int, default=0)
    parser.add_argument("--mode", choices=("hybrid", "identity", "anchored"), default="hybrid")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--anchor-batch-size", type=int, default=4)
    parser.add_argument("--attention", choices=("auto", "sdpa", "flash_attention_2"), default="auto")
    return parser.parse_args()


def seed_for(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big")


def batches(items: list, size: int):
    size = max(1, size)
    for start in range(0, len(items), size):
        yield items[start:start + size]


def synthesis_text(entry: dict) -> str:
    value = PERFORMANCE_TEXT_OVERRIDES.get(entry["text"], entry.get("synthesisText", entry["text"]))
    for written, spoken in PRONUNCIATION_OVERRIDES.items():
        value = value.replace(written, spoken)
    return value


def main() -> None:
    args = parse_args()
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    from qwen_tts.inference.qwen3_tts_model import VoiceClonePromptItem

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    stages = None if args.stages.lower() == "all" else {item.strip() for item in args.stages.split(",") if item.strip()}
    speakers = {item.strip() for item in args.speakers.split(",") if item.strip()}
    entry_ids = {item.strip() for item in args.entry_ids.split(",") if item.strip()}
    if args.entry_id_file:
        raw_entry_ids = args.entry_id_file.read_text(encoding="utf-8")
        entry_ids.update(item.strip() for item in raw_entry_ids.replace(",", "\n").splitlines() if item.strip())
    identity_only_entry_ids = {
        item.strip() for item in args.identity_only_entry_ids.split(",") if item.strip()
    }
    if args.identity_only_entry_file:
        raw_identity_ids = args.identity_only_entry_file.read_text(encoding="utf-8")
        identity_only_entry_ids.update(
            item.strip() for item in raw_identity_ids.replace(",", "\n").splitlines() if item.strip()
        )
    output_root = (
        IDENTITY_OUTPUT_ROOT if args.mode == "identity"
        else ANCHORED_OUTPUT_ROOT if args.mode == "anchored"
        else OUTPUT_ROOT
    )
    index_path = (
        IDENTITY_INDEX_PATH if args.mode == "identity"
        else ANCHORED_INDEX_PATH if args.mode == "anchored"
        else INDEX_PATH
    )
    selected = [
        entry for entry in plan["entries"]
        if (stages is None or entry["firstOccurrence"]["stageId"] in stages)
        and (not speakers or entry["speaker"] in speakers)
        and (not entry_ids or entry["id"] in entry_ids)
        and (args.mode != "hybrid" or (SOURCE_ROOT / entry["id"] / "candidate-1.wav").is_file())
    ][: args.limit or None]
    if not selected:
        raise SystemExit("No dialogue entries matched the requested filters.")
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    attention = args.attention
    if attention == "auto":
        try:
            import flash_attn  # noqa: F401
            attention = "flash_attention_2"
        except ImportError:
            attention = "sdpa"
    print(f"attention={attention}", flush=True)
    model = Qwen3TTSModel.from_pretrained(
        str(MODEL_PATH), dtype=dtype, attn_implementation=attention, low_cpu_mem_usage=False,
    )
    model.model.to(args.device)
    model.device = torch.device(args.device)
    target_prompts: dict[str, object] = {}
    anchor_prompts: dict[tuple[str, str], object] = {}
    existing_records = {}
    if index_path.is_file():
        existing_document = json.loads(index_path.read_text(encoding="utf-8"))
        existing_records = {record["entryId"]: record for record in existing_document.get("entries", [])}

    def target_prompt(card: dict):
        if card["id"] not in target_prompts:
            target_prompts[card["id"]] = model.create_voice_clone_prompt(
                ref_audio=str(ROOT / card["referenceFile"]),
                ref_text=card["referenceText"],
                x_vector_only_mode=False,
            )[0]
        return target_prompts[card["id"]]

    def write_index(records_by_id: dict[str, dict]) -> None:
        selected_ids = {entry["id"] for entry in selected}
        ordered = [records_by_id[entry["id"]] for entry in plan["entries"] if entry["id"] in records_by_id]
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps({
            "schemaVersion": 2,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "method": args.mode,
            "selectedCount": len(selected_ids),
            "completedSelectedCount": sum(entry_id in records_by_id for entry_id in selected_ids),
            "entries": ordered,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def make_record(entry: dict, card: dict, output: Path) -> dict:
        source = SOURCE_ROOT / entry["id"] / "candidate-1.wav"
        return {
            "entryId": entry["id"], "speaker": entry["speaker"], "text": entry["text"],
            "synthesisText": synthesis_text(entry),
            "voiceCardId": entry["voiceCardId"],
            "expectedGender": card["gender"], "expectedAgeBand": card["ageBand"],
            "context": entry["context"], "delivery": entry["delivery"],
            "sourceFile": str(source.relative_to(ROOT)).replace("\\", "/") if source.is_file() else None,
            "candidates": [{"candidate": 1, "file": str(output.relative_to(ROOT)).replace("\\", "/")}],
            "generationAttempt": args.attempt,
            "method": (
                "qwen-base-target-xvector-plus-contextual-source-code"
                if args.mode == "hybrid"
                else "qwen-base-identity-reference-plus-contextual-punctuation"
                if args.mode == "anchored" and entry["id"] in identity_only_entry_ids
                else "qwen-base-identity-style-anchor-plus-contextual-punctuation"
                if args.mode == "anchored"
                else "qwen-base-identity-reference-plus-contextual-punctuation"
            ),
            "gates": {
                "text": "pending_independent_asr", "identity": "pending_approved_anchor",
                "humanReview": "pending_blind_review", "calibration": "pending_project_calibration",
                "waveform": "pending_full_evaluation", "prosody": "pending_full_evaluation",
                "broadcastCadence": "pending_full_evaluation",
            },
            "alerts": [], "approvedAnchorCandidate": None, "promotionEligible": False,
        }

    records_by_id = dict(existing_records)
    try:
        if args.mode == "anchored":
            needed_anchors = []
            seen_anchors = set()
            for entry in selected:
                if entry["id"] in identity_only_entry_ids:
                    continue
                card = cards_by_id[entry["voiceCardId"]]
                style_id = entry["delivery"]["styleAnchor"]
                key = (card["id"], style_id)
                if key not in seen_anchors:
                    style = next(item for item in card["styleAnchors"] if item["id"] == style_id)
                    needed_anchors.append((card, style))
                    seen_anchors.add(key)
            missing_anchors = []
            for card, style in needed_anchors:
                anchor_file = ANCHOR_ROOT / card["id"] / f"{style['id']}.wav"
                if args.force_anchors or not anchor_file.is_file():
                    missing_anchors.append((card, style, anchor_file))
            for batch_index, batch in enumerate(batches(missing_anchors, args.anchor_batch_size), start=1):
                for _, _, anchor_file in batch:
                    anchor_file.parent.mkdir(parents=True, exist_ok=True)
                torch.manual_seed(seed_for(
                    f"attempt={args.attempt}|" + "|".join(f"{card['id']}:{style['id']}" for card, style, _ in batch)
                ))
                torch.cuda.manual_seed_all(torch.initial_seed())
                wavs, sample_rate = model.generate_voice_clone(
                    text=[style["referenceText"] for _, style, _ in batch],
                    language=["Chinese"] * len(batch),
                    voice_clone_prompt=[target_prompt(card) for card, _, _ in batch],
                    max_new_tokens=180, do_sample=True, top_p=0.75, temperature=0.58,
                    repetition_penalty=1.08,
                )
                for waveform, (_, _, anchor_file) in zip(wavs, batch):
                    sf.write(anchor_file, waveform, sample_rate)
                done = min(batch_index * args.anchor_batch_size, len(missing_anchors))
                print(f"[anchors {done}/{len(missing_anchors)}]", flush=True)
            for card, style in needed_anchors:
                anchor_file = ANCHOR_ROOT / card["id"] / f"{style['id']}.wav"
                raw_anchor_prompt = model.create_voice_clone_prompt(
                    ref_audio=str(anchor_file), ref_text=style["referenceText"], x_vector_only_mode=False,
                )[0]
                anchor_prompts[(card["id"], style["id"])] = VoiceClonePromptItem(
                    ref_code=raw_anchor_prompt.ref_code,
                    ref_spk_embedding=target_prompt(card).ref_spk_embedding,
                    x_vector_only_mode=False,
                    icl_mode=True,
                    ref_text=raw_anchor_prompt.ref_text,
                )

        pending = []
        for entry in selected:
            output = output_root / entry["id"] / "candidate-1.wav"
            if output.is_file() and not args.force:
                records_by_id[entry["id"]] = make_record(entry, cards_by_id[entry["voiceCardId"]], output)
            else:
                pending.append(entry)
        write_index(records_by_id)

        pending.sort(key=lambda entry: len(entry.get("synthesisText", entry["text"])))
        generated = len(selected) - len(pending)
        for batch in batches(pending, args.batch_size):
            active_prompts = []
            texts = []
            for entry in batch:
                card = cards_by_id[entry["voiceCardId"]]
                identity_prompt = target_prompt(card)
                if args.mode == "hybrid":
                    source = SOURCE_ROOT / entry["id"] / "candidate-1.wav"
                    performance_prompt = model.create_voice_clone_prompt(
                        ref_audio=str(source), ref_text=entry["text"], x_vector_only_mode=False,
                    )[0]
                    active_prompt = VoiceClonePromptItem(
                        ref_code=performance_prompt.ref_code,
                        ref_spk_embedding=identity_prompt.ref_spk_embedding,
                        x_vector_only_mode=False, icl_mode=True, ref_text=performance_prompt.ref_text,
                    )
                elif args.mode == "anchored":
                    if entry["id"] in identity_only_entry_ids:
                        active_prompt = identity_prompt
                    else:
                        style_id = entry["delivery"]["styleAnchor"]
                        active_prompt = anchor_prompts[(card["id"], style_id)]
                else:
                    active_prompt = identity_prompt
                active_prompts.append(active_prompt)
                texts.append(synthesis_text(entry))
            torch.manual_seed(seed_for(f"attempt={args.attempt}|" + "|".join(entry["id"] for entry in batch)))
            torch.cuda.manual_seed_all(torch.initial_seed())
            max_new_tokens = max(160, min(640, max(len(text) for text in texts) * 6 + 80))
            wavs, sample_rate = model.generate_voice_clone(
                text=texts, language=["Chinese"] * len(batch), voice_clone_prompt=active_prompts,
                max_new_tokens=max_new_tokens, do_sample=True, top_p=0.78, temperature=0.62,
                repetition_penalty=1.08,
            )
            for waveform, entry in zip(wavs, batch):
                output = output_root / entry["id"] / "candidate-1.wav"
                output.parent.mkdir(parents=True, exist_ok=True)
                sf.write(output, waveform, sample_rate)
                card = cards_by_id[entry["voiceCardId"]]
                records_by_id[entry["id"]] = make_record(entry, card, output)
            generated += len(batch)
            write_index(records_by_id)
            print(f"[dialogue {generated}/{len(selected)}] {batch[-1]['speaker']} {batch[-1]['id']}", flush=True)
    finally:
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
