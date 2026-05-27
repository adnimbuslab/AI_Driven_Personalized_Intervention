"""Ethics & Consent Agent — Verifies consent before any data processing (BR-002)."""

from backend.agents.base_agent import BaseAgent


class EthicsConsentAgent(BaseAgent):
    agent_id = "ethics-consent"
    step_number = 1

    def process(self, state: dict) -> dict:
        case_id = state.get("case_id", "")
        consent = state.get("consent_status")

        if consent == "GRANTED":
            self.audit.log_event(
                case_id=case_id,
                agent_id=self.agent_id,
                event_type="CONSENT_CHECK",
                action="Consent verified: GRANTED",
                confidence_score=1.0,
            )
            return {
                "consent_status": "GRANTED",
                "workflow_status": "CONSENT_GRANTED",
                "current_step": self.agent_id,
                "confidence_score": 1.0,
            }

        if consent == "DENIED":
            self.audit.log_event(
                case_id=case_id,
                agent_id=self.agent_id,
                event_type="CONSENT_CHECK",
                action="Consent denied — workflow blocked",
                confidence_score=1.0,
            )
            return {
                "consent_status": "DENIED",
                "workflow_status": "CONSENT_DENIED",
                "current_step": self.agent_id,
                "confidence_score": 1.0,
            }

        self.audit.log_event(
            case_id=case_id,
            agent_id=self.agent_id,
            event_type="CONSENT_CHECK",
            action="Consent pending — workflow paused",
            confidence_score=1.0,
        )
        return {
            "consent_status": "PENDING",
            "workflow_status": "CONSENT_PENDING",
            "current_step": self.agent_id,
            "confidence_score": 1.0,
        }
