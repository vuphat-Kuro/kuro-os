---
type: wiki
status: active
tags: [wiki, qlda, kcpt, vong-vay-coc-van]
created: 2026-11-06
updated: 2026-11-06
version: v1.2
thay_the: 20261106_CHUNG_PPT_KhungPhuongPhapTinh_VongVayCocVan_v1.1.md (duyet 06/11/2026, sao luu _backup/20261106/, SHA256 7969cf79833120080e1af99f2ee4569f754b38117c18b88dcdfe7a3b9904cc5b)
can_cu_ra_soat: 99-Temp/20261106_NHAP_RaSoat_KhungPPT_VongVay.md; 99-Temp/20261106_NHAP_PhanTich_SBIM2_KeHoach_TichHop_Midas_VongVay_v2.md (D1 den D5)
approved: 2026-11-06
approved_by: Kiều Linh Nghĩa - Phó phòng KT-TC
---

> **Trạng thái:** ĐÃ DUYỆT - v1.2 = v1.1 (duyệt 06/11/2026) cộng 5 sửa đổi D1 đến D5 được anh Kiều Linh Nghĩa duyệt ngày 06/11/2026 ("Duyệt theo đề xuất", kế hoạch v2 Phần 4). Các mục sửa đổi ghi mã `[D1]` đến `[D5]`. Mọi thay đổi về sau phải lập đề xuất xin ý kiến anh Nghĩa.
> - Nội dung v1.1 gốc:
> - Duyệt toàn văn v1.1, kể cả các giá trị mặc định nêu ở Phần VI (giữ 0,85 làm giả thiết cho bê tông bịt đáy; γ_M = 1,00; dạng hiện I15; β lấy cận trên, α = 0,5, d = D). Các mục này vẫn mang nhãn [GIẢ THIẾT] trong hồ sơ tính.
> - Lập theo kết quả rà soát ngày 06/11/2026 và chỉ đạo của anh cùng ngày: Phần A, B duyệt theo đề xuất; C1, C2, C3, C4 theo đề xuất; C5 số hóa thành bảng điểm.
> - Bản v1 (duyệt 26/10/2026) giữ nguyên văn tại vị trí cũ và có bản sao lưu.
> - Mỗi mục thay đổi ghi mã `[A..]`, `[B..]`, `[C..]` để tra ngược văn bản rà soát.
> - Module 7 (đà giáo, ván khuôn) đã tách sang file riêng `20261106_NHAP_PPT_KhungPhuongPhapTinh_DaGiaoVanKhuon_v1.0.md` [C3].

# KHUNG PHƯƠNG PHÁP TÍNH VÒNG VÂY CỌC VÁN THÉP HỐ MÓNG MỐ, TRỤ CẦU - v1.2

## KẾT LUẬN 10 GIÂY

Khung giữ 4 trục phân loại và 6 module tính. Thứ tự tính: Module 2 và Module 6 tính trước, độc lập với giai đoạn thi công; các module còn lại tính theo từng giai đoạn.

Mọi hệ số trong khung được tra theo điều kiện, không còn khoảng giá trị tự chọn.

Sơ đồ tính mômen cừ theo đúng TCVN 11815:2017: gối dưới tại t/2, hoặc 0,5 m dưới mặt bê tông bịt đáy. Phương pháp Blum và FEM 1D chỉ dùng để đối chứng.

### Cơ sở tiêu chuẩn và thứ bậc áp dụng

| Bậc | Tiêu chuẩn | Dùng cho | Nhãn |
|---|---|---|---|
| 1 | TCVN 11815:2017 *Thiết kế công trình phụ trợ trong thi công cầu*, mục 4.3, 5, 7.3, Phụ lục D | Toàn bộ vòng vây: tải trọng, chiều sâu ngàm, ổn định, độ bền cừ, khung chống | [ĐÃ XÁC MINH] |
| 2 | TCVN 10400:2015 *Công trình thủy lợi - Đập trụ đỡ*, mục 5.5.2.3 và Phụ lục I (tham khảo) | Chiều dày bê tông bịt đáy, ổn định thấm, đẩy nổi tầng nước áp, đẩy trồi đáy sét | [ĐÃ XÁC MINH] |
| 3 | TCVN 5575:2024 *Thiết kế kết cấu thép* | Cường độ tính toán thép, ổn định nén uốn thanh chống, vành đai | [ĐÃ XÁC MINH] Bảng 2, Bảng 3 |
| 4 | TCVN 5574:2018 *Thiết kế kết cấu bê tông và bê tông cốt thép* | Cường độ bê tông bịt đáy | [ĐÃ XÁC MINH] Bảng 7 |
| Đối chiếu | 22TCN 200-89 (văn bản gốc của TCVN 11815) | Kiểm tra chéo các biểu đồ hệ số m | [ĐÃ XÁC MINH] Hình 16, 17, 19 |

Khi TCVN 11815 có quy định thì dùng TCVN 11815. TCVN 10400 chỉ dùng cho nội dung mà TCVN 11815 không có công thức.

---

## PHẦN I: MA TRẬN PHÂN LOẠI ĐẦU VÀO (4 TRỤC)

