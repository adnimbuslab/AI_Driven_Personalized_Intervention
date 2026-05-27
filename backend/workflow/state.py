"""LangGraph workflow state shared across all agents."""

from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
import operator


class WorkflowState(TypedDict, total=False):
    # Case identifiers
    case_id: str
    child_id: str
    current_step: str
    workflow_status: str

    # Consent
    consent_status: Optional[str]
    reporter_id: Optional[str]

    # Input data
    raw_inputs: Optional[dict]
    structured_inputs: Optional[dict]
    uploaded_documents: Optional[list]
    follow_up_round: int
    follow_up_questions: Optional[list]

    # Data quality
    data_quality_score: Optional[float]
    data_quality_gaps: Optional[list]
    data_quality_status: Optional[str]

    # Profile
    child_profile: Optional[dict]
    profile_confidence: Optional[float]

    # Prediction
    domain_priorities: Optional[list]
    prediction_confidence: Optional[dict]

    # Confidence check
    proceed_decision: Optional[str]
    abstention_reason: Optional[str]
    partial_proceed_domains: Optional[list]

    # Domain analysis
    domain_analysis: Optional[list]

    # Guidelines
    intervention_guidelines: Optional[list]
    guideline_confidence: Optional[dict]

    # Bias check
    bias_check_status: Optional[str]
    bias_concerns: Optional[list]

    # Goals
    smart_goals: Optional[list]

    # Milestones
    milestones: Optional[list]

    # Caregiver guidance
    caregiver_guidance: Optional[dict]

    # Plan
    plan_id: Optional[str]

    # Review
    clinician_review: Optional[dict]

    # Audit tracking
    agent_outputs: Annotated[list, operator.add]
    escalation_history: Annotated[list, operator.add]

    # Error handling
    error: Optional[str]


def create_initial_state(case_id: str, child_id: str, reporter_id: str = "") -> WorkflowState:
    return WorkflowState(
        case_id=case_id,
        child_id=child_id,
        current_step="initiated",
        workflow_status="INITIATED",
        consent_status=None,
        reporter_id=reporter_id,
        raw_inputs=None,
        structured_inputs=None,
        uploaded_documents=None,
        follow_up_round=0,
        follow_up_questions=None,
        data_quality_score=None,
        data_quality_gaps=None,
        data_quality_status=None,
        child_profile=None,
        profile_confidence=None,
        domain_priorities=None,
        prediction_confidence=None,
        proceed_decision=None,
        abstention_reason=None,
        partial_proceed_domains=None,
        domain_analysis=None,
        intervention_guidelines=None,
        guideline_confidence=None,
        bias_check_status=None,
        bias_concerns=None,
        smart_goals=None,
        milestones=None,
        caregiver_guidance=None,
        plan_id=None,
        clinician_review=None,
        agent_outputs=[],
        escalation_history=[],
        error=None,
    )
