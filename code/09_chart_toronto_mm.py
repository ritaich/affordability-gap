# i make a plotly version because the matplotlib show window is flaky on mac
# and i want hover tooltips for reading exact values
# plotly saves an html file that opens in chrome

import pandas as pd
import plotly.graph_objects as go
import subprocess
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/cities_with_mm.csv"
out_path = base / "visualizations/04_four_cities_median_multiple.html"

city_colors = {
    "Toronto":   "#02FF35",
    "Vancouver": "#FF00BB",
    "London":    "#FFF700",
    "New York":  "#00E5FF",
}

# demographia rating bands shown as background rectangles
bands = [
    (3.0, 4.0,  "rgba(225, 245, 238, 0.5)", "moderately unaffordable"),
    (4.0, 5.0,  "rgba(252, 239, 212, 0.5)", "seriously unaffordable"),
    (5.0, 8.9,  "rgba(252, 227, 203, 0.5)", "severely unaffordable"),
    (8.9, 20.0, "rgba(251, 208, 208, 0.5)", "impossibly unaffordable"),
]

events = [
    ("2020-03-01", "covid"),
    ("2022-03-01", "first canadian rate hike"),
    ("2023-07-01", "peak rates"),
]

df = pd.read_csv(in_path)
df["d"] = pd.to_datetime(df["date"], format="%Y-%m")

fig = go.Figure()

# i add the rating bands first so they sit behind everything
for low, high, color, _ in bands:
    fig.add_hrect(y0=low, y1=high, fillcolor=color, line_width=0, layer="below")

# one line per city
for city, color in city_colors.items():
    s = df[df["city"] == city].sort_values("d")
    fig.add_trace(go.Scatter(
        x=s["d"], y=s["median_multiple"],
        name=city,
        mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=5),
        hovertemplate="%{y:.2f}<extra>" + city + "</extra>",
    ))

# event lines with labels at top
# i split this into two calls because plotly's add_vline + annotation_text
# is buggy on date axes in newer plotly versions
for date_str, label in events:
    fig.add_shape(
        type="line",
        x0=date_str, x1=date_str,
        y0=0, y1=1, yref="paper",
        line=dict(color="gray", width=1, dash="dot"),
    )
    fig.add_annotation(
        x=date_str, y=1.02, yref="paper",
        text=label, showarrow=False,
        font=dict(size=10, color="#444"),
        xanchor="center",
        bgcolor="white", bordercolor="gray", borderwidth=0.5,
    )

fig.update_layout(
    title=dict(
        text="<b>Housing Affordability across Four Global Cities, 2019-2024</b><br>"
             "<span style='font-size:12px;color:#666'>"
             "Median Multiple = composite house price / median annual household income</span>",
        x=0.02, y=0.96,
    ),
    yaxis=dict(title="median multiple", range=[5, 15], dtick=1, showgrid=True, gridcolor="#eee"),
    xaxis=dict(showgrid=True, gridcolor="#eee"),
    plot_bgcolor="white",
    legend=dict(x=0.02, y=0.02, bgcolor="rgba(255,255,255,0.8)"),
    height=600, width=1100,
    font=dict(family="Helvetica, Arial", size=11),
    margin=dict(t=80, b=70, l=60, r=180),
    hovermode="x unified",  # show all 4 cities at once when hovering on a date
)

# band labels on the right margin
band_label_x = df["d"].max() + pd.Timedelta(days=15)
for low, high, _, label in bands:
    if 5 <= (low + high) / 2 <= 15:
        fig.add_annotation(
            x=band_label_x, y=(low + high) / 2,
            text=label, showarrow=False,
            font=dict(size=10, color="#666"),
            xanchor="left",
        )

# source line at the bottom
fig.add_annotation(
    text="sources: crea hpi (toronto, vancouver), uk land registry hpi (london), "
         "case-shiller / fred (new york). income from statcan, ons, fred-saipe.",
    showarrow=False,
    xref="paper", yref="paper",
    x=0, y=-0.12, xanchor="left",
    font=dict(size=9, color="#888"),
)

out_path.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(str(out_path), include_plotlyjs="cdn")
print(f"saved chart to {out_path}")

subprocess.run(["open", str(out_path)])