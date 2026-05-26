# Business Requirements: AI-Driven Personalized Intervention Guideline Generator

## 1. Purpose

This POC builds a governance-aware Agentic AI system that takes autism screening reports and clinician assessment inputs as starting points and generates personalized, structured intervention guidelines for children with autism. The system uses multiple specialized agents to process inputs, synthesize child profiles, prioritize developmental domains, generate intervention plans with SMART goals, create milestones, and produce caregiver-friendly guidance — all under mandatory clinician review before any output reaches families.

The system does NOT diagnose. It does NOT replace clinicians. It is a clinical decision support tool that reduces documentation burden and improves consistency in intervention planning.

---

## 2. Primary Users

### 2.1 Clinician / Authorized Interventionist (Primary Reporter)

The clinician or authorized early interventionist who uploads screening reports, assessment data, and observational notes into the system. They interact through a chatbot interface that collects information conversationally.

Responsibilities:
- Upload screening reports (system-generated or manual)
- Provide additional child/family context when prompted
- Review and approve/modify/reject generated intervention plans

### 2.2 Clinician Reviewer

A qualified professional (developmental pediatrician, BCBA, speech-language pathologist, or other autism specialist) who reviews all AI-generated outputs before they are shared with caregivers.

Responsibilities:
- Review generated intervention guidelines, goals, and milestones
- Approve, modify, or reject system outputs
- Provide override notes when modifying AI recommendations
- Escalate cases that require additional specialist input

### 2.3 Caregiver / Parent (End Consumer — Read-Only)

Parents or caregivers receive the clinician-approved intervention plan. They do NOT interact with the AI system directly. They only see outputs that have been reviewed and approved by a qualified professional.

### 2.4 System Administrator

Manages system configuration, confidence thresholds, model settings, and audit access.

---

## 3. Input Types

The system accepts the following inputs through the chatbot interface:

| Input Type | Description |
|---|---|
| Screening Reports | Outputs from autism screening tools (e.g., M-CHAT-R, ADOS-2 reports, or system-generated reports from prior screening tools) |
| Clinical Assessment Reports | Developmental pediatric reports, speech-language assessments, OT assessments, feeding evaluations |
| Observational Notes | Clinician or teacher observations about the child's behavior, communication, and social interaction |
| Family Context | Family structure, home environment, cultural considerations, language(s) spoken, available support systems |
| Prior Intervention History | Any existing therapy records, IEP/IFSP documents, progress notes |
| Supporting Documents | PDFs, scanned reports, clinical forms |

---

## 4. System Outputs

All outputs are generated as drafts requiring clinician approval:

| Output | Description |
|---|---|
| Unified Child Profile | Comprehensive profile including strengths, support areas, developmental history, family context |
| Domain Priorities | Ranked list of developmental domains requiring intervention (communication, behavioral, motor, sensory, etc.) |
| Domain Analysis | Detailed breakdown of each priority domain into specific focus areas |
| Intervention Guidelines | Personalized strategies, suggested approaches, home-based practice ideas |
| SMART Goals | Specific, Measurable, Achievable, Relevant, Time-bound developmental goals (short-term and long-term) |
| Milestone Plan | Time-bound checkpoints tied to goals with expected progress markers |
| Caregiver Guidance | Plain-language recommendations for parents/caregivers for home use |
| Audit Trail | Complete log of all agent decisions, confidence scores, and state transitions |

---

## 5. Business Rules

### BR-001: Mandatory Clinician Review
No AI-generated intervention plan, goal, milestone, or caregiver recommendation shall be delivered to a caregiver or parent without explicit clinician approval.

### BR-002: Consent Before Processing
The system must verify that proper consent has been obtained from the authorized reporter before processing any child data. Without consent, the system must not proceed.

### BR-003: Data Completeness Threshold
If required input data (child age, screening results, at least one assessment area) is below the minimum completeness threshold, the system must either:
- Ask follow-up questions to collect missing information (max 3 rounds)
- Abstain from generating output and escalate to clinician for manual review

