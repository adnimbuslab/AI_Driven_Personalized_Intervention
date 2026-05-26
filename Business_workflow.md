# Business Workflow: AI-Driven Personalized Intervention Guideline Generator

## 1. End-to-End Workflow Overview

```
Clinician uploads screening reports & assessments
       ↓
[Ethics & Consent Agent] — Verify consent
       ↓
[Input Aggregation Agent] — Convert unstructured inputs to structured data
       ↓
[Data Quality Agent] — Validate completeness; ask follow-up questions or escalate
       ↓
[Profile Synthesis Agent] — Build unified child profile
       ↓
[Prediction Agent] — Prioritize developmental domains
       ↓
[Confidence & Abstention Agent] — Check confidence; proceed or abstain
       ↓
[Domain Analysis Agent] — Break domains into specific focus areas
       ↓
[Guideline Generation Agent] — Generate draft intervention guidelines
       ↓
[Bias Monitoring Agent] — Check for demographic/cultural/language bias
       ↓
[Goal Generation Agent] — Create SMART goals from guidelines
       ↓
[Milestone Planning Agent] — Create short-term & long-term milestones
       ↓
[Caregiver Guidance Agent] — Generate plain-language caregiver recommendations
       ↓
[MANDATORY CLINICIAN REVIEW] — Approve / Modify / Reject
       ↓
Approved plan delivered to caregivers/interventionists
```

---

## 2. Detailed Workflow Steps

### Step 1: Consent Verification

**Agent:** Ethics and Consent Agent

**Trigger:** Clinician initiates a new case

**Process:**
1. System checks whether the authorized reporter has provided consent for data processing
2. Consent type and scope are verified (data storage, AI processing, sharing with reviewers)
3. Consent is recorded with timestamp in the audit trail

**Outputs:**
- Consent status: `GRANTED` | `PENDING` | `DENIED`
- If `DENIED` → workflow stops, case flagged as consent-pending

**Decision Gate:** If consent is not granted, the system does not proceed with any data processing.

---

### Step 2: Input Aggregation

**Agent:** Input Aggregation Agent

**Trigger:** Consent verified successfully

**Process:**
1. Clinician uploads screening reports through the chatbot interface (PDFs, clinical forms, text narratives)
2. Agent extracts structured fields from uploaded documents:
   - Child demographics (name, DOB, age, gender)
   - Screening tool used and scores (M-CHAT-R, ADOS-2, etc.)
   - Areas of concern identified
   - Clinician observations
   - Family information
   - Prior interventions or therapies
3. If documents are unreadable or critical fields cannot be extracted, agent asks follow-up questions
4. Agent presents extracted data to clinician for confirmation

**Outputs:**
- Structured input record with confidence scores per field
- List of missing/uncertain fields
- Document metadata and extraction results

**Decision Gate:** If extraction confidence is below threshold or documents are unreadable → escalate to human review.

**Example Interaction:**
```
Clinician: [Uploads M-CHAT-R report + developmental pediatric assessment]

System: I've reviewed the uploaded reports. I've extracted the following:
- Child: Age 3 years 2 months
- Screening Tool: M-CHAT-R (Score: 8/20 - Medium Risk)
- Areas flagged: Expressive language delay, limited joint attention, sensory sensitivities
- Assessment: Developmental pediatric evaluation confirms ASD Level 1

I notice the reports don't include information about the family's home environment 
or current support services. Could you share:
1. What is the primary language spoken at home?
2. Are there any current therapies or interventions in place?
```

---

### Step 3: Data Quality Validation

**Agent:** Data Quality Agent

**Trigger:** Input aggregation complete

**Process:**
1. Validate all required fields are present and consistent
2. Check for contradictions between different input sources
3. Verify age/DOB consistency
4. Confirm minimum data threshold is met for intervention planning
5. If data is incomplete:
   - Generate adaptive follow-up questions (max 3 rounds)
   - If still incomplete after 3 rounds → escalate with abstention

**Outputs:**
- Data quality score (percentage completeness)
- List of validated fields
- List of remaining gaps
- Consistency check results

**Decision Gate:**
- Data quality >= threshold → proceed to profile synthesis
- Data quality < threshold AND follow-up exhausted → escalate to clinician for manual data entry or case closure

---

### Step 4: Profile Synthesis

**Agent:** Profile Synthesis Agent

**Trigger:** Data quality validation passed

**Process:**
1. Aggregate all structured input data into a unified child profile
2. Identify and document child's strengths (not just deficits)
3. Identify support areas across all developmental domains
4. Include family context: home environment, cultural background, languages, available support
5. Include relevant history: prior interventions, medical history, school setting
6. Flag any information that appears inconsistent for human attention

