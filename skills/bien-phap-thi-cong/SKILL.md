---
name: "Biện pháp thi công"
description: "Lập, thẩm định biện pháp tổ chức thi công cầu, đường, cống, cảng: trình tự, mặt bằng, kết cấu phụ trợ, thiết bị, an toàn."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Biện pháp thi công

## Khi nào dùng

Lập, thẩm định và trình duyệt biện pháp tổ chức thi công cho công trình cầu, đường, cống, hạ tầng kỹ thuật, cảng - công trình thủy và dân dụng - bao gồm bố trí mặt bằng, trình tự thi công, kết cấu phụ trợ (ván khuôn, đà giáo, xe đúc, giá lao, cọc ván thép, hệ văng chống), huy động thiết bị - nhân lực, và biện pháp an toàn kèm theo. Dùng skill này khi người dùng nhắc tới biện pháp thi công, phương án thi công, thuyết minh biện pháp, tổ chức thi công, đà giáo, ván khuôn, xe đúc hẫng, lao lắp dầm, hố móng sâu, thi công dưới nước, hoặc hỏi "thi công cái này thế nào", "làm sao qua được đoạn này", "so sánh mấy phương án" - kể cả khi họ chỉ mô tả một tình huống vướng mắc ngoài công trường.

Người dùng đã trực tiếp làm hiện trường cầu và hạ tầng, có kinh nghiệm dựng mô hình biện pháp trên Tekla/Revit. Đừng giảng lý thuyết. Tập trung vào ba thứ họ thực sự cần: **trình tự đúng, kết cấu phụ trợ tính được, và rủi ro được gọi tên trước khi nó xảy ra**.

## Bước 0 - Thu thập ràng buộc trước khi đề xuất

Một biện pháp thi công tốt là biện pháp phù hợp với ràng buộc, không phải biện pháp hay nhất về kỹ thuật. Hỏi những gì còn thiếu:

- **Hình học và kết cấu**: khẩu độ, chiều cao, cao độ đáy móng, mực nước, địa chất theo hố khoan
- **Mặt bằng**: diện tích được bàn giao, đường tiếp cận, tải trọng cho phép, tĩnh không, công trình lân cận
- **Thời gian**: mùa mưa/lũ, mực nước theo mùa, thời gian phong tỏa được phép, mốc tiến độ ràng buộc
- **Nguồn lực**: thiết bị đang có sẵn của đơn vị so với thiết bị phải thuê - thứ này quyết định phương án nhiều hơn kỹ thuật
- **Ràng buộc bên ngoài**: giao thông đang khai thác, đường sắt, điện cao thế, dân cư, môi trường, thủy lợi

Nếu người dùng chưa nói rõ, hỏi tối đa 2-3 điều quan trọng nhất rồi đề xuất với giả định ghi rõ. Đừng hỏi dồn 10 câu.

## Cấu trúc thuyết minh biện pháp thi công

Dùng khung này khi soạn văn bản trình duyệt:

```
1. Căn cứ lập biện pháp (hồ sơ thiết kế, chỉ dẫn kỹ thuật, hợp đồng, tiêu chuẩn, điều kiện hiện trường)
2. Đặc điểm công trình và điều kiện thi công (địa hình, địa chất, thủy văn, mặt bằng, giao thông)
3. Tổng mặt bằng thi công (bố trí, đường công vụ, bãi tập kết, lán trại, điện nước, thoát nước)
4. Trình tự và sơ đồ tổ chức thi công tổng thể
5. Biện pháp thi công chi tiết từng hạng mục
   5.x  Trình tự công đoạn - Kết cấu phụ trợ và tính toán - Thiết bị - Nhân lực - Kiểm soát chất lượng - Rủi ro
6. Huy động thiết bị, nhân lực (bảng)
7. Tiến độ thi công và biểu đồ huy động
8. Biện pháp đảm bảo chất lượng (dẫn chiếu ITP)
9. Biện pháp an toàn lao động, vệ sinh môi trường, đảm bảo giao thông
10. Biện pháp ứng phó sự cố và tình huống khẩn cấp
11. Phụ lục: bản vẽ biện pháp, bảng tính kết cấu phụ trợ
```

Với văn bản dài trình duyệt, tạo file .docx (đọc skill `docx` trước). Với trao đổi nội bộ nhanh, trả lời thẳng trong hội thoại.

## Kết cấu phụ trợ - phần dễ sai nhất

Ván khuôn, đà giáo, sàn đạo, giá lao, xe đúc, hệ văng chống là **kết cấu chịu lực thật** và là nguyên nhân của phần lớn sự cố sập đổ trong thi công. Khi hỗ trợ phần này:

