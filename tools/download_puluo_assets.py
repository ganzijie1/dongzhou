"""List or download files from the public Puluo Baidu Pan share."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlencode

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


SHARE_URL = "https://pan.baidu.com/s/1aAVgn2xXw4dFYHoT6kOtdA?pwd=lcfg"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--download", help="Exact shared filename to download")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(EDGE),
            headless=True,
        )
        page = browser.new_page(accept_downloads=True)
        responses: list[dict] = []

        def capture(response) -> None:
            if not any(part in response.url for part in ("share/list", "sharedownload")):
                return
            try:
                payload = response.json()
                payload["_url"] = response.url
                responses.append(payload)
            except Exception:
                pass

        page.on("response", capture)
        page.goto(SHARE_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(8_000)
        if not responses or not responses[-1].get("list"):
            raise RuntimeError("Baidu Pan did not return a share listing")

        root = responses[-1]
        pending = [item["path"] for item in root["list"] if item.get("isdir") == "1"]
        all_items = list(root["list"])
        while pending:
            directory = pending.pop(0)
            params = urlencode(
                {
                    "shareid": root["share_id"],
                    "uk": root["uk"],
                    "web": 1,
                    "page": 1,
                    "num": 100,
                    "order": "name",
                    "desc": 0,
                    "showempty": 0,
                    "dir": directory,
                }
            )
            response = page.request.get(f"https://pan.baidu.com/share/list?{params}")
            listing = response.json()
            if listing.get("errno") != 0:
                raise RuntimeError(f"Failed to list {directory}: {listing}")
            items = listing.get("list", [])
            all_items.extend(items)
            pending.extend(item["path"] for item in items if item.get("isdir") == "1")
        if args.download:
            if not args.output:
                parser.error("--output is required with --download")
            page.get_by_text("普罗自研制作工具", exact=True).dblclick()
            page.wait_for_timeout(3_000)
            page.locator('[node-type="fydGNC"]:visible').last.click()
            page.get_by_text(args.download, exact=True).click()
            page.locator("a:visible").filter(has_text="下载").last.click()
            try:
                download = page.wait_for_event("download", timeout=30_000)
            except PlaywrightTimeoutError:
                if args.snapshot:
                    args.snapshot.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(args.snapshot), full_page=True)
                print(json.dumps(responses, ensure_ascii=False, indent=2))
                raise
            args.output.parent.mkdir(parents=True, exist_ok=True)
            download.save_as(args.output)
        if args.snapshot:
            args.snapshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(args.snapshot), full_page=True)
        print(json.dumps(all_items, ensure_ascii=False, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
