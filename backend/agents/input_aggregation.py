"""Input Aggregation Agent — Extracts structured data from screening reports and documents."""

import json
from backend.agents.base_agent import BaseAgent

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "child_demographics": {
            "type": "object",
            "properties": {
                "age_years": {"type": "integer"},
                "age_months": {"type": "integer"},
                "gender": {"type": "string"},
            },
        },
        "screening_tool": {"type": "string"},
        "ados2_module": {"type": "string"},
        "ados2_social_affect": {"type": "number"},
        "ados2_rrb": {"type": "number"},
        "ados2_comparison_score": {"type": "string"},
        "areas_of_concern": {"type": "array", "items": {"type": "string"}},
        "clinician_observations": {"type": "string"},
        "family_information": {
            "type": "object",
            "properties": {
                "home_language": {"type": "string"},
                "home_environment": {"type": "string"},
                "cultural_notes": {"type": "string"},
            },
        },
        "prior_interventions": {"type": "array", "items": {"type": "string"}},
        "cognitive_verbal_percentile": {"type": "number"},
        "cognitive_nonverbal_percentile": {"type": "number"},
        "adaptive_composite_percentile": {"type": "number"},
        "extraction_confidence": {"type": "number"},
    },
}

SYSTEM_PROMPT = """You are a clinical data extraction specialist for autism screening reports.
Your task is to extract structured data from uploaded screening and assessment documents.

Extract all available fields. If a field is not present in the document, set it to null.
Be precise — only extract information that is explicitly stated in the document.

IMPORTANT: This is a clinical decision support tool. You must NEVER generate diagnostic statements.
You are extracting data, not interpreting or diagnosing."""


class InputAggregationAgent(BaseAgent):
    agent_id = "input-aggregation"
    step_number = 2

    def process(self, state: dict) -> dict:
        raw_inputs = state.get("raw_inputs") or {}
        documents = state.get("uploaded_documents") or []

        extracted_data = dict(raw_inputs)

        for doc_ref in documents:
            if isinstance(doc_ref, dict) and "content" in doc_ref:
                doc_extraction = self.llm.analyze_document(
                    document_content=doc_ref["content"],
                    extraction_schema=EXTRACTION_SCHEMA,
                )
                extracted_data = self._merge_extractions(extracted_data, doc_extraction)

        structured = self._build_structured_inputs(extracted_data)

        self.dynamo.put_screening_input(
            assessment_id=f"ASS-{state.get('child_id', 'unknown')}",
            data={"child_id": state.get("child_id", ""), **structured},
        )

        confidence = extracted_data.get("extraction_confidence", 0.8)
        return {
            "structured_inputs": structured,
            "workflow_status": "INPUT_COLLECTION",
            "current_step": self.agent_id,
            "confidence_score": confidence,
        }

    def _merge_extractions(self, base: dict, new: dict) -> dict:
        for key, value in new.items():
            if value is not None and key not in ("error",):
                if key not in base or base[key] is None:
                    base[key] = value
        return base

    def _build_structured_inputs(self, data: dict) -> dict:
        demographics = data.get("child_demographics", {})
        family = data.get("family_information", {})

        return {
            "age_years": demographics.get("age_years") or data.get("age_years"),
            "age_months": demographics.get("age_months") or data.get("age_months"),
            "gender": demographics.get("gender") or data.get("gender"),
            "screening_tool": data.get("screening_tool"),
            "ados2_module": data.get("ados2_module"),
            "ados2_social_affect": data.get("ados2_social_affect"),
            "ados2_rrb": data.get("ados2_rrb"),
            "ados2_comparison_score": data.get("ados2_comparison_score"),
            "primary_domain": data.get("primary_domain"),
            "secondary_domain": data.get("secondary_domain"),
            "support_level": data.get("support_level"),
            "diagnosis": data.get("diagnosis"),
            "home_language": family.get("home_language") or data.get("home_language"),
            "home_environment": family.get("home_environment"),
            "cultural_notes": family.get("cultural_notes"),
            "areas_of_concern": data.get("areas_of_concern", []),
            "clinician_observations": data.get("clinician_observations"),
            "prior_interventions": data.get("prior_interventions", []),
            "cognitive_verbal_percentile": data.get("cognitive_verbal_percentile"),
            "cognitive_nonverbal_percentile": data.get("cognitive_nonverbal_percentile"),
            "adaptive_composite_percentile": data.get("adaptive_composite_percentile"),
            "strength_domains": data.get("strength_domains"),
            "gap_domains": data.get("gap_domains"),
            "family_priorities": data.get("family_priorities"),
            "current_services": data.get("current_services"),
            "referral_source": data.get("referral_source"),
            "primary_setting": data.get("primary_setting"),
        }
