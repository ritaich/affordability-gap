"""
03_extract_trreb.py
here code extracts monthly Toronto housing market data from all 72 TRREB Market Watch PDFs so again i may not do it manually 
Saves a clean CSV to data/clean/toronto_raw.csv

parse Page 3 of each PDF, find the "All TRREB Areas" row, extract
the 6 numeric fields we care about: Sales, AvgPrice, MedianPrice, NewListings,
ActiveListings, AvgDaysOnMarket

Why Page 3, because it has the cleanest summary table for the entire GTA in one row
"""

import re
import pdfplumber
import pandas as pd
from pathlib import Path

PDF_DIR = Path(__file__).parent.parent / "data" / "raw" / "trreb_pdfs"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "clean" / "toronto_raw.csv"

def parse_filename_to_date(filename):
    """Convert 'mw1901.pdf' into ('2019-01', 2019, 1)."""
    match = re.match(r"mw(\d{2})(\d{2})\.pdf", filename)
    if not match:
        return None
    yy, mm = match.groups()
    year = 2000 + int(yy)
    month = int(mm)
    return f"{year}-{month:02d}", year, month


def clean_number(text):
    """
    Strip $, commas, %, and whitespace, then convert to float
    Returns None if conversion fails
    """
    if text is None:
        return None
    cleaned = re.sub(r"[\$,%\s]", "", text)
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def extract_all_trreb_row(pdf_path):
    """
    Opens a TRREB PDF, find the page with the GTA-wide summary table,
    and pull out the 11 numeric fields i need
    Handles two label formats:
      - 'All TRREB Areas' (used in 2019-early 2020 and mid-2022 onwards)
      - 'TRREB Total'     (used during COVID-era reports, mid-2020 to mid-2022)
    Returns a dict, or None if extraction fails
    """
    with pdfplumber.open(pdf_path) as pdf:
        # Try pages 3, 4, 2 in order — TRREB sometimes shifts the table by one page.
        for page_idx in [2, 3, 1]:
            if page_idx >= len(pdf.pages):
                continue
            text = pdf.pages[page_idx].extract_text() or ""
            if any(label in text for label in ("All TRREB Areas", "TRREB Total", "TREB Total")):
                return parse_summary_row(text)
        return None

def parse_summary_row(page_text):
    """
    From a page of text containing the summary table, find the GTA-wide
    summary line and extract numeric fields

    Handles three label formats:
       'All TRREB Areas' (current style, mid-2022 onwards)
       'TRREB Total'     (mid-2020 to early 2022 style)
       'TREB Total'      (2019-early 2020 style, single R in TREB)

    Also it handles the May 2022 PDF which has every value duplicated due to
    overlapping text — we deduplicate adjacent identical tokens
    """
    LABELS = ("All TRREB Areas", "TRREB Total", "TREB Total")
    lines = page_text.split("\n")

    for line in lines:
        stripped = line.strip()
        matched_label = None
        for label in LABELS:
            if stripped.startswith(label):
                matched_label = label
                break
        if matched_label is None:
            continue

        data_part = stripped[len(matched_label):].strip()

        # Strips TRREB's Ab/c markers around active-listings 
        data_part = re.sub(r"A([\d,\.]+)b", r"\1", data_part)
        data_part = data_part.replace("c", "")

        tokens = data_part.split()
        # Handles the May 2022 doubled-token glitch...
        tokens = _deduplicate_doubled_tokens(tokens)
        if len(tokens) < 10:
            return None

        # Map tokens to fields. The first 10 columns are always the same
        result = {
            "sales": clean_number(tokens[0]),
            "dollar_volume": clean_number(tokens[1]),
            "avg_price": clean_number(tokens[2]),
            "median_price": clean_number(tokens[3]),
            "new_listings": clean_number(tokens[4]),
            "snlr_trend_pct": clean_number(tokens[5]),
            "active_listings": clean_number(tokens[6]),
            "months_inventory": clean_number(tokens[7]),
            "avg_sp_lp_pct": clean_number(tokens[8]),
            "avg_ldom": clean_number(tokens[9]),
            "avg_pdom": clean_number(tokens[10]) if len(tokens) >= 11 else None,
        }
        return result
    return None


def _deduplicate_doubled_tokens(tokens):
    """
    Some PDFs (espesially mw2205) have overlapping text that causes every value
    to appear twice in sequence. If the first half of the list is identical
    to the second half, return just the first half
    """
    n = len(tokens)
    if n < 4 or n % 2 != 0:
        return tokens
    half = n // 2
    if tokens[:half] == tokens[half:]:
        return tokens[:half]
    return tokens

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(PDF_DIR.glob("mw*.pdf"))
    print(f"Found {len(pdf_files)} PDF files. Extracting...\n")

    rows = []
    failed = []

    for pdf_path in pdf_files:
        date_info = parse_filename_to_date(pdf_path.name)
        if date_info is None:
            print(f"  ✗ {pdf_path.name} — couldn't parse date")
            failed.append(pdf_path.name)
            continue

        date_str, year, month = date_info
        try:
            data = extract_all_trreb_row(pdf_path)
        except Exception as e:
            print(f"  ✗ {pdf_path.name} — error: {e}")
            failed.append(pdf_path.name)
            continue

        if data is None:
            print(f"  ✗ {pdf_path.name} — couldn't find summary row")
            failed.append(pdf_path.name)
            continue

        row = {"date": date_str, "year": year, "month": month, **data}
        rows.append(row)
        print(f"  ✓ {pdf_path.name}  →  AvgPrice ${data['avg_price']:>12,.0f} "
              f"| Sales {data['sales']:>6.0f}")

    print(f"\nExtracted: {len(rows)}  |  Failed: {len(failed)}")
    if failed:
        print(f"Failed files: {failed}")

    df = pd.DataFrame(rows)
    df = df.sort_values("date").reset_index(drop=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))
    print(f"\nLast 3 rows:")
    print(df.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()