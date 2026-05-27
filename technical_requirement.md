# Technical Requirements: AI-Driven Personalized Intervention Guideline Generator

## 1. System Architecture Overview

The system follows a four-layer architecture as described in the research paper:

1. **Input Layer** — React chatbot interface for conversational data collection
2. **Agent Orchestration Layer** — LangGraph multi-agent workflow (10 workflow + 4 governance agents)
3. **Infrastructure Layer** — LocalStack-simulated AWS services (DynamoDB, S3, Lambda, API Gateway)
4. **Clinician Review Layer** — React dashboard for mandatory human review

All agent-to-backend communication is routed through MCP servers. No agent may call DynamoDB, S3, Lambda, or any backend service directly.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                             │
│  ┌─────────────────────┐    ┌────────────────────────────────────┐  │
│  │  Chatbot Interface   │    │  Clinician Review Dashboard        │  │
│  │  (intake + follow-up)│    │  (approve / modify / reject)       │  │
│  └────────┬────────────┘    └─────────────┬──────────────────────┘  │
└───────────┼───────────────────────────────┼─────────────────────────┘
            │ REST                           │ REST
┌───────────▼───────────────────────────────▼─────────────────────────┐
│                    API GATEWAY (LocalStack)                          │
└───────────┬───────────────────────────────┬─────────────────────────┘
            │                               │
┌───────────▼───────────────────────────────▼─────────────────────────┐
│                  LAMBDA FUNCTIONS (LocalStack + Docker)              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────┐  │
│  │ case-intake   │ │ workflow-    │ │ clinician-   │ │ audit-    │  │
│  │ -handler     │ │ orchestrator │ │ review-handler│ │ logger    │  │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └─────┬─────┘  │
└─────────┼────────────────┼────────────────┼───────────────┼─────────┘
          │                │                │               │
┌─────────▼────────────────▼────────────────▼───────────────▼─────────┐
│               LANGGRAPH ORCHESTRATION ENGINE                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    WORKFLOW AGENTS                            │    │
│  │  input-aggregation → profile-synthesis → prediction →        │    │
│  │  domain-analysis → guideline-generation → goal-generation →  │    │
│  │  milestone-planning → caregiver-guidance                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   GOVERNANCE AGENTS                          │    │
│  │  ethics-consent │ data-quality │ bias-monitoring │            │    │
│  │  confidence-abstention                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│          │                                                          │
│          │  ALL agent I/O goes through MCP servers                  │
│          ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      MCP SERVERS                             │    │
│  │  dynamo-mcp │ s3-mcp │ audit-mcp │ llm-mcp │ workflow-mcp   │    │
│  └──────┬──────────┬─────────┬──────────┬──────────┬───────────┘    │
└─────────┼──────────┼─────────┼──────────┼──────────┼────────────────┘
          │          │         │          │          │
┌─────────▼──────────▼─────────▼──────────▼──────────▼────────────────┐
│                 LOCALSTACK (Docker)                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ DynamoDB  │  │   S3     │  │  Lambda   │  │  API Gateway     │    │
│  │ (6 tables)│  │ (docs)   │  │(functions)│  │  (REST routes)   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18+ | Chatbot intake UI + clinician review dashboard |
| API Gateway | LocalStack API Gateway | REST endpoint routing |
| Backend | Python 3.11+ Lambda (LocalStack + Docker) | Business logic, request handling |
| Agent Orchestration | LangGraph | Multi-agent workflow graph with state management |
| LLM | Claude Opus 4.7 (Anthropic) | Shared LLM for all agents via single config |
| Tool Access | MCP Servers (Model Context Protocol) | Agent-to-backend communication layer |
| Database | DynamoDB (LocalStack) | Primary data store (6 tables) |
| Object Storage | S3 (LocalStack) | Uploaded documents (PDFs, clinical forms) |
| Infrastructure | Docker + Docker Compose | Container orchestration for LocalStack |
| Package Management | pip (Python) / npm (React) | Dependency management |

---

## 3. LLM Configuration

All agents share a single LLM configuration. Swapping to a different model requires only changing environment variables — zero code changes.

```
LLM_MODEL_ID=claude-opus-4-7
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<set in .claude/settings.local.json, never committed>
```

### LLM Factory

A shared factory function provides the LLM client to every agent:

```python
# llm_factory.py
def get_llm_client():
    provider = os.environ["LLM_PROVIDER"]
    model_id = os.environ["LLM_MODEL_ID"]
    if provider == "anthropic":
        return AnthropicClient(model=model_id, api_key=os.environ["ANTHROPIC_API_KEY"])
    raise ValueError(f"Unsupported provider: {provider}")
```

---

## 4. Environment Variables

All thresholds and configurations are externalized — no hardcoded values in application code.

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL_ID` | `claude-opus-4-7` | LLM model all agents use |
| `LLM_PROVIDER` | `anthropic` | LLM provider |
| `ANTHROPIC_API_KEY` | — | API key (secret, not committed) |
| `CONFIDENCE_THRESHOLD_DEFAULT` | `0.70` | Default confidence threshold for agent outputs |
| `CONFIDENCE_THRESHOLD_PREDICTION` | `0.75` | Threshold for prediction agent domain prioritization |
| `CONFIDENCE_THRESHOLD_GUIDELINE` | `0.70` | Threshold for guideline generation |
| `DATA_COMPLETENESS_THRESHOLD` | `0.80` | Minimum data completeness score to proceed |
| `MAX_FOLLOWUP_ROUNDS` | `3` | Maximum follow-up question rounds before escalation |
| `BIAS_SENSITIVITY` | `medium` | Bias detection sensitivity (`low`, `medium`, `high`) |
| `AUDIT_RETENTION_DAYS` | `2555` | Audit log retention period (7 years default) |
| `LOCALSTACK_ENDPOINT` | `http://localhost:4566` | LocalStack service endpoint |
| `DYNAMODB_TABLE_PREFIX` | `aig_` | Prefix for DynamoDB table names |
| `S3_DOCUMENT_BUCKET` | `aig-documents` | S3 bucket for uploaded clinical documents |
| `CASE_ID_PREFIX` | `AIG` | Prefix for case ID generation (AIG-YYYY-NNNN) |

---

## 5. DynamoDB Schema

Six tables store all application data. All tables use on-demand capacity mode on LocalStack.

### 5.1 ChildProfiles