- Luôn nêu rõ **tổ hợp tải trọng** phải xét: trọng lượng bản thân, bê tông ướt, cốt thép, người và thiết bị thi công, tải trọng khi đổ và đầm, gió, va chạm, và tải trọng trong giai đoạn lắp dựng - tháo dỡ (thường nguy hiểm hơn giai đoạn khai thác).
- Nêu rõ **các trạng thái phải kiểm tra**: cường độ, ổn định tổng thể (lật, trượt), ổn định cục bộ (mất ổn định thanh mảnh), biến dạng - độ võng, và khả năng chịu tải của nền dưới chân đà giáo. Nền dưới chân chống là thứ bị bỏ quên nhiều nhất.
- Nêu rõ **độ vồng và biến dạng dự kiến** với đà giáo nhịp lớn và bệ đúc dầm - ảnh hưởng trực tiếp tới hình học công trình.
- Nêu rõ **trình tự lắp dựng và trình tự tháo dỡ**. Tháo sai thứ tự làm sập kết cấu còn ổn định khi lắp.

**Ranh giới cần giữ:** hỗ trợ lập sơ đồ tính, liệt kê tải trọng, nêu công thức và các bước kiểm toán, rà soát kết quả người dùng đưa ra. Nhưng kết quả tính kết cấu phụ trợ phải do người có chuyên môn kiểm tra và ký duyệt, và với đà giáo/xe đúc/hệ chống hố đào sâu, khuyến nghị thẩm tra độc lập. Nói rõ điều này một lần, ngắn gọn, không lặp lại nhiều lần trong cùng câu trả lời.

## So sánh phương án

Khi có nhiều phương án, đừng chỉ liệt kê. Lập bảng so sánh theo các tiêu chí có trọng số thực tế:

| Tiêu chí | PA1 | PA2 | PA3 |
|---|---|---|---|
| Thời gian thi công | | | |
| Chi phí (kể cả kết cấu phụ trợ và thiết bị thuê) | | | |
| Yêu cầu mặt bằng và tiếp cận | | | |
| Phụ thuộc thời tiết / mực nước | | | |
| Rủi ro an toàn | | | |
| Ảnh hưởng giao thông và dân cư | | | |
| Thiết bị: có sẵn hay phải huy động | | | |
| Độ quen thuộc của đội thi công | | | |

Rồi **đưa ra khuyến nghị rõ ràng kèm lý do**, không dừng ở việc bày bàn. Nếu khuyến nghị phụ thuộc vào một thông tin chưa có, nói rõ thông tin đó là gì.

Xem `references/phuong-an-theo-hang-muc.md` cho các phương án điển hình theo loại công trình và tiêu chí chọn giữa chúng.

## Rủi ro - gọi tên trước khi nó xảy ra

Với mỗi biện pháp, liệt kê rủi ro theo dạng: **tình huống → dấu hiệu nhận biết sớm → ngưỡng dừng thi công → hành động**.

Ví dụ cách viết đúng:
> Sạt vách hố đào. Dấu hiệu: nứt mép hố, chuyển vị cọc ván vượt trị số cảnh báo trong quan trắc, nước rỉ mang theo cát. Ngưỡng dừng: chuyển vị đạt trị số quy định trong thiết kế quan trắc. Hành động: dừng đào, rút người, gia cường tầng chống, báo thiết kế.

Các rủi ro luôn phải xét trong hạ tầng giao thông và cảng: mưa lũ và dâng nước bất thường, sạt vách hố đào, mất ổn định đà giáo, tai nạn khi cẩu và lao lắp, va chạm phương tiện đang lưu thông, sự cố trong quá trình đổ bê tông khối lớn liên tục, tụt neo khi căng kéo, va tàu và thay đổi thủy triều với công trình bến.

## Liên kết với BIM

Người dùng dựng mô hình biện pháp trên Tekla và Revit. Khi phù hợp:

- Đề xuất mô hình hóa kết cấu phụ trợ để phát hiện xung đột với kết cấu chính và với không gian thao tác - rẻ hơn nhiều so với phát hiện ngoài công trường.
- Đề xuất mô phỏng 4D theo trình tự thi công để kiểm tra tính khả thi của trình tự và bố trí thiết bị; xem skill `tien-do-san-luong`.
- Khi cần dựng nhanh family/cấu kiện biện pháp hoặc script tham số hóa, xem skill `bim-automation`.
- Bản vẽ biện pháp trích từ mô hình phải được kiểm tra lại kích thước thực trước khi đóng vào hồ sơ trình duyệt.

## An toàn không phải phụ lục

Trong hạ tầng giao thông, các nguyên nhân tai nạn hàng đầu là: ngã cao, vật rơi, sập đổ kết cấu phụ trợ, tai nạn thiết bị nâng, tai nạn giao thông tại khu vực thi công, ngạt trong không gian hạn chế (giếng, hố sâu, thùng dầm hộp), và điện giật. Với mỗi biện pháp, nêu cụ thể: rào chắn và phân luồng, lan can và dây neo an toàn, sàn thao tác, kiểm định thiết bị nâng, phương án làm việc trong không gian hạn chế, và quy trình khóa - treo thẻ khi cần.
