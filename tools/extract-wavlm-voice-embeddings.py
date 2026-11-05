#!/usr/bin/env python3
"""Extract WavLM X-vectors without importing the Qwen/SpeechBrain environment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly
from transformers import Wav2Vec2FeatureExtractor, WavLMForXVector


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
INDEX_PATH = ROOT / "output" / "voice-production" / "contextual-candidate-index.json"
OUTPUT_ROOT = ROOT / "output" / "voice-production" / "speaker-embeddings" / "wavlm"
MODEL_CACHE_ROOT = WORKSPACE / ".tools" / "models"
MODEL_ID = "microsoft/wavlm-base-plus-sv"


def safe_audio(relative_name: str) -> Path:
    relative = Path(relative_name)
    path = (ROOT / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or ROOT.resolve() not in path.parents or not path.is_file():
        raise RuntimeError(f"Unsafe or missing candidate path: {relative}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_ID, cache_dir=str(MODEL_CACHE_ROOT))
    model = WavLMForXVector.from_pretrained(MODEL_ID, cache_dir=str(MODEL_CACHE_ROOT)).to(args.device)
    model.eval()
    processed = 0
    for entry in index["entries"]:
        for candidate in entry.get("candidates", []):
            if args.limit and processed >= args.limit:
                break
            audio, sample_rate = sf.read(safe_audio(candidate["file"]), dtype="float32")
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            if sample_rate != 16000:
                divisor = np.gcd(sample_rate, 16000)
                audio = resample_poly(audio, 16000 // divisor, sample_rate // divisor).astype(np.float32)
            inputs = extractor(audio, sampling_rate=16000, return_tensors="pt")
            inputs = {name: value.to(args.device) for name, value in inputs.items()}
            with torch.inference_mode():
                embedding = model(**inputs).embeddings.squeeze(0)
                embedding = torch.nn.functional.normalize(embedding, dim=-1).cpu().numpy().astype(np.float32)
            output = OUTPUT_ROOT / entry["entryId"] / f"candidate-{candidate['candidate']}.npy"
            output.parent.mkdir(parents=True, exist_ok=True)
            np.save(output, embedding)
            candidate["wavlmSpeakerEmbedding"] = {
                "model": MODEL_ID,
                "dimension": int(embedding.shape[0]),
                "file": str(output.relative_to(ROOT)).replace("\\", "/"),
                "thresholdPolicy": "project_calibration_required",
            }
            processed += 1
        if args.limit and processed >= args.limit:
            break
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": "PASS",
        "model": MODEL_ID,
        "device": args.device,
        "processed": processed,
        "thresholdPolicy": "project_calibration_required",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