Stores unified child profiles built by the profile-synthesis agent.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `child_id` | S | PK | Unique ID: `CH-NNN` |
| `case_id` | S | GSI-PK | Case ID: `AIG-YYYY-NNNN` |
| `created_at` | S | GSI-SK | ISO 8601 timestamp |
| `age_years` | N | — | Child age in years |
| `age_months` | N | — | Child age in months |
| `gender` | S | — | Male / Female / Non-binary |
| `support_level` | S | — | DSM-5 ASD support level (Level 1, 2, 3) |
| `diagnosis` | S | — | Diagnosis variant |
| `primary_domain` | S | — | Primary developmental domain |
| `secondary_domain` | S | — | Secondary developmental domain |
| `home_language` | S | — | Family's primary language |
| `bilingual` | BOOL | — | Whether family is bilingual |
| `primary_setting` | S | — | Intervention setting |
| `referral_source` | S | — | Referral origin |
| `screening_tool` | S | — | Assessment tool(s) used |
| `ados2_module` | S | — | ADOS-2 module |
| `ados2_social_affect` | N | — | ADOS-2 social affect score |
| `ados2_rrb` | N | — | ADOS-2 restricted/repetitive behavior score |
| `ados2_comparison_score` | S | — | ADOS-2 comparison level |
| `cognitive_verbal_percentile` | N | — | Verbal cognitive percentile |
| `cognitive_nonverbal_percentile` | N | — | Nonverbal cognitive percentile |
| `cognitive_gca_percentile` | N | — | General cognitive ability percentile |
| `adaptive_composite_percentile` | N | — | Adaptive behavior composite percentile |
| `strength_domains` | SS | — | Identified developmental strengths |
| `gap_domains` | SS | — | Identified developmental gaps |
| `family_priorities` | SS | — | Family-identified priorities |
| `family_context` | M | — | Map: language, home environment, cultural notes |
| `current_services` | SS | — | Current services/therapies |
| `status` | S | — | Profile status (draft, validated, approved) |

**GSI: `case_id-index`** — PK: `case_id`, SK: `created_at`

### 5.2 ScreeningInputs

Stores raw and structured screening/assessment data from the input-aggregation agent.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `assessment_id` | S | PK | Unique ID: `ASS-CH-NNN` |
| `child_id` | S | GSI-PK | Links to ChildProfiles |
| `assessment_date` | S | GSI-SK | Date of assessment |
| `assessment_type` | S | — | Type of assessment |
| `primary_tool` | S | — | Primary screening tool used |
| `ados2_module` | S | — | ADOS-2 module used |
| `ados2_social_affect_score` | N | — | ADOS-2 SA score |
| `ados2_rrb_score` | N | — | ADOS-2 RRB score |
| `ados2_total` | N | — | ADOS-2 total score |
| `ados2_comparison` | S | — | Comparison level (low, moderate, high) |
| `cognitive_tool` | S | — | Cognitive assessment tool |
| `cognitive_verbal_pct` | N | — | Verbal percentile |
| `cognitive_nonverbal_pct` | N | — | Nonverbal percentile |
| `cognitive_composite_pct` | N | — | Composite percentile |
| `adaptive_tool` | S | — | Adaptive behavior tool |
| `adaptive_composite_pct` | N | — | Adaptive composite percentile |
| `adaptive_communication_pct` | N | — | Communication domain percentile |
| `adaptive_social_pct` | N | — | Social domain percentile |
| `adaptive_practical_pct` | N | — | Practical domain percentile |
| `behavioral_tool` | S | — | Behavioral assessment tool (if used) |
| `diagnosis_given` | S | — | Resulting diagnosis |
| `support_level` | S | — | Assigned support level |
| `assessor_role` | S | — | Role of the assessing clinician |
| `raw_documents` | SS | — | S3 keys of uploaded documents |
| `extraction_confidence` | N | — | Data extraction confidence score |

**GSI: `child_id-index`** — PK: `child_id`, SK: `assessment_date`

### 5.3 InterventionPlans

Stores intervention guidelines, goals, milestones, and caregiver guidance — the complete plan output.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `plan_id` | S | PK | Unique plan ID |
| `child_id` | S | GSI-PK | Links to ChildProfiles |
| `case_id` | S | GSI-PK | Links to case |
| `created_at` | S | SK | ISO 8601 timestamp |
| `status` | S | — | draft / pending_review / approved / modified / rejected |
| `guidelines` | L | — | List of guideline objects (per domain) |
| `guidelines[].guideline_id` | S | — | `GL-CH-NNN-N` |
| `guidelines[].domain` | S | — | Developmental domain |
| `guidelines[].priority` | S | — | high / moderate / low |
| `guidelines[].intervention_intensity` | S | — | intensive / moderate / maintenance |
| `guidelines[].recommended_frequency` | S | — | Session frequency |
| `guidelines[].evidence_based_approaches` | SS | — | Evidence-based approaches |
| `guidelines[].focus_sub_domains` | SS | — | Specific focus sub-domains |
| `guidelines[].recommended_modality` | S | — | Delivery modality |
| `guidelines[].session_duration_minutes` | N | — | Recommended session length |
| `guidelines[].environmental_modifications` | SS | — | Environmental modification suggestions |
| `guidelines[].confidence_score` | N | — | Agent confidence score |
| `smart_goals` | L | — | List of SMART goal objects |
| `smart_goals[].goal_id` | S | — | `GOAL-CH-NNN-N` |
| `smart_goals[].domain` | S | — | Domain |
| `smart_goals[].sub_domain` | S | — | Sub-domain |
| `smart_goals[].goal_text` | S | — | Full SMART goal statement |
| `smart_goals[].baseline_percent` | N | — | Current performance level |
| `smart_goals[].target_percent` | N | — | Target performance level |
| `smart_goals[].measurement_frequency` | S | — | Measurement cadence |
| `smart_goals[].measurement_method` | S | — | How progress is measured |
| `smart_goals[].weeks_duration` | N | — | Goal timeline in weeks |
| `milestones` | L | — | List of milestone objects per goal |
| `milestones[].milestone_id` | S | — | `MS-GOAL-CH-NNN-N` |
| `milestones[].goal_id` | S | — | Parent goal ID |
| `milestones[].short_term_milestones` | L | — | List of short-term checkpoint objects |
| `milestones[].long_term_milestones` | L | — | List of long-term checkpoint objects |
| `caregiver_guidance` | M | — | Caregiver guidance object |
| `caregiver_guidance.language_preference` | S | — | Target language |
| `caregiver_guidance.reading_level` | S | — | Target reading level |
| `caregiver_guidance.activities` | L | — | Home activity recommendations |
| `caregiver_guidance.general_strategies` | SS | — | General strategies list |
| `domain_priorities` | L | — | Ranked domain priority list from prediction agent |
| `domain_analysis` | L | — | Domain analysis with focus areas |
| `bias_check_result` | M | — | Bias monitoring result |
| `confidence_check_result` | M | — | Confidence/abstention check result |

