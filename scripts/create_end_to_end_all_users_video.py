"""Create an end-to-end MP4 demo showing every user role in the workflow."""

from pathlib import Path
import shutil
import subprocess
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "demo_video"
VIDEO_DIR = OUT_DIR / "end_to_end_raw"
MP4_PATH = OUT_DIR / "autism_intervention_end_to_end_all_users.mp4"
FRONTEND_URL = "http://localhost:3000"


def wait(seconds: float) -> None:
    time.sleep(seconds)


def role_card(page, title: str, subtitle: str, bullets: list[str], seconds: float = 4) -> None:
    bullet_html = "".join(f"<li>{item}</li>" for item in bullets)
    page.set_content(
        f"""
        <!doctype html>
        <html>
        <head>
          <style>
            * {{ box-sizing: border-box; }}
            body {{
              margin: 0;
              width: 100vw;
              height: 100vh;
              font-family: Arial, Helvetica, sans-serif;
              background: #f8fafc;
              color: #0f172a;
              display: flex;
              align-items: center;
              justify-content: center;
            }}
            .wrap {{
              width: 1180px;
              border-left: 10px solid #0f766e;
              background: white;
              padding: 58px 70px;
              box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
            }}
            .eyebrow {{
              color: #0f766e;
              font-size: 22px;
              font-weight: 700;
              text-transform: uppercase;
              letter-spacing: 1px;
              margin-bottom: 20px;
            }}
            h1 {{
              font-size: 58px;
              line-height: 1.05;
              margin: 0 0 18px;
            }}
            p {{
              font-size: 28px;
              color: #475569;
              margin: 0 0 28px;
            }}
            ul {{
              margin: 0;
              padding-left: 32px;
              font-size: 25px;
              line-height: 1.55;
              color: #1e293b;
            }}
          </style>
        </head>
        <body>
          <section class="wrap">
            <div class="eyebrow">Autism Intervention Guideline Generator</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <ul>{bullet_html}</ul>
          </section>
        </body>
        </html>
        """,
        wait_until="load",
    )
    wait(seconds)


def add_overlay(page, role: str, note: str) -> None:
    page.evaluate(
        """({role, note}) => {
            const old = document.getElementById('demo-role-overlay');
            if (old) old.remove();
            const el = document.createElement('div');
            el.id = 'demo-role-overlay';
            el.style.position = 'fixed';
            el.style.left = '24px';
            el.style.bottom = '24px';
            el.style.zIndex = '999999';
            el.style.background = '#0f766e';
            el.style.color = 'white';
            el.style.borderRadius = '10px';
            el.style.boxShadow = '0 12px 28px rgba(15, 23, 42, 0.25)';
            el.style.padding = '14px 18px';
            el.style.fontFamily = 'Arial, Helvetica, sans-serif';
            el.style.maxWidth = '680px';
            el.innerHTML = `<div style="font-size:18px;font-weight:800;">${role}</div><div style="font-size:14px;margin-top:3px;">${note}</div>`;
            document.body.appendChild(el);
        }""",
        {"role": role, "note": note},
    )


