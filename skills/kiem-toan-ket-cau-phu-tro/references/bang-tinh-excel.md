# Cấu trúc bảng tính Excel kết quả kiểm toán

Kết quả kiểm toán bàn giao dưới dạng Excel **có công thức thật** (không dán giá trị). Đọc skill `xlsx` trước khi tạo file. Sau khi tạo, tính lại toàn bộ công thức và kiểm tra không có lỗi (#REF!, #DIV/0!, #VALUE!, #NAME?).

Mục tiêu: người soát xét mở file ra là thấy ngay số nào lấy từ đâu, đổi một đầu vào thì kết quả tự cập nhật, và việc nào còn treo.

## Các sheet

| Sheet | Nội dung |
|---|---|
| `Tong_hop` | Kết luận, bảng hệ số sử dụng từng trạng thái, trạng thái khống chế, điều kiện áp dụng, số mục còn `CHƯA CÓ CĂN CỨ` |
| `Thong_tin` | Tên công trình, hạng mục, phiên bản, ngày lập, người lập, người soát, hồ sơ biện pháp đã dẫn |
| `Nguon` | Sổ nguồn (mã, số hiệu, tên, vai trò trong bài, bản gốc đã nhận, hiệu lực do người dùng xác nhận) và chỉ mục trị số đã trích |
| `Dau_vao` | Toàn bộ dữ liệu đầu vào: hình học, vật liệu, địa chất, mực nước, thiết bị; mỗi dòng có nguồn số liệu |
| `Tai_trong` | Từng loại tải, giá trị, giai đoạn xuất hiện, nguồn |
| `To_hop` | Các tổ hợp theo giai đoạn, hệ số lấy từ nguồn, ghi rõ tổ hợp nào khống chế |
| `KT_<nhóm>` | Mỗi nhóm trong ma trận một sheet (ví dụ `KT_VK`, `KT_DG`, `KT_NM`, `KT_VV`) |
| `Gia_dinh` | Danh sách giả định chưa được xác nhận, người chịu trách nhiệm xác nhận, tình trạng |
| `Chua_co_can_cu` | Các nội dung không tính được vì thiếu nguồn, loại tài liệu cần bổ sung |
| `Nhat_ky` | Lịch sử sửa đổi giữa các phiên bản |

Sheet nào không phù hợp với bài toán cụ thể thì bỏ, đừng giữ sheet rỗng.

## Dựng khung tự động

Chạy `scripts/tao_bang_tinh.py` để tạo khung đúng cấu trúc, sheet `Nguon` điền sẵn từ `assets/so-nguon.json`, một dòng ví dụ và các công thức hệ số sử dụng - kết luận - tổng hợp:

```bash
python scripts/tao_bang_tinh.py --out "<thư mục dự án>/KT_<hang-muc>.xlsx" \
  --cong-trinh "Tên công trình" --hang-muc "Đà giáo nhịp 3" \
  --he cau --nhom VK DG NM
```

`--he`: `cau` (N01 chính) hoặc `dan-dung` (N02 + N03 + N04) hoặc `cang`; `--nhom`: các nhóm trong ma trận cần tạo sheet kiểm tra (VK, DG, NM, VV, TB, CT, TH). Script tạo sẵn các dòng trạng thái của nhóm với mã, tên và điều khoản gợi ý; ô S, R để trống cho người tính. Sau khi điền, chạy `recalc.py` của skill `xlsx` và sửa đến khi không còn lỗi.

## Quy ước từng sheet kiểm tra

Mỗi dòng có các cột:

`Mã | Trạng thái kiểm tra | Giai đoạn | Dạng điều kiện | S (tác động) | R (khả năng) | K (hệ số an toàn / tin cậy nếu có) | Đơn vị | Hệ số sử dụng | Kết luận | Nguồn công thức | Nguồn R và K | Ghi chú`

**Hệ số sử dụng** thống nhất nghĩa "≤ 1 là đạt" cho mọi dạng:
- `S ≤ R`: u = S / R
- `S·K ≤ R`: u = S × K / R (dùng cho lật, trượt, đẩy nổi, trồi đáy, neo... khi nguồn quy định hệ số an toàn hoặc hệ số tin cậy). Nếu nguồn viết dạng R / S ≥ K thì vẫn quy về dạng này.
- `δ ≤ [δ]`: u = δ / [δ], S là biến dạng tính, R là giới hạn.
- `KT`: kiểm tra cấu tạo, u để trống, kết luận nhập tay "Đạt" / "Không đạt" kèm ghi chú.

Công thức Excel (đã có trong khung):
`u = IF(OR(S="",R=""),"",IF(Dạng="S·K≤R",S*K/R,S/R))`
`Kết luận = IF(Nguồn công thức="","CHƯA CÓ CĂN CỨ",IF(u="","CHƯA TÍNH",IF(u<=1,"ĐẠT","KHÔNG ĐẠT")))`

Chỉ khi hệ số sử dụng tính được **và** cột nguồn đã điền thì mới có "ĐẠT". Trạng thái chưa có nguồn: để trống R, không điền số tạm.

## Quy ước trình bày

- Ô đầu vào: chữ xanh, nền vàng nhạt. Ô công thức: chữ đen. Ô kết luận và kiểm tra: đổi màu theo đạt hay không đạt bằng định dạng có điều kiện.
- Mỗi giá trị hằng dùng nhiều nơi nằm ở `Dau_vao` hoặc `Tai_trong` và được tham chiếu, không gõ lại trong công thức.
- Đơn vị ghi ở cột riêng, không nhúng vào tên ô. Đơn vị thống nhất toàn file.
- Tên sheet và tiêu đề tiếng Việt có dấu trong ô nội dung; tên sheet dùng không dấu để tránh lỗi tham chiếu.
- Khóa các ô công thức, cho phép sửa ô đầu vào.
- Thêm ô kiểm tra tự động: tổng tải với tổng phản lực, đơn vị nhất quán, giá trị đầu vào âm hoặc bằng 0 bất thường, tham chiếu vòng.
- Kết quả lấy từ phần mềm (Midas, Plaxis, Geo5) dán vào sheet riêng `Ket_qua_PM`, ghi rõ tên file mô hình, phiên bản, ngày chạy; các sheet kiểm tra tham chiếu tới đó, không gõ tay lại.

## Sheet Tong_hop: nội dung tối thiểu

1. Kết luận một câu: đạt, không đạt, hoặc chưa đủ cơ sở kết luận
2. Bảng các trạng thái, hệ số sử dụng, trạng thái khống chế
3. Điều kiện áp dụng của kết luận: tải, trình tự thi công, mực nước lớn nhất, yêu cầu quan trắc
4. Số mục `CHƯA CÓ CĂN CỨ` và số giả định chưa xác nhận
5. Một dòng về việc kết quả phải do người có chuyên môn kiểm tra và ký duyệt, kèm khuyến nghị thẩm tra độc lập nếu hạng mục thuộc nhóm nêu trong file tham chiếu

Không được ghi "đạt" ở đầu trang khi còn mục `CHƯA CÓ CĂN CỨ` ở trạng thái khống chế.
