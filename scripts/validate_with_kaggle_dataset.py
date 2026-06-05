"""Validate the POC by running Kaggle dataset children through the live workflow.

Loads child_profiles.csv and screening_assessments.csv, sends each child through
the API, and collects pass/fail results for the POC evaluation document.
"""

import csv
import json
import math
import time
import sys
import os
import requests

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kaggle_dataset")
RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "kaggle_validation_results.json")

SAMPLE_SIZE = int(os.environ.get("SAMPLE_SIZE", "500"))


def load_csv(filename):
    path = os.path.join(DATASET_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def safe_float(val):
    if val is None or val == "" or val == "None":
        return None
    try:
        v = float(val)
        return None if math.isnan(v) else v
    except (ValueError, TypeError):
        return None


def safe_str(val):
    if val is None or val == "" or val == "None":
        return None
    return str(val).strip()


def build_structured_inputs(profile, assessment):
    return {
        "age_years": safe_float(profile.get("age_years")),
        "age_months": safe_float(profile.get("age_months")),
        "gender": safe_str(profile.get("gender")),
        "support_level": safe_str(profile.get("support_level")),
        "screening_tool": safe_str(profile.get("screening_tool") or assessment.get("primary_tool")),
        "primary_domain": safe_str(profile.get("primary_domain")),
        "secondary_domain": safe_str(profile.get("secondary_domain")),
        "ados2_social_affect": safe_float(profile.get("ados2_social_affect") or assessment.get("ados2_social_affect_score")),
        "ados2_rrb": safe_float(profile.get("ados2_rrb") or assessment.get("ados2_rrb_score")),
        "home_language": safe_str(profile.get("home_language")),
        "strength_domains": safe_str(profile.get("strength_domains")),
        "gap_domains": safe_str(profile.get("gap_domains")),
        "family_priorities": safe_str(profile.get("family_priorities")),
        "current_services": safe_str(profile.get("current_services")),
        "diagnosis": safe_str(profile.get("diagnosis")),
        "cognitive_verbal_percentile": safe_float(profile.get("cognitive_verbal_percentile") or assessment.get("cognitive_verbal_pct")),
        "cognitive_nonverbal_percentile": safe_float(profile.get("cognitive_nonverbal_percentile") or assessment.get("cognitive_nonverbal_pct")),
        "adaptive_composite_percentile": safe_float(profile.get("adaptive_composite_percentile") or assessment.get("adaptive_composite_pct")),
        "referral_source": safe_str(profile.get("referral_source")),
        "primary_setting": safe_str(profile.get("primary_setting")),
    }


def count_required_present(inputs):
    required = ["age_years", "age_months", "gender", "screening_tool",
                 "ados2_social_affect", "ados2_rrb", "primary_domain"]
    return sum(1 for f in required if inputs.get(f) is not None)


def count_desired_present(inputs):
    desired = ["support_level", "diagnosis", "secondary_domain", "home_language",
               "primary_setting", "referral_source", "cognitive_verbal_percentile",
               "cognitive_nonverbal_percentile", "adaptive_composite_percentile",
               "strength_domains", "gap_domains", "family_priorities", "current_services"]
    return sum(1 for f in desired if inputs.get(f) is not None)


def run_child(profile, assessment, idx, total):
    child_id = profile["child_id"]
    result = {
        "child_id": child_id,
        "age_years": safe_float(profile.get("age_years")),
        "gender": safe_str(profile.get("gender")),
        "support_level": safe_str(profile.get("support_level")),
        "primary_domain": safe_str(profile.get("primary_domain")),
        "home_language": safe_str(profile.get("home_language")),
    }

    structured = build_structured_inputs(profile, assessment)
    result["required_fields_present"] = count_required_present(structured)
    result["desired_fields_present"] = count_desired_present(structured)

    try:
        resp = requests.post(f"{API_BASE}/api/cases",
                             json={"reporter_id": "KAGGLE-VALIDATOR", "consent_status": "PENDING"},
                             timeout=10)
        case_data = resp.json()
        case_id = case_data["case_id"]
        result["case_id"] = case_id
    except Exception as e:
        result["case_creation"] = "FAIL"
        result["error"] = str(e)
        return result

    result["case_creation"] = "PASS"

    try:
        resp = requests.post(f"{API_BASE}/api/cases/{case_id}/workflow/start",
                             json={
                                 "child_id": child_id,
                                 "reporter_id": "KAGGLE-VALIDATOR",
                                 "consent_status": "GRANTED",
                                 "structured_inputs": structured,
                             },
                             timeout=60)
        wf = resp.json()
        result["workflow_status"] = wf.get("workflow_status")
        result["plan_id"] = wf.get("plan_id")
        result["has_guidelines"] = wf.get("has_guidelines", False)
        result["has_goals"] = wf.get("has_goals", False)
        result["has_milestones"] = wf.get("has_milestones", False)
        result["has_caregiver"] = wf.get("has_caregiver_guidance", False)
        result["workflow_error"] = wf.get("error")
    except Exception as e:
        result["workflow_status"] = "ERROR"
        result["error"] = str(e)
        return result

    if result["workflow_status"] == "AWAITING_CLINICIAN_REVIEW":
        result["workflow_pass"] = True

        try:
            resp = requests.get(f"{API_BASE}/api/cases/{case_id}/plan", timeout=10)
            plan = resp.json()
            result["plan_has_guidelines"] = len(plan.get("guidelines", [])) > 0
            result["plan_has_goals"] = len(plan.get("smart_goals", [])) > 0
            result["plan_has_milestones"] = len(plan.get("milestones", [])) > 0
            result["plan_has_caregiver"] = plan.get("caregiver_guidance") is not None
            result["plan_has_bias_result"] = plan.get("bias_check_result") is not None
            result["plan_has_confidence_result"] = plan.get("confidence_check_result") is not None
            result["plan_status"] = plan.get("status")
            result["guideline_count"] = len(plan.get("guidelines", []))
            result["goal_count"] = len(plan.get("smart_goals", []))
            result["milestone_count"] = len(plan.get("milestones", []))
        except Exception as e:
            result["plan_retrieval_error"] = str(e)

        try:
            resp = requests.get(f"{API_BASE}/api/cases/{case_id}/audit", timeout=10)
            audit = resp.json()
            result["audit_event_count"] = len(audit.get("events", []))
            agents_logged = set(e.get("agent_id") for e in audit.get("events", []))
            result["agents_in_audit"] = sorted(agents_logged)
        except Exception:
            pass

        try:
            resp = requests.post(f"{API_BASE}/api/cases/{case_id}/review",
                                 json={
                                     "action": "approved",
                                     "reviewer_id": "KAGGLE-AUTO-REVIEWER",
                                     "plan_id": result.get("plan_id", f"PLAN-{case_id}"),
                                     "notes": f"Auto-approved during Kaggle dataset validation for {child_id}",
                                 },
                                 timeout=10)
            review = resp.json()
            result["review_status"] = review.get("plan_status")
            result["review_pass"] = review.get("plan_status") == "approved"
        except Exception as e:
            result["review_error"] = str(e)

    elif result["workflow_status"] in ("ABSTAINED", "CONSENT_DENIED"):
        result["workflow_pass"] = False
    else:
        result["workflow_pass"] = False

    if (idx + 1) % 25 == 0 or idx == 0:
        status_icon = "OK" if result.get("workflow_pass") else "SKIP"
        print(f"  [{idx+1:3d}/{total}] {child_id} — {result['workflow_status']} [{status_icon}]")

    return result


def compute_statistics(results):
    total = len(results)
    passed = sum(1 for r in results if r.get("workflow_pass"))
    abstained = sum(1 for r in results if r.get("workflow_status") == "ABSTAINED")
    errored = sum(1 for r in results if r.get("workflow_status") == "ERROR")

    all_required = sum(1 for r in results if r.get("required_fields_present") == 7)
    missing_required = sum(1 for r in results if (r.get("required_fields_present") or 0) < 7)

    with_plans = [r for r in results if r.get("workflow_pass")]
    avg_guidelines = sum(r.get("guideline_count", 0) for r in with_plans) / max(len(with_plans), 1)
    avg_goals = sum(r.get("goal_count", 0) for r in with_plans) / max(len(with_plans), 1)
    avg_milestones = sum(r.get("milestone_count", 0) for r in with_plans) / max(len(with_plans), 1)
    avg_audit = sum(r.get("audit_event_count", 0) for r in with_plans) / max(len(with_plans), 1)

    reviewed = sum(1 for r in with_plans if r.get("review_pass"))

    support_levels = {}
    for r in results:
        sl = r.get("support_level", "Unknown") or "Unknown"
        if sl not in support_levels:
            support_levels[sl] = {"total": 0, "passed": 0}
        support_levels[sl]["total"] += 1
        if r.get("workflow_pass"):
            support_levels[sl]["passed"] += 1

    domains = {}
    for r in results:
        d = r.get("primary_domain", "Unknown") or "Unknown"
        if d not in domains:
            domains[d] = {"total": 0, "passed": 0}
        domains[d]["total"] += 1
        if r.get("workflow_pass"):
            domains[d]["passed"] += 1

    languages = {}
    for r in results:
        lang = r.get("home_language", "Unknown") or "Unknown"
        if lang not in languages:
            languages[lang] = {"total": 0, "passed": 0}
        languages[lang]["total"] += 1
        if r.get("workflow_pass"):
            languages[lang]["passed"] += 1

    age_groups = {"2-3": {"total": 0, "passed": 0}, "4-5": {"total": 0, "passed": 0},
                  "6-7": {"total": 0, "passed": 0}, "8+": {"total": 0, "passed": 0}}
    for r in results:
        age = r.get("age_years")
        if age is None:
            continue
        if age <= 3:
            grp = "2-3"
        elif age <= 5:
            grp = "4-5"
        elif age <= 7:
            grp = "6-7"
        else:
            grp = "8+"
        age_groups[grp]["total"] += 1
        if r.get("workflow_pass"):
            age_groups[grp]["passed"] += 1

    genders = {}
    for r in results:
        g = r.get("gender", "Unknown") or "Unknown"
        if g not in genders:
            genders[g] = {"total": 0, "passed": 0}
        genders[g]["total"] += 1
        if r.get("workflow_pass"):
            genders[g]["passed"] += 1

    return {
        "total_children": total,
        "workflow_passed": passed,
        "workflow_pass_rate": round(passed / max(total, 1) * 100, 1),
        "workflow_abstained": abstained,
        "workflow_errored": errored,
        "all_required_fields_present": all_required,
        "missing_required_fields": missing_required,
        "clinician_reviews_completed": reviewed,
        "avg_guidelines_per_plan": round(avg_guidelines, 1),
        "avg_goals_per_plan": round(avg_goals, 1),
        "avg_milestones_per_plan": round(avg_milestones, 1),
        "avg_audit_events_per_plan": round(avg_audit, 1),
        "by_support_level": support_levels,
        "by_primary_domain": domains,
        "by_home_language": languages,
        "by_age_group": age_groups,
        "by_gender": genders,
    }


def main():
    print("=" * 60)
    print("Kaggle Dataset Validation — POC End-to-End Test")
    print("=" * 60)

    print(f"\nLoading dataset from {DATASET_DIR}...")
    profiles = load_csv("child_profiles.csv")
    assessments = load_csv("screening_assessments.csv")

    assess_map = {a["child_id"]: a for a in assessments}

    if SAMPLE_SIZE < len(profiles):
        profiles = profiles[:SAMPLE_SIZE]
    total = len(profiles)
    print(f"Loaded {total} child profiles, {len(assessments)} assessments")

    print(f"\nRunning {total} children through the workflow...\n")

    results = []
    start_time = time.time()

    for idx, profile in enumerate(profiles):
        child_id = profile["child_id"]
        assessment = assess_map.get(child_id, {})
        result = run_child(profile, assessment, idx, total)
        results.append(result)

    elapsed = time.time() - start_time

    stats = compute_statistics(results)
    stats["total_elapsed_seconds"] = round(elapsed, 1)
    stats["avg_per_child_ms"] = round(elapsed / max(total, 1) * 1000, 0)

    output = {"statistics": stats, "results": results}

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total children processed:    {stats['total_children']}")
    print(f"Workflow PASSED:             {stats['workflow_passed']} ({stats['workflow_pass_rate']}%)")
    print(f"Workflow ABSTAINED:          {stats['workflow_abstained']}")
    print(f"Workflow ERRORED:            {stats['workflow_errored']}")
    print(f"All required fields present: {stats['all_required_fields_present']}")
    print(f"Missing required fields:     {stats['missing_required_fields']}")
    print(f"Clinician reviews completed: {stats['clinician_reviews_completed']}")
    print(f"Avg guidelines per plan:     {stats['avg_guidelines_per_plan']}")
    print(f"Avg SMART goals per plan:    {stats['avg_goals_per_plan']}")
    print(f"Avg milestones per plan:     {stats['avg_milestones_per_plan']}")
    print(f"Avg audit events per plan:   {stats['avg_audit_events_per_plan']}")
    print(f"Total elapsed time:          {stats['total_elapsed_seconds']}s")
    print(f"Avg per child:               {stats['avg_per_child_ms']}ms")

    print(f"\nBy Support Level:")
    for sl, data in sorted(stats["by_support_level"].items()):
        rate = round(data["passed"] / max(data["total"], 1) * 100, 1)
        print(f"  {sl:12s}: {data['passed']:3d}/{data['total']:3d} passed ({rate}%)")

    print(f"\nBy Primary Domain:")
    for d, data in sorted(stats["by_primary_domain"].items()):
        rate = round(data["passed"] / max(data["total"], 1) * 100, 1)
        print(f"  {d:25s}: {data['passed']:3d}/{data['total']:3d} passed ({rate}%)")

    print(f"\nBy Age Group:")
    for ag, data in stats["by_age_group"].items():
        rate = round(data["passed"] / max(data["total"], 1) * 100, 1)
        print(f"  {ag:6s}: {data['passed']:3d}/{data['total']:3d} passed ({rate}%)")

    print(f"\nResults saved to: {RESULTS_PATH}")
    return stats


if __name__ == "__main__":
    main()
