"""Create an MP4 demo video by driving the running frontend with Playwright."""

from pathlib import Path
import shutil
import subprocess
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "demo_video"
VIDEO_DIR = OUT_DIR / "raw"
MP4_PATH = OUT_DIR / "autism_intervention_demo.mp4"
FRONTEND_URL = "http://localhost:3000"


def wait(seconds: float) -> None:
    time.sleep(seconds)


def click_if_visible(page, text: str, timeout: int = 2500) -> bool:
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

        page.goto(FRONTEND_URL, wait_until="networkidle")
        wait(3)

        click_if_visible(page, "New Child Assessment")
        wait(2)

        click_if_visible(page, "Begin New Assessment")
        wait(2)

        click_if_visible(page, "Consent Granted")
        wait(2)

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
        wait(2)

        click_if_visible(page, "Submit & Generate Intervention Plan")
        try:
            page.get_by_text("awaiting clinician review", exact=False).wait_for(timeout=90000)
        except PlaywrightTimeoutError:
            page.get_by_text("Workflow", exact=False).first.wait_for(timeout=5000)
        wait(4)

        click_if_visible(page, "Clinician Review")
        wait(4)

        try:
            page.locator('button:has-text("AIG-")').first.click(timeout=15000)
            wait(3)
            for label in [
                "Intervention Guidelines",
                "SMART Developmental Goals",
                "Parent & Caregiver Guidance",
                "Governance & Audit Trail",
            ]:
                click_if_visible(page, label, timeout=1500)
                wait(1)
            try:
                page.locator("textarea").first.fill(
                    "Reviewed domain priorities, SMART goals, caregiver guidance, and audit trail. Approved for family delivery."
                )
            except PlaywrightTimeoutError:
                pass
            wait(2)
            click_if_visible(page, "Approve Plan", timeout=4000)
            wait(4)
        except PlaywrightTimeoutError:
            wait(4)

        click_if_visible(page, "Dashboard")
        wait(3)

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
