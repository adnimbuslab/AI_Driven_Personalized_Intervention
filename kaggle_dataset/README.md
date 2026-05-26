# Synthetic Autism Intervention Planning Dataset

## Overview

A comprehensive synthetic dataset designed for developing and evaluating AI-driven personalized intervention planning systems for children with Autism Spectrum Disorder (ASD). This dataset contains **500 synthetic child profiles** with linked screening assessments, intervention guidelines, SMART developmental goals, therapy session notes, milestones, caregiver guidance, progress summaries, and governance audit logs — totaling over **22,000 records** across 9 interconnected tables.

This dataset was created as part of the research paper:
> **"AI-Driven Personalized Intervention Guideline Generator for Children with Autism Based on Screening Outcomes"**
> Ambar Nath Saha, Debashis Patra — 2026

## Important Disclaimer

**This is entirely synthetic data.** It does not contain any real patient information. All child profiles, assessment scores, therapy notes, and clinical details are programmatically generated. This dataset is intended for research, model development, and educational purposes only. It should NOT be used for clinical decision-making.

## Dataset Structure

| File | Records | Description |
|------|---------|-------------|
| `child_profiles.csv` | 500 | Demographic and clinical profiles of synthetic children with ASD |
| `screening_assessments.csv` | 500 | Standardized assessment scores (ADOS-2, cognitive, adaptive) |
| `intervention_guidelines.csv` | 1,311 | Evidence-based intervention recommendations per domain |
| `smart_goals.csv` | 1,347 | SMART developmental goals (Specific, Measurable, Achievable, Relevant, Time-bound) |
| `therapy_notes.csv` | 9,398 | Individual therapy session records with outcomes |
| `milestones.csv` | 1,347 | Short-term and long-term developmental milestones |
| `caregiver_guidance.csv` | 500 | Plain-language home activity recommendations for parents |
| `progress_summaries.csv` | 1,347 | Per-goal progress analysis with trend detection |
| `audit_log.csv` | 6,000 | Governance and agent execution audit trail |

## Table Relationships

```
child_profiles (child_id)
├── screening_assessments (child_id)
├── intervention_guidelines (child_id) → guideline_id
│   └── smart_goals (child_id, associated_guideline) → goal_id
│       ├── therapy_notes (child_id, goal_id)
│       ├── milestones (child_id, goal_id)
│       └── progress_summaries (child_id, goal_id)
├── caregiver_guidance (child_id)
└── audit_log (child_id)
```

## Column Descriptions

### child_profiles.csv
| Column | Description |
|--------|-------------|
| child_id | Unique identifier (CH-001 to CH-500) |
| age_years / age_months | Child's age |
| gender | Male, Female, or Non-binary (reflects ASD 4:1 male-to-female ratio) |
| support_level | DSM-5 ASD support level (Level 1, 2, or 3) |
| diagnosis | Specific ASD diagnosis variant |
| primary_domain / secondary_domain | Primary and secondary areas of developmental need |
| home_language | Family's primary language (20 languages represented) |
| bilingual | Whether the family is bilingual (Yes/No) |
| primary_setting | Primary intervention setting (clinic, home, school, community, telehealth) |
| referral_source | Who referred the child for assessment |
| screening_tool | Assessment tool(s) used for screening |
| ados2_module / ados2_social_affect / ados2_rrb / ados2_comparison_score | ADOS-2 assessment scores |
| cognitive_verbal_percentile / cognitive_nonverbal_percentile / cognitive_gca_percentile | Cognitive assessment percentiles |
| adaptive_composite_percentile | Adaptive behavior composite percentile |
| strength_domains / gap_domains | Identified developmental strengths and gaps |
| family_priorities | Family-identified intervention priorities |
| current_services | Services the child is currently receiving |
| country / region | Geographic location |

### screening_assessments.csv
| Column | Description |
|--------|-------------|
| assessment_id | Unique assessment identifier |
| assessment_date | Date of assessment |
| primary_tool | Primary screening/assessment tool used |
| ados2_* | ADOS-2 module, scores, and comparison level |
| cognitive_* | Cognitive assessment tool and percentile scores |
| adaptive_* | Adaptive behavior tool and domain percentiles |
| behavioral_tool | Behavioral assessment tool (if used) |
| diagnosis_given | Diagnosis resulting from assessment |
| assessor_role | Role of the clinician who conducted the assessment |

### smart_goals.csv
| Column | Description |
|--------|-------------|
| goal_id | Unique goal identifier |
| domain / sub_domain | Developmental domain and sub-domain |
| goal_text | Full SMART goal statement |
| baseline_percent | Current performance level (0-100) |
| target_percent | Target performance level (0-100) |
| measurement_frequency | How often progress is measured |
| measurement_method | Method used to measure progress |
| weeks_duration | Goal timeline in weeks |
| status | Current goal status (active, met, modified, pending_review) |

