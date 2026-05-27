"""Bias Monitoring Agent — Checks guidelines for demographic/cultural/language bias (BR-005, BR-007)."""

from backend.agents.base_agent import BaseAgent

BIAS_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "bias_check_status": {"type": "string", "enum": ["PASSED", "FLAGGED", "REVIEW_REQUIRED"]},
        "overall_score": {"type": "number"},
        "concerns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "bias_type": {"type": "string"},
                    "concern": {"type": "string"},
                    "affected_section": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "recommendation": {"type": "string"},
                },
            },
        },
    },
}

SYSTEM_PROMPT = """You are a bias monitoring specialist for autism intervention planning.
Review the intervention guidelines and check for these bias types:

1. DEMOGRAPHIC BIAS: Recommendations differ based on race, ethnicity, or gender
2. CULTURAL BIAS: Assumes Western cultural norms without considering the family's context
3. LANGUAGE BIAS: Assumes English fluency when the family speaks another language
4. SOCIOECONOMIC BIAS: Assumes resources (specialized toys, therapist availability) the family may not have
5. GEOGRAPHIC BIAS: Assumes urban service availability

If no bias is detected, set bias_check_status to "PASSED".
If concerns are found, set it to "FLAGGED" and list each concern with its type, affected section, severity, and recommendation.

This is a clinical decision support tool — it does not diagnose. Do not generate diagnostic statements."""


class BiasMonitoringAgent(BaseAgent):
    agent_id = "bias-monitoring"
    step_number = 9

    def process(self, state: dict) -> dict:
        guidelines = state.get("intervention_guidelines", [])
        profile = state.get("child_profile", {})

        user_prompt = (
            f"Child Profile:\n"
            f"- Home Language: {profile.get('home_language', 'Not specified')}\n"
            f"- Family Context: {profile.get('family_context', 'Not specified')}\n"
            f"- Primary Setting: {profile.get('primary_setting', 'Not specified')}\n"
            f"- Current Services: {profile.get('current_services', 'Not specified')}\n\n"
            f"Intervention Guidelines to Review:\n{self._format_guidelines(guidelines)}"
        )

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=BIAS_CHECK_SCHEMA,
        )

        status = result.get("bias_check_status", "PASSED")
        concerns = result.get("concerns", [])

        if status == "FLAGGED" and concerns:
            self.workflow.trigger_escalation(
                case_id=state.get("case_id", ""),
                agent_id=self.agent_id,
                reason=f"Bias detected: {len(concerns)} concern(s)",
            )

        return {
            "bias_check_status": status,
            "bias_concerns": concerns,
            "workflow_status": "BIAS_CHECK",
            "current_step": self.agent_id,
            "confidence_score": result.get("overall_score", 0.9),
        }

    def _format_guidelines(self, guidelines: list) -> str:
        parts = []
        for g in guidelines:
            parts.append(
                f"Domain: {g.get('domain', 'N/A')}\n"
                f"  Approaches: {', '.join(g.get('evidence_based_approaches', []))}\n"
                f"  Focus: {', '.join(g.get('focus_sub_domains', []))}\n"
                f"  Modality: {g.get('recommended_modality', 'N/A')}\n"
                f"  Env Modifications: {', '.join(g.get('environmental_modifications', []))}"
            )
        return "\n".join(parts) if parts else "No guidelines provided"
