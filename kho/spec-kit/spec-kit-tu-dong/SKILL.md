---
name: spec-kit-tu-dong
description: Tự động dùng GitHub Spec Kit (phát triển theo đặc tả - spec-driven) khi người dùng BẮT ĐẦU một dự án lớn - viết phần mềm, ứng dụng, web, công cụ nhiều tệp, tính năng lớn, hoặc một dự án xây dựng lớn (bộ hồ sơ thiết kế thi công, hồ sơ dự thầu, dự toán công trình, hệ thống quản lý dự án). Dùng khi người dùng nói "làm dự án", "viết phần mềm", "xây dựng ứng dụng", "làm bộ hồ sơ", "dự án mới", "code cho tôi một hệ thống...". KHÔNG dùng cho việc nhỏ - sửa một lỗi, sửa một tờ bản vẽ, viết một script ngắn, hỏi đáp - hoặc khi người dùng nói "làm nhanh", "không cần spec".
---

# Spec Kit tự động

Người dùng muốn mọi dự án lớn đi theo quy trình Spec Kit: **đặc tả trước, rồi kế hoạch, rồi danh sách việc,
rồi mới làm**. Người dùng đọc tiếng Anh kém: viết mọi tài liệu đặc tả, kế hoạch, danh sách việc bằng **tiếng Việt**
và giải thích từng bước bằng tiếng Việt. Lệnh `specify` đã cài sẵn (trong `~/.local/bin`).

Skill này thay cho `superpowers:brainstorming` và `superpowers:writing-plans` ở các dự án lớn: không chạy song song
hai quy trình lập kế hoạch.

## Bước 0. Báo và khởi tạo

1. Báo người dùng một câu: "Dự án này lớn, em dùng quy trình Spec Kit: đặc tả, kế hoạch, danh sách việc rồi mới làm."
2. Nếu thư mục dự án chưa có `.specify/`, khởi tạo (an toàn trên thư mục đã có tệp: không ghi đè tệp nào, không tạo git):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"; specify init --here --force --non-interactive --integration claude
   ```
   Lệnh tạo các skill `speckit-*` trong `.claude/skills/` của dự án. Phiên đang mở chưa thấy chúng: đọc thẳng
   `.claude/skills/speckit-<bước>/SKILL.md` và làm theo, phiên sau mới gọi được bằng `/speckit-<bước>`.

## Các bước (mỗi bước xong thì dừng, tóm tắt bằng tiếng Việt, chờ người dùng duyệt)

| Bước | Skill | Ra gì |
|---|---|---|
| 1. Nguyên tắc dự án (một lần cho mỗi dự án) | `speckit-constitution` | `.specify/memory/constitution.md` |
| 2. Đặc tả: làm gì, cho ai, vì sao | `speckit-specify` | `specs/<số>-<tên>/spec.md` |
| 3. Hỏi lại chỗ mơ hồ (nên làm) | `speckit-clarify` | cập nhật spec.md |
| 4. Kế hoạch kỹ thuật | `speckit-plan` | `plan.md` và tài liệu kèm |
| 5. Danh sách việc | `speckit-tasks` | `tasks.md` |
| 6. Soát nhất quán (nên làm) | `speckit-analyze` | báo cáo |
| 7. Làm theo danh sách việc | `speckit-implement` | mã nguồn hoặc sản phẩm |
| 8. Soát đến khi khớp đặc tả | `speckit-converge` | lặp 7-8 đến khi báo `Converged` |

Người dùng nói "tự làm hết" thì đi liền các bước, chỉ dừng khi cần thông tin.

## Dự án xây dựng (không phải phần mềm)

Mẫu của Spec Kit viết cho phần mềm; đổi nghĩa khi điền:
- **Nguyên tắc** = tiêu chuẩn áp dụng (TCVN, QCVN), quy cách hồ sơ, phông chữ, khổ giấy, đơn vị.
- **Đặc tả** = yêu cầu công trình: quy mô, số tầng, công năng, chủ đầu tư cần gì, phạm vi hồ sơ.
- **Kế hoạch** = chia bộ môn (kiến trúc, kết cấu, cơ điện, dự toán) và skill thực hiện từng phần
  (ví dụ `vn-autocad-skill:vn-quy-trinh-ho-so`, `vn-kien-truc`, `vn-ket-cau`, `vn-du-toan`).
- **Danh sách việc** = danh sách tờ bản vẽ, bảng tính, bảng dự toán cần làm, theo thứ tự phụ thuộc.
- **Làm** = gọi đúng skill chuyên ngành cho từng việc; **soát** = các skill soát bản vẽ, đối chiếu với đặc tả.

Repo gốc đã kiểm tra an toàn: `E:/0.Code/Repo github/spec-kit` (tài liệu chi tiết: `spec-driven.md`, `docs/`).
