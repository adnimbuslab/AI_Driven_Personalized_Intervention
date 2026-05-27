"""Confidence & Abstention Agent — Reviews confidence levels, decides proceed/abstain (BR-004)."""

from backend.agents.base_agent import BaseAgent
from backend.config import Config


class ConfidenceAbstentionAgent(BaseAgent):
    agent_id = "confidence-abstention"
    step_number = 6

    def process(self, state: dict) -> dict:
        scores = {
            "data_quality": state.get("data_quality_score"),
            "profile_synthesis": state.get("profile_confidence"),
        }

        prediction_conf = state.get("prediction_confidence", {})
        if isinstance(prediction_conf, dict):
            for domain, score in prediction_conf.items():
                scores[f"prediction_{domain}"] = score

        default_threshold = Config.CONFIDENCE_THRESHOLD_DEFAULT
        below_threshold = {}
        above_threshold = {}

        for name, score in scores.items():
            if score is None:
                continue
            if score < default_threshold:
                below_threshold[name] = score
            else:
                above_threshold[name] = score

        critical_failures = [
            name for name in below_threshold
            if name in ("data_quality", "profile_synthesis")
        ]

        if critical_failures:
            reason = f"Critical confidence failures: {critical_failures} — scores: {below_threshold}"
            self.audit.log_event(
                case_id=state.get("case_id", ""),
                agent_id=self.agent_id,
                event_type="CONFIDENCE_CHECK",
                action=f"ABSTAIN: {reason}",
            )
            return {
                "proceed_decision": "ABSTAIN",
                "abstention_reason": reason,
                "workflow_status": "ABSTAINED",
                "current_step": self.agent_id,
                "confidence_score": min(below_threshold.values()) if below_threshold else 0,
            }

        if below_threshold:
            failed_domains = [
                name.replace("prediction_", "")
                for name in below_threshold
                if name.startswith("prediction_")
            ]
            safe_domains = [
                name.replace("prediction_", "")
                for name in above_threshold
                if name.startswith("prediction_")
            ]

            return {
                "proceed_decision": "PARTIAL_PROCEED",
                "partial_proceed_domains": safe_domains,
                "abstention_reason": f"Low confidence in domains: {failed_domains}",
                "workflow_status": "CONFIDENCE_CHECK",
                "current_step": self.agent_id,
                "confidence_score": sum(scores.values()) / len(scores) if scores else 0,
            }

        avg_confidence = sum(s for s in scores.values() if s is not None) / max(len(scores), 1)
        return {
            "proceed_decision": "PROCEED",
            "abstention_reason": None,
            "workflow_status": "CONFIDENCE_CHECK",
            "current_step": self.agent_id,
            "confidence_score": avg_confidence,
        }
