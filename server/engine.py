"""Chạy một lượt chat qua Claude Code (claude-agent-sdk), dùng chung cho web, Telegram và nhắc hẹn.

Luồng sự kiện gửi cho giao diện:
  {"type": "text", "text"}           đoạn chữ đang stream
  {"type": "tool", "name", "input"}  Claude vừa gọi một tool
  {"type": "final", "text", "cost"}  hết lượt
  {"type": "error", "text"}
"""
import asyncio
import json
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

import httpx
import yaml
from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, HookMatcher,
                              ResultMessage, StreamEvent, ToolUseBlock, query)

import calc
import kho
import cli_engines
import dien_hoa
import config
import store
import workspace_rules


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
        "provider": "",
        "model": "",
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
                "provider": (meta.get("provider") or "").strip(),
                "model": (meta.get("model") or "").strip(),
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


# Dùng chung cho cả phiên Claude Code lẫn CLI (codex/agy)
KHO_MANG_CAM_XOA = (
    "- CẤM XÓA TRÊN KHO MẠNG, KỂ CẢ KHI NGƯỜI DÙNG YÊU CẦU: không xóa bất kỳ tệp/thư mục nào trên "
    "`\\\\phuongthanhtranconsin.data.com\\...` (kể cả qua ổ map như `Y:\\`) bằng mọi cách (lệnh shell, script, công cụ tệp). "
    "Việc xóa do người dùng tự làm bằng tay: từ chối và ghi rõ đường dẫn để người dùng tự xóa.\n"
    "- KHÔNG TỰ ĐỘNG TẠO TỆP TRÊN KHO MẠNG: chỉ thêm/tạo tệp khi người dùng yêu cầu đích danh việc thêm/tạo tệp đó, "
    "đúng tệp và đúng vị trí được yêu cầu."
)


async def chan_xoa_kho_mang(inp, tool_use_id, ctx):
    """PreToolUse (lớp chặn cứng sau lời dặn trên): chặn lệnh shell, mã tính toán, script viết ra có xóa/di chuyển tệp trên kho mạng."""
    ten, vao = inp.get("tool_name", ""), inp.get("tool_input") or {}
    if ten in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        if not str(vao.get("file_path") or vao.get("notebook_path") or "").lower().endswith(config.DUOI_MA):
            return {}   # tệp văn bản/báo cáo: chỉ chặn script, tránh chặn nhầm báo cáo có chữ "move"/"delete"
    elif ten not in ("Bash", "PowerShell") and not ten.startswith("mcp__kuro__"):
        return {}
    text = "\n".join(str(v) for k, v in vao.items() if k != "old_string")
    if config.xoa_tren_kho_mang(text):
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                       "permissionDecisionReason": config.TU_CHOI_XOA_KHO}}
    return {}


# Cách Claude Code Desktop làm việc với tệp: nhận ĐƯỜNG DẪN, tự mở bằng Read theo từng đoạn, không nuốt cả tệp
DOC_TEP_LON = (
    "\n\n## ĐỌC TỆP LỚN (hồ sơ, bản vẽ, bảng tính nặng)\n"
    "- Tệp đính kèm chỉ là đường dẫn. Tự mở bằng Read từ đường dẫn đó, không nhờ người dùng dán nội dung.\n"
    "- Chưa rõ cỡ tệp thì kiểm tra trước (Bash: `python -c \"import os,sys;print(os.path.getsize(sys.argv[1]))\" <tệp>`), "
    "không đọc nguyên một tệp hàng chục MB.\n"
    "- PDF trên 20 MB hoặc trên 20 trang: Read với `pages` (tối đa 20 trang mỗi lần). Xem trang đầu/mục lục/khung tên "
    "trước, chọn đúng trang cần, đọc tiếp từng đoạn. Cần text hoặc bảng cả tệp thì viết script `pdfplumber` chạy bằng Bash, "
    "lưu kết quả vào thư mục dự án rồi đọc kết quả.\n"
    "- Tệp text/CSV lớn: Read với `offset`/`limit` hoặc Grep. Excel lớn: `openpyxl` (read_only) qua script. DXF: `ezdxf`. "
    "IFC: `ifcopenshell`. DWG: cần chuyển sang DXF trước, nói rõ cho người dùng nếu máy chưa có bộ chuyển đổi.\n"
    "- Không đọc được tệp thì nói rõ lý do và hướng xử lý, không trả lời như thể đã đọc."
)


