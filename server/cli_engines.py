"""Bộ não ngoài Claude Code: ChatGPT (qua `codex`) và Google Antigravity (`agy`).

Chạy chính chương trình của hãng, dùng tài khoản đã đăng nhập trên máy, giống Javis. Cờ dòng lệnh và
định dạng sự kiện ĐO THẬT trên codex-cli 0.156.1 và agy 1.3.3 (31/10/2026), không đoán:

- codex `exec --json`: thread.started{thread_id}; item.completed{item.type=agent_message, text};
  item.started{item.type=command_execution|file_change|mcp_tool_call|web_search}; turn.failed/error.
  `exec resume <id>` không nhận -C/-s, nên sandbox truyền bằng `-c sandbox_mode=...` cho cả hai đường.
- agy `-p --output-format stream-json`: init{conversation_id}; step_update{step_type=agent_response,
  text_delta} hoặc {step_type=tool, tool_name, state}; result{status, response}. Dòng không phải JSON
  (vd "a tool required the command permission ... auto-denied") giữ lại làm ghi chú, không nuốt im.

Quyền chạy lệnh: chỉ khi KURO_ALLOWED_TOOLS có Bash (cùng luật với đường Claude). Đã thử trên Windows:
sandbox "elevated" của codex lỗi quyền (mã 5) trên máy thường, còn "unelevated" KHÔNG chặn ghi ra ngoài
thư mục làm việc, nên không coi sandbox của codex là lớp bảo vệ.
"""
import asyncio
import json
import os
import shutil
import subprocess
from pathlib import Path

import config


