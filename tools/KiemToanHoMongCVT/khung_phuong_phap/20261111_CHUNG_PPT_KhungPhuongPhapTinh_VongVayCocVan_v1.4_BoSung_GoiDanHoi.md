---
type: wiki
status: active
tags: [wiki, qlda, kcpt, vong-vay-coc-van, goi-dan-hoi]
created: 2026-11-10
version: v1.4 (bản bổ sung, ĐÃ DUYỆT 11/11/2026)
bo_sung_cho: 20261111_CHUNG_PPT_KhungPhuongPhapTinh_VongVayCocVan_v1.3_BoSung.md (ĐÃ DUYỆT 11/11/2026) và 20261106_CHUNG_PPT_KhungPhuongPhapTinh_VongVayCocVan_v1.2.md (ĐÃ DUYỆT 06/11/2026)
ap_dung_cho: 99-Temp/NHAP_kiem_toan_vong_vay.html (chương trình đã làm theo bản này, 10/11/2026)
approved: 2026-11-11
approved_by: Kiều Linh Nghĩa - Phó phòng KT-TC
nguon_du_thao: 99-Temp/qlda/NHAP_20261110_KhungPhuongPhapTinh_VongVayCocVan_v1.4_BoSung_GoiDanHoi.md (sao lưu _backup/20261111/)
ap_dung_cho_sha: 975831955a0e

---

> **Trạng thái: ĐÃ DUYỆT 11/11/2026 (anh Kiều Linh Nghĩa).** Bản gốc là dự thảo xin ý kiến; nội dung dưới đây giữ nguyên như bản dự thảo đã trình. Đề xuất xin ý kiến anh Kiều Linh Nghĩa. Anh đã đồng ý các đề xuất và cho làm tiếp (10/11/2026); chương trình đã làm theo bản này (xem Phần F), văn bản khung vẫn chờ anh duyệt chính thức. Khung v1.2 (đã duyệt) và v1.3 (đã duyệt 11/11/2026) giữ nguyên.
> Bản này **không đổi khung bốn trục và sáu module**. Nó thêm một tùy chọn ở Module 4 (độ bền cừ): sơ đồ gối dưới của cừ là **gối cố định theo TCVN 11815:2017** (như hiện nay, mặc định) hoặc **gối đàn hồi theo TCVN 10304:2014 Phụ lục A**.
> Nhãn: `[ĐÃ XÁC MINH]` (đọc văn bản gốc, PDF trong `04-TieuChuan/` và thư viện), `[NGƯỜI DÙNG KHAI]` (anh chốt 10/11/2026), `[GIẢ THIẾT]` (em đặt, chờ anh duyệt), `[CẦN KIỂM TRA]`.
> File Excel mẫu chỉ dùng để học cách trình bày, không làm căn cứ tính. Mọi công thức và hệ số dưới đây lấy từ tiêu chuẩn hoặc từ quyết định của anh.

## KẾT LUẬN 10 GIÂY

- Thêm tùy chọn **gối đàn hồi**: cừ là dầm trên các lò xo đặt cách nhau s (ô nhập, mặc định 0,4 m) từ đáy hố xuống mũi cừ; độ cứng lò xo theo C_z = k·z/γc (TCVN 10304 A.1, A.2), k tra Bảng A.1 do người dùng chọn.
- Giữ nguyên chống lật (Module 3) và thanh chống (Module 5). Giai đoạn bịt đáy giữ gối 0,5 m dưới mặt bê tông bịt đáy.
- Bổ sung hai kiểm tra: chuyển vị cừ ≤ L/400 (theo A.3, giới hạn do anh chốt, không kiểm góc xoay) và áp lực nền (A.7), cùng kiểm hội tụ theo khoảng cách gối (ngưỡng 1%).
- Tiêu chuẩn **không quy định** khoảng cách gối, tải trọng lên tường cừ khi dùng lò xo, và các hệ số của (A.7) cho tường cừ. Phần C liệt kê các giả thiết em đặt để anh duyệt.
- Sửa lỗi trích dẫn ở v1.3 (C10): nền đàn hồi nằm ở **Phụ lục A** của TCVN 10304:2014, không phải Phụ lục G.

---

## PHẦN A. CÁC QUYẾT ĐỊNH NGÀY 10/11/2026 [NGƯỜI DÙNG KHAI]