# Claude Code chỉ tự nạp skill ở .claude/skills của thư mục làm việc (= dự án), không phải brain: phải chỉ đường cho nó.
SKILL_NGANH = ("\n\n## Skill ngành của Kuro\nViệc chuyên môn: dùng Read mở đúng file SKILL.md phù hợp dưới đây TRƯỚC khi làm, rồi làm theo. "
               "Chỉ mở skill khi việc thật sự liên quan; mô tả của skill nói rõ khi nào dùng.\n{skills}")


# Mức suy nghĩ trên giao diện (high/standard/off) -> từng AI. Đo thật 2026-11:
# - Claude Code: effort low..max + thinking disabled, mỗi model hỗ trợ khác nhau (get_server_info báo supportedEffortLevels,
#   supportsThinkingOff). Haiku và model ngoài họ Claude không có effort: bỏ qua.
# - Codex: -c model_reasoning_effort (low..ultra), không có "tắt" nên Tắt = low.
# - Agy: --effort xung đột với model có hậu tố (báo ERROR); mức suy nghĩ nằm trong tên model -low/-medium/-high
#   (flash-low 230 token suy nghĩ, flash-high 638): đổi hậu tố cho đúng mức, Tắt = low.
THINK_LEVELS = ("high", "standard", "off")
_CAPS = {"t": 0.0, "models": []}
_AGY_SUFFIX = re.compile(r"^(.*)-(low|medium|high|xhigh)$")


async def claude_models_caps() -> list[dict]:
    """Khả năng suy nghĩ từng model do chính Claude Code báo, cache 1 giờ."""
    if _CAPS["models"] and time.time() - _CAPS["t"] < 3600:
        return _CAPS["models"]
    try:
        async with ClaudeSDKClient(ClaudeAgentOptions(setting_sources=[], cwd=str(config.STATE))) as c:
            info = await c.get_server_info()
        _CAPS.update(t=time.time(), models=info.get("models") or [])
    except Exception as e:
        print(f"[thinking] không hỏi được Claude Code: {e}")
    return _CAPS["models"]


def claude_cap(models: list[dict], model: str | None) -> dict | None:
    m = (model or "").lower()
    if not m:
        return models[0] if models else None
    # Ưu tiên khớp chính xác (value, rồi tên model đã giải) để claude-opus-5-5 không bị nhầm sang claude-opus-5
    for hit in (lambda c: m == c["value"].lower(), lambda c: m == (c.get("resolvedModel") or "").lower(),
                lambda c: m.startswith(c["value"].lower())):
        for c in models:
            if hit(c):
                return c
    return None


def thinking_options(cap: dict | None, level: str | None) -> dict:
    """Cao = effort high, Tiêu chuẩn = medium, Tắt = tắt hẳn suy nghĩ (model không tắt được thì effort low)."""
    if not cap or not cap.get("supportsEffort") or level not in THINK_LEVELS:
        return {}
    levels = cap.get("supportedEffortLevels") or []
    if level == "off":
        if cap.get("supportsThinkingOff"):
            return {"thinking": {"type": "disabled"}}
        return {"effort": "low"} if "low" in levels else {}
    eff = "high" if level == "high" else "medium"
    return {"effort": eff} if eff in levels else {}


async def thinking_support(provider: str, model: str | None) -> dict:
    """Model này chỉnh được mức suy nghĩ không, và "Tắt" nghĩa là gì: disable (tắt hẳn) hoặc low (mức thấp nhất)."""
    prov = provider or config.PROVIDER or "claude"
    mod = model or config.get_provider_model(prov) or ""
    if kind := cli_kind(prov):
        if kind == "agy":
            m = _AGY_SUFFIX.match(mod)
            if not m:
                return {"supported": False, "off": None}
            ids = {x["id"] for x in await cli_engines.models("agy")}
            ok = any(f"{m.group(1)}-{lv}" in ids for lv in ("high", "medium"))
            return {"supported": ok, "off": "low" if ok else None}
        return {"supported": True, "off": "low"}
    cap = claude_cap(await claude_models_caps(), mod)
    if not cap or not cap.get("supportsEffort"):
        return {"supported": False, "off": None}
    return {"supported": True, "off": "disable" if cap.get("supportsThinkingOff") else "low"}


