import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/toilet.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        gender TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        role TEXT,
        member_name TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS round_status (
        role TEXT,
        member_name TEXT,
        done INTEGER DEFAULT 0,
        PRIMARY KEY (role, member_name)
    )""")
    c.execute("SELECT COUNT(*) FROM members")
    if c.fetchone()[0] == 0:
        with open("members.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for name in data.get("men", []):
            c.execute("INSERT OR IGNORE INTO members (name, gender) VALUES (?, ?)", (name, "M"))
        for name in data.get("women", []):
            c.execute("INSERT OR IGNORE INTO members (name, gender) VALUES (?, ?)", (name, "F"))
        for name in data.get("men", []):
            c.execute("INSERT OR IGNORE INTO round_status (role, member_name, done) VALUES (?, ?, 0)", ("Men", name))
            c.execute("INSERT OR IGNORE INTO round_status (role, member_name, done) VALUES (?, ?, 0)", ("Guest", name))
        for name in data.get("women", []):
            c.execute("INSERT OR IGNORE INTO round_status (role, member_name, done) VALUES (?, ?, 0)", ("Women", name))
    conn.commit()
    conn.close()


def get_members(gender=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if gender:
        c.execute("SELECT name FROM members WHERE gender=?", (gender,))
    else:
        c.execute("SELECT name FROM members")
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows


def get_recent_winners(role, days):
    from datetime import date, timedelta
    threshold = (date.today() - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT member_name FROM history WHERE role=? AND date > ?", (role, threshold))
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows


def get_round_done(role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT member_name FROM round_status WHERE role=? AND done=1", (role,))
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows


def get_round_counts(role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM round_status WHERE role=?", (role,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM round_status WHERE role=? AND done=1", (role,))
    done = c.fetchone()[0]
    conn.close()
    return done, total


def save_result(winners):
    from datetime import date
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE date=?", (today,))
    for role, name in winners.items():
        if name and name != "該当者なし":
            c.execute("INSERT INTO history (date, role, member_name) VALUES (?, ?, ?)", (today, role, name))
            c.execute("UPDATE round_status SET done=1 WHERE role=? AND member_name=?", (role, name))
    for role in ("Men", "Guest", "Women"):
        c.execute("SELECT COUNT(*) FROM round_status WHERE role=? AND done=0", (role,))
        if c.fetchone()[0] == 0:
            c.execute("UPDATE round_status SET done=0 WHERE role=?", (role,))
    conn.commit()
    conn.close()


def get_history(limit=7):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT date, role, member_name FROM history ORDER BY date DESC LIMIT ?", (limit * 3,))
    rows = c.fetchall()
    conn.close()
    return rows


def reset_round(role=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if role:
        c.execute("UPDATE round_status SET done=0 WHERE role=?", (role,))
    else:
        c.execute("UPDATE round_status SET done=0")
    conn.commit()
    conn.close()


def rename_member(old_name, new_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE members SET name=? WHERE name=?", (new_name, old_name))
    c.execute("UPDATE history SET member_name=? WHERE member_name=?", (new_name, old_name))
    c.execute("UPDATE round_status SET member_name=? WHERE member_name=?", (new_name, old_name))
    conn.commit()
    conn.close()


def clear_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()
