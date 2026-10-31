"""Chạy một lượt chat qua Claude Code (claude-agent-sdk), dùng chung cho web, Telegram và nhắc hẹn.

Luồng sự kiện gửi cho giao diện:
  {"type": "text", "text"}           đoạn chữ đang stream
  {"type": "tool", "name", "input"}  Claude vừa gọi một tool
  {"type": "final", "text", "cost"}  hết lượt
  {"type": "error", "text"}
"""
import asyncio
import json
from datetime import datetime

import httpx
import yaml
from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, ResultMessage,
                              StreamEvent, ToolUseBlock, query)

import calc
import cli_engines
import config
import store


def mcp_from_file() -> dict:
    """MCP ngoài (Revit, AutoCAD...) khai trong state/mcp.json, cùng định dạng .mcp.json của Claude Code."""
    if not config.MCP_FILE.is_file():
        return {}
    try:
        return json.loads(config.MCP_FILE.read_text(encoding="utf-8")).get("mcpServers", {})
    except (ValueError, AttributeError) as e:
        print(f"[mcp] state/mcp.json hỏng, bỏ qua: {e}")
        return {}


def load_agents() -> dict[str, AgentDefinition]:
    """Đọc brain/agents/*.md (cùng định dạng agent của Javis) thành subagent của Claude Code."""
    out = {}
    for p in sorted((config.BRAIN / "agents").glob("*.md")):
        raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
        if not raw.startswith("---\n"):
            continue
        try:
            _, fm, body = raw.split("---\n", 2)
            meta = yaml.safe_load(fm) or {}
        except (ValueError, yaml.YAMLError) as e:
            print(f"[agent] bỏ qua {p.name}: {e}")
            continue
        out[meta.get("slug") or p.stem] = AgentDefinition(
            description=meta.get("role") or meta.get("name") or p.stem,
            prompt=body.strip(),
            skills=meta.get("skills") or None,
            model=meta.get("model") or None,
        )
    return out


def system_append() -> str:
    """Kernel (CLAUDE.md gốc) + ký ức + giờ hiện tại, nối vào sau prompt mặc định của Claude Code."""
    parts = []
    for p in (config.ROOT / "CLAUDE.md", config.BRAIN / "memory" / "MEMORY.md"):
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8"))
    parts.append(f"Bây giờ là {datetime.now():%H:%M %d/%m/%Y} (giờ máy).")
    return "\n\n".join(parts)


def options(claude_id: str | None) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code", "append": system_append()},
        cwd=str(config.BRAIN),
        model=config.MODEL or None,
        env=config.provider_env(),
        resume=claude_id,
        skills="all",
        setting_sources=["project"],      # chỉ đọc cấu hình trong brain, KHÔNG nạp ~/.claude của máy
        # Hai lớp chặn: `tools` gỡ hẳn tool built-in ngoài danh sách (dontAsk một mình vẫn cho chạy
        # lệnh Bash "chỉ đọc" như echo - đã thử thật); dontAsk từ chối MCP tool chưa được liệt kê.
        tools=[t for t in config.ALLOWED_TOOLS if not t.startswith("mcp__")] + ["Skill", "Agent"],
        allowed_tools=config.ALLOWED_TOOLS + ["Agent"],
        agents=load_agents(),
        permission_mode="dontAsk",
        mcp_servers={**mcp_from_file(), "kuro": calc.SERVER},
        include_partial_messages=True,
    )


def cli_kind() -> str | None:
    """"codex"/"agy" nếu AI đã chọn chạy bằng chương trình riêng của hãng, không qua Claude Code."""
    return (config.PROVIDERS.get(config.PROVIDER) or {}).get("cli")


def skill_index() -> str:
    """Danh mục skill cho bộ não không tự nạp .claude/skills: tên, mô tả, đường dẫn để nó tự mở SKILL.md."""
    out = []
    for p in sorted((config.BRAIN / ".claude" / "skills").glob("*/SKILL.md")):
        raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
        try:
            meta = yaml.safe_load(raw.split("---\n", 2)[1]) if raw.startswith("---\n") else {}
        except (IndexError, yaml.YAMLError):
            meta = {}
        desc = str((meta or {}).get("description") or "").replace("\n", " ")[:220]
        out.append(f"- {p.parent.name}: {desc} (file: {p.relative_to(config.BRAIN).as_posix()})")
    return "\n".join(out)


def cli_prompt(text: str, first: bool) -> str:
    if not first:   # lượt sau nối tiếp hội thoại cũ, CLI đã giữ hướng dẫn của lượt đầu
        return f"(Bây giờ là {datetime.now():%H:%M %d/%m/%Y}.)\n\n{text}"
    if "Bash" in config.ALLOWED_TOOLS:
        calc_rule = ("Không có tool tinh_python: viết script Python vào thư mục tinh-toan/, chạy bằng shell, ghi đường "
                     "dẫn script vào câu trả lời.")
    else:   # đo thật: agy bị từ chối ghi file thì dừng lượt không trả lời; codex trên Windows chặn cả lệnh đọc
        calc_rule = ("Phiên này KHÔNG được ghi file và KHÔNG được chạy lệnh: thử là bị chặn và hỏng lượt trả lời. "
                     "Đọc file thì được nếu công cụ cho phép; không đọc được thì dựa vào mô tả skill ở trên. Phép tính "
                     "làm trực tiếp trong câu trả lời, ghi rõ \"(chưa kiểm bằng script)\" cạnh mỗi kết quả.")
    return (f"<huong_dan_kuro>\n{system_append()}\n\n## Skill ngành\nCâu hỏi chuyên môn: đọc file SKILL.md phù hợp "
            f"TRƯỚC khi trả lời rồi làm theo.\n{skill_index()}\n\n## Tính toán\n{calc_rule}\n</huong_dan_kuro>\n\n"
            "Câu hỏi của người dùng:\n" + text)


