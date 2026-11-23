# 06-Kho-Font - kho font gọn của phòng

Kho này là NGUỒN để đối chiếu và cài font khi bản vẽ thiếu font (PKTTC TextHub, lệnh `PKTEXTFONT`). Không phải thư mục AutoCAD tự nạp: muốn dùng phải cài (xem cuối).

## Gồm gì (bộ gọn ban đầu: 56 tệp, 2,9 MB; sau bổ sung 2026-11-23: 357 tệp, 17,2 MB, xem mục bổ sung bên dưới)

| Nhóm | Số tệp | Tiêu chí chọn |
|---|---|---|
| TrueType TCVN3: `.VnTime`, `.VnTimeH`, `.VnArial`, `.VnArialH`, `.VnArial Narrow`, `.VnArial NarrowH`, `.VnAvant`, `.VnAvantH` (thường, đậm, nghiêng, đậm nghiêng) | 28 | Có trong style hoặc mã `\f` của bản vẽ thật "Đà giáo xà mũ" (`.VnAvantH` 304 lần, `.VnArial NarrowH` 302, `.VnArialH` 53...) và các họ cùng bộ |
| TrueType VNI: `VNI-Times`, `VNI-Helve` (kèm biến thể) | 9 | Hai họ VNI phổ biến nhất |
| TrueType Unicode: `Be Vietnam Pro` và bản `H` (4 biến thể mỗi bản) | 8 | Có trong style bản vẽ; font Unicode miễn phí hợp quy định phòng |
| SHX Unicode (header `unifont`): `VN_UNI`, `uv-abc`, `3T-Unicode`, `ads civil`, `unicode` | 5 | `VN_UNI.shx` dùng 1.133 lần (nhiều nhất); các tệp còn lại có trong style bản vẽ |
| SHX TCVN3 (header `shapes`, 8 bit): `vntime`, `vntimeh`, `vn-abc`, `vnsimple` | 4 | `vn-abc` 168 lần, `vntime` trong style và mã `\F`; còn lại có trong style bản vẽ |
| SHX BigFont (header `bigfont`): `VN1`, `vns` | 2 | `VN1` đi cặp `vntime` (`\Fvntime,vn1`); `vns` có trong style bản vẽ |

Bảng mã SHX xác định từ header tệp (`AutoCAD-86 unifont` = Unicode, `shapes` = 8 bit, `bigfont` = BigFont), không đoán theo tên: ví dụ `uv-abc` và `VN_UNI` là Unicode dù tên gợi ý khác.

Danh sách chi tiết (tệp, họ font, bảng mã, lý do chọn) ở `_danh_sach.csv`.

## Bổ sung ngày 2026-11-23: từ kho `C:\Users\KTTC CAU - NGHIA\Downloads\Fonts`

Kho nay có 357 tệp font, 17,2 MB (trước đó 56 tệp). Đã chép thêm 301 tệp còn thiếu so với kho Downloads\Fonts (tệp gốc không bị đụng):

