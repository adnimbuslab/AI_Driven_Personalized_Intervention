"""Audit MCP Server — Immutable audit event logging and querying."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from boto3.dynamodb.conditions import Key

from backend.config import Config
from backend.mcp_servers.base_mcp import BaseMCP


class AuditMCP(BaseMCP):

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def log_event(
        self,
        case_id: str,
        agent_id: str,
        event_type: str,
        action: str,
        confidence_score: Optional[float] = None,
        input_hash: Optional[str] = None,
        output_hash: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        table = self._get_table(Config.TABLE_AUDIT_EVENTS)
        event_id = str(uuid.uuid4())
        timestamp = self._now()

        item = {
            "event_id": event_id,
            "case_id": case_id,
            "agent_id": agent_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "action": action,
            "escalated": False,
            "human_review_required": False,
        }

        if confidence_score is not None:
            from decimal import Decimal
            item["confidence_score"] = Decimal(str(confidence_score))
        if input_hash:
            item["input_hash"] = input_hash
        if output_hash:
            item["output_hash"] = output_hash
        if metadata:
            from backend.mcp_servers.dynamo_mcp import _sanitize_for_dynamo
            item["metadata"] = _sanitize_for_dynamo(metadata)

        table.put_item(Item=item)
        return {"event_id": event_id, "timestamp": timestamp}

    def get_case_audit_trail(self, case_id: str) -> list[dict]:
        table = self._get_table(Config.TABLE_AUDIT_EVENTS)
        resp = table.query(
            IndexName="case_id-time-index",
            KeyConditionExpression=Key("case_id").eq(case_id),
            ScanIndexForward=True,
        )
        from backend.mcp_servers.dynamo_mcp import _deserialize
        return [_deserialize(item) for item in resp.get("Items", [])]

    def get_agent_audit_trail(self, agent_id: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> list[dict]:
        table = self._get_table(Config.TABLE_AUDIT_EVENTS)
        key_expr = Key("agent_id").eq(agent_id)
        if from_date and to_date:
            key_expr = key_expr & Key("timestamp").between(from_date, to_date)
        elif from_date:
            key_expr = key_expr & Key("timestamp").gte(from_date)

        resp = table.query(
            IndexName="agent_id-time-index",
            KeyConditionExpression=key_expr,
            ScanIndexForward=True,
        )
        from backend.mcp_servers.dynamo_mcp import _deserialize
        return [_deserialize(item) for item in resp.get("Items", [])]

    def log_state_transition(self, case_id: str, from_state: str, to_state: str, trigger: str) -> dict:
        return self.log_event(
            case_id=case_id,
            agent_id="workflow-engine",
            event_type="STATE_TRANSITION",
            action=f"State: {from_state} -> {to_state}",
            metadata={"from_state": from_state, "to_state": to_state, "trigger": trigger},
        )

    def log_escalation(self, case_id: str, agent_id: str, reason: str, target: Optional[str] = None) -> dict:
        table = self._get_table(Config.TABLE_AUDIT_EVENTS)
        event_id = str(uuid.uuid4())
        timestamp = self._now()

        item = {
            "event_id": event_id,
            "case_id": case_id,
            "agent_id": agent_id,
            "timestamp": timestamp,
            "event_type": "ESCALATION",
            "action": f"Escalated: {reason}",
            "escalated": True,
            "human_review_required": True,
            "metadata": {"reason": reason},
        }
        if target:
            item["metadata"]["target_reviewer"] = target

        table.put_item(Item=item)
        return {"event_id": event_id, "timestamp": timestamp}

    def log_clinician_action(self, case_id: str, reviewer_id: str, action: str, notes: Optional[str] = None) -> dict:
        return self.log_event(
            case_id=case_id,
            agent_id=reviewer_id,
            event_type="CLINICIAN_REVIEW",
            action=action,
            metadata={"reviewer_id": reviewer_id, "review_action": action, "notes": notes or ""},
        )