**GSI: `child_id-index`** — PK: `child_id`, SK: `created_at`
**GSI: `case_id-index`** — PK: `case_id`, SK: `created_at`

### 5.4 AgentOutputs

Stores individual agent outputs for traceability and debugging. Each agent writes its output here before the next agent runs.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `output_id` | S | PK | Unique output ID |
| `case_id` | S | GSI-PK | Case this output belongs to |
| `agent_id` | S | GSI-PK | Agent that produced this output |
| `step_number` | N | SK | Workflow step number (1–13) |
| `timestamp` | S | — | ISO 8601 timestamp |
| `input_hash` | S | — | SHA-256 hash of agent input |
| `output_hash` | S | — | SHA-256 hash of agent output |
| `output_data` | M | — | Full agent output (structured) |
| `confidence_score` | N | — | Agent's confidence in this output |
| `execution_time_ms` | N | — | Agent execution time |
| `status` | S | — | completed / escalated / abstained / error |
| `escalation_reason` | S | — | Reason for escalation (if applicable) |
| `next_agent` | S | — | Next agent in the workflow |

**GSI: `case_id-agent-index`** — PK: `case_id`, SK: `agent_id`
**GSI: `agent_id-index`** — PK: `agent_id`, SK: `step_number`

### 5.5 AuditEvents

Immutable audit trail. Records cannot be modified or deleted.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `event_id` | S | PK | UUID |
| `case_id` | S | GSI-PK | Case ID |
| `timestamp` | S | GSI-SK | ISO 8601 timestamp |
| `agent_id` | S | GSI-PK | Agent that generated the event |
| `event_type` | S | — | CONSENT_CHECK / DATA_VALIDATION / AGENT_OUTPUT / BIAS_CHECK / CONFIDENCE_CHECK / CLINICIAN_REVIEW / ESCALATION / STATE_TRANSITION / ERROR |
| `action` | S | — | Human-readable action description |
| `confidence_score` | N | — | Confidence score (if applicable) |
| `input_hash` | S | — | SHA-256 hash of input data |
| `output_hash` | S | — | SHA-256 hash of output data |
| `escalated` | BOOL | — | Whether this event triggered an escalation |
| `human_review_required` | BOOL | — | Whether human review is needed |
| `reviewer_id` | S | — | Clinician ID (for review events) |
| `review_action` | S | — | approved / modified / rejected / partial_approved |
| `review_notes` | S | — | Clinician notes (for review events) |
| `metadata` | M | — | Additional context (varies by event type) |

**GSI: `case_id-time-index`** — PK: `case_id`, SK: `timestamp`
**GSI: `agent_id-time-index`** — PK: `agent_id`, SK: `timestamp`

### 5.6 ClinicianReviews

Stores clinician review decisions and modifications.

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| `review_id` | S | PK | Unique review ID |
| `case_id` | S | GSI-PK | Case under review |
| `plan_id` | S | GSI-PK | Plan under review |
| `reviewer_id` | S | GSI-PK | Clinician performing review |
| `timestamp` | S | SK | ISO 8601 timestamp |
| `action` | S | — | approved / modified / rejected / partial_approved |
| `sections_reviewed` | SS | — | List of sections reviewed |
| `modifications` | L | — | List of modification objects (section, original, modified, reason) |
| `rejection_reason` | S | — | Reason for rejection (if applicable) |
| `override_notes` | S | — | Clinician override justification |
| `approved_sections` | SS | — | Sections approved for delivery |
| `flagged_sections` | SS | — | Sections flagged for revision |

**GSI: `case_id-index`** — PK: `case_id`, SK: `timestamp`
**GSI: `reviewer_id-index`** — PK: `reviewer_id`, SK: `timestamp`

---

## 6. S3 Storage

**Bucket:** `aig-documents`

| Prefix | Content | Format |
|--------|---------|--------|
| `uploads/{case_id}/` | Raw uploaded documents | PDF, DOCX, images |
| `extractions/{case_id}/` | Structured extraction results | JSON |
| `plans/{case_id}/` | Finalized intervention plans | JSON, PDF |
| `exports/{case_id}/` | Caregiver-facing exports | PDF |

---

## 7. API Endpoints

All endpoints are served through LocalStack API Gateway. Base URL: `http://localhost:4566/restapis/{api-id}/local/_user_request_`

### 7.1 Case Management

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| POST | `/api/cases` | Create a new case | `{ reporter_id, consent_status }` | `{ case_id, status }` |
| GET | `/api/cases/{case_id}` | Get case details | — | Case object with current status |
| GET | `/api/cases/{case_id}/status` | Get workflow status | — | `{ case_id, current_step, state }` |
| PUT | `/api/cases/{case_id}/consent` | Record consent decision | `{ consent_type, granted }` | Updated consent status |
| GET | `/api/cases` | List cases (with filters) | Query: `?status=&reviewer_id=` | Paginated case list |

### 7.2 Input & Document Upload

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| POST | `/api/cases/{case_id}/documents` | Upload screening document | Multipart form (file) | `{ document_id, s3_key }` |
| POST | `/api/cases/{case_id}/inputs` | Submit structured input data | Structured screening data JSON | `{ input_id, validation_status }` |
| POST | `/api/cases/{case_id}/followup` | Submit follow-up answers | `{ round, answers[] }` | `{ status, next_questions? }` |
| GET | `/api/cases/{case_id}/inputs` | Get all inputs for a case | — | Aggregated input data |

### 7.3 Workflow Control

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| POST | `/api/cases/{case_id}/workflow/start` | Trigger workflow execution | — | `{ workflow_id, status }` |
| GET | `/api/cases/{case_id}/workflow/state` | Get current workflow state | — | LangGraph state snapshot |
| POST | `/api/cases/{case_id}/workflow/resume` | Resume after human review | `{ decision, notes }` | Updated workflow state |
| POST | `/api/cases/{case_id}/escalate` | Manually escalate a case | `{ reason, target_reviewer }` | Escalation confirmation |

### 7.4 Intervention Plan

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| GET | `/api/cases/{case_id}/plan` | Get generated plan | — | Full intervention plan |
| GET | `/api/cases/{case_id}/plan/profile` | Get child profile | — | Unified child profile |
| GET | `/api/cases/{case_id}/plan/domains` | Get domain priorities | — | Prioritized domain list |
| GET | `/api/cases/{case_id}/plan/guidelines` | Get intervention guidelines | — | Guidelines per domain |
| GET | `/api/cases/{case_id}/plan/goals` | Get SMART goals | — | Goals with milestones |
| GET | `/api/cases/{case_id}/plan/caregiver` | Get caregiver guidance | — | Caregiver-facing content |

