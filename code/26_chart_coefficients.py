# the money chart: rate coefficient with 95% confidence interval per city
# i build this in plotly so it's interactive and goes on the github pages dashboard
# the ordering reflects mortgage market structure: canada > uk > usa

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import plotly.graph_objects as go
import subprocess
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/master.csv"
out_path = base / "visualizations/05_rate_coefficient_by_city.html"

df = pd.read_csv(in_path)
df["mdsr_pct"] = df["mdsr"] * 100
df["log_price"] = np.log(df["price_local"])
df["log_income"] = np.log(df["income"])
df = df.sort_values(["city", "date"]).reset_index(drop=True)

# i re-run the corrected regression to get the numbers for plotting
results = {}
for city in df["city"].unique():
    sub = df[df["city"] == city]
    m = smf.ols(
        "mdsr_pct ~ rate + unemployment + log_price + log_income",
        data=sub
    ).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
    ci = m.conf_int().loc["rate"]
    results[city] = {
        "coef": m.params["rate"],
        "se": m.bse["rate"],
        "ci_low": ci[0],
        "ci_high": ci[1],
    }

# order by coefficient size (biggest exposure first)
order = sorted(results.keys(), key=lambda c: -results[c]["coef"])

city_colors = {
    "Vancouver": "#345136",
    "Toronto":   "#7D0015",
    "London":    "#0044A3",
    "New York":  "#6F1474",
}

# i annotate each bar with the country's mortgage market structure
mortgage_market = {
    "Vancouver": "5-yr fixed",
    "Toronto":   "5-yr fixed",
    "London":    "2-yr fixed",
    "New York":  "30-yr fixed",
}

fig = go.Figure()

for city in order:
    r = results[city]
    error = r["coef"] - r["ci_low"]
    fig.add_trace(go.Bar(
        x=[city],
        y=[r["coef"]],
        name=city,
        marker_color=city_colors[city],
        error_y=dict(
            type="data", array=[error], thickness=1.5, width=12, color="#333"
        ),
        text=f"<b>{r['coef']:.2f}</b><br>{mortgage_market[city]}",
        textposition="outside",
        textfont=dict(size=12),
        hovertemplate=(f"<b>{city}</b><br>"
                       f"rate coefficient: {r['coef']:.3f}<br>"
                       f"95% ci: [{r['ci_low']:.2f}, {r['ci_high']:.2f}]<br>"
                       f"hac se: {r['se']:.3f}<br>"
                       f"mortgage market: {mortgage_market[city]}<extra></extra>"),
        showlegend=False,
    ))

fig.update_layout(
    title=dict(
        text="<b>Mortgage rate transmission to housing burden by city</b><br>"
             "<span style='font-size:12px;color:#666'>"
             "OLS coefficient on mortgage rate, controlling for price, income, unemployment. "
             "Bars show 95% CI with Newey-West HAC standard errors.</span>",
        x=0.02, y=0.95,
    ),
    yaxis=dict(
        title="percentage-point increase in MDSR per 1pp rise in mortgage rate",
        range=[0, 11], dtick=1,
        showgrid=True, gridcolor="#eee",
    ),
    xaxis=dict(title=""),
    plot_bgcolor="white",
    height=550, width=900,
    font=dict(family="Helvetica, Arial", size=11),
    margin=dict(t=100, b=80, l=80, r=40),
)

# explanatory annotation at bottom
fig.add_annotation(
    text=("interpretation: a 1 percentage-point increase in the prevailing mortgage rate raises "
          "the typical buyer's<br>monthly mortgage burden as a share of income by the values shown. "
          "the ranking follows mortgage market structure."),
    showarrow=False,
    xref="paper", yref="paper", x=0, y=-0.20, xanchor="left",
    font=dict(size=10, color="#666"),
)

out_path.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(str(out_path), include_plotlyjs="cdn")
print(f"saved chart to {out_path}")
subprocess.run(["open", str(out_path)])