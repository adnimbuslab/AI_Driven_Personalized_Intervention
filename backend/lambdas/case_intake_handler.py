"""Case intake handler — Creates new cases and initializes workflow state."""

import json
from backend.utils.case_id import generate_case_id
from backend.mcp_servers.audit_mcp import AuditMCP
from backend.mcp_servers.dynamo_mcp import DynamoMCP


def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except (json.JSONDecodeError, TypeError):
        body = event.get("body", {}) if isinstance(event.get("body"), dict) else {}

    reporter_id = body.get("reporter_id", "")
    consent_status = body.get("consent_status", "PENDING")

    if not reporter_id:
        return _response(400, {"error": "reporter_id is required"})

    case_id = generate_case_id()
    child_id = body.get("child_id", f"CH-{case_id.split('-')[-1]}")

    dynamo = DynamoMCP()
    dynamo.put_child_profile(
        child_id=child_id,
        profile_data={
            "case_id": case_id,
            "status": "initiated",
            "reporter_id": reporter_id,
        },
    )

    audit = AuditMCP()
    audit.log_event(
        case_id=case_id,
        agent_id="system",
        event_type="STATE_TRANSITION",
        action="Case initiated",
        metadata={"reporter_id": reporter_id, "consent_status": consent_status},
    )

    return _response(201, {
        "case_id": case_id,
        "child_id": child_id,
        "status": "INITIATED",
        "consent_status": consent_status,
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
