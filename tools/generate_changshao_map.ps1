param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Add-Type -AssemblyName System.Drawing

$sourceRoot = Join-Path $ProjectRoot "assets\lzc\map_sources\changshao"
$outputPath = Join-Path $ProjectRoot "assets\lzc\map\m025.png"
$width = 1520
$height = 1120
$tile = 80

$canvas = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic

function New-TextureBrush([string]$name) {
    $image = [System.Drawing.Image]::FromFile((Join-Path $sourceRoot $name))
    $brush = [System.Drawing.TextureBrush]::new($image, [System.Drawing.Drawing2D.WrapMode]::Tile)
    return @{ Image = $image; Brush = $brush }
}

function Fill-PathTexture([System.Drawing.Drawing2D.GraphicsPath]$path, [string]$name) {
    $texture = New-TextureBrush $name
    $graphics.FillPath($texture.Brush, $path)
    $texture.Brush.Dispose()
    $texture.Image.Dispose()
}

$base = New-TextureBrush "grass.png"
$graphics.FillRectangle($base.Brush, 0, 0, $width, $height)
$base.Brush.Dispose()
$base.Image.Dispose()

$plainPath = New-Object System.Drawing.Drawing2D.GraphicsPath
$plainPath.StartFigure()
$plainPath.AddBezier(80, 85, 330, 40, 1190, 55, 1450, 120)
$plainPath.AddBezier(1450, 120, 1500, 360, 1465, 800, 1400, 1015)
$plainPath.AddBezier(1400, 1015, 1100, 1085, 360, 1070, 95, 1005)
$plainPath.AddBezier(95, 1005, 35, 760, 45, 340, 80, 85)
$plainPath.CloseFigure()
Fill-PathTexture $plainPath "plain.png"
$plainPath.Dispose()

$road = New-Object System.Drawing.Drawing2D.GraphicsPath
$road.AddBezier(760, -80, 690, 250, 850, 440, 730, 680)
$road.AddBezier(730, 680, 650, 850, 790, 1010, 760, 1200)
$earthTexture = New-TextureBrush "earth.png"
$roadPen = [System.Drawing.Pen]::new($earthTexture.Brush, 235)
$roadPen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$roadPen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$graphics.DrawPath($roadPen, $road)
$roadPen.Dispose()
$earthTexture.Brush.Dispose()
$earthTexture.Image.Dispose()
$road.Dispose()

$leftRidge = New-Object System.Drawing.Drawing2D.GraphicsPath
$leftRidge.AddBezier(95, 300, 170, 245, 320, 265, 410, 340)
$leftRidge.AddBezier(410, 340, 465, 455, 395, 610, 300, 710)
$leftRidge.AddBezier(300, 710, 170, 730, 75, 635, 55, 500)
$leftRidge.AddBezier(55, 500, 45, 415, 55, 350, 95, 300)
$leftRidge.CloseFigure()
Fill-PathTexture $leftRidge "rock.png"
$ridgeOutline = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(105, 48, 65, 43), 22)
$graphics.DrawPath($ridgeOutline, $leftRidge)
$leftRidge.Dispose()

$rightRidge = New-Object System.Drawing.Drawing2D.GraphicsPath
$rightRidge.AddBezier(1120, 535, 1240, 470, 1420, 525, 1480, 640)
$rightRidge.AddBezier(1480, 640, 1500, 780, 1435, 905, 1320, 985)
$rightRidge.AddBezier(1320, 985, 1180, 970, 1075, 855, 1070, 720)
$rightRidge.AddBezier(1070, 720, 1060, 650, 1080, 580, 1120, 535)
$rightRidge.CloseFigure()
Fill-PathTexture $rightRidge "rock.png"
$graphics.DrawPath($ridgeOutline, $rightRidge)
$rightRidge.Dispose()
$ridgeOutline.Dispose()

$fieldOne = New-Object System.Drawing.Drawing2D.GraphicsPath
$fieldOne.AddEllipse(180, 760, 300, 205)
Fill-PathTexture $fieldOne "field.png"
$fieldOne.Dispose()

$fieldTwo = New-Object System.Drawing.Drawing2D.GraphicsPath
$fieldTwo.AddEllipse(1080, 120, 315, 190)
Fill-PathTexture $fieldTwo "field.png"
$fieldTwo.Dispose()

function Draw-Camp([int]$x, [int]$y, [bool]$flip) {
    $camp = New-Object System.Drawing.Bitmap (Join-Path $sourceRoot "camp.png")
    if ($flip) {
        $camp.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipNone)
    }
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $graphics.DrawImage($camp, $x * $tile, $y * $tile, $tile, $tile)
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $camp.Dispose()
}

Draw-Camp 9 1 $true
Draw-Camp 9 12 $false

$light = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
    [System.Drawing.Point]::new(0, 0),
    [System.Drawing.Point]::new($width, $height),
    [System.Drawing.Color]::FromArgb(24, 255, 232, 178),
    [System.Drawing.Color]::FromArgb(30, 34, 54, 39)
)
$graphics.FillRectangle($light, 0, 0, $width, $height)
$light.Dispose()

$graphics.Dispose()
$canvas.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$canvas.Dispose()
Write-Output $outputPath