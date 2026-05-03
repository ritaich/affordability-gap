"""Diagnostic: check the layout of multiple failing pdfs"""
import pdfplumber
from pathlib import Path
PDFS_TO_CHECK = ["mw1901.pdf", "mw2001.pdf", "mw2205.pdf"]
PDF_DIR = Path(__file__).parent.parent / "data" / "raw" / "trreb_pdfs"
for pdf_name in PDFS_TO_CHECK:
    path = PDF_DIR / pdf_name
    print(f"\n{'#' * 70}")
    print(f"# FILE: {pdf_name}")
    print(f"{'#' * 70}")
    with pdfplumber.open(path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages[:5], start=1):
            text = page.extract_text() or "(no text)"
            print(f"\n----- Page {i} (first 1200 chars) -----")
            print(text[:1200])