| Nhóm | Số tệp | Chỗ để |
|---|---|---|
| TrueType TCVN3 (họ `V...`, `Vn...`, `Vh...`) | 102 | `TTF\` |
| TrueType VNI | 35 | `TTF\` |
| TrueType khác (biển báo `Giaothong1`, `Giaothong2`, `UTM Neo Sans Intel`, `CourierTCVN3`...) | 7 | `TTF\` |
| SHX 8 bit TCVN3 (header `shapes`) | 132 | `SHX\` |
| SHX Unicode (header `unifont`) | 11 | `SHX\` |
| SHX BigFont | 10 | `SHX\` |
| SHX trùng khóa tra cứu với tệp khác nhưng nội dung khác (`VN______`, `VNCC_RMD`, `VNT_____`, `VNTIME__`) | 4 | `ZTrungTen\SHX\` |

- Khóa tra cứu của TextHub là tên bỏ dấu chấm, cách, gạch ngang và gạch dưới (ví dụ `VN-ABC.SHX` và `VN_ABC.SHX` cùng khóa `vnabc.shx`); khi trùng thì tệp được tìm thấy trước thắng. 4 tệp trên để trong `ZTrungTen` (xếp sau thư mục chính) để không che tệp đã có; muốn dùng tay thì cài như các tệp khác.
- Không ghi đè 7 tệp đã có cùng tên nhưng nội dung khác bản Downloads: `Vhelvcn.ttf`, `Vhelveb.ttf`, `Vhelvebi.ttf`, `Vhelvei.ttf`, `Vnarial.ttf`, `Vnarialb.ttf`, `Vntime.ttf` (giữ bản đã có trong kho; chưa so xem bản nào mới hơn).
- Không chép 19 tệp .shx không phải font SHX hợp lệ: `gothnib.shx`, `VN_ABC.SHX`, `VN_ABCH.SHX`, `VN_LITE.SHX`, `VNABC1.SHX`, `VNCC-ARI.SHX`, `VNCC-TIM.SHX`, `VNCC_ARI.SHX`, `VNCC_COM.SHX`, `VNCC_MNT.SHX`, `VNCC_RMC.SHX`, `VNCC_RMS.SHX`, `VNCC_RMT.SHX`, `VNCC_SCR.SHX`, `VNCC_SIM.SHX`, `VNCC_TIM.SHX`, `VNCC_TXT.SHX`, `VNCCARIA.SHX`, `VNL.SHX` (tệp toàn byte 0, tệp PostScript, tệp khóa AutoCAD hoặc dữ liệu thô). Không chép `VNSIMPLE.SHP` (mã nguồn, không phải font).
- Bảng mã SHX xác định từ header tệp; bảng mã TrueType suy từ tên họ font (`.Vn...` là TCVN3, `VNI-` là VNI), cột `khong ro` trong `_danh_sach.csv` nghĩa là chưa phân loại. Các dòng bổ sung trong `_danh_sach.csv` ghi lý do "Bo sung tu kho font Downloads\Fonts (2026-11-23)".
- Script thêm: `99-Temp\texthub_s6\kho_font_them.py <thu_muc_nguon> <kho> [--apply]` (mặc định chỉ xem, không ghi đè, kiểm header, kiểm trùng khóa).

## Font Unicode mặc định khi đổi chữ (2026-11-23)

Bảng PKTEXTUI chọn sẵn font đích: chữ ở font TrueType nguồn đổi sang **Arial Unicode MS**, chữ ở font SHX nguồn đổi sang **uv-abc.shx**. Ba font này được ghim đầu danh sách font đích: `Arial Unicode MS`, `uv-abc.shx`, `3T-Unicode.shx`.

- `TTF\ARIALUNI.ttf` (23 MB, họ "Arial Unicode MS") chép từ `C:\Windows\Fonts` của máy anh Nghĩa. Font này đi kèm Microsoft Office: dùng trong nội bộ các máy phòng đã có giấy phép Office; không phát tán ra ngoài phòng.
- Máy thiếu font này thì trong bảng PKTEXTUI, thẻ Đổi chữ có nút **Cài font đích thiếu từ kho** (cài cho người dùng hiện tại, hỏi xác nhận; cần mở lại AutoCAD để nhận font mới).
- `uv-abc.shx` và `3T-Unicode.shx` đã có sẵn trong `SHX\`. TextHub chưa tự thêm thư mục kho vào đường dẫn hỗ trợ của AutoCAD (Support File Search Path): thư mục `05-ThuVien\04-Fonts-SHX` của anh đã nằm trong đường dẫn đó.

## Không gồm (cố ý)

- Font hệ thống Windows (Arial, Times New Roman, Segoe UI...) và SHX đi kèm AutoCAD (`txt`, `romans`, `simplex`): luôn có sẵn trên máy CAD.
- Hơn 1.700 tệp font trang trí và biểu tượng trong thư viện cũ (`Fonts for Cad`, `Fonts for Windows`).

## Dùng với TextHub

Tệp `%LOCALAPPDATA%\PKTTC\fontstore.txt` trỏ tới thư mục này. `PKTEXTFONT` đối chiếu font bản vẽ với kho và sinh `cai_font.ps1`; script đó chỉ xem, và chỉ chép tệp khi bạn thêm `-Apply`.

Cài thủ công: SHX chép vào thư mục có trong Support File Search Path của AutoCAD (đã có `05-ThuVien\04-Fonts-SHX`); TrueType bấm phải tệp, chọn Install for current user.

## Tạo lại hoặc thêm font

`_tao_kho.ps1` chép lại các tệp còn thiếu từ máy nguồn (`%LOCALAPPDATA%\Microsoft\Windows\Fonts` và `Fonts` của AutoCAD). Thêm font: thêm một dòng vào danh sách trong script rồi chạy lại.
