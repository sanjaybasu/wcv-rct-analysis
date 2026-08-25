"""Marginal cost and cost-consequence analysis for the AI-facilitated scheduling arm.

All figures are illustrative unit-cost constants documented in the trial's
eAppendix; no patient-level data is required or referenced by this module.
"""
from __future__ import annotations

# Per-attempt marginal technology cost components (Arm 3 scheduling attempts)
LLM_API_COST_PER_ATTEMPT = 0.09          # GPT-4o input + output tokens
TTS_COST_PER_ATTEMPT = 0.15              # text-to-speech vendor
TELEPHONY_COST_PER_ATTEMPT = 0.07        # outbound voice minutes
SMS_COST_PER_MESSAGE = 0.0079

STAFF_COST_PER_MINUTE = 0.50


def marginal_technology_cost_per_attempt() -> float:
    return LLM_API_COST_PER_ATTEMPT + TTS_COST_PER_ATTEMPT + TELEPHONY_COST_PER_ATTEMPT


def total_intervention_cost(
    n_call_attempts: int,
    n_arm3_participants: int,
    sms_messages_per_participant: int,
    n_ai_booked_appointments: int,
    ai_qa_minutes_per_appointment: float,
    n_human_escalations: int,
    human_staff_minutes_per_escalation: float,
) -> dict:
    """Reproduces the marginal-cost table (eTable 4) from its component parts.

    This excludes fixed scheduler development and piloting costs, which are
    amortized across the broader deployment rather than attributable to an
    individual scheduling attempt (see manuscript eAppendix 3).
    """
    llm_cost = LLM_API_COST_PER_ATTEMPT * n_call_attempts
    tts_cost = TTS_COST_PER_ATTEMPT * n_call_attempts
    telephony_cost = TELEPHONY_COST_PER_ATTEMPT * n_call_attempts
    sms_cost = SMS_COST_PER_MESSAGE * sms_messages_per_participant * n_arm3_participants
    staff_qa_cost = ai_qa_minutes_per_appointment * STAFF_COST_PER_MINUTE * n_ai_booked_appointments
    staff_escalation_cost = human_staff_minutes_per_escalation * STAFF_COST_PER_MINUTE * n_human_escalations

    total = llm_cost + tts_cost + telephony_cost + sms_cost + staff_qa_cost + staff_escalation_cost
    return {
        "llm_api_cost": llm_cost,
        "tts_cost": tts_cost,
        "telephony_cost": telephony_cost,
        "sms_cost": sms_cost,
        "staff_qa_cost": staff_qa_cost,
        "staff_escalation_cost": staff_escalation_cost,
        "total_cost": total,
        "cost_per_randomized_participant": total / n_arm3_participants,
    }


def cost_per_incremental_completion(total_cost: float, incremental_completions: int) -> float:
    """Incremental completions = Arm 3 completions minus Arm 2 completions."""
    return total_cost / incremental_completions