async def ping() -> dict:
    """Hỏi AI đã chọn một câu ngắn, không tool, để màn hình chọn AI báo kết nối được hay chưa."""
    if kind := cli_kind():
        text, err = "", ""
        try:
            async with asyncio.timeout(120):
                async for ev in cli_engines.run(kind, "Trả lời đúng một từ: OK", None):
                    text += ev["text"] if ev["type"] == "text" else ""
                    err = ev["text"] if ev["type"] == "error" else err
        except TimeoutError:
            err = f"Quá 120 giây không thấy trả lời. Thử mở PowerShell gõ `{kind}` xem đã đăng nhập chưa."
        return {"ok": bool(text) and not err, "text": text[:200], "error": err[:500]}
    opts = ClaudeAgentOptions(model=config.MODEL or None, env=config.provider_env(), max_turns=1, tools=[],
                              setting_sources=[], permission_mode="dontAsk", cwd=str(config.STATE))
    text, err = "", ""
    env = config.provider_env()
    url = env.get("ANTHROPIC_BASE_URL")
    if url:
        # Claude Code tự thử lại rất lâu khi máy chủ im lặng hoặc báo sai key (đã thử: treo đủ 90 giây với lỗi 401),
        # nên gõ cửa trước. Model giả "kuro-kiem-tra" để không tốn token: key đúng thì máy chủ chỉ chê model.
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.post(url.rstrip("/") + "/v1/messages", json={
                    "model": "kuro-kiem-tra", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]},
                    headers={"Authorization": f"Bearer {env['ANTHROPIC_AUTH_TOKEN']}",
                             "x-api-key": env["ANTHROPIC_AUTH_TOKEN"], "anthropic-version": "2023-06-01"})
        except httpx.HTTPError:
            return {"ok": False, "text": "", "error": f"Không kết nối được tới {url}. Kiểm tra mạng, địa chỉ, "
                                                      "hoặc Ollama đã mở chưa."}
        if r.status_code in (401, 403):
            return {"ok": False, "text": "", "error": f"Máy chủ từ chối key (lỗi {r.status_code}): {r.text[:200]}"}
    try:
        async with asyncio.timeout(90):
            async for m in query(prompt="Trả lời đúng một từ: OK", options=opts):
                if isinstance(m, ResultMessage):
                    text = m.result or ""
                    if m.is_error:
                        err = text or "; ".join(map(str, m.errors or [])) or m.subtype
    except TimeoutError:
        err = "Quá 90 giây không thấy trả lời. Kiểm tra mạng, địa chỉ máy chủ, hoặc Ollama đã chạy chưa."
    except Exception as e:  # chưa cài Claude Code, sai địa chỉ...
        err = f"{type(e).__name__}: {e}"
    return {"ok": bool(text) and not err, "text": text[:200], "error": err[:500]}


async def run_turn(prompt: str, claude_id: str | None = None):
    """Sinh sự kiện của một lượt; sự kiện final mang thêm claude_id để lượt sau nối tiếp."""
    # claude_id của bộ não CLI có tiền tố "codex:"/"agy:"; đổi AI giữa chừng thì bắt đầu hội thoại mới.
    if kind := cli_kind():
        resume = claude_id[len(kind) + 1:] if claude_id and claude_id.startswith(kind + ":") else None
        async for ev in cli_engines.run(kind, cli_prompt(prompt, resume is None), resume):
            yield ev
        return
    if claude_id and ":" in claude_id:
        claude_id = None
    try:
        async for m in query(prompt=prompt, options=options(claude_id)):
            if isinstance(m, StreamEvent):
                ev = m.event
                if m.parent_tool_use_id is None and ev.get("type") == "content_block_delta" \
                        and ev.get("delta", {}).get("type") == "text_delta":
                    yield {"type": "text", "text": ev["delta"]["text"]}
            elif isinstance(m, AssistantMessage) and m.parent_tool_use_id is None:
                for b in m.content:
                    if isinstance(b, ToolUseBlock):
                        yield {"type": "tool", "name": b.name, "input": b.input}
            elif isinstance(m, ResultMessage):
                if m.is_error:
                    yield {"type": "error", "text": m.result or "; ".join(map(str, m.errors or [])) or m.subtype}
                yield {"type": "final", "text": m.result or "", "claude_id": m.session_id,
                       "cost": m.total_cost_usd}
    except Exception as e:  # CLI chưa cài, chưa đăng nhập, mất mạng...
        yield {"type": "error", "text": f"{type(e).__name__}: {e}"}


async def chat(sid: str, text: str, emit=None) -> str:
    """Một lượt hoàn chỉnh: lưu câu hỏi, chạy, đẩy sự kiện qua emit (nếu có), lưu câu trả lời."""
    store.ensure(sid, title=text)
    store.add(sid, "user", text)
    shown, final = [], ""
    async for ev in run_turn(text, (store.get(sid) or {}).get("claude_id")):
        if ev["type"] == "text":
            shown.append(ev["text"])
        elif ev["type"] == "error":
            shown.append(f"\n\n[Lỗi] {ev['text']}")
        elif ev["type"] == "final":
            final = ev["text"]
            if ev.get("claude_id"):
                store.set_claude_id(sid, ev["claude_id"])
        if emit:
            await emit({k: v for k, v in ev.items() if k != "claude_id"})
    answer = "".join(shown) or final
    store.add(sid, "assistant", answer)
    return answer
