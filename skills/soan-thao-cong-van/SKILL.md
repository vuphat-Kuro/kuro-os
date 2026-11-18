---
name: "Soạn thảo công văn"
description: "Soạn công văn, tờ trình, văn bản hành chính theo biểu mẫu Phương Thành (BM01 gửi ngoài, BM03A nội bộ/trình Ban Lãnh đạo) bằng cách nhân bản mẫu đã duyệt và chỉ thay nội dung, giữ nguyên thể thức, tuân thủ NĐ 30/2020."
group: Vận hành
---

# Soạn thảo Công văn (Phương Thành)

## 0. NGUYÊN TẮC GỐC
1. **Giữ đúng form mẫu, chỉ khác nội dung.** Luôn nhân bản mẫu đã duyệt rồi thay chữ. Cấm dựng Word từ trang trắng, cấm tự đổi lề, cỡ chữ, dãn dòng, thụt dòng, header, bảng ký, khối Ý kiến Lãnh đạo. Mọi thông số lấy từ chính file mẫu, không lấy từ trí nhớ.
2. **Ngắn gọn, đúng trọng tâm.** Số trang tùy nội dung, không khống chế 1 hay 2 trang. Viết cái Lãnh đạo cần để quyết: vấn đề, kết quả kiểm tra của Phòng, đề xuất. Số liệu nhiều thì đưa vào phụ lục.
3. **Không bịa** số văn bản, ngày, căn cứ, người ký, số liệu. Chưa có thì để trống số văn bản hoặc ghi `[CẦN BỔ SUNG: ...]`.
4. **Chỉ xuất Word (.docx).** PDF chỉ khi người dùng yêu cầu.
5. **Nháp trước, ban hành sau.** File nháp tên `NHAP_...docx`. Chỉ chuyển vào hồ sơ dự án khi người dùng nói "duyệt" / "phát hành".

## 1. CHẠY TRONG KURO
- Thư mục skill = thư mục chứa file này; gọi script bằng đường dẫn tuyệt đối `<thư mục skill>/scripts/...`.
- Cwd là thư mục dự án hiện hành: file nháp và sổ theo dõi ghi vào đó (hoặc `--outdir`). Chưa rõ nơi lưu thì HỎI. Không ghi vào kho mạng công ty (chỉ đọc).
- Cần `python-docx`, `openpyxl` (có trong `requirements-ky-thuat.txt`). PDF cần Word + `pywin32`.

## 2. CHỌN MẪU

| Mẫu | File trong `templates/` | Gửi cho |
| :--- | :--- | :--- |
| **BM03A** (mẫu duyệt, ưu tiên) | `Mau_BM03A_Trinh_Lanh_Dao_Da_Duyet.docx` | Ban Lãnh đạo Công ty, phòng ban, BĐH dự án, công trường |
| BM03A trọn 1 trang (ví dụ) | `Mau_BM03A_1Trang_Thue_Van_Chuyen_CV841.docx` | tham khảo cách viết ngắn |
| BM03A trắng | `BM3A_VB-2025_VB_Noi_Bo.docx` | nội bộ khi không dùng mẫu duyệt |
| **BM01** | `BM01_VB-2025_CV_Gui_Ra_Ngoai.docx` | Chủ đầu tư, Ban QLDA, TVGS, TVTK, cơ quan nhà nước, đối tác, thầu ngoài |

Nơi nhận lẫn cả ngoài và nội bộ, hoặc nội dung nói "Quý Công ty" mà người nhận là nội bộ: HỎI người dùng chọn mẫu.

## 3. QUY TRÌNH
1. **Hỏi gộp 1 lần** các thông tin thiếu: nơi nhận, trích yếu, nội dung và căn cứ (báo cáo BĐH, biên bản, bản vẽ), người ký, ngày, số văn bản.
2. **Soạn nội dung ngắn** theo mẫu duyệt:
   - Căn cứ: chỉ căn cứ nội bộ/kỹ thuật (chức năng nhiệm vụ Phòng, báo cáo BĐH, BVTC, thực tế công trường), viết "Căn cứ ...;". Không đưa căn cứ hợp đồng xây lắp vào văn bản nội bộ.
   - Mở đầu bằng câu chuẩn: "Sau khi kiểm tra, rà soát số liệu báo cáo của Ban Điều hành và tình hình thi công trên công trường, Phòng Kỹ thuật Thi công báo cáo Lãnh đạo Công ty một số nội dung sau:".
   - Thân bài 2-4 đoạn ngắn: hiện trạng và nguyên nhân, kết quả kiểm tra của Phòng, đề xuất dứt khoát. Không đánh giá chi tiết số liệu của BĐH trong thân bài; bảng đối chiếu để phụ lục.
   - Kết bằng "Trân trọng cảm ơn!".
