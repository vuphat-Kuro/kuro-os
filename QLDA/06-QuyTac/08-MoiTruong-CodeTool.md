> Đọc khi: Cần viết script, tool, kiểm tra phần mềm chuyên ngành, môi trường máy và quy ước viết code.
> Nguồn gốc: tách từ GEMINI.md v2.12 (bản lưu). Quy tắc chung ở QLDA/CLAUDE.md; số mục trong file này là số nội bộ, giữ nguyên.

### 11.3. Phần mềm chuyên ngành & Công cụ hỗ trợ

- **Đã cài trên máy làm việc:** AutoCAD 2020 (R23.1, có VBA Enabler) · Microsoft 365 Apps (Word, Excel, PowerPoint, Outlook) · MS Project Pro 2019.
- **Có dùng trong công việc nhưng chưa cài trên máy này:** Civil 3D, Revit, Midas, RM Bridge, Msheet, GEO5, Plaxis. AI không giả định chạy được các phần mềm này; khi cần thì người dùng chạy ở máy khác và gửi file kết quả để AI rà soát.
- Script AutoLISP / DXF phải tương thích **AutoCAD 2020** (không dùng lệnh/hàm chỉ có ở bản mới hơn).

### 11.4. Môi trường máy

> Kiểm tra thực tế ngày 05/10/2026. Khi cài thêm/nâng cấp phần mềm, cập nhật lại mục này.

| Thành phần | Phiên bản / ghi chú |
|---|---|
| Hệ điều hành | Windows 11 Pro |
| Python | 3.14.3 – openpyxl 3.1.5, pandas 3.0.6, python-docx 1.2.0, matplotlib 3.11.2, ezdxf 1.4.4, pypdf 6.7.5, PyMuPDF 1.27.2, pywin32 |
| Office | Microsoft 365 Apps (16.0) + Project Pro 2019 |
| CAD | AutoCAD 2020 |
| LibreOffice | **Không cài** - kiểm tra công thức Excel bằng **Excel 365 qua COM** (script `tinh_lai_excel.py` tại `QLDA/02-Tools/02-Python/TinhLaiExcel/`) |

- **Đọc PDF bằng script Python (PyMuPDF / pypdf)**, không dựa vào công cụ xem file của AI. PDF scan hoặc font cũ (TCVN3, VNI) → dùng PyMuPDF chuyển trang sang ảnh rồi đọc, ghi rõ chỗ đọc không chắc chắn.
- Thư mục `%APPDATA%\Python\<phiên bản>\Scripts` chưa có trong PATH → gọi công cụ dòng lệnh qua `python -m <ten_goi>`.

---

## PHẦN 12. HỖ TRỢ CÔNG NGHỆ & QUY ƯỚC VIẾT CODE / TOOL

### 12.1. Định hướng chung
- Đề xuất giải pháp theo quy mô: Excel/Google Sheets → cơ sở dữ liệu → ứng dụng web → AI Agent.
- Thiết kế công cụ: dữ liệu có cấu trúc, truy vết, phân quyền, lịch sử chỉnh sửa, nhập/xuất, báo cáo.
- **Tách biệt:** dữ liệu đầu vào · quy tắc xử lý · kết quả tính · phần người dùng xác nhận.
- Ưu tiên triển khai từng bước, dễ bảo trì, dùng được cả văn phòng và công trường.
- Ưu tiên tự động hóa: tổng hợp báo cáo tuần/tháng, đối chiếu KH–TT, theo dõi tồn tại, theo dõi vật tư luân chuyển, tra cứu tiêu chuẩn/hồ sơ.
- Đầu ra AI sau khi được anh Nghĩa soát xét và chấp thuận sẽ là sản phẩm chính thức cuối cùng theo QLDA/CLAUDE.md (mục 1); khi cần trình CĐT/TVGS hoặc phục vụ hồ sơ pháp lý, tiếp tục tuân thủ quy trình thẩm tra, phê duyệt theo quy định dự án.

### 12.2. Quy ước khi viết code / tool
**Ngôn ngữ ưu tiên:** AutoLISP, Python, C# add-in, Web (HTML/JS), Excel VBA / công thức. (Chọn ngôn ngữ phù hợp nhất với công việc, nếu có nhiều lựa chọn thì đề xuất một và nêu lý do).

