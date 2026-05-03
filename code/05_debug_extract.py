"""Debug: see exactly which lines start with TREB-related labels."""
import pdfplumber
from pathlib import Path

PDF_PATH = Path(__file__).parent.parent / "data" / "raw" / "trreb_pdfs" / "mw1901.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    for page_idx in [2, 3, 1]:
        text = pdf.pages[page_idx].extract_text() or ""
        print(f"\n========== PAGE {page_idx + 1} ==========")
        for i, line in enumerate(text.split("\n")):
            stripped = line.strip()
            if "TREB" in stripped or "TRREB" in stripped:
                # Show the raw line AND its repr (to expose hidden characters)
                print(f"Line {i}: {stripped!r}")
                print(f"  starts with 'TREB Total': {stripped.startswith('TREB Total')}")
                print(f"  starts with 'TRREB Total': {stripped.startswith('TRREB Total')}")
                print(f"  starts with 'All TRREB Areas': {stripped.startswith('All TRREB Areas')}")