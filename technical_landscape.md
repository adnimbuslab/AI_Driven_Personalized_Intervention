# Technical Landscape: Governance-Aware Agentic AI for Personalized Autism Intervention Guideline Generation

---

## 1. System Overview

The implemented system is a proof-of-concept (POC) platform that accepts autism screening reports as input and, through a structured multi-agent workflow, generates personalized intervention plans for children with autism spectrum disorder (ASD). The platform enforces a strict governance model: no AI-generated output reaches caregivers without clinician approval, every agent decision is immutably audited, and the system explicitly positions itself as a clinical decision *support* tool rather than a diagnostic instrument.

The architecture follows a three-tier design: a React-based chatbot and clinician review frontend, a Python backend exposing RESTful APIs, and a LangGraph-orchestrated multi-agent pipeline backed by a serverless AWS infrastructure (simulated via LocalStack for the POC). All twelve agents share a single LLM configuration (Claude Opus 4.7 via the Anthropic API) and access backend services exclusively through a Model Context Protocol (MCP) server abstraction layer.

---

## 2. Technology Stack

| Layer | Technology | Role |
|---|---|---|
| **LLM** | Claude Opus 4.7 (Anthropic API) | Reasoning engine for all 12 agents |
| **Agent Orchestration** | LangGraph (v0.2+) with LangChain Core | Directed acyclic graph (DAG) workflow with conditional routing |
| **Backend API** | FastAPI (v0.115+) / Uvicorn | REST API gateway wrapping Lambda-style handlers |
| **Infrastructure** | LocalStack (Docker) | Simulates DynamoDB, S3, Lambda, API Gateway locally |
| **Data Layer** | Amazon DynamoDB (7 tables, 12 GSIs) | Stores profiles, inputs, plans, agent outputs, audit events, reviews |
| **Object Storage** | Amazon S3 | Document uploads, extraction artifacts, plan exports |
| **Frontend** | React 18.3 + Vite 6 + Tailwind CSS 3.4 | Chatbot intake interface + clinician review dashboard |
| **Containerization** | Docker Compose (3 services) | Orchestrates LocalStack, backend, and frontend containers |
| **Language** | Python 3.x (backend) / JavaScript/JSX (frontend) | |

### Key Dependencies

- `anthropic>=0.42.0` -- Anthropic Python SDK for Claude API calls
- `langgraph>=0.2.0` / `langchain-core>=0.3.0` -- Agent workflow orchestration
- `boto3>=1.35.0` -- AWS SDK for DynamoDB and S3 (routed to LocalStack)
- `fastapi>=0.115.0` / `uvicorn>=0.32.0` -- Async HTTP server
- `pydantic>=2.10.0` -- Data validation and schema enforcement
- `react-router-dom>=6.28.0` / `axios>=1.7.0` -- Frontend routing and HTTP client

---

## 3. Multi-Agent Architecture

### 3.1 Agent Taxonomy

The system implements **12 agents** organized into two categories:

**Workflow Agents (8)** -- Execute the core intervention planning pipeline:

| # | Agent | Step | Responsibility |
|---|---|---|---|
| 1 | `ethics-consent` | 1 | Verifies informed consent before any data processing |
| 2 | `input-aggregation` | 2 | Extracts structured data from screening reports via LLM-powered document analysis |
| 3 | `data-quality` | 3 | Validates data completeness against required/desired field checklists; generates adaptive follow-up questions |
| 4 | `profile-synthesis` | 4 | Builds a unified, strength-based child profile from structured inputs via LLM |
| 5 | `prediction` | 5 | Prioritizes developmental domains (Communication, Social Interaction, Behavioral Regulation, Sensory Processing, Motor Skills, Adaptive/Self-Care, Cognitive/Academic) with per-domain confidence scores |
| 6 | `domain-analysis` | 7 | Breaks prioritized domains into specific focus areas with baselines and target directions |
| 7 | `guideline-generation` | 8 | Generates personalized intervention guidelines citing evidence-based practices (ABA, ESDM, TEACCH, NDBI, PRT, etc.) |
| 8 | `goal-generation` | 10 | Converts guidelines into SMART developmental goals with baseline/target percentages and measurement criteria |
| 9 | `milestone-planning` | 11 | Creates time-bound milestone checkpoints with graduated assistance levels |
| 10 | `caregiver-guidance` | 12 | Translates professional plans into plain-language, culturally-aware caregiver recommendations |

