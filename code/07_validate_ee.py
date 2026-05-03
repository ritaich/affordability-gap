"""
07_validate_ee.py
Validates the automated TRREB extraction against the manually-typed EE data

Why this matters, because 24 months were typed by hand (because of my extened essay for my ib studies) from the same PDFs we now extract
automatically. If the numbers match, we trust the extractor for the other 48 months
"""

import pandas as pd
from pathlib import Path
ee_path = Path(__file__).parent.parent / "data" / "raw" / "ee_toronto_manual.csv"
extracted_path = Path(__file__).parent.parent / "data" / "clean" / "toronto_raw.csv"
# Mapping: EE column name → extracted column name
COLUMN_MAP = {
    "avg residental price $ (all types)": "avg_price",
    "total sales volume": "sales",
    "new listings": "new_listings",
}
# 0.0 = exact match required. Set higher (e.g., 1.0) if minor revisions are acceptable.
TOLERANCE = 0.0
def load_ee():
    """Load and clean the manually-typed EE Google Sheet export."""
    df = pd.read_csv(ee_path, thousands=",", skipinitialspace=True)
    # Strip whitespace from column names (the EE file has trailing spaces)
    df.columns = df.columns.str.strip()
    
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y").dt.strftime("%Y-%m")
    return df


def load_extracted():
    return pd.read_csv(extracted_path)


def main():
    ee = load_ee()
    extracted = load_extracted()

    print(f"EE sheet:        {len(ee)} months, columns: {list(ee.columns)}")
    print(f"Extracted CSV:   {len(extracted)} months")
    print()

    # Filter extracted data to only the months covered by the EE sheet
    overlap_months = set(ee["date"]) & set(extracted["date"])
    print(f"Overlapping months: {len(overlap_months)}")
    print()

    if not overlap_months:
        print("ERROR: No overlapping months. Check that EE dates parsed correctly.")
        print("EE dates:", ee["date"].head().tolist())
        return
    # Merge the two datasets on date so we can compare row-by-row
    merged = ee.merge(extracted, on="date", suffixes=("_ee", "_ext"))
    merged = merged.sort_values("date").reset_index(drop=True)
    total_comparisons = 0
    mismatches = []
    print(f"{'Month':<10} {'Field':<22} {'EE value':>15} {'Extracted':>15} {'Match':>8}")
    print("-" * 75)
    for _, row in merged.iterrows():
        for ee_col, ext_col in COLUMN_MAP.items():
            ee_val = row[ee_col]
            ext_val = row[ext_col]
            total_comparisons += 1
            if pd.isna(ee_val) or pd.isna(ext_val):
                status = "skip(NA)"
                match = None
            else:
                diff = abs(float(ee_val) - float(ext_val))
                match = diff <= TOLERANCE
                status = "✓" if match else f"✗ Δ={diff:,.0f}"
            print(f"{row['date']:<10} {ext_col:<22} {ee_val:>15,.0f} {ext_val:>15,.0f}  {status}")
            if match is False:
                mismatches.append({
                    "date": row["date"], "field": ext_col,
                    "ee": ee_val, "extracted": ext_val, "diff": diff,
                })

    print()
    print("=" * 75)
    print(f"Comparisons: {total_comparisons}")
    print(f"Mismatches:  {len(mismatches)}")
    print(f"Match rate:  {100 * (total_comparisons - len(mismatches)) / total_comparisons:.1f}%")
    if mismatches:
        print(f"\nMismatch details:")
        for m in mismatches:
            print(f"  {m['date']} {m['field']}: "
                  f"EE={m['ee']:,.0f}, Extracted={m['extracted']:,.0f}, Δ={m['diff']:,.0f}")


if __name__ == "__main__":
    main()