param(
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$web = Join-Path $root "web-game"
$outputDir = Join-Path $root "output"
$stamp = Get-Date -Format "yyyyMMdd"
if (-not $OutputPath) {
    $OutputPath = Join-Path $root "dongzhou-h5-release-final-$stamp.zip"
}
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$staging = Join-Path $outputDir ("h5-staging-" + [guid]::NewGuid().ToString("N"))

if (-not $staging.StartsWith($outputDir, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Staging path escaped output directory: $staging"
}

try {
    node (Join-Path $PSScriptRoot "verify-web-release.js")
    if ($LASTEXITCODE -ne 0) { throw "H5 release verification failed" }

    New-Item -ItemType Directory -Path $staging -Force | Out-Null
    foreach ($name in @("assets", "scenario", "vendor")) {
        Copy-Item -LiteralPath (Join-Path $web $name) -Destination (Join-Path $staging $name) -Recurse
    }
    foreach ($name in @("index.html", "styles.css", "game.js", "game-systems.js", "runtime.js", "pcgrl.js", "map-elites.js", "README.md")) {
        Copy-Item -LiteralPath (Join-Path $web $name) -Destination (Join-Path $staging $name)
    }

    $audioDir = Join-Path $staging "audio"
    New-Item -ItemType Directory -Path $audioDir -Force | Out-Null
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

    if (Test-Path -LiteralPath $OutputPath) { Remove-Item -LiteralPath $OutputPath -Force }
    & tar.exe -a -cf $OutputPath -C $staging .
    if ($LASTEXITCODE -ne 0) { throw "System ZIP creation failed" }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($OutputPath)
    try {
        $names = @($archive.Entries | ForEach-Object { $_.FullName.Replace("\", "/").TrimStart(".", "/") })
        foreach ($required in @("index.html", "game.js", "game-systems.js", "scenario/difficulty-profiles.json", "audio/dialogue-manifest.json")) {
            if ($names -notcontains $required) { throw "Release archive missing: $required" }
        }
    } finally {
        $archive.Dispose()
    }

    $file = Get-Item -LiteralPath $OutputPath
    $hash = Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256
    [ordered]@{
        result = "PASS"
        path = $file.FullName
        bytes = $file.Length
        mib = [math]::Round($file.Length / 1MB, 2)
        files = (Get-ChildItem -LiteralPath $staging -Recurse -File).Count
        sha256 = $hash.Hash.ToLowerInvariant()
    } | ConvertTo-Json
} finally {
    if (Test-Path -LiteralPath $staging) {
        $resolved = (Resolve-Path -LiteralPath $staging).Path
        if ($resolved.StartsWith($outputDir, [System.StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $resolved -Recurse -Force
        }
    }
}