| Mã | Quyết định (anh chốt) |
|---|---|
| **E1** | Hệ số điều kiện làm việc γc của (A.1) áp dụng cho tường cừ (mặc định 3, ô nhập). |
| **E2** | Tải lên cừ khi dùng lò xo: áp lực đất chủ động phía sau cộng áp lực nước. Phía hố đào: áp lực nước **giữ nguyên là tải**, các lớp đất trong hố móng (từ đáy hố xuống) được **thay bằng gối đàn hồi**. |
| **E3** | Hệ số k do người dùng chọn. Chương trình hiển thị bảng tra Bảng A.1 làm cơ sở chọn. |
| **E4** | Giai đoạn bịt đáy: giữ gối cố định 0,5 m dưới mặt bê tông bịt đáy (TCVN 11815 7.3.5.4, v1.3 D7 a). |
| **E5** | Giai đoạn công xôn (chưa có tầng chống) cũng dùng lò xo. |
| **E6** | Có kiểm tra theo TCVN 10304 A.3 (chuyển vị) và A.7 (áp lực nền). |
| **E7** | Khoảng cách gối đàn hồi s là **ô nhập**, mặc định **0,4 m**. Lưới phần tử dầm giữ như bộ giải hiện nay (100 phần tử, thêm nút tại chỗ tải đổi đột ngột). Kiểm hội tụ ngưỡng **1%**. |
| **E8** | Giới hạn chuyển vị ngang của cừ lấy **L/400** (thay cho ô nhập u_u). **Không kiểm tra góc xoay** Ψ. TCVN 10304 A.3 chỉ yêu cầu giới hạn "cho trước trong đồ án", không cho con số; L/400 là quyết định của anh. |

---

## PHẦN B. THAY ĐỔI PHƯƠNG PHÁP (Module 4)

### B1. Phạm vi áp dụng

| Giai đoạn | Sơ đồ gối dưới | Ghi chú |
|---|---|---|
| Công xôn (chưa có tầng chống, nAct = 0), không bịt đáy | Gối đàn hồi (khi chọn tùy chọn) | v1.2: gối ngàm tại t0 theo 7.3.3.2 |
| Có tầng chống, không bịt đáy | Gối đàn hồi | v1.3 D7 b: gối t/2 theo 7.3.5.3 |
| Có bịt đáy (kể cả chưa hút cạn) | **Gối cố định 0,5 m dưới mặt bịt đáy**, không đổi | v1.3 D7 a, 7.3.5.4 |

Lựa chọn là **một cho cả công trình** (không chọn từng giai đoạn). Mặc định: gối cố định, nên mọi kết quả hiện có không đổi nếu anh không bật tùy chọn.

### B2. Sơ đồ tính của phương án gối đàn hồi

1. **Dầm:** dải 1 m theo chiều dài tường, từ đỉnh cừ đến mũi cừ. EI giữ như hiện nay (EI = 0,21·I_x, T.m² trên mét; E = 2,1·10⁶ kg/cm²).
2. **Gối trên:** các tầng chống là gối chốt như cũ.
3. **Mũi cừ tự do** (không đặt gối).
4. **Lò xo phía hố đào**, chỉ từ đáy hố của giai đoạn đó xuống mũi cừ. Gọi z là độ sâu kể từ đáy hố (mặt đất tính toán của phía hố đào, theo A.2 "kể từ mặt đất" [GIẢ THIẾT: coi đáy hố là mặt đất tính toán]).
5. **Các trạm lò xo:** z_j = j·s (j = 1, 2, ...) cho đến mũi cừ, thêm một trạm tại mũi cừ nếu phần dư lớn hơn 1 mm. Trạm z = 0 không có lò xo (C_z = 0).
6. **Đoạn đại diện mỗi lò xo:** từ trung điểm với trạm trước đến trung điểm với trạm sau; đoạn đầu bắt đầu từ đáy hố, đoạn cuối kết thúc tại mũi cừ. Tổng các đoạn bằng đúng chiều sâu ngập. [GIẢ THIẾT cách chia đoạn]
7. **Độ cứng lò xo:** `K_v,j = b · ∫ C_z(z) dz` trên đoạn đại diện, với `C_z(z) = k(z)·z / γc` (A.1, kN/m³). k lấy theo lớp đất tại độ cao của z. Đoạn nằm vắt qua ranh hai lớp thì tích phân theo từng lớp, không phải lấy k của một lớp. b = 1 m (dải tính, khớp với I_x tính trên mét) [GIẢ THIẾT].
8. **Lò xo chỉ chịu nén:** lò xo nằm ở phía cừ dịch chuyển ra khỏi đất (bị kéo) bị loại khỏi hệ; giải lặp đến khi tập lò xo làm việc không đổi [GIẢ THIẾT: TCVN 10304 A.2 coi nền là môi trường đàn hồi tuyến tính, không nói lò xo chỉ chịu nén; cừ ở phía đất bị động nên cần loại lực kéo].
9. **Tải:**
   - Áp lực chủ động phía sau (p_a) trên toàn chiều dài cừ, kể cả đoạn dưới đáy hố.
   - Áp lực nước theo Hình 7.13 (hiệu nước ngoài trừ nước trong, v1.3 Q1), toàn chiều dài. Nước trong hố giữ làm tải.
   - **Bỏ p_p** (áp lực bị động) dưới đáy hố khỏi tải; phần chống đỡ của đất đó do lò xo đảm nhận.
   - Hai sơ đồ 7.3.2.6 vẫn được bao (v1.3 CT-B11).
