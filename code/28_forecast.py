# forecasting mdsr under three interest-rate scenarios
# these are conditional forecasts: i hold price, income, and unemployment
# constant at their dec 2024 levels and only vary the mortgage rate path
# this isolates the effect of rate policy from other market movements

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path
base = Path(__file__).parent.parent
in_path = base / "data/clean/master.csv"
out_path = base / "data/clean/forecasts.csv"
df = pd.read_csv(in_path)
df["mdsr_pct"] = df["mdsr"] * 100
df["log_price"] = np.log(df["price_local"])
df["log_income"] = np.log(df["income"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)
# forecast from jan 2025 through dec 2025
forecast_months = pd.date_range("2025-01-01", "2025-12-01", freq="MS")
forecast_dates = [d.strftime("%Y-%m") for d in forecast_months]
# rate paths (annual mortgage rate percentages)
# baseline holds at the country's dec 2024 rate
# optimistic drops linearly to 4% by june then stays
# pessimistic rises linearly to 7% by june then stays
def rate_path(start, end, n=12, hold_from=6):
    # linear from start to end for the first `hold_from` months, then flat
    out = []
    for i in range(n):
        if i < hold_from:
            frac = i / max(hold_from - 1, 1)
            r = start + (end - start) * frac
        else:
            r = end
        out.append(r)
    return out

forecasts = []
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    # fit the model on historical data with newey-west errors
    model = smf.ols(
        "mdsr_pct ~ rate + unemployment + log_price + log_income",
        data=sub
    ).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    # last observed values, i hold these constant across forecasts
    last = sub.iloc[-1]
    last_rate = float(last["rate"])
    last_unemp = float(last["unemployment"])
    last_logprice = float(last["log_price"])
    last_logincome = float(last["log_income"])
    # build the three scenarios' rate paths
    scenarios = {
        "optimistic":   rate_path(last_rate, 4.0),
        "baseline":     rate_path(last_rate, last_rate),
        "pessimistic": rate_path(last_rate, 7.0),
    }

    for scenario_name, rates in scenarios.items():
        for date_str, r in zip(forecast_dates, rates):
            X = pd.DataFrame([{
                "rate": r,
                "unemployment": last_unemp,
                "log_price": last_logprice,
                "log_income": last_logincome,
            }])
            pred = model.get_prediction(X)
            mdsr_hat = float(pred.predicted_mean[0])
            ci = pred.conf_int()
            ci_low, ci_high = float(ci[0][0]), float(ci[0][1])

            forecasts.append({
                "city": city,
                "scenario": scenario_name,
                "date": date_str,
                "rate": r,
                "mdsr_pct_forecast": mdsr_hat,
                "ci_low": ci_low,
                "ci_high": ci_high,
            })

fc = pd.DataFrame(forecasts)
out_path.parent.mkdir(parents=True, exist_ok=True)
fc.to_csv(out_path, index=False)
print(f"saved {len(fc)} forecast rows to {out_path}\n")
# summary at end of forecast window (dec 2025)
print("mdsr at dec 2025 under each scenario (in %):")
print(f"{'city':<12} {'optimistic':>12} {'baseline':>12} {'pessimistic':>12}")
print("-" * 55)
last_month = fc[fc["date"] == "2025-12"]
for city in sorted(last_month["city"].unique()):
    sub = last_month[last_month["city"] == city]
    opt = float(sub[sub["scenario"] == "optimistic"]["mdsr_pct_forecast"].iloc[0])
    base_v = float(sub[sub["scenario"] == "baseline"]["mdsr_pct_forecast"].iloc[0])
    pes = float(sub[sub["scenario"] == "pessimistic"]["mdsr_pct_forecast"].iloc[0])
    print(f"{city:<12} {opt:>+11.1f}% {base_v:>+11.1f}% {pes:>+11.1f}%")