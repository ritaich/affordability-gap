# simple ols regression: mdsr ~ rate, one per city
# this tests hypothesis h1 from methodology section 2.3
# i'll get the coefficient (beta), p-value, r-squared, and standard error
# also a pooled model with city fixed effects for comparison

import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/master.csv"

df = pd.read_csv(in_path)

# mdsr is currently a fraction (0.53), but i convert to percent (53.3)
# so the coefficient reads naturally as "pp of mdsr per pp of rate"
df["mdsr_pct"] = df["mdsr"] * 100

print("=" * 70)
print("simple regression: mdsr ~ mortgage rate")
print("=" * 70)
print()

results = {}
for city in sorted(df["city"].unique()):
    sub = df[df["city"] == city].copy()
    model = smf.ols("mdsr_pct ~ rate", data=sub).fit()

    # i pull out what i care about
    beta = model.params["rate"]
    se = model.bse["rate"]
    p = model.pvalues["rate"]
    r2 = model.rsquared
    n = int(model.nobs)

    results[city] = {
        "beta": beta, "se": se, "p": p, "r2": r2, "n": n
    }

    # significance stars (econ convention)
    stars = ""
    if p < 0.01: stars = "***"
    elif p < 0.05: stars = "**"
    elif p < 0.10: stars = "*"

    print(f"{city}:")
    print(f"  beta = {beta:+.3f}{stars}  (se = {se:.3f}, p = {p:.4f})")
    print(f"  r² = {r2:.3f}   n = {n}")
    print()

# pooled model with city fixed effects
print("=" * 70)
print("pooled regression: mdsr ~ rate + city fixed effects")
print("=" * 70)
print()
pooled = smf.ols("mdsr_pct ~ rate + C(city)", data=df).fit()
print(pooled.summary())

# summary table for the paper
print("\n" + "=" * 70)
print("clean summary for paper:")
print("=" * 70)
print(f"{'city':<12} {'beta':>8} {'se':>7} {'p':>9} {'r²':>6}  {'sig':>4}")
print("-" * 50)
for city, r in results.items():
    sig = "***" if r["p"] < 0.01 else "**" if r["p"] < 0.05 else "*" if r["p"] < 0.10 else ""
    print(f"{city:<12} {r['beta']:>+8.3f} {r['se']:>7.3f} {r['p']:>9.4f} {r['r2']:>6.3f}  {sig:>4}")

print("\nsignificance: *** p<0.01, ** p<0.05, * p<0.10")
print("beta interpretation: 1 pp rate increase → beta pp mdsr increase, holding price/income fixed")