def options(claude_id: str | None, agent: str = "kuro-core", cwd: str | None = None, model: str | None = None, provider: str | None = None,
            think: dict | None = None) -> ClaudeAgentOptions:
    extra = agent_prompt_block(agent)
    ws_path = cwd or str(active_workspace_dir())
    ws_note = workspace_rules.build_workspace_rules_prompt(Path(ws_path), get_workspaces_config()) + f"\n{KHO_MANG_CAM_XOA}"
    prov = provider or config.PROVIDER or "claude"
    chosen_model = model or config.get_provider_model(prov) or None
    return ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code", "append": system_append() + extra + ws_note + DOC_TEP_LON + SKILL_NGANH.format(skills=skill_index())},
        cwd=ws_path,
        model=chosen_model,
        env=config.provider_env(chosen_model, provider=prov),
        resume=claude_id,
        skills="all",
        setting_sources=["project"],      # chỉ đọc cấu hình trong brain, KHÔNG nạp ~/.claude của máy
        # Hai lớp chặn: `tools` gỡ hẳn tool built-in ngoài danh sách (dontAsk một mình vẫn cho chạy
        # lệnh Bash "chỉ đọc" như echo - đã thử thật); dontAsk từ chối MCP tool chưa được liệt kê.
        tools=[t for t in config.ALLOWED_TOOLS if not t.startswith("mcp__")] + ["Skill", "Agent"],
        allowed_tools=config.ALLOWED_TOOLS + ["Agent"] + calc.KHO_TOOLS,   # kho luôn bật (specs/002); mã vẫn phải duyệt
        agents=load_agents(),
        permission_mode="dontAsk",
        hooks={"PreToolUse": [HookMatcher(hooks=[chan_xoa_kho_mang])]},
        mcp_servers={**mcp_from_file(), "kuro": calc.SERVER},
        include_partial_messages=True,
        # Mặc định 1 MB: đọc tệp đính kèm lớn (PDF, Excel, txt) sinh một dòng JSON vượt mức là báo CLIJSONDecodeError.
        # Read của Claude Code tối đa ~20 MB PDF (~27 MB base64): 256 MB dư nhiều, chỉ tốn RAM khi có dòng lớn thật.
        max_buffer_size=256 * 1024 * 1024,
        **(think or {}),
    )


def cli_kind(provider: str | None = None) -> str | None:
    """"codex"/"agy" nếu AI đã chọn chạy bằng chương trình riêng của hãng, không qua Claude Code."""
    prov = provider or config.PROVIDER
    return (config.PROVIDERS.get(prov) or {}).get("cli")


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
        out.append(f"- {p.parent.name}: {desc} (file: {p.as_posix()})")   # đường dẫn tuyệt đối: cwd của AI là thư mục dự án, không phải brain
    return "\n".join(out)


def cli_prompt(text: str, first: bool, agent: str = "kuro-core", ws_dir: str | None = None) -> str:
    ws_path = ws_dir or str(active_workspace_dir())
    ws_cfg = get_workspaces_config()
    co_quy_tac = workspace_rules.inspect_workspace_rules(Path(ws_path), ws_cfg)["has_rules"]
    ws_rules = workspace_rules.build_workspace_rules_prompt(Path(ws_path), ws_cfg) + f"\n{KHO_MANG_CAM_XOA}"
    ws_note = ws_rules + DOC_TEP_LON
    if not first:   # lượt sau nối tiếp hội thoại cũ, CLI đã giữ hướng dẫn của lượt đầu
        # quy tắc thư mục dự án + kho mạng gửi lại MỖI lượt: dự án có thể vừa đổi quy tắc, đổi thư mục, hoặc hội
        # thoại bắt đầu trước khi có quy tắc (đường Claude đã gửi lại cả system prompt mỗi lượt)
        return (f"(Bây giờ là {datetime.now():%H:%M %d/%m/%Y}.)\n<huong_dan_kuro>{ws_rules}\n</huong_dan_kuro>\n\n"
                f"Câu hỏi của người dùng:\n{text}")
    can_shell = "Bash" in config.ALLOWED_TOOLS
    can_write = "Write" in config.ALLOWED_TOOLS or "Edit" in config.ALLOWED_TOOLS
    if can_shell:
        if co_quy_tac:
            calc_rule = ("Viết script Python, chạy bằng shell hoặc python để tính toán chính xác. Script, file trung gian và sản phẩm "
                         f"hoàn thiện lưu đúng nơi quy định trong `{workspace_rules.RULES_FILE}` ở trên; thông báo rõ tên file cùng đường dẫn kết quả.")
        else:
            calc_rule = ("Viết script Python vào thư mục dự án, chạy bằng shell hoặc python để tính toán chính xác, tạo tệp HTML/Excel và ghi đường "
                         "dẫn script/tệp vào câu trả lời.")
    elif can_write:
        if co_quy_tac:
            calc_rule = ("Phiên này được phép tạo và ghi tệp tin trực tiếp vào thư mục dự án, lưu đúng nơi quy định trong "
                         f"`{workspace_rules.RULES_FILE}` ở trên.")
        else:
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


