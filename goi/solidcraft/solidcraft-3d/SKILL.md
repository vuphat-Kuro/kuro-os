---
name: solidcraft-3d
description: "CHỈ dùng khi người dùng muốn dựng, sửa hoặc xuất mô hình 3D tham số (chi tiết cơ khí, gối, bản mã, khuôn, đồ gá) bằng SolidCraft, xuất STEP, hoặc hỏi SolidCraft đã cài chưa. Không dùng cho bản vẽ 2D (DXF/DWG), BIM/IFC hay kết cấu bê tông cả công trình."
---

# SolidCraft (CAD 3D tham số, Rust, Apache-2.0)

Nguồn: https://github.com/tangency-labs/solidcraft, tài liệu https://docs.solidcraft.io/. Bản portable x64 ghim `v0.49.0` (~220 MB), kiểm SHA-256, cài ở `%LOCALAPPDATA%\Programs\SolidCraft`. Bản Windows chưa ký số: SmartScreen có thể cảnh báo khi chạy `solidcraft.exe`.

## Bước 0 - Đã cài chưa
`python scripts/solidcraft_setup.py status`. `chua_cai`: hỏi người dùng rồi `install` (tải nền, vài phút; `status` báo `dang_cai` tới khi xong). Cài xong mà `solidcraft-cli.exe` không có trong thư mục thì báo, không tự dò nơi khác.

## Bước 1 - Dùng
Ưu tiên MCP `solidcraft` (headless). Trình tự do chính tài liệu SolidCraft: xem lệnh có sẵn rồi chạy kịch bản JSON.
```
solidcraft-cli commands
solidcraft-cli run script.json --out part.step
```
- Mọi kích thước đưa vào là THAM SỐ của kịch bản; con số kỹ thuật (tải, hệ số) vẫn theo luật số liệu của Kuro: tính bằng `tinh_python`, ghi nguồn.
- Sau mỗi bước đối chiếu thể tích/bao hình mong đợi với kết quả đo; không báo "xong" chỉ vì lệnh trả OK.
- Tệp .step/.json lưu vào thư mục dự án hiện hành, KHÔNG ghi vào kho mạng UNC công ty.
- Cú pháp chính xác của kịch bản/MCP: đọc `docs/mcp.md` trong repo, không đoán.
