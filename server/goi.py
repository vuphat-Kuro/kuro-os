"""Quản lý Plugins (Gói tiện ích tùy chọn) của Kuro:
- Plugin tích hợp sẵn nằm trong `goi/<id>/`, CHỈ cài vào brain khi người dùng yêu cầu.
- Plugin bên ngoài cài từ file `.zip`/`.kuro-plugin` hoặc thư mục trên máy tính, lưu tách biệt ở `state/plugins/<id>/`
  (không bị ghi đè khi cập nhật mã nguồn Kuro).

Dòng lệnh:
    python server/goi.py list | cai <id> | go <id>
"""
from datetime import datetime
import importlib.util
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path

import yaml

import config

GOI = config.ROOT / "goi"

MAX_ZIP_BYTES = 100 * 1024 * 1024          # tối đa 100 MB cho tệp gói plugin nén
MAX_UNCOMPRESSED_BYTES = 200 * 1024 * 1024 # tối đa 200 MB sau khi giải nén (chống zip bomb)
MAX_ZIP_FILES = 2000

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_AGENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.md$")
_PIP_SPEC_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-\[\],<>=!~ ]{0,127}$")
_MCP_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".pytest_cache", "__MACOSX"}


def ngoai_dir() -> Path:
    """Thư mục lưu gói plugin cài từ bên ngoài (nằm trong state/ nên sống qua các bản cập nhật Kuro)."""
    return config.STATE / "plugins"


def _slugify(raw: str) -> str:
    txt = unicodedata.normalize("NFKD", (raw or "").strip())
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = txt.replace("đ", "d").replace("Đ", "d").lower()
    txt = re.sub(r"[^a-z0-9_-]+", "-", txt).strip("-_")
    txt = re.sub(r"-{2,}", "-", txt)
    return txt[:64]


def _validate_id(gid: str, label: str = "Mã plugin") -> str:
    gid = (gid or "").strip().lower()
    if not _ID_RE.fullmatch(gid):
        raise ValueError(f"{label} '{gid}' không hợp lệ (chỉ gồm chữ thường a-z, số 0-9, '-' hoặc '_', tối đa 64 ký tự).")
    return gid


def _validate_pip_specs(specs: list) -> list[str]:
    out: list[str] = []
    if not specs:
        return out
    if not isinstance(specs, list):
        raise ValueError("Trường 'pip' trong manifest phải là danh sách chuỗi.")
    for item in specs:
        s = str(item).strip()
        if not s:
            continue
        if s.startswith("-") or "://" in s or "\\" in s or "/" in s or ".." in s:
            raise ValueError(f"Gói pip không hợp lệ hoặc không được phép: '{s}'")
        if not _PIP_SPEC_RE.fullmatch(s):
            raise ValueError(f"Tên gói pip không hợp lệ: '{s}'")
        out.append(s)
    return out


def _validate_mcp(raw) -> dict:
    if not raw:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("Trường 'mcp' trong manifest phải là đối tượng JSON (map tên server -> cấu hình).")
    servers = raw.get("mcpServers") if "mcpServers" in raw and isinstance(raw.get("mcpServers"), dict) else raw
    clean: dict = {}
    for name, cfg in servers.items():
        if not isinstance(name, str) or not _MCP_NAME_RE.fullmatch(name):
            raise ValueError(f"Tên MCP server không hợp lệ: '{name}'")
        if not isinstance(cfg, dict) or not (cfg.get("command") or cfg.get("url")):
            raise ValueError(f"Cấu hình MCP '{name}' phải có 'command' hoặc 'url'.")
        clean[name] = cfg
    return clean


