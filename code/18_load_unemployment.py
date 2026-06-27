# i pull unemployment for all four cities from fred
# fred has unemployment series for both countries and metros
# new york is already downloaded, i just need to add canada uk

import pandas as pd
import requests
from pathlib import Path
from io import StringIO

base = Path(__file__).parent.parent
out_dir = base / "data/raw/fred"
out_dir.mkdir(parents=True, exist_ok=True)

# fred series for unemployment
# i use country/metro level where i can get monthly data
unemployment_series = {
    "LRHUTTTTCAM156S": "canada_unemployment",  # canada national, monthly seasonally adjusted
    "LRHUTTTTGBM156S": "uk_unemployment",      # uk national, monthly seasonally adjusted
    # nyurn already downloaded as ny_unemployment.csv (new york state)
}

start = "2018-01-01"
end   = "2025-01-01"

for series_id, label in unemployment_series.items():
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
    df = pd.read_csv(StringIO(r.text))
    print(f"ok, {len(df)} rows")

print("\ndone, all unemployment files now in:", out_dir)