import html
import os
import random
import re
import smtplib
import time
from email.message import EmailMessage
from pathlib import Path

import pandas as pd

from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = Path(__file__).resolve().parent

# =========================
# CONFIGURATION
# =========================

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()

EXCEL_FILE = os.getenv("EXCEL_FILE", "Email_finder.xlsx").strip()
RESUME_FILE = os.getenv("RESUME_FILE", "resume.pdf").strip()

SUBJECT = os.getenv(
    "SUBJECT",
    "Application for Data Analyst / Business Analyst Intern and FTE",
).strip()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_TIMEOUT_SEC = float(os.getenv("SMTP_TIMEOUT_SEC", "120"))

# Random pause between sends (seconds); varies each time so sending looks less automated
MIN_EMAIL_DELAY_SEC = float(os.getenv("MIN_EMAIL_DELAY_SEC", "15"))
MAX_EMAIL_DELAY_SEC = float(os.getenv("MAX_EMAIL_DELAY_SEC", "30"))

EMAIL_TEMPLATE_DIR = os.getenv("EMAIL_TEMPLATE_DIR", "templates").strip()
EMAIL_TEMPLATE = os.getenv("EMAIL_TEMPLATE", "default").strip()

# Fallback values when a {{PLACEHOLDER}} is not set in .env (Excel wins for HR_NAME / COMPANY)
TEMPLATE_ENV_DEFAULTS = {
    "CONTACT_NAME": "Shivani Khare",
    "CONTACT_PHONE": "8109166735",
    "CONTACT_EMAIL": "shivanikhare0001@gmail.com",
}

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise SystemExit(
        "Missing EMAIL_ADDRESS or EMAIL_PASSWORD. Copy .env.example to .env and set them."
    )

# =========================
# EMAIL TEMPLATES (HTML + optional plain)
# =========================

PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")


def _template_env_value(key: str) -> str:
    v = os.getenv(key, "").strip()
    if v:
        return v
    return TEMPLATE_ENV_DEFAULTS.get(key, "")


def render_email_template(template: str, hr_name: str, company: str, *, escape_html: bool) -> str:
    """Replace {{HR_NAME}}, {{COMPANY}}, and any {{NAME}} with matching environment variables."""

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key == "HR_NAME":
            val = hr_name
        elif key == "COMPANY":
            val = company
        else:
            val = _template_env_value(key)
        if escape_html:
            return html.escape(val or "", quote=False)
        return val or ""

    return PLACEHOLDER_PATTERN.sub(repl, template)


def _html_to_plain_fallback(rendered_html: str) -> str:
    t = re.sub(r"<br\s*/?>", "\n", rendered_html, flags=re.I)
    t = re.sub(r"</(p|h[1-6]|div|li|tr)>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    return "\n".join(line.strip() for line in t.splitlines() if line.strip())


_templates_root = Path(EMAIL_TEMPLATE_DIR)
if not _templates_root.is_absolute():
    _templates_root = SCRIPT_DIR / _templates_root

_html_path = _templates_root / f"{EMAIL_TEMPLATE}.html"
_plain_path = _templates_root / f"{EMAIL_TEMPLATE}.plain.txt"

if not _html_path.is_file():
    raise SystemExit(f"Missing HTML template file: {_html_path}")

HTML_TEMPLATE_SOURCE = _html_path.read_text(encoding="utf-8")
PLAIN_TEMPLATE_SOURCE = (
    _plain_path.read_text(encoding="utf-8") if _plain_path.is_file() else None
)

# =========================
# READ EXCEL FILE
# =========================

df = pd.read_excel(EXCEL_FILE)

# =========================
# SEND EMAILS
# =========================


def send_message_smtp(msg: EmailMessage) -> None:
    """One connection per send so idle timeouts (e.g. long delays between mails) cannot stale the socket."""
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SEC) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


for index, row in df.iterrows():

    hr_name = str(row['Employee'])
    hr_email = str(row['mail'])
    company = str(row['company'])

    # Skip empty emails
    if hr_email == "nan" or hr_email.strip() == "":
        continue

    body_html = render_email_template(
        HTML_TEMPLATE_SOURCE, hr_name, company, escape_html=True
    )
    if PLAIN_TEMPLATE_SOURCE is not None:
        body_plain = render_email_template(
            PLAIN_TEMPLATE_SOURCE, hr_name, company, escape_html=False
        )
    else:
        body_plain = _html_to_plain_fallback(body_html)

    try:
        msg = EmailMessage()

        msg['Subject'] = SUBJECT
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = hr_email

        msg.set_content(body_plain)
        msg.add_alternative(body_html, subtype="html")

        # Attach Resume
        with open(RESUME_FILE, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(RESUME_FILE)

        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='octet-stream',
            filename=file_name
        )

        send_message_smtp(msg)

        print(f"✅ Email sent to {hr_name} ({hr_email})")

        # Delay to avoid spam detection (randomized within range)
        delay_sec = random.uniform(MIN_EMAIL_DELAY_SEC, MAX_EMAIL_DELAY_SEC)
        time.sleep(delay_sec)

    except Exception as e:
        print(f"❌ Failed for {hr_email}")
        print(e)

print("\nAll emails processed.")