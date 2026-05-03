"""
01_download_trreb.py
Downloads all TRREB Market Watch PDFs from January 2019 to December 2024.
Saves them to /data/raw/trreb_pdfs/


"""

import os
import requests
from pathlib import Path
from time import sleep

# ============ CONFIG ============
START_YEAR = 2019
END_YEAR = 2024
URL_PATTERN = "https://trreb.ca/wp-content/files/market-stats/market-watch/mw{yy}{mm}.pdf"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "trreb_pdfs"
SLEEP_BETWEEN_REQUESTS = 1.0  # be polite — 1 second between downloads


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Saving PDFs to: {OUTPUT_DIR}")
    print()

    successful = 0
    failed = []
    skipped = 0

    for year in range(START_YEAR, END_YEAR + 1):
        yy = str(year)[-2:]  # last 2 digits, e.g. 2019 → "19"
        for month in range(1, 13):
            mm = f"{month:02d}"  # zero-padded, e.g. 1 → "01"
            filename = f"mw{yy}{mm}.pdf"
            filepath = OUTPUT_DIR / filename

            if filepath.exists():
                print(f"  ✓ {filename} already exists, skipping")
                skipped += 1
                continue

            url = URL_PATTERN.format(yy=yy, mm=mm)
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200 and response.content[:4] == b"%PDF":
                    filepath.write_bytes(response.content)
                    size_kb = len(response.content) / 1024
                    print(f"  ↓ {filename}  ({size_kb:.0f} KB)")
                    successful += 1
                else:
                    print(f"  ✗ {filename}  (HTTP {response.status_code})")
                    failed.append(filename)
            except Exception as e:
                print(f"  ✗ {filename}  (error: {e})")
                failed.append(filename)

            sleep(SLEEP_BETWEEN_REQUESTS)

    print()
    print(f"Done. Downloaded: {successful}, Skipped: {skipped}, Failed: {len(failed)}")
    if failed:
        print(f"Failed files: {failed}")


if __name__ == "__main__":
    main()