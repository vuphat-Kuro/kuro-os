# -*- coding: utf-8 -*-
"""Kiểm tệp MCT do chương trình xuất: đọc lại CHỈ từ nội dung tệp (nút, phần tử, góc xoay, tiết diện, E, gối, tải BEAMLOAD),
dựng và giải lại khung phẳng bằng Python (numpy, dầm Euler 3 bậc tự do mỗi nút), rồi so chuyển vị nút và mômen đầu phần tử
với số chương trình đã giải (_dump.json). Chạy: python kiem_mct.py out_T1.mct T1  (tên tầng khớp khóa trong _dump.json)
Bản 2 (11/11/2026): tải dạng 8.7.5 (LINE UNILOAD, D1 P1 D2 P2), liên kết khớp *FRAME-RLS (khử tĩnh phần tử), kiểm trình tự khai báo và tham chiếu nút, phần tử.
Quy ước Midas (đã nêu trong tệp): ANGLE 90 = ván nằm, độ cứng trong mặt bằng là Ix; ANGLE 0 = ván đứng, là Iy.
Không kiểm được trong Midas thật; đây chỉ chứng minh tệp MCT mô tả đúng mô hình và tải mà chương trình đã giải."""
import sys, re, json
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
f, tier = sys.argv[1], sys.argv[2]
L = open(f, encoding='ascii', newline='').read().splitlines()
def block(name):
    out = []; on = False
    for ln in L:
        if ln.startswith('*'): on = ln.startswith(name)
        elif on and ln.strip() and not ln.lstrip().startswith(';'): out.append(ln)
    return out
nodes = np.array([[float(x) for x in ln.split(',')[1:3]] for ln in block('*NODE')])
els = [[x.strip() for x in ln.split(',')] for ln in block('*ELEMENT')]
sec_lines = [ln for ln in block('*SECTION')]
sec_cm = re.findall(r';\s+(\S+): A = ([\d.]+) cm2, Ix = ([\d.]+) cm4, Iy = ([\d.]+) cm4', '\n'.join(L))
secs = {}
for k, ln in enumerate(sec_lines):
    p = [x.strip() for x in ln.split(',')]; nm, A, Ix, Iy = sec_cm[k]
    m = 2.0 if p[2].startswith('2H') else 1.0
    secs[int(p[0])] = (m * float(A) * 1e-4, m * float(Ix) * 1e-8, m * float(Iy) * 1e-8)
E = float(next(ln for ln in block('*MATERIAL') if ln.lstrip()[0].isdigit() and 'STEEL' in ln).split(',')[10])
cons = {}
for ln in block('*CONSTRAINT'):
    a, c = ln.rsplit(',', 2)[0], ln.rsplit(',', 2)[1].strip()
    for n in a.split(): cons[int(n) - 1] = c
# trình tự khai báo: *UNIT trước *NODE trước *ELEMENT trước mọi *CONSTRAINT, *SPRING, *FRAME-RLS, *USE-STLD
order = []
for ln in L:
    if ln.startswith('*'):
        k = re.split(r'[\s,;]', ln)[0]
        if k not in order: order.append(k)
pos = {k: order.index(k) for k in order}
for a, b in [('*UNIT', '*NODE'), ('*NODE', '*ELEMENT'), ('*ELEMENT', '*MATERIAL'), ('*SECTION', '*STLDCASE'), ('*STLDCASE', '*CONSTRAINT'), ('*CONSTRAINT', '*USE-STLD')]:
    assert pos[a] < pos[b], f'sai trình tự: {a} phải đứng trước {b}'
for k in ('*FRAME-RLS', '*SPRING'):
    if k in pos: assert pos['*ELEMENT'] < pos[k] < pos['*USE-STLD'], f'{k} phải sau *ELEMENT, trước *USE-STLD'
assert order[0] == '*VERSION' and order[1] == '*UNIT', 'đơn vị phải ở ngay đầu tệp'
assert any(ln.strip().startswith('TONF , M,') for ln in L), 'đơn vị TONF, M'
nN, nE = len(nodes), len(els)
for e in els: assert 1 <= int(e[4]) <= nN and 1 <= int(e[5]) <= nN, 'phần tử tham chiếu nút chưa khai báo'
cases = {}; cur = None; on = False
for ln in L:
    if ln.startswith('*USE-STLD'): cur = ln.split(',')[1].strip(); cases[cur] = {}; on = False
    elif ln.startswith('*BEAMLOAD'): on = True
    elif ln.startswith('*') and not ln.startswith('*BEAMLOAD'): on = False
    elif on and cur and ln.strip() and not ln.lstrip().startswith(';'):
        p = [x.strip() for x in ln.split(',')]
        assert p[1] == 'LINE' and p[2] == 'UNILOAD' and p[10] == '0' and p[12] == '1', ln
        e = int(p[0]) - 1; d = p[3]; v = float(p[11]); assert 0 <= e < nE and abs(float(p[13]) - v) < 1e-12
        cases[cur].setdefault(e, [0.0, 0.0]); cases[cur][e][0 if d == 'GX' else 1] += v
