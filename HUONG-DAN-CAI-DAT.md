# HƯỚNG DẪN CÀI ĐẶT KURO OS CHO MÁY TÍNH MỚI (DÀNH CHO NGƯỜI DÙNG LOWTECH)

Tài liệu này hướng dẫn chi tiết từng bước dành riêng cho các kỹ sư công trường, quản lý chất lượng (QC/QS), hồ sơ dự án muốn cài đặt trợ lý kỹ sư hạ tầng **Kuro OS** trên một máy tính Windows mới hoàn toàn mà không cần am hiểu sâu về công nghệ thông tin.

---

## BƯỚC 1: TẢI VÀ CÀI ĐẶT 3 PHẦN MỀM CƠ BẢN

Trước khi chạy Kuro OS, máy tính cần có 3 công cụ nền tảng sau. Bạn chỉ cần tải và bấm **Next** theo hướng dẫn:

### 1. Cài đặt Python (Môi trường tính toán)
- **Link tải chính thức:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Phiên bản khuyến nghị:** Python 3.12 hoặc Python 3.13 (bấm nút vàng *Download Python 3.13.x*).
- **LƯU Ý CỰC KỲ QUAN TRỌNG:** Khi mở file cài đặt lên, ở màn hình đầu tiên, bạn **BẮT BUỘC TÍCH VÀO Ô TRÒN**:
  - `[x] Add python.exe to PATH` (nằm ở mép dưới cùng cửa sổ).
  - Sau đó mới bấm **Install Now** -> chờ chạy xong -> bấm **Close**.