### 7.5 Clinician Review

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| GET | `/api/reviews/pending` | List plans awaiting review | Query: `?reviewer_id=` | Paginated pending reviews |
| POST | `/api/cases/{case_id}/review` | Submit clinician review | `{ action, modifications[], notes }` | Review confirmation |
| GET | `/api/cases/{case_id}/reviews` | Get review history | — | List of review events |

### 7.6 Audit

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| GET | `/api/cases/{case_id}/audit` | Get audit trail for a case | — | Chronological audit events |
| GET | `/api/audit/agent/{agent_id}` | Get audit events by agent | Query: `?from=&to=` | Agent audit events |

### 7.7 Chat Interface

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|-------------|----------|
| POST | `/api/chat/{case_id}/message` | Send chat message | `{ message, attachments[] }` | `{ response, follow_up_questions? }` |
| GET | `/api/chat/{case_id}/history` | Get chat history | — | Message list |

---

## 8. MCP Servers

Agents interact with backend services exclusively through MCP (Model Context Protocol) servers. Each MCP server exposes a set of tools that agents can invoke.

### 8.1 dynamo-mcp

Provides read/write access to all DynamoDB tables.

**Tools:**

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_child_profile` | `child_id` | Retrieve a child profile |
| `put_child_profile` | `child_id, profile_data` | Create or update a child profile |
| `get_screening_inputs` | `child_id` | Retrieve screening/assessment data |
| `put_screening_input` | `assessment_id, data` | Store structured screening data |
| `get_intervention_plan` | `plan_id` | Retrieve an intervention plan |
| `put_intervention_plan` | `plan_id, plan_data` | Create or update a plan |
| `update_plan_status` | `plan_id, status` | Update plan status |
| `get_agent_output` | `output_id` | Retrieve a specific agent output |
| `put_agent_output` | `output_id, data` | Store an agent output |
| `query_by_case` | `case_id, table` | Query any table by case_id |
| `get_clinician_review` | `review_id` | Retrieve a clinician review |
| `put_clinician_review` | `review_id, data` | Store a clinician review |

### 8.2 s3-mcp

Manages document upload, retrieval, and storage in S3.

**Tools:**

| Tool | Parameters | Description |
|------|-----------|-------------|
| `upload_document` | `case_id, file_name, content_type, body` | Upload a document to S3 |
| `get_document` | `s3_key` | Retrieve a document from S3 |
| `list_documents` | `case_id` | List all documents for a case |
| `store_extraction` | `case_id, extraction_data` | Store structured extraction results |
| `store_plan_export` | `case_id, plan_pdf` | Store final plan PDF |

### 8.3 audit-mcp

Writes immutable audit events. Provides read-only query access.

**Tools:**

| Tool | Parameters | Description |
|------|-----------|-------------|
| `log_event` | `case_id, agent_id, event_type, action, confidence_score, input_hash, output_hash, metadata` | Write an immutable audit event |
| `get_case_audit_trail` | `case_id` | Retrieve full audit trail for a case |
| `get_agent_audit_trail` | `agent_id, from_date, to_date` | Query audit events by agent and time range |
| `log_state_transition` | `case_id, from_state, to_state, trigger` | Log a workflow state transition |
| `log_escalation` | `case_id, agent_id, reason, target` | Log an escalation event |
| `log_clinician_action` | `case_id, reviewer_id, action, notes` | Log a clinician review action |

### 8.4 llm-mcp

Provides a unified interface for LLM calls. All agents go through this MCP server rather than calling the Anthropic API directly.

**Tools:**

| Tool | Parameters | Description |
|------|-----------|-------------|
| `generate` | `system_prompt, user_prompt, max_tokens, temperature` | Generate LLM response |
| `generate_structured` | `system_prompt, user_prompt, output_schema` | Generate structured JSON output conforming to a schema |
| `analyze_document` | `document_content, extraction_schema` | Extract structured data from a clinical document |

### 8.5 workflow-mcp

Manages workflow state and inter-agent coordination.

**Tools:**

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_workflow_state` | `case_id` | Get current workflow state |
| `update_workflow_state` | `case_id, new_state, agent_id` | Transition workflow to new state |
| `get_previous_agent_output` | `case_id, agent_id` | Retrieve a specific agent's output from the workflow |
| `check_confidence_threshold` | `agent_id, confidence_score` | Check if a confidence score meets the threshold for a given agent |
| `trigger_escalation` | `case_id, agent_id, reason` | Trigger an escalation event and pause workflow |
| `request_human_review` | `case_id, agent_id, review_data` | Queue a case for human review |

---

## 9. LangGraph Workflow

### 9.1 Graph Definition

The LangGraph workflow is a directed graph where nodes are agents and edges define transitions (including conditional routing for governance checks).

```
                          ┌────────────────┐
                          │   START         │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ ethics-consent  │──── DENIED ──→ END (consent_denied)
                          └───────┬────────┘
                              GRANTED
                          ┌───────▼────────┐
                          │ input-          │──── ESCALATE ──→ HUMAN_REVIEW
                          │ aggregation     │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ data-quality    │──── INCOMPLETE (after 3 rounds) ──→ ABSTAIN
                          │                 │──── FOLLOW_UP ──→ (loop: max 3)
                          └───────┬────────┘
                              VALIDATED
                          ┌───────▼────────┐
                          │ profile-        │──── LOW_CONFIDENCE ──→ HUMAN_REVIEW
                          │ synthesis       │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ prediction      │──── LOW_CONFIDENCE ──→ HUMAN_REVIEW
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ confidence-     │──── ABSTAIN ──→ END (abstained)
                          │ abstention      │──── PARTIAL ──→ domain-analysis (partial)
                          └───────┬────────┘
                              PROCEED
                          ┌───────▼────────┐
                          │ domain-analysis │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ guideline-      │
                          │ generation      │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ bias-monitoring │──── FLAGGED ──→ HUMAN_REVIEW
                          └───────┬────────┘
                              PASSED
                          ┌───────▼────────┐
                          │ goal-generation │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ milestone-      │
                          │ planning        │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ caregiver-      │
                          │ guidance        │
                          └───────┬────────┘
                                  │
                          ┌───────▼────────┐
                          │ MANDATORY       │
                          │ CLINICIAN       │──── APPROVE ──→ END (approved)
                          │ REVIEW          │──── MODIFY  ──→ END (modified+approved)
                          │                 │──── REJECT  ──→ END (rejected)
                          │                 │──── PARTIAL ──→ (loop: revise flagged)
                          └────────────────┘
```