**Outputs:**
- Unified Child Profile document containing:
  - Child demographics
  - Developmental strengths
  - Areas requiring support
  - Family context and resources
  - Intervention history
  - Environmental factors
  - Cultural considerations

**Example Output:**
```json
{
  "childId": "AIG-2026-0001",
  "age": "3 years 2 months",
  "strengths": [
    "Strong visual learner",
    "Shows interest in music and rhythm",
    "Good gross motor skills",
    "Affectionate with familiar adults"
  ],
  "supportAreas": [
    "Expressive language (limited to single words)",
    "Joint attention (does not consistently follow point)",
    "Sensory processing (tactile defensiveness)",
    "Play skills (limited pretend play)"
  ],
  "familyContext": {
    "primaryLanguage": "English",
    "homeEnvironment": "Two-parent household, one sibling (age 6)",
    "currentSupports": "Speech therapy 1x/week",
    "culturalNotes": "Family prefers home-based activities"
  }
}
```

---

### Step 5: Domain Prioritization

**Agent:** Prediction Agent

**Trigger:** Profile synthesis complete

**Process:**
1. Analyze the child profile to identify all developmental domains requiring intervention
2. Prioritize domains based on:
   - Severity of delay or concern
   - Impact on daily functioning
   - Developmental stage appropriateness
   - Interdependencies between domains
3. Assign confidence scores to each priority
4. Flag low-confidence priorities for clinician attention

**Developmental Domains:**
- Communication (receptive, expressive, social communication)
- Social Interaction (joint attention, peer engagement, emotional regulation)
- Behavioral Regulation (self-regulation, transitions, routines)
- Sensory Processing (tactile, auditory, visual, proprioceptive)
- Motor Skills (fine motor, gross motor, oral motor)
- Adaptive / Self-Care (feeding, dressing, toileting)
- Play and Cognitive (pretend play, problem-solving, imitation)

**Outputs:**
- Prioritized domain list with confidence scores
- Rationale for each priority ranking
- Flags for low-confidence predictions

**Decision Gate:** If prediction confidence < threshold for any domain → flag for clinician review before proceeding.

---

### Step 6: Confidence Check

**Agent:** Confidence and Abstention Agent

**Trigger:** Domain prioritization complete

**Process:**
1. Review confidence scores from all preceding steps
2. Evaluate whether the system has sufficient information and certainty to generate intervention guidelines
3. Check for:
   - Low aggregate confidence across multiple steps
   - Critical information gaps that were flagged but unresolved
   - Conflicting priorities that could not be reconciled
4. Decision: proceed or abstain

**Outputs:**
- Workflow status: `PROCEED` | `ABSTAIN` | `PARTIAL_PROCEED`
- If abstaining: detailed reason and what additional information would be needed
- If partial: which domains are safe to proceed and which need more input

**Decision Gate:**
- `PROCEED` → continue to domain analysis
- `ABSTAIN` → escalate entire case to clinician for manual intervention planning
- `PARTIAL_PROCEED` → continue for high-confidence domains, flag others for clinician

---

### Step 7: Domain Analysis

**Agent:** Domain Analysis Agent

**Trigger:** Confidence check passed (PROCEED or PARTIAL_PROCEED)

**Process:**
1. Take each prioritized developmental domain
2. Break it into specific, actionable focus areas
3. Connect focus areas to the child's specific profile data
4. Consider developmental stage appropriateness
5. Note interdependencies between focus areas

**Example:**
```
Domain: Communication (Priority 1, Confidence: 0.91)
├── Focus Area: Expressive vocabulary expansion
│   └── Current: ~20 single words, Target: 2-word combinations
├── Focus Area: Joint attention responses
│   └── Current: Inconsistent point-following, Target: Consistent response to point + gaze
├── Focus Area: Requesting behavior
│   └── Current: Reaches/cries, Target: Uses gesture or word to request
└── Focus Area: Social communication initiation
    └── Current: Rarely initiates, Target: Initiates interaction with familiar adults
```

**Outputs:**
- Detailed domain analysis with focus areas per domain
- Current baseline for each focus area (from profile data)
- Target direction (not yet full goals — that comes next)

---

### Step 8: Guideline Generation

**Agent:** Guideline Generation Agent

**Trigger:** Domain analysis complete

**Process:**
1. Generate personalized intervention guidelines based on:
   - Child's profile (strengths, support areas, family context)
   - Domain analysis (focus areas and current baselines)
   - Evidence-based intervention approaches appropriate for the child's age and needs