async def mot_lan(prompt: str, timeout: int = 120, provider: str | None = None, model: str | None = None) -> tuple[str, str]:
    """Hỏi AI một câu, không tool, không lưu phiên; trả (chữ, lỗi). Dùng cho ping và dịch prompt diễn hoạ."""
    prov = provider or config.PROVIDER or "claude"
    eff_model = model or config.get_provider_model(prov) or None
    text, err = "", ""
    try:
        async with asyncio.timeout(timeout):
            if kind := cli_kind(prov):
                async for ev in cli_engines.run(kind, prompt, None, model=eff_model, provider=prov):
                    text += ev["text"] if ev["type"] == "text" else ""
                    err = ev["text"] if ev["type"] == "error" else err
            else:
                opts = ClaudeAgentOptions(model=eff_model, env=config.provider_env(eff_model, provider=prov),
                                          max_turns=1, tools=[], setting_sources=[], permission_mode="dontAsk",
                                          cwd=str(config.STATE))
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


async def ping(provider: str | None = None, model: str | None = None) -> dict:
    """Hỏi AI một câu ngắn, không tool, để kiểm tra kết nối độc lập theo từng hãng."""
    prov = provider or config.PROVIDER or "claude"
    eff_model = model if model is not None else (config.get_provider_model(prov) or None)
    if kind := cli_kind(prov):
        text, err = await mot_lan("Trả lời đúng một từ: OK", 120, provider=prov, model=eff_model)
        if err.startswith("Quá"):
            err += f" Thử mở PowerShell gõ `{kind}` xem đã đăng nhập chưa."
        return {"ok": bool(text) and not err, "text": text[:200],
                "error": loi_tieng_viet(err, provider=prov, model=eff_model)[:600], "provider": prov}
    env = config.provider_env(eff_model, provider=prov)
    opts = ClaudeAgentOptions(model=eff_model or None, env=env, max_turns=1, tools=[],
                              setting_sources=[], permission_mode="dontAsk", cwd=str(config.STATE))
    text, err = "", ""
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
            return {"ok": False, "text": "", "provider": prov,
                    "error": f"Không kết nối được tới {url}. Kiểm tra mạng, địa chỉ, hoặc Ollama đã mở chưa."}
        if r.status_code in (401, 403):
            return {"ok": False, "text": "", "provider": prov,
                    "error": f"Máy chủ từ chối key (lỗi {r.status_code}): {r.text[:200]}"}
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
    return {"ok": bool(text) and not err, "text": text[:200],
            "error": loi_tieng_viet(err, provider=prov, model=eff_model)[:600], "provider": prov}


def split_conv(stored: str | None) -> tuple[str | None, str | None]:
    """Mã hội thoại lưu dạng "<id AI>:<mã>". Mã trần (bản cũ) là của claude; tiền tố cũ codex/agy đổi về id AI."""
    return store.parse_conv_id(stored)


# Dấu hiệu lỗi "model không tồn tại" đo được (Claude Code: "There's an issue with the selected model ... may not exist").
_MODEL_LOI = ("issue with the selected model", "may not exist", "model_not_found", "model not found", "invalid model")


def loi_tieng_viet(err: str, provider: str | None = None, model: str | None = None) -> str:
    prov = provider or config.PROVIDER or "claude"
    eff_model = model if model is not None else config.get_provider_model(prov)
    if eff_model and any(k in err.lower() for k in _MODEL_LOI):
        p = config.PROVIDERS.get(prov, {})
        return f'Model "{eff_model}" không có ở {p.get("ten")}. {p.get("goi_y", "")} (Lỗi gốc: {err})'
    return err


