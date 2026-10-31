# Ma trận kiểm tra - móc nối trạng thái với điều khoản

Đây là bảng móc nối chính. Mỗi dòng là một trạng thái phải kiểm, kèm dạng điều kiện và vị trí điều khoản theo từng hệ tiêu chuẩn. Dùng mã dòng (VK-01, DG-03...) trong bảng tính, cột "Mã kiểm tra".

**Ký hiệu**
- `§?` = tiêu chuẩn có nội dung này nhưng số điều chưa đối chiếu; đọc bản gốc rồi điền.
- `[CH]` = cơ học cơ bản, không cần tiêu chuẩn cho phần công thức, nhưng hệ số và giới hạn vẫn cần nguồn.
- `[D04]` = hồ sơ nhà sản xuất; với thiết bị chế tạo sẵn đây là căn cứ khả năng, tiêu chuẩn chỉ để kiểm điều kiện sử dụng.
- Dạng điều kiện: `S ≤ R` (tác động ≤ khả năng), `S·K ≤ R` (có hệ số an toàn / tin cậy K), `δ ≤ [δ]` (biến dạng), `KT` (kiểm tra cấu tạo, định tính).

## Mục lục
1. VK - Ván khuôn
2. DG - Đà giáo, cột chống, trụ tạm, bệ đúc
3. NM - Nền, móng tạm, KCPT trên kết cấu vĩnh cửu
4. VV - Vòng vây cọc ván, hố đào, văng chống, neo, bịt đáy
5. TB - Xe đúc, MSS, giá lao, lao đẩy, cẩu
6. CT - Cầu tạm, cầu cho cẩu, sàn đạo, sàn thao tác
7. TH - Công trình thủy tạm và hệ nổi
8. TT - Tải trọng và tổ hợp (dùng chung)

## 1. VK - Ván khuôn

| Mã | Trạng thái | Dạng | Cầu [N01] | Dân dụng | Đối chiếu | Ghi chú |
|---|---|---|---|---|---|---|
| VK-01 | Áp lực ngang bê tông tươi lên ván thành | xác định tải | 5.13, Bảng 5.5 (theo phương pháp đầm, tốc độ đổ V, chiều cao H, k1, k2, k3) | [N02] Phụ lục A (bảng áp lực ngang §?) | [Q07] CIRIA R108 / DIN 18218; [Q08] | Chiều cao lớp gây áp lực bị giới hạn theo thời gian đổ; đổ dưới nước có công thức riêng trong Bảng 5.5 |
| VK-02 | Tải ngang do xả bê tông | xác định tải | 5.13, Bảng 5.6 | [N02] Phụ lục A §? | | Phụ thuộc cách xả và dung tích thùng |
| VK-03 | Tải đứng do đầm lên ván đáy | xác định tải | 5.13 a) | [N02] Phụ lục A §? | | |
| VK-04 | Ván mặt: uốn, võng cục bộ | S ≤ R; δ ≤ [δ] | 8.2; hệ số m ván khuôn Bảng 4.1; gỗ mục 11, thép mục 13 | [N02] Phụ lục A (độ võng cho phép §?); [N04] | | Giới hạn võng mặt lộ ra khác mặt bị che |
| VK-05 | Sườn, nẹp, xà gồ: uốn, cắt, võng | S ≤ R; δ ≤ [δ] | 8.2; mục 11 / 13 | [N02]; [N04] | | Sơ đồ liên tục hay đơn giản phải khớp cách nối thực tế |
| VK-06 | Ty giằng, bu lông, cùm | S·K ≤ R | 8.2; 4.3.5 | [N04] liên kết §?; [D04] | | Lấy khả năng theo nhà sản xuất ty, không theo thép tròn chung |
| VK-07 | Ván khuôn trượt | S ≤ R | 8.3 | | | |
| VK-08 | Ổn định ván thành, chống lật trước khi đổ (gió) | S·K ≤ R | 4.3.6, 5.16 | [N03] gió §? | | Giai đoạn chưa đổ, chưa giằng đủ |

## 2. DG - Đà giáo, cột chống, trụ tạm, bệ đúc

