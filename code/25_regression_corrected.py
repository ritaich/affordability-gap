# corrected regression with two methodological fixes:
# 1. drop rate_lag1 because of severe multicollinearity (vif > 100)
# 2. use newey-west (hac) standard errors to account for serial correlation
#    and heteroskedasticity simultaneously
# this is the version that goes in the paper

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/master.csv"

df = pd.read_csv(in_path)
df["mdsr_pct"] = df["mdsr"] * 100
df["log_price"] = np.log(df["price_local"])
df["log_income"] = np.log(df["income"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)

# i fit with hac standard errors, maxlags=6 (six month autocorrelation window)
# this is standard for monthly data with strong serial correlation

print("=" * 70)
print("corrected regression — newey-west robust SE, lag dropped")
print("=" * 70)
print()

results = {}
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    model = smf.ols(
        "mdsr_pct ~ rate + unemployment + log_price + log_income",
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
        print(f"  {var:<13} {coef:>+10.3f} {se:>9.3f} {p:>9.4f}  {sig:>3}")
    print()

# summary table for the paper
print("=" * 70)
print("rate coefficient summary (the key finding)")
print("=" * 70)
print(f"{'city':<12} {'coef':>10} {'hac se':>10} {'95% ci':>20} {'p':>10}")
print("-" * 70)
for city in sorted(results.keys()):
    m = results[city]
    coef = m.params["rate"]
    se = m.bse["rate"]
    ci_low, ci_high = m.conf_int().loc["rate"]
    p = m.pvalues["rate"]
    print(f"{city:<12} {coef:>+10.3f} {se:>10.3f}  [{ci_low:>+6.2f}, {ci_high:>+6.2f}] {p:>10.4f}")