import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
master_path = os.path.join(root, "data", "clean", "master.csv")
out_dir = os.path.join(root, "data", "paper")
os.makedirs(out_dir, exist_ok=True)
order = ["Toronto", "Vancouver", "London", "New York"]
df = pd.read_csv(master_path)
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)
df["mdsr_pct"] = df["mdsr"] * 100
df["ln_price"] = np.log(df["price_local"])
df["ln_income"] = np.log(df["income"])
df["yr"] = df["date"].dt.year
def save(frame, name, index=False):
    path = os.path.join(out_dir, name)
    frame.to_csv(path, index=index)
    print("saved", name)
def stars(p):
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""
def fit(d, ycol, xcols, lags=6):
    x = sm.add_constant(d[xcols])
    return sm.OLS(d[ycol], x).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
# figure data (paste into google sheets and make line charts) 
fig1 = df.pivot(index="date", columns="city", values="median_multiple")[order].round(2)
fig1["threshold_5.1"] = 5.1
save(fig1.reset_index().assign(date=lambda t: t["date"].dt.strftime("%Y-%m")), "fig1_median_multiple_monthly.csv")
fig2 = df.pivot(index="date", columns="city", values="mdsr_pct")[order].round(1)
fig2["line_100pct"] = 100
save(fig2.reset_index().assign(date=lambda t: t["date"].dt.strftime("%Y-%m")), "fig2_mdsr_monthly.csv")
# toronto, both indices set to 100 in jan 2019 so they sit on one axis
t = df[df["city"] == "Toronto"].set_index("date")
fig3 = pd.DataFrame({
    "median_multiple_index": (t["median_multiple"] / t["median_multiple"].iloc[0] * 100).round(1),
    "mdsr_index": (t["mdsr_pct"] / t["mdsr_pct"].iloc[0] * 100).round(1),
    "mortgage_rate": t["rate"].round(2),
})
save(fig3.reset_index().assign(date=lambda x: x["date"].dt.strftime("%Y-%m")), "fig3_toronto_mm_vs_mdsr.csv")
rates = df.groupby(["yr", "city"])["rate"].mean().unstack()[order].round(2)
save(rates.reset_index(), "fig4_mortgage_rate_by_year.csv")
# annual descriptive table 
ann = df.groupby(["city", "yr"]).agg(mm=("median_multiple", "mean"), mdsr=("mdsr_pct", "mean")).round(2).reset_index()
ann_mm = ann.pivot(index="yr", columns="city", values="mm")[order]
ann_md = ann.pivot(index="yr", columns="city", values="mdsr")[order]
save(ann_mm.reset_index(), "tbl_annual_median_multiple.csv")
save(ann_md.reset_index(), "tbl_annual_mdsr_pct.csv")
peaks = []
for c in order:
    d = df[df["city"] == c]
    imm = d["median_multiple"].idxmax()
    imd = d["mdsr_pct"].idxmax()
    peaks.append({
        "city": c,
        "mm_peak": round(d.loc[imm, "median_multiple"], 2),
        "mm_peak_month": d.loc[imm, "date"].strftime("%Y-%m"),
        "mm_dec2024": round(d[d["date"] == "2024-12-01"]["median_multiple"].iloc[0], 2),
        "mdsr_peak_pct": round(d.loc[imd, "mdsr_pct"], 1),
        "mdsr_peak_month": d.loc[imd, "date"].strftime("%Y-%m"),
        "mdsr_dec2024_pct": round(d[d["date"] == "2024-12-01"]["mdsr_pct"].iloc[0], 1),
    })
save(pd.DataFrame(peaks), "tbl_peaks.csv")
# table 1 mdsr regressions 
xs = ["rate", "unemployment", "ln_price", "ln_income"]
labels = {"rate": "Mortgage rate", "unemployment": "Unemployment rate",
          "ln_price": "ln(price)", "ln_income": "ln(income)", "const": "Constant"}
models = {}
for c in order:
    models[c] = fit(df[df["city"] == c], "mdsr_pct", xs)

rows = []
for v in ["rate", "unemployment", "ln_price", "ln_income", "const"]:
    r1 = {"variable": labels[v]}
    r2 = {"variable": ""}
    for c in order:
        m = models[c]
        r1[c] = f"{m.params[v]:.3f}{stars(m.pvalues[v])}"
        r2[c] = f"({m.bse[v]:.3f})"
    rows += [r1, r2]
rows.append({"variable": "Observations", **{c: int(models[c].nobs) for c in order}})
rows.append({"variable": "R-squared", **{c: f"{models[c].rsquared:.3f}" for c in order}})
tbl1 = pd.DataFrame(rows)
save(tbl1, "tbl1_mdsr_regression.csv")
#  table 2 mm vs mdsr rate coefficient
rows = []
for c in order:
    d = df[df["city"] == c]
    mm_m = fit(d, "median_multiple", xs)
    rows.append({
        "city": c,
        "mdsr_rate_coef": round(models[c].params["rate"], 3),
        "mdsr_rate_se": round(models[c].bse["rate"], 3),
        "mm_rate_coef": round(mm_m.params["rate"], 4),
        "mm_rate_se": round(mm_m.bse["rate"], 4),
        "mm_rate_p": round(mm_m.pvalues["rate"], 3),
        "ratio_mdsr_over_mm": round(abs(models[c].params["rate"] / mm_m.params["rate"]), 0),
    })
