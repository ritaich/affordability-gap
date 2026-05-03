"""
09_chart_toronto_mm.py

Plots Toronto's Median Multiple from Jan 2019 to Dec 2024, with key
macroeconomic events annotated. This is the first visual deliverable
of the project.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

INPUT_PATH = Path(__file__).parent.parent / "data" / "clean" / "toronto_with_mm.csv"
OUTPUT_PATH = Path(__file__).parent.parent / "visualizations" / "01_toronto_median_multiple.png"

# Project-wide chart styling (same as Session 3 setup)
mpl.rcParams['font.family'] = 'Helvetica'
mpl.rcParams['font.size'] = 11
mpl.rcParams['axes.titlesize'] = 13
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.grid'] = True
mpl.rcParams['grid.alpha'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'

CITY_COLORS = {
    'Toronto':   '#C8102E',
    'Vancouver': '#1B5E20',
    'London':    '#1D3557',
    'New York':  '#E8A317',
}

# Key events to annotate on the chart
EVENTS = [
    ("2020-03", "COVID-19 onset"),
    ("2022-03", "First BoC rate hike"),
    ("2023-07", "Peak policy rate (5.0%)"),
]

DEMOGRAPHIA_BANDS = [
    (3.0, 4.0,  "#E1F5EE", "Moderately unaffordable"),
    (4.0, 5.0,  "#FCEFD4", "Seriously unaffordable"),
    (5.0, 8.9,  "#FCE3CB", "Severely unaffordable"),
    (8.9, 20.0, "#FBD0D0", "Impossibly unaffordable"),
]


def main():
    df = pd.read_csv(INPUT_PATH)
    df["date_dt"] = pd.to_datetime(df["date"], format="%Y-%m")

    fig, ax = plt.subplots(figsize=(11, 6))

    # Background colour bands for Demographia rating categories
    for low, high, color, label in DEMOGRAPHIA_BANDS:
        ax.axhspan(low, high, color=color, alpha=0.5, zorder=0)

    # Main line — Toronto Median Multiple over time
    ax.plot(df["date_dt"], df["median_multiple"],
            color=CITY_COLORS["Toronto"], linewidth=2.2,
            marker='o', markersize=3.5,
            label="Toronto Median Multiple",
            zorder=3)

    # Event annotations
    for date_str, label in EVENTS:
        event_date = pd.to_datetime(date_str, format="%Y-%m")
        # find the y-value at this date
        row = df.loc[df["date"] == date_str]
        if row.empty:
            continue
        y_val = row["median_multiple"].iloc[0]
        ax.axvline(event_date, color='gray', linestyle=':', linewidth=0.9, zorder=2)
        ax.annotate(label,
                    xy=(event_date, y_val),
                    xytext=(0, 22),
                    textcoords="offset points",
                    ha='center', fontsize=9, color='#333',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white",
                              ec="gray", lw=0.5, alpha=0.9))

    # Title and labels
    ax.set_title("Toronto Housing Affordability, 2019–2024\n"
                 "Median Multiple = Median House Price ÷ Median Annual Household Income",
                 loc="left", pad=14)
    ax.set_ylabel("Median Multiple")
    ax.set_xlabel("")
    # Y-axis range — show the full Demographia spectrum
    ax.set_ylim(5, 14)
    ax.set_yticks(range(5, 15))
    # Annotate the bands on the right side
    band_labels_x = df["date_dt"].max() + pd.Timedelta(days=20)
    for low, high, _, label in DEMOGRAPHIA_BANDS:
        if low >= 5 and high <= 14:
            mid = (low + high) / 2
            if 5 <= mid <= 14:
                ax.text(band_labels_x, mid, label, fontsize=8,
                        color='#666', ha='left', va='center')

    # Source footer
    fig.text(0.01, 0.01,
             "Sources: TRREB Market Watch (monthly), Statistics Canada Table 11-10-0190-01 (annual income, "
             "linearly interpolated). Background bands: Demographia rating categories.",
             fontsize=8, color='#888')

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=160, bbox_inches='tight')
    print(f"Saved chart to: {OUTPUT_PATH}")

    plt.show()


if __name__ == "__main__":
    main()