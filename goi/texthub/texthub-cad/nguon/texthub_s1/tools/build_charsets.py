# -*- coding: utf-8 -*-
"""Dung data/charsets.csv va src/Core/CharsetData.g.cs tu cac nguon doi chieu.

Chay: python -X utf8 -I build_charsets.py
Quy tac:
  - Tap 134 chu Viet do quy tac sinh (khong phu thuoc nguon).
  - TCVN3: byte lay tu BVC, phai trung LISP v2.6 o 74 muc chung; chu HOA co dau dung byte cua chu thuong (font H).
  - VNI: lay tu BVC; muc LISP v2.6 khac duoc ghi 'LISP_KHAC' (bug cua LISP).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_tables as E  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))


def main():
    letters = E.viet_letters()
    uni, tc, vn = E.bvc_decoded()
    assert set(uni) == letters and len(uni) == 134, 'BVC khong khop 134 chu quy tac'

    A = E.parse_lsp_tables()
    lisp_tc = {chr(u): bytes([b]) for b, u in A['TCVN3_MAP'].items()}
    lisp_vn = {chr(u): bytes(seq) for seq, u in A['VNI_MAP'].items()}

    rows = []
    problems = []
    for u, t, v in zip(uni, tc, vn):
        assert len(t) == 1
        # TCVN3
        if u in lisp_tc:
            if lisp_tc[u] != t:
                problems.append('TCVN3 khac: %r LISP=%r BVC=%r' % (u, lisp_tc[u], t))
            tsrc = 'LISP=BVC'
            tflag = ''
        else:
            tsrc = 'BVC(font H)'
            tflag = 'H'
        # VNI
        if u in lisp_vn:
            vsrc = 'LISP=BVC' if lisp_vn[u] == v else 'BVC;LISP_KHAC=' + lisp_vn[u].hex()
        else:
            vsrc = 'BVC'
        rows.append((ord(u), u, t.hex(), tflag, tsrc, v.hex(), vsrc))
    rows.sort()
    assert not problems, problems

    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'charsets.csv'), 'w', encoding='utf-8', newline='') as f:
        f.write('unicode,char,tcvn3_hex,tcvn3_font_H,tcvn3_nguon,vni_hex,vni_nguon\n')
        for r in rows:
            f.write('U+%04X,%s,%s,%s,%s,%s,%s\n' % r)

    # C# du lieu (chuoi 'U+XXXX|tcvn|H|vni')
    os.makedirs(os.path.join(ROOT, 'src', 'Core'), exist_ok=True)
    lines = []
    lines.append('// TU DONG SINH boi tools/build_charsets.py tu data/charsets.csv. KHONG SUA TAY.')
    lines.append('namespace Pkttc.Text.Core')
    lines.append('{')
    lines.append('    internal static class CharsetData')
    lines.append('    {')
    lines.append('        // Dinh dang: codepoint(hex)|tcvn3 byte(hex)|H neu chi dung duoc voi font HOA|vni byte(hex, cach bang dau cach)')
    lines.append('        internal static readonly string[] Rows = new string[]')
    lines.append('        {')
    for r in rows:
        vni = ' '.join(r[5][i:i + 2] for i in range(0, len(r[5]), 2))
        lines.append('            "%04X|%s|%s|%s",' % (r[0], r[2].upper(), r[3], vni.upper()))
    lines.append('        };')
    lines.append('    }')
    lines.append('}')
    os.makedirs(os.path.join(ROOT, 'src', 'Core'), exist_ok=True)
    open(os.path.join(ROOT, 'src', 'Core', 'CharsetData.g.cs'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

    n_h = sum(1 for r in rows if r[3] == 'H')
    n_conf = sum(1 for r in rows if 'LISP_KHAC' in r[6])
    print('134 dong. TCVN3 font H: %d. VNI LISP khac BVC: %d.' % (n_h, n_conf))


if __name__ == '__main__':
    main()
