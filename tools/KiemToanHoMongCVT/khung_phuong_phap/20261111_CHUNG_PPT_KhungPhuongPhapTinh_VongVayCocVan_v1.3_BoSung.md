---
type: wiki
status: active
tags: [wiki, qlda, kcpt, vong-vay-coc-van]
created: 2026-11-09
version: v1.3 (bản bổ sung, ĐÃ DUYỆT 11/11/2026)
bo_sung_cho: 20261106_CHUNG_PPT_KhungPhuongPhapTinh_VongVayCocVan_v1.2.md (ĐÃ DUYỆT 06/11/2026, giữ nguyên, không ghi đè)
ap_dung_cho: 99-Temp/NHAP_kiem_toan_vong_vay.html, SHA 58394fd073ec (sau pha 3D-33)
approved: 2026-11-11
approved_by: Kiều Linh Nghĩa - Phó phòng KT-TC
nguon_du_thao: 99-Temp/qlda/NHAP_20261109_KhungPhuongPhapTinh_VongVayCocVan_v1.3_BoSung.md (sao lưu _backup/20261111/)
ap_dung_cho_sha: 975831955a0e

---

> **Trạng thái: ĐÃ DUYỆT 11/11/2026 (anh Kiều Linh Nghĩa).** Bản gốc là dự thảo xin ý kiến; nội dung dưới đây giữ nguyên như bản dự thảo đã trình. Đây là đề xuất xin ý kiến anh Kiều Linh Nghĩa theo quy định "mọi thay đổi khung phải xin ý kiến". Khung v1.2 vẫn là bản đã duyệt cho đến khi anh chấp thuận bản này.
> Bản này **không đổi khung bốn trục và sáu module**. Nó ghi lại (A) các thay đổi phương pháp đã làm trong chương trình kể từ v1.2 mà văn bản v1.2 chưa phản ánh, (B) các quyết định ngày 09/11/2026, (C) phạm vi chưa thực hiện, (D) các điểm còn chờ anh quyết.
> Nhãn: `[ĐÃ XÁC MINH]` (đọc văn bản gốc), `[NGƯỜI DÙNG KHAI]` (anh chốt hoặc cung cấp), `[GIẢ THIẾT]` (em đặt), `[CẦN KIỂM TRA]`.
> Mã `CT-Bn` là mã sửa chương trình của các đợt phân tích mẫu (07/11/2026), đặt tiền tố CT để không trùng mã `[B1]` đến `[B12]` của văn bản rà soát trong v1.2. Nguồn chi tiết từng mã: README trong `99-Temp/qlda/mau_tinh/dotN/`.

## KẾT LUẬN 10 GIÂY

- Từ v1.2 đến nay chương trình có **20 mục sửa phương pháp hoặc kết luận** (CT-B1 đến CT-B13 trừ CT-B5 chưa quyết, cộng Q1, I5, N1, W1, G1, G3, G4, 3D-6b), **10 thay đổi cách xác định hoặc nạp đầu vào** (E1 đến E10) và **8 quyết định ngày 09/11/2026** (D7 đến D14). Tất cả đều đã được anh duyệt hoặc chốt trong các phiên làm việc; văn bản khung chưa ghi. CT-B5 (lớp vắt qua mực nước ngầm) chưa có căn cứ, nằm ở Phần C.
- Quyết định D7 đã **sửa lại theo đúng chữ TCVN 11815 7.3.5.3**: t là chiều sâu đóng cọc tối thiểu, tính trước (lớn nhất của t ổn định, t cấu tạo 7.3.2.1, t đất chồi 7.3.2.2), rồi mới đặt gối tại t/2. Không còn chỗ nào khác chữ tiêu chuẩn.
- Còn **2 điểm tiêu chuẩn không quy định** mà chương trình dùng giả thiết: sơ đồ gối cho giai đoạn có bịt đáy nhưng chưa hút cạn (anh chốt giữ gối 0,5 m) và hệ số hao mòn cừ (mặc định 1,0). Xem Phần B.

---

## PHẦN A. THAY ĐỔI PHƯƠNG PHÁP KỂ TỪ v1.2 (đã làm, đã duyệt)

### A1. Áp lực và nước (Module 1)

