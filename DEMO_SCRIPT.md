# Demo Video Script - 2-Minute Walkthrough

**Application URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- LocalStack: http://localhost:4566

**Recording tip:** Use QuickTime Player or OBS Studio. Record at 1920x1080.

## Scene 1: Dashboard (0:00-0:15)

1. Open browser to **http://localhost:3000**.
2. Show the **Autism Intervention Guideline Generator** header with **AIG** branding.
3. Show the **Intervention Planning Dashboard** cards: Total Children, Awaiting Clinician Review, Plans Approved, Delivered to Families.
4. Point out navigation: **Dashboard**, **New Child**, **Clinician Review**.
5. Click **New Child Assessment**.

## Scene 2: New Child Assessment (0:15-0:35)

1. On **Child Assessment & Intervention Planning**, click **Begin New Assessment**.
2. System creates a case and asks for informed consent.
3. Click **Consent Granted**.
4. System shows the grouped **Screening & Assessment Data** form.

## Scene 3: Fill Assessment Data (0:35-1:00)

Fill in these fields quickly:

| Field | Value |
|---|---|
| Child's Age (years) | 4 |
| Age (months) | 6 |
| Gender | Male |
| ASD Support Level (DSM-5) | Level 2 |
| Screening Tool Used | ADOS-2 |
| Primary Domain of Concern | Communication |
| Secondary Domain | Social Interaction |
| ADOS-2 Social Affect Score | 12 |
| ADOS-2 RRB Score | 4 |
| Home Language | English |
| Child's Strengths | Visual learning, music |
| Areas Needing Support | Expressive language, peer interaction |
| Family's Priorities | Improve communication |
| Current Therapies/Services | Speech therapy 2x/week |

Click **Submit & Generate Intervention Plan**.

## Scene 4: Workflow Execution (1:00-1:20)

1. Show the workflow progress bar: Consent, Data Collection, Quality Check, Child Profile, Domain Priorities, Bias Review, SMART Goals, Milestones, Parent Guide, Clinician Review.
2. Show the message explaining that 12 AI agents are validating data, building a strength-based profile, prioritizing domains, generating guidelines, creating goals and milestones, and preparing parent guidance.
3. Wait for the success message that the draft intervention plan is awaiting clinician review.

**Voiceover:** "The multi-agent pipeline processes the case through 12 specialized agents: consent verification, data quality checks, profile synthesis, domain prioritization, confidence assessment, guideline generation, bias monitoring, SMART goal creation, milestone planning, and caregiver guidance. The result is only a draft until a clinician approves it."

## Scene 5: Clinician Review Dashboard (1:20-1:50)

1. Click **Clinician Review** in the top navigation.
2. The **Plans Awaiting Review** queue on the left shows the case.
3. Click the case. The right panel loads the intervention plan.
4. Scroll through expandable sections:
   - **Developmental Domain Priorities**: prioritized domains with confidence scores
   - **Intervention Guidelines**: evidence-based approaches
   - **SMART Developmental Goals**: baseline and target progress bars
   - **Parent & Caregiver Guidance**: plain-language activities and strengths-based encouragement
   - **Governance & Audit Trail**: agent decisions with timestamps and confidence
5. Optionally type a review note.
6. Read the message: **No plan reaches the family without your approval.**
7. Click **Approve Plan**.

## Scene 6: Wrap-Up (1:50-2:00)

1. System shows **Review Submitted Successfully**.
2. Navigate back to **Dashboard** and refresh.
3. Show the case with **Approved** status and updated stats.

## Exact 2-Minute Voiceover

**0:00-0:15**  
"This is the Autism Intervention Guideline Generator. The dashboard tracks children across the intervention planning pipeline: total children, plans awaiting clinician review, approved plans, and plans ready for family delivery."

**0:15-0:35**  
"I start a new child assessment. Before any child data is processed, the system requires confirmation that informed consent has been obtained from the parent or legal guardian."

**0:35-1:00**  
"The intake form captures structured clinical context: age, DSM-5 support level, screening tool, ADOS-2 scores, developmental domains of concern, strengths, family priorities, language, and current services."

**1:00-1:20**  
"Submitting the form starts the governed 12-agent workflow. The agents validate data quality, synthesize a strength-based child profile, prioritize developmental domains, generate intervention guidelines, check confidence and bias, create SMART goals and milestones, and prepare parent-friendly guidance."

**1:20-1:50**  
"The output is not released. It enters the clinician review dashboard. The reviewer checks domain priorities, intervention guidelines, SMART developmental goals, caregiver activities, bias alerts, and the audit trail. Every agent step is logged with confidence metadata."

**1:50-2:00**  
"The clinician is the final authority. They can approve, modify and approve, or reject the plan. No plan reaches a family without clinician approval."

## Key Points to Emphasize

- **12 AI agents** work together in a governed pipeline.
- **4 governance agents** enforce consent, data quality, confidence thresholds, and bias detection.
- **Human-in-the-loop** review is mandatory before family delivery.
- **Audit trail** records agent decisions, confidence scores, and hashes.
- **LLM-powered** generation uses the configured provider, with local mock fallback support.
- **Evidence-informed** output includes intervention approaches, SMART goals, milestones, and caregiver activities.
- **Family context** is considered through language, strengths, priorities, and current services.
