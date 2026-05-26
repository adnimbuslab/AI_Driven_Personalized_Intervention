# Testing Skill — AI-Driven Personalized Intervention Guideline Generator

## When to Use
Invoke this skill when writing, running, or validating tests for the Intervention Guideline Generator project.

## Test Categories

### Category A — Session & API Layer
- TEST-001: Session creation happy path (AIG-YYYY-NNNN format, INITIATED status)
- TEST-002: Missing required fields returns HTTP 400
- TEST-003: Malformed JSON returns HTTP 400
- TEST-004: Case ID uniqueness across sessions
- TEST-005: Message to non-existent case returns HTTP 404
- TEST-006: Message to completed case returns HTTP 409

### Category B — Input Aggregation & Data Quality
- TEST-010: Structured field extraction from screening report
- TEST-011: Follow-up question generation for missing fields
- TEST-012: Empty message text returns HTTP 400
- TEST-013: Large document upload processes without crash
- TEST-014: Non-English input does not crash system
- TEST-015: Whitespace-only message returns HTTP 400
- TEST-016: Data quality score computed correctly
- TEST-017: Max follow-up rounds triggers escalation
- TEST-018: Conflicting data across sources flags for review

### Category C — Document Upload
- TEST-020: File upload happy path (S3 + ScreeningInputs record)
- TEST-021: Upload to non-existent case returns HTTP 404
- TEST-022: Unsupported file type (.exe) returns HTTP 400
- TEST-023: Zero-byte file returns HTTP 400
- TEST-024: Corrupted PDF returns extractionStatus=failed gracefully
- TEST-025: Upload after final status returns HTTP 409

### Category D — Governance Agents
- TEST-030: Consent verification blocks processing when consent absent
- TEST-031: Consent granted allows workflow to proceed
- TEST-032: Bias monitoring flags biased recommendations
- TEST-033: Bias monitoring passes fair recommendations
- TEST-034: Confidence below threshold triggers abstention
- TEST-035: Confidence above threshold allows continuation
- TEST-036: Abstention logs detailed reason in audit trail

### Category E — Workflow Agents
- TEST-040: Profile synthesis produces unified child profile from inputs
- TEST-041: Domain prioritization produces ranked domain list
- TEST-042: Domain analysis breaks domains into focus areas
- TEST-043: Guideline generation produces personalized strategies
- TEST-044: Goal generation produces SMART-formatted goals
- TEST-045: Vague goals are rejected/regenerated
- TEST-046: Milestone planning creates time-bound checkpoints
- TEST-047: Caregiver guidance uses plain language (no jargon)
- TEST-048: All outputs link back to source profile data

### Category F — Clinician Review
- TEST-050: Clinician approve action finalizes plan
- TEST-051: Clinician modify action updates plan with edits
- TEST-052: Clinician reject action discards plan with reason
- TEST-053: No output reaches caregiver without clinician approval
- TEST-054: Review action logged in audit trail with reviewer ID

## Test Execution
```bash
# Run all tests against LocalStack
python -m pytest tests/ -v --tb=short

# Run by category
python -m pytest tests/ -k "category_a" -v
python -m pytest tests/ -k "category_b" -v
python -m pytest tests/ -k "category_c" -v
python -m pytest tests/ -k "category_d" -v
python -m pytest tests/ -k "category_e" -v
python -m pytest tests/ -k "category_f" -v
```

## Test Writing Rules
1. Each test must reference its TEST-xxx ID and traced requirement IDs in the docstring
2. Tests must run against LocalStack (use `DYNAMODB_ENDPOINT_URL` env var)
3. Assert specific HTTP status codes, DynamoDB record states, and agent output shapes
4. Never mock DynamoDB — use LocalStack for integration tests
5. Clean up test data after each test run (use fixtures with teardown)
6. Clinical safety tests must verify no diagnostic language in outputs
