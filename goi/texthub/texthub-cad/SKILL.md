---
name: texthub-cad
description: "CHỈ dùng khi người dùng muốn ĐỔI chữ tiếng Việt cũ (TCVN3, VNI, font .Vn*, vn-abc, vntime...) sang Unicode, KIỂM chữ lỗi font hoặc font thiếu, hoặc dọn style chữ trong bản vẽ DWG đang mở trong AutoCAD (plugin PKTTC TextHub). Cũng dùng khi người dùng hỏi plugin này đã cài chưa hoặc muốn cài, gỡ, cập nhật. Không dùng để vẽ hoặc xuất DXF (đó là skill autocad-pkttc) và không dùng khi chỉ hỏi nội dung bản vẽ."
---

# Đổi chữ cũ sang Unicode trong AutoCAD (PKTTC TextHub)

Plugin chạy TRONG AutoCAD của người dùng. Kuro điều khiển qua cổng cục bộ (named pipe), không đọc file DWG trực tiếp.
Mọi script nằm ở `scripts/` của skill này; chạy bằng `python`. Tài liệu chi tiết: `references/`.

## Bước 0 - Plugin đã cài chưa

```
python scripts/texthub_setup.py status
```
Đọc `trang_thai` và `thong_bao`, nói lại cho người dùng bằng lời thường (không dán nguyên JSON):

| `trang_thai` | Việc làm |
|---|---|
| `chua_cai` hoặc `co_ban_moi` | Hỏi người dùng có muốn cài/cập nhật không. Đồng ý thì `python scripts/texthub_setup.py install`. |
| `da_cai` | Sang bước 1. |
| `khong_ho_tro` | Nói rõ bản AutoCAD nào chưa được hỗ trợ (đọc `autocad[].ly_do`). KHÔNG thử cài. |
| `khong_co_autocad` | Báo máy không có AutoCAD đầy đủ. |
| `loi` | Báo `thong_bao`, dừng. |

- `can_dong_autocad_de_cai: true` hoặc `install` trả `can_dong_autocad`: nhờ người dùng LƯU rồi ĐÓNG AutoCAD, sau đó chạy lại. Không đóng AutoCAD thay họ.
- Cài xong báo: **mở lại AutoCAD** để plugin tự nạp; gõ `PKTEXTABOUT` kiểm tra; menu **KTTC > Text > Convert Font**; lệnh `PKTEXTUI` mở bảng.
- `install` cũng chép **kho font** của gói vào `%LOCALAPPDATA%\PKTTC\KhoFont` và thêm vào `fontstore.txt` (không ghi đè cấu hình sẵn có); `--no-fonts` để bỏ qua. SHX Unicode (`uv-abc.shx`, `3T-Unicode.shx`, `VN_UNI.shx`...) đi kèm bundle và AutoCAD tự nhận qua Support File Search Path.
- `status.font_can_thiet`: font TrueType cần cho font đích mặc định (Arial Unicode MS). `da_cai: false` và `co_trong_kho: true` thì hỏi người dùng có cài không; đồng ý thì `python scripts/texthub_setup.py fonts-install` (cài cho người dùng hiện tại, ghi registry HKCU, cần mở lại AutoCAD). Arial Unicode MS thuộc Microsoft Office: chỉ cài trên máy có giấy phép; không có thì dùng Segoe UI làm font đích.
- Gỡ: `python scripts/texthub_setup.py uninstall` (chỉ khi người dùng yêu cầu); `--xoa-kho-font` xóa cả kho font do gói cài.
- Kho font riêng của người dùng: chưa cấu hình thì hỏi đường dẫn rồi `python scripts/texthub_setup.py fontstore --set "<thư mục>"`.

## Bước 1 - Mở cổng (người dùng làm)

Người dùng mở đúng bản vẽ cần xử lý, rồi trong AutoCAD gõ `PKTEXTBRIDGE`, gõ `yes`. (Hoặc bảng `PKTEXTUI`, thẻ **Trợ lý**, nút **Mở cổng Kuro**.)
Cổng gắn với bản vẽ ĐANG HIỆN lúc mở: đổi bản vẽ thì đóng cổng (`PKTEXTBRIDGESTOP`) và mở lại. Không tự mở cổng thay người dùng.

```
python scripts/texthub_cad.py ping
```
Lỗi `no-bridge` hoặc `connect`: cổng chưa mở, nhắc người dùng như trên.

