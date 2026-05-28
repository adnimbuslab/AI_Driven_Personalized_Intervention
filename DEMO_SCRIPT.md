# Demo Video Script — 2-Minute Walkthrough

**Application URLs (running now):**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- LocalStack: http://localhost:4566

**Recording tip:** Use QuickTime Player (File > New Screen Recording) or OBS Studio. Record at 1920x1080.

---

## Scene 1: Dashboard (0:00 – 0:15)

1. Open browser to **http://localhost:3000**
2. Show the **Case Dashboard** — empty state with stats cards (Total Cases, Pending Review, Approved, Rejected)
3. Point out the navigation: **Dashboard**, **Intake**, **Review**
4. Click **"+ New Case"** button (top right) → navigates to Intake page

---

## Scene 2: Clinical Intake — Create Case (0:15 – 0:35)

1. On the **Intake** page, click **"New Case"** button in the center
2. System creates case and displays: *"Case AIG-2026-XXXX created. Before we proceed, we need to verify consent..."*
3. Click the green **"Consent Granted"** button
4. System confirms consent and shows the **Screening Data Input** form

---

## Scene 3: Fill Screening Data (0:35 – 1:00)

Fill in the form fields (quickly, just the key ones):

| Field | Value |
|---|---|
| Age Years | 4 |
| Age Months | 6 |
| Gender | Male |
| Support Level | Level 2 |
| Screening Tool | ADOS-2 |
| Primary Domain | Communication |
| Secondary Domain | Social Interaction |
| Home Language | English |
| ADOS2 Social Affect | 12 |
| ADOS2 RRB | 4 |
| Strength Domains | Visual learning, Music |
| Gap Domains | Expressive language, Peer interaction |
| Family Priorities | Improve communication |
| Current Services | Speech therapy 2x/week |

Click **"Submit & Start Workflow"**

---

## Scene 4: Workflow Execution (1:00 – 1:20)

1. Watch the **13-step progress bar** at the top light up as the workflow runs
2. The system shows: *"Data received. Starting the intervention planning workflow..."*
3. Wait for completion — system shows: *"Intervention plan generated successfully! Plan ID: PLAN-AIG-2026-XXXX. The plan is now awaiting clinician review."*
4. The progress bar shows all 13 steps complete

**Narration:** "The multi-agent pipeline processes the case through 12 specialized agents — consent verification, data quality checks, profile synthesis, domain prioritization, confidence assessment, guideline generation, bias monitoring, SMART goal creation, milestone planning, and caregiver guidance — all orchestrated by LangGraph."

---

## Scene 5: Clinician Review Dashboard (1:20 – 1:50)

1. Click **"Review"** in the top navigation
2. The **Pending Reviews** queue on the left shows the case
3. Click on the case — the right panel loads the full intervention plan
4. Scroll through expandable sections:
   - **Domain Priorities** — shows prioritized developmental domains with confidence scores
   - **Intervention Guidelines** — evidence-based approaches (ABA, ESDM, etc.)
   - **SMART Goals** — with baseline/target progress bars
   - **Caregiver Guidance** — plain-language activities for parents
   - **Audit Trail** — every agent decision logged with timestamps
5. Optionally type a note in the review box
6. Click the green **"Approve"** button

---

## Scene 6: Wrap-up (1:50 – 2:00)

1. System shows **"Review Submitted"** confirmation
2. Navigate back to **Dashboard** — show the case now appears with "Approved" status badge
3. Quick final shot of the dashboard with updated stats

---

## Key Points to Emphasize in Voiceover

- **12 AI agents** work together in a governed pipeline
- **4 governance agents** enforce consent, data quality, confidence thresholds, and bias detection
- **Human-in-the-loop**: No AI output reaches caregivers without clinician approval
- **Immutable audit trail**: Every agent decision is logged with SHA-256 hashes
- **LLM-powered**: Uses Ollama (llama3.2) locally — swappable to Claude Opus via env vars
- **Evidence-based**: References ABA, ESDM, TEACCH, PRT, and other validated interventions
- **Culturally sensitive**: Considers family language, context, and available resources
