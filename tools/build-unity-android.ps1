param(
    [string]$UnityPath = "",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$projectPath = Join-Path $repoRoot "unity-remake"

if ([string]::IsNullOrWhiteSpace($UnityPath)) {
    $UnityPath = Join-Path ${env:ProgramFiles} "Unity\Hub\Editor\2022.3.62f1\Editor\Unity.exe"
}
if (-not (Test-Path -LiteralPath $UnityPath)) {
    throw "Unity 2022.3.62f1 was not found at: $UnityPath"
}
if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $env:DONGZHOU_ANDROID_OUTPUT = [System.IO.Path]::GetFullPath($OutputPath)
}

& $UnityPath -batchmode -quit -projectPath $projectPath `
    -executeMethod DongZhou.UnityRemake.Editor.MobileBuild.BuildAndroid `
    -logFile "-"
if ($LASTEXITCODE -ne 0) {
    throw "Unity Android build failed with exit code $LASTEXITCODE"
}

$resolvedOutput = if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    Join-Path $projectPath "Builds\Android\Dongzhou.apk"
} else {
    [System.IO.Path]::GetFullPath($OutputPath)
}
$modelPath = Join-Path $projectPath "Assets\Resources\Models\HappoMobile.onnx"
$manifestPath = [System.IO.Path]::ChangeExtension($resolvedOutput, ".build.json")
$manifest = [ordered]@{
    artifact = [System.IO.Path]::GetFileName($resolvedOutput)
    artifact_bytes = (Get-Item -LiteralPath $resolvedOutput).Length
    artifact_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedOutput).Hash.ToLowerInvariant()
    built_at = (Get-Date).ToUniversalTime().ToString("o")
    unity = "2022.3.62f1 (4af31df58517)"
    package = "com.deepsignal.dongzhou"
    version_name = "0.1.0"
    version_code = 1
    min_api = 26
    target_api = 36
    architecture = "ARM64"
    scripting_backend = "IL2CPP"
    model_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $modelPath).Hash.ToLowerInvariant()
}
$manifest | ConvertTo-Json | Set-Content -Encoding utf8 -LiteralPath $manifestPath
Get-Item -LiteralPath $resolvedOutput,$manifestPath | Select-Object FullName,Length
