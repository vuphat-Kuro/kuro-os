"""Lưu phiên chat vào SQLite (state/kuro.db)."""
import sqlite3
import time
import uuid

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions(
  id TEXT PRIMARY KEY, title TEXT, claude_id TEXT, created REAL, updated REAL, agent TEXT DEFAULT 'kuro-core');
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
    try:
        _q("ALTER TABLE sessions ADD COLUMN agent TEXT DEFAULT 'kuro-core'")
    except Exception:
        pass
    try:
        _q("ALTER TABLE sessions ADD COLUMN workspace TEXT DEFAULT ''")
    except Exception:
        pass
    try:
        from pathlib import Path
        import config
        def_ws = normalize_workspace(str(config.ROOT / "projects" / "DuAn_KhoiTao"))
        _q("UPDATE sessions SET workspace=? WHERE workspace='' OR workspace IS NULL", (def_ws,))
    except Exception:
        pass


def normalize_workspace(ws: str | None) -> str:
    if not ws:
        return ""
    try:
        from pathlib import Path
        return Path(ws).resolve().as_posix().lower()
    except Exception:
        return ws.strip().replace("\\", "/").lower()


def ensure(sid: str | None, title: str = "Phiên mới", agent: str = "kuro-core", workspace: str = "") -> str:
    sid = sid or uuid.uuid4().hex[:12]
    now = time.time()
    agent = agent or "kuro-core"
    workspace = normalize_workspace(workspace)
    _q("INSERT OR IGNORE INTO sessions(id,title,agent,workspace,created,updated) VALUES(?,?,?,?,?,?)",
       (sid, title[:80], agent, workspace, now, now))
    return sid


def get(sid: str) -> dict | None:
    rows = _q("SELECT * FROM sessions WHERE id=?", (sid,))
    return rows[0] if rows else None


def set_claude_id(sid: str, claude_id: str | None) -> None:
    _q("UPDATE sessions SET claude_id=?, updated=? WHERE id=?", (claude_id, time.time(), sid))


def set_agent(sid: str, agent: str) -> None:
    _q("UPDATE sessions SET agent=?, updated=? WHERE id=?", (agent, time.time(), sid))


def delete_session(sid: str) -> None:
    _q("DELETE FROM messages WHERE session_id=?", (sid,))
    _q("DELETE FROM sessions WHERE id=?", (sid,))


def replace_messages(sid: str, new_messages: list[dict]) -> None:
    _q("DELETE FROM messages WHERE session_id=?", (sid,))
    now = time.time()
    for m in new_messages:
        _q("INSERT INTO messages(session_id,role,text,ts) VALUES(?,?,?,?)", (sid, m.get("role", "assistant"), m.get("text", ""), now))
    _q("UPDATE sessions SET updated=?, claude_id=NULL WHERE id=?", (now, sid))


def add(sid: str, role: str, text: str) -> None:
    _q("INSERT INTO messages(session_id,role,text,ts) VALUES(?,?,?,?)", (sid, role, text, time.time()))
    _q("UPDATE sessions SET updated=? WHERE id=?", (time.time(), sid))


def sessions(limit: int = 100, agent: str | None = None, workspace: str | None = None) -> list[dict]:
    clauses = []
    args = []
    if agent and agent != "all":
        clauses.append("agent=?")
        args.append(agent)
    if workspace and workspace != "all":
        norm_ws = normalize_workspace(workspace)
        clauses.append("workspace=?")
        args.append(norm_ws)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT id,title,updated,agent,workspace FROM sessions {where} ORDER BY updated DESC LIMIT ?"
    args.append(limit)
    return _q(sql, tuple(args))


def messages(sid: str) -> list[dict]:
    return _q("SELECT role,text,ts FROM messages WHERE session_id=? ORDER BY id", (sid,))
