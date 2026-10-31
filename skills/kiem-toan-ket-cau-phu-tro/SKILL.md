---
name: "Kiểm toán kết cấu phụ trợ"
description: "Kiểm toán kết cấu phụ trợ thi công (đà giáo, ván khuôn, xe đúc, cọc ván, hố đào, trụ tạm) theo TCVN 11815, 4453, 2737, 5575."
group: Xây dựng
source: vnp-hatang-bim (skill Claude của chủ brain, nhập 2026-10-09)
---

# Kiểm toán kết cấu phụ trợ thi công

## Khi nào dùng

Kiểm toán, rà soát kết cấu phụ trợ thi công cầu, hạ tầng, dân dụng, cảng; móc nối từng trạng thái kiểm tra với điều khoản TCVN 11815, 4453, 2737, 5575, QCVN 18. Gồm đà giáo, ván khuôn, cột chống, trụ tạm, xe đúc, MSS, giá lao, sàn đạo, cầu tạm, vòng vây cọc ván, hố đào, văng chống, neo, bịt đáy, hệ nổi, nền móng tạm. Dùng khi người dùng hỏi tính, kiểm tra, rà soát bảng tính các kết cấu trên, áp lực bê tông, ổn định, lật, trượt, đẩy nổi, trồi đáy, hoặc gửi kết quả Midas, Plaxis, Geo5 để soát, kể cả chỉ hỏi "có đủ chịu không". Không dùng cho kết cấu vĩnh cửu; lập phương án thi công thì dùng bien-phap-thi-cong.

Kết cấu phụ trợ là kết cấu chịu lực thật, chỉ tồn tại tạm thời nên hay bị tính sơ, và là nguồn của nhiều sự cố sập đổ. Skill này giúp Claude đi đúng quy trình, không bỏ sót trạng thái giới hạn, và **mỗi con số đều truy được về một điều khoản cụ thể**.

Người dùng là kỹ sư cầu đường - hạ tầng - cảng, vừa làm hiện trường vừa làm QC/QS và BIM. Không giảng lý thuyết cơ bản; đi thẳng vào sơ đồ tính, tải, tổ hợp, điều khoản và kết luận.

## Nguyên tắc cốt lõi

**1. Tách hai loại công thức.**
- **Cơ học và toán cơ bản** (cân bằng tĩnh học, nội lực dầm - khung theo sơ đồ, đặc trưng hình học tiết diện, công thức Euler, áp lực thủy tĩnh γ·h, quy đổi đơn vị): được dùng, ghi nguồn là `[CH] cơ học cơ bản`.
- **Mọi nội dung phụ thuộc tiêu chuẩn**: giá trị tải tiêu chuẩn, hệ số vượt tải / độ tin cậy, hệ số tổ hợp, hệ số xung kích, hệ số điều kiện làm việc m, hệ số tin cậy kH, hệ số uốn dọc, cường độ tính toán vật liệu và đất, áp lực bê tông tươi, giới hạn võng - chuyển vị, hệ số an toàn ổn định. Bắt buộc dẫn nguồn. **Không lấy từ trí nhớ**, kể cả khi "nhớ khá chắc".

Lý do: một hệ số sai trong kết cấu phụ trợ có thể dẫn tới sập đổ; tiêu chuẩn lại hay được thay thế (TCVN 2737:1995 → 2023, TCVN 5575:2012 → 2024, TCVN 4453:1995 đang soát xét), nên bản Claude nhớ có thể đã cũ.

**2. Dẫn nguồn theo định dạng** `[Mã] - Điều/mục - CT/Bảng số - Trang`, ví dụ `[N01] - 4.3.6 - CT (4-1) - tr. __`. Mã lấy từ `references/nguon-tieu-chuan.md`. Vị trí điều khoản trong `references/tcvn-11815-chi-muc.md` và `references/ma-tran-kiem-tra.md` đã được đối chiếu với mục lục bản công bố; **số trang và trị số phải đọc từ bản gốc người dùng gửi**. Chưa có bản gốc thì ghi `trang: cần bản gốc` và không điền trị số.

**3. Chọn một hệ tiêu chuẩn chính cho mỗi bài toán, không trộn.** TCVN 11815 dùng hệ số vượt tải n, hệ số m, kH và đơn vị T - kG; TCVN 2737:2023 dùng hệ số độ tin cậy về tải trọng theo cách tổ hợp riêng; TCVN 11823 theo LRFD. Trộn tải của hệ này với sức kháng của hệ kia là lỗi. Quy tắc chọn ở mục "Chọn hệ tiêu chuẩn" bên dưới.

**4. Thiếu căn cứ thì dừng đúng phần đó.** Ghi `CHƯA CÓ CĂN CỨ: <nội dung> - cần <tài liệu, điều khoản>`, rồi làm tiếp phần không phụ thuộc: sơ đồ tính, giai đoạn, danh mục tải, cơ học cơ bản, checklist. Không điền "giá trị tham khảo" cho có.

