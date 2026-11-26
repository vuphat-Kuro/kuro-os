"""Lưu phiên chat vào SQLite (state/kuro.db)."""
import json
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
    for ddl in (
        "ALTER TABLE sessions ADD COLUMN agent TEXT DEFAULT 'kuro-core'",
        "ALTER TABLE sessions ADD COLUMN workspace TEXT DEFAULT ''",
        "ALTER TABLE sessions ADD COLUMN model TEXT DEFAULT ''",
        "ALTER TABLE sessions ADD COLUMN provider TEXT DEFAULT ''",
        "ALTER TABLE sessions ADD COLUMN conv_ids TEXT DEFAULT '{}'",
        "ALTER TABLE sessions ADD COLUMN usage_json TEXT DEFAULT '{}'",
        "ALTER TABLE messages ADD COLUMN provider TEXT DEFAULT ''",
    ):
        try:
            _q(ddl)
        except Exception:
            pass
    try:
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


def parse_conv_id(stored: str | None) -> tuple[str | None, str | None]:
    """Tách '<provider>:<id>'; mã trần bản cũ là 'claude', tiền tố cũ codex/agy đổi về id chuẩn."""
    if not stored:
        return None, None
    if ":" not in stored:
        return "claude", stored
    owner, conv = stored.split(":", 1)
    return {"codex": "chatgpt", "agy": "antigravity"}.get(owner, owner), conv


def get_conv_ids(sess_or_sid) -> dict[str, str]:
    """Lấy bản đồ mã hội thoại theo từng nhà cung cấp AI của phiên (hợp nhất cả claude_id cũ)."""
    sess = get(sess_or_sid) if isinstance(sess_or_sid, str) else (sess_or_sid or {})
    out: dict[str, str] = {}
    if not sess:
        return out
    raw = sess.get("conv_ids")
    if raw:
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(parsed, dict):
                for k, v in parsed.items():
                    if k and v:
                        norm_k = {"codex": "chatgpt", "agy": "antigravity"}.get(str(k), str(k))
                        out[norm_k] = str(v)
        except Exception:
            pass
    owner, conv = parse_conv_id(sess.get("claude_id"))
    if owner and conv and owner not in out:
        out[owner] = conv
    return out


def session_provider(sess: dict | None) -> str:
    """Suy ra provider của phiên: cột provider -> tiền tố claude_id -> rỗng (chưa gán)."""
    if not sess:
        return ""
    prov = (sess.get("provider") or "").strip()
    if prov:
        return prov
    owner, _ = parse_conv_id(sess.get("claude_id"))
    return owner or ""


def ensure(sid: str | None, title: str = "Phiên mới", agent: str = "kuro-core", workspace: str = "", model: str = "", provider: str = "") -> str:
    sid = sid or uuid.uuid4().hex[:12]
    now = time.time()
    agent = agent or "kuro-core"
    workspace = normalize_workspace(workspace)
    provider = (provider or "").strip()
    _q("INSERT OR IGNORE INTO sessions(id,title,agent,workspace,model,provider,conv_ids,created,updated) VALUES(?,?,?,?,?,?,?,?,?)",
       (sid, title[:80], agent, workspace, model or "", provider, "{}", now, now))
    if model:
        _q("UPDATE sessions SET model=? WHERE id=? AND (model IS NULL OR model='')", (model, sid))
    if provider:
        _q("UPDATE sessions SET provider=? WHERE id=? AND (provider IS NULL OR provider='')", (provider, sid))
    return sid


def get(sid: str) -> dict | None:
    rows = _q("SELECT * FROM sessions WHERE id=?", (sid,))
    return rows[0] if rows else None


def set_claude_id(sid: str, claude_id: str | None) -> None:
    if claude_id is None:
        _q("UPDATE sessions SET claude_id=NULL, conv_ids='{}', usage_json='{}', updated=? WHERE id=?", (time.time(), sid))
        return
    owner, conv = parse_conv_id(claude_id)
    conv_map = get_conv_ids(sid)
    if owner and conv:
        conv_map[owner] = conv
    _q("UPDATE sessions SET claude_id=?, conv_ids=?, updated=? WHERE id=?",
       (claude_id, json.dumps(conv_map, ensure_ascii=False), time.time(), sid))