def click_text(page, text: str, timeout: int = 4000) -> bool:
    try:
        page.get_by_text(text, exact=False).first.click(timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False


def fill_placeholder(page, placeholder: str, value: str, index: int = 0) -> None:
    page.locator(f'input[placeholder="{placeholder}"]').nth(index).fill(value)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    if VIDEO_DIR.exists():
        shutil.rmtree(VIDEO_DIR)
    VIDEO_DIR.mkdir(parents=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1440, "height": 900},
        )
        page = context.new_page()
        page.set_default_timeout(15000)

        role_card(
            page,
            "End-to-End Demo: All Users",
            "A governed autism intervention planning flow from intake to family delivery.",
            [
                "Intake clinician enters child and family context",
                "AI workflow generates a draft plan with governance checks",
                "Reviewing clinician approves, modifies, or rejects",
                "Caregiver receives only clinician-approved guidance",
                "Administrator has auditability and configurable governance controls",
            ],
            5,
        )

        role_card(
            page,
            "User 1: Intake Clinician",
            "Starts the case and confirms consent before any child data is processed.",
            [
                "Creates a new child assessment",
                "Confirms informed consent",
                "Submits assessment scores, strengths, support needs, and family priorities",
            ],
            4,
        )

        page.goto(FRONTEND_URL, wait_until="networkidle")
        add_overlay(page, "Intake Clinician", "Reviews the dashboard and starts a new child assessment.")
        wait(3)
        click_text(page, "New Child Assessment")
        wait(2)
        add_overlay(page, "Intake Clinician", "Creates a case and confirms informed consent.")
        click_text(page, "Begin New Assessment")
        wait(2)
        click_text(page, "Consent Granted")
        wait(2)
        add_overlay(page, "Intake Clinician", "Enters structured child assessment and family context.")
        fill_placeholder(page, "e.g., 4", "4")
        fill_placeholder(page, "e.g., 6", "6")
        fill_placeholder(page, "e.g., Male", "Male")
        fill_placeholder(page, "Level 1, 2, or 3", "Level 2")
        fill_placeholder(page, "e.g., ADOS-2, M-CHAT-R", "ADOS-2")
        fill_placeholder(page, "e.g., Communication", "Communication")
        fill_placeholder(page, "e.g., Social Interaction", "Social Interaction")
        fill_placeholder(page, "e.g., 12", "12")
        fill_placeholder(page, "e.g., 4", "4", index=1)
        fill_placeholder(page, "e.g., English, Spanish", "English")
        fill_placeholder(page, "e.g., Visual learning, Music", "Visual learning, music")
        fill_placeholder(page, "e.g., Expressive language", "Expressive language, peer interaction")
        fill_placeholder(page, "What matters most to the family?", "Improve communication")
        fill_placeholder(page, "e.g., Speech therapy 2x/week", "Speech therapy 2x/week")
        wait(3)

        role_card(
            page,
            "User 2: AI Workflow / System",
            "The system runs the governed multi-agent pipeline and creates a draft only.",
            [
                "12 agents validate, synthesize, prioritize, generate, and check outputs",
                "Governance gates enforce consent, data quality, confidence, and bias checks",
                "Every agent decision is written to the audit trail",
            ],
            4,
        )

        page.goto(FRONTEND_URL + "/intake", wait_until="networkidle")
        add_overlay(page, "System / AI Workflow", "The submitted case runs through the 12-agent pipeline.")
        click_text(page, "Begin New Assessment", timeout=2000)
        wait(1)
        click_text(page, "Consent Granted", timeout=2000)
        try:
            fill_placeholder(page, "e.g., 4", "4")
            fill_placeholder(page, "e.g., 6", "6")
            fill_placeholder(page, "e.g., Male", "Male")
            fill_placeholder(page, "Level 1, 2, or 3", "Level 2")
            fill_placeholder(page, "e.g., ADOS-2, M-CHAT-R", "ADOS-2")
            fill_placeholder(page, "e.g., Communication", "Communication")
            fill_placeholder(page, "e.g., Social Interaction", "Social Interaction")
            fill_placeholder(page, "e.g., 12", "12")
            fill_placeholder(page, "e.g., 4", "4", index=1)
            fill_placeholder(page, "e.g., English, Spanish", "English")
            fill_placeholder(page, "e.g., Visual learning, Music", "Visual learning, music")
            fill_placeholder(page, "e.g., Expressive language", "Expressive language, peer interaction")
            fill_placeholder(page, "What matters most to the family?", "Improve communication")
            fill_placeholder(page, "e.g., Speech therapy 2x/week", "Speech therapy 2x/week")
        except PlaywrightTimeoutError:
            pass
        click_text(page, "Submit & Generate Intervention Plan", timeout=5000)
        try:
            page.get_by_text("awaiting clinician review", exact=False).wait_for(timeout=90000)
        except PlaywrightTimeoutError:
            pass
        wait(5)

        role_card(
            page,
            "User 3: Reviewing Clinician",
            "The reviewer is the final clinical authority before family delivery.",
            [
                "Reviews domain priorities, guidelines, SMART goals, and caregiver guidance",
                "Checks bias alerts, confidence, and audit trail",
                "Approves, modifies and approves, or rejects the plan",
            ],
            4,
        )

        page.goto(FRONTEND_URL + "/review", wait_until="networkidle")
        add_overlay(page, "Reviewing Clinician", "Selects a draft plan from the review queue.")
        wait(3)
        try:
            page.locator('button:has-text("AIG-")').first.click(timeout=15000)
        except PlaywrightTimeoutError:
            pass
        wait(3)
        add_overlay(page, "Reviewing Clinician", "Reviews clinical content, confidence, bias alerts, and audit history.")
        for label in [
            "Developmental Domain Priorities",
            "Intervention Guidelines",
            "SMART Developmental Goals",
            "Parent & Caregiver Guidance",
            "Governance & Audit Trail",
        ]:
            click_text(page, label, timeout=2000)
            wait(1.5)
        try:
            page.locator("textarea").first.fill(
                "Reviewed plan, caregiver guidance, confidence, and audit trail. Approved for family delivery."
            )
            wait(2)
            click_text(page, "Approve Plan", timeout=5000)
        except PlaywrightTimeoutError:
            pass
        wait(4)

        role_card(
            page,
            "User 4: Parent / Caregiver",
            "The family receives only clinician-approved guidance.",
            [
                "Plain-language activities are tied to daily routines",
                "Guidance highlights child strengths and family priorities",
                "No AI-generated plan reaches the family without approval",
            ],
            5,
        )

        page.goto(FRONTEND_URL + "/review", wait_until="networkidle")
        add_overlay(page, "Caregiver / Parent", "Receives the approved parent-friendly guidance, not raw AI output.")
        wait(3)
        try:
            page.locator('button:has-text("AIG-")').first.click(timeout=8000)
            wait(2)
            click_text(page, "Parent & Caregiver Guidance", timeout=3000)
        except PlaywrightTimeoutError:
            pass
        wait(5)

        role_card(
            page,
            "User 5: System Administrator / Governance",
            "Admin responsibility is configuration, auditability, and operational oversight.",
            [
                "Confidence thresholds and model provider are configurable",
                "Audit trail records agent steps, confidence scores, and clinician decisions",
                "Approved status controls downstream delivery",
            ],
            5,
        )

        page.goto(FRONTEND_URL + "/", wait_until="networkidle")
        add_overlay(page, "System Administrator", "Monitors status, approved plans, and review backlog from the dashboard.")
        wait(5)

        role_card(
            page,
            "End-to-End Result",
            "The system supports clinicians, but the clinician remains accountable.",
            [
                "Drafts are generated by AI agents",
                "Governance gates catch missing consent, low confidence, and bias concerns",
                "The reviewing clinician controls final release to the family",
            ],
            5,
        )

        context.close()
        browser.close()

    webm_files = sorted(VIDEO_DIR.glob("*.webm"), key=lambda path: path.stat().st_mtime)
    if not webm_files:
        raise RuntimeError("Playwright did not create a recording.")

    source = webm_files[-1]
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(MP4_PATH),
        ],
        check=True,
    )
    print(MP4_PATH)


if __name__ == "__main__":
    main()
