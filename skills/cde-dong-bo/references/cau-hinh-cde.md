# Cấu hình kết nối CDE

## Phần 1 - ACC / BIM 360 (Autodesk Platform Services)

### Lấy khóa

1. Vào `aps.autodesk.com` → đăng nhập → **Create App**
2. Chọn kiểu **Server-to-Server** (token 2-legged) cho việc chạy script tự động
3. Ghi lại **Client ID** và **Client Secret**
4. **Bước hay bị bỏ sót:** vào ACC → *Account Admin* → *Custom Integrations* →
   *Add custom integration* → dán Client ID → chọn dự án và quyền

Thiếu bước 4 thì token lấy được nhưng mọi lệnh trả về 403. Đây là nguyên nhân
phổ biến nhất khi "code đúng mà vẫn không chạy".

### Khai báo

PowerShell, chỉ có tác dụng trong cửa sổ đang mở:
```powershell
$env:APS_CLIENT_ID     = "xxxxx"
$env:APS_CLIENT_SECRET = "yyyyy"
```

Đặt lâu dài (một lần, áp dụng mọi cửa sổ sau đó):
```powershell
[Environment]::SetEnvironmentVariable("APS_CLIENT_ID", "xxxxx", "User")
```

Hoặc tạo file `.env` cùng thư mục chạy lệnh:
```
APS_CLIENT_ID=xxxxx
APS_CLIENT_SECRET=yyyyy
```
Thêm ngay `.env` vào `.gitignore`. Khóa lọt lên GitHub public thường bị quét và
lạm dụng trong vòng vài phút.

### Khi cần token 3-legged

Token 2-legged chạy dưới danh nghĩa ứng dụng. Một số thao tác (ví dụ ghi vào
thư mục mà chỉ tài khoản người dùng có quyền) cần token 3-legged - token đại
diện cho chính người dùng. Lấy được rồi thì đặt vào `APS_TOKEN`, công cụ sẽ
dùng luôn thay vì tự xin token mới.

Token 3-legged hết hạn sau khoảng một giờ. Với việc chạy dài, cần luồng refresh
token - khi tới lúc đó thì dựng riêng.

### Phạm vi quyền (scope)

Mặc định: `data:read data:write data:create account:read`. Đổi bằng biến
`APS_SCOPE`. Nguyên tắc: xin đúng quyền cần dùng, không xin thừa.

---

## Phần 2 - CDE nội bộ có REST API

Dùng cho nền tảng tự phát triển hoặc phần mềm quản lý dự án của đơn vị.

### Cách dò endpoint - làm một lần cho mỗi hệ thống

1. Mở CDE trên Chrome, đăng nhập
2. F12 → tab **Network** → lọc **Fetch/XHR**
3. Thao tác một lần bằng tay (đăng nhập, mở danh sách tài liệu, tải một file lên)
4. Xem từng request: đường dẫn, phương thức, phần thân, phần trả về
5. Chép các thông tin đó vào file cấu hình dưới đây

Với hệ thống chạy .NET, thường có sẵn `/swagger` hoặc `/swagger/index.html` mô
tả toàn bộ API - mở thử trước khi ngồi dò tay.

### Mẫu file cấu hình

```json
{
  "ten": "CDE nội bộ dự án X",
  "goc": "https://ten-mien.vn/api",

  "dang_nhap": {
    "duong_dan": "/auth/login",
    "kieu": "json",
    "truong": {
      "username": "$ENV:CDE_USER",
      "password": "$ENV:CDE_PASS"
    },
    "duong_token": "data.accessToken"
  },

  "danh_sach": {
    "duong_dan": "/documents",
    "duong_ket_qua": "data.items"
  },

  "tai_len": {
    "duong_dan": "/documents/upload",
    "truong_file": "file"
  }
}
```

Giải thích vài chỗ:

- `$ENV:TEN_BIEN` - lấy giá trị từ biến môi trường. **Không viết mật khẩu thẳng
  vào file này.**
- `duong_token` - đường đi tới token trong phần trả về. Nếu máy chủ trả
  `{"data": {"accessToken": "..."}}` thì ghi `data.accessToken`.
- `duong_ket_qua` - đường tới mảng dữ liệu trong phần trả về. Bỏ trống nếu máy
  chủ trả thẳng một mảng.

### Cách dùng

```powershell
$env:CDE_USER = "tai.khoan"
$env:CDE_PASS = "..."
python cde.py tai-len --nguon rest --cau-hinh cde-noi-bo.json --vao "hoso/" --thu
```

Luôn chạy `--thu` lần đầu.

### Khi CDE dùng cách xác thực khác

- **API key trong header** - bỏ phần `dang_nhap`, hệ thống chưa hỗ trợ header
  tùy ý sẵn; cần thêm vài dòng vào `RestChung.dau`. Việc nhỏ.
- **OAuth2 / SSO doanh nghiệp** - luồng phức tạp hơn, cần dựng riêng theo tài
  liệu của nhà cung cấp.
- **Chỉ có giao diện web, không có API** - cân nhắc dùng Claude in Chrome để
  thao tác trên trình duyệt, hoặc đề nghị bên phát triển mở API. Tự động hóa
  bằng cách mô phỏng thao tác trình duyệt rất dễ vỡ khi giao diện đổi.

---

## Phần 3 - Trimble Connect

Có REST API riêng tại `app.connect.trimble.com`, cơ chế xác thực dùng Trimble
Identity. Cấu trúc gần giống mẫu REST ở trên: đăng nhập lấy token, rồi gọi các
endpoint project/folder/file. Khi cần dùng, tra tài liệu chính thức của Trimble
rồi điền vào file cấu hình theo mẫu.

---

## Kiểm tra trước khi chạy hàng loạt

1. `python cde.py du-an` - có ra danh sách dự án không? Không ra thì vấn đề ở
   khóa hoặc quyền, chưa phải ở lệnh đang định chạy.
2. `python cde.py cay --du-an <mã>` - có duyệt được thư mục không?
3. Chạy lệnh thật với `--thu` - xem danh sách file sẽ động vào.
4. Chạy thật với vài file trước, kiểm tra kết quả trên giao diện web.
5. Rồi mới chạy toàn bộ.