### Trục 1: Thủy văn
- **W1, trên cạn khô:** không có nước ngầm trong phạm vi cừ.
- **W2, trên cạn có nước ngầm:** áp lực đất chia 2 đoạn: trên mực nước ngầm dùng `γ`, dưới mực nước ngầm dùng `γ_đn`. Cộng áp lực thủy tĩnh `p_w = γ_n × z_w`. Hệ số m tra Hình 7.15 (chỉ khi qua cổng 3.3).
- **W3, ngập nước:** áp lực thủy tĩnh ngoài, thủy động nếu có. Hệ số m tra Hình 7.14 (1 tầng chống) hoặc Hình 7.17 (từ 2 tầng). Kiểm toán đẩy nổi vòng vây khép kín tại MNTC cao nhất (TCVN 11815, Điều 7.3.6.2) [B8].
- **W4, ngập sâu, dòng chảy xiết:** như W3, thêm va trôi, sóng gió, va tàu (7.3.6.2) và xói lở (Điều 4.1.5) [B8].

### Trục 2: Địa chất
- **G1:** cát thô, cát sỏi, á cát. `m1 = 0,7` (7.3.2.2).
- **G2:** cát trung, cát nhỏ. `m1 = 0,5`.
- **G3:** cát bột. `m1 = 0,4`.
- **G4, đất dính (sét, á sét, bùn):**
  - Áp lực theo Phụ lục D mục 12 (chủ động giảm `2C × √λa`) và 2 sơ đồ thấm của Điều 7.3.2.6 [B5].
  - Kiểm toán đất chồi theo (7-18) [A1].
  - Kiểm toán đẩy trồi đáy theo TCVN 10400 Phụ lục I.
  - Hệ số m chống lật = 0,95 [A5].
- **G5, đất nhiều lớp:** gộp lớp khi các chỉ tiêu `γ`, `φ`, `C` chênh nhau không quá 20%, theo (D.1). Nếu không đạt điều kiện thì tính từng lớp [B10].

### Trục 3: Sơ đồ kết cấu
- **S1, không có thanh chống ngang:** Điều 7.3.3.
  - Bỏ giới hạn "h ≤ 4 - 5 m" của v1 vì TCVN không quy định [A9].
- **S2, một tầng chống:** Điều 7.3.4.
- **S3, từ hai tầng chống trở lên:** Điều 7.3.5.
- **S4, cừ kết hợp neo ngoài hoặc cọc dẫn hướng:** ngoài phạm vi khung này.
  - TCVN 11815 mục 7.3 không có phương pháp tính.
  - Gặp trường hợp này thì báo "Chưa có căn cứ" và chuyển sang tính riêng.

### Trục 4: Biện pháp thi công và giai đoạn kiểm toán
- **C1:** đào khô, đào đến đâu lắp khung đến đó.
- **C2:** đào hở, có hạ mực nước ngầm.
- **C3:** đào ngập nước, đổ bê tông bịt đáy, rồi hút cạn.

Theo Điều 7.3.2.1 và 4.3.4, phải kiểm toán ở **mọi giai đoạn** [B11]:
1. Từng bước đào và lắp từng tầng khung chống.
2. Hút nước (từng nấc hoặc toàn bộ). Riêng trước khi đổ bịt đáy: cột nước hút lấy ≥ 1,5 m và ≥ 1/4 độ chênh giữa mực nước và đáy hố (7.3.2.5) [B4].
3. Sau khi đổ bê tông bịt đáy và hút cạn. Đây là giai đoạn chịu lực lớn nhất (TCVN 10400, 5.5.2.3.3).
4. Đắp đất lại và tháo từng tầng giằng chống [B11].

Hai nhánh trình tự lắp khung dưới mực nước (rút nước đến đâu lắp đến đó, hoặc hạ khung trước rồi mới đào) giữ nguyên theo wiki [[Khung phương pháp tính kiểm toán hố móng]] (duyệt 31/10/2026).

---

## PHẦN II: BƯỚC 0 - KIỂM TRA CẤU TẠO ĐẦU VÀO [B9]

| Kiểm tra | Điều kiện | Căn cứ |
|---|---|---|
| Kích thước mặt bằng | Vòng vây rộng hơn móng ≥ 0,30 m (phần đổ bê tông trong nước) | TCVN 11815, 7.3.1 mục 1 |
| Khoảng cách mép bệ đến chân vòng vây | 0,75 m đến 1,0 m | TCVN 10400, 5.5.2.3.2 |
| Cao độ đỉnh cừ | ≥ MNN + 0,3 m và ≥ MNTC + 0,7 m | TCVN 11815, 7.3.1 mục 2 |
| Cọc xiên của móng | Mũi cừ cách cọc móng ≥ 1 m (không bịt đáy), ≥ 0,5 m (có bịt đáy) | TCVN 11815, 7.3.1 mục 1 |
| Cao độ đất bên ngoài dùng trong tính | Lấy sau khi đã trừ chiều sâu xói dự kiến | TCVN 11815, 7.3.1 mục 2; 4.1.5 |

Không đạt điều kiện nào thì chương trình cảnh báo, nhưng vẫn cho tính tiếp.

---

## PHẦN III: CHI TIẾT 6 MODULE TÍNH TOÁN

### MODULE 1: TẢI TRỌNG VÀ TÁC ĐỘNG

