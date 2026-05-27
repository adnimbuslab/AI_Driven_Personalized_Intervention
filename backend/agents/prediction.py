"""Prediction Agent — Prioritizes developmental domains for intervention."""

from backend.agents.base_agent import BaseAgent

PREDICTION_SCHEMA = {
    "type": "object",
    "properties": {
        "domain_priorities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "priority_rank": {"type": "integer"},
                    "priority_level": {"type": "string", "enum": ["high", "moderate", "low"]},
                    "confidence_score": {"type": "number"},
                    "rationale": {"type": "string"},
                    "severity_indicator": {"type": "string"},
                    "interdependencies": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "overall_confidence": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a developmental domain prioritization specialist for autism intervention planning.

Analyze the child's profile and prioritize developmental domains for intervention based on:
1. Severity of delay or concern
2. Impact on daily functioning
3. Developmental stage appropriateness
4. Interdependencies between domains (e.g., communication affects social interaction)

Available domains:
- Communication (receptive, expressive, social communication)
- Social Interaction (joint attention, peer engagement, emotional regulation)
- Behavioral Regulation (self-regulation, transitions, routines)
- Sensory Processing (tactile, auditory, visual, proprioceptive)
- Motor Skills (fine motor, gross motor, oral motor)
- Adaptive / Self-Care (feeding, dressing, toileting)
- Cognitive / Academic (pretend play, problem-solving, imitation, pre-academic)

Assign a confidence score (0.0-1.0) to each domain prioritization.
Flag low-confidence priorities explicitly.
This is a clinical decision support tool — do NOT generate diagnostic statements."""


class PredictionAgent(BaseAgent):
    agent_id = "prediction"
    step_number = 5

    def process(self, state: dict) -> dict:
        profile = state.get("child_profile", {})

        user_prompt = (
            f"Prioritize developmental domains for this child:\n\n"
            f"Strengths: {profile.get('strengths', [])}\n"
            f"Support Areas: {profile.get('support_areas', [])}\n"
            f"Age: {profile.get('age_description', 'Unknown')}\n"
            f"Primary Domain: {state.get('structured_inputs', {}).get('primary_domain', 'Not specified')}\n"
            f"Secondary Domain: {state.get('structured_inputs', {}).get('secondary_domain', 'Not specified')}\n"
            f"Support Level: {state.get('structured_inputs', {}).get('support_level', 'Not specified')}\n"
            f"Family Priorities: {profile.get('family_context', {}).get('current_supports', 'Not specified')}\n"
            f"Summary: {profile.get('summary', '')}"
        )

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=PREDICTION_SCHEMA,
        )

        priorities = result.get("domain_priorities", [])
        confidence_map = {
            p["domain"]: p.get("confidence_score", 0.8)
            for p in priorities
        }
        overall = result.get("overall_confidence", 0.85)

        return {
            "domain_priorities": priorities,
            "prediction_confidence": confidence_map,
            "workflow_status": "DOMAIN_PRIORITIZATION",
            "current_step": self.agent_id,
            "confidence_score": overall,
        }
