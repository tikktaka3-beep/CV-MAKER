"""
database.py
Foydalanuvchilarning kunlik limitini va ishlatilgan slaydlar sonini SQLite orqali boshqaradi.
"""

import sqlite3
from datetime import date

DB_PATH = "slidebot.db"
DEFAULT_DAILY_LIMIT = 1


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            daily_limit INTEGER DEFAULT 1,
            username TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usage (
            user_id INTEGER,
            usage_date TEXT,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, usage_date)
        )
        """
    )
    conn.commit()
    conn.close()


def ensure_user(user_id: int, username: str = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, daily_limit, username) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username",
        (user_id, DEFAULT_DAILY_LIMIT, username),
    )
    conn.commit()
    conn.close()


def get_limit(user_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT daily_limit FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["daily_limit"] if row else DEFAULT_DAILY_LIMIT


def set_limit(user_id: int, new_limit: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, daily_limit) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET daily_limit=excluded.daily_limit",
        (user_id, new_limit),
    )
    conn.commit()
    conn.close()


def get_usage_today(user_id: int) -> int:
    today = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT count FROM usage WHERE user_id = ? AND usage_date = ?",
        (user_id, today),
    )
    row = cur.fetchone()
    conn.close()
    return row["count"] if row else 0


def increment_usage(user_id: int):
    today = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usage (user_id, usage_date, count) VALUES (?, ?, 1) "
        "ON CONFLICT(user_id, usage_date) DO UPDATE SET count = count + 1",
        (user_id, today),
    )
    conn.commit()
    conn.close()


def can_generate(user_id: int) -> bool:
    return get_usage_today(user_id) < get_limit(user_id)


def remaining_today(user_id: int) -> int:
    return max(get_limit(user_id) - get_usage_today(user_id), 0)
