import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(root, "data", "clean", "master.csv"))
df["ln_price"] = np.log(df["price_local"])
df["ln_income"] = np.log(df["income"])
cols = ["rate", "unemployment", "ln_price", "ln_income"]

rows = []
for c in ["Toronto", "Vancouver", "London", "New York"]:
    d = df[df["city"] == c]
    x = sm.add_constant(d[cols])
    v = {k: round(variance_inflation_factor(x.values, i), 1) for i, k in enumerate(x.columns) if k != "const"}
    rows.append({"city": c, **v, "max_vif_final": max(v.values())})

out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv(os.path.join(root, "data", "paper", "tbl3b_final_vif.csv"), index=False)
