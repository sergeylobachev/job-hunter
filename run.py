# ============================================================
#  run.py — entry point
#  Run manually or via Task Scheduler twice a day:
#
#  Windows Task Scheduler:
#    Program:   C:\Python\job-hunter\job_env\Scripts\python.exe
#    Arguments: C:\Python\job-hunter\run.py
#
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from datetime import datetime

from config.settings import (
    COMPANIES, KEYWORDS, LOCATION_FILTERS, TITLE_FILTERS,
    MAX_JOBS_PER_COMPANY, PAGE_SIZE, REQUEST_DELAY_SEC,
    FRESH_ONLY, FRESH_DAYS,
    EMAIL_ENABLED, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD, SMTP_HOST, SMTP_PORT,
)
from scrapers.workday import (
    scrape_company, title_matches,
    fetch_detail, extract_all_locations, location_matches_any,
)
from storage.database import init_db, is_seen, mark_seen
from notifier.email_alert import send_email


def main():
    print(f"\n{'='*60}")
    print(f"Job Hunter started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Companies: {len(COMPANIES)} | Keywords: {KEYWORDS}")
    print(f"Freshness: {'up to ' + str(FRESH_DAYS) + ' days' if FRESH_ONLY else 'all'}")
    print(f"{'='*60}\n")

    init_db()
    session            = requests.Session()
    new_jobs           = []
    seen_keys_this_run = set()

    for company in COMPANIES:
        print(f"\n── {company['name']} ──────────────────────────")
        company_new = 0

        for keyword in KEYWORDS:
            print(f"  Keyword: '{keyword}'")
            try:
                jobs = scrape_company(
                    session    = session,
                    company    = company,
                    keyword    = keyword,
                    max_jobs   = MAX_JOBS_PER_COMPANY,
                    page_size  = PAGE_SIZE,
                    delay      = REQUEST_DELAY_SEC,
                    fresh_only = FRESH_ONLY,
                    fresh_days = FRESH_DAYS,
                )
            except Exception as e:
                print(f"  Error: {e}")
                continue

            for job in jobs:
                key = job["job_key"]

                # 1. Deduplication within this run
                if key in seen_keys_this_run:
                    continue
                seen_keys_this_run.add(key)

                # 2. Already seen in previous runs?
                if is_seen(job["company"], job["job_id"]):
                    continue

                # 3. Title filter — fast, no extra requests
                if not title_matches(job["title"], TITLE_FILTERS):
                    continue

                # 4. Location filter — check basic location first
                basic_loc = job.get("location", "")
                if location_matches_any([basic_loc], LOCATION_FILTERS):
                    # Basic location matched — no need to fetch details
                    new_jobs.append(job)
                    company_new += 1
                else:
                    # Basic location didn't match — fetch details to check
                    # additionalLocations (e.g. Remote might be listed there)
                    detail    = fetch_detail(session, job["json_url"])
                    all_locs  = extract_all_locations(detail)

                    if location_matches_any(all_locs, LOCATION_FILTERS):
                        # Update job with full location info
                        job["additional_locations"] = "; ".join(all_locs[1:])
                        new_jobs.append(job)
                        company_new += 1

                    import time
                    time.sleep(REQUEST_DELAY_SEC)

        print(f"  New jobs: {company_new}")

    # Save to database
    if new_jobs:
        mark_seen(new_jobs)

    print(f"\n{'='*60}")
    print(f"Total new jobs: {len(new_jobs)}")
    print(f"{'='*60}\n")

    # Send email
    if new_jobs and EMAIL_ENABLED:
        print("Sending email...")
        try:
            send_email(new_jobs, {
                "EMAIL_FROM":     EMAIL_FROM,
                "EMAIL_TO":       EMAIL_TO,
                "EMAIL_PASSWORD": EMAIL_PASSWORD,
                "SMTP_HOST":      SMTP_HOST,
                "SMTP_PORT":      SMTP_PORT,
            })
        except Exception as e:
            print(f"  Email error: {e}")
    elif not new_jobs:
        print("No new jobs — email not sent.")

    # Console output
    if new_jobs:
        print("\nNew jobs:")
        for j in new_jobs:
            days     = j.get("posted_days", "?")
            days_str = "today" if days == 0 else f"{days}d ago"
            locs     = j["location"]
            if j.get("additional_locations"):
                locs += f" | {j['additional_locations']}"
            print(f"  [{j['company']}] {j['title']} — {locs} ({days_str})")
            print(f"    {j['external_url']}")


if __name__ == "__main__":
    main()