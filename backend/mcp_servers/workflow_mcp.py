"""Workflow MCP Server — State management, inter-agent coordination, confidence checks."""

from typing import Optional

from backend.config import Config
from backend.mcp_servers.base_mcp import BaseMCP


class WorkflowMCP(BaseMCP):

    def __init__(self):
        super().__init__()
        self._audit = None

    @property
    def audit(self):
        if self._audit is None:
            from backend.mcp_servers.audit_mcp import AuditMCP
            self._audit = AuditMCP()
        return self._audit

    def get_workflow_state(self, case_id: str) -> Optional[dict]:
        from backend.mcp_servers.dynamo_mcp import DynamoMCP, _deserialize
        dynamo = DynamoMCP()
        results = dynamo.query_by_case(case_id, Config.TABLE_AGENT_OUTPUTS)
        if not results:
            return None
        latest = sorted(results, key=lambda x: x.get("timestamp", ""), reverse=True)
        return _deserialize(latest[0]) if latest else None

    def update_workflow_state(self, case_id: str, new_state: str, agent_id: str) -> dict:
        self.audit.log_state_transition(
            case_id=case_id,
            from_state="",
            to_state=new_state,
            trigger=agent_id,
        )
        return {"case_id": case_id, "workflow_status": new_state, "updated_by": agent_id}

    def get_previous_agent_output(self, case_id: str, agent_id: str) -> Optional[dict]:
        from backend.mcp_servers.dynamo_mcp import DynamoMCP
        dynamo = DynamoMCP()
        output_id = f"{case_id}-{agent_id}"
        return dynamo.get_agent_output(output_id)

    def check_confidence_threshold(self, agent_id: str, confidence_score: float) -> dict:
        threshold = Config.get_confidence_threshold(agent_id)
        return {
            "meets_threshold": confidence_score >= threshold,
            "threshold": threshold,
            "actual": confidence_score,
            "agent_id": agent_id,
        }

    def trigger_escalation(self, case_id: str, agent_id: str, reason: str) -> dict:
        self.audit.log_escalation(case_id=case_id, agent_id=agent_id, reason=reason)
        self.update_workflow_state(case_id, "ESCALATED_TO_REVIEWER", agent_id)
        return {"case_id": case_id, "escalated": True, "reason": reason}

    def request_human_review(self, case_id: str, agent_id: str, review_data: dict) -> dict:
        self.audit.log_event(
            case_id=case_id,
            agent_id=agent_id,
            event_type="HUMAN_REVIEW_REQUESTED",
            action=f"Human review requested by {agent_id}",
            metadata=review_data,
        )
        return {"case_id": case_id, "review_requested": True, "requested_by": agent_id}