**5. Mâu thuẫn hoặc nghi hết hiệu lực thì báo.** Claude không tự xác định hiệu lực pháp lý; ghi vào bảng giả định để người dùng xác nhận. Các mâu thuẫn đã biết nằm trong `nguon-tieu-chuan.md` mục "Lưu ý khi dùng".

**6. Claude hỗ trợ lập và rà soát, không thay người ký.** Nói một lần, ngắn, ở kết luận; với đà giáo cao - nhịp lớn, xe đúc, MSS, giá lao, hố đào sâu, vòng vây dưới nước thì khuyến nghị thẩm tra độc lập.

## Chọn hệ tiêu chuẩn

| Loại công trình chính | Hệ chính cho tải - tổ hợp - ổn định | Kết cấu thép / BT của KCPT | Nền - móng tạm | An toàn |
|---|---|---|---|---|
| Cầu đường bộ, đường sắt (mọi KCPT phục vụ thi công cầu) | [N01] TCVN 11815:2017 | [N01] mục 12, 13; tiêu chuẩn cầu [N06] khi N01 dẫn chiếu. **Không mặc nhiên dùng [N04]** vì phạm vi N04 loại trừ cầu | [N01] mục 10, Phụ lục C, D, I, J; [N07] khi dẫn chiếu | [N05] |
| Dân dụng, công nghiệp | [N02] Phụ lục A (ván khuôn, đà giáo) + [N03] | [N04], [N13] cho cột chống ống lồng, [N17] | [N08], [N07] | [N05] |
| Hố đào nhà - tầng hầm | [N09] + [N03] | [N04], [N17] | [N08], [N07] | [N05] mục 2.8 |
| Cảng biển, công trình thủy | [N12] + [N01] mục 6.3, 7 cho công trình tạm dưới nước | [N04] hoặc theo chỉ dẫn dự án; [N10], [N11] cho cọc ván | [N12] | [N05] mục 2.13, 2.14 |
| Chỉ dẫn kỹ thuật dự án quy định khác | Theo chỉ dẫn kỹ thuật, ghi rõ vào sheet `Nguon` | | | |

Tiêu chuẩn nước ngoài (EN 12812, BS 5975, EN 1991-1-6, CIRIA C760, AASHTO Temporary Works...) chỉ dùng khi chỉ dẫn kỹ thuật dự án cho phép, hoặc làm đối chiếu. Ghi rõ vai trò trong bảng nguồn.

## Quy trình

**Bước 1 - Phân loại và giai đoạn.** Xác định nhóm hạng mục, đọc file tham chiếu tương ứng (bảng định tuyến). Một bài toán thường thuộc nhiều nhóm: đà giáo luôn kèm nền chân giáo; vòng vây luôn kèm văng chống, thấm, đẩy nổi.

**Bước 2 - Chọn hệ tiêu chuẩn và rà sổ nguồn.** Chọn hệ theo bảng trên. Mở `ma-tran-kiem-tra.md`, lấy các dòng trạng thái của hạng mục, liệt kê ngay điều khoản cần cho từng dòng và **tài liệu nào người dùng đã gửi, tài liệu nào còn thiếu**. Nếu thiếu bản gốc tiêu chuẩn chính, đề nghị gửi trước khi tính số.

**Bước 3 - Dữ liệu vào.** Theo danh sách trong file tham chiếu. Hỏi tối đa 2-3 điều quan trọng nhất; còn lại ghi giả định có đánh dấu. Ba thứ hay sai nhất: địa chất đúng vị trí, mực nước thi công bất lợi, thiết bị thực tế (hồ sơ nhà sản xuất, không phải catalog chung).

**Bước 4 - Sơ đồ tính và giai đoạn.** Mô tả sơ đồ (gối, liên kết, chiều dài tính toán theo giằng thực có, điều kiện biên). Liệt kê **mọi giai đoạn**: lắp dựng, chất tải, làm việc, biến đổi (dời, hạ, lao), tháo dỡ, và trạng thái ngừng thi công khi gió - lũ. Lắp dựng và tháo dỡ thường nguy hiểm hơn giai đoạn làm việc.

**Bước 5 - Tải trọng và tổ hợp.** Dựng bảng tải theo danh mục của hệ đã chọn (với [N01] là Bảng 5.1, đủ 20 loại, loại nào không có thì ghi "không xuất hiện - lý do"). Mỗi tải: giá trị tiêu chuẩn, nguồn, giai đoạn xuất hiện, hệ số (vượt tải lớn/nhỏ, xung kích, tổ hợp). Với kiểm tra ổn định, tải gây lật - trượt lấy hệ số lớn, tải giữ lấy hệ số nhỏ ([N01] 4.3.8).

**Bước 6 - Kiểm tra từng trạng thái.** Đi theo `ma-tran-kiem-tra.md` và trình tự trong `trinh-tu-tinh-toan.md`. Mỗi trạng thái ghi: dạng điều kiện, giai đoạn bất lợi nhất, nguồn, S, R, hệ số sử dụng, đạt hay không.

**Bước 7 - Đối chiếu độc lập.** Với kết quả phần mềm luôn có kiểm tra thô bằng cơ học cơ bản: tổng phản lực so với tổng tải, bậc độ lớn mômen - lực dọc, độ võng gần đúng. Xem `phan-mem.md`.

**Bước 8 - Tổng hợp.** Bảng hệ số sử dụng, trạng thái khống chế, **điều kiện áp dụng** của kết luận (tải lớn nhất, trình tự, tốc độ đổ bê tông, mực nước lớn nhất, gió giới hạn làm việc, ngưỡng quan trắc) và giả định còn treo.

**Bước 9 - Bàn giao.** Bảng tính Excel có công thức theo `bang-tinh-excel.md`, dựng khung bằng `scripts/tao_bang_tinh.py` (đọc skill `xlsx` trước). Mọi file của một hạng mục kiểm toán (Excel, `so-nguon.md`, ghi chú) nằm chung **một thư mục**. Rà soát nhanh thì trả lời trong hội thoại theo cùng khung.

## Định tuyến tham chiếu

| Khi bài toán liên quan tới | Đọc |
|---|---|
| Chọn tiêu chuẩn, mã nguồn, hiệu lực, mâu thuẫn đã biết | `references/nguon-tieu-chuan.md` |
| Trạng thái nào kiểm theo điều khoản nào (bảng móc nối chính) | `references/ma-tran-kiem-tra.md` |
| Vị trí điều khoản TCVN 11815:2017 theo từng nội dung | `references/tcvn-11815-chi-muc.md` |
| Trình tự tính từng loại kiểm tra (đầu vào - bước - đầu ra - bẫy) | `references/trinh-tu-tinh-toan.md` |
| Đà giáo, ván khuôn, cột chống, trụ tạm, bệ đúc | `references/da-giao-van-khuon.md` |
| Vòng vây cọc ván, hố đào, văng chống, neo, bịt đáy | `references/ho-dao-coc-van.md` |
| Xe đúc, MSS, giá lao, lao đẩy, sàn đạo, cầu tạm, cẩu | `references/thiet-bi-thi-cong.md` |
| Đê quây, thùng chụp, đảo nhân tạo, sàn thao tác khoan cọc, bến tạm, hệ nổi - sà lan | `references/cong-trinh-thuy-tam.md` |
| Nền, móng tạm, đường cẩu, KCPT đặt trên kết cấu vĩnh cửu | `references/nen-mong-tam.md` |
| Midas, Plaxis, Geo5, Excel | `references/phan-mem.md` |
| Cấu trúc file Excel kết quả, quy ước hệ số sử dụng | `references/bang-tinh-excel.md` |

## Chế độ rà soát bảng tính của người khác

Không tính lại từ đầu. Rà theo thứ tự:
1. Hệ tiêu chuẩn có nhất quán không? Có trộn hệ số vượt tải của hệ này với cường độ của hệ kia không? Có dùng tiêu chuẩn đã bị thay thế (TCVN 2737:1995, TCVN 5575:2012) mà không có lý do không? Có dùng TCVN 5575 cho KCPT cầu mà không có chấp thuận không?
2. Mỗi hệ số, công thức có nguồn đến cấp điều - bảng không?
3. Giai đoạn có đủ không, nhất là lắp dựng, tháo dỡ, trước khi lắp tầng chống mới, mực nước thi công bất lợi (cả cao nhất và thấp nhất)?
4. Sơ đồ tính có khớp biện pháp thực tế (giằng, khoảng cách chống, liên kết, lệch tâm đầu kích)?
5. Có bỏ trạng thái nào trong ma trận không, nhất là ổn định tổng thể, nền chân chống, biến dạng mối nối, đẩy nổi?
6. Đơn vị (T, kG, kN), dấu, tổ hợp có nhất quán không?
7. Có dấu hiệu sao chép bảng tính cũ (tiêu chuẩn cũ, địa danh cũ, chiều cao - khoảng cách không khớp bản vẽ)?

Báo cáo theo mức độ: lỗi ảnh hưởng an toàn trước, sai sót trình bày sau.

## Cách trình bày kết luận

Nêu thẳng: đạt / không đạt / chưa đủ cơ sở kết luận; trạng thái khống chế; điều kiện đi kèm; việc còn treo. Không viết "kết cấu đảm bảo an toàn" chung chung khi còn mục `CHƯA CÓ CĂN CỨ` hoặc giả định chưa xác nhận ở trạng thái khống chế.

## Sổ nguồn giữa các phiên

Skill đã cài là tệp cố định. Khi người dùng gửi bản gốc tiêu chuẩn, trích vị trí + trị số cần dùng vào `so-nguon.md` của dự án (mẫu trong `nguon-tieu-chuan.md`) và xuất cùng thư mục với bảng tính để họ gửi lại phiên sau. Muốn nhúng cố định vào skill thì cập nhật `assets/so-nguon.json` và `nguon-tieu-chuan.md` rồi đóng gói lại.