- **Chung:** Comment và tên biến có ý nghĩa (được dùng tiếng Việt). Tham số đầu vào (lớp, tên, đường dẫn, dung sai…) gom lên đầu file để dễ sửa. Code phải có bẫy lỗi (không có đối tượng, chọn sai loại, giá trị rỗng) và báo lỗi dễ hiểu cho người dùng.
- **Thao tác sửa mô hình/bản vẽ:** Phải gói trong Transaction (Revit) hoặc undo group (AutoCAD `_.UNDO BE/E`) để người dùng có thể hoàn tác. Cuối lệnh cần báo số đối tượng đã xử lý.
- **AutoLISP:** Đặt tiền tố lệnh `c:` rõ nghĩa. Khai báo biến cục bộ sau `/`. Phải có `*error*` handler để khôi phục biến hệ thống (OSMODE, CMDECHO…).
- **C# add-in:** Cung cấp kèm file `.addin` / cấu hình build và hướng dẫn cài đặt.
- **Python độc lập:** Dùng `openpyxl` / `pandas` cho Excel, `python-docx` cho Word, `ezdxf` cho bản vẽ DXF, `matplotlib` cho biểu đồ, `PyMuPDF` / `pypdf` cho PDF. Ghi rõ dependency vào `requirements.txt`.
- **Kiểm thử:** Excel có công thức phải mở lại bằng Excel 365 (`tinh_lai_excel.py` tại `QLDA/02-Tools/02-Python/TinhLaiExcel/`) để bắt lỗi `#` và thử sửa ô đầu vào xem kết luận có đổi theo không, trước khi báo "đạt".
- **Web app:** Dùng HTML/CSS/JS thuần hoặc framework nhẹ, ưu tiên chạy offline, đảm bảo giao diện responsive dùng tốt trên điện thoại khi ở công trường.
- **VBA:** Luôn dùng `Option Explicit`. Tắt `ScreenUpdating` khi xử lý dữ liệu lớn và phải chắc chắn bật lại trong mọi nhánh thoát lệnh.
- **Đa phiên bản & Đơn vị nội bộ phần mềm (BẮT BUỘC v2.11):** Khi viết tool/script cần chạy trên nhiều phiên bản phần mềm (AutoCAD 2020+, Civil 3D, Revit/Dynamo...), bắt buộc ghi rõ phiên bản mục tiêu trong header/README và xử lý phân nhánh các hàm API khác nhau giữa các phiên bản. Riêng khi viết script/add-in cho **Revit/Dynamo** (chạy trên máy phối hợp, không cài trên máy anh Nghĩa): lưu ý đơn vị nội bộ của Revit là `feet` (không phải mm), bắt buộc quy đổi qua `UnitUtils` hoặc `UnitFormatUtils` sang `mm`/`m` trước khi hiển thị/xuất kết quả; Dynamo phiên bản mới ưu tiên `CPython3` (IronPython đang bị loại dần). Đối với **AutoLISP**: tuyệt đối tuân thủ tương thích AutoCAD 2020 (R23.1), không dùng hàm/lệnh chỉ có ở phiên bản mới hơn.
- **Kỷ luật Tra cứu trước khi viết mã & Tái sử dụng (Search-Before-Code v2.15):** Trước khi bắt tay viết bất kỳ script Python nào mới, AI bắt buộc phải tra cứu danh mục tại `QLDA/02-Tools/` và `skills/`.
  + *Thư viện nền tảng dùng chung (Tầng 1):* Bắt buộc quét và tái sử dụng 100% (`cad_geo_utils.py`, `tcvn3_unicode.py`), chấm dứt việc viết lại cùng một thuật toán cơ bản.
  + *Mô hình tính toán chuyên môn & kết cấu (Tầng 2):* Cho phép AI và kỹ sư tự do kế thừa có chọn lọc hoặc viết script mới tại `QLDA/99-Temp/<slug_agent>/` phù hợp với điều kiện biên, địa chất, thủy văn của công trình mới. Nghiêm cấm áp đặt máy móc mô hình của dự án này sang dự án khác.
- **Cơ chế Phân tầng Vòng đời Công cụ (3-Tier Tool Maturity Lifecycle):**
  + *Tầng 1: Thư viện nền tảng (Generic Utilities tại `00-Common/`):* Các hàm toán học, hình học CAD, chuyển mã font độc lập dự án, đã kiểm thử độc lập, bắt buộc tái sử dụng 100%.
  + *Tầng 2: Module đang phát triển & Thử nghiệm (WIP / Experimental):* Các bài toán kết cấu, thủy lực, thi công chuyên sâu đang trong quá trình anh Nghĩa nghiên cứu, hiệu chỉnh (như `KiemToanVongVay`). Chỉ tham khảo giải thuật, cấm ép dùng bắt buộc, được toàn quyền tùy biến và phân nhánh phục vụ bài toán mới.
  + *Tầng 3: Công cụ chuẩn hóa sản xuất (Production Tools):* Các công cụ tự động hóa quy trình đã hoàn thiện ổn định, áp dụng đúng phạm vi và có đầy đủ Hồ sơ Thẩm tra Kỹ thuật được phê duyệt.
- **Quy trình Thẩm tra Kỹ thuật trước khi Đóng gói (Tool Validation Dossier):** Điều kiện chuyển từ Tầng 2 (WIP) lên Tầng 3 (Production) bắt buộc phải lập Hồ sơ Thẩm tra gồm 4 nội dung: (1) Thuyết minh cơ sở lý thuyết và tiêu chuẩn áp dụng, (2) Phạm vi và giới hạn áp dụng cụ thể, (3) Bảng đối chứng kiểm thử (Benchmark) với Excel chuẩn, phần mềm chuyên ngành hoặc số liệu hiện trường, (4) Phê duyệt chấp thuận của Phó phòng KT-TC (anh Nghĩa).
- **Chu trình Chưng cất Công cụ & Thu hoạch định kỳ:** Tệp nháp tạo tại `99-Temp/<slug>/`, định kỳ cuối tuần dùng `ThuHoachTool` rà soát, dọn dẹp file rác debug và thu hoạch thuật toán đóng gói lên Cấp 2 (`02-Tools/`) hoặc Cấp 3 (`skills/`).

