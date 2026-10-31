# Sổ nguồn tiêu chuẩn và quy tắc dẫn nguồn

## Mục lục
1. Quy tắc dẫn nguồn
2. Sổ nguồn chuẩn (đã điền sẵn)
3. Lưu ý khi dùng - mâu thuẫn và thay thế đã biết
4. Mẫu sổ nguồn dự án và chỉ mục trị số đã trích
5. Tài liệu dự án bắt buộc (mã D)

## 1. Quy tắc dẫn nguồn

Mỗi hệ số, tải trọng, cường độ, giới hạn biến dạng, hệ số an toàn phải có một dòng dẫn nguồn:

`[Mã] - Điều/mục - CT/Bảng/Phụ lục - Trang`

Ví dụ: `[N01] - 5.13 - Bảng 5.5 - tr. __`, `[N05] - 2.3 - - tr. __`, `[CH] cơ học cơ bản`.

Khi đọc bản gốc người dùng gửi:
- Trích **vị trí** (mục, số công thức, số bảng, trang), **điều kiện áp dụng** và **đơn vị** của công thức, không chỉ chép công thức.
- Ghi ký hiệu của tài liệu để không nhầm với tài liệu khác (ví dụ n của N01 khác γf của N03).
- Không suy công thức từ đoạn văn mô tả. Tài liệu không nêu rõ thì ghi "tài liệu không nêu công thức".
- Hai tài liệu yêu cầu khác nhau cho cùng một kiểm tra: đánh dấu mâu thuẫn, hỏi người dùng dùng nguồn nào.
- Trị số đọc từ bản gốc ghi vào mục 4 (chỉ mục trị số) để lần sau không phải đọc lại.

## 2. Sổ nguồn chuẩn

Cột "Xác minh" cho biết đã kiểm tra những gì, **không** thay cho xác nhận hiệu lực của người dùng. Trạng thái "Đã đối chiếu (09/2026)" nghĩa là đã kiểm tra trên nguồn công bố: số hiệu tồn tại, quan hệ thay thế, phạm vi hoặc mục lục như ghi. "Cần xác nhận" nghĩa là chưa kiểm tra trong lúc lập skill.

### Tiêu chuẩn Việt Nam