10. **Không áp (7-14)** (M = M_B + 0,75·M_m). Hệ số 0,75 gắn với sơ đồ dầm gối cố định 7.3.4.3, nên phương án đàn hồi giải **tổng tải** [GIẢ THIẾT].
11. **Mômen và ứng suất:** M_max từ FEM; σ = M_max / (η_w·k_hm·W_x) so với σ cho phép như Module 4 hiện hành. Không đổi.
12. **Phản lực tầng chống:** lấy từ FEM của phương án này, đưa sang Module 5. Phản lực tổng của lò xo được báo riêng.

### B3. Kiểm tra mới

**(a) Chuyển vị giới hạn, TCVN 10304 A.3 b) (A.2):** `u_p ≤ u_u`. A.3 nêu rõ u_u "cần được cho trước trong đồ án" nhưng không cho số; **u_u = L/400** theo quyết định E8 [NGƯỜI DÙNG KHAI]. **Không kiểm góc xoay** Ψ (A.3) [NGƯỜI DÙNG KHAI]. Không có ô nhập u_u.
- u_p lấy là chuyển vị ngang lớn nhất của cừ trong từng đoạn [GIẢ THIẾT: A.3 viết cho chuyển vị đầu cọc].
- **L là gì** (chưa có chỉ định, em đặt [GIẢ THIẾT], anh sửa nếu khác): chia cừ thành các đoạn theo gối chốt (tầng chống). Mỗi đoạn kiểm `u_max,đoạn ≤ L_đoạn/400`, kết luận theo đoạn có tỷ số u/(L/400) lớn nhất.
  - Đoạn giữa hai tầng chống kề nhau: L = khoảng cách hai tầng.
  - Đoạn từ đầu cừ đến tầng chống đầu tiên (đầu hẫng): L = khoảng cách đó. **u là chuyển vị so với tiếp tuyến của cừ tại tầng chống đầu tiên** (không phải chuyển vị tuyệt đối), vì đầu cừ dịch chuyển chủ yếu do cừ xoay quanh tầng chống chứ không do đoạn hẫng cong [GIẢ THIẾT, bổ sung khi lập trình; ca T11 thử cho chuyển vị tuyệt đối 24 mm so với giới hạn 2,5 mm ở đoạn hẫng 1 m, không phản ánh độ võng của đoạn hẫng].
  - Đoạn từ tầng chống thấp nhất xuống mũi cừ (có lò xo): L = khoảng cách từ tầng chống thấp nhất đến đáy hố; u_max lấy trên cả đoạn này kể cả phần dưới đáy hố.
  - Giai đoạn công xôn (chưa có tầng chống): L = chiều cao từ đầu cừ đến đáy hố.
- Tỷ số u/(L/400) chỉ dùng nội bộ để chọn đoạn chi phối và kết luận đạt hay không đạt; thuyết minh in u_max, L, L/400, kết luận.

**(b) Áp lực nền, TCVN 10304 A.7 [ĐÃ XÁC MINH trên PDF trang 71]:**

`σ_z ≤ η1 · η2 · (4 / cosφ_I) · (γ_I · z · tgφ_I + ξ · c_I)`  (A.7)

`η2 = (M_c + M_t) / (n̄·M_c + M_t)`  (A.8)

