# Kế hoạch thực hiện: Kho repo GitHub cho Kuro, tự dùng và chạy ngầm

**Nhánh**: làm thẳng trên `main` (người dùng chọn) | **Ngày**: 2026-11-17 | **Đặc tả**: [spec.md](spec.md)

## Tóm tắt

Thêm thư mục `kho/` vào repo Kuro: bản sao đã ghim commit của các repo trong phạm vi (chỉ phần skill), kèm
`kho/nguon.json` (nguồn, commit, giấy phép, chọn/loại) và `kho/muc-luc.json` (mục lục skill sinh tự động).
Kuro KHÔNG nạp skill trong kho vào lời nhắc; thay vào đó có 3 tool trong máy chủ MCP nội bộ `kuro`:
`tim_skill` (tìm theo từ khoá), `doc_skill` (đọc hướng dẫn và tệp kèm), `chay_ma_kho` (chạy script trong kho
chỉ khi gói mã của skill khớp dấu vân tay trong sổ duyệt). Lịch có thêm 3 việc cài sẵn (báo cáo tuần, soát hồ sơ,
kiểm tra kho), bật/tắt và chạy thử trong Cài đặt. Đồng bộ kho là script `tools/dong_bo_kho.py`: chữ cập nhật
ngay, mã đổi thì giữ bản đã duyệt và để bản mới ở dạng chờ duyệt.

## Bối cảnh kỹ thuật

**Ngôn ngữ**: Python 3.13 (server, script đồng bộ), JavaScript thuần (dashboard), Node ≥18 (chạy mã archify, anatomy)
**Phụ thuộc mới**: không
**Lưu trữ**: `kho/` (theo repo), `kho/da-duyet.json` (sổ duyệt đi kèm repo), `state/kho-da-duyet.json` (duyệt trên máy), `state/reminders.json`, `state/soat-ho-so.json`
**Kiểm thử**: `unittest` trong `tests/test_core.py`; thử thật qua WebSocket với Claude
**Nền tảng**: Windows 10/11
**Ràng buộc**: không đưa mục lục kho vào mỗi lượt chat (SC-002); không sửa tệp theo dõi bởi git trên máy người dùng (để `git pull --ff-only` không vỡ)
**Quy mô**: khoảng 250 skill trong kho

## Soát nguyên tắc

| Nguyên tắc | Kế hoạch đáp ứng | Đạt |
|---|---|---|
| I. Số liệu có nguồn | Skill trong kho dùng chung `tinh_python`; câu trả lời ghi tên skill và repo | Đạt |
| II. Đo, không đoán | Giấy phép, kích thước, loại mã từng repo đã đo trên bản clone (research.md) | Đạt |
| III. Lỗi hiện ra | Mã chưa duyệt bị chặn kèm câu tiếng Việt; soát hồ sơ không có gì mới vẫn ghi "không có gì mới" | Đạt |
| IV. An toàn mặc định | Chạy mã chỉ qua `chay_ma_kho` + dấu vân tay; Bash vẫn tắt; route duyệt qua `local_only` | Đạt |
| V. Ít mã nhất | Dùng lại máy chủ MCP `kuro`, vòng lặp nhắc hẹn, hộp Cài đặt; không thêm thư viện | Đạt |

## Cấu trúc

```text
kho/nguon.json, kho/muc-luc.json, kho/da-duyet.json, kho/<repo>/...   # dữ liệu kho
tools/dong_bo_kho.py      # đồng bộ từ clone gốc, sinh mục lục, giữ mã đã duyệt
server/kho.py             # tìm, đọc, kiểm dấu vân tay, chạy mã đã duyệt, duyệt
server/calc.py            # thêm tool tim_skill, doc_skill, chay_ma_kho vào MCP "kuro"
server/engine.py          # luôn cho phép 3 tool kho; lời nhắc CLI có đường dẫn kho
server/scheduler.py       # việc cài sẵn, soát hồ sơ chỉ gọi AI khi có tệp mới, kiểm tra kho
server/main.py            # /api/kho, /api/kho/duyet, /api/lich, /api/lich/{id}, /api/lich/{id}/chay
dashboard/index.html, app.js   # mục "Kho skill" và "Việc theo lịch" trong Cài đặt
CLAUDE.md                 # một luật: câu chuyên môn skill sẵn có không phủ thì gọi tim_skill
tests/test_core.py
```

## Theo dõi độ phức tạp

Không vi phạm nguyên tắc.
