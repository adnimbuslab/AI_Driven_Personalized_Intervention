"""Clinician review handler — Records review decisions (BR-001)."""

import json
import uuid
from backend.mcp_servers.dynamo_mcp import DynamoMCP
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
            return _response(400, {"error": "Invalid request body"})

    action = body.get("action", "")
    if action not in ("approved", "modified", "rejected", "partial_approved"):
        return _response(400, {"error": "action must be approved, modified, rejected, or partial_approved"})

    reviewer_id = body.get("reviewer_id", "")
    if not reviewer_id:
        return _response(400, {"error": "reviewer_id is required"})

    plan_id = body.get("plan_id", f"PLAN-{case_id}")
    modifications = body.get("modifications", [])
    notes = body.get("notes", "")

    review_id = f"REV-{uuid.uuid4().hex[:8]}"

    dynamo = DynamoMCP()
    dynamo.put_clinician_review(
        review_id=review_id,
        data={
            "case_id": case_id,
            "plan_id": plan_id,
            "reviewer_id": reviewer_id,
            "action": action,
            "modifications": modifications,
            "notes": notes,
            "sections_reviewed": body.get("sections_reviewed", []),
            "approved_sections": body.get("approved_sections", []),
            "flagged_sections": body.get("flagged_sections", []),
        },
    )

    status_map = {
        "approved": "approved",
        "modified": "approved",
        "rejected": "rejected",
        "partial_approved": "pending_review",
    }
    dynamo.update_plan_status(plan_id, status_map[action])

    audit = AuditMCP()
    audit.log_clinician_action(
        case_id=case_id,
        reviewer_id=reviewer_id,
        action=action,
        notes=notes,
    )

    return _response(200, {
        "review_id": review_id,
        "case_id": case_id,
        "action": action,
        "plan_status": status_map[action],
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
