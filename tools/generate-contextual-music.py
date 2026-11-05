#!/usr/bin/env python3
"""Render compact, context-conditioned music assets from the Dongzhou music plan."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "web-game" / "audio" / "context-music-plan.json"
MANIFEST_PATH = ROOT / "web-game" / "audio" / "context-music-manifest.json"
SAMPLE_RATE = 24_000

MODE_DEGREES = {
    "zhi-pentatonic": (0, 2, 5, 7, 9),
    "yu-pentatonic": (0, 3, 5, 7, 10),
    "shang-pentatonic": (0, 2, 5, 7, 10),
}

MOOD_ROOTS = {
    "grief": 48,
    "threat": 43,
    "ritual": 50,
    "hope": 53,
    "intrigue": 46,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="", help="Optional exact stage ID.")
    parser.add_argument("--kind", default="", help="Optional cue kind.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def midi_frequency(note: float) -> float:
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))


def envelope(length: int, attack: float, release: float) -> np.ndarray:
    env = np.ones(length, dtype=np.float32)
    attack_n = min(length, max(1, int(length * attack)))
    release_n = min(length, max(1, int(length * release)))
    env[:attack_n] = np.linspace(0.0, 1.0, attack_n, dtype=np.float32)
    env[-release_n:] *= np.linspace(1.0, 0.0, release_n, dtype=np.float32)
    return env


def pan_add(track: np.ndarray, signal: np.ndarray, start: int, pan: float, gain: float = 1.0) -> None:
    if start >= len(track) or not len(signal):
        return
    end = min(len(track), start + len(signal))
    source = signal[: end - start] * gain
    angle = (max(-1.0, min(1.0, pan)) + 1.0) * math.pi / 4.0
    track[start:end, 0] += source * math.cos(angle)
    track[start:end, 1] += source * math.sin(angle)


def pluck(freq: float, seconds: float, rng: np.random.Generator) -> np.ndarray:
    count = max(1, int(SAMPLE_RATE * seconds))
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    phase = rng.uniform(0.0, math.tau)
    body = np.zeros(count, dtype=np.float32)
    for harmonic, weight in ((1, 1.0), (2, 0.36), (3, 0.18), (5, 0.08)):
        body += weight * np.sin(math.tau * freq * harmonic * t + phase / harmonic)
    pick = rng.normal(0.0, 0.18, count).astype(np.float32) * np.exp(-t * 28.0)
    return (body * np.exp(-t * 4.6) + pick) * envelope(count, 0.003, 0.28)


def breath_flute(freq: float, seconds: float, rng: np.random.Generator) -> np.ndarray:
    count = max(1, int(SAMPLE_RATE * seconds))
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    vibrato = 1.0 + 0.004 * np.sin(math.tau * 4.7 * t + rng.uniform(0, math.tau))
    phase = np.cumsum(math.tau * freq * vibrato / SAMPLE_RATE, dtype=np.float64).astype(np.float32)
    tone = np.sin(phase) + 0.19 * np.sin(2.0 * phase) + 0.06 * np.sin(3.0 * phase)
    noise = rng.normal(0.0, 0.045, count).astype(np.float32)
    return (tone + noise) * envelope(count, 0.12, 0.22)


def bell(freq: float, seconds: float, rng: np.random.Generator) -> np.ndarray:
    count = max(1, int(SAMPLE_RATE * seconds))
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    phase = rng.uniform(0, math.tau)
    partials = ((1.0, 1.0, 2.1), (1.47, 0.42, 2.8), (2.09, 0.24, 3.5), (2.73, 0.12, 4.4))
    out = sum(weight * np.sin(math.tau * freq * ratio * t + phase) * np.exp(-t * decay)
              for ratio, weight, decay in partials)
    return np.asarray(out, dtype=np.float32) * envelope(count, 0.002, 0.18)


def drum(seconds: float, rng: np.random.Generator, low: bool = True) -> np.ndarray:
    count = max(1, int(SAMPLE_RATE * seconds))
    t = np.arange(count, dtype=np.float32) / SAMPLE_RATE
    start_freq = 105.0 if low else 180.0
    end_freq = 45.0 if low else 82.0
    phase = math.tau * (end_freq * t + (start_freq - end_freq) * (1.0 - np.exp(-t * 16.0)) / 16.0)
    body = np.sin(phase) * np.exp(-t * (7.0 if low else 11.0))
    strike = rng.normal(0.0, 0.32, count).astype(np.float32) * np.exp(-t * 38.0)
    return (body + strike) * envelope(count, 0.001, 0.12)


def add_delay(track: np.ndarray, delay_seconds: float, feedback: float) -> None:
    delay = int(SAMPLE_RATE * delay_seconds)
    if delay <= 0 or delay >= len(track):
        return
    track[delay:] += track[:-delay] * feedback


def mode_notes(cue: dict) -> tuple[int, ...]:
    root = MOOD_ROOTS.get(cue.get("mood"), 48)
    degrees = MODE_DEGREES.get(cue.get("mode"), MODE_DEGREES["yu-pentatonic"])
    return tuple(root + degree for degree in degrees)


def render(cue: dict) -> np.ndarray:
    duration = float(cue["durationTarget"])
    samples = int(round(duration * SAMPLE_RATE))
    track = np.zeros((samples, 2), dtype=np.float32)
    rng = np.random.default_rng(int(cue["seed"]))
    notes = mode_notes(cue)
    tempo = float(cue["tempo"])
    beat = 60.0 / tempo
    bar = beat * 4.0
    density = float(cue["density"])
    loop = bool(cue.get("loop"))

    # A quiet tonal floor prevents dead air without claiming historical reconstruction.
    t = np.arange(samples, dtype=np.float32) / SAMPLE_RATE
    root_freq = midi_frequency(notes[0] - 12)
    drone = 0.055 * np.sin(math.tau * root_freq * t)
    drone += 0.022 * np.sin(math.tau * root_freq * 1.5 * t + 0.7)
    breath = rng.normal(0.0, 0.006, samples).astype(np.float32)
    floor = (drone + breath).astype(np.float32)
    track[:, 0] += floor
    track[:, 1] += np.roll(floor, 31)

    bars = max(1, int(math.ceil(duration / bar)))
    motif = [notes[(int(cue["seed"]) >> (index * 3)) % len(notes)] for index in range(6)]
    if cue.get("mood") == "hope":
        motif = sorted(motif)
    elif cue.get("mood") == "grief":
        motif = sorted(motif, reverse=True)

    for bar_index in range(bars):
        bar_start = bar_index * bar
        if bar_start >= duration:
            break
        pattern_steps = 4 if density < 0.42 else 6 if density < 0.66 else 8
        for step in range(pattern_steps):
            if rng.random() > density + 0.12:
                continue
            start_seconds = bar_start + step * bar / pattern_steps
            note = motif[(bar_index + step) % len(motif)] + (12 if step % 5 == 4 and cue["kind"] != "defeat" else 0)
            length = min(beat * (1.25 if cue["kind"] in {"intro", "defeat"} else 0.85), duration - start_seconds)
            if length <= 0:
                continue
            signal = pluck(midi_frequency(note), length + 0.32, rng)
            pan_add(track, signal, int(start_seconds * SAMPLE_RATE), -0.42 + 0.84 * rng.random(), 0.075)

        if cue["kind"] in {"battle", "event"} or cue.get("scene") in {"siege", "ambush", "breakout"}:
            hits = (0.0, beat * 2.0) if density < 0.62 else (0.0, beat, beat * 2.0, beat * 3.0)
            for hit_index, offset in enumerate(hits):
                start_seconds = bar_start + offset
                if start_seconds >= duration:
                    continue
                signal = drum(min(0.8, duration - start_seconds), rng, low=hit_index % 2 == 0)
                pan_add(track, signal, int(start_seconds * SAMPLE_RATE), 0.0, 0.11 if cue["kind"] == "battle" else 0.085)

        if bar_index % (2 if cue["kind"] == "battle" else 3) == 0:
            start_seconds = bar_start + beat * (1.5 if cue.get("scene") == "court" else 0.5)
            if start_seconds < duration:
                note = notes[(bar_index // 2 + 2) % len(notes)] + 12
                use_bell = cue["era"] == "western-zhou" or cue.get("scene") in {"court", "ritual"}
                signal = bell(midi_frequency(note), min(2.1, duration - start_seconds), rng) if use_bell else breath_flute(midi_frequency(note), min(bar * 0.9, duration - start_seconds), rng)
                pan_add(track, signal, int(start_seconds * SAMPLE_RATE), 0.28 if bar_index % 4 else -0.28, 0.045)

    add_delay(track, min(0.34, beat * 0.75), 0.13)
    add_delay(track, min(0.61, beat * 1.5), 0.07)

    if loop:
        crossfade = min(samples // 8, int(SAMPLE_RATE * 0.7))
        if crossfade > 1:
            weight = np.linspace(0.0, 1.0, crossfade, dtype=np.float32)[:, None]
            blend = track[-crossfade:] * (1.0 - weight) + track[:crossfade] * weight
            track[:crossfade] = blend
            track[-crossfade:] = blend
    else:
        fade_in = min(samples, int(SAMPLE_RATE * 0.25))
        fade_out = min(samples, int(SAMPLE_RATE * 0.9))
        track[:fade_in] *= np.linspace(0.0, 1.0, fade_in, dtype=np.float32)[:, None]
        track[-fade_out:] *= np.linspace(1.0, 0.0, fade_out, dtype=np.float32)[:, None]

    peak = float(np.max(np.abs(track))) or 1.0
    track *= min(1.0, 0.68 / peak)
    return np.tanh(track * 1.08).astype(np.float32)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_ogg(output: Path, audio: np.ndarray) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to encode contextual music")
    temporary = output.with_suffix(".tmp.wav")
    try:
        sf.write(temporary, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(temporary), "-c:a", "libopus", "-b:a", "48k",
            "-vbr", "on", "-application", "audio", str(output),
        ], check=True)
    finally:
        temporary.unlink(missing_ok=True)


def render_asset(cue: dict, force: bool) -> dict:
    output = ROOT / "web-game" / cue["file"]
    output.parent.mkdir(parents=True, exist_ok=True)
    if force or not output.exists():
        write_ogg(output, render(cue))
    info = sf.info(output)
    return {
        **cue,
        "duration": round(info.frames / info.samplerate, 3),
        "sampleRate": info.samplerate,
        "channels": info.channels,
        "bytes": output.stat().st_size,
        "sha256": sha256(output),
    }


def main() -> None:
    args = parse_args()
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    cues = [cue for cue in plan["cues"] if (not args.stage or cue["stageId"] == args.stage) and (not args.kind or cue["kind"] == args.kind)]
    cues = cues[: args.limit or None]
    rendered_by_id: dict[str, dict] = {}
    jobs = max(1, min(12, int(args.jobs)))
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        pending = {executor.submit(render_asset, cue, args.force): cue for cue in cues}
        for index, future in enumerate(concurrent.futures.as_completed(pending), start=1):
            item = future.result()
            rendered_by_id[item["id"]] = item
            if index == 1 or index % 25 == 0 or index == len(cues):
                print(f"[music {index}/{len(cues)}] {item['id']}", flush=True)
    rendered = [rendered_by_id[cue["id"]] for cue in cues]

    if len(cues) != len(plan["cues"]):
        print("Partial render complete; manifest not replaced.", flush=True)
        return
    manifest = {
        "schemaVersion": int(plan.get("schemaVersion") or 1),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generator": plan["generator"],
        "policy": plan["policy"],
        "summary": {
            **plan["summary"],
            "renderedCues": len(rendered),
            "totalBytes": sum(item["bytes"] for item in rendered),
        },
        "cues": rendered,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["summary"], ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
