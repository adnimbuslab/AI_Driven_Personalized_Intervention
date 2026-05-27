"""Profile Synthesis Agent — Builds unified child profile from structured inputs."""

import json
from backend.agents.base_agent import BaseAgent

PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "child_id": {"type": "string"},
        "age_description": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "support_areas": {"type": "array", "items": {"type": "string"}},
        "developmental_history": {"type": "string"},
        "family_context": {
            "type": "object",
            "properties": {
                "primary_language": {"type": "string"},
                "home_environment": {"type": "string"},
                "current_supports": {"type": "string"},
                "cultural_notes": {"type": "string"},
            },
        },
        "intervention_history": {"type": "array", "items": {"type": "string"}},
        "environmental_factors": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
        "confidence_score": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a child development specialist synthesizing a unified profile for a child with autism.

Build a comprehensive profile that includes:
1. The child's STRENGTHS (not just deficits) — what they are good at, what they enjoy
2. Areas requiring support across developmental domains
3. Family context: language, home environment, cultural background, available support
4. Intervention history: current and past therapies
5. Environmental factors relevant to intervention planning

Be strength-based — always lead with what the child CAN do.
This is a clinical decision support tool. NEVER generate diagnostic statements.
Use specific observations from the data, not generic descriptions."""


class ProfileSynthesisAgent(BaseAgent):
    agent_id = "profile-synthesis"
    step_number = 4

    def process(self, state: dict) -> dict:
        inputs = state.get("structured_inputs") or {}
        child_id = state.get("child_id", "")

        user_prompt = self._build_prompt(child_id, inputs)

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=PROFILE_SCHEMA,
        )

        result["child_id"] = child_id
        confidence = result.get("confidence_score", 0.85)

        profile_data = {
            **result,
            "case_id": state.get("case_id", ""),
            "age_years": inputs.get("age_years"),
            "age_months": inputs.get("age_months"),
            "gender": inputs.get("gender"),
            "support_level": inputs.get("support_level"),
            "diagnosis": inputs.get("diagnosis"),
            "primary_domain": inputs.get("primary_domain"),
            "secondary_domain": inputs.get("secondary_domain"),
            "home_language": inputs.get("home_language"),
            "screening_tool": inputs.get("screening_tool"),
            "primary_setting": inputs.get("primary_setting"),
            "current_services": inputs.get("current_services"),
            "status": "draft",
        }
        self.dynamo.put_child_profile(child_id=child_id, profile_data=profile_data)

        return {
            "child_profile": result,
            "profile_confidence": confidence,
            "workflow_status": "PROFILE_BUILDING",
            "current_step": self.agent_id,
            "confidence_score": confidence,
        }

    def _build_prompt(self, child_id: str, inputs: dict) -> str:
        return (
            f"Build a unified profile for child {child_id}.\n\n"
            f"Demographics: Age {inputs.get('age_years', '?')} years {inputs.get('age_months', '?')} months, "
            f"Gender: {inputs.get('gender', 'Not specified')}\n"
            f"Support Level: {inputs.get('support_level', 'Not specified')}\n"
            f"Screening Tool: {inputs.get('screening_tool', 'Not specified')}\n"
            f"ADOS-2 SA: {inputs.get('ados2_social_affect', 'N/A')}, RRB: {inputs.get('ados2_rrb', 'N/A')}\n"
            f"Primary Domain: {inputs.get('primary_domain', 'Not specified')}\n"
            f"Secondary Domain: {inputs.get('secondary_domain', 'Not specified')}\n"
            f"Strengths: {inputs.get('strength_domains', 'Not specified')}\n"
            f"Gaps: {inputs.get('gap_domains', 'Not specified')}\n"
            f"Home Language: {inputs.get('home_language', 'Not specified')}\n"
            f"Family Priorities: {inputs.get('family_priorities', 'Not specified')}\n"
            f"Current Services: {inputs.get('current_services', 'Not specified')}\n"
            f"Areas of Concern: {inputs.get('areas_of_concern', [])}\n"
            f"Clinician Observations: {inputs.get('clinician_observations', 'None provided')}"
        )
