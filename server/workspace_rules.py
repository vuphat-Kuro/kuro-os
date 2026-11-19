"""Quy tắc làm việc của từng thư mục dự án trên máy người dùng.

Nguồn quy tắc DUY NHẤT là tệp `QUY_TAC_LAM_VIEC.md` ở gốc thư mục dự án:
- Có tệp: mỗi lượt chat Kuro đọc lại tệp và làm đúng theo nội dung hiện tại (người dùng sửa tệp là đổi quy tắc).
- Không có tệp: Kuro làm việc bình thường.
Mẫu Kuro Standard (3 thư mục 01_TAI_LIEU / 02_KURO_XU_LY / 03_KET_QUA) chỉ dùng để viết tệp lần đầu khi người dùng
chọn áp dụng; Kuro không giữ quy tắc trong nội bộ. Cấu hình của Kuro chỉ nhớ dự án nào người dùng đã chọn "không áp
dụng" để khỏi hỏi lại.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

STANDARD_DIRS = ("01_TAI_LIEU", "02_KURO_XU_LY", "03_KET_QUA")
RULES_FILE = "QUY_TAC_LAM_VIEC.md"
OLD_RULES_FILE = "QUY_TAC_RIENG.md"   # tên cũ (v1.8.1), tự đổi sang RULES_FILE

KURO_STANDARD_TEMPLATE = """# QUY TẮC LÀM VIỆC CỦA DỰ ÁN (KURO STANDARD)

Kuro đọc tệp này ở mỗi lượt chat và làm đúng theo nội dung hiện tại. Muốn đổi quy tắc của dự án thì sửa trực tiếp tệp này.

## Cấu trúc thư mục (3 thư mục)
- `01_TAI_LIEU/` (Đầu vào): tài liệu phục vụ công việc (file người dùng cung cấp, bản vẽ, Excel, PDF, tiêu chuẩn, hình ảnh, dữ liệu tham khảo).
- `02_KURO_XU_LY/` (Trung gian): mọi file Kuro tạo ra trong quá trình làm việc (code, script Python/JS, file trung gian, dữ liệu trích xuất, bảng tính nháp, bản phân tích, file thử nghiệm, tệp đính kèm chat trong `02_KURO_XU_LY/.attachments/`).
- `03_KET_QUA/` (Đầu ra): sản phẩm hoàn thành theo yêu cầu (Excel tính toán, PDF thuyết minh, bản vẽ DXF, HTML công cụ tính toán, báo cáo...).
- Gốc dự án chỉ có 3 thư mục trên và tệp `QUY_TAC_LAM_VIEC.md` này. Sắp xếp, dọn dẹp dự án thì theo đúng 3 thư mục trên.
- Cấu trúc 9 thư mục Phòng KT-TC (`1. HO SO PHAP LY` ... `9. KIEM TOAN CONG TRUONG`) là của kho mạng công ty, KHÔNG dùng cho thư mục dự án này.

## 7 quy tắc làm việc bắt buộc
1. Trước khi thực hiện, kiểm tra tài liệu hiện có trong thư mục dự án (đặc biệt trong `01_TAI_LIEU/`).
2. Không tự ý sửa đổi hoặc ghi đè tài liệu gốc trong `01_TAI_LIEU/`.
3. Mọi file phát sinh trong quá trình xử lý lưu tại `02_KURO_XU_LY/`, không tạo file rải rác ngoài gốc dự án.
4. Không tạo nhiều file trùng lặp hoặc nhiều phiên bản không cần thiết.
5. Kết quả hoàn thành lưu tại `03_KET_QUA/`.
6. Code, script chỉ phục vụ nội bộ Kuro để trong `02_KURO_XU_LY/`. Công cụ tạo cho người dùng sử dụng (vd file HTML công cụ tính toán) để trong `03_KET_QUA/`.
7. Khi kết thúc nhiệm vụ, thông báo rõ tên file kết quả và đường dẫn lưu đầy đủ.

## Khi có nhiều nhiệm vụ
- Không tạo sẵn nhiều thư mục con khi chưa cần.
- Nhiệm vụ phát sinh nhiều file trung gian thì tạo thư mục con riêng trong `02_KURO_XU_LY/` dạng `TASK_001_<TEN_NHIEM_VU>/`, `TASK_002_<TEN_NHIEM_VU>/`.

## Quy định riêng của dự án
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


def read_rules(ws_dir: Path, max_chars: int = 12000) -> str:
    f = Path(ws_dir) / RULES_FILE
    if not f.is_file():
        return ""
    try:
        return f.read_text(encoding="utf-8-sig", errors="replace").strip()[:max_chars]   # -sig: Notepad có thể lưu kèm BOM
    except Exception:
        return ""


def attachments_dir(ws_dir: Path) -> Path:
    """Nơi lưu tệp đính kèm chat: trong 02_KURO_XU_LY nếu dự án có thư mục đó, để gốc dự án chỉ còn 3 thư mục."""
    xu_ly = Path(ws_dir) / "02_KURO_XU_LY"
    return (xu_ly if xu_ly.is_dir() else Path(ws_dir)) / ".attachments"


def _chuyen_ban_cu(ws: Path, saved: str | None):
    """Dự án làm từ v1.8.1 (quy tắc 'standard' nằm trong cấu hình Kuro, quy tắc riêng ở QUY_TAC_RIENG.md):
    viết thành một tệp QUY_TAC_LAM_VIEC.md trong dự án, một lần."""
    new, old = ws / RULES_FILE, ws / OLD_RULES_FILE
    if new.exists() or not (saved == "standard" or old.is_file()):
        return
    cu = old.read_text(encoding="utf-8-sig", errors="replace").strip() if old.is_file() else ""
    if saved == "standard":
        noi_dung = KURO_STANDARD_TEMPLATE + (f"\n## Quy định riêng (chuyển từ {OLD_RULES_FILE})\n\n{cu}\n" if cu else "")
    else:
        noi_dung = cu + "\n"
    new.write_text(noi_dung, encoding="utf-8")
    if old.is_file():
        old.unlink()   # nội dung đã nằm trong QUY_TAC_LAM_VIEC.md


