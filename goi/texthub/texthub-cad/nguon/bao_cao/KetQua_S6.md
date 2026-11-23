# Kết quả S6 - đóng gói bundle tự nạp

Trạng thái: ĐẠT (31/31 điều kiện), chờ anh duyệt. Ngày: 2026-11-21. Thư mục: `QLDA/99-Temp/texthub_s6/`.

## Kết luận

TextHub được đóng thành bundle Autodesk tự nạp khi AutoCAD 2020 khởi động, kèm trình cài một bước (cài, nâng cấp, gỡ), mã kiểm tra toàn vẹn và hướng dẫn. Đã kiểm cả việc tự nạp thật: cài vào thư mục ApplicationPlugins của anh, mở một phiên AutoCAD riêng, lệnh `PKTEXTSCAN` có sẵn mà không cần `NETLOAD`, rồi gỡ sạch. Trên máy anh hiện không còn gì từ lần thử (không còn bundle, không còn tệp cấu hình Kuro tạm); phiên AutoCAD đang làm việc của anh vẫn chạy.

## Sản phẩm (`dist/`, tạo bằng `dong_goi.ps1`)

| Tệp | Nội dung |
|---|---|
| `PKTTC.TextHub-0.6.0.zip` | Gói phát cho máy khác: bundle, `cai_dat.ps1`, `HUONG_DAN_CAI_DAT.md` |
| `PKTTC.TextHub.bundle/PackageContents.xml` | Khai báo bundle: chỉ AutoCAD 2020 (R23.1), Win64, `LoadOnAutoCADStartup`, 12 lệnh lấy từ mã nguồn, ProductCode và UpgradeCode cố định |
| `.../Contents/Windows/Pkttc.TextHub.dll` | Plugin (Core, Db, cổng trợ lý), mang phiên bản 0.6.0 |
| `.../Contents/Bridge/` | `pkttc_client.py`, `pkttc_mcp.py` cho trợ lý Kuro |
| `.../Contents/Docs/` | `HUONG_DAN_SU_DUNG.md`, `HUONG_DAN_KURO.md` |
| `.../MANIFEST.txt` | SHA-256 của từng tệp trong bundle |
| `cai_dat.ps1` | Trình cài (xem dưới) |

Phiên bản lấy từ tệp `VERSION` (0.6.0), nhúng vào DLL, `PackageContents.xml` và tên zip. Lệnh mới `PKTEXTABOUT` in phiên bản, đường dẫn DLL, danh sách lệnh, số tệp kho font, trạng thái cổng.

## Cài đặt

```powershell
powershell -File cai_dat.ps1                # cài hoặc nâng cấp
powershell -File cai_dat.ps1 -WhatIf        # chỉ xem
powershell -File cai_dat.ps1 -Uninstall     # gỡ
powershell -File cai_dat.ps1 -FontStore "D:\Kho-Font"   # kèm cấu hình kho font (chỉ khi chưa có)
```

- Chép vào `%APPDATA%\Autodesk\ApplicationPlugins\PKTTC.TextHub.bundle`; AutoCAD tự nạp ở lần khởi động sau.
- Kiểm tra `MANIFEST.txt` trước khi chép; gói bị sửa thì từ chối cài.
- Nâng cấp giữ bản cũ ở `PKTTC.TextHub.old` (không có đuôi `.bundle` nên AutoCAD không nạp nhầm); cài lỗi thì khôi phục bản cũ.
- DLL đang bị AutoCAD dùng thì báo "AutoCAD đang dùng TextHub" và không đụng vào bản đang có (cả cài lẫn gỡ).
- Không ghi registry, không đổi thiết lập AutoCAD, không cài font, không dùng mạng (đã kiểm bằng quét mã script).
- Gỡ giữ lại cấu hình kho font, nhật ký cổng, bản sao lưu bản vẽ.

## Kiểm thử (`run_tests_package.ps1`, 31/31)

| Nhóm | Điều kiện đã đạt |
|---|---|
| A. Nội dung gói (14) | AppVersion khớp VERSION; GUID hợp lệ; chỉ R23.1 Win64; tự nạp khi khởi động; ModuleName trỏ tệp có thật; 12 lệnh trong XML khớp mã nguồn, không có lệnh kiểm thử; MANIFEST đúng và đủ tệp; DLL mang đúng phiên bản; zip đủ thành phần; trình cài không có lệnh ghi registry; tài liệu không có dấu gạch ngang dài, không ký tự điều khiển lạ, không rỗng |
| B. Trình cài từ zip giải nén, thư mục tạm (11) | `-WhatIf` không đổi gì; cài mới; DLL khớp gốc; cấu hình kho font sẵn có không bị ghi đè; nâng cấp giữ bản cũ; bản cũ không có đuôi `.bundle`; gói bị sửa bị từ chối; DLL đang bị dùng thì cả cài và gỡ đều từ chối mà bản đang có nguyên vẹn; gỡ sạch; gỡ lần hai báo "chưa cài" |
| C. Tự nạp thật (6) | Cài vào ApplicationPlugins mặc định; AutoCAD khởi động không `NETLOAD` mà `PKTEXTSCAN` chạy và ra đúng 20 mục; gỡ sạch; gỡ luôn tệp cấu hình Kuro do trình cài tạo; phiên AutoCAD của anh vẫn chạy |

## Giới hạn

- Chỉ AutoCAD 2020. DLL tham chiếu API 23.1 nên gói không tự nạp trên bản khác; chưa thử bản khác.
- Chưa thử với `SECURELOAD` bật (máy anh đang tắt): khi bật, AutoCAD có thể hỏi có nạp ứng dụng không; hướng dẫn nêu cách chọn Always Load. DLL chưa ký số.
- Chưa thử trên máy khác. Cần .NET Framework 4.7 trở lên (đã có cùng AutoCAD 2020) và Python 3 chỉ khi dùng trợ lý Kuro.
- Cửa sổ giao diện (WPF) chưa làm: TextHub dùng lệnh và hộp thoại; theo đề xuất ban đầu đây là phần tùy chọn.
- `PKTEXTABOUT` kiểm bằng cách khởi động phiên thật nhưng nội dung dòng lệnh không đọc được từ phiên GUI; phần lệnh, phiên bản đã kiểm gián tiếp (phiên bản DLL, danh sách lệnh trong XML).
- Mã nguồn dựng gói nằm ở ba thư mục (`texthub_s1` Core, `texthub_s5` Db, `texthub_s6` đóng gói); chưa gom về một cây mã nguồn.
- Chưa cài vào máy anh: bundle chỉ được cài rồi gỡ trong lúc thử. Muốn dùng: đóng AutoCAD, chạy `dist\cai_dat.ps1`, mở lại AutoCAD.

## Tệp

- `dong_goi.ps1`, `VERSION`, `src/About.cs`, `package/` (`cai_dat.ps1`, `HUONG_DAN_CAI_DAT.md`, `HUONG_DAN_SU_DUNG.md`).
- `run_tests_package.ps1`, `tests/package_test.py`.
- `dist/`: sản phẩm đóng gói (tạo lại bằng `dong_goi.ps1`).
