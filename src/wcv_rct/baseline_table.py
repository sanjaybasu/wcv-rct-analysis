"""Fully reproducible baseline characteristics (Table 1) for the well-child visit
conversational-AI RCT (NCT06698640).

Expects two DataFrames merged on a participant identifier and both carrying an
`ARM` column (1/2/3):

demographics columns:
    ARM, age, gender ('Male'/'Female'), race (categorical, already recoded to
    the reporting categories: 'Black or African American', 'White', 'Asian',
    'Hispanic or Latinx', 'Other', 'Unknown/Missing'),
    elig_pre  (count of eligible months in a 5-month pre-randomization window),
    elig_post (count of eligible months in a 7-month post-randomization window)

clinical columns:
    ARM, diagn1_count, number_of_tests, ndc_count, medical_adherence,
    pcp_appointment, ED_visit, hospitalization, acute_care_visits,
    hypertension, heart_failure, diabetes, copd, asthma, depression, anxiety
    (condition columns are counts; presence is defined as count >= 1)

Every row below is independently derived from these two files. One row from
the published table — "Members per household" — is NOT reproduced here: no
source computation for it exists anywhere in the original analysis notebook,
and it does not reconcile with any household/contact grouping variable present
in the data (see README). It should not be treated as verified until its
source is identified.

No patient data is included in or referenced by this module.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, f_oneway

N_BASELINE_CHARACTERISTICS = 15  # matches the Bonferroni multiplier used in the source analysis


def _fmt(mean: float, median: float) -> str:
    return f"{mean:.1f} ({median:.1f})"


def _bonf(p: float) -> float:
    return min(p * N_BASELINE_CHARACTERISTICS, 1.0)


def _continuous_row(demo_or_clin: pd.DataFrame, col: str) -> dict:
    means, medians, groups = {}, {}, []
    for arm in (1, 2, 3):
        sub = demo_or_clin[demo_or_clin["ARM"] == arm][col].dropna()
        means[arm] = sub.mean()
        medians[arm] = sub.median()
        groups.append(sub)
    f_stat, p = f_oneway(*groups)
    return {
        "by_arm": {a: _fmt(means[a], medians[a]) for a in (1, 2, 3)},
        "p_value": p,
        "corrected_p": _bonf(p),
    }


def _binary_row(df: pd.DataFrame, mask_col: str, threshold: int = 1) -> dict:
    counts, totals = {}, {}
    table = []
    for arm in (1, 2, 3):
        sub = df[df["ARM"] == arm]
        n = int((sub[mask_col] >= threshold).sum())
        counts[arm] = n
        totals[arm] = len(sub)
        table.append([n, len(sub) - n])
    try:
        chi2, p, dof, _ = chi2_contingency(table)
    except ValueError:
        p = 1.0  # degenerate all-zero column (e.g. heart failure, COPD)
    return {
        "by_arm": {a: f"{counts[a]} ({100*counts[a]/totals[a]:.1f}%)" for a in (1, 2, 3)},
        "p_value": p,
        "corrected_p": _bonf(p),
    }


def _categorical_row(df: pd.DataFrame, col: str, category: str) -> dict:
    counts, totals = {}, {}
    for arm in (1, 2, 3):
        sub = df[df["ARM"] == arm]
        counts[arm] = int((sub[col] == category).sum())
        totals[arm] = len(sub)
    return {"by_arm": {a: f"{counts[a]} ({100*counts[a]/totals[a]:.1f}%)" for a in (1, 2, 3)}}


def categorical_omnibus_p(df: pd.DataFrame, col: str, categories: list[str]) -> dict:
    tab = []
    for cat in categories:
        row = [int(((df["ARM"] == arm) & (df[col] == cat)).sum()) for arm in (1, 2, 3)]
        tab.append(row)
    chi2, p, dof, _ = chi2_contingency(tab)
    return {"p_value": p, "corrected_p": _bonf(p)}


def build_table1(demo: pd.DataFrame, clin: pd.DataFrame) -> dict:
    """Returns a dict keyed by Table 1 row label, each containing per-arm
    formatted values and, where applicable, uncorrected and Bonferroni-
    corrected P values (correcting for 15 baseline comparisons, matching the
    source analysis)."""
    table = {}

    table["Baseline enrollment, mean (median), mo"] = _continuous_row(demo, "elig_pre")
    table["Study period observation, mean (median), mo"] = _continuous_row(demo, "elig_post")
    table["Members per household, mean (median)"] = "NOT REPRODUCIBLE from data provided — no source found"

    table["Age, mean (median), y"] = _continuous_row(demo, "age")
    demo = demo.copy()
    demo["age_18_21"] = ((demo["age"] >= 18) & (demo["age"] <= 21)).astype(int)
    table["Age 18-21 y, No. (%)"] = _binary_row(demo, "age_18_21")

    gender_tab = [
        [int(((demo["ARM"] == arm) & (demo["gender"] == g)).sum()) for arm in (1, 2, 3)]
        for g in ("Male", "Female")
    ]
    chi2, p, _, _ = chi2_contingency(gender_tab)
    table["Sex, No. (%)"] = {
        "Male": _categorical_row(demo, "gender", "Male")["by_arm"],
        "Female": _categorical_row(demo, "gender", "Female")["by_arm"],
        "p_value": p,
        "corrected_p": _bonf(p),
    }

    race_categories = ["Black or African American", "White", "Asian", "Hispanic or Latinx", "Other", "Unknown/Missing"]
    race_p = categorical_omnibus_p(demo, "race", race_categories)
    table["Race/Ethnicity, No. (%)"] = {
        cat: _categorical_row(demo, "race", cat)["by_arm"] for cat in race_categories
    } | race_p

    clin_cols_continuous = {
        "Primary care visits, mean (median), No.": "pcp_appointment",
        "Acute care visits, mean (median), No.": "acute_care_visits",
        "Emergency department visits, mean (median), No.": "ED_visit",
        "Hospitalizations, mean (median), No.": "hospitalization",
        "Laboratory tests, mean (median), No.": "number_of_tests",
        "Medications, mean (median), No.": "ndc_count",
        "Medication adherence, mean (median)": "medical_adherence",
        "Clinical conditions, mean (median), No.": "diagn1_count",
    }
    for label, col in clin_cols_continuous.items():
        table[label] = _continuous_row(clin, col)

    conditions = ["hypertension", "heart_failure", "diabetes", "copd", "asthma", "depression", "anxiety"]
    for cond in conditions:
        label = f"{cond.replace('_', ' ').title()}, No. (%)"
        table[label] = _binary_row(clin, cond)

    return table