### 9.2 Workflow State Schema

The LangGraph state object shared across all agents:

```python
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph

class WorkflowState(TypedDict):
    case_id: str
    child_id: str
    current_step: str
    workflow_status: Literal[
        "INITIATED", "CONSENT_PENDING", "CONSENT_GRANTED", "CONSENT_DENIED",
        "INPUT_COLLECTION", "DATA_VALIDATION", "FOLLOW_UP",
        "PROFILE_BUILDING", "DOMAIN_PRIORITIZATION", "CONFIDENCE_CHECK",
        "DOMAIN_ANALYSIS", "GUIDELINE_GENERATION", "BIAS_CHECK",
        "GOAL_GENERATION", "MILESTONE_PLANNING", "CAREGIVER_GUIDANCE",
        "AWAITING_CLINICIAN_REVIEW", "APPROVED", "MODIFIED", "REJECTED",
        "PARTIAL_APPROVED", "ABSTAINED", "ESCALATED_TO_REVIEWER",
        "ON_HOLD", "CLOSED"
    ]

    # Consent
    consent_status: Optional[Literal["GRANTED", "PENDING", "DENIED"]]

    # Input data
    raw_inputs: Optional[dict]
    structured_inputs: Optional[dict]
    follow_up_round: int
    follow_up_questions: Optional[list]

    # Data quality
    data_quality_score: Optional[float]
    data_quality_gaps: Optional[list]
    data_quality_status: Optional[Literal["VALIDATED", "INCOMPLETE", "FOLLOW_UP"]]

    # Profile
    child_profile: Optional[dict]
    profile_confidence: Optional[float]

    # Prediction
    domain_priorities: Optional[list]
    prediction_confidence: Optional[dict]

    # Confidence check
    proceed_decision: Optional[Literal["PROCEED", "ABSTAIN", "PARTIAL_PROCEED"]]
    abstention_reason: Optional[str]
    partial_proceed_domains: Optional[list]

    # Domain analysis
    domain_analysis: Optional[list]

    # Guidelines
    intervention_guidelines: Optional[list]
    guideline_confidence: Optional[dict]

    # Bias check
    bias_check_status: Optional[Literal["PASSED", "FLAGGED", "REVIEW_REQUIRED"]]
    bias_concerns: Optional[list]

    # Goals
    smart_goals: Optional[list]

    # Milestones
    milestones: Optional[list]

    # Caregiver guidance
    caregiver_guidance: Optional[dict]

    # Review
    clinician_review: Optional[dict]

    # Audit
    agent_outputs: list  # Accumulated agent output references
    escalation_history: list

    # Error handling
    error: Optional[str]
```

### 9.3 Graph Construction

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(WorkflowState)

# Add agent nodes
workflow.add_node("ethics_consent", ethics_consent_agent)
workflow.add_node("input_aggregation", input_aggregation_agent)
workflow.add_node("data_quality", data_quality_agent)
workflow.add_node("profile_synthesis", profile_synthesis_agent)
workflow.add_node("prediction", prediction_agent)
workflow.add_node("confidence_abstention", confidence_abstention_agent)
workflow.add_node("domain_analysis", domain_analysis_agent)
workflow.add_node("guideline_generation", guideline_generation_agent)
workflow.add_node("bias_monitoring", bias_monitoring_agent)
workflow.add_node("goal_generation", goal_generation_agent)
workflow.add_node("milestone_planning", milestone_planning_agent)
workflow.add_node("caregiver_guidance", caregiver_guidance_agent)
workflow.add_node("clinician_review", clinician_review_handler)

# Entry point
workflow.set_entry_point("ethics_consent")

# Conditional edges
workflow.add_conditional_edges("ethics_consent", route_consent)
workflow.add_conditional_edges("input_aggregation", route_input)
workflow.add_conditional_edges("data_quality", route_data_quality)
workflow.add_conditional_edges("profile_synthesis", route_profile)
workflow.add_conditional_edges("prediction", route_prediction)
workflow.add_conditional_edges("confidence_abstention", route_confidence)
workflow.add_edge("domain_analysis", "guideline_generation")
workflow.add_conditional_edges("bias_monitoring", route_bias)
workflow.add_edge("goal_generation", "milestone_planning")
workflow.add_edge("milestone_planning", "caregiver_guidance")
workflow.add_edge("caregiver_guidance", "clinician_review")
workflow.add_conditional_edges("clinician_review", route_review)

app = workflow.compile()
```

---

## 10. Agent Contracts

Each agent has a defined input/output contract. All agents receive the shared `WorkflowState` and return an updated state. All agents must use MCP server tools for data access and must log audit events.

### 10.1 Ethics & Consent Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `ethics-consent` |
| **Trigger** | Case initiated |
| **Input** | `case_id`, `reporter_id` |
| **MCP Tools** | `dynamo-mcp.query_by_case`, `audit-mcp.log_event` |
| **Output** | `consent_status`: GRANTED / PENDING / DENIED |
| **State Update** | `consent_status`, `workflow_status` |
| **Routing** | GRANTED → `input-aggregation`; DENIED → END; PENDING → HOLD |
| **Traces** | BR-002, FR-001 |

### 10.2 Input Aggregation Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `input-aggregation` |
| **Trigger** | Consent granted |
| **Input** | Uploaded documents (S3 keys), chat messages |
| **MCP Tools** | `s3-mcp.get_document`, `llm-mcp.analyze_document`, `dynamo-mcp.put_screening_input`, `audit-mcp.log_event` |
| **Output** | `structured_inputs` with per-field confidence scores, list of missing fields |
| **State Update** | `raw_inputs`, `structured_inputs` |
| **Routing** | Success → `data-quality`; Extraction failure → ESCALATE |
| **Traces** | BR-003, FR-002 |

### 10.3 Data Quality Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `data-quality` |
| **Trigger** | Input aggregation complete |
| **Input** | `structured_inputs` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | `data_quality_score`, `data_quality_gaps`, `follow_up_questions` (if incomplete) |
| **State Update** | `data_quality_score`, `data_quality_status`, `follow_up_round` |
| **Routing** | VALIDATED → `profile-synthesis`; FOLLOW_UP → loop (max 3); INCOMPLETE → ABSTAIN |
| **Traces** | BR-003, BR-004, FR-003 |

### 10.4 Profile Synthesis Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `profile-synthesis` |
| **Trigger** | Data quality validated |
| **Input** | `structured_inputs`, `data_quality_score` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_child_profile`, `audit-mcp.log_event` |
| **Output** | Unified child profile (demographics, strengths, support areas, family context, history) |
| **State Update** | `child_profile`, `profile_confidence` |
| **Routing** | Confidence >= threshold → `prediction`; Below threshold → HUMAN_REVIEW |
| **Traces** | BR-008, FR-004 |

### 10.5 Prediction Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `prediction` |
| **Trigger** | Profile synthesis complete |
| **Input** | `child_profile` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | Prioritized domain list with confidence scores and rationale |
| **State Update** | `domain_priorities`, `prediction_confidence` |
| **Routing** | All domains >= threshold → `confidence-abstention`; Any below → flag + `confidence-abstention` |
| **Traces** | BR-004, FR-005 |

### 10.6 Confidence & Abstention Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `confidence-abstention` |
| **Trigger** | Prediction complete |
| **Input** | All preceding confidence scores, flagged issues |
| **MCP Tools** | `workflow-mcp.check_confidence_threshold`, `audit-mcp.log_event` |
| **Output** | Workflow decision: PROCEED / ABSTAIN / PARTIAL_PROCEED |
| **State Update** | `proceed_decision`, `abstention_reason`, `partial_proceed_domains` |
| **Routing** | PROCEED → `domain-analysis`; ABSTAIN → END; PARTIAL → `domain-analysis` (partial) |
| **Traces** | BR-004, BR-009, FR-006 |

### 10.7 Domain Analysis Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `domain-analysis` |
| **Trigger** | Confidence check passed |
| **Input** | `child_profile`, `domain_priorities` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | Focus areas per domain with current baselines and target directions |
| **State Update** | `domain_analysis` |
| **Routing** | Always → `guideline-generation` |
| **Traces** | FR-007 |

### 10.8 Guideline Generation Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `guideline-generation` |
| **Trigger** | Domain analysis complete |
| **Input** | `child_profile`, `domain_analysis` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | Draft intervention guidelines per domain/focus area |
| **State Update** | `intervention_guidelines`, `guideline_confidence` |
| **Routing** | Always → `bias-monitoring` |
| **Traces** | BR-006, FR-008 |

### 10.9 Bias Monitoring Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `bias-monitoring` |
| **Trigger** | Guideline generation complete |
| **Input** | `intervention_guidelines`, `child_profile` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | Bias check status: PASSED / FLAGGED / REVIEW_REQUIRED; bias concerns if flagged |
| **State Update** | `bias_check_status`, `bias_concerns` |
| **Routing** | PASSED → `goal-generation`; FLAGGED → HUMAN_REVIEW |
| **Traces** | BR-005, BR-007, FR-009 |

### 10.10 Goal Generation Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `goal-generation` |
| **Trigger** | Bias monitoring passed |
| **Input** | `intervention_guidelines`, `child_profile`, `domain_analysis` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | SMART goals (short-term 1–3 months, long-term 6–12 months) per focus area |
| **State Update** | `smart_goals` |
| **Routing** | Always → `milestone-planning` |
| **Traces** | BR-010, FR-010 |

### 10.11 Milestone Planning Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `milestone-planning` |
| **Trigger** | Goal generation complete |
| **Input** | `smart_goals`, `child_profile` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | Time-bound milestones per goal with progress markers |
| **State Update** | `milestones` |
| **Routing** | Always → `caregiver-guidance` |
| **Traces** | FR-011 |

### 10.12 Caregiver Guidance Agent

| Field | Value |
|-------|-------|
| **Agent ID** | `caregiver-guidance` |
| **Trigger** | Milestone planning complete |
| **Input** | `intervention_guidelines`, `smart_goals`, `milestones`, `child_profile` |
| **MCP Tools** | `llm-mcp.generate_structured`, `dynamo-mcp.put_agent_output`, `audit-mcp.log_event` |
| **Output** | Plain-language caregiver recommendations, home activities, daily routine suggestions |
| **State Update** | `caregiver_guidance` |
| **Routing** | Always → `clinician-review` (MANDATORY) |
| **Traces** | BR-007, FR-012 |

---

## 11. Frontend Architecture

### 11.1 Chatbot Interface (Intake)

**Route:** `/intake`

The conversational intake interface where clinicians upload reports and provide case context.

**Components:**
- `ChatWindow` — Main conversation display with message bubbles
- `MessageInput` — Text input with file attachment support
- `DocumentUploader` — Drag-and-drop upload for PDFs, clinical forms
- `FollowUpPrompt` — Displays system-generated follow-up questions
- `ExtractionPreview` — Shows extracted data for clinician confirmation
- `WorkflowProgress` — Step indicator showing current workflow position

**Key Interactions:**
1. Clinician opens new case → consent verification prompt
2. Clinician uploads documents → extraction preview shown for confirmation
3. System asks follow-up questions (max 3 rounds) → clinician responds
4. Real-time workflow progress shown as agents complete

### 11.2 Clinician Review Dashboard

**Route:** `/review`

The review interface where clinicians approve, modify, or reject generated plans.

**Components:**
- `ReviewQueue` — List of pending reviews with case summaries
- `PlanViewer` — Full plan display organized by section (profile, domains, guidelines, goals, milestones, caregiver guidance)
- `SectionReview` — Per-section approve/modify/reject controls
- `ModificationEditor` — Inline editing for clinician modifications
- `ConfidenceIndicator` — Visual confidence score per section
- `BiasAlerts` — Display bias monitoring flags and concerns
- `AuditTrailViewer` — Expandable audit log for the case
- `ReviewSubmit` — Final review action (approve/modify/reject/partial)

**Key Interactions:**
1. Clinician sees pending review queue sorted by date
2. Selects a case → full plan displayed with section-by-section review
3. Each section shows confidence score and any governance flags
4. Clinician can inline-edit any section (modifications logged)
5. Final action recorded with notes → audit trail updated

### 11.3 Case Dashboard

**Route:** `/dashboard`

Overview of all cases and their statuses.

**Components:**
- `CaseList` — Filterable/sortable list of all cases
- `CaseDetail` — Expanded view of a single case with timeline
- `StatusFilter` — Filter by workflow state
- `SearchBar` — Search by case ID, child ID, or keywords

---

## 12. Lambda Functions

All Lambda functions run on LocalStack + Docker. They are Python 3.11+ handlers.

