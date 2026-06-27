# regression for the long-run affordability index (median multiple)
# same predictors as the mdsr regression but expected to show different rankings
# rates should matter less, prices and incomes should matter mechanically
# this contrast is what makes both indices worth reporting

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/master.csv"

df = pd.read_csv(in_path)
df["log_price"] = np.log(df["price_local"])
df["log_income"] = np.log(df["income"])

print("=" * 70)
print("regression: median multiple ~ rate + unemployment + log_price + log_income")
print("with newey-west hac standard errors")
print("=" * 70)
print()

results = {}
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    model = smf.ols(
        "median_multiple ~ rate + unemployment + log_price + log_income",
        data=sub
    ).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    results[city] = model

    print(f"--- {city} ---")
    print(f"r² = {model.rsquared:.4f}   n = {int(model.nobs)}")
    print(f"{'variable':<15} {'coef':>10} {'hac se':>9} {'p':>9}  {'sig':>3}")
    print("-" * 55)
    for var in ["Intercept", "rate", "unemployment", "log_price", "log_income"]:
        coef = model.params[var]
        se = model.bse[var]
        p = model.pvalues[var]
        sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
        print(f"  {var:<13} {coef:>+10.4f} {se:>9.4f} {p:>9.4f}  {sig:>3}")
    print()

# direct comparison: rate coefficient on mdsr vs on median multiple
# (i re-fit mdsr to get matched numbers)
print("=" * 70)
print("comparison: rate effect on mdsr vs on median multiple")
print("=" * 70)
print(f"{'city':<12} {'mdsr coef':>12} {'mm coef':>12} {'ratio mdsr/mm':>16}")
print("-" * 55)

for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    sub["mdsr_pct"] = sub["mdsr"] * 100

    mdsr_model = smf.ols(
        "mdsr_pct ~ rate + unemployment + log_price + log_income",
        data=sub
    ).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    mm_model = results[city]

    mdsr_coef = mdsr_model.params["rate"]
    mm_coef = mm_model.params["rate"]
    ratio = mdsr_coef / mm_coef if abs(mm_coef) > 0.001 else float("inf")

    print(f"{city:<12} {mdsr_coef:>+12.3f} {mm_coef:>+12.4f} {ratio:>+16.1f}")

print("\ninterpretation: the ratio shows how much more rate-sensitive mdsr is than mm.")
print("a large ratio confirms that rates move monthly burden but not long-run cost.")