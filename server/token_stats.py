"""Thống kê token đã đốt theo nguồn: Kuro, Claude Desktop/Claude Code, Codex trực tiếp.

Đọc nhật ký sẵn có trên máy, không gọi API:
- ~/.claude/projects/*/*.jsonl (và subagents/): mỗi bản ghi assistant có message.usage và `entrypoint`.
  sdk-py = Kuro (Claude Agent SDK Python), claude-desktop = app Claude, cli = Claude Code ở terminal.
- ~/.codex/sessions/**/rollout-*.jsonl: sự kiện token_count.last_token_usage; originator codex_exec = Kuro gọi.
  OpenAI tính cached_input_tokens nằm trong input_tokens.
- Antigravity (agy) chưa ghi token ra tệp nên chưa đo được.

"Quy đổi" = token đầu vào tương đương theo tỉ lệ giá của Anthropic: mới 1, ghi bộ nhớ đệm 1.25, đọc bộ nhớ đệm 0.1,
đầu ra 5. Codex dùng cùng công thức để so được với nhau (giá thật của OpenAI khác, chỉ là so sánh tương đối).
"""
import datetime as dt
import glob
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

NGUON = {"sdk-py": "Kuro (Claude)", "claude-desktop": "Claude Desktop", "cli": "Claude Code (terminal)"}
CTX_CANH_BAO = 200_000   # phiên dài hơn mức này: mỗi câu đọc lại cả khối, nên mở phiên mới
# Kuro phải rẻ hơn dùng AI trực tiếp: một lần gọi của Kuro quá mức này là báo đỏ (nền ~29k: system prompt + tool;
# 100k = nền + khoảng 70k hội thoại/tệp đọc, lúc đó mở phiên mới rẻ hơn đi tiếp)
NGUONG_KURO = 100_000
_cache: dict[str, tuple[tuple, dict]] = {}   # đường dẫn tệp -> ((mtime, size), kết quả đọc)
_lock = threading.Lock()


def quy_doi(moi: int, ghi: int, doc: int, ra: int) -> float:
    return moi + 1.25 * ghi + 0.1 * doc + 5 * ra


def tiet_kiem(ghi: int, doc: int) -> float:
    """Token quy đổi bộ nhớ đệm đã bớt so với gửi lại toàn bộ như token mới: đọc lại 0.1 thay vì 1, trừ phụ phí ghi 0.25."""
    return 0.9 * doc - 0.25 * ghi


def rtk_tiet_kiem(ngays: list[str]) -> int | None:
    """Token RTK đã cắt khỏi đầu ra lệnh shell trong các ngày này (mọi AI trên máy, không riêng Kuro); None nếu không có RTK."""
    exe = shutil.which("rtk")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "gain", "--daily", "--format", "json"], capture_output=True, text=True, timeout=20,
                             env={**os.environ, "RTK_TELEMETRY_DISABLED": "1"},
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        return sum(d.get("saved_tokens", 0) for d in json.loads(out).get("daily", []) if d.get("date") in ngays)
    except (OSError, subprocess.SubprocessError, ValueError, AttributeError):
        return None


def _ngay(ts: str) -> str:
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d")


