import importlib.util
import subprocess
import sys
from pathlib import Path

if importlib.util.find_spec("openpyxl") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl"], check=True)

import pandas as pd

project = Path(__file__).resolve().parent.parent
file = project / "data" / "raw" / "bls" / "oesm25in4" / "nat3d_M2025_dl.xlsx"

bls = pd.read_excel(file, dtype=str)
bls.columns = bls.columns.str.upper()
print("Columns:", bls.columns.tolist())

banking = bls[bls["NAICS"] == "522000"].copy()
print("Banking rows:", len(banking))

banking["TOT_EMP"] = pd.to_numeric(banking["TOT_EMP"], errors="coerce")
total = banking.loc[banking["OCC_CODE"] == "00-0000", "TOT_EMP"].iloc[0]
print("Total banking employment:", f"{total:,.0f}")

jobs = banking[banking["O_GROUP"] == "detailed"].copy()
jobs["PER_10000"] = (jobs["TOT_EMP"] / total * 10000).round(0)
jobs = jobs.sort_values("TOT_EMP", ascending=False)
print(jobs[["OCC_CODE", "OCC_TITLE", "TOT_EMP", "PER_10000"]].head(25).to_string(index=False))

chosen = ["15-2051", "15-1252", "15-1212", "13-2054", "13-1041"]
print(jobs[jobs["OCC_CODE"].isin(chosen)][["OCC_CODE", "OCC_TITLE", "TOT_EMP", "PER_10000"]].to_string(index=False))

(project / "data" / "processed").mkdir(parents=True, exist_ok=True)
jobs.to_csv(project / "data" / "processed" / "bls_banking_occupations.csv", index=False)
print("Saved", len(jobs), "occupations")
