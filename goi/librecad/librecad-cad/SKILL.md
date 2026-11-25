---
name: librecad-cad
description: "CHỈ dùng khi người dùng muốn XEM, IN, đổi bản vẽ DXF/DWG sang PDF, PNG hoặc SVG, hoặc mở bản vẽ bằng LibreCAD (không cần AutoCAD), hoặc hỏi LibreCAD đã cài chưa, muốn cài/gỡ. Không dùng để vẽ/kiểm DXF theo chuẩn PKTTC (skill autocad-pkttc) và không dùng để đổi chữ TCVN3/VNI (skill texthub-cad)."
---

# LibreCAD (CAD 2D mã nguồn mở, GPLv2)

Nguồn: https://github.com/LibreCAD/LibreCAD. Kuro KHÔNG kèm mã LibreCAD; chỉ cài bản chính thức qua winget. Script ở `scripts/`, chạy bằng `python`.

## Bước 0 - Đã cài chưa
```
python scripts/librecad_setup.py status
```
`trang_thai`: `da_cai` (đọc `cai_dat.duong_dan`) hoặc `chua_cai`. Chưa cài thì hỏi người dùng rồi `python scripts/librecad_setup.py install` (winget, có thể hiện hộp thoại quyền quản trị: người dùng bấm, không bấm thay). Gỡ (`uninstall`) chỉ khi người dùng yêu cầu.

## Bước 1 - Đổi sang PDF/PNG/SVG
```
python scripts/librecad_cli.py convert "<tep.dxf>" --to pdf --out "<thu muc ket qua>"
python scripts/librecad_cli.py convert "<tep.dxf>" --to png --size 3000x2000
```
- Kết quả lưu vào thư mục dự án hiện hành của người dùng, KHÔNG ghi vào kho mạng công ty. Chưa rõ chỗ lưu thì hỏi.
- Đọc `ok` và `tep_ra`; `ok: false` thì báo nguyên `thong_bao`, không tự nói "đã xuất".
- SVG do LibreCAD co theo khung, không phải tỉ lệ 1:1. PDF/PNG theo khổ mặc định của LibreCAD: không dùng để in đúng tỉ lệ khi chưa đối chiếu với bản vẽ gốc.
- DWG cần bản LibreCAD có hỗ trợ DWG; lỗi thì báo, gợi ý đổi sang DXF.

## Bước 2 - Mở bản vẽ
`python scripts/librecad_cli.py open "<tep>"` chỉ khi người dùng muốn xem trong LibreCAD.

## Giới hạn
- LibreCAD là CAD 2D, không có 3D/BIM.
- Cú pháp dòng lệnh lấy từ mã nguồn nhánh master (cần xác minh với bản đang cài: `LibreCAD.exe dxf2pdf -h`).

## MCP
LibreCAD không có MCP riêng: Kuro kèm MCP tự viết `librecad` (nút Cài MCP trong Plugins) với 3 tool `librecad_status`, `librecad_convert`, `librecad_open`, gọi lại đúng 2 script trên.
