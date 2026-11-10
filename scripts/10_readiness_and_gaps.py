from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
processed = project / "data" / "processed"
employees = pd.read_csv(processed / "dim_employee.csv")
roles = pd.read_csv(processed / "dim_role.csv")
role_skill = pd.read_csv(processed / "fact_role_skill.csv")
ratings = pd.read_csv(processed / "fact_employee_skill.csv")

# Official reporting uses manager ratings only.
manager = ratings[ratings["RaterType"] == "Manager"]

# Attach each employee's role, then the requirement for that role and skill.
manager = manager.merge(employees[["EmployeeID", "RoleID"]], on="EmployeeID")
manager = manager.merge(role_skill[["RoleID", "SkillID", "SkillName", "AILayer", "RequiredProficiency", "Importance"]],
                        on=["RoleID", "SkillID"])

# ---------- 1. AI readiness: Level 2+ in all four Foundations skills ----------
target = round(len(employees) * 0.5)
foundations = manager[manager["AILayer"] == "AI Foundations"]
lowest = foundations.groupby(["RatingDate", "EmployeeID"])["Proficiency"].min()
ready = (lowest >= 2).groupby("RatingDate").agg(["sum", "mean"])
ready.columns = ["ReadyEmployees", "ReadinessRate"]
ready["ReadinessRate"] = (ready["ReadinessRate"] * 100).round(1)
ready["Target"] = target
ready["ShortOfTarget"] = target - ready["ReadyEmployees"]
print("AI readiness (manager-rated)")
print(ready.to_string())

# ---------- 2. Gaps in AI-critical roles (October) ----------
latest = manager[manager["RatingDate"] == manager["RatingDate"].max()].copy()
latest["Gap"] = (latest["RequiredProficiency"] - latest["Proficiency"]).clip(lower=0)
latest["MeetsRequirement"] = latest["Gap"] == 0

critical_ids = roles.loc[roles["IsAICritical"], "RoleID"]
core = latest[latest["RoleID"].isin(critical_ids) & (latest["Importance"] == "High") & (latest["RequiredProficiency"] == 4)]

skill_gaps = core.groupby("SkillName").agg(
    EmployeesRated=("EmployeeID", "nunique"),
    MeetingLevel4=("MeetsRequirement", "sum"),
    AverageGap=("Gap", "mean"),
)
skill_gaps["CoveragePct"] = (skill_gaps["MeetingLevel4"] / skill_gaps["EmployeesRated"] * 100).round(1)
skill_gaps["AverageGap"] = skill_gaps["AverageGap"].round(2)
print("\nCore AI skills in AI-critical roles, October (lowest coverage first)")
print(skill_gaps.sort_values("CoveragePct").to_string())

ready.to_csv(processed / "result_readiness.csv")
skill_gaps.to_csv(processed / "result_critical_skill_gaps.csv")
print("\nSaved result_readiness.csv and result_critical_skill_gaps.csv")
