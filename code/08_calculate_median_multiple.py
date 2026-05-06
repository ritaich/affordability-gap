# i calculate median multiple for each city using:
#   - crea hpi composite benchmark for canadian cities
#   - uk land registry hpi for london
#   - statcan / ons median household income (annual, interpolated)
# median multiple is currency-independent (ratio), so i don't need fx here

import pandas as pd
from pathlib import Path

base = Path(__file__).parent.parent
canada_path = base / "data/clean/crea_hpi_two_cities.csv"
london_path = base / "data/clean/london_prices.csv"
out_path = base / "data/clean/cities_with_mm.csv"

# annual median household income, sources documented in methodology section 4
# all values in 2024 constant currency (CAD for canada, GBP for london)
incomes = {
    "Toronto": {
        2019: 93000,    # backward extrapolation from 2020
        2020: 95000,
        2021: 96700,
        2022: 93900,
        2023: 94600,
        2024: 94300,
    },
    "Vancouver": {
        2019: 92000,    # backward extrapolation
        2020: 92300,
        2021: 90100,
        2022: 87700,
        2023: 87500,
        2024: 89900,
    },

"New York": {
        2019: 72038,    # statcan-equivalent: us census saipe via fred
        2020: 73354,
        2021: 74230,
        2022: 79463,
        2023: 82052,
        2024: 85768,
    },

    "London": {
        2019: 47000,    # estimated from ONS regional series
        2020: 49500,
        2021: 50500,
        2022: 51000,
        2023: 51500,
        2024: 52000,
    },
}


def monthly_income_series(annual):
    # i anchor each year at june and linearly interpolate between
    # this matches what statcan / boc / ons all do
    anchors = pd.DataFrame({
        "date": [pd.Timestamp(year=y, month=6, day=1) for y in annual],
        "income": list(annual.values()),
    }).set_index("date")

    yr_min, yr_max = min(annual), max(annual)
    full_idx = pd.date_range(f"{yr_min}-01-01", f"{yr_max}-12-01", freq="MS")
    s = anchors.reindex(anchors.index.union(full_idx)).sort_index()
    s["income"] = s["income"].interpolate(method="time")
    s = s.reindex(full_idx)

    out = s.reset_index().rename(columns={"index": "date"})
    out["date"] = out["date"].dt.strftime("%Y-%m")
    return out


# load price data from both sources
canada = pd.read_csv(canada_path)
canada = canada.rename(columns={"benchmark_sa_cad": "price_local"})
canada["currency"] = "CAD"
canada = canada[["city", "date", "price_local", "currency", "hpi_sa"]]
canada = canada.rename(columns={"hpi_sa": "hpi"})

london = pd.read_csv(london_path)
london = london.rename(columns={"avg_price_gbp": "price_local"})
london["currency"] = "GBP"
london = london[["city", "date", "price_local", "currency", "hpi"]]
ny_path = base / "data/clean/newyork_prices.csv"
newyork = pd.read_csv(ny_path)
# already in the right format from 15_build_newyork.py

# stack all three cities
prices = pd.concat([canada, london, newyork], ignore_index=True)

# attach income and compute median multiple
all_rows = []
for city, annual_inc in incomes.items():
    inc = monthly_income_series(annual_inc)
    sub = prices[prices["city"] == city].copy()
    merged = sub.merge(inc, on="date", how="left")
    merged["median_multiple"] = merged["price_local"] / merged["income"]
    all_rows.append(merged)

combined = pd.concat(all_rows, ignore_index=True)
combined = combined.sort_values(["city", "date"]).reset_index(drop=True)

out_path.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(out_path, index=False)
print(f"saved {len(combined)} rows to {out_path}\n")

# annual summary so i can spot-check
combined["yr"] = combined["date"].str[:4]
summary = (combined.groupby(["city", "yr"])
           .agg(price=("price_local", "mean"),
                income=("income", "mean"),
                mm=("median_multiple", "mean"))
           .round(2))
print("annual median multiple by city (price in local currency):")
print(summary.to_string())
combined = combined.drop(columns=["yr"])

print("\npeak and trough by city:")
for city in incomes:
    s = combined[combined["city"] == city]
    pk = s.loc[s["median_multiple"].idxmax()]
    tr = s.loc[s["median_multiple"].idxmin()]
    print(f"  {city:<10} peak {pk['median_multiple']:>5.2f} ({pk['date']}) | "
          f"trough {tr['median_multiple']:>5.2f} ({tr['date']})")