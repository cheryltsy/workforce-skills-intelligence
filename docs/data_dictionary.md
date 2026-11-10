# Data Dictionary

All tables are in `data/processed/`. Tables starting `dim_` describe things (roles, skills, employees). Tables starting `fact_` record events or requirements and link to the dimension tables by ID.

**Synthetic data:** `dim_employee`, `fact_learning` and `fact_employee_skill` are generated in Python. They contain no real people.

## How the tables connect

```text
dim_role ──< fact_role_skill >── dim_skill
   │                                 │
   └──< dim_employee                 │
             │                       │
             ├──< fact_learning      │
             └──< fact_employee_skill >┘
```

`──<` means one-to-many: for example, one role has many employees.

The **gap** is calculated by matching an employee's rating in `fact_employee_skill` with the requirement for their role and that skill in `fact_role_skill`.

---

## dim_role

One row per role. Built by `05_build_roles.py`.

| Column | Type | Description |
| --- | --- | --- |
| RoleID | Text | Unique role ID, such as `R01` |
| JobFamily | Text | One of five job families |
| RoleName | Text | Bank role title, such as `Data Scientist` |
| OCC_CODE | Text | Official US occupation code (SOC), such as `15-2051` |
| IsAICritical | True/False | Whether the role needs an Applied or Specialist skill at Level 4 with High importance |
| OfficialOccupation | Text | Official occupation title from BLS |
| PositionCount | Number | Positions in the 10,000-person bank, from BLS banking proportions |

**Note:** ML Engineer (40) and Software Engineer (228) share code `15-1252`. The split is an assumption.

## dim_skill

One row per skill. Built by `07_build_role_skills.py`.

| Column | Type | Description |
| --- | --- | --- |
| SkillID | Text | Unique skill ID, such as `SK001` |
| SkillName | Text | Skill name |
| AILayer | Text | `AI Foundations`, `Applied AI` or `Specialist AI` |
| ValidationStatus | Text | `Suggested`: a design assumption not yet validated by experts |

## dim_employee

One row per employee. Built by `06_generate_employees.py`. **Synthetic.**

| Column | Type | Description |
| --- | --- | --- |
| EmployeeID | Text | Unique fictional ID, such as `E00001` |
| RoleID | Text | Links to `dim_role` |
| RoleName | Text | Copied from `dim_role` for readability |
| JobFamily | Text | Copied from `dim_role` for readability |
| HireDate | Date | Simulated, spread evenly over about 15 years. Not used in analysis |
| IsSynthetic | True/False | Always `True` |

## fact_role_skill

One row per role and required skill. Built by `07_build_role_skills.py`. This is the **required** side of the gap.

| Column | Type | Description |
| --- | --- | --- |
| RoleID | Text | Links to `dim_role` |
| RoleName | Text | Copied for readability |
| SkillID | Text | Links to `dim_skill` |
| SkillName | Text | Copied for readability |
| AILayer | Text | Copied for readability |
| RequiredProficiency | Number, 1–5 | Level the role needs |
| Importance | Text | `High` or `Medium`, set by role |
| ValidationStatus | Text | `Suggested` |

## fact_learning

One row per enrolled employee and course. Built by `08_generate_learning.py`. **Synthetic.**

| Column | Type | Description |
| --- | --- | --- |
| EmployeeID | Text | Links to `dim_employee` |
| CourseID | Text | `C001` |
| CourseName | Text | `AI Foundations` |
| Status | Text | `Completed` or `In progress`. Employees not enrolled have no row |
| CompletionDate | Date | Between 1 May and 31 October 2026. Blank if in progress |
| IsSynthetic | True/False | Always `True` |

## fact_employee_skill

One row per employee, skill, rater and date. Built by `09_generate_ratings.py`. This is the **assessed** side of the gap. **Synthetic.**

| Column | Type | Description |
| --- | --- | --- |
| EmployeeID | Text | Links to `dim_employee` |
| SkillID | Text | Links to `dim_skill`. Only skills the employee's role requires |
| RaterType | Text | `Self` or `Manager`. Never averaged |
| RatingDate | Date | `2026-04-30` or `2026-10-31` |
| Proficiency | Number, 1–5 | Rated level |
| IsSynthetic | True/False | Always `True` |

## Supporting and result files

| File | Built by | Contents |
| --- | --- | --- |
| `bls_banking_occupations.csv` | `04_explore_bls.py` | BLS banking occupations with `PER_10000`, each occupation's jobs per 10,000 |
| `result_readiness.csv` | `10_readiness_and_gaps.py` | Ready employees, readiness rate and distance from target, by rating date |
| `result_critical_skill_gaps.csv` | `10_readiness_and_gaps.py` | Coverage and average gap for core skills in AI-critical roles, October 2026 |
