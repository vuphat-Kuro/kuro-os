# -*- coding: utf-8 -*-
"""Chạy chương trình kiểm toán vòng vây cọc ván thép (HTML một tệp) KHÔNG cần mở trình duyệt bằng tay, để agent hoặc người dùng gọi từ dòng lệnh.

Cách dùng (cần Python 3 và gói playwright, trình duyệt Chromium hoặc Edge):
    python chay_kiem_toan.py                                   # bộ số mặc định (T11 Ninh Cơ)
    python chay_kiem_toan.py --config mau/Mau_KiemToan_NinhCo_T11_T12.json
    python chay_kiem_toan.py --config du_an_moi.json --out ket_qua_du_an_moi
    python chay_kiem_toan.py --luu-config mau/T11_mac_dinh.json --khong-excel --khong-mct   # xuất bộ số hiện dùng ra JSON
    python chay_kiem_toan.py --config du_an.json --khung-json T2:4 --khong-excel --khong-mct   # số khung chống tầng T2 giai đoạn 4 để so Midas
    python chay_kiem_toan.py --hoi-quy                         # so 5 mốc hồi quy với bộ số mặc định (thoát 1 nếu lệch)

Đầu vào --config: tệp JSON xuất từ chương trình (menu Công cụ, "Xuất JSON").
Đầu ra (thư mục --out): tong_hop.json (số liệu tóm tắt), tong_hop.md (bảng đạt, không đạt), mct/*.mct (khung chống từng tầng, dầm cừ từng giai đoạn),
thuyet_minh.xlsx (Excel thuyết minh), ghi_chu.txt (lỗi console nếu có). Không ghi đè tệp chương trình, không gửi gì ra ngoài.
Chương trình tự tính; script này chỉ nạp số liệu, bấm tính và đọc kết quả."""
import argparse, base64, glob, json, os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
# 5 mốc hồi quy của bộ số mặc định T11 (đo 11/11/2026, chương trình v2.0)
MOC = {'tong_hop': '68b005dd', 'chi_tiet': 'feeb1273', 'khung_mat_bang': 'b187c6dd', 'thuyet_minh_cu': '6104f99f', 'ty_so_40': 'e2741f1c'}

JS_TOM_TAT = r"""() => {
  const c = calcResults, out = { du_an: (currentConfig.project || {}).name || '', so_giai_doan: (c.dynamicStages || []).length };
  const prim = o => { const r = {}; Object.keys(o || {}).forEach(k => { const v = o[k]; if (['number', 'boolean', 'string'].includes(typeof v)) r[k] = v; }); return r; };
  out.bit_day = prim(c.modA); out.on_dinh_day_ho = prim(c.modB);
  try { out.ma_tran = v18Rows().map(x => ({ nhom: x.grp, muc: x.item, vi_tri: x.where, giai_doan: x.stage, loai: x.kind, ty_so: x.ratio, dat: x.ok, can_cu: x.dc })); } catch (e) { out.ma_tran = String(e); }
  out.giai_doan = (c.dynamicStages || []).map(s => ({
    so: s.stage_num, ten: s.name, co_dam_cu: !!s.beam, M_max: s.beam && s.beam.M_max, sigma: s.beam && s.beam.sigma, sigma_cho_phep: s.beam && s.beam.sigma_allow, ty_so_cu: s.beam && s.beam.ratio, dat_cu: s.beam && s.beam.is_safe,
    chuyen_vi_mm: s.beam && s.beam.max_defl, phan_luc: s.beam && (s.beam.reactions || []).map(r => ({ gối: r.name, R: r.R })), quy_tac: s.beam && s.beam.rule,
    thanh_chong: (s.strutCheck || []).map(t => ({ ten: t.name, ty_so: t.ratio, dat: t.is_safe })),
    khung_mat_bang: Object.fromEntries(Object.entries(s.frame2D_results || {}).filter(([k, f]) => f).map(([k, f]) => [k, { ty_so_max: Math.max(...f.elements.map(e => e.check.ratio)), so_thanh_khong_dat: f.elements.filter(e => !e.check.is_safe).length, so_thanh: f.elements.length, chuyen_vi_max_mm: f.maxDisplacement, q_T_m: f.q_line }]))
  }));
  return out; }"""
JS_MCT = r"""() => { const o = []; mctTiers().forEach(t => { const r = mctBuild(t); o.push({ loai: 'khung', ten: t, err: r.err || null, file: r.fileName, text: r.text || null, ghi_chu: r.notes || [], canh_bao: r.warn || [] }); });
  mctStages().forEach(s => { const r = mctBuildPile(s.i); o.push({ loai: 'dam_cu', ten: s.s.name, err: r.err || null, file: r.fileName, text: r.text || null, ghi_chu: r.notes || [], canh_bao: r.warn || [] }); }); return o; }"""
JS_XLSX = r"""async () => { const b = await tmBuildWorkbook(); let s = ''; const u = new Uint8Array(b); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); }"""

