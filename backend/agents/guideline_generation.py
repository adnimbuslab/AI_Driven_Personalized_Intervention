"""Guideline Generation Agent — Generates personalized intervention guidelines (BR-006)."""

from backend.agents.base_agent import BaseAgent

GUIDELINE_SCHEMA = {
    "type": "object",
    "properties": {
        "guidelines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "priority": {"type": "string", "enum": ["high", "moderate", "low"]},
                    "intervention_intensity": {"type": "string", "enum": ["intensive", "moderate", "maintenance"]},
                    "recommended_frequency": {"type": "string"},
                    "evidence_based_approaches": {"type": "array", "items": {"type": "string"}},
                    "focus_sub_domains": {"type": "array", "items": {"type": "string"}},
                    "recommended_modality": {"type": "string"},
                    "session_duration_minutes": {"type": "integer"},
                    "environmental_modifications": {"type": "array", "items": {"type": "string"}},
                    "home_activities": {"type": "array", "items": {"type": "string"}},
                    "rationale": {"type": "string"},
                    "confidence_score": {"type": "number"},
                },
            },
        },
        "overall_confidence": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are an autism intervention guideline specialist.

Generate personalized intervention guidelines based on the child's profile and domain analysis.

For each domain, provide:
1. Evidence-based intervention approaches (ABA, ESDM, TEACCH, Sensory Integration, etc.)
2. Recommended frequency and intensity
3. Specific focus sub-domains
4. Delivery modality (parent-mediated, one-on-one, school-based, group)
5. Session duration
6. Environmental modifications
7. Home-based activity suggestions

CRITICAL RULES:
- Guidelines MUST be specific to THIS child — not generic ASD recommendations
- NEVER generate diagnostic statements
- Consider the family's cultural context and primary language
- Include approaches that match the family's available resources
- Reference evidence-based practices only

Evidence-based approaches to consider:
- Applied Behavior Analysis (ABA)
- Naturalistic Developmental Behavioral Interventions (NDBI)
- Early Start Denver Model (ESDM)
- TEACCH Structured Teaching
- AAC/PECS for communication
- Sensory Integration Therapy
- DIR/Floor Time
- Pivotal Response Training (PRT)
- Hanen Programs"""


class GuidelineGenerationAgent(BaseAgent):
    agent_id = "guideline-generation"
    step_number = 8

    def process(self, state: dict) -> dict:
        profile = state.get("child_profile", {})
        domain_analysis = state.get("domain_analysis", [])
        inputs = state.get("structured_inputs", {})

        user_prompt = (
            f"Generate intervention guidelines for this child:\n\n"
            f"Child Profile:\n"
            f"  Age: {profile.get('age_description', 'Unknown')}\n"
            f"  Support Level: {inputs.get('support_level', 'Not specified')}\n"
            f"  Strengths: {profile.get('strengths', [])}\n"
            f"  Support Areas: {profile.get('support_areas', [])}\n"
            f"  Home Language: {inputs.get('home_language', 'Not specified')}\n"
            f"  Family Context: {profile.get('family_context', {})}\n"
            f"  Current Services: {inputs.get('current_services', 'Not specified')}\n"
            f"  Primary Setting: {inputs.get('primary_setting', 'Not specified')}\n\n"
            f"Domain Analysis:\n"
        )
        for da in domain_analysis:
            user_prompt += f"\nDomain: {da.get('domain', 'Unknown')}\n"
            for fa in da.get("focus_areas", []):
                user_prompt += (
                    f"  Focus: {fa.get('focus_area', '')}\n"
                    f"  Baseline: {fa.get('current_baseline', '')}\n"
                    f"  Target: {fa.get('target_direction', '')}\n"
                )

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=GUIDELINE_SCHEMA,
        )

        guidelines = result.get("guidelines", [])
        child_id = state.get("child_id", "")
        for i, g in enumerate(guidelines):
            g["guideline_id"] = f"GL-{child_id}-{i+1}"

        confidence_map = {g["domain"]: g.get("confidence_score", 0.8) for g in guidelines}

        return {
            "intervention_guidelines": guidelines,
            "guideline_confidence": confidence_map,
            "workflow_status": "GUIDELINE_GENERATION",
            "current_step": self.agent_id,
            "confidence_score": result.get("overall_confidence", 0.85),
        }