def build_handoff_context(messages: list[dict], max_msgs: int = 8, max_chars: int = 3600) -> tuple[str, int]:
    """Tạo khối ngữ cảnh bàn giao gọn từ lịch sử phiên khi chuyển sang nhà cung cấp AI khác.

    Giữ tổng độ dài nhỏ (<= 3600 ký tự) để không vượt giới hạn tham số dòng lệnh Windows khi gọi CLI `agy -p`.
    """
    if not messages:
        return "", 0
    recent = messages[-max_msgs:]
    lines = []
    used = 0
    count = 0
    for m in recent:
        txt = (m.get("text") or "").strip()
        if not txt:
            continue
        # Bỏ dòng thông báo chuyển AI hệ thống ở đầu tin assistant nếu có
        if txt.startswith("_(Đã ") and "\n\n" in txt:
            txt = txt.split("\n\n", 1)[1].strip()
        if not txt:
            continue
        role_lbl = "Kỹ sư" if m.get("role") == "user" else "Kuro"
        snippet = txt[:550] + ("..." if len(txt) > 550 else "")
        entry = f"- {role_lbl}: {snippet}"
        if used + len(entry) > max_chars and lines:
            break
        lines.append(entry)
        used += len(entry) + 1
        count += 1
    if not lines:
        return "", 0
    block = (
        "<ngu_canh_ban_giao>\n"
        "Phiên chat này trước đó chạy bằng một nhà cung cấp AI khác. Dưới đây là diễn biến gần nhất để bạn tiếp nối mạch công việc tự nhiên, không hỏi lại những gì đã trao đổi:\n"
        + "\n".join(lines)
        + "\n</ngu_canh_ban_giao>\n\n"
    )
    return block, count


async def run_turn(prompt: str, claude_id: str | None = None, agent: str = "kuro-core", cwd: str | None = None,
                   model: str | None = None, provider: str | None = None, conv_ids: dict[str, str] | None = None,
                   handoff_messages: list[dict] | None = None, thinking: str | None = None):
    """Sinh sự kiện của một lượt; sự kiện final mang claude_id "<id AI>:<mã>" để lượt sau nối tiếp."""
    cur = provider or config.PROVIDER or "claude"
    owner, conv = split_conv(claude_id)
    conv_map = dict(conv_ids or {})
    if owner and conv and owner not in conv_map:
        conv_map[owner] = conv

    resume_id = conv_map.get(cur)
    switched = bool(owner and owner != cur)
    effective_prompt = prompt

    if switched:
        prov_name = config.PROVIDERS.get(cur, {}).get("ten", cur)
        if handoff_messages:
            handoff_block, n_msgs = build_handoff_context(handoff_messages, max_msgs=4 if resume_id else 8)
            if handoff_block:
                effective_prompt = handoff_block + prompt
                if resume_id:
                    yield {"type": "text", "text": f"_(Đã chuyển sang {prov_name} - tiếp nối mạch cũ kèm cập nhật {n_msgs} tin gần nhất.)_\n\n"}
                else:
                    yield {"type": "text", "text": f"_(Đã chuyển sang {prov_name} - đã bàn giao ngữ cảnh {n_msgs} tin gần nhất.)_\n\n"}
            else:
                yield {"type": "text", "text": f"_(Đã đổi sang {prov_name}: AI mới chưa biết các câu trước trong phiên này.)_\n\n"}
        else:
            # Giữ nguyên thông báo chuẩn specs/001 FR-007 khi gọi trực tiếp không truyền lịch sử bàn giao
            yield {"type": "text", "text": f"_(Đã đổi sang {prov_name}: AI mới chưa biết các câu trước trong phiên này.)_\n\n"}

    async for ev in _engine_turn(effective_prompt, resume_id, cur, agent=agent, cwd=cwd, model=model, thinking=thinking):
        if ev["type"] == "error":
            ev = {**ev, "text": loi_tieng_viet(ev["text"], provider=cur, model=model)}
        elif ev["type"] == "final" and ev.get("claude_id"):
            ev = {**ev, "claude_id": f"{cur}:{ev['claude_id']}"}
        yield ev


