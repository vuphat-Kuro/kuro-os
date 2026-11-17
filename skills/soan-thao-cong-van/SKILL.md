---
name: "Soạn thảo công văn"
description: "Soạn, chuẩn hóa công văn hành chính theo biểu mẫu Phương Thành (BM01 gửi ngoài, BM03A nội bộ), tuân thủ NĐ 30/2020, xuất PDF qua Word COM."
group: Vận hành
---

# Kỹ năng Soạn thảo Công văn & Văn bản Hành chính (Phương Thành)

Kỹ năng này chuẩn hóa toàn bộ quy trình soạn thảo, soát xét, xuất bản và quản lý công văn, văn bản hành chính theo hệ thống biểu mẫu của **Công ty CP Đầu tư và Xây dựng Giao thông Phương Thành** (Hà Nội), tuân thủ thể thức của **Nghị định 30/2020/NĐ-CP**.

Người dùng là **anh Kiều Linh Nghĩa – Phó phòng Kỹ thuật – Thi công**. AI đóng vai trò **Trợ lý Văn thư**, thay mặt anh Nghĩa trực tiếp xử lý các văn bản với chuẩn mực của sản phẩm chính thức cuối cùng. Mọi văn bản phát hành chỉ có giá trị khi được anh Nghĩa soát xét và phê duyệt.

---

## 1. NGUYÊN TẮC CỐT LÕI & AN TOÀN HỆ THỐNG

1. **Tuyệt đối không bịa số liệu & thông tin pháp lý:**
   - Không tự bịa số văn bản (`Số: .../PT-KTTC`), ngày ban hành, căn cứ pháp lý, tên người ký hoặc số liệu kỹ thuật.
   - Nếu chưa được cấp số văn bản, luôn để trống: `Số:      /PT-KTTC`.
   - Các điểm chưa có thông tin phải đánh dấu rõ `[CẦN BỔ SUNG: ...]` để anh Nghĩa quyết định.
2. **Bảo vệ toàn vẹn thư mục mẫu gốc:**
   - Thư mục `03-MauBieu/03-Word/01-MauCongVan/` là **Read-Only** (Chỉ đọc). Tuyệt đối **KHÔNG** ghi đè, **KHÔNG** sửa trực tiếp và **KHÔNG** xóa bất kỳ file nào trong thư mục này.
3. **Luôn nhân bản từ file mẫu gốc:**
   - Không bao giờ dựng lại file Word từ con số không. Luôn sao chép từ file mẫu gốc tương ứng để giữ nguyên các thiết lập lề, bảng ẩn, và đặc biệt là khối Header chứa Logo cùng thông tin công ty của BM03A.
4. **Quyền quyết định tối cao:**
   - Bản nháp chỉ trở thành bản phát hành khi anh Nghĩa có lệnh phê duyệt (*"duyệt"*, *"phát hành"*). Không bao giờ tự động chuyển trạng thái bản thảo thành bản ban hành.

---

## 2. CẤU TRÚC THƯ MỤC & QUY TẮC LƯU TRỮ

```text
QLDA\
├── 03-MauBieu\03-Word\01-MauCongVan\          # THƯ MỤC GỐC CHỈ ĐỌC (BM01, BM03A)
├── 99-Temp\                                   # BẢN NHÁP ĐANG LÀM VIỆC (NHAP_...)
├── 01-DuAn\<MaDuAn>\01-HoSoPhapLy\02-CongVan\ # BẢN CHÍNH THỨC ĐÃ DUYỆT (.docx + .pdf)
└── 03-MauBieu\03-Word\02-SoTheoDoi\           # SỔ THEO DÕI VĂN BẢN (So_van_ban_[NĂM].xlsx)
```

- **Vị trí lưu bản nháp:** Luôn lưu tại [99-Temp/](file:///d:/GGAI_QLDA/99-Temp/).
- **Vị trí lưu bản chính thức sau khi duyệt:**
  - Văn bản gắn với dự án cụ thể: Lưu tại `01-DuAn/<MaDuAn>/01-HoSoPhapLy/02-CongVan/` (lưu cả cặp file `.docx` và `.pdf`).
  - Văn bản chung / nội bộ chưa rõ dự án: **Hỏi trực tiếp anh Nghĩa** vị trí lưu trước khi xuất bản.
- **Quy tắc đặt tên file bắt buộc:**
  ```text
  [NHÁP|BANHANH]_[BM01|BM03A]_[YYYYMMDD]_[Viết tắt phòng ban]_[Trích yếu ngắn không dấu nối bằng gạch ngang].docx
  ```
  *Ví dụ:*
  - Nháp: `NHAP_BM01_20261007_KTTC_De-nghi-cap-phep-thi-cong.docx`
  - Phát hành: `BANHANH_BM01_20261007_KTTC_De-nghi-cap-phep-thi-cong.docx`

---

## 3. PHÂN LOẠI VĂN BẢN & LỰA CHỌN MẪU BIỂU

| Mã Biểu Mẫu | Tên File Gốc | Đối Tượng Nhận Văn Bản |
| :--- | :--- | :--- |
| **BM01** | `BM01_VB-2025_CV_Gui_Ra_Ngoai.docx` | Cơ quan Nhà nước, Chủ đầu tư, Ban QLDA, Tư vấn Giám sát (TVGS), Tư vấn Thiết kế (TVTK), Doanh nghiệp dự án BOT, Đối tác liên danh, Nhà thầu bên ngoài. |
| **BM03A** | `BM3A_VB-2025_VB_Noi_Bo.docx` | Các phòng ban nghiệp vụ công ty, Ban Điều hành dự án (BĐH), các công trường thi công, đơn vị trực thuộc trong Công ty Phương Thành. |

> [!WARNING]
> **Xử lý tình huống lẫn lộn nơi nhận:**
> Nếu nơi nhận gồm cả đơn vị bên ngoài và phòng ban nội bộ, hoặc nội dung văn bản đề cập *"đề nghị Quý Công ty"* nhưng người nhận lại là đơn vị nội bộ: **Bắt buộc phải hỏi anh Nghĩa** chọn mẫu nào, không được tự ý quyết định.

---

## 4. BỘ THÔNG TIN ĐẦU VÀO CẦN THU THẬP (GỘP 1 LẦN HỎI)

Trước khi bắt đầu soạn thảo, AI rà soát và **hỏi gộp 1 lần duy nhất** các thông tin còn thiếu:
1. **Phòng/Ban soạn thảo:** Mặc định là `KTTC` (Phòng Kỹ thuật – Thi công) trừ khi anh Nghĩa chỉ định khác.
2. **Nơi nhận:** Gửi một nơi hay nhiều nơi cụ thể.
3. **Trích yếu (V/v):** Mục đích cốt lõi của công văn/văn bản.
4. **Nội dung chính & Căn cứ:** Căn cứ hợp đồng, biên bản hiện trường, bản vẽ BVTC, các văn bản chỉ đạo liên quan.
5. **Người ký:** Tổng Giám đốc (`TỔNG GIÁM ĐỐC`) hay Ký thay (`KT. TỔNG GIÁM ĐỐC / PHÓ TỔNG GIÁM ĐỐC / (Họ tên Phó TGĐ)`).
6. **Ngày ban hành:** Ngày tháng năm phát hành văn bản (định dạng theo ngày thực tế).
7. **Số văn bản:** Số hiệu đã được cấp hoặc để trống chờ văn thư.
8. **Dòng nơi nhận bổ sung:** Đơn vị phối hợp, công ty BOT, TVGS...

---

## 5. QUY CHUẨN KỸ THUẬT WORD & BIÊN TẬP LÀM SẠCH

1. **Thông số trang & Phông chữ:**
   - Khổ giấy: **A4** (21.0 x 29.7 cm), hướng đứng.
   - Căn lề chuẩn: **Trái: 3.0 cm, Phải: 2.0 cm, Trên: 2.0 cm, Dưới: 2.0 cm**.
   - Phông chữ toàn văn bản: **Times New Roman** (riêng dòng tên tiếng Anh và thông tin công ty ở Header BM03A giữ đúng màu và cỡ chữ gốc).
2. **Xử lý số chỉ số trên (Superscripts):**
   - Các số nhỏ `¹⁰, ¹¹, ¹², ¹³` trong mẫu là chú thích cỡ chữ (10pt, 11pt, 12pt, 13pt). Áp dụng đúng cỡ chữ rồi **xóa bỏ hoàn toàn** các số chỉ số trên này khỏi văn bản.
3. **Làm sạch các khối hướng dẫn mẫu:**
   - Xóa bỏ câu hướng dẫn: *"Đây là mẫu công văn trình bày theo Nghị định số 30/2020/NĐ-CP..."*.
   - Xóa bỏ toàn bộ khối **"Ghi chú:" (1)–(7)** ở cuối BM01.
   - Xóa bỏ các chú thích in nghiêng `(Gửi một nơi)` / `(Gửi nhiều nơi)`.
   - Xóa bỏ mọi highlight màu vàng và phương án kính gửi không sử dụng.
4. **Xử lý khung "Mẫu số: BM../VB-2025" khi phát hành (Mặc định BỎ):**
   - **Đối với BM01:** Xóa Table 2 (chứa Text Box khung mẫu số ở góc trên bên phải trang 1).
   - **Đối với BM03A:** Xóa hẳn Table 0 (bảng chứa dòng chữ *"Mẫu số: BM03A/VB-2025 (Nghị định 30/2020/NĐ-CP)"*) trong Header. **Tuyệt đối giữ nguyên** Table 1 (chứa Logo Phương Thành, 4 dòng thông tin công ty 10pt và đường kẻ màu đỏ cam).
5. **Sửa lỗi chính tả gốc của mẫu:**
   - Thay thế `"Qúy"` thành **`"Quý"`**.
   - Thay thế `"Công công trường"` thành **`"Các công trường"`**.
   - Báo cáo rõ cho anh Nghĩa biết các lỗi chính tả đã được tự động xử lý.

---

## 5.1 QUY CHUẨN ĐẶC THÙ BM03A TRÌNH BAN LÃNH ĐẠO CÔNG TY (ANH NGHĨA DUYỆT 20/10/2026)

Khi soạn thảo văn bản nội bộ BM03A của Phòng KT-TC trình Ban Lãnh đạo Công ty phê duyệt:
1. **Header:**
   - Xóa bảng Mẫu số BM03A trong Header.
   - Giữ nguyên Logo và bảng thông tin Công ty; tạo paragraph đệm đầu tiên để hạ cụm chữ thông tin xuống ngang bằng đỉnh Logo (tránh Logo cao hơn text).
   - Dãn khoảng cách dòng trong cụm thông tin: `space_before = 2.5 pt`, `space_after = 2.5 pt`, `line_spacing = 1.15` (không để dính sát co cụm).
   - Kích hoạt `different_first_page_header_footer = True` và xóa header các trang sau để Header chỉ xuất hiện duy nhất ở trang 1.
2. **Số văn bản:** `Số:       /PT-KTTC` (cỡ 13, chữ thường, không đậm). Tận dụng trực tiếp paragraph đầu tiên của ô, xóa bỏ dòng trắng thừa phía trên dòng số.
3. **Địa danh, ngày tháng:** `Hà Nội, ngày ... tháng ... năm 2026` (cỡ 13, chữ nghiêng, căn phải).
4. **Trích yếu:** Dàn đều 2 bên (Justified / Ctrl+J), cỡ 12, chữ thường đứng (không in đậm, không in nghiêng, bỏ dấu `:` sau `V/v`).
5. **Kính gửi:** `Kính gửi: Ban Lãnh đạo Công ty` (cỡ 13, chữ thường không đậm, căn theo mẫu).
6. **Thể thức ký Phòng KT-TC:** Đúng 2 dòng (dòng trên: `PHÒNG KỸ THUẬT THI CÔNG`, dòng dưới: `TP. Đỗ Đắc Luận`, cỡ 13, in đậm, căn giữa), tuyệt đối không tách riêng dòng `TRƯỞNG PHÒNG`. Khoảng trống ký tên tương đương 5 dòng chuẩn (~75 pt / ~2,8 cm) để Trưởng phòng ký và đóng dấu.
7. **Nơi nhận:** Ghi đúng nguyên văn chuẩn: `- Như trên;` cùng các đơn vị phối hợp/thực hiện, kết thúc bằng `- Lưu: VT, KTTC.`
8. **Khối phê duyệt Lãnh đạo:** Đặt ngay dưới bảng ký Phòng KT-TC; tiêu đề căn giữa `Ý KIẾN BAN LÃNH ĐẠO CÔNG TY` (in hoa, in đậm, cỡ 13). Phía dưới để trống hoàn toàn để Lãnh đạo viết tay ý kiến và ký duyệt (không đặt trước tên Lãnh đạo, không để các dòng chấm kẻ).
9. **Định dạng file xuất:** Mặc định **chỉ xuất file Word (.docx)**, không cần xuất file .pdf (trừ khi anh Nghĩa yêu cầu).
10. **Quy chuẩn văn phong & Kiến trúc trình bày trình Lãnh đạo (Chuẩn hóa đột phá theo bản duyệt của anh Nghĩa 21/10/2026):**
   - **Kiến trúc Tờ trình 1 trang + Phụ lục bảng tính riêng (1-Page Memo + Separate Appendix):**
     + **Trang 1 (Tờ trình báo cáo chính):** Toàn bộ nội dung báo cáo, bảng chữ ký Phòng KT-TC và khối Ý kiến Ban Lãnh đạo Công ty nằm trọn vẹn trên **đúng 01 trang A4**. Thân bài chắt lọc tối đa chỉ 4 đoạn văn:
       * *Đoạn mở đầu:* "Sau khi kiểm tra, rà soát số liệu báo cáo của Ban Điều hành và tình hình thi công trên công trường, Phòng Kỹ thuật Thi công báo cáo Lãnh đạo Công ty một số nội dung sau:"
       * *Hiện trạng & Nguyên nhân:* Nêu ngắn gọn khối lượng BVTC và nguyên nhân phát sinh (phạm vi tiếp giáp đường cũ lẫn đất phải làm mới...).
       * *Kết quả kiểm tra của Phòng:* Nêu trực tiếp kết quả cốt lõi mà Phòng đã tính toán/xác định (ví dụ: hệ số thi công thực tế trên tuyến là 1.39).
       * *Kiến nghị duyệt dứt khoát:* Đề xuất rõ ràng khối lượng duyệt phát sinh thêm theo hệ số kiểm tra, nêu rõ số lượng trừ đi đợt 1 và số lượng giao Phòng KTKH cấp bổ sung đợt 2 còn lại.
       * *Khối ký & Phê duyệt:* Ký duyệt Phòng KT-TC và khối `Ý KIẾN BAN LÃNH ĐẠO CÔNG TY` nằm ngay ở đáy trang 1, giúp Ban Lãnh đạo ra quyết định và ký bút phê chỉ trong 10-15 giây.
     + **Trang 2 (Phụ lục số liệu chi tiết):** Toàn bộ bảng tính chi tiết nhiều dòng/cột (như bảng đối chiếu rà soát 18 dòng) được tách riêng thành **"PHỤ LỤC KIỂM TRA KHỐI LƯỢNG..."**, đảm bảo số liệu minh bạch, rõ ràng mà không làm loãng tờ trình và không làm vỡ phom dáng trang ký.

---

## 6. QUY TRÌNH TÁC NGHIỆP 5 BƯỚC KHÉP KÍN

### Bước 1: Tiếp nhận yêu cầu & Lựa chọn mẫu
- Xác định văn bản thuộc mẫu BM01 hay BM03A.
- Kiểm tra dữ liệu đầu vào; gộp các câu hỏi còn thiếu gửi anh Nghĩa.

### Bước 2: Khởi tạo bản nháp & Điền nội dung
- Gọi công cụ tự động để nhân bản file mẫu vào thư mục `99-Temp/`:
  ```bash
  python .agents/skills/soan-thao-cong-van/scripts/van_ban_engine.py clone [BM01|BM03A] [Ten_File_Nhap.docx]
  ```
- Biên tập nội dung, căn cứ pháp lý, bảng nơi nhận và người ký.
- Chạy làm sạch sơ bộ:
  ```bash
  python .agents/skills/soan-thao-cong-van/scripts/van_ban_engine.py clean 99-Temp/[Ten_File_Nhap.docx]
  ```

### Bước 3: Kiểm soát thể thức & Xuất file
- Đối chiếu bản thảo với **Checklist mục 7** và **Quy chuẩn 5.1**.
- Mặc định chỉ xuất file Word `.docx`. Chỉ thực hiện xuất PDF qua Word COM khi anh Nghĩa có yêu cầu riêng.
- Kiểm tra trực quan xem văn bản có bị rớt trang (tràn sang trang mới chỉ vài dòng), vỡ khung bảng nơi nhận hay không.

### Bước 4: Bàn giao bản nháp cho anh Nghĩa soát xét
- Gửi phản hồi báo cáo anh Nghĩa với các nội dung:
  1. Clickable link tới file `.docx` trong [99-Temp/](file:///d:/GGAI_QLDA/99-Temp/).
  2. Danh sách các mục `[CẦN BỔ SUNG: ...]` (nếu có).
  3. Báo cáo ngắn gọn kết quả và đề xuất Lãnh đạo quyết định.

### Bước 5: Ban hành chính thức & Ghi sổ theo dõi
- **Chỉ thực hiện khi anh Nghĩa duyệt ("duyệt", "phát hành"):**
  1. Chạy lệnh làm sạch chế độ phát hành (xóa bỏ triệt để khung/bảng Mẫu số):
     ```bash
     python .agents/skills/soan-thao-cong-van/scripts/van_ban_engine.py clean 99-Temp/[Ten_File_Nhap.docx] --release
     ```
  2. Đổi tên tiền tố từ `NHAP_` sang `BANHANH_`, chuyển cả 2 file `.docx` và `.pdf` vào thư mục dự án tương ứng: `01-DuAn/<MaDuAn>/01-HoSoPhapLy/02-CongVan/`.
  3. Ghi 1 dòng nhật ký vào file [So_van_ban_2026.xlsx](file:///d:/GGAI_QLDA/03-MauBieu/03-Word/02-SoTheoDoi/So_van_ban_2026.xlsx):
     ```bash
     python .agents/skills/soan-thao-cong-van/scripts/van_ban_engine.py log --so "[Số VB]" --ngay "[Ngày]" --mau "[BM01|BM03A]" --pb "P.KTTC" --nhan "[Nơi nhận]" --trich "[Trích yếu]" --ky "[Người ký]" --file "[Đường dẫn file]" --status "Đã ban hành"
     ```
  4. Giữ nguyên bản nháp trong `99-Temp/` làm lịch sử đối chiếu; không bao giờ ghi đè file đã phát hành (nếu sửa đổi, lập phiên bản `_v2`).

---

## 7. CHECKLIST 10 ĐIỂM KIỂM SOÁT CHẤT LƯỢNG VĂN BẢN

Trước khi gửi bản nháp cho anh Nghĩa duyệt, bắt buộc kiểm tra đạt toàn bộ 10 tiêu chí:

- [ ] **1. Mẫu biểu:** Đúng loại biểu mẫu (BM01 gửi ngoài / BM03A gửi nội bộ).
- [ ] **2. Số & Ký hiệu:** Đúng cú pháp `Số: .../PT-KTTC` (hoặc để trống đúng khoảng cách, không tự chế số).
- [ ] **3. Địa danh & Ngày tháng:** Lấy theo ngày ban hành thực tế (năm 2026), không giữ nguyên năm của mẫu cũ.
- [ ] **4. Trích yếu:** Cụm `"V/v ..."` ngắn gọn, phản ánh đúng trọng tâm công văn.
- [ ] **5. Kính gửi:** Chỉ còn duy nhất 1 phương án (1 nơi hoặc nhiều nơi), không còn các ghi chú mẫu.
- [ ] **6. Nội dung & Căn cứ:** Lập luận chặt chẽ, số liệu chuẩn xác, không có căn cứ tự suy diễn.
- [ ] **7. Tẩy sạch dấu vết mẫu:** Đã xóa toàn bộ số chỉ số trên (`¹⁰ ¹¹ ¹² ¹³`), số chú thích `(1)-(7)`, khối Ghi chú cuối bài và highlight vàng.
- [ ] **8. Người ký & Chức danh:** Phân định rõ Ký trực tiếp hay Ký thay (`KT. TỔNG GIÁM ĐỐC / PHÓ TỔNG GIÁM ĐỐC`), chừa đủ khoảng trống ký và đóng dấu.
- [ ] **9. Nơi nhận:** Đầy đủ các đầu mối: `Như trên;`, `TGĐ (để b/c);`, các đơn vị liên quan, và kết thúc bằng `Lưu: VT, KTTC.`
- [ ] **10. Bố cục trang:** Không bị tràn trang thừa dòng, không lệch bảng; Header/Logo BM03A còn nguyên vẹn và sắc nét.
