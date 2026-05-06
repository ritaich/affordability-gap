# i pull all new york data from fred (federal reserve st. louis)
# fred has free csv downloads with stable urls
# i grab prices, income, mortgage rate, unemployment all at once
import pandas as pd
import requests
from pathlib import Path
from io import StringIO
base = Path(__file__).parent.parent
out_dir = base / "data/raw/fred"
out_dir.mkdir(parents=True, exist_ok=True)

# fred series i want, with the project window dates baked into the url
series = {
    "NYXRSA":             "ny_caseshiller_index",   # ny home price index
    "MHINY36000A052NCEN": "ny_median_income",        # ny state median income (annual)
    "MORTGAGE30US":       "us_mortgage_30y",         # 30-year fixed mortgage rate
    "NYURN":              "ny_unemployment",         # ny state unemployment (monthly)
}

start = "2018-01-01"  # i grab a year of buffer so monthly interpolation works
end   = "2025-01-01"

for series_id, label in series.items():
    url = (f"https://fred.stlouisfed.org/graph/fredgraph.csv"
           f"?id={series_id}"
           f"&cosd={start}&coed={end}")
    print(f"  downloading {series_id} ({label})... ", end="")
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        print(f"FAILED (http {r.status_code})")
        continue
    out_path = out_dir / f"{label}.csv"
    out_path.write_text(r.text)
    # quick check of what we got
    df = pd.read_csv(StringIO(r.text))
    print(f"ok, {len(df)} rows, columns {list(df.columns)}")

print("\ndone. files in:", out_dir)