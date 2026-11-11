# -*- coding: utf-8 -*-
"""Kiểm tệp MCT dầm cừ dải 1 m do chương trình xuất: đọc lại CHỈ từ nội dung tệp (nút theo Z, phần tử, tiết diện SB, E, gối, *SPRING,
*BEAMLOAD hình thang theo từng trường hợp tải, *LOADCOMB), dựng và giải lại dầm Euler bằng Python, so chuyển vị tại nút và mômen đầu phần tử
với số chương trình đã giải trên lưới 100 phần tử (_dumpB.json). Lưới tệp là tập con của lưới chương trình (đã gộp phần tử), nên so tại các nút còn giữ.
Kiểm cả trình tự khai báo và tham chiếu nút, phần tử.
Chạy: python kiem_mct_cu.py <tep.mct> <chi so giai doan trong dump> [dump.json]
Quy ước: x = độ sâu từ đỉnh cừ (x = Z_đỉnh - Z), chuyển vị v theo +X (phía hố), như bộ giải của chương trình; so |M| và v."""
import sys, re, json
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
f, idx = sys.argv[1], sys.argv[2]
DUMP = sys.argv[3] if len(sys.argv) > 3 else '_dumpB.json'
L = open(f, encoding='ascii', newline='').read().splitlines()
def block(name):
    out = []; on = False
    for ln in L:
        if ln.startswith('*'): on = ln.startswith(name)
        elif on and ln.strip() and not ln.lstrip().startswith(';'): out.append(ln)
    return out
def expand(txt):  # "1to5 8" -> [1,2,3,4,5,8]
    r = []
    for t in txt.split():
        m = re.fullmatch(r'(\d+)to(\d+)', t)
        r += list(range(int(m.group(1)), int(m.group(2)) + 1)) if m else [int(t)]
    return r
order = []
for ln in L:
    if ln.startswith('*'):
        k = re.split(r'[\s,;]', ln)[0]
        if k not in order: order.append(k)
pos = {k: i for i, k in enumerate(order)}
assert order[0] == '*VERSION' and order[1] == '*UNIT' and any(ln.strip().startswith('TONF , M,') for ln in L), 'don vi phai o dau tep'
for a, b in [('*NODE', '*ELEMENT'), ('*ELEMENT', '*SECTION'), ('*SECTION', '*STLDCASE'), ('*STLDCASE', '*CONSTRAINT'), ('*CONSTRAINT', '*SPRING'), ('*SPRING', '*USE-STLD'), ('*USE-STLD', '*LOADCOMB')]:
    if a in pos and b in pos: assert pos[a] < pos[b], f'sai trinh tu {a} / {b}'
nodes = [float(ln.split(',')[3]) for ln in block('*NODE')]            # Z
els = [[x.strip() for x in ln.split(',')] for ln in block('*ELEMENT')]
nN, nE = len(nodes), len(els)
for k, e in enumerate(els): assert int(e[4]) == k + 1 and int(e[5]) == k + 2 and 1 <= int(e[5]) <= nN
sec = [x.strip() for x in block('*SECTION')[0].split(',')]; assert sec[12] == 'SB', sec
a = float(sec[14]); I = a ** 4 / 12
E = float(next(ln for ln in block('*MATERIAL') if ln.lstrip()[0].isdigit() and 'STEEL' in ln).split(',')[10])
EI = E * I
fixDx, fixRy = set(), set()
for ln in block('*CONSTRAINT'):
    ns, c = ln.rsplit(',', 2)[0], ln.rsplit(',', 2)[1].strip()
    for n in expand(ns):
        assert 1 <= n <= nN; assert n - 1 not in fixDx | fixRy
        if c[0] == '1': fixDx.add(n - 1)
        if c[4] == '1': fixRy.add(n - 1)
spr = {}
for ln in block('*SPRING'):
    p = [x.strip() for x in ln.split(',')]
    for n in expand(p[0]): assert 1 <= n <= nN; spr[n - 1] = spr.get(n - 1, 0) + float(p[2])
cases = {}; cur = None; on = False
for ln in L:
    if ln.startswith('*USE-STLD'): cur = ln.split(',')[1].strip(); cases[cur] = {}; on = False
    elif ln.startswith('*BEAMLOAD'): on = True
    elif ln.startswith('*'): on = False
    elif on and cur and ln.strip() and not ln.lstrip().startswith(';'):
        p = [x.strip() for x in ln.split(',')]
        assert p[1] == 'LINE' and p[2] == 'UNILOAD' and p[3] == 'GX' and p[10] == '0' and p[12] == '1', ln
        e = int(p[0]); assert 1 <= e <= nE; cases[cur][e - 1] = (float(p[11]), float(p[13]))
