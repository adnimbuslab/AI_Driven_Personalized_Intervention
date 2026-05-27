"""LangGraph workflow graph definition.

Constructs the StateGraph with all agent nodes and conditional routing.
"""

from langgraph.graph import StateGraph, END

from backend.workflow.state import WorkflowState
from backend.workflow.routing import (
    route_consent,
    route_input,
    route_data_quality,
    route_profile,
    route_prediction,
    route_confidence,
    route_bias,
    route_review,
    human_review_node,
)


def _make_node(agent_cls):
    """Create a LangGraph node function from an agent class."""
    def node_fn(state: WorkflowState) -> dict:
        agent = agent_cls()
        return agent.execute(state)
    return node_fn


def build_workflow() -> StateGraph:
    """Build and return the compiled LangGraph workflow."""
    from backend.agents.ethics_consent import EthicsConsentAgent
    from backend.agents.input_aggregation import InputAggregationAgent
    from backend.agents.data_quality import DataQualityAgent
    from backend.agents.profile_synthesis import ProfileSynthesisAgent
    from backend.agents.prediction import PredictionAgent
    from backend.agents.confidence_abstention import ConfidenceAbstentionAgent
    from backend.agents.domain_analysis import DomainAnalysisAgent
    from backend.agents.guideline_generation import GuidelineGenerationAgent
    from backend.agents.bias_monitoring import BiasMonitoringAgent
    from backend.agents.goal_generation import GoalGenerationAgent
    from backend.agents.milestone_planning import MilestonePlanningAgent
    from backend.agents.caregiver_guidance import CaregiverGuidanceAgent

    workflow = StateGraph(WorkflowState)

    # Add agent nodes
    workflow.add_node("ethics_consent", _make_node(EthicsConsentAgent))
    workflow.add_node("input_aggregation", _make_node(InputAggregationAgent))
    workflow.add_node("data_quality", _make_node(DataQualityAgent))
    workflow.add_node("profile_synthesis", _make_node(ProfileSynthesisAgent))
    workflow.add_node("prediction", _make_node(PredictionAgent))
    workflow.add_node("confidence_abstention", _make_node(ConfidenceAbstentionAgent))
    workflow.add_node("domain_analysis", _make_node(DomainAnalysisAgent))
    workflow.add_node("guideline_generation", _make_node(GuidelineGenerationAgent))
    workflow.add_node("bias_monitoring", _make_node(BiasMonitoringAgent))
    workflow.add_node("goal_generation", _make_node(GoalGenerationAgent))
    workflow.add_node("milestone_planning", _make_node(MilestonePlanningAgent))
    workflow.add_node("caregiver_guidance", _make_node(CaregiverGuidanceAgent))
    workflow.add_node("human_review", human_review_node)

    # Entry point
    workflow.set_entry_point("ethics_consent")

    # Edges
    workflow.add_conditional_edges("ethics_consent", route_consent)
    workflow.add_conditional_edges("input_aggregation", route_input)
    workflow.add_conditional_edges("data_quality", route_data_quality)
    workflow.add_conditional_edges("profile_synthesis", route_profile)
    workflow.add_conditional_edges("prediction", route_prediction)
    workflow.add_conditional_edges("confidence_abstention", route_confidence)
    workflow.add_edge("domain_analysis", "guideline_generation")
    workflow.add_conditional_edges("bias_monitoring", route_bias)
    workflow.add_edge("goal_generation", "milestone_planning")
    workflow.add_edge("milestone_planning", "caregiver_guidance")
    workflow.add_edge("caregiver_guidance", "human_review")
    workflow.add_edge("guideline_generation", "bias_monitoring")
    workflow.add_edge("human_review", END)

    return workflow.compile()


# Lazy singleton
_compiled_workflow = None


def get_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_workflow()
    return _compiled_workflow
