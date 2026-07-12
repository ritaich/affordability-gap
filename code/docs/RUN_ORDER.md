# run order

its just for reference for rebuilding the project from scratch or refreshing parts of it. files are numbered roughly chronologically but a few load steps must precede the calculation steps, so the actual run order doesn't perfectly follow the numbering. I created this so i will always have them and i can access them fast 

## full rebuild from scratch

```bash
# week 2 — toronto data pipeline
python code/01_download_trreb.py              # downloads 72 trreb pdfs
python code/02_inspect_trreb.py               # peeks at one pdf format
python code/03_extract_trreb.py               # parses all pdfs to toronto_raw.csv
python code/04_diagnose_fail.py               # debugging (optional)
python code/05_debug_extract.py               # debugging (optional)
python code/06_patch_may_2022.py              # patches corrupted pdf
python code/07_validate_ee.py                 # validates against ee data

# week 3 — multi-city data
python code/10_inspect_crea.py                # inspects crea excel sheets
python code/11_load_crea_hpi.py               # toronto + vancouver from crea
python code/12_check_crea_vs_trreb.py         # cross-validation
python code/13_load_london.py                 # london from uk land registry
python code/14_load_newyork.py                # ny data from fred
python code/15_build_newyork.py               # converts case-shiller to dollars

# week 4 — predictors
python code/16_load_mortgage_rates.py         # mortgage rates: canada/uk/usa
python code/18_load_unemployment.py           # unemployment: canada/uk

# affordability indices + master dataset (depends on data above)
python code/08_calculate_median_multiple.py   # median multiple, all 4 cities
python code/17_calculate_mdsr.py              # mdsr, all 4 cities
python code/19_build_master_dataset.py        # combines everything

# week 4 — exploratory
python code/20_correlations.py                # per-city correlation matrix

# week 5 — regressions
python code/21_regression_simple.py           # mdsr ~ rate (per city)
python code/22_regression_full.py             # multivariate (uncorrected)
python code/23_regression_standardized.py     # standardized coefficients
python code/24_diagnostics.py                 # vif, b-p, d-w tests
python code/25_regression_corrected.py        # newey-west robust se
python code/27_regression_mm.py               # same model on median multiple

# visualizations
python code/09_chart_toronto_mm.py            # 4-city affordability over time
python code/26_chart_coefficients.py          # coefficient comparison chart
```

## fast refresh after data change

if the income or rate data changes, only these need to re-run:

```bash
python code/08_calculate_median_multiple.py
python code/17_calculate_mdsr.py
python code/19_build_master_dataset.py
python code/25_regression_corrected.py
python code/26_chart_coefficients.py
```

## just look at the outputs

```bash
open data/clean/master.csv
open visualizations/04_four_cities_median_multiple.html
open visualizations/05_rate_coefficient_by_city.html
```

## key data flow