# i build the master dataset that week 5 regression will use
# every city / month / variable in one tidy long-format csv
# inputs: cities_with_mdsr.csv (price, income, mm, mdsr, rate)
#         + unemployment csvs for each country
# output: master.csv with everything joined

import pandas as pd
from pathlib import Path

base = Path(__file__).parent.parent
in_path  = base / "data/clean/cities_with_mdsr.csv"
fred_dir = base / "data/raw/fred"
out_path = base / "data/clean/master.csv"

# country -> unemployment file mapping
unemp_files = {
    "Canada": "canada_unemployment.csv",
    "UK":     "uk_unemployment.csv",
    "USA":    "ny_unemployment.csv",  # i use ny state for new york
}


def load_unemployment(country, filename):
    # all fred files have format: observation_date, SERIES_CODE
    # i normalize to: country, date, unemployment
    df = pd.read_csv(fred_dir / filename)
    df.columns = ["date", "unemployment"]
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
    df["country"] = country
    return df[["country", "date", "unemployment"]]


# load main dataset (already has price, income, mortgage rate, mm, mdsr)
master = pd.read_csv(in_path)

# stack all three unemployment series into one frame
unemp_all = pd.concat([
    load_unemployment(country, fname)
    for country, fname in unemp_files.items()
], ignore_index=True)

# join unemployment in by country + date
master = master.merge(unemp_all, on=["country", "date"], how="left")

# drop the helper "yr" column if it sneaked in from earlier scripts
master = master.drop(columns=[c for c in ["yr"] if c in master.columns])

# put columns in a sensible order for regression work
ordered_cols = [
    "city", "country", "date",
    "price_local", "currency", "hpi",
    "income",
    "rate", "monthly_payment",
    "unemployment",
    "median_multiple", "mdsr",
]
master = master[[c for c in ordered_cols if c in master.columns]]
master = master.sort_values(["city", "date"]).reset_index(drop=True)

out_path.parent.mkdir(parents=True, exist_ok=True)
master.to_csv(out_path, index=False)
print(f"saved {len(master)} rows to {out_path}")
print(f"columns: {list(master.columns)}")
print()

# sanity check: any missing values?
missing = master.isna().sum()
print("missing values per column:")
print(missing[missing > 0] if missing.sum() > 0 else "  (none — clean dataset)")

# quick peek
print("\nfirst 3 rows for each city:")
for city in master["city"].unique():
    sub = master[master["city"] == city].head(3)
    print(f"\n--- {city} ---")
    print(sub.to_string(index=False))