def find(binary: str) -> str | None:
    # Trình cài agy thả vào %LOCALAPPDATA%\agy\bin, không chắc nằm trong PATH của tiến trình Kuro.
    extra = Path(os.getenv("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe"
    return shutil.which(binary) or (str(extra) if binary == "agy" and extra.is_file() else None)


_models: dict[str, list[dict]] = {}


async def models(kind: str) -> list[dict]:
    """Model mà tài khoản đăng nhập trên máy được dùng, lấy từ chính CLI (agy 1.3.3: dòng "slug<TAB>tên").
    Không giữ bảng model chép tay: Google đổi tên model liên tục. Chỉ agy có lệnh liệt kê; codex chưa có."""
    if kind != "agy" or not find("agy"):
        return []
    if kind not in _models:
        proc = await asyncio.create_subprocess_exec(
            find("agy"), "models", stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), 60)
        except TimeoutError:
            proc.kill()
            return []
        found = [dict(zip(("id", "ten"), l.strip().split("\t", 1)))
                 for l in out.decode("utf-8", "replace").splitlines() if "\t" in l]
        if found:   # lỗi mạng thì lần sau hỏi lại, không nhớ danh sách rỗng
            _models[kind] = found
        return found
    return _models[kind]


def _cmd(kind: str, prompt: str, resume: str | None, shell: bool, model: str | None = None) -> tuple[list[str], bytes | None]:
    """Trả (lệnh, dữ liệu stdin). codex nhận prompt qua stdin nên không vướng giới hạn dòng lệnh Windows."""
    chosen_model = model or config.MODEL
    if kind == "codex":
        cmd = [find("codex"), "exec"] + (["resume", resume] if resume else []) + [
            # --ignore-user-config: không nạp MCP và cấu hình cá nhân trong ~/.codex (đăng nhập vẫn giữ), cùng
            # nguyên tắc setting_sources=["project"] của đường Claude
            "--json", "--skip-git-repo-check", "--ignore-user-config", "-c", "approval_policy=\"never\"",
            "-c", f"sandbox_mode=\"{'workspace-write' if shell else 'read-only'}\""]
        if shell:   # elevated lỗi quyền trên máy thường; unelevated chạy được (xem ghi chú đầu file)
            cmd += ["-c", "windows.sandbox=\"unelevated\""]
        if chosen_model:
            cmd += ["-m", chosen_model]
        return cmd + ["-"], prompt.encode("utf-8")
    cmd = [find("agy"), "-p", prompt, "--output-format", "stream-json"]
    if resume:
        cmd += ["--conversation", resume]
    if chosen_model:
        cmd += ["--model", chosen_model]
    if shell:   # headless không hỏi được: không có cờ này thì agy tự từ chối mọi lệnh shell
        cmd.append("--dangerously-skip-permissions")
    return cmd, None


def _codex_event(e: dict, st: dict):
    t, it = e.get("type"), e.get("item") or {}
    if t == "thread.started":
        st["id"] = e.get("thread_id")
    elif t == "item.completed" and it.get("type") == "agent_message":
        txt = (it.get("text") or "").strip()
        if txt:
            yield {"type": "text", "text": ("\n\n" if st["text"] else "") + txt}
            st["text"] = True
    elif t == "item.started" and it.get("type") not in (None, "agent_message", "reasoning"):
        yield {"type": "tool", "name": it["type"], "input": {}}
    elif t in ("turn.failed", "error"):
        st["error"] = str((e.get("error") or {}).get("message") or e.get("message") or e)[:500]


def _agy_event(e: dict, st: dict):
    ev = e.get("event")
    if ev == "init":
        st["id"] = e.get("conversation_id")
    elif ev == "step_update":
        s = e.get("step_update") or {}
        if s.get("step_type") == "agent_response" and s.get("text_delta"):
            st["text"] = True
            yield {"type": "text", "text": s["text_delta"]}
        elif s.get("step_type") == "tool" and s.get("state") == "ACTIVE" and s.get("step_index") not in st["tools"]:
            st["tools"].add(s.get("step_index"))
            yield {"type": "tool", "name": s.get("tool_name") or "tool", "input": {}}
    elif ev == "result":
        r = e.get("result") or {}
        if r.get("status") != "SUCCESS":
            st["error"] = f"{r.get('status')}: {r.get('error') or r.get('response') or ''}"[:500]
        elif r.get("denied_actions") and not st["text"] and not r.get("response"):
            # Đo thật: tool bị từ chối thì agy dừng lượt, status vẫn SUCCESS, response rỗng, lý do nằm ở stderr
            names = ", ".join(a.get("display_name") or a.get("action", "") for a in r["denied_actions"])
            st["error"] = (f"AI dừng vì bị chặn quyền ({names}). Muốn cho phép thì thêm Bash ở ⚙ Cài đặt > "
                           "Tool được phép.")
        elif not st["text"] and r.get("response"):
            st["text"] = True
            yield {"type": "text", "text": r["response"]}


async def run(kind: str, prompt: str, resume: str | None, cwd: str | None = None, model: str | None = None):
    """Sinh sự kiện cùng khuôn với engine.run_turn; final mang mã hội thoại trần, engine gắn tiền tố id AI."""
    if not find(kind):
        yield {"type": "error", "text": f"Chưa cài `{kind}` trên máy này. Xem hướng dẫn ở ⚙ Cài đặt."}
        yield {"type": "final", "text": ""}
        return
    cmd, stdin = _cmd(kind, prompt, resume, "Bash" in config.ALLOWED_TOOLS, model=model)
    st = {"id": None, "text": False, "error": "", "tools": set(), "notes": []}
    work_dir = cwd or str(config.BRAIN)
    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=work_dir, limit=16 * 1024 * 1024,
        stdin=subprocess.PIPE if stdin else subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if stdin:
        proc.stdin.write(stdin)
        await proc.stdin.drain()
        proc.stdin.close()
    parse = _codex_event if kind == "codex" else _agy_event
    async for raw in proc.stdout:
        line = raw.decode("utf-8", "replace").strip()
        try:
            e = json.loads(line)
        except ValueError:
            if line:
                st["notes"].append(line)
            continue
        for out in parse(e, st):
            yield out
    err = (await proc.stderr.read()).decode("utf-8", "replace")
    code = await proc.wait()
    # Không bao giờ trả bong bóng rỗng: không có chữ thì phải có lý do (stderr, dòng lạ, hoặc câu mặc định).
    if (code or not st["text"]) and not st["error"]:
        st["error"] = (err.strip().splitlines() or st["notes"] or
                       [f"{kind} thoát mã {code}" if code else "AI không trả lời gì."])[-1][:500]
    if st["error"]:
        yield {"type": "error", "text": st["error"]}
    yield {"type": "final", "text": "", "claude_id": st["id"]}   # engine gắn tiền tố <id AI>:
