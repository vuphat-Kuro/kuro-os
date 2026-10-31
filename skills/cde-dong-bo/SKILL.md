---
name: "CDE - Đồng bộ hồ sơ"
description: "Thao tác CDE qua API (ACC/BIM 360, Trimble Connect): tải hồ sơ hàng loạt, document register, Issue/RFI ra Excel, tên ISO 19650."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Đồng bộ và kiểm soát hồ sơ trên CDE

## Khi nào dùng

Làm việc với môi trường dữ liệu chung (CDE) qua API thay vì bấm tay trên trình duyệt - liệt kê dự án và cây thư mục trên ACC/BIM 360, tải hàng loạt tài liệu về hoặc lên, xuất bảng đăng ký tài liệu (document register), kéo danh sách Issue/RFI ra Excel để làm báo cáo, kiểm tra và đổi tên file theo ISO 19650, lập ma trận trách nhiệm thông tin. Cũng kết nối được CDE nội bộ có REST API bằng file cấu hình. Dùng skill này khi người dùng nhắc tới CDE, ACC, BIM 360, Autodesk Docs, Trimble Connect, tải hồ sơ lên/xuống, đăng ký tài liệu, issue, RFI, quy ước đặt tên, ISO 19650, đồng bộ hồ sơ, hoặc nói "tải 200 bản vẽ về mà bấm từng cái", "làm báo cáo issue tuần này", "tên file bị trả về vì sai quy ước", "kiểm tra xem trên CDE có đủ hồ sơ chưa".

Việc trên CDE tốn thời gian không phải vì khó, mà vì **số lượng**: tải 200 bản
vẽ, đổi tên 80 file, tổng hợp issue mỗi tuần. Đây là những việc gọi API xong
trong vài phút.

## Trước tiên: bảo mật

Không bao giờ viết token, mật khẩu, client secret vào script hay vào file
quy trình. Khai báo qua biến môi trường hoặc file `.env` (thêm `.env` vào
`.gitignore`):

```powershell
$env:APS_CLIENT_ID     = "..."
$env:APS_CLIENT_SECRET = "..."
```

Nếu người dùng dán token vào cuộc trò chuyện, nhắc họ thu hồi và tạo lại - đã
lộ ra ngoài thì coi như hỏng.

Đừng tự tay tải lên, xóa hay sửa dữ liệu trên CDE thay người dùng khi họ chưa
nói rõ. Đọc dữ liệu thì thoải mái; ghi lên máy chủ thì hỏi trước. Mọi lệnh có
tác động đều có cờ `--thu` để chạy thử trước.

## Hai công cụ

**`scripts/cde.py`** - nói chuyện với máy chủ:

| Lệnh | Việc |
|---|---|
| `du-an` | Liệt kê hub và dự án, lấy mã dự án để dùng cho lệnh sau |
| `cay` | Duyệt cây thư mục, xem có gì trong đó |
| `dang-ky` | Xuất bảng đăng ký tài liệu ra Excel - ai sửa, lúc nào, bản mấy |
| `tai-ve` | Tải hàng loạt, lọc theo đuôi file, giữ nguyên cấu trúc thư mục |
| `tai-len` | Tải hàng loạt lên một thư mục |
| `issue` | Kéo Issue/RFI ra Excel, kèm thống kê theo trạng thái |

**`scripts/iso19650.py`** - kiểm soát trước khi hồ sơ lên CDE:

| Lệnh | Việc |
|---|---|
| `kiem-tra` | Soát tên file theo quy ước, bắt lỗi dấu cách, dấu tiếng Việt, thiếu trường, thiếu mã trạng thái |
| `dat-ten` | Sinh tên chuẩn từ bảng Excel các trường |
| `doi-ten` | Đổi tên hàng loạt theo bảng ánh xạ, có `--thu` |
| `dang-ky` | Quét thư mục trên máy → bảng đăng ký, phát hiện file trùng ruột khác tên |
| `ma-tran` | Sinh khung ma trận trách nhiệm thông tin (bộ môn × giai đoạn) |

## Chỗ hay gây lỗi 404 trên ACC

Mã dự án tồn tại ở hai dạng và **không dùng lẫn được**:

- Data Management API (thư mục, tài liệu) dùng mã **có** tiền tố `b.`
- Issues API và các API xây dựng khác dùng mã **không có** `b.`

Công cụ tự xử lý, nhưng khi gỡ lỗi tay thì nhớ điều này trước tiên.

Lỗi 403 thường không phải sai token mà là **ứng dụng chưa được cấp quyền vào dự
án**: ACC Account Admin → Custom Integrations → thêm Client ID. Kiểm tra chỗ này
trước khi nghi ngờ code.

## Quy ước tên ISO 19650

Mặc định:
```
<Dự án>-<Đơn vị>-<Khu>-<Cao độ>-<Loại>-<Bộ môn>-<Số hiệu>[-<Trạng thái>][-<Rev>]
HCMTLMT-A2Z-KM12-ZZ-DR-C-0001-S3-P01.pdf
```

Mỗi dự án có quy ước riêng - hỏi người dùng quy ước của dự án họ đang làm rồi
truyền qua `--mau`, đừng áp mặc định vào rồi báo cả trăm file sai.

Mã trạng thái (S0–S7, A, B, CR) và mã loại tài liệu (DR, M3, RP, SP...) nằm
trong `references/quy-uoc-ten-va-ma.md`.

Lệnh `kiem-tra` còn phát hiện **một số hiệu xuất hiện nhiều lần** - dấu hiệu
bản cũ chưa gỡ, và đây là nguyên nhân kinh điển khiến hiện trường thi công theo
bản vẽ đã bị thay thế.

## CDE nội bộ, không phải ACC

Dùng `--nguon rest --cau-hinh <file.json>`. File cấu hình mô tả đường đăng
nhập, đường lấy danh sách, đường tải lên - xem mẫu và cách dò endpoint trong
`references/cau-hinh-cde.md`.

Cách dò nhanh: mở CDE trên trình duyệt, F12 → tab Network, thao tác một lần
bằng tay, xem nó gọi đường nào. Đó chính là thứ cần điền vào file cấu hình.

## Nối với việc khác

- Quy trình BIM cấp dự án, BEP, EIR, LOD → skill `bim-quan-ly-du-an`.
- Trước khi tải lên: sinh hồ sơ bằng `word-ho-so-tu-dong`, kiểm tên bằng
  `iso19650 kiem-tra --chan` để chặn nếu còn file sai.
- Issue đã xuất ra Excel → tổng hợp, lọc, dựng báo cáo bằng `excel-tu-dong-hoa`.
- Gói cả chuỗi thành một lệnh → `quy-trinh-hop-nhat`.