**1.1. Áp lực đất (Phụ lục D)** [B10]
- Áp lực tiêu chuẩn theo Coulomb, có kể lực dính của sét và á sét (D mục 1).
- Khi `δ = 0`: `λa = tan²(45° - φ/2)`, `λn = tan²(45° + φ/2)` (D.18).
- Ma sát tường được phép dùng `δ = φ/3` (khi h'_B > 0) hoặc `δ = φ/2` (khi h'_B = 0), chỉ khi vùng không có nước mặt **và** h'_B ≤ 2 m **và** h'_B ≤ 1/3 chiều sâu hố. Ngoài trường hợp đó lấy `δ = 0` (D mục 5). Mặc định của chương trình: `δ = 0`.
- Đất dính: tung độ áp lực chủ động giảm `p_c = 2C × √λa` (D.15). Đoạn có `p_c` lớn hơn tung độ áp lực rời thì lấy áp lực bằng 0 (D mục 12).
- Đất dưới nước: áp lực bằng tổng áp lực thủy tĩnh và áp lực đất lơ lửng. Dung trọng đẩy nổi theo (D.2), được phép lấy 1 T/m³ (D mục 4).
- Gần công trình hiện hữu không cho phép lún: dùng áp lực đất ở trạng thái tĩnh. Thanh chống phải có nêm hoặc kích nén trước bằng lực tính toán (7.3.6.2) [B8].

**1.2. Áp lực nước**
- Áp lực thủy tĩnh: `p_w = γ_n × z_w`.
- Đất không thấm (sét, á sét) dưới mực nước: tính theo **2 sơ đồ** của Điều 7.3.2.6, lấy kết quả bất lợi [B5]:
  - Sơ đồ 1: dưới mặt lớp không thấm, chỉ có áp lực thủy tĩnh của nước thấm vào khe giữa tường và đất, trên chiều cao `h_B`.
  - Sơ đồ 2: không xét nước thấm vào khe; lớp đất gây áp lực ngang khi phía trên nó chịu áp lực thủy tĩnh và trọng lượng các lớp thấm bên trên (có kể đẩy nổi).
  - **[D1] Dung trọng trong Sơ đồ 2:** lớp không thấm nằm dưới mực nước dùng **γ_đn** cho cả phía ngoài (chủ động) và phía trong (bị động), cột nước phía trên lớp tính như phụ tải (theo bảng tính đã duyệt T11-T12 Ninh Cơ). Phương án γ tự nhiên được tính song song làm đối chứng thiên an toàn, không dùng để kết luận. [GIẢ THIẾT đã duyệt]
  - **[D1] γ_đn theo (D.2):** khi có γ_s và hệ số rỗng e thì `γ_đn = (γ_s - γ_n) / (1 + e)`; không có thì dùng γ_đn nhập trực tiếp.
- Chiều cao thấm `h_B`, tính từ mặt lớp không thấm:

| Sơ đồ kết cấu | `h_B` | Căn cứ |
|---|---|---|
| S1 không chống | 0,7 × h', với h' là chiều sâu cừ trong lớp không thấm | (7-7) |
| S1, khi tính t0 | 0,8 × (h_m + t0) | 7.3.3.1 |
| S2 một tầng chống | h' - t/2 | (7-8) |
| S3 nhiều tầng chống | Đến cao độ 0,5 m dưới đáy hố, khi tầng chống dưới cùng nằm trong lớp không thấm | 7.3.2.6 mục c |

**1.3. Phụ tải trên lăng thể phá hoại (Phụ lục D mục 6)** [A2]

| Nguồn tải | Dạng tải | Cường độ tiêu chuẩn |
|---|---|---|
| Vật liệu, đống đất | Phân bố đều theo kích thước thiết kế của đống | Không nhỏ hơn 1 T/m² |
| Thiết bị thi công, cẩu, giá búa, phương tiện chạy trên ray | Theo lý lịch máy, đặt ở vị trí bất lợi | Theo lý lịch máy |
| Ô tô tải, xe < 25 T, băng rộng 3 m mỗi làn (Hình D.1) | Băng | b > 3 m: p = 1; b = 2 đến 3 m: p = 2; b = 1 đến 2 m: p = 3; b < 1 m: p = 4 T/m². Xe đến 30 T nhân 1,2; xe 45 T nhân 1,9; xe 60 T nhân 2,5 |
| Cẩu xích, cẩu lốp làm việc sát hố, băng rộng 1,5 m (Hình D.2) | Băng | Trọng lượng làm việc ≤ 10 / 30 / 50 / 70 T thì p = 3 / 6 / 9 / 12 T/m², nội suy |
| Đường sắt song song thành vây | Băng rộng 3,5 m | 28 T/m dài |

Tải băng quy đổi thành áp lực ngang theo (D.3) đến (D.5). Mặt đất phẳng có tải phân bố đều q thì dùng (D.7).

**1.4. Hệ số vượt tải (Điều 7.3.2.4, Bảng 5.12)** [B1]
- Áp lực đất chủ động: `η_a = 1,2`.
- Áp lực đất bị động: `η_n = 0,8`.
- Áp lực thủy tĩnh: `n = 1,0`.
- Phụ tải thiết bị: lấy theo Bảng 5.12.
- Áp lực tính toán = áp lực tiêu chuẩn theo Phụ lục D × hệ số vượt tải.
- Khi hút nước khỏi hố móng đất cát, TCVN cho phép đưa thêm hệ số điều kiện làm việc để kể ảnh hưởng của dòng thấm (7.3.2.4), chọn theo điều kiện địa chất thủy văn. Mặc định của chương trình: 1,0. [GIẢ THIẾT]

**1.5. Tải đứng lên khung chống (Điều 7.3.2.7, công thức 7-9)**
- Mômen lớn nhất trong thanh chống do thiết bị và kết cấu ấn định không nhỏ hơn mômen do tải phân bố đều `q = q1 × F / l`.
- `q1 = 50 kg/m²` cho tầng trên cùng, `25 kg/m²` cho các tầng còn lại.
- `F` là diện tích hố móng thanh chống đảm nhận; `l` là chiều dài thanh.

