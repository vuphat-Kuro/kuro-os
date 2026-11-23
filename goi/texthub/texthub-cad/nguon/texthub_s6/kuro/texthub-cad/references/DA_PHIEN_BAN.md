# Hỗ trợ nhiều bản AutoCAD

## Hiện trạng

DLL `Pkttc.TextHub.dll` dựng bằng API của AutoCAD 2020 (R23.1, .NET Framework 4.7/4.8) và chỉ kiểm thử trên bản đó.
`PackageContents.xml` khai `SeriesMin=SeriesMax=R23.1`, nên AutoCAD chỉ nạp plugin ở bản 2020. `texthub_setup.py status` báo các bản khác là `khong_ho_tro`.
Autodesk không cam kết một DLL .NET chạy được mọi bản; chưa có bằng chứng DLL này chạy được trên bản khác. [CHƯA KIỂM TRA]

## Cách thêm một bản AutoCAD

Một bundle chứa được nhiều thành phần, AutoCAD tự chọn thành phần theo bản đang chạy. Mỗi thành phần:

```xml
<Components Description="AutoCAD 2023-2024">
  <RuntimeRequirements OS="Win64" Platform="AutoCAD" SeriesMin="R24.2" SeriesMax="R24.3" SupportPath="./Contents/Windows2023" />
  <ComponentEntry AppName="PKTTC.TextHub" Version="..." ModuleName="./Contents/Windows2023/Pkttc.TextHub.dll" LoadOnAutoCADStartup="true">
    <Commands GroupName="PKTTC_TEXTHUB"> ... </Commands>
  </ComponentEntry>
</Components>
```

Các bước:
1. Dựng DLL mới tham chiếu `acmgd.dll`, `acdbmgd.dll`, `accoremgd.dll` của đúng bản đó (từ thư mục cài AutoCAD hoặc ObjectARX SDK của bản đó).
2. Đặt vào `Contents/Windows<nam>/`, thêm thành phần vào `PackageContents.xml`, sinh lại `MANIFEST.txt` (SHA-256 mọi tệp).
3. Đóng gói lại. `texthub_setup.py` tự đọc `RuntimeRequirements` nên không cần sửa mã để biết bản mới được hỗ trợ.
4. Kiểm thử trên máy có bản đó (xem bảng bên dưới) trước khi khai `SeriesMax`.

Ánh xạ năm sang mã bản (để điền `SeriesMin`, `SeriesMax`): 2018 = R22.0, 2019 = R23.0, 2020 = R23.1, 2021 = R24.0, 2022 = R24.1, 2023 = R24.2, 2024 = R24.3, 2025 = R25.0, 2026 = R25.1. [CẦN KIỂM TRA với từng bản; registry ghi đúng mã]

## Hai nhóm dựng

- **AutoCAD 2018 đến 2024:** .NET Framework 4.x. Dựng `net48`.
- **AutoCAD 2025 trở lên:** .NET 8. Phải dựng riêng `net8.0-windows`; mã hiện dùng `JavaScriptSerializer` (System.Web.Extensions) không có trong .NET 8, cần đổi sang `System.Text.Json`. `PaletteSet`, WinForms và `dynamic` dùng được.
- AutoCAD LT, BricsCAD, ZWCAD: không nạp được plugin .NET của AutoCAD.

## Bảng kiểm thử cho mỗi bản

1. Cài bằng `texthub_setup.py install`, mở AutoCAD: plugin tự nạp, không hỏi gì (hoặc ghi lại câu hỏi).
2. `PKTEXTABOUT` báo đúng phiên bản; menu KTTC > Text > Convert Font có 15 dòng; `PKTEXTUI` mở bảng.
3. Trên bản vẽ mẫu: `PKTEXTSCAN`, `PKTEXTPLAN`, `PKTEXTFIX` (YES), kiểm `U` hoàn tác trả đúng nguyên trạng.
4. Cổng: `PKTEXTBRIDGE` rồi `texthub_cad.py ping`, `scan`, `plan.create`, `plan.apply` (bấm Yes).
5. Gỡ bằng `texthub_setup.py uninstall`, mở lại AutoCAD: không còn menu KTTC, không lỗi.
