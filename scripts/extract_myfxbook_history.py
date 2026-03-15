#!/usr/bin/env python3
"""Extract Myfxbook Trading Activity -> History table to CSV/JSON.

Usage:
  python scripts/extract_myfxbook_history.py --url "https://www.myfxbook.com/members/ATCSoftware/hrc-algo/11801141"
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def normalize_cell(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def write_csv(rows: list[dict[str, str]], out_path: Path) -> None:
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def extract_table_rows(page: Any) -> list[dict[str, str]]:
    table = page.locator("table:has(th:has-text('Open Date'))").first
    if table.count() == 0:
        raise RuntimeError("Could not find the History table with 'Open Date' header.")

    headers = table.locator("thead th").all_inner_texts()
    headers = [normalize_cell(h) or f"col_{i + 1}" for i, h in enumerate(headers)]
    row_locs = table.locator("tbody tr")
    row_count = row_locs.count()
    rows: list[dict[str, str]] = []

    for i in range(row_count):
        row = row_locs.nth(i)
        cells = [normalize_cell(x) for x in row.locator("td").all_inner_texts()]
        if not any(cells):
            continue
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        elif len(cells) > len(headers):
            cells = cells[: len(headers)]
        rows.append(dict(zip(headers, cells)))

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Myfxbook history table to CSV/JSON.")
    parser.add_argument("--url", required=True, help="Full Myfxbook system URL.")
    parser.add_argument("--out-dir", default="output", help="Output directory (default: output).")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run headless (default is headed so you can complete login/captcha).",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=120,
        help="Max seconds to wait for History rows after clicking tab (default: 120).",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "myfxbook_history.csv"
    json_path = out_dir / "myfxbook_history.json"
    screenshot_path = out_dir / "myfxbook_history_debug.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(viewport={"width": 1600, "height": 1200})
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=90000)

        print("\nIf captcha/login appears, complete it in the browser window.")
        input("When you can see the full page, press Enter here to continue...")

        history_tab = page.locator("text=/^History\\s*\\(\\d+\\)$/i").first
        if history_tab.count() == 0:
            history_tab = page.locator("text=/History\\s*\\(/i").first
        history_tab.click(timeout=20000)

        try:
            page.locator("table:has(th:has-text('Open Date')) tbody tr").first.wait_for(
                timeout=args.wait_seconds * 1000
            )
            no_data = page.locator("text=No data to display")
            if no_data.count() > 0 and no_data.first.is_visible():
                raise RuntimeError("History tab loaded but shows 'No data to display'.")
        except PlaywrightTimeoutError as exc:
            page.screenshot(path=str(screenshot_path), full_page=True)
            raise RuntimeError(
                "Timed out waiting for rows in History table. "
                f"Saved debug screenshot: {screenshot_path}"
            ) from exc

        rows = extract_table_rows(page)
        if not rows:
            page.screenshot(path=str(screenshot_path), full_page=True)
            raise RuntimeError(
                "History table found but no rows extracted. "
                f"Saved debug screenshot: {screenshot_path}"
            )

        write_csv(rows, csv_path)
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"Extracted rows: {len(rows)}")
        print(f"CSV:  {csv_path.resolve()}")
        print(f"JSON: {json_path.resolve()}")

        context.close()
        browser.close()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        raise SystemExit(130)
    except Exception as err:
        print(f"\nERROR: {err}", file=sys.stderr)
        raise SystemExit(1)
