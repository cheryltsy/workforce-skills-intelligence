# Do We Have Enough AI Skills?

**A Workforce Skills Intelligence model for a fictional bank, built with O\*NET, US labour market data and Python.**

📖 Read the full write-up on Medium: https://medium.com/@cheryltansy/do-we-have-enough-ai-skills-building-a-workforce-skills-intelligence-model-for-a-bank-1c12e5f3ebda

> All employee, skill rating and learning data in this repository is \*\*synthetic\*\*. No employer or real employee data was used.

\---

## The problem

Most organisations say AI skills are a priority, but when leaders ask *"Do we have enough AI skills?"*, HR teams can often only report course completions. That answer falls short for three reasons:

* **"AI skills" is undefined**, so nothing can be counted consistently.
* **"Enough" has no target**, so no one can say whether the number is good or bad.
* **Training is not capability.** Finishing a course does not prove someone can use AI safely at work.

**Business question:**

> Are we building the AI capability the business needs, in the right people and at the right level, and is our investment working?

## Context

A fictional **bank with digital ambitions** and **10,000 employees**. The analysis covers **6,124 in-scope employees in 16 roles across five job families**: Customer Operations, Technology and Data, Cybersecurity, Risk and Compliance, and Finance.

Role sizes follow real US banking employment proportions, so most employees are frontline staff and only a small group are AI specialists.

## Key definitions

**Layers and levels answer different questions.**

||Layer|Level|
|-|-|-|
|Question|**Which** AI skills does a role need?|**How well** does a person perform each skill?|
|Set by|The role|The person's assessed proficiency|

**Three layers, 20 AI skills:**

|Layer|Who needs it|Skills|
|-|-|-|
|AI Foundations|Every role|AI concepts and limits, using AI tools, checking AI output, responsible AI and data use|
|Applied AI|Roles using AI daily|AI-enabled job tasks, AI workflow redesign|
|Specialist AI|Technical, cyber and specialist risk roles|14 skills, such as machine learning, AI security and model validation|

**Five proficiency levels:** 1 Awareness, 2 Developing, 3 Proficient, 4 Advanced, 5 Expert.

**Two targets:**

* **Breadth:** 50% of in-scope employees (3,062 people) have basic AI capability, meaning Level 2+ in **all four** Foundations skills.
* **Depth:** AI-critical roles reach Level 4 in their core AI skills. A role is AI-critical if it needs an Applied or Specialist skill at Level 4 with High importance. Five roles qualify, covering 342 positions.

**Gap** = required level − manager-rated level, with surpluses set to zero. Self and manager ratings are stored separately and never averaged.

## Approach and key decisions

1. **Started with public job data, then found its limits.** O\*NET traced one occupation from tasks to rated skills, but it has no specific AI skills such as model validation. I defined those myself and labelled them as design assumptions.
2. **Separated capabilities, skills and roles.** AI is a capability across many roles, not a job family.
3. **Let the leadership question define "critical".** An early three-test classification was replaced with measurable breadth and depth targets.
4. **Grouped AI skills into three layers**, in line with tiered approaches used by Singapore organisations such as DBS, OCBC, UOB and the Public Service.
5. **Replaced estimated headcounts with official proportions**, which cut AI-critical positions from an estimated 1,050 to 342.
6. **Kept self and manager ratings separate**, because the difference between them is useful information.

## Data sources

