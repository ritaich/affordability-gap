# i build new york's monthly price series and merge with income
# case-shiller is an index, so i convert to dollars using a 2024 anchor
# from zillow research (~$640k median for nyc metro)
import pandas as pd
from pathlib import Path
base = Path(__file__).parent.parent
fred_dir = base / "data/raw/fred"
out_path = base / "data/clean/newyork_prices.csv"

# anchor: nyc metro median sale price, jan 2024 ≈ $640,000 (zillow research)
# i use this to convert the case-shiller index into dollar values
anchor_date = "2024-01-01"
anchor_price_usd = 640_000

# load price index
cs = pd.read_csv(fred_dir / "ny_caseshiller_index.csv")
cs.columns = ["date", "cs_index"]
cs["date"] = pd.to_datetime(cs["date"])

# scale index to dollars using the anchor
cs_anchor = cs.loc[cs["date"] == anchor_date, "cs_index"].iloc[0]
print(f"case-shiller index at {anchor_date}: {cs_anchor:.2f}")
print(f"anchoring to ${anchor_price_usd:,} → scale factor = {anchor_price_usd / cs_anchor:.2f}")

cs["price_local"] = cs["cs_index"] * (anchor_price_usd / cs_anchor)
cs["city"] = "New York"
cs["currency"] = "USD"
cs["hpi"] = cs["cs_index"]  # case-shiller IS an hpi

# slice to project window (jan 2019 - dec 2024)
cs["yymm"] = cs["date"].dt.strftime("%Y-%m")
cs = cs[(cs["yymm"] >= "2019-01") & (cs["yymm"] <= "2024-12")].copy()
cs["date"] = cs["yymm"]
cs = cs[["city", "date", "price_local", "currency", "hpi"]]

print(f"\nrows: {len(cs)}")
print(f"price range: ${cs['price_local'].min():,.0f} ({cs.loc[cs['price_local'].idxmin(), 'date']})"
      f" to ${cs['price_local'].max():,.0f} ({cs.loc[cs['price_local'].idxmax(), 'date']})")

out_path.parent.mkdir(parents=True, exist_ok=True)
cs.to_csv(out_path, index=False)
print(f"saved to {out_path}")