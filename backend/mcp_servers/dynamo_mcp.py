"""DynamoDB MCP Server — CRUD operations for all 6 data tables."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from boto3.dynamodb.conditions import Key

from backend.config import Config
from backend.mcp_servers.base_mcp import BaseMCP


def _sanitize_for_dynamo(obj: Any) -> Any:
    """Convert floats to Decimals and strip empty strings for DynamoDB."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _sanitize_for_dynamo(v) for k, v in obj.items() if v != ""}
    if isinstance(obj, list):
        return [_sanitize_for_dynamo(v) for v in obj]
    return obj


def _deserialize(obj: Any) -> Any:
    """Convert Decimals back to floats for JSON compatibility."""
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    if isinstance(obj, dict):
        return {k: _deserialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deserialize(v) for v in obj]
    return obj


class DynamoMCP(BaseMCP):

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # --- ChildProfiles ---

    def get_child_profile(self, child_id: str) -> Optional[dict]:
        table = self._get_table(Config.TABLE_CHILD_PROFILES)
        resp = table.get_item(Key={"child_id": child_id})
        item = resp.get("Item")
        return _deserialize(item) if item else None

    def put_child_profile(self, child_id: str, profile_data: dict) -> dict:
        table = self._get_table(Config.TABLE_CHILD_PROFILES)
        item = {"child_id": child_id, **profile_data}
        item.setdefault("created_at", self._now())
        table.put_item(Item=_sanitize_for_dynamo(item))
        return {"child_id": child_id, "status": "saved"}

    # --- ScreeningInputs ---

    def get_screening_inputs(self, child_id: str) -> list[dict]:
        table = self._get_table(Config.TABLE_SCREENING_INPUTS)
        resp = table.query(
            IndexName="child_id-index",
            KeyConditionExpression=Key("child_id").eq(child_id),
        )
        return [_deserialize(item) for item in resp.get("Items", [])]

    def put_screening_input(self, assessment_id: str, data: dict) -> dict:
        table = self._get_table(Config.TABLE_SCREENING_INPUTS)
        item = {"assessment_id": assessment_id, **data}
        item.setdefault("assessment_date", self._now())
        table.put_item(Item=_sanitize_for_dynamo(item))
        return {"assessment_id": assessment_id, "status": "saved"}

    # --- InterventionPlans ---

    def get_intervention_plan(self, plan_id: str) -> Optional[dict]:
        table = self._get_table(Config.TABLE_INTERVENTION_PLANS)
        resp = table.get_item(Key={"plan_id": plan_id})
        item = resp.get("Item")
        return _deserialize(item) if item else None

    def put_intervention_plan(self, plan_id: str, plan_data: dict) -> dict:
        table = self._get_table(Config.TABLE_INTERVENTION_PLANS)
        item = {"plan_id": plan_id, **plan_data}
        item.setdefault("created_at", self._now())
        table.put_item(Item=_sanitize_for_dynamo(item))
        return {"plan_id": plan_id, "status": "saved"}

    def update_plan_status(self, plan_id: str, status: str) -> dict:
        table = self._get_table(Config.TABLE_INTERVENTION_PLANS)
        table.update_item(
            Key={"plan_id": plan_id},
            UpdateExpression="SET #s = :s, updated_at = :t",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": status, ":t": self._now()},
        )
        return {"plan_id": plan_id, "status": status}

    # --- AgentOutputs ---

    def get_agent_output(self, output_id: str) -> Optional[dict]:
        table = self._get_table(Config.TABLE_AGENT_OUTPUTS)
        resp = table.get_item(Key={"output_id": output_id})
        item = resp.get("Item")
        return _deserialize(item) if item else None

    def put_agent_output(self, output_id: str, data: dict) -> dict:
        table = self._get_table(Config.TABLE_AGENT_OUTPUTS)
        item = {"output_id": output_id, **data}
        item.setdefault("timestamp", self._now())
        table.put_item(Item=_sanitize_for_dynamo(item))
        return {"output_id": output_id, "status": "saved"}

    # --- ClinicianReviews ---

    def get_clinician_review(self, review_id: str) -> Optional[dict]:
        table = self._get_table(Config.TABLE_CLINICIAN_REVIEWS)
        resp = table.get_item(Key={"review_id": review_id})
        item = resp.get("Item")
        return _deserialize(item) if item else None

    def put_clinician_review(self, review_id: str, data: dict) -> dict:
        table = self._get_table(Config.TABLE_CLINICIAN_REVIEWS)
        item = {"review_id": review_id, **data}
        item.setdefault("timestamp", self._now())
        table.put_item(Item=_sanitize_for_dynamo(item))
        return {"review_id": review_id, "status": "saved"}

    # --- Cross-table queries ---

    def query_by_case(self, case_id: str, table_name: str) -> list[dict]:
        table = self._get_table(table_name)
        index_map = {
            Config.TABLE_CHILD_PROFILES: "case_id-index",
            Config.TABLE_INTERVENTION_PLANS: "case_id-index",
            Config.TABLE_AGENT_OUTPUTS: "case_id-agent-index",
            Config.TABLE_AUDIT_EVENTS: "case_id-time-index",
            Config.TABLE_CLINICIAN_REVIEWS: "case_id-index",
        }
        index_name = index_map.get(table_name)
        if not index_name:
            return []
        resp = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key("case_id").eq(case_id),
        )
        return [_deserialize(item) for item in resp.get("Items", [])]

    def query_plans_by_status(self, status: str) -> list[dict]:
        table = self._get_table(Config.TABLE_INTERVENTION_PLANS)
        resp = table.scan(
            FilterExpression="#s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": status},
        )
        return [_deserialize(item) for item in resp.get("Items", [])]