async def _engine_turn(prompt: str, resume: str | None, cur: str, agent: str = "kuro-core", cwd: str | None = None, model: str | None = None,
                       thinking: str | None = None):
    ws_path = cwd or str(active_workspace_dir())
    if kind := cli_kind(cur):
        eff_model = model
        if kind == "agy" and thinking in THINK_LEVELS:
            eff_model = await cli_engines.agy_model_for_thinking(model or config.get_provider_model(cur), thinking)
        async for ev in cli_engines.run(kind, cli_prompt(prompt, resume is None, agent=agent, ws_dir=ws_path),
                                        resume, cwd=ws_path, model=eff_model, provider=cur, thinking=thinking):
            yield ev
        return
    try:
        think = {}
        if thinking in THINK_LEVELS:
            think = thinking_options(claude_cap(await claude_models_caps(), model or config.get_provider_model(cur)), thinking)
        async for m in query(prompt=prompt, options=options(resume, agent=agent, cwd=ws_path, model=model, provider=cur, think=think)):
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
    ws_p = Path(ws_path)
    out_dir = (ws_p / "03_KET_QUA" / "dien-hoa") if (ws_p / "03_KET_QUA").is_dir() else (ws_p / "dien-hoa")
    ra = await asyncio.to_thread(dien_hoa.ve, anh, prompt_en or mo_ta or "finished building exterior", che_do, out_dir)
    for p in ra:   # bản sao trong .attachments để khung chat hiện ảnh qua /api/attachments
        att = workspace_rules.attachments_dir(ws_p)
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


async def chat(sid: str, text: str, agent: str = "kuro-core", emit=None, workspace: str | None = None,
               model: str | None = None, provider: str | None = None, thinking: str | None = None) -> str:
    """Một lượt hoàn chỉnh: lưu câu hỏi, chạy theo provider riêng của phiên, đẩy sự kiện qua emit, lưu câu trả lời."""
    ws_path = workspace or str(active_workspace_dir())
    sess = store.get(sid) or {}
    agent_meta, _ = agent_persona(agent)
    agent_prov = (agent_meta.get("provider") or "").strip()
    agent_model = (agent_meta.get("model") or "").strip()

    prev_provider = store.session_provider(sess)
    chosen_provider = (provider or "").strip() or prev_provider or agent_prov or (config.PROVIDER or "claude")
    switched_provider = bool(prev_provider and prev_provider != chosen_provider)

    if model is not None:
        chosen_model = model.strip()
    elif switched_provider:
        # Chuyển sang hãng khác mà không chỉ định model cụ thể: dùng mặc định hãng mới, không mang model hãng cũ sang
        chosen_model = ""
    else:
        chosen_model = sess.get("model") or (agent_model if chosen_provider == agent_prov else "") or ""

    prev_msgs = store.messages(sid) if sess else []
    conv_ids = store.get_conv_ids(sess)

    store.ensure(sid, title=text, agent=agent, workspace=ws_path, model=chosen_model, provider=chosen_provider)
    if chosen_provider != (sess.get("provider") or "") or chosen_model != (sess.get("model") or ""):
        store.set_model(sid, chosen_model, provider=chosen_provider)
    store.add(sid, "user", text, provider=chosen_provider)

    if job := dien_hoa.yeu_cau(text):   # "diễn hoạ" + ảnh đính kèm: Kuro tự làm, dùng được với mọi AI (specs/003)
        answer = await _dien_hoa_turn(job, ws_path, emit)
        store.add(sid, "assistant", answer, provider=chosen_provider)
        return answer

    shown, final = [], ""
    async for ev in run_turn(
        text,
        sess.get("claude_id"),
        agent=agent,
        cwd=ws_path,
        model=chosen_model or None,
        provider=chosen_provider,
        conv_ids=conv_ids,
        handoff_messages=prev_msgs if prev_msgs else None,
        thinking=thinking,
    ):
        if ev["type"] == "text":
            shown.append(ev["text"])
        elif ev["type"] == "error":
            shown.append(f"\n\n[Lỗi] {ev['text']}")
        elif ev["type"] == "usage" and isinstance(ev.get("usage"), dict):
            try:
                store.set_usage(sid, chosen_provider, ev["usage"])
            except Exception:
                pass
        elif ev["type"] == "final":
            final = ev["text"]
            if ev.get("claude_id"):
                owner_id, raw_id = split_conv(ev["claude_id"])
                if raw_id:
                    store.set_conv_id(sid, owner_id or chosen_provider, raw_id)
            usage_payload = ev.get("usage") if isinstance(ev.get("usage"), dict) else None
            if ev.get("init_tools"):
                usage_payload = dict(usage_payload or {})
                usage_payload["init_tools"] = ev["init_tools"]
            if usage_payload:
                try:
                    store.set_usage(sid, chosen_provider, usage_payload)
                except Exception:
                    pass
        if emit:
            await emit({k: v for k, v in ev.items() if k not in ("claude_id", "init_tools")})
    answer = "".join(shown) or final
    store.add(sid, "assistant", answer, provider=chosen_provider)
    return answer