| Mã | Nội dung | Vị trí v1.2 | Nguồn, duyệt |
|---|---|---|---|
| CT-B1 | Đất trên mực nước dùng γ tự nhiên, dưới mực nước dùng γ_đn. Trước đó phần đất khô bị tính theo γ_đn (σ thiếu, cả chủ động và bị động) | M1.1, M1.2 | dot1 mục 3, 5; duyệt 07/11/2026 |
| CT-B2 | Mặt trong Sơ đồ 2 (7.3.2.6): phần lớp nằm trên mực nước trong hố dùng γ tự nhiên | M1.2 | dot1; duyệt 07/11/2026 |
| CT-B6 | Dưới đáy đào, trong vùng lớp không thấm: Sơ đồ 2 không có nước trong hố; Sơ đồ 1 chỉ có nước đến cùng độ sâu thấm h_B như phía ngoài | M1.2 | dot2 mục 4, 7; duyệt 07/11/2026 |
| CT-B7 | Phụ tải cột nước trong hố lên lớp sét (Sơ đồ 2) tính đến mặt lớp sét, đối xứng với phía ngoài | M1.2 | dot2; duyệt 07/11/2026 |
| Q1 | Áp lực thủy tĩnh lấy **hiệu** nước ngoài trừ nước trong theo Hình 7.13 (trang 56), 7.3.4.1, 7.3.2.5, thay cho D2. Đã ghi chú thay thế trong v1.2 | M3.2, D2 | dot5 mục 7; duyệt 07/11/2026 "Đổi theo Hình 7.13" |
| D6 (v1.2) | Giữ nguyên: bắt buộc kiểm cả hai sơ đồ 7.3.2.6, kết luận theo sơ đồ bất lợi | M1.2, M3.2 | v1.2 |

### A2. Biện pháp thi công và giai đoạn (Trục 4)

| Mã | Nội dung | Nguồn, duyệt |
|---|---|---|
| CT-B3 | Chế độ AUTO: MNTC không cao hơn mặt đất thì đào hở (C1, C2), kể cả khi có bịt đáy. Ở kịch bản rút nước, mực nước trong hố không được cao hơn mực nước ngoài | dot1; 07/11/2026 |
| CT-B4 | Đào hở đến đáy hố (đáy bịt đáy nếu có), rồi thêm giai đoạn "đổ bịt đáy, hố khô" với gối 0,5 m dưới mặt bịt đáy (7.3.4.3, 7.3.5.4) | dot1; 07/11/2026 |
| CT-B8 | W2 có bịt đáy, đất tại đáy bịt đáy là đất thấm và MNTC cao hơn đáy bịt đáy thì chọn kịch bản 2 (đào trong nước rồi bịt đáy, TCVN 11815 7.3.2.5). Đất dính hoặc mực nước thấp hơn đáy thì giữ đào hở | dot2; 07/11/2026 |
| G1 | Thêm giai đoạn đào công xôn trước khi lắp T1 (T1 dưới mặt đất, từ 2 tầng chống) và các giai đoạn tháo giằng từ dưới lên sau khi đổ bệ và chèn khe bệ - cừ. Gối chèn bệ **không có trong TCVN**, [GIẢ THIẾT] | Đợt 1 (duyệt 06/11/2026) theo ghi chú trong mã chương trình |
| 3D-6b | Đáy hố một nguồn `v11FinalDredge()`: sâu hơn trong đáy đào hình học và đáy đào thấp nhất của danh sách giai đoạn sửa tay. Mặt đất một nguồn `v11GroundEl()` | M2, Bước 0; duyệt 07/11/2026 "Duyệt 3D-6b" |

### A3. Chống lật và độ bền cừ (Module 3, 4)

