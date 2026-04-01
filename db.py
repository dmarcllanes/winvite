import os
import re
import secrets
from datetime import datetime, timezone

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
import polars as pl

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "")

_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    if _pool is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _pool


def init_db() -> None:
    global _pool
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    _pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10)
    _create_tables()


def _create_tables() -> None:
    with _get_pool().connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id          SERIAL PRIMARY KEY,
                slug        TEXT UNIQUE NOT NULL,
                name        TEXT NOT NULL,
                phone       TEXT,
                category    TEXT NOT NULL DEFAULT 'General',
                plus_one    BOOLEAN NOT NULL DEFAULT FALSE,
                rsvp_status TEXT NOT NULL DEFAULT 'pending',
                opened_at   TIMESTAMPTZ
            )
        """)
        conn.commit()


def slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower().strip()).strip("-")
    return f"{base}-{secrets.token_hex(3)}"


def format_phone(phone: str) -> str:
    """Normalize PH phone numbers to international WhatsApp format."""
    digits = re.sub(r"[^\d]", "", phone)
    if digits.startswith("09") and len(digits) == 11:
        return "63" + digits[1:]
    if digits.startswith("9") and len(digits) == 10:
        return "63" + digits
    if digits.startswith("63"):
        return digits
    return digits


def get_guest(slug: str) -> dict | None:
    with _get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM guests WHERE slug = %s", (slug,))
            return cur.fetchone()


def mark_opened(slug: str) -> None:
    with _get_pool().connection() as conn:
        conn.execute(
            "UPDATE guests SET opened_at = %s WHERE slug = %s AND opened_at IS NULL",
            (datetime.now(timezone.utc), slug),
        )
        conn.commit()


def update_rsvp(slug: str, status: str, plus_one: bool) -> None:
    with _get_pool().connection() as conn:
        conn.execute(
            "UPDATE guests SET rsvp_status = %s, plus_one = %s WHERE slug = %s",
            (status, plus_one, slug),
        )
        conn.commit()


def get_all_guests() -> list[dict]:
    with _get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM guests ORDER BY name")
            return cur.fetchall()


def add_guest(name: str, phone: str, category: str) -> dict:
    slug = slugify(name)
    with _get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO guests (name, phone, category, slug)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (name.strip(), phone.strip(), category, slug),
            )
            conn.commit()
            return cur.fetchone()


def bulk_add_guests(csv_path: str) -> int:
    """Load guests from a CSV file using Polars and bulk-insert."""
    df = pl.read_csv(csv_path)
    required = {"name", "phone", "category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")

    count = 0
    with _get_pool().connection() as conn:
        for row in df.iter_rows(named=True):
            slug = slugify(row["name"])
            conn.execute(
                """
                INSERT INTO guests (name, phone, category, slug)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (slug) DO NOTHING
                """,
                (row["name"].strip(), row["phone"].strip(), row["category"], slug),
            )
            count += 1
        conn.commit()
    return count
