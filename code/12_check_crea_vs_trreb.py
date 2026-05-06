# does crea's toronto hpi line up with trreb's average price?
# they're different metrics (benchmark vs average) so absolute values
# will differ, but the percent changes month over month should be similar
# if they don't agree on direction we have a problem
import pandas as pd
from pathlib import Path
base = Path(__file__).parent.parent / "data/clean"
crea = pd.read_csv(base / "crea_hpi_two_cities.csv")
trreb = pd.read_csv(base / "toronto_with_mm.csv")
# just toronto from crea
crea_tor = crea[crea["city"] == "Toronto"][["date", "benchmark_sa_cad"]].copy()
crea_tor = crea_tor.rename(columns={"benchmark_sa_cad": "crea_benchmark"})
# just the bits we need from trreb
trreb_tor = trreb[["date", "avg_price"]].copy()
trreb_tor = trreb_tor.rename(columns={"avg_price": "trreb_avg"})
merged = crea_tor.merge(trreb_tor, on="date", how="inner")
merged = merged.sort_values("date").reset_index(drop=True)
# correlation between the two series - should be very high
corr = merged["crea_benchmark"].corr(merged["trreb_avg"])
print(f"correlation between crea benchmark and trreb avg price: {corr:.4f}")
print(f"(closer to 1.0 = they tell the same story)")
print()
# pct change per month, see if they move together
merged["crea_pct"] = merged["crea_benchmark"].pct_change() * 100
merged["trreb_pct"] = merged["trreb_avg"].pct_change() * 100
# how often do they agree on direction (both up or both down)?
both = merged.dropna(subset=["crea_pct", "trreb_pct"])
agree = ((both["crea_pct"] > 0) == (both["trreb_pct"] > 0)).sum()
total = len(both)
print(f"directional agreement: {agree}/{total} months ({100*agree/total:.0f}%)")
print()
# show the months where they disagreed - usually small movements near zero
disagree = both[(both["crea_pct"] > 0) != (both["trreb_pct"] > 0)]
if len(disagree) > 0:
    print("months where they disagreed on direction:")
    print(disagree[["date", "crea_pct", "trreb_pct"]].to_string(index=False))