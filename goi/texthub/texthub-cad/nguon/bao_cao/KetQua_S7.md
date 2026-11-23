# Kết quả S7 - bảng PKTEXTUI và menu KTTC (PKTTC TextHub 0.7.0)

Ngày 2026-11-23. Trạng thái: DỰ THẢO - CHỜ DUYỆT. Bản 0.7.0 đã đóng gói (`texthub_s6\dist\PKTTC.TextHub-0.7.0.zip`), CHƯA cài vào AutoCAD của anh (đang mở, giữ DLL 0.6.3).

## Làm gì

- **Lệnh `PKTEXTUI`:** mở bảng PaletteSet + WinForms, làm việc trên bản vẽ đang hiện, không chặn AutoCAD. 5 thẻ: Quét, Đổi chữ, Font, Kho font, Trợ lý.
- **Menu KTTC** cuối thanh menu: KTTC > Text > Convert Font, 15 dòng (12 lệnh và 3 đường kẻ), `PKTEXTUI` ở dòng đầu, mỗi dòng có giải thích ngắn trên nhãn và mô tả dài ở thanh trạng thái. Tạo bằng mã lúc AutoCAD khởi động (COM động), không sửa `NK-WorkSpace.cuix` trên Drive của anh.
- Mã nằm ở `texthub_s5\src\Db\`: `UiHost.cs` (lệnh, PaletteSet, nhật ký `ui.log`, cài menu) và `UiPanel.cs` (5 thẻ). Gọi lại Ops, PlanBuilder, FontReporter, StyleOps, Bridge, FontStore có sẵn.

## Các thẻ

| Thẻ | Chức năng |
|---|---|
| Quét | Quét bản vẽ, tóm tắt theo bảng mã và cờ, lọc, bấm đúp để chọn và phóng tới chữ |
| Đổi chữ | Chọn font đích (cảnh báo nếu font không vẽ được chữ Việt trên AutoCAD), lập kế hoạch, lưới xem trước cũ và mới bằng font thật, bỏ chọn từng mục, áp dụng (xác nhận, sao lưu, một bước `U`) |
| Font | Báo cáo font, thay font thiếu, dọn style không dùng (đều xác nhận và sao lưu) |
| Kho font | Thư mục và số tệp kho, mở thư mục, lưu script cài font thiếu (chỉ xem) |
| Trợ lý | Mở hoặc đóng cổng Kuro (xác nhận), nhật ký audit |

Việc GHI chạy qua lệnh nội bộ `PKTEXTUIEXEC` để có đúng một bước UNDO (cùng cách cổng Kuro dùng).

## Đã kiểm (trên AutoCAD giao diện thật, phiên riêng của em, bản sao của bản vẽ Đà giáo xà mũ)

- Bảng mở, 5 thẻ hiện đúng. Quét: 2.125 mục, Ascii 1.491, Unicode 337, Tcvn3 297, cờ legacy 297 và mismatch 1 (khớp kết quả quét trước).
- Đổi chữ: lập kế hoạch 297 mục sang Segoe UI; cột xem trước vẽ chữ cũ bằng font TCVN3 gốc và chữ mới bằng Segoe UI; áp dụng hiện hộp thoại xác nhận, bấm Yes thì sao lưu (`_backup`) và đổi 297 mục, ghi trạng thái.
- Font: 25 font, 25 có sẵn; Dọn style: liệt kê 23 style, bấm No thì bản vẽ không đổi; Thay font thiếu: báo không có gì cần thay.
- Kho font: 357 tệp trong 1 thư mục. Trợ lý: mở cổng (có xác nhận), pipe xuất hiện; Đóng cổng, pipe biến mất; nhật ký hiện.
- Menu: tự kiểm bằng cách đọc lại thanh menu: trên thanh menu = True, số mục thanh menu từ 13 lên 14, Convert Font có 15 dòng, dòng đầu `PKTEXTUI`, dòng cuối `PKTEXTABOUT`.
- Kiểm thử mã: Core 138, font 26, áp dụng 27, cổng vòng lặp 47 đạt. Gói: nhóm nội dung và trình cài 25/25 đạt; nhóm tự nạp thật tự dừng vì máy đã cài bundle.

## Chưa kiểm hoặc còn hạn chế

- Chưa cài 0.7.0 vào AutoCAD của anh và chưa thấy menu trên thanh menu thật của anh. Em chỉ xác nhận qua đọc lại thanh menu của phiên thử (cùng hồ sơ người dùng và cùng tệp menu chính `NK-WorkSpace.cuix`).
- Chưa bấm thử từng dòng menu để chạy lệnh (macro dạng `^C^C<lệnh> `).
- Menu chỉ hiện khi thanh menu đang bật (`MENUBAR`=1) và chỉ nạp khi AutoCAD khởi động.
- Bảng nổi, chưa tự dock vào cạnh phải (có thể kéo thả để dock); kích thước mặc định 560x720.
- Bấm đúp phóng tới chữ chưa thử tay (chỉ chọn qua `SetImpliedSelection` rồi `ZOOM O`); chữ trong định nghĩa block chỉ báo vị trí.
- Cổng Kuro vẫn gắn với bản vẽ lúc bật, chưa theo bản vẽ đang hiện.
- Kiểm thử giao diện chạy bằng điều khiển Win32 từ ngoài (nút, hộp thoại, chụp riêng cửa sổ bảng), không có bộ kiểm thử tự động nằm trong gói.

## Cài đặt

Đóng AutoCAD (lưu bản vẽ), rồi chạy `powershell -File "...\texthub_s6\dist\cai_dat.ps1"`; mở lại AutoCAD, gõ `PKTEXTUI` hoặc chọn menu KTTC.

## Cập nhật 2026-11-23: bảng ánh xạ font nguồn sang font đích (bản 0.8.0)

Anh góp ý: danh sách font đích quá ít, không có SHX, cảnh báo đỏ khó hiểu; muốn liệt kê font nguồn và chọn font đích cho từng loại.

- Thẻ **Đổi chữ** làm lại: **Quét font nguồn** liệt kê từng loại font cũ có chữ cần đổi kèm số mục; mỗi dòng chọn font đích riêng; font mặc định và nút **Áp cho tất cả**; cột ghi chú về font đích.
- Danh sách font đích đầy đủ: mọi TrueType đã cài (trừ font TCVN3/VNI cũ), sau đó SHX Unicode (kho font, thư mục Fonts của AutoCAD, Style đang dùng trong bản vẽ; chỉ SHX có header `unifont`).
- Kế hoạch có `newFont` cho từng mục và `fontMap` trong tùy chọn; mỗi font đích một style đặt theo tên font (`Segoe UI`, `Calibri`, `VN_UNI`...), dùng lại style cùng tên đã dùng đúng font (TrueType so tên họ, SHX so tên tệp). Bản vẽ áp dụng qua `Applier` hỗ trợ style SHX (đặt `FileName`).
- Trợ lý (Kuro): `pkttc_plan_create` nhận thêm `fontMap`.
- Lưu ý đỏ về Arial: giữ nhưng nói rõ căn cứ ("em in thử bằng AutoCAD 2020 trên máy này, kiểu thường của font này không vẽ Ả Ế ọ Ố Ỡ Ơ Ư"), chỉ hiện ở dòng ghi chú, không chặn việc chọn.
- Đã kiểm: PlanTests 17 (có 8 ca ánh xạ font), Core, font 26, áp dụng 27 đạt; cổng vòng lặp thêm ca `fontMap` (`.VnTime` sang Calibri, tạo đúng style Calibri) đạt 3/3 lần chạy trong một đợt và chập chờn ở các lần khác (xem hạn chế). Trên AutoCAD giao diện thật (phiên riêng): bảng liệt kê 6 font nguồn của bản vẽ Đà giáo xà mũ (`.VnAvantH` 246, `.VnArialH` 27, `vntime.shx` 10, `.VnArial NarrowH` 8, `vn-abc.shx` 5, `VN_UNI.shx` 1); đặt font đích `VN_UNI.shx` cho tất cả, lập kế hoạch 297 mục và áp dụng thành công, AutoCAD không treo.

Hạn chế: kiểm thử tự động cổng vòng lặp (accoreconsole) chập chờn ở khoảng 1 trong 3 lần (một lần ngay ở bước ping MCP, các lần khác sau khi áp dụng); nguyên nhân chưa xác định, ca SHX trong accoreconsole từng làm tăng tần suất nên em chuyển sang kiểm SHX trên AutoCAD giao diện. Chưa chọn từng font đích khác nhau cho từng dòng bằng chuột trên giao diện (em chỉ đặt chung rồi áp cho tất cả); ánh xạ nhiều font đã kiểm bằng PlanTests và cổng. Chưa cài 0.8.0 vào AutoCAD của anh.

## Cập nhật 2026-11-23 (2): font Unicode ghim đầu và mặc định theo loại font nguồn (bản 0.9.0)

- **Kho font:** thêm `TTF\ARIALUNI.ttf` (Arial Unicode MS, 23 MB, chép từ `C:\Windows\Fonts` của máy anh Nghĩa; thuộc Microsoft Office, chỉ dùng trong phòng trên máy có giấy phép). `FontStore.Find("Arial Unicode MS")` tìm được qua bí danh tên tệp `arialuni`. `_danh_sach.csv` và `README.md` đã sao lưu vào `_backup\20261123` trước khi sửa.
- **Ghim đầu danh sách font đích:** `Arial Unicode MS`, `uv-abc.shx`, `3T-Unicode.shx` (kể cả khi chưa cài trên máy), rồi Segoe UI, Calibri, rồi các TrueType khác, rồi SHX Unicode khác. Đã đọc lại 2 ô chọn trên AutoCAD thật: 3 font ghim đứng ở vị trí 0, 1, 2.
- **Mặc định theo loại font nguồn:** nguồn TrueType sang `Arial Unicode MS`, nguồn SHX sang `uv-abc.shx` (hai ô "Nguồn TrueType" và "Nguồn SHX", nút "Đặt lại theo mặc định"). Mặc định này cũng áp cho `PKTEXTPLAN`, `PKTEXTFIX` và trợ lý Kuro (`targetFont`, `targetShxFont`).
- **Cài font từ kho:** font đích chưa cài mà kho có thì hiện nút "Cài font đích thiếu từ kho": hộp thoại xác nhận, rồi chạy script cài (chép vào `%APPDATA%\PKTTC\Fonts` và cài TrueType cho người dùng hiện tại bằng `-Apply -RegisterFonts`); cần mở lại AutoCAD. Em đã kiểm phát hiện font thiếu và hộp thoại xác nhận (trả lời No); CHƯA chạy thật bước cài.
- **Đã kiểm:** PlanTests 19, font 26, áp dụng 27 (nguồn SHX `txt.shx` đi `uv-abc`, nguồn TrueType đi `Arial Unicode MS_2`), cổng vòng lặp đạt 2 trong 3 lần; trên AutoCAD giao diện thật: bảng chọn sẵn đúng theo loại font nguồn.
