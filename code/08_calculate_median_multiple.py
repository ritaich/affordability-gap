"""
08_calculate_median_multiple.py

Adds median household income to the Toronto dataset (linearly interpolated from
annual Statistics Canada figures to monthly), then calculates the Median Multiple:
  MM = Median house price / Median annual household income

Income source: Statistics Canada Table 11-10-0190-01 (median total household
income, Toronto CMA). 2024 is an estimate based on the recent 3.6% YoY trend.

Output: data/clean/toronto_with_mm.csv
"""

import pandas as pd
from pathlib import Path
input_path = Path(__file__).parent.parent / "data" / "clean" / "toronto_raw.csv"
output_path = Path(__file__).parent.parent / "data" / "clean" / "toronto_with_mm.csv"

# Annual median household income for Toronto CMA, in CAD
# Source: Statistics Canada Table 11-10-0190-01
# 2024 is estimated from recent CIS trend pending official release
# Toronto CMA median total household income (Economic families and persons not
# in an economic family). Source: Statistics Canada Table 11-10-0190-01,
# expressed in 2024 constant CAD dollars (i.e., already inflation-adjusted)
# Income concept = "Median total income" (gross / pre-tax), which matches the
# Demographia Median Multiple methodology
#
# 2019 is estimated as $93,000 (extrapolated backward from 2020). All other
# years are official Statistics Canada figures with data quality "A" or "B"
toronto_income_annual = {
    2019: 93_000,   # estimate (pre-2020 backward extrapolation)
    2020: 95_000,   # Stat Can, quality A
    2021: 96_700,   # Stat Can, quality B
    2022: 93_900,   # Stat Can, quality A
    2023: 94_600,   # Stat Can, quality A
    2024: 94_300,   # Stat Can, quality A
}


def build_monthly_income(years_dict):
    """
    Build a monthly time series of income by linearly interpolating between
    annual values.

    We anchor each year's value at mid-year (June) — this is the standard
    interpolation approach used by Stats Can and the Bank of Canada when
    moving annual to monthly data. So 2019's $89,700 is anchored at June 2019,
    2020's $93,000 is anchored at June 2020, and we linearly interpolate
    between consecutive June values.
    """
    # Build anchor points: one row per year at June 1
    anchors = pd.DataFrame({
        "date": [pd.Timestamp(year=y, month=6, day=1) for y in years_dict.keys()],
        "income": list(years_dict.values()),
    }).set_index("date")

    # Build a full monthly index covering Jan of first year to Dec of last year
    first_year = min(years_dict.keys())
    last_year = max(years_dict.keys())
    full_index = pd.date_range(
        start=f"{first_year}-01-01",
        end=f"{last_year}-12-01",
        freq="MS",  # Month Start
    )

    # Reindex to monthly and interpolate
    monthly = anchors.reindex(anchors.index.union(full_index)).sort_index()
    monthly["income"] = monthly["income"].interpolate(method="time")
    monthly = monthly.reindex(full_index)  # keep only the monthly slots

    # Format the date column as YYYY-MM strings to match toronto_raw.csv
    out = monthly.reset_index().rename(columns={"index": "date"})
    out["date"] = out["date"].dt.strftime("%Y-%m")
    return out


def main():
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows from toronto_raw.csv")

    income_monthly = build_monthly_income(toronto_income_annual)
    print(f"Built {len(income_monthly)} months of interpolated income")

    df = df.merge(income_monthly, on="date", how="left")

    # Calculate Median Multiple = Median Price / Annual Median Household Income
    df["median_multiple"] = df["median_price"] / df["income"]

    # Also calculate Price-to-Income ratio using AVERAGE price (some sources do this)
    df["price_income_ratio_avg"] = df["avg_price"] / df["income"]

    df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}\n")

    # Quick summary statistics by year
    print("Annual summary — Toronto Median Multiple:")
    summary = (df.groupby("year")
                 .agg(median_price=("median_price", "mean"),
                      income=("income", "mean"),
                      median_multiple=("median_multiple", "mean"))
                 .round(2))
    print(summary.to_string())

    print(f"\nPeak Median Multiple: {df['median_multiple'].max():.2f} "
          f"in {df.loc[df['median_multiple'].idxmax(), 'date']}")
    print(f"Trough Median Multiple: {df['median_multiple'].min():.2f} "
          f"in {df.loc[df['median_multiple'].idxmin(), 'date']}")


if __name__ == "__main__":
    main()