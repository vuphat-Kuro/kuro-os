---
name: cadcraft-dxf
description: "CHỈ dùng khi người dùng muốn xem thông tin, đổi DXF/DWG sang SVG/PNG, chạy lệnh CAD trên bản vẽ bằng CADCraft, hoặc hỏi CADCraft đã cài chưa. Không dùng để vẽ/kiểm DXF theo chuẩn PKTTC (skill autocad-pkttc), không đổi chữ TCVN3/VNI (skill texthub-cad)."
---

# CADCraft (CAD 2D/3D, Rust, Apache-2.0)

Nguồn: https://github.com/storytold/cadcraft. Giai đoạn phát triển sớm (README ghi "early development"). Bản portable ghim `v0.20.1`, kiểm SHA-256, cài ở `%LOCALAPPDATA%\Programs\CADCraft`.

## Bước 0 - Đã cài chưa
`python scripts/cadcraft_setup.py status`. `chua_cai`: hỏi người dùng rồi `install` (tải nền ~75 MB, `status` báo `dang_cai` cho tới khi xong).

## Bước 1 - Dùng
Ưu tiên MCP `cadcraft` (headless). Bản 0.20.1 CHƯA có cờ giới hạn thư mục đọc/ghi cho MCP (README nhánh mới có, bản này không): MCP đọc/ghi được mọi nơi người dùng có quyền, nên chỉ cho nó đụng tệp trong thư mục dự án. Hoặc `cadcraft-cli.exe` trong thư mục cài:
```
cadcraft-cli info d.dxf
cadcraft-cli convert d.dxf d.svg
cadcraft-cli convert d.dwg d.png --window 0,0,20000,15000
cadcraft-cli run d.dwg --cmd 'zoom {"mode":"window","p1":[0,0],"p2":[20000,15000]}' --export out.png
cadcraft-cli commands                  # danh sách lệnh
```
- Kết quả lưu vào thư mục dự án hiện hành, KHÔNG ghi vào kho mạng UNC công ty.
- Ảnh/SVG xuất ra chưa chắc đúng tỉ lệ in: không dùng để in chính thức khi chưa đối chiếu bản gốc.
- DWG/DXF có chữ TCVN3/VNI cũ sẽ hiện sai dấu: báo người dùng, dùng skill texthub-cad để đổi trong AutoCAD.
