---
name: "Excel hồ sơ xây dựng"
description: "Xử lý Excel hồ sơ xây dựng hàng loạt: gộp/tách bảng khối lượng, làm sạch số kiểu VN, so sánh hai phiên bản, soát lỗi, xuất JSON."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Tự động hóa Excel cho hồ sơ xây dựng

## Khi nào dùng

Xử lý Excel hàng loạt cho hồ sơ xây dựng - gộp nhiều file bảng khối lượng của các đội thành một, tách bảng theo hạng mục/gói thầu, làm sạch dữ liệu (số kiểu Việt Nam, khoảng trắng thừa, unicode lệch), so sánh hai phiên bản bảng để tìm chênh lệch, tổng hợp pivot, soát lỗi trước khi nộp, và xuất JSON để nạp vào app/ERP. Dùng skill này bất cứ khi nào người dùng nhắc tới gộp file Excel, nhiều file cùng mẫu, tách bảng, đối chiếu hai bảng, VLOOKUP không ra, dữ liệu lộn xộn, bảng khối lượng, bảng tiến độ, bảng theo dõi - kể cả khi họ chỉ nói "gộp mấy file này lại", "sao hai bảng lệch nhau", "làm sạch cái này hộ tôi", "bảng này có lỗi gì không", "chuyển sang JSON để nạp app". Cũng dùng khi cần lặp một thao tác Excel trên hàng chục file.

Người dùng là kỹ sư QS/QC làm hạ tầng giao thông, đồng thời viết phần mềm. Họ
biết Excel rất rõ. Cái họ cần không phải hướng dẫn dùng hàm, mà là **bỏ hẳn
thao tác tay lặp lại** - 30 file khối lượng của 6 đội, mỗi tháng một lần.

## Nguyên tắc trước khi đụng vào số

**Không bao giờ ghi đè file gốc.** Hồ sơ xây dựng có thể bị truy vết ngược
nhiều năm sau. Luôn xuất ra file mới, giữ bản gốc nguyên vẹn.

**Soát trước, tính sau.** Chạy `soat` trước khi gộp hay tổng hợp. Một bảng có
khóa trùng mà đem đi cộng thì con số tổng sai mà không ai biết cho đến lúc bị
trả hồ sơ.

**Nêu bất thường kể cả khi không được hỏi.** Chênh lệch trên 10% giữa hai kỳ,
hàm lượng thép lệch dải hợp lý, khối lượng âm - nói ra ngay.

## Công cụ

Toàn bộ nằm ở `scripts/xlkit.py`. Chạy `python xlkit.py <lệnh> -h` để xem
tham số. Các lệnh:

| Lệnh | Việc | Khi nào dùng |
|---|---|---|
| `xem` | In cấu trúc file: sheet, dòng tiêu đề, tên cột | **Luôn chạy đầu tiên** khi gặp file lạ |
| `gop` | Gộp nhiều file/sheet cùng mẫu thành một bảng | Tổng hợp khối lượng nhiều đội, nhiều gói |
| `tach` | Tách bảng theo giá trị một cột | Chia bảng tổng theo hạng mục để gửi từng đội |
| `lam-sach` | Chuẩn hóa khoảng trắng, unicode, số | Trước khi VLOOKUP hoặc nạp vào app |
| `so-sanh` | So hai phiên bản theo cột khóa | Đối chiếu bảng tháng này với tháng trước, dự toán với thanh toán |
| `tong-hop` | Nhóm và cộng | Lên bảng tổng theo hạng mục/lý trình |
| `soat` | Soát lỗi chất lượng bảng | Trước khi nộp bất cứ bảng nào |
| `sang-json` | Xuất JSON | Nạp vào CONSBASE ERP hoặc nền tảng sgmt |

## Cách làm việc

**Bước 1 - nhìn trước khi làm.** Bảng hồ sơ Việt Nam hầu như không bao giờ có
tiêu đề ở dòng 1: phía trên là tên đơn vị, tên công trình, ô gộp. `xem` dò
được dòng tiêu đề thật. Nếu dò sai, ép bằng `--dong-tieu-de N` (đếm từ 0).

**Bước 2 - soát.** Chạy `soat --khoa "<cột khóa>"` để bắt: khóa trùng, khóa
rỗng, cột số lẫn chữ, giá trị âm, unicode lệch. Lỗi mức Nặng làm lệnh thoát
với mã 2 - dùng được trong quy trình tự động để chặn bước sau.

**Bước 3 - xử lý.** Chạy lệnh cần dùng.

**Bước 4 - đối chiếu ngẫu nhiên.** Sau khi gộp hay tổng hợp, mở file kết quả,
đối chiếu 3-5 dòng với file gốc. Script chạy đúng không có nghĩa dữ liệu vào
đã đúng.

## Vài chỗ hay vấp

**Gộp mà tổng sai** - thường do các file không cùng mẫu biểu. Lệnh `gop` cảnh
báo khi phát hiện cột chỉ có ở một số file, và ghi sheet "Nhật ký gộp" cho biết
mỗi file góp bao nhiêu dòng. Đọc sheet đó trước khi tin số tổng.

**VLOOKUP trượt dù mắt nhìn giống hệt** - chữ tiếng Việt gõ từ nguồn khác nhau
có thể khác byte (tổ hợp NFC/NFD), hoặc có khoảng trắng không ngắt. `lam-sach`
chuẩn hóa cả hai. Đây là nguyên nhân thật sự trong đa số trường hợp.

**Số bị hiểu sai** - `1.234,56` kiểu Việt Nam và `1,234.56` kiểu quốc tế đều
được nhận đúng. Chuỗi không đổi được sang số thì **giữ nguyên**, không âm thầm
biến thành 0 - vì một ô ghi "chờ TK" biến thành 0 là cách làm hỏng bảng dự toán
êm ái nhất.

**Số hiệu 01 thành 1** - Excel đọc "01" thành số. Với cột số hiệu văn bản, ép
giữ dạng chữ khi cần.

## Nối với việc khác

- Bảng đã sạch → dùng skill `word-ho-so-tu-dong` để sinh biên bản hàng loạt.
- Bảng đã tổng hợp → `sang-json` để nạp vào CONSBASE ERP hoặc nền tảng sgmt.
- Cần bóc khối lượng từ mô hình chứ không phải file Excel → dùng skill
  `qs-khoi-luong-du-toan` và `bim-automation`.
- Lặp cả chuỗi hằng tháng → gói lại bằng skill `quy-trinh-hop-nhat`.

## Khi nào đừng dùng script

Bảng dưới 50 dòng làm một lần: mở Excel làm tay nhanh hơn. Script đáng dùng khi
việc **lặp lại** hoặc **số file nhiều**. Nói thẳng điều này với người dùng thay
vì dựng công cụ cho một việc chạy đúng một lần.