### BR-004: Confidence-Based Abstention
If any workflow agent's confidence score falls below the configurable threshold, the system must:
- Flag the specific output as low-confidence
- Escalate to clinician review with explanation
- NOT proceed to subsequent workflow steps that depend on the flagged output

### BR-005: Bias Check Before Output
All generated intervention guidelines must pass bias monitoring before being presented for clinician review. If bias is detected, the case must be flagged and the specific concern documented.

### BR-006: No Diagnosis
The system must never generate diagnostic statements. It generates intervention planning support only. Any output that could be interpreted as a diagnosis must be blocked.

### BR-007: Cultural and Language Sensitivity
Caregiver guidance must be generated with awareness of the family's cultural context and primary language (when provided). The system must not generate culturally inappropriate recommendations.

### BR-008: Traceability
Every agent decision, output, state transition, and human review action must be logged in an immutable audit trail with timestamps, agent IDs, confidence scores, and rationale.

### BR-009: Escalation Paths
Cases must be escalable at any point in the workflow. Escalation reasons include: low confidence, incomplete data, bias detection, conflicting assessment data, or clinician override.

### BR-010: SMART Goal Format
All generated goals must follow the SMART format: Specific, Measurable, Achievable, Relevant, and Time-bound. Vague goals such as "improve communication in 6 months" are not acceptable.

---

## 6. Governance Requirements

### 6.1 Ethics and Consent Gate
- System checks for valid consent before any data processing
- Consent must be explicitly recorded with timestamp
- If consent is withdrawn, all processing must stop and data handling follows retention policy

### 6.2 Data Quality Gate
- Validates completeness of structured input data
- Checks for conflicting information across sources
- Generates adaptive follow-up questions when data is incomplete
- Escalates to clinician when data cannot be completed after max attempts

### 6.3 Bias Monitoring Gate
- Checks whether generated recommendations show demographic bias
- Checks for cultural or language-related bias
- Checks for socioeconomic proxy bias
- Flags cases where similar profiles receive inconsistent recommendations
- All flagged cases route to clinician review with bias concern documented

### 6.4 Confidence and Abstention Gate
- Reviews confidence levels at each workflow step
- Stops the workflow when the system should not proceed
- Documents reason for abstention
- Escalates to clinician with full context

---

## 7. Human-in-the-Loop Decision Gates

### 7.1 After Input Aggregation
Trigger human review if:
- Screening reports are unreadable or corrupted
- Input data contains significant contradictions
- System cannot extract minimum required fields
- Reporter provides insufficient information after 3 follow-up rounds

### 7.2 After Profile Synthesis
Trigger human review if:
- Profile confidence is below threshold
- Critical information gaps remain
- Conflicting data sources cannot be reconciled

### 7.3 After Domain Prioritization
Trigger human review if:
- Prediction confidence is low for any prioritized domain
- Domain priorities conflict with explicit clinician notes
- System detects unusual domain combination

### 7.4 After Guideline Generation
Trigger human review if:
- Guidelines confidence is below threshold
- Bias monitoring flags the guidelines
- Generated guidelines conflict with known contraindications

### 7.5 Final Clinician Review (Mandatory)
ALL generated outputs must undergo final clinician review regardless of confidence scores. This is non-negotiable. The clinician can:
- **Approve** — output proceeds to caregiver delivery
- **Modify** — clinician edits are applied and become the final version
- **Reject** — output is discarded, clinician provides manual alternative or requests re-generation with additional context

---

## 8. Non-Functional Requirements

### NFR-001: Response Time
The system should generate a complete intervention plan draft within 60 seconds of having all required inputs.

### NFR-002: Audit Retention
All audit logs must be retained for the configured retention period (default: 7 years for clinical records).

### NFR-003: Data Privacy
All child data must be encrypted at rest and in transit. No child data should be logged in application-level logs.

### NFR-004: Configurable Thresholds
All confidence thresholds, data completeness requirements, and workflow parameters must be configurable via environment variables without code changes.

### NFR-005: Model Swappability
The LLM model must be swappable via environment variables. The system must work with any compatible LLM without code changes.

### NFR-006: Offline Capability (Future)
For POC, internet connectivity is required for LLM access. Future versions should explore on-premise model deployment for clinical settings.