| Mã | Nội dung | Vị trí v1.2 | Nguồn, duyệt |
|---|---|---|---|
| CT-B9 | Lưới dầm cừ chèn nút đúng vị trí gối (trước đó làm tròn gối về nút gần nhất) | M4.1 (số) | dot5 mục 5; 07/11/2026 |
| CT-B10 | Chèn thêm nút tại cao độ áp lực đổi đột ngột (mực nước, đáy đào, mặt bịt đáy, ranh lớp) | M4.1 (số) | dot5 mục 6; 07/11/2026 |
| CT-B11 | Độ bền cừ **bao mọi sơ đồ 7.3.2.6**, kể cả khi kiểm tra lật đã chọn sơ đồ chi phối. Mỗi sơ đồ dùng gối t/2 theo t của chính nó; M lấy sơ đồ lớn nhất; phản lực từng gối lấy trị tuyệt đối lớn nhất | M4.1 | dot5 mục 8; 07/11/2026 |
| CT-B12 | Kết luận chống lật theo FS ở **chiều dài cừ thật**. Sơ đồ chi phối là sơ đồ có FS nhỏ nhất. FS < 1 chỉ chấp nhận khi phần thiếu nằm trong mức giảm chiều sâu 10% hoặc 15% của 7.3.4.1; nếu FS giảm khi cừ dài thêm (đất yếu dưới đáy hố) thì KHÔNG ĐẠT, ghi "cần kiểm tra trồi đáy hoặc gia cố đất". S1 công xôn chưa bịt đáy giữ theo t0 + Δt | M3.2 | dot6 mục 6; 07/11/2026 |
| CT-B13 | Ngưỡng số trong `solveBeamFEM1D` từ 1e-9 lên 1e-6 (sửa lỗi lưới, M sai ở T25 và T3 tham khảo) | số | dot7 mục 2.1; 07/11/2026 |
| I5 | Mẫu số của (I4) giữ dạng (I5): (γ_bh - γ_n)·H·B1 + γ_n·H1·B1. Dạng (I1) cho K = 0,973 với ca HK chỉ ghi tham khảo | M2.3 | dot16 "Giữ I5"; 07/11/2026 |

### A4. Khung chống (Module 5)

| Mã | Nội dung | Nguồn, duyệt |
|---|---|---|
| N1 | Tầng neo chịu kéo: N_h = max[1,1·q·(l_i + l_i+1)/2; phản lực lớn nhất dầm gông liên tục] [GIẢ THIẾT: (7-15) viết cho thanh chống]; thanh neo theo TCVN 5575:2024 7.1.1.1 (4); dầm gông 8.2.1 (40); cọc neo, khối neo N ≤ R với R do anh khai. Ngoài khung S4 nhưng neo là gối của cừ | dot3 mục 6; 07/11/2026 "Làm N1" |
| W1 | Mối nối hàn góc đầu thanh: TCVN 5575:2024 14.1.7, Bảng 41, 42, (182a), (182b), (183), Bảng C.1; đường hàn quanh chu vi H [GIẢ THIẾT]; lực nén truyền qua đường hàn (thiên an toàn) | dot4 mục 8; 07/11/2026 "Làm W1" |
| G3, G4 | Ổn định nén uốn TCVN 5575:2024 9.2.2, 9.2.4, 9.2.5, 9.2.8, 9.2.9 (Bảng D.2, D.3); cột chống tạm TCVN 11815 7.3.6.1 và TCVN 10304 | Đợt 2 (06/11/2026) |

### A5. Thay đổi cách xác định đầu vào (không đổi công thức)

