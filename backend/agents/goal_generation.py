"""Goal Generation Agent — Creates SMART developmental goals (BR-010)."""

from backend.agents.base_agent import BaseAgent

GOAL_SCHEMA = {
    "type": "object",
    "properties": {
        "goals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "sub_domain": {"type": "string"},
                    "goal_type": {"type": "string", "enum": ["short_term", "long_term"]},
                    "goal_text": {"type": "string"},
                    "baseline_percent": {"type": "number"},
                    "target_percent": {"type": "number"},
                    "measurement_frequency": {"type": "string"},
                    "measurement_method": {"type": "string"},
                    "weeks_duration": {"type": "integer"},
                    "associated_guideline": {"type": "string"},
                    "smart_check": {
                        "type": "object",
                        "properties": {
                            "specific": {"type": "boolean"},
                            "measurable": {"type": "boolean"},
                            "achievable": {"type": "boolean"},
                            "relevant": {"type": "boolean"},
                            "time_bound": {"type": "boolean"},
                        },
                    },
                    "confidence_score": {"type": "number"},
                },
            },
        },
        "overall_confidence": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a SMART goal generation specialist for autism intervention planning.

Convert intervention guidelines into structured SMART developmental goals.

EVERY goal MUST follow the SMART format:
- Specific: Clearly defines what the child will do
- Measurable: Includes observable criteria (e.g., "in 3 out of 5 opportunities")
- Achievable: Appropriate for the child's current level
- Relevant: Directly tied to the child's profile and priorities
- Time-bound: Includes a target timeframe

Generate both short-term goals (4-12 weeks) and long-term goals (6-12 months).

EXAMPLE of an acceptable SMART goal:
"[Child] will use 2-word combinations to make requests in at least 3 out of 5 opportunities during structured play activities, as measured by clinician observation, within 10 weeks."

EXAMPLE of an UNACCEPTABLE goal:
"Improve communication in 6 months" — This is NOT specific, NOT measurable.

Include baseline_percent (current performance) and target_percent (target performance).
Link each goal to its corresponding guideline.
This is a clinical decision support tool — NEVER generate diagnostic statements."""


class GoalGenerationAgent(BaseAgent):
    agent_id = "goal-generation"
    step_number = 10

    def process(self, state: dict) -> dict:
        guidelines = state.get("intervention_guidelines", [])
        profile = state.get("child_profile", {})
        domain_analysis = state.get("domain_analysis", [])

        user_prompt = (
            f"Generate SMART goals for this child based on the intervention guidelines:\n\n"
            f"Child Profile:\n"
            f"  Age: {profile.get('age_description', 'Unknown')}\n"
            f"  Strengths: {profile.get('strengths', [])}\n"
            f"  Support Areas: {profile.get('support_areas', [])}\n\n"
            f"Intervention Guidelines:\n"
        )
        for g in guidelines:
            user_prompt += (
                f"\nDomain: {g.get('domain', 'Unknown')} ({g.get('guideline_id', '')})\n"
                f"  Approaches: {', '.join(g.get('evidence_based_approaches', []))}\n"
                f"  Focus: {', '.join(g.get('focus_sub_domains', []))}\n"
                f"  Intensity: {g.get('intervention_intensity', 'N/A')}\n"
            )

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=GOAL_SCHEMA,
        )

        goals = result.get("goals", [])
        child_id = state.get("child_id", "")
        for i, goal in enumerate(goals):
            goal["goal_id"] = f"GOAL-{child_id}-{i+1}"
            goal["status"] = "active"

        return {
            "smart_goals": goals,
            "workflow_status": "GOAL_GENERATION",
            "current_step": self.agent_id,
            "confidence_score": result.get("overall_confidence", 0.85),
        }
