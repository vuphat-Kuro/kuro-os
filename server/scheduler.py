"""Nhắc hẹn theo cron, đọc từ state/reminders.json. Mỗi 30 giây kiểm một lần.

reminders.json:
  [{"id": "tien-do-tuan", "cron": "0 7 * * 1", "prompt": "Tổng hợp tiến độ tuần...", "enabled": true}]
Cron 5 trường: phút giờ ngày tháng thứ (0 hoặc 7 = Chủ nhật). Hỗ trợ *, */n, a-b, a-b/n, a,b.
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

import config
import engine
import kho
import store

RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]


def _field(spec: str, lo: int, hi: int) -> set[int]:
    out = set()
    for part in spec.split(","):
        rng, _, step = part.partition("/")
        if rng == "*":
            a, b = lo, hi
        elif "-" in rng:
            a, b = map(int, rng.split("-"))
        else:
            a = b = int(rng)
        if not (lo <= a <= hi and lo <= b <= hi):
            raise ValueError(f"cron ngoài khoảng: {part}")
        out.update(range(a, b + 1, int(step) if step else 1))
    return out


def cron_match(expr: str, dt: datetime) -> bool:
    f = expr.split()
    if len(f) != 5:
        raise ValueError(f"cron phải có 5 trường: {expr!r}")
    mi, ho, dom, mon, dow = (_field(s, *r) for s, r in zip(f, RANGES))
    dow = {d % 7 for d in dow}
    if dt.minute not in mi or dt.hour not in ho or dt.month not in mon:
        return False
    day_ok, wd_ok = dt.day in dom, (dt.weekday() + 1) % 7 in dow  # Python: Thứ 2 = 0
    # Như cron chuẩn: khi cả "ngày" lẫn "thứ" đều bị giới hạn thì chỉ cần khớp một trong hai.
    if f[2] != "*" and f[4] != "*":
        return day_ok or wd_ok
    return day_ok and wd_ok


# Việc cài sẵn (specs/002): thêm khi chưa có id đó, KHÔNG ghi đè bản người dùng đã sửa/tắt.
MAC_DINH = [
    {"id": "bao-cao-tuan", "ten": "Báo cáo tiến độ tuần", "cron": "0 7 * * 1", "enabled": True,
     "prompt": "Lập báo cáo tiến độ tuần cho dự án trong thư mục đang mở, theo skill tien-do-san-luong và pm-report: "
               "việc đã xong, đang làm, chậm so với kế hoạch, việc tuần tới, vướng mắc. Ghi nguồn từng số liệu; thiếu "
               "dữ liệu thì liệt kê tệp cần bổ sung, không tự đặt số."},
    {"id": "soat-ho-so", "ten": "Soát hồ sơ mới trong dự án", "cron": "0 20 * * *", "enabled": True,
     "kieu": "soat-ho-so",
     "prompt": "Soát các tệp mới hoặc vừa sửa trong thư mục dự án (danh sách dưới). Với từng tệp: loại hồ sơ, chỗ "
               "thiếu, sai, mâu thuẫn theo skill qc-nghiem-thu-ho-so; tệp không phải hồ sơ thì bỏ qua. Ngắn gọn."},
    {"id": "kiem-tra-kho", "ten": "Kiểm tra kho skill có bản mới", "cron": "0 9 * * 1", "enabled": True,
     "kieu": "kiem-tra-kho"},
]
BO_THU_MUC = {".git", ".venv", "node_modules", "__pycache__", ".agents", ".claude", "state"}


def load() -> list[dict]:
    try:
        return json.loads(config.REMINDERS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def save(viec: list[dict]) -> None:
    config.REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.REMINDERS_FILE.write_text(json.dumps(viec, ensure_ascii=False, indent=1), encoding="utf-8")


def ensure_defaults() -> list[dict]:
    viec = load()
    co = {v["id"] for v in viec}
    them = [dict(v) for v in MAC_DINH if v["id"] not in co]
    if them:
        save(viec + them)
    return viec + them


def _ghi_lan_chay(vid: str, ket_qua: str) -> None:
    f = config.STATE / "lich-chay.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        d = {}
    d[vid] = {"luc": datetime.now().isoformat(timespec="seconds"), "ket_qua": ket_qua[:300]}
    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def lan_chay() -> dict:
    try:
        return json.loads((config.STATE / "lich-chay.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def tep_moi(goc: Path, moc: float, toi_da: int = 200) -> list[str]:
    """Tệp trong thư mục dự án sửa sau mốc thời gian (bỏ thư mục máy móc như .git, .venv)."""
    out = []
    for f in goc.rglob("*"):
        if f.is_file() and not BO_THU_MUC & set(f.relative_to(goc).parts) and f.stat().st_mtime > moc:
            out.append(f.relative_to(goc).as_posix())
            if len(out) >= toi_da:
                break
    return sorted(out)


def _luu_khong_ai(sid: str, ten: str, text: str) -> None:
    store.ensure(sid, title=ten)
    store.add(sid, "assistant", text)


async def run_job(r: dict, notify=None) -> str:
    """Chạy một việc; trả kết quả (cho nút Chạy thử). Soát hồ sơ và kiểm tra kho chỉ gọi AI khi cần."""
    sid, ten = f"nhac-{r['id']}", r.get("ten") or r["id"]
    kieu = r.get("kieu")
    if kieu == "soat-ho-so":
        f = config.STATE / "soat-ho-so.json"
        try:
            moc = json.loads(f.read_text(encoding="utf-8"))["lan_truoc"]
        except (FileNotFoundError, ValueError, KeyError):
            moc = time.time() - 86400   # lần đầu: soát tệp của 24 giờ qua
        goc = engine.active_workspace_dir()
        bat_dau = time.time()
        moi = await asyncio.to_thread(tep_moi, goc, moc)
        f.write_text(json.dumps({"lan_truoc": bat_dau}), encoding="utf-8")
        if not moi:
            answer = f"Không có gì mới: thư mục {goc} không có tệp nào sửa từ lần soát trước."
            _luu_khong_ai(sid, ten, answer)
        else:
            answer = await engine.chat(sid, f"{r['prompt']}\n\nThư mục: {goc}\nTệp mới ({len(moi)}):\n- " + "\n- ".join(moi))
    elif kieu == "kiem-tra-kho":
        moi = await asyncio.to_thread(kho.kiem_tra_nguon)
        answer = ("Kho skill có bản mới, người bảo trì chạy tools/dong_bo_kho.py để đọc duyệt và cập nhật:\n- "
                  + "\n- ".join(moi)) if moi else "Kho skill đang dùng bản mới nhất của mọi nguồn."
        _luu_khong_ai(sid, ten, answer)
        if not moi:
            notify = None   # không có gì mới thì không nhắn Telegram
    else:
        answer = await engine.chat(sid, r["prompt"])
    _ghi_lan_chay(r["id"], answer)
    if notify:
        await notify(f"⏰ {ten}\n\n{answer}")
    return answer


async def _fire(r: dict, notify) -> None:
    try:
        await run_job(r, notify)
    except Exception as e:  # một việc lỗi không làm chết vòng lặp
        _ghi_lan_chay(r["id"], f"[Lỗi] {type(e).__name__}: {e}")
        print(f"[nhắc hẹn] {r['id']}: {type(e).__name__}: {e}")


async def loop(notify=None) -> None:
    # shortcut: chống chạy trùng bằng bộ nhớ trong RAM; khởi động lại đúng phút hẹn có thể chạy 2 lần
    done: set[str] = set()
    ensure_defaults()
    while True:
        now = datetime.now()
        key = now.strftime("%Y%m%d%H%M")
        try:
            for r in load():
                if r.get("enabled", True) and f"{r['id']}@{key}" not in done and cron_match(r["cron"], now):
                    done.add(f"{r['id']}@{key}")
                    asyncio.create_task(_fire(r, notify))
        except Exception as e:  # file hỏng hoặc cron sai: báo log, không làm chết vòng lặp
            print(f"[nhắc hẹn] {type(e).__name__}: {e}")
        await asyncio.sleep(30)