| # | Nội dung | Nguồn |
|---|---|---|
| E1 | Danh mục cừ 9 loại (FSP, NSP) theo bảng tra anh gửi; bề rộng một tấm theo loại cừ; NSP-IIW A = 78,7 cm² (bảng ghi nhầm 787,0, anh xác nhận) | 3D-14, 3D-15 |
| E2 | Cọc góc mặc định a = 0,373 m, b = 0,246 m, có nút đổi hai cạnh. Mở rộng so với bệ mỗi bên mặc định ≥ 0,9 m; số tấm theo chiều rộng chốt trước, rồi theo chiều dài; **số tấm mỗi phương phải lẻ** (cọc sát cọc góc là cọc úp); hố a, b theo tim cừ tự tính | 3D-14, 3D-19 |
| E3 | Bịt đáy: nhập chiều dày; đỉnh = đáy bệ - 0,1 m (lót); đáy = đỉnh - chiều dày; L_b = khoảng cách lớn nhất từ cọc khoan nhồi biên đến cừ, L_g = khoảng cách lớn nhất giữa hai cọc, tính từ lưới cọc. Lưới không vuông góc đủ chỗ thì nhập tay | 3D-8, 3D-17 |
| E4 | Dầm biên khung chống: chiều dài dầm là ô nhập chính; khe hở δ mặc định 0, tính từ mép trong cọc ngửa = tim hàng cọc trừ chiều cao mặt cắt cọc ván h; khe và chiều dài sửa qua lại được; nhập theo từng tầng | 3D-19, 3D-20, 3D-23 |
| E5 | Thép hình khung chống lấy từ TCVN 7571-16:2017 Bảng 4 (53 dòng); H890x299 Zx = 7610 (bảng in 7160 là đảo chữ số, anh xác nhận) | 3D-21, 3D-22 |
| E6 | Ô β đổi nhãn "hệ số triết giảm áp lực thấm" theo TCVN 10400:2015 Phụ lục I, Bảng I1 (sét 0,50 đến 0,80; cát pha 0,80 đến 0,90; cát 1,00), không phải hệ số hoạt tải của TCVN 11815 | 3D-16 |
| E7 | Thanh chéo góc nhập theo từng góc: thanh 1 hai cạnh góc vuông, thanh sau khoảng cách đầu thanh trên mỗi thanh biên; mặc định đối xứng 4 góc | 3D-25 đến 3D-28 |
| E8 (CT-B14) | Nạp tệp JSON giữ `sand_class`, `t_min_2m`, `is_weak`, `gamma_s`, `e` của lớp đất (trước đó bị bỏ, về mặc định cát bột và không yếu; ảnh hưởng m1 của (7-5), η_w nền yếu, kiểm tra 7.3.2.1) | dot8; duyệt 07/11/2026 |
| E9 (CT-B15) | Bảng 5A đọc đúng tiết diện vành đai từ `plan_config.waler_profile` (trước đó hiển thị 2xH350x350 trong khi khung tính bằng H400x400); chỉ đổi hiển thị | dot8; duyệt 07/11/2026 |
| E10 (CT-B16) | Nạp tệp JSON giữ mọi trường của tầng chống, kể cả `kind` và `anchor` của tầng neo N1 (trước đó tầng neo nạp lại thành thanh chống thường) | dot8; duyệt 07/11/2026 |

---

## PHẦN B. QUYẾT ĐỊNH NGÀY 09/11/2026

