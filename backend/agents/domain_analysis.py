"""Domain Analysis Agent — Breaks prioritized domains into specific focus areas."""

from backend.agents.base_agent import BaseAgent

DOMAIN_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "domain_analyses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "focus_areas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "focus_area": {"type": "string"},
                                "current_baseline": {"type": "string"},
                                "target_direction": {"type": "string"},
                                "developmental_stage_notes": {"type": "string"},
                                "interdependencies": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                },
            },
        },
        "confidence_score": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a developmental domain analysis specialist.

For each prioritized domain, break it into specific, actionable focus areas:
1. Identify 2-4 focus areas per domain
2. For each focus area, describe the current baseline (from the child's profile)
3. Describe the target direction (what improvement looks like)
4. Note developmental stage considerations
5. Identify interdependencies between focus areas

Be specific to THIS child — use data from their profile, not generic descriptions.
This is a clinical decision support tool — do NOT generate diagnostic statements."""


class DomainAnalysisAgent(BaseAgent):
    agent_id = "domain-analysis"
    step_number = 7

    def process(self, state: dict) -> dict:
        profile = state.get("child_profile", {})
        priorities = state.get("domain_priorities", [])
        partial_domains = state.get("partial_proceed_domains")

        if partial_domains:
            priorities = [p for p in priorities if p.get("domain") in partial_domains]

        user_prompt = (
            f"Analyze these prioritized domains for the child:\n\n"
            f"Child Profile:\n"
            f"  Strengths: {profile.get('strengths', [])}\n"
            f"  Support Areas: {profile.get('support_areas', [])}\n"
            f"  Age: {profile.get('age_description', 'Unknown')}\n\n"
            f"Prioritized Domains:\n"
        )
        for p in priorities:
            user_prompt += (
                f"  - {p.get('domain', 'Unknown')} (Priority: {p.get('priority_level', '?')}, "
                f"Confidence: {p.get('confidence_score', '?')})\n"
                f"    Rationale: {p.get('rationale', 'N/A')}\n"
            )

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=DOMAIN_ANALYSIS_SCHEMA,
        )

        return {
            "domain_analysis": result.get("domain_analyses", []),
            "workflow_status": "DOMAIN_ANALYSIS",
            "current_step": self.agent_id,
            "confidence_score": result.get("confidence_score", 0.85),
        }
