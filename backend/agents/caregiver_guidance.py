"""Caregiver Guidance Agent — Generates plain-language recommendations for parents (BR-007)."""

from backend.agents.base_agent import BaseAgent

CAREGIVER_SCHEMA = {
    "type": "object",
    "properties": {
        "language_preference": {"type": "string"},
        "reading_level": {"type": "string"},
        "activities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "activity": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                    "daily_routine_link": {"type": "string"},
                    "estimated_time_minutes": {"type": "integer"},
                    "materials_needed": {"type": "string"},
                },
            },
        },
        "general_strategies": {"type": "array", "items": {"type": "string"}},
        "strength_based_encouragement": {"type": "string"},
        "progress_tracking_tips": {"type": "array", "items": {"type": "string"}},
        "confidence_score": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a caregiver guidance specialist for families of children with autism.

Convert the professional intervention plan into plain-language guidance that any parent or caregiver can understand and follow.

RULES:
1. Use simple, jargon-free language (Grade 5-6 reading level)
2. Provide practical, home-based activities families can do daily
3. Link activities to daily routines (mealtime, bath time, play time, bedtime, morning routine)
4. Consider the family's cultural context and primary language
5. Consider available resources — include low-cost/no-cost options
6. Include sibling involvement opportunities where possible
7. Start with strength-based encouragement — what the child CAN do
8. Include simple progress tracking suggestions

NEVER use clinical jargon without explanation.
NEVER generate diagnostic statements.
Frame everything positively — focus on growth and celebration of small wins."""


class CaregiverGuidanceAgent(BaseAgent):
    agent_id = "caregiver-guidance"
    step_number = 12

    def process(self, state: dict) -> dict:
        profile = state.get("child_profile", {})
        guidelines = state.get("intervention_guidelines", [])
        goals = state.get("smart_goals", [])
        milestones = state.get("milestones", [])
        inputs = state.get("structured_inputs", {})

        home_language = inputs.get("home_language", "English")
        family_context = profile.get("family_context", {})

        user_prompt = (
            f"Generate caregiver guidance for this child's family:\n\n"
            f"Child Profile:\n"
            f"  Age: {profile.get('age_description', 'Unknown')}\n"
            f"  Strengths: {profile.get('strengths', [])}\n"
            f"  Support Areas: {profile.get('support_areas', [])}\n"
            f"  Home Language: {home_language}\n"
            f"  Family Context: {family_context}\n\n"
            f"Intervention Domains:\n"
        )
        for g in guidelines:
            user_prompt += (
                f"  - {g.get('domain', '?')}: {', '.join(g.get('focus_sub_domains', []))}\n"
                f"    Approaches: {', '.join(g.get('evidence_based_approaches', []))}\n"
                f"    Home Activities: {g.get('home_activities', [])}\n"
            )

        user_prompt += f"\nSMART Goals Summary:\n"
        for goal in goals[:6]:
            user_prompt += f"  - {goal.get('domain', '?')}: {goal.get('goal_text', 'N/A')}\n"

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=CAREGIVER_SCHEMA,
        )

        result["language_preference"] = home_language

        plan_id = f"PLAN-{state.get('case_id', 'unknown')}"
        self.dynamo.put_intervention_plan(
            plan_id=plan_id,
            plan_data={
                "child_id": state.get("child_id", ""),
                "case_id": state.get("case_id", ""),
                "status": "pending_review",
                "guidelines": guidelines,
                "smart_goals": goals,
                "milestones": milestones,
                "caregiver_guidance": result,
                "domain_priorities": state.get("domain_priorities", []),
                "domain_analysis": state.get("domain_analysis", []),
                "bias_check_result": {
                    "status": state.get("bias_check_status"),
                    "concerns": state.get("bias_concerns", []),
                },
                "confidence_check_result": {
                    "decision": state.get("proceed_decision"),
                    "reason": state.get("abstention_reason"),
                },
            },
        )

        return {
            "caregiver_guidance": result,
            "plan_id": plan_id,
            "workflow_status": "CAREGIVER_GUIDANCE",
            "current_step": self.agent_id,
            "confidence_score": result.get("confidence_score", 0.85),
        }
