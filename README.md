# Email outreach automation

Sends personalized application emails from a Gmail account using contacts listed in an Excel file, with your resume attached. Includes a random delay between messages (default 15–30 seconds) to reduce automated-looking bursts.

## Prerequisites

- **Python 3.9+** (or any recent 3.x)
- A **Gmail** account with [2-Step Verification](https://support.google.com/accounts/answer/185839) enabled and an **[App Password](https://support.google.com/accounts/answer/185833)** for SMTP (not your normal Gmail password)

## Configure

1. **Clone or download** this repository.

2. **Create a virtual environment** (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**: copy the template and edit **`.env`** (never commit **`.env`** — it is gitignored).

   ```bash
   cp .env.example .env
   ```

   Required:

   | Variable | Description |
   |----------|-------------|
   | `EMAIL_ADDRESS` | Gmail address used to send |
   | `EMAIL_PASSWORD` | Gmail App Password (quote it if it contains spaces) |

   Optional overrides (defaults match the comments in `.env.example`):

   `EXCEL_FILE`, `RESUME_FILE`, `SUBJECT`, `SMTP_HOST`, `SMTP_PORT`, `MIN_EMAIL_DELAY_SEC`, `MAX_EMAIL_DELAY_SEC`.

5. **Excel file**: place your spreadsheet next to `script.py` (or set `EXCEL_FILE` in `.env`). It must include these columns:

   - **`Employee`** — recipient name used in the greeting  
   - **`mail`** — recipient email  
   - **`company`** — company name used in the body  

   Default filename: **`Email_finder.xlsx`**.

6. **Resume**: add **`resume.pdf`** in the project folder, or set **`RESUME_FILE`** in `.env` to another path.

## Run

From the project directory (with the virtual environment activated if you use one):

```bash
python script.py
```

The script logs success or failure per row and waits a random interval between **15** and **30** seconds after each successful send (configurable via **`MIN_EMAIL_DELAY_SEC`** and **`MAX_EMAIL_DELAY_SEC`**).

## Important

- Double-check your Excel list and **`.env`** before running — every valid **`mail`** row triggers a real email.
- Mass mailing can still violate provider limits or spam policies; use responsibly and comply with applicable laws and terms of service.
