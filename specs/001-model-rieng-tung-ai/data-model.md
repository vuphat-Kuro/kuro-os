# Mô hình dữ liệu: Mỗi AI nhớ model riêng

## Model đã chọn của AI (`.env`)

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| `KURO_MODEL_<ID>` | chuỗi | regex `[\w.:/\[\]-]*` (không xuống dòng); trống = mặc định của AI |
| `<ID>` | id AI viết hoa | một trong khóa của `config.PROVIDERS` |
| `KURO_MODEL` (cũ) | chuỗi | chỉ đọc lúc chuyển đổi, sau đó luôn rỗng |

Quy tắc hợp lệ khi lưu:
- `claude`: rỗng, `sonnet`, `opus`, `haiku`, hoặc bắt đầu `claude-`.
- `antigravity`: rỗng hoặc có trong `agy models`; không lấy được danh sách thì không chặn.
- AI khác: không chặn.

## Phiên chat (SQLite `sessions.claude_id`, không đổi lược đồ)

| Giá trị | Nghĩa |
|---|---|
| `NULL` | phiên chưa có câu trả lời nào |
| `<id AI>:<mã>` | mã hội thoại do AI `<id AI>` cấp (`claude:...`, `antigravity:...`, `chatgpt:...`) |
| `<mã>` không có dấu `:` (cũ) | coi như `claude:<mã>` |

Chuyển trạng thái mỗi lượt: tiền tố trùng AI đang chọn thì nối tiếp hội thoại; khác thì bắt đầu mới, phát dòng báo,
lưu mã mới với tiền tố AI hiện tại.
