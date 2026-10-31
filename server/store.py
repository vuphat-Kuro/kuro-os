"""Lưu phiên chat vào SQLite (state/kuro.db)."""
import sqlite3
import time
import uuid

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions(
  id TEXT PRIMARY KEY, title TEXT, claude_id TEXT, created REAL, updated REAL);
CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY, session_id TEXT, role TEXT, text TEXT, ts REAL);
CREATE INDEX IF NOT EXISTS ix_messages ON messages(session_id, id);
"""


def _q(sql: str, args=(), script=False):
    # shortcut: gọi SQLite đồng bộ trong vòng async, đủ cho 1 người dùng; nhiều người thì chuyển sang to_thread
    c = sqlite3.connect(config.STATE / "kuro.db")
    c.row_factory = sqlite3.Row
    try:
        rows = c.executescript(sql) if script else c.execute(sql, args)
        out = [dict(r) for r in rows.fetchall()] if not script else []
        c.commit()
        return out
    finally:
        c.close()


def init() -> None:
    _q(SCHEMA, script=True)


def ensure(sid: str | None, title: str = "Phiên mới") -> str:
    sid = sid or uuid.uuid4().hex[:12]
    now = time.time()
    _q("INSERT OR IGNORE INTO sessions(id,title,created,updated) VALUES(?,?,?,?)", (sid, title[:80], now, now))
    return sid


def get(sid: str) -> dict | None:
    rows = _q("SELECT * FROM sessions WHERE id=?", (sid,))
    return rows[0] if rows else None


def set_claude_id(sid: str, claude_id: str | None) -> None:
    _q("UPDATE sessions SET claude_id=?, updated=? WHERE id=?", (claude_id, time.time(), sid))


def add(sid: str, role: str, text: str) -> None:
    _q("INSERT INTO messages(session_id,role,text,ts) VALUES(?,?,?,?)", (sid, role, text, time.time()))
    _q("UPDATE sessions SET updated=? WHERE id=?", (time.time(), sid))


def sessions(limit: int = 100) -> list[dict]:
    return _q("SELECT id,title,updated FROM sessions ORDER BY updated DESC LIMIT ?", (limit,))


def messages(sid: str) -> list[dict]:
    return _q("SELECT role,text,ts FROM messages WHERE session_id=? ORDER BY id", (sid,))
