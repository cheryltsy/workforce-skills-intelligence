from pathlib import Path
import numpy as np
import pandas as pd

project = Path(__file__).resolve().parent.parent
roles = pd.read_csv(project / "data" / "processed" / "dim_role.csv")

rng = np.random.default_rng(42)

# Create one row per position, so every role gets its exact approved count.
employees = roles.loc[roles.index.repeat(roles["PositionCount"]), ["RoleID", "RoleName", "JobFamily"]]

# Shuffle the rows so employee IDs are not grouped by role.
employees = employees.sample(frac=1, random_state=42).reset_index(drop=True)

n = len(employees)
employees.insert(0, "EmployeeID", [f"E{i:05d}" for i in range(1, n + 1)])

days_employed = rng.integers(30, 5475, size=n)
employees["HireDate"] = pd.Timestamp("2026-10-31") - pd.to_timedelta(days_employed, unit="D")
employees["IsSynthetic"] = True

counts = employees["RoleID"].value_counts().sort_index()
expected = roles.set_index("RoleID")["PositionCount"].sort_index()

print(employees.head(5).to_string(index=False))
print("Employees:", n, "| expected 6124")
print("Unique IDs:", employees["EmployeeID"].is_unique, "| expected True")
print("Role counts match:", counts.equals(expected), "| expected True")

employees.to_csv(project / "data" / "processed" / "dim_employee.csv", index=False)
print("Saved dim_employee.csv")
