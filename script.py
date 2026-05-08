import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import random
import time

from dotenv import load_dotenv

load_dotenv()

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

# Random pause between sends (seconds); varies each time so sending looks less automated
MIN_EMAIL_DELAY_SEC = float(os.getenv("MIN_EMAIL_DELAY_SEC", "15"))
MAX_EMAIL_DELAY_SEC = float(os.getenv("MAX_EMAIL_DELAY_SEC", "30"))

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise SystemExit(
        "Missing EMAIL_ADDRESS or EMAIL_PASSWORD. Copy .env.example to .env and set them."
    )

# =========================
# READ EXCEL FILE
# =========================

df = pd.read_excel(EXCEL_FILE)

# =========================
# SMTP SERVER SETUP
# =========================

server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
server.starttls()
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

# =========================
# SEND EMAILS
# =========================

for index, row in df.iterrows():

    hr_name = str(row['Employee'])
    hr_email = str(row['mail'])
    company = str(row['company'])

    # Skip empty emails
    if hr_email == "nan" or hr_email.strip() == "":
        continue

    body = f"""
Good Morning {hr_name},

I hope you are doing well.

I am Shivani Khare, a graduate from National Institute of Technology, Raipur (CGPA: 8.44), currently seeking entry-level opportunities in Data Analytics / Business Analytics at {company}.

During my Data Analyst Internship at PwC (Virtual), I built dashboards and solved real business problems using data, identifying key drivers of customer churn and improving retention strategies.

Additionally, as a Graduate Engineer Trainee at AMNS Surat, I monitored KPIs and analyzed production data to identify operational inefficiencies, gaining hands-on exposure to real-world data applications.

Here are some of my key projects:

1. Pizza Sales Analysis (SQL)
Video:
https://www.loom.com/share/ed8f60f9041f4cf698af8396bbd47b1d

2. Cost & Profitability Analysis of Food Delivery (Python)
- Reduced delivery costs by 15%
- Improved profit margins by 12%

Video:
https://www.loom.com/share/4995c2bb080647c3b0dddc86e72d2421

GitHub:
https://github.com/shivanii-khare/first-project

3. Blinkit Sales Insights Dashboard (Power BI, Excel)
- Built dashboards tracking sales trends and customer behavior
- Improved marketing effectiveness by 12%

GitHub:
https://github.com/shivanii-khare/powberBi-Dashboard

I am particularly interested in roles where I can apply data analysis to solve real-world business problems and contribute to decision-making at {company}.

Please find my resume attached for your reference.

I would really appreciate the opportunity to connect and discuss any relevant openings.

Looking forward to hearing from you.

Regards,
Shivani Khare
8109166735
shivanikhare0001@gmail.com
"""

    try:
        msg = EmailMessage()

        msg['Subject'] = SUBJECT
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = hr_email

        msg.set_content(body)

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

        # Send Email
        server.send_message(msg)

        print(f"✅ Email sent to {hr_name} ({hr_email})")

        # Delay to avoid spam detection (randomized within range)
        delay_sec = random.uniform(MIN_EMAIL_DELAY_SEC, MAX_EMAIL_DELAY_SEC)
        time.sleep(delay_sec)

    except Exception as e:
        print(f"❌ Failed for {hr_email}")
        print(e)

# =========================
# CLOSE SERVER
# =========================

server.quit()

print("\nAll emails processed.")