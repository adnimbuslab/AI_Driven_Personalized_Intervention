"""
Helpers for Claude Code skills in the AI-Driven Personalized Intervention project.
Provides utilities for test validation, requirement tracing, and LocalStack checks.
"""

import json
import re
from typing import Optional


REQUIREMENT_PREFIXES = ["BR", "FR", "AR", "HITL", "API", "MCP", "DB", "FE", "NFR", "WF", "DEP", "TEST"]
CASE_ID_PATTERN = re.compile(r"^AIG-\d{4}-\d{4}$")

VALID_CASE_STATUSES = {
    "INITIATED",
    "CONSENT_PENDING",
    "CONSENT_GRANTED",
    "CONSENT_DENIED",
    "INPUT_COLLECTION",
    "DATA_VALIDATION",
    "PROFILE_BUILDING",
    "DOMAIN_PRIORITIZATION",
    "CONFIDENCE_CHECK",
    "ABSTAINED",
    "DOMAIN_ANALYSIS",
    "GUIDELINE_GENERATION",
    "BIAS_CHECK",
    "BIAS_FLAGGED",
    "GOAL_GENERATION",
    "MILESTONE_PLANNING",
    "CAREGIVER_GUIDANCE",
    "AWAITING_CLINICIAN_REVIEW",
    "APPROVED",
    "MODIFIED",
    "REJECTED",
    "PARTIAL_APPROVED",
    "ESCALATED_TO_REVIEWER",
    "ON_HOLD",
    "CLOSED",
}

VALID_WORKFLOW_AGENTS = {
    "input-aggregation",
    "profile-synthesis",
    "prediction",
    "domain-analysis",
    "guideline-generation",
    "goal-generation",
    "milestone-planning",
    "caregiver-guidance",
}

VALID_GOVERNANCE_AGENTS = {
    "ethics-consent",
    "data-quality",
    "bias-monitoring",
    "confidence-abstention",
}

VALID_AGENT_NAMES = VALID_WORKFLOW_AGENTS | VALID_GOVERNANCE_AGENTS

DEVELOPMENTAL_DOMAINS = {
    "communication",
    "social-interaction",
    "behavioral-regulation",
    "sensory-processing",
    "motor-skills",
    "adaptive-self-care",
    "play-cognitive",
}


def validate_case_id(case_id: str) -> bool:
    return bool(CASE_ID_PATTERN.match(case_id))


def validate_case_status(status: str) -> bool:
    return status in VALID_CASE_STATUSES


def validate_confidence_score(score: float) -> bool:
    return isinstance(score, (int, float)) and 0.0 <= score <= 1.0


def validate_agent_output_shape(agent_name: str, output: dict) -> list[str]:
    errors = []
    if agent_name not in VALID_AGENT_NAMES:
        errors.append(f"Unknown agent name: {agent_name}")
        return errors

    required_keys = {
        "input-aggregation": ["structuredFields", "missingFields", "followUpQuestions", "confidenceScore", "escalate"],
        "profile-synthesis": ["childProfile", "strengths", "supportAreas", "familyContext", "confidenceScore"],
        "prediction": ["prioritizedDomains", "confidenceScores", "rationale", "lowConfidenceFlags"],
        "domain-analysis": ["domainBreakdown", "focusAreas", "currentBaselines", "confidenceScore"],
        "guideline-generation": ["guidelines", "strategies", "homeActivities", "confidenceScore"],
        "goal-generation": ["shortTermGoals", "longTermGoals", "goalFormat", "confidenceScore"],
        "milestone-planning": ["milestones", "timeline", "reviewPoints", "confidenceScore"],
        "caregiver-guidance": ["recommendations", "dailyActivities", "plainLanguage", "confidenceScore"],
        "ethics-consent": ["consentStatus", "consentTimestamp", "scope", "canProceed"],
        "data-quality": ["qualityScore", "missingCriticalFields", "inconsistencies", "readyForProcessing", "escalate"],
        "bias-monitoring": ["biasStatus", "biasConfidence", "flags", "humanReviewRequired", "concerns"],
        "confidence-abstention": ["workflowStatus", "overallConfidence", "abstentionReason", "canProceed"],
    }

    for key in required_keys.get(agent_name, []):
        if key not in output:
            errors.append(f"Missing required key '{key}' in {agent_name} output")

    return errors


def validate_smart_goal(goal: dict) -> list[str]:
    errors = []
    required = ["specific", "measurable", "achievable", "relevant", "timeBound"]
    for field in required:
        if field not in goal:
            errors.append(f"SMART goal missing '{field}' component")
    return errors


def extract_requirement_ids(text: str) -> list[str]:
    pattern = re.compile(r"\b(" + "|".join(REQUIREMENT_PREFIXES) + r")-\d{3}\b")
    return sorted(set(m.group() for m in pattern.finditer(text)))


def format_localstack_endpoint(service: str, endpoint_url: Optional[str] = None) -> str:
    base = endpoint_url or "http://localhost:4566"
    return base