### 2. Cài đặt Git (Công cụ tải và cập nhật tự động)
- **Link tải chính thức:** [https://git-scm.com/download/win](https://git-scm.com/download/win)
- **Cách cài:** Tải bản *64-bit Git for Windows Setup*, mở file cài đặt lên và bấm **Next** liên tục cho đến khi hoàn tất -> bấm **Finish**.

### 3. Cài đặt Node.js (Bộ máy chạy nền Claude Code)
- **Link tải chính thức:** [https://nodejs.org/](https://nodejs.org/)
- **Cách cài:** Chọn bản **LTS (Recommended for Most Users)**, tải về mở file và bấm **Next** liên tục đến khi hoàn tất.
- Sau khi cài xong Node.js:
  - Bấm phím `Windows` trên bàn phím, gõ `powershell` rồi nhấn `Enter`.
  - Dán dòng lệnh sau vào cửa sổ xanh rồi nhấn `Enter`:
    ```powershell
    npm install -g @anthropic-ai/claude-code
    ```
  - Chờ máy chạy khoảng 10-30 giây khi hiện chữ thông báo xong thì đóng cửa sổ lại.

*(Lưu ý thêm: Windows 10 và Windows 11 hiện nay đều đã có sẵn trình duyệt Microsoft Edge WebView2. Nếu bạn dùng Windows cũ hơn mà mở ứng dụng bị báo thiếu WebView2 thì tải miễn phí tại [Microsoft Edge WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)).*

---

## BƯỚC 2: TẢI KURO OS VỀ MÁY TÍNH

Khuyến nghị tạo thư mục cài đặt tại đường dẫn: `C:\Kuro-os\Kuro` để hệ thống hoạt động ổn định nhất.

### Cách 1: Tải tự động bằng lệnh Git (Nhanh nhất)
1. Bấm phím `Windows`, gõ `cmd` hoặc `powershell`, nhấn `Enter`.
2. Dán dòng lệnh sau và nhấn `Enter`:
   ```powershell
   git clone https://github.com/vuphat-Kuro/kuro-os.git C:\Kuro-os\Kuro
   ```
3. Chờ vài giây khi máy tải xong thư mục Kuro về ổ C.

### Cách 2: Tải file nén ZIP (Thao tác chuột)
1. Mở trình duyệt web truy cập: [https://github.com/vuphat-Kuro/kuro-os](https://github.com/vuphat-Kuro/kuro-os)
2. Bấm vào nút màu xanh lá cây **Code** ở góc phải -> chọn **Download ZIP**.
3. Mở file nén vừa tải về, giải nén toàn bộ nội dung vào thư mục: `C:\Kuro-os\Kuro`.

---

## BƯỚC 3: CÀI ĐẶT TỰ ĐỘNG BẰNG 1 CÚ NHẤP CHUỘT

1. Mở ổ đĩa `C:`, vào thư mục `Kuro-os`, rồi vào thư mục `Kuro` (đường dẫn: `C:\Kuro-os\Kuro`).
2. Tìm tệp có tên là **`setup.bat`** (hoặc `setup` có biểu tượng hai bánh răng).
3. **Nhấp đúp chuột (Double click)** vào tệp `setup.bat`.
4. Một cửa sổ màu đen sẽ tự động xuất hiện và làm toàn bộ các công việc:
   - Tự tạo môi trường ảo Python biệt lập (`.venv`).
   - Tự động tải và cài đặt toàn bộ thư viện kỹ thuật hạ tầng (tính toán, xử lý Excel, Word, PDF...).
   - Tự động sinh file cấu hình `.env`.
   - Tự động tạo biểu tượng lối tắt **Kuro OS** ngoài màn hình chính (Desktop) và Start Menu.
5. Khi màn hình đen hiện chữ `Xong. Bam dup bieu tuong KURO tren man hinh chinh... Press any key to continue . . .`, bạn nhấn phím bất kỳ để tắt cửa sổ.

---

## BƯỚC 4: KHỞI CHẠY VÀ KẾT NỐI AI LẦN ĐẦU

1. Ra ngoài màn hình chính máy tính (Desktop), bạn sẽ thấy biểu tượng **Kuro OS** hình linh vật cú công trình đeo kính bảo hộ.
2. **Nhấp đúp chuột vào biểu tượng Kuro OS**: Ứng dụng sẽ khởi động dưới dạng cửa sổ phần mềm máy tính chuyên dụng (Native App).
3. **Cấu hình mô hình AI**:
   - Ở góc dưới hoặc trong bảng cài đặt, bạn chọn nhà cung cấp AI muốn dùng (Google Antigravity, Claude Code, OpenAI, OpenRouter, DeepSeek...).
   - Nếu bạn dùng tài khoản Claude Code cá nhân: Mở PowerShell chạy `claude auth login` để đăng nhập tài khoản.
   - Nếu dùng API Key (Gemini / DeepSeek / OpenAI): Điền mã khoá API Key vào file `.env` hoặc trên hộp thoại cài đặt.
4. Bắt đầu làm việc: Nhập câu hỏi, kéo thả bản vẽ, file bảng tính dự toán, hồ sơ KCS vào khung chat để Kuro hỗ trợ.

---

## HƯỚNG DẪN CẬP NHẬT PHIÊN BẢN MỚI SAU NÀY

Mỗi khi hệ thống có tính năng mới (ví dụ nâng cấp panel ngữ cảnh, thêm agent chuyên môn...):
- **Cách 1:** Ngay trên thanh điều hướng Kuro OS, bấm vào biểu tượng tên lửa "Phiên bản & Cập nhật" -> bấm **Kiểm tra bản mới trên GitHub** -> bấm **Cập nhật ngay**.
- **Cách 2:** Vào thư mục `C:\Kuro-os\Kuro`, nhấp đúp vào tệp **`cap-nhat.bat`**. Ứng dụng sẽ tự động tải các điều chỉnh mới nhất về máy trong vài giây.

---

## CÁC TỆP TIỆN ÍCH DỄ DÙNG TRONG THƯ MỤC KURO

- **`kuro.vbs`** hoặc Icon **Kuro OS** ngoài Desktop: Mở ứng dụng chạy êm ái, không hiện cửa sổ đen.
- **`tat-kuro.bat`**: Tắt toàn bộ Kuro khi không dùng để giải phóng bộ nhớ RAM máy tính.
- **`cap-nhat.bat`**: Cập nhật nhanh mã nguồn mới nhất từ GitHub.
- **`setup.bat`**: Chạy lại cài đặt nếu bạn lỡ xoá môi trường hoặc cài thêm thư viện mới.
