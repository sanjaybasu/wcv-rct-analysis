from wcv_rct.cost_analysis import cost_per_incremental_completion, marginal_technology_cost_per_attempt, total_intervention_cost


def test_marginal_technology_cost_per_attempt():
    assert round(marginal_technology_cost_per_attempt(), 2) == 0.31


def test_total_intervention_cost_arithmetic():
    result = total_intervention_cost(
        n_call_attempts=10,
        n_arm3_participants=100,
        sms_messages_per_participant=2,
        n_ai_booked_appointments=5,
        ai_qa_minutes_per_appointment=3.0,
        n_human_escalations=2,
        human_staff_minutes_per_escalation=10.0,
    )
    assert round(result["llm_api_cost"], 2) == 0.90
    assert round(result["tts_cost"], 2) == 1.50
    assert round(result["telephony_cost"], 2) == 0.70
    assert round(result["sms_cost"], 2) == 1.58
    assert round(result["staff_qa_cost"], 2) == 7.50
    assert round(result["staff_escalation_cost"], 2) == 10.00
    assert round(result["total_cost"], 2) == 22.18
    assert round(result["cost_per_randomized_participant"], 4) == 0.2218


def test_cost_per_incremental_completion():
    assert round(cost_per_incremental_completion(22.18, 4), 2) == 5.54
