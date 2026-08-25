import pandas as pd

from wcv_rct.baseline_table import build_table1


def _toy_demo():
    return pd.DataFrame({
        "ARM": [1, 1, 2, 2, 3, 3],
        "age": [10, 20, 10, 20, 10, 20],
        "gender": ["Male", "Female", "Male", "Female", "Male", "Female"],
        "race": ["White", "Black or African American"] * 3,
        "elig_pre": [5, 5, 5, 5, 5, 5],
        "elig_post": [7, 7, 7, 7, 7, 7],
    })


def _toy_clin():
    return pd.DataFrame({
        "ARM": [1, 1, 2, 2, 3, 3],
        "diagn1_count": [0, 1, 0, 1, 0, 1],
        "number_of_tests": [0, 0, 0, 0, 0, 0],
        "ndc_count": [0, 0, 0, 0, 0, 0],
        "medical_adherence": [1, 1, 1, 1, 1, 1],
        "pcp_appointment": [0, 0, 0, 0, 0, 0],
        "ED_visit": [0, 0, 0, 0, 0, 0],
        "hospitalization": [0, 0, 0, 0, 0, 0],
        "acute_care_visits": [0, 0, 0, 0, 0, 0],
        "hypertension": [0, 0, 0, 0, 0, 0],
        "heart_failure": [0, 0, 0, 0, 0, 0],
        "diabetes": [0, 0, 0, 0, 0, 0],
        "copd": [0, 0, 0, 0, 0, 0],
        "asthma": [0, 0, 0, 0, 0, 0],
        "depression": [0, 0, 0, 0, 0, 0],
        "anxiety": [0, 0, 0, 0, 0, 0],
    })


def test_age_row_matches_hand_computed_mean():
    table = build_table1(_toy_demo(), _toy_clin())
    assert table["Age, mean (median), y"]["by_arm"][1] == "15.0 (15.0)"


def test_members_per_household_marked_not_reproducible():
    table = build_table1(_toy_demo(), _toy_clin())
    assert "NOT REPRODUCIBLE" in table["Members per household, mean (median)"]


def test_heart_failure_zero_variance_column_does_not_raise():
    # a condition with zero events in every arm must not crash chi2_contingency
    table = build_table1(_toy_demo(), _toy_clin())
    assert table["Heart Failure, No. (%)"]["p_value"] == 1.0
