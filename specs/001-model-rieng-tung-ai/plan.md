# Kế hoạch thực hiện: Mỗi AI nhớ model riêng

**Nhánh**: `001-model-rieng-tung-ai` | **Ngày**: 2026-11-03 | **Đặc tả**: [spec.md](spec.md)
**Đầu vào**: Đặc tả tại `specs/001-model-rieng-tung-ai/spec.md`

## Tóm tắt

Thay một khóa model chung `KURO_MODEL` bằng một khóa cho mỗi AI (`KURO_MODEL_CLAUDE`, `KURO_MODEL_ANTIGRAVITY`...).
`config.MODEL` vẫn giữ tên cũ nhưng luôn là model của AI đang chọn, nên mọi chỗ đang đọc nó (Claude Code, codex, agy,
kiểm tra kết nối) đúng ngay mà không phải sửa. API vẫn nhận khóa `KURO_MODEL`; server tự ghi vào khóa của đúng AI và
chặn tên sai khi AI có danh sách. Mã hội thoại lưu kèm tên AI để biết khi nào báo "AI mới chưa biết các câu trước".

## Bối cảnh kỹ thuật

**Ngôn ngữ/Phiên bản**: Python 3.13 (server), JavaScript thuần (dashboard)
**Phụ thuộc chính**: FastAPI, claude-agent-sdk, python-dotenv; CLI `agy` 1.3.3, `codex` 0.156.1 (không thêm thư viện mới)
**Lưu trữ**: `.env` (khóa model theo AI), SQLite `state/` (cột `claude_id` của phiên, giữ nguyên lược đồ)
**Kiểm thử**: `unittest` trong `tests/test_core.py` + thử thật qua giao diện và WebSocket
**Nền tảng**: Windows 10/11, chạy ở 127.0.0.1
**Loại dự án**: ứng dụng web nội bộ (server + trang tĩnh)
**Mục tiêu hiệu năng**: đổi model trên thanh trên cùng có hiệu lực ngay câu hỏi kế tiếp; lưu bị chặn trả lời dưới 1 giây (danh sách agy đã nhớ tạm)
**Ràng buộc**: không đổi lược đồ SQLite; máy cài bản cũ cập nhật xong chạy được ngay
**Quy mô**: 1 người dùng mỗi máy, khoảng 10 AI, mỗi AI 0 đến khoảng 20 model

## Soát nguyên tắc

*Cổng: đạt trước Giai đoạn 0, soát lại sau Giai đoạn 1.*

| Nguyên tắc | Kế hoạch đáp ứng | Đạt |
|---|---|---|
| I. Số liệu có nguồn | Không đụng phần tính toán | Đạt |
| II. Đo, không đoán | Danh sách Antigravity lấy từ `agy models` (đã đo); danh sách Claude là bí danh Claude Code nhận (sonnet/opus/haiku, đã dùng thật ở bản 1.0) | Đạt |
| III. Lỗi hiện ra, chặn trước | Chặn tên sai lúc lưu (FR-005); lỗi model của hãng không có danh sách dịch sang tiếng Việt (FR-006) | Đạt |
| IV. An toàn mặc định | Khóa mới đi qua cùng cổng `local_only` và regex chặn xuống dòng như khóa cũ | Đạt |
| V. Ít mã nhất, có kiểm tra | Giữ `config.MODEL` và khóa API `KURO_MODEL` để không sửa nơi gọi; thêm bài kiểm tra cho lưu theo AI, chặn tên sai, chuyển đổi bản cũ, tiền tố phiên | Đạt |

Soát lại sau thiết kế: vẫn đạt cả 5, không có ngoại lệ cần biện minh.

## Cấu trúc dự án

### Tài liệu (tính năng này)

```text
specs/001-model-rieng-tung-ai/
├── plan.md          # tệp này
├── research.md      # Giai đoạn 0: các quyết định
├── data-model.md    # Giai đoạn 1: dữ liệu
├── quickstart.md    # Giai đoạn 1: cách thử
└── contracts/
    └── api.md       # Giai đoạn 1: thay đổi API nội bộ
```

### Mã nguồn bị chạm

```text
server/
├── config.py        # khóa model theo AI, MODEL suy ra từ AI đang chọn, chuyển đổi bản cũ, danh sách model Claude
├── engine.py        # tiền tố AI cho mã hội thoại, dòng báo đổi AI, dịch lỗi model
├── cli_engines.py   # trả mã hội thoại trần (engine tự gắn tiền tố)
└── main.py          # lưu KURO_MODEL vào khóa của đúng AI, chặn tên sai, /api/models có Claude
dashboard/
├── app.js           # đổi AI trong Cài đặt thì nạp model của AI đó; ô chọn nhanh cho Claude
└── index.html       # tăng số phiên bản app.js
tests/test_core.py   # bài kiểm tra mới
env.example, README.md, KE-HOACH.md, VERSION
```

**Quyết định cấu trúc**: giữ nguyên các tệp hiện có, không thêm mô-đun mới.

## Theo dõi độ phức tạp

Không có vi phạm nguyên tắc nên không cần biện minh.
