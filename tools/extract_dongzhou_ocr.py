from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BODY_RE = re.compile(r'\n  "text": "(.*)",\r?\n  "page": \d+,', re.DOTALL)
HEADING_RE = re.compile(r"第[一二三四五六七八九十百零]+回[^\n]+")


def page_body(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    match = BODY_RE.search(raw)
    if not match:
        raise ValueError(f"page body not found: {path}")
    return json.loads(f'"{match.group(1)}"')


def extract_chapters(ocr_dir: Path) -> list[dict[str, object]]:
    pages = []
    for path in sorted(ocr_dir.glob("page-*.json")):
        try:
            pages.append((path, page_body(path)))
        except (OSError, ValueError, json.JSONDecodeError):
            continue

    corpus = "\n".join(body for _, body in pages)
    headings = list(HEADING_RE.finditer(corpus))
    chapters = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(corpus)
        title = heading.group(0).strip()
        chapters.append({
            "ordinal": index + 1,
            "title": title,
            "text": corpus[heading.start():end].strip(),
        })
    return chapters


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract complete Dongzhou chapters from tolerant OCR page bodies.")
    parser.add_argument("--ocr-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=108)
    parser.add_argument("--print-chapter", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--length", type=int)
    args = parser.parse_args()

    chapters = [
        chapter for chapter in extract_chapters(args.ocr_dir)
        if args.start <= int(chapter["ordinal"]) <= args.end
    ]
    if args.print_chapter is not None:
        chapter = next((item for item in chapters if item["ordinal"] == args.print_chapter), None)
        if chapter is None:
            raise SystemExit(f"chapter not found: {args.print_chapter}")
        text = str(chapter["text"])[args.offset:]
        if args.length is not None:
            text = text[:args.length]
        print(text)
        return

    if args.output is None:
        parser.error("--output is required unless --print-chapter is used")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(chapters, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"extracted {len(chapters)} chapters: {args.start}-{args.end} -> {args.output}")


if __name__ == "__main__":
    main()
