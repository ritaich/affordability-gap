# per-city correlation matrix between predictors and outcomes
# this is exploratory only - it tells me what relationships to expect
# before running formal regressions in week 5

import pandas as pd
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/master.csv"

df = pd.read_csv(in_path)

# the columns i care about for correlation
cols = ["price_local", "hpi", "rate", "unemployment", "median_multiple", "mdsr"]

print("per-city pearson correlations:\n")
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city][cols]
    corr = sub.corr().round(2)
    print(f"--- {city} ---")
    print(corr.to_string())
    print()

# also: what's the relationship between mortgage rate and mdsr across all cities?
# this is the most important regression hypothesis: rate -> mdsr
print("=" * 50)
print("rate vs mdsr correlation by city:")
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city]
    r = sub["rate"].corr(sub["mdsr"])
    print(f"  {city:<10} {r:>+.3f}")