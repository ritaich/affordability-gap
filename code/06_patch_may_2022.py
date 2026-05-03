"""
06_patch_may_2022.py
Adds May 2022 (mw2205.pdf) data manually

Reason why i did that is because  mw2205.pdf has overlapping/doubled text from a PDF rendering glitch
that prevented automated extraction. Values verified manually against the
PDF, cross-checked against the EE-typed dataset which independently produced
identical numbers (avg_price 1,212,806)

This script is idempotent : running it multiple times produces the same
result, so it's safe to re-run after every extractor run
"""

import pandas as pd
from pathlib import Path
CSV_PATH = Path(__file__).parent.parent / "data" / "clean" / "toronto_raw.csv"
MAY_2022 = {
    "date": "2022-05",
    "year": 2022,
    "month": 5,
    "sales": 7283,
    "dollar_volume": 8832867274,
    "avg_price": 1212806,
    "median_price": 1050000,
    "new_listings": 18679,
    "snlr_trend_pct": 65.1,
    "active_listings": 15433,
    "months_inventory": 1.0,
    "avg_sp_lp_pct": 103.0,
    "avg_ldom": 12.0,
    "avg_pdom": 18.0,
}


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} rows from {CSV_PATH.name}")

    # Idempotent, drop any existing 2022-05 row before adding
    df = df[df["date"] != "2022-05"]

    df = pd.concat([df, pd.DataFrame([MAY_2022])], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)

    df.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(df)} rows. May 2022 row added.")
    print()
    print("Apr-Jun 2022 sanity check (Apr should be ~1.25M, May ~1.21M, Jun ~1.15M):")
    print(df[df["date"].isin(["2022-04", "2022-05", "2022-06"])].to_string(index=False))


if __name__ == "__main__":
    main()