---

### MODULE 2: ỔN ĐỊNH ĐÁY HỐ MÓNG (tính trước, độc lập giai đoạn)

| # | Kiểm toán | Áp dụng khi | Công thức và tiêu chí | Căn cứ |
|---|---|---|---|---|
| 2.1 | Đất chồi khi hút nước (đất rời) | G1 đến G3, không có lớp bịt đáy ngăn nước | `t ≥ (h'_B / (π × m1)) × (γ_B / γ_w)`, với γ_B = γ_w = 1 T/m³, π = 3,14. Được giảm 10% khi khoảng cách từ mực nước ngoài đến chân cừ > 2 lần khoảng cách từ chân cừ đến đỉnh lớp không thấm [B3] | TCVN 11815 (7-5), 7.3.2.2 |
| 2.2 | Đất chồi dưới chân cừ, nền yếu | G4 đất yếu | `t ≥ h = 1,5q / [γ × (2tan⁴(45° + φ/2) - 1)]`. `q` là áp lực tính toán lên cừ tại cao độ đáy hố; `γ`, `φ` của đất đáy hố [A1] | TCVN 11815 (7-18), 7.3.6.2 |
| 2.3 | Đẩy trồi đáy, sét thuần φ = 0 | G4, có C_u | `K = [5,7 × C_u × B_1 + C_u × H + (1 + α) × C_u × D] / [(γ_bh - γ_n) × H × B_1 + γ_n × H_1 × B_1] ≥ 1,5`. α = 0,5 đến 1,0 (mặc định 0,5). Nhiều lớp dùng (I5) | TCVN 10400 (I4), (I5) |
| 2.4 | Đẩy trồi đáy, sét có φ và c | G4, có φ > 0 và c | `K = (γ_2 × d × N_q + c × N_c) / [γ_1 × (H + D)] ≥ 1,2`, với `N_q = tan²(45° + φ/2) × e^(π × tanφ)`, `N_c = (N_q - 1) / tanφ` | TCVN 10400 (I8), (I9) |
| 2.5 | Ổn định thấm chung | Có chênh cột nước, nền thấm | `K_s = i_c / i`, `i = h_w / L`, `L = ΣL_n + m × ΣL_v`; m = 1,50 (1 hàng cừ), 2,00 (2 hàng cừ). `i_c` theo mật độ hạt và hệ số rỗng: nhập từ hồ sơ địa chất | TCVN 10400 (13), (14) |
| 2.6 | Đẩy nổi lớp sét trên tầng nước có áp | Sét không thấm phủ trên tầng chứa nước áp | `K = P_cz / P_wy ≥ 1,05` | TCVN 10400 (15) |

Ghi chú:
- Ký hiệu `d` trong (I8) không được định nghĩa trong bản in. Theo sơ đồ, chương trình lấy `d = D`. [GIẢ THIẾT]
- Ngưỡng `K_s` yêu cầu cho mục 2.5 chưa có trong phần đã đọc: "Chưa có căn cứ", nhập theo hồ sơ thiết kế.
- Không đạt mục nào thì phải có biện pháp gia cường. Biện pháp thường dùng là bê tông bịt đáy, chuyển sang Module 6 (TCVN 10400, 5.5.2.3.4).

---

### MODULE 3: CHIỀU SÂU NGÀM t VÀ ỔN ĐỊNH CHỐNG LẬT (theo giai đoạn)

**3.1. Chiều sâu ngàm tối thiểu cấu tạo** [B2]
- t ≥ 2 m (tính từ đáy hố hoặc từ cao độ xói) với: sét chảy, sét dẻo chảy, á sét, á cát, bùn no nước, cát nhỏ, cát bột (TCVN 11815, 7.3.2.1).
- t ≥ 1 m với các loại đất còn lại.
- Vòng vây có lớp lót ngăn nước: t ≥ 1 m với mọi loại đất.
- Chân cừ thấp hơn đường xói cục bộ **tối thiểu 2 m** (TCVN 10400, 5.5.2.3.2; TCVN 11815, 4.1.5).
- Bỏ yêu cầu "ngàm vào đất tốt tối thiểu 1,0 m" của v1 vì không có căn cứ [A9].

**3.2. Điều kiện ổn định chống lật:** `M1 ≤ m × Mg` (7-6), lấy theo từng sơ đồ.

**[D2] Cách hạch toán áp lực nước:** áp lực thủy tĩnh **phía ngoài** đưa vào vế gây lật M1; áp lực thủy tĩnh **phía trong hố** đưa vào vế giữ Mg (cùng áp lực bị động, có nhân hệ số m), không gộp chênh áp. Với (7-16), (7-17): M_B là mômen nước phía ngoài dưới trục quay; mômen nước phía trong dưới trục quay cộng vào M_n. [GIẢ THIẾT đã duyệt, theo bảng tính T11-T12]

> **Thay thế ngày 07/11/2026 (Q1, anh Nghĩa duyệt "Đổi theo Hình 7.13"):** áp lực thủy tĩnh lấy **hiệu** nước ngoài - nước trong theo TCVN 11815:2017 Hình 7.13 (trang 56), 7.3.4.1 và 7.3.2.5 [ĐÃ XÁC MINH]. Hiệu mômen nước dương cộng vào M1; âm cộng vào Mg (nhân m). Với (7-16): phần dưới trục là M_B (hiệu dương vào vế lật), phần trên trục là M'B (hiệu dương vào vế giữ). D2 không còn áp dụng. Chi tiết: `99-Temp/qlda/mau_tinh/dot5/README.md` mục 7.