**Governance Agents (4)** -- Enforce safety, quality, and fairness constraints:

| # | Agent | Step | Responsibility |
|---|---|---|---|
| 1 | `ethics-consent` | 1 | (Also classified as governance) -- Blocks workflow if consent is not granted |
| 2 | `data-quality` | 3 | (Also classified as governance) -- Enforces minimum 80% data completeness; loops up to 3 follow-up rounds |
| 3 | `confidence-abstention` | 6 | Reviews cumulative confidence scores; can ABSTAIN (halt workflow), PARTIAL_PROCEED (filter to high-confidence domains), or PROCEED |
| 4 | `bias-monitoring` | 9 | Checks guidelines for demographic, cultural, language, socioeconomic, and geographic bias; triggers escalation on detection |

### 3.2 Agent Base Class and Tool Access Pattern

All agents inherit from a shared `BaseAgent` class that provides:

```
BaseAgent
  |-- dynamo: DynamoMCP       (DynamoDB read/write)
  |-- s3: S3MCP               (Document storage)
  |-- audit: AuditMCP         (Immutable event logging)
  |-- llm: LlmMCP             (LLM inference)
  |-- workflow: WorkflowMCP   (State management, confidence checks, escalation)
```

**Critical architectural constraint:** Agents never call DynamoDB, S3, or any backend service directly. All data access is mediated through MCP server abstractions, enforcing a uniform tool interface and enabling centralized auditing of every data operation.

Each agent execution follows a standardized lifecycle:
1. **Input hashing** -- SHA-256 hash of the input state for audit trail integrity
2. **Processing** -- Agent-specific logic (LLM calls, rule-based validation, or both)
3. **Output hashing** -- SHA-256 hash of the result for tamper detection
4. **Audit logging** -- Immutable `AuditEvent` recording agent ID, confidence score, input/output hashes
5. **State update** -- Returns a partial state dict merged into the LangGraph `WorkflowState`

On any unhandled exception, the base class automatically escalates to clinician review with a full error audit trail.

### 3.3 LLM Integration

All agents access the LLM through a unified `LlmMCP` server that provides three interfaces:

1. **`generate()`** -- Free-form text generation with system/user prompts
2. **`generate_structured()`** -- JSON-schema-constrained generation with automatic retry (3 attempts) and response parsing
3. **`analyze_document()`** -- Specialized clinical document extraction

The LLM client is instantiated via a singleton factory (`llm_factory.py`) that reads `LLM_MODEL_ID` and `LLM_PROVIDER` from environment variables. Swapping the underlying model (e.g., from Claude Opus to Claude Sonnet) requires only changing these two variables -- zero code modifications across all 12 agents.

For development without an API key, the `LlmMCP` provides a mock fallback that generates deterministic responses from the output schemas, enabling full workflow testing without LLM costs.

---

## 4. Workflow Orchestration

### 4.1 LangGraph State Machine

The workflow is modeled as a `StateGraph` (LangGraph) with 13 nodes (12 agents + 1 human review node) and conditional edges that implement governance gates:

```
                         +-----------------+
                         | ethics_consent  |
                         +--------+--------+
                                  |
                    GRANTED       |        DENIED
                  +---------------+-----------+---> END
                  |
         +--------v---------+
         | input_aggregation |
         +--------+---------+
                  |
         +--------v--------+
         |  data_quality   |<----- FOLLOW_UP (up to 3 rounds)
         +--------+--------+
                  |
              VALIDATED
                  |
         +--------v---------+
         | profile_synthesis |
         +--------+---------+
                  |
             confidence >= 0.70
                  |
         +--------v--------+
         |   prediction    |
         +--------+--------+
                  |
         +--------v-----------+
         | confidence_abstention |
         +--------+------------+
                  |
      PROCEED / PARTIAL_PROCEED
                  |
         +--------v---------+
         | domain_analysis  |
         +--------+---------+
                  |
         +--------v-----------+
         | guideline_generation |
         +--------+------------+
                  |
         +--------v---------+
         | bias_monitoring  |
         +--------+---------+
                  |
               PASSED          FLAGGED
                  |               +---> human_review ---> END
         +--------v----------+
         |  goal_generation  |
         +--------+----------+
                  |
         +--------v-----------+
         | milestone_planning |
         +--------+-----------+
                  |
         +--------v-----------+
         | caregiver_guidance |
         +--------+-----------+
                  |
         +--------v--------+
         |  human_review   |----> END
         +--------+--------+
```

