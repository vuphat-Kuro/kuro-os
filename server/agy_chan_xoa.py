"""Hook PreToolUse của agy (Google Antigravity CLI): chặn lệnh xóa/di chuyển tệp trên kho mạng công ty.

Hook của Claude Code (engine.chan_xoa_kho_mang) không áp dụng khi Kuro chạy AI bằng agy, nên agy cần hook riêng.
CHƯA CÀI: bản đầu trả {} khi không chặn, agy coi là từ chối nên chặn mọi tool; cli_engines.go_hook_agy() đang gỡ nó.
Cài lại vào ~/.gemini/config/hooks.json chỉ sau khi thử với agy thật rằng {"decision": "allow"} cho tool chạy bình thường.
Vào (stdin): {"toolCall": {"name", "args"}, ...}. Ra (stdout): {"decision": "deny"|"allow"|"ask", "reason"}; agy
bắt buộc có "decision".
"""
import contextlib
import json
import os
import re
import sys

LENH = {"run_command", "shell_exec", "send_command_input", "run_extension_code", "execute_notebook", "mcp_tool"}
XOA = {"delete_directory", "move"}


def chuoi(x):
    """Mọi chuỗi trong args, kể cả lồng trong list/dict."""
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from chuoi(v)
    elif isinstance(x, list):
        for v in x:
            yield from chuoi(v)


def quyet_dinh(call: dict) -> dict:
    import config
    ten, args = (call.get("name") or "").lower(), call.get("args") or {}
    text = "\n".join(chuoi(args))
    if ten in XOA or "delete" in ten:
        chan = config.nhac_kho_mang(text)
    elif ten in LENH:
        chan = config.xoa_tren_kho_mang(text)
    else:   # công cụ đọc/ghi tệp: chỉ soát khi ghi script, tránh chặn nhầm báo cáo có chữ "move"/"delete"
        duong_dan = [str(v) for k, v in args.items() if re.search("file|path", k, re.I)]
        chan = any(d.lower().endswith(config.DUOI_MA) for d in duong_dan) and config.xoa_tren_kho_mang(text)
    if chan:
        with open(config.STATE / "chan-xoa-kho-mang.log", "a", encoding="utf-8") as f:   # dấu vết để soát
            f.write(json.dumps({"tool": ten, "args": args}, ensure_ascii=False) + "\n")
        return {"decision": "deny", "reason": config.TU_CHOI_XOA_KHO}
    return {}


def main():
    raw = sys.stdin.buffer.read().decode("utf-8", "replace")
    # agy do Kuro chạy đã tự duyệt mọi tool (--dangerously-skip-permissions) nên "allow" giữ nguyên hành vi.
    # shortcut: agy người dùng tự mở thì "ask" (hỏi người dùng), chưa thử thật; nếu phiền thì đổi cách cài hook.
    out = {"decision": "allow" if os.getenv("KURO_AGY") == "1" else "ask"}
    if os.getenv("KURO_AGY") == "1":
        try:
            with contextlib.redirect_stdout(sys.stderr):   # config in thông báo khi nạp; stdout chỉ dành cho JSON
                out = quyet_dinh(json.loads(raw or "{}").get("toolCall") or {}) or out
        except Exception as e:   # shortcut: lỗi hook thì cho qua (không chặn), chỉ ghi stderr
            print(f"[agy_chan_xoa] {e}", file=sys.stderr)
    sys.stdout.write(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
