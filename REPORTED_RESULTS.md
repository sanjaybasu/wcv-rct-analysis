# Reported Results (for independent verification)

## Table 1 (baseline characteristics), key rows

| Characteristic | Arm 1 | Arm 2 | Arm 3 | P | Corrected P |
|---|---|---|---|---|---|
| Baseline enrollment, mean (median), mo | 4.6 (5.0) | 4.7 (5.0) | 4.7 (5.0) | .62 | >.99 |
| Study period observation, mean (median), mo | 5.9 (7.0) | 5.8 (7.0) | 5.7 (7.0) | .31 | >.99 |
| Age, mean (median), y | 12.8 (13.1) | 13.1 (13.7) | 12.7 (13.2) | .21 | >.99 |
| Age 18-21 y, No. (%) | 177 (19.1) | 175 (18.4) | 171 (18.1)* | .85 | >.99 |
| Black or African American | 386 (41.6%) | 331 (34.9%) | 378 (40.0%) | <.001 | .004 |
| White | 303 (32.7%) | 379 (39.9%) | 330 (34.9%) | <.001 | .004 |
| Anxiety, No. (%) | 25 (2.7%) | 50 (5.3%) | 41 (4.3%) | .02 | .27 |

\* Age 18-21 uses an inclusive 18≤age≤21 definition, matching the row label and the trial's stated 0-21 year eligibility range.



Running `primary_analysis.run_primary_analysis` and `subgroup_analysis.age_subgroups` /
`race_subgroups` against a correctly formatted extract of the trial data should
reproduce the following manuscript results.

## Primary outcome

| Arm | Completed | N | % |
|---|---|---|---|
| 1: Traditional passive outreach | 218 | 927 | 23.5% |
| 2: Automated SMS | 209 | 949 | 22.0% |
| 3: Automated SMS + AI scheduling | 280 | 945 | 29.6% |

Omnibus chi-squared: χ²=16.34, df=2, P<.001

## GEE (household-clustered)

Household clusters are defined using the trial's `shared_contact` indicator: a
participant's contact phone number where that number was flagged as shared
with another household member; a participant with a unique, unshared, or
missing phone number is treated as a single-participant cluster. (An earlier
version of this file, and of the manuscript, defined clusters as raw
phone-number matches without this flag, which produced 2,283 clusters and
excluded 4 participants with no phone number on file; that definition
undercounted true clusters — see `src/wcv_rct/primary_analysis.py`'s
`household_id` docstring for the exact rule.)

- N clusters: 2,316; mean cluster size: 1.2; max cluster size: 7
- Arm 2 vs Arm 1: OR=0.88 (95% CI, 0.70–1.11), P=.29
- Arm 3 vs Arm 1: OR=1.41 (95% CI, 1.13–1.76), P=.002
- Arm 3 vs Arm 2: OR=1.60 (95% CI, 1.28–2.01), P<.001

## Exploratory subgroup analyses (Arm 3 vs Arm 2)

| Subgroup | Arm 2 | Arm 3 | Diff (pp) | P |
|---|---|---|---|---|
| Age 0-11 | 97/343 (28.3%) | 131/366 (35.8%) | +7.5 | .032 |
| Age 12-21 | 112/606 (18.5%) | 149/579 (25.7%) | +7.3 | .003 |
| Black or African American | 72/331 (21.8%) | 101/378 (26.7%) | +5.0 | .124 |
| White | 79/379 (20.8%) | 93/330 (28.2%) | +7.3 | .023 |

## Exploratory age-band subgroup analysis (eTable 6, Bright Futures-aligned)

| Age band | Arm 1 | Arm 2 | Arm 3 | Overall P | Arm3 vs Arm2 diff (pp) | P |
|---|---|---|---|---|---|---|
| 0-5 | 38/94 (40.4%) | 35/88 (39.8%) | 31/92 (33.7%) | .584 | -6.1 | .398 |
| 6-11 | 62/262 (23.7%) | 62/255 (24.3%) | 100/274 (36.5%) | .001 | +12.2 | .002 |
| 12-17 | 81/313 (25.9%) | 83/334 (24.9%) | 100/331 (30.2%) | .257 | +5.4 | .122 |
| 18-21 | 37/258 (14.3%) | 29/272 (10.7%) | 49/248 (19.8%) | .014 | +9.1 | .004 |