combos = {}; cl = block('*LOADCOMB')
for k in range(0, len(cl), 2):
    nm = re.match(r'\s*NAME=([^,]+),', cl[k]).group(1).strip(); t = [x.strip() for x in cl[k + 1].split(',')]
    combos[nm] = [(t[j + 1], float(t[j + 2])) for j in range(0, len(t), 3)]
    for tg, _ in combos[nm]: assert tg in cases, f'to hop {nm} tham chieu {tg} chua co'
ztop = nodes[0]; X = [ztop - z for z in nodes]
assert all(X[i + 1] > X[i] for i in range(nN - 1)), 'nut phai di tu dinh xuong day'
nd = 2 * nN; K = np.zeros((nd, nd))
for k in range(nE):
    le = X[k + 1] - X[k]; b = EI / le ** 3
    ke = b * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le * le, -6 * le, 2 * le * le], [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le * le, -6 * le, 4 * le * le]])
    d = [2 * k, 2 * k + 1, 2 * k + 2, 2 * k + 3]; K[np.ix_(d, d)] += ke
for n, kx in spr.items(): K[2 * n, 2 * n] += kx
fixed = sorted([2 * n for n in fixDx] + [2 * n + 1 for n in fixRy]); free = [i for i in range(nd) if i not in set(fixed)]
def solve(ld):
    F = np.zeros(nd)
    for k in range(nE):
        le = X[k + 1] - X[k]; qa, qb = ld.get(k, (0.0, 0.0)); d = [2 * k, 2 * k + 1, 2 * k + 2, 2 * k + 3]
        F[d] += np.array([le * (7 * qa + 3 * qb) / 20, le ** 2 * (3 * qa + 2 * qb) / 60, le * (3 * qa + 7 * qb) / 20, -le ** 2 * (2 * qa + 3 * qb) / 60])
    U = np.zeros(nd); U[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    M = []   # mômen đầu i từng phần tử theo lực đầu phần tử (như Midas): m1 = (ke u - fe)[1], M = m1 (cùng dấu với M = -EI v'' của chương trình)
    for k in range(nE):
        le = X[k + 1] - X[k]; bb = EI / le ** 3; qa, qb = ld.get(k, (0.0, 0.0))
        ke = bb * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le * le, -6 * le, 2 * le * le], [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le * le, -6 * le, 4 * le * le]])
        fe = np.array([le * (7 * qa + 3 * qb) / 20, le ** 2 * (3 * qa + 2 * qb) / 60, le * (3 * qa + 7 * qb) / 20, -le ** 2 * (2 * qa + 3 * qb) / 60])
        M.append((ke @ U[2 * k:2 * k + 4] - fe)[1])
    return U, np.array(M)
res = {k: solve(c) for k, c in cases.items()}
def comb(items): return sum(fct * res[t][0] for t, fct in items), sum(fct * res[t][1] for t, fct in items)
ref = json.load(open(DUMP, encoding='utf-8'))[idx]
Xp = ref['X']; pi = [int(np.argmin([abs(x - xp) for xp in Xp])) for x in X]
assert all(abs(Xp[j] - x) < 1e-6 for j, x in zip(pi, X)), 'nut tep khong nam tren luoi chuong trinh'
mom = np.array(ref['mom'])                   # tại nút đầu mỗi phần tử của lưới chương trình: x, M, v (mm)
out = []
def cmp(U, M, Mref, name):
    vref = np.array([mom[j][2] for j in pi[:-1]]); v = U[0::2][:nN - 1] * 1000
    Mr = np.array([Mref[j] for j in pi[:-1]])
    du = np.max(np.abs(v - vref)) / max(np.max(np.abs(vref)), 1e-9); dM = np.max(np.abs(M - Mr)) / max(np.max(np.abs(Mr)), 1e-9)
    out.append(f"{name}: v max {np.max(np.abs(vref)):.4f} mm lech {du:.2e} | M max {np.max(np.abs(Mr)):.4f} T.m lech {dM:.2e}")
Mprog = mom[:, 1]; Mtot = np.array(ref['Mtot']) if ref.get('Mtot') else Mprog
tag = [k for k in cases if not k.endswith(('_N', '_D'))]
if tag: U, M = res[tag[0]]; cmp(U, M, Mprog, tag[0])
else:
    Ut, Mt = comb(combos[[c for c in combos if c.endswith('_TongTai')][0]]); U7, M7 = comb(combos[[c for c in combos if c.endswith('_7-14')][0]])
    cmp(Ut, M7, Mprog, '7-14 (M to hop; v la v tong tai)'); cmp(Ut, Mt, Mtot, 'tong tai')
print(f"{f.split('/')[-1]}: {nN} nut (luoi chuong trinh {len(Xp)}), {nE} phan tu, {len(spr)} lo xo, {len(cases)} truong hop, EI = {EI:.4f} | " + ' | '.join(out))
