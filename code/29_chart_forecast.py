# forecast visualization 4 cities × 3 scenarios overlaid on historical mdsr
# i show the historical trajectory as a solid line and each scenario as
# a dashed line with a shaded confidence band into 2025
# this is the paper's forward-looking figure
import pandas as pd
import plotly.graph_objects as go
import subprocess
from pathlib import Path
from plotly.subplots import make_subplots
base = Path(__file__).parent.parent
hist_path = base / "data/clean/master.csv"
fc_path = base / "data/clean/forecasts.csv"
out_path = base / "visualizations/06_mdsr_forecast_scenarios.html"
hist = pd.read_csv(hist_path)
fc = pd.read_csv(fc_path)
hist["mdsr_pct"] = hist["mdsr"] * 100
hist["date_dt"] = pd.to_datetime(hist["date"], format="%Y-%m")
fc["date_dt"] = pd.to_datetime(fc["date"], format="%Y-%m")
# one subplot per city
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=["Toronto", "Vancouver", "London", "New York"],
    shared_yaxes=False,
    vertical_spacing=0.13,
    horizontal_spacing=0.09,
)

positions = {
    "Toronto":   (1, 1),
    "Vancouver": (1, 2),
    "London":    (2, 1),
    "New York":  (2, 2),
}

scenario_colors = {
    "optimistic":   "#327400",
    "baseline":     "#546E7A",
    "pessimistic": "#760000",
}
for city, (row, col) in positions.items():
    # historical line
    h = hist[hist["city"] == city].sort_values("date_dt")
    fig.add_trace(
        go.Scatter(
            x=h["date_dt"], y=h["mdsr_pct"],
            name="historical" if city == "Toronto" else None,
            mode="lines",
            line=dict(color="#333", width=2),
            showlegend=(city == "Toronto"),
            hovertemplate="%{x|%b %Y}<br>MDSR: %{y:.1f}%<extra></extra>",
        ),
        row=row, col=col,
    )
    # add each scenario forecast
    for scenario, color in scenario_colors.items():
        s = fc[(fc["city"] == city) & (fc["scenario"] == scenario)].sort_values("date_dt")

        # forecasted mdsr line
        fig.add_trace(
            go.Scatter(
                x=s["date_dt"], y=s["mdsr_pct_forecast"],
                name=scenario if city == "Toronto" else None,
                mode="lines",
                line=dict(color=color, width=2, dash="dash"),
                showlegend=(city == "Toronto"),
                hovertemplate=f"%{{x|%b %Y}}<br>{scenario}: %{{y:.1f}}%<extra></extra>",
            ),
            row=row, col=col,
        )
        # confidence band, i map each hex to a matching semi-transparent rgba
        band_fill = {
            "optimistic":   "rgba(46, 125, 50, 0.15)",
            "baseline":     "rgba(84, 110, 122, 0.15)",
            "pessimistic": "rgba(198, 40, 40, 0.15)",
        }[scenario]
        fig.add_trace(
            go.Scatter(
                x=list(s["date_dt"]) + list(s["date_dt"])[::-1],
                y=list(s["ci_high"]) + list(s["ci_low"])[::-1],
                fill="toself",
                fillcolor=band_fill,
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=row, col=col,
        )
    # mark where forecast begins
    fig.add_vline(x="2024-12-01", line=dict(color="#999", width=1, dash="dot"),
                  row=row, col=col)

fig.update_layout(
    title=dict(
        text="<b>MDSR forecast scenarios, jan-dec 2025</b><br>"
             "<span style='font-size:12px;color:#666'>"
             "solid line = historical MDSR through dec 2024. dashed lines = forecast under three interest-rate paths, "
             "holding price/income/unemployment constant. shaded bands are 95% CI.</span>",
        x=0.02, y=0.97,
    ),
    height=800, width=1150,
    plot_bgcolor="white",
    font=dict(family="Helvetica, Arial", size=11),
    margin=dict(t=110, b=60, l=60, r=40),
    legend=dict(x=0.02, y=1.02, orientation="h"),
    hovermode="x unified",
)

for anchor in fig.layout.annotations:
    anchor.font.size = 12
    anchor.font.color = "#333"

fig.update_yaxes(title_text="MDSR (%)", showgrid=True, gridcolor="#eee", zeroline=False)
fig.update_xaxes(showgrid=True, gridcolor="#eee")
out_path.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(str(out_path), include_plotlyjs="cdn")
print(f"saved chart to {out_path}")
subprocess.run(["open", str(out_path)])