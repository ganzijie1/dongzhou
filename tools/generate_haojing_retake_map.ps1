param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Add-Type -AssemblyName System.Drawing

$sourceRoot = Join-Path $ProjectRoot "assets\lzc\map_sources\haojing"
$outputPath = Join-Path $ProjectRoot "assets\lzc\map\m024.png"
$tile = 80
$width = 19 * $tile
$height = 14 * $tile

$canvas = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
$graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half

function Fill-Texture {
    param(
        [System.Drawing.Graphics]$Target,
        [string]$Path,
        [System.Drawing.Rectangle]$Area
    )
    $image = [System.Drawing.Image]::FromFile($Path)
    $brush = [System.Drawing.TextureBrush]::new($image, [System.Drawing.Drawing2D.WrapMode]::Tile)
    $Target.FillRectangle($brush, $Area)
    $brush.Dispose()
    $image.Dispose()
}

Fill-Texture $graphics (Join-Path $sourceRoot "grass.png") ([System.Drawing.Rectangle]::new(0, 0, $width, $height))
Fill-Texture $graphics (Join-Path $sourceRoot "earth.png") ([System.Drawing.Rectangle]::new(8 * $tile, 0, 3 * $tile, $height))
Fill-Texture $graphics (Join-Path $sourceRoot "earth.png") ([System.Drawing.Rectangle]::new(0, 5 * $tile, $width, 3 * $tile))
Fill-Texture $graphics (Join-Path $sourceRoot "stone.png") ([System.Drawing.Rectangle]::new(5 * $tile, 3 * $tile, 9 * $tile, 7 * $tile))

$shade = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(26, 38, 26, 20))
$graphics.FillRectangle($shade, 0, 0, $width, $height)
$shade.Dispose()

$wall = New-Object System.Drawing.Bitmap (Join-Path $sourceRoot "wall-strip.png")

function Draw-WallTile {
    param([int]$Index, [int]$X, [int]$Y, [int]$Rotation = 0)
    $piece = New-Object System.Drawing.Bitmap 48, 48
    $pieceGraphics = [System.Drawing.Graphics]::FromImage($piece)
    $pieceGraphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $pieceGraphics.DrawImage(
        $wall,
        [System.Drawing.Rectangle]::new(0, 0, 48, 48),
        $Index * 48, 0, 48, 48,
        [System.Drawing.GraphicsUnit]::Pixel
    )
    $pieceGraphics.Dispose()
    if ($Rotation -eq 90) {
        $piece.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipNone)
    } elseif ($Rotation -eq 180) {
        $piece.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipNone)
    } elseif ($Rotation -eq 270) {
        $piece.RotateFlip([System.Drawing.RotateFlipType]::Rotate270FlipNone)
    }
    $graphics.DrawImage($piece, $X * $tile, $Y * $tile, $tile, $tile)
    $piece.Dispose()
}

for ($x = 5; $x -le 13; $x++) {
    if ($x -ne 9) {
        Draw-WallTile 0 $x 2
        Draw-WallTile 9 $x 10
    }
}
for ($y = 3; $y -le 9; $y++) {
    if ($y -ne 6) {
        Draw-WallTile 1 4 $y
        Draw-WallTile 12 14 $y
    }
}
Draw-WallTile 4 4 2
Draw-WallTile 5 14 2
Draw-WallTile 6 4 10
Draw-WallTile 8 14 10
Draw-WallTile 2 9 2
Draw-WallTile 10 9 10
Draw-WallTile 2 4 6 270
Draw-WallTile 2 14 6 90

function Draw-Building {
    param([int]$Id, [int]$X, [int]$Y, [int]$SpanX = 1, [int]$SpanY = 1)
    $image = [System.Drawing.Image]::FromFile((Join-Path $sourceRoot ("building-{0}.png" -f $Id)))
    $graphics.DrawImage($image, $X * $tile, $Y * $tile, $SpanX * $tile, $SpanY * $tile)
    $image.Dispose()
}

Draw-Building 48 9 4
Draw-Building 43 6 5
Draw-Building 44 12 5
Draw-Building 25 12 4
Draw-Building 37 7 8
Draw-Building 42 2 11

$wall.Dispose()

$edgeShade = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    [System.Drawing.Point]::new(0, 0),
    [System.Drawing.Point]::new(0, $height),
    [System.Drawing.Color]::FromArgb(12, 255, 232, 184),
    [System.Drawing.Color]::FromArgb(38, 21, 28, 23)
)
$graphics.FillRectangle($edgeShade, 0, 0, $width, $height)
$edgeShade.Dispose()

$graphics.Dispose()
$canvas.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$canvas.Dispose()

Write-Output $outputPath