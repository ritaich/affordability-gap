# regression diagnostics for the full per-city models
# i run vif, breusch-pagan, and durbin-watson
# tomorrow's chart and tomorrow's writing will reflect what these show

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import statsmodels.stats.api as sms
from statsmodels.stats.outliers_influence import variance_inflation_factor
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

predictors = ["rate", "rate_lag1", "unemployment", "log_price", "log_income"]

print("=" * 70)
print("regression diagnostics per city")
print("=" * 70)
print()

for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    model = smf.ols(
        "mdsr_pct ~ rate + rate_lag1 + unemployment + log_price + log_income",
        data=sub
    ).fit()

    print(f"--- {city} ---")

    # vif - i build a design matrix and compute vif per predictor
    X = sub[predictors].copy()
    X["const"] = 1  # vif formula needs a constant column
    print("  vif (multicollinearity):")
    for i, col in enumerate(predictors):
        vif = variance_inflation_factor(X.values, i)
        flag = "  ⚠️ HIGH" if vif > 10 else "  warning" if vif > 5 else ""
        print(f"    {col:<15} {vif:>8.2f}{flag}")

    # breusch-pagan (heteroskedasticity)
    bp_test = sms.het_breuschpagan(model.resid, model.model.exog)
    bp_stat, bp_p = bp_test[0], bp_test[1]
    bp_verdict = "heteroskedasticity ⚠️" if bp_p < 0.05 else "ok"
    print(f"  breusch-pagan: stat={bp_stat:.2f}, p={bp_p:.4f}  → {bp_verdict}")

    # durbin-watson (autocorrelation)
    from statsmodels.stats.stattools import durbin_watson
    dw = durbin_watson(model.resid)
    if dw < 1.5: dw_verdict = "positive serial correlation ⚠️"
    elif dw > 2.5: dw_verdict = "negative serial correlation ⚠️"
    else: dw_verdict = "ok"
    print(f"  durbin-watson: {dw:.3f}  → {dw_verdict}")
    print()

# summary table
print("=" * 70)
print("summary table — diagnostic results across cities")
print("=" * 70)
print(f"{'city':<12} {'max vif':>10} {'b-p p':>10} {'d-w':>8}")
print("-" * 45)
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    model = smf.ols(
        "mdsr_pct ~ rate + rate_lag1 + unemployment + log_price + log_income",
        data=sub
    ).fit()
    X = sub[predictors].copy()
    X["const"] = 1
    vifs = [variance_inflation_factor(X.values, i) for i in range(len(predictors))]
    bp_p = sms.het_breuschpagan(model.resid, model.model.exog)[1]
    from statsmodels.stats.stattools import durbin_watson
    dw = durbin_watson(model.resid)
    print(f"{city:<12} {max(vifs):>10.2f} {bp_p:>10.4f} {dw:>8.3f}")