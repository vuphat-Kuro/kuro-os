# Trình tự tính từng loại kiểm tra

Mỗi mục: mã trong ma trận, đầu vào, trình tự, đầu ra, bẫy thường gặp. Phần ghi `[CH]` là cơ học cơ bản, được dùng trực tiếp. Phần ghi `→ nguồn` là chỗ bắt buộc lấy từ điều khoản ở ma trận, không điền từ trí nhớ.

## Mục lục
1. Áp lực bê tông và ván khuôn thành
2. Dầm, xà gồ, sườn đỡ ván khuôn
3. Cột chống, thanh đứng giáo
4. Ổn định lật, trượt tổng thể
5. Biến dạng tổng và độ vồng đặt trước
6. Nền chân giáo, móng tạm
7. Cọc ván: công-xôn, một tầng, nhiều tầng chống
8. Văng chống, dầm đai
9. Trồi đáy, thấm, đẩy nổi, bịt đáy
10. Neo trong đất
11. Cầu tạm, sàn đạo, sàn thao tác
12. Hệ nổi, sà lan
13. Thiết bị chế tạo sẵn (xe đúc, MSS, giá lao, cẩu)

## 1. Áp lực bê tông và ván khuôn thành (VK-01 đến VK-06)

**Đầu vào:** chiều cao đổ, tốc độ đổ V (m/h, từ năng suất bơm / diện tích mặt bằng), phương pháp đầm (trong / ngoài), độ sụt, nhiệt độ hỗn hợp, dung trọng bê tông, thời gian bắt đầu ninh kết hoặc thời gian duy trì độ lưu động, kích thước cấu kiện, bố trí ty - sườn - nẹp.

**Trình tự:**
1. Tính V = năng suất đổ / diện tích mặt bằng đổ `[CH]`.
2. Chọn công thức áp lực lớn nhất theo phương pháp đầm và phạm vi V, H → nguồn ([N01] Bảng 5.5 hoặc [N02] Phụ lục A). Ghi rõ điều kiện áp dụng công thức đã thỏa.
3. Cộng tải ngang do xả bê tông → nguồn ([N01] Bảng 5.6). Mặt nghiêng: nhân theo quy tắc của nguồn.
4. Dựng biểu đồ áp lực theo chiều cao (tam giác đến độ sâu tới hạn rồi hằng số, hoặc theo nguồn) `[CH]`.
5. Truyền tải: ván mặt → sườn → nẹp → ty. Nội lực theo sơ đồ khớp với cách nối thực tế `[CH]`.
6. Kiểm uốn, cắt, võng từng bộ phận; ty kiểm kéo với khả năng [D04] và hệ số → nguồn.

**Đầu ra:** áp lực lớn nhất, tốc độ đổ lớn nhất cho phép (điều kiện áp dụng), hệ số sử dụng ván - sườn - nẹp - ty.

**Bẫy:** V lấy theo "đổ từ từ" không khớp năng suất bơm; bê tông tự lèn hoặc có phụ gia chậm ninh kết vượt phạm vi công thức (cần nguồn khác); quên k3 cho cấu kiện rộng; không ghi tốc độ đổ cho phép vào điều kiện kết luận.

## 2. Dầm, xà gồ, sườn đỡ ván khuôn (DG-01, VK-05)

**Đầu vào:** tải đứng (bê tông, cốt thép, ván khuôn, người - thiết bị, đầm), bước dầm, nhịp, tiết diện, vật liệu, liên kết đầu dầm, giằng cánh nén.

**Trình tự:**
1. Tải tiêu chuẩn từng loại → nguồn (TT-01, TT-07); tải tính toán = tiêu chuẩn × hệ số → nguồn (TT-02, TT-03).
2. Nội lực M, V, phản lực theo sơ đồ `[CH]`. Đổ lệch hoặc theo lớp: xét sơ đồ tải bất lợi từng giai đoạn.
3. Kiểm bền uốn, cắt, ổn định ngang cánh nén, ổn định cục bộ bản bụng tại gối → nguồn (mục 13 N01 hoặc N04).
4. Võng với tải tiêu chuẩn `[CH]`, so giới hạn → nguồn.

