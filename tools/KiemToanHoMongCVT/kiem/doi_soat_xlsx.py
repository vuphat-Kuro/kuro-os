# -*- coding: utf-8 -*-
"""TM5: đối soát độc lập file Excel thuyết minh với số của chương trình (calcResults dump ra JSON).
Đọc ô lưu sẵn bằng openpyxl, tìm theo nhãn dòng trong từng mục; so M_max, σ, [σ], phản lực, tỷ số cừ, bịt đáy, thanh chống và mọi kết luận.
Chạy: python doi_soat_xlsx.py ca/T11"""
import sys, json, re, openpyxl
sys.stdout.reconfigure(encoding='utf-8')
base = sys.argv[1]
J = json.load(open(base + '.json', encoding='utf-8'))
WS = openpyxl.load_workbook(base + '.xlsx', data_only=True)['ThuyetMinh']
ALL = [[c.value for c in r] for r in WS.iter_rows()]
bad = []; n = 0
def near(a, b, tol=1e-6): return abs(a - b) <= tol * max(1, abs(b))
def isbad(c): return 'KHÔNG' in c or 'không đảm bảo' in c or 'không đủ' in c
def cmp(tag, a, b, tol=1e-6):
    global n; n += 1
    if a is None or not isinstance(a, (int, float)) or not near(a, b, tol): bad.append((tag, a, b))
def first(r): return next((v for v in r if v not in (None, '')), '')
def region(start_re, end_re=None):
    """Các dòng từ tiêu đề khớp start_re đến trước tiêu đề khớp end_re."""
    out = []; on = False
    for r in ALL:
        t = first(r)
        if not on and isinstance(t, str) and re.match(start_re, t): on = True
        elif on and end_re and isinstance(t, str) and re.match(end_re, t): break
        if on: out.append(r)
    return out
def label_val(rs, start):
    for r in rs:
        t = [v for v in r if v is not None and v != '']
        if t and isinstance(t[0], str) and t[0].startswith(start):
            nums = [v for v in t[1:] if isinstance(v, (int, float))]
            return nums[0] if nums else None
    return None
def all_vals(rs, start):
    out = []
    for r in rs:
        t = [v for v in r if v is not None and v != '']
        if t and isinstance(t[0], str) and t[0].startswith(start): out += [v for v in t[1:] if isinstance(v, (int, float))][:1]
    return out
def concls(rs): return [first(r) for r in rs if isinstance(first(r), str) and first(r).startswith('Kết luận:')]

A = J['modA']
if A:
    rs = region(r'5\. KIỂM TOÁN LỚP BÊ TÔNG BỊT ĐÁY', r'6\. KIỂM TOÁN')
    cmp('bd h_min', label_val(rs, 'Chiều dày tối thiểu'), A['h_min']); cmp('bd FS', label_val(rs, 'Hệ số an toàn FS'), A['FS'])
    sv = all_vals(rs, 'σ = M / W'); cmp('bd sigma (max)', max(sv) if sv else None, A['sigma'])
    cc = concls(rs)
    for c, ok in zip(cc, [A['ok'], A['okb']]):
        n += 1
        if (not isbad(c)) != bool(ok): bad.append(('bd kết luận', c, ok))
for s in J['stages']:
    rs = region(r'6\.\d+\. Giai đoạn %d:' % s['n'], r'(6\.\d+\. Giai đoạn|7\. KIỂM TOÁN)')
    g = f'GD{s["n"]}'
    cmp(g + ' M_max', label_val(rs, 'Giá trị mômen lớn nhất'), s['M'])
    sv2 = all_vals(rs, 'σmax'); cmp(g + ' sigma', sv2[0] if sv2 else None, s['sigma'])
    cmp(g + ' [sigma]', label_val(rs, '[σ]: ứng suất cho phép'), s['sa'])
    rv = all_vals(rs, 'Giá trị phản lực'); n += 1
    if len(rv) != len(s['react']) or any(not near(x, y) for x, y in zip(rv, s['react'])): bad.append((g + ' phản lực', rv, s['react']))
    cc = concls(rs); n += 1
    if cc and (not isbad(cc[-1])) != bool(s['ok']): bad.append((g + ' kết luận độ bền', cc[-1], s['ok']))
    if s['lat']['req'] and len(cc) >= 2:
        n += 1
        if (not isbad(cc[0])) != bool(s['lat']['ok']): bad.append((g + ' kết luận lật', cc[0], s['lat']['ok']))
