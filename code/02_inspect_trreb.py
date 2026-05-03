import pdfplumber
from pathlib import Path

PDF_PATH = Path(__file__).parent.parent / "data" / "raw" / "trreb_pdfs" / "mw2206.pdf"

def main():
    print(f"Inspecting: {PDF_PATH.name}")
    print("=" * 70)

    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"Number of pages: {len(pdf.pages)}\n")

        # Print text from the first 2 pages only — that's where the summary lives
        for page_num, page in enumerate(pdf.pages[:4], start=1):
            print(f"\n--- PAGE {page_num} ---\n")
            text = page.extract_text()
            if text:
                # Only print first 2000 characters per page to keep output readable
                print(text[:2000])
                if len(text) > 2000:
                    print(f"\n[... {len(text) - 2000} more characters on this page ...]")
            print()

if __name__ == "__main__":
    main()