**Bẫy:** coi sàn gỗ là giằng cứng cho cánh nén (N01 mục 6.2.2 có quy định khi nào được coi là liên kết cứng); tải tập trung của bơm, ống dẫn, xe đầm không đưa vào.

## 3. Cột chống, thanh đứng giáo (DG-02 đến DG-05)

**Đầu vào:** phản lực từ dầm, chiều cao, vị trí giằng thực tế (hai phương), tiết diện, độ vươn ống điều chỉnh và đầu kích, sai lệch thẳng đứng cho phép, hồ sơ nhà sản xuất.

**Trình tự:**
1. Lực dọc tính toán lớn nhất trong các tổ hợp `[CH]` + hệ số → nguồn.
2. Chiều dài tính toán theo khoảng cách giằng **thực có** và điều kiện liên kết hai đầu; ghi rõ giả định.
3. Kể lệch tâm: đầu kích, mối nối lồng ống, độ nghiêng ban đầu → lượng lệch tâm theo nguồn hoặc [D04].
4. Kiểm bền và ổn định cấu kiện chịu nén (đúng tâm / lệch tâm) → nguồn (N01 mục 13 hoặc N04; cột ống lồng theo N13 và [D04]).
5. Nếu dùng khả năng chịu tải catalog: xác nhận điều kiện catalog (chiều cao, độ vươn, giằng) trùng với thực tế.
6. Hệ giằng: lực giằng giả định (tỷ lệ lực dọc) → nguồn; kiểm thanh giằng và liên kết.

**Bẫy:** chiều dài tính toán theo sơ đồ lý tưởng trong khi hiện trường giằng không liên tục; dùng catalog nhưng ống điều chỉnh vượt mức nhà sản xuất; bỏ lệch tâm.

## 4. Ổn định lật, trượt tổng thể (DG-06, DG-07, NM-04, VV-11)

**Đầu vào:** mọi tải đứng và ngang (gió làm việc, gió bão khi ngừng, đổ lệch, dòng chảy, va chạm), kích thước đáy, hệ số ma sát, neo - văng hiện có.

**Trình tự:**
1. Xác định trục lật và mặt trượt có thể `[CH]`.
2. Tách lực gây lật - trượt và lực giữ; áp hệ số: gây lật - trượt dùng hệ số lớn, giữ dùng hệ số nhỏ → nguồn ([N01] 4.3.8, Bảng 5.12).
3. Mômen gây lật M1, mômen giữ Mg `[CH]`; so theo điều kiện [N01] CT (4-1) với m theo loại gối → nguồn.
4. Trượt: lực trượt và lực giữ theo [N01] CT (4-2), hệ số ma sát Phụ lục B, hệ số kH → nguồn.
5. Có neo - văng: cộng lực giữ bằng khả năng chịu lực tính toán của neo - văng (không phải lực căng giả định).

**Bẫy:** dùng cùng hệ số cho lực gây và lực giữ; tính gió làm việc mà quên gió bão khi ngừng thi công; giàn chưa đổ bê tông (nhẹ) mới là trạng thái lật bất lợi.

## 5. Biến dạng tổng và độ vồng đặt trước (DG-08)

**Trình tự:**
1. Võng đàn hồi của hệ dưới tải tiêu chuẩn `[CH]` (hoặc từ phần mềm).
2. Cộng biến dạng mối nối (tăng theo loại liên kết), biến dạng dư tại chỗ tiếp giáp theo cặp vật liệu, lún tà vẹt kê, hộp cát → trị số theo [N01] 4.3.10.
3. Cộng lún nền chân giáo (mục 6 dưới đây).
4. Độ vồng đặt trước = tổng biến dạng dự kiến + độ vồng thiết kế của kết cấu chính (lấy từ hồ sơ thiết kế).

**Bẫy:** chỉ lấy võng đàn hồi từ phần mềm, bỏ khe mối nối và lún nền, làm cao độ hoàn thiện sai.

## 6. Nền chân giáo, móng tạm (NM-01 đến NM-05)

**Đầu vào:** phản lực chân cột lớn nhất (không phải trung bình), kích thước đế và tấm kê, cấu tạo lớp đệm, chỉ tiêu đất tại đúng vị trí (và khi bão hòa), mực nước ngầm, thí nghiệm hiện trường.

