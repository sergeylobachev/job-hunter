# ============================================================
#  notifier/email_alert.py
#  Sends an HTML email with new job listings
# ============================================================

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def _build_html(jobs: list[dict]) -> str:
    rows = ""
    for j in jobs:
        days = j.get("posted_days", "?")
        days_str = "today" if days == 0 else f"{days}d ago"
        add_loc = f"<br><small style='color:#888'>{j['additional_locations']}</small>" \
                  if j.get("additional_locations") else ""
        rows += f"""
        <tr>
            <td style='padding:8px;border-bottom:1px solid #eee'>{j['company']}</td>
            <td style='padding:8px;border-bottom:1px solid #eee'>
                <a href='{j['external_url']}' style='color:#1a73e8;text-decoration:none'>{j['title']}</a>
            </td>
            <td style='padding:8px;border-bottom:1px solid #eee'>{j['location']}{add_loc}</td>
            <td style='padding:8px;border-bottom:1px solid #eee;color:#888;font-size:12px'>{days_str}</td>
        </tr>"""

    return f"""
    <html><body style='font-family:Arial,sans-serif;color:#333'>
        <h2 style='color:#1a73e8'>Job Hunter — {len(jobs)} new jobs</h2>
        <p style='color:#888;font-size:13px'>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <table style='width:100%;border-collapse:collapse;font-size:14px'>
            <thead>
                <tr style='background:#f5f5f5'>
                    <th style='padding:10px;text-align:left;width:100px'>Company</th>
                    <th style='padding:10px;text-align:left'>Title</th>
                    <th style='padding:10px;text-align:left;width:200px'>Location</th>
                    <th style='padding:10px;text-align:left;width:80px'>Posted</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <p style='color:#aaa;font-size:12px;margin-top:20px'>Job Hunter — automated alert</p>
    </body></html>
    """


def send_email(jobs: list[dict], config: dict):
    """Sends an HTML email with new job listings."""
    if not jobs:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Hunter: {len(jobs)} new jobs"
    msg["From"]    = config["EMAIL_FROM"]
    msg["To"]      = config["EMAIL_TO"]
    msg.attach(MIMEText(_build_html(jobs), "html"))

    with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"]) as server:
        server.starttls()
        server.login(config["EMAIL_FROM"], config["EMAIL_PASSWORD"])
        server.sendmail(config["EMAIL_FROM"], config["EMAIL_TO"], msg.as_string())

    print(f"  Email sent: {len(jobs)} jobs → {config['EMAIL_TO']}")