| Mã | Trạng thái | Dạng | Cầu [N01] | Dân dụng | Đối chiếu | Ghi chú |
|---|---|---|---|---|---|---|
| DG-01 | Dầm ngang, dầm dọc đỡ ván khuôn: uốn, cắt, ổn định ngang cánh nén | S ≤ R | 9.1; mục 13 | [N04] cấu kiện chịu uốn §? | [Q01] | |
| DG-02 | Cột chống / thanh đứng: bền, ổn định (uốn dọc) theo chiều dài tính toán thực có giằng | S ≤ R | 9.1.5; mục 13; hệ số m Bảng 4.1 | [N04] cấu kiện chịu nén §?; [N13] cho cột ống lồng | [Q01] sai lệch hình học | Kể lệch tâm đầu kích, độ vươn ống điều chỉnh |
| DG-03 | Cột chống ống lồng chế tạo sẵn | S ≤ R | [D04] | [N13] nhóm tải danh định; [D04] | | Không vượt chiều dài kéo dài lớn nhất của nhóm |
| DG-04 | Mối nối giáo, chân đế, đầu kích, cùm | S ≤ R | 9.1; mục 13; [D04] | [N04] liên kết §?; [D04] | | |
| DG-05 | Hệ giằng: đủ cứng, truyền lực ngang | S ≤ R; KT | 9.1.1 cấu tạo; 4.3.11 | [N04]; [N05] 2.3 | [Q01] tải ngang giả định | |
| DG-06 | Ổn định chống lật tổng thể (gió, đổ lệch, dòng chảy, va chạm) | S·K ≤ R | 4.3.6 CT (4-1), 4.3.8; gió 5.16-5.17; va ô tô 5.19 | [N02] (hệ số ổn định chống lật §?); [N03] gió | | Tải gây lật hệ số lớn, tải giữ hệ số nhỏ |
| DG-07 | Ổn định chống trượt | S·K ≤ R | 4.3.7 CT (4-2); Phụ lục B | [N03] | | |
| DG-08 | Biến dạng tổng và độ vồng đặt trước | δ ≤ [δ] | 4.3.10 (tải tiêu chuẩn, tăng võng mối nối bu lông thường, biến dạng dư tiếp giáp, lún tà vẹt - hộp cát); 5.20 lún nền | [N02] §? | | Cộng: đàn hồi + khe mối nối + tiếp giáp + lún nền |
| DG-09 | Trụ tạm (thân, mũ, liên kết chân) | S ≤ R; S·K ≤ R | 9.1.3, 9.1.4, 9.1.5; 9.2 nếu là trụ lao | | | Liên kết cột trụ với bệ có hệ số kH riêng trong Bảng 4.1 |
| DG-10 | Đà giáo lắp hẫng, nửa hẫng | S ≤ R | 9.1.4, 9.1.5 | | | |
| DG-11 | Bệ đúc dầm | S ≤ R; δ ≤ [δ] | mục 8, 10 | [N08] | | Lún lệch bệ làm nứt dầm khi căng |
| DG-12 | Yêu cầu an toàn bắt buộc về giàn giáo, chống đỡ tạm | KT | [N05] 2.2, 2.3 | [N05] 2.2, 2.3 | | Kiểm cả hồ sơ, nghiệm thu trước khi chất tải |
| DG-13 | Sàn công tác, giá treo, lan can, thang | S ≤ R; δ ≤ [δ]; KT | 6.7 (6.7.2 cấu tạo, 6.7.3 tính toán) | [N05] 2.2, 2.7 | [Q11] | Có kiểm độ võng ván sàn dưới tải tập trung |

## 3. NM - Nền, móng tạm, KCPT trên kết cấu vĩnh cửu

