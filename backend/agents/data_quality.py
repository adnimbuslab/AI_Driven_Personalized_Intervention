"""Data Quality Agent — Validates completeness, generates follow-up questions (BR-003)."""

from backend.agents.base_agent import BaseAgent
from backend.config import Config


REQUIRED_FIELDS = [
    "age_years", "age_months", "gender",
    "screening_tool", "ados2_social_affect", "ados2_rrb",
    "primary_domain",
]

DESIRED_FIELDS = [
    "support_level", "diagnosis", "secondary_domain",
    "home_language", "primary_setting", "referral_source",
    "cognitive_verbal_percentile", "cognitive_nonverbal_percentile",
    "adaptive_composite_percentile",
    "strength_domains", "gap_domains", "family_priorities",
    "current_services",
]


class DataQualityAgent(BaseAgent):
    agent_id = "data-quality"
    step_number = 3

    def process(self, state: dict) -> dict:
        inputs = state.get("structured_inputs") or {}
        follow_up_round = state.get("follow_up_round", 0)

        present_required = sum(1 for f in REQUIRED_FIELDS if inputs.get(f) is not None)
        present_desired = sum(1 for f in DESIRED_FIELDS if inputs.get(f) is not None)
        total = len(REQUIRED_FIELDS) + len(DESIRED_FIELDS)
        present_total = present_required + present_desired
        quality_score = present_total / total if total > 0 else 0

        missing_required = [f for f in REQUIRED_FIELDS if inputs.get(f) is None]
        missing_desired = [f for f in DESIRED_FIELDS if inputs.get(f) is None]

        threshold = Config.DATA_COMPLETENESS_THRESHOLD

        if quality_score >= threshold and not missing_required:
            return {
                "data_quality_score": quality_score,
                "data_quality_gaps": missing_desired,
                "data_quality_status": "VALIDATED",
                "workflow_status": "DATA_VALIDATION",
                "current_step": self.agent_id,
                "confidence_score": quality_score,
            }

        if follow_up_round >= Config.MAX_FOLLOWUP_ROUNDS:
            self.workflow.trigger_escalation(
                case_id=state.get("case_id", ""),
                agent_id=self.agent_id,
                reason=f"Data incomplete after {follow_up_round} follow-up rounds. Missing required: {missing_required}",
            )
            return {
                "data_quality_score": quality_score,
                "data_quality_gaps": missing_required + missing_desired,
                "data_quality_status": "INCOMPLETE",
                "workflow_status": "ABSTAINED",
                "current_step": self.agent_id,
                "confidence_score": quality_score,
            }

        questions = self._generate_follow_up_questions(missing_required, missing_desired)
        return {
            "data_quality_score": quality_score,
            "data_quality_gaps": missing_required + missing_desired,
            "data_quality_status": "FOLLOW_UP",
            "follow_up_round": follow_up_round + 1,
            "follow_up_questions": questions,
            "workflow_status": "FOLLOW_UP",
            "current_step": self.agent_id,
            "confidence_score": quality_score,
        }

    def _generate_follow_up_questions(self, missing_required: list, missing_desired: list) -> list:
        field_questions = {
            "age_years": "What is the child's age?",
            "age_months": "What is the child's age in months?",
            "gender": "What is the child's gender?",
            "screening_tool": "Which screening tool was used (e.g., ADOS-2, M-CHAT-R, CARS-2)?",
            "ados2_social_affect": "What was the ADOS-2 Social Affect score?",
            "ados2_rrb": "What was the ADOS-2 Restricted/Repetitive Behavior score?",
            "primary_domain": "What is the primary developmental domain of concern?",
            "support_level": "What DSM-5 ASD support level has been assigned (Level 1, 2, or 3)?",
            "home_language": "What is the primary language spoken at home?",
            "family_priorities": "What are the family's main priorities for intervention?",
            "current_services": "What services or therapies is the child currently receiving?",
        }
        questions = []
        for field in missing_required[:3]:
            questions.append(field_questions.get(field, f"Please provide information for: {field}"))
        if len(questions) < 3:
            for field in missing_desired[:3 - len(questions)]:
                if field in field_questions:
                    questions.append(field_questions[field])
        return questions
