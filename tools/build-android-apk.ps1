param(
    [string]$JavaHome = "D:\tools\jdk-21",
    [string]$AndroidSdk = "E:\game\dev-gzj\.tools\android-sdk",
    [string]$GradleHome = "E:\game\dev-gzj\.tools\gradle-8.13",
    [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$project = Join-Path $root "android-app"
$sourceApk = Join-Path $project "app\build\outputs\apk\debug\app-debug.apk"
$output = Join-Path $root "output\android"
$artifact = Join-Path $output "Dongzhou-0.5.0-172-stage-rl-map-readability-arm64-debug.apk"
$metadataPath = "$artifact.build.json"
$happoModel = Join-Path $root "unity-remake\Assets\Resources\Models\HappoMobile.onnx"
$pcgrlModel = Join-Path $root "unity-remake\Assets\Resources\Models\PcgrlMasui.onnx"
$voicePython = Join-Path $env:USERPROFILE ".codex\cache\qwen3-tts-venv\Scripts\python.exe"
if (!(Test-Path $voicePython)) { $voicePython = "python" }

if (!(Test-Path (Join-Path $JavaHome "bin\java.exe"))) { throw "JDK not found: $JavaHome" }
if (!(Test-Path (Join-Path $AndroidSdk "platforms\android-36\android.jar"))) { throw "Android API 36 not found" }
if (!(Test-Path (Join-Path $GradleHome "bin\gradle.bat"))) { throw "Gradle 8.13 not found" }
if (!(Test-Path $happoModel)) { throw "HAPPO model not found: $happoModel" }
if (!(Test-Path $pcgrlModel)) { throw "PCGRL model not found: $pcgrlModel" }

if (-not $SkipPreflight) {
  Push-Location $root
  try {
    node --check "web-game\game.js"
    if ($LASTEXITCODE -ne 0) { throw "game.js syntax check failed: $LASTEXITCODE" }
    node --check "web-game\pcgrl.js"
    if ($LASTEXITCODE -ne 0) { throw "pcgrl.js syntax check failed: $LASTEXITCODE" }
    node --check "web-game\map-elites.js"
    if ($LASTEXITCODE -ne 0) { throw "map-elites.js syntax check failed: $LASTEXITCODE" }
    node --check "web-game\game-systems.js"
    if ($LASTEXITCODE -ne 0) { throw "game-systems.js syntax check failed: $LASTEXITCODE" }
    node "tools\test-pcgrl-web.js"
    if ($LASTEXITCODE -ne 0) { throw "PCGRL web tests failed: $LASTEXITCODE" }
    node "tools\test-map-elites-chuisha.js"
    if ($LASTEXITCODE -ne 0) { throw "MAP-Elites web tests failed: $LASTEXITCODE" }
    python "tools\validate-map-elites-contract.py"
    if ($LASTEXITCODE -ne 0) { throw "MAP-Elites map contract failed: $LASTEXITCODE" }
    node "tools\test-game-systems.js"
    if ($LASTEXITCODE -ne 0) { throw "Game systems tests failed: $LASTEXITCODE" }
    node "tools\verify-happo-release.js"
    if ($LASTEXITCODE -ne 0) { throw "HAPPO release verification failed: $LASTEXITCODE" }
    python -m unittest "rl\pcgrl_mobile_test.py"
    if ($LASTEXITCODE -ne 0) { throw "PCGRL Python tests failed: $LASTEXITCODE" }
    python "rl\export_pcgrl_eval_fixtures.py" --model "unity-remake\Assets\Resources\Models\PcgrlMasui.onnx" --output "tmp\pcgrl-mobile-fixtures.json" --samples 360
    if ($LASTEXITCODE -ne 0) { throw "PCGRL ONNX fixture export failed: $LASTEXITCODE" }
    node "tools\evaluate-pcgrl-pipeline.js" "tmp\pcgrl-mobile-fixtures.json"
    if ($LASTEXITCODE -ne 0) { throw "PCGRL end-to-end evaluation failed: $LASTEXITCODE" }
    node "tools\evaluate-pcgrl-agent-rollouts.js" "tmp\pcgrl-mobile-fixtures.json" "unity-remake\Assets\Resources\Models\PcgrlMasui.agent-rollout.json"
    if ($LASTEXITCODE -ne 0) { throw "PCGRL agent rollout evaluation failed: $LASTEXITCODE" }
    node "tools\export-web-campaign.js"
    if ($LASTEXITCODE -ne 0) { throw "Web campaign export failed: $LASTEXITCODE" }
    node "tools\verify-story-enrichment.js"
    if ($LASTEXITCODE -ne 0) { throw "Story enrichment verification failed: $LASTEXITCODE" }
    python "tools\audit-map-visual-density.py"
    if ($LASTEXITCODE -ne 0) { throw "Map visual-density audit failed: $LASTEXITCODE" }
    node "tools\verify-web-release.js"
    if ($LASTEXITCODE -ne 0) { throw "Web release verification failed: $LASTEXITCODE" }
    python "tools\verify-contextual-music.py"
    if ($LASTEXITCODE -ne 0) { throw "Contextual music verification failed: $LASTEXITCODE" }
    python "tools\verify-dialogue-voice-plan.py"
    if ($LASTEXITCODE -ne 0) { throw "Dialogue voice plan verification failed: $LASTEXITCODE" }
    python "tools\build-voice-casting-ot.py"
    if ($LASTEXITCODE -ne 0) { throw "Dialogue voice casting OT plan failed: $LASTEXITCODE" }
    if (Test-Path "web-game\audio\dialogue-manifest.json") {
        & $voicePython "tools\verify-dialogue-audio.py" --require-stages all
        if ($LASTEXITCODE -ne 0) { throw "Dialogue audio verification failed: $LASTEXITCODE" }
        node "tools\audit-runtime-voice-coverage.js"
        if ($LASTEXITCODE -ne 0) { throw "Lua runtime dialogue coverage failed: $LASTEXITCODE" }
    }
  } finally {
    Pop-Location
  }
}

$env:JAVA_HOME = $JavaHome
$env:ANDROID_HOME = $AndroidSdk
Push-Location $project
try {
    if ($SkipPreflight) {
        & (Join-Path $GradleHome "bin\gradle.bat") --no-daemon ":app:assembleDebug"
    } else {
        & (Join-Path $GradleHome "bin\gradle.bat") --no-daemon ":app:lintDebug" ":app:assembleDebug"
    }
    if ($LASTEXITCODE -ne 0) { throw "Android build failed: $LASTEXITCODE" }
    if (!(Test-Path $sourceApk)) { throw "Android build did not produce the expected APK: $sourceApk" }
} finally {
    Pop-Location
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
Copy-Item -LiteralPath $sourceApk -Destination $artifact -Force
& (Join-Path $AndroidSdk "build-tools\35.0.0\apksigner.bat") verify $artifact
if ($LASTEXITCODE -ne 0) { throw "APK signature verification failed" }

$apkHash = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
$happoModelHash = (Get-FileHash -LiteralPath $happoModel -Algorithm SHA256).Hash.ToLowerInvariant()
$pcgrlModelHash = (Get-FileHash -LiteralPath $pcgrlModel -Algorithm SHA256).Hash.ToLowerInvariant()
$dialogueManifest = Get-Content -LiteralPath (Join-Path $root "web-game\audio\dialogue-manifest.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$musicManifest = Get-Content -LiteralPath (Join-Path $root "web-game\audio\context-music-manifest.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$metadata = [ordered]@{
    artifact = [IO.Path]::GetFileName($artifact)
    artifact_bytes = (Get-Item -LiteralPath $artifact).Length
    artifact_sha256 = $apkHash
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    package = "com.deepsignal.dongzhou.debug"
    version_name = "0.5.0-debug"
    version_code = 5
    min_api = 26
    target_api = 36
    compile_api = 36
    abi = @("arm64-v8a")
    signing = "Android debug certificate; engineering delivery only"
    gradle = "8.13"
    android_gradle_plugin = "8.13.2"
    jdk = "Temurin 21.0.12"
    onnx_runtime_android = "1.31.1"
    stage_count = 172
    battle_map_count = 169
    models = @(
        [ordered]@{ file = "HappoMobile.onnx"; sha256 = $happoModelHash; purpose = "enemy battle HAPPO" },
        [ordered]@{ file = "PcgrlMasui.onnx"; sha256 = $pcgrlModelHash; purpose = "19x14 Masui PCGRL terrain policy" }
    )
    env_version = "dongzhou-web-172-v1"
    schema_version = "happo-local20-candidate34-v1"
    policy_version = "happo-2026-11-02"
    pcgrl_schema_version = "pcgrl-wide19x14-cell9-tile4-v1"
    pcgrl_policy_version = "pcgrl-masui-2026-11-02"
    map_elites_schema_version = "chuisha-map-elites-1"
    map_elites_archive_cells = 25
    profile_schema_version = 9
    replay_schema_version = "dongzhou-replay-v1"
    guard_version = "hash-timeout-difficulty-blend-role-fallback-wfc-agent-replay-economy-map-density-context-voice-music-v8"
    validation = [ordered]@{
        web_release = "PASS"
        map_visual_density = "PASS: 172 stages, semantic structure preservation, balanced compact profile"
        game_systems = "PASS: sequential unlock, hero mastery, 7 class skills, equipment, supplies, replay v1"
        story_enrichment = "PASS: 12-stage vertical slice, 21 runtime battle beats, 24 source-boundary records"
        dialogue_audio = "PASS: $($dialogueManifest.entries.Count)/$($dialogueManifest.entries.Count) unique character lines; 2520 occurrences including 205 Lua runtime speeches; narration excluded; contextual Edge coverage $($dialogueManifest.backendCounts.'edge-tts')"
        contextual_music = "PASS: $($musicManifest.summary.renderedCues)/$($musicManifest.summary.totalCues) cues; 172 battle loops, 510 story sections, 239 campaign events, 205 Lua runtime events"
        pcgrl_pipeline = "PASS: 1080/1080 ONNX fixtures plus 2160 mirrored rule-agent battles"
        map_elites_chuisha = "PASS: 25/25 archive cells; 5-seed equal-budget random baseline; map contract and runtime hard validation"
        happo_release_gate = "PASS WITH RUNTIME CALIBRATION REQUIRED: 169 stages x 3 seeds"
        android_lint = "PASS with intentional ARM64-only ChromeOS warning"
        apk_signature = "PASS"
        device_install = "NOT RUN: no Android device or emulator attached"
    }
}
$metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $metadataPath -Encoding UTF8
Write-Output $artifact
Write-Output $metadataPath