### 12.3. Quy chuẩn kỹ thuật cho ứng dụng web / HTML Bình đồ tiến độ 4D

- **Xử lý múi giờ địa phương (formatLocalDate):** Tuyệt đối không dùng `toISOString().slice(0, 10)` để lấy ngày hiển thị vì múi giờ UTC làm lùi 7 giờ (ngày 02/11 GMT+7 bị lùi về 01/11 UTC). Bắt buộc dùng hàm `formatLocalDate(d)` định dạng theo giờ địa phương (`d.getFullYear()`, `d.getMonth() + 1`, `d.getDate()`).
- **Cơ chế snapshot_version cache busting:** Khi lưu trữ trạng thái tiến độ vào `localStorage`, bắt buộc kiểm tra `snapshot_version`. Nếu mã phiên bản khác với mã hiện hành trong file HTML, bắt buộc gọi `localStorage.removeItem()` và nạp lại dữ liệu gốc, chống lưu cache sai lệch.
- **Bóc tách XML MS Project trực tiếp trên trình duyệt:** Dùng `DOMParser` phân tích cú pháp XML, duyệt tag `<Task>`, bóc tách `<WBS>`, `<Start>`, `<Finish>`, `<Duration>`, `<PercentComplete>`, `<Critical>`, `<TotalSlack>`. Tự động ánh xạ vào từ điển cấu kiện hình học SVG.
- **Kỷ luật Component Gate trong mã nguồn:** Điều kiện kiểm tra hoàn thành bệ móng phải viết độc lập: `grpActual && grpActual.footing_done === true`, tuyệt đối cấm dùng `grpActual.status === 'COMPLETED'` của cụm cọc khoan nhồi.
- **Hiển thị màu dầm bản rỗng theo Book2:** Sử dụng bảng mã màu nhận diện có độ tương phản cao trên nền tối SVG: Qua đường (`#f97316` - Cam), Qua sông (`#06b6d4` - Cyan), Qua hầm (`#a855f7` - Tím), Trên cạn (`#22c55e` - Lục).

#### Danh mục Công cụ & Thư viện Dùng chung Chính thức (`02-Tools`)

| Nhóm công cụ | Vị trí thư mục / tệp tin | Chức năng chính | Môi trường / Ghi chú |
| :--- | :--- | :--- | :--- |
| **Dùng chung (Tầng 1)** | `02-Tools/00-Common/tcvn3_unicode.py` | Chuyển đổi mã TCVN3 - Unicode 2 chiều, khởi tạo Layer/TextStyle/DimStyle chuẩn PKTTC | `ezdxf`, AutoCAD 2020 |
| **Dùng chung (Tầng 1)** | `02-Tools/00-Common/cad_geo_utils.py` | Giải mã cung tròn bulge, biến đổi Affine 2D, diện tích Shoelace, trọng tâm, chuyển đổi tọa độ VN-2000 | `math`, `ezdxf` |
| **Python CLI (Tầng 3)** | `02-Tools/02-Python/TinhLaiExcel/` | Mở lại workbook bằng Excel 365 COM để tính lại toàn bộ công thức và kiểm tra lỗi `#` | `pywin32`, Excel 365 |
| **Python CLI (Tầng 3)** | `02-Tools/02-Python/KiemTraCauTruc/` | Kiểm tra cấu trúc GEMINI.md (bản lưu), không còn dùng | Python 3.14+ |
| **Python CLI (Tầng 3)** | `02-Tools/02-Python/KiemTraDauRa/` | Quét LaTeX, em dash, link, nhãn dữ liệu. **Chỉ chạy khi anh yêu cầu** | Python 3.14+ |
| **Python CLI (Tầng 3)** | `02-Tools/02-Python/DxfToSvgMaster/` | Trình xuất mặt bằng thi công SVG chuẩn từ AutoCAD DXF (lọc layer, tọa độ VN-2000, HTML preview) | `ezdxf >= 1.4.4` |
| **Python CLI (Tầng 2 - WIP)** | `02-Tools/02-Python/KiemToanVongVay/` | Thử nghiệm: Kiểm toán vòng vây cọc ván thép tham khảo Ninh Cơ (đang hiệu chỉnh, cấm ép dùng) | TCVN 11815:2017 (WIP) |
| **Python CLI (Tầng 3)** | `02-Tools/02-Python/ThuHoachTool/` | Rà soát phân loại 411+ script vùng đệm 99-Temp, dọn dẹp file rác và thu hoạch thuật toán định kỳ | Python 3.14+ |

---

