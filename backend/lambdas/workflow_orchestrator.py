"""Workflow orchestrator — Runs the LangGraph workflow for a case."""

import json
from backend.workflow.state import create_initial_state
from backend.workflow.graph import get_workflow
from backend.mcp_servers.audit_mcp import AuditMCP


def handler(event, context):
    case_id = event.get("pathParameters", {}).get("case_id", "")
    if not case_id:
        return _response(400, {"error": "case_id is required"})

    body = event.get("body", {})
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}

    child_id = body.get("child_id", "")
    reporter_id = body.get("reporter_id", "")
    consent_status = body.get("consent_status", "GRANTED")
    structured_inputs = body.get("structured_inputs", {})

    initial_state = create_initial_state(
        case_id=case_id,
        child_id=child_id,
        reporter_id=reporter_id,
    )
    initial_state["consent_status"] = consent_status
    if structured_inputs:
        initial_state["structured_inputs"] = structured_inputs
        initial_state["raw_inputs"] = structured_inputs

    audit = AuditMCP()
    audit.log_event(
        case_id=case_id,
        agent_id="workflow-engine",
        event_type="STATE_TRANSITION",
        action="Workflow started",
    )

    try:
        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        return _response(200, {
            "case_id": case_id,
            "workflow_status": final_state.get("workflow_status", "UNKNOWN"),
            "current_step": final_state.get("current_step", ""),
            "plan_id": final_state.get("plan_id"),
            "has_guidelines": final_state.get("intervention_guidelines") is not None,
            "has_goals": final_state.get("smart_goals") is not None,
            "has_milestones": final_state.get("milestones") is not None,
            "has_caregiver_guidance": final_state.get("caregiver_guidance") is not None,
            "error": final_state.get("error"),
        })
    except Exception as e:
        audit.log_event(
            case_id=case_id,
            agent_id="workflow-engine",
            event_type="ERROR",
            action=f"Workflow failed: {e}",
        )
        return _response(500, {"error": str(e), "case_id": case_id})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
