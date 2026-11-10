from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
processed = project / "data" / "processed"
roles = pd.read_csv(processed / "dim_role.csv")

# ---------- 1. The skill library: 20 skills in three layers ----------
foundations = ["AI concepts and limits", "Using AI tools", "Checking AI output", "Responsible AI and data use"]
applied = ["AI-enabled job tasks", "AI workflow redesign"]

# Specialist skills for the five AI-critical roles, in this order:
# Data Scientist, ML Engineer, Cybersecurity Analyst, Model Risk Analyst, AI Compliance Officer
# C = core (Level 4, High importance), S = supporting (Level 2, Medium), - = not required
critical_roles = ["Data Scientist", "ML Engineer", "Cybersecurity Analyst", "Model Risk Analyst", "AI Compliance Officer"]
specialist = {
    "Machine learning":                ["C", "C", "-", "S", "-"],
    "Statistical modelling":           ["C", "S", "-", "C", "-"],
    "Model evaluation":                ["C", "C", "-", "C", "S"],
    "Generative AI development":       ["C", "C", "S", "S", "S"],
    "Data preparation":                ["C", "C", "-", "S", "-"],
    "Python programming":              ["C", "C", "S", "C", "-"],
    "Data pipeline engineering":       ["S", "C", "-", "-", "-"],
    "Model deployment and monitoring": ["S", "C", "-", "S", "-"],
    "AI security":                     ["S", "C", "C", "S", "S"],
    "Data protection and privacy":     ["S", "S", "C", "S", "C"],
    "Model validation":                ["S", "-", "-", "C", "S"],
    "AI risk assessment":              ["S", "S", "S", "C", "C"],
    "AI regulatory compliance":        ["-", "-", "S", "C", "C"],
    "AI explainability":               ["C", "S", "-", "C", "C"],
}

skill_list = ([(s, "AI Foundations") for s in foundations]
              + [(s, "Applied AI") for s in applied]
              + [(s, "Specialist AI") for s in specialist])
skills = pd.DataFrame(skill_list, columns=["SkillName", "AILayer"])
skills.insert(0, "SkillID", [f"SK{i:03d}" for i in range(1, len(skills) + 1)])
skills["ValidationStatus"] = "Suggested"

# ---------- 2. Role requirements: one row per role and skill ----------
rows = []

def require(role, skill, level, importance):
    rows.append({"RoleName": role, "SkillName": skill, "RequiredProficiency": level, "Importance": importance})

# Every role needs all four Foundations skills.
level_3_foundations = ["Software Engineer", "Systems Analyst"] + critical_roles
for role in roles["RoleName"]:
    level = 3 if role in level_3_foundations else 2
    for skill in foundations:
        require(role, skill, level, "High" if skill == "Responsible AI and data use" else "Medium")

# Applied AI: using AI in daily work.
applied_level = {
    "Bank Teller": 2, "Customer Service Officer": 2, "Loan Processing Clerk": 2,
    "Relationship Manager": 3, "Loan Officer": 3, "Credit Analyst": 3,
    "Branch or Finance Manager": 3, "Financial Analyst": 3, "Accountant": 3,
    "Software Engineer": 3, "Systems Analyst": 3,
    "Cybersecurity Analyst": 3, "Model Risk Analyst": 3, "AI Compliance Officer": 3,
}
for role, level in applied_level.items():
    require(role, "AI-enabled job tasks", level, "Medium")
for role in ["Data Scientist", "ML Engineer"]:
    require(role, "AI-enabled job tasks", 4, "High")
for role in ["Data Scientist", "ML Engineer", "Software Engineer", "Systems Analyst"]:
    require(role, "AI workflow redesign", 3, "Medium")

# Specialist AI for the five AI-critical roles.
for skill, marks in specialist.items():
    for role, mark in zip(critical_roles, marks):
        if mark == "C":
            require(role, skill, 4, "High")
        elif mark == "S":
            require(role, skill, 2, "Medium")

# Specialist AI for other roles.
require("Software Engineer", "Python programming", 3, "High")
require("Software Engineer", "Model deployment and monitoring", 2, "Medium")
require("Software Engineer", "AI security", 2, "Medium")
require("Systems Analyst", "Data preparation", 2, "Medium")
require("Systems Analyst", "AI security", 2, "Medium")
require("Credit Analyst", "Statistical modelling", 2, "Medium")
require("Credit Analyst", "Model evaluation", 2, "Medium")
require("Financial Analyst", "Data preparation", 2, "Medium")

role_skill = pd.DataFrame(rows)
role_skill = role_skill.merge(roles[["RoleID", "RoleName"]], on="RoleName", how="left")
role_skill = role_skill.merge(skills[["SkillID", "SkillName", "AILayer"]], on="SkillName", how="left")
role_skill["ValidationStatus"] = "Suggested"
role_skill = role_skill[["RoleID", "RoleName", "SkillID", "SkillName", "AILayer",
                         "RequiredProficiency", "Importance", "ValidationStatus"]]

# ---------- 3. Checks ----------
print("Skills:", len(skills), "| expected 20")
print("Role-skill rows:", len(role_skill))
print("Missing IDs:", role_skill[["RoleID", "SkillID"]].isna().sum().sum(), "| expected 0")
print("Duplicate role-skill pairs:", role_skill.duplicated(["RoleID", "SkillID"]).sum(), "| expected 0")

# Apply the AI-critical rule: an Applied or Specialist skill at Level 4 with High importance.
rule = role_skill[(role_skill["AILayer"] != "AI Foundations")
                  & (role_skill["RequiredProficiency"] >= 4)
                  & (role_skill["Importance"] == "High")]
rule_roles = set(rule["RoleName"])
approved_roles = set(roles.loc[roles["IsAICritical"], "RoleName"])
print("Rule matches approved AI-critical roles:", rule_roles == approved_roles, "| expected True")
print("AI-critical positions:", roles.loc[roles["RoleName"].isin(rule_roles), "PositionCount"].sum(), "| expected 342")

summary = role_skill.pivot_table(index="RoleName", columns="AILayer", values="SkillID", aggfunc="count", fill_value=0)
print(summary.reindex(roles["RoleName"]).to_string())

skills.to_csv(processed / "dim_skill.csv", index=False)
role_skill.to_csv(processed / "fact_role_skill.csv", index=False)
print("Saved dim_skill.csv and fact_role_skill.csv")
