# Code Review Skill — AI-Driven Personalized Intervention Guideline Generator

## When to Use
Invoke this skill when reviewing PRs or code changes in the Intervention Guideline Generator project.

## Review Checklist

### Architecture Compliance
- Agents must NOT call DynamoDB, S3, Lambda, or any backend service directly
- All agent resource access goes through MCP server tools only
- LLM client obtained via shared factory reading `LLM_MODEL_ID` / `LLM_PROVIDER` env vars
- No hardcoded AWS endpoints — all must use endpoint URL env vars

### Agent Contract Validation
- Verify agent input/output matches the contracts defined in SPEC.md
- Every extracted field must carry a confidence score between 0 and 1
- Escalation triggers must match the spec (e.g., low confidence always escalates)
- Confidence thresholds must be read from config, not hardcoded
- All workflow agents must produce outputs traceable to input data

### Governance Gates
- Consent must be verified before any data processing begins
- Data quality check must run before profile synthesis
- Bias monitoring must run after guideline generation, before clinician delivery
- Confidence/abstention agent must be able to halt the workflow at any step
- All governance decisions must be logged in audit trail

### Human-in-the-Loop Gates
- Confirm HITL gates exist at: post-input, post-profile, post-prediction, post-guideline, final-review
- ALL generated outputs require mandatory clinician review before caregiver delivery
- Audit trail must be saved BEFORE escalation occurs
- Clinician can approve, modify, or reject at final review

### Audit Trail
- Every agent decision, state transition, and human action logged as immutable AuditEvent
- Every LangGraph node transition logged
- AuditEvents records must never be updated or deleted
- Human review actions include reviewer ID, action, timestamp, and notes

### Data Safety
- Input validation at API boundaries (no XSS, injection)
- Case IDs follow `AIG-YYYY-NNNN` format
- File uploads reject unsupported types (.exe, etc.)
- Empty/whitespace-only messages rejected with HTTP 400
- Child PII never logged in application logs

### Clinical Safety
- System must NEVER generate diagnostic statements
- All outputs are clearly labeled as drafts pending clinician review
- SMART goals must be specific and measurable — reject vague goals
- Caregiver guidance must use plain language (no clinical jargon)
- Cultural/language context must be respected in recommendations

### DynamoDB Schema
- Table names and key structures match spec
- Sort keys use ISO 8601 format where specified
- All required attributes are populated

## Output Format
Produce findings grouped by: Critical (blocks merge), Warning (should fix), Info (suggestion).