2. Include:
   - Recommended intervention strategies
   - Suggested approaches (e.g., naturalistic, structured, play-based)
   - Home-based practice ideas
   - Environmental modifications
   - Materials or tools that may help
3. Ensure guidelines are specific to the child — not generic ASD recommendations

**Outputs:**
- Draft intervention guidelines per domain/focus area
- Suggested approaches with rationale
- Home-based activity ideas
- Environmental modification suggestions

**Decision Gate:** Guidelines proceed to bias monitoring before further processing.

---

### Step 9: Bias Monitoring

**Agent:** Bias Monitoring Agent

**Trigger:** Guideline generation complete

**Process:**
1. Review generated guidelines for potential bias:
   - Demographic bias (recommendations differ based on race, ethnicity, gender)
   - Cultural bias (assumes Western cultural norms without considering family's context)
   - Language bias (recommendations assume English fluency)
   - Socioeconomic bias (recommendations assume resources the family may not have)
   - Geographic bias (recommendations assume urban service availability)
2. Compare recommendations against similar profiles for consistency
3. Flag any concerns

**Outputs:**
- Bias check status: `PASSED` | `FLAGGED` | `REVIEW_REQUIRED`
- If flagged: specific concern, affected sections, recommended remediation
- Comparison consistency score

**Decision Gate:**
- `PASSED` → proceed to goal generation
- `FLAGGED` → escalate to clinician review with documented concern

**Example Flag:**
```json
{
  "biasCheckStatus": "FLAGGED",
  "concern": "Home-based recommendations assume availability of specialized toys and materials that may not be accessible to all families.",
  "affectedSection": "Sensory Processing - Environmental Modifications",
  "recommendation": "Generate alternative low-cost or no-cost options alongside material-dependent suggestions."
}
```

---

### Step 10: Goal Generation

**Agent:** Goal Generation Agent

**Trigger:** Bias monitoring passed

**Process:**
1. Convert intervention guidelines into structured SMART goals
2. Generate short-term goals (1-3 months) and long-term goals (6-12 months)
3. Ensure every goal is:
   - **Specific** — clearly defines what the child will do
   - **Measurable** — includes observable criteria
   - **Achievable** — appropriate for the child's current level
   - **Relevant** — directly tied to the child's profile and priorities
   - **Time-bound** — includes a target timeframe
4. Link each goal to its corresponding focus area and domain

**Example SMART Goal:**
```
Domain: Communication
Focus Area: Expressive vocabulary expansion
Short-term Goal (3 months):
  "[Child] will use 2-word combinations (e.g., 'more juice', 'go outside') 
   to make requests in at least 3 out of 5 opportunities during structured 
   play activities, as measured by clinician observation and parent report."

Long-term Goal (12 months):
  "[Child] will use 3-4 word sentences to communicate wants, label objects, 
   and comment on activities in both home and therapy settings, demonstrating 
   this in at least 4 out of 5 opportunities across 3 consecutive sessions."
```

**NOT Acceptable:**
- "Improve communication in 6 months" (not specific, not measurable)
- "Get better at talking" (vague, unmeasurable)

**Outputs:**
- Structured SMART goals (short-term and long-term) per focus area
- Goal-to-domain-to-profile traceability

---

### Step 11: Milestone Planning

**Agent:** Milestone Planning Agent

**Trigger:** Goal generation complete

**Process:**
1. Create time-bound milestones as checkpoints between current baseline and goals
2. Consider:
   - Severity of delay (more severe = smaller milestone increments)
   - Child's demonstrated learning pace (from history if available)
   - Typical developmental progressions
3. Milestones should be observable and celebratable — marking real progress

**Example Milestones:**
```
Goal: 2-word combinations for requesting (3-month target)

Month 1 Milestone:
  "Child consistently uses at least 5 new single words for requesting 
   (beyond current baseline of ~20 words)"

Month 2 Milestone:
  "Child occasionally produces 2-word combinations with modeling support 
   (e.g., clinician says 'more ___' and child fills in)"

Month 3 Milestone:
  "Child independently uses 2-word combinations to request in at least 
   3/5 opportunities during structured activities"
```

**Outputs:**
- Milestone timeline per goal
- Expected progress markers
- Suggested review points

---

### Step 12: Caregiver Guidance Generation

**Agent:** Caregiver Guidance Agent

**Trigger:** Milestone planning complete

**Process:**
1. Convert the professional intervention plan into plain-language guidance for parents/caregivers
2. Use simple, jargon-free language
3. Provide practical, home-based activities families can do daily
4. Consider:
   - Family's cultural context and language
   - Available resources and time constraints
   - Sibling involvement opportunities
   - Daily routine integration (mealtime, bath time, play time)
5. Include encouragement and strength-based framing

**Example Caregiver Guidance:**
```
FOR BUILDING COMMUNICATION AT HOME:

During mealtimes:
- Before giving food, hold it up and wait 3-5 seconds for your child to 
  say the word or attempt it. If they reach, model the word "more" or 
  "juice" and wait again.
- Celebrate any attempt to communicate — even a sound or gesture counts!

During play:
- Play with bubbles, blocks, or balls. Pause the activity and wait for 
  your child to request "more" or "again" before continuing.
- Narrate what you're doing in short phrases: "push car", "big tower", 
  "pop bubble"

What you're already doing well:
- Your child loves music — use songs with pauses to encourage them to 
  fill in words (e.g., "Twinkle twinkle little ___")
```

**Outputs:**
- Caregiver-friendly guidance document
- Activity suggestions organized by daily routine
- Strength-based encouragement
- Simple progress tracking suggestions for parents

---

### Step 13: Final Clinician Review (MANDATORY)

**Trigger:** All workflow agents have completed their outputs

**Process:**
1. System presents the complete generated plan to the clinician reviewer:
   - Unified child profile
   - Domain priorities with rationale
   - Domain analysis
   - Intervention guidelines
   - SMART goals (short-term and long-term)
   - Milestone plan
   - Caregiver guidance
   - Confidence scores for each section
   - Bias check results
   - Audit trail summary
2. Clinician reviews each section
3. Clinician takes action:

| Action | Result |
|---|---|
| **Approve** | Plan is finalized and can be shared with caregivers |
| **Modify** | Clinician edits specific sections; modified version becomes final |
| **Reject** | Plan is discarded; clinician provides reason; may request re-generation with additional context |
| **Partial Approve** | Some sections approved, others sent back for revision with clinician notes |

4. Clinician review action is logged in audit trail
5. Only approved content proceeds to caregiver delivery

**This step is NON-NEGOTIABLE. No AI-generated content reaches caregivers without clinician sign-off.**

---

## 3. Workflow State Machine

Each case moves through the following states:

```
INITIATED
  → CONSENT_PENDING
  → CONSENT_GRANTED
    → INPUT_COLLECTION
    → DATA_VALIDATION
    → PROFILE_BUILDING
    → DOMAIN_PRIORITIZATION
    → CONFIDENCE_CHECK
      → ABSTAINED (terminal — requires manual intervention)
    → DOMAIN_ANALYSIS
    → GUIDELINE_GENERATION
    → BIAS_CHECK
      → BIAS_FLAGGED → CLINICIAN_REVIEW_REQUIRED
    → GOAL_GENERATION
    → MILESTONE_PLANNING
    → CAREGIVER_GUIDANCE
    → AWAITING_CLINICIAN_REVIEW
      → APPROVED
      → MODIFIED → APPROVED
      → REJECTED
      → PARTIAL_APPROVED → (loop back for revisions)
  → CONSENT_DENIED (terminal)
```

At any state, a case can be moved to:
- `ESCALATED_TO_REVIEWER` — manual intervention needed
- `ON_HOLD` — waiting for additional information
- `CLOSED` — case closed without completion (with reason)

---

## 4. Escalation Triggers Summary

| Trigger | Action |
|---|---|
| Consent not provided | Block processing, notify clinician |
| Data incomplete after 3 follow-up rounds | Abstain, escalate to clinician |
| Confidence below threshold | Flag output, require clinician review before proceeding |
| Bias detected in recommendations | Flag case, route to clinician with documented concern |
| Conflicting assessment data | Escalate for manual reconciliation |
| System cannot extract minimum fields | Escalate with extraction failure reason |
| Any critical agent failure | Log error, escalate to clinician, do not generate partial output |

---

## 5. Audit Trail Requirements

Every action in the system must generate an audit event:

```json
{
  "eventId": "uuid",
  "caseId": "AIG-2026-0001",
  "timestamp": "2026-05-25T14:30:00Z",
  "agentId": "profile-synthesis",
  "eventType": "AGENT_OUTPUT",
  "action": "Profile generated",
  "confidenceScore": 0.89,
  "inputHash": "sha256:...",
  "outputHash": "sha256:...",
  "escalation": false,
  "humanReviewRequired": false
}
```

Audit events are immutable. They cannot be modified or deleted. They support full traceability from input to final approved output.
