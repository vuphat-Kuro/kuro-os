# Lịch sử phiên bản PKTTC TextHub

Phiên bản ghi theo tệp `VERSION`. Chi tiết từng giai đoạn: `nguon\bao_cao\KetQua_*.md`.

## 0.9.3 (2026-11-23) - gói đầy đủ cho máy mới
- Gói Kuro mang theo **kho font đầy đủ** (`payload/KhoFont`, 361 tệp) và các **SHX Unicode** trong bundle (`Contents/Fonts`, thêm vào Support File Search Path của AutoCAD qua `SupportPath`).
- `texthub_setup.py install` chép kho font, thêm vào `fontstore.txt`; thêm `fonts-install` (cài Arial Unicode MS cho người dùng hiện tại), `status` báo kho font và font cần thiết, `uninstall --xoa-kho-font`.
- Kèm mã nguồn (`nguon/`), lịch sử này, `references/KHO_FONT.md`.

## 0.9.2 / 0.9.1 (2026-11-23) - gói cho Kuro
- Gói `texthub` theo quy ước `goi/` của Kuro: `goi.json`, skill `texthub-cad`, `texthub_setup.py` (trạng thái, cài, gỡ, phát hiện bản AutoCAD), `texthub_cad.py` (gọi cổng), máy chủ MCP.
- `pkttc_client.find_bridges` bỏ qua tệp cổng cũ sót lại; tài liệu cổng viết lại.

## 0.9.0 (2026-11-23)
- Font đích mặc định theo loại font nguồn: TrueType sang Arial Unicode MS, SHX sang uv-abc.shx; ghim `Arial Unicode MS`, `uv-abc.shx`, `3T-Unicode.shx` đầu danh sách; nút "Cài font đích thiếu từ kho".
- Kho font bổ sung 301 tệp từ `Downloads\Fonts`; thêm `ARIALUNI.ttf`.

## 0.8.0 (2026-11-23)
- Thẻ **Đổi chữ**: liệt kê font nguồn, chọn font đích riêng cho từng loại (TrueType và SHX Unicode); kế hoạch có `newFont` và `fontMap`; style SHX.

## 0.7.1 / 0.7.0 (2026-11-23) - bảng và menu
- Bảng `PKTEXTUI` (PaletteSet, 5 thẻ: Quét, Đổi chữ, Font, Kho font, Trợ lý) và menu **KTTC > Text > Convert Font**.
- 0.7.1 sửa macro menu (ký tự Ctrl+C thật thay chuỗi `^C^C`).

## 0.6.3 đến 0.6.1 (2026-11-21 đến 2026-11-23)
- 0.6.3: font đích mặc định đổi từ Arial sang Segoe UI (Arial thường không vẽ được `Ả Ế ọ Ố Ỡ Ơ Ư` trên AutoCAD 2020).
- 0.6.2: sửa nhận font HOA có dấu cách (`.VnArial NarrowH`); chữ TCVN3 trong style Unicode toàn chữ ASCII HOA coi là HOA.
- 0.6.1: lệnh xác nhận không phân biệt hoa thường (`yes`).

## 0.6.0 (2026-11-21) - bản đóng gói đầu tiên
- Bundle Autodesk tự nạp khi AutoCAD khởi động, trình cài `cai_dat.ps1` (kiểm SHA-256, giữ bản cũ, gỡ sạch), lệnh `PKTEXTABOUT`.

## Giai đoạn S0 đến S5 (2026-11)
- S1 lõi chuyển bảng mã TCVN3/VNI/Unicode và bộ tách MTEXT; S2 quét mọi loại chữ; S3 kế hoạch, áp dụng, sao lưu, hoàn tác; S4 báo cáo font, kho font, dọn style; S5 cổng cho trợ lý (named pipe, MCP, hộp thoại xác nhận, nhật ký).
