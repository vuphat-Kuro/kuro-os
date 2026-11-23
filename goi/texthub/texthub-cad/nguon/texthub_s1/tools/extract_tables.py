# -*- coding: utf-8 -*-
"""Rut bang ma TCVN3 / VNI tu 3 nguon doc lap de doi chieu (chay: python -X utf8 -I extract_tables.py).

Nguon:
  A. LISP v2.6 cua phong (VnFontConvert_PKTTC.lsp)
  B. BVC CF free (ban dich nguoc, fas_cf_free/m2_decomp.lsp, doc o dang byte)
  C. Quy tac sinh: 134 chu cai Viet dung san Unicode (NFC) sinh tu quy tac, khong phu thuoc nguon nao.
Dau ra: data/charsets.csv va tools/doi_chieu.txt
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
TEMP = os.path.abspath(os.path.join(ROOT, '..'))
LSP = os.path.join(TEMP, 'VFCC', 'VnFontConvert_PKTTC.lsp')
BVC = os.path.join(TEMP, 'fas_cf_free', 'm2_decomp.lsp')

BS = chr(92)


def viet_letters():
    """134 chu cai tieng Viet dung san (67 chu thuong + 67 chu hoa) sinh tu quy tac."""
    bases = 'aăâeêioôơuưy'
    tones = [0x0300, 0x0301, 0x0309, 0x0303, 0x0323]  # huyen sac hoi nga nang
    out = set()
    for b in bases:
        out.add(b)
        for t in tones:
            c = unicodedata.normalize('NFC', b + chr(t))
            if len(c) == 1:
                out.add(c)
    out.add('đ')
    out |= set(c.upper() for c in list(out))
    # chi giu chu Viet (loai a,e,i,o,u,y khong dau)
    out = set(c for c in out if ord(c) > 127)
    return out


def parse_lsp_tables():
    s = open(LSP, encoding='utf-8', errors='replace').read()

    def block(name):
        m = re.search(r'\(setq \*PKTTC:' + name + r'\*\s*\(list(.*?)\n\)\)', s, re.S)
        return m.group(1) if m else ''

    res = {}
    # byte -> unicode (TCVN3 thuong va HOA)
    for nm in ('TCVN3_MAP', 'TCVN3_UPPER_MAP'):
        t = {}
        for m in re.finditer(r'\(cons (\d+) "\\\\U\+([0-9A-Fa-f]{4})"\)', block(nm)):
            t[int(m.group(1))] = int(m.group(2), 16)
        res[nm] = t
    # VNI: (list b1 [b2]) -> unicode
    t = {}
    for m in re.finditer(r"\(cons '\(([\d ]+)\) \"\\\\U\+([0-9A-Fa-f]{4})\"\)", block('VNI_MAP')):
        seq = tuple(int(x) for x in m.group(1).split())
        t[seq] = int(m.group(2), 16)
    res['VNI_MAP'] = t
    return res


def parse_bvc_tables():
    """Doc cac cot 'unicode', 'tcvn', 'vni' cua CHARCODETABLE trong ban dich nguoc (dang byte)."""
    b = open(BVC, 'rb').read()
    m0 = re.search(rb'CHARCODETABLE\s*\(LIST', b)
    seg = b[m0.start():m0.start() + 400000]
    cols = {}
    for nm in (b'unicode', b'tcvn', b'vni'):
        j = seg.find(b'"' + nm + b'"')
        if j < 0:
            continue
        k = seg.find(b'(LIST', j)
        # lay cac chuoi cho den dau ngoac dong cua LIST
        depth = 0
        pos = k
        items = []
        cur = None
        while pos < len(seg):
            ch = seg[pos:pos + 1]
            if cur is None:
                if ch == b'(':
                    depth += 1
                elif ch == b')':
                    depth -= 1
                    if depth == 0:
                        break
                elif ch == b'"':
                    cur = bytearray()
            else:
                if ch == b'"':
                    items.append(bytes(cur))
                    cur = None
                elif ch == b'\\' and seg[pos + 1:pos + 2] == b'\\':
                    cur.append(92)
                    pos += 1
                elif ch == b'\\' and seg[pos + 1:pos + 2] == b'"':
                    cur.append(34)
                    pos += 1
                else:
                    cur.extend(ch)
            pos += 1
        cols[nm.decode()] = items
    return cols


def bvc_decoded():
    """Tra ve (unicode_list, tcvn_list_bytes, vni_list_bytes) cua BVC, cung thu tu."""
    C = parse_bvc_tables()
    uni = []
    for e in C['unicode']:
        m = re.match(rb'\\U\+([0-9A-Fa-f]{4})$', e)
        uni.append(chr(int(m.group(1), 16)) if m else e.decode('cp1252'))
    return uni, [bytes(x) for x in C['tcvn']], [bytes(x) for x in C['vni']]


def main():
    out = []
    letters = viet_letters()
    out.append('Chu cai Viet sinh tu quy tac: %d (ky vong 134)' % len(letters))

    A = parse_lsp_tables()
    out.append('Nguon A (LISP): TCVN3_MAP=%d, TCVN3_UPPER_MAP=%d, VNI_MAP=%d' % (
        len(A['TCVN3_MAP']), len(A['TCVN3_UPPER_MAP']), len(A['VNI_MAP'])))

    C = parse_bvc_tables()
    for k, v in C.items():
        out.append('Nguon B (BVC) cot %s: %d muc' % (k, len(v)))

    # Giai ma cot unicode cua BVC: "\U+xxxx" hoac 1 byte cp1252
    uni = []
    for e in C.get('unicode', []):
        m = re.match(rb'\\U\+([0-9A-Fa-f]{4})$', e)
        if m:
            uni.append(chr(int(m.group(1), 16)))
        elif len(e) == 1:
            uni.append(e.decode('cp1252', errors='replace'))
        else:
            uni.append('?')
    out.append('BVC unicode: duy nhat=%d, khop quy tac=%s' % (len(set(uni)), set(uni) == letters))
    miss = sorted(letters - set(uni))
    extra = sorted(set(uni) - letters)
    out.append('  thieu so voi quy tac: %s | thua: %s' % (miss, extra))

    # TCVN3 cot BVC: moi muc la chuoi byte (1 hoac 2 byte)
    tc = [tuple(e) for e in C.get('tcvn', [])]
    vn = [tuple(e) for e in C.get('vni', [])]
    out.append('BVC tcvn do dai: ' + str({n: sum(1 for x in tc if len(x) == n) for n in (1, 2, 3)}))
    out.append('BVC vni do dai: ' + str({n: sum(1 for x in vn if len(x) == n) for n in (1, 2, 3)}))

    # Bang hop nhat: ky tu -> tcvn byte (BVC) va (LISP)
    bvc_tc = {}
    bvc_vn = {}
    if len(uni) == len(tc) == len(vn):
        for u, t, v in zip(uni, tc, vn):
            bvc_tc[u] = t
            bvc_vn[u] = v
    lisp_tc_lower = {chr(u): bytes([b]) for b, u in A['TCVN3_MAP'].items()}
    lisp_vn = {chr(u): bytes(seq) for seq, u in A['VNI_MAP'].items()}

    def cmp(name, x, y):
        keys = set(x) & set(y)
        diff = [(k, x[k], y[k]) for k in sorted(keys) if x[k] != y[k]]
        out.append('%s: chung=%d, khac=%d' % (name, len(keys), len(diff)))
        for k, a, b in diff[:20]:
            out.append('   %r  A=%r  B=%r' % (k, a, b))

    cmp('TCVN3 thuong (LISP vs BVC)', lisp_tc_lower, {k: bytes(v) for k, v in bvc_tc.items() if len(v) == 1})
    cmp('VNI (LISP vs BVC)', lisp_vn, {k: bytes(v) for k, v in bvc_vn.items()})

    open(os.path.join(HERE, 'doi_chieu.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
