# Vài mẹo Excel đáng nhớ khi làm việc cùng công cụ

## Khi nào dùng script, khi nào làm tay

| Tình huống | Nên làm |
|---|---|
| 1 bảng, dưới 50 dòng, làm một lần | Làm tay trong Excel, nhanh hơn |
| Nhiều file cùng mẫu | `xlkit gop` |
| Việc lặp lại hằng tháng | Gói bằng `quy-trinh-hop-nhat` |
| Cần đối chiếu hai bản để giải trình | `xlkit so-sanh` - có sẵn cột chênh lệch và chênh % |
| Nạp dữ liệu vào app | `xlkit sang-json` |

## Ba nguyên nhân VLOOKUP trượt dù nhìn giống hệt

1. **Unicode khác tổ hợp** - "ầ" gõ liền một ký tự (NFC) khác với "a" + dấu
   (NFD). Mắt không phân biệt được, Excel thì có.
2. **Khoảng trắng không ngắt** (`\xa0`) lẫn vào khi copy từ web hoặc PDF.
3. **Số lưu dưới dạng chữ** - cột mã hiệu bên này là số, bên kia là chữ.

`xlkit lam-sach` xử lý cả ba.

## Định dạng số Việt Nam

`1.234,56` - chấm phân nhóm nghìn, phẩy thập phân. Ngược với quốc tế. Khi nhận
file từ phần mềm nước ngoài hoặc xuất từ Revit/Tekla, số thường ở dạng quốc tế.
`xlkit` nhận đúng cả hai dạng, nhưng khi làm tay thì phải để ý - đây là nguồn
sai số âm thầm.

## Đặt cột khóa cho tốt

Cột khóa nên là thứ **không đổi giữa các kỳ**: mã hiệu định mức + hạng mục + lý
trình. Đừng dùng STT làm khóa - chèn thêm một dòng là lệch toàn bộ.

Khi một mã xuất hiện ở nhiều hạng mục (ví dụ đào đất ở cả mố và trụ), khóa phải
gồm nhiều cột: `--khoa "Mã hiệu,Hạng mục"`.

## Kiểm tra chéo nên chạy trước khi nộp

- Cân bằng đào – đắp – vận chuyển
- Hàm lượng thép (kg/m³ bê tông) có nằm trong dải hợp lý không
- Tỷ lệ diện tích ván khuôn trên thể tích bê tông
- Đơn vị đo: m / m² / m³ / tấn / cái - sai đơn vị là lỗi tốn kém nhất

Ba mục đầu cần biết nghiệp vụ, script không tự làm được. Mục cuối `xlkit soat`
có thể gợi ý một phần. Xem skill `qs-khoi-luong-du-toan` cho phần nghiệp vụ.
