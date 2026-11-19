"""Quản lý quy tắc Local Workspace cho các thư mục dự án trên máy người dùng (Kuro Standard).

Triết lý thiết kế:
- Người dùng chỉ cần quan tâm 2 việc: cung cấp tài liệu (01_TAI_LIEU) và nhận kết quả (03_KET_QUA).
- Mọi file kỹ thuật nội bộ (script Python, file trung gian, bản nháp) do Kuro tự quản lý trong 02_KURO_XU_LY.
- Quy tắc riêng (nếu dự án cần bổ sung) lưu gọn trong 1 file duy nhất `QUY_TAC_RIENG.md` ở gốc dự án.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

STANDARD_DIRS = ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA")
CUSTOM_RULES_FILE = "QUY_TAC_RIENG.md"

KURO_STANDARD_PROMPT = """### CẤU TRÚC THƯ MỤC DỰ ÁN (KURO STANDARD - 3 THƯ MỤC)
Dự án này đang áp dụng chuẩn **Kuro Standard** với 3 thư mục nghiệp vụ cấp cao nhất:
- `01_TAI_LIEU/` (Đầu vào): Tất cả tài liệu phục vụ công việc (file người dùng cung cấp, bản vẽ, Excel, PDF, tiêu chuẩn, hình ảnh, dữ liệu tham khảo). **Những gì Kuro tiếp nhận để làm việc.**
- `02_KURO_XU_LY/` (Trung gian): Toàn bộ file Kuro tạo ra trong quá trình làm việc (code, script Python/JS, file trung gian, dữ liệu trích xuất, bảng tính nháp, bản phân tích, file thử nghiệm). **Những gì Kuro tạo ra để phục vụ quá trình làm việc.**
- `03_KET_QUA/` (Đầu ra): Sản phẩm hoàn thành theo yêu cầu (Excel tính toán, PDF thuyết minh, bản vẽ DXF, HTML công cụ tính toán, báo cáo...). **Những gì người dùng cần nhận và sử dụng.**
- Sắp xếp, dọn dẹp thư mục dự án này thì theo đúng 3 thư mục trên. Cấu trúc 9 thư mục Phòng KT-TC (`1. HO SO PHAP LY` ... `9. KIEM TOAN CONG TRUONG`) là của kho mạng công ty, KHÔNG dùng cho thư mục dự án này.

### 7 QUY TẮC LÀM VIỆC BẮT BUỘC TRONG THƯ MỤC DỰ ÁN
1. Trước khi thực hiện, Kuro phải kiểm tra tài liệu hiện có trong thư mục dự án (đặc biệt trong `01_TAI_LIEU/`).
2. Không tự ý sửa đổi hoặc ghi đè tài liệu gốc trong `01_TAI_LIEU/`.
3. Mọi file phát sinh trong quá trình xử lý phải được lưu tại `02_KURO_XU_LY/`, không tạo file rải rác ngoài thư mục gốc.
4. Không tạo nhiều file trùng lặp hoặc nhiều phiên bản không cần thiết.
5. Kết quả hoàn thành phải được lưu tại `03_KET_QUA/`.
6. File code, script chỉ phục vụ nội bộ Kuro phải nằm trong `02_KURO_XU_LY/`. Công cụ được tạo ra để người dùng sử dụng (ví dụ file HTML công cụ tính toán) phải nằm trong `03_KET_QUA/`.
7. Khi kết thúc nhiệm vụ, Kuro phải thông báo rõ tên file kết quả và đường dẫn lưu đầy đủ.

### QUY TẮC QUẢN LÝ KHI CÓ NHIỀU NHIỆM VỤ
- Không tạo sẵn nhiều thư mục con khi chưa cần thiết.
- Chỉ khi một nhiệm vụ phát sinh nhiều file xử lý trung gian thì mới tạo thư mục con riêng trong `02_KURO_XU_LY/` theo dạng `TASK_001_<TEN_NHIEM_VU>/`, `TASK_002_<TEN_NHIEM_VU>/`."""

CUSTOM_RULES_TEMPLATE = """# QUY TẮC RIÊNG CỦA DỰ ÁN

Ghi các quy định đặc thù riêng cho dự án này (Kuro sẽ tự động đọc và tuân thủ mỗi lượt chat):