R = region(r'7\. KIỂM TOÁN HỆ KHUNG CHỐNG')
tab = [r for r in R if isinstance(first(r), str) and re.fullmatch(r'GĐ\d+', first(r))]
for s in J['stages']:
    for c in s['struts']:
        hit = [r for r in tab if r[0] == 'GĐ%d' % s['n'] and (c['name'] in r[1:4])]
        if not hit: bad.append((f'thiếu dòng GĐ{s["n"]} {c["name"]}', None, None)); continue
        nums = [v for v in hit[0] if isinstance(v, (int, float))]
        # nums: q, bước, P, L0, λx, λy, φ, M_u, f, bền, tỷ số chi phối
        for k, i, key in (('P', 2, 'P'), ('M_u', 7, 'Mu')): cmp(f'GĐ{s["n"]} {c["name"]} {k}', nums[i], c[key])
        cmp(f'GĐ{s["n"]} {c["name"]} σ', nums[9], c['rs'] * c['f'], 1e-5)
        n += 1
        kq = [v for v in hit[0] if v in ('ĐẠT', 'VƯỢT')]
        if not kq or (kq[0] == 'ĐẠT') != bool(c['ok']): bad.append((f'GĐ{s["n"]} {c["name"]} kết quả', kq, c['ok']))
# --- mục 7 bản 5: khung chống từng tầng, cột chống tạm, mối nối hàn (đọc ô lưu sẵn, so với số chương trình)
tiers = sorted({f['name'] for s in J['stages'] for f in s.get('frames', [])})
for nm in tiers:
    rs = region(r'7\.\d+\. Khung chống tầng %s$' % re.escape(nm), r'7\.\d+\. (Khung chống tầng|Kiểm toán)')
    fr = [(s['n'], f) for s in J['stages'] for f in s.get('frames', []) if f['name'] == nm]
    rows = [r for r in rs if isinstance(first(r), str) and re.fullmatch(r'GĐ\d+', first(r))]
    for sn, f in fr:
        hit = [r for r in rows if first(r) == 'GĐ%d' % sn]
        if not hit: bad.append((f'thiếu dòng khung {nm} GĐ{sn}', None, None)); continue
        nums = [v for v in hit[-1] if isinstance(v, (int, float))]      # q, chuyển vị
        cmp(f'khung {nm} GĐ{sn} q', nums[0], f['q']); cmp(f'khung {nm} GĐ{sn} chuyển vị', nums[1], f['disp'])
        n += 1
        if ('ĐẠT' in hit[-1]) != (f['ratio'] <= 1 + 1e-9): bad.append((f'khung {nm} GĐ{sn} kết quả', hit[-1], f['ratio']))
    cc = [first(r) for r in rs if isinstance(first(r), str) and first(r).startswith('Kết luận:')]
    n += 1
    okf = all(f['ratio'] <= 1 + 1e-9 for _, f in fr)
    if not cc or (not isbad(cc[-1])) != okf: bad.append((f'khung {nm} kết luận', cc[-1:] , okf))
posts = J.get('posts', [])
if posts:
    rs = region(r'7\.\d+\. Kiểm toán cột chống tạm', r'7\.\d+\. Kiểm toán mối nối')
    for p in posts:
        hit = [r for r in rs if first(r) == p['id']]
        if not hit: bad.append((f'thiếu cột {p["id"]}', None, None)); continue
        nums = [v for v in hit[0] if isinstance(v, (int, float))]; cmp(f'cột {p["id"]} σ', nums[-2], p['ratio'] * p['f'], 1e-5)
        n += 1
        if (('ĐẠT' in hit[0]) != bool(p['ok'])): bad.append((f'cột {p["id"]} kết quả', hit[0], p['ok']))
W = J.get('welds', [])
if W:
    TL = {'waler': 'vành đai', 'strut_x': 'văng ngang', 'strut_y': 'văng dọc', 'brace': 'chống chéo, khuỷu'}
    rs = region(r'7\.\d+\. Kiểm toán mối nối hàn')
    for w in W:
        lab = f'Tầng {w["level"]}: {TL.get(w["type"], w["type"])}'
        hit = [r for r in rs if first(r) == lab]
        if not hit: bad.append((f'thiếu nhóm hàn {lab}', None, None)); continue
        nums = [v for v in hit[0] if isinstance(v, (int, float))]      # N, M, hf, tau, fwf, tỷ số
        cmp(f'hàn {lab} τf', nums[3], w['tauf'], 1e-3)
        n += 1
        if ('ĐẠT' in hit[0]) != bool(w['ok']): bad.append((f'hàn {lab} kết quả', hit[0], w['ok']))
print(f'{base}: so {n} giá trị, lệch {len(bad)}')
for b in bad[:20]: print('  ', b)
sys.exit(1 if bad else 0)
