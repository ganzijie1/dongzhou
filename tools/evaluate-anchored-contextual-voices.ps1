param(
    [string]$Python = "E:\game\dev-gzj\.tools\venvs\qwen3-tts\Scripts\python.exe",
    [string]$Index = "output\voice-production\anchored-contextual-clone-index.json",
    [string]$EntryIdFile = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$tool = Join-Path $PSScriptRoot "evaluate-contextual-voice-candidates.py"
$selectionArgs = @()
if ($EntryIdFile) {
    $selectionArgs = @("--entry-id-file", $EntryIdFile)
}

& $Python $tool --index $Index --asr --device cuda @selectionArgs
if ($LASTEXITCODE -ne 0) { throw "ASR evaluation failed" }

& $Python $tool --index $Index --speaker-embeddings --device cuda @selectionArgs
if ($LASTEXITCODE -ne 0) { throw "ECAPA identity evaluation failed" }

& $Python $tool --index $Index --wavlm-embeddings --device cuda @selectionArgs
if ($LASTEXITCODE -ne 0) { throw "WavLM identity evaluation failed" }

& $Python $tool --index $Index --emotion --device cuda @selectionArgs
if ($LASTEXITCODE -ne 0) { throw "Emotion evaluation failed" }

& $Python $tool --index $Index --research-demographics --device cuda @selectionArgs
if ($LASTEXITCODE -ne 0) { throw "Demographic soft-evidence evaluation failed" }

& $Python (Join-Path $PSScriptRoot "verify-contextual-voice-candidates.py") --index $Index
if ($LASTEXITCODE -ne 0) { throw "Contextual voice verification failed" }