def inspect_workspace_rules(ws_dir: Path, ws_cfg: dict | None = None) -> dict:
    """Trạng thái quy tắc làm việc của một thư mục dự án (quyết định bởi tệp QUY_TAC_LAM_VIEC.md)."""
    ws = Path(ws_dir).resolve()
    saved = ((ws_cfg or {}).get("rules") or {}).get(_norm_ws(ws))   # "none" | "standard" (cũ) | None
    try:
        _chuyen_ban_cu(ws, saved)
    except OSError:
        pass
    has_rules = (ws / RULES_FILE).is_file()
    existing_dirs = [d for d in STANDARD_DIRS if (ws / d).is_dir()]
    mode = "rules" if has_rules else ("none" if saved == "none" else "unset")
    return {
        "workspace": str(ws),
        "workspace_name": ws.name,
        "mode": mode,
        "has_rules": has_rules,
        "has_standard_dirs": len(existing_dirs) == len(STANDARD_DIRS),
        "existing_standard_dirs": existing_dirs,
        "rules_file": RULES_FILE,
        "rules_path": str(ws / RULES_FILE),
        "needs_prompt": mode == "unset",   # chỉ hỏi khi dự án chưa có tệp quy tắc và chưa từng chọn bỏ qua
    }


def apply_workspace_rules(
    ws_dir: Path,
    mode: str,
    ws_cfg: dict,
    save_cfg_fn: Callable[[dict], None],
    content: str | None = None,
) -> dict:
    """standard: tạo 3 thư mục + viết QUY_TAC_LAM_VIEC.md từ mẫu (không ghi đè tệp người dùng đã có).
    none: nhớ là không áp dụng (không xóa tệp). keep: chỉ lưu nội dung tệp quy tắc do người dùng sửa."""
    ws = Path(ws_dir).resolve()
    ws.mkdir(parents=True, exist_ok=True)
    norm = _norm_ws(ws)
    rules_map = dict(ws_cfg.get("rules") or {})
    f = ws / RULES_FILE

    if mode == "standard":
        for d in STANDARD_DIRS:
            (ws / d).mkdir(parents=True, exist_ok=True)
        if not f.exists():
            f.write_text(KURO_STANDARD_TEMPLATE, encoding="utf-8")
        rules_map.pop(norm, None)
    elif mode == "none":
        rules_map[norm] = "none"
    elif mode != "keep":
        raise ValueError(f"Chế độ quy tắc không hợp lệ: {mode}")

    if content is not None:
        cleaned = content.strip()
        if cleaned:
            f.write_text(cleaned + "\n", encoding="utf-8")
        elif f.is_file():
            f.unlink()   # người dùng xóa trắng nội dung = bỏ quy tắc, dự án làm việc bình thường

    ws_cfg["rules"] = rules_map
    save_cfg_fn(ws_cfg)
    return inspect_workspace_rules(ws, ws_cfg)


def build_workspace_rules_prompt(ws_dir: Path, ws_cfg: dict | None = None) -> str:
    """Khối hướng dẫn thư mục dự án nạp vào prompt mỗi lượt cho mọi AI (đọc lại tệp quy tắc mỗi lần)."""
    ws = Path(ws_dir).resolve()
    inspect_workspace_rules(ws, ws_cfg)   # chuyển bản cũ nếu cần
    parts = [f"\n\n## THƯ MỤC DỰ ÁN ĐANG LÀM VIỆC (LOCAL WORKSPACE)\nĐường dẫn thư mục dự án trên máy người dùng: `{ws}`."]
    rules = read_rules(ws)
    if rules:
        parts.append(
            f"### QUY TẮC LÀM VIỆC CỦA DỰ ÁN (tệp `{RULES_FILE}` ở gốc dự án)\n"
            "Đây là quy tắc người dùng đặt cho dự án này và có thể đã được sửa. BẮT BUỘC làm đúng theo nội dung "
            "hiện tại dưới đây, ưu tiên hơn quy tắc lưu tệp mặc định của Kuro. Không tự sửa tệp này khi người dùng chưa yêu cầu.\n\n"
            f"{rules}"
        )
    else:
        parts.append(
            f"- NƠI LƯU KẾT QUẢ BẮT BUỘC: Mọi tệp tin kết quả (.xlsx, .html, .docx, .py, script, báo cáo...) do AI tạo ra PHẢI lưu vào thư mục dự án này (`{ws}`).\n"
            f"- NGUYÊN TẮC HỎI VỊ TRÍ LƯU: Nếu trong thư mục dự án chưa có quy định cấu trúc thư mục lưu cụ thể thì hỏi lại người dùng vị trí muốn lưu, không tự ý lưu vào các vị trí chưa được phép."
        )
    parts.append(
        "- KHO DỮ LIỆU CÔNG TY (UNC): Các kho mạng chung như `\\\\phuongthanhtranconsin.data.com\\12.KỸ THUẬT THI CÔNG` và các kho hợp đồng CHỈ là nơi lưu trữ, tra cứu hồ sơ (READ-ONLY). "
        "TUYỆT ĐỐI KHÔNG tự ý lưu kết quả, tạo tệp tạm, ghi đè hoặc xóa trên kho mạng chung này."
    )
    return "\n\n".join(parts)
