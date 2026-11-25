---
name: chili3d-cad
description: "CHỈ dùng khi người dùng muốn dựng, sửa, đo hoặc chụp mô hình 3D trong Chili3D (CAD 3D chạy trên trình duyệt), hoặc hỏi cầu nối Chili3D đã cài chưa. Không dùng cho bản vẽ 2D DXF/DWG và không dùng cho mô hình BIM/IFC."
---

# Chili3D qua cầu nối MCP (AGPL-3.0)

Web app: https://chili3d.com (mã https://github.com/xiangechen/chili3d). Cầu nối: `@chili3d/mcp` ghim `0.1.0`, cài ở `state/chili3d-mcp`, cần Node.js 20+. Kuro không kèm mã Chili3D.

## Bước 0 - Cầu nối MCP đã cài chưa
Trong Cài đặt > Plugins, hàng MCP của Chili3D: nút Cài MCP (npm, dưới 1 phút) rồi mở phiên chat mới. Chưa cài thì tool `chili3d_*` không có: báo người dùng bấm nút đó. Phần mềm = trang web, không cần cài.

## Bước 1 - Mở trang và nối
1. Gọi tool MCP `chili3d_open`: khởi động cầu nối (chỉ nghe 127.0.0.1:17373) và mở trang. Người dùng để tab Chili3D ở phía trước (tab nền bị trình duyệt làm chậm).
2. `chili3d_status` trả `connected: true` thì tool của trang xuất hiện dạng `chili3d_<tool>` (`run_program`, `get_document_state`, `capture_screenshot`, `load_skill`...). Chưa thấy tool: khởi động lại phiên chat một lần.
3. Trang trống chưa có tài liệu: gọi `chili3d_new_document` trước khi dựng.

## Lưu ý
- Tài liệu nằm trong trình duyệt của người dùng; báo họ tự lưu/xuất. Một trang tại một thời điểm.
- Trang tải từ chili3d.com (bên thứ ba). Không dán dữ liệu mật của công ty vào trang đó.
- Không bấm/duyệt thay người dùng ngoài các tool MCP. Mọi con số kỹ thuật vẫn theo luật số liệu của Kuro.