### therapy_notes.csv
| Column | Description |
|--------|-------------|
| session_id | Unique session identifier |
| session_date | Date of therapy session |
| session_type | Type of session (Direct Therapy, Parent Coaching, ABA, etc.) |
| setting | Where the session took place |
| mood | Child's observed mood at session start |
| engagement_1_5 | Engagement rating (1=minimal, 5=strong) |
| interventions_used | Evidence-based interventions applied (semicolon-separated) |
| behavior_observed | Primary behavior observed during session |
| prompts_required | Number of prompts needed |
| task_success_percent | Percentage of successful task completions (0-100) |
| assistance_level | Level of support needed |
| duration_minutes | Session length |
| session_note | Therapist's session narrative |
| next_plan | Plan for next session |

### progress_summaries.csv
| Column | Description |
|--------|-------------|
| total_sessions | Number of sessions in the review period |
| avg_success_first_2 / avg_success_last_2 | Average success in first vs. last 2 sessions |
| change_points | Numerical change in performance |
| trend_status | Improving, Slow Progress, Plateau, or Regression |
| avg_engagement / avg_prompts | Average engagement and prompt levels |
| recommendation | AI-generated recommendation based on trend |

## Data Distributions

- **Support Levels:** ~35% Level 1, ~40% Level 2, ~25% Level 3
- **Age Range:** 2-8 years (weighted toward 3-5 years, peak intervention age)
- **Gender:** ~72% Male, ~24% Female, ~4% Non-binary (reflects ASD prevalence ratios)
- **Languages:** 20 languages represented (30% English, 15% Spanish, plus 18 others)
- **Settings:** Clinic (30%), Home (25%), School (25%), Community (10%), Telehealth (10%)
- **Developmental Domains:** All 7 domains represented as primary/secondary across children

## Potential Use Cases

1. **ML Model Development:** Train models to predict intervention priorities, optimal approaches, or expected outcomes based on child profiles
2. **NLP Tasks:** Extract information from therapy notes, generate summaries, classify session outcomes
3. **Recommendation Systems:** Build systems that recommend evidence-based interventions based on child profiles
4. **Goal Generation:** Develop AI systems that generate SMART goals from assessment data
5. **Progress Prediction:** Predict developmental trajectories from early session data
6. **Fairness/Bias Analysis:** Analyze whether intervention recommendations vary systematically across demographic groups
7. **Clinical Decision Support:** Prototype AI tools that assist clinicians in intervention planning
8. **Data Visualization:** Create dashboards for tracking multi-domain developmental progress

## Clinical Document Types That Informed This Dataset

This synthetic dataset was designed by studying the structure and content of real-world clinical documents used in autism assessment and intervention:

1. Autism Diagnostic Assessment Reports (ADOS-2, DAS-II, ABAS-3)
2. Speech-Language Pathology Assessment Reports
3. Clinical Feeding and Swallowing Evaluations
4. Developmental Pediatric Clinic Follow-up Reports
5. School/Daycare Reports and Behavioral Rating Scales
6. Early Childhood Development Intake Forms
7. Social Communication Checklists (Hanen More Than Words)
8. Self-Care Technique Guides (Backward Chaining)
9. Caregiver Training Program Schedules
10. Off-Site Visit Logs and Therapy Session Notes
11. Referral Forms and Consent Documents
12. Prescription/Medical Letters

## Evidence-Based Approaches Represented

The dataset references the following evidence-based intervention approaches:
- Applied Behavior Analysis (ABA)
- Naturalistic Developmental Behavioral Interventions (NDBI)
- Early Start Denver Model (ESDM)
- TEACCH Structured Teaching
- Augmentative and Alternative Communication (AAC/PECS)
- Sensory Integration Therapy
- DIR/Floor Time
- PEERS Social Skills Program
- Hanen Programs (More Than Words, All Together Now!)
- Pivotal Response Training (PRT)

## Citation

If you use this dataset, please cite:

```
Saha, A. N., & Patra, D. (2026). AI-Driven Personalized Intervention Guideline Generator
for Children with Autism Based on Screening Outcomes. [Manuscript in preparation].
```

Also see our related published work:
```
Patra, D., Saha, A. N., & Mukherjee, S. S. (2026). Clinician-Augmented Agentic AI for
Autism Screening Support: A Safety-Constrained Multimodal Architecture. Cureus.
doi:10.7759/cureus
```

## License

This dataset is released under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license. You are free to share and adapt this dataset for any purpose, provided you give appropriate credit.

## Contact

- Debashis Patra — debashis31@gmail.com
- Ambar Nath Saha
