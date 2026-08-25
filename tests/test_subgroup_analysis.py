import pandas as pd

from wcv_rct.subgroup_analysis import age_band_subgroups, age_subgroups, race_subgroups, subgroup_result


def _toy_df():
    rows = []
    for arm, rate, n in [(1, 0.2, 50), (2, 0.2, 50), (3, 0.4, 50)]:
        for i in range(n):
            rows.append({
                "ARM": arm,
                "outcome": 1 if i < int(rate * n) else 0,
                "denominator": 1,
                "age": [3, 8, 15, 20][i % 4],
                "race": "Black or African American" if i % 2 == 0 else "White",
            })
    return pd.DataFrame(rows)


def test_subgroup_result_counts_match_mask():
    df = _toy_df()
    result = subgroup_result(df, df["age"] < 10)  # matches ages 3 and 8 in every arm
    expected = int(((df["ARM"] == 1) & (df["age"] < 10)).sum())
    assert result["n_by_arm"][1] == expected == 26
    assert result["n_by_arm"][2] == expected
    assert result["n_by_arm"][3] == expected


def test_age_subgroups_partition_is_disjoint_and_complete():
    df = _toy_df()
    result = age_subgroups(df)
    assert result["0-11"]["n_by_arm"][1] + result["12-21"]["n_by_arm"][1] == (df["ARM"] == 1).sum()


def test_age_band_subgroups_bins_are_correct():
    ages = [5, 6, 17, 18]  # one participant per band, per arm
    df = pd.DataFrame({
        "ARM": [arm for arm in (1, 2, 3) for _ in ages],
        "outcome": [0, 1, 0, 1] * 3,
        "denominator": [1] * 12,
        "age": ages * 3,
    })
    result = age_band_subgroups(df)
    for band in ("0-5", "6-11", "12-17", "18-21"):
        assert result[band]["n_by_arm"] == {1: 1, 2: 1, 3: 1}


def test_race_subgroups_default_categories():
    df = _toy_df()
    result = race_subgroups(df)
    assert set(result.keys()) == {"Black or African American", "White"}
