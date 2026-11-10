"""Stage 1b: prove the downloaded O*NET data matches its published documentation.

A file that loads is not a file that is correct. These checks compare your copy
with the O*NET 31.0 data dictionary and test the relationships later stages need.

Usage (run from the project root):  python scripts/02_verify_onet.py
Exit code 0 means every check passed. Exit code 1 means at least one failed.
"""

import sys
from pathlib import Path

import pandas as pd

ONET_VERSION = "31.0"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "onet" / ONET_VERSION
REPORT_PATH = PROJECT_ROOT / "outputs" / "stage1_onet_validation.csv"

# Published row counts from the O*NET 31.0 database page.
EXPECTED_ROWS = {
    "occupation_data.csv": 1_016,
    "essential_skills.csv": 18_200,
    "transferable_skills.csv": 45_500,
    "knowledge.csv": 60_060,
    "software_skills.csv": 31_821,
    "task_statements.csv": 18_838,
    "work_activities.csv": 74_702,
    "tasks_to_dwas.csv": 24_087,
    "gwas_to_iwas_to_dwas.csv": 2_087,
    "content_model_reference.csv": 3_006,
    "scales_reference.csv": 33,
    "level_scale_anchors.csv": 483,
}

# Published rating facts: 910 occupations, 2 scales, and 10 or 25 skill elements.
RATED_SKILL_FILES = {"essential_skills.csv": 10, "transferable_skills.csv": 25}
RATED_COLUMNS = ["O*NET-SOC Code", "Element ID", "Scale ID", "Data Value",
                 "Recommend Suppress", "Not Relevant"]

results: list[dict] = []


def record(check: str, passed: bool, detail: str) -> None:
    """Store and print one result, so every check is reported the same way."""
    results.append({"check": check, "status": "PASS" if passed else "FAIL", "detail": detail})
    print(f"[{'PASS' if passed else 'FAIL'}] {check}: {detail}")


def load(file_name: str) -> pd.DataFrame | None:
    """Load a CSV as text so pandas cannot alter identifiers or guess at blanks.

    dtype=str keeps codes such as 49-3011.00 exactly as published.
    keep_default_na=False stops pandas turning text like "NA" into missing data.
    utf-8-sig quietly removes an invisible marker some CSV files begin with.
    """
    path = RAW_DIR / file_name
    if not path.is_file():
        record(f"{file_name} exists", False, "file not found")
        return None
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def check_rated_file(name: str, expected_elements: int, valid_codes: set[str]) -> None:
    """Check a skills ratings file: columns, grain, coverage and links."""
    table = load(name)
    if table is None:
        return

    missing = [column for column in RATED_COLUMNS if column not in table.columns]
    record(f"{name} columns", not missing, f"missing: {missing}" if missing else "all present")
    if missing:
        return

    # Grain: one row must mean one occupation x one skill x one scale.
    grain = ["O*NET-SOC Code", "Element ID", "Scale ID"]
    duplicates = int(table.duplicated(subset=grain).sum())
    record(f"{name} grain", duplicates == 0, f"{duplicates:,} duplicate keys")

    occupations = table["O*NET-SOC Code"].nunique()
    elements = table["Element ID"].nunique()
    scales = sorted(table["Scale ID"].unique())
    record(f"{name} occupations", occupations == 910, f"{occupations} (expected 910)")
    record(f"{name} elements", elements == expected_elements,
           f"{elements} (expected {expected_elements})")
    record(f"{name} scales", len(scales) == 2, f"{scales}")

    # Foreign key: a rating that points at an unknown occupation cannot be joined.
    orphans = set(table["O*NET-SOC Code"]) - valid_codes
    record(f"{name} occupation links", not orphans, f"{len(orphans)} unknown codes")

    # Do not assume the rating range. Measure it and show it.
    values = pd.to_numeric(table["Data Value"], errors="coerce")
    unreadable = int(values.isna().sum())
    record(f"{name} numeric ratings", unreadable == 0, f"{unreadable:,} unreadable values")
    for scale, group in values.groupby(table["Scale ID"]):
        print(f"       Scale {scale}: min {group.min():.2f}, max {group.max():.2f}")

    # These flags are O*NET quality signals. Count them now and decide on them later.
    for flag in ["Recommend Suppress", "Not Relevant"]:
        print(f"       {flag} = Y: {(table[flag] == 'Y').sum():,} rows")


def main() -> int:
    if not RAW_DIR.is_dir():
        print(f"ERROR: {RAW_DIR} not found. Run scripts/01_download_onet.py first.")
        return 1

    record("manifest exists", (RAW_DIR / "manifest.json").is_file(), "provenance record")

    for file_name, expected in EXPECTED_ROWS.items():
        table = load(file_name)
        if table is not None:
            record(f"{file_name} rows", len(table) == expected,
                   f"{len(table):,} (expected {expected:,})")

    occupations = load("occupation_data.csv")
    if occupations is None or "O*NET-SOC Code" not in occupations.columns:
        record("occupation key", False, "cannot read O*NET-SOC Code from occupation_data.csv")
    else:
        codes = occupations["O*NET-SOC Code"]
        record("occupation key unique", codes.is_unique, f"{codes.nunique():,} unique codes")
        for file_name, expected_elements in RATED_SKILL_FILES.items():
            check_rated_file(file_name, expected_elements, set(codes))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(REPORT_PATH, index=False)

    failed = sum(result["status"] == "FAIL" for result in results)
    print(f"\n{len(results) - failed} passed, {failed} failed. Report: {REPORT_PATH}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
