param(
    [string]$OutputPath = "",
    [switch]$Compact,
    [double]$MusicBudgetMiB = 24,
    [int]$BaseMusicStages = 8,
    [double]$MusicPackTargetMiB = 16,
    [string]$PacksOutputPath = ""
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$web = Join-Path $root "web-game"
$outputDir = Join-Path $root "output"
$stamp = Get-Date -Format "yyyyMMdd"
if (-not $OutputPath) {
    $variant = if ($Compact) { "compact" } else { "final" }
    $OutputPath = Join-Path $root "dongzhou-h5-release-$variant-$stamp.zip"
}
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$compactAudioResult = $null
if ($Compact) {
    if (-not $PacksOutputPath) {
        $PacksOutputPath = Join-Path $outputDir ("music-packs-" + $stamp + "-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
    }
    $PacksOutputPath = [System.IO.Path]::GetFullPath($PacksOutputPath)
    if (Test-Path -LiteralPath $PacksOutputPath) {
        throw "Compact music-pack output already exists: $PacksOutputPath"
    }
}
$staging = Join-Path $outputDir ("h5-staging-" + [guid]::NewGuid().ToString("N"))

if (-not $staging.StartsWith($outputDir, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Staging path escaped output directory: $staging"
}

try {
    node (Join-Path $PSScriptRoot "verify-web-release.js")
    if ($LASTEXITCODE -ne 0) { throw "H5 release verification failed" }
    python (Join-Path $PSScriptRoot "verify-dialogue-voice-plan.py")
    if ($LASTEXITCODE -ne 0) { throw "Dialogue production-plan verification failed" }
    python (Join-Path $PSScriptRoot "verify-dialogue-audio.py") --require-stages all
    if ($LASTEXITCODE -ne 0) { throw "Dialogue audio verification failed" }
    node (Join-Path $PSScriptRoot "audit-runtime-voice-coverage.js")
    if ($LASTEXITCODE -ne 0) { throw "Lua runtime dialogue coverage failed" }
    python (Join-Path $PSScriptRoot "verify-contextual-music.py")
    if ($LASTEXITCODE -ne 0) { throw "Contextual music verification failed" }

    New-Item -ItemType Directory -Path $staging -Force | Out-Null
    foreach ($name in @("assets", "scenario", "vendor")) {
        Copy-Item -LiteralPath (Join-Path $web $name) -Destination (Join-Path $staging $name) -Recurse
    }
    foreach ($name in @("index.html", "styles.css", "game.js", "game-systems.js", "organization-play.js", "integration-client.js", "runtime.js", "pcgrl.js", "map-elites.js", "README.md")) {
        Copy-Item -LiteralPath (Join-Path $web $name) -Destination (Join-Path $staging $name)
    }

    $audioDir = Join-Path $staging "audio"
    New-Item -ItemType Directory -Path $audioDir -Force | Out-Null
    if ($Compact) {
        $compactOutput = & python (Join-Path $PSScriptRoot "build-compact-audio.py") `
            --staging $staging `
            --packs-output $PacksOutputPath `
            --music-budget-mib $MusicBudgetMiB `
            --base-stages $BaseMusicStages `
            --pack-target-mib $MusicPackTargetMiB
        if ($LASTEXITCODE -ne 0) { throw "Compact audio build failed" }
        $compactAudioResult = ($compactOutput -join "`n") | ConvertFrom-Json
    } else {
        $manifestPath = Join-Path $web "audio\dialogue-manifest.json"
        Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $audioDir "dialogue-manifest.json")
        $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($entry in $manifest.entries) {
            $relative = [string]$entry.file
            if (-not $relative.StartsWith("audio/dialogue/", [System.StringComparison]::Ordinal)) {
                throw "Unsafe dialogue path in manifest: $relative"
            }
            $source = Join-Path $web ($relative.Replace("/", "\"))
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing dialogue file: $relative" }
            $target = Join-Path $staging ($relative.Replace("/", "\"))
            New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $target
        }

        $musicManifestPath = Join-Path $web "audio\context-music-manifest.json"
        Copy-Item -LiteralPath $musicManifestPath -Destination (Join-Path $audioDir "context-music-manifest.json")
        $musicManifest = Get-Content -LiteralPath $musicManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($cue in $musicManifest.cues) {
            $relative = [string]$cue.file
            if (-not $relative.StartsWith("audio/context-music/", [System.StringComparison]::Ordinal)) {
                throw "Unsafe contextual music path in manifest: $relative"
            }
            $source = Join-Path $web ($relative.Replace("/", "\"))
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing contextual music file: $relative" }
            $target = Join-Path $staging ($relative.Replace("/", "\"))
            New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $target
        }
    }

    if (Test-Path -LiteralPath $OutputPath) { Remove-Item -LiteralPath $OutputPath -Force }
    $rootEntries = @(Get-ChildItem -LiteralPath $staging | ForEach-Object { $_.Name })
    & tar.exe -a -cf $OutputPath -C $staging @rootEntries
    if ($LASTEXITCODE -ne 0) { throw "System ZIP creation failed" }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($OutputPath)
    try {
        $names = @($archive.Entries | ForEach-Object { $_.FullName.Replace("\", "/") })
        foreach ($required in @("index.html", "game.js", "game-systems.js", "organization-play.js", "integration-client.js", "scenario/difficulty-profiles.json", "scenario/dongzhou-knowledge.json", "audio/dialogue-manifest.json", "audio/context-music-manifest.json")) {
            if ($names -notcontains $required) { throw "Release archive missing: $required" }
        }
    } finally {
        $archive.Dispose()
    }

    $file = Get-Item -LiteralPath $OutputPath
    if ($Compact -and $file.Length -gt 200000000) {
        throw "Compact H5 archive exceeds the 200 MB upload limit: $([math]::Round($file.Length / 1000000, 2)) MB"
    }
    $hash = Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256
    [ordered]@{
        result = "PASS"
        compact = [bool]$Compact
        path = $file.FullName
        bytes = $file.Length
        mib = [math]::Round($file.Length / 1MB, 2)
        files = (Get-ChildItem -LiteralPath $staging -Recurse -File).Count
        sha256 = $hash.Hash.ToLowerInvariant()
        musicPacksPath = if ($Compact) { $PacksOutputPath } else { "" }
        compactAudio = $compactAudioResult
    } | ConvertTo-Json
} finally {
    if (Test-Path -LiteralPath $staging) {
        $resolved = (Resolve-Path -LiteralPath $staging).Path
        if ($resolved.StartsWith($outputDir, [System.StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolved -Recurse -Force
        }
    }
}