**Trình tự:**
1. Áp lực dưới tấm kê: phân bố qua lớp đệm theo góc lan truyền → nguồn (hoặc giả định ghi rõ) `[CH]` cho phép tính diện tích.
2. Sức chịu tải nền → nguồn ([N01] 10.3, 10.5 và Phụ lục C, hoặc [N08]); trường hợp nền bão hòa tính riêng.
3. Lún tổng và lún lệch giữa hai chân kề nhau → nguồn; so giới hạn từ yêu cầu hình học kết cấu được đỡ.
4. Cọc tạm: sức chịu nén, nhổ, ngang sau khi trừ chiều sâu xói → nguồn ([N01] Phụ lục I hoặc [N07]).

**Bẫy:** số liệu địa chất thiết kế xa vị trí; bỏ nền đắp - nền tự nhiên xen kẽ; bỏ giai đoạn tháo dỡ làm tải dồn sang chân còn lại.

## 7. Cọc ván: công-xôn, một tầng, nhiều tầng chống (VV-01 đến VV-07)

**Đầu vào:** địa tầng và chỉ tiêu (γ, c, φ theo điều kiện thoát nước phù hợp), mực nước trong - ngoài theo giai đoạn, tải mặt, cao độ đào từng bước, cao độ tầng chống, tiết diện cọc ván (thực tế nếu tái sử dụng).

**Trình tự:**
1. Áp lực ngang đất: chủ động, bị động, tĩnh → nguồn ([N01] Phụ lục D hoặc [N09]); chọn trạng thái phù hợp chuyển vị.
2. Áp lực nước: thủy tĩnh `[CH]` với mực nước bất lợi → nguồn cho việc chọn mực nước ([N01] 5.6, 4.2.3). Có thấm quanh chân: phân bố áp lực nước theo phương pháp → nguồn.
3. Tải mặt quy đổi thành áp lực ngang → nguồn.
4. Công-xôn: độ ngàm theo cân bằng mômen quanh chân hoặc phương pháp của nguồn, tăng chiều sâu theo hệ số → nguồn ([N01] 7.3.3).
5. Một tầng chống: phương pháp gối tự do hoặc ngàm theo nguồn ([N01] 7.3.4); lực chống, mômen lớn nhất, độ ngàm.
6. Nhiều tầng: **tính theo từng bước đào**, bước khống chế thường là ngay trước khi lắp tầng chống mới ([N01] 7.3.5-7.3.6 hoặc [N09]); phần mềm Plaxis / Geo5 cần kiểm thô.
7. Kiểm bền cọc ván với W thực tế → nguồn (mục 13 N01 hoặc N04; đặc trưng [N10] / [D04]).
8. Chuyển vị đầu tường so ngưỡng [D07].

**Bẫy:** một mực nước cho mọi giai đoạn; quên bước trước khi lắp chống; chỉ tiêu tổng hợp trong khi cần thoát nước / không thoát nước; coi cọc tái sử dụng như mới.

## 8. Văng chống, dầm đai (VV-08, VV-09)

**Trình tự:**
1. Lực chống từ bước 7, lấy giá trị lớn nhất qua mọi giai đoạn, cộng lực do nhiệt độ nếu nguồn yêu cầu.
2. Dầm đai: dầm liên tục trên gối là thanh chống, chịu tải phân bố bằng phản lực tường `[CH]`; kiểm uốn, cắt, ổn định cục bộ tại điểm chống → nguồn.
3. Thanh chống: nén lệch tâm (lệch tâm cấu tạo + tự trọng gây uốn), chiều dài tính toán theo giằng trung gian → nguồn.
4. Liên kết đầu chống - đai: ép mặt, hàn, sườn tăng cứng → nguồn.

## 9. Trồi đáy, thấm, đẩy nổi, bịt đáy (VV-12 đến VV-15)