| Mã | Trạng thái | Dạng | Cầu [N01] | Dân dụng / khác | Đối chiếu | Ghi chú |
|---|---|---|---|---|---|---|
| NM-01 | Sức chịu tải nền dưới đế cột, tấm kê, dầm kê | S ≤ R | 10.3, 10.5; Phụ lục C | [N08] | [Q04] | Tải tập trung chân cột, không phải tải trung bình; nền bão hòa mùa mưa |
| NM-02 | Phân bố tải qua lớp đệm, tấm kê | [CH] + S ≤ R | 10.4 | [N08] | | |
| NM-03 | Lún và lún lệch giữa các chân | δ ≤ [δ] | 5.20; 10.5 | [N08] | | Giới hạn lún lệch lấy từ yêu cầu hình học của kết cấu được đỡ |
| NM-04 | Móng nông tạm: trượt, lật | S·K ≤ R | 4.3.6, 4.3.7 | [N08] | | |
| NM-05 | Cọc tạm: sức chịu dọc, nhổ, ngang; độ ngàm sau xói | S ≤ R | 10; Phụ lục I; 4.1.5 xói | [N07]; [N12] cảng | | Kiểm nhổ khi cẩu làm việc lệch |
| NM-06 | Đường cẩu, ray, tà vẹt, nền ray | S ≤ R | 6.1.1 (ray, tà vẹt, lớp ba lát); 5.12 lực cẩu | [N14] tải từ cẩu xuống nền | | |
| NM-07 | Kết cấu vĩnh cửu chịu tải tạm (bản, dầm, bệ) | S ≤ R | 6.7.3 (kiểm bộ phận công trình nhận tải); [N06] | [N17] | | Cường độ bê tông tại thời điểm chịu tải |
| NM-08 | Mái dốc gần chân giáo, mép hố đào | S·K ≤ R | 6.1.1 (khoảng cách chân taluy nền đắp tới mép hố); mục 7 | [N05] 2.8 | [Q04] | |

## 4. VV - Vòng vây cọc ván, hố đào, văng chống, neo, bịt đáy

| Mã | Trạng thái | Dạng | Cầu [N01] | Dân dụng / cảng | Đối chiếu | Ghi chú |
|---|---|---|---|---|---|---|
| VV-01 | Áp lực đất ngang lên vòng vây | xác định tải | 5.5; Phụ lục C (chỉ tiêu đất), **Phụ lục D** | [N09]; [N12] | [Q04], [Q06] | Chọn chủ động / tĩnh / bị động theo chuyển vị thực |
| VV-02 | Áp lực nước, mực nước thi công bất lợi (cao nhất và thấp nhất) | xác định tải | 5.6 CT (5-2); 4.2.3 | [N09]; [D03] | | Mỗi giai đoạn một mực nước bất lợi |
| VV-03 | Cao độ đỉnh vòng vây so mực nước thi công | KT | 4.2.3 b) | | | |
| VV-04 | Cọc ván không chống (công-xôn): độ ngàm, mômen, chuyển vị | S·K ≤ R; S ≤ R | 7.3.2, 7.3.3; hệ số m tường cọc ván Bảng 4.1 và mục 7 | [N09] | [Q05], [Q06] | |
| VV-05 | Cọc ván một tầng chống | S ≤ R | 7.3.4 | [N09] | [Q06] | |
| VV-06 | Cọc ván nhiều tầng chống, giai đoạn trước khi lắp tầng chống mới | S ≤ R | 7.3.5 (tên cần xác nhận); 7.3.6 | [N09] | [Q06] | Thường là giai đoạn khống chế |
| VV-07 | Đặc trưng tiết diện, vật liệu cọc ván | nhập liệu | [N10] (xem lưu ý số hiệu 3.4); [D04] | [N10]; [N11] cọc ống ván | | Cọc tái sử dụng: giảm tiết diện theo đo thực tế |
| VV-08 | Thanh chống, văng chống vách: nén, lệch tâm, ổn định | S ≤ R | 7.5; mục 13 | [N09]; [N04] | | Thanh dài cần giằng trung gian |
| VV-09 | Dầm đai (vành đai): uốn, cắt, liên kết | S ≤ R | 7.3; mục 13 | [N09]; [N04] | | |
| VV-10 | Neo trong đất (cọc neo, neo đứng, neo nằm) | S·K ≤ R | 6.6.2 CT (6-1) đến (6-11) | [N09] (neo §?) | [Q04] | Neo ứng suất trước: N01 không có mục riêng, cần nguồn bổ sung |
| VV-11 | Ổn định tổng thể (trượt sâu) | S·K ≤ R | 4.3.1; 7.3.2 | [N09] | [Q04] | |
| VV-12 | Trồi đáy, đùn đất | S·K ≤ R | 4.3.1 (trồi của đất nền); 7.3.6 | [N09] | [Q04], [Q06] | |
| VV-13 | Thấm, xói ngầm, cát chảy, lưu lượng bơm | S·K ≤ R; tính lưu lượng | 4.3.2; **Phụ lục J** | [N09] | [Q04] | Công suất bơm dự phòng |
| VV-14 | Đẩy nổi (bịt đáy, bệ, giai đoạn bơm khô) | S·K ≤ R | 4.3.8 CT (4-3) (dạng tổng quát độ nổi); 7.9 bê tông dưới nước | [N09] | [Q04] | Lực giữ lấy hệ số nhỏ; mực nước ngoài lớn nhất |
| VV-15 | Lớp bê tông bịt đáy: uốn, cắt, dính bám với cọc ván - cọc | S ≤ R | 7.9; mục 12 | [N17] | | Giả thiết dính bám phải có nguồn |
| VV-16 | Vòng vây đất (đê quai) | S·K ≤ R; KT | 7.2 (Bảng 7.1, 7.2.3) | | | |
| VV-17 | Khung dẫn hướng hạ cọc ván | S ≤ R | 7.8 | | | |
| VV-18 | Tháo chống từng tầng | S ≤ R | 4.3.4 (mọi giai đoạn); 4.3.11 | [N09] | | Kết cấu thay thế phải đủ tuổi |
| VV-19 | Ảnh hưởng xung quanh, quan trắc, ngưỡng | δ ≤ [δ]; KT | 4.1.6 | [N09]; [N05] 2.8 | | Ngưỡng từ thiết kế quan trắc [D07] |
| VV-20 | An toàn đào đắp, cofferdam | KT | [N05] 2.8, 2.9 | [N05] 2.8, 2.9 | | |

