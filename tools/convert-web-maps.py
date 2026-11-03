from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "assets" / "lzc" / "map"
OUTPUT_ROOT = ROOT / "web-game" / "assets" / "maps"
MANIFEST_FILE = ROOT / "web-game" / "scenario" / "campaign.json"
MAX_DIMENSION = 3072
WEBP_QUALITY = 74


def convert(source: Path, output: Path) -> dict[str, object]:
    with Image.open(source) as image:
        image = image.convert("RGB")
        original_size = image.size
        if max(image.size) > MAX_DIMENSION:
            scale = MAX_DIMENSION / max(image.size)
            image = image.resize(
                (round(image.width * scale), round(image.height * scale)),
                Image.Resampling.LANCZOS,
            )
        image.save(output, "WEBP", quality=WEBP_QUALITY, method=6)
        return {
            "source": source.name,
            "output": output.name,
            "originalSize": list(original_size),
            "webSize": list(image.size),
            "sourceBytes": source.stat().st_size,
            "webBytes": output.stat().st_size,
        }


def main() -> None:
    campaign = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    names = sorted({stage["mapAsset"] for stage in campaign["stages"] if stage.get("mapAsset")})
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    records = []
    for index, name in enumerate(names, start=1):
        source = SOURCE_ROOT / name
        output = OUTPUT_ROOT / f"{Path(name).stem}.webp"
        records.append(convert(source, output))
        if index % 20 == 0 or index == len(names):
            print(f"converted {index}/{len(names)}")
    index = {
        "quality": WEBP_QUALITY,
        "maxDimension": MAX_DIMENSION,
        "sourceCount": len(records),
        "sourceBytes": sum(int(record["sourceBytes"]) for record in records),
        "webBytes": sum(int(record["webBytes"]) for record in records),
        "maps": records,
    }
    (OUTPUT_ROOT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in index.items() if key != "maps"}, indent=2))


if __name__ == "__main__":
    main()
