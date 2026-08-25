import pytest

from wcv_rct.cost_analysis import cost_per_incremental_completion, marginal_technology_cost_per_attempt, total_intervention_cost


def test_marginal_technology_cost_per_attempt():
    assert round(marginal_technology_cost_per_attempt(), 2) == 0.31


def test_total_intervention_cost_matches_etable4_example():
    # eTable 4 reports a $22.42 SMS line item, implying an average of ~3.003
    # messages per participant rather than the flat 3 used here as an
    # illustrative unit-cost input; this reproduces the total to within the
    # resulting $0.02 (0.01%) rounding gap.
    result = total_intervention_cost(
        n_call_attempts=86,
        n_arm3_participants=945,
        sms_messages_per_participant=3,
        n_ai_booked_appointments=63,
        ai_qa_minutes_per_appointment=2.0,
        n_human_escalations=12,
        human_staff_minutes_per_escalation=14.0,
    )
    assert result["total_cost"] == pytest.approx(196.08, abs=0.05)
    assert round(result["cost_per_randomized_participant"], 2) == 0.21


def test_cost_per_incremental_completion():
    assert round(cost_per_incremental_completion(196.08, 71), 2) == 2.76
