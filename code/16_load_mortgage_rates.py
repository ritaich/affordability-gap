# i pull mortgage rates for all three countries from official sources
# canada: statcan table 34100145 (5-year conventional)
# uk: bank of england series IUMBV34 (5-year fixed, 75% ltv)
# us: already have MORTGAGE30US in fred folder, just reformat
import pandas as pd
import requests
from pathlib import Path
from io import StringIO
base = Path(__file__).parent.parent
out_path = base / "data/clean/mortgage_rates.csv"

# == canada ==
# statcan table 34100145, vector v733833 = canada cmhc 5-year conventional mortgage rate
# i tried the api originally but had wrong vector id, switched to manual csv download
print("loading canada (manual download from statcan)...")
ca_path = base / "data/raw/statcan/34100145.csv"
ca_raw = pd.read_csv(ca_path)
# the file has many columns but i only need REF_DATE and VALUE
ca_df = ca_raw[["REF_DATE", "VALUE"]].copy()
ca_df.columns = ["date", "rate"]
ca_df["country"] = "Canada"
print(f"  ok, {len(ca_df)} rows (will filter to project window below)")

# == uk ==
# i tried scraping boe directly but they block bots, so i downloaded the csv manually
# the file has UK 2-year fixed mortgage rate (the dominant uk product)
# header is one giant string, dates are in "31 dec 24" format, listed newest first
print("loading uk (manual download from boe)...")
uk_path = base / "data/raw/boe/uk_5yr_mortgage.csv"
uk_df = pd.read_csv(uk_path)
# rename whatever the header is to clean names
uk_df.columns = ["date", "rate"]
# parse "31 Dec 24" → "2024-12"
uk_df["date"] = pd.to_datetime(uk_df["date"], format="%d %b %y").dt.strftime("%Y-%m")
uk_df["country"] = "UK"
print(f"  ok, {len(uk_df)} rows")

# == us ==
# i already have this from earlier
print("loading us (already in fred folder)...")
us_raw = pd.read_csv(base / "data/raw/fred/us_mortgage_30y.csv")
us_raw.columns = ["date", "rate"]
us_raw["date"] = pd.to_datetime(us_raw["date"])
# this is weekly, so i resample to monthly average
us_monthly = (us_raw.set_index("date")
              .resample("MS").mean()
              .reset_index())
us_monthly["date"] = us_monthly["date"].dt.strftime("%Y-%m")
us_monthly["country"] = "USA"
print(f"  ok, {len(us_monthly)} rows after resampling weekly to monthly")

# stack and trim to project window
all_rates = pd.concat([ca_df, uk_df, us_monthly], ignore_index=True)
all_rates = all_rates[(all_rates["date"] >= "2019-01") & (all_rates["date"] <= "2024-12")]
all_rates = all_rates.sort_values(["country", "date"]).reset_index(drop=True)

out_path.parent.mkdir(parents=True, exist_ok=True)
all_rates.to_csv(out_path, index=False)
print(f"\nsaved {len(all_rates)} rows to {out_path}")

# quick summary
print("\nrate range by country:")
for country in ["Canada", "UK", "USA"]:
    sub = all_rates[all_rates["country"] == country]
    print(f"  {country}: {sub['rate'].min():.2f}% to {sub['rate'].max():.2f}% "
          f"({len(sub)} months)")