**Trình tự:**
1. **Thấm:** lưới thấm hoặc phương pháp giải tích → nguồn ([N01] Phụ lục J cho lưu lượng); gradient thủy lực tại đáy so gradient tới hạn `[CH]` với hệ số an toàn → nguồn. Chọn công suất bơm có dự phòng.
2. **Trồi đáy** (đất dính) và **đùn đất** → nguồn ([N09] hoặc tài liệu đối chiếu); N01 chỉ nêu là trạng thái nhóm 1 (4.3.1).
3. **Đẩy nổi:** lực đẩy nổi = γw × thể tích chiếm chỗ dưới mực nước ngoài lớn nhất `[CH]`; lực giữ = trọng lượng bịt đáy + bệ + ma sát / dính bám với cọc (nếu có nguồn cho phép) với hệ số nhỏ; điều kiện theo dạng [N01] CT (4-3) và hệ số → nguồn.
4. **Bịt đáy:** bản chịu áp lực nước ngược, gối lên cọc hoặc tường `[CH]` cho nội lực; kiểm uốn - cắt bê tông không cốt thép → nguồn; dính bám bê tông - thép → nguồn.
5. Giai đoạn: bơm khô lần đầu, mực nước ngoài dâng nhanh, trước khi đổ bệ.

**Bẫy:** tính ma sát với cọc ván mà không có nguồn; quên kịch bản lũ khi hố đang khô.

## 10. Neo trong đất (VV-10)

**Trình tự (neo cọc, neo đứng, neo nằm theo [N01] 6.6):**
1. Lực dây chằng N, góc α; phân thành thành phần ngang và đứng `[CH]`.
2. Kiểm nén đất trước neo, nhổ neo theo các CT (6-1) đến (6-11) với hệ số → nguồn.
3. Kích thước neo: tham khảo bảng của nguồn, nhưng phải kiểm lại bằng tính.

Neo ứng suất trước (neo phụt vữa): N01 không có mục riêng → cần nguồn khác; thử tải neo theo chỉ dẫn dự án.

## 11. Cầu tạm, sàn đạo, sàn thao tác (CT-01 đến CT-04)

**Trình tự:**
1. Xe - máy thực tế: tải trục, vệt bánh, chân chống cẩu; vị trí bất lợi (tầm với nhỏ - tải lớn và tầm với lớn - tải nhỏ) → [N01] 5.10, 6.2.2.
2. Xung kích, lực hãm theo tốc độ hạn chế → nguồn.
3. Mặt sàn → dầm ngang → dầm dọc → xà mũ → cọc `[CH]` cho truyền lực.
4. Cọc: nén, nhổ, ngang; chiều dài ngàm sau xói; giằng dọc ngang chịu dòng chảy, sóng, hãm, va tàu → nguồn.
5. Sàn thao tác khoan nhồi: thêm lực khi rút ống vách, lực kích, rung → [D04] máy khoan.

## 12. Hệ nổi, sà lan (TH-06 đến TH-08)

**Trình tự:**
1. Trọng lượng tính toán (hệ số theo nguồn) và thể tích chiếm nước → độ nổi theo [N01] CT (4-3).
2. Ổn định: chiều cao tâm nghiêng dương, mép boong không ngập, đáy không nổi → [N01] 4.3.9; cẩu làm việc lệch tạo mômen nghiêng `[CH]`.
3. Nội lực hệ phao do sóng → [N01] Phụ lục G; mômen quán tính hệ ghép → Phụ lục F.
4. Neo giữ hệ nổi: lực dòng chảy + gió + sóng → [N01] 5.7, 5.16.

## 13. Thiết bị chế tạo sẵn (xe đúc, MSS, giá lao, cẩu)

Khả năng thiết bị lấy theo [D04]. Kiểm toán gồm:
1. Điều kiện sử dụng thực tế nằm trong phạm vi hồ sơ: tải lớn nhất, sơ đồ gối, độ dốc, gió giới hạn, trình tự.
2. Tác động của thiết bị lên kết cấu chính, trụ, nền → nguồn (TB-11, NM-07).
3. Các trạng thái không có trong hồ sơ (di chuyển, dừng đột ngột, chênh tải hai cánh, gió bão khi ngừng) → tính bổ sung theo mục 4, 5 của N01.
4. Thiết bị tự chế hoặc đã cải tạo: tính như kết cấu mới, không dựa vào hồ sơ cũ.
