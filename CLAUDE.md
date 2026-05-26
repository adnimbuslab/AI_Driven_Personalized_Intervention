# AI-Driven Personalized Intervention Guideline Generator — Project Instructions

## Overview
Governance-Aware Agentic AI Intervention Guideline Generator POC: a chatbot-based platform that takes autism screening reports as inputs and, through a structured multi-agent workflow, generates personalized intervention plans for children with autism. Uses multi-agent orchestration (LangGraph), Claude Opus 4.7, MCP servers, and LocalStack AWS simulation.

## Key Documents
- `Business_requirement.md` — Business workflow, user personas, agent responsibilities, HITL rules, end-to-end workflow
- `technical_requirement.md` — Technical HLD: architecture, API endpoints, DynamoDB schema, MCP servers, LangGraph flow, agent contracts
- `SPEC.md` — Full detailed specification with requirement traceability (BR/FR/AR/HITL/API/MCP/DB/FE/NFR/WF/DEP/TEST)
- `arc/` — Architecture diagrams and design documents

## Tech Stack
- **Frontend:** React (chatbot intake interface + clinician review dashboard)
- **Backend:** Python Lambda functions on LocalStack + Docker (no real AWS)
- **Agent Orchestration:** LangGraph with 10 workflow agents + 4 governance agents
- **LLM:** Claude Opus 4.7 — single-point config via `LLM_MODEL_ID` + `LLM_PROVIDER` env vars; ALL agents share this one config
- **Tool Access:** All agents use MCP servers only — no direct backend calls
- **Infrastructure:** LocalStack (Docker) for DynamoDB, S3, Lambda, API Gateway — no real AWS accounts needed

## Architecture Rules
1. Agents must NEVER call DynamoDB, S3, Lambda, or any backend service directly — use MCP server tools only
2. Every agent decision, state transition, and human action must be logged as an immutable AuditEvent
3. All generated intervention plans must route through clinician review before finalization — no AI output reaches caregivers without human approval
4. All confidence thresholds are configurable via environment variables
5. LLM provider/model must be swappable via env vars without code changes
6. The system is a clinical decision SUPPORT tool — it does not diagnose, and it does not replace clinicians

## LLM Configuration (Single Point)
All agents read from the same two env vars — change once, applies everywhere:
- `LLM_MODEL_ID=claude-opus-4-7` — the model all agents use
- `LLM_PROVIDER=anthropic` — the provider all agents use
- `ANTHROPIC_API_KEY` — API key (set in `.claude/settings.local.json`, not committed)

Agents obtain their LLM client via a shared factory function. Swapping to a different model requires only changing these env vars — zero code changes.

## Agents
### Specialized Workflow Agents
1. `input-aggregation` — Collects screening reports and assessment inputs, converts to structured data
2. `profile-synthesis` — Builds unified child profile (strengths, support areas, family context)
3. `prediction` — Prioritizes developmental domains for intervention; flags low-confidence areas
4. `domain-analysis` — Interprets prioritized domains, connects to practical intervention focus areas
5. `guideline-generation` — Generates draft intervention guidelines from profile + domain analysis
6. `goal-generation` — Converts guidelines into SMART developmental goals
7. `milestone-planning` — Creates short-term and long-term milestone plans
8. `caregiver-guidance` — Converts plans into simple caregiver-facing recommendations

### Governance Agents
1. `ethics-consent` — Verifies proper consent before data processing
2. `data-quality` — Validates data completeness; generates adaptive follow-up questions or escalates
3. `bias-monitoring` — Checks fairness across demographic, cultural, and language dimensions
4. `confidence-abstention` — Reviews confidence levels; stops workflow when system should not proceed

## Development Workflow
1. Start LocalStack + Docker: `docker-compose up -d`
2. All services (DynamoDB, S3, Lambda, API Gateway) run locally via LocalStack — no AWS account needed
3. Test iteratively on LocalStack before any handoff
4. Follow requirement traceability IDs (BR-xxx, FR-xxx, AR-xxx, etc.) from SPEC.md

## Naming Conventions
- Case IDs: `AIG-YYYY-NNNN` format (Autism Intervention Guideline)
- Agent names: kebab-case as listed above
- DynamoDB tables: `ChildProfiles`, `ScreeningInputs`, `InterventionPlans`, `AgentOutputs`, `AuditEvents`, `ClinicianReviews`