tbl2 = pd.DataFrame(rows)
save(tbl2, "tbl2_mm_vs_mdsr_rate.csv")
# table 3 diagnostics 
rows = []
for c in order:
    d = df[df["city"] == c].copy()
    d["rate_lag1"] = d["rate"].shift(1)
    d = d.dropna(subset=["rate_lag1"])
    xfull = sm.add_constant(d[["rate", "rate_lag1", "unemployment", "ln_price", "ln_income"]])
    vifs = {v: variance_inflation_factor(xfull.values, i) for i, v in enumerate(xfull.columns) if v != "const"}
    dfin = df[df["city"] == c]
    xf = sm.add_constant(dfin[xs])
    ols = sm.OLS(dfin["mdsr_pct"], xf).fit()
    bp = het_breuschpagan(ols.resid, xf)
    rows.append({
        "city": c,
        "max_vif_with_lag": round(max(vifs.values()), 1),
        "vif_rate": round(vifs["rate"], 1),
        "vif_rate_lag1": round(vifs["rate_lag1"], 1),
        "bp_lm_stat": round(bp[0], 2),
        "bp_p_value": round(bp[1], 4),
        "durbin_watson": round(durbin_watson(ols.resid), 3),
    })
tbl3 = pd.DataFrame(rows)
save(tbl3, "tbl3_diagnostics.csv")
# diagram data payment per 100k as the rate moves 
def pay(p, r, years):
    i = r / 100 / 12
    n = years * 12
    return p * i / (1 - (1 + i) ** -n)

grid = np.arange(1, 9.01, 0.5)
curve = pd.DataFrame({
    "rate_pct": grid,
    "payment_25y_per_100k": [round(pay(100000, r, 25), 0) for r in grid],
    "payment_30y_per_100k": [round(pay(100000, r, 30), 0) for r in grid],
})
save(curve, "diagram_payment_vs_rate.csv")
# renewal shock, loan sizes are just examples i picked
def renewal(loan, r_old, r_new, amort, term_years):
    p_old = pay(loan, r_old, amort)
    i = r_old / 100 / 12
    k = term_years * 12
    bal = loan * (1 + i) ** k - p_old * (((1 + i) ** k - 1) / i)
    p_new = pay(bal, r_new, amort - term_years)
    return {"loan_at_start": loan, "rate_start_pct": r_old, "payment_start": round(p_old, 0),
            "balance_at_renewal": round(bal, 0), "rate_renewal_pct": r_new,
            "payment_after_renewal": round(p_new, 0), "payment_rise_pct": round((p_new / p_old - 1) * 100, 1)}

shock = pd.DataFrame([
    {"case": "canada 5y fixed, 2021 rate to 2024 rate", **renewal(600000, rates.loc[2021, "Toronto"], rates.loc[2024, "Toronto"], 25, 5)},
    {"case": "uk 2y fixed, 2021 rate to 2023 rate", **renewal(400000, rates.loc[2021, "London"], rates.loc[2023, "London"], 25, 2)},
])
us_old = pay(500000, rates.loc[2021, "New York"], 30)
us_new = pay(500000, rates.loc[2024, "New York"], 30)
shock.loc[len(shock)] = {"case": "us 30y locked at 2021 rate vs new buyer at 2024 rate", "loan_at_start": 500000,
    "rate_start_pct": rates.loc[2021, "New York"], "payment_start": round(us_old, 0), "balance_at_renewal": np.nan,
    "rate_renewal_pct": rates.loc[2024, "New York"], "payment_after_renewal": round(us_new, 0),
    "payment_rise_pct": round((us_new / us_old - 1) * 100, 1)}
save(shock, "diagram_renewal_shock.csv")
# checks against numbers already written in the paper 
print("\n--- check against the paper ---")
want = {"Vancouver": (9.047, 0.110), "Toronto": (7.361, 0.130), "London": (6.979, 0.103), "New York": (4.953, 0.153)}
for c in order:
    got = (round(float(models[c].params["rate"]), 3), round(float(models[c].bse["rate"]), 3))
    ok = abs(got[0] - want[c][0]) < 0.005 and abs(got[1] - want[c][1]) < 0.005
    print(c, "rate coef/se", got, "paper", want[c], "OK" if ok else "DIFFERENT")
tor = peaks[0]
print("\ntoronto mm: peak", tor["mm_peak"], tor["mm_peak_month"], "| dec 2024", tor["mm_dec2024"],
      "| change from peak %", round((tor["mm_dec2024"] / tor["mm_peak"] - 1) * 100, 1))
print("toronto mm 2022 avg -> 2024 avg %", round((ann_mm.loc[2024, "Toronto"] / ann_mm.loc[2022, "Toronto"] - 1) * 100, 1))
print("toronto mdsr 2024 avg", ann_md.loc[2024, "Toronto"])
print("new york mm 2019 -> 2024 avg %", round((ann_mm.loc[2024, "New York"] / ann_mm.loc[2019, "New York"] - 1) * 100, 1))
print("london mm 2019:", ann_mm.loc[2019, "London"])
print("\nall done, files are in", out_dir)