|Data|Source|Type|
|-|-|-|
|Occupations, tasks, broad skills|[O\*NET 31.0 Database](https://www.onetcenter.org/database.html)|Public, CC BY 4.0|
|Role sizes|[BLS Occupational Employment and Wage Statistics, May 2025](https://www.bls.gov/oes/2025/may/oessrci.htm), banking and credit (NAICS 522000)|Public|
|AI skills and role requirements|My design, informed by O\*NET tasks and tools|Assumption, needs expert validation|
|Employees, ratings, learning records|Generated in Python with documented rules and fixed seeds|Synthetic|

Raw O\*NET and BLS files are not stored here. See *How to run* to download them.

## Data model

Requirements and employee ratings are kept in separate tables. See [docs/data\_dictionary.md](docs/data_dictionary.md) for every column.

|Table|One row per|Rows|
|-|-|-:|
|`dim\_role`|Role|16|
|`dim\_skill`|Skill|20|
|`dim\_employee`|Employee|6,124|
|`fact\_role\_skill`|Role × skill|144|
|`fact\_learning`|Enrolled employee × course|4,278|
|`fact\_employee\_skill`|Employee × skill × rater × date|143,940|

## Repository structure

```text
workforce-skills-intelligence/
├── README.md
├── LICENSE
├── requirements.txt
├── docs/
│   └── data\_dictionary.md
├── scripts/
│   ├── 01\_load\_onet.py              Unzip O\*NET and check row counts
│   ├── 02\_explore\_onet\_example.py   Worked example: tasks to skills for one occupation
│   ├── 03\_explore\_onet\_bank\_roles.py  What O\*NET can and cannot show for AI roles
│   ├── 04\_explore\_bls.py            Banking employment per 10,000 jobs
│   ├── 05\_build\_roles.py            Build dim\_role (16 roles)
│   ├── 06\_generate\_employees.py     Create 6,124 synthetic employees
│   ├── 07\_build\_role\_skills.py      Build dim\_skill and fact\_role\_skill
│   ├── 08\_generate\_learning.py      Create learning records
│   ├── 09\_generate\_ratings.py       Simulate self and manager ratings
│   └── 10\_readiness\_and\_gaps.py     Calculate readiness and critical skill gaps
└── data/
    └── processed/                   All tables and results as CSV
```

## How to run

1. Install Python 3.10 or newer, then the packages:

```bash
   pip install -r requirements.txt
   ```

2. Download the [O\*NET 31.0 CSV database](https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip) and save `db\_31\_0\_csv.zip` in the project folder.
3. Download the [BLS May 2025 industry data](https://www.bls.gov/oes/special-requests/oesm25in4.zip) and extract it to `data/raw/bls/`.
4. Run the scripts in order, from `01` to `10`. Each script prints checks with expected values, such as `6124 | expected 6124`.

Fixed random seeds mean the synthetic data and results are identical on every run.

## Simulation rules

|Rule|Setting|
|-|-|
|Starting level by role group|Frontline 1.3, Business 1.9, Technology 2.8, AI-critical 3.2|
|Consistency|One general AI strength per person, applied across their skills|
|Built-in shortages|AI security and model validation lowered by one level|
|Self-rating bias|About 0.5 levels above manager ratings|
|Learning|55% complete an AI Foundations course between ratings|
|Training effect|45% of completers improve each Foundations skill, against 20% of others; other skills improve for 15%|

## Results (simulated data, manager ratings)

||April 2026|October 2026|
|-|-:|-:|
|Employees with basic AI capability|2,002|2,664|
|Readiness rate|32.7%|43.5%|
|Short of the 3,062 target|1,060|398|

|Critical skill|Needing Level 4|Meeting Level 4|
|-|-:|-:|
|Model validation|90|3 (3.3%)|
|AI security|107|10 (9.3%)|

Other core skills in AI-critical roles have 36% to 50% coverage.

**These results reflect patterns built into the synthetic data.** They show that the method detects them, not what a real bank would find.

## Limitations

* Employee data is synthetic, so results demonstrate the method rather than real findings.
* Skill definitions and requirements need validation by subject matter experts.
* Role proportions reflect US banking, not a specific organisation or Singapore.
* Manager ratings can be biased. Critical skills need stronger evidence, such as assessments.

**A production version would need** approved internal skill definitions, secure HR data integration, rating calibration across managers, privacy controls and regular refreshes.

## Tools

Python · pandas · NumPy · Power BI (dashboard in progress)

## Attribution

This project includes information from the [O\*NET 31.0 Database](https://www.onetcenter.org/database.html) by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license. O\*NET® is a trademark of USDOL/ETA. I have modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications.

Role proportions come from the U.S. Bureau of Labor Statistics [Occupational Employment and Wage Statistics](https://www.bls.gov/oes/).

The MIT License in this repository covers the code only.

