"""Kênh Telegram: long-poll, chỉ trả lời ID chủ trong TELEGRAM_OWNER_IDS. Gõ /moi để sang cuộc mới."""
import asyncio

import httpx

import config
import engine
import store

API = f"https://api.telegram.org/bot{config.TG_TOKEN}"


async def send(chat_id: int, text: str) -> None:
    async with httpx.AsyncClient(timeout=30) as c:
        for i in range(0, max(len(text), 1), 4000):   # Telegram giới hạn 4096 ký tự mỗi tin
            await c.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text[i:i + 4000] or "(trống)"})


async def notify(text: str) -> None:
    for uid in config.TG_OWNERS:
        await send(uid, text)


async def loop() -> None:
    offset = 0
    async with httpx.AsyncClient(timeout=60) as c:
        while True:
            try:
                r = await c.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 50})
                for u in r.json().get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message") or {}
                    uid, text = (msg.get("from") or {}).get("id"), msg.get("text")
                    if uid not in config.TG_OWNERS or not text:
                        continue                                  # người lạ: im lặng
                    sid = f"tg-{msg['chat']['id']}"
                    if text.strip() == "/moi":
                        store.ensure(sid)
                        store.set_claude_id(sid, None)
                        await send(msg["chat"]["id"], "Đã sang cuộc trò chuyện mới.")
                        continue
                    await send(msg["chat"]["id"], await engine.chat(sid, text))
            except Exception as e:  # mất mạng: chờ rồi thử lại, không chết vòng lặp
                print(f"[telegram] {type(e).__name__}: {e}")
                await asyncio.sleep(5)