## Bước 2 - Quét và lập kế hoạch (chỉ đọc)

```
python scripts/texthub_cad.py scan
python scripts/texthub_cad.py fonts
python scripts/texthub_cad.py plan.create
```
- `scan`: đọc `summary.byCharset` (Tcvn3, Vni, Unicode, Ascii) và `byFlag`. Không có chữ Tcvn3/Vni thì báo "không có gì cần đổi".
- `plan.create` trả `planId`, `count`, `skipped` (lý do bỏ qua), `sample`. Chưa sửa bản vẽ.
- Font đích mặc định: nguồn TrueType sang **Arial Unicode MS**, nguồn SHX sang **uv-abc.shx**. Đổi cho từng font nguồn: ghi tham số vào một tệp JSON (UTF-8) như `{"fontMap":{".VnAvantH":"Segoe UI","vn-abc.shx":"VN_UNI.shx"}}` rồi gọi `plan.create --json-file <tệp>`; cũng có `targetFont`, `targetShxFont`. Font đích SHX phải là SHX Unicode. LUÔN dùng `--json-file` khi tham số có dấu cách hoặc dấu nháy (dòng lệnh Windows làm hỏng dấu nháy trong `--json`).
- Arial thường (không phải Arial Unicode MS), Tahoma, Verdana, Times thường KHÔNG vẽ được `Ả Ế ọ Ố Ỡ Ơ Ư` trên AutoCAD 2020 (đã in thử): không chọn các font này làm font đích.
- Font đích chưa cài trên máy (ví dụ Arial Unicode MS khi không có Office): nói rõ, gợi ý Segoe UI hoặc cài từ kho font (bảng PKTEXTUI, nút "Cài font đích thiếu từ kho").

## Bước 3 - Báo cáo rồi xin phép

Trước khi ghi, nói với người dùng bằng lời: bao nhiêu mục sẽ đổi, bao nhiêu bị bỏ qua và vì sao, font đích, vài mẫu `oldRaw` và `newText`.
Chữ ở font HOA TCVN3 (`.VnAvantH`, `.VnArialH`, `.VnTimeH`...) sẽ thành chữ HOA Unicode vĩnh viễn: nói rõ khi có.

## Bước 4 - Áp dụng (người dùng bấm Yes trong AutoCAD)

```
python scripts/texthub_cad.py plan.apply --json-file <tep_tham_so.json> --timeout 300
```
với tệp là `{"planId":"<mã>","note":"Doi chu cu sang Unicode"}`.

- Lệnh CHỜ người dùng bấm Yes hoặc No trong hộp thoại AutoCAD (hiện tên Kuro, mã kế hoạch, số mục). Không thể tự duyệt thay họ.
- `status: rejected`: dừng, hỏi lại người dùng, KHÔNG gọi lại tự động. `het_gio`: người dùng chưa trả lời, không gọi lại.
- Chỉ gửi `planId`; mỗi kế hoạch chỉ áp dụng một lần.
- Sau khi áp dụng báo đúng `ok`, `errors`, `backup`: **bản vẽ chưa lưu**, gõ `U` để hoàn tác một bước, bản sao lưu nằm ở đường dẫn trong `backup`.
- Quét lại (`scan`) để xác nhận `Tcvn3` và `Vni` đã hết (trừ mục bị bỏ qua có lý do).
- Font/style: `fontsub.plan` rồi `fontsub.apply` (thay font Style thiếu), `purge.plan` rồi `purge.apply` (dọn style không dùng), cùng cách hỏi và chờ Yes.

## Luật cứng

- Không bao giờ nói "đã đổi xong" khi chưa thấy `status: applied` và kết quả quét lại.
- Không tự sửa file DWG ngoài AutoCAD, không đóng AutoCAD, không bấm thay người dùng.
- Mục DIMENSION chữ kiểu cũ chưa được đổi; mục trên layer khóa, mục có field, mục không chắc chắn bị bỏ qua và được liệt kê.
- Chỉ AutoCAD đầy đủ bản được liệt kê trong `ho_tro_series` của `status`. AutoCAD LT, BricsCAD, ZWCAD không dùng được.
- Cổng chỉ nối được khi Kuro và AutoCAD chạy trên CÙNG máy Windows, cùng tài khoản người dùng.