| Function | Trigger | Description |
|----------|---------|-------------|
| `case-intake-handler` | API Gateway POST `/api/cases` | Creates a new case, initializes workflow state |
| `document-upload-handler` | API Gateway POST `/api/cases/{id}/documents` | Handles file upload to S3, triggers extraction |
| `workflow-orchestrator` | API Gateway POST `/api/cases/{id}/workflow/start` | Initializes and runs the LangGraph workflow |
| `workflow-resume-handler` | API Gateway POST `/api/cases/{id}/workflow/resume` | Resumes workflow after human review decision |
| `chat-handler` | API Gateway POST `/api/chat/{id}/message` | Processes chat messages, routes to appropriate agent |
| `clinician-review-handler` | API Gateway POST `/api/cases/{id}/review` | Records clinician review decisions |
| `audit-logger` | Internal (invoked by other Lambdas) | Writes audit events to AuditEvents table |
| `case-query-handler` | API Gateway GET `/api/cases/*` | Handles all case query endpoints |
| `review-queue-handler` | API Gateway GET `/api/reviews/pending` | Returns pending review queue |

---

## 13. Docker Compose Configuration

```yaml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=dynamodb,s3,lambda,apigateway
      - DEBUG=1
      - LAMBDA_EXECUTOR=docker
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "./init-scripts:/etc/localstack/init/ready.d"
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "localstack-data:/var/lib/localstack"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:4566
    depends_on:
      - localstack

volumes:
  localstack-data:
```

---

## 14. Workflow State Machine

Maps to the business workflow state machine (Business_workflow.md Section 3) with technical implementation details.

| State | Triggered By | Next States | Agent Responsible |
|-------|-------------|-------------|-------------------|
| `INITIATED` | POST `/api/cases` | CONSENT_PENDING | System |
| `CONSENT_PENDING` | Workflow start | CONSENT_GRANTED, CONSENT_DENIED | ethics-consent |
| `CONSENT_GRANTED` | Consent verified | INPUT_COLLECTION | ethics-consent |
| `CONSENT_DENIED` | Consent denied | END (terminal) | ethics-consent |
| `INPUT_COLLECTION` | Consent granted | DATA_VALIDATION | input-aggregation |
| `DATA_VALIDATION` | Input aggregated | PROFILE_BUILDING, FOLLOW_UP, ESCALATED | data-quality |
| `FOLLOW_UP` | Data incomplete | DATA_VALIDATION (loop), ABSTAINED | data-quality |
| `PROFILE_BUILDING` | Data validated | DOMAIN_PRIORITIZATION, ESCALATED | profile-synthesis |
| `DOMAIN_PRIORITIZATION` | Profile built | CONFIDENCE_CHECK | prediction |
| `CONFIDENCE_CHECK` | Domains prioritized | DOMAIN_ANALYSIS, ABSTAINED, PARTIAL | confidence-abstention |
| `DOMAIN_ANALYSIS` | Confidence passed | GUIDELINE_GENERATION | domain-analysis |
| `GUIDELINE_GENERATION` | Domains analyzed | BIAS_CHECK | guideline-generation |
| `BIAS_CHECK` | Guidelines generated | GOAL_GENERATION, ESCALATED | bias-monitoring |
| `GOAL_GENERATION` | Bias passed | MILESTONE_PLANNING | goal-generation |
| `MILESTONE_PLANNING` | Goals generated | CAREGIVER_GUIDANCE | milestone-planning |
| `CAREGIVER_GUIDANCE` | Milestones planned | AWAITING_CLINICIAN_REVIEW | caregiver-guidance |
| `AWAITING_CLINICIAN_REVIEW` | All agents done | APPROVED, MODIFIED, REJECTED, PARTIAL_APPROVED | Clinician (human) |
| `APPROVED` | Clinician approves | END (terminal) | Clinician |
| `MODIFIED` | Clinician modifies | APPROVED | Clinician |
| `REJECTED` | Clinician rejects | CLOSED or re-trigger | Clinician |
| `PARTIAL_APPROVED` | Partial approval | Loop back for revisions | Clinician |
| `ABSTAINED` | Confidence too low | END (terminal — manual review) | confidence-abstention |
| `ESCALATED_TO_REVIEWER` | Any escalation trigger | AWAITING_CLINICIAN_REVIEW or ON_HOLD | Any agent |
| `ON_HOLD` | Awaiting additional info | Resumes at paused step | System |
| `CLOSED` | Manual closure | END (terminal) | System/Clinician |

---

## 15. Case ID Generation

Format: `AIG-YYYY-NNNN`

- `AIG` — Autism Intervention Guideline (configurable via `CASE_ID_PREFIX`)
- `YYYY` — Year of case creation
- `NNNN` — Sequential counter, zero-padded

Implementation: Atomic counter in DynamoDB (`CaseCounter` table) to guarantee uniqueness across concurrent requests.

---

## 16. Security Requirements

### 16.1 Data Protection
- All data encrypted at rest (DynamoDB encryption, S3 server-side encryption) — simulated via LocalStack for POC
- All API traffic over HTTPS (LocalStack HTTP acceptable for local dev)
- No child PII in application-level logs — only case IDs and agent IDs
- API keys stored in `.claude/settings.local.json`, never committed to version control

### 16.2 Authentication & Authorization (POC Scope)
- Clinician authentication via API key or session token (simplified for POC)
- Role-based access: `reporter` (upload + view own cases), `reviewer` (full review access), `admin` (configuration + audit)
- Future: integration with clinical identity providers (OAuth2/SAML)

### 16.3 Audit Integrity
- AuditEvents table has no `DeleteItem` or `UpdateItem` permissions — append-only
- Every event includes input/output hashes for tamper detection
- Retention period enforced via DynamoDB TTL (configurable, default 7 years)

---

## 17. Error Handling & Resilience

| Scenario | Handling |
|----------|---------|
| Agent LLM call fails | Retry with exponential backoff (max 3 retries), then escalate |
| Agent confidence below threshold | Route to confidence-abstention agent for decision |
| Document extraction fails | Mark fields as `extraction_failed`, escalate to human |
| DynamoDB write fails | Retry, log error audit event, pause workflow |
| Workflow timeout (>60s for full plan) | Log partial progress, allow resume |
| MCP server unreachable | Circuit breaker pattern, escalate after 3 failures |
| Concurrent case modifications | Optimistic locking via DynamoDB conditional writes |

---

## 18. Testing Strategy

### 18.1 Unit Tests
- Agent logic (input → output transformation) with mocked MCP tools
- LangGraph routing logic (conditional edge functions)
- Data validation and schema compliance

### 18.2 Integration Tests
- Full workflow execution against LocalStack
- MCP server tool invocations against DynamoDB/S3
- API endpoint request/response validation

### 18.3 End-to-End Tests
- Complete case flow: intake → all agents → clinician review → approval
- Escalation paths: low confidence, bias flagged, incomplete data
- Follow-up question loops (1, 2, 3 rounds + abstention)

### 18.4 Governance Tests
- Consent denial blocks all processing
- Data below completeness threshold triggers follow-up or abstention
- Bias detection flags route to clinician review
- No output reaches caregiver without clinician approval
- All state transitions generate audit events