- σ_z là áp lực tính toán trên thân cừ lên đất tại độ sâu z: `σ_z = C_z(z) · u(z)` (u là chuyển vị ngang của cừ tại z).
- Độ sâu kiểm: khi `α_ε·l ≤ 2,5` kiểm tại `z = l/3` và `z = l`; khi `α_ε·l > 2,5` kiểm tại `z = 0,85/α_ε`. l là chiều sâu cừ dưới đáy hố. `α_ε = (k·b_p / (γc·E·I))^(1/5)` theo (A.4). Trang 71 in sai "(A.5)", đúng là (A.4) [ĐÃ XÁC MINH, đối chiếu trang 69].
- γ_I, φ_I, c_I theo lớp đất tại z, γ_I có xét đẩy nổi.
- Các hệ số và đại lượng mà tiêu chuẩn viết cho **cọc**, em đề xuất như sau cho tường cừ (anh duyệt hoặc sửa, mục C3):
  - **ξ = 0,6** (cừ đóng, tương ứng "cọc đóng và cọc ống").
  - **η1 = 0,7** (A.7 ghi: "tính móng công trình chắn đất lấy η1 = 0,7"; vòng vây là kết cấu chắn đất).
  - **n̄ = 2,5** (giá trị mặc định của (A.8); hai trường hợp ngoại lệ a, b không áp dụng cho vòng vây).
  - **M_c, M_t:** A.8 định nghĩa mômen "tại tiết diện mũi cọc"; mũi cừ tự do có M ≈ 0 nên (A.8) suy biến (0/0). Đề xuất lấy M_c, M_t tại **tiết diện có mômen lớn nhất** của cừ trong giai đoạn đó, M_c do áp lực đất và nước, M_t do phụ tải mặt (cẩu, thiết bị). Không có phụ tải thì M_t = 0 và η2 = 1/n̄ = 0,4.
  - **k đại diện cho α_ε:** (A.4) cần một k duy nhất; lấy trung bình trọng số theo chiều dày các lớp trong đoạn z từ 0 đến l.

**(c) Chú thích của A.7:** nếu σ_z không đạt (A.7) nhưng cừ còn đủ bền và chuyển vị còn nhỏ, chiều sâu tính đổi `α_ε·l > 2,5` thì phải tính lại với k nhỏ hơn. Chương trình **không tự giảm k** (k do người dùng chọn); chỉ ghi kết quả "không đạt (A.7)" kèm nhắc chú thích này.

### B4. Kiểm hội tụ theo khoảng cách gối (E7)

- Mỗi lần tính, chương trình tính thêm một lần với khoảng cách gối s/2 và so M_max, chuyển vị lớn nhất u_max, áp lực nền lớn nhất σ_z,max.
- Chênh lệch tương đối của cả ba đại lượng ≤ **1%** thì "hội tụ". Vượt 1% thì cảnh báo "kết quả còn phụ thuộc khoảng cách gối, nên giảm s".
- **Không tự đổi s** (s là đầu vào của anh); kết quả chính báo theo s anh nhập, kèm chênh lệch so với s/2. Mục này khác ý ban đầu "tự dùng lưới mịn hơn" vì s nay là ô nhập: chờ anh xác nhận (mục C4).
- Ngưỡng 1% là giả thiết [GIẢ THIẾT, anh đồng ý 10/11/2026], không có trong tiêu chuẩn.

### B5. Thuyết minh in ra khi bật tùy chọn

Ghi rõ: sơ đồ gối đàn hồi theo TCVN 10304:2014 Phụ lục A; bảng đất (lớp, k, nhóm theo Bảng A.1, γc, b); số lò xo, khoảng cách s, tổng phản lực lò xo; kết quả M, σ, u_max so với L/400, (A.7); kết quả kiểm hội tụ; ghi chú các điểm [GIẢ THIẾT] và dòng "tiêu chuẩn viết cho cọc, áp dụng cho tường cừ theo quyết định của người dùng".

---

## PHẦN C. CÁC ĐIỂM TIÊU CHUẨN KHÔNG QUY ĐỊNH, EM ĐẶT [GIẢ THIẾT], CHỜ ANH DUYỆT

