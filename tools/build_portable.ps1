param(
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv-rl\Scripts\python.exe"
$Native = Join-Path $RepoRoot "build\rl-vcpkg\game\src\rl\$Configuration\mengde_rl.exe"
$Entry = Join-Path $RepoRoot "packaging\portable_entry.py"
$Payload = Join-Path $RepoRoot "rl\_play_gui_runtime.cpython-310.pyc"
$HappoModel = Join-Path $RepoRoot "rl\models\ppo_mappo_happo_comparison\happo.pt"
$CqlModel = Join-Path $RepoRoot "rl\models\offline_iql_cql_comparison\cql.pt"

foreach ($Required in @($Python, $Native, $Entry, $Payload, $HappoModel, $CqlModel)) {
    if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
        throw "Required portable-build input is missing: $Required"
    }
}

$PyInstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--onedir",
    "--windowed",
    "--name", "Ekgd",
    "--paths", $RepoRoot,
    "--distpath", (Join-Path $RepoRoot "release"),
    "--workpath", (Join-Path $RepoRoot "build\pyinstaller\work"),
    "--specpath", (Join-Path $RepoRoot "build\pyinstaller"),
    "--add-data", "$Payload;rl",
    "--add-data", "$(Join-Path $RepoRoot 'assets\lzc');assets\lzc",
    "--add-data", "$(Join-Path $RepoRoot 'rl\assets');rl\assets",
    "--add-data", "$HappoModel;rl\models\runtime",
    "--add-data", "$CqlModel;rl\models\runtime",
    "--add-data", "$(Join-Path $RepoRoot 'game\sce\dongzhou');game\sce\dongzhou",
    "--add-binary", "$Native;native",
    $Entry
)
& $Python -m PyInstaller @PyInstallerArgs
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

$DistDir = Join-Path $RepoRoot "release\Ekgd"
$Guide = @"
东周列国志 MOD 便携版（Windows 10/11 64 位）

1. 请先完整解压压缩包。
2. 双击 Ekgd.exe 启动。
3. 不要只把 Ekgd.exe 单独复制出来；_internal 文件夹必须与它放在一起。
4. 无需安装 Python、无需命令行。
5. 存档位置：%LOCALAPPDATA%\Ekgd\saves
6. 启动失败日志：%LOCALAPPDATA%\Ekgd\logs\startup-error.log
"@
[IO.File]::WriteAllText(
    (Join-Path $DistDir "README.txt"),
    $Guide,
    [Text.UTF8Encoding]::new($true)
)

$ZipPath = Join-Path $RepoRoot "release\Ekgd-portable-win64.zip"
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Compress-Archive -LiteralPath $DistDir -DestinationPath $ZipPath -CompressionLevel Optimal

Write-Host "Portable directory: $(Join-Path $DistDir 'Ekgd.exe')"
Write-Host "Portable archive: $ZipPath"