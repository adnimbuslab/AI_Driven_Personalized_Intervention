"""Review queue handler — Returns pending reviews for clinicians."""

import json
from backend.mcp_servers.dynamo_mcp import DynamoMCP


def handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    reviewer_id = query_params.get("reviewer_id", "")

    dynamo = DynamoMCP()
    pending = dynamo.query_plans_by_status("pending_review")

    reviews = []
    for plan in pending:
        reviews.append({
            "plan_id": plan.get("plan_id"),
            "case_id": plan.get("case_id"),
            "child_id": plan.get("child_id"),
            "status": plan.get("status"),
            "created_at": plan.get("created_at"),
            "domain_count": len(plan.get("guidelines", [])),
            "goal_count": len(plan.get("smart_goals", [])),
        })

    return _response(200, {"pending_reviews": reviews, "total": len(reviews)})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }
