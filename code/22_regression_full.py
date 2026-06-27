# full multiple regression: mdsr ~ rate + lag(rate) + unemployment + log(price) + log(income)
# i include lag(rate) because mortgage rates affect buyers with a delay
# i use logs for price/income so coefficients are interpretable as elasticities

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

# build lagged rate by city (one month lag)
df = df.sort_values(["city", "date"]).reset_index(drop=True)
df["rate_lag1"] = df.groupby("city")["rate"].shift(1)

# drop the first month per city (no lag available)
df_clean = df.dropna(subset=["rate_lag1"]).copy()

print("=" * 70)
print("full regression: mdsr ~ rate + rate_lag1 + unemployment + log_price + log_income")
print("=" * 70)
print()

# i fit one model per city to see how the structure differs
results = {}
for city in sorted(df_clean["city"].unique()):
    sub = df_clean[df_clean["city"] == city].copy()
    model = smf.ols(
        "mdsr_pct ~ rate + rate_lag1 + unemployment + log_price + log_income",
        data=sub
    ).fit()
    results[city] = model

    print(f"--- {city} ---")
    print(f"r² = {model.rsquared:.3f}   adj r² = {model.rsquared_adj:.3f}   n = {int(model.nobs)}")
    print(f"durbin-watson = {model.resid.autocorr():.3f}")
    # ^ a simple autocorrelation check, formal d-w is in summary()

    # i print a clean coefficient table
    print(f"{'variable':<15} {'coef':>10} {'se':>8} {'p':>9} {'sig':>4}")
    for var in ["Intercept", "rate", "rate_lag1", "unemployment", "log_price", "log_income"]:
        if var in model.params.index:
            coef = model.params[var]
            se = model.bse[var]
            p = model.pvalues[var]
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
            print(f"  {var:<13} {coef:>+10.3f} {se:>8.3f} {p:>9.4f}  {sig:>4}")
    print()

# pooled model with city fixed effects
print("=" * 70)
print("pooled regression with city fixed effects")
print("=" * 70)
pooled = smf.ols(
    "mdsr_pct ~ rate + rate_lag1 + unemployment + log_price + log_income + C(city)",
    data=df_clean
).fit()
print(pooled.summary())
