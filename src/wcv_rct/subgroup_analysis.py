"""Exploratory subgroup analyses for the well-child visit conversational-AI RCT (NCT06698640).

Expects a DataFrame with the same schema as primary_analysis, plus:
    age    float, participant age at randomization
    race   str, participant race category

Subgroup analyses are exploratory and were not prespecified for confirmatory
inference. For each subgroup, we report an omnibus three-arm chi-squared test
and a Bonferroni-corrected pairwise comparison (Arm 3 vs Arm 2) using a
two-proportion z-test, with the correction applied across the three pairwise
comparisons within each subgroup (alpha = 0.05 / 3 = 0.0167).

No patient data is included in or referenced by this module.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportions_ztest

BONFERRONI_ALPHA = 0.05 / 3


def _rate_ci(num: int, den: int) -> tuple[float, float, float]:
    p = num / den
    se = np.sqrt(p * (1 - p) / den)
    return p * 100, (p - 1.96 * se) * 100, (p + 1.96 * se) * 100


def subgroup_result(df: pd.DataFrame, mask: pd.Series) -> dict:
    sub = df[mask]
    counts = {}
    for arm in (1, 2, 3):
        a = sub[sub["ARM"] == arm]
        counts[arm] = (int(a["outcome"].sum()), int(a["denominator"].sum()))

    table = [[num, den - num] for num, den in counts.values()]
    chi2, overall_p, dof, _ = chi2_contingency(table)

    stat, p32 = proportions_ztest(
        [counts[3][0], counts[2][0]], [counts[3][1], counts[2][1]]
    )
    diff_pp = 100 * (counts[3][0] / counts[3][1] - counts[2][0] / counts[2][1])

    return {
        "n_by_arm": {arm: den for arm, (num, den) in counts.items()},
        "rate_by_arm": {arm: _rate_ci(num, den) for arm, (num, den) in counts.items()},
        "overall_chi2_p": overall_p,
        "arm3_vs_arm2_diff_pp": diff_pp,
        "arm3_vs_arm2_p": p32,
        "significant_at_bonferroni": bool(p32 < BONFERRONI_ALPHA),
    }


def age_subgroups(df: pd.DataFrame) -> dict:
    return {
        "0-11": subgroup_result(df, df["age"] <= 11),
        "12-21": subgroup_result(df, df["age"] > 11),
    }


def age_band_subgroups(df: pd.DataFrame) -> dict:
    """Exploratory post hoc age-band analysis (eTable 6), using age bands that
    approximate AAP Bright Futures periodicity groupings."""
    bins = [-0.01, 5, 11, 17, 100]
    labels = ["0-5", "6-11", "12-17", "18-21"]
    band = pd.cut(df["age"], bins=bins, labels=labels)
    return {label: subgroup_result(df, band == label) for label in labels}


def race_subgroups(df: pd.DataFrame, race_values: list[str] | None = None) -> dict:
    race_values = race_values or ["Black or African American", "White"]
    return {race: subgroup_result(df, df["race"] == race) for race in race_values}


def non_responder_comparison(df: pd.DataFrame, arm: int = 3) -> pd.DataFrame:
    """Standardized differences between responders and non-responders within an arm.

    Expects an additional boolean/int `responder` column on df.
    Returns a DataFrame with mean/percentage, standardized difference, and a
    p-value for each compared characteristic column present in df.
    """
    from scipy.stats import chi2_contingency as _chi2, ttest_ind

    sub = df[df["ARM"] == arm]
    responders = sub[sub["responder"] == 1]
    non_responders = sub[sub["responder"] == 0]

    rows = []
    continuous_vars = [c for c in ["age", "diagn1_count", "ndc_count", "ED_visit",
                                    "acute_care_visits", "hospitalization"] if c in df.columns]
    for var in continuous_vars:
        m1, s1 = responders[var].mean(), responders[var].std()
        m2, s2 = non_responders[var].mean(), non_responders[var].std()
        pooled_sd = np.sqrt((s1**2 + s2**2) / 2)
        std_diff = abs(m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0
        _, p = ttest_ind(responders[var].dropna(), non_responders[var].dropna())
        rows.append({"variable": var, "responders": m1, "non_responders": m2,
                      "std_diff": std_diff, "p_value": p})

    return pd.DataFrame(rows)