rls = {}
rl = block('*FRAME-RLS')
for k in range(0, len(rl), 2):
    a = [x.strip() for x in rl[k].split(',')]; b = [x.strip() for x in rl[k + 1].split(',')]
    e = int(a[0]) - 1; assert 0 <= e < nE
    rls[e] = (any(c == '1' for c in a[2][4:]), any(c == '1' for c in b[0][4:]))   # nhả mômen uốn (Mx My Mz) ở đầu i, đầu j; chỉ lấy My, Mz
n = len(nodes); ndof = 3 * n
data = json.load(open(sys.argv[3] if len(sys.argv) > 3 else '_dump.json', encoding='utf-8'))[tier]
tot_bad = []; worst = {}
Ks = None
geo = []
for e in els:
    n1, n2 = int(e[4]) - 1, int(e[5]) - 1; ang = float(e[6]); A, Ix, Iy = secs[int(e[3])]
    I = Ix if abs(ang - 90) < 1e-9 else Iy
    dx, dy = nodes[n2] - nodes[n1]; Le = float(np.hypot(dx, dy)); c, s = dx / Le, dy / Le
    geo.append((n1, n2, A, I, Le, c, s))
def solve(load):
    K = np.zeros((ndof, ndof)); F = np.zeros(ndof); ends = []
    for k, (n1, n2, A, I, Le, c, s) in enumerate(geo):
        a, b = E * A / Le, E * I / Le ** 3
        kl = np.array([[a, 0, 0, -a, 0, 0], [0, 12*b, 6*b*Le, 0, -12*b, 6*b*Le], [0, 6*b*Le, 4*b*Le*Le, 0, -6*b*Le, 2*b*Le*Le],
                       [-a, 0, 0, a, 0, 0], [0, -12*b, -6*b*Le, 0, 12*b, -6*b*Le], [0, 6*b*Le, 2*b*Le*Le, 0, -6*b*Le, 4*b*Le*Le]])
        T = np.zeros((6, 6)); R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]); T[:3, :3] = R; T[3:, 3:] = R
        dof = [3*n1, 3*n1+1, 3*n1+2, 3*n2, 3*n2+1, 3*n2+2]
        wx, wy = load.get(k, [0.0, 0.0]); qa, qt = wx * c + wy * s, -wx * s + wy * c
        fl = np.array([qa * Le / 2, qt * Le / 2, qt * Le ** 2 / 12, qa * Le / 2, qt * Le / 2, -qt * Le ** 2 / 12])
        for r in [i for i, on_ in zip((2, 5), rls.get(k, (False, False))) if on_]:
            col = kl[:, r].copy(); piv = kl[r, r]
            fl = fl - col * fl[r] / piv; kl = kl - np.outer(col, kl[r, :]) / piv
        K[np.ix_(dof, dof)] += T.T @ kl @ T
        F[dof] += T.T @ fl; ends.append((kl, T, fl, dof))
    fixed = []
    for i, code in cons.items():
        if code[0] == '1': fixed.append(3 * i)
        if code[1] == '1': fixed.append(3 * i + 1)
        if code[5] == '1': fixed.append(3 * i + 2)
    free = [i for i in range(ndof) if i not in set(fixed)]
    U = np.zeros(ndof); U[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    Mend = [(lambda r: (r[2], r[5]))(ends[k][0] @ (ends[k][1] @ U[ends[k][3]]) - ends[k][2]) for k in range(len(geo))]
    return U, Mend
print(f'{f}: {n} nút, {len(els)} phần tử, E = {E:.4g} T/m2, {len(cases)} trường hợp tải')
for st in data:
    load = cases.get(st['tag']);
    if load is None: print('thiếu trường hợp', st['tag']); continue
    U, Mend = solve(load)
    ref = np.array([[nd[2], nd[3]] for nd in st['nodes']]).reshape(-1); Ut = U.reshape(-1, 3)[:, :2].reshape(-1)   # chỉ so chuyển vị tịnh tiến (góc xoay nút có khớp nhả hết là tùy ý)
    du = np.max(np.abs(Ut - ref)); scale = np.max(np.abs(ref))
    Mref = np.array([[abs(x) for x in el['M']] for el in st['elements'] if el['M']]); Mmy = np.array([[abs(a), abs(b)] for a, b in Mend])
    dM = np.max(np.abs(np.sort(Mref.ravel()) - np.sort(Mmy.ravel()))); Mmax = np.max(Mref)
    print(f"{st['tag']}: chuyển vị lớn nhất {scale*1000:.4f} mm, lệch {du/scale:.2e} tương đối | M lớn nhất {Mmax:.4f} T.m, lệch {dM/max(Mmax,1e-9):.2e}")
    worst['u'] = max(worst.get('u', 0), du / scale); worst['M'] = max(worst.get('M', 0), dM / max(Mmax, 1e-9))
print('lệch lớn nhất:', {k: f'{v:.2e}' for k, v in worst.items()})
