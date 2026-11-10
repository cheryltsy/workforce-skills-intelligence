from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
bls = pd.read_csv(project / "data" / "processed" / "bls_banking_occupations.csv", dtype={"OCC_CODE": str})

role_map = [
    ("Customer Operations", "Bank Teller", "43-3071", False),
    ("Customer Operations", "Relationship Manager", "41-3031", False),
    ("Customer Operations", "Loan Officer", "13-2072", False),
    ("Customer Operations", "Customer Service Officer", "43-4051", False),
    ("Customer Operations", "Loan Processing Clerk", "43-4131", False),
    ("Technology and Data", "Software Engineer", "15-1252", False),
    ("Technology and Data", "Systems Analyst", "15-1211", False),
    ("Technology and Data", "Data Scientist", "15-2051", True),
    ("Technology and Data", "ML Engineer", "15-1252", True),
    ("Cybersecurity", "Cybersecurity Analyst", "15-1212", True),
    ("Risk and Compliance", "Credit Analyst", "13-2041", False),
    ("Risk and Compliance", "Model Risk Analyst", "13-2054", True),
    ("Risk and Compliance", "AI Compliance Officer", "13-1041", True),
    ("Finance", "Branch or Finance Manager", "11-3031", False),
    ("Finance", "Financial Analyst", "13-2051", False),
    ("Finance", "Accountant", "13-2011", False),
]
roles = pd.DataFrame(role_map, columns=["JobFamily", "RoleName", "OCC_CODE", "IsAICritical"])

roles = roles.merge(bls[["OCC_CODE", "OCC_TITLE", "PER_10000"]], on="OCC_CODE", how="left")
roles["PositionCount"] = roles["PER_10000"].astype(int)

# Assumption: 40 of the 268 Software Developer positions are ML Engineers.
roles.loc[roles["RoleName"] == "ML Engineer", "PositionCount"] = 40
roles.loc[roles["RoleName"] == "Software Engineer", "PositionCount"] = 228

roles.insert(0, "RoleID", [f"R{i:02d}" for i in range(1, len(roles) + 1)])
roles = roles.drop(columns="PER_10000").rename(columns={"OCC_TITLE": "OfficialOccupation"})

total = roles["PositionCount"].sum()
critical = roles.loc[roles["IsAICritical"], "PositionCount"].sum()
print(roles[["RoleID", "JobFamily", "RoleName", "PositionCount", "IsAICritical"]].to_string(index=False))
print("In-scope positions:", total, "| expected 6124")
print("AI-critical positions:", critical, "| expected 342")

roles.to_csv(project / "data" / "processed" / "dim_role.csv", index=False)
print("Saved dim_role.csv")
