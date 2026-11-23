# -*- coding: utf-8 -*-
"""Kiem ket qua S4. Chay: python -X utf8 -I verify_s4.py <thu_muc_test> <thu_muc_src_Db>"""
import glob
import json
import os
import re
import sys

t, src = sys.argv[1], sys.argv[2]
fails = []


def check(cond, name, got=None):
    if cond:
        print('  dat  ' + name)
    else:
        print('  LOI  %s (thuc te: %r)' % (name, got))
        fails.append(name)


def load(n):
    return json.load(open(os.path.join(t, n), encoding='utf-8'))


def fonts(d):
    return {f['name'].lower(): f for f in d['fonts']}


fb, fa, fn = load('fonts_before.json'), load('fonts_after_sub.json'), load('fonts_nostore.json')
sb, sa, su, sc = load('scan_before.json'), load('scan_after.json'), load('scan_undo.json'), load('scan_cancel.json')

print('Bao cao font (co kho font)')
F = fonts(fb)
check(fb['meta']['storeFiles'] >= 15, 'doc duoc kho font (>= 15 tep)', fb['meta']['storeFiles'])
check(F['pkttdemo.shx']['status'] == 'inStore' and F['pkttdemo.shx']['storePath'].lower().endswith('pkttdemo.shx'), 'pkttdemo.shx: thieu tren may, co trong kho, co duong dan tep', (F['pkttdemo.shx']['status'], F['pkttdemo.shx']['storePath']))
check(F['khongco.shx']['status'] == 'missing' and F['khongco.shx']['substitute'] == 'Segoe UI' and F['khongco.shx']['substituteSource'] == 'installed', 'khongco.shx: thieu hoan toan, goi y Segoe UI (da cai)', F['khongco.shx'])
check(F['font khong ton tai']['status'] == 'missing' and F['font khong ton tai']['substitute'] == 'Segoe UI', 'TrueType "Font Khong Ton Tai": thieu, goi y Segoe UI', F['font khong ton tai'])
check(F['font khac khong co']['status'] == 'missing' and 'mtext' in F['font khac khong co']['sources'], 'font dat bang ma \\f trong MTEXT: phat hien va bao thieu', F['font khac khong co'])
check(F['arial']['status'] == 'ok', 'Arial: co san', F['arial']['status'])
check(F['txt.shx']['shxKind'] == 'unifont' and F['txt.shx']['hint'] == 'Unicode', 'SHX: header unifont -> Unicode (txt.shx)', (F['txt.shx']['shxKind'], F['txt.shx']['hint']))
check('txt,romans' not in F and 'txt' not in F and 'romans' not in F, '\\Ftxt,romans khong bi coi la ten font "txt,romans"', sorted(F))
check(F.get('romans.shx', {}).get('status') == 'ok' and 'mtext' in F.get('romans.shx', {}).get('sources', []), '\\F: tach font va bigfont, them duoi .shx (romans.shx co san)', F.get('romans.shx'))
check((fb['meta']['ok'] >= 1, fb['meta']['inStore'], fb['meta']['missing']) == (True, 1, 3), 'tong: 1 trong kho, 3 thieu', (fb['meta']['inStore'], fb['meta']['missing']))

print('Khong cau hinh kho font')
Fn = fonts(fn)
check(fn['meta']['storeFiles'] == 0 and Fn['pkttdemo.shx']['status'] == 'missing', 'khong co kho thi pkttdemo.shx la thieu (khong tu doan)', (fn['meta']['storeFiles'], Fn['pkttdemo.shx']['status']))

print('Thay font Style')
st = {s['name']: s for s in sa['styles']}
check(st['S_NOSHX']['fontName'] == 'Segoe UI' and st['S_NOTTF']['fontName'] == 'Segoe UI', 'S_NOSHX va S_NOTTF da chuyen sang Segoe UI', (st['S_NOSHX']['fontName'], st['S_NOTTF']['fontName']))
check(st['S_ALUMNI']['fontName'].lower() == 'pkttdemo.shx', 'S_ALUMNI (co trong kho) khong bi thay', st['S_ALUMNI']['fontName'])
Fa = fonts(fa)
check(fa['meta']['missing'] == 1 and fa['meta']['inStore'] == 1, 'sau thay: con 1 thieu (font trong MTEXT, khong dong vao), 1 trong kho', (fa['meta']['missing'], fa['meta']['inStore']))
check(Fa['font khac khong co']['status'] == 'missing', 'font trong chuoi MTEXT khong bi sua')

print('Don Style')
names_after = set(st)
check('S_UNUSED' not in names_after and 'S_UNUSED2' not in names_after, 'S_UNUSED va S_UNUSED2 da xoa')
check({'Standard', 'S_ALUMNI', 'S_NOSHX', 'S_NOTTF', 'S_ARIAL'} <= names_after, 'Standard va style dang dung con nguyen', sorted(names_after))
names_before = {s['name'] for s in sb['styles']}
check({'S_UNUSED', 'S_UNUSED2'} <= names_before, 'truoc don: co S_UNUSED va S_UNUSED2')

print('Nhat ky, sao luu')
bk = glob.glob(os.path.join(t, '_backup', '*', '*.dwg'))
tags = sorted(re.sub(r'^.*_\d{6}_', '', os.path.basename(b)) for b in bk)
check(tags == ['truoc_PKTEXTFONTSUB.dwg', 'truoc_PKTEXTFONTSUB.dwg', 'truoc_PKTEXTPURGE.dwg', 'truoc_PKTEXTPURGE.dwg'], 'sao luu: 2 kich ban x (thay font + don), C khong tao', tags)
lg = os.path.join(t, '_backup', '_log.md')
check(os.path.exists(lg) and open(lg, encoding='utf-8').read().count('| PKTEXT') >= 4, 'nhat ky _log.md co 4 dong', os.path.exists(lg))

print('UNDO, huy')


def sig(d):
    return sorted((s['name'], s['fontName']) for s in d['styles'])


check(sig(su) == sig(sb), 'UNDO 2 lan tra ve y nguyen danh sach style va font')
check(sig(sc) == sig(sb), 'go khong phai YES: ban ve khong doi')

print('Script cai font va registry')
ps = open(os.path.join(t, 'cai_before.ps1'), encoding='utf-8').read()
check('pkttdemo.shx' in ps.lower() and 'pkttdemo.shx' in ps, 'script cai co tep pkttdemo.shx tu kho')
gate = ps.find('if ($Apply -and $RegisterFonts)')
reg = [m.start() for m in re.finditer(r'New-ItemProperty|Set-ItemProperty|HKCU:|reg add', ps)]
check(gate > 0 and reg and all(r > gate for r in reg), 'moi lenh ghi registry nam sau cong -RegisterFonts', (gate, reg))
check('param([switch]$Apply, [switch]$RegisterFonts)' in ps, 'mac dinh chi xem (can -Apply, -RegisterFonts)')
nst = open(os.path.join(t, 'cai_nostore.ps1'), encoding='utf-8').read()
check('Khong co font nao can cai tu kho' in nst, 'khong co kho thi script bao khong co gi de cai')
code = ''
for f in glob.glob(os.path.join(src, '*.cs')):
    code += open(f, encoding='utf-8-sig').read() + '\n'
code_wo_comments = re.sub(r'//.*', '', code)
check('Microsoft.Win32' not in code_wo_comments and 'RegistryKey' not in code_wo_comments, 'ma TextHub khong dung API registry')

print()
print('KET QUA: %s' % ('DAT' if not fails else 'CO LOI (%d)' % len(fails)))
sys.exit(0 if not fails else 1)