## 5. TB - Xe đúc, MSS, giá lao, lao đẩy, cẩu

| Mã | Trạng thái | Dạng | Cầu [N01] | Khác | Đối chiếu | Ghi chú |
|---|---|---|---|---|---|---|
| TB-01 | Xe đúc: khung chính, dàn treo, thanh treo, chốt | S ≤ R | Không có mục riêng: tải theo 5.9, 5.13, 5.16; kết cấu mục 13; [D04] | [N04] khi được chấp thuận | [Q09] | Xem tcvn-11815-chi-muc mục 9 |
| TB-02 | Xe đúc: neo sau, chống lật | S·K ≤ R | 4.3.6; Bảng 4.1 (kết cấu kim loại của neo giữ chống lật; neo chôn trong BT) | | | Thanh neo: khả năng theo nhà sản xuất, kiểm tình trạng |
| TB-03 | Xe đúc: di chuyển, gió khi ngừng | S·K ≤ R | 5.12, 5.16 | | | |
| TB-04 | MSS: kết cấu, gối, di chuyển | S ≤ R | 9.1, 5.12, 5.16; [D04] | | [Q09] | |
| TB-05 | Giá lao, cầu cho cẩu lao lắp | S ≤ R; S·K ≤ R | 6.1.4 Bảng 6.3; 5.10, 5.12; 9.6 | [N14] | | |
| TB-06 | Lao dọc: đường trượt, thiết bị trượt, lực ma sát, lực hông | S ≤ R | 9.4; 5.12 CT (5-9)-(5-13); 5.15 CT (5-17)-(5-19) | | | |
| TB-07 | Mũi dẫn, giá đón, kết cấu neo khi lao | S ≤ R | 9.4 | | | |
| TB-08 | Thiết bị kéo đẩy, hãm | S ≤ R | 9.5 | | | Trường hợp dừng đột ngột |
| TB-09 | Trụ lao cầu | S ≤ R | 9.2 | | | |
| TB-10 | Kích điều chỉnh ứng suất, vị trí, độ vồng | S ≤ R | 5.14; hệ số vượt tải kích Bảng 5.12 | | | |
| TB-11 | Phản lực tạm lên trụ, mố, dầm đã lắp | S ≤ R | 6.7.3; [N06] | [N17] | | |
| TB-12 | Cẩu: sức nâng - tầm với, ổn định, gió giới hạn | S ≤ R | 5.10; [D04] biểu đồ tải | [N14]; [N05] 2.4 | | Không suy biểu đồ tải |
| TB-13 | Cáp treo, móc, pa lăng | S·K ≤ R | 6.7.3.3 (hệ số cho cáp treo đà giáo) | [N16]; [N05] 2.4 | | |

## 6. CT - Cầu tạm, cầu cho cẩu, sàn đạo, sàn thao tác

