# i calculate mortgage debt service ratio (mdsr) for each city
# mdsr = monthly mortgage payment on median home / monthly household income
# this is the affordability metric that actually responds to interest rates
# (median multiple ignores rates, so we need both)

import pandas as pd
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/cities_with_mm.csv"   # already has price + income per city
rates_path = base / "data/clean/mortgage_rates.csv"
out_path = base / "data/clean/cities_with_mdsr.csv"

# country mapping for cities (so i can attach the right mortgage rate)
city_to_country = {
    "Toronto":   "Canada",
    "Vancouver": "Canada",
    "London":    "UK",
    "New York":  "USA",
}

# amortization period in months (canadian/uk are 25-year, us is 30-year typical)
amortization = {
    "Canada": 300,  # 25 years
    "UK":     300,  # 25 years
    "USA":    360,  # 30 years
}


def monthly_payment(price, annual_rate_pct, n_months):
    # standard amortizing-mortgage formula
    # if rate is zero, fall back to simple division to avoid div-by-zero
    if annual_rate_pct == 0:
        return price / n_months
    r = annual_rate_pct / 100 / 12
    return price * r * (1 + r) ** n_months / ((1 + r) ** n_months - 1)


# load the per-city dataset i already built
df = pd.read_csv(in_path)
rates = pd.read_csv(rates_path)

# attach country to each city row, then merge in the rate for that country/month
df["country"] = df["city"].map(city_to_country)
df = df.merge(rates, on=["country", "date"], how="left")

# calculate monthly payment and mdsr per row
df["n_months"] = df["country"].map(amortization)
df["monthly_payment"] = df.apply(
    lambda r: monthly_payment(r["price_local"], r["rate"], r["n_months"]),
    axis=1
)
df["mdsr"] = df["monthly_payment"] * 12 / df["income"]   # i annualize then divide by annual income

df = df.drop(columns=["n_months"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)

out_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out_path, index=False)
print(f"saved {len(df)} rows to {out_path}\n")

# annual summary
df["yr"] = df["date"].str[:4]
summary = (df.groupby(["city", "yr"])
             .agg(price=("price_local", "mean"),
                  rate=("rate", "mean"),
                  income=("income", "mean"),
                  mm=("median_multiple", "mean"),
                  mdsr=("mdsr", "mean"))
             .round(3))
print("annual mdsr by city:")
print(summary.to_string())

print("\npeak mdsr by city (i.e. worst affordability moment):")
for city in city_to_country:
    s = df[df["city"] == city]
    pk = s.loc[s["mdsr"].idxmax()]
    tr = s.loc[s["mdsr"].idxmin()]
    print(f"  {city:<10} peak {pk['mdsr']*100:>5.1f}% ({pk['date']}) | "
          f"trough {tr['mdsr']*100:>5.1f}% ({tr['date']})")