### 4.2 Conditional Routing Logic

The workflow implements seven conditional routing functions:

| Gate | Condition | Routes |
|---|---|---|
| `route_consent` | Consent status | GRANTED -> `input_aggregation`; DENIED -> END |
| `route_input` | Error presence | Error -> `human_review`; else -> `data_quality` |
| `route_data_quality` | Completeness score + round count | VALIDATED -> `profile_synthesis`; FOLLOW_UP (< 3 rounds) -> `data_quality` (loop); else -> END |
| `route_profile` | Profile confidence | >= 0.70 -> `prediction`; else -> `human_review` |
| `route_prediction` | (Unconditional) | Always -> `confidence_abstention` |
| `route_confidence` | Proceed decision | PROCEED/PARTIAL_PROCEED -> `domain_analysis`; ABSTAIN -> END |
| `route_bias` | Bias check status | PASSED -> `goal_generation`; FLAGGED -> `human_review` |

### 4.3 Shared Workflow State

The `WorkflowState` is a typed dictionary (`TypedDict`) with 30+ fields organized by pipeline stage: consent, input data, data quality, profile, prediction, confidence check, domain analysis, guidelines, bias check, goals, milestones, caregiver guidance, and plan/review metadata. Two fields use LangGraph's `Annotated[list, operator.add]` pattern for append-only accumulation: `agent_outputs` and `escalation_history`.

---

## 5. Governance and Safety Mechanisms

### 5.1 Human-in-the-Loop (HITL)

The system enforces mandatory clinician review at multiple points:

1. **Terminal HITL gate:** Every completed intervention plan routes through a `human_review` node before finalization. The workflow status changes to `AWAITING_CLINICIAN_REVIEW` and pauses until a clinician takes action.
2. **Escalation triggers:** Low profile confidence, bias detection, or agent errors automatically escalate to clinician review.
3. **Review actions:** Clinicians can *approve*, *modify and approve*, *partially approve* (triggering re-generation), or *reject* the plan.

### 5.2 Confidence-Based Abstention

The `confidence-abstention` agent aggregates confidence scores from upstream agents and applies configurable thresholds (default: 0.70):

- **Critical failures** (data quality or profile synthesis below threshold) -> ABSTAIN (workflow halts)
- **Domain-level failures** (individual prediction domains below threshold) -> PARTIAL_PROCEED (only high-confidence domains continue)
- **All passing** -> PROCEED

All thresholds are configurable via environment variables (`CONFIDENCE_THRESHOLD_DEFAULT`, `CONFIDENCE_THRESHOLD_PREDICTION`, `CONFIDENCE_THRESHOLD_GUIDELINE`, `DATA_COMPLETENESS_THRESHOLD`).

### 5.3 Bias Monitoring

The `bias-monitoring` agent checks generated intervention guidelines across five bias dimensions:
- Demographic bias (race, ethnicity, gender)
- Cultural bias (Western-normative assumptions)
- Language bias (English fluency assumptions)
- Socioeconomic bias (resource availability assumptions)
- Geographic bias (urban service availability assumptions)

Detected concerns are logged with type, affected section, severity level, and remediation recommendations. Flagged cases are escalated to clinician review with full bias audit details.

### 5.4 Immutable Audit Trail

Every system action is recorded in the `AuditEvents` DynamoDB table:

- **Agent outputs:** Input/output SHA-256 hashes, confidence scores, step number
- **State transitions:** From-state, to-state, triggering agent
- **Escalations:** Reason, target reviewer, flagged as `human_review_required`
- **Clinician actions:** Reviewer ID, action taken, review notes
- **Errors:** Error type, message, originating agent

