# QUY CHUẨN TRÌNH BÀY VĂN BẢN NỘI BỘ BM03A PHÒNG KỸ THUẬT THI CÔNG
*Phê duyệt và chuẩn hóa bởi Phó phòng KT-TC (Tháng 10/2026)*

---

## 1. NGUYÊN TẮC CỐT LÕI
1. **Ưu tiên số 1: Tuyệt đối tuân thủ biểu mẫu chuẩn đã duyệt.** Luôn nhân bản mẫu duyệt `Mau_BM03A_Trinh_Lanh_Dao_Da_Duyet.docx` và chỉ thay nội dung; cấm dựng lại Word từ trang trắng, cấm tự đổi lề, cỡ chữ, dãn dòng. Số trang tùy nội dung, viết ngắn gọn đúng trọng tâm.
2. **Mặc định chỉ xuất file Word (.docx).** Tuyệt đối không tự ý xuất file .pdf trừ khi người dùng có yêu cầu riêng.
3. **Kỷ luật lưu trữ:**
   - Dự thảo lưu tại thư mục tạm (thư mục dự án hiện hành trên máy, hỏi người dùng nếu chưa rõ) với tiền tố `NHAP_`.
   - Chỉ lưu vào hồ sơ dự án chính thức khi người dùng có lệnh phê duyệt ("duyệt", "phát hành").

---

## 2. BỘ 10 QUY CHUẨN THỂ THỨC BM03A TRÌNH BAN LÃNH ĐẠO CÔNG TY

| STT | Thành phần | Quy chuẩn kỹ thuật chi tiết |
| :---: | :--- | :--- |
| **1** | **Header (Trang đầu)** | - Xóa bỏ Table 0 (khung chữ *"Mẫu số: BM03A/VB-2025"*).<br>- Giữ nguyên Logo và bảng thông tin Công ty Phương Thành.<br>- Thêm paragraph đệm đầu ô thông tin để đỉnh cụm chữ ngang bằng chuẩn xác với đỉnh tròn Logo Phương Thành.<br>- Dãn khoảng cách dòng trong ô thông tin: `space_before = 2.5 pt`, `space_after = 2.5 pt`, `line_spacing = 1.15` (không để dính sát co cụm).<br>- Chiều rộng ô thông tin đảm bảo dòng tiếng Anh và dòng Website/Email nằm gọn trên 1 dòng duy nhất.<br>- Bật `different_first_page_header_footer = True`, các trang sau hoàn toàn không lặp Header. |
| **2** | **Số văn bản** | - `Số:       /PT-KTTC` (cỡ 13, Times New Roman, chữ thường đứng, không in đậm).<br>- Kéo sát lên ngay dưới đường kẻ Header, xóa bỏ dòng trắng thừa phía trên dòng số. |
| **3** | **Địa danh, ngày tháng** | - Căn phải, cỡ 13, chữ nghiêng: `Hà Nội, ngày ... tháng ... năm 2026`. |
| **4** | **Trích yếu (V/v)** | - Căn dàn đều 2 bên (Justified / Ctrl+J).<br>- Cỡ 12, chữ thường đứng (không in đậm, không in nghiêng, bỏ dấu `:` sau `V/v`).<br>- Ví dụ: `V/v Báo cáo rà soát khối lượng móng mặt...`. |
| **5** | **Kính gửi** | - Cỡ 13, chữ thường không in đậm, căn thụt theo mẫu: `Kính gửi: Ban Lãnh đạo Công ty`. |
| **6** | **Căn cứ** | - Cỡ 13, chữ đứng thường (không in nghiêng), thụt đầu dòng đúng như file mẫu duyệt.<br>- Chỉ viện dẫn căn cứ nội bộ (chức năng nhiệm vụ Phòng KT-TC, thực tế công trường, BVTC, báo cáo BĐH). Lược bỏ căn cứ Hợp đồng xây lắp trong văn bản nội bộ. |
| **7** | **Thân bài & Thụt lề** | - Cỡ 13, Times New Roman, chữ đứng thường, giãn dòng 1.15, thụt đầu dòng đồng nhất theo file mẫu duyệt.<br>- Đoạn mở đầu chuẩn: *"Sau khi kiểm tra, rà soát số liệu báo cáo của Ban Điều hành và tình hình thi công trên công trường, Phòng Kỹ thuật Thi công báo cáo Lãnh đạo Công ty một số nội dung sau:"*<br>- Nội dung ngắn gọn, tập trung vào kết quả kiểm tra của Phòng và đề xuất khối lượng duyệt phát sinh, không phân tích chi tiết số liệu BĐH trên văn bản.<br>- Kết thúc chuẩn: `Trân trọng cảm ơn!`. |
| **8** | **Thể thức ký Phòng KT-TC** | - Bố trí tại cột phải Table 2, **đúng 2 dòng text**:<br>  + Dòng trên: `PHÒNG KỸ THUẬT THI CÔNG` (cỡ 13, in hoa, in đậm, căn giữa).<br>  + Khoảng trống ký tên rộng rãi: tương đương 5 dòng chuẩn (đúng như file mẫu duyệt) để Trưởng phòng ký và đóng dấu.<br>  + Dòng dưới: `TP. Đỗ Đắc Luận` (cỡ 13, in đậm, căn giữa).<br>- *Tuyệt đối không tách riêng dòng TRƯỞNG PHÒNG.* |
| **9** | **Nơi nhận** | - Cột trái Table 2, cỡ 10 pt (tiêu đề `Nơi nhận:` cỡ 11 pt bold italic):<br>  `- Như trên;`<br>  `- Phòng KTKH (để thực hiện / để p/h);`<br>  `- Ban Điều hành ... (để thực hiện);`<br>  `- Lưu: VT, KTTC.` |
| **10** | **Khối Ý kiến Ban Lãnh đạo** | - Đặt ngay phía dưới Table 2 chữ ký.<br>- Tiêu đề căn giữa: **`Ý KIẾN BAN LÃNH ĐẠO CÔNG TY`** (cỡ 13, in hoa, in đậm).<br>- Phía dưới để trống hoàn toàn không gian trang trọng để Lãnh đạo viết tay ý kiến và ký duyệt (không đặt trước tên Lãnh đạo, không để dòng chấm kẻ). |

---

## 3. KIẾN TRÚC TRÌNH BÀY TRÌNH LÃNH ĐẠO: "TỜ TRÌNH NGẮN + PHỤ LỤC RIÊNG"
Khi soạn thảo báo cáo/tờ trình có kèm bảng số liệu lớn:
1. **Tờ trình cốt lõi (thường vừa 1 trang, không bắt buộc):**
   - Header + Số/Trích yếu + Kính gửi + Căn cứ.
   - Thân bài cô đọng trong 3-4 đoạn: Hiện trạng & nguyên nhân → Kết quả kiểm tra của Phòng → Đề xuất dứt khoát khối lượng duyệt.
   - Chữ ký Phòng KT-TC và Khối `Ý KIẾN BAN LÃNH ĐẠO CÔNG TY` nằm trọn vẹn ở đáy trang 1.
   - Giúp Ban Lãnh đạo chỉ mất 10-15 giây là nắm trọn bản chất và ký phê duyệt ngay tại chỗ.
2. **Trang 2 trở đi (Phụ lục số liệu chi tiết):**
   - Đẩy toàn bộ bảng biểu nhiều dòng/cột sang trang riêng làm **"PHỤ LỤC KIỂM TRA KHỐI LƯỢNG..."**.
   - Bố trí bảng biểu thoáng đãng, lặp tiêu đề bảng (`tblHeader`), khóa chống cắt rách dòng (`cantSplit`).