| Mã | Số hiệu | Tên | Dùng cho | Xác minh |
|---|---|---|---|---|
| N01 | TCVN 11815:2017 | Thiết kế công trình phụ trợ trong thi công cầu | Căn cứ chính cho mọi KCPT thi công cầu đường bộ và đường sắt, theo trạng thái giới hạn: tải, hệ số, ổn định, vòng vây, ván khuôn, đà giáo, trụ tạm, lao lắp, hệ nổi, neo, nền móng tạm | Đã đối chiếu (09/2026): mục lục đầy đủ, xem `tcvn-11815-chi-muc.md`. Do Cục Đường sắt VN chủ trì biên soạn |
| N02 | TCVN 4453:1995 | Kết cấu BT và BTCT toàn khối - Quy phạm thi công và nghiệm thu | Ván khuôn, đà giáo công trình dân dụng: tải trọng, hệ số vượt tải, áp lực ngang (Phụ lục A), độ võng cho phép, tháo dỡ | Đã đối chiếu (09/2026): vẫn được viện dẫn rộng rãi; **đang có dự thảo TCVN 4453:202x soát xét**. Người dùng xác nhận bản đang áp dụng |
| N03 | TCVN 2737:2023 | Tải trọng và tác động | Tải, tổ hợp, gió cho KCPT dân dụng - công nghiệp; tiêu chuẩn này nêu phải kể tải xuất hiện trong thi công | Đã đối chiếu (09/2026): **thay thế TCVN 2737:1995**; Điều 11 và Phụ lục G thay Phụ lục M của TCVN 5574:2018 |
| N04 | TCVN 5575:2024 | Thiết kế kết cấu thép | Kiểm tra cấu kiện và liên kết thép của KCPT dân dụng - công nghiệp - cảng | Đã đối chiếu (09/2026): **thay thế TCVN 5575:2012**; phạm vi **không áp dụng cho cầu đường bộ, cầu đường sắt, công trình thủy lợi, công trình biển** |
| N05 | QCVN 18:2021/BXD | Quy chuẩn kỹ thuật quốc gia về an toàn trong thi công xây dựng | Yêu cầu bắt buộc: 2.2 giàn giáo và thang; 2.3 kết cấu chống đỡ tạm; 2.4 thiết bị nâng; 2.8 đào đắp, công trình ngầm; 2.9 cốp-phơ-đem, cai-sờn; 2.10 lắp dựng, tháo dỡ cấu kiện; 2.11 ván khuôn và thi công bê tông; 2.12 thi công cọc; 2.13 làm việc trên mặt nước; 2.14 dưới nước | Đã đối chiếu (09/2026): ban hành theo TT 16/2021/TT-BXD, hiệu lực 20/6/2022, thay QCVN 18:2014/BXD; mục lục như ghi |
| N06 | TCVN 11823:2017 (bộ nhiều phần) | Thiết kế cầu đường bộ | Kiểm tra tác động tạm lên kết cấu cầu chính; thép, BT khi N01 dẫn chiếu | Tồn tại bộ tiêu chuẩn đã đối chiếu (phần 5 Kết cấu bê tông). Số phần cho tải trọng, thép, nền móng, mố trụ: **cần xác nhận** |
| N07 | TCVN 10304:2014 | Móng cọc - Tiêu chuẩn thiết kế | Cọc tạm, móng cọc sàn đạo, trụ tạm (khi không theo N01 Phụ lục I) | Đã đối chiếu (09/2026). Lưu ý: viện dẫn TCVN 2737:1995 đã bị thay |
| N08 | TCVN 9362:2012 | Tiêu chuẩn thiết kế nền nhà và công trình | Sức chịu tải, lún nền móng nông tạm | **Cần xác nhận** số hiệu và hiệu lực |
| N09 | TCVN 14213-1:2024 | Tường barrette - Phần 1: Yêu cầu thiết kế thi công | Thiết kế tường và **kết cấu chống giữ** hố đào sâu (tham khảo SP 381.1325800.2018); Phần 2 là yêu cầu kỹ thuật thi công | Đã đối chiếu (09/2026). Không áp dụng cho công trình thủy lợi |
| N10 | TCVN 9685:2013 | Cọc ván thép cán nóng | Đặc trưng tiết diện, vật liệu cọc ván | Đã đối chiếu (09/2026) qua danh mục viện dẫn của TCVN 11820-4-1:2020. **Xem lưu ý 3.4** |
| N11 | TCVN 9245:2012; TCVN 9246:2012 | Cọc ống thép; Cọc ống ván thép | Vòng vây cọc ống, trụ tạm cọc ống | Đã đối chiếu (09/2026) qua danh mục viện dẫn của TCVN 11820-4-1:2020 |
| N12 | TCVN 11820 (bộ), trong đó 11820-4-1:2020 | Công trình cảng biển - Yêu cầu thiết kế; Phần 4-1 Nền móng | KCPT công trình cảng, bến tạm, tường cừ | Đã đối chiếu phần 4-1 (09/2026); các phần khác cần xác nhận |
| N13 | TCVN 13661:2023 | Cột chống thép kiểu ống lồng - Thông số kỹ thuật, thiết kế | Nhóm tải danh định, đánh giá cột chống bằng tính toán và thử nghiệm | Đã đối chiếu (09/2026). Không hướng dẫn cách sử dụng cột chống |
| N14 | TCVN 10202:2013 | Cần trục - Yêu cầu ổn định | Ổn định cẩu, tải truyền xuống nền đỡ cẩu (nhà sản xuất phải công bố) | Đã đối chiếu (09/2026) |
| N15 | TCVN 9394:2012; TCVN 9395:2012; TCVN 9393:2012 | Đóng và ép cọc; Cọc khoan nhồi; Thử tĩnh cọc | Thi công cọc tạm, sàn thao tác khoan cọc, thử tải | Đã đối chiếu (09/2026) qua danh mục viện dẫn |
| N16 | TCVN 4244:2005 | Thiết bị nâng - Thiết kế, chế tạo và kiểm tra kỹ thuật | Thiết bị nâng tự chế, móc, cáp, pa lăng | Tồn tại đã đối chiếu; hiệu lực **cần xác nhận** |
| N17 | TCVN 5574:2018 | Thiết kế kết cấu BT và BTCT | Kết cấu vĩnh cửu dân dụng chịu tải tạm; bệ BT tạm | **Cần xác nhận** hiệu lực |
| N18 | TCVN 9152:2012 | Công trình thủy lợi - Quy trình thiết kế tường chắn | Chỉ tường cứng; **không dùng cho tường cừ, tường cọc, tường có neo** | Đã đối chiếu phạm vi (09/2026). Ghi ở đây để tránh dùng nhầm |

### Tài liệu nước ngoài (chỉ dùng khi chỉ dẫn kỹ thuật cho phép, hoặc để đối chiếu)

Chưa xác minh phiên bản hiện hành khi lập skill; người dùng xác nhận năm ban hành trước khi dẫn.

| Mã | Tài liệu | Dùng cho |
|---|---|---|
| Q01 | EN 12812 | Đà giáo chống đỡ (falsework): phân loại thiết kế, tải, sai lệch hình học |
| Q02 | BS 5975 | Quy phạm công trình tạm và falsework, quy trình quản lý temporary works |
| Q03 | EN 1991-1-6 | Tác động trong quá trình thi công |
| Q04 | EN 1997-1 | Địa kỹ thuật: tường chắn, ổn định đáy, đẩy nổi, thấm |
| Q05 | EN 1993-5 | Cọc và cọc ván thép |
| Q06 | CIRIA C760 | Tường chắn ngàm (embedded retaining walls) |
| Q07 | CIRIA Report 108; DIN 18218 | Áp lực bê tông tươi lên ván khuôn thành |
| Q08 | ACI 347 | Ván khuôn |
| Q09 | AASHTO Guide Design Specifications for Bridge Temporary Works | KCPT cầu theo hệ AASHTO |
| Q10 | EAU (khuyến nghị công trình bến) | Tường cừ, vòng vây cảng |
| Q11 | EN 12811-1 | Giàn giáo công tác |