Audit events are queryable by case ID (chronological), agent ID (with time range filtering), and reviewer ID. The retention period defaults to 2,555 days (~7 years), matching typical clinical record retention requirements.

### 5.5 Data Integrity

- All agent inputs and outputs are hashed using SHA-256 before audit logging
- Hashes are stored alongside each audit event, enabling tamper detection
- Case IDs are generated atomically using DynamoDB atomic counters (`AIG-YYYY-NNNN` format)

---

## 6. Data Architecture

### 6.1 DynamoDB Schema

The system uses 7 DynamoDB tables with 12 Global Secondary Indexes (GSIs):

| Table | Partition Key | GSIs | Purpose |
|---|---|---|---|
| `ChildProfiles` | `child_id` (S) | `case_id-index` | Unified child profile with strengths, support areas, demographics |
| `ScreeningInputs` | `assessment_id` (S) | `child_id-index` | Raw and structured screening/assessment data |
| `InterventionPlans` | `plan_id` (S) | `child_id-index`, `case_id-index` | Complete intervention plans (guidelines, goals, milestones, caregiver guidance) |
| `AgentOutputs` | `output_id` (S) | `case_id-agent-index`, `agent_id-index` | Per-agent output snapshots with confidence scores |
| `AuditEvents` | `event_id` (S) | `case_id-time-index`, `agent_id-time-index` | Immutable audit trail |
| `ClinicianReviews` | `review_id` (S) | `case_id-index`, `reviewer_id-index` | Clinician review decisions and notes |
| `CaseCounter` | `counter_id` (S) | -- | Atomic counter for sequential case ID generation |

All tables use PAY_PER_REQUEST billing mode. Float values are automatically converted to DynamoDB-compatible `Decimal` types via a sanitization layer, and deserialized back to floats/ints on read.

### 6.2 S3 Object Storage

Documents are organized in a hierarchical key structure:
- `uploads/{case_id}/{filename}` -- Uploaded screening reports
- `extractions/{case_id}/extraction.json` -- LLM-extracted structured data
- `exports/{case_id}/plan.pdf` -- Finalized plan exports

---

## 7. MCP Server Abstraction Layer

The system implements five MCP (Model Context Protocol) servers as the sole interface between agents and infrastructure:

| MCP Server | Operations | Backend Service |
|---|---|---|
| **DynamoMCP** | CRUD for all 6 data tables + cross-table queries + status-based scans | DynamoDB |
| **S3MCP** | Document upload/retrieval, extraction storage, plan export storage | S3 |
| **AuditMCP** | Event logging, case/agent audit trail queries, state transition logging, escalation logging, clinician action logging | DynamoDB (AuditEvents table) |
| **LlmMCP** | Free-form generation, structured (JSON-schema) generation, document analysis, mock fallback | Anthropic API |
| **WorkflowMCP** | Workflow state queries, state updates, previous agent output retrieval, confidence threshold checks, escalation triggers, human review requests | DynamoDB + AuditMCP |

All MCP servers inherit from `BaseMCP`, which provides lazy-initialized, singleton `boto3` clients preconfigured for LocalStack endpoints.

---

## 8. API Layer

The backend exposes **20 RESTful endpoints** via FastAPI, organized into six resource groups:

| Group | Endpoints | Purpose |
|---|---|---|
| **Case Management** | `POST /api/cases`, `GET /api/cases`, `GET /api/cases/{id}`, `GET /api/cases/{id}/status`, `PUT /api/cases/{id}/consent` | Case lifecycle management |
| **Documents & Inputs** | `POST /api/cases/{id}/documents`, `POST /api/cases/{id}/inputs`, `POST /api/cases/{id}/followup`, `GET /api/cases/{id}/inputs` | Screening data submission |
| **Workflow** | `POST /api/cases/{id}/workflow/start`, `GET /api/cases/{id}/workflow/state`, `POST /api/cases/{id}/escalate` | Workflow orchestration and control |
| **Plan** | `GET /api/cases/{id}/plan`, `GET /api/cases/{id}/plan/{section}` (profile, domains, guidelines, goals, caregiver) | Section-level plan retrieval |
| **Review** | `GET /api/reviews/pending`, `POST /api/cases/{id}/review`, `GET /api/cases/{id}/reviews` | Clinician review queue and actions |
| **Audit & Chat** | `GET /api/cases/{id}/audit`, `GET /api/audit/agent/{id}`, `POST /api/chat/{id}/message`, `GET /api/chat/{id}/history` | Audit trails and conversational intake |