def _parse_skill_frontmatter(skill_md: Path) -> tuple[str, str]:
    """Đọc name và description từ YAML frontmatter đầu SKILL.md (nếu có)."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")[:8192]
    except OSError:
        return "", ""
    m = re.match(r"^---\s*\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return "", ""
    try:
        meta = yaml.safe_load(m.group(1)) or {}
        if isinstance(meta, dict):
            return str(meta.get("name") or "").strip(), str(meta.get("description") or "").strip()
    except Exception:
        pass
    return "", ""


def _read_manifest_file(p: Path) -> dict:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"Không đọc được tệp cấu hình plugin ({p.name}): {e}")
    if not isinstance(data, dict):
        raise ValueError(f"Tệp cấu hình plugin ({p.name}) phải là JSON object.")
    return data


def _normalize_manifest(raw: dict, gid: str, base_dir: Path, nguon: str) -> dict:
    """Chuẩn hóa manifest từ goi.json / plugin.json sang định dạng thống nhất."""
    skills_raw = raw.get("skills")
    skills: list[str] = []
    if isinstance(skills_raw, list):
        for s in skills_raw:
            s_str = str(s).strip()
            if s_str and s_str not in skills:
                skills.append(s_str)
    single_skill = str(raw.get("skill") or "").strip()
    if single_skill and single_skill not in skills:
        skills.insert(0, single_skill)

    agents_raw = raw.get("agents")
    agents: list[str] = []
    if isinstance(agents_raw, list):
        for a in agents_raw:
            a_str = Path(str(a).strip()).name
            if a_str and a_str not in agents:
                agents.append(a_str)
    elif (base_dir / "agents").is_dir():
        agents = sorted(p.name for p in (base_dir / "agents").glob("*.md") if p.is_file())

    pip_list = [str(x).strip() for x in (raw.get("pip") or []) if str(x).strip()]
    imp_list = [str(x).strip() for x in (raw.get("import") or []) if str(x).strip()]
    mcp_cfg = raw.get("mcp") if isinstance(raw.get("mcp"), dict) else {}

    ten = str(raw.get("ten") or raw.get("name") or gid).strip()
    mo_ta = str(raw.get("mo_ta") or raw.get("description") or "").strip()
    phien_ban = str(raw.get("phien_ban") or raw.get("version") or "1.0.0").strip()
    tac_gia = str(raw.get("tac_gia") or raw.get("author") or ("Kuro OS" if nguon == "builtin" else "Bên ngoài")).strip()

    return {
        "id": gid,
        "ten": ten,
        "mo_ta": mo_ta,
        "phien_ban": phien_ban,
        "tac_gia": tac_gia,
        "nguon": nguon,
        "nguon_tep": str(raw.get("nguon_tep") or "").strip(),
        "skill": skills[0] if skills else "",
        "skills": skills,
        "agents": agents,
        "pip": pip_list,
        "import": imp_list,
        "mcp": mcp_cfg,
        "kiem_tra": str(raw.get("kiem_tra") or "").strip(),
        "mcp_tu_khoa": [str(x) for x in raw.get("mcp_tu_khoa") or [] if str(x).strip()],   # có khóa này: MCP chỉ nạp khi câu hỏi nhắc từ khóa
        "mcp_cai": bool(raw.get("mcp_cai")),   # script kiem_tra có hành động mcp-install / mcp-uninstall (cài thành phần MCP riêng)
    }


def _find_plugin(gid: str) -> tuple[Path, dict, str]:
    """Tìm plugin theo id: ưu tiên gói tích hợp sẵn trong goi/, sau đó gói ngoài trong state/plugins/."""
    gid = (gid or "").strip()
    if not gid or "/" in gid or "\\" in gid or ".." in gid:
        raise ValueError(f"Mã plugin không hợp lệ: '{gid}'")
    builtin_f = GOI / gid / "goi.json"
    if builtin_f.is_file():
        return GOI / gid, _normalize_manifest(_read_manifest_file(builtin_f), gid, GOI / gid, "builtin"), "builtin"
    ext_f = ngoai_dir() / gid / "goi.json"
    if ext_f.is_file():
        return ngoai_dir() / gid, _normalize_manifest(_read_manifest_file(ext_f), gid, ngoai_dir() / gid, "external"), "external"
    co_san = sorted(p.parent.name for p in GOI.glob("*/goi.json"))
    if ngoai_dir().is_dir():
        co_san += [p.parent.name for p in sorted(ngoai_dir().glob("*/goi.json")) if p.parent.name not in co_san]
    raise ValueError(f"Không có gói '{gid}'. Gói hiện có: {', '.join(co_san) or 'chưa có'}")


def _manifest(gid: str) -> dict:
    _, m, _ = _find_plugin(gid)
    return m


def da_cai() -> dict:
    f = config.STATE / "goi-cai.json"
    if not f.is_file():
        return {}
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def _luu(st: dict) -> None:
    config.STATE.mkdir(parents=True, exist_ok=True)
    (config.STATE / "goi-cai.json").write_text(json.dumps(st, indent=1, ensure_ascii=False), encoding="utf-8")


def _xoa_van_tay(keys: list[str]) -> None:
    """Xóa dấu vân tay cũ trong state/goi-kem.json khi gỡ/cập nhật plugin để lần cài lại luôn chép bản mới."""
    log = config.STATE / "goi-kem.json"
    if not log.is_file() or not keys:
        return
    try:
        seen = json.loads(log.read_text(encoding="utf-8"))
    except ValueError:
        return
    changed = False
    for k in keys:
        if k in seen:
            seen.pop(k, None)
            changed = True
    if changed:
        log.write_text(json.dumps(seen, indent=1, ensure_ascii=False), encoding="utf-8")


def _doc_mcp() -> dict:
    if not config.MCP_FILE.is_file():
        return {"mcpServers": {}}
    try:
        data = json.loads(config.MCP_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            if not isinstance(data.get("mcpServers"), dict):
                data["mcpServers"] = {}
            return data
    except ValueError:
        pass
    return {"mcpServers": {}}


def _luu_mcp(data: dict) -> None:
    config.STATE.mkdir(parents=True, exist_ok=True)
    config.MCP_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _kiem_tra_thieu_pip(imp_list: list[str]) -> list[str]:
    thieu = []
    for mod in imp_list:
        try:
            if importlib.util.find_spec(mod) is None:
                thieu.append(mod)
        except (ImportError, ValueError, ModuleNotFoundError):
            thieu.append(mod)
    return thieu


_SETUP_ACTIONS = {"status", "install", "uninstall", "fonts-install", "open"}


def _setup_script(base: Path, m: dict, nguon: str) -> tuple[Path, list[str]] | None:
    """Tìm script cài đặt / kiểm tra trên máy đi kèm gói TÍCH HỢP SẴN (khóa `kiem_tra` trong goi.json).

    Chỉ chạy cho gói tích hợp sẵn trong `goi/` (không chạy tự động mã của gói ngoài khi chỉ mở trang Cài đặt).
    """
    cmd_str = (m.get("kiem_tra") or "").strip()
    if nguon != "builtin" or not cmd_str:
        return None
    try:
        parts = shlex.split(cmd_str, posix=True)
    except ValueError:
        return None
    if not parts or not parts[0].lower().endswith(".py"):
        return None
    rel = parts[0]
    base_res = base.resolve()
    candidates = []
    if m.get("skill"):
        candidates.append((base / m["skill"] / rel).resolve())
    candidates.append((base / rel).resolve())
    for cand in candidates:
        if cand.is_file() and cand.is_relative_to(base_res):
            return cand, parts[1:]
    return None


def _run_setup_cmd(script: Path, args: list[str], timeout: int = 25) -> tuple[int, dict]:
    try:
        r = subprocess.run(
            [_python(), "-X", "utf8", str(script), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        return 1, {"ok": False, "trang_thai": "loi", "thong_bao": "Quá thời gian phản hồi khi kiểm tra/cài đặt trên máy."}
    except OSError as e:
        return 1, {"ok": False, "trang_thai": "loi", "thong_bao": f"Không chạy được trình cài đặt: {e}"}

    raw_out = (r.stdout or "").strip()
    if raw_out:
        try:
            data = json.loads(raw_out)
            if isinstance(data, dict):
                return r.returncode, data
        except ValueError:
            pass
    err_msg = (r.stderr or raw_out or "Không đọc được kết quả JSON từ trình cài đặt.").strip().splitlines()[-1]
    return r.returncode or 1, {"ok": False, "trang_thai": "loi", "thong_bao": err_msg}


def kiem_tra_may(gid: str) -> dict | None:
    """Chạy lệnh kiểm tra trạng thái trên máy tính (chỉ đọc) cho gói tích hợp sẵn có khóa `kiem_tra`."""
    try:
        base, m, nguon = _find_plugin(gid)
    except ValueError:
        return None
    found = _setup_script(base, m, nguon)
    if not found:
        return None
    script, default_args = found
    _, data = _run_setup_cmd(script, default_args or ["status"], timeout=20)
    return data


def cai_dat_may(gid: str, hanh_dong: str) -> dict:
    """Chạy trình cài đặt/gỡ/cài font trên máy tính cho gói tích hợp sẵn (vd PKTTC TextHub vào AutoCAD)."""
    action = (hanh_dong or "").strip()
    if action not in _SETUP_ACTIONS:
        raise ValueError(f"Hành động không hợp lệ: '{action}'. Chỉ hỗ trợ: {', '.join(sorted(_SETUP_ACTIONS))}.")
    base, m, nguon = _find_plugin(gid)
    found = _setup_script(base, m, nguon)
    if not found:
        raise ValueError(f"Plugin '{gid}' không có trình cài đặt phần mềm đi kèm.")
    script, _ = found
    timeout = 25 if action == "status" else 180
    rc, data = _run_setup_cmd(script, [action], timeout=timeout)
    ok = bool(data.get("ok", rc == 0))
    msg = str(data.get("thong_bao") or "").strip()

    # Khi cài phần mềm trên máy thành công -> tự động cài luôn skill vào Kuro Brain nếu chưa cài
    if action == "install" and ok and gid not in da_cai():
        try:
            cai(gid)
            msg = (msg + " Đã đồng thời kích hoạt skill trong Kuro.").strip()
        except ValueError as e:
            msg = (msg + f" (Lưu ý: chưa nạp được skill vào Kuro: {e})").strip()

    return {
        "ok": ok,
        "id": gid,
        "action": action,
        "message": msg or ("Hoàn tất." if ok else "Thao tác không thành công."),
        "ket_qua": data,
    }


def danh_sach(kiem_tra: bool = False) -> dict:
    """Trả về danh sách đầy đủ plugin tích hợp sẵn và plugin cài từ bên ngoài cho giao diện Cài đặt."""
    st = da_cai()
    items: list[dict] = []
    seen_ids: set[str] = set()

    def _collect(root: Path, nguon: str) -> None:
        if not root.is_dir():
            return
        for p in sorted(root.glob("*/goi.json")):
            gid = p.parent.name
            if gid in seen_ids:
                continue
            try:
                m = _normalize_manifest(_read_manifest_file(p), gid, p.parent, nguon)
            except ValueError:
                continue
            seen_ids.add(gid)
            inst = st.get(gid)
            is_installed = gid in st
            thieu = _kiem_tra_thieu_pip(m["import"])
            setup_info = _setup_script(p.parent, m, nguon)
            may_status = None
            if kiem_tra and setup_info:
                _, may_status = _run_setup_cmd(setup_info[0], setup_info[1] or ["status"], timeout=20)
            items.append({
                "id": gid,
                "ten": m["ten"],
                "mo_ta": m["mo_ta"],
                "phien_ban": m["phien_ban"],
                "tac_gia": m["tac_gia"],
                "nguon": nguon,
                "nguon_tep": m["nguon_tep"],
                "da_cai": is_installed,
                "cai_luc": (inst or {}).get("cai_luc", "") if isinstance(inst, dict) else "",
                "skills": m["skills"],
                "agents": m["agents"],
                "mcp": sorted(m["mcp"].keys()),
                "mcp_da_cai": _mcp_da_dang_ky(m),
                "pip": m["pip"],
                "thieu_pip": thieu,
                "co_cai_dat_may": bool(setup_info),
                "trang_thai_may": may_status,
            })

    _collect(GOI, "builtin")
    _collect(ngoai_dir(), "external")

    builtin = [x for x in items if x["nguon"] == "builtin"]
    external = [x for x in items if x["nguon"] == "external"]
    return {
        "plugins": items,
        "tong_tich_hop": len(builtin),
        "da_cai_tich_hop": sum(1 for x in builtin if x["da_cai"]),
        "tong_ben_ngoai": len(external),
        "da_cai_ben_ngoai": sum(1 for x in external if x["da_cai"]),
    }


def liet_ke() -> str:
    ds = danh_sach()["plugins"]
    rows = []
    for p in ds:
        tag = "ĐÃ CÀI" if p["da_cai"] else "chưa cài"
        src = " · gói ngoài" if p["nguon"] == "external" else ""
        rows.append(f"- {p['id']}: {p['ten']} [{tag}{src}]")
    return "\n".join(rows) or "Chưa có gói tiện ích nào."


def _python() -> str:
    exe = Path(sys.executable)   # pythonw không có console để pip in ra
    return str(exe.with_name("python.exe")) if exe.name.lower() == "pythonw.exe" and exe.with_name("python.exe").is_file() else str(exe)


def _cai_pip(pip_specs: list[str], imp_list: list[str]) -> None:
    pip_specs = _validate_pip_specs(pip_specs)
    if not pip_specs:
        return
    # Nếu có khai báo `import` thì chỉ chạy pip khi còn thiếu ít nhất 1 module; nếu không khai báo `import` thì chạy pip luôn.
    if imp_list and not _kiem_tra_thieu_pip(imp_list):
        return
    r = subprocess.run(
        [_python(), "-m", "pip", "install", *pip_specs],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if r.returncode:
        err_line = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or ["lỗi pip"])[-1]
        raise ValueError("Không cài được thư viện Python (kiểm tra kết nối mạng): " + err_line)


def _cfg_ghi(m: dict, srv: str, cfg: dict) -> dict:
    """Cấu hình MCP ghi vào state/mcp.json; thêm khóa `_kuro` (engine.mcp_cho_luot) khi gói khai `mcp_tu_khoa`."""
    out = _thay_giu_cho(cfg)
    if m.get("mcp_tu_khoa"):
        out["_kuro"] = {"khi_can": True, "tu_khoa": [srv, *m["mcp_tu_khoa"]]}
    return out


def _thay_giu_cho(v):
    """Thay ${KURO_ROOT} và ${KURO_PYTHON} trong cấu hình MCP bằng đường dẫn thật trên máy này."""
    if isinstance(v, str):
        return v.replace("${KURO_ROOT}", config.ROOT.as_posix()).replace("${KURO_PYTHON}", _python())
    if isinstance(v, list):
        return [_thay_giu_cho(x) for x in v]
    if isinstance(v, dict):
        return {k: _thay_giu_cho(x) for k, x in v.items()}
    return v


def _mcp_da_dang_ky(m: dict) -> bool:
    ten = list(m["mcp"])
    have = _doc_mcp()["mcpServers"]
    return bool(ten) and all(t in have for t in ten)


def mcp_bat(gid: str, bat: bool) -> str:
    """Thêm/bớt RIÊNG khối MCP của plugin trong state/mcp.json (không đụng skill). Có hiệu lực cho phiên chat mới."""
    base, m, nguon = _find_plugin(gid)
    cfg = _validate_mcp(m["mcp"])
    if not cfg:
        raise ValueError(f"Plugin '{gid}' không có MCP.")
    if m.get("mcp_cai"):   # thành phần MCP cần cài riêng (vd cầu nối npm): chạy script trước khi ghi cấu hình
        found = _setup_script(base, m, nguon)
        if not found:
            raise ValueError(f"Plugin '{gid}' khai mcp_cai nhưng thiếu script kiem_tra.")
        rc, res = _run_setup_cmd(found[0], ["mcp-install" if bat else "mcp-uninstall"], timeout=170)
        if rc != 0 or not res.get("ok", True):
            raise ValueError(str(res.get("thong_bao") or "Cài thành phần MCP không thành công."))
    data = _doc_mcp()
    owned = set((da_cai().get(gid) or {}).get("mcp") or [])
    for srv, c in cfg.items():
        want = _cfg_ghi(m, srv, c)
        if bat:
            if srv in data["mcpServers"] and data["mcpServers"][srv] != want and srv not in owned:
                raise ValueError(f"MCP '{srv}' đã có trong state/mcp.json với cấu hình khác (không ghi đè).")
            data["mcpServers"][srv] = want
        else:
            data["mcpServers"].pop(srv, None)
    _luu_mcp(data)
    return f"Đã {'cài' if bat else 'gỡ'} MCP {', '.join(cfg)}. Áp dụng cho phiên chat mới."


def cai(gid: str) -> str:
    base, m, nguon = _find_plugin(gid)
    pip_specs = _validate_pip_specs(m["pip"])
    mcp_cfg = _validate_mcp(m["mcp"])

    # Kiểm tra trùng MCP server với cấu hình có sẵn của người dùng / plugin khác
    st = da_cai()
    owned_mcp = set((st.get(gid) or {}).get("mcp") or [])
    if mcp_cfg:
        mcp_data = _doc_mcp()
        for srv in mcp_cfg:
            if srv in mcp_data["mcpServers"] and srv not in owned_mcp and mcp_data["mcpServers"][srv] != _cfg_ghi(m, srv, mcp_cfg[srv]):
                raise ValueError(f"MCP server '{srv}' đã tồn tại trong state/mcp.json (thuộc cấu hình khác).")

    _cai_pip(pip_specs, m["import"])

    if mcp_cfg:
        mcp_data = _doc_mcp()
        for srv, cfg in mcp_cfg.items():
            mcp_data["mcpServers"][srv] = _cfg_ghi(m, srv, cfg)
        _luu_mcp(mcp_data)

    st[gid] = {
        "skill": m["skills"][0] if m["skills"] else "",
        "skills": m["skills"],
        "agents": m["agents"],
        "mcp": sorted(mcp_cfg.keys()),
        "nguon": nguon,
        "cai_luc": datetime.now().isoformat(timespec="seconds"),
    }
    _luu(st)

    # Xóa dấu vân tay cũ của các skill/agent thuộc gói này để bảo đảm chép đủ phiên bản mới nhất
    _xoa_van_tay([f"{gid}/{s}" for s in m["skills"]] + [f"agents/{a}" for a in m["agents"]])
    config.sync_bundled()

    for s in m["skills"]:
        dst = config.BRAIN / ".claude" / "skills" / s
        if not (dst / "SKILL.md").is_file():
            raise ValueError(f"Chép skill '{s}' không thành (kiểm tra {dst})")
    for a in m["agents"]:
        dst_a = config.BRAIN / "agents" / a
        if not dst_a.is_file():
            raise ValueError(f"Chép agent '{a}' không thành (kiểm tra {dst_a})")

    parts = []
    if m["skills"]:
        parts.append("Skill " + ", ".join(f"`{s}`" for s in m["skills"]) + " tự nạp khi việc liên quan")
    if m["agents"]:
        parts.append(f"{len(m['agents'])} cộng sự (agent) mới")
    if mcp_cfg:
        mcp_tools = ", ".join(f"`mcp__{k}`" for k in sorted(mcp_cfg.keys()))
        parts.append(f"MCP {', '.join(sorted(mcp_cfg.keys()))} (nhớ thêm {mcp_tools} vào Tool được phép nếu cần)")
    detail = (". " + "; ".join(parts) + ".") if parts else "."
    return (f"Đã cài plugin '{gid}' ({m['ten']}){detail} "
            "Mở cuộc trò chuyện mới để AI nhận đầy đủ kỹ năng mới.")


def go(gid: str, xoa_ngoai: bool = True) -> str:
    gid = (gid or "").strip()
    st = da_cai()
    ext_path = ngoai_dir() / gid if gid and "/" not in gid and "\\" not in gid and ".." not in gid else None

    if gid not in st:
        if xoa_ngoai and ext_path and ext_path.is_dir():
            shutil.rmtree(ext_path, ignore_errors=True)
            return f"Đã xóa gói ngoài '{gid}'."
        return f"Gói '{gid}' chưa cài."

    entry = st.pop(gid)
    skills = entry.get("skills") or ([entry["skill"]] if entry.get("skill") else [])
    agents = entry.get("agents") or []
    mcp_names = entry.get("mcp") or []
    nguon = entry.get("nguon") or ("external" if (ext_path and ext_path.is_dir() and not (GOI / gid).is_dir()) else "builtin")

    for s in skills:
        if s:
            shutil.rmtree(config.BRAIN / ".claude" / "skills" / s, ignore_errors=True)
    for a in agents:
        if a:
            try:
                (config.BRAIN / "agents" / a).unlink(missing_ok=True)
            except OSError:
                pass
    if mcp_names and config.MCP_FILE.is_file():
        mcp_data = _doc_mcp()
        changed = False
        for srv in mcp_names:
            if srv in mcp_data["mcpServers"]:
                mcp_data["mcpServers"].pop(srv, None)
                changed = True
        if changed:
            _luu_mcp(mcp_data)

    _xoa_van_tay([f"{gid}/{s}" for s in skills] + [f"agents/{a}" for a in agents])
    _luu(st)

    if nguon == "external" and xoa_ngoai and ext_path and ext_path.is_dir():
        shutil.rmtree(ext_path, ignore_errors=True)
        return f"Đã gỡ và xóa gói ngoài '{gid}'. Thư viện pip giữ nguyên (không ảnh hưởng gì)."

    return f"Đã gỡ gói '{gid}'. Thư viện pip giữ nguyên (không ảnh hưởng gì)."


def _safe_extract_zip(data: bytes, dst_dir: Path) -> None:
    if len(data) > MAX_ZIP_BYTES:
        raise ValueError(f"Tệp gói plugin vượt quá giới hạn {MAX_ZIP_BYTES // (1024 * 1024)} MB.")
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise ValueError("Tệp không phải định dạng nén .zip hợp lệ.")
    with zf:
        infos = zf.infolist()
        if len(infos) > MAX_ZIP_FILES:
            raise ValueError(f"Gói plugin chứa quá nhiều tệp ({len(infos)} > {MAX_ZIP_FILES}).")
        total_size = 0
        base = dst_dir.resolve()
        for info in infos:
            name = info.filename.replace("\\", "/")
            if not name or name.startswith("__MACOSX/") or "/__MACOSX/" in name:
                continue
            # Chặn symlink trong file zip (Unix mode 0o120000)
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError(f"Gói plugin chứa liên kết tượng trưng (symlink) không được phép: {name}")
            if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
                raise ValueError(f"Đường dẫn không an toàn trong gói nén: {name}")
            parts = [pt for pt in name.split("/") if pt]
            if any(pt in (".", "..") for pt in parts) or any(pt in _SKIP_DIRS for pt in parts):
                if any(pt == ".." for pt in parts):
                    raise ValueError(f"Đường dẫn thoát thư mục (path traversal) trong gói nén: {name}")
                continue
            if total_size + info.file_size > MAX_UNCOMPRESSED_BYTES:
                raise ValueError(f"Dung lượng giải nén vượt giới hạn {MAX_UNCOMPRESSED_BYTES // (1024 * 1024)} MB.")
            target = (base / Path(*parts)).resolve()
            if not target.is_relative_to(base):
                raise ValueError(f"Đường dẫn không an toàn trong gói nén: {name}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as src_f, open(target, "wb") as out_f:
                    while True:
                        chunk = src_f.read(65536)
                        if not chunk:
                            break
                        total_size += len(chunk)
                        if total_size > MAX_UNCOMPRESSED_BYTES:
                            raise ValueError(f"Dung lượng giải nén vượt giới hạn {MAX_UNCOMPRESSED_BYTES // (1024 * 1024)} MB.")
                        out_f.write(chunk)


def _safe_copy_dir(src_dir: Path, dst_dir: Path) -> None:
    """Sao chép thư mục nguồn (chỉ đọc trên nguồn) sang thư mục tạm, chặn symlink thoát ra ngoài và giới hạn dung lượng."""
    src_base = src_dir.resolve()
    total_size = 0
    count = 0
    for cur, dirs, files in os.walk(src_base, followlinks=False):
        cur_p = Path(cur)
        # Lọc bỏ thư mục hệ thống / symlink
        kept_dirs = []
        for d in dirs:
            if d in _SKIP_DIRS:
                continue
            dp = cur_p / d
            if dp.is_symlink():
                raise ValueError(f"Thư mục nguồn chứa symlink không được phép: {d}")
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        rel_dir = cur_p.relative_to(src_base)
        (dst_dir / rel_dir).mkdir(parents=True, exist_ok=True)
        for fn in files:
            fp = cur_p / fn
            if fp.is_symlink():
                raise ValueError(f"Thư mục nguồn chứa symlink không được phép: {fn}")
            count += 1
            if count > MAX_ZIP_FILES:
                raise ValueError(f"Thư mục plugin chứa quá nhiều tệp (> {MAX_ZIP_FILES}).")
            total_size += fp.stat().st_size
            if total_size > MAX_UNCOMPRESSED_BYTES:
                raise ValueError(f"Dung lượng thư mục plugin vượt giới hạn {MAX_UNCOMPRESSED_BYTES // (1024 * 1024)} MB.")
            shutil.copy2(fp, dst_dir / rel_dir / fn)


def _unwrap_root(stage_dir: Path) -> Path:
    """Nếu file nén bọc tất cả trong 1 thư mục con duy nhất (kiểu GitHub zip), tự động đi vào thư mục đó."""
    cur = stage_dir
    for _ in range(3):
        if any((cur / f).is_file() for f in ("goi.json", "plugin.json", "SKILL.md")):
            break
        if (cur / ".claude-plugin" / "plugin.json").is_file() or (cur / "skills").is_dir():
            break
        visible = [p for p in cur.iterdir() if not p.name.startswith(".") and p.name not in _SKIP_DIRS]
        if len(visible) == 1 and visible[0].is_dir():
            cur = visible[0]
        else:
            break
    return cur


def _kiem_tra_xung_dot(gid: str, skill_names: list[str], agent_names: list[str], mcp_names: list[str]) -> None:
    if (GOI / gid / "goi.json").is_file():
        raise ValueError(f"Mã plugin '{gid}' trùng với plugin tích hợp sẵn của Kuro. Vui lòng đổi mã gói.")

    core_skills = {p.parent.name for p in (config.ROOT / "skills").glob("*/SKILL.md")}
    core_agents = {p.name for p in (config.ROOT / "agents").glob("*.md")}
    builtin_skills: set[str] = set()
    for p in GOI.glob("*/goi.json"):
        try:
            bm = _normalize_manifest(_read_manifest_file(p), p.parent.name, p.parent, "builtin")
            builtin_skills.update(bm["skills"])
        except ValueError:
            pass

    st = da_cai()
    other_skills: set[str] = set()
    other_agents: set[str] = set()
    other_mcp: set[str] = set()
    for ogid, entry in st.items():
        if ogid == gid:
            continue
        other_skills.update(entry.get("skills") or ([entry["skill"]] if entry.get("skill") else []))
        other_agents.update(entry.get("agents") or [])
        other_mcp.update(entry.get("mcp") or [])

    for s in skill_names:
        _validate_id(s, "Tên skill")
        if s in core_skills or s in builtin_skills:
            raise ValueError(f"Skill '{s}' trùng với skill mặc định của Kuro, không được ghi đè.")
        if s in other_skills:
            raise ValueError(f"Skill '{s}' đang thuộc về một plugin khác đã cài.")

    for a in agent_names:
        if not _AGENT_RE.fullmatch(a):
            raise ValueError(f"Tên tệp agent không hợp lệ: '{a}'")
        if a in core_agents:
            raise ValueError(f"Agent '{a}' trùng với cộng sự mặc định của Kuro, không được ghi đè.")
        if a in other_agents:
            raise ValueError(f"Agent '{a}' đang thuộc về một plugin khác đã cài.")

    mcp_existing = set(_doc_mcp().get("mcpServers", {}).keys())
    owned_mcp = set((st.get(gid) or {}).get("mcp") or [])
    for srv in mcp_names:
        if srv in other_mcp or (srv in mcp_existing and srv not in owned_mcp):
            raise ValueError(f"MCP server '{srv}' đã tồn tại trong cấu hình máy.")


def _chuan_hoa_va_cai(stage_dir: Path, ten_nguon: str, ghi_de: bool = True) -> dict:
    root = _unwrap_root(stage_dir)

    # Tìm manifest nếu có
    manifest_file = None
    for cand in (root / "goi.json", root / "plugin.json", root / ".claude-plugin" / "plugin.json"):
        if cand.is_file():
            manifest_file = cand
            break

    raw: dict = _read_manifest_file(manifest_file) if manifest_file else {}

    # Đọc file mcp.json / .mcp.json nếu manifest không khai trực tiếp
    mcp_raw = raw.get("mcp")
    if not mcp_raw:
        for mcp_cand in (root / "mcp.json", root / ".mcp.json"):
            if mcp_cand.is_file():
                try:
                    mcp_raw = json.loads(mcp_cand.read_text(encoding="utf-8"))
                except ValueError as e:
                    raise ValueError(f"Tệp {mcp_cand.name} lỗi định dạng JSON: {e}")
                break
    mcp_cfg = _validate_mcp(mcp_raw) if mcp_raw else {}

    # Gom danh sách skill (map: slug -> thư mục nguồn chứa SKILL.md)
    skill_sources: dict[str, Path] = {}
    declared_skills: list[str] = []
    if isinstance(raw.get("skills"), list):
        declared_skills.extend(str(s).strip() for s in raw["skills"] if str(s).strip())
    if raw.get("skill"):
        s0 = str(raw["skill"]).strip()
        if s0 and s0 not in declared_skills:
            declared_skills.insert(0, s0)

    if declared_skills:
        for s in declared_skills:
            if "/" in s or "\\" in s or ".." in s:
                raise ValueError(f"Tên skill không hợp lệ: '{s}'")
            cand_dir = None
            for d in (root / s, root / "skills" / s):
                if (d / "SKILL.md").is_file():
                    cand_dir = d
                    break
            if not cand_dir:
                raise ValueError(f"Không tìm thấy '{s}/SKILL.md' trong gói plugin.")
            skill_sources[s] = cand_dir
    else:
        # Tự phát hiện skill: (1) skills/*/SKILL.md, (2) root/SKILL.md, (3) */SKILL.md
        if (root / "skills").is_dir():
            for sm in sorted((root / "skills").glob("*/SKILL.md")):
                slug = _slugify(sm.parent.name)
                if slug:
                    skill_sources[slug] = sm.parent
        if not skill_sources and (root / "SKILL.md").is_file():
            fm_name, _ = _parse_skill_frontmatter(root / "SKILL.md")
            slug = _slugify(raw.get("id") or fm_name or Path(ten_nguon).stem or root.name)
            if not slug:
                slug = "plugin-ngoai"
            skill_sources[slug] = root
        if not skill_sources:
            for sm in sorted(root.glob("*/SKILL.md")):
                if sm.parent.name in _SKIP_DIRS or sm.parent.name.startswith("."):
                    continue
                slug = _slugify(sm.parent.name)
                if slug:
                    skill_sources[slug] = sm.parent

    # Gom agents/*.md (nếu có)
    agent_sources: dict[str, Path] = {}
    if isinstance(raw.get("agents"), list):
        for a in raw["agents"]:
            aname = Path(str(a).strip()).name
            for cand_a in (root / "agents" / aname, root / aname):
                if cand_a.is_file():
                    agent_sources[aname] = cand_a
                    break
            else:
                raise ValueError(f"Không tìm thấy tệp agent '{aname}' trong gói plugin.")
    elif (root / "agents").is_dir():
        for ap in sorted((root / "agents").glob("*.md")):
            if ap.is_file():
                agent_sources[ap.name] = ap

    if not skill_sources and not agent_sources and not mcp_cfg:
        raise ValueError(
            "Gói plugin không hợp lệ: cần có tệp goi.json (hoặc plugin.json) kèm thư mục skill, "
            "hoặc thư mục/tệp nén chứa SKILL.md."
        )

    # Xác định mã gói (gid), tên, mô tả
    fm_name = ""
    fm_desc = ""
    if skill_sources:
        first_dir = next(iter(skill_sources.values()))
        fm_name, fm_desc = _parse_skill_frontmatter(first_dir / "SKILL.md")

    raw_id = (
        raw.get("id")
        or (root.name if root != stage_dir else "")
        or raw.get("skill")
        or Path(ten_nguon).stem
        or fm_name
        or next(iter(skill_sources.keys()), "")
    )
    gid = _validate_id(_slugify(str(raw_id)), "Mã plugin")

    ten = str(raw.get("ten") or raw.get("name") or fm_name or gid).strip()
    mo_ta = str(raw.get("mo_ta") or raw.get("description") or fm_desc or f"Plugin bên ngoài cài từ {ten_nguon}").strip()
    phien_ban = str(raw.get("phien_ban") or raw.get("version") or "1.0.0").strip()
    tac_gia = str(raw.get("tac_gia") or raw.get("author") or "Bên ngoài").strip()
    pip_specs = _validate_pip_specs(raw.get("pip") or [])
    imp_list = [str(x).strip() for x in (raw.get("import") or []) if str(x).strip()]

    skill_names = list(skill_sources.keys())
    agent_names = list(agent_sources.keys())
    mcp_names = sorted(mcp_cfg.keys())

    if not ghi_de and (ngoai_dir() / gid).exists():
        raise ValueError(f"Plugin ngoài '{gid}' đã tồn tại trên máy.")

    _kiem_tra_xung_dot(gid, skill_names, agent_names, mcp_names)

    # Đóng gói chuẩn hóa vào thư mục tạm rồi đưa vào state/plugins/<gid>
    norm_manifest = {
        "id": gid,
        "ten": ten,
        "mo_ta": mo_ta,
        "phien_ban": phien_ban,
        "tac_gia": tac_gia,
        "nguon": "external",
        "nguon_tep": ten_nguon,
        "skill": skill_names[0] if skill_names else "",
        "skills": skill_names,
        "agents": agent_names,
        "pip": pip_specs,
        "import": imp_list,
        "mcp": mcp_cfg,
    }

    dst_root = ngoai_dir()
    dst_root.mkdir(parents=True, exist_ok=True)
    target_dir = dst_root / gid
    backup_dir: Path | None = None
    prev_installed = gid in da_cai()

    with tempfile.TemporaryDirectory(prefix="kuro-pkg-") as pack_tmp:
        pack_p = Path(pack_tmp) / gid
        pack_p.mkdir(parents=True, exist_ok=True)
        (pack_p / "goi.json").write_text(json.dumps(norm_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        for s_slug, s_dir in skill_sources.items():
            s_dst = pack_p / s_slug
            if s_dir.resolve() == root.resolve():
                # Gói chỉ có SKILL.md ở gốc: chép tất cả trừ các tệp cấu hình gói tổng
                s_dst.mkdir(parents=True, exist_ok=True)
                for item in s_dir.iterdir():
                    if item.name in ("goi.json", "plugin.json", ".claude-plugin", "mcp.json", ".mcp.json", "agents") or item.name in _SKIP_DIRS:
                        continue
                    if item.is_dir():
                        shutil.copytree(item, s_dst / item.name)
                    else:
                        shutil.copy2(item, s_dst / item.name)
            else:
                shutil.copytree(s_dir, s_dst)

        if agent_sources:
            (pack_p / "agents").mkdir(parents=True, exist_ok=True)
            for aname, apath in agent_sources.items():
                shutil.copy2(apath, pack_p / "agents" / aname)

        # Nếu đang cập nhật gói cũ, gỡ skill/agent/mcp cũ trước nhưng giữ backup phòng rollback
        if target_dir.exists():
            backup_dir = dst_root / f".{gid}.bak"
            if backup_dir.exists():
                shutil.rmtree(backup_dir, ignore_errors=True)
            shutil.move(str(target_dir), str(backup_dir))
        if prev_installed:
            go(gid, xoa_ngoai=False)

        shutil.move(str(pack_p), str(target_dir))

    try:
        msg = cai(gid)
    except Exception:
        # Rollback sạch sẽ nếu bước cài pip / chép brain gặp lỗi
        shutil.rmtree(target_dir, ignore_errors=True)
        if backup_dir and backup_dir.exists():
            shutil.move(str(backup_dir), str(target_dir))
            if prev_installed:
                try:
                    cai(gid)
                except Exception:
                    pass
        raise
    else:
        if backup_dir and backup_dir.exists():
            shutil.rmtree(backup_dir, ignore_errors=True)

    return {"ok": True, "id": gid, "ten": ten, "message": msg}


def cai_tu_zip(data: bytes, ten_tep: str = "plugin.zip", ghi_de: bool = True) -> dict:
    """Cài gói plugin bên ngoài từ dữ liệu tệp .zip / .kuro-plugin."""
    if not data:
        raise ValueError("Tệp gói plugin rỗng.")
    with tempfile.TemporaryDirectory(prefix="kuro-zip-") as tmp:
        stage = Path(tmp)
        _safe_extract_zip(data, stage)
        return _chuan_hoa_va_cai(stage, Path(ten_tep or "plugin.zip").name, ghi_de=ghi_de)


def cai_tu_duong_dan(duong_dan: str, ghi_de: bool = True) -> dict:
    """Cài gói plugin bên ngoài từ đường dẫn tệp .zip/.kuro-plugin hoặc thư mục trên máy tính (chỉ đọc trên nguồn)."""
    raw = (duong_dan or "").strip().strip('"').strip("'")
    if not raw:
        raise ValueError("Vui lòng nhập hoặc chọn đường dẫn tệp .zip hoặc thư mục plugin.")
    p = Path(raw)
    if not p.exists():
        raise ValueError(f"Không tìm thấy đường dẫn: {raw}")
    if p.is_file():
        if p.suffix.lower() not in (".zip", ".kuro-plugin"):
            raise ValueError("Chỉ hỗ trợ tệp nén .zip, .kuro-plugin hoặc thư mục chứa gói plugin.")
        if p.stat().st_size > MAX_ZIP_BYTES:
            raise ValueError(f"Tệp gói plugin vượt quá giới hạn {MAX_ZIP_BYTES // (1024 * 1024)} MB.")
        return cai_tu_zip(p.read_bytes(), p.name, ghi_de=ghi_de)
    if p.is_dir():
        with tempfile.TemporaryDirectory(prefix="kuro-dir-") as tmp:
            stage = Path(tmp)
            _safe_copy_dir(p, stage)
            return _chuan_hoa_va_cai(stage, p.name, ghi_de=ghi_de)
    raise ValueError(f"Đường dẫn không hợp lệ: {raw}")


def chay(hanh_dong: str, gid: str = "") -> str:
    if hanh_dong == "list":
        return liet_ke()
    if hanh_dong in ("cai", "go"):
        return (cai if hanh_dong == "cai" else go)(gid)
    raise ValueError("hanh_dong phải là list, cai hoặc go")


if __name__ == "__main__":
    try:
        print(chay(*sys.argv[1:3]))
    except (ValueError, TypeError) as e:
        sys.exit(f"[LỖI] {e}")
