"""Step 1: Unzip the O*NET 31.0 database and check it is complete.

Before running: download db_31_0_csv.zip from https://www.onetcenter.org/database.html
and put it in the project folder, next to README.md.
"""
import zipfile
from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
zip_file = project / "db_31_0_csv.zip"
data_folder = project / "data" / "raw" / "onet" / "31.0"

if not zip_file.exists():
    raise FileNotFoundError(f"Download db_31_0_csv.zip and save it here: {zip_file}")

# Unzip every O*NET file into the raw data folder.
with zipfile.ZipFile(zip_file) as archive:
    archive.extractall(data_folder)

# Find every CSV, wherever it sits inside the unzipped folder.
files = {path.name: path for path in data_folder.rglob("*.csv")}
print("CSV files found:", len(files))

# Compare key files with the row counts O*NET publishes for release 31.0.
expected = {
    "occupation_data.csv": 1016,
    "essential_skills.csv": 18200,
    "transferable_skills.csv": 45500,
    "task_statements.csv": 18838,
    "software_skills.csv": 31821,
}

all_match = True
for name, target in expected.items():
    table = pd.read_csv(files[name], dtype=str, keep_default_na=False, encoding="utf-8-sig")
    match = len(table) == target
    all_match = all_match and match
    print(f"{name}: {len(table):,} rows | expected {target:,} | {'OK' if match else 'CHECK'}")

print("All row counts match:", all_match)
