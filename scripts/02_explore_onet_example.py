"""Step 2: Trace one occupation from its tasks to its rated skills.

This worked example proves the method before applying it to bank roles.
Occupation: Aircraft Mechanics and Service Technicians (49-3011.00).
Run 01_load_onet.py first.
"""
from pathlib import Path
import pandas as pd

project = Path(__file__).resolve().parent.parent
data_folder = project / "data" / "raw" / "onet" / "31.0"
files = {path.name: path for path in data_folder.rglob("*.csv")}

def load(name):
    """Read an O*NET file as text, so codes such as 49-3011.00 stay exactly as published."""
    return pd.read_csv(files[name], dtype=str, keep_default_na=False, encoding="utf-8-sig")

code = "49-3011.00"

# ---------- 1. Skill ratings: importance and level ----------
skills = load("transferable_skills.csv")
skills = skills[skills["O*NET-SOC Code"] == code].copy()
skills["Data Value"] = pd.to_numeric(skills["Data Value"])
ratings = skills.pivot(index="Element Name", columns="Scale Name", values="Data Value")

scales = load("scales_reference.csv")
print("Rating scales:")
print(scales[scales["Scale ID"].isin(["IM", "LV"])].to_string(index=False))

# ---------- 2. Tasks ----------
tasks = load("task_statements.csv")
job_tasks = tasks[tasks["O*NET-SOC Code"] == code]
print("\nTasks for this occupation:", len(job_tasks))

# ---------- 3. Link tasks to skills ----------
# Task -> detailed work activity -> general work activity -> skill
task_links = load("tasks_to_dwas.csv")
activity_links = load("gwas_to_iwas_to_dwas.csv").drop(columns="DWA Element Name")
skill_links = load("transferable_skills_to_work_activities.csv")

chain = task_links[task_links["O*NET-SOC Code"] == code]
chain = chain.merge(activity_links, on="DWA Element ID", how="left")
chain = chain.merge(skill_links, left_on="GWA Element ID", right_on="Work Activities Element ID", how="left")
print("Tasks linked:", chain["Task ID"].nunique(), "of", len(job_tasks))

# Count unique tasks per skill. Counting rows would inflate the result,
# because one task can link to several activities and skills.
linked_tasks = chain.groupby("Transferable Skills Element Name")["Task ID"].nunique().rename("Linked tasks")

profile = ratings.join(linked_tasks).fillna({"Linked tasks": 0})
profile = profile.sort_values("Importance", ascending=False)
print("\nSkill profile (highest importance first):")
print(profile.to_string())

output = project / "outputs" / "onet_example"
output.mkdir(parents=True, exist_ok=True)
profile.to_csv(output / "aircraft_mechanic_skill_profile.csv")
chain.to_csv(output / "aircraft_mechanic_task_skill_chain.csv", index=False)
print("\nSaved to", output)
