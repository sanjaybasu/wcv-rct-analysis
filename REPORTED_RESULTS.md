# Reported Results (for independent verification)

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

- N clusters: 2,283; mean cluster size: 1.2
- Arm 2 vs Arm 1: OR=0.88 (95% CI, 0.69–1.11), P=.27
- Arm 3 vs Arm 1: OR=1.40 (95% CI, 1.13–1.73), P=.002
- Arm 3 vs Arm 2: OR=1.60 (95% CI, 1.28–2.00), P<.001

## Exploratory subgroup analyses (Arm 3 vs Arm 2)

| Subgroup | Arm 2 | Arm 3 | Diff (pp) | P |
|---|---|---|---|---|
| Age 0-11 | 97/343 (28.3%) | 131/366 (35.8%) | +7.5 | .032 |
| Age 12-21 | 112/606 (18.5%) | 149/579 (25.7%) | +7.3 | .003 |
| Black or African American | 72/331 (21.8%) | 101/378 (26.7%) | +5.0 | .124 |
| White | 79/379 (20.8%) | 93/330 (28.2%) | +7.3 | .023 |