| Sơ đồ | Trục quay | M1 (gây lật) | Mg (giữ) | m | Căn cứ |
|---|---|---|---|---|---|
| S1 không bịt đáy | Điểm 0 ở độ sâu t0 | Áp lực chủ động và thủy tĩnh phía trên t0 | Áp lực bị động phía trên t0 | 0,95 | 7.3.3.1 |
| S1 có bịt đáy, sau khi đổ | 0,5 m dưới mặt bịt đáy | Chủ động (đất đẩy nổi) và thủy tĩnh phía trên trục | Bị động (phản lực ngược) phía dưới trục; biểu đồ tam giác có tung độ 0 tại trục, với H = h_m + t | 0,95 | 7.3.3.4 |
| S2 một tầng chống | Tầng chống | Chủ động và thủy tĩnh | Bị động (phản lực trực tiếp) | theo 3.3 | 7.3.4.1 |
| S3 nhiều tầng chống | Tầng chống thấp nhất của giai đoạn | (7-16) khi `2M'a + M'B < Wx × R`; ngược lại dùng (7-17) | | theo 3.3 | 7.3.5.1 |

- S1: `t = t0 + Δt` (7-10), với `Δt = E'n / (2 × P'n)` (7-11), `E'n = En - (Ea + EB)` (7-12). Giải t0 bằng phương pháp thử dần [B6].
- S3, dạng (7-17): `Ma + MB = m × (Mn + Wx × R)` [B7].
- Giảm t cho vòng vây khép kín (7.3.4.1, 7.3.5.2) [B7]: 15% với vòng tròn bán kính < 5 m; 10% với chữ nhật có cạnh lớn nhất < 5 m. Mức giảm không được làm t nhỏ hơn giá trị của mục 3.1 và Module 2. [GIẢ THIẾT: thứ tự áp dụng]
- Có tải đứng lên cừ (búa, cẩu): kiểm tra phần cừ truyền tải đứng theo tiêu chuẩn cọc; mặt đất lấy tại đáy hố; tải phân bố dưới góc 30° (7.3.6.1) [B8].

**3.3. Cổng chọn hệ số m (Điều 7.3.4.2, 7.3.5.2)** [A5]

Chương trình xét theo thứ tự, gặp điều kiện nào đúng trước thì dùng điều kiện đó:
1. Sơ đồ S1 (không chống), có hoặc không có bịt đáy: m = 0,95.
2. Đất dính, hoặc mũi cừ ngập vào lớp sét, á sét: m = 0,95.
3. Đất không dính, chỉ hút một phần nước (đến 0,25h nơi ngập nước, hoặc 0,25h_B trên cạn): m = 0,95.
4. Đất không dính, hút toàn bộ nước:
   - Trên cạn (W2): tra Hình 7.15.
   - Ngập nước, 1 tầng chống: tra Hình 7.14.
   - Ngập nước, từ 2 tầng chống: tra Hình 7.17.

**3.4. Bảng số hóa hệ số m** [C5] [ĐÃ XÁC MINH]

Phương pháp số hóa:
- Đọc tọa độ đường lưới và đường biểu đồ từ dữ liệu vector của PDF TCVN 11815:2017, trang 56, 57, 59, bằng script `99-Temp/so-hoa-he-so-m/so_hoa_hinh_7_14_7_15_7_17.py`. Kết quả lưu tại `bang_he_so_m.json` trong cùng thư mục.
- Chỉ đọc tại các đường lưới có nhãn in.
- Kiểm tra chéo với ảnh biểu đồ gốc 22TCN 200-89 (Hình 16, 17, 19): khớp tại các nút 20°, 30°, 45°.

Ký hiệu: `M_m = h_m / h`, `M_B = h'_B / h`. Giữa các nút thì nội suy tuyến tính theo φ và theo M_m (hoặc M_B), đúng như TCVN cho phép.

Hình 7.14, ngập nước, 1 tầng chống:

| φ | 15° | 20° | 25° | 35° | 45° |
|---|---|---|---|---|---|
| m khi M_m = 0 | 0,974 | 0,910 | 0,840 | 0,770 | 0,701 |
| m khi M_m = 1 | 1,136 | 1,106 | 1,072 | 1,038 | 1,004 |

Hình 7.17, ngập nước, từ 2 tầng chống:

| φ | 15° | 20° | 25° | 30° | 35° |
|---|---|---|---|---|---|
| m khi M_m = 0 | 0,873 | 0,819 | 0,760 | 0,701 | 0,647 |
| m khi M_m = 1 | 1,200 | 1,139 | 1,070 | 1,002 | 0,929 |

Hình 7.15, trên cạn, có nước ngầm:

| M_B | 0 | 0,2 | 0,4 | 0,6 | 0,8 | 1,0 |
|---|---|---|---|---|---|---|
| m | 0,950 | 0,995 | 1,039 | 1,060 | 1,082 | 1,100 |

Lưu ý khi dùng bảng:
- Trục φ của Hình 7.14 in nhãn 15°, 20°, 25°, 35°, 45° trên các đường lưới cách đều nhau. Bản gốc 22TCN 200-89 cũng in như vậy. Vì thế bảng chỉ dùng các nút có nhãn và nội suy tuyến tính giữa hai nút liền kề, không suy diễn thêm nhãn.
- φ ngoài miền bảng (Hình 7.14: 15° đến 45°; Hình 7.17: 15° đến 35°): chương trình lấy giá trị tại nút biên gần nhất và cảnh báo. [GIẢ THIẾT]
- Thay cho các hàm tuyến tính của v1. Hàm 7.15 của v1 khớp bảng; hàm 7.14 và 7.17 của v1 lệch đến 0,06 [A6].

