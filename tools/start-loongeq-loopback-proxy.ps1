$ErrorActionPreference = "Continue"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root "integration-service\.venv\Scripts\python.exe"
$proxy = Join-Path $PSScriptRoot "loongeq-loopback-proxy.py"

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Dongzhou integration Python environment is missing: $python"
}

while ($true) {
    & $python $proxy
    Start-Sleep -Seconds 5
}
