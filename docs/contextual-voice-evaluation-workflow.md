# Contextual voice evaluation workflow

This workflow keeps generated speech outside `web-game` until every required gate passes.

## 1. Generate isolated VoiceDesign candidates

```powershell
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe `
  tools/generate-contextual-voice-candidates.py `
  --stages 01 --one-per-speaker --candidates 4
```

The automatic rank uses waveform quality, speech rate, pause structure, and energy dynamics. Pitch is an alert only and is excluded from rank and promotion gates.

## 2. Evaluate candidates

```powershell
$env:HF_ENDPOINT='https://hf-mirror.com'
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe `
  tools/evaluate-contextual-voice-candidates.py --asr --speaker-embeddings --device cpu
```

The evaluator writes:

- acoustic metrics to `output/voice-production/contextual-candidate-index.json`;
- independent ASR transcripts and CER to each candidate;
- ECAPA-TDNN embeddings to `output/voice-production/speaker-embeddings`;
- a run summary to `output/voice-production/contextual-evaluation-summary.json`.

ASR CER is normalized to simplified Chinese. Ancient names and terms still require human review.

## 3. Run blind review

```powershell
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe `
  tools/serve-contextual-voice-review.py --port 8766
```

Open `http://127.0.0.1:8766/`. Candidate numbers and automatic scores are hidden. Review all dimensions and hard errors before approving a single candidate as a character anchor.

Single-reviewer anchor approval does not authorize shipping. It only allows the next cross-sentence experiment.

## 4. Generate cross-sentence clone candidates

```powershell
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe `
  tools/generate-approved-voice-clones.py --stages 01 --candidates 2
```

The command refuses to run until at least one anchor has been approved. Clone output remains under `output/voice-production/approved-voice-clones` and cannot overwrite shipped audio.

## 5. Verify

```powershell
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe tools/test_voice_quality_metrics.py
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe tools/verify-contextual-voice-candidates.py
python tools/verify-dialogue-audio.py
```

Production promotion additionally requires distinct-text identity calibration, panel blind review, and explicit deployment approval.
