"""Nhắc hẹn theo cron, đọc từ state/reminders.json. Mỗi 30 giây kiểm một lần.

reminders.json:
  [{"id": "tien-do-tuan", "cron": "0 7 * * 1", "prompt": "Tổng hợp tiến độ tuần...", "enabled": true}]
Cron 5 trường: phút giờ ngày tháng thứ (0 hoặc 7 = Chủ nhật). Hỗ trợ *, */n, a-b, a-b/n, a,b.
"""
import asyncio
import json
from datetime import datetime

import config
import engine

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


def load() -> list[dict]:
    try:
        return json.loads(config.REMINDERS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


async def _fire(r: dict, notify) -> None:
    answer = await engine.chat(f"nhac-{r['id']}", r["prompt"])
    if notify:
        await notify(f"⏰ {r['id']}\n\n{answer}")


async def loop(notify=None) -> None:
    # shortcut: chống chạy trùng bằng bộ nhớ trong RAM; khởi động lại đúng phút hẹn có thể chạy 2 lần
    done: set[str] = set()
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
