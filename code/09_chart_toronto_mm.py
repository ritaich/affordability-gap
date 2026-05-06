# three-city affordability chart with demographia bands as background
# i annotate key macro events so the story is readable

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

base = Path(__file__).parent.parent
in_path = base / "data/clean/cities_with_mm.csv"
out_path = base / "visualizations/03_three_cities_median_multiple.png"

# styling consistent with previous charts
mpl.rcParams['font.family'] = 'Helvetica'
mpl.rcParams['font.size'] = 11
mpl.rcParams['axes.titlesize'] = 13
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.grid'] = True
mpl.rcParams['grid.alpha'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'

city_colors = {
    "Toronto":   "#C8102E",
    "Vancouver": "#1B5E20",
    "London":    "#1D3557",
}

bands = [
    (3.0, 4.0,  "#E1F5EE", "moderately unaffordable"),
    (4.0, 5.0,  "#FCEFD4", "seriously unaffordable"),
    (5.0, 8.9,  "#FCE3CB", "severely unaffordable"),
    (8.9, 20.0, "#FBD0D0", "impossibly unaffordable"),
]

events = [
    ("2020-03", "covid"),
    ("2022-03", "first canadian rate hike"),
    ("2023-07", "peak rates"),
]

df = pd.read_csv(in_path)
df["d"] = pd.to_datetime(df["date"], format="%Y-%m")

fig, ax = plt.subplots(figsize=(12, 7))

for low, high, color, _ in bands:
    ax.axhspan(low, high, color=color, alpha=0.5, zorder=0)

for city in city_colors:
    s = df[df["city"] == city].sort_values("d")
    ax.plot(s["d"], s["median_multiple"],
            color=city_colors[city], linewidth=2.2,
            marker="o", markersize=3.5,
            label=city, zorder=3)

# event lines and labels at the top
for date_str, label in events:
    ev = pd.to_datetime(date_str, format="%Y-%m")
    ax.axvline(ev, color="gray", linestyle=":", linewidth=0.9, zorder=2)
    ax.annotate(label, xy=(ev, 14.2), xytext=(0, 0),
                textcoords="offset points", ha="center", fontsize=8.5,
                color="#444",
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec="gray", lw=0.5, alpha=0.9))

ax.set_title("Housing Affordability in Toronto, Vancouver, and London, 2019-2024\n"
             "Median Multiple = composite house price index / median annual household income",
             loc="left", pad=14)
ax.set_ylabel("median multiple")
ax.set_xlabel("")
ax.set_ylim(7, 15)
ax.set_yticks(range(7, 16))
ax.legend(loc="lower left", frameon=False, fontsize=11)

# band labels on right side
band_x = df["d"].max() + pd.Timedelta(days=20)
for low, high, _, label in bands:
    if low >= 7 and high <= 15:
        mid = (low + high) / 2
        if 7 <= mid <= 15:
            ax.text(band_x, mid, label, fontsize=8, color="#666",
                    ha="left", va="center")

fig.text(0.01, 0.01,
         "sources: crea hpi composite benchmark (toronto, vancouver), uk land registry hpi (london), "
         "statcan table 11-10-0190-01 + ons regional series (income, 2024 currency).",
         fontsize=8, color="#888")

plt.tight_layout(rect=[0, 0.04, 1, 1])
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=160, bbox_inches="tight")
print(f"saved chart to {out_path}")
plt.show()