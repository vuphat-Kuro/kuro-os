# Kết quả: gói TextHub cho Kuro (bản 0.9.2)

Ngày 2026-11-23. Trạng thái: DỰ THẢO - CHỜ DUYỆT. Gói chưa được chép vào `C:\Kuro-os\Kuro` và chưa thử bên trong Kuro.

## Sản phẩm

- `dist_kuro\PKTTC-TextHub-Kuro-0.9.2.zip` (108.230 B, SHA-256 `07A000011F3A8D70064B0C2A4BA96D65666985CD7825C9EE2E094AB31F02BEEA`) và thư mục `dist_kuro\texthub\` (cùng nội dung, 21 tệp).
- Theo quy ước `goi/<id>/` của Kuro (đọc từ `C:\Kuro-os\Kuro\goi\README.md`, `goi\autocad\goi.json` và `server\goi.py`): `goi.json` (`ten`, `mo_ta`, `skill`, `pip`, `import`), thư mục skill `texthub-cad` trùng giá trị `skill`, `SKILL.md` có front matter `name` và `description`.
- Tự chứa: chỉ cần Python 3 (thư viện chuẩn), không `pip`. Không dính gì tới Javis.
- Nguồn dựng: `kuro\` (phần riêng cho Kuro), `dong_goi_kuro.py` (lắp gói từ `dist\` và `texthub_s5\bridge`).

## Gồm gì

| Thành phần | Việc |
|---|---|
| `texthub_setup.py status` | Trạng thái JSON: các bản AutoCAD trên máy (đọc registry) và có được hỗ trợ không, plugin đã cài hay chưa và bản nào, có bản mới không, AutoCAD đang mở/khóa DLL không, kho font, cổng Kuro đang mở |
| `texthub_setup.py install / uninstall` | Cài, cập nhật, gỡ cho người dùng hiện tại (không admin, không registry); kiểm SHA-256 từng tệp; giữ `.old` và tự khôi phục khi lỗi; từ chối khi AutoCAD đang dùng DLL hoặc không có bản AutoCAD nào được hỗ trợ |
| `texthub_setup.py fontstore` | Xem hoặc đặt thư mục kho font |
| `texthub_cad.py` | Gọi cổng TextHub: ping, scan, fonts, plan.create/get/apply, fontsub, purge, shutdown; tham số qua `--json-file` hoặc stdin |
| `pkttc_mcp.py`, `mcp.example.json` | Máy chủ MCP (11 công cụ), nếu muốn Kuro gọi qua MCP |
| `SKILL.md`, `references/` | Quy trình dùng, luật cứng, hướng dẫn, ghi chú đa phiên bản |

## Trạng thái cài đặt để Kuro hiển thị

`trang_thai`: `chua_cai`, `da_cai`, `co_ban_moi`, `da_cai_ban_moi_hon`, `khong_ho_tro`, `khong_co_autocad`, `loi`, kèm `thong_bao`, `goi_y` (`install`, `fontstore`), `autocad[]` (mỗi bản có `ho_tro` và `ly_do`). `goi.json` có khóa bổ sung `kiem_tra` trỏ lệnh này. **Kuro hiện chưa đọc khóa đó** (`server/goi.py` bỏ qua): màn hình danh sách công cụ cần bổ sung bên Kuro.

## Nhiều bản AutoCAD

- Làm được trong gói này: phát hiện mọi bản AutoCAD trên máy; so với khoảng bản bundle khai báo trong `PackageContents.xml` (`SeriesMin`, `SeriesMax`); báo rõ bản nào chưa hỗ trợ, AutoCAD LT không hỗ trợ; từ chối cài khi không có bản nào hỗ trợ. Trên máy này thấy AutoCAD 2020 (R23.1, hỗ trợ) và AutoCAD 2007 (R17.0, không hỗ trợ).
- CHƯA làm: DLL chỉ dựng và thử cho AutoCAD 2020 nên bundle chỉ khai R23.1. Hỗ trợ bản khác cần dựng thêm DLL (nhóm .NET Framework 2018-2024, nhóm .NET 8 từ 2025) và thử trên máy có bản đó: xem `references\DA_PHIEN_BAN.md`. Em chỉ có AutoCAD 2020 để thử.

## Đã kiểm

- `tests\kuro_setup_test.py`: 29/29 đạt (thư mục tạm, không đụng máy thật): đọc gói và MANIFEST, so sánh phiên bản theo số, đánh giá hỗ trợ theo bản AutoCAD (2020 có, 2023 không, LT không), 7 trạng thái, cài/cập nhật/gỡ, cài không ghi tệp ngoài thư mục plugin, DLL đang bị dùng thì từ chối cả cài lẫn gỡ, gói bị sửa bị từ chối, lỗi sau khi chép thì khôi phục bản cũ, kho font.
- `status` chạy thật trên máy này: đúng (đã cài 0.9.0, gói 0.9.2: `co_ban_moi`).
- Đầu cuối trên AutoCAD 2020 thật (phiên riêng, bản sao bản vẽ): mở cổng, `status` thấy cổng, `ping`, `scan` (Tcvn3 297), `plan.create` với `fontMap` qua `--json-file` (297 mục, font đích theo bảng), `plan.apply` hiện hộp thoại mang tên Kuro, sau Yes: `applied`, 297 mục, 0 lỗi, có sao lưu; quét lại 0 Tcvn3; `ping` pipe sai và tham số hỏng báo đúng lỗi kèm gợi ý; `shutdown`. MCP trong gói liệt kê 11 công cụ, `plan_create` có `fontMap` và `targetShxFont`.
- Sửa thêm khi làm gói: `pkttc_client.find_bridges` hết báo cổng giả do tệp cổng cũ sót lại (PID bị dùng lại) và đóng tệp đúng cách; tài liệu cổng `HUONG_DAN_KURO.md` viết lại (bản cũ còn hướng dẫn `NETLOAD` của giai đoạn thử).

## Chưa kiểm hoặc cần quyết định bên Kuro

- Chưa chép vào `goi\texthub` và chưa chạy `server\goi.py cai texthub`; chưa kiểm Kuro nạp skill, chạy script qua công cụ của Kuro.
- Kuro và AutoCAD phải cùng máy Windows, cùng tài khoản (cổng là named pipe cục bộ).
- Kho font không nằm trong gói: `ARIALUNI.ttf` (23 MB) thuộc bản quyền Microsoft Office. Máy không có Arial Unicode MS và không có kho: plugin vẫn đặt font đích mặc định là Arial Unicode MS (chưa có cơ chế tự lùi về Segoe UI).
- DLL chưa ký số: bản AutoCAD mới có thể hỏi trước khi nạp.
- Plugin đã cài trên máy anh vẫn là 0.9.0 (gói đã lên 0.9.2: sửa thư viện nối cổng và tài liệu, DLL không đổi).