def md_bang(t):
    L = [f"# Tổng hợp kiểm toán: {t['du_an']}", '', f"Số giai đoạn: {t['so_giai_doan']}.", '']
    rows = t.get('ma_tran')
    if isinstance(rows, list):
        L += ['| Nhóm | Mục | Vị trí | Giai đoạn | Tỷ số | Kết quả |', '|---|---|---|---|---|---|']
        for r in rows:
            L.append(f"| {r['nhom']} | {r['muc']} | {r['vi_tri']} | {r['giai_doan']} | {'' if r['ty_so'] is None else round(r['ty_so'], 3)} | {'ĐẠT' if r['dat'] else 'KHÔNG ĐẠT'} |")
    return '\n'.join(L) + '\n'

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--html', help='đường dẫn chương trình HTML (mặc định: bản mới nhất trong chuong_trinh/)')
    ap.add_argument('--config', help='JSON số liệu xuất từ chương trình')
    ap.add_argument('--out', help='thư mục kết quả (mặc định ket_qua_<thời gian>)')
    ap.add_argument('--luu-config', help='ghi số liệu đang dùng (sau chuẩn hóa) ra tệp JSON, dùng lại bằng --config')
    ap.add_argument('--khung-json', help='TANG:GD, ví dụ T2:4: ghi số từng thanh khung chống (N, V, M, A, W, L, q) vào khung_<TANG>_GD<n>.json để đối soát Midas bằng kiem/so_midas_khung.py')
    ap.add_argument('--khong-mct', action='store_true'); ap.add_argument('--khong-excel', action='store_true')
    ap.add_argument('--hoi-quy', action='store_true', help='so 5 mốc hồi quy (chỉ với bộ số mặc định)')
    a = ap.parse_args()
    html = a.html or sorted(glob.glob(os.path.join(HERE, 'chuong_trinh', '*.html')))[-1]
    out = a.out or os.path.join(os.getcwd(), 'ket_qua_' + time.strftime('%Y%m%d_%H%M%S'))
    os.makedirs(out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    errs = []; code = 0
    with sync_playwright() as p:
        try: b = p.chromium.launch(headless=True)
        except Exception: b = p.chromium.launch(headless=True, channel='msedge')
        pg = b.new_context(accept_downloads=False).new_page()
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e))); pg.on('console', lambda m: errs.append('console.error: ' + m.text) if m.type == 'error' and 'favicon' not in m.text else None)
        pg.goto('file:///' + os.path.abspath(html).replace('\\', '/')); pg.wait_for_function("typeof runCalculation === 'function' && typeof mctBuild === 'function'", timeout=60000)
        if a.config:
            txt = open(a.config, encoding='utf-8').read()
            pg.evaluate("t => { currentConfig = normalizeAndMigrateConfig(JSON.parse(t)); syncConfigToForm(); runCalculation(); }", txt)
        else:
            pg.evaluate("() => runCalculation()")
        tt = pg.evaluate(JS_TOM_TAT)
        if a.luu_config: open(a.luu_config, 'w', encoding='utf-8').write(pg.evaluate('() => JSON.stringify(currentConfig, null, 1)'))
        json.dump(tt, open(os.path.join(out, 'tong_hop.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        open(os.path.join(out, 'tong_hop.md'), 'w', encoding='utf-8').write(md_bang(tt))
        if a.khung_json:
            tang, gd = a.khung_json.split(':')
            kj = pg.evaluate("([t, g]) => { const st = calcResults.dynamicStages.find(s => s.stage_num === +g && s.frame2D_results && s.frame2D_results[t]); if (!st) return null; const f = st.frame2D_results[t]; return { q: f.q_line, els: f.elements.map(e => ({ name: e.name, prof: e.profile, orient: e.orient, A: e.A, W: e.W, I: e.I, L: e.L, q: e.q, rel: e.release, N: e.internal.N, V1: e.internal.V1, V2: e.internal.V2, M1: e.internal.M1, M2: e.internal.M2 })) }; }", [tang, gd])
            if kj is None: errs.append(f'--khung-json: không có khung tầng {tang} giai đoạn {gd}')
            else: json.dump(kj, open(os.path.join(out, f'khung_{tang}_GD{gd}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        if not a.khong_mct:
            os.makedirs(os.path.join(out, 'mct'), exist_ok=True); n = 0
            for m in pg.evaluate(JS_MCT):
                if m['err']: errs.append(f"MCT {m['loai']} {m['ten']}: {m['err']}"); continue
                open(os.path.join(out, 'mct', m['file']), 'w', encoding='ascii', newline='').write(m['text']); n += 1
            print('MCT đã ghi:', n)
        if not a.khong_excel:
            try: open(os.path.join(out, 'thuyet_minh.xlsx'), 'wb').write(base64.b64decode(pg.evaluate(JS_XLSX)))
            except Exception as e: errs.append('Excel: ' + str(e))
        if a.hoi_quy:
            if a.config: print('Bỏ qua hồi quy: chỉ so được với bộ số mặc định.')
            else:
                pg.add_script_tag(path=os.path.join(HERE, 'kiem', 'hoi_quy_T11.js')); pg.evaluate("() => switchTab('kq')")
                r = pg.evaluate("async () => await hoiQuyT11()")
                bad = {k: (r[k].split(' ')[0], MOC[k]) for k in MOC if r[k].split(' ')[0] != MOC[k]}
                print('Hồi quy:', json.dumps(r, ensure_ascii=False)); print('KHỚP 5 mốc' if not bad else f'LỆCH: {bad}'); code = 0 if not bad else 1
        b.close()
    open(os.path.join(out, 'ghi_chu.txt'), 'w', encoding='utf-8').write('\n'.join(errs) if errs else 'Không có lỗi console, không có tầng hoặc giai đoạn bị từ chối khi xuất MCT.\n')
    nd = sum(1 for r in tt['ma_tran'] if r['dat']) if isinstance(tt.get('ma_tran'), list) else 0
    print(f"{tt['du_an']}: {tt['so_giai_doan']} giai đoạn, ma trận {nd}/{len(tt['ma_tran'])} mục đạt. Kết quả ở {out}" + (f"; {len(errs)} ghi chú lỗi" if errs else ''))
    sys.exit(code)

if __name__ == '__main__':
    main()
