# peek inside the crea hpi excel file to see all sheet names
# and a sample of what's in greater_vancouver
import pandas as pd
from pathlib import Path

xlsx = Path(__file__).parent.parent / "data/raw/crea_hpi/Seasonally Adjusted (M).xlsx"

# get all sheet names
xl = pd.ExcelFile(xlsx)
print(f"total sheets: {len(xl.sheet_names)}")
print()
print("all sheet names:")
for name in xl.sheet_names:
    print(f"  {name}")

# read greater_vancouver and look at it
print()
print("=" * 60)
print("greater_vancouver sample:")
print("=" * 60)
vc = pd.read_excel(xlsx, sheet_name="GREATER_VANCOUVER")
print(f"shape: {vc.shape}  (rows x columns)")
print(f"columns: {list(vc.columns)}")
print()
print("first 3 rows:")
print(vc.head(3).to_string())
print()
print("last 3 rows:")
print(vc.tail(3).to_string())