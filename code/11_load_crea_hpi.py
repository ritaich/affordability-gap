# pulls toronto and vancouver hpi from crea's monthly excel
# we keep just the composite benchmark (whole market, all home types)
# and slice to our project window: jan 2019 - dec 2024
import pandas as pd
from pathlib import Path
xlsx = Path(__file__).parent.parent / "data/raw/crea_hpi/Seasonally Adjusted (M).xlsx"
out_path = Path(__file__).parent.parent / "data/clean/crea_hpi_two_cities.csv"
# what we want from each sheet
cities = {
    "Toronto":   "GREATER_TORONTO",
    "Vancouver": "GREATER_VANCOUVER",
}
# project window
start = "2019-01-01"
end   = "2024-12-01"

frames = []
for city_name, sheet in cities.items():
    df = pd.read_excel(xlsx, sheet_name=sheet)
    # keep only what we need
    df = df[["Date", "Composite_HPI_SA", "Composite_Benchmark_SA"]].copy()
    # filter to project window
    df = df[(df["Date"] >= start) & (df["Date"] <= end)].copy()
    df["city"] = city_name
    df["date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m")
    df = df.rename(columns={
        "Composite_HPI_SA": "hpi_sa",
        "Composite_Benchmark_SA": "benchmark_sa_cad",
    })
    df = df[["city", "date", "hpi_sa", "benchmark_sa_cad"]]
    frames.append(df)
    print(f"{city_name}: {len(df)} months")

# stack vertically into long format
combined = pd.concat(frames, ignore_index=True)
combined = combined.sort_values(["city", "date"]).reset_index(drop=True)
out_path.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(out_path, index=False)
print(f"\nsaved to {out_path}")

# quick sanity check - show start, peak, end for each city
print("\nsanity check (peak benchmark and when):")
for city_name in cities:
    sub = combined[combined["city"] == city_name]
    peak_row = sub.loc[sub["benchmark_sa_cad"].idxmax()]
    print(f"  {city_name}:")
    print(f"    first month {sub.iloc[0]['date']}: ${sub.iloc[0]['benchmark_sa_cad']:>10,.0f}")
    print(f"    peak {peak_row['date']}:        ${peak_row['benchmark_sa_cad']:>10,.0f}")
    print(f"    last month {sub.iloc[-1]['date']}: ${sub.iloc[-1]['benchmark_sa_cad']:>10,.0f}")