---

### MODULE 4: ĐỘ BỀN THÂN CỌC VÁN (theo giai đoạn)

**4.1. Sơ đồ tính mômen** [A4] [C1]

| Sơ đồ | Mô hình | Gối dưới | Tải bỏ qua | Mômen thiết kế | Căn cứ |
|---|---|---|---|---|---|
| S1 không chống | Công xôn ngàm tại t0 | Ngàm ở độ sâu t0 | Áp lực dưới t0 | Mômen tại ngàm. Có bịt đáy thì lấy bằng M1 của 7.3.3.4 | 7.3.3.2; 7.3.3.4 |
| S2 một tầng chống, trước bịt đáy | Dầm đơn giản 2 gối | Độ sâu t/2 dưới đáy hố | Mọi áp lực dưới t/2 | `M = M_B + 0,75 × M_m` (7-14). M_B do nước, M_m do đất | 7.3.4.3 |
| S3 nhiều tầng chống, trước bịt đáy | Dầm liên tục nhiều nhịp, gối tại các tầng chống | Độ sâu t/2 dưới đáy hố | Mọi áp lực dưới t/2 | Mômen của dầm liên tục | 7.3.5.3 |
| S2, S3 sau bịt đáy và hút cạn | Dầm đơn giản (S2) hoặc liên tục (S3) | 0,5 m dưới mặt trên bê tông bịt đáy | | Mômen của dầm | 7.3.4.3; 7.3.5.4; TCVN 10400 5.5.2.3.4 c |

- Blum `u_0` và BeamSolver FEM 1D giữ trong chương trình **chỉ để đối chứng**, hiển thị song song với kết quả theo TCVN. Kết luận đạt hay không đạt lấy theo sơ đồ TCVN [C1].
- Nếu độ bền không đạt: đổi vị trí tầng chống, hạ thấp tầng chống dưới cùng, tăng chiều sâu ngàm, đổi loại cừ hoặc thêm tầng chống (7.3.4.3, 7.3.5.2).

**4.2. Kiểm toán ứng suất** [A3] [A7] [C2]

`σ = M_max / (η_w × W_x) ≤ m × f_yd / k`

| Hệ số | Giá trị | Căn cứ |
|---|---|---|
| `η_w` (giảm mômen kháng uốn do trượt khóa cừ) | 0,7: đất yếu, không có vành đai tăng cường. 0,8: đất yếu, có vành đai. 1,0: các trường hợp còn lại | TCVN 11815, 7.3.2.9 |
| `m` (điều kiện làm việc, độ bền) | 1,15: vòng vây tròn. 1,10: cừ dài < 5 m, khép kín chữ nhật, có tầng chống trung gian. 1,0: các trường hợp còn lại | 7.3.2.10; 4.3.5 |
| `k` (độ tin cậy) | 1,1: vòng vây nằm trong nước. 1,0: các trường hợp còn lại | 7.3.2.8 |
| `f_yd` (cường độ tính toán thép) | `f_yd = f_y / γ_M`. f_y theo tiêu chuẩn sản phẩm hoặc chứng chỉ (SY295: 295 MPa; SY390: 390 MPa) | TCVN 5575:2024, Bảng 2 |
| `γ_M` (độ tin cậy vật liệu) | **1,00**: tường cừ hố đào, trụ tạm, công trình cấp C1 có thời hạn sử dụng hạn chế (Bảng 3, dòng 4). Mặc định của chương trình: 1,00. Nếu công trình không thuộc cấp C1 thì dùng 1,10 cho thép theo tiêu chuẩn nước ngoài (dòng 3) | TCVN 5575:2024, Bảng 3 |

- Cừ luân chuyển nhiều lần bị rỉ mòn: giảm W_x theo chiều dày đo thực tế. TCVN không quy định hệ số; hệ số 0,85 đến 0,90 của v1 chuyển thành giá trị nhập tay. [GIẢ THIẾT]
- Kiểm tra cả lực cắt ở gối theo TCVN 5575:2024. Lực cắt là bổ sung kỹ thuật, TCVN 11815 không yêu cầu riêng. [GIẢ THIẾT]

---

### MODULE 5: VÀNH ĐAI VÀ THANH CHỐNG (theo giai đoạn)

**5.1. Tải lên vành đai:** phản lực gối `q` (T/m) của dầm cừ tại cao độ tầng chống, lấy từ sơ đồ Module 4.1 (7.3.4.3, 7.3.5.3).

**5.2. Lực nén thanh chống:** `P = 1,1 × q × (l1 + ln) / 2` (7-15, Điều 7.3.4.3; dùng cho nhiều tầng theo 7.3.5.3) [A9].
- `l1` và `ln` là khẩu độ vành đai bên trái và bên phải thanh chống đang xét.
- Đối chứng: phản lực gối của dầm liên tục vành đai, theo TCVN 10400 5.5.2.3.4 c.

**5.3. Vành đai:** dầm liên tục chịu nén uốn, gối là các thanh chống. Hai gối biên là điểm tựa trên 2 thanh chống vuông góc. Lực dọc là phản lực gối biên của vành đai vuông góc (TCVN 10400, Hình 2, Hình 3). Kiểm toán bền và ổn định theo TCVN 5575:2024.