## 3. Lưu ý khi dùng - mâu thuẫn và thay thế đã biết

3.1 **KCPT cầu dùng TCVN 5575:2024?** Phạm vi TCVN 5575:2024 loại trừ cầu. Với KCPT phục vụ thi công cầu, căn cứ chính là N01 (mục 13 kết cấu kim loại). Chỉ dùng N04 khi chỉ dẫn kỹ thuật hoặc chủ đầu tư chấp thuận, và phải ghi vào `Gia_dinh`.

3.2 **Bảng tính còn dùng TCVN 2737:1995 hoặc TCVN 5575:2012** là dấu hiệu sao chép từ bảng tính cũ. Nêu trong rà soát; hỏi lý do (hợp đồng ký trước, chỉ dẫn kỹ thuật cố định phiên bản...).

3.3 **TCVN 4453:1995 đang soát xét.** Dự thảo TCVN 4453:202x (Viện KHCN Xây dựng) có thay đổi về ván khuôn - đà giáo. Khi phiên bản mới được công bố, cập nhật N02 và ma trận.

3.4 **Số hiệu cọc ván thép.** TCVN 11815:2017 viện dẫn "TCVN 9686:2013 cọc ván thép", trong khi TCVN 11820-4-1:2020 viện dẫn "TCVN 9685:2013 Cọc ván thép cán nóng". Có thể một trong hai là lỗi số hiệu. Người dùng tra số hiệu đúng trước khi dẫn trong hồ sơ.

3.5 **Đơn vị trong N01.** N01 dùng T, T/m², kG/m², kG/cm² và có Phụ lục K quy đổi. Bảng tính quy về kN, kPa, MPa và ghi hệ số quy đổi ở `Dau_vao`.

3.6 **Hệ số trong N01 không dùng lẫn với hệ số của N03 hoặc N06.** Ví dụ: tải tính toán theo N01 = tải tiêu chuẩn × n × (1+μ) × ηc (4.3.3); đừng nhân tải N01 với γ của N03.

3.7 **Động đất.** N01 (chú thích mục 5.2) không tính tải đặc biệt như động đất, sự cố máy móc cho KCPT. Nếu chỉ dẫn dự án yêu cầu khác thì theo chỉ dẫn.

3.8 **TCVN 9152:2012** chỉ cho tường cứng thủy lợi. Không dùng cho tường cừ, vòng vây cọc ván.

## 4. Mẫu sổ nguồn dự án và chỉ mục trị số đã trích

Xuất thành `so-nguon.md` trong thư mục dự án.

**Bảng nguồn dự án**

| Mã | Số hiệu / năm | Vai trò trong bài (chính / bổ sung / đối chiếu) | Bản gốc đã nhận? | Hiệu lực (người dùng xác nhận) | Ghi chú |
|---|---|---|---|---|---|
| N01 | TCVN 11815:2017 | chính | có / chưa | | |

**Chỉ mục trị số đã trích** (chỉ điền khi đọc từ bản gốc)

| Mã | Điều / CT / Bảng | Trang | Nội dung | Trị số / biểu thức | Đơn vị | Điều kiện áp dụng |
|---|---|---|---|---|---|---|
| | | | | | | |

## 5. Tài liệu dự án bắt buộc (mã D)

| Mã | Tài liệu | Vì sao cần |
|---|---|---|
| D01 | Chỉ dẫn kỹ thuật, điều khoản hợp đồng về biện pháp thi công | Quyết định hệ tiêu chuẩn, yêu cầu thẩm tra |
| D02 | Hồ sơ khảo sát địa chất (hố khoan gần vị trí nhất) | Chỉ tiêu đất, mực nước ngầm |
| D03 | Số liệu thủy văn: mực nước theo mùa, lũ, triều, lưu tốc | Mực nước thi công bất lợi, thủy động, xói |
| D04 | Hồ sơ nhà sản xuất: giáo, cột chống, cọc ván, xe đúc, giá lao, cẩu (biểu đồ tải) | Khả năng chịu lực thiết bị, điều kiện sử dụng |
| D05 | Bản vẽ biện pháp, trình tự thi công | Sơ đồ tính, giai đoạn |
| D06 | Kết quả thí nghiệm hiện trường nền (tấm nén, CBR, xuyên), thử tải cọc | Sức chịu nền thực tế |
| D07 | Thiết kế quan trắc, ngưỡng cảnh báo | Điều kiện hiệu lực của kết luận |
