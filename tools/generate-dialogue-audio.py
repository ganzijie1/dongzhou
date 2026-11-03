#!/usr/bin/env python3
"""Generate the first Dongzhou dialogue slice with Qwen3-TTS."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
DEFAULT_CACHE = WORKSPACE / ".tools" / "huggingface"
os.environ.setdefault("HF_HOME", str(DEFAULT_CACHE))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


REMOTE_MODEL_ID = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
LOCAL_MODEL_DIR = WORKSPACE / ".tools" / "models" / "Qwen3-TTS-12Hz-1.7B-CustomVoice"


def local_qwen_model_is_complete() -> bool:
    model_file = LOCAL_MODEL_DIR / "model.safetensors"
    tokenizer_file = LOCAL_MODEL_DIR / "speech_tokenizer" / "model.safetensors"
    incomplete_files = list(LOCAL_MODEL_DIR.rglob("*.incomplete")) if LOCAL_MODEL_DIR.exists() else []
    return (
        model_file.exists()
        and model_file.stat().st_size > 3_000_000_000
        and tokenizer_file.exists()
        and tokenizer_file.stat().st_size > 500_000_000
        and not incomplete_files
    )


MODEL_ID = str(LOCAL_MODEL_DIR) if local_qwen_model_is_complete() else REMOTE_MODEL_ID
OUTPUT_DIR = ROOT / "web-game" / "audio" / "dialogue" / "chapter-01"
MANIFEST_PATH = ROOT / "web-game" / "audio" / "dialogue-manifest.json"
CAMPAIGN_PATH = ROOT / "web-game" / "scenario" / "campaign.json"


SAMPLES = [
    {
        "id": "01-narrator-01",
        "speaker": "旁白",
        "voice": "Serena",
        "text": "三十九年，宣王征姜戎败于千亩，王师伤亡惨重，王心自此多疑。",
        "context": "第一回开端，交代周宣王由中兴转向多疑的历史背景。",
        "instruction": "庄重克制的历史叙事，语速稍慢，字音清楚，避免新闻播报腔和夸张表演。",
    },
    {
        "id": "01-narrator-02",
        "speaker": "旁白",
        "voice": "Serena",
        "text": "杜伯含冤伏诛。左儒痛哭收尸，回家后自刎而死。",
        "context": "忠臣被冤杀后的沉痛转折，场景肃静。",
        "instruction": "低沉哀恸但保持克制，句间留出短暂停顿，不煽情，不使用现代短视频腔。",
    },
    {
        "id": "01-narrator-03",
        "speaker": "旁白",
        "voice": "Serena",
        "text": "三年后，宣王率百官东郊游猎。旌旗蔽日，车马雷动。",
        "context": "时间推进到东郊围猎，表面盛大，暗含索命将至。",
        "instruction": "庄重叙事，前半平稳，后半略增强压迫感，语速中等，吐字清楚。",
    },
    {
        "id": "01-king-01",
        "speaker": "周宣王",
        "voice": "Uncle_Fu",
        "text": "市井孩童唱的是何等妖言？速召百官入朝解说！",
        "context": "周宣王听见亡周童谣，帝王威严之下已经产生疑惧。",
        "instruction": "成年帝王男声，威严、疑惧而克制，后一句是急促命令，不要咆哮。",
    },
    {
        "id": "01-king-02",
        "speaker": "周宣王",
        "voice": "Uncle_Fu",
        "text": "那弃女至今无踪，司市官杜伯办事不力，推出斩首！",
        "context": "梦兆之后迁怒杜伯，君王以权威压制事实。",
        "instruction": "成年帝王男声，冷硬、多疑、决断，末句短促有压迫感，但不要戏曲化。",
    },
    {
        "id": "01-king-03",
        "speaker": "周宣王",
        "voice": "Uncle_Fu",
        "text": "君叫臣死，臣不得不死。再敢多言，与杜伯同罪！",
        "context": "左儒为杜伯进谏，周宣王拒绝并威胁同罪。",
        "instruction": "低沉威严，第一句傲慢笃定，第二句明显加重，保持宫廷人物的克制。",
    },
    {
        "id": "01-king-04",
        "speaker": "周宣王",
        "voice": "Uncle_Fu",
        "text": "今日围猎，众卿随寡人尽兴而归！",
        "context": "三年后的东郊围猎，周宣王尚未察觉杜伯亡魂将至。",
        "instruction": "帝王男声，兴致高昂而从容，公开对百官讲话，声音有户外距离感。",
    },
    {
        "id": "01-dubo-01",
        "speaker": "杜伯",
        "voice": "Dylan",
        "text": "臣奉命搜访多年，并无踪迹。无罪而杀臣，何以服天下？",
        "context": "杜伯面对死刑仍以臣礼进谏，悲愤但不失理性。",
        "instruction": "成年忠臣男声，沉稳、悲愤、清醒，前句陈述事实，末句有质问力度但不嘶吼。",
    },
    {
        "id": "01-dubo-02",
        "speaker": "杜伯",
        "voice": "Dylan",
        "text": "若死者无知，此事便休；若死者有知，三年之内，必使王知妄杀之报。",
        "context": "杜伯临刑立誓，仍保持忠臣的沉着，预示三年后东郊索命。",
        "instruction": "低沉坚定的成年男声，语速稍慢，前后两层形成递进，最后一句冷峻有力。",
    },
    {
        "id": "01-dubo-03",
        "speaker": "杜伯",
        "voice": "Dylan",
        "text": "赤弓在手，白矢已发。周王，偿还你滥杀忠良的血债吧！",
        "context": "杜伯亡魂驾白马素车现于东郊，远距离向周宣王索命。",
        "instruction": "保持同一忠臣声纹，加入亡魂般冷峻与远距离喊话感，悲愤强烈但不要狂乱。",
    },
    {
        "id": "01-dubo-04",
        "speaker": "杜伯",
        "voice": "Dylan",
        "text": "周王，白矢在此！",
        "context": "东郊战斗胜利瞬间，杜伯放箭击中周宣王。",
        "instruction": "短促、决绝、有穿透力的战场喊话，保持成年忠臣音色，不拖长尾音。",
    },
    {
        "id": "01-zuoru-01",
        "speaker": "左儒",
        "voice": "Eric",
        "text": "杜伯无罪。王若必杀忠臣，臣愿以死相谏！",
        "context": "左儒在朝堂冒死为杜伯辩护，忠直而急切。",
        "instruction": "成年臣子男声，忠直、急切、悲愤，礼制用语清楚，末句坚定，不要轻浮。",
    },
    {
        "id": "01-zuoru-02",
        "speaker": "左儒",
        "voice": "Eric",
        "text": "昏王可还记得无罪而死的杜大夫？今日东郊，正是鸣冤之时！",
        "context": "左儒亡魂随杜伯现身东郊，当面斥责周宣王。",
        "instruction": "保持同一忠臣声纹，愤怒而悲恸，户外远距离喊话，吐字清楚，不要喜剧化。",
    },
    {
        "id": "01-zuoru-03",
        "speaker": "左儒",
        "voice": "Eric",
        "text": "王师势众，今日未能使沉冤昭雪……",
        "context": "战斗失败，左儒亡魂不甘退去，冤情仍未昭雪。",
        "instruction": "保持同一忠臣声纹，气力渐弱、悲痛不甘，末尾自然收住，不要夸张哭腔。",
    },
]


EDGE_PROFILES = {
    "旁白": {"voice": "zh-CN-XiaoxiaoNeural", "rate": "-8%", "pitch": "-3Hz", "volume": "+0%"},
    "周宣王": {"voice": "zh-CN-YunyangNeural", "rate": "-3%", "pitch": "-8Hz", "volume": "+4%"},
    "杜伯": {"voice": "zh-CN-YunxiNeural", "rate": "-6%", "pitch": "-5Hz", "volume": "+2%"},
    "左儒": {"voice": "zh-CN-YunjianNeural", "rate": "-2%", "pitch": "-2Hz", "volume": "+2%"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_ID)
    parser.add_argument("--backend", choices=("qwen", "edge"), default="qwen")
    parser.add_argument("--limit", type=int, default=0, help="Generate only the first N samples.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def validate_source_text(samples: list[dict]) -> None:
    campaign = json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))
    stage = next(item for item in campaign["stages"] if item["id"] == "01")
    source_lines = set()
    for section in ("intro", "events", "victory", "defeat"):
        raw = stage.get("story", {}).get(section, [])
        entries = raw if isinstance(raw, list) else list(raw.values())
        source_lines.update(str(entry.get("text", "")) for entry in entries)
    missing = [sample["text"] for sample in samples if sample["text"] not in source_lines]
    if missing:
        raise RuntimeError("Curated speech is absent from campaign.json: " + " | ".join(missing))


def encode_opus(wav_path: Path, output_path: Path) -> None:
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav_path),
        "-af", "loudnorm=I=-18:LRA=7:TP=-1.5", "-ar", "48000", "-ac", "1",
        "-c:a", "libopus", "-b:a", "56k", "-vbr", "on", str(output_path),
    ]
    subprocess.run(command, check=True)


def edge_profile(sample: dict) -> dict:
    profile = dict(EDGE_PROFILES[sample["speaker"]])
    if sample["id"] in {"01-narrator-02", "01-dubo-02"}:
        profile["rate"] = "-12%"
    elif sample["id"] in {"01-king-04", "01-dubo-04"}:
        profile["rate"] = "+4%"
    elif sample["id"] == "01-zuoru-03":
        profile.update(rate="-14%", pitch="-5Hz", volume="-3%")
    return profile


async def generate_edge_audio(sample: dict, output_path: Path) -> dict:
    import edge_tts

    profile = edge_profile(sample)
    communicate = edge_tts.Communicate(
        sample["text"],
        profile["voice"],
        rate=profile["rate"],
        pitch=profile["pitch"],
        volume=profile["volume"],
    )
    await communicate.save(str(output_path))
    return profile


def duration_seconds(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return round(float(result.stdout.strip()), 3)


def main() -> None:
    args = parse_args()
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe are required")

    samples = SAMPLES[: args.limit or None]
    validate_source_text(samples)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model = None
    torch = None
    sf = None
    if args.backend == "qwen":
        import soundfile as soundfile
        import torch as torch_module
        from qwen_tts import Qwen3TTSModel

        sf = soundfile
        torch = torch_module
        dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
        print(f"Loading {args.model} on {args.device} with {dtype}", flush=True)
        model = Qwen3TTSModel.from_pretrained(
            args.model,
            device_map=args.device,
            dtype=dtype,
            attn_implementation="sdpa",
        )

    manifest_entries = []
    for index, sample in enumerate(samples, start=1):
        output_path = OUTPUT_DIR / f"{sample['id']}.ogg"
        source_path = OUTPUT_DIR / f".{sample['id']}.{'mp3' if args.backend == 'edge' else 'wav'}"
        render_voice = sample["voice"]
        render_profile = {}
        if args.force or not output_path.exists():
            print(f"[{index}/{len(samples)}] {sample['speaker']}: {sample['text']}", flush=True)
            if args.backend == "edge":
                render_profile = asyncio.run(generate_edge_audio(sample, source_path))
                render_voice = render_profile["voice"]
            else:
                seed = int.from_bytes(hashlib.sha256(sample["id"].encode("utf-8")).digest()[:4], "big")
                torch.manual_seed(seed)
                wavs, sample_rate = model.generate_custom_voice(
                    text=sample["text"],
                    language="Chinese",
                    speaker=sample["voice"],
                    instruct=sample["instruction"],
                )
                sf.write(source_path, wavs[0], sample_rate)
            encode_opus(source_path, output_path)
            source_path.unlink(missing_ok=True)
        elif args.backend == "edge":
            render_profile = edge_profile(sample)
            render_voice = render_profile["voice"]

        file_hash = hashlib.sha256(output_path.read_bytes()).hexdigest()
        manifest_entries.append({
            **sample,
            "voice": render_voice,
            "prosody": render_profile,
            "file": f"audio/dialogue/chapter-01/{output_path.name}",
            "duration": duration_seconds(output_path),
            "sha256": file_hash,
        })

    manifest = {
        "schemaVersion": 1,
        "backend": args.backend,
        "model": args.model if args.backend == "qwen" else "edge-tts/7.3.1",
        "stageId": "01",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "entries": manifest_entries,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH} with {len(manifest_entries)} entries", flush=True)


if __name__ == "__main__":
    main()