def _doc_claude(f: str) -> dict:
    """{ngay: [moi, ghi, doc, ra, so_goi]}, nguồn, ngữ cảnh lớn nhất, lần cuối, câu hỏi đầu."""
    ngay, seen = {}, set()
    out = {"nguon": None, "max_ctx": 0, "cuoi": "", "dau": "", "theo_ngay": ngay}
    with open(f, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"user"' in line and not out["dau"] and '"content":"' in line:
                try:
                    e = json.loads(line)
                    c = (e.get("message") or {}).get("content")
                    if isinstance(c, str) and not c.startswith(("<", "(")):
                        out["dau"] = c[:90].replace("\n", " ")
                except ValueError:
                    pass
            if '"usage"' not in line or '"assistant"' not in line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            m = e.get("message") or {}
            u = m.get("usage") or {}
            if e.get("type") != "assistant" or not u or m.get("id") in seen:
                continue
            seen.add(m.get("id"))   # một lần gọi API ghi nhiều dòng (mỗi khối nội dung), cùng message.id
            out["nguon"] = out["nguon"] or e.get("entrypoint")
            moi, ghi, doc = u.get("input_tokens", 0), u.get("cache_creation_input_tokens", 0), u.get("cache_read_input_tokens", 0)
            d = ngay.setdefault(_ngay(e["timestamp"]), [0, 0, 0, 0, 0])
            for i, v in enumerate((moi, ghi, doc, u.get("output_tokens", 0), 1)):
                d[i] += v
            out["max_ctx"] = max(out["max_ctx"], moi + ghi + doc)
            out["ctx_cuoi"] = moi + ghi + doc
            out["cuoi"] = max(out["cuoi"], e["timestamp"])
    return out


def _doc_codex(f: str) -> dict:
    ngay = {}
    out = {"nguon": None, "max_ctx": 0, "cuoi": "", "dau": "", "theo_ngay": ngay}
    with open(f, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i == 0:
                try:
                    p = json.loads(line).get("payload") or {}
                    out["nguon"] = "Kuro (Codex)" if p.get("originator") == "codex_exec" else "Codex trực tiếp"
                    out["du_an"] = p.get("cwd") or ""
                except ValueError:
                    pass
            if '"token_count"' not in line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            u = ((e.get("payload") or {}).get("info") or {}).get("last_token_usage") or {}
            if not u:
                continue
            doc = u.get("cached_input_tokens", 0)
            moi = max(0, u.get("input_tokens", 0) - doc)
            d = ngay.setdefault(_ngay(e["timestamp"]), [0, 0, 0, 0, 0])
            for j, v in enumerate((moi, u.get("cache_write_input_tokens", 0), doc, u.get("output_tokens", 0), 1)):
                d[j] += v
            out["max_ctx"] = max(out["max_ctx"], u.get("input_tokens", 0))
            out["ctx_cuoi"] = u.get("input_tokens", 0)
            out["cuoi"] = max(out["cuoi"], e["timestamp"])
    return out


def _doc(f: str, ham) -> dict:
    st = os.stat(f)
    key = (st.st_mtime_ns, st.st_size)
    with _lock:
        hit = _cache.get(f)
    if hit and hit[0] == key:
        return hit[1]
    kq = ham(f)
    with _lock:
        _cache[f] = (key, kq)
    return kq


def thong_ke(so_ngay: int = 7, home: Path | None = None) -> dict:
    home = home or Path.home()
    tu = dt.date.today() - dt.timedelta(days=so_ngay - 1)
    moc = dt.datetime.combine(tu, dt.time()).timestamp()
    ngays = [(tu + dt.timedelta(days=i)).isoformat() for i in range(so_ngay)]
    tep = [(f, _doc_claude, "claude") for f in glob.glob(str(home / ".claude" / "projects" / "*" / "*.jsonl"))
           + glob.glob(str(home / ".claude" / "projects" / "*" / "*" / "subagents" / "*.jsonl"))]
    tep += [(f, _doc_codex, "codex") for f in glob.glob(str(home / ".codex" / "sessions" / "**" / "*.jsonl"), recursive=True)]
    nguon: dict[str, dict] = {}
    phien = []
    for f, ham, loai in tep:
        try:
            if os.path.getmtime(f) < moc:
                continue
            r = _doc(f, ham)
        except OSError:
            continue
        ten = r["nguon"] if loai == "codex" else NGUON.get(r["nguon"], r["nguon"] or "Claude (khác)")
        if not ten:
            continue
        tong = [0, 0, 0, 0, 0]
        for ng, v in r["theo_ngay"].items():
            if ng < ngays[0]:
                continue
            n = nguon.setdefault(ten, {"theo_ngay": {d: 0.0 for d in ngays}, "moi": 0, "ghi": 0, "doc": 0, "ra": 0, "goi": 0})
            n["theo_ngay"][ng] = n["theo_ngay"].get(ng, 0) + quy_doi(*v[:4])
            for k, i in (("moi", 0), ("ghi", 1), ("doc", 2), ("ra", 3), ("goi", 4)):
                n[k] += v[i]
            tong = [a + b for a, b in zip(tong, v)]
        if tong[4]:
            du_an = r.get("du_an") if loai == "codex" else Path(f).relative_to(home / ".claude" / "projects").parts[0]
            phien.append({"nguon": ten, "du_an": du_an, "ma": Path(f).stem[-36:], "goi": tong[4],
                          "quy_doi": round(quy_doi(*tong[:4])), "tiet_kiem": round(tiet_kiem(tong[1], tong[2])),
                          "max_ctx": r["max_ctx"], "cuoi": r["cuoi"],
                          "cau_dau": r["dau"], "qua_dai": r["max_ctx"] > CTX_CANH_BAO,
                          "ctx_cuoi": r.get("ctx_cuoi", 0),
                          # theo lần gọi gần nhất: phiên vẫn nặng thì gõ tiếp vẫn tốn; mở phiên mới là hết đỏ
                          "vuot": ten.startswith("Kuro") and r.get("ctx_cuoi", 0) > NGUONG_KURO})
    for n in nguon.values():
        n["quy_doi"] = round(sum(n["theo_ngay"].values()))
        n["tiet_kiem"] = round(tiet_kiem(n["ghi"], n["doc"]))
        n["tb_goi"] = round(n["quy_doi"] / n["goi"]) if n["goi"] else 0
        n["theo_ngay"] = {d: round(v) for d, v in n["theo_ngay"].items()}
    # So theo token quy đổi trung bình mỗi lần gọi: Kuro phải thấp hơn các AI dùng trực tiếp
    k = [v for t, v in nguon.items() if t.startswith("Kuro")]
    o = [v for t, v in nguon.items() if not t.startswith("Kuro")]
    tb = lambda ds: round(sum(v["quy_doi"] for v in ds) / max(1, sum(v["goi"] for v in ds))) if ds else None
    so_sanh = {"kuro_tb": tb(k), "khac_tb": tb(o), "nguong": NGUONG_KURO}
    # Đỏ khi Kuro trung bình tốn hơn, hoặc phiên Kuro VỪA DÙNG còn nặng. Phiên cũ bỏ dở chỉ tô đỏ trong bảng: chúng
    # không đốt thêm, và gõ tiếp vào là Kuro tự mở hội thoại mới (engine.chat), nên không giữ nút đỏ cả ngày.
    gan = max((p for p in phien if p["nguon"].startswith("Kuro")), key=lambda p: p["cuoi"], default=None)
    so_sanh["phien_gan_vuot"] = bool(gan and gan["vuot"])
    so_sanh["vuot"] = bool(k and o and so_sanh["kuro_tb"] > so_sanh["khac_tb"]) or so_sanh["phien_gan_vuot"]
    phien.sort(key=lambda p: -p["quy_doi"])
    # phiên Kuro vượt ngưỡng luôn hiện (dù không lọt top 20) để người dùng thấy lý do báo đỏ
    hien = phien[:20] + [p for p in phien[20:] if p["vuot"]]
    return {"ngay": ngays, "nguon": nguon, "phien": hien, "canh_bao_ctx": CTX_CANH_BAO, "rtk": rtk_tiet_kiem(ngays),
            "so_sanh": so_sanh,
            "ghi_chu": "Antigravity (agy) chưa ghi số token ra tệp nên chưa đo được. Quy đổi theo tỉ lệ giá Anthropic: "
                       "đọc bộ nhớ đệm 0.1, ghi 1.25, đầu ra 5 (Codex dùng cùng công thức để so tương đối)."}


def mot_phien(ma: list[str], home: Path | None = None) -> dict | None:
    """Số token của một phiên Kuro (mã hội thoại Claude/Codex lưu trong kuro.db) để báo đỏ ngay sau lượt chat."""
    home = home or Path.home()
    ra = None
    for m in filter(None, ma):
        m = Path(m.split(":")[-1]).name   # bỏ tiền tố "claude:"; chặn ký tự đường dẫn trước khi ghép vào glob
        tep = [(f, _doc_claude) for f in glob.glob(str(home / ".claude" / "projects" / "*" / f"{glob.escape(m)}.jsonl"))]
        tep += [(f, _doc_codex) for f in glob.glob(str(home / ".codex" / "sessions" / "**" / f"rollout-*{glob.escape(m)}.jsonl"),
                                                   recursive=True)]
        for f, ham in tep:
            r = _doc(f, ham)
            if not ra or r["cuoi"] > ra["cuoi"]:   # nhiều AI trong một phiên: lấy AI vừa trả lời
                tong = [sum(v[i] for v in r["theo_ngay"].values()) for i in range(5)]
                ra = {"cuoi": r["cuoi"], "goi": tong[4], "quy_doi": round(quy_doi(*tong[:4])),
                      "tiet_kiem": round(tiet_kiem(tong[1], tong[2])), "max_ctx": r["max_ctx"],
                      "ctx_cuoi": r.get("ctx_cuoi", 0), "nguong": NGUONG_KURO}
    if ra:
        ra["vuot"] = ra["ctx_cuoi"] > NGUONG_KURO
    return ra