**5.4. Thanh chống:**
- Cấu kiện chịu nén uốn đồng thời: lực nén P (mục 5.2) và mômen do tải đứng `M_u ≥ q × l² / 8`, với q theo (7-9) (Điều 7.3.2.7).
- Kiểm toán bền và ổn định tổng thể theo các điều về cấu kiện chịu nén uốn của TCVN 5575:2024. Điều khoản cụ thể sẽ ghi khi lập module code; khung này không tự đặt công thức `φ_u`. [CẦN KIỂM TRA HIỆU LỰC]
- Bỏ dẫn chiếu "Điều 7.5 TCVN 11815" vì Điều 7.5 là tường cọc chữ I kèm ván ngang, không phải thanh chống vòng vây [A9].

---

### MODULE 6: BÊ TÔNG BỊT ĐÁY (tính trước, độc lập giai đoạn) [C4]

**6.1. Chiều dày chống đẩy nổi (TCVN 10400, Phụ lục I, mục I.2)**

| Đại lượng | Công thức |
|---|---|
| Lực đẩy nổi | `P_đn = β × H × F × γ_n` (I10). H tính từ **đáy** lớp bịt đáy đến MNTC |
| Trọng lượng bê tông | `P_1 = F × h_b × γ_b` (I11). γ_b là trọng lượng riêng bê tông vữa dâng, **không trừ đẩy nổi** |
| Ma sát cọc móng | `P_2 = n × F_tx × f_1` (I12) |
| Ma sát cừ | `P_3 = C × h_b × f_2` (I13), C là chu vi khung vây theo tim cừ |
| Điều kiện | `P_1 + P_2 + P_3 ≥ K × P_đn`, **K = 1,05** (I.2.3) |
| Dạng hiện, với H = H_0 + h_b và F_tx = u × h_b | `h_b ≥ K × β × γ_n × H_0 × F / [F × γ_b - K × β × γ_n × F + n × u × f_1 + C × f_2]` |

- `β` theo Bảng I1: sét 0,50 đến 0,80; cát pha 0,80 đến 0,90; cát 1,00. Mặc định là cận trên của khoảng, thiên an toàn. [GIẢ THIẾT]
- `H_0`: từ MNTC đến mặt trên bịt đáy. `u`: chu vi một cọc móng. `n`: số cọc. Dạng hiện là biến đổi đại số của (I15). [GIẢ THIẾT: biến đổi của em, anh duyệt cùng v1.1]
- `f_1`, `f_2`: TCVN không cho trị số. Nhập theo hồ sơ thiết kế được duyệt. Nếu bôi chất chống dính để nhổ cừ thì `f_2 = 0`. [NGƯỜI DÙNG KHAI]
- Sửa lỗi của v1: không dùng đồng thời "γ_bt_nổi" và lực đẩy nổi toàn phần, vì làm vậy là trừ nước 2 lần [A8].
- K = 1,05 là giá trị của TCVN 10400 [C4]. Chương trình cho phép nhập K lớn hơn nếu tư vấn yêu cầu, và ghi rõ đó là yêu cầu bổ sung, không phải của tiêu chuẩn.
- Làm tròn h_b lên bội số 0,5 m theo thông lệ thi công trụ cầu. [GIẢ THIẾT]

**6.2. Độ bền chịu uốn của bản bịt đáy (TCVN 5574:2018)**
- **[D4] Sơ đồ tính:** tách dải bê tông rộng 1 m, xét 2 sơ đồ theo bảng tính đã duyệt T11-T12:
  - Giữa hàng cọc biên và cừ: dầm công xôn ngàm tại tim hàng cọc biên, đầu kia chịu lực ma sát cừ `F_ms = 1 m × h_b × f_2`: `M = (q_2 - q_1) × L_b² / 2 - F_ms × L_b`.
  - Giữa 2 hàng cọc khoan nhồi: dầm ngàm 2 đầu: `M = (q_2 - q_1) × L_g² / 12`.
  - Với `q_1 = γ_bt × h_b` (trọng lượng bê tông), `q_2 = γ_n × (H_0 + h_b)` (đẩy nổi toàn phần, không nhân β), `W = 1 m × h_b² / 6`; `L_b`, `L_g` nhập theo bố trí cọc [NGƯỜI DÙNG KHAI].
- Bản bê tông không cốt thép, chịu áp lực đẩy nổi từ dưới lên trừ trọng lượng bản thân.
- Điều kiện: `σ_kéo ≤ R_bt × γ_b1`.
  - B15: `R_bt = 0,75 MPa` (Bảng 7). [ĐÃ XÁC MINH]
  - Tải ngắn hạn: `γ_b1 = 1,0` (6.1.2.3 a). [ĐÃ XÁC MINH]
- Hệ số 0,85 "đổ bê tông dưới nước qua ống tremie" của v1 **chưa có căn cứ trong TCVN 5574:2018**. Hệ số γ_b3 = 0,85 của 6.1.2.3 c chỉ áp dụng cho cường độ nén R_b, khi đổ theo phương đứng mỗi lớp cao hơn 1,5 m. Chương trình giữ hệ số 0,85 làm giả thiết kỹ thuật, chờ anh xác nhận. [GIẢ THIẾT]