| Mã | Trạng thái | Dạng | Cầu [N01] | Khác | Ghi chú |
|---|---|---|---|---|---|
| CT-01 | Cầu tạm thi công: mặt sàn, dầm, xung kích, tổ hợp | S ≤ R | 6.2.1, 6.2.2 (Bảng 6.4) | | Hoạt tải thực tế; lực hãm theo tốc độ hạn chế |
| CT-02 | Cầu cho cẩu chân dê: nhịp, trụ, độ võng giới hạn | S ≤ R; δ ≤ [δ] | 6.1.4 (Bảng 6.2, 6.3) | | Kiểm cọc chịu nhổ |
| CT-03 | Sàn đạo lắp ráp | S ≤ R | 9.3 | | |
| CT-04 | Sàn thao tác khoan cọc nhồi | S ≤ R | Không có mục riêng: 6.2 (cầu tạm), 6.7 (sàn công tác), 7.8 (khung dẫn hướng), 10 + Phụ lục I (cọc); tải máy khoan theo 5.10 | [N15] | Tải máy khoan khi rút ống vách, lực kích |
| CT-05 | Cao độ đáy nhịp so mực nước thi công, tĩnh không | KT | 4.2.3 c), 6.1.1 | | |
| CT-06 | Chống va trôi | S ≤ R; KT | 6.5; 5.21 | | |
| CT-07 | Va tàu vào trụ cầu tạm, sàn đạo | S ≤ R | 5.18 Bảng 5.11 | | |

## 7. TH - Công trình thủy tạm và hệ nổi

| Mã | Trạng thái | Dạng | Cầu [N01] | Cảng / khác | Ghi chú |
|---|---|---|---|---|---|
| TH-01 | Thùng chụp ngăn nước | S ≤ R; S·K ≤ R | 7.6; áp lực thủy động 5.7 (F, S cho thùng chụp) | | |
| TH-02 | Đảo nhân tạo | KT; S·K ≤ R | 7.7; 4.2.3 b) | | |
| TH-03 | Bê tông dưới nước: phễu, ống dẫn, sàn đỡ | S ≤ R | 7.9; áp lực bê tông đổ dưới nước Bảng 5.5 | | |
| TH-04 | Bến tạm (bến cọc, bến phao) | S ≤ R; S·K ≤ R | 6.3 (6.3.2) | [N12] | Tải va cập bến 5.18 |
| TH-05 | Triền tàu, hạ thủy | S ≤ R | 6.4 | | |
| TH-06 | Độ nổi hệ nổi, sà lan | S·K ≤ R | 4.3.8 CT (4-3); Bảng 4.1 (trụ nổi, sà lan) | | |
| TH-07 | Ổn định hệ nổi (tâm nghiêng, mép boong, đáy) | KT + tính | 4.3.9; 9.7, 9.8 | | Cẩu làm việc lệch trên sà lan |
| TH-08 | Nội lực trụ nổi do sóng | S ≤ R | 9.7; Phụ lục G; mômen quán tính hệ phao Phụ lục F | | |
| TH-09 | Thủy động, sóng lên phần ngập | xác định tải | 5.7 CT (5-3)-(5-8) | [N12] | |
| TH-10 | An toàn làm việc trên và dưới nước | KT | [N05] 2.13, 2.14 | | |

## 8. TT - Tải trọng và tổ hợp (dùng chung)

| Mã | Nội dung | Cầu [N01] | Dân dụng | Ghi chú |
|---|---|---|---|---|
| TT-01 | Danh mục tải | 5.1 Bảng 5.1 | [N03]; [N02] Phụ lục A | Lập đủ, loại không xuất hiện ghi lý do |
| TT-02 | Hệ số vượt tải / độ tin cậy | 5.22 Bảng 5.12 | [N03] §?; [N02] Phụ lục A (bảng hệ số vượt tải §?) | Không trộn hệ |
| TT-03 | Hệ số xung kích | 4.3.3; 5.9, 5.10; 6.2.2 | [N03] §? | |
| TT-04 | Hệ số tổ hợp | 4.3.3; 5.3 (ηc); 6.1.4 | [N03] §? | |
| TT-05 | Hệ số m, kH | 4.3.5 Bảng 4.1 | [N04] hệ số điều kiện làm việc §? | |
| TT-06 | Gió làm việc và gió bão | 5.16, 5.17 (có gió giới hạn khi thi công bị hạn chế) | [N03] §? | Kết luận phải nêu gió giới hạn làm việc |
| TT-07 | Tải người, dụng cụ | 5.11 | [N02] Phụ lục A §?; [N05] 2.2 | |
| TT-08 | Mực nước thi công | 4.2.3; 5.6 | [D03] | |
