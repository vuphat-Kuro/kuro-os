#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ kiểm định tự động đầu ra tài liệu & báo cáo (kiem_tra_san_pham.py v2.15)
Phòng Kỹ thuật - Thi công | Công ty CP ĐT & XD Giao thông Phương Thành

Quy chuẩn kiểm tra dựa trên QLDA/GEMINI.md v2.15 và QLDA/GEMINI_DISCIPLINE.md:
1. [CẤM] Cú pháp LaTeX: $, $$, \\text, \\frac, \\times, \\ge, \\le, \\Delta, \\sqrt...
2. [CẤM] Ký tự em dash (U+2014: —).
3. [CẤM] Giao thức file:// hoặc mã neo dòng #L... trong liên kết markdown.
4. [CẤM] Đường dẫn tuyệt đối ổ đĩa C:\\ trong liên kết markdown.
5. [CẢNH BÁO] Thiếu cấu trúc chuẩn "KẾT LUẬN 10 GIÂY" đối với báo cáo/văn bản hoàn chỉnh.
6. [CẢNH BÁO] Số liệu kỹ thuật chưa gắn nhãn hợp lệ ([ĐÃ XÁC MINH], [NGƯỜI DÙNG KHAI], [GIẢ THIẾT], [CẦN KIỂM TRA], [CẦN KIỂM TRA HIỆU LỰC]).
"""

import sys
import os
import re
import argparse
from pathlib import Path

# Danh mục pattern vi phạm
PATTERNS_LATEX = [
    (r'(?<!\\)\$\$[\s\S]*?\$\$', 'Khối công thức toán LaTeX ($$...$$)'),
    (r'(?<!\\)\$(?!\{)[^$\n]+(?<!\\)\$', 'Công thức inline LaTeX ($...$)'),
    (r'\\text\{[^}]*\}', 'Lệnh LaTeX \\text{...}'),
    (r'\\frac\{[^}]*\}\{[^}]*\}', 'Lệnh phân số LaTeX \\frac{...}{...}'),
    (r'\\(times|Delta|alpha|beta|gamma|sigma|phi|lambda|sqrt|pm|le|ge)\b', 'Ký hiệu/lệnh LaTeX (thay bằng ký tự Unicode trực quan)'),
]

PATTERNS_EMDASH = [
    (r'\u2014', 'Ký tự em dash (U+2014 "—"). Bắt buộc thay bằng dấu gạch ngang "-"'),
]

PATTERNS_LINKS = [
    (r'\[([^\]]*)\]\(file://[^\)]*\)', 'Giao thức cấm file:// trong liên kết markdown'),
    (r'\[([^\]]*)\]\([^)#\s]+#L\d+(?:-L\d+)?\)', 'Mã neo dòng #L... trong liên kết markdown'),
    (r'\[([^\]]*)\]\([a-zA-Z]:[\\/][^\)]*\)', 'Đường dẫn tuyệt đối máy tính trong liên kết (bắt buộc dùng đường dẫn tương đối từ vault root)'),
]

VALID_DATA_TAGS = [
    '[ĐÃ XÁC MINH]',
    '[NGƯỜI DÙNG KHAI]',
    '[GIẢ THIẾT]',
    '[CẦN KIỂM TRA]',
    '[CẦN KIỂM TRA HIỆU LỰC]'
]

# Tệp nhị phân: không đọc như text (byte nén gây báo lỗi LaTeX giả)
BINARY_EXTS = {'.pdf', '.docx', '.doc', '.xls', '.pptx', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.dwg'}


def extract_xlsx_text(path):
    """Chỉ lấy chuỗi văn bản trong ô (sharedStrings và inline string), bỏ công thức và XML."""
    import zipfile
    import html
    parts = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name == 'xl/sharedStrings.xml' or re.match(r'xl/worksheets/sheet\d+\.xml$', name):
                xml = z.read(name).decode('utf-8', errors='ignore')
                parts += [html.unescape(t) for t in re.findall(r'<t(?:\s[^>]*)?>([^<]*)</t>', xml)]
    return '\n'.join(parts)


class ProductAuditor:
    def __init__(self, strict=False):
        self.strict = strict
        self.total_checked = 0
        self.total_errors = 0
        self.total_warnings = 0
        self.results = []

    def audit_content(self, content, source_name="<input>", is_report=False):
        errors = []
        warnings = []
        lines = content.splitlines()

        # 1. Quét lỗi LaTeX
        for pattern, desc in PATTERNS_LATEX:
            matches = list(re.finditer(pattern, content))
            for m in matches:
                # Tìm dòng xuất hiện
                start_pos = m.start()
                line_no = content[:start_pos].count('\n') + 1
                matched_snippet = m.group(0)[:40].replace('\n', ' ')
                errors.append({
                    'type': 'LATEX',
                    'line': line_no,
                    'snippet': matched_snippet,
                    'desc': desc
                })

        # 2. Quét lỗi Em dash
        for pattern, desc in PATTERNS_EMDASH:
            matches = list(re.finditer(pattern, content))
            for m in matches:
                start_pos = m.start()
                line_no = content[:start_pos].count('\n') + 1
                snippet = lines[line_no - 1] if line_no <= len(lines) else ''
                errors.append({
                    'type': 'EM_DASH',
                    'line': line_no,
                    'snippet': snippet.strip()[:60],
                    'desc': desc
                })

        # 3. Quét lỗi liên kết và đường dẫn
        for pattern, desc in PATTERNS_LINKS:
            matches = list(re.finditer(pattern, content))
            for m in matches:
                start_pos = m.start()
                line_no = content[:start_pos].count('\n') + 1
                snippet = m.group(0)[:60]
                errors.append({
                    'type': 'BAD_LINK',
                    'line': line_no,
                    'snippet': snippet,
                    'desc': desc
                })

        # 4. Kiểm tra cấu trúc KẾT LUẬN 10 GIÂY nếu là báo cáo/văn bản hoàn chỉnh
        if is_report:
            has_conclusion = bool(re.search(r'KẾT LUẬN 10 GIÂY', content, re.IGNORECASE))
            if not has_conclusion:
                warnings.append({
                    'type': 'STRUCTURE',
                    'line': 1,
                    'snippet': content[:60].replace('\n', ' '),
                    'desc': 'Thiếu khối mở đầu [KẾT LUẬN 10 GIÂY] theo quy định Mục 0.5 & 7.0.1'
                })

        # 5. Đánh giá số liệu và nhãn dữ liệu nếu có bảng/số liệu kỹ thuật
        has_figures = bool(re.search(r'\b\d+(?:[\.,]\d+)?\s*(?:m3|m2|m|tấn|kg|kN|kNm|%|đồng|VNĐ|triệu|tỷ)\b', content, re.IGNORECASE))
        has_tags = any(tag in content for tag in VALID_DATA_TAGS)
        if has_figures and not has_tags and is_report:
            warnings.append({
                'type': 'DATA_TAG',
                'line': 1,
                'snippet': 'Phát hiện số liệu kỹ thuật nhưng chưa thấy xuất hiện 4 nhãn dữ liệu chuẩn',
                'desc': 'Nên bổ sung nhãn minh bạch: [ĐÃ XÁC MINH], [NGƯỜI DÙNG KHAI], [GIẢ THIẾT], [CẦN KIỂM TRA]'
            })

        self.total_checked += 1
        self.total_errors += len(errors)
        self.total_warnings += len(warnings)

        res = {
            'source': source_name,
            'errors': errors,
            'warnings': warnings,
            'status': 'FAIL' if errors else ('WARN' if warnings else 'PASS')
        }
        self.results.append(res)
        return res

    def audit_file(self, file_path, is_report=False):
        path = Path(file_path)
        if not path.is_file():
            print(f"[ERROR] Không tìm thấy file: {file_path}", file=sys.stderr)
            return None
        suffix = path.suffix.lower()
        if suffix in BINARY_EXTS:
            print(f"[SKIP] Tệp nhị phân, không quét nội dung text: {file_path}", file=sys.stderr)
            return None
        try:
            if suffix in ('.xlsx', '.xlsm'):
                content = extract_xlsx_text(path)
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
        except Exception as e:
            print(f"[ERROR] Không thể đọc file {file_path}: {e}", file=sys.stderr)
            return None

        # Tự nhận diện báo cáo nếu file là markdown và không phải script/quy tắc/agent
        if not is_report and path.suffix.lower() == '.md':
            path_str = str(path).lower()
            if 'agents' not in path_str and '06-quytac' not in path_str:
                if any(k in path.name.lower() for k in ['bao-cao', 'baocao', 'nghiem-thu', 'bien-ban', 'bienban']):
                    is_report = True

        return self.audit_content(content, source_name=str(path), is_report=is_report)

    def print_report(self):
        print("=" * 80)
        print("BÁO CÁO KIỂM ĐỊNH SẢN PHẨM ĐẦU RA (kiem_tra_san_pham.py v2.15)")
        print(f"Tổng số nguồn đã kiểm tra : {self.total_checked}")
        print(f"Số lỗi nghiêm trọng (LỖI) : {self.total_errors}")
        print(f"Số khuyến nghị (CẢNH BÁO)  : {self.total_warnings}")
        print("=" * 80)

        for res in self.results:
            status_symbol = "[PASS]" if res['status'] == 'PASS' else ("[WARN]" if res['status'] == 'WARN' else "[FAIL]")
            print(f"\n{status_symbol} {res['source']}")
            
            if res['errors']:
                print("  --- DANH SÁCH LỖI NGHIÊM TRỌNG (BẮT BUỘC SỬA) ---")
                for err in res['errors']:
                    print(f"  + [Dòng {err['line']}] [{err['type']}] {err['desc']}")
                    print(f"    Trích đoạn: \"{err['snippet']}\"")

            if res['warnings']:
                print("  --- KHUYẾN NGHỊ HOÀN THIỆN ---")
                for w in res['warnings']:
                    print(f"  * [Dòng {w['line']}] [{w['type']}] {w['desc']}")
                    if w['snippet']:
                        print(f"    Trích đoạn: \"{w['snippet']}\"")

        print("\n" + "=" * 80)
        if self.total_errors > 0:
            print("KẾT LUẬN: KHÔNG ĐẠT (Phát hiện vi phạm quy tắc bắt buộc. Vui lòng chỉnh sửa trước khi xuất xưởng).")
            return 1
        elif self.total_warnings > 0:
            print("KẾT LUẬN: ĐẠT CÓ CẢNH BÁO (Đủ điều kiện xuất bản, khuyến nghị rà soát cảnh báo).")
            return 0
        else:
            print("KẾT LUẬN: HOÀN TOÀN ĐẠT TIÊU CHUẨN (100% PASS - Tuyệt đối sạch lỗi).")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="Kiểm tra chất lượng và quy chuẩn tài liệu đầu ra theo QLDA/GEMINI.md v2.15"
    )
    parser.add_argument("target", nargs="?", help="Đường dẫn tệp tin hoặc thư mục cần kiểm tra")
    parser.add_argument("--text", help="Nội dung chuỗi văn bản trực tiếp cần kiểm tra")
    parser.add_argument("--report", action="store_true", help="Bắt buộc kiểm tra cấu trúc báo cáo (KẾT LUẬN 10 GIÂY)")
    parser.add_argument("--strict", action="store_true", help="Bật chế độ nghiêm ngặt: cảnh báo cũng coi là lỗi")
    parser.add_argument("--ext", default=".md,.txt", help="Phần mở rộng tệp cần quét khi duyệt thư mục (mặc định: .md,.txt)")

    args = parser.parse_args()
    auditor = ProductAuditor(strict=args.strict)

    if args.text:
        auditor.audit_content(args.text, source_name="<raw_text>", is_report=args.report)
    elif args.target:
        target_path = Path(args.target)
        if target_path.is_file():
            auditor.audit_file(target_path, is_report=args.report)
        elif target_path.is_dir():
            allowed_exts = [e.strip().lower() for e in args.ext.split(",")]
            for root, _, files in os.walk(target_path):
                # Bỏ qua thư mục .git, _backup, __pycache__, node_modules
                if any(ignored in root for ignored in ['.git', '_backup', '__pycache__', 'node_modules']):
                    continue
                for f in sorted(files):
                    p = Path(root) / f
                    if p.suffix.lower() in allowed_exts:
                        auditor.audit_file(p, is_report=args.report)
        else:
            print(f"[ERROR] Đường dẫn không tồn tại: {args.target}", file=sys.stderr)
            sys.exit(2)
    else:
        # Nếu đọc từ stdin
        if not sys.stdin.isatty():
            content = sys.stdin.read()
            auditor.audit_content(content, source_name="<stdin>", is_report=args.report)
        else:
            parser.print_help()
            sys.exit(0)

    exit_code = auditor.print_report()
    if args.strict and auditor.total_warnings > 0:
        sys.exit(1)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
