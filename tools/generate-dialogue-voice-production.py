#!/usr/bin/env python3
"""Generate historically directed Dongzhou character speech with resumable Qwen3-TTS jobs."""

from __future__ import annotations

import argparse
import asyncio
import gc
import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PLAN_PATH = ROOT / "web-game" / "audio" / "dialogue-production-plan.json"
CARDS_PATH = ROOT / "web-game" / "audio" / "voice-cards.json"
MANIFEST_PATH = ROOT / "web-game" / "audio" / "dialogue-manifest.json"
VOICE_DESIGN_DIR = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-VoiceDesign"
VOICE_CLONE_DIR = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-Base"
REFERENCE_ROOT = ROOT / "output" / "voice-production" / "references"
EDGE_INDEX_PATH = ROOT / "output" / "voice-production" / "edge-coverage-index.json"
CONTEXTUAL_INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-render-index.json"
CASTING_PATH = ROOT / "web-game" / "audio" / "voice-casting-ot-plan.json"
QWEN_MODEL_NAME = "Qwen3-TTS-12Hz-1.7B-VoiceDesign + Qwen3-TTS-12Hz-1.7B-Base"
QWEN_PYTHON = WORKSPACE / ".tools" / "venvs" / "qwen3-tts" / "Scripts" / "python.exe"
_CASTING_BY_SPEAKER: dict[str, dict] | None = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("references", "dialogue", "coverage", "all"), default="all")
    parser.add_argument("--stages", default="01", help="Comma-separated stage IDs, or 'all'.")
    parser.add_argument("--speakers", default="", help="Optional comma-separated exact speaker names.")
    parser.add_argument("--batch-size", type=int, default=3)
    parser.add_argument("--reference-attempt", type=int, default=0, help="Write retry identity references to an isolated candidate tree.")
    parser.add_argument("--limit", type=int, default=0, help="Limit speakers for references or lines for dialogue.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def model_is_complete(path: Path) -> bool:
    model_file = path / "model.safetensors"
    tokenizer_file = path / "speech_tokenizer" / "model.safetensors"
    active_incomplete = list(path.glob("*.incomplete")) + list((path / "speech_tokenizer").glob("*.incomplete"))
    return (
        model_file.exists()
        and model_file.stat().st_size > 3_000_000_000
        and tokenizer_file.exists()
        and tokenizer_file.stat().st_size > 500_000_000
        and not active_incomplete
    )


def selected_assets(plan: dict, cards: dict, stages: set[str] | None, speakers: set[str]) -> tuple[list[dict], list[dict]]:
    selected_entry_ids: set[str]
    selected_speakers: set[str]
    if stages is None:
        selected_entry_ids = {entry["id"] for entry in plan["entries"]}
        selected_speakers = {entry["speaker"] for entry in plan["entries"]}
    else:
        occurrences = [item for item in plan["occurrences"] if item["stageId"] in stages]
        selected_entry_ids = {item["entryId"] for item in occurrences}
        selected_speakers = {item["speaker"] for item in occurrences}
    if speakers:
        selected_speakers &= speakers
    entries = [
        entry for entry in plan["entries"]
        if entry["id"] in selected_entry_ids and entry["speaker"] in selected_speakers
    ]
    return entries, [cards[name] for name in sorted(selected_speakers) if name in cards]


def seed_for(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:4], "big")


def load_edge_index() -> dict[str, dict]:
    if not EDGE_INDEX_PATH.exists():
        return {}
    return json.loads(EDGE_INDEX_PATH.read_text(encoding="utf-8"))


def save_edge_index(index: dict[str, dict]) -> None:
    EDGE_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    EDGE_INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_model(path: Path, device: str):
    import torch
    from qwen_tts import Qwen3TTSModel

    if not model_is_complete(path):
        raise RuntimeError(f"Qwen model is incomplete: {path}")
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    print(f"Loading {path.name} on CPU with {dtype}, then moving it to {device}", flush=True)
    wrapper = Qwen3TTSModel.from_pretrained(
        str(path),
        dtype=dtype,
        attn_implementation="sdpa",
        low_cpu_mem_usage=False,
    )
    wrapper.model.to(device)
    wrapper.device = torch.device(device)
    return wrapper


