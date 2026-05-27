"""Milestone Planning Agent — Creates time-bound milestones for each SMART goal."""

from backend.agents.base_agent import BaseAgent

MILESTONE_SCHEMA = {
    "type": "object",
    "properties": {
        "milestones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "goal_id": {"type": "string"},
                    "domain": {"type": "string"},
                    "total_weeks": {"type": "integer"},
                    "short_term_milestones": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "week": {"type": "integer"},
                                "target_percent": {"type": "number"},
                                "assistance_level": {"type": "string"},
                                "description": {"type": "string"},
                            },
                        },
                    },
                    "long_term_milestones": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "month": {"type": "integer"},
                                "target_percent": {"type": "number"},
                                "generalization_settings": {"type": "integer"},
                                "description": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
        "confidence_score": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a developmental milestone planning specialist.

Create time-bound milestones as checkpoints between each goal's baseline and target.

For each SMART goal, create:
1. Short-term milestones (every 2 weeks) showing incremental progress
   - Include expected assistance level at each milestone (hand-over-hand → partial physical → verbal → visual cue → independent)
   - Target percentages should increase gradually from baseline to target
2. Long-term milestones (monthly) showing generalization
   - Include how many settings the skill should generalize to
   - Target percentages approaching the final goal target

Consider:
- More severe delays → smaller milestone increments
- Child's demonstrated learning pace (from history if available)
- Typical developmental progressions

Milestones should be observable and celebratable — marking real progress.
This is a clinical decision support tool — NEVER generate diagnostic statements."""


class MilestonePlanningAgent(BaseAgent):
    agent_id = "milestone-planning"
    step_number = 11

    def process(self, state: dict) -> dict:
        goals = state.get("smart_goals", [])
        profile = state.get("child_profile", {})

        user_prompt = (
            f"Create milestones for these SMART goals:\n\n"
            f"Child: Age {profile.get('age_description', 'Unknown')}\n"
            f"Support Level: {state.get('structured_inputs', {}).get('support_level', 'Not specified')}\n\n"
            f"Goals:\n"
        )
        for goal in goals:
            user_prompt += (
                f"\n{goal.get('goal_id', 'Unknown')} — {goal.get('domain', '?')}/{goal.get('sub_domain', '?')}\n"
                f"  Goal: {goal.get('goal_text', 'N/A')}\n"
                f"  Baseline: {goal.get('baseline_percent', '?')}%\n"
                f"  Target: {goal.get('target_percent', '?')}%\n"
                f"  Duration: {goal.get('weeks_duration', '?')} weeks\n"
            )

        result = self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=MILESTONE_SCHEMA,
        )

        milestones = result.get("milestones", [])
        child_id = state.get("child_id", "")
        for i, ms in enumerate(milestones):
            ms["milestone_id"] = f"MS-{ms.get('goal_id', f'{child_id}-{i+1}')}"

        return {
            "milestones": milestones,
            "workflow_status": "MILESTONE_PLANNING",
            "current_step": self.agent_id,
            "confidence_score": result.get("confidence_score", 0.85),
        }
