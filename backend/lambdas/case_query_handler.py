"""Case query handler — Handles GET endpoints for case data, plans, and audit."""

import json
from backend.mcp_servers.dynamo_mcp import DynamoMCP
from backend.mcp_servers.audit_mcp import AuditMCP
from backend.config import Config


def handler(event, context):
    path = event.get("path", "")
    case_id = event.get("pathParameters", {}).get("case_id", "")

    dynamo = DynamoMCP()
    audit = AuditMCP()

    if path.endswith("/audit"):
        trail = audit.get_case_audit_trail(case_id)
        return _response(200, {"case_id": case_id, "events": trail})

    if path.endswith("/plan/profile"):
        profile = dynamo.get_child_profile(case_id.replace("AIG-", "CH-").rsplit("-", 1)[-1])
        if not profile:
            profiles = dynamo.query_by_case(case_id, Config.TABLE_CHILD_PROFILES)
            profile = profiles[0] if profiles else None
        return _response(200, profile or {"error": "Profile not found"})

    if path.endswith("/plan") or path.endswith("/plan/guidelines") or path.endswith("/plan/goals") or path.endswith("/plan/caregiver") or path.endswith("/plan/domains"):
        plan_id = f"PLAN-{case_id}"
        plan = dynamo.get_intervention_plan(plan_id)
        if not plan:
            return _response(404, {"error": "Plan not found"})

        if path.endswith("/guidelines"):
            return _response(200, {"guidelines": plan.get("guidelines", [])})
        if path.endswith("/goals"):
            return _response(200, {"goals": plan.get("smart_goals", [])})
        if path.endswith("/caregiver"):
            return _response(200, plan.get("caregiver_guidance", {}))
        if path.endswith("/domains"):
            return _response(200, {"domain_priorities": plan.get("domain_priorities", [])})
        return _response(200, plan)

    if path.endswith("/status"):
        plans = dynamo.query_by_case(case_id, Config.TABLE_INTERVENTION_PLANS)
        latest = plans[-1] if plans else {}
        return _response(200, {
            "case_id": case_id,
            "plan_status": latest.get("status", "unknown"),
            "plan_id": latest.get("plan_id"),
        })

    if case_id:
        profiles = dynamo.query_by_case(case_id, Config.TABLE_CHILD_PROFILES)
        plans = dynamo.query_by_case(case_id, Config.TABLE_INTERVENTION_PLANS)
        return _response(200, {
            "case_id": case_id,
            "profiles": profiles,
            "plans": [{"plan_id": p.get("plan_id"), "status": p.get("status")} for p in plans],
        })

    pending = dynamo.query_plans_by_status("pending_review")
    return _response(200, {"cases": pending})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
