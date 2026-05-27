"""Conditional routing functions for LangGraph workflow edges."""

from langgraph.graph import END

from backend.config import Config


def route_consent(state: dict) -> str:
    status = state.get("consent_status")
    if status == "GRANTED":
        return "input_aggregation"
    if status == "DENIED":
        return END
    return END


def route_input(state: dict) -> str:
    if state.get("error"):
        return "human_review"
    return "data_quality"


def route_data_quality(state: dict) -> str:
    status = state.get("data_quality_status")
    if status == "VALIDATED":
        return "profile_synthesis"
    if status == "FOLLOW_UP":
        round_num = state.get("follow_up_round", 0)
        if round_num < Config.MAX_FOLLOWUP_ROUNDS:
            return "data_quality"
        return END
    return END


def route_profile(state: dict) -> str:
    confidence = state.get("profile_confidence", 0)
    threshold = Config.CONFIDENCE_THRESHOLD_DEFAULT
    if confidence >= threshold:
        return "prediction"
    return "human_review"


def route_prediction(state: dict) -> str:
    return "confidence_abstention"


def route_confidence(state: dict) -> str:
    decision = state.get("proceed_decision")
    if decision == "PROCEED":
        return "domain_analysis"
    if decision == "PARTIAL_PROCEED":
        return "domain_analysis"
    return END


def route_bias(state: dict) -> str:
    status = state.get("bias_check_status")
    if status == "PASSED":
        return "goal_generation"
    return "human_review"


def route_review(state: dict) -> str:
    review = state.get("clinician_review", {})
    action = review.get("action", "")
    if action in ("approved", "modified"):
        return END
    if action == "partial_approved":
        return "guideline_generation"
    return END


def human_review_node(state: dict) -> dict:
    """Placeholder node that pauses workflow for human review."""
    return {
        "workflow_status": "AWAITING_CLINICIAN_REVIEW",
        "current_step": "human_review",
        "agent_outputs": [{"agent": "human_review", "status": "awaiting_input"}],
    }
