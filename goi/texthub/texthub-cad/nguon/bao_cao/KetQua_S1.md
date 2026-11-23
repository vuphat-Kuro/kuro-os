# Kết quả S1 - lõi Core của TextHub

Trạng thái: ĐẠT, chờ anh duyệt. Ngày: 2026-11-20. Thư mục: `QLDA/99-Temp/texthub_s1/`.

## Kết luận

Lõi `Pkttc.Text.Core` (C# 5, không phụ thuộc AutoCAD) dựng được và qua 122 kiểm thử, 0 lỗi: bảng mã, đổi mã hai chiều, tách MTEXT, nhận dạng bảng mã, quy tắc font. Chưa chạy trong AutoCAD (đó là việc của S2).

## Phát hiện quan trọng: bảng VNI của LISP v2.6 sai 17 mục

Đối chiếu 3 nguồn độc lập cho bảng mã (`tools/extract_tables.py`, kết quả ở `tools/doi_chieu.txt`):

| Nguồn | Kết quả |
|---|---|
| Quy tắc sinh (NFC) | 134 chữ Việt dựng sẵn; BVC `CF` có đúng 134 chữ này |
| TCVN3: LISP v2.6 và BVC | 74 mục chung, **0 khác biệt** |
| VNI: LISP v2.6 và BVC | 117 mục chung, **17 khác biệt** |
| VNI: AJS VFCC (chuỗi literal) | Cùng giá trị với BVC ở các cặp A, E, O, U, Y có dấu (ví dụ `AÚ aú`, `AÜ aü`, `ÔÙ ôù`) |

17 mục sai của LISP v2.6 (bản VNI Unicode→VNI và VNI→Unicode): `Ã`, `ì`, `í`, `ĩ`, `ỉ`, `ị`, `ỵ`, `Ẳ`, `ẳ`, `Ẵ`, `ẵ`, `Ặ`, `ặ`, `Ớ`, `ớ`, `Ờ`, `ờ` (ví dụ `ớ` và `ờ` bị đảo dấu sắc và huyền; `ẳ ẵ ặ` bị đổi sang chữ `e`). Giá trị đúng được kiểm bằng chuỗi vàng trong `tests/CoreTests.cs` (hàm `TestVniKnownGood`), viết theo hiểu biết về bảng VNI chuẩn, không sinh từ tệp dữ liệu. Đối chiếu thêm với tài liệu chuẩn VNI chính thức vẫn nên làm [CẦN KIỂM TRA].

Hệ quả: LISP v2.6 đổi sai các chữ này nếu bản vẽ dùng VNI. Đây là lý do bổ sung vào danh sách lỗi của P0.

## Đã làm

| Tệp | Nội dung |
|---|---|
| `tools/extract_tables.py`, `tools/build_charsets.py` | Rút bảng từ LISP v2.6 và BVC, đối chiếu, sinh `data/charsets.csv` và `src/Core/CharsetData.g.cs` |
| `data/charsets.csv` | 134 dòng: Unicode, byte TCVN3, cờ font HOA, chuỗi byte VNI, nguồn |
| `src/Core/Types.cs` | `Charset`, `ConversionResult`, `DetectionResult` |
| `src/Core/CharsetTables.cs` | Các bảng tra từ dữ liệu sinh |
| `src/Core/VietnameseConverter.cs` | TCVN3, VNI, Unicode hai chiều; trang ma 1252 và 1258 |
| `src/Core/CadEscapes.cs` | `\U+XXXX` và `%%nnn` |
| `src/Core/FontRules.cs` | Suy bảng mã và chữ HOA từ tên font |
| `src/Core/SyllableValidator.cs` | Kiểm âm tiết tiếng Việt hợp lệ để chấm điểm |
| `src/Core/CharsetDetector.cs` | Nhận dạng hai tầng (font rồi nội dung) kèm độ tin cậy |
| `src/Core/MTextTokenizer.cs` | Tách MTEXT, bảo đảm `Join(Tokenize(s)) == s` |
| `src/Core/MTextConverter.cs` | Đổi MTEXT và TEXT, chỉ đụng đoạn chữ, giữ mã định dạng |
| `tests/CoreTests.cs`, `build.ps1` | 122 kiểm thử, dựng và chạy bằng `csc.exe` |

## Kết quả kiểm thử (122 đạt, 0 lỗi)

- Bảng: 134 chữ, 74 byte TCVN3 (67 chữ thường và 7 chữ HOA không dấu thanh), 134 chuỗi VNI khác nhau.
- Vòng, trang mã 1252 và 1258: VNI 134/134; TCVN3 thường 74/74; TCVN3 font HOA 134/134. Nối liền 134 chữ qua VNI không nhầm ranh giới. 60 chữ HOA có dấu thanh được báo "không đổi được" khi đích là font thường (đúng bản chất TCVN3: loại chữ này chỉ có ở font HOA).
- Chuỗi vàng viết tay, độc lập với bảng: "Đà Nẵng" và "Việt Nam" bằng TCVN3 và VNI, "đường" bằng VNI.
- Tách MTEXT: 16 mẫu cố định và 20.000 chuỗi ngẫu nhiên, nối lại đều bằng chuỗi gốc; nhận đúng nhóm `{}`, `\f`, `\S`, `\P`, `\U+`.
- Nhận dạng: TCVN3 và VNI (có và không gợi ý font), Unicode, ASCII, tên đường mẫu.
- Đổi MTEXT: bỏ `\f` cũ, giữ `\P`, giữ `\fArial`; `%%189` thành `ẵ`; nội dung trong `\S`; font HOA cho chữ HOA; Unicode thành TCVN3 rồi về; xuất dạng `\U+XXXX`.

## Quyết định thiết kế (đã dùng trong mã)

1. Font HOA TCVN3 (`.VnTimeH`): mọi chữ dùng mã của chữ thường tương ứng và hiển thị thành chữ HOA; chuyển sang Unicode cho chữ HOA (theo quy ước của hai chương trình đối chiếu).
2. Đích là TCVN3 font thường: chữ HOA có dấu thanh không biểu diễn được, trả danh sách `Unmapped` để lớp trên quyết định (chuyển font HOA hoặc báo người dùng). Không tự đoán.
3. Nhận dạng dùng tên font thật của Style, không dùng tên Style (sửa lỗi của LISP v2.6).
4. Độ tin cậy: `điểm tốt nhất - 0,5 × điểm thứ hai`; dưới 0,6 thì giữ nguyên và ghi là không chắc, không đoán.
5. Chuỗi có ký tự không mã hóa được trong trang mã ANSI của bản vẽ (ví dụ `ạ` ở trang mã 1252) được coi là Unicode với độ tin cậy 0,95.

## Hạn chế và việc chưa làm

- Bảng TCVN3 và VNI lấy từ sự trùng khớp của hai chương trình (LISP, BVC) cộng chuỗi vàng và chuỗi literal của VFCC; chưa đối chiếu với văn bản chuẩn gốc TCVN 5712 hay tài liệu VNI chính thức [CẦN KIỂM TRA].
- Bộ kiểm âm tiết là quy tắc âm vị cơ bản, không phải từ điển. Chuỗi rất ngắn (một chữ) hay viết tắt kỹ thuật (BTCT, TP, Km) dễ có độ tin cậy thấp; khi đó Core giữ nguyên. Cần thử trên văn bản thật của phòng ở S2.
- Trang mã 1258 mới kiểm bằng vòng đổi, chưa có chuỗi vàng riêng.
- `ConversionResult.Unmapped` ở đường đổi hai bước (TCVN3 sang VNI) trộn vị trí của hai chuỗi trung gian; chỉ dùng số đếm, chưa dùng vị trí.
- Chưa có cấu hình quy tắc font bằng tệp JSON (đang là mã cứng trong `FontRules`).
- Chưa thử trong AutoCAD; Core chưa được đóng vào bundle.
- `csc.exe` Framework chỉ biên dịch C# 5; chưa thử Roslyn của SDK.

## Chạy lại

```powershell
powershell -File "C:\Users\KTTC CAU - NGHIA\javis-os\brains\Brain Default\QLDA\99-Temp\texthub_s1\build.ps1"
```