The API follows a Lambda-compatible handler pattern: each endpoint delegates to a handler function that accepts `(event, context)` and returns `{statusCode, headers, body}`, enabling future migration to actual AWS Lambda with minimal refactoring.

---

## 9. Frontend Architecture

The frontend is a single-page React application with three primary views:

### 9.1 Intake Page (Chatbot Interface)
- Conversational UI for case creation and screening data collection
- Explicit consent verification gate (GRANTED/DENIED buttons) before any data processing
- Structured input form for clinical assessment data (14 fields covering demographics, ADOS-2 scores, domains, family context)
- Real-time workflow progress visualization (13-step progress bar)
- LLM-powered conversational assistant for adaptive data collection

### 9.2 Clinician Review Dashboard
- Review queue showing pending cases with domain/goal counts
- Expandable plan sections: Domain Priorities, Intervention Guidelines, SMART Goals, Caregiver Guidance, Audit Trail
- Per-section confidence score badges (color-coded: green >= 80%, yellow >= 60%, red < 60%)
- Bias concern alerts prominently displayed
- Three-action review panel: Approve, Modify & Approve, Reject
- Free-text review notes

### 9.3 Case Dashboard
- Overview statistics (total, pending, approved, rejected)
- Filterable case table with status badges
- Quick navigation to intake and review workflows

---

## 10. Deployment Architecture

```
+--------------------+     +--------------------+     +--------------------+
|     Frontend       |     |     Backend        |     |    LocalStack      |
|  (React + Vite)    |---->|  (FastAPI/Uvicorn) |---->|  (DynamoDB, S3,    |
|  Port 3000         |     |  Port 8000         |     |   Lambda, APIGw)   |
|  Nginx             |     |  Python 3.x        |     |  Port 4566         |
+--------------------+     +--------------------+     +--------------------+
                                    |
                                    v
                           +--------------------+
                           |   Anthropic API    |
                           |  (Claude Opus 4.7) |
                           +--------------------+
```

Docker Compose orchestrates three services:
1. **LocalStack** -- Starts first, provisions DynamoDB tables and S3 buckets via init scripts, exposes health check on port 4566
2. **Backend** -- Waits for LocalStack health check, mounts source code for hot reload, exposes port 8000
3. **Frontend** -- Waits for backend availability, serves static assets via Nginx on port 3000

---

## 11. Clinical Domain Modeling

### 11.1 Input Schema

The system processes structured screening data covering:
- **Demographics:** Age (years/months), gender
- **Assessment Instruments:** ADOS-2 (Social Affect score, Restricted/Repetitive Behavior score, comparison score, module), screening tool identification (ADOS-2, M-CHAT-R, CARS-2)
- **Developmental Profile:** Primary and secondary domains of concern, support level (DSM-5 Levels 1-3), strength domains, gap domains
- **Cognitive/Adaptive Measures:** Verbal and nonverbal cognitive percentiles, adaptive behavior composite percentile
- **Family Context:** Home language, home environment, cultural notes, family priorities, current services
- **Clinical History:** Prior interventions, clinician observations, referral source, primary setting

### 11.2 Output Artifacts

The pipeline produces a structured intervention plan containing:

1. **Unified Child Profile** -- Strength-based narrative with support areas, developmental history, family context, and environmental factors
2. **Domain Priority Rankings** -- Ranked developmental domains with per-domain confidence scores, severity indicators, rationale, and interdependency mapping
3. **Domain Analysis** -- 2-4 focus areas per domain with current baseline, target direction, developmental stage notes, and cross-domain interdependencies
4. **Intervention Guidelines** -- Per-domain recommendations including evidence-based approaches (ABA, ESDM, TEACCH, NDBI, PRT, DIR/Floortime, Hanen, AAC/PECS, Sensory Integration), intervention intensity, session frequency/duration, delivery modality, environmental modifications, and home activities
5. **SMART Goals** -- Goals validated against all five SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound) with baseline/target percentages, measurement methods, and explicit guideline linkage
6. **Milestone Plans** -- Short-term milestones (biweekly) with graduated assistance levels (hand-over-hand -> partial physical -> verbal -> visual cue -> independent) and long-term milestones (monthly) with generalization setting targets
7. **Caregiver Guidance** -- Plain-language activities linked to daily routines (mealtime, bath time, play time, bedtime), general parenting strategies, strength-based encouragement, and progress tracking tips -- written at a Grade 5-6 reading level

