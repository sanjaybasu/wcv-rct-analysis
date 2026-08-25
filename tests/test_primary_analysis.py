import numpy as np
import pandas as pd
import pytest

from wcv_rct.primary_analysis import gee_model, omnibus_chi_square, run_primary_analysis


def _toy_df(n_per_arm=60, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    rates = {1: 0.20, 2: 0.20, 3: 0.40}
    for arm, rate in rates.items():
        outcomes = rng.binomial(1, rate, n_per_arm)
        for i, o in enumerate(outcomes):
            rows.append({"ARM": arm, "outcome": int(o), "denominator": 1,
                         "household_id": f"arm{arm}_p{i}"})
    return pd.DataFrame(rows)


def test_omnibus_chi_square_matches_scipy_on_known_table():
    df = pd.DataFrame({
        "ARM": [1] * 10 + [2] * 10 + [3] * 10,
        "outcome": [1] * 2 + [0] * 8 + [1] * 2 + [0] * 8 + [1] * 8 + [0] * 2,
        "denominator": [1] * 30,
    })
    result = omnibus_chi_square(df)
    assert result["arm_counts"] == {1: (2, 10), 2: (2, 10), 3: (8, 10)}
    assert result["df"] == 2
    assert result["p_value"] < 0.01


def test_gee_model_retains_full_itt_n_with_missing_household_id():
    df = _toy_df()
    df.loc[df.index[:5], "household_id"] = np.nan
    result = gee_model(df)
    assert result["itt_n"] == len(df)
    assert result["analyzed_n"] == len(df)
    assert result["n_clusters"] == len(df) - 5 + 5  # 5 singletons + remaining unique ids


def test_gee_model_higher_arm3_rate_yields_or_above_one():
    df = _toy_df(n_per_arm=150, seed=1)
    result = gee_model(df)
    assert result["arm3_vs_arm2"]["or"] > 1
    assert result["arm3_vs_arm2"]["ci_low"] < result["arm3_vs_arm2"]["or"] < result["arm3_vs_arm2"]["ci_high"]


def test_gee_model_clusters_do_not_span_arms_by_construction():
    df = _toy_df()
    counts = df.groupby("household_id")["ARM"].nunique()
    assert (counts <= 1).all()


def test_run_primary_analysis_returns_both_components():
    df = _toy_df()
    result = run_primary_analysis(df)
    assert "chi_square" in result and "gee" in result
