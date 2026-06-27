# standardized coefficients let me rank predictors on a common scale
# i z-score every variable (mean=0, sd=1) then re-run the regression
# the coefficients are now directly comparable across variables AND cities

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
df["rate_lag1"] = df.groupby("city")["rate"].shift(1)
df = df.dropna(subset=["rate_lag1"]).copy()


def standardize(s):
    # z-score: (value - mean) / standard deviation
    return (s - s.mean()) / s.std()


variables = ["rate", "rate_lag1", "unemployment", "log_price", "log_income"]

print("=" * 70)
print("standardized regression coefficients per city")
print("=" * 70)
print("(beta now reads as: sd-change in mdsr per sd-change in predictor)")
print()

all_coefs = {}
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()

    # standardize everything within this city
    sub["mdsr_z"] = standardize(sub["mdsr_pct"])
    for v in variables:
        sub[v + "_z"] = standardize(sub[v])

    formula = ("mdsr_z ~ rate_z + rate_lag1_z + unemployment_z "
               "+ log_price_z + log_income_z")
    model = smf.ols(formula, data=sub).fit()

    print(f"--- {city} ---")
    coefs = {}
    for v in variables:
        z_name = v + "_z"
        beta = model.params[z_name]
        p = model.pvalues[z_name]
        sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
        print(f"  {v:<15} {beta:>+7.3f}  {sig}")
        coefs[v] = beta
    all_coefs[city] = coefs
    print(f"  r² = {model.rsquared:.4f}")
    print()

# side-by-side comparison
print("=" * 70)
print("side-by-side: which predictor matters most in each city")
print("=" * 70)
print(f"{'variable':<15} {'toronto':>10} {'vancouver':>10} {'london':>10} {'new york':>10}")
print("-" * 60)
for v in variables:
    row = f"{v:<15}"
    for city in ["Toronto", "Vancouver", "London", "New York"]:
        row += f" {all_coefs[city][v]:>+10.3f}"
    print(row)

# the most important predictor per city
print("\ntop predictor of mdsr per city (by absolute standardized coef):")
for city, coefs in all_coefs.items():
    ranked = sorted(coefs.items(), key=lambda x: -abs(x[1]))
    top = ranked[0]
    print(f"  {city:<12} → {top[0]} (|β|={abs(top[1]):.3f})")