### 11.3 Evidence-Based Approaches Referenced

The system's prompt engineering references established autism intervention methodologies:
- Applied Behavior Analysis (ABA)
- Naturalistic Developmental Behavioral Interventions (NDBI)
- Early Start Denver Model (ESDM)
- TEACCH Structured Teaching
- Augmentative and Alternative Communication (AAC) / Picture Exchange Communication System (PECS)
- Sensory Integration Therapy
- Developmental, Individual Difference, Relationship-based Model (DIR/Floortime)
- Pivotal Response Training (PRT)
- Hanen Programs

---

## 12. Configurable Parameters

All system thresholds and behavioral parameters are externalized as environment variables:

| Parameter | Default | Purpose |
|---|---|---|
| `LLM_MODEL_ID` | `claude-opus-4-7` | LLM model identifier (single point of change) |
| `LLM_PROVIDER` | `anthropic` | LLM provider (extensible to other providers) |
| `CONFIDENCE_THRESHOLD_DEFAULT` | 0.70 | Minimum confidence for most agent decisions |
| `CONFIDENCE_THRESHOLD_PREDICTION` | 0.75 | Elevated threshold for domain prioritization |
| `CONFIDENCE_THRESHOLD_GUIDELINE` | 0.70 | Minimum confidence for generated guidelines |
| `DATA_COMPLETENESS_THRESHOLD` | 0.80 | Minimum data completeness score to proceed |
| `MAX_FOLLOWUP_ROUNDS` | 3 | Maximum adaptive follow-up question rounds |
| `BIAS_SENSITIVITY` | `medium` | Sensitivity level for bias detection |
| `AUDIT_RETENTION_DAYS` | 2555 (~7 years) | Audit event retention period |

---

## 13. Design Principles and Constraints

1. **No direct backend calls from agents.** Every agent accesses infrastructure exclusively through MCP server abstractions, ensuring uniform tool interfaces and centralized audit logging.
2. **Mandatory HITL for all outputs.** No AI-generated intervention plan reaches a caregiver without clinician approval. The `human_review` node is an unconditional terminal gate.
3. **Immutable audit trail.** Every agent decision, state transition, escalation, and clinician action is logged with input/output hashes and confidence scores.
4. **Strength-based framing.** All prompts instruct agents to lead with what the child *can* do, not just deficits.
5. **No diagnostic statements.** Every agent prompt explicitly prohibits generating diagnostic conclusions -- the system is framed as clinical decision *support*.
6. **Cultural and linguistic sensitivity.** Family context (language, culture, resources) is threaded through profile synthesis, guideline generation, bias monitoring, and caregiver guidance.
7. **Graceful degradation.** The confidence-abstention agent can halt or narrow the workflow scope rather than producing low-confidence outputs. The LLM layer falls back to mock responses when the API key is unavailable.
8. **Single-point LLM configuration.** Changing the model or provider requires modifying two environment variables and zero lines of code.

---

## 14. Quantitative Summary

| Metric | Count |
|---|---|
| Total agents | 12 (8 workflow + 4 governance) |
| Workflow nodes (LangGraph) | 13 (12 agents + 1 human review) |
| Conditional routing functions | 7 |
| MCP servers | 5 |
| DynamoDB tables | 7 |
| Global Secondary Indexes | 12 |
| REST API endpoints | 20 |
| Frontend pages | 3 |
| Configurable environment variables | 18 |
| Lines of Python (backend) | ~2,100 |
| Lines of JSX (frontend) | ~700 |
| Evidence-based approaches referenced | 9 |
| Bias dimensions monitored | 5 |
| SMART goal criteria validated | 5 |
| Developmental domains modeled | 7 |
