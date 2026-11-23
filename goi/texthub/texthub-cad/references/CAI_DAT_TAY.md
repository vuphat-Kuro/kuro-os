> Trong goi Kuro, plugin duoc cai bang `python scripts/texthub_setup.py install`. Tai lieu nay mo ta cach cai TAY bang PowerShell (`payload/cai_dat.ps1`), de dung khi can cai ma khong qua Kuro.

# Cài đặt PKTTC TextHub

PKTTC TextHub là plugin của phòng Kỹ thuật - Thi công cho AutoCAD 2020: quét mọi loại chữ trong bản vẽ, đổi chữ TCVN3 và VNI sang Unicode, quản lý font và style, và có cổng để trợ lý (Kuro) điều khiển.

## Yêu cầu

- Windows 64 bit, AutoCAD 2020 (bản 23.1). Chưa thử trên phiên bản AutoCAD khác nên gói không tự nạp trên các phiên bản đó.
- Python 3 chỉ cần nếu dùng trợ lý Kuro.

## Cài đặt (một bước)

1. Giải nén tệp `PKTTC.TextHub-<phiên bản>.zip` vào một thư mục bất kỳ.
2. Đóng AutoCAD.
3. Mở PowerShell trong thư mục vừa giải nén và chạy:

```powershell
powershell -File cai_dat.ps1
```

   Nếu PowerShell từ chối chạy tệp: `powershell -ExecutionPolicy Bypass -File cai_dat.ps1`.
4. Mở AutoCAD. TextHub tự nạp và in một dòng thông báo. Gõ `PKTEXTABOUT` để xem phiên bản và danh sách lệnh.

Muốn xem trước việc cài đặt sẽ làm gì mà chưa thay đổi gì: thêm `-WhatIf`.

## Thư mục kho font (tùy chọn)

Lệnh `PKTEXTFONT` đối chiếu font của bản vẽ với kho font của phòng. Cài kèm cấu hình kho:

```powershell
powershell -File cai_dat.ps1 -FontStore "D:\Duong-dan\Kho-Font"
```

Cấu hình chỉ được tạo khi chưa có, và không ghi đè cấu hình sẵn có. Có thể sửa sau trong tệp `%LOCALAPPDATA%\PKTTC\fontstore.txt` (mỗi dòng một thư mục).

## Nâng cấp

Đóng AutoCAD rồi chạy lại `cai_dat.ps1` từ gói mới. Bản cũ được giữ lại trong thư mục `PKTTC.TextHub.old` cạnh bản mới; nếu cài lỗi, bản cũ được khôi phục tự động.

## Gỡ cài đặt

Đóng AutoCAD rồi chạy:

```powershell
powershell -File cai_dat.ps1 -Uninstall
```

Lệnh gỡ giữ lại cấu hình kho font, nhật ký cổng trợ lý và các bản sao lưu bản vẽ (thư mục `_backup` cạnh bản vẽ).

## Cài đặt làm gì và không làm gì

- Chép bundle vào `%APPDATA%\Autodesk\ApplicationPlugins\PKTTC.TextHub.bundle`. AutoCAD tự nạp mọi bundle trong thư mục này khi khởi động.
- Tạo tệp mẫu cấu hình cho trợ lý tại `%LOCALAPPDATA%\PKTTC\kuro_mcp_config.json` (đường dẫn thật tới `pkttc_mcp.py`).
- Không ghi registry, không đổi thiết lập AutoCAD, không cài font, không kết nối mạng.
- Mỗi tệp trong bundle có mã SHA-256 trong `MANIFEST.txt`; trình cài kiểm tra mã trước khi chép và từ chối cài nếu có tệp sai.

## Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| "AutoCAD đang dùng TextHub" khi cài hoặc gỡ | Đóng hết cửa sổ AutoCAD rồi chạy lại |
| Mở AutoCAD không thấy dòng thông báo, `PKTEXTABOUT` báo lệnh không tồn tại | Kiểm tra bản AutoCAD (chỉ 2020); kiểm tra thư mục `%APPDATA%\Autodesk\ApplicationPlugins\PKTTC.TextHub.bundle` có tệp `PackageContents.xml`; nếu AutoCAD hỏi có nạp ứng dụng không, chọn Always Load |
| `NETLOAD` báo lỗi tham chiếu tệp | Mở AutoCAD sau khi cài bằng `cai_dat.ps1` thay vì NETLOAD thủ công |
| Cổng trợ lý không kết nối được | Gõ `PKTEXTBRIDGE`, rồi `YES` trong AutoCAD; xem hướng dẫn `Contents\Docs\HUONG_DAN_KURO.md` |

## Tệp và thư mục TextHub tạo ra

| Vị trí | Nội dung |
|---|---|
| `%APPDATA%\Autodesk\ApplicationPlugins\PKTTC.TextHub.bundle` | Plugin (do `cai_dat.ps1` tạo) |
| `%LOCALAPPDATA%\PKTTC\` | Cấu hình kho font, tệp kết quả quét và kế hoạch mặc định (`out`), nhật ký cổng trợ lý (`bridge`) |
| `<thư mục bản vẽ>\_backup\YYYYMMDD\` | Bản sao lưu bản vẽ trước mỗi lần ghi, nhật ký `_log.md` |
