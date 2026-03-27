# Job Hunter

`Job Hunter` is a small Python project that scans Workday job boards, filters results by keyword, title, location, and freshness, stores previously seen jobs in SQLite, and sends an email when new matching jobs appear.

## What It Does

- Queries multiple Workday-based career sites
- Filters jobs by your search keywords and title rules
- Applies location and freshness filters
- Saves seen jobs in a local SQLite database so alerts are not repeated
- Sends an HTML email with new matching jobs

## Project Structure

- `run.py` - main entry point
- `scrapers/workday.py` - Workday scraper and filter helpers
- `storage/database.py` - SQLite storage for seen jobs
- `notifier/email_alert.py` - email sender
- `config/settings.example.py` - safe config template

## Setup

1. Create and activate the virtual environment.

```powershell
.\job_env\Scripts\Activate.ps1
```

2. Install dependencies if needed.

```powershell
pip install requests beautifulsoup4 pandas
```

3. Copy the example config and edit your local settings.

```powershell
Copy-Item config\settings.example.py config\settings.py
```

4. Update `config/settings.py`:

- your keywords
- location filters
- company list
- Gmail address and app password

## Run

From the project root:

```powershell
python run.py
```

The script will:

- create `data/jobs.db` if it does not exist
- scrape configured companies
- skip jobs already seen in previous runs
- send an email only when new jobs are found

## Gmail App Password

This project uses Gmail SMTP, so you should use a Google App Password instead of your normal Gmail password.

### Requirements

- your Google account must have 2-Step Verification enabled

### How to generate it

1. Sign in to your Google account.
2. Open `https://myaccount.google.com/security`
3. Enable `2-Step Verification` if it is not already enabled.
4. After that, open `https://myaccount.google.com/apppasswords`
5. Choose an app name such as `Job Hunter`
6. Google will show a 16-character app password
7. Put that value into `EMAIL_PASSWORD` in `config/settings.py`

Example:

```python
EMAIL_FROM = "your-email@gmail.com"
EMAIL_TO = "your-email@gmail.com"
EMAIL_PASSWORD = "your-16-character-app-password-without-spaces"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
```

## GitHub Notes

The repository is set up so local-only files are not committed:

- `job_env/`
- `data/`
- `config/settings.py`
- Python cache files

Keep your real secrets only in `config/settings.py`. Commit `config/settings.example.py`, not your private config.

## Optional Automation

You can run a script on a schedule with Windows Task Scheduler.
