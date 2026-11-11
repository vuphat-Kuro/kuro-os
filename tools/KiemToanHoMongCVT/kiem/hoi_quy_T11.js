// Hồi quy T11: dấu vân tay 5 vùng (bảng tổng hợp, chi tiết kiểm toán, khung mặt bằng, thuyết minh cũ, 40 tỷ số sử dụng), 07/11/2026.
// Nạp ngay sau khi trang mở (bộ số T11 mặc định), rồi gọi await hoiQuyT11(). So kết quả trước và sau mỗi lần sửa chương trình.
// Bỏ mã engine E- và dấu thời gian vì đổi theo mã nguồn và giờ chạy.
async function hoiQuyT11() {
  runCalculation();
  const sach = t => String(t || '').replace(/E-[0-9A-F]{8}/g, 'E-x').replace(/\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}/g, 't').replace(/\d{4}-\d{2}-\d{2}T[\d:.]+Z/g, 't');
  const fnv = s => { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16); };
  const txt = id => { const e = document.getElementById(id); return e ? sach(e.innerText) : '(không có)'; };
  const vung = {
    tong_hop: txt('summaryTableBody'),
    chi_tiet: txt('modulesDetailContainer'),
    khung_mat_bang: ['planFemKpiContainer', 'planFrameFemTableBody'].map(txt).join('|'),
    thuyet_minh_cu: txt('printDossierContainer'),
    ty_so_40: sach(JSON.stringify(v18Rows().slice(0, 40).map(x => [x.grp, x.item, x.where, x.dc, x.ratio, x.ok, x.kind])))
  };
  const out = {}; Object.entries(vung).forEach(([k, v]) => out[k] = fnv(v) + ' (' + v.length + ')');
  out.so_dong_ty_so = v18Rows().length; // 40 dòng gốc; W1 thêm dòng mối hàn ở cuối, ty_so_40 so 40 dòng đầu
  return out;
}

// A4 (07/11/2026): kiểm thử lưới dầm FEM, rút từ bài học B13 (hai nút cách nhau 1e-9 m làm kết quả phụ thuộc số phần tử).
// kiemLuoi(chayCa, dungSai): chạy chayCa (mặc định runCalculation, tức ca đang nạp), ghi lại mọi lần gọi solveBeamFEM1D,
// giải lại từng lần ở lưới 100 và 400 phần tử rồi so mômen lớn nhất và phản lực từng gối.
// Lệch = |a - b| / max(a, b, mômen lớn nhất của cả ca) với mômen; tương tự với phản lực (sàn = phản lực lớn nhất của cả ca).
// Sàn theo cả ca để thành phần rất nhỏ (vài phần trăm T.m) không báo lỗi giả. Đạt khi mọi lần gọi lệch ≤ dungSai (mặc định 0,5%).
// Ví dụ: kiemLuoi(() => caT25(1.2, 0.8)). Không đổi chương trình và không đổi hoiQuyT11.
function kiemLuoi(chayCa, dungSai) {
  dungSai = dungSai === undefined ? 0.005 : dungSai;
  const goc = solveBeamFEM1D, goi = [];
  solveBeamFEM1D = function () { goi.push(Array.from(arguments)); return goc.apply(this, arguments); };
  try { (chayCa || runCalculation)(); } finally { solveBeamFEM1D = goc; }
  const Mx = r => Math.max(...r.moments.map(m => Math.abs(m.M)));
  const kq = goi.map(a => ({ a, r1: goc(a[0], a[1], a[2], a[3], 100, a[5]), r4: goc(a[0], a[1], a[2], a[3], 400, a[5]) }));
  const sanM = Math.max(0.01, ...kq.map(k => Mx(k.r4))), sanR = Math.max(0.01, ...kq.map(k => Math.max(...k.r4.reactions.map(x => Math.abs(x.R)))));
  const vuot = []; let lechM = 0, lechR = 0;
  kq.forEach((k, i) => {
    const m1 = Mx(k.r1), m4 = Mx(k.r4);
    const dM = Math.abs(m1 - m4) / Math.max(m1, m4, sanM);
    const dR = Math.max(0, ...k.r1.reactions.map((x, j) => Math.abs(x.R - k.r4.reactions[j].R) / Math.max(Math.abs(x.R), Math.abs(k.r4.reactions[j].R), sanR)));
    lechM = Math.max(lechM, dM); lechR = Math.max(lechR, dR);
    if (dM > dungSai || dR > dungSai) vuot.push({ lan: i, L: +k.a[0].toFixed(3), goi: k.a[2].map(s => s.name + '@' + s.pos.toFixed(2)).join(' '), M100: +m1.toFixed(3), M400: +m4.toFixed(3), lechM: +dM.toFixed(4), lechR: +dR.toFixed(4) });
  });
  return { so_lan_goi: goi.length, lech_M_max: +lechM.toFixed(5), lech_R_max: +lechR.toFixed(5), dung_sai: dungSai, so_lan_vuot: vuot.length, dat: vuot.length === 0 && goi.length > 0, vuot };
}