def release_model(model) -> None:
    import torch

    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def design_references(cards: list[dict], args: argparse.Namespace) -> None:
    import soundfile as sf
    import torch

    targets = cards[: args.limit or None]
    jobs: list[dict] = []
    for card in targets:
        identity_output = (
            ROOT / "output" / "voice-production" / "reference-candidates" / card["id"] / f"attempt-{args.reference_attempt}.wav"
            if args.reference_attempt > 0 else ROOT / card["referenceFile"]
        )
        jobs.append({
            "card": card,
            "label": f"identity-attempt-{args.reference_attempt}" if args.reference_attempt > 0 else "identity",
            "text": card["referenceText"],
            "instruction": card["voiceDesignInstruction"],
            "output": identity_output,
        })
        if args.reference_attempt > 0:
            continue
        for anchor in card.get("styleAnchors", []):
            jobs.append({
                "card": card,
                "label": f"style:{anchor['id']}",
                "text": anchor["referenceText"],
                "instruction": f"{card['voiceDesignInstruction']} 表演方向：{anchor['direction']} 保持同一人物的性别、年龄、声道尺度和基本音色。",
                "output": ROOT / anchor["referenceFile"],
            })
    pending = [job for job in jobs if args.force or not job["output"].exists()]
    if not pending:
        print(f"Reference and style-anchor voices already present: {len(jobs)}", flush=True)
        return
    model = load_model(VOICE_DESIGN_DIR, args.device)
    try:
        batch_size = max(1, int(args.batch_size))
        for start in range(0, len(pending), batch_size):
            batch = pending[start:start + batch_size]
            batch_seed = seed_for("|".join(f"{job['card']['speaker']}|{job['label']}" for job in batch))
            torch.manual_seed(batch_seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(batch_seed)
            names = ", ".join(f"{job['card']['speaker']}:{job['label']}" for job in batch)
            print(f"[references {start + 1}-{start + len(batch)}/{len(pending)}] {names}", flush=True)
            wavs, sample_rate = model.generate_voice_design(
                text=[job["text"] for job in batch],
                language=["Chinese"] * len(batch),
                instruct=[job["instruction"] for job in batch],
                max_new_tokens=max(160, min(360, max(len(job["text"]) for job in batch) * 6 + 80)),
                do_sample=True,
                top_p=0.85,
                temperature=0.75,
                repetition_penalty=1.08,
            )
            if len(wavs) != len(batch):
                raise RuntimeError(f"VoiceDesign batch returned {len(wavs)} outputs for {len(batch)} jobs")
            for job, waveform in zip(batch, wavs):
                output = job["output"]
                output.parent.mkdir(parents=True, exist_ok=True)
                sf.write(output, waveform, sample_rate)
    finally:
        release_model(model)


def encode_opus(wav_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav_path),
        "-af", "loudnorm=I=-18:LRA=7:TP=-1.5", "-ar", "48000", "-ac", "1",
        "-c:a", "libopus", "-b:a", "56k", "-vbr", "on", str(output_path),
    ], check=True)


def duration_seconds(path: Path) -> float:
    try:
        import soundfile as sf
        info = sf.info(path)
        return round(info.frames / info.samplerate, 3)
    except ImportError:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            check=True, capture_output=True, text=True,
        )
        return round(float(result.stdout.strip()), 3)