| Mã | Quyết định (anh chốt) | Căn cứ và ghi chú |
|---|---|---|
| **D7** | **Gối dưới của cừ.** (a) Hố có bịt đáy, sau khi đổ bịt đáy **và cả giai đoạn có bịt đáy nhưng chưa hút cạn** (T11 GĐ2 đến GĐ4): gối 0,5 m dưới mặt trên bịt đáy. (b) Giai đoạn chưa có bịt đáy (xói hút đến đáy bịt đáy, hoặc hố không bịt đáy), có tầng chống: gối tại t/2 dưới đáy đào, **t = chiều sâu đóng cọc tối thiểu theo 7.3.5.3**, tính trước: t = max(t ổn định lật 7.3.4.1 và 7.3.5.1, đã giảm 10% hoặc 15% theo 7.3.5.2 nếu có; t cấu tạo 7.3.2.1; t chống đất chồi 7.3.2.2 theo (7-5)). t cấu tạo: có lớp lót ngăn nước 1 m; không có thì 2 m với đất tick t ≥ 2 m, 1 m với đất còn lại. t đất chồi: đất rời tại đáy đào, không có bịt đáy. Ổn định lật không tìm được t trong chiều dài cừ thì dầm cừ lấy chiều sâu ngập thật | TCVN 11815 7.3.4.3 (bản in thiếu "t/", Hình 7.13b có h + t/2), 7.3.5.3, Hình 7.16b [ĐÃ XÁC MINH trên PDF]. 7.3.4.3 (một tầng) chỉ dẫn t theo 7.3.4.1; chương trình dùng định nghĩa 7.3.5.3 cho cả hai [GIẢ THIẾT đồng bộ]. Ví dụ T11 GĐ1: t ổn định 0, t cấu tạo 1,00 m (có lớp lót) thì t = 1,00 m, gối -12,60 m, M = 48,33 T.m, σ = 2129 kg/cm² (tỷ số 0,794, đạt). Gối sau bịt đáy theo (a) vẫn [GIẢ THIẾT] ở giai đoạn chưa hút cạn vì TCVN chỉ nêu trường hợp hút cạn. [NGƯỜI DÙNG KHAI, anh chốt 09/11/2026] |
| **D8** | **Thép hình khung chống SS400** (JIS G 3101:2015): f_y theo chiều dày, 245 MPa khi t ≤ 16 mm, 235 MPa khi 16 < t ≤ 40 mm; **tra riêng cho cánh (t_f) và bụng (t_w)** (anh chốt). Có ô chọn "Nhập tay" | TCVN 5575:2024 Phụ lục M (tham khảo), Bảng M.1 tiếp theo, PDF trang 235 [ĐÃ XÁC MINH]. Ứng suất pháp (nén, uốn) lấy f_y cánh, thấp hơn nên thiên an toàn [GIẢ THIẾT]; f_y bụng dành cho kiểm tra cắt (Bảng 2: f_vd = 0,58·f_y/γ_m), chương trình chưa kiểm cắt thanh. Quy ước 1 MPa = 10 kg/cm² như mác cừ. Thép không phải H TCVN 7571-16 dùng ô nhập tay |
| **D9** | n_g = 1,1 (trọng lượng bản thân thép hình khung chống); n_w = 1,0 (thủy tĩnh); thêm ô nhập | TCVN 11815 Bảng 5.12 (đọc từ bản trích văn bản): không luân chuyển 1,1 và 0,9; thủy tĩnh 1,0; thủy động 1,2 và 0,75. n_d = 1,2 có ô nhưng chưa phép tính nào dùng |
| **D10** | Hao mòn cừ luân chuyển: ô k_hm nhân vào W_x khi kiểm tra ứng suất cừ và (7-17); mặc định 1,0 | TCVN 11815 không quy định (7.3.2.9 chỉ có η_w do khóa cừ). Anh nhập theo bề dày đo thực tế [NGƯỜI DÙNG KHAI] |
| **D11** | Bê tông bịt đáy: ô R_bt (mặc định 0,75 MPa, B15) và hệ số bê tông đổ dưới nước (mặc định 0,85) | TCVN 5574:2018 Bảng 7 (R_bt B15) [ĐÃ XÁC MINH theo v1.2]. Hệ số 0,85: TCVN 5574 không quy định, giữ [GIẢ THIẾT] đã duyệt v1.1; mục chờ xác nhận số 1 của v1.2 coi như giữ nguyên |
| **D12** | Đẩy trồi đáy hố (TCVN 10400:2015 Phụ lục I): ô α của (I3), mặc định 0,5, khoảng 0,5 đến 1,0. **d trong (I8) lấy bằng D** | (I8) bản in có d trong tử số nhưng không định nghĩa; D là độ sâu tường cừ cắm vào nền. Suy luận: γ₂ tính từ mặt đào đến đáy tường nên γ₂·d cùng đoạn đó. Chưa tìm thấy tài liệu gốc của (I8). [NGƯỜI DÙNG KHAI] |
| **D13** | Loại đất quy về tên theo tiêu chuẩn. **Thấm hay không theo định nghĩa TCVN 11815 7.3.2.6**: chỉ á sét và sét là đất không thấm; cát, á cát là đất thấm. T11 lớp 4 "Cát sét" đổi thành "Á sét" (không thấm) | 7.3.2.6, (7-5) nhóm m1 xếp á cát cùng cát thô [ĐÃ XÁC MINH] |
| **D14** | T11 đẩy trồi đáy (I4): K = 0,70 < 1,5, chấp nhận xếp "đạt nhờ bịt đáy là biện pháp gia cường" | TCVN 10400:2015 mục 5.5.2.3.4 theo ghi chú chương trình. Giữ cách xếp, kèm dòng ghi chú trong hồ sơ |

---

## PHẦN C. PHẠM VI CHƯA THỰC HIỆN (in vào mọi sản phẩm hồ sơ)

