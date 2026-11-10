from pathlib import Path
import numpy as np
import pandas as pd

project = Path(__file__).resolve().parent.parent
processed = project / "data" / "processed"
employees = pd.read_csv(processed / "dim_employee.csv")

rng = np.random.default_rng(8)
n = len(employees)

# Each employee gets one outcome for the AI Foundations course:
# 55% completed, 15% in progress, 30% not enrolled.
status = rng.choice(["Completed", "In progress", "Not enrolled"], size=n, p=[0.55, 0.15, 0.30])

learning = pd.DataFrame({
    "EmployeeID": employees["EmployeeID"],
    "CourseID": "C001",
    "CourseName": "AI Foundations",
    "Status": status,
})

# Only enrolled employees get a learning record.
learning = learning[learning["Status"] != "Not enrolled"].reset_index(drop=True)

# Completion dates fall between the two rating dates.
start = pd.Timestamp("2026-05-01")
days = rng.integers(0, 183, size=len(learning))
learning["CompletionDate"] = (start + pd.to_timedelta(days, unit="D")).where(learning["Status"] == "Completed")
learning["IsSynthetic"] = True

print(learning["Status"].value_counts().to_string())
print("Learning records:", len(learning))
print("Completion rate:", round((learning["Status"] == "Completed").sum() / n * 100, 1), "% | expected about 55")
print("Completed records with no date:", learning.loc[learning["Status"] == "Completed", "CompletionDate"].isna().sum(), "| expected 0")

learning.to_csv(processed / "fact_learning.csv", index=False)
print("Saved fact_learning.csv")
