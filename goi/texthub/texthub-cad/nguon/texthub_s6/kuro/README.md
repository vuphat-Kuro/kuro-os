# Gói `texthub` cho Kuro (PKTTC TextHub)

Gói đổi chữ tiếng Việt cũ (TCVN3, VNI) sang Unicode trong AutoCAD. Gồm plugin AutoCAD (bảng `PKTEXTUI`, menu KTTC, cổng cho trợ lý), skill hướng dẫn Kuro dùng, và công cụ kiểm tra trạng thái, cài, gỡ. Tự chứa, chỉ cần Python 3 (thư viện chuẩn), không cần `pip`.

## Cấu trúc (theo quy ước `goi/` của Kuro)

```
texthub/
  goi.json                      ten, mo_ta, skill, pip=[], import=[] (+ phien_ban, kiem_tra: khoa bo sung)
  mcp.example.json              mẫu khai báo MCP (tùy chọn, nếu muốn Kuro gọi qua MCP thay vì script)
  README.md                     tệp này
  CHANGELOG.md                  lịch sử phiên bản
  texthub-cad/                  = giá trị "skill" trong goi.json
    SKILL.md                    khi nào dùng, quy trình, luật cứng
    scripts/
      texthub_setup.py          status | install | uninstall | fontstore | fonts-install  (in JSON)
      texthub_cad.py            gọi cổng TextHub: ping, scan, plan.create, plan.apply...  (in JSON)
      pkttc_client.py           thư viện nối cổng (named pipe)
      pkttc_mcp.py              máy chủ MCP stdio (11 công cụ pkttc_*)
    payload/
      PKTTC.TextHub.bundle/     plugin AutoCAD (DLL, PackageContents.xml, MANIFEST.txt, tài liệu)
        Contents/Fonts/         SHX Unicode (uv-abc, 3T-Unicode, VN_UNI...) AutoCAD tự nhận qua SupportPath
      KhoFont/                  kho font đầy đủ (SHX, TTF gồm ARIALUNI.ttf, ZTrungTen): 361 tệp, ~41 MB
      cai_dat.ps1               cài tay bằng PowerShell (dự phòng)
      VERSION
    references/                 HUONG_DAN_SU_DUNG.md, CAI_DAT_TAY.md, CONG_KURO.md, DA_PHIEN_BAN.md, KHO_FONT.md
    nguon/                      mã nguồn đầy đủ (C#, Python, PowerShell, kiểm thử) để dựng lại: xem nguon/README.md
```

## Tích hợp vào Kuro

1. Chép cả thư mục `texthub` vào `C:\Kuro-os\Kuro\goi\texthub`.
2. `.venv\Scripts\python server\goi.py cai texthub` (hoặc nói với Kuro "cài gói TextHub"). Việc này chép skill vào brain; KHÔNG cài plugin vào AutoCAD. Plugin cài ở bước dùng đầu tiên, do Kuro chạy `texthub_setup.py install` khi người dùng đồng ý.
3. Thử từ dòng lệnh (không cần Kuro): `python goi\texthub\texthub-cad\scripts\texthub_setup.py status`.

## Hiển thị "danh sách công cụ và trạng thái cài"

`goi.py list` hiện chỉ biết skill đã chép vào brain hay chưa. Trạng thái THẬT (plugin đã cài vào AutoCAD, phiên bản, có bản mới, bản AutoCAD có được hỗ trợ không) lấy từ `texthub_setup.py status`, in JSON, ví dụ:

```json
{"id": "texthub", "phien_ban_goi": "0.9.3", "trang_thai": "da_cai",
 "autocad": [{"series": "R23.1", "ten": "AutoCAD 2020 - English", "ho_tro": true}],
 "cai_dat": {"phien_ban": "0.9.3"}, "goi_y": [], "thong_bao": "Da cai ban 0.9.3."}
```

`trang_thai`: `chua_cai`, `da_cai`, `co_ban_moi`, `da_cai_ban_moi_hon`, `khong_ho_tro`, `khong_co_autocad`, `loi`. `goi_y` liệt kê việc nên làm (`install`, `fontstore`). `goi.json` có khóa bổ sung `kiem_tra` trỏ đúng lệnh này: để màn hình công cụ của Kuro gọi lệnh đó cho từng gói có khóa `kiem_tra` rồi hiện cột "trạng thái" và nút Cài/Cập nhật/Gỡ (gọi `install`, `uninstall`). Phần hiển thị này CHƯA có trong Kuro: `server/goi.py` hiện bỏ qua khóa lạ. Cần bổ sung bên Kuro.

## Nhiều bản AutoCAD

Bundle khai báo bản AutoCAD hỗ trợ trong `PackageContents.xml` (`RuntimeRequirements`: `SeriesMin`, `SeriesMax`). Hiện chỉ **AutoCAD 2020 (R23.1)**. `texthub_setup.py` đọc khai báo đó, so với các bản AutoCAD cài trên máy (registry), và báo rõ bản nào chưa hỗ trợ; nó từ chối cài khi không có bản nào được hỗ trợ. Muốn thêm bản khác phải dựng thêm DLL và khai thêm thành phần: xem `texthub-cad/references/DA_PHIEN_BAN.md`.

## Ràng buộc cần biết

- Kuro và AutoCAD chạy trên CÙNG máy Windows và cùng tài khoản người dùng (cổng là named pipe cục bộ, chỉ cho đúng tài khoản).
- Plugin cài vào `%APPDATA%\Autodesk\ApplicationPlugins` của từng người dùng, không cần admin. `install` chép thêm kho font vào `%LOCALAPPDATA%\PKTTC\KhoFont`. Chỉ lệnh `fonts-install` (cài Arial Unicode MS cho người dùng hiện tại) ghi registry HKCU. AutoCAD đang mở thì không cài/cập nhật/gỡ được (DLL đang dùng): bảo người dùng lưu và đóng AutoCAD.
- Mọi thao tác ghi vào bản vẽ cần người dùng bấm Yes trong hộp thoại AutoCAD; có sao lưu `_backup` và hoàn tác bằng `U`.
- Kho font nằm trong gói (`payload/KhoFont`) cùng SHX Unicode trong bundle. `ARIALUNI.ttf` (Arial Unicode MS, 23 MB) thuộc bản quyền Microsoft Office: chỉ cài trên máy có giấy phép; xem `texthub-cad/references/KHO_FONT.md` trước khi phát gói ra ngoài tổ chức.
- DLL chưa ký số: bản AutoCAD mới có thể hỏi trước khi nạp.
