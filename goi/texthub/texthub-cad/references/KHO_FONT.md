# Kho font và font Unicode đi kèm gói

Máy mới cần đúng font thì mới đổi và hiển thị được chữ Unicode. Gói mang sẵn:

| Thứ | Nằm ở | Ai nạp |
|---|---|---|
| SHX Unicode (`uv-abc.shx`, `3T-Unicode.shx`, `VN_UNI.shx`, `uniSONHA.shx`, `unicode.shx`, `VnRomandU`, `VnSimpleU`, `VnTxtU`, `VnitalicU`, các bản Arial/Tahoma/Times/Verdana/Courier New Unicode...) | `payload/PKTTC.TextHub.bundle/Contents/Fonts` | AutoCAD tự nhận: `PackageContents.xml` khai `SupportPath="./Contents/Fonts"`, không sửa tùy chọn của AutoCAD |
| Kho font đầy đủ (SHX, TTF, ZTrungTen: 361 tệp) | `payload/KhoFont` | `texthub_setup.py install` chép vào `%LOCALAPPDATA%\PKTTC\KhoFont` và thêm vào `%LOCALAPPDATA%\PKTTC\fontstore.txt`; bảng PKTEXTUI thẻ **Kho font** dùng để cài font thiếu |
| Font TrueType `Arial Unicode MS` (`TTF\ARIALUNI.ttf`) | trong `payload/KhoFont` | `texthub_setup.py fonts-install` (hoặc nút "Cài font đích thiếu từ kho" trong bảng): chép vào `%LOCALAPPDATA%\Microsoft\Windows\Fonts` và ghi registry `HKCU\...\Fonts` cho người dùng hiện tại; cần mở lại AutoCAD |

## Lưu ý bản quyền

`ARIALUNI.ttf` (Arial Unicode MS) là font đi kèm Microsoft Office. Chỉ cài trên máy có giấy phép Office. Máy không có: dùng `Segoe UI` hoặc `Calibri` làm font đích TrueType (đã in thử, vẽ đủ `Ả Ế ọ Ố Ỡ Ơ Ư`); bỏ tệp này khỏi `payload/KhoFont/TTF` trước khi phát cho người ngoài tổ chức nếu cần.

## Việc Kuro làm

1. `texthub_setup.py status`: đọc `kho_font_goi`, `kho_font_da_cai`, `font_can_thiet`.
2. `font_can_thiet[].da_cai` là `false` và `co_trong_kho` là `true`: hỏi người dùng, đồng ý thì `texthub_setup.py fonts-install`.
3. Cấu hình kho riêng của người dùng: `texthub_setup.py fontstore --set "<thư mục>"` (thay cho kho đi kèm).
4. Gỡ: `texthub_setup.py uninstall --xoa-kho-font` xóa cả kho đã chép (chỉ khi có dấu `.texthub-khofont` do gói tạo; không xóa thư mục của người dùng).
5. `fonts-install` không có lệnh gỡ riêng: font nằm ở thư mục font của người dùng, gỡ bằng Cài đặt Windows, Cá nhân hóa, Phông chữ.

## SupportPath của bundle: đã thử trên AutoCAD 2020 thật

- Với hồ sơ AutoCAD (profile) bình thường, lần mở đầu tiên AutoCAD tự thêm `...\PKTTC.TextHub.bundle\Contents\Fonts` vào Support File Search Path của profile đó (ghi vào registry của profile, nên còn lại sau khi gỡ plugin; có thể xóa tay trong Options, Files, Support File Search Path).
- Trên profile mặc định của máy anh Nghĩa (đường dẫn hỗ trợ đã dài 4.221 ký tự) AutoCAD KHÔNG thêm đường dẫn của bundle. Chưa xác định nguyên nhân (nghi do giới hạn độ dài). Máy như vậy: các SHX Unicode vẫn dùng được nếu đã nằm trong thư mục font của AutoCAD (máy này đã có sẵn); nếu thiếu thì dùng bảng PKTEXTUI, thẻ Kho font, nút "Cài font đích thiếu từ kho" (chép vào thư mục font của AutoCAD), hoặc chép SHX từ `Contents/Fonts` của bundle.

