# ============================================================
#  storage/database.py
#  SQLite database — stores all seen jobs
# ============================================================

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the table if it doesn't exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_jobs (
                job_key       TEXT PRIMARY KEY,
                job_id        TEXT,
                company       TEXT,
                title         TEXT,
                location      TEXT,
                add_locations TEXT,
                posted_date   TEXT,
                posted_days   INTEGER,
                external_url  TEXT,
                json_url      TEXT,
                keyword       TEXT,
                first_seen    TEXT
            )
        """)
        conn.commit()


def make_key(company: str, job_id: str) -> str:
    """Composite key company::job_id — globally unique."""
    return f"{company}::{job_id}"


def is_seen(company: str, job_id: str) -> bool:
    """Returns True if job has already been seen."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_jobs WHERE job_key = ?",
            (make_key(company, job_id),)
        ).fetchone()
        return row is not None


def mark_seen(jobs: list[dict]):
    """Saves new jobs to the database."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with _connect() as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO seen_jobs
                (job_key, job_id, company, title, location, add_locations,
                 posted_date, posted_days, external_url, json_url, keyword, first_seen)
            VALUES
                (:job_key, :job_id, :company, :title, :location, :additional_locations,
                 :posted_date, :posted_days, :external_url, :json_url, :keyword, :first_seen)
        """, [{**j, "first_seen": now} for j in jobs])
        conn.commit()


def get_all_jobs() -> list[dict]:
    """Returns all jobs from the database."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM seen_jobs ORDER BY first_seen DESC"
        ).fetchall()
        return [dict(r) for r in rows]