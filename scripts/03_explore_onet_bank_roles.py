"""Step 3: Check what O*NET can and cannot tell us about AI-related bank roles.

Compares five occupations, checks which have skill ratings,
and searches O*NET's software data for AI tools.
Run 01_load_onet.py first.
"""
from pathlib import Path
import pandas as pd
pd.set_option("display.max_colwidth", None)

project = Path(__file__).resolve().parent.parent
data_folder = project / "data" / "raw" / "onet" / "31.0"
files = {path.name: path for path in data_folder.rglob("*.csv")}

def load(name):
    """Read an O*NET file as text, so occupation codes stay exactly as published."""
    return pd.read_csv(files[name], dtype=str, keep_default_na=False, encoding="utf-8-sig")

# The five AI-related occupations, with short labels for the bank roles they map to.
chosen = {
    "15-2051.00": "Data Scientist",
    "15-1252.00": "ML Engineer",
    "15-1212.00": "Cybersecurity",
    "13-2054.00": "Model Risk",
    "13-1041.00": "AI Compliance",
}

# ---------- 1. Compare skill importance across the roles ----------
skills = load("transferable_skills.csv")
importance = skills[skills["O*NET-SOC Code"].isin(chosen) & (skills["Scale ID"] == "IM")].copy()
importance["Data Value"] = pd.to_numeric(importance["Data Value"])
importance["Role"] = importance["O*NET-SOC Code"].map(chosen)

comparison = importance.pivot(index="Element Name", columns="Role", values="Data Value")
comparison = comparison.sort_values("Data Scientist", ascending=False)
print("Skill importance by role (1-5):")
print(comparison.to_string())

# ---------- 2. Check which roles have skill ratings ----------
rated = set(importance["Role"])
missing = [role for role in chosen.values() if role not in rated]
print("\nRoles with no O*NET skill ratings:", missing)

# ---------- 3. Use tasks where ratings are missing ----------
tasks = load("task_statements.csv")
risk_tasks = tasks[tasks["O*NET-SOC Code"] == "13-2054.00"]
print("\nFinancial Risk Specialist tasks:", len(risk_tasks))
print(risk_tasks["Task"].head(12).to_string(index=False))

# ---------- 4. Search software data for AI tools ----------
software = load("software_skills.csv")
ai_terms = "machine learning|tensorflow|pytorch|scikit|deep learning|artificial intelligence|generative|openai"
ai_tools = software[software["O*NET-SOC Code"].isin(chosen)
                    & software["Workplace Example"].str.contains(ai_terms, case=False)].copy()
ai_tools["Role"] = ai_tools["O*NET-SOC Code"].map(chosen)
print("\nAI tools linked to these roles:")
print(ai_tools[["Role", "Workplace Example", "Hot Technology", "In Demand"]].to_string(index=False))

# ---------- 5. Conclusion ----------
print("\nFinding: O*NET lists broad skills and some AI tools, but no specific")
print("AI skills such as model validation. These were defined for this project.")
