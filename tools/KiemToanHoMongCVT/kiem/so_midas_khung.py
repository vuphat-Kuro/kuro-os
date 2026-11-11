# -*- coding: utf-8 -*-
"""So bảng Midas (Beam Force.xls, Beam Stress.xls) với kết quả chương trình (_prog_T2_GD4.json) cho khung chống một tầng, một giai đoạn.
Chạy: python so_midas_khung.py <Beam Force.xls> <Beam Stress.xls> <prog.json>"""
import sys, json, re
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
bf = pd.read_excel(sys.argv[1], header=None).iloc[2:].reset_index(drop=True)
bs = pd.read_excel(sys.argv[2], header=None).iloc[2:].reset_index(drop=True)
P = json.load(open(sys.argv[3], encoding='utf-8')); els = P['els']
ne = len(els)
# Midas: mỗi phần tử 5 dòng (I, 1/4, 2/4, 3/4, J); cột Elem là số
bf = bf[pd.to_numeric(bf[3], errors='coerce').notna()].reset_index(drop=True); bs = bs[pd.to_numeric(bs[2], errors='coerce').notna()].reset_index(drop=True)
print('dòng Midas', len(bf), len(bs), 'phần tử chương trình', ne)
t = np.array([0, .25, .5, .75, 1.0])
rows = []
for i, e in enumerate(els):
    sel = bf[bf[3].astype(float) == i + 1]; sel2 = bs[bs[2].astype(float) == i + 1]
    assert len(sel) == 5 and len(sel2) == 5, (i, len(sel), len(sel2))
    N_m = sel[11].astype(float).values / 1000                      # T
    Vz, Vy = sel[13].astype(float).values / 1000, sel[12].astype(float).values / 1000
    My, Mz = sel[15].astype(float).values / 1e5, sel[16].astype(float).values / 1e5   # T.m
    V_m = Vz if np.abs(Vz).max() >= np.abs(Vy).max() else Vy; M_m = My if np.abs(My).max() >= np.abs(Mz).max() else Mz
    L = e['L']; q = e['q'] or 0
    xl = t * L; Mp = e['M1'] * (1 - t) - e['M2'] * t + q * xl * (L - xl) / 2; Vp = e['V1'] * (1 - t) + e['V2'] * t
    sax = sel2[10].astype(float).values; cbmm = sel2[17].astype(float).values
    A, W = e['A'], e['W']
    sNp = e['N'] / A * 0.1; sbp = Mp / W * 0.1
    cbp = np.where(np.abs(sNp - np.abs(sbp)) > np.abs(sNp + np.abs(sbp)), sNp - np.abs(sbp), sNp + np.abs(sbp))
    # dấu M, V có thể ngược quy ước: lấy dấu khớp nhất
    sM = 1 if np.abs(M_m - Mp).max() <= np.abs(M_m + Mp).max() else -1
    sV = 1 if np.abs(V_m - Vp).max() <= np.abs(V_m + Vp).max() else -1
    rows.append(dict(i=i + 1, name=e['name'], orient=e['orient'], rel=e['rel'], Nm=N_m[0], Np=e['N'], dN=np.abs(N_m - e['N']).max(), dV=np.abs(V_m - sV * Vp).max(), sV=sV, dM=np.abs(M_m - sM * Mp).max(), sM=sM, Mmax=np.abs(Mp).max(),
                     dsax=np.abs(sax - sNp).max(), dcb=np.abs(cbmm - cbp).max(), cbmax=np.abs(cbp).max(), Mm_max=np.abs(M_m).max(), W=W))
d = pd.DataFrame(rows)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
print('so phan tu', ne); print('lệch lớn nhất: N', d.dN.max().round(3), 'T | V', d.dV.max().round(3), 'T | M', d.dM.max().round(3), 'T.m | σ dọc trục', d.dsax.max().round(2), '| Cb(min/max)', d.dcb.max().round(1), 'kg/cm2')
print('tỉ lệ M lệch tương đối max:', (d.dM / d.Mmax.clip(lower=0.5)).max().round(4))
print('dấu M khác nhau giữa phần tử:', d.sM.value_counts().to_dict(), ' dấu V:', d.sV.value_counts().to_dict())
bad = d[(d.dN > 0.5) | (d.dM > 0.3) | (d.dV > 0.5)]
print('phần tử lệch (N>0.5T hoặc M>0.3 T.m hoặc V>0.5T):', len(bad)); print(bad[['i', 'name', 'orient', 'rel', 'Nm', 'Np', 'dN', 'dV', 'dM', 'Mmax', 'Mm_max']].to_string())
d.to_csv('so_midas_khung.csv', index=False)