| # | Điểm | Em đề xuất | Căn cứ |
|---|---|---|---|
| C1 | Khoảng cách gối đàn hồi | Ô nhập, mặc định 0,4 m, kiểm hội tụ 1% | A.2 chỉ nói "dùng chương trình dầm trên nền đàn hồi"; không có khoảng cách. [ĐÃ XÁC MINH] |
| C2 | Tải lên tường khi dùng lò xo, lò xo chỉ chịu nén, z tính từ đáy hố, b = 1 m, không áp (7-14) | Như B2 mục 4, 8, 9, 10 | Tiêu chuẩn viết cho cọc, không nói tải tường cừ |
| C3 | Hệ số (A.7), (A.8) cho tường cừ | ξ = 0,6; η1 = 0,7; n̄ = 2,5; M_c, M_t tại tiết diện M lớn nhất; k đại diện là trung bình trọng số | B3 (b) |
| C4 | Kiểm hội tụ không tự đổi s | Chỉ cảnh báo | B4 |
| C5 | Cách xác định L của L/400 | Theo đoạn giữa các gối chốt, B3 (a); giới hạn L/400 là quyết định của anh, chỉ cách chia đoạn là giả thiết | A.3 b) |
| C6 | Cách chia đoạn đại diện, tích phân k qua ranh lớp | B2 mục 6, 7 | Chọn của em, không có trong tiêu chuẩn |

---

## PHẦN D. THAY ĐỔI ĐẦU VÀO VÀ CHƯƠNG TRÌNH (ghi trước, làm sau khi anh duyệt khung)

### D1. Tab Đầu vào

**Bảng lớp đất, thêm cột:**
- `I_L` (độ sệt), chỉ cho đất dính, dùng để chọn nhóm Bảng A.1. Cột `e` đã có.
- `Nhóm theo Bảng A.1`: ô chọn 5 nhóm (bảng dưới); chương trình gợi ý theo e và I_L, anh sửa tay.
- `k (kN/m⁴)`: nhập trong khoảng của nhóm; không có giá trị mặc định (anh chọn). Ngoài khoảng của Bảng A.1 thì cảnh báo, không chặn.

**Thẻ mới "Sơ đồ gối dưới cừ":** chọn gối cố định (11815) hoặc gối đàn hồi (10304); khoảng cách gối đàn hồi s (m, mặc định 0,4); γc (mặc định 3); b (mặc định 1 m); bật hoặc tắt kiểm tra (A.7) (giới hạn chuyển vị L/400 cố định, không có ô nhập); hiển thị Bảng A.1 để tra.

**Bảng A.1, hệ số tỷ lệ k theo (A.1)** [ĐÃ XÁC MINH, TCVN 10304:2014 trang 72]:

| Nhóm đất bao quanh | k (kN/m⁴) |
|---|---|
| Cát to (0,55 ≤ e ≤ 0,7); sét và sét pha cứng (I_L < 0) | 18.000 đến 30.000 |
| Cát hạt nhỏ (0,6 ≤ e ≤ 0,75); cát hạt vừa (0,55 ≤ e ≤ 0,7); cát pha cứng (I_L < 0); sét, sét pha dẻo cứng và nửa cứng (0 ≤ I_L ≤ 0,5) | 12.000 đến 18.000 |
| Cát bụi (0,6 ≤ e ≤ 0,8); cát pha dẻo (0 ≤ I_L ≤ 1); sét và sét pha dẻo mềm (0,5 ≤ I_L ≤ 0,75) | 7.000 đến 12.000 |
| Sét và sét pha dẻo chảy (0,75 ≤ I_L ≤ 1) | 4.000 đến 7.000 |
| Cát sạn (0,55 ≤ e ≤ 0,7); đất hạt lớn lẫn cát | 50.000 đến 100.000 |

**Chặn và cảnh báo:** chọn gối đàn hồi mà lớp đất dưới đáy hố thiếu k thì chặn tùy chọn và ghi "Chưa có căn cứ" (không tự điền). Chiều sâu ngập nhỏ hơn t tối thiểu của Module 3 thì giữ cảnh báo hiện có.

### D2. Chương trình (`99-Temp/NHAP_kiem_toan_vong_vay.html`)

1. `solveBeamFEM1D`: thêm lò xo phân bố, giải lặp loại lò xo bị kéo, trả thêm áp lực nền, chuyển vị, phản lực lò xo. Phản lực các gối chốt tính từ ma trận không có lò xo.
2. `solveDynamicBeamStage`: thêm nhánh đàn hồi (dầm đến mũi cừ, bỏ p_p dưới đáy hố, bỏ (7-14) và đối chứng Blum cho nhánh này); giai đoạn bịt đáy giữ nhánh cũ.
3. Hàm tra k(z) và tích phân C_z theo lớp; hàm kiểm (A.7); hàm kiểm hội tụ s và s/2.
4. Cấu hình: trường mới trong `normalizeAndMigrateConfig`, `resetToBlankState`, bảng đất, nạp và lưu JSON; mặc định gối cố định; đổi `snapshot_version`.
5. Kết quả, hình vẽ (ký hiệu lò xo thay tam giác gối), thuyết minh (mục 5 và 6), Excel (C_z, K_v bằng công thức sống; nội lực FEM là giá trị như hiện nay), phạm vi chưa thực hiện C10.

