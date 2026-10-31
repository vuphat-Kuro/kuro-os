# Quy ước tên file và bảng mã theo ISO 19650

Đọc file này khi cần đặt tên, kiểm tra tên, hoặc giải thích mã trạng thái cho
người khác trong tổ.

## Cấu trúc tên

```
<Dự án>-<Đơn vị>-<Khu>-<Cao độ>-<Loại>-<Bộ môn>-<Số hiệu>-<Trạng thái>-<Rev>
```

Ví dụ: `HCMTLMT-A2Z-KM12-ZZ-DR-C-0001-S3-P01.pdf`

| Trường | Ý nghĩa | Ví dụ |
|---|---|---|
| Dự án | Mã dự án, viết tắt không dấu | HCMTLMT, VABG, LTA |
| Đơn vị | Tổ chức tạo ra tài liệu | A2Z, PT, TEDI |
| Khu | Phân vùng công trình theo lý trình / khu | KM12, GOI2, TRUP1 |
| Cao độ | Cao độ hoặc tầng; `ZZ` = không áp dụng | ZZ, 00, B1 |
| Loại | Loại tài liệu (bảng dưới) | DR, M3, RP |
| Bộ môn | Bộ môn kỹ thuật (bảng dưới) | C, S, E, M |
| Số hiệu | Số thứ tự trong nhóm, thường 4 chữ số | 0001 |
| Trạng thái | Mã trạng thái phát hành | S3, A |
| Rev | Số hiệu bản sửa | P01, C01 |

Quy tắc chung: **không dấu tiếng Việt, không dấu cách, dùng dấu gạch ngang làm
dấu phân cách duy nhất.** Ba lỗi này chiếm phần lớn số file bị CDE trả về.

Mỗi dự án có thể quy định khác. Lấy quy ước trong BEP của dự án làm chuẩn, và
truyền vào công cụ qua `--mau`, đừng áp mặc định.

## Mã trạng thái phát hành

| Mã | Nghĩa | Dùng khi |
|---|---|---|
| S0 | Bản khởi tạo, chưa dùng được | Đang làm dở, chia sẻ nội bộ tổ |
| S1 | Phát hành để phối hợp | Gửi bộ môn khác để dựng mô hình phối hợp |
| S2 | Phát hành để tham khảo | Thông tin nền, không dùng làm căn cứ |
| S3 | Phát hành để duyệt nội bộ | Trình chỉ huy trưởng / trưởng bộ môn |
| S4 | Phát hành để chủ đầu tư phê duyệt | Trình TVGS / chủ đầu tư |
| S6 | Phát hành để đấu thầu (PIM) | Hồ sơ mời thầu |
| S7 | Phát hành cho AIM | Bàn giao mô hình vận hành |
| A | Đã duyệt - dùng thi công | Bản duy nhất được phép mang ra hiện trường |
| B | Duyệt có điều kiện | Thi công được nhưng phải sửa theo ghi chú |
| CR | Bị trả lại, làm lại | Không được dùng dưới mọi hình thức |

Điểm cần nói rõ với hiện trường: chỉ tài liệu mã **A** (và **B** kèm điều kiện)
mới được thi công theo. Tài liệu S3/S4 nằm trên CDE không có nghĩa là được duyệt.

## Mã loại tài liệu

| Mã | Loại |
|---|---|
| DR | Bản vẽ |
| M2 | Mô hình 2D |
| M3 | Mô hình 3D |
| SP | Chỉ dẫn kỹ thuật |
| SH | Bảng biểu, schedule |
| RP | Báo cáo |
| CA | Bảng tính, tính toán kết cấu |
| PP | Trình chiếu |
| MI | Biên bản họp |
| CO | Công văn, thư từ |
| PH | Ảnh hiện trường |

## Mã bộ môn thường dùng cho hạ tầng giao thông

| Mã | Bộ môn |
|---|---|
| C | Cầu / kết cấu bê tông |
| S | Kết cấu thép |
| R | Đường, nền mặt đường |
| D | Thoát nước |
| G | Địa kỹ thuật, nền móng |
| E | Điện, chiếu sáng |
| T | An toàn giao thông, tổ chức giao thông |
| L | Cảnh quan, cây xanh |
| A | Kiến trúc (công trình dân dụng trong dự án) |
| M | Cơ điện MEP |

## Quy tắc đánh số bản sửa

- `P01`, `P02`... - bản sửa trước khi được duyệt (preliminary)
- `C01`, `C02`... - bản sửa sau khi đã duyệt (construction)

Chuyển từ P sang C là mốc quan trọng: từ đó mọi thay đổi phải có văn bản chấp
thuận kèm theo, không sửa lặng lẽ.

## Kiểm tra thường xuyên nên chạy

1. Trước mỗi lần phát hành: `iso19650 kiem-tra --thu-muc <thư mục> --chan`
2. Hằng tháng: `iso19650 dang-ky --ma-bam` để phát hiện file trùng ruột khác tên
3. Sau mỗi đợt duyệt: soát xem còn bản S3/S4 nào lẫn trong thư mục thi công không
