"""Chạy một lượt chat qua Claude Code (claude-agent-sdk), dùng chung cho web, Telegram và nhắc hẹn.

Luồng sự kiện gửi cho giao diện:
  {"type": "text", "text"}           đoạn chữ đang stream
  {"type": "tool", "name", "input"}  Claude vừa gọi một tool
  {"type": "final", "text", "cost"}  hết lượt
  {"type": "error", "text"}
"""
import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path

import httpx
import yaml
from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, ResultMessage,
                              StreamEvent, ToolUseBlock, query)

import calc
import kho
import cli_engines
import dien_hoa
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


GROUPS_FILE = config.STATE / "groups.json"


def get_groups_config() -> dict:
    if GROUPS_FILE.is_file():
        try:
            return json.loads(GROUPS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_groups_config(cfg: dict):
    GROUPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    GROUPS_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


WORKSPACES_FILE = config.STATE / "workspaces.json"


def get_workspaces_config() -> dict:
    if WORKSPACES_FILE.is_file():
        try:
            return json.loads(WORKSPACES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_workspaces_config(cfg: dict):
    WORKSPACES_FILE.parent.mkdir(parents=True, exist_ok=True)
    WORKSPACES_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def get_default_workspace() -> Path:
    default_dir = config.ROOT / "projects" / "DuAn_KhoiTao"
    if not default_dir.is_dir():
        default_dir.mkdir(parents=True, exist_ok=True)
        readme = default_dir / "README.md"
        if not readme.exists():
            readme.write_text(
                "# DỰ ÁN KHỞI TẠO\n\nĐây là thư mục làm việc của dự án. Bạn có thể lưu bản vẽ, hồ sơ thiết kế, bảng tính Excel, tài liệu QA/QC tại đây để Kuro và các Agent phân tích.",
                encoding="utf-8"
            )
    return default_dir


def active_workspace_dir() -> Path:
    cfg = get_workspaces_config()
    act = (cfg.get("active") or "").strip()
    if act and Path(act).is_dir():
        return Path(act).resolve()
    def_ws = get_default_workspace()
    save_workspaces_config({
        "active": str(def_ws.resolve()),
        "recent": [
            {
                "name": def_ws.name,
                "path": str(def_ws.resolve()),
                "last_opened": int(datetime.now().timestamp())
            }
        ]
    })
    return def_ws.resolve()


def agent_persona(slug: str) -> tuple[dict, str]:
    """Lấy metadata và nội dung hướng dẫn của agent từ file markdown hoặc nhóm điều phối."""
    if not slug or slug == "kuro-core":
        return {"name": "Kuro Core", "role": "Trợ lý hệ thống kỹ sư hạ tầng"}, ""

    # Nếu là Agent Điều phối Tổng của một Nhóm
    if slug.startswith("group:"):
        group_name = slug[6:].strip()
        cfg = get_groups_config()
        grp_data = cfg.get(group_name) or {}
        workflow = (grp_data.get("workflow") or "").strip()
        role = (grp_data.get("role") or "").strip() or f"Agent điều phối tổng nhóm {group_name}"

        # Tìm các agent thành viên con trong nhóm
        all_agents = list_agents_info()
        member_slugs = [a["slug"] for a in all_agents if a.get("group") == group_name and not a["slug"].startswith("group:")]

        meta = {
            "name": f"Agent Tổng - {group_name}",
            "slug": slug,
            "role": role,
            "group": group_name,
            "workflow": workflow,
            "members": member_slugs,
            "is_group_lead": True
        }
        body = f"""Bạn là **Agent Điều phối Tổng** (Lead Coordinator) của nhóm chuyên môn **{group_name}**.
Trách nhiệm của bạn là nhận bài toán tổng thể từ kỹ sư hạ tầng, vận hành theo quy trình (workflow) dưới đây để chỉ huy và phối hợp nhịp nhàng các cộng sự trong nhóm.

### QUY TRÌNH PHỐI HỢP & WORKFLOW ĐIỀU PHỐI CỦA NHÓM:
{workflow or "(Chưa có quy trình cụ thể, hãy tự động phối hợp các chuyên môn con phù hợp)"}
"""
        return meta, body

    for d in (config.BRAIN / "agents", config.ROOT / "agents"):
        p = d / f"{slug}.md"
        if p.is_file():
            raw = p.read_text(encoding="utf-8").replace("\r\n", "\n")
            if raw.startswith("---\n"):
                try:
                    _, fm, body = raw.split("---\n", 2)
                    return yaml.safe_load(fm) or {}, body.strip()
                except Exception:
                    pass
            return {}, raw.strip()
    return {}, ""


def list_agents_info() -> list[dict]:
    """Danh sách tất cả agent cho giao diện web (Kuro Core + các kỹ sư chuyên môn)."""
    agents = [{
        "slug": "kuro-core",
        "name": "Kuro Core",
        "role": "Trợ lý kỹ sư hạ tầng: điều phối chung, kết nối dữ liệu và giải quyết tổng thể dự án.",
        "group": "Hệ thống",
        "badge": "Hệ thống",
        "icon": "kuro",
        "members": [],
        "is_team": False,
        "is_core": True,
        "pinned": True,
    }]
    seen = {"kuro-core"}
    for d in (config.BRAIN / "agents", config.ROOT / "agents"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            slug = p.stem
            if slug in seen:
                continue
            meta, _ = agent_persona(slug)
            name = meta.get("name") or slug
            role = meta.get("role") or ""
            group = meta.get("group") or "Chuyên môn"
            skills = meta.get("skills") or []
            members = meta.get("members") or []
            is_team = bool(members)
            seen.add(slug)
            agents.append({
                "slug": slug,
                "name": name,
                "role": role,
                "group": group,
                "badge": "Điều phối" if is_team else group,
                "skills": skills,
                "members": members,
                "is_team": is_team,
                "icon": "team" if is_team else slug,
                "is_core": False,
                "pinned": True,
            })
    return agents


def agent_prompt_block(agent: str) -> str:
    """Xây dựng nội dung vai trò chuyên môn, hỗ trợ gộp tri thức các agent con nếu là agent điều phối/nhóm."""
    if not agent or agent == "kuro-core":
        return ""
    meta, body = agent_persona(agent)
    if not meta and not body:
        return ""
    name = meta.get("name") or agent
    role = meta.get("role") or ""
    members = meta.get("members") or []

    lines = [f"\n\n## VAI TRÒ CHUYÊN MÔN CỦA BẠN TRONG PHIÊN NÀY\nBạn đang đảm nhiệm vai trò: **{name}**\nChức trách: {role}\nQuy trình thực hiện:\n{body}"]

    if members:
        lines.append("\n\n### DANH SÁCH CÁC CỘNG SỰ & QUY TRÌNH BẠN ĐIỀU PHỐI:")
        lines.append("Bản chất bạn là một Agent Điều phối (Team Lead). Bạn chỉ huy và kết hợp toàn diện năng lực của các Agent thành viên sau:")
        for idx, m_slug in enumerate(members, 1):
            m_meta, m_body = agent_persona(m_slug)
            m_name = m_meta.get("name") or m_slug
            m_role = m_meta.get("role") or ""
            lines.append(f"\n{idx}. **{m_name}** ({m_role}):\n{m_body}")
        lines.append("\n*Yêu cầu điều phối:* Khi nhận nhiệm vụ từ người dùng, hãy áp dụng quy trình và góc nhìn kỹ thuật của từng thành viên liên quan, kiểm tra chéo và đưa ra giải pháp toàn diện, chặt chẽ!")

    return "\n".join(lines)


def system_append() -> str:
    """Kernel (CLAUDE.md gốc) + ký ức + giờ hiện tại, nối vào sau prompt mặc định của Claude Code."""
    parts = []
    for p in (config.ROOT / "CLAUDE.md", config.BRAIN / "memory" / "MEMORY.md"):
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8"))
    parts.append(f"Bây giờ là {datetime.now():%H:%M %d/%m/%Y} (giờ máy).")
    return "\n\n".join(parts)


def options(claude_id: str | None, agent: str = "kuro-core", cwd: str | None = None, model: str | None = None) -> ClaudeAgentOptions:
    extra = agent_prompt_block(agent)
    ws_path = cwd or str(active_workspace_dir())
    ws_note = (
        f"\n\n## THƯ MỤC DỰ ÁN ĐANG LÀM VIỆC (WORKSPACE)\n"
        f"Đường dẫn thư mục dự án trên máy người dùng: `{ws_path}`.\n"
        f"- NƠI LƯU KẾT QUẢ BẮT BUỘC: Mọi tệp tin kết quả (.xlsx, .html, .docx, .py, script, báo cáo...) do AI tạo ra PHẢI lưu vào thư mục dự án này (`{ws_path}`).\n"
        f"- NGUYÊN TẮC HỎI VỊ TRÍ LƯU: Nếu trong thư mục dự án chưa có quy định cấu trúc thư mục lưu cụ thể thì BẮT BUỘC hỏi lại người dùng xem muốn lưu vào thư mục/vị trí nào, tuyệt đối không tự ý lưu vào các vị trí chưa được phép.\n"
        f"- KHO DỮ LIỆU CÔNG TY (UNC): Các kho mạng chung như `\\\\phuongthanhtranconsin.data.com\\12.KỸ THUẬT THI CÔNG` và các kho hợp đồng CHỈ là nơi lưu trữ, tra cứu hồ sơ (READ-ONLY). TUYỆT ĐỐI KHÔNG tự ý lưu kết quả, không tạo tệp tạm hay ghi đè vào kho mạng chung này (trừ khi có chỉ đạo rõ ràng từ người dùng)."
    )
    chosen_model = model or config.MODEL or None
    return ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code", "append": system_append() + extra + ws_note},
        cwd=ws_path,
        model=chosen_model,
        env=config.provider_env(chosen_model),
        resume=claude_id,
        skills="all",
        setting_sources=["project"],      # chỉ đọc cấu hình trong brain, KHÔNG nạp ~/.claude của máy
        # Hai lớp chặn: `tools` gỡ hẳn tool built-in ngoài danh sách (dontAsk một mình vẫn cho chạy
        # lệnh Bash "chỉ đọc" như echo - đã thử thật); dontAsk từ chối MCP tool chưa được liệt kê.
        tools=[t for t in config.ALLOWED_TOOLS if not t.startswith("mcp__")] + ["Skill", "Agent"],
        allowed_tools=config.ALLOWED_TOOLS + ["Agent"] + calc.KHO_TOOLS,   # kho luôn bật (specs/002); mã vẫn phải duyệt
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


def cli_prompt(text: str, first: bool, agent: str = "kuro-core", ws_dir: str | None = None) -> str:
    ws_path = ws_dir or str(active_workspace_dir())
    ws_note = (
        f"\n\n## THƯ MỤC DỰ ÁN ĐANG LÀM VIỆC (WORKSPACE)\n"
        f"Thư mục hiện hành trên máy người dùng: `{ws_path}`.\n"
        f"- NƠI LƯU KẾT QUẢ BẮT BUỘC: Mọi file kết quả (.xlsx, .html, .docx, script tính toán...) PHẢI lưu vào thư mục dự án hiện hành `{ws_path}`.\n"
        f"- NGUYÊN TẮC HỎI VỊ TRÍ LƯU: Nếu trong thư mục dự án chưa có quy tắc phân loại thư mục lưu, hãy hỏi lại người dùng vị trí muốn lưu, không tự ý tạo thư mục hay lưu vào vị trí chưa được phép.\n"
        f"- KHO DỮ LIỆU CÔNG TY (UNC): Kho `\\\\phuongthanhtranconsin.data.com\\...` CHỈ ĐỂ TRA CỨU HỒ SƠ (READ-ONLY), không lưu kết quả vào đây trừ khi người dùng yêu cầu đích danh."
    )
    if not first:   # lượt sau nối tiếp hội thoại cũ, CLI đã giữ hướng dẫn của lượt đầu
        return f"(Bây giờ là {datetime.now():%H:%M %d/%m/%Y}. Thư mục làm việc: {ws_path})\n\n{text}"
    can_shell = "Bash" in config.ALLOWED_TOOLS
    can_write = "Write" in config.ALLOWED_TOOLS or "Edit" in config.ALLOWED_TOOLS
    if can_shell:
        calc_rule = ("Viết script Python vào thư mục tinh-toan/ hoặc thư mục dự án, chạy bằng shell hoặc python để tính toán chính xác, tạo tệp HTML/Excel và ghi đường "
                     "dẫn script/tệp vào câu trả lời.")
    elif can_write:
        calc_rule = ("Phiên này được phép tạo và ghi đè tệp tin (.html, .xlsx, .md...) trực tiếp vào thư mục dự án. "
                     "Khi người dùng yêu cầu xuất file báo cáo, hãy dùng công cụ ghi tệp tạo ra file thật trên ổ cứng.")
    else:   # Cả shell lẫn write đều tắt
        calc_rule = ("Phiên này chỉ đọc, không ghi tệp và không chạy lệnh shell. "
                     "Đọc file thì được nếu công cụ cho phép; không đọc được thì dựa vào mô tả skill ở trên. Phép tính "
                     "làm trực tiếp trong câu trả lời, ghi rõ \"(chưa kiểm bằng script)\" cạnh mỗi kết quả.")
    agent_info = agent_prompt_block(agent)
    return (f"<huong_dan_kuro>\n{system_append()}{agent_info}{ws_note}\n\n## Skill ngành\nCâu hỏi chuyên môn: đọc file SKILL.md phù hợp "
            f"TRƯỚC khi trả lời rồi làm theo.\n{skill_index()}\n\n## Kho skill (specs/002)\nSkill trên không phủ việc thì tra "
            f"kho 230 skill (DDC xây dựng, archify, anatomy...): mục lục `{kho.MUC_LUC}` (id, ten, mo_ta tiếng Anh, "
            f"duong_dan), đọc SKILL.md ở `{config.ROOT}/<duong_dan>`. Ghi tên skill và repo đã dùng. CHỈ chạy mã của "
            f"skill có trong `{kho.SO_GOC}`. Dữ liệu giá CWICR cấm dùng thương mại: báo trước khi dùng.\n\n"
            f"## Tính toán\n{calc_rule}\n</huong_dan_kuro>\n\n"
            "Câu hỏi của người dùng:\n" + text)


async def mot_lan(prompt: str, timeout: int = 120) -> tuple[str, str]:
    """Hỏi AI đang chọn một câu, không tool, không lưu phiên; trả (chữ, lỗi). Dùng cho ping và dịch prompt diễn hoạ."""
    text, err = "", ""
    try:
        async with asyncio.timeout(timeout):
            if kind := cli_kind():
                async for ev in cli_engines.run(kind, prompt, None):
                    text += ev["text"] if ev["type"] == "text" else ""
                    err = ev["text"] if ev["type"] == "error" else err
            else:
                opts = ClaudeAgentOptions(model=config.MODEL or None, env=config.provider_env(), max_turns=1, tools=[],
                                          setting_sources=[], permission_mode="dontAsk", cwd=str(config.STATE))
                async for m in query(prompt=prompt, options=opts):
                    if isinstance(m, ResultMessage):
                        text = m.result or ""
                        if m.is_error:
                            err = text or "; ".join(map(str, m.errors or [])) or m.subtype
    except TimeoutError:
        err = f"Quá {timeout} giây không thấy trả lời."
    except Exception as e:  # chưa cài CLI, sai địa chỉ...
        err = f"{type(e).__name__}: {e}"
    return text, err


async def ping() -> dict:
    """Hỏi AI đã chọn một câu ngắn, không tool, để màn hình chọn AI báo kết nối được hay chưa."""
    if kind := cli_kind():
        text, err = await mot_lan("Trả lời đúng một từ: OK", 120)
        if err.startswith("Quá"):
            err += f" Thử mở PowerShell gõ `{kind}` xem đã đăng nhập chưa."
        return {"ok": bool(text) and not err, "text": text[:200], "error": loi_tieng_viet(err)[:600]}
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
    return {"ok": bool(text) and not err, "text": text[:200], "error": loi_tieng_viet(err)[:600]}


def split_conv(stored: str | None) -> tuple[str | None, str | None]:
    """Mã hội thoại lưu dạng "<id AI>:<mã>". Mã trần (bản cũ) là của claude; tiền tố cũ codex/agy đổi về id AI."""
    if not stored:
        return None, None
    if ":" not in stored:
        return "claude", stored
    owner, conv = stored.split(":", 1)
    return {"codex": "chatgpt", "agy": "antigravity"}.get(owner, owner), conv


# Dấu hiệu lỗi "model không tồn tại" đo được (Claude Code: "There's an issue with the selected model ... may not exist").
_MODEL_LOI = ("issue with the selected model", "may not exist", "model_not_found", "model not found", "invalid model")


def loi_tieng_viet(err: str) -> str:
    if config.MODEL and any(k in err.lower() for k in _MODEL_LOI):
        p = config.PROVIDERS.get(config.PROVIDER or "claude", {})
        return f'Model "{config.MODEL}" không có ở {p.get("ten")}. {p.get("goi_y", "")} (Lỗi gốc: {err})'
    return err


async def run_turn(prompt: str, claude_id: str | None = None, agent: str = "kuro-core", cwd: str | None = None, model: str | None = None):
    """Sinh sự kiện của một lượt; sự kiện final mang claude_id "<id AI>:<mã>" để lượt sau nối tiếp."""
    cur = config.PROVIDER or "claude"
    owner, conv = split_conv(claude_id)
    if owner and owner != cur:   # mỗi hãng giữ hội thoại riêng: AI mới không nối được mạch cũ (specs/001 FR-007)
        yield {"type": "text", "text": f"_(Đã đổi sang {config.PROVIDERS.get(cur, {}).get('ten', cur)}: "
                                       "AI mới chưa biết các câu trước trong phiên này.)_\n\n"}
    async for ev in _engine_turn(prompt, conv if owner == cur else None, cur, agent=agent, cwd=cwd, model=model):
        if ev["type"] == "error":
            ev = {**ev, "text": loi_tieng_viet(ev["text"])}
        elif ev["type"] == "final" and ev.get("claude_id"):
            ev = {**ev, "claude_id": f"{cur}:{ev['claude_id']}"}
        yield ev


async def _engine_turn(prompt: str, resume: str | None, cur: str, agent: str = "kuro-core", cwd: str | None = None, model: str | None = None):
    ws_path = cwd or str(active_workspace_dir())
    if kind := cli_kind():
        async for ev in cli_engines.run(kind, cli_prompt(prompt, resume is None, agent=agent, ws_dir=ws_path), resume, cwd=ws_path, model=model):
            yield ev
        return
    try:
        async for m in query(prompt=prompt, options=options(resume, agent=agent, cwd=ws_path, model=model)):
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


DICH_PROMPT = ("Viết MỘT prompt tiếng Anh (dưới 60 từ) cho Stable Diffusion SDXL để diễn hoạ ảnh thật công trình xây "
               "dựng từ mô tả dưới đây: loại công trình, vật liệu, màu, cảnh quan, ánh sáng, thời điểm. Chỉ trả đúng "
               "prompt trên một dòng, không giải thích. Mô tả trống thì viết prompt chung cho công trình hoàn thiện.\n"
               "Mô tả: {mo_ta}")


async def dien_hoa_anh(anh: Path, mo_ta: str, che_do: str, ws_path: str) -> list[Path]:
    """Dịch mô tả sang prompt SDXL bằng AI đang chọn (lỗi thì dùng nguyên văn), vẽ, chép ảnh vào dự án."""
    prompt_en, err = await mot_lan(DICH_PROMPT.format(mo_ta=mo_ta), 120)
    prompt_en = (prompt_en.strip().splitlines() or [""])[0].strip(' "') if not err else ""
    ra = await asyncio.to_thread(dien_hoa.ve, anh, prompt_en or mo_ta or "finished building exterior", che_do,
                                 Path(ws_path) / "dien-hoa")
    for p in ra:   # bản sao trong .attachments để khung chat hiện ảnh qua /api/attachments
        att = Path(ws_path) / ".attachments"
        att.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, att / p.name)
    return ra


async def _dien_hoa_turn(job: dict, ws_path: str, emit) -> str:
    async def say(t: str):
        if emit:
            await emit({"type": "text", "text": t})
    if loi := dien_hoa.thieu():
        await say(loi)
        if emit:
            await emit({"type": "final", "text": ""})
        return loi
    ten = {"net": "bản vẽ nét", "anh": "ảnh chụp hiện trạng", "3d": "ảnh mô hình 3D/BIM"}[job["che_do"]]
    head = (f"Đang diễn hoạ {dien_hoa.SO_ANH} phương án từ {ten} `{job['anh'].name}` "
            "(ComfyUI + RealVisXL + ControlNet Union SDXL, lần đầu khoảng 1-3 phút)...\n\n")
    await say(head)
    try:
        ra = await dien_hoa_anh(job["anh"], job["mo_ta"], job["che_do"], ws_path)
        body = "".join(f"**Phương án {i}**\n\n![Phương án {i}](/api/attachments/{p.name})\n\n`{p}`\n\n"
                       for i, p in enumerate(ra, 1)) or "ComfyUI không trả ảnh nào."
    except Exception as e:  # thiếu model, ComfyUI lỗi...: báo rõ, không im lặng
        body = f"[Lỗi diễn hoạ] {e}"
    await say(body)
    if emit:
        await emit({"type": "final", "text": ""})
    return head + body


async def chat(sid: str, text: str, agent: str = "kuro-core", emit=None, workspace: str | None = None, model: str | None = None) -> str:
    """Một lượt hoàn chỉnh: lưu câu hỏi, chạy, đẩy sự kiện qua emit (nếu có), lưu câu trả lời."""
    ws_path = workspace or str(active_workspace_dir())
    sess = store.get(sid) or {}
    chosen_model = model or sess.get("model") or ""
    store.ensure(sid, title=text, agent=agent, workspace=ws_path, model=chosen_model)
    if chosen_model and chosen_model != sess.get("model"):
        store.set_model(sid, chosen_model)
    store.add(sid, "user", text)
    if job := dien_hoa.yeu_cau(text):   # "diễn hoạ" + ảnh đính kèm: Kuro tự làm, dùng được với mọi AI (specs/003)
        answer = await _dien_hoa_turn(job, ws_path, emit)
        store.add(sid, "assistant", answer)
        return answer
    shown, final = [], ""
    async for ev in run_turn(text, sess.get("claude_id"), agent=agent, cwd=ws_path, model=chosen_model):
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