### 18.5 Synthetic Dataset Validation
- Run all 500 child profiles from `kaggle_dataset/` through the workflow
- Verify structured outputs match expected schema
- Validate SMART goal format compliance (specific, measurable, achievable, relevant, time-bound)
- Check milestone progression logic (baselines → targets)

---

## 19. Project Directory Structure

```
AI_Driven_Personalized_Intervention/
├── CLAUDE.md                          # Project instructions
├── Business_requirement.md            # Business rules and requirements
├── Business_workflow.md               # Workflow steps and state machine
├── technical_requirement.md           # This document
├── docker-compose.yml                 # LocalStack + frontend services
├── init-scripts/                      # LocalStack initialization
│   ├── create-tables.sh              # DynamoDB table creation
│   ├── create-buckets.sh             # S3 bucket creation
│   └── deploy-lambdas.sh            # Lambda deployment
├── backend/
│   ├── requirements.txt
│   ├── llm_factory.py               # Shared LLM client factory
│   ├── config.py                    # Environment variable configuration
│   ├── lambdas/
│   │   ├── case_intake_handler.py
│   │   ├── document_upload_handler.py
│   │   ├── workflow_orchestrator.py
│   │   ├── workflow_resume_handler.py
│   │   ├── chat_handler.py
│   │   ├── clinician_review_handler.py
│   │   ├── audit_logger.py
│   │   ├── case_query_handler.py
│   │   └── review_queue_handler.py
│   ├── agents/
│   │   ├── base_agent.py            # Base class with MCP tool access + audit logging
│   │   ├── ethics_consent.py
│   │   ├── input_aggregation.py
│   │   ├── data_quality.py
│   │   ├── profile_synthesis.py
│   │   ├── prediction.py
│   │   ├── confidence_abstention.py
│   │   ├── domain_analysis.py
│   │   ├── guideline_generation.py
│   │   ├── bias_monitoring.py
│   │   ├── goal_generation.py
│   │   ├── milestone_planning.py
│   │   └── caregiver_guidance.py
│   ├── workflow/
│   │   ├── graph.py                 # LangGraph workflow definition
│   │   ├── state.py                 # WorkflowState TypedDict
│   │   └── routing.py              # Conditional edge routing functions
│   ├── mcp_servers/
│   │   ├── dynamo_mcp.py
│   │   ├── s3_mcp.py
│   │   ├── audit_mcp.py
│   │   ├── llm_mcp.py
│   │   └── workflow_mcp.py
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── e2e/
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── api/                     # API client
│       ├── pages/
│       │   ├── IntakePage.jsx       # Chatbot intake
│       │   ├── ReviewPage.jsx       # Clinician review dashboard
│       │   └── DashboardPage.jsx    # Case overview
│       └── components/
│           ├── chat/
│           │   ├── ChatWindow.jsx
│           │   ├── MessageInput.jsx
│           │   ├── DocumentUploader.jsx
│           │   └── FollowUpPrompt.jsx
│           ├── review/
│           │   ├── ReviewQueue.jsx
│           │   ├── PlanViewer.jsx
│           │   ├── SectionReview.jsx
│           │   └── ModificationEditor.jsx
│           └── shared/
│               ├── WorkflowProgress.jsx
│               ├── ConfidenceIndicator.jsx
│               └── AuditTrailViewer.jsx
└── kaggle_dataset/                  # Synthetic dataset (500 children, 22K+ records)
    ├── child_profiles.csv
    ├── screening_assessments.csv
    ├── intervention_guidelines.csv
    ├── smart_goals.csv
    ├── therapy_notes.csv
    ├── milestones.csv
    ├── caregiver_guidance.csv
    ├── progress_summaries.csv
    ├── audit_log.csv
    └── dataset-metadata.json
```

---

## 20. Requirement Traceability

Maps business requirements to technical components.

| Requirement | Technical Component |
|-------------|-------------------|
| BR-001: Mandatory Clinician Review | `clinician-review` node in LangGraph (terminal gate), `ClinicianReviews` table, `/api/cases/{id}/review` endpoint |
| BR-002: Consent Before Processing | `ethics-consent` agent as workflow entry point, blocks all downstream processing |
| BR-003: Data Completeness Threshold | `data-quality` agent with `DATA_COMPLETENESS_THRESHOLD` env var, follow-up loop (max `MAX_FOLLOWUP_ROUNDS`) |
| BR-004: Confidence-Based Abstention | `confidence-abstention` agent, `CONFIDENCE_THRESHOLD_*` env vars, per-agent confidence scores in `AgentOutputs` |
| BR-005: Bias Check Before Output | `bias-monitoring` agent positioned after `guideline-generation` in the graph |
| BR-006: No Diagnosis | System prompt constraint in `llm-mcp.generate` calls, output validation in `guideline-generation` |
| BR-007: Cultural/Language Sensitivity | `child_profile.family_context` passed to `caregiver-guidance` agent, `home_language` in caregiver output |
| BR-008: Traceability | `AuditEvents` table (append-only), `audit-mcp.log_event` in every agent, input/output hashes |
| BR-009: Escalation Paths | `workflow-mcp.trigger_escalation`, conditional edges in LangGraph, `ESCALATED_TO_REVIEWER` state |
| BR-010: SMART Goal Format | `goal-generation` agent system prompt + output schema validation, structured output via `llm-mcp.generate_structured` |
| NFR-001: Response Time (<60s) | Async LangGraph execution, agent-level timeouts, workflow timeout tracking |
| NFR-002: Audit Retention (7 years) | DynamoDB TTL on `AuditEvents` set to `AUDIT_RETENTION_DAYS` |
| NFR-003: Data Privacy | No PII in logs, encryption at rest (LocalStack simulation), S3 server-side encryption |
| NFR-004: Configurable Thresholds | All thresholds externalized to environment variables (Section 4) |
| NFR-005: Model Swappability | `llm_factory.py` reads `LLM_MODEL_ID` + `LLM_PROVIDER` — zero code changes to swap |

---

## 21. Development Workflow

1. **Start infrastructure:** `docker-compose up -d` (starts LocalStack + frontend)
2. **Initialize resources:** `./init-scripts/create-tables.sh && ./init-scripts/create-buckets.sh`
3. **Deploy lambdas:** `./init-scripts/deploy-lambdas.sh`
4. **Run backend tests:** `cd backend && pytest tests/`
5. **Run frontend:** `cd frontend && npm start` (port 3000)
6. **Test full workflow:** Use the chatbot to create a case and run through the entire pipeline
7. **Validate with dataset:** Run the 500 synthetic profiles through the workflow for regression testing
