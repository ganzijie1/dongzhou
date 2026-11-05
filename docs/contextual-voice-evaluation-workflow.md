# Contextual voice evaluation workflow

This workflow keeps generated speech outside `web-game` until every required gate passes.

## 1. Generate isolated VoiceDesign candidates

```powershell
python tools/generate-contextual-voice-candidates.py `
  --stages 01 --speakers 周宣王,杜伯,左儒 --candidates 3
```

The launcher automatically re-enters the project Qwen environment when the default Python does not expose `qwen_tts`. The production plan compiles long-term memory, previous and following turns, speech act, subtext, state transition, pivot words, focus words, and a non-uniform pause plan for every selected line.

The automatic acoustic score uses waveform quality, speech rate, pause structure, and energy dynamics to order listening work only. It is not a quality score or a release threshold. Pitch is an alert only and is excluded from promotion gates.

## 2. Evaluate candidates

```powershell
$env:HF_ENDPOINT='https://hf-mirror.com'
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe `
  tools/evaluate-contextual-voice-candidates.py --asr --speaker-embeddings --device cpu

$env:HF_ENDPOINT='https://hf-mirror.com'
python tools/extract-wavlm-voice-embeddings.py --device cuda

& E:\game\dev-gzj\.tools\venvs\voice-eval\Scripts\python.exe `
  tools/evaluate-contextual-voice-candidates.py --emotion --device cuda

& E:\game\dev-gzj\.tools\venvs\voice-eval\Scripts\python.exe `
  tools/evaluate-contextual-voice-candidates.py --research-demographics --device cuda
```

The evaluator writes:

- acoustic metrics to `output/voice-production/contextual-candidate-index.json`;
- independent ASR transcripts, character edits, and critical-term checks to each candidate;
- ECAPA-TDNN and WavLM X-vector evidence to `output/voice-production/speaker-embeddings`;
- emotion2vec coarse emotion probabilities and research-only age/gender soft alerts;
- a run summary to `output/voice-production/contextual-evaluation-summary.json`.
- a per-line evidence report to `output/voice-production/contextual-evaluation-report.md`.

ASR CER is normalized to simplified Chinese, but there is no universal CER pass threshold. Ancient names and terms are checked separately and still require listening confirmation. WavLM and ECAPA similarities require project-specific calibration. The age/gender model has a non-commercial license and can only be used for internal soft alerts.

## 3. Run blind review

```powershell
& E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe `
  tools/serve-contextual-voice-review.py --port 8766
```

Open `http://127.0.0.1:8766/`. Candidate numbers and automatic scores are hidden. Review all dimensions and hard errors before approving a single candidate as a character anchor. Anchor approval requires three explicitly confirmed listening scopes: isolated utterance, adjacent dialogue pair, and full scene.

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