**6.3. Sơ đồ cừ sau khi bịt đáy:** gối dưới cùng tại 0,5 m dưới mặt trên lớp bịt đáy (7.3.5.4, 7.3.3.4; TCVN 10400 5.5.2.3.4 c). Sơ đồ này dùng trong Module 3 và 4 cho giai đoạn sau bịt đáy.

---

## PHẦN IV: LƯU ĐỒ ĐIỀU PHỐI

```
[NHAP DU LIEU] -> [BUOC 0: KIEM TRA CAU TAO]
        |
[MA TRAN 4 TRUC: W, G, S, C]
        |
[MODULE 1: TAI TRONG]  (Phu luc D, he so vuot tai 1,2 / 0,8 / 1,0)
        |
[MODULE 2: ON DINH DAY]  [MODULE 6: BE TONG BIT DAY]   <- tinh truoc, doc lap giai doan
        |
[VONG LAP GIAI DOAN THI CONG]  (dao, lap khung, hut nuoc, sau bit day, dap lai, thao giang)
        |-- [MODULE 3: t VA CHONG LAT]  (cong chon m -> bang so hoa)
        |-- [MODULE 4: DO BEN CU]  (so do TCVN: t/2 hoac 0,5 m; Blum/FEM doi chung)
        |-- [MODULE 5: VANH DAI, THANH CHONG]  (7-15, nen uon TCVN 5575)
        |
[TONG HOP GIAI DOAN BAT LOI NHAT] -> [THUYET MINH DOSSIER-READY]
```

## PHẦN V: NHẬT KÝ THAY ĐỔI SO VỚI v1

| Mã | Nội dung | Vị trí trong v1.1 |
|---|---|---|
| A1 | Sửa (7-18): h là chiều sâu đóng cừ cần thiết, dạng t ≥ h | M2.2 |
| A2 | Phụ tải thi công lấy theo bảng Phụ lục D | M1.3 |
| A3 | η_w, m, k tra theo điều kiện | M4.2 |
| A4 | Ghi đúng (7-14) và gối dưới t/2 | M4.1 |
| A5 | Thêm cổng chọn m | M3.3 |
| A6 | Thay hàm tuyến tính 7.14 và 7.17 bằng bảng số hóa | M3.4 |
| A7 | R thành f_yd = f_y / γ_M theo TCVN 5575:2024 | M4.2 |
| A8 | K = 1,05 theo TCVN 10400; bỏ γ_bt_nổi đi kèm đẩy nổi toàn phần | M6.1 |
| A9 | Sửa dẫn chiếu (7-15) và Điều 7.5; bỏ "h ≤ 4 - 5 m" và "ngàm đất tốt 1 m" | Trục 3, M3.1, M5 |
| B1 đến B12 | Bổ sung theo văn bản rà soát (B12 chuyển sang file đà giáo, ván khuôn) | Ghi tại từng mục |
| C1 | Sơ đồ TCVN là sơ đồ chính; Blum và FEM để đối chứng | M4.1 |
| C2 | f_yd theo TCVN 5575:2024, γ_M = 1,00 | M4.2 |
| C3 | Tách Module 7 sang file riêng | Đầu file |
| C4 | K = 1,05 đã đối chiếu PDF TCVN 10400 | M6.1 |
| C5 | Bảng số hóa hệ số m | M3.4 |

## PHẦN V-B: NHẬT KÝ THAY ĐỔI v1.2 SO VỚI v1.1

| Mã | Nội dung | Vị trí |
|---|---|---|
| D1 | Sơ đồ 2 dùng γ_đn cho lớp không thấm; γ_đn tính theo (D.2) từ γ_s, e khi có số liệu | M1.2 |
| D2 | Nước ngoài vào vế lật, nước trong hố vào vế giữ (nhân m). **Đã thay bằng Q1 ngày 07/11/2026: lấy hiệu áp lực thủy tĩnh theo Hình 7.13** | M3.2 |
| D3 | Bảng tính xuất ra dùng Unicode, Times New Roman (không dùng mã TCVN3 của mẫu) | Đầu ra Excel |
| D4 | Uốn bê tông bịt đáy theo 2 sơ đồ dầm của bảng tính T11-T12 | M6.2 |
| D5 | Giai đoạn chống tăng cường xuống bệ chỉ mô tả, ghi "chưa tính" | Trục 4 |
| D6 | Đất không thấm dưới mực nước: **bắt buộc kiểm tra cả Sơ đồ 1 và Sơ đồ 2** của Điều 7.3.2.6, kết luận theo sơ đồ bất lợi (anh Nghĩa chốt 06/11/2026: "Cả 2 sơ đồ"). Sơ đồ 1 giả thiết nước trong hố thấm vào khe phía trong đến cùng cao độ với phía ngoài [GIẢ THIẾT] | M1.2, M3.2 |

## PHẦN VI: VIỆC CÒN CHỜ XÁC NHẬN

1. Có giữ hệ số 0,85 (bê tông bịt đáy đổ dưới nước) làm giả thiết kỹ thuật không (M6.2).
2. γ_M = 1,00: xác nhận vòng vây trụ cầu thuộc nhóm "tường cừ hố đào, trụ tạm" của Bảng 3 dòng 4, TCVN 5575:2024. Văn bản phân cấp [2] mà Bảng 3 dẫn chiếu em chưa đối chiếu (M4.2).
3. Dạng hiện của (I15), các giá trị mặc định β, α và cách hiểu `d = D` trong (I8) (M2, M6).
4. Điều khoản cụ thể của TCVN 5575:2024 cho cấu kiện nén uốn: sẽ ghi khi lập module code (M5.4).
