"""Primary outcome analysis for the well-child visit conversational-AI RCT (NCT06698640).

Expects a DataFrame with one row per randomized participant and columns:
    ARM            int, 1/2/3 (1=traditional passive outreach, 2=automated SMS,
                   3=automated SMS + AI scheduling assistance)
    outcome        int, 1 if the participant completed a well-child visit by the
                   end of the outcome-observation window, else 0
    denominator    int, 1 for every included participant (HEDIS-style numerator/
                   denominator convention retained from the source pipeline)
    household_id   household- or contact-level identifier used to cluster
                   participants who were randomized together (all children in a
                   household were assigned to the same arm)

No patient data is included in or referenced by this module.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.cov_struct import Exchangeable

ARM_LABELS = {1: "Traditional passive outreach", 2: "Automated SMS", 3: "Automated SMS + AI scheduling"}


def _arm_counts(df: pd.DataFrame) -> dict[int, tuple[int, int]]:
    out = {}
    for arm in (1, 2, 3):
        sub = df[df["ARM"] == arm]
        out[arm] = (int(sub["outcome"].sum()), int(sub["denominator"].sum()))
    return out


def omnibus_chi_square(df: pd.DataFrame) -> dict:
    """Three-arm chi-squared test of independence on well-child visit completion."""
    counts = _arm_counts(df)
    table = [[num, den - num] for num, den in counts.values()]
    chi2, p, dof, _ = chi2_contingency(table)
    return {"arm_counts": counts, "chi2": chi2, "df": dof, "p_value": p}


def gee_model(df: pd.DataFrame) -> dict:
    """GEE model (binomial family, exchangeable correlation, robust sandwich SEs)
    clustered by household_id, with Arm 1 as the reference category.

    Rows with a missing household_id are excluded prior to fitting, consistent
    with standard GEE handling of missing cluster identifiers; the analyzed N
    is reported alongside the intention-to-treat N so any difference is
    explicit.
    """
    itt_n = len(df)
    gee_df = df[["outcome", "ARM", "household_id"]].dropna().copy()
    gee_df["arm2"] = (gee_df["ARM"] == 2).astype(int)
    gee_df["arm3"] = (gee_df["ARM"] == 3).astype(int)
    exog = pd.DataFrame({"intercept": 1, "arm2": gee_df["arm2"], "arm3": gee_df["arm3"]})

    model = GEE(
        endog=gee_df["outcome"],
        exog=exog,
        groups=gee_df["household_id"],
        family=Binomial(),
        cov_struct=Exchangeable(),
    )
    result = model.fit()

    def _or_ci(name: str) -> dict:
        est = result.params[name]
        ci = result.conf_int().loc[name]
        return {
            "or": float(np.exp(est)),
            "ci_low": float(np.exp(ci[0])),
            "ci_high": float(np.exp(ci[1])),
            "p_value": float(result.pvalues[name]),
        }

    # Arm 3 vs Arm 2 contrast via delta method on the log-OR difference
    log_or_diff = result.params["arm3"] - result.params["arm2"]
    cov = result.cov_params()
    se_diff = np.sqrt(cov.loc["arm3", "arm3"] + cov.loc["arm2", "arm2"] - 2 * cov.loc["arm3", "arm2"])
    z = log_or_diff / se_diff
    p_diff = 2 * (1 - norm.cdf(abs(z)))

    return {
        "itt_n": itt_n,
        "analyzed_n": len(gee_df),
        "n_clusters": gee_df["household_id"].nunique(),
        "mean_cluster_size": len(gee_df) / gee_df["household_id"].nunique(),
        "arm2_vs_arm1": _or_ci("arm2"),
        "arm3_vs_arm1": _or_ci("arm3"),
        "arm3_vs_arm2": {
            "or": float(np.exp(log_or_diff)),
            "ci_low": float(np.exp(log_or_diff - 1.96 * se_diff)),
            "ci_high": float(np.exp(log_or_diff + 1.96 * se_diff)),
            "p_value": float(p_diff),
        },
        "summary": result.summary(),
    }


def run_primary_analysis(df: pd.DataFrame) -> dict:
    """Convenience wrapper returning the full primary-outcome analysis."""
    return {
        "chi_square": omnibus_chi_square(df),
        "gee": gee_model(df),
    }