- Tiêu chuẩn / phiên bản áp dụng:
- Quy ước đặt tên file kết quả:
- Yêu cầu định dạng trình bày / mẫu biểu riêng:
- Lưu ý khác:
"""


def _norm_ws(p: Path | str) -> str:
    try:
        return Path(p).resolve().as_posix().lower()
    except Exception:
        return str(p).strip().replace("\\", "/").lower()


def read_custom_rules(ws_dir: Path, max_chars: int = 8000) -> str:
    f = ws_dir / CUSTOM_RULES_FILE
    if not f.is_file():
        return ""
    try:
        txt = f.read_text(encoding="utf-8", errors="replace").strip()
        return txt[:max_chars]
    except Exception:
        return ""


def inspect_workspace_rules(ws_dir: Path, ws_cfg: dict | None = None) -> dict:
    """Kiểm tra trạng thái quy tắc làm việc của một thư mục dự án."""
    ws = Path(ws_dir).resolve()
    norm = _norm_ws(ws)
    rules_map = (ws_cfg or {}).get("rules") or {}
    saved = rules_map.get(norm)  # "standard" | "none" | None

    custom_file = ws / CUSTOM_RULES_FILE
    has_custom = custom_file.is_file()
    existing_dirs = [d for d in STANDARD_DIRS if (ws / d).is_dir()]
    has_all_standard_dirs = len(existing_dirs) == len(STANDARD_DIRS)

    standard_enabled = (saved == "standard") or (saved is None and has_all_standard_dirs)

    if standard_enabled and has_custom:
        mode = "standard+custom"
    elif has_custom:
        mode = "custom"
    elif standard_enabled:
        mode = "standard"
    elif saved == "none":
        mode = "none"
    else:
        mode = "unset"

    # Chỉ hỏi đề xuất khi dự án chưa có quy tắc riêng, chưa có đủ 3 thư mục chuẩn và chưa từng chọn bỏ qua
    needs_prompt = (mode == "unset")

    return {
        "workspace": str(ws),
        "workspace_name": ws.name,
        "mode": mode,
        "standard_enabled": standard_enabled,
        "has_standard_dirs": has_all_standard_dirs,
        "existing_standard_dirs": existing_dirs,
        "has_custom_rules": has_custom,
        "custom_rules_file": CUSTOM_RULES_FILE,
        "custom_rules_path": str(custom_file),
        "needs_prompt": needs_prompt,
    }


def apply_workspace_rules(
    ws_dir: Path,
    mode: str,
    ws_cfg: dict,
    save_cfg_fn: Callable[[dict], None],
    create_custom: bool = False,
    custom_content: str | None = None,
) -> dict:
    """Áp dụng hoặc tắt chuẩn Kuro Standard, và/hoặc tạo/lưu QUY_TAC_RIENG.md cho dự án."""
    ws = Path(ws_dir).resolve()
    ws.mkdir(parents=True, exist_ok=True)
    norm = _norm_ws(ws)

    rules_map = dict(ws_cfg.get("rules") or {})
    if mode == "standard":
        for d in STANDARD_DIRS:
            (ws / d).mkdir(parents=True, exist_ok=True)
        rules_map[norm] = "standard"
    elif mode == "none":
        rules_map[norm] = "none"
    elif mode == "keep":
        # Không thay đổi trạng thái standard/none, chỉ cập nhật QUY_TAC_RIENG.md
        pass
    else:
        raise ValueError(f"Chế độ quy tắc không hợp lệ: {mode}")

    ws_cfg["rules"] = rules_map
    save_cfg_fn(ws_cfg)

    custom_file = ws / CUSTOM_RULES_FILE
    if custom_content is not None:
        cleaned = custom_content.strip()
        if cleaned:
            custom_file.write_text(cleaned + "\n", encoding="utf-8")
        elif custom_file.is_file():
            # Nếu người dùng xóa sạch nội dung thì gỡ file rỗng để không gây hiểu nhầm
            custom_file.unlink()
    elif create_custom and not custom_file.is_file():
        custom_file.write_text(CUSTOM_RULES_TEMPLATE, encoding="utf-8")

    return inspect_workspace_rules(ws, ws_cfg)


def build_workspace_rules_prompt(ws_dir: Path, ws_cfg: dict | None = None) -> str:
    """Xây dựng khối hướng dẫn Local Workspace nạp vào System Prompt cho mọi AI."""
    ws = Path(ws_dir).resolve()
    st = inspect_workspace_rules(ws, ws_cfg)
    parts = [
        f"\n\n## THƯ MỤC DỰ ÁN ĐANG LÀM VIỆC (LOCAL WORKSPACE)\n"
        f"Đường dẫn thư mục dự án trên máy người dùng: `{ws}`."
    ]

    if st["standard_enabled"]:
        parts.append(KURO_STANDARD_PROMPT)
    else:
        parts.append(
            f"- NƠI LƯU KẾT QUẢ BẮT BUỘC: Mọi tệp tin kết quả (.xlsx, .html, .docx, .py, script, báo cáo...) do AI tạo ra PHẢI lưu vào thư mục dự án này (`{ws}`).\n"
            f"- NGUYÊN TẮC HỎI VỊ TRÍ LƯU: Nếu trong thư mục dự án chưa có quy định cấu trúc thư mục lưu cụ thể thì hỏi lại người dùng vị trí muốn lưu, không tự ý lưu vào các vị trí chưa được phép."
        )

    custom_txt = read_custom_rules(ws)
    if custom_txt:
        parts.append(
            f"### QUY TẮC RIÊNG CỦA DỰ ÁN (`{CUSTOM_RULES_FILE}`)\n"
            f"(Ưu tiên tuân thủ các quy định riêng dưới đây nếu có điểm bổ sung/khác biệt)\n\n"
            f"{custom_txt}"
        )

    parts.append(
        "- KHO DỮ LIỆU CÔNG TY (UNC): Các kho mạng chung như `\\\\phuongthanhtranconsin.data.com\\12.KỸ THUẬT THI CÔNG` và các kho hợp đồng CHỈ là nơi lưu trữ, tra cứu hồ sơ (READ-ONLY). "
        "TUYỆT ĐỐI KHÔNG tự ý lưu kết quả, tạo tệp tạm, ghi đè hoặc xóa trên kho mạng chung này."
    )
    return "\n\n".join(parts)