def get_usage(sess_or_sid, provider: str | None = None) -> dict | None:
    """Lấy thống kê token gần nhất đã lưu cho phiên (theo provider nếu chỉ định)."""
    sess = get(sess_or_sid) if isinstance(sess_or_sid, str) else (sess_or_sid or {})
    if not sess:
        return None
    raw = sess.get("usage_json")
    if not raw:
        return None
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    if provider:
        prov = {"codex": "chatgpt", "agy": "antigravity"}.get(str(provider), str(provider))
        val = parsed.get(prov)
        return val if isinstance(val, dict) else None
    return parsed


def set_usage(sid: str, provider: str, usage: dict) -> None:
    """Lưu thống kê token thật (input/cache/output/total) gần nhất của phiên theo provider."""
    if not sid or not isinstance(usage, dict):
        return
    prov = {"codex": "chatgpt", "agy": "antigravity"}.get((provider or "claude").strip(), (provider or "claude").strip())
    cur = get_usage(sid) or {}
    merged = dict(cur.get(prov) or {})
    for k, v in usage.items():
        if v is not None:
            merged[k] = v
    merged["updated_at"] = time.time()
    cur[prov] = merged
    _q("UPDATE sessions SET usage_json=? WHERE id=?", (json.dumps(cur, ensure_ascii=False), sid))


def set_conv_id(sid: str, provider: str, conv_id: str) -> None:
    """Lưu mã hội thoại riêng cho từng provider trong cùng phiên (không xóa mạch của provider khác)."""
    prov = (provider or "claude").strip()
    conv_map = get_conv_ids(sid)
    if conv_id:
        conv_map[prov] = conv_id
    combined = f"{prov}:{conv_id}" if conv_id else None
    _q("UPDATE sessions SET claude_id=?, conv_ids=?, updated=? WHERE id=?",
       (combined, json.dumps(conv_map, ensure_ascii=False), time.time(), sid))


def bo_conv_id(sid: str, provider: str) -> None:
    """Bỏ hội thoại của một AI trong phiên (nén ngữ cảnh): lượt sau AI đó bắt đầu hội thoại mới, AI khác giữ nguyên."""
    prov = (provider or "claude").strip()
    conv_map = get_conv_ids(sid)
    conv_map.pop(prov, None)
    owner, conv = parse_conv_id((get(sid) or {}).get("claude_id"))
    combined = f"{owner}:{conv}" if owner and owner != prov and conv else None
    _q("UPDATE sessions SET claude_id=?, conv_ids=?, updated=? WHERE id=?",
       (combined, json.dumps(conv_map, ensure_ascii=False), time.time(), sid))


def set_agent(sid: str, agent: str) -> None:
    _q("UPDATE sessions SET agent=?, updated=? WHERE id=?", (agent, time.time(), sid))


def set_provider(sid: str, provider: str) -> None:
    _q("UPDATE sessions SET provider=?, updated=? WHERE id=?", ((provider or "").strip(), time.time(), sid))


def set_model(sid: str, model: str, provider: str | None = None) -> None:
    if provider is not None:
        _q("UPDATE sessions SET provider=?, model=?, updated=? WHERE id=?",
           ((provider or "").strip(), model or "", time.time(), sid))
    else:
        _q("UPDATE sessions SET model=?, updated=? WHERE id=?", (model or "", time.time(), sid))


def delete_session(sid: str) -> None:
    _q("DELETE FROM messages WHERE session_id=?", (sid,))
    _q("DELETE FROM sessions WHERE id=?", (sid,))


def replace_messages(sid: str, new_messages: list[dict]) -> None:
    _q("DELETE FROM messages WHERE session_id=?", (sid,))
    now = time.time()
    for m in new_messages:
        _q("INSERT INTO messages(session_id,role,text,ts,provider) VALUES(?,?,?,?,?)",
           (sid, m.get("role", "assistant"), m.get("text", ""), now, m.get("provider", "")))
    _q("UPDATE sessions SET updated=?, claude_id=NULL, conv_ids='{}', usage_json='{}' WHERE id=?", (now, sid))


def add(sid: str, role: str, text: str, provider: str = "") -> None:
    _q("INSERT INTO messages(session_id,role,text,ts,provider) VALUES(?,?,?,?,?)",
       (sid, role, text, time.time(), (provider or "").strip()))
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
    sql = f"SELECT id,title,updated,agent,workspace,model,provider,claude_id FROM sessions {where} ORDER BY updated DESC LIMIT ?"
    args.append(limit)
    rows = _q(sql, tuple(args))
    for r in rows:
        if not r.get("provider"):
            r["provider"] = session_provider(r)
        r.pop("claude_id", None)
    return rows


def messages(sid: str) -> list[dict]:
    return _q("SELECT role,text,ts,provider FROM messages WHERE session_id=? ORDER BY id", (sid,))