def generate_dialogue(entries: list[dict], cards_by_id: dict[str, dict], args: argparse.Namespace) -> None:
    import soundfile as sf
    import torch

    targets = entries[: args.limit or None]
    pending = [entry for entry in targets if args.force or not (ROOT / "web-game" / entry["file"]).exists()]
    if not pending:
        print(f"Dialogue audio already present: {len(targets)}", flush=True)
        write_manifest()
        return
    def selected_reference(card: dict, entry: dict) -> tuple[Path, str, str]:
        style_id = entry.get("delivery", {}).get("styleAnchor", "neutral")
        approved = next((
            anchor for anchor in card.get("styleAnchors", [])
            if anchor.get("id") == style_id and anchor.get("approvedForCloning") is True
        ), None)
        if approved:
            return ROOT / approved["referenceFile"], approved["referenceText"], style_id
        return ROOT / card["referenceFile"], card["referenceText"], "identity"

    for entry in pending:
        reference, _, _ = selected_reference(cards_by_id[entry["voiceCardId"]], entry)
        if not reference.exists():
            raise RuntimeError(f"Missing designed reference for {entry['speaker']}: {reference}")

    model = load_model(VOICE_CLONE_DIR, args.device)
    temp_root = ROOT / "output" / "voice-production" / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    generated = 0
    edge_index = load_edge_index()
    prompt_cache: dict[str, object] = {}
    try:
        for entry in pending:
            card = cards_by_id[entry["voiceCardId"]]
            reference, reference_text, reference_kind = selected_reference(card, entry)
            prompt_key = str(reference.resolve())
            if prompt_key not in prompt_cache:
                prompt_cache[prompt_key] = model.create_voice_clone_prompt(
                    ref_audio=str(reference), ref_text=reference_text, x_vector_only_mode=False,
                )
            line_seed = seed_for(f"{entry['id']}|{entry['context']['id']}|{reference_kind}")
            torch.manual_seed(line_seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(line_seed)
            print(f"[dialogue {generated + 1}/{len(pending)}] {entry['speaker']} {entry['context']['id']} {reference_kind}", flush=True)
            wavs, sample_rate = model.generate_voice_clone(
                text=entry["text"], language="Chinese",
                voice_clone_prompt=prompt_cache[prompt_key],
                max_new_tokens=max(160, min(640, len(entry["text"]) * 6 + 80)),
                do_sample=True, top_p=0.82, temperature=0.72, repetition_penalty=1.08,
            )
            temp_wav = temp_root / f"{entry['id']}.wav"
            output = ROOT / "web-game" / entry["file"]
            sf.write(temp_wav, wavs[0], sample_rate)
            encode_opus(temp_wav, output)
            temp_wav.unlink(missing_ok=True)
            edge_index.pop(entry["id"], None)
            save_edge_index(edge_index)
            generated += 1
            write_manifest()
    finally:
        release_model(model)
    write_manifest()


def edge_profile(card: dict, entry: dict) -> dict[str, str]:
    global _CASTING_BY_SPEAKER
    if _CASTING_BY_SPEAKER is None:
        if CASTING_PATH.exists():
            casting = json.loads(CASTING_PATH.read_text(encoding="utf-8"))
            _CASTING_BY_SPEAKER = {item["speaker"]: item for item in casting["assignments"]}
        else:
            _CASTING_BY_SPEAKER = {}
    assigned = _CASTING_BY_SPEAKER.get(card["speaker"])
    if assigned:
        profile = {key: assigned[key] for key in ("voice", "rate", "pitch", "volume")}
    else:
        gender = card.get("gender", "male")
        age = card.get("ageBand", "adult")
        role = card.get("role", "")
        variant = seed_for(card["speaker"]) % 3
        if gender == "female":
            voices = ("zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural", "zh-CN-XiaoxiaoNeural")
        elif age == "child":
            voices = ("zh-CN-YunxiaNeural",) * 3
        elif age == "elder" or role in {"senior_minister", "senior_general", "ruler"}:
            voices = ("zh-CN-YunyangNeural", "zh-CN-YunjianNeural", "zh-CN-YunyangNeural")
        else:
            voices = ("zh-CN-YunxiNeural", "zh-CN-YunjianNeural", "zh-CN-YunyangNeural")
        rate_by_age = {
            "child": 2, "young_adult": 1, "adult": 0,
            "mature": -2, "late_middle": -4, "elder": -6,
        }
        profile = {
            "voice": voices[variant],
            "rate": f"{rate_by_age.get(age, 0):+d}%",
            "pitch": "-2Hz" if age in {"elder", "late_middle"} else "+0Hz",
            "volume": "+0%",
        }

    def signed_number(value: str, suffix: str) -> int:
        return int(str(value).replace(suffix, "").replace("+", "") or 0)

    delivery = entry.get("delivery") or {}
    performance = entry.get("context", {}).get("performanceState") or {}
    emotion = str(delivery.get("emotion") or "")
    speech_act = str(delivery.get("speechAct") or entry.get("context", {}).get("speechAct") or "")
    pace = float(delivery.get("pace", 1.0))
    intensity = float(delivery.get("intensity", 0.5))
    pause_strength = float(delivery.get("pauseStrength", 0.5))
    dominance = float(delivery.get("dominance", 0.5))

    rate = signed_number(profile["rate"], "%") + round((pace - 1.0) * 38) - round((pause_strength - 0.5) * 5)
    volume = signed_number(profile["volume"], "%") + round((intensity - 0.5) * 8)
    pitch = signed_number(profile["pitch"], "Hz") - round((dominance - 0.5) * 3)
    if re.search(r"grief|defeat|fading|subdued|mourning|sorrow", emotion):
        rate -= 4
        volume -= 2
    if re.search(r"command|warning|battle|urgent|alarm|threat", f"{emotion} {speech_act}"):
        rate += 3
        volume += 2
    if re.search(r"cold|controlled|restrained|contained", emotion):
        rate -= 2
    if performance.get("emotionBefore") and performance.get("emotionAfter") and performance["emotionBefore"] != performance["emotionAfter"]:
        rate -= 1
    profile["rate"] = f"{max(-18, min(14, rate)):+d}%"
    profile["volume"] = f"{max(-8, min(6, volume)):+d}%"
    profile["pitch"] = f"{max(-6, min(4, pitch)):+d}Hz"
    profile["contextual"] = {
        "emotion": emotion,
        "speechAct": speech_act,
        "pace": pace,
        "intensity": intensity,
        "pauseStrength": pause_strength,
        "dominance": dominance,
        "pausePlan": str(performance.get("pausePlan") or delivery.get("pausePlan") or ""),
    }
    return profile


def edge_synthesis_text(entry: dict) -> str:
    text = str(entry["text"])
    performance = entry.get("context", {}).get("performanceState") or {}
    for pivot in performance.get("pivotWords") or []:
        pivot = str(pivot).strip()
        if not pivot:
            continue
        text = re.sub(rf"{re.escape(pivot)}(?![，。！？；：、…])", f"{pivot}，", text, count=1)
    return text


async def generate_edge_coverage(entries: list[dict], cards_by_id: dict[str, dict], args: argparse.Namespace) -> None:
    import edge_tts

    targets = entries[: args.limit or None]
    edge_index = load_edge_index()
    qwen_ids: set[str] = set()
    if MANIFEST_PATH.exists():
        previous_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        qwen_ids = {
            item["id"] for item in previous_manifest.get("entries", [])
            if item.get("backend") == "qwen3-tts-voice-design-clone"
        }
    recovered = 0
    for entry in targets:
        output = ROOT / "web-game" / entry["file"]
        if output.exists() and entry["id"] not in edge_index and entry["id"] not in qwen_ids:
            profile = edge_profile(cards_by_id[entry["voiceCardId"]], entry)
            edge_index[entry["id"]] = {
                "backend": "edge-tts",
                "model": "edge-tts/7.3.1",
                "voice": profile["voice"],
                "prosody": {key: profile[key] for key in ("rate", "pitch", "volume")},
                "contextualProsody": profile["contextual"],
            }
            recovered += 1
    if recovered:
        save_edge_index(edge_index)
        print(f"Recovered {recovered} completed coverage files into the render index", flush=True)
    pending = [entry for entry in targets if args.force or not (ROOT / "web-game" / entry["file"]).exists()]
    if not pending:
        print(f"Coverage audio already present: {len(targets)}", flush=True)
        write_manifest()
        return

    temp_root = ROOT / "output" / "voice-production" / "tmp-edge"
    temp_root.mkdir(parents=True, exist_ok=True)
    concurrency = max(1, args.batch_size)
    semaphore = asyncio.Semaphore(concurrency)
    completed = 0

    async def render(entry: dict) -> tuple[str, dict]:
        nonlocal completed
        card = cards_by_id[entry["voiceCardId"]]
        profile = edge_profile(card, entry)
        source = temp_root / f"{entry['id']}.mp3"
        output = ROOT / "web-game" / entry["file"]
        replacement = output.with_suffix(".new.ogg")
        output.parent.mkdir(parents=True, exist_ok=True)
        async with semaphore:
            error: Exception | None = None
            for attempt in range(1, 5):
                try:
                    communicate = edge_tts.Communicate(
                        edge_synthesis_text(entry), profile["voice"], rate=profile["rate"],
                        pitch=profile["pitch"], volume=profile["volume"],
                    )
                    await asyncio.wait_for(communicate.save(str(source)), timeout=35)
                    await asyncio.to_thread(encode_opus, source, replacement)
                    replacement.replace(output)
                    source.unlink(missing_ok=True)
                    completed += 1
                    if completed == 1 or completed % 25 == 0 or completed == len(pending):
                        print(f"[coverage {completed}/{len(pending)}] {entry['speaker']}", flush=True)
                    return entry["id"], {
                        "backend": "edge-tts",
                        "model": "edge-tts/7.3.1",
                        "voice": profile["voice"],
                        "prosody": {key: profile[key] for key in ("rate", "pitch", "volume")},
                        "contextualProsody": profile["contextual"],
                    }
                except Exception as exc:
                    error = exc
                    source.unlink(missing_ok=True)
                    replacement.unlink(missing_ok=True)
                    if attempt < 4:
                        await asyncio.sleep(attempt * 1.5)
            raise RuntimeError(f"Edge coverage failed for {entry['id']}: {error}")

    for offset in range(0, len(pending), concurrency):
        batch = pending[offset:offset + concurrency]
        results = await asyncio.gather(*(render(entry) for entry in batch))
        edge_index.update(dict(results))
        batch_number = offset // concurrency + 1
        batch_count = math.ceil(len(pending) / concurrency)
        if batch_number % 10 == 0 or batch_number == batch_count:
            save_edge_index(edge_index)
    write_manifest()


def write_manifest() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_id = {card["id"]: card for card in cards}
    edge_index = load_edge_index()
    contextual_index = (
        json.loads(CONTEXTUAL_INDEX_PATH.read_text(encoding="utf-8"))
        if CONTEXTUAL_INDEX_PATH.exists() else {}
    )
    occurrences_by_entry: dict[str, list[dict]] = defaultdict(list)
    for occurrence in plan.get("occurrences", []):
        occurrences_by_entry[occurrence["entryId"]].append({
            key: occurrence[key]
            for key in ("contextId", "stageId", "section", "sourceIndex", "chunkIndex", "timelineIndex")
        })
    manifest_entries = []
    backend_counts: dict[str, int] = defaultdict(int)
    for entry in plan["entries"]:
        output = ROOT / "web-game" / entry["file"]
        if not output.exists():
            continue
        contextual_render = contextual_index.get(entry["id"])
        edge_render = edge_index.get(entry["id"])
        render = contextual_render or edge_render or {
            "backend": "qwen3-tts-voice-design-clone",
            "model": QWEN_MODEL_NAME,
            "voice": entry["voiceCardId"],
        }
        card = cards_by_id[entry["voiceCardId"]]
        backend_counts[render["backend"]] += 1
        manifest_entry = {
            "id": entry["id"],
            "speaker": entry["speaker"],
            "text": entry["text"],
            "file": entry["file"],
            "duration": duration_seconds(output),
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "voice": render["voice"],
            "backend": render["backend"],
            "model": render["model"],
            "voiceCardId": entry["voiceCardId"],
            "gender": card["gender"],
            "genderVerification": (
                "provider-voice-contract" if render["backend"] == "edge-tts"
                else render.get("genderVerification", "unverified")
            ),
            "humanReview": render.get("humanReview", "not_applicable"),
            "sourceSha256": render.get("sourceSha256", ""),
            "ageBand": card["ageBand"],
            "ageBasis": card["ageBasis"],
            "delivery": {
                key: entry["delivery"][key]
                for key in ("emotion", "intensity", "pace", "pauseStrength", "dominance", "styleAnchor")
            },
            "contextId": entry["context"]["id"],
            "firstOccurrence": entry["firstOccurrence"],
            "styleAnchor": entry["delivery"].get("styleAnchor", "neutral"),
            "occurrences": occurrences_by_entry.get(entry["id"], []),
        }
        if render.get("prosody"):
            manifest_entry["prosody"] = render["prosody"]
        if render.get("contextualProsody"):
            manifest_entry["contextualProsody"] = render["contextualProsody"]
        manifest_entries.append(manifest_entry)
    hybrid = len(backend_counts) > 1
    manifest = {
        "schemaVersion": 5,
        "backend": "hybrid" if hybrid else next(iter(backend_counts), "unknown"),
        "model": "Qwen3-TTS high-quality plus Edge age-directed coverage" if hybrid else next((entry["model"] for entry in manifest_entries), ""),
        "backendCounts": dict(sorted(backend_counts.items())),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "narrationExcluded": True,
        "entries": manifest_entries,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Manifest entries: {len(manifest_entries)}", flush=True)


def main() -> None:
    args = parse_args()
    if args.phase in {"references", "dialogue", "all"} and importlib.util.find_spec("qwen_tts") is None:
        if not QWEN_PYTHON.exists():
            raise RuntimeError("Qwen TTS runtime is missing; install qwen-tts in the project voice environment")
        result = subprocess.run([str(QWEN_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])
        raise SystemExit(result.returncode)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe are required")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    card_list = json.loads(CARDS_PATH.read_text(encoding="utf-8"))["cards"]
    cards_by_name = {card["speaker"]: card for card in card_list}
    cards_by_id = {card["id"]: card for card in card_list}
    stages = None if args.stages.strip().lower() == "all" else {item.strip() for item in args.stages.split(",") if item.strip()}
    speakers = {item.strip() for item in args.speakers.split(",") if item.strip()}
    entries, cards = selected_assets(plan, cards_by_name, stages, speakers)
    print(json.dumps({"selectedSpeakers": len(cards), "selectedLines": len(entries), "stages": sorted(stages) if stages else "all"}, ensure_ascii=False), flush=True)
    if args.phase in {"references", "all"}:
        design_references(cards, args)
    if args.phase in {"dialogue", "all"}:
        generate_dialogue(entries, cards_by_id, args)
    if args.phase == "coverage":
        asyncio.run(generate_edge_coverage(entries, cards_by_id, args))


if __name__ == "__main__":
    main()