| # | Hạng mục | Lý do | Điều khoản liên quan |
|---|---|---|---|
| C1 | Ổn định thấm chung K_s = i_c / i (M2.5) | Chưa có ô i_c, ΣL_n, ΣL_v, số hàng cừ; ngưỡng K_s "Chưa có căn cứ" | TCVN 10400:2015 (13), (14) theo v1.2, chưa mở lại phần thân |
| C2 | Đẩy nổi lớp sét trên tầng nước áp (M2.6) | Chưa có số liệu tầng chứa nước, cột áp | TCVN 10400 (15), K ≥ 1,05 theo v1.2 |
| C3 | δ ma sát đất - tường | Chỉ dùng δ = 0. Được phép δ = φ/3 hoặc φ/2 khi không có nước mặt, h'_B ≤ 2 m và ≤ 1/3 chiều sâu hố (T11 không đủ điều kiện) | TCVN 11815 Phụ lục D mục 5 |
| C4 | Hệ số điều kiện làm việc do dòng thấm khi hút nước hố đất cát | TCVN không cho trị số, mặc định 1,0 [GIẢ THIẾT] | 7.3.2.4 |
| C5 | Áp lực đất tĩnh và nêm kích nén trước khi gần công trình hiện hữu | TCVN 11815 không cho công thức hệ số áp lực tĩnh | 7.3.6.2 a, b |
| C6 | Thủy động, va thuyền bè, sóng, xói lở (N2, W4) | Điều 5.7 chỉ cho hợp lực lên phao, sà lan, thùng chụp, giếng chìm, không áp thẳng cho vòng vây cừ | 5.7, 7.3.6.2, 4.1.5 |
| C7 | Đẩy nổi toàn khối vòng vây khép kín | Ô MN_max có nhưng chưa phép tính nào dùng; TCVN chỉ có một câu, không công thức | 7.3.6.2 |
| C8 | Đắp đất lại và tháo tầng trên cùng (T1); chống tăng cường xuống bệ | Chưa mô hình hóa; khung v1.2 D5 chỉ cho phép ghi "chưa tính" với chống tăng cường | Trục 4 mục 4 |
| C9 | Đất phía trong hố khác phía ngoài (CDM, cát đắp, rọ đá) | TCVN không có quy đổi CDM | N4 |
| C10 | S4 hai hàng cừ, hố thế; dầm trên nền đàn hồi (TCVN 10304 Phụ lục A; nay là tùy chọn ở khung v1.4 dự thảo); độ võng cho phép vành đai | Ngoài khung hoặc chưa có căn cứ | khung v1.2 Trục 3 |
| C11 | Lớp đất vắt qua mực nước ngầm, coi thấm hay không | Chưa có căn cứ | CT-B5 |
| C12 | Cao độ xói cục bộ | Ô trống thì lấy mặt đất tự nhiên [GIẢ THIẾT] | 4.1.5, 7.3.1 |
| C13 | f_u SS400 = 400 MPa chưa nối vào ô f_u của mối hàn | Ô vẫn trống, chưa kiểm (182b) | TCVN 5575:2024 Bảng M.1 |
| C14 | Tải đứng lên cừ (búa, cẩu) | Chưa thấy ô riêng, có thể nằm trong phụ tải loại cẩu; chưa kiểm sâu | 7.3.6.1 |

---

## PHẦN D. CÁC ĐIỂM ĐÃ CHỐT NGÀY 09/11/2026 (sau khi gửi dự thảo)

1. Giai đoạn có bịt đáy chưa hút cạn: **giữ gối 0,5 m** dưới mặt bịt đáy (ghi trong D7 a).
2. t của gối t/2: **chiều sâu đóng cọc tối thiểu theo 7.3.5.3**, tính trước rồi mới đặt gối (D7 b). Thay cho cách lấy t = chiều sâu ngập thật của lần chốt đầu.
3. f_y SS400: **tra riêng cho cánh và bụng** (D8).
4. Hệ số 0,85 của bê tông bịt đáy: **giữ làm giả thiết chung** (D11).
5. Tab Đầu vào: **bỏ hiển thị cột Nguồn số liệu** (nhãn nguồn) cho gọn; dữ liệu `input_sources` vẫn giữ trong cấu hình, Phụ lục 2 của thuyết minh vẫn đọc từ đây [chưa xem lại cách Phụ lục 2 hiển thị khi không còn nhãn].

## PHẦN E. KIỂM CHỨNG ĐÃ CÓ

- T11 chạy 7 giai đoạn; 18 lệnh ca nền T11 cũ giống bản trước ở mọi giá trị số sau 3D-32; mô hình hình học M1 giống.
- Kiểm tra độc lập bằng Python cho **bản chương trình hiện tại** chưa làm (kế hoạch P1). Các lần dựng lại Python trước đây chỉ cho từng mục (A3, B13, HK 3D-6b, N1) trên bản chương trình lúc đó.
