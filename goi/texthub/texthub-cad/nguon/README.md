# Mã nguồn PKTTC TextHub (kèm trong gói)

Thư mục này là ảnh chụp mã nguồn tại thời điểm đóng gói, để có thể dựng lại, sửa và hỗ trợ thêm bản AutoCAD khác mà không phụ thuộc máy gốc. Đã bỏ `bin`, `obj`, gói đã dựng, nhật ký và ảnh chụp màn hình.

## Bố cục (giữ nguyên tên thư mục để các tập lệnh dựng tìm được nhau)

| Thư mục | Nội dung |
|---|---|
| `texthub_s1/` | Lõi chuyển bảng mã (không phụ thuộc AutoCAD): `src/Core`, `data/charsets.csv`, `tests/CoreTests.cs`, `tools/` (dựng bảng ký tự), `build.ps1` |
| `texthub_s5/` | Lớp AutoCAD: `src/Db` (quét, kế hoạch, áp dụng, sao lưu, kho font, bảng PKTEXTUI, menu, cổng), `bridge/` (thư viện nối cổng và máy chủ MCP bằng Python), `tests/`, `build.ps1`, `run_tests*.ps1` |
| `texthub_s6/` | Đóng gói: `dong_goi.ps1` (dựng bundle), `dong_goi_kuro.py` (lắp gói Kuro), `src/About.cs`, `package/` (tài liệu, `cai_dat.ps1`), `kuro/` (phần riêng cho Kuro), `tests/`, `VERSION` |
| `texthub_s7/` | Tập lệnh lái giao diện để thử bảng: `ui/drive.ps1`, `ui/uia.ps1` |
| `bao_cao/` | Báo cáo từng giai đoạn (`KetQua_*.md`) |

## Dựng lại (cần máy có AutoCAD 2020 và .NET Framework 4.x)

1. Chép các thư mục `texthub_s1`, `texthub_s5`, `texthub_s6`, `texthub_s7` vào CÙNG một thư mục cha (các tập lệnh tìm nhau theo tên anh em).
2. Đường dẫn AutoCAD trong `dong_goi.ps1` và `build.ps1` (biến `$ac`) trỏ tới thư mục cài AutoCAD; sửa nếu máy khác. Trình dịch dùng `csc.exe` của .NET Framework 4 (C# 5: không dùng `?.`, `$""`, `nameof`).
3. Dựng và đóng gói: chạy `texthub_s6\dong_goi.ps1`, sau đó `python texthub_s6\dong_goi_kuro.py`.
4. `dong_goi_kuro.py` lấy kho font từ `..\..\05-ThuVien\06-Kho-Font` (tương đối với `texthub_s6`). Máy khác: đặt biến `KHO` ở đầu tệp về thư mục kho font của máy đó, hoặc dùng bản đã nằm sẵn trong gói (`payload/KhoFont`).
5. Hỗ trợ AutoCAD khác 2020: xem `references/DA_PHIEN_BAN.md`.

Kiểm thử: `texthub_s1` (`tests/CoreTests.cs`), `texthub_s5\tests` (cần AutoCAD hoặc `accoreconsole`), `texthub_s6\tests` (`kuro_setup_test.py` chạy được trên mọi máy có Python, không đụng máy thật).
