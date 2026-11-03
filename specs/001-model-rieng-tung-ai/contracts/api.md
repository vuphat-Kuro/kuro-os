# Hợp đồng API nội bộ (chỉ trang Kuro gọi, qua `local_only`)

## GET /api/settings

Thêm trường `model_theo_ai`: `{ "<id AI>": "<model đã lưu>" }` cho mọi AI trong `providers`.
`settings.KURO_MODEL.value` = model của AI đang chọn (không còn là khóa chung).

## POST /api/settings

Nhận `KURO_MODEL` như cũ. Server ghi vào `KURO_MODEL_<AI>`, với AI = `KURO_PROVIDER` trong cùng thân yêu cầu nếu có,
không thì AI đang chọn.

- Tên sai với AI có danh sách: HTTP 400, `detail` tiếng Việt, ví dụ:
  `Model "gemini-3.8-flash-medium" không dùng được với Tài khoản Claude. Chọn: Mặc định, sonnet, opus, haiku (hoặc tên bắt đầu claude-).`
- Đổi `KURO_PROVIDER` mà không gửi `KURO_MODEL`: model của AI mới giữ nguyên giá trị đã lưu trước đó.

## GET /api/models

`{ "models": [{"id", "ten"}], "current": "<model của AI đang chọn>" }`.
Claude: `[{"id":"","ten":"Mặc định"}, sonnet, opus, haiku]`. Antigravity: từ `agy models`. AI khác: `[]`.

## WebSocket /ws

Sự kiện `text` mới (đầu lượt, chỉ khi phiên đã có câu trả lời của AI khác):
`_(Đã đổi sang <tên AI>: AI mới chưa biết các câu trước trong phiên này.)_`
