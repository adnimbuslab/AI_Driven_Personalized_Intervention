"""Base agent class — all 12 agents inherit from this.

Provides MCP tool access, automatic audit logging, error handling, and confidence scoring.
"""

from typing import Any

from backend.mcp_servers.dynamo_mcp import DynamoMCP
from backend.mcp_servers.s3_mcp import S3MCP
from backend.mcp_servers.audit_mcp import AuditMCP
from backend.mcp_servers.llm_mcp import LlmMCP
from backend.mcp_servers.workflow_mcp import WorkflowMCP
from backend.utils.hashing import compute_hash


class BaseAgent:
    agent_id: str = "base"
    step_number: int = 0

    def __init__(self):
        self.dynamo = DynamoMCP()
        self.s3 = S3MCP()
        self.audit = AuditMCP()
        self.llm = LlmMCP()
        self.workflow = WorkflowMCP()

    def execute(self, state: dict) -> dict:
        """Main entry point called by LangGraph. Returns state update dict."""
        input_data = self._get_input(state)
        input_hash = compute_hash(input_data)

        try:
            result = self.process(state)
            output_hash = compute_hash(result)
            self._log_output(state, result, input_hash, output_hash)
            self._log_audit(state, input_hash, output_hash, result.get("confidence_score"))
            result["agent_outputs"] = [{
                "agent": self.agent_id,
                "step": self.step_number,
                "status": "completed",
                "confidence": result.get("confidence_score"),
            }]
            return result
        except Exception as e:
            self._log_error(state, e)
            return {
                "error": str(e),
                "workflow_status": "ESCALATED_TO_REVIEWER",
                "current_step": self.agent_id,
                "agent_outputs": [{
                    "agent": self.agent_id,
                    "step": self.step_number,
                    "status": "error",
                    "error": str(e),
                }],
                "escalation_history": [{
                    "agent": self.agent_id,
                    "reason": f"Agent error: {e}",
                }],
            }

    def process(self, state: dict) -> dict:
        """Override in subclass. Returns state update dict."""
        raise NotImplementedError

    def _get_input(self, state: dict) -> Any:
        return {
            "case_id": state.get("case_id"),
            "child_id": state.get("child_id"),
            "current_step": state.get("current_step"),
        }

    def _log_audit(self, state: dict, input_hash: str, output_hash: str, confidence: float = None) -> None:
        self.audit.log_event(
            case_id=state.get("case_id", "unknown"),
            agent_id=self.agent_id,
            event_type="AGENT_OUTPUT",
            action=f"{self.agent_id} completed step {self.step_number}",
            confidence_score=confidence,
            input_hash=input_hash,
            output_hash=output_hash,
        )

    def _log_output(self, state: dict, result: dict, input_hash: str, output_hash: str) -> None:
        case_id = state.get("case_id", "unknown")
        output_id = f"{case_id}-{self.agent_id}"
        self.dynamo.put_agent_output(
            output_id=output_id,
            data={
                "case_id": case_id,
                "agent_id": self.agent_id,
                "step_number": self.step_number,
                "output_data": result,
                "input_hash": input_hash,
                "output_hash": output_hash,
                "confidence_score": result.get("confidence_score"),
                "status": "completed",
            },
        )

    def _log_error(self, state: dict, error: Exception) -> None:
        self.audit.log_event(
            case_id=state.get("case_id", "unknown"),
            agent_id=self.agent_id,
            event_type="ERROR",
            action=f"{self.agent_id} failed: {error}",
            metadata={"error_type": type(error).__name__, "error_message": str(error)},
        )
