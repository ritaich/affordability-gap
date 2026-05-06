# load uk land registry hpi data for london
# this csv is one region (london) over the project window already
# i just pull out the columns we need and add to our cities dataset
import pandas as pd
from pathlib import Path
base = Path(__file__).parent.parent
in_path = base / "data/raw/uk_hpi/london.csv"
out_path = base / "data/clean/london_prices.csv"

df = pd.read_csv(in_path)
print(f"loaded {len(df)} rows")

# keep what i need, rename to match our other cities
keep = {
    "Period": "date",
    "Average price All property types": "avg_price_gbp",
    "House price index All property types": "hpi",
    "Sales volume All property types": "sales",
}
df = df[list(keep.keys())].rename(columns=keep)

# date is already YYYY-MM format thankfully
df["city"] = "London"

# put columns in a nice order
df = df[["city", "date", "avg_price_gbp", "hpi", "sales"]]
df = df.sort_values("date").reset_index(drop=True)

out_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out_path, index=False)
print(f"saved {len(df)} rows to {out_path}")

print(f"\nfirst 3 rows:")
print(df.head(3).to_string(index=False))
print(f"\nlast 3 rows:")
print(df.tail(3).to_string(index=False))

# quick sanity check
print(f"\nprice range:")
print(f"  min: £{df['avg_price_gbp'].min():>8,.0f} ({df.loc[df['avg_price_gbp'].idxmin(), 'date']})")
print(f"  max: £{df['avg_price_gbp'].max():>8,.0f} ({df.loc[df['avg_price_gbp'].idxmax(), 'date']})")