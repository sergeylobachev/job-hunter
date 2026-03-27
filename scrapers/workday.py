# ============================================================
#  scrapers/workday.py
#  Universal Workday scraper — works with any company
# ============================================================

import re
import time
from urllib.parse import urljoin

import requests

HEADERS = {
    "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept":       "application/json",
    "Content-Type": "application/json",
}


def _build_urls(company: dict) -> dict:
    """Generates all required URLs from three config fields."""
    host        = company["wd_host"]
    tenant_id   = company["tenant_id"]
    tenant_name = company["tenant_name"]
    base        = f"https://{host}/wday/cxs/{tenant_id}/{tenant_name}"
    return {
        "api_url":     f"{base}/jobs",
        "detail_base": f"{base}/",
        "public_base": f"https://{host}/en-US/{tenant_name}",
    }


def _build_external_url(urls: dict, job: dict) -> str:
    external_url = job.get("externalUrl")
    if external_url:
        return external_url
    path = job.get("externalPath", "")
    if path:
        return urljoin(urls["public_base"].rstrip("/") + "/", path.lstrip("/"))
    return urls["public_base"]


def _build_json_url(urls: dict, job: dict) -> str:
    path = job.get("externalPath", "")
    if path:
        return urls["detail_base"].rstrip("/") + "/" + path.lstrip("/")
    return ""


def _extract_job_id(job: dict, json_url: str) -> str:
    """Extracts job_id from bulletFields or falls back to the last URL segment."""
    for field in job.get("bulletFields", []):
        if isinstance(field, str) and field.strip():
            return field.strip()
    if json_url:
        return json_url.rstrip("/").split("_")[-1]
    return json_url


def parse_posted_days(posted_on: str) -> int:
    """
    Parses a string like 'Posted 3 Days Ago' -> 3.
    'Posted Today' / 'Just Posted' -> 0
    'Posted 30+ Days Ago' -> 999
    Returns number of days as integer.
    """
    if not posted_on:
        return 999
    text = posted_on.lower()
    if "today" in text or "just posted" in text:
        return 0
    match = re.search(r"(\d+)\+?\s+day", text)
    if match:
        return int(match.group(1))
    return 999


def is_fresh(posted_days: int, max_days: int) -> bool:
    return posted_days <= max_days


def _fetch_page(session, api_url, keyword, limit, offset) -> dict:
    payload = {"appliedFacets": {}, "limit": limit, "offset": offset, "searchText": keyword}
    r = session.post(api_url, json=payload, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_detail(session, json_url) -> dict:
    """Fetches full job detail JSON — location, additionalLocations, startDate."""
    if not json_url:
        return {}
    try:
        r = session.get(
            json_url,
            headers={**HEADERS, "Accept-Language": "en-US,en;q=0.9"},
            timeout=20,
        )
        r.raise_for_status()
        return r.json().get("jobPostingInfo", {})
    except Exception:
        return {}


def extract_all_locations(detail: dict) -> list[str]:
    """Returns a flat list of all location strings from job detail."""
    locations = []

    loc = detail.get("location")
    if isinstance(loc, dict):
        locations.append(loc.get("descriptor", ""))
    elif isinstance(loc, str):
        locations.append(loc)

    for l in detail.get("additionalLocations", []):
        if isinstance(l, dict):
            locations.append(l.get("descriptor", ""))
        elif isinstance(l, str):
            locations.append(l)

    return [l for l in locations if l]


def location_matches(location_text: str, location_filters: dict) -> bool:
    """Returns True if location string matches any filter zone."""
    loc = location_text.lower()
    for zone, keywords in location_filters.items():
        if any(kw.lower() in loc for kw in keywords):
            return True
    return False


def location_matches_any(locations: list[str], location_filters: dict) -> bool:
    """Returns True if ANY location in the list matches any filter zone."""
    return any(location_matches(loc, location_filters) for loc in locations)


def title_matches(title: str, title_filters: list) -> bool:
    """Returns True if job title contains at least one of the title filters."""
    t = title.lower()
    return any(kw.lower() in t for kw in title_filters)


def scrape_company(
    session: requests.Session,
    company: dict,
    keyword: str,
    max_jobs: int,
    page_size: int,
    delay: float,
    fresh_only: bool = False,
    fresh_days: int = 3,
) -> list[dict]:
    """
    Scrapes one company for one keyword.
    Returns raw job list — filtering happens in run.py.
    """
    urls   = _build_urls(company)
    rows   = []
    offset = 0

    while len(rows) < max_jobs:
        try:
            data     = _fetch_page(session, urls["api_url"], keyword, page_size, offset)
            postings = data.get("jobPostings", [])
            total    = data.get("total", 0)
        except Exception as e:
            print(f"    Request error {company['name']}: {e}")
            break

        if not postings:
            break

        for job in postings:
            posted_on   = job.get("postedOn", "")
            posted_days = parse_posted_days(posted_on)

            # Skip old jobs but keep scanning
            if fresh_only and not is_fresh(posted_days, fresh_days):
                continue

            json_url     = _build_json_url(urls, job)
            external_url = _build_external_url(urls, job)
            job_id       = _extract_job_id(job, json_url)

            rows.append({
                "job_key":              f"{company['name']}::{job_id}",
                "job_id":               job_id,
                "company":              company["name"],
                "title":                job.get("title", "N/A"),
                "posted_date":          posted_on,
                "posted_days":          posted_days,
                "location":             job.get("locationsText", ""),
                "additional_locations": "",   # filled later if needed
                "external_url":         external_url,
                "json_url":             json_url,
                "keyword":              keyword,
            })

            if len(rows) >= max_jobs:
                break

        if offset + page_size >= total:
            break

        offset += page_size
        time.sleep(delay)

    return rows