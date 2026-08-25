# wcv-rct-analysis

Statistical analysis code for a three-arm randomized clinical trial evaluating
conversational AI-powered appointment scheduling assistance for closing the
well-child visit (WCV) gap among Medicaid-enrolled children.

- **Trial registration:** [NCT06698640](https://clinicaltrials.gov/study/NCT06698640) (ClinicalTrials.gov)
- **Protocol:** HEDIS-OPT-2024-001
- **Design:** Three-arm, parallel-group, superiority randomized trial (traditional passive outreach vs automated SMS vs automated SMS + AI-powered scheduling assistance), household-randomized 1:1:1, N=2,821.

This repository contains the statistical analysis code used to produce the
primary and secondary results, exploratory subgroup analyses, and cost
analysis reported in the trial manuscript. It is provided so that the
reported statistics can be independently verified against a correctly
formatted extract of the trial data.

## Contribution

- **Primary analysis** (`src/wcv_rct/primary_analysis.py`): omnibus chi-squared
  test of well-child visit completion across the three arms, followed by a
  generalized estimating equations (GEE) model (binomial family, exchangeable
  correlation structure, robust sandwich standard errors) clustered by
  household to account for within-household correlation from household-level
  randomization. Household clusters are defined using the source data's
  phone-sharing indicator (`shared_contact`): a phone number is treated as one
  household only where it was flagged as intentionally shared between
  participants; every other participant, including those with no phone number
  on file, is its own single-participant cluster.
- **Subgroup analysis** (`src/wcv_rct/subgroup_analysis.py`): exploratory
  age-group, finer Bright Futures-aligned age-band, and race subgroup
  analyses, each with an omnibus three-arm chi-squared test and a
  Bonferroni-corrected pairwise comparison (Arm 3 vs Arm 2).
- **Cost analysis** (`src/wcv_rct/cost_analysis.py`): marginal technology cost
  per scheduling attempt and incremental cost per completed well-child visit.
- **Baseline characteristics** (`src/wcv_rct/baseline_table.py`): fully
  reproduces Table 1 (age, sex, race, clinical utilization, medication use,
  and condition prevalence by arm, with omnibus tests and a Bonferroni
  correction across 15 baseline comparisons). One published row — "Members
  per household" — is explicitly marked as **not reproducible from the data
  provided**: no computation for it exists in the source analysis notebook,
  and it does not reconcile with any household/contact grouping variable
  present in the data.

## Reproducibility and data

**No patient data is included in this repository.** All source data are
Medicaid protected health information (PHI) and are not, and will not be,
made public. The modules in `src/wcv_rct/` are pure functions that operate on
a pandas DataFrame with the column schema documented in each module's
docstring; they can be run against a properly de-identified or
access-controlled extract of the trial data, but no such extract is provided
or referenced here.

```
pip install -r requirements.txt
```

```python
import pandas as pd
from wcv_rct.primary_analysis import run_primary_analysis

df = pd.read_csv("your_local_extract.csv")  # not included in this repo
results = run_primary_analysis(df)
print(results)
```

## Layout

```
src/wcv_rct/          analysis modules: primary_analysis, subgroup_analysis, cost_analysis
requirements.txt      Python dependencies
```

## Study context

Conducted within Waymark, a community-based provider organization providing
free medical and social services to patients receiving Medicaid. Approved
with a waiver of informed consent by WCG IRB (protocol HEDIS-OPT-2024-001,
amended May 31, 2025).

## License

MIT. See LICENSE.