3. **Dựng file** bằng `build_bm03a_document` (mục 4). Hàm nhân bản mẫu duyệt và chỉ thay chữ.
4. **Rà soát**: chạy `python "<thư mục skill>/scripts/kiem_tra_form.py" file.docx` (đối chiếu lề, header, ký, nơi nhận, khối Ý kiến, câu kết với mẫu duyệt); còn `LỖI` thì sửa và dựng lại. Không còn chữ mẫu cũ; `[CẦN BỔ SUNG]` còn lại phải báo người dùng. Con số tính từ tool `tinh_python`.
5. **Báo người dùng**: đường dẫn file nháp, các điểm cần bổ sung.

## 4. DỰNG BM03A TỪ MẪU DUYỆT
```python
import sys; sys.path.insert(0, "<thư mục skill>/scripts")
from bm03a_builder import build_bm03a_document

build_bm03a_document(
    output_path="NHAP_BM03A_TenNgan.docx",
    trich_yeu="V/v ...",                       # tự thêm "V/v", không dấu ":"
    can_cu_list=["Căn cứ ...;", "Căn cứ ... ."],
    noi_dung_paragraphs=[                      # đoạn đầu = câu mở đầu chuẩn; **...** = chữ đậm
        "Sau khi kiểm tra, ... một số nội dung sau:",
        "Hiện trạng ...",
        "Kết quả kiểm tra của Phòng ... **30.000.000 đồng** ...",
        "Kính đề nghị Lãnh đạo Công ty ...",
        "Trân trọng cảm ơn!"],
    so_vb="Số:       /PT-KTTC",
    ngay_vb="Hà Nội, ngày ... tháng ... năm 2026",
    kinh_gui="Ban Lãnh đạo Công ty",           # hoặc list nhiều nơi
    noi_nhan_list=["- Như trên;", "- ... (để t/h);", "- Lưu: VT, KTTC."],
    # Phụ lục (bỏ hết 4 tham số này nếu không cần phụ lục):
    phu_luc_title="PHỤ LỤC ...",
    phu_luc_table_headers=["TT", "Nội dung", "Căn cứ số liệu", "Giá trị"],
    phu_luc_table_rows=[["1", "...", "...", "25.000.000"]],
    phu_luc_notes=["Ghi chú: ..."],
)
```
- Phần giữ nguyên từ mẫu: header logo (chỉ trang đầu), lề, cỡ chữ, dãn dòng, thụt dòng, khối ký 2 dòng, chừa chỗ viết tay dưới "Ý KIẾN BAN LÃNH ĐẠO CÔNG TY".
- Phụ lục: bảng khung đơn, đầu bảng tô xanh nhạt, cỡ 11, số căn phải, bắt đầu trang mới.
- Chỉ đổi người ký / khối Ý kiến khi người dùng yêu cầu (`nguoi_ky_chuc_danh`, `nguoi_ky_ho_ten`, `khoi_lanh_dao_title`).

## 5. CÔNG CỤ KHÁC (`van_ban_engine.py`)
- Nhân bản mẫu để sửa tay (BM01): `python "<thư mục skill>/scripts/van_ban_engine.py" clone BM01 NHAP_BM01_X.docx`
- Làm sạch khi phát hành (bỏ khung "Mẫu số", sửa lỗi chính tả mẫu): `... clean NHAP_BM01_X.docx --release`
- Dựng BM03A từ JSON: `... build-bm03a cauhinh.json --out NHAP_BM03A_X.docx`
- Ghi sổ theo dõi: `... log --so "..." --ngay "..." --mau BM03A --nhan "..." --trich "..." --ky "..." --file "..."`
- BM01: nhân bản rồi thay chữ trong mẫu theo cách tương tự; xóa chỉ số trên `¹⁰ ¹¹ ¹² ¹³`, xóa khối "Ghi chú (1)-(7)", highlight vàng và phương án kính gửi không dùng.

## 6. QUY CHUẨN BM03A (chi tiết: `references/QUY_CHUAN_BM03A_PKTTC.md`)
Số `Số:       /PT-KTTC`; ngày `Hà Nội, ngày ... tháng ... năm 2026` nghiêng căn phải; trích yếu cỡ 12 justify, không đậm, không nghiêng; ký đúng 2 dòng `PHÒNG KỸ THUẬT THI CÔNG` / `TP. Đỗ Đắc Luận` in đậm; nơi nhận cỡ 10 kết thúc `- Lưu: VT, KTTC.`; khối `Ý KIẾN BAN LÃNH ĐẠO CÔNG TY` in hoa đậm, để trống viết tay. Tất cả đã nằm sẵn trong mẫu duyệt: dùng hàm ở mục 4 là đủ.
