from pathlib import Path
import numpy as np
import pandas as pd

project = Path(__file__).resolve().parent.parent
processed = project / "data" / "processed"
employees = pd.read_csv(processed / "dim_employee.csv")
role_skill = pd.read_csv(processed / "fact_role_skill.csv")
learning = pd.read_csv(processed / "fact_learning.csv")

rng = np.random.default_rng(9)

# ---------- 1. One row per employee and required skill ----------
ratings = employees[["EmployeeID", "RoleID"]].merge(
    role_skill[["RoleID", "SkillID", "SkillName", "AILayer", "Importance"]], on="RoleID")

# ---------- 2. Starting level by role group (April) ----------
group = {
    "Bank Teller": "Frontline", "Customer Service Officer": "Frontline", "Loan Processing Clerk": "Frontline",
    "Relationship Manager": "Business", "Loan Officer": "Business", "Credit Analyst": "Business",
    "Branch or Finance Manager": "Business", "Financial Analyst": "Business", "Accountant": "Business",
    "Software Engineer": "Technology", "Systems Analyst": "Technology",
    "Data Scientist": "AI-critical", "ML Engineer": "AI-critical", "Cybersecurity Analyst": "AI-critical",
    "Model Risk Analyst": "AI-critical", "AI Compliance Officer": "AI-critical",
}
starting_level = {"Frontline": 1.3, "Business": 1.9, "Technology": 2.8, "AI-critical": 3.2}

role_name = employees.drop_duplicates("RoleID").set_index("RoleID")["RoleName"]
ratings["RoleGroup"] = ratings["RoleID"].map(role_name).map(group)

# Consistency: each person has one general AI strength that applies to all their skills.
person_strength = pd.Series(rng.normal(0, 0.5, len(employees)), index=employees["EmployeeID"])

level = (ratings["RoleGroup"].map(starting_level)
         + ratings["EmployeeID"].map(person_strength)
         + rng.normal(0, 0.6, len(ratings)))

# Built-in shortage: these two skills run about one level lower.
shortage = ratings["SkillName"].isin(["AI security", "Model validation"])
level = level - shortage * 1.0

ratings["April"] = level.round().clip(1, 5).astype(int)

# ---------- 3. Change by October ----------
completed = set(learning.loc[learning["Status"] == "Completed", "EmployeeID"])
did_course = ratings["EmployeeID"].isin(completed)
is_foundations = ratings["AILayer"] == "AI Foundations"

# The course targets Foundations skills: 45% of completers improve, against 20% of others.
# Other skills improve for 15% of people, whatever their training.
chance = np.where(is_foundations, np.where(did_course, 0.45, 0.20), 0.15)
improved = rng.random(len(ratings)) < chance
ratings["October"] = (ratings["April"] + improved).clip(upper=5)

# ---------- 4. Long format: one row per employee, skill, rater and date ----------
manager = ratings.melt(id_vars=["EmployeeID", "SkillID"], value_vars=["April", "October"],
                       var_name="Cycle", value_name="Proficiency")
manager["RaterType"] = "Manager"

# Self-ratings run about half a level higher than manager ratings.
self_rated = manager.copy()
self_rated["Proficiency"] = (self_rated["Proficiency"] + rng.normal(0.5, 0.6, len(self_rated))).round().clip(1, 5).astype(int)
self_rated["RaterType"] = "Self"

employee_skill = pd.concat([manager, self_rated], ignore_index=True)
employee_skill["RatingDate"] = employee_skill["Cycle"].map({"April": "2026-04-30", "October": "2026-10-31"})
employee_skill["IsSynthetic"] = True
employee_skill = employee_skill[["EmployeeID", "SkillID", "RaterType", "RatingDate", "Proficiency", "IsSynthetic"]]

# ---------- 5. Checks ----------
print("Employee-skill pairs:", len(ratings))
print("Rating rows:", len(employee_skill), "| expected", len(ratings) * 4)
print("Duplicate keys:", employee_skill.duplicated(["EmployeeID", "SkillID", "RaterType", "RatingDate"]).sum(), "| expected 0")
print("Levels outside 1-5:", (~employee_skill["Proficiency"].between(1, 5)).sum(), "| expected 0")
averages = employee_skill.groupby("RaterType")["Proficiency"].mean()
print("Average self minus manager:", round(averages["Self"] - averages["Manager"], 2), "| expected about 0.4-0.5")
employee_skill.to_csv(processed / "fact_employee_skill.csv", index=False)
print("Saved fact_employee_skill.csv")