### D3. Kiểm chứng sẽ làm khi lập trình

- Dựng lại độc lập bằng Python (FEM riêng) và so M, phản lực, chuyển vị.
- Thử với k không đổi, so nghiệm giải tích của dầm trên nền đàn hồi (Hetenyi).
- Tổng phản lực bằng tổng tải; hội tụ lưới; đối xứng.
- Hồi quy T11 5 mốc: tùy chọn tắt thì mọi số giữ nguyên.

---

## PHẦN E. SỬA VĂN BẢN KHUNG v1.3

- Dòng C10 của v1.3 ghi "dầm trên nền đàn hồi (TCVN 10304 Phụ lục G)". **Sửa thành Phụ lục A**; Phụ lục G của TCVN 10304:2014 là các phương pháp khác xác định sức chịu tải của cọc [ĐÃ XÁC MINH]. Khi anh duyệt v1.4, C10 tách làm hai: "dầm cừ trên nền đàn hồi" chuyển vào khung (bản này); "S4 hai hàng cừ, hố thế; độ võng cho phép vành đai" giữ ngoài khung.
- `99-Temp/qlda/mau_tinh/dot7/README.md` (dòng 70) cũng ghi nhầm Phụ lục G; đó là README của đợt cũ, em chưa sửa.

---

## PHẦN F. ĐÃ LÀM TRONG CHƯƠNG TRÌNH (10/11/2026, theo bản dự thảo này)

Mã: `99-Temp/NHAP_kiem_toan_vong_vay.html`; tập lệnh vá tái lập được và ghi chú kiểm chứng: `99-Temp/qlda/mau_tinh/dot60/` (README.md).

- **Tab Đầu vào:** bảng lớp đất có thêm cột I_L, Nhóm Bảng A.1 (có gợi ý ★), k; sơ đồ gối dưới cừ (chọn gối cố định hoặc gối đàn hồi, s, γc, b, bật (A.7), bảng A.1 tra cứu) đặt ở **mục 2 Phân tầng địa chất**, trên bảng lớp đất; ba cột I_L, Nhóm Bảng A.1, k chỉ hiện khi chọn gối đàn hồi (gối cố định: bảng chỉ có γ, γ_s, e, γ_đn, φ, c, loại thấm, nhóm cát, t ≥ 2 m, nền yếu). Mặc định gối cố định.
- **Bộ giải:** `solveBeamFEM1D` thêm lò xo phân bố chịu nén (giải lặp); `solveDynamicBeamStage` có nhánh gối đàn hồi cho mọi giai đoạn không có bịt đáy, kể cả giai đoạn công xôn; giai đoạn bịt đáy giữ gối cố định 0,5 m.
- **Chặn khi thiếu k:** thiếu k của lớp đất dưới đáy hố thì giai đoạn tính theo gối cố định, ghi "Chưa có căn cứ" và đánh dấu không đạt, kèm cảnh báo ở tab Đầu vào.
- **Kiểm tra:** u ≤ L/400 theo đoạn (đầu hẫng so với tiếp tuyến tại gối), (A.7) với η2 tách M_c và M_t bằng một lần giải thêm không có phụ tải mặt, hội tụ theo s/2 (chỉ cảnh báo).
- **Hiển thị:** thẻ giai đoạn, tab Kết quả (thẻ chuyển vị, (A.7), hội tụ; bước tính; phạm vi chưa thực hiện C10; danh sách giả thiết), hình mặt cắt (lò xo thay áp lực bị động), thuyết minh mục 6.x.5 (bảng lò xo, bảng L/400, bảng (A.7), hội tụ), Excel (C_z, [u], σz, [σz] bằng công thức sống; nội lực FEM là giá trị).
- **Kết luận giai đoạn:** `is_safe` = σ ≤ [σ] và L/400 và (A.7, nếu bật) và giải lặp ổn định; khi bao nhiều sơ đồ áp lực 7.3.2.6 thì đạt khi mọi sơ đồ đạt.
