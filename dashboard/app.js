const $ = (id) => document.getElementById(id);

// Helper render biểu tượng Lucide Icons & SVG chuyên ngành KURO từ Inline Sprite (#kuro-icon-sprite)
function kuroIcon(id, sizeCls = "ic-sm", colorCls = "") {
  const cls = ["ic", sizeCls, colorCls].filter(Boolean).join(" ");
  return `<svg class="${cls}" aria-hidden="true"><use href="#${id}"/></svg>`;
}

// ========================================================
// NHẬN DIỆN TỆP XUẤT RA TRONG CÂU TRẢ LỜI KURO & MENU MỞ BẰNG WINDOWS
// ========================================================
const KURO_FILE_META = {
  xlsx: { icon: "📊", iconId: "ic-file-spreadsheet", colorCls: "ic-xls", app: "Excel (Windows)", text: false },
  xls:  { icon: "📊", iconId: "ic-file-spreadsheet", colorCls: "ic-xls", app: "Excel (Windows)", text: false },
  xlsm: { icon: "📊", iconId: "ic-file-spreadsheet", colorCls: "ic-xls", app: "Excel (Windows)", text: false },
  xlsb: { icon: "📊", iconId: "ic-file-spreadsheet", colorCls: "ic-xls", app: "Excel (Windows)", text: false },
  csv:  { icon: "📊", iconId: "ic-file-spreadsheet", colorCls: "ic-xls", app: "Excel / ứng dụng mặc định", text: true },
  docx: { icon: "📝", iconId: "ic-file-text", colorCls: "ic-doc", app: "Word (Windows)", text: false },
  doc:  { icon: "📝", iconId: "ic-file-text", colorCls: "ic-doc", app: "Word (Windows)", text: false },
  rtf:  { icon: "📝", iconId: "ic-file-text", colorCls: "ic-doc", app: "Word (Windows)", text: false },
  pptx: { icon: "📽️", iconId: "ic-file-text", colorCls: "ic-amber", app: "PowerPoint (Windows)", text: false },
  ppt:  { icon: "📽️", iconId: "ic-file-text", colorCls: "ic-amber", app: "PowerPoint (Windows)", text: false },
  pdf:  { icon: "📕", iconId: "ic-file-text", colorCls: "ic-pdf", app: "trình đọc PDF (Windows)", text: false },
  dwg:  { icon: "📐", iconId: "ic-compass", colorCls: "ic-cad", app: "AutoCAD / CAD mặc định", text: false },
  dxf:  { icon: "📐", iconId: "ic-compass", colorCls: "ic-cad", app: "AutoCAD / CAD mặc định", text: false },
  ifc:  { icon: "🏗️", iconId: "kuro-ic-bim", colorCls: "ic-cad", app: "phần mềm BIM mặc định", text: false },
  rvt:  { icon: "🏗️", iconId: "kuro-ic-bim", colorCls: "ic-cad", app: "Revit / BIM mặc định", text: false },
  png:  { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình xem ảnh (Windows)", text: false },
  jpg:  { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình xem ảnh (Windows)", text: false },
  jpeg: { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình xem ảnh (Windows)", text: false },
  webp: { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình xem ảnh (Windows)", text: false },
  bmp:  { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình xem ảnh (Windows)", text: false },
  gif:  { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình xem ảnh (Windows)", text: false },
  svg:  { icon: "🖼️", iconId: "ic-image", colorCls: "ic-image", app: "trình duyệt / xem ảnh", text: true },
  html: { icon: "🌐", iconId: "ic-globe", colorCls: "ic-web", app: "trình duyệt (Windows)", text: true },
  htm:  { icon: "🌐", iconId: "ic-globe", colorCls: "ic-web", app: "trình duyệt (Windows)", text: true },
  py:   { icon: "🐍", iconId: "ic-file-code", colorCls: "ic-code", app: "phần mềm mặc định Windows", text: true },
  js:   { icon: "📜", iconId: "ic-file-code", colorCls: "ic-code", app: "phần mềm mặc định Windows", text: true },
  ts:   { icon: "📜", iconId: "ic-file-code", colorCls: "ic-code", app: "phần mềm mặc định Windows", text: true },
  json: { icon: "📄", iconId: "ic-file-code", colorCls: "ic-amber", app: "phần mềm mặc định Windows", text: true },
  md:   { icon: "📄", iconId: "ic-file-text", colorCls: "ic-web", app: "phần mềm mặc định Windows", text: true },
  txt:  { icon: "📄", iconId: "ic-file-text", colorCls: "ic-muted", app: "Notepad / mặc định Windows", text: true },
  log:  { icon: "📄", iconId: "ic-file-text", colorCls: "ic-muted", app: "Notepad / mặc định Windows", text: true },
  yaml: { icon: "📄", iconId: "ic-file-code", colorCls: "ic-amber", app: "phần mềm mặc định Windows", text: true },
  yml:  { icon: "📄", iconId: "ic-file-code", colorCls: "ic-amber", app: "phần mềm mặc định Windows", text: true },
  xml:  { icon: "📄", iconId: "ic-file-code", colorCls: "ic-amber", app: "phần mềm mặc định Windows", text: true },
  sql:  { icon: "📄", iconId: "ic-file-code", colorCls: "ic-web", app: "phần mềm mặc định Windows", text: true },
  css:  { icon: "📄", iconId: "ic-file-code", colorCls: "ic-web", app: "phần mềm mặc định Windows", text: true },
  zip:  { icon: "📦", iconId: "ic-file-archive", colorCls: "ic-archive", app: "trình giải nén (Windows)", text: false },
  rar:  { icon: "📦", iconId: "ic-file-archive", colorCls: "ic-archive", app: "trình giải nén (Windows)", text: false },
  "7z": { icon: "📦", iconId: "ic-file-archive", colorCls: "ic-archive", app: "trình giải nén (Windows)", text: false },
};
const _KNOWN_EXT_PATTERN = Object.keys(KURO_FILE_META).join("|");
const _WIN_ABS_PATH_RE = /^[A-Za-z]:[\\/][^\r\n<>|"*?]+$/;
const _UNC_PATH_RE = /^\\\\[^\\\s<>|"*?]+\\[^\\\r\n<>|"*?]+$/;
const _REL_FILE_RE = new RegExp(`^(?:[\\w.\\-\\/\\\\]+[\\/\\\\])?[\\w.\\-\\u00C0-\\u1EF9][\\w.\\-\\u00C0-\\u1EF9 ]*\\.(${_KNOWN_EXT_PATTERN})$`, "i");
const _INLINE_WIN_FILE_RE = new RegExp(`((?:[A-Za-z]:[\\\\/]|\\\\\\\\[^\\\\\\s<>|"*?]+\\\\)[^\\s<>|"*?(),;'"\`]+\\.(?:${_KNOWN_EXT_PATTERN}))`, "gi");

function getFileExt(pathStr) {
  const clean = String(pathStr || "").replace(/#L\d+(?:-L?\d+)?$/i, "").trim();
  const m = clean.match(/\.([A-Za-z0-9]{1,6})$/);
  return m ? m[1].toLowerCase() : "";
}

function getFileMeta(pathStr) {
  const ext = getFileExt(pathStr);
  return KURO_FILE_META[ext] || { icon: "📄", iconId: "ic-file-text", colorCls: "ic-muted", app: "phần mềm mặc định Windows", text: false };
}

function getFileBaseName(pathStr) {
  const clean = String(pathStr || "").replace(/#L\d+(?:-L?\d+)?$/i, "").replace(/[\\/]+$/, "");
  const parts = clean.split(/[\\/]/);
  return parts[parts.length - 1] || clean;
}

function decodeFileHref(href) {
  try {
    let raw = String(href || "").trim();
    if (!raw.toLowerCase().startsWith("file://")) return raw;
    raw = raw.replace(/#L\d+(?:-L?\d+)?$/i, "");
    const u = new URL(raw);
    if (u.hostname && u.hostname.toLowerCase() !== "localhost") {
      return "\\\\" + u.hostname + decodeURIComponent(u.pathname).replace(/\//g, "\\");
    }
    let p = decodeURIComponent(u.pathname);
    if (/^\/[A-Za-z]:/.test(p)) p = p.slice(1);
    return p.replace(/\//g, "\\");
  } catch {
    return String(href || "");
  }
}

function looksLikeFilePath(text) {
  const s = (text || "").trim();
  if (!s || s.length > 260 || s.includes("\n") || /^https?:\/\//i.test(s) || /^mailto:/i.test(s)) {
    return false;
  }
  if (_WIN_ABS_PATH_RE.test(s) || _UNC_PATH_RE.test(s)) {
    // Có đuôi file hoặc là đường dẫn sâu rõ ràng
    return Boolean(getFileExt(s)) || /[\\/][^\\/]+$/.test(s);
  }
  if (s.length <= 120 && !s.startsWith("-") && _REL_FILE_RE.test(s)) {
    return true;
  }
  return false;
}

function makeFileLinkEl(doc, filePath, displayText) {
  const meta = getFileMeta(filePath);
  const btn = doc.createElement("button");
  btn.type = "button";
  btn.className = "kuro-file-link";
  btn.setAttribute("data-file-path", filePath);
  btn.title = `${filePath}\nBấm để mở bằng ${meta.app} hoặc xem tùy chọn`;

  const ico = doc.createElement("span");
  ico.className = "kfl-ico";
  ico.innerHTML = kuroIcon(meta.iconId || "ic-file-text", "ic-xs", meta.colorCls || "");
  const txt = doc.createElement("span");
  txt.textContent = displayText || filePath;
  const arr = doc.createElement("span");
  arr.className = "kfl-arrow";
  arr.innerHTML = kuroIcon("ic-external-link", "ic-xs");
  btn.append(ico, txt, arr);
  return btn;
}

function enhanceFilePathsInHtml(cleanHtml) {
  if (!cleanHtml || (cleanHtml.indexOf("\\") === -1 && cleanHtml.indexOf("/") === -1 && cleanHtml.indexOf(".") === -1)) {
    return cleanHtml;
  }
  const tpl = document.createElement("template");
  tpl.innerHTML = cleanHtml;
  const root = tpl.content;

  // 1. Nâng cấp thẻ <a href="file://..."> thành nút mở file native Windows
  root.querySelectorAll("a[href]").forEach((a) => {
    const href = a.getAttribute("href") || "";
    if (href.toLowerCase().startsWith("file://")) {
      const pathStr = decodeFileHref(href);
      const label = (a.textContent || "").trim() || getFileBaseName(pathStr);
      a.replaceWith(makeFileLinkEl(document, pathStr, label));
    }
  });

  // 2. Nâng cấp thẻ inline <code> chứa đường dẫn file (không đụng khối <pre><code>)
  root.querySelectorAll("code").forEach((code) => {
    if (code.closest("pre") || code.closest("a") || code.closest("button")) return;
    const text = (code.textContent || "").trim();
    if (looksLikeFilePath(text)) {
      code.replaceWith(makeFileLinkEl(document, text, text));
    }
  });

  // 3. Nâng cấp đường dẫn tuyệt đối Windows / UNC viết trực tiếp trong văn bản thường
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  let node;
  while ((node = walker.nextNode())) {
    const p = node.parentElement;
    if (!p || p.closest("pre, code, a, button, script, style, .katex")) continue;
    if (node.nodeValue && (node.nodeValue.includes(":\\") || node.nodeValue.includes(":/") || node.nodeValue.includes("\\\\"))) {
      textNodes.push(node);
    }
  }
  textNodes.forEach((tn) => {
    const val = tn.nodeValue;
    _INLINE_WIN_FILE_RE.lastIndex = 0;
    if (!_INLINE_WIN_FILE_RE.test(val)) return;
    _INLINE_WIN_FILE_RE.lastIndex = 0;
    const frag = document.createDocumentFragment();
    let last = 0;
    let m;
    while ((m = _INLINE_WIN_FILE_RE.exec(val)) !== null) {
      if (m.index > last) frag.append(document.createTextNode(val.slice(last, m.index)));
      const p = m[1];
      frag.append(makeFileLinkEl(document, p, p));
      last = m.index + p.length;
    }
    if (last < val.length) frag.append(document.createTextNode(val.slice(last)));
    tn.replaceWith(frag);
  });

  const box = document.createElement("div");
  box.appendChild(root);
  return box.innerHTML;
}

// Công thức LaTeX ($...$, $$...$$, \(...\), \[...\]) dựng bằng KaTeX trước khi qua marked, để marked không ăn mất
// dấu "\" và "_". Khối code giữ nguyên. "$" phải sát chữ hai đầu và không theo sau là số, để "$5 và $10" không bị nhận nhầm.
const MATH_RE = /(```[\s\S]*?```|`[^`\n]*`)|\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|\$(?=\S)([^$\n]+?)(?<=\S)\$(?!\d)/g;
const md = (t) => {
  const math = [];
  const src = (t || "").replace(MATH_RE, (m, code, d1, d2, i1, i2) => {
    if (code || typeof katex === "undefined") return m;
    try {
      math.push(katex.renderToString(d1 ?? d2 ?? i1 ?? i2, { displayMode: (d1 ?? d2) != null, throwOnError: false }));
    } catch { return m; }
    return `@@KM${math.length - 1}@@`;
  });
  const safeHtml = DOMPurify.sanitize(marked.parse(src).replace(/@@KM(\d+)@@/g, (_, i) => math[i]));
  return enhanceFilePathsInHtml(safeHtml);
};

let session = null;
let ws;
let bot = null;
let botText = "";
let busy = false;
let agents = [];
let selectedAgent = localStorage.getItem("kuro_active_agent") || "kuro-core";
let currentSessions = [];

// Linh vật Kuro: Chibi kỹ sư robot đội mũ bảo hộ
const MASCOT_SVG = `<svg viewBox="-100 -100 200 200" aria-hidden="true">
  <circle class="m-ring2" r="88"/><circle class="m-ring" r="96"/>
  <path class="m-vest" d="M-40 88 Q-40 58 -14 50 H14 Q40 58 40 88 Z"/>
  <rect class="m-reflect" x="-40" y="70" width="80" height="7"/>
  <path class="m-collar" d="M-14 50 L0 63 L14 50 Z"/>
  <circle class="m-bolt" cx="-60" cy="4" r="7"/><circle class="m-bolt" cx="60" cy="4" r="7"/>
  <rect class="m-head" x="-56" y="-40" width="112" height="90" rx="32"/>
  <rect class="m-screen" x="-42" y="-22" width="84" height="58" rx="20"/>
  <g class="m-eyes">
    <g class="m-open"><ellipse cx="-19" cy="4" rx="8" ry="11"/><ellipse cx="19" cy="4" rx="8" ry="11"/></g>
    <path class="m-happy" d="M-28 8 Q-19 -6 -10 8 M10 8 Q19 -6 28 8"/>
    <path class="m-err" d="M-26 -4 L-12 10 M-12 -4 L-26 10 M12 -4 L26 10 M26 -4 L12 10"/>
  </g>
  <path class="m-mouth" d="M-8 22 Q0 28 8 22"/>
  <ellipse class="m-blush" cx="-31" cy="20" rx="6" ry="3.5"/><ellipse class="m-blush" cx="31" cy="20" rx="6" ry="3.5"/>
  <path class="m-hat" d="M-60 -40 C-60 -96 60 -96 60 -40 Z"/>
  <path class="m-hat-hl" d="M-46 -50 C-46 -70 -28 -80 -14 -82"/>
  <rect class="m-ridge" x="-9" y="-86" width="18" height="46" rx="7"/>
  <rect class="m-brim" x="-70" y="-46" width="140" height="11" rx="5.5"/>
  <circle class="m-lamp-ring" cy="-64" r="10"/><circle class="m-lamp" cy="-64" r="6"/>
</svg>`;

const MASCOT_IMG = `<img src="/kuro_logo_256.png" alt="Kuro Core" style="width:100%; height:100%; object-fit:contain; display:block; filter:drop-shadow(0 3px 6px rgba(21,38,75,0.22));" />`;

// Icon chuyên môn theo từng Agent:
// - Logo nhận diện KURO cho kuro-core
// - SVG chuyên ngành cầu đường thiết kế riêng cho các kỹ sư hạ tầng (đồng bộ nét 1.85px với Lucide)
// - Lucide Icons chuẩn cho các tác vụ chung
const AGENT_ICONS = {
  "kuro-core": MASCOT_IMG,
  "ky-su-bien-phap": kuroIcon("kuro-ic-hardhat", "ic-sm"),
  "ky-su-an-toan-lao-dong-hse": kuroIcon("kuro-ic-hardhat", "ic-sm"),
  "ky-su-kiem-toan-phu-tro": kuroIcon("kuro-ic-scaffold", "ic-sm"),
  "ky-su-kiem-toan-ho-mong-cvt": kuroIcon("kuro-ic-sheetpile", "ic-sm"),
  "ky-su-trac-dia": kuroIcon("kuro-ic-survey", "ic-sm"),
  "ky-su-trac-dia-hien-truong": kuroIcon("kuro-ic-survey", "ic-sm"),
  "ky-su-qs": kuroIcon("kuro-ic-qs", "ic-sm"),
  "xac-nhan-thanh-quyet-toan": kuroIcon("kuro-ic-qs", "ic-sm"),
  "ky-su-qaqc": kuroIcon("kuro-ic-qaqc", "ic-sm"),
  "ky-su-thi-nghiem-vat-lieu": kuroIcon("kuro-ic-qaqc", "ic-sm"),
  "ky-su-ke-hoach": kuroIcon("ic-calendar-check", "ic-sm"),
  "dieu-phoi-bim": kuroIcon("kuro-ic-bim", "ic-sm"),
};

function getAgentIcon(slug) {
  if (AGENT_ICONS[slug]) return AGENT_ICONS[slug];
  const s = String(slug || "").toLowerCase();
  if (s.includes("hse") || s.includes("an-toan") || s.includes("bien-phap")) return kuroIcon("kuro-ic-hardhat", "ic-sm");
  if (s.includes("trac-dia") || s.includes("quan-trac")) return kuroIcon("kuro-ic-survey", "ic-sm");
  if (s.includes("ho-mong") || s.includes("cvt") || s.includes("cu-van")) return kuroIcon("kuro-ic-sheetpile", "ic-sm");
  if (s.includes("phu-tro") || s.includes("da-giao") || s.includes("kiem-toan")) return kuroIcon("kuro-ic-scaffold", "ic-sm");
  if (s.includes("bim") || s.includes("so-hoa")) return kuroIcon("kuro-ic-bim", "ic-sm");
  if (s.includes("qs") || s.includes("khoi-luong") || s.includes("hop-dong") || s.includes("thanh-quyet-toan")) return kuroIcon("kuro-ic-qs", "ic-sm");
  if (s.includes("qa") || s.includes("qc") || s.includes("thi-nghiem")) return kuroIcon("kuro-ic-qaqc", "ic-sm");
  if (s.includes("ke-hoach") || s.includes("tien-do")) return kuroIcon("ic-calendar-check", "ic-sm");
  if (s.includes("cong-van") || s.includes("van-ban") || s.includes("hanh-chinh")) return kuroIcon("ic-file-text", "ic-sm");
  return kuroIcon("ic-bot", "ic-sm");
}

// Gợi ý câu hỏi nhanh (Quick Prompts) riêng cho từng Agent
const AGENT_PROMPTS = {
  "kuro-core": [
    "Tóm tắt tiến độ, các vướng mắc kỹ thuật và công việc cần ưu tiên hôm nay",
    "Rà soát căn cứ pháp lý và tiêu chuẩn kỹ thuật áp dụng cho dự án hạ tầng",
    "Phối hợp giải quyết xung đột mặt bằng và biện pháp giữa các phân đoạn thi công"
  ],
  "ky-su-bien-phap": [
    "Lập biện pháp thi công cọc khoan nhồi D1500 trong điều kiện chật hẹp đô thị",
    "So sánh phương án đúc dầm Super T tại bãi đúc hiện trường vs đúc sẵn tại nhà máy",
    "Xác định các điểm dừng kiểm soát (Hold Points) khi thi công kết cấu hầm/cống hộp"
  ],
  "ky-su-kiem-toan-phu-tro": [
    "Kiểm toán kết cấu hệ đà giáo ván khuôn dầm bê tông bản theo TCVN 11823:2017",
    "Rà soát tính ổn định tổng thể và chuyển vị đỉnh cừ ván thép Larsen IV đào hố móng",
    "Kiểm tra tải trọng gió tác dụng lên hệ tháp tạm và dây neo thi công dầm cầu"
  ],
  "ky-su-kiem-toan-ho-mong-cvt": [
    "Kiểm toán vòng vây cọc ván thép hố móng trụ T11 cầu Ninh Cơ theo TCVN 11815:2017",
    "Chạy kiểm toán theo file JSON số liệu và xuất bảng tổng hợp đạt/không đạt",
    "Xuất mô hình MCT sang Midas Civil và đối chiếu nội lực dầm cừ, khung văng chống"
  ],
  "ky-su-qs": [
    "Bóc tách khối lượng bê tông, cốt thép và ván khuôn kết cấu mố trụ cầu M1",
    "Rà soát đối chiếu chênh lệch khối lượng bản vẽ BVTC so với khối lượng Hợp đồng EPC",
    "Lập biểu tổng hợp khối lượng phụ lục phát sinh ngoài phạm vi hợp đồng xây lắp"
  ],
  "xac-nhan-thanh-quyet-toan": [
    "Soát hồ sơ đề nghị thanh toán đợt cho thầu phụ theo hợp đồng và đối chiếu khối lượng BĐH",
    "Lập phiếu xác nhận khối lượng quyết toán (1.XNKL) và đánh giá tiến độ (4.DGTD)",
    "Kiểm tra khối lượng vật tư thi công (2.VTC) và hao hụt vật tư luân chuyển (3.VTLC) theo BVTC"
  ],
  "ky-su-qaqc": [
    "Lập bảng kế hoạch kiểm tra và thí nghiệm (ITP) cho hạng mục móng cọc bê tông",
    "Soạn thảo checklist nghiệm thu công tác lắp dựng cốt thép trước khi đổ bê tông",
    "Rà soát danh mục tài liệu và biên bản để hoàn thiện bộ hồ sơ hoàn công công trình"
  ],
  "ky-su-ke-hoach": [
    "Lập tiến độ thi công đường găng (CPM) gói thầu cầu hoàn thành trong 18 tháng",
    "Phân tích chỉ số EVM (SPI, CPI) khi sản lượng thực tế chậm 12% so với kế hoạch",
    "Đề xuất kịch bản bù tiến độ bằng cách bổ sung thêm mũi thi công đà giáo luân chuyển"
  ],
  "dieu-phoi-bim": [
    "Hướng dẫn quy chuẩn đặt tên file mô hình và cây thư mục CDE theo ISO 19650",
    "Viết kịch bản tự động gán tham số mã WBS và ngày thi công cho cấu kiện dầm",
    "Kiểm tra xung đột hình học (Clash Detection) giữa mố trụ cầu và hệ thống hạ tầng ngầm"
  ]
};

// Render mascots
document.querySelectorAll(".mascot").forEach((el) => { el.innerHTML = MASCOT_SVG; });

// Mắt mascot nhìn theo con trỏ
document.addEventListener("pointermove", (e) => {
  document.documentElement.style.setProperty("--lx", (e.clientX / innerWidth * 2 - 1).toFixed(2));
  document.documentElement.style.setProperty("--ly", (e.clientY / innerHeight * 2 - 1).toFixed(2));
});

let happyTimer;
function mood(cls) {
  document.body.classList.remove("happy", "err");
  clearTimeout(happyTimer);
  if (cls) document.body.classList.add(cls);
  if (cls === "happy") happyTimer = setTimeout(() => document.body.classList.remove("happy"), 2500);
}

// Quản lý các phiên đang phản hồi độc lập (Multi-Session Concurrent Processing)
const runningSessions = new Map(); // sid -> { text: "", agent: "", botEl: null }

const SEND_ICON_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>';
const STOP_ICON_SVG = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>';

function isSessionBusy(sid) {
  return !!sid && runningSessions.has(sid);
}

function isCurrentSessionBusy() {
  return isSessionBusy(session);
}

function updateSendButtonState() {
  const btn = $("btn-send");
  const isBusy = isCurrentSessionBusy();
  if (btn) {
    if (isBusy) {
      btn.classList.add("is-stopping");
      btn.setAttribute("title", "Dừng phản hồi (Bấm để dừng)");
      btn.innerHTML = STOP_ICON_SVG;
    } else {
      btn.classList.remove("is-stopping");
      btn.setAttribute("title", "Gửi (Enter)");
      btn.innerHTML = SEND_ICON_SVG;
    }
  }

  const indicator = $("typing-indicator");
  if (indicator) {
    indicator.style.display = isBusy ? "inline" : "none";
  }

  document.body.classList.toggle("busy", isBusy);

  const stateEl = $("state");
  if (stateEl) {
    if (isBusy) {
      stateEl.textContent = "Đang xử lý";
    } else if (runningSessions.size > 0) {
      stateEl.textContent = `${runningSessions.size} phiên đang chạy`;
    } else {
      stateEl.textContent = "Sẵn sàng";
    }
  }

  updateSidebarSessionBadges();
  if (!isBusy && typeof fetchAndRenderQuota === "function") {
    fetchAndRenderQuota().catch(() => {});
  }
}

function updateSidebarSessionBadges() {
  const listEl = $("session-list");
  if (!listEl) return;
  const items = listEl.querySelectorAll(".session-item");
  items.forEach(el => {
    const sid = el.getAttribute("data-sid");
    let badge = el.querySelector(".session-running-indicator");
    if (isSessionBusy(sid)) {
      if (!badge) {
        badge = document.createElement("span");
        badge.className = "session-running-indicator";
        badge.innerHTML = `<span class="spinner-dot" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#22d3ee; margin-right:3px; animation:blink .8s infinite;"></span>Đang xử lý`;
        badge.style.cssText = "font-size:10px; color:#22d3ee; margin-left:6px; font-weight:600; padding:1px 4px; background:rgba(34,211,238,0.12); border-radius:3px; border:1px solid rgba(34,211,238,0.3);";
        const sub = el.querySelector(".session-item-sub") || el;
        sub.appendChild(badge);
      }
    } else {
      if (badge) badge.remove();
    }
  });
}

async function stopSession(sid) {
  const targetSid = sid || session;
  if (!targetSid) return;

  // 1. Gửi lệnh stop qua WebSocket
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "stop", session: targetSid }));
  }

  // 2. Gửi lệnh stop qua REST API dự phòng
  try {
    fetch(`/api/sessions/${encodeURIComponent(targetSid)}/stop`, { method: "POST" });
  } catch (_) {}

  // 3. Nếu là phiên đang mở, cập nhật DOM
  if (runningSessions.has(targetSid)) {
    const sessData = runningSessions.get(targetSid);
    if (targetSid === session && sessData && sessData.botEl) {
      sessData.botEl.insertAdjacentHTML("beforeend", `<div style="margin-top:8px; font-style:italic; color:var(--amber); font-size:13px;">⏹ _(Đã dừng phản hồi theo yêu cầu)_</div>`);
    }
    runningSessions.delete(targetSid);
  }

  updateSendButtonState();
  mood(null);
}

function setBusy(b, sid) {
  const targetSid = sid || session;
  if (targetSid) {
    if (b) {
      if (!runningSessions.has(targetSid)) {
        runningSessions.set(targetSid, { text: "", agent: selectedAgent, botEl: null });
      }
    } else {
      runningSessions.delete(targetSid);
    }
  }
  busy = runningSessions.size > 0;
  updateSendButtonState();
  if (b) mood(null);
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function addMessage(role, html, senderName) {
  const d = document.createElement("div");
  d.className = "msg " + (role === "user" ? "user" : "bot");
  if (role !== "user") {
    d.setAttribute("data-sender", senderName || (currentAgent() ? currentAgent().name.toUpperCase() : "KURO"));
  }
  d.innerHTML = html;
  $("log").append(d);
  $("log").scrollTop = $("log").scrollHeight;
  if (typeof updateChatNavTicks === "function") {
    setTimeout(updateChatNavTicks, 50);
  }
  return d;
}

let groupsConfig = {};

function currentAgent() {
  if (selectedAgent && selectedAgent.startsWith("group:")) {
    const grpName = selectedAgent.substring(6).trim();
    const grpCfg = groupsConfig[grpName] || {};
    return {
      slug: selectedAgent,
      name: `Agent Tổng: ${grpName}`,
      role: grpCfg.role || `Điều phối quy trình tổng cho toàn bộ cộng sự nhóm ${grpName}`,
      badge: "Agent Tổng",
      is_core: false,
      is_group_lead: true
    };
  }
  return agents.find((a) => a.slug === selectedAgent) || agents[0] || { slug: "kuro-core", name: "Kuro Core", role: "" };
}

// Icon và quản lý nhóm cho từng Agent (Lucide Icons + SVG chuyên ngành KURO)
const GROUP_ICONS = {
  "Hệ thống": kuroIcon("ic-shield-check", "ic-xs", "ic-accent"),
  "Kỹ thuật & Thi công": kuroIcon("kuro-ic-bridge", "ic-xs", "ic-amber"),
  "Quản lý & Hồ sơ": kuroIcon("ic-clipboard-list", "ic-xs", "ic-green"),
  "BIM & Số hóa": kuroIcon("kuro-ic-bim", "ic-xs", "ic-web"),
  "Tổ đội & Quy trình": kuroIcon("ic-users", "ic-xs"),
  "Chuyên môn": kuroIcon("ic-settings", "ic-xs"),
  "Vận hành - Hành chính kỹ thuật": kuroIcon("ic-briefcase", "ic-xs", "ic-folder"),
};

function getGroupIcon(groupName) {
  if (GROUP_ICONS[groupName]) return GROUP_ICONS[groupName];
  const g = String(groupName || "").toLowerCase();
  if (g.includes("vận hành") || g.includes("hành chính")) return kuroIcon("ic-briefcase", "ic-xs", "ic-folder");
  return kuroIcon("ic-folder", "ic-xs", "ic-folder");
}

let currentGroupFilter = "all";
let collapsedGroups = {};
try {
  collapsedGroups = JSON.parse(localStorage.getItem("kuro_agent_groups_collapsed") || "{}");
} catch (_) {
  collapsedGroups = {};
}

function saveCollapsedGroups() {
  try {
    localStorage.setItem("kuro_agent_groups_collapsed", JSON.stringify(collapsedGroups));
  } catch (_) {}
}

// Render các chip lọc nhanh theo nhóm (Filter Pills)
function renderGroupFilterChips() {
  const bar = $("agent-filter-chips");
  const datalist = $("agent-groups-datalist");
  const btnMore = $("agent-filter-dropdown-btn");
  const dropMenu = $("agent-filter-dropdown-menu");
  if (!bar) return;
  bar.innerHTML = "";

  // Thu thập các nhóm duy nhất và đếm số lượng
  const groupCounts = {};
  agents.forEach((a) => {
    const grp = a.group || (a.is_core ? "Hệ thống" : "Chuyên môn");
    groupCounts[grp] = (groupCounts[grp] || 0) + 1;
  });

  // Cập nhật datalist cho input nhóm ở các dialog
  if (datalist) {
    datalist.innerHTML = "";
    Object.keys(groupCounts).forEach((grp) => {
      if (grp !== "Hệ thống") {
        const opt = document.createElement("option");
        opt.value = grp;
        datalist.appendChild(opt);
      }
    });
  }

  const preferredOrder = ["Hệ thống", "Kỹ thuật & Thi công", "Quản lý & Hồ sơ", "BIM & Số hóa", "Tổ đội & Quy trình"];
  const sortedGroups = Object.keys(groupCounts).sort((a, b) => {
    const ia = preferredOrder.indexOf(a);
    const ib = preferredOrder.indexOf(b);
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a.localeCompare(b, "vi");
  });

  // Tạo chip "Tất cả"
  const isAllActive = (currentGroupFilter === "all");
  const allChip = document.createElement("button");
  allChip.type = "button";
  allChip.className = "filter-chip" + (isAllActive ? " active" : "");
  allChip.title = `Tất cả cộng sự (${agents.length})`;
  allChip.innerHTML = `<span class="chip-icon">${kuroIcon("ic-layout-grid", "ic-xs")}</span><span class="chip-label">Tất cả</span><span class="chip-count">(${agents.length})</span>`;
  allChip.onclick = () => {
    currentGroupFilter = "all";
    renderGroupFilterChips();
    renderAgentList();
  };
  bar.appendChild(allChip);

  sortedGroups.forEach((grp) => {
    const chip = document.createElement("button");
    chip.type = "button";
    const isActive = (currentGroupFilter === grp);
    chip.className = "filter-chip" + (isActive ? " active" : "");
    chip.title = `${grp} (${groupCounts[grp]} cộng sự)`;
    chip.innerHTML = `<span class="chip-icon">${getGroupIcon(grp)}</span><span class="chip-label">${escapeHtml(grp)}</span><span class="chip-count">(${groupCounts[grp]})</span>`;
    chip.onclick = () => {
      currentGroupFilter = (currentGroupFilter === grp) ? "all" : grp;
      renderGroupFilterChips();
      renderAgentList();
    };
    bar.appendChild(chip);
  });

  // Xây dựng menu thả xuống xem toàn bộ danh sách nhóm
  if (dropMenu) {
    dropMenu.innerHTML = "";
    const allItem = document.createElement("div");
    allItem.className = "filter-dropdown-item" + (isAllActive ? " active" : "");
    allItem.innerHTML = `<span style="display:inline-flex;align-items:center;gap:6px;">${kuroIcon("ic-layout-grid", "ic-xs")} Tất cả</span><span style="opacity:0.6;font-size:11px;">${agents.length}</span>`;
    allItem.onclick = () => {
      currentGroupFilter = "all";
      dropMenu.style.display = "none";
      renderGroupFilterChips();
      renderAgentList();
    };
    dropMenu.appendChild(allItem);

    sortedGroups.forEach((grp) => {
      const item = document.createElement("div");
      item.className = "filter-dropdown-item" + (currentGroupFilter === grp ? " active" : "");
      item.innerHTML = `<span style="display:inline-flex;align-items:center;gap:6px;">${getGroupIcon(grp)} ${escapeHtml(grp)}</span><span style="opacity:0.6;font-size:11px;">${groupCounts[grp]}</span>`;
      item.onclick = () => {
        currentGroupFilter = (currentGroupFilter === grp) ? "all" : grp;
        dropMenu.style.display = "none";
        renderGroupFilterChips();
        renderAgentList();
      };
      dropMenu.appendChild(item);
    });
  }

  // Tự động cuộn chip đang active vào tầm nhìn
  const activeChip = bar.querySelector(".filter-chip.active");
  if (activeChip) {
    setTimeout(() => {
      activeChip.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    }, 50);
  }

  // Khởi tạo sự kiện cuộn và cập nhật trạng thái nút
  initFilterBarEvents();
  updateFilterScrollButtons();
}

// Cập nhật hiển thị và trạng thái nút điều hướng cuộn ‹ và ›
function updateFilterScrollButtons() {
  const bar = $("agent-filter-chips");
  const btnLeft = $("agent-filter-scroll-left");
  const btnRight = $("agent-filter-scroll-right");
  if (!bar || !btnLeft || !btnRight) return;
  const isOverflow = bar.scrollWidth > bar.clientWidth + 2;
  if (!isOverflow) {
    btnLeft.style.display = "none";
    btnRight.style.display = "none";
  } else {
    btnLeft.style.display = "flex";
    btnRight.style.display = "flex";
    btnLeft.classList.toggle("disabled", bar.scrollLeft <= 2);
    btnRight.classList.toggle("disabled", bar.scrollLeft + bar.clientWidth >= bar.scrollWidth - 3);
  }
}

// Gán sự kiện cho thanh lọc nhóm (chỉ gán 1 lần)
function initFilterBarEvents() {
  const bar = $("agent-filter-chips");
  const btnLeft = $("agent-filter-scroll-left");
  const btnRight = $("agent-filter-scroll-right");
  const btnMore = $("agent-filter-dropdown-btn");
  const dropMenu = $("agent-filter-dropdown-menu");
  if (!bar || bar._filterEventsBound) return;
  bar._filterEventsBound = true;

  // 1. Cuộn ngang bằng con lăn chuột (wheel)
  bar.addEventListener("wheel", (e) => {
    if (e.deltaY !== 0) {
      e.preventDefault();
      bar.scrollLeft += e.deltaY;
      updateFilterScrollButtons();
    }
  }, { passive: false });

  // 2. Theo dõi cuộn ngang để cập nhật nút ‹ và ›
  bar.addEventListener("scroll", () => {
    updateFilterScrollButtons();
  }, { passive: true });

  // 3. Nút cuộn trái / phải
  if (btnLeft) {
    btnLeft.onclick = () => {
      bar.scrollBy({ left: -90, behavior: "smooth" });
      setTimeout(updateFilterScrollButtons, 150);
    };
  }
  if (btnRight) {
    btnRight.onclick = () => {
      bar.scrollBy({ left: 90, behavior: "smooth" });
      setTimeout(updateFilterScrollButtons, 150);
    };
  }

  // 4. Menu thả xuống xem tất cả các nhóm
  if (btnMore && dropMenu) {
    btnMore.onclick = (e) => {
      e.stopPropagation();
      dropMenu.style.display = (dropMenu.style.display === "none" || !dropMenu.style.display) ? "block" : "none";
    };
    document.addEventListener("click", (e) => {
      if (dropMenu.style.display !== "none" && !btnMore.contains(e.target) && !dropMenu.contains(e.target)) {
        dropMenu.style.display = "none";
      }
    });
  }

  window.addEventListener("resize", () => {
    updateFilterScrollButtons();
  });
}

// Lấy danh sách Agents và cấu hình Groups từ server
async function loadAgents() {
  try {
    const [resAgents, resGroups] = await Promise.all([
      fetch("/api/agents"),
      fetch("/api/groups").catch(() => ({ json: () => ({}) }))
    ]);
    agents = await resAgents.json();
    try {
      groupsConfig = await resGroups.json();
    } catch (_) {
      groupsConfig = {};
    }
    $("agent-count").textContent = agents.length;
    renderGroupFilterChips();
    renderAgentList();
    updateActiveAgentUI();
  } catch (e) {
    console.error("Lỗi tải agents:", e);
  }
}

// Render danh sách Agents theo Accordion Group
function renderAgentList() {
  const listEl = $("agent-list");
  listEl.innerHTML = "";
  const filter = ($("agent-search").value || "").trim().toLowerCase();

  // Lọc theo từ khóa tìm kiếm
  let filtered = agents.filter((a) => {
    const matchSearch = !filter ||
      a.name.toLowerCase().includes(filter) ||
      (a.role && a.role.toLowerCase().includes(filter)) ||
      (a.group && a.group.toLowerCase().includes(filter)) ||
      a.slug.includes(filter);
    return matchSearch;
  });

  // Lọc theo chip nhóm đang chọn
  if (currentGroupFilter !== "all") {
    filtered = filtered.filter((a) => (a.group || (a.is_core ? "Hệ thống" : "Chuyên môn")) === currentGroupFilter);
  }

  // Cập nhật dòng trạng thái
  const statusEl = $("agent-filter-status");
  if (statusEl) {
    if (filter) {
      statusEl.textContent = `TÌM THẤY: ${filtered.length} CỘNG SỰ`;
    } else if (currentGroupFilter !== "all") {
      statusEl.textContent = `${currentGroupFilter.toUpperCase()} (${filtered.length})`;
    } else {
      statusEl.textContent = `TẤT CẢ (${agents.length})`;
    }
  }

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "session-empty";
    empty.textContent = "Không tìm thấy cộng sự nào phù hợp.";
    listEl.appendChild(empty);
    return;
  }

  // Gom nhóm
  const grouped = {};
  filtered.forEach((a) => {
    const grp = a.group || (a.is_core ? "Hệ thống" : "Chuyên môn");
    if (!grouped[grp]) grouped[grp] = [];
    grouped[grp].push(a);
  });

  const preferredOrder = ["Hệ thống", "Kỹ thuật & Thi công", "Quản lý & Hồ sơ", "BIM & Số hóa", "Tổ đội & Quy trình"];
  const sortedGroupNames = Object.keys(grouped).sort((a, b) => {
    const ia = preferredOrder.indexOf(a);
    const ib = preferredOrder.indexOf(b);
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a.localeCompare(b, "vi");
  });

  sortedGroupNames.forEach((grpName) => {
    const groupAgents = grouped[grpName];
    const groupEl = document.createElement("div");
    const isSys = grpName === "Hệ thống";

    const grpCfg = groupsConfig[grpName] || {};
    const hasWorkflow = !!(grpCfg.workflow && grpCfg.workflow.trim());
    const isGroupLeadSelected = selectedAgent === ("group:" + grpName);

    let grpClasses = "agent-group";
    if (isSys) grpClasses += " sys-group";
    if (hasWorkflow) grpClasses += " is-coordinator";
    if (isGroupLeadSelected) grpClasses += " is-active-lead";
    groupEl.className = grpClasses;

    // Nếu đang tìm kiếm hoặc đang chọn nhóm/agent trong nhóm: luôn mở nhóm
    const containsSelected = groupAgents.some((a) => a.slug === selectedAgent) || isGroupLeadSelected;
    if (containsSelected && !filter) {
      collapsedGroups[grpName] = false;
    }

    const isCollapsed = !filter && !!collapsedGroups[grpName];
    if (isCollapsed) {
      groupEl.classList.add("collapsed");
    }

    // Header của Accordion
    const header = document.createElement("div");
    header.className = "agent-group-header";
    header.innerHTML = `
      <div class="agent-group-title">
        <span class="agent-group-icon">${getGroupIcon(grpName)}</span>
        <span class="agent-group-name">${DOMPurify.sanitize(grpName)}</span>
        ${!isSys ? `<button class="agent-group-btn" title="Cấu hình nhóm & Workflow Agent Tổng" type="button" data-config-grp="${encodeURIComponent(grpName)}">${kuroIcon("ic-pencil", "ic-xs")}</button>` : ""}
      </div>
      <div class="agent-group-meta">
        ${hasWorkflow ? `
          <button type="button" class="agent-group-chat-btn" data-chat-grp="${encodeURIComponent(grpName)}" title="Giao việc và chat trực tiếp với Agent Điều phối Tổng của nhóm này">
            ${kuroIcon("ic-zap", "ic-xs")} AGENT TỔNG
          </button>
        ` : ""}
        <span class="agent-group-count">${groupAgents.length}</span>
        <span class="agent-group-chevron">${kuroIcon("ic-chevron-down", "ic-xs")}</span>
      </div>
    `;

    // Click cấu hình nhóm & workflow
    const configBtn = header.querySelector("[data-config-grp]");
    if (configBtn) {
      configBtn.onclick = (e) => {
        e.stopPropagation();
        openConfigGroup(grpName);
      };
    }

    // Click nút Chat Agent Tổng
    const chatGrpBtn = header.querySelector("[data-chat-grp]");
    if (chatGrpBtn) {
      chatGrpBtn.onclick = (e) => {
        e.stopPropagation();
        selectAgent("group:" + grpName);
      };
    }

    header.onclick = (e) => {
      e.stopPropagation();
      const nowCollapsed = groupEl.classList.toggle("collapsed");
      collapsedGroups[grpName] = nowCollapsed;
      saveCollapsedGroups();
    };

    // Body của Accordion
    const body = document.createElement("div");
    body.className = "agent-group-body";
    groupAgents.forEach((a) => {
      body.appendChild(createAgentCard(a));
    });

    groupEl.appendChild(header);
    groupEl.appendChild(body);
    listEl.appendChild(groupEl);
  });
}

// Render bảng chọn Agent điều phối / thành viên
function renderMembersCheckboxes(targetTbodyId, selectedSlugs = [], excludeSlug = null) {
  const tbody = $(targetTbodyId);
  if (!tbody) return;
  tbody.innerHTML = "";

  const availableAgents = agents.filter((a) => !a.is_core && a.slug !== excludeSlug);
  if (!availableAgents.length) {
    tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:var(--muted); padding:8px;">Chưa có Agent nào khác để phối hợp.</td></tr>`;
    return;
  }

  availableAgents.forEach((a) => {
    const isChecked = selectedSlugs.includes(a.slug);
    const tr = document.createElement("tr");
    tr.style.cursor = "pointer";
    tr.innerHTML = `
      <td style="text-align:center;">
        <input type="checkbox" value="${a.slug}" ${isChecked ? "checked" : ""}>
      </td>
      <td>
        <div style="display:flex; align-items:center; gap:6px;">
          <b style="color:var(--text); font-size:12px;">${DOMPurify.sanitize(a.name)}</b>
        </div>
      </td>
      <td style="color:var(--muted); font-size:11.5px;">${DOMPurify.sanitize(a.role || '')}</td>
    `;
    tr.onclick = (e) => {
      if (e.target.tagName !== "INPUT") {
        const cb = tr.querySelector("input[type=checkbox]");
        cb.checked = !cb.checked;
      }
    };
    tbody.appendChild(tr);
  });
}

// Thẻ Agent: Gọn gàng thanh lịch, chỉ hiển thị tên ngắn gọn, bung chi tiết khi chọn
function createAgentCard(agent) {
  const isSelected = agent.slug === selectedAgent;
  const isTeam = agent.members && agent.members.length > 0;
  const card = document.createElement("div");
  card.className = "agent-card" + (agent.is_core ? " core-agent" : "") + (isSelected ? " on" : "");
  card.onclick = () => selectAgent(agent.slug);

  let html = `
    <div class="agent-row-main">
      <div class="agent-avatar">${isTeam ? kuroIcon("ic-users", "ic-sm") : getAgentIcon(agent.slug)}</div>
      <span class="agent-name" title="${DOMPurify.sanitize(agent.name)}">
        ${DOMPurify.sanitize(agent.name)}
        ${isTeam ? `<small style="font-size:10px; color:var(--cyan); margin-left:4px; opacity:.85;">[ĐIỀU PHỐI: ${agent.members.length}]</small>` : ''}
      </span>
      <span class="agent-dot-active"></span>
    </div>
  `;

  // Chỉ khi được chọn: bung chi tiết phần mô tả và các nút hành động
  if (isSelected) {
    let teamMembersHtml = "";
    if (isTeam) {
      const memberNames = agent.members.map((mSlug) => {
        const found = agents.find((x) => x.slug === mSlug);
        return found ? found.name : mSlug;
      }).join(", ");
      teamMembersHtml = `
        <div style="font-size:11px; padding:4px 6px; background:var(--blue-bg); border:1px solid var(--blue-border); border-radius:6px; color:var(--text); margin-bottom:4px; display:flex; align-items:center; gap:5px;">
          ${kuroIcon("ic-users", "ic-xs")} <span><b>Điều phối ${agent.members.length} Agent:</b> ${DOMPurify.sanitize(memberNames)}</span>
        </div>
      `;
    }

    html += `
      <div class="agent-details">
        ${teamMembersHtml}
        <p class="agent-desc">${DOMPurify.sanitize(agent.role || 'Trợ lý kỹ sư hạ tầng chuyên trách.')}</p>
        <div class="agent-card-actions">
          ${!agent.is_core ? `
            <button type="button" class="btn-agent-act" data-edit-agent="${agent.slug}" title="Chỉnh sửa thông tin, đổi nhóm hoặc chọn Agent điều phối">${kuroIcon("ic-pencil", "ic-xs")} Sửa / Điều phối</button>
            <button type="button" class="btn-agent-act danger" data-delete-agent="${agent.slug}" title="Xóa cộng sự này">${kuroIcon("ic-trash-2", "ic-xs")} Xóa</button>
          ` : `
            <span style="font-size:10px; color:var(--amber); letter-spacing:.05em;">LÕI HỆ THỐNG</span>
          `}
        </div>
      </div>
    `;
  }

  card.innerHTML = html;

  // Xử lý nút Sửa và Xóa trong card
  const editBtn = card.querySelector("[data-edit-agent]");
  if (editBtn) {
    editBtn.onclick = (e) => {
      e.stopPropagation();
      openEditAgent(agent.slug);
    };
  }

  const delBtn = card.querySelector("[data-delete-agent]");
  if (delBtn) {
    delBtn.onclick = (e) => {
      e.stopPropagation();
      confirmDeleteAgent(agent.slug, agent.name);
    };
  }

  return card;
}

// Nạp danh sách provider và gợi ý model cho dialog Tạo / Sửa Agent
function populateAgentProviderSelect(selId, datalistId, selectedProvider = "") {
  const sel = $(selId);
  const dl = $(datalistId);
  if (sel) {
    const provs = window._providers || {};
    sel.replaceChildren(
      new Option("- Theo mặc định hệ thống -", ""),
      ...Object.entries(provs).map(([k, v]) => new Option(v.ten || k, k))
    );
    sel.value = selectedProvider || "";
  }
  const updateDatalist = (prov) => {
    if (!dl) return;
    dl.innerHTML = "";
    const grp = (typeof modelGroups !== "undefined" ? modelGroups : []).find(g => g.provider === prov);
    const list = grp ? grp.models : (prov === "claude" ? [{ id: "sonnet", ten: "Sonnet" }, { id: "opus", ten: "Opus" }, { id: "haiku", ten: "Haiku" }] : []);
    list.forEach(m => {
      if (!m.id) return;
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.label = m.ten || m.id;
      dl.appendChild(opt);
    });
  };
  updateDatalist(selectedProvider);
  if (sel && !sel._agentBound) {
    sel._agentBound = true;
    sel.onchange = () => updateDatalist(sel.value);
  }
}

// Mở dialog chỉnh sửa Agent
async function openEditAgent(slug) {
  try {
    const res = await fetch(`/api/agents/${encodeURIComponent(slug)}`);
    if (!res.ok) {
      alert("Không tìm thấy thông tin cộng sự này");
      return;
    }
    const d = await res.json();
    $("ea-slug").value = d.slug;
    $("ea-name").value = d.name;
    $("ea-group").value = d.group || "";
    $("ea-role").value = d.role || "";
    $("ea-prompt").value = d.prompt || "";
    $("ea-msg").textContent = "";
    populateAgentProviderSelect("ea-provider", "ea-model-list", d.provider || "");
    if ($("ea-model")) $("ea-model").value = d.model || "";

    // Render danh sách checkbox các agent thành viên
    renderMembersCheckboxes("ea-members-list", d.members || [], slug);

    $("edit-agent-dialog").showModal();
  } catch (err) {
    alert("Lỗi kết nối máy chủ");
  }
}

// Mở dialog cấu hình nhóm & Workflow Agent tổng
function openConfigGroup(groupName) {
  const grpCfg = groupsConfig[groupName] || {};
  $("cg-old-name").value = groupName;
  $("cg-name").value = groupName;
  $("cg-role").value = grpCfg.role || "";
  $("cg-workflow").value = grpCfg.workflow || "";
  $("cg-msg").textContent = "";
  $("config-group-dialog").showModal();
}

// Xóa cộng sự
async function confirmDeleteAgent(slug, name) {
  if (!confirm(`Bạn có chắc muốn xóa cộng sự "${name}" (${slug}) không? Thao tác này sẽ xóa tệp định nghĩa trong thư mục agents.`)) {
    return;
  }
  try {
    const res = await fetch(`/api/agents/${encodeURIComponent(slug)}`, { method: "DELETE" });
    if (res.ok) {
      if (selectedAgent === slug) {
        selectedAgent = "kuro-core";
        localStorage.setItem("kuro_active_agent", "kuro-core");
      }
      await loadAgents();
      selectAgent(selectedAgent);
    } else {
      const j = await res.json();
      alert(j.detail || "Không thể xóa cộng sự");
    }
  } catch (err) {
    alert("Lỗi kết nối khi xóa");
  }
}

// Khi người dùng bấm chọn một Agent
async function selectAgent(slug) {
  if (selectedAgent === slug && session) {
    if (window.innerWidth <= 768) closeAllDrawers();
    return;
  }
  selectedAgent = slug;
  localStorage.setItem("kuro_active_agent", slug);

  // Đảm bảo mở nhóm của agent vừa chọn
  const agentObj = agents.find((a) => a.slug === slug);
  if (agentObj) {
    const grp = agentObj.group || (agentObj.is_core ? "Hệ thống" : "Chuyên môn");
    collapsedGroups[grp] = false;
    saveCollapsedGroups();
  }

  // Cập nhật highlight thẻ Agent
  renderAgentList();
  updateActiveAgentUI();

  // Tải danh sách phiên riêng của Agent này
  await loadSessions(slug);

  // Nếu chưa có phiên nào thì mới tạo phiên mới
  if (!session && (!currentSessions || currentSessions.length === 0)) {
    newSession();
  }

  // Đồng bộ trạng thái Agent sang thiết bị khác (PC / ĐT)
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "sync_active",
      agent: slug,
      session: session,
      workspace: currentWorkspace.path
    }));
  }

  // Trên Mobile: tự động đóng ngăn kéo lại để tập trung vào khung chat
  if (window.innerWidth <= 768) {
    closeAllDrawers();
  }
}

function updateActiveAgentUI() {
  const a = currentAgent();
  $("header-avatar").innerHTML = getAgentIcon(a.slug);
  $("header-agent-name").textContent = a.name;
  $("header-agent-badge").textContent = a.badge || (a.is_core ? "Hệ thống" : "Chuyên môn");
  $("header-agent-badge").className = "agent-badge-tag " + (a.is_core ? "sys" : "");
  $("header-agent-role").textContent = a.role || "";

  $("q").placeholder = `Hỏi ${a.name}... (Enter để gửi)`;

  // Hero view
  $("hero-avatar").innerHTML = getAgentIcon(a.slug);
  $("hero-title").textContent = a.name.toUpperCase();
  $("hero-desc").textContent = a.role || "Trợ lý kỹ sư hạ tầng chuyên trách.";

  // Quick prompts
  const prompts = AGENT_PROMPTS[a.slug] || AGENT_PROMPTS["kuro-core"];
  const promptsBox = $("hero-prompts");
  promptsBox.innerHTML = "";
  prompts.forEach((pText) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "prompt-btn";
    btn.textContent = pText;
    btn.onclick = () => {
      $("q").value = pText;
      $("f").requestSubmit();
    };
    promptsBox.appendChild(btn);
  });
}

// Tìm kiếm và điều khiển nhóm Agent
$("agent-search").oninput = renderAgentList;

const btnExpandAll = $("btn-agents-expand-all");
if (btnExpandAll) {
  btnExpandAll.onclick = () => {
    collapsedGroups = {};
    saveCollapsedGroups();
    renderAgentList();
  };
}

const btnCollapseAll = $("btn-agents-collapse-all");
if (btnCollapseAll) {
  btnCollapseAll.onclick = () => {
    agents.forEach((a) => {
      const grp = a.group || (a.is_core ? "Hệ thống" : "Chuyên môn");
      collapsedGroups[grp] = true;
    });
    saveCollapsedGroups();
    renderAgentList();
  };
}

// Tải lịch sử phiên cho Agent được chọn (cô lập theo Workspace hiện tại)
async function loadSessions(agentSlug) {
  agentSlug = agentSlug || selectedAgent;
  try {
    const wsParam = currentWorkspace && currentWorkspace.path ? `&workspace=${encodeURIComponent(currentWorkspace.path)}` : "";
    const res = await fetch(`/api/sessions?agent=${encodeURIComponent(agentSlug)}${wsParam}`);
    currentSessions = await res.json();
    renderSessionList();
    if (!session && currentSessions.length > 0) {
      await openSession(currentSessions[0].id);
    } else if (session && !currentSessions.some((s) => s.id === session)) {
      if (currentSessions.length > 0) {
        await openSession(currentSessions[0].id);
      } else {
        newSession();
      }
    } else {
      await loadSessionContext(session);
    }
  } catch (e) {
    console.error("Lỗi tải phiên:", e);
  }
}

// Nhóm phiên theo mốc thời gian: Hôm nay / 7 ngày qua / Cũ hơn
function renderSessionList() {
  const container = $("sessions");
  container.innerHTML = "";
  const filter = ($("session-search").value || "").trim().toLowerCase();

  const filtered = currentSessions.filter((s) => {
    return !filter || s.title.toLowerCase().includes(filter);
  });

  if (!filtered.length) {
    container.innerHTML = `<div class="session-empty">Chưa có hội thoại nào với ${DOMPurify.sanitize(currentAgent().name)}. Bấm "Phiên mới" để bắt đầu!</div>`;
    return;
  }

  const now = Date.now() / 1000;
  const ONE_DAY = 86400;
  const SEVEN_DAYS = 7 * ONE_DAY;

  const today = [];
  const week = [];
  const older = [];

  filtered.forEach((s) => {
    const diff = now - (s.updated || now);
    if (diff < ONE_DAY) today.push(s);
    else if (diff < SEVEN_DAYS) week.push(s);
    else older.push(s);
  });

  const renderGroup = (label, list) => {
    if (!list.length) return;
    const gTitle = document.createElement("div");
    gTitle.className = "session-group-title";
    gTitle.textContent = label;
    container.appendChild(gTitle);
    list.forEach((s) => container.appendChild(createSessionItem(s)));
  };

  renderGroup("Hôm nay", today);
  renderGroup("7 ngày qua", week);
  renderGroup("Cũ hơn", older);
}

function formatSessionTime(ts) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) {
    return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
  }
  return `${d.getDate().toString().padStart(2, "0")}/${(d.getMonth() + 1).toString().padStart(2, "0")}`;
}

function getProviderShort(providerId) {
  const p = (providerId || "").trim();
  if (!p) return "";
  if (typeof modelGroups !== "undefined") {
    const g = modelGroups.find(x => x.provider === p);
    if (g && g.short) return g.short;
  }
  const info = window._providers && window._providers[p];
  if (info && info.short) return info.short;
  const fallback = { antigravity: "AGY", claude: "Claude", chatgpt: "Codex", anthropic: "Anthropic", openrouter: "OpenRouter", deepseek: "DeepSeek", zai: "GLM", kimi: "Kimi", ollama: "Ollama", custom: "Custom" };
  return fallback[p] || p.toUpperCase();
}

function getProviderClass(providerId) {
  const p = (providerId || "").trim();
  if (p === "antigravity") return "prov-antigravity";
  if (p === "claude" || p === "anthropic") return "prov-claude";
  if (p === "chatgpt") return "prov-chatgpt";
  return p ? "prov-api" : "";
}

function getShortModelName(modelId, providerId = "") {
  if (!modelId) return "";
  if (typeof modelGroups !== "undefined" && modelGroups.length) {
    const grp = providerId ? modelGroups.find(g => g.provider === providerId) : null;
    if (grp) {
      const m = (grp.models || []).find(x => x.id === modelId);
      if (m && m.ten) return m.ten;
    }
    for (const g of modelGroups) {
      const m = (g.models || []).find(x => x.id === modelId);
      if (m && m.ten) return m.ten;
    }
  }
  const match = availableModelsList.find(m => m.id === modelId);
  if (match && match.ten) return match.ten;
  let s = String(modelId).trim();
  if (s.startsWith("claude-")) s = s.replace("claude-", "Claude ");
  else if (s.startsWith("gemini-")) s = s.replace("gemini-", "Gemini ");
  else if (s.startsWith("gpt-")) s = s.replace("gpt-", "GPT ");
  return s.length > 22 ? s.slice(0, 20) + "…" : s;
}

function createSessionItem(s) {
  const el = document.createElement("div");
  el.className = "session-item" + (s.id === session ? " on" : "");
  el.setAttribute("data-sid", s.id);
  el.onclick = () => openSession(s.id);

  const prov = s.provider || "";
  const provShort = getProviderShort(prov);
  const provCls = getProviderClass(prov);
  const modelText = s.model ? getShortModelName(s.model, prov) : (provShort ? "Mặc định" : "");
  const badgeLabel = provShort ? (s.model ? `${provShort} · ${modelText}` : provShort) : modelText;
  const badgeTitle = `${prov ? (window._providers?.[prov]?.ten || prov) + " · " : ""}${s.model || "Model mặc định"}`;
  const modelBadge = badgeLabel ? `<span class="session-model-badge ${provCls}" title="${DOMPurify.sanitize(badgeTitle)}">${DOMPurify.sanitize(badgeLabel)}</span>` : "";
  const runningBadge = isSessionBusy(s.id) ? `<span class="session-running-indicator" style="font-size:10px; color:#22d3ee; margin-left:6px; font-weight:600; padding:1px 4px; background:rgba(34,211,238,0.12); border-radius:3px; border:1px solid rgba(34,211,238,0.3);"><span class="spinner-dot" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#22d3ee; margin-right:3px; animation:blink .8s infinite;"></span>Đang xử lý</span>` : "";

  el.innerHTML = `
    <div class="session-title" title="${DOMPurify.sanitize(s.title)}">${DOMPurify.sanitize(s.title)}</div>
    <div class="session-item-sub">
      <span class="session-time">${formatSessionTime(s.updated)}</span>
      ${modelBadge}
      ${runningBadge}
    </div>
    <button class="btn-del-session" type="button" title="Xóa phiên này">${kuroIcon("ic-trash-2", "ic-xs")}</button>
  `;

  el.querySelector(".btn-del-session").onclick = async (e) => {
    e.stopPropagation();
    if (!confirm(`Xóa phiên "${s.title}"?`)) return;
    await fetch(`/api/sessions/${s.id}`, { method: "DELETE" });
    if (session === s.id) newSession();
    await loadSessions(selectedAgent);
  };

  return el;
}

$("session-search").oninput = renderSessionList;

  // Mở phiên hội thoại
async function openSession(id) {
  session = id;
  pendingSessionModel = "";
  pendingSessionProvider = "";
  $("log").replaceChildren();
  renderSessionList();
  loadSessionContext(id);

  // Cập nhật provider + model riêng của session
  let sessObj = currentSessions.find(s => s.id === id);
  const currentProv = (sessObj && sessObj.provider !== undefined) ? (sessObj.provider || "") : null;
  const currentModel = (sessObj && sessObj.model !== undefined) ? (sessObj.model || "") : null;

  if (currentModel !== null || currentProv !== null) {
    const p = currentProv || "";
    const m = currentModel || "";
    activeSessionProvider = p;
    activeSessionModel = m;
    if ($("model-pick")) $("model-pick").value = m;
    updateModelPillUI(m, p);
    renderModelMenuPopover(m, p);
    updateContextEnvModel(m, p);
    if (typeof fetchAndRenderQuota === "function") fetchAndRenderQuota().catch(() => {});
  } else {
    activeSessionProvider = "";
    activeSessionModel = "";
    if ($("model-pick")) $("model-pick").value = "";
    updateModelPillUI("", "");
    renderModelMenuPopover("", "");
    updateContextEnvModel("", "");

    fetch(`/api/sessions/${id}/info`).then(r => r.ok ? r.json() : null).then(info => {
      if (info && session === id) {
        const p = info.provider || "";
        const val = info.model || "";
        if (sessObj) {
          sessObj.provider = p;
          sessObj.model = val;
        }
        activeSessionProvider = p;
        activeSessionModel = val;
        if ($("model-pick")) $("model-pick").value = val;
        updateModelPillUI(val, p);
        renderModelMenuPopover(val, p);
        updateContextEnvModel(val, p);
        renderSessionList();
        if (typeof fetchAndRenderQuota === "function") fetchAndRenderQuota().catch(() => {});
      }
    }).catch(() => {});
  }

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: "sync_active",
      agent: selectedAgent,
      session: id,
      workspace: currentWorkspace.path
    }));
  }

  if (window.innerWidth <= 768) {
    closeAllDrawers();
  }

  try {
    const res = await fetch(`/api/sessions/${id}`);
    const msgs = await res.json();
    const a = currentAgent();
    for (const m of msgs) {
      if (m.role === "user") {
        const uEl = addMessage("user", "");
        if (m.text && (m.text.includes("/api/attachments/") || m.text.includes("[Hình ảnh đính kèm:"))) {
          let cleanText = m.text;
          const imgMatches = cleanText.match(/\[Hình ảnh đính kèm:\s*([^\]]+)\]/g);
          let extraImgHtml = "";
          if (imgMatches) {
            imgMatches.forEach(tag => {
              cleanText = cleanText.replace(tag, "").trim();
              const p = tag.replace(/\[Hình ảnh đính kèm:\s*/, "").replace(/\]$/, "").trim();
              const filename = p.split(/[\\/]/).pop();
              extraImgHtml += `<div class="msg-image-wrap"><img src="/api/attachments/${encodeURIComponent(filename)}" alt="${filename}" onclick="window.open(this.src,'_blank')" title="Bấm để xem ảnh phóng to"></div>`;
            });
          }
          uEl.innerHTML = extraImgHtml + (cleanText ? `<div>${escapeHtml(cleanText)}</div>` : "");
        } else {
          uEl.textContent = m.text;
        }
      } else {
        addMessage("bot", md(m.text), a.name.toUpperCase());
      }
    }

    // Nếu phiên này đang trong quá trình phản hồi nền (Multi-session active):
    if (isSessionBusy(id)) {
      const sessData = runningSessions.get(id);
      if (sessData) {
        sessData.botEl = addMessage("bot", "", (sessData.agent || a.name).toUpperCase());
        if (sessData.text) {
          try {
            sessData.botEl.innerHTML = md(sessData.text);
          } catch (_) {
            sessData.botEl.textContent = sessData.text;
          }
        }
      }
    }
    updateSendButtonState();

    if (typeof updateChatNavTicks === "function") {
      setTimeout(updateChatNavTicks, 80);
    }
  } catch (e) {
    console.error("Lỗi mở phiên:", e);
  }
}

// Tạo phiên mới
function newSession() {
  session = null;
  $("log").replaceChildren();
  renderSessionList();
  loadSessionContext(null);

  // Ưu tiên pending người dùng chọn tay, sau đó tới cấu hình mặc định của Agent đang chọn
  const ag = typeof currentAgent === "function" ? currentAgent() : null;
  const defaultProvVal = pendingSessionProvider || (ag && ag.provider) || "";
  const defaultModelVal = pendingSessionProvider ? pendingSessionModel : (pendingSessionModel || (ag && ag.model) || "");
  activeSessionProvider = defaultProvVal;
  activeSessionModel = defaultModelVal;
  if ($("model-pick")) $("model-pick").value = defaultModelVal;
  updateModelPillUI(defaultModelVal, defaultProvVal);
  renderModelMenuPopover(defaultModelVal, defaultProvVal);
  updateContextEnvModel(defaultModelVal, defaultProvVal);
  if (typeof fetchAndRenderQuota === "function") fetchAndRenderQuota().catch(() => {});
  updateSendButtonState();

  if (typeof updateChatNavTicks === "function") {
    updateChatNavTicks();
  }
  $("q").focus();
}

$("new").onclick = newSession;
$("btn-new-conv").onclick = newSession;

// ========================================================
// QUẢN LÝ NGĂN KÉO DRAWER TRÊN MOBILE & DESKTOP
// ========================================================
function openAgentsSidebar() {
  if (window.innerWidth <= 768) {
    $("agents-sidebar").classList.add("open");
    $("history-sidebar").classList.remove("open");
    const backdrop = $("sidebar-backdrop");
    if (backdrop) backdrop.classList.add("active");
  } else {
    $("agents-sidebar").classList.toggle("collapsed");
  }
}

function closeAgentsSidebar() {
  $("agents-sidebar").classList.remove("open");
  if (window.innerWidth <= 768 && !$("history-sidebar").classList.contains("open")) {
    const backdrop = $("sidebar-backdrop");
    if (backdrop) backdrop.classList.remove("active");
  }
}

function syncHistoryToggleBtn() {
  const hs = $("history-sidebar");
  const btn = $("btn-toggle-history");
  if (!hs || !btn) return;
  const isClosed = hs.classList.contains("collapsed") || (window.innerWidth <= 768 && !hs.classList.contains("open"));
  btn.classList.toggle("is-collapsed", isClosed);
  btn.title = isClosed ? "Mở rộng bảng Lịch sử & Ngữ cảnh" : "Thu gọn bảng Lịch sử & Ngữ cảnh";
  const label = $("history-toggle-text");
  if (label) label.textContent = isClosed ? "Mở rộng" : "Thu gọn";
}

function openHistorySidebar() {
  const hs = $("history-sidebar");
  if (!hs) return;
  hs.classList.remove("collapsed");
  if (window.innerWidth <= 768) {
    hs.classList.add("open");
    $("agents-sidebar").classList.remove("open");
    const backdrop = $("sidebar-backdrop");
    if (backdrop) backdrop.classList.add("active");
  }
  syncHistoryToggleBtn();
  if (currentInspectorTab === "context") {
    loadSessionContext(session);
  }
}

function closeHistorySidebar() {
  const hs = $("history-sidebar");
  if (!hs) return;
  hs.classList.remove("open");
  hs.classList.add("collapsed");
  if (window.innerWidth <= 768 && !$("agents-sidebar").classList.contains("open")) {
    const backdrop = $("sidebar-backdrop");
    if (backdrop) backdrop.classList.remove("active");
  }
  syncHistoryToggleBtn();
}

function closeAllDrawers() {
  closeAgentsSidebar();
  closeHistorySidebar();
  const backdrop = $("sidebar-backdrop");
  if (backdrop) backdrop.classList.remove("active");
}

function toggleHistorySidebar() {
  const hs = $("history-sidebar");
  if (!hs) return;
  const isClosed = hs.classList.contains("collapsed") || (window.innerWidth <= 768 && !hs.classList.contains("open"));
  if (isClosed) {
    openHistorySidebar();
  } else {
    closeHistorySidebar();
  }
}
$("btn-toggle-history").onclick = toggleHistorySidebar;
syncHistoryToggleBtn();
if ($("btn-toggle-history-mobile")) $("btn-toggle-history-mobile").onclick = toggleHistorySidebar;
if ($("gear-mobile")) $("gear-mobile").onclick = () => $("gear").click();
$("btn-close-history").onclick = closeHistorySidebar;

if ($("btn-close-agents-mobile")) {
  $("btn-close-agents-mobile").onclick = closeAgentsSidebar;
}

if ($("sidebar-backdrop")) {
  $("sidebar-backdrop").onclick = closeAllDrawers;
}

// ===================== THỐNG KÊ NGỮ CẢNH (CONTEXT INSPECTOR) =====================
let currentInspectorTab = "history";
let currentContextData = null;

function switchInspectorTab(tab) {
  currentInspectorTab = tab;
  const isContext = tab === "context";
  $("tab-btn-history").classList.toggle("active", !isContext);
  $("tab-btn-context").classList.toggle("active", isContext);
  $("view-history").style.display = isContext ? "none" : "flex";
  $("view-context").style.display = isContext ? "flex" : "none";

  if (isContext) {
    loadSessionContext(session);
  }
}

function toggleContextAccordion(accId) {
  const el = $(accId);
  if (!el) return;
  el.classList.toggle("open");
}

function formatTokens(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
  if (num >= 1000) return (num / 1000).toFixed(1) + "k";
  return String(num || 0);
}

async function loadSessionContext(sid) {
  const esc = (t) => DOMPurify.sanitize(String(t || ""), { ALLOWED_TAGS: [] });
  const url = sid ? `/api/sessions/${encodeURIComponent(sid)}/context` : `/api/context`;

  try {
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();
    currentContextData = data;

    // 1. Cập nhật môi trường
    const env = data.environment || {};
    $("ctx-env-proj").textContent = "Kuro OS (" + (data.agent_name || "Kuro") + ")";
    $("ctx-env-path").textContent = env.brain_path ? env.brain_path.split("\\").pop() : "Brain Default";
    $("ctx-env-path").title = env.brain_path || "";
    $("ctx-env-branch").textContent = env.git_branch || "main";
    const curSess = sid ? currentSessions.find(s => s.id === sid) : null;
    const activeProv = (curSess && curSess.provider) || data.session_provider || env.provider || activeSessionProvider || "";
    const activeModel = (curSess && curSess.model) || data.session_model || env.model || activeSessionModel || "";
    updateContextEnvModel(activeModel, activeProv);

    // 2. Cập nhật tỷ lệ sử dụng & Header Pill
    const usage = data.usage || {};
    const pct = usage.percent || 0;
    const totalTok = usage.total_tokens || 0;
    const winSize = usage.window_size || 1000000;
    const formattedTok = formatTokens(totalTok);
    const formattedWin = formatTokens(winSize);

    $("ctx-used-percent").textContent = `Đã dùng ${pct}%`;
    $("ctx-used-ratio").textContent = `${formattedTok} / ${formattedWin}`;
    $("sidebar-context-badge").textContent = `${pct}%`;
    $("header-context-text").textContent = `📊 ${pct}% · ${formattedTok}`;

    const pillBtn = $("btn-context-header");
    pillBtn.className = "btn-hdr btn-context-pill" + (pct >= 80 ? " danger" : pct >= 60 ? " warn" : "");

    // 3. Render Stacked Progress Bar
    const breakdown = data.breakdown || {};
    const bar = $("ctx-stacked-bar");
    bar.innerHTML = "";

    const barSegments = [
      "messages", "memory_files", "system_tools", "mcp_tools",
      "system_prompt", "skills", "autocompact_buffer", "free_space"
    ];

    barSegments.forEach(key => {
      const seg = breakdown[key];
      if (!seg || seg.percent <= 0) return;
      const el = document.createElement("div");
      const isFree = key === "free_space";
      el.className = "ctx-bar-seg" + (isFree ? " ctx-bar-free" : "");
      el.style.width = Math.max(1, seg.percent) + "%";
      el.style.backgroundColor = isFree ? "transparent" : (seg.color || "#475569");
      el.title = `${seg.name}: ${formatTokens(seg.tokens)} (${seg.percent}%)`;
      bar.appendChild(el);
    });

    // 4. Render Breakdown List
    const list = $("ctx-breakdown-list");
    list.innerHTML = "";
    barSegments.forEach(key => {
      const seg = breakdown[key];
      if (!seg) return;
      const isFree = key === "free_space";
      const row = document.createElement("div");
      row.className = "ctx-break-row";
      row.innerHTML = `
        <div class="ctx-break-left">
          <span class="ctx-color-dot${isFree ? " ctx-dot-free" : ""}" style="${isFree ? "" : `background:${esc(seg.color)};`}"></span>
          <span class="ctx-break-name">${esc(seg.name)}</span>
        </div>
        <div class="ctx-break-right">
          <span class="ctx-break-tokens">${formatTokens(seg.tokens)}</span>
          <span class="ctx-break-pct">${seg.percent}%</span>
        </div>
      `;
      list.appendChild(row);
    });

    // 5. Cập nhật các bộ đếm và danh sách chi tiết (Accordion Details)
    const counts = data.counts || {};
    const details = data.details || {};

    // 5.1 MCP Tools
    const mcpTools = details.mcp_tools || [];
    $("ctx-count-mcp").textContent = mcpTools.length || counts.mcp_tools_count || 0;
    const mcpList = $("ctx-list-mcp");
    if (mcpList) {
      mcpList.innerHTML = "";
      if (!mcpTools.length) {
        mcpList.innerHTML = `<div class="ctx-sub-row" style="color:var(--muted); padding:4px 6px;">Chưa có công cụ MCP</div>`;
      } else {
        mcpTools.forEach(t => {
          const row = document.createElement("div");
          row.className = "ctx-sub-row";
          row.title = t.desc || t.name;
          row.innerHTML = `
            <div class="ctx-sub-left">
              ${kuroIcon("ic-wrench", "ic-xs", "ic-muted")}
              <span class="ctx-sub-name">${esc(t.name)}</span>
            </div>
            <span class="ctx-sub-tok">${formatTokens(t.tokens)}</span>
          `;
          mcpList.appendChild(row);
        });
      }
    }

    // 5.2 Memory Files
    const memFiles = details.memory_files || [];
    $("ctx-count-mem").textContent = memFiles.length || counts.memory_files_count || 0;
    const memList = $("ctx-list-mem");
    if (memList) {
      memList.innerHTML = "";
      if (!memFiles.length) {
        memList.innerHTML = `<div class="ctx-sub-row" style="color:var(--muted); padding:4px 6px;">Chưa có tệp bộ nhớ</div>`;
      } else {
        memFiles.forEach(f => {
          const row = document.createElement("div");
          row.className = "ctx-sub-row clickable";
          const filePath = f.path || f.name;
          const fileName = f.name || filePath.split("/").pop();
          const ext = "." + (fileName.split(".").pop() || "").toLowerCase();
          row.title = `Nhấp để xem tệp: ${filePath}`;
          row.innerHTML = `
            <div class="ctx-sub-left">
              ${kuroIcon("ic-file-text", "ic-xs", "ic-doc")}
              <span class="ctx-sub-name">${esc(filePath)}</span>
            </div>
            <span class="ctx-sub-tok">${formatTokens(f.tokens)}</span>
          `;
          row.onclick = () => openFilePreview(filePath, fileName, ext);
          memList.appendChild(row);
        });
      }
    }

    // 5.3 Skills
    const skillsList = details.skills || [];
    $("ctx-count-skills").textContent = skillsList.length || counts.skills_count || 0;
    const skillsCont = $("ctx-list-skills");
    if (skillsCont) {
      skillsCont.innerHTML = "";
      if (!skillsList.length) {
        skillsCont.innerHTML = `<div class="ctx-sub-row" style="color:var(--muted); padding:4px 6px;">Chưa có kỹ năng chuyên môn</div>`;
      } else {
        skillsList.forEach(s => {
          const row = document.createElement("div");
          row.className = "ctx-sub-row clickable";
          row.title = `Nhấp để xem hướng dẫn SKILL.md: ${s.name}`;
          const skillPath = `.claude/skills/${s.slug}/SKILL.md`;
          row.innerHTML = `
            <div class="ctx-sub-left">
              ${kuroIcon("ic-zap", "ic-xs", "ic-amber")}
              <span class="ctx-sub-name">${esc(s.name)}</span>
            </div>
            <span class="ctx-sub-tok">${formatTokens(s.tokens)}</span>
          `;
          row.onclick = () => openFilePreview(skillPath, `${s.name} (SKILL.md)`, ".md");
          skillsCont.appendChild(row);
        });
      }
    }

    // 5.4 Custom Agents
    const agentsList = details.custom_agents || [];
    $("ctx-count-agents").textContent = agentsList.length || counts.custom_agents_count || 0;
    const agentsCont = $("ctx-list-agents");
    if (agentsCont) {
      agentsCont.innerHTML = "";
      if (!agentsList.length) {
        agentsCont.innerHTML = `<div class="ctx-sub-row" style="color:var(--muted); padding:4px 6px;">Chưa có tác nhân</div>`;
      } else {
        agentsList.forEach(a => {
          const row = document.createElement("div");
          row.className = "ctx-sub-row clickable";
          row.title = a.role ? `Nhấp để xem vai trò: ${a.name} (${a.role})` : `Nhấp để xem vai trò: ${a.name}`;
          const agentPath = `agents/${a.slug}.md`;
          row.innerHTML = `
            <div class="ctx-sub-left">
              ${kuroIcon("ic-bot", "ic-xs", "ic-accent")}
              <span class="ctx-sub-name">${esc(a.name)}</span>
            </div>
            <span class="ctx-sub-tok">${formatTokens(a.tokens)}</span>
          `;
          row.onclick = () => openFilePreview(agentPath, `${a.name} (${a.slug}.md)`, ".md");
          agentsCont.appendChild(row);
        });
      }
    }

    // 6. Cảnh báo nén phiên
    const untilCompact = usage.tokens_until_compact || 0;
    if (!sid) {
      $("ctx-until-compact").textContent = "Phiên mới chưa có tin nhắn";
    } else if (untilCompact > 0) {
      $("ctx-until-compact").textContent = `Còn ${formatTokens(untilCompact)} đến khi tự động nén`;
    } else {
      $("ctx-until-compact").innerHTML = `<b style="color:#f87171;">⚠️ Ngữ cảnh đã đầy, nên nén ngay</b>`;
    }

    // 7. Render danh sách Artifacts
    const artList = $("ctx-artifacts-list");
    artList.innerHTML = "";
    const artifacts = data.artifacts || [];
    if (!artifacts.length) {
      artList.innerHTML = `<div class="session-empty" style="padding:10px;">Chưa có tệp kết quả nào sinh ra.</div>`;
    } else {
      artifacts.forEach(art => {
        const item = document.createElement("div");
        item.className = "ctx-artifact-item";
        item.title = `Xem tệp: ${art.path}`;
        const rawExt = art.name.split(".").pop() || "";
        const ext = "." + rawExt.toLowerCase();
        const artMeta = getFileMeta(art.name);
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:6px; min-width:0;">
            ${kuroIcon(artMeta.iconId || "ic-file-text", "ic-xs", artMeta.colorCls || "")}
            <span class="ctx-art-name">${esc(art.name)}</span>
          </div>
          <span class="ctx-art-ext">${esc(rawExt.toUpperCase())}</span>
        `;
        item.onclick = () => openFilePreview(art.path, art.name, ext);
        artList.appendChild(item);
      });
    }
  } catch (e) {
    console.error("Lỗi tải context session:", e);
  }
}

async function compactCurrentSession() {
  if (!session) {
    alert("Chưa có phiên hội thoại nào để nén.");
    return;
  }
  if (!confirm("Bạn có muốn nén và thu gọn toàn bộ ngữ cảnh phiên này không? Các quyết định kỹ thuật và số liệu quan trọng sẽ được lưu giữ đầy đủ.")) {
    return;
  }

  const btn = $("btn-trigger-compact");
  const origText = btn ? btn.textContent : "⚡ Nén phiên";
  if (btn) {
    btn.textContent = "⏳ Đang nén...";
    btn.disabled = true;
  }

  try {
    const res = await fetch(`/api/sessions/${session}/compact`, { method: "POST" });
    const data = await res.json();
    if (res.ok) {
      if (data.compacted === false) {
        alert(data.msg || "Phiên chưa có đủ tin nhắn để nén.");
        return;
      }
      await openSession(session);
      await loadSessionContext(session);
      alert("✅ Đã nén phiên thành công! Ngữ cảnh đã được giải phóng gọn gàng.");
    } else {
      alert("Không thể nén: " + (data.detail || data.msg || "Lỗi không xác định"));
    }
  } catch (e) {
    alert("Lỗi khi gọi nén phiên: " + e.message);
  } finally {
    if (btn) {
      btn.textContent = origText;
      btn.disabled = false;
    }
  }
}

// Gán sự kiện cho Inspector Panel
$("tab-btn-history") && ($("tab-btn-history").onclick = () => switchInspectorTab("history"));
$("tab-btn-context") && ($("tab-btn-context").onclick = () => switchInspectorTab("context"));
$("btn-context-header") && ($("btn-context-header").onclick = () => {
  $("history-sidebar").classList.remove("collapsed");
  switchInspectorTab("context");
});
$("btn-trigger-compact") && ($("btn-trigger-compact").onclick = compactCurrentSession);

// Đóng mở danh sách Agent trên điện thoại/màn hình nhỏ
$("btn-menu-agents").onclick = () => {
  if ($("agents-sidebar").classList.contains("open")) {
    closeAgentsSidebar();
  } else {
    openAgentsSidebar();
  }
};

// Quản lý Render Throttling & Heartbeat & Auto-Recovery
let renderPending = false;
function scheduleBotRender() {
  if (renderPending) return;
  renderPending = true;
  requestAnimationFrame(() => {
    if (bot) {
      try {
        bot.innerHTML = md(botText);
      } catch (err) {
        bot.textContent = botText;
      }
      $("log").scrollTop = $("log").scrollHeight;
    }
    renderPending = false;
  });
}

let wsPingInterval = null;
function startWsPing() {
  if (wsPingInterval) clearInterval(wsPingInterval);
  wsPingInterval = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify({ type: "ping" }));
      } catch (_) {}
    }
  }, 15000);
}

let autoSyncTimer = null;
function startSessionAutoSync(targetSid) {
  if (autoSyncTimer) clearInterval(autoSyncTimer);
  let ticks = 0;
  autoSyncTimer = setInterval(async () => {
    ticks++;
    if (!busy) {
      clearInterval(autoSyncTimer);
      return;
    }
    const curSid = session || targetSid;
    if (!curSid) return;

    if (ticks >= 2) {
      try {
        const r = await fetch(`/api/sessions/${encodeURIComponent(curSid)}`);
        if (!r.ok) return;
        const msgs = await r.json();
        const last = msgs[msgs.length - 1];
        if (last && last.role === "assistant" && last.text) {
          if (curSid === session) {
            const a = currentAgent();
            if (!bot) {
              bot = addMessage("bot", "", a.name.toUpperCase());
            }
            botText = last.text;
            try {
              bot.innerHTML = md(botText);
            } catch (_) {
              bot.textContent = botText;
            }
            bot = null;
            setBusy(false);
            clearInterval(autoSyncTimer);
            loadSessions(selectedAgent);
            loadSessionContext(session);
            $("log").scrollTop = $("log").scrollHeight;
          }
        }
      } catch (_) {}
    }

    if (ticks >= 45) {
      clearInterval(autoSyncTimer);
      if (busy) setBusy(false);
    }
  }, 4000);
}

// Kết nối WebSocket & Đồng bộ đa thiết bị (Máy tính & Điện thoại)
function connect() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${proto}//${location.host}/ws`);
  ws.onmessage = async (e) => {
    let m;
    try {
      m = JSON.parse(e.data);
    } catch (err) {
      return;
    }

    try {
      if (m.type === "pong") {
        return;
      }

      // 1. Khởi tạo trạng thái ban đầu từ server
      if (m.type === "init_state" && m.state) {
        if (m.state.workspace && (!currentWorkspace.path || m.state.workspace.toLowerCase() !== (currentWorkspace.path || "").toLowerCase())) {
          currentWorkspace.path = m.state.workspace;
          currentWorkspace.name = m.state.workspace_name;
          updateWorkspaceUI();
          refreshFsTree();
        }
        if (!session && m.state.session) {
          if (m.state.agent && m.state.agent !== selectedAgent) {
            selectedAgent = m.state.agent;
            renderAgentList();
            updateActiveAgentUI();
          }
          await openSession(m.state.session);
        }
        return;
      }

      // 2. Nhận tín hiệu đồng bộ chuyển Agent / Session / Workspace từ thiết bị khác
      if (m.type === "sync_active") {
        let changed = false;
        if (m.workspace && (!currentWorkspace.path || m.workspace.toLowerCase() !== (currentWorkspace.path || "").toLowerCase())) {
          currentWorkspace.path = m.workspace;
          currentWorkspace.name = m.workspace_name;
          updateWorkspaceUI();
          refreshFsTree();
          changed = true;
        }
        if (m.agent && m.agent !== selectedAgent) {
          selectedAgent = m.agent;
          renderAgentList();
          updateActiveAgentUI();
          changed = true;
        }
        if (m.session && m.session !== session) {
          await openSession(m.session);
        } else if (changed) {
          await loadSessions(selectedAgent);
        }
        return;
      }

      // 3. Cập nhật thông tin session id
      if (m.type === "session") {
        const oldSid = session;
        session = m.id;
        if (oldSid && runningSessions.has(oldSid)) {
          const data = runningSessions.get(oldSid);
          runningSessions.delete(oldSid);
          runningSessions.set(m.id, data);
        } else if (!runningSessions.has(m.id)) {
          runningSessions.set(m.id, { text: "", agent: m.agent || selectedAgent, botEl: null });
        }
        if (m.provider !== undefined) activeSessionProvider = m.provider || "";
        if (m.model !== undefined) activeSessionModel = m.model || "";
        const existingItem = currentSessions.find(s => s.id === m.id);
        if (existingItem) {
          if (m.provider !== undefined) existingItem.provider = m.provider || "";
          if (m.model !== undefined) existingItem.model = m.model || "";
        }
        pendingSessionModel = "";
        pendingSessionProvider = "";
        updateModelPillUI(activeSessionModel, activeSessionProvider);
        renderModelMenuPopover(activeSessionModel, activeSessionProvider);
        updateSendButtonState();
        return;
      }

      // 4. Nhận tin nhắn User gửi từ thiết bị khác (PC hoặc ĐT)
      if (m.type === "user_message") {
        const uSid = m.session;
        if (uSid && !runningSessions.has(uSid)) {
          runningSessions.set(uSid, { text: "", agent: m.agent, botEl: null });
        }
        if (m.workspace && currentWorkspace.path && m.workspace.toLowerCase() !== currentWorkspace.path.toLowerCase()) {
          currentWorkspace.path = m.workspace;
          updateWorkspaceUI();
          refreshFsTree();
        }
        if (m.agent && m.agent !== selectedAgent) {
          selectedAgent = m.agent;
          renderAgentList();
          updateActiveAgentUI();
        }
        if (session === uSid) {
          const lastMsg = $("log").querySelector(".msg:last-child");
          if (!lastMsg || !lastMsg.classList.contains("user") || lastMsg.textContent.trim() !== (m.text || "").trim()) {
            addMessage("user", "").textContent = m.text;
          }
        }
        updateSendButtonState();
        return;
      }

      // 4b. Các sự kiện hệ thống KHÔNG phải luồng streaming AI (tránh gắn nhầm trạng thái "Đang xử lý")
      if (m.type === "fs_changed") {
        scheduleFsAutoRefresh();
        return;
      }
      if (m.type === "session_saved") {
        loadSessions(selectedAgent);
        return;
      }
      if (m.type === "workspace_changed") {
        if (m.active && (!currentWorkspace.path || m.active.toLowerCase() !== currentWorkspace.path.toLowerCase())) {
          currentWorkspace.path = m.active;
          currentWorkspace.name = m.name;
          recentWorkspaces = m.recent || [];
          updateWorkspaceUI();
          refreshFsTree();
          loadSessions(selectedAgent);
        }
        return;
      }
      if (m.type === "final") {
        return;
      }

      // 5. Luồng sinh câu trả lời Streaming từ AI (cô lập độc lập theo session)
      const targetSid = m.session || session;
      if ((m.type === "text" || m.type === "tool") && targetSid && !runningSessions.has(targetSid)) {
        runningSessions.set(targetSid, { text: "", agent: m.agent || selectedAgent, botEl: null });
        updateSendButtonState();
      }
      const sessData = targetSid ? runningSessions.get(targetSid) : null;

      if (m.type === "text") {
        if (sessData) {
          sessData.text = (sessData.text || "") + m.text;
        }
        if (targetSid === session) {
          if (!sessData.botEl) {
            const a = currentAgent();
            sessData.botEl = addMessage("bot", "", (m.agent || a.name).toUpperCase());
          }
          bot = sessData.botEl;
          botText = sessData.text;
          scheduleBotRender();
        }
      } else if (m.type === "tool") {
        if (targetSid === session && sessData && sessData.botEl) {
          sessData.botEl.insertAdjacentHTML("beforeend", `<span class="tool">${DOMPurify.sanitize(m.name)}</span>`);
        }
      } else if (m.type === "error") {
        if (sessData) sessData.text = (sessData.text || "") + `\n\n**Lỗi:** ${m.text}`;
        if (targetSid === session && sessData && sessData.botEl) {
          sessData.botEl.innerHTML = md(sessData.text);
          mood("err");
        }
      } else if (m.type === "turn_error") {
        renderPending = false;
        const errMsg = m.error || m.text || "Lỗi không xác định khi xử lý phản hồi.";
        if (targetSid === session) {
          const targetEl = (sessData && sessData.botEl) || addMessage("bot", "", (m.agent || currentAgent().name).toUpperCase());
          targetEl.insertAdjacentHTML("beforeend", `<div style="margin-top:8px; color:var(--accent); font-size:13px;"><b>Lỗi:</b> ${DOMPurify.sanitize(errMsg)}</div>`);
          mood("err");
          bot = null;
          botText = "";
        }
        if (targetSid) runningSessions.delete(targetSid);
        updateSendButtonState();
        if (autoSyncTimer) clearInterval(autoSyncTimer);
        loadSessions(selectedAgent);
      } else if (m.type === "turn_stopped") {
        renderPending = false;
        if (targetSid === session) {
          if (sessData && sessData.botEl) {
            sessData.botEl.insertAdjacentHTML("beforeend", `<div style="margin-top:8px; font-style:italic; color:var(--amber); font-size:13px;">⏹ _(Đã dừng phản hồi theo yêu cầu)_</div>`);
          }
          bot = null;
          botText = "";
        }
        if (targetSid) runningSessions.delete(targetSid);
        updateSendButtonState();
        loadSessions(selectedAgent);
      } else if (m.type === "turn_complete") {   // "final" của engine bị bỏ: nếu xử lý cả hai, câu trả lời hiện 2 khung
        renderPending = false;
        const ans = (m.answer || (sessData ? sessData.text : "") || m.text || "").trim();
        if (targetSid === session) {
          if (sessData) {
            if (!sessData.botEl) {
              const a = currentAgent();
              sessData.botEl = addMessage("bot", "", (m.agent || a.name).toUpperCase());
            }
            try {
              sessData.botEl.innerHTML = md(ans || "_(Đã hoàn tất)_");
            } catch (err) {
              sessData.botEl.textContent = ans;
            }
          }
          bot = null;
          botText = "";
          if (!document.body.classList.contains("err")) mood("happy");
          $("log").scrollTop = $("log").scrollHeight;
        }
        if (targetSid) runningSessions.delete(targetSid);
        updateSendButtonState();
        if (autoSyncTimer) clearInterval(autoSyncTimer);
        loadSessions(selectedAgent);
        if (targetSid === session) loadSessionContext(session);
        scheduleFsAutoRefresh();
      }
      if ((m.type === "text" || m.type === "tool" || m.type === "error") && targetSid === session) {
        $("log").scrollTop = $("log").scrollHeight;
      }
    } catch (err) {
      console.error("Lỗi xử lý websocket message:", err);
    }
  };
  ws.onopen = () => {
    document.body.classList.add("online");
    $("net").textContent = "Ổn định";
    startWsPing();
    syncExplorerWatchState();
    if (busy && session) {
      startSessionAutoSync(session);
    }
  };
  ws.onclose = () => {
    document.body.classList.remove("online");
    $("net").textContent = "Mất nối";
    if (wsPingInterval) clearInterval(wsPingInterval);
    setTimeout(connect, 2000);
  };
}

// Xử lý gửi tin nhắn & Lệnh gạch chéo Slash Commands
const SYSTEM_SLASH_COMMANDS = [
  { cmd: "/compact", name: "/compact", desc: "Thu gọn và tóm tắt ngữ cảnh hội thoại hiện tại", needArg: false },
  { cmd: "/context", name: "/context", desc: "Xem thống kê ngữ cảnh, số tin nhắn, token và ký ức đang dùng", needArg: false },
  { cmd: "/skill", name: "/skill <tên_skill>", desc: "Chỉ định áp dụng một skill kỹ thuật chuyên môn", needArg: true },
  { cmd: "/plan", name: "/plan <nội dung>", desc: "Chế độ lập kế hoạch chi tiết từng bước trước khi thực thi", needArg: true },
  { cmd: "/goal", name: "/goal <mục tiêu>", desc: "Chế độ tập trung theo đuổi mục tiêu kỹ thuật đến cùng", needArg: true },
  { cmd: "/version", name: "/version", desc: "Xem phiên bản và cập nhật Kuro OS từ GitHub", needArg: false },
  { cmd: "/update", name: "/update", desc: "Kiểm tra phiên bản mới từ GitHub và cập nhật trực tiếp", needArg: false },
  { cmd: "/remote", name: "/remote (hoặc /mobile)", desc: "Mã QR và địa chỉ kết nối đồng bộ điện thoại di động", needArg: false },
  { cmd: "/mobile", name: "/mobile", desc: "Mã QR và địa chỉ kết nối đồng bộ điện thoại di động", needArg: false },
  { cmd: "/model", name: "/model", desc: "Xem hoặc đổi nhanh model AI đang sử dụng", needArg: false },
  { cmd: "/clear", name: "/clear (hoặc /new)", desc: "Bắt đầu một phiên hội thoại mới sạch sẽ", needArg: false },
  { cmd: "/help", name: "/help", desc: "Xem hướng dẫn danh sách toàn bộ các lệnh gạch chéo", needArg: false }
];

let skillsList = [];
let slashActive = false;
let slashSelectedIndex = 0;
let slashFilteredItems = [];

async function loadSkills() {
  try {
    const res = await fetch("/api/skills");
    if (res.ok) {
      const data = await res.json();
      skillsList = Array.isArray(data) ? data : [];
    }
  } catch (e) {
    console.error("Lỗi tải skills:", e);
    skillsList = [];
  }
}

function getAllSlashItems() {
  const sysItems = SYSTEM_SLASH_COMMANDS.map((c) => ({ ...c, type: "system", badge: "Hệ thống" }));
  const skillItems = Array.isArray(skillsList) ? skillsList.map((s) => ({
    cmd: "/" + s.slug,
    name: "/" + s.slug,
    desc: s.desc || s.name,
    needArg: true,
    type: "skill",
    badge: "Skill"
  })) : [];
  return [...sysItems, ...skillItems];
}

function showSlashMenu(query) {
  const all = getAllSlashItems();
  const q = (query || "").toLowerCase();
  slashFilteredItems = all.filter((it) => {
    return !q || it.cmd.toLowerCase().includes(q) || it.desc.toLowerCase().includes(q) || it.name.toLowerCase().includes(q);
  });

  if (!slashFilteredItems.length) {
    hideSlashMenu();
    return;
  }

  slashSelectedIndex = 0;
  renderSlashMenu();
  $("slash-menu").style.display = "flex";
  slashActive = true;
}

function hideSlashMenu() {
  $("slash-menu").style.display = "none";
  slashActive = false;
}

function renderSlashMenu() {
  const container = $("slash-items");
  container.innerHTML = "";

  const sys = slashFilteredItems.filter((i) => i.type === "system");
  const sk = slashFilteredItems.filter((i) => i.type === "skill");

  let globalIdx = 0;

  const renderSection = (title, items) => {
    if (!items.length) return;
    const cat = document.createElement("div");
    cat.className = "slash-cat-title";
    cat.textContent = title;
    container.appendChild(cat);

    items.forEach((item) => {
      const idx = globalIdx++;
      const el = document.createElement("div");
      el.className = "slash-item" + (idx === slashSelectedIndex ? " active" : "");
      el.innerHTML = `
        <span class="slash-cmd">${DOMPurify.sanitize(item.name)}</span>
        <span class="slash-desc">${DOMPurify.sanitize(item.desc)}</span>
        <span class="slash-badge ${item.type === 'skill' ? 'skill' : ''}">${DOMPurify.sanitize(item.badge)}</span>
      `;
      el.onclick = () => selectSlashItem(item);
      container.appendChild(el);
    });
  };

  renderSection("Lệnh hệ thống", sys);
  renderSection("Skill chuyên môn", sk);
}

function selectSlashItem(item) {
  hideSlashMenu();
  if (item.needArg) {
    $("q").value = item.cmd + " ";
    $("q").focus();
    $("q").selectionStart = $("q").selectionEnd = $("q").value.length;
  } else {
    $("q").value = item.cmd;
    $("f").requestSubmit();
  }
}

// Lắng nghe sự kiện gõ phím trên textarea
$("q").addEventListener("input", function() {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 200) + "px";

  const val = this.value;
  if (val.startsWith("/")) {
    const query = val.slice(1).split(/\s+/)[0];
    showSlashMenu(query);
  } else {
    hideSlashMenu();
  }
});

$("q").onkeydown = (e) => {
  if (slashActive) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      slashSelectedIndex = (slashSelectedIndex + 1) % slashFilteredItems.length;
      renderSlashMenu();
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      slashSelectedIndex = (slashSelectedIndex - 1 + slashFilteredItems.length) % slashFilteredItems.length;
      renderSlashMenu();
      return;
    }
    if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();
      if (slashFilteredItems[slashSelectedIndex]) {
        selectSlashItem(slashFilteredItems[slashSelectedIndex]);
      }
      return;
    }
    if (e.key === "Escape") {
      e.preventDefault();
      hideSlashMenu();
      return;
    }
  }

  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    $("f").requestSubmit();
  }
};

// Đóng menu nếu click ra ngoài
document.addEventListener("click", (e) => {
  if (slashActive && !$("f").contains(e.target)) {
    hideSlashMenu();
  }
});

// ===================== DÁN & KÉO THẢ TỆP TIN VÀO KHUNG CHAT (GIỐNG CLAUDE CODE) =====================
function insertTextAtCursor(textarea, text) {
  if (!textarea) return;
  const start = textarea.selectionStart ?? textarea.value.length;
  const end = textarea.selectionEnd ?? textarea.value.length;
  const val = textarea.value;

  const needLeadingSpace = start > 0 && !/\s$/.test(val.slice(0, start));
  const needTrailingSpace = end < val.length && !/^\s/.test(val.slice(end));

  const insert = (needLeadingSpace ? " " : "") + text + (needTrailingSpace ? " " : " ");
  textarea.value = val.slice(0, start) + insert + val.slice(end);

  const newPos = start + insert.length;
  textarea.selectionStart = textarea.selectionEnd = newPos;
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  textarea.focus();
}

function formatFilePaths(files) {
  if (!files || !files.length) return "";
  return files.map((f) => (/\s/.test(f) ? `"${f}"` : f)).join(" ");
}

async function fetchClipboardFiles() {
  if (window.pywebview?.api?.get_clipboard_files) {
    try {
      const files = await window.pywebview.api.get_clipboard_files();
      if (files && files.length) return files;
    } catch (_) {}
  }
  try {
    const res = await fetch("/api/clipboard/files");
    if (res.ok) {
      const data = await res.json();
      if (data.files && data.files.length) return data.files;
    }
  } catch (_) {}
  return [];
}

let pendingAttachments = [];

function renderAttachmentChips() {
  const bar = $("chat-attachments-bar");
  if (!bar) return;
  if (!pendingAttachments.length) {
    bar.innerHTML = "";
    bar.style.display = "none";
    return;
  }
  bar.style.display = "flex";
  bar.innerHTML = pendingAttachments.map((att, idx) => {
    const isImg = att.isImage || (att.file && att.file.type && att.file.type.startsWith("image/"));
    const thumbHtml = isImg
      ? `<img src="${att.previewUrl || att.url}" alt="${att.filename}">`
      : `<span style="font-size:18px; line-height:1; flex:none;">📄</span>`;
    return `
      <div class="chat-attachment-chip ${att.uploading ? 'uploading' : ''}">
        ${thumbHtml}
        <span>${escapeHtml(att.filename)} ${att.uploading ? '(đang tải...)' : (att.error ? `<span style="color:#ef4444">${escapeHtml(att.error)}</span>` : '✓')}</span>
        <button type="button" class="btn-remove-attach" data-idx="${idx}" title="Xóa đính kèm">✕</button>
      </div>
    `;
  }).join("");

  bar.querySelectorAll(".btn-remove-attach").forEach(btn => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const idx = parseInt(btn.dataset.idx, 10);
      pendingAttachments.splice(idx, 1);
      renderAttachmentChips();
    };
  });
}

async function uploadGeneralFile(file) {
  const isImage = file.type && file.type.startsWith("image/");
  const previewUrl = isImage ? URL.createObjectURL(file) : "";
  const att = {
    file,
    filename: file.name || "file.dat",
    previewUrl,
    url: "",
    path: "",
    isImage,
    uploading: true,
    error: null
  };
  pendingAttachments.push(att);
  renderAttachmentChips();

  const fd = new FormData();
  fd.append("file", file);

  try {
    const endpoint = isImage ? "/api/upload-image" : "/api/upload-file";
    const res = await fetch(endpoint, {
      method: "POST",
      body: fd
    });
    if (!res.ok) {
      throw new Error(`Lỗi máy chủ (${res.status})`);
    }
    const data = await res.json();
    if (data.ok) {
      att.uploading = false;
      att.url = data.url;
      att.path = data.path;
      att.filename = data.filename;
      att.isImage = data.is_image !== undefined ? data.is_image : isImage;
      renderAttachmentChips();
    } else {
      throw new Error(data.error || "Tải lên thất bại");
    }
  } catch (err) {
    console.error("Lỗi upload file:", err);
    att.uploading = false;
    att.error = err.message || "Lỗi tải";
    renderAttachmentChips();
  }
}

async function uploadImageFile(file) {
  return uploadGeneralFile(file);
}

function extractImageFromClipboard(e) {
  if (!e.clipboardData) return null;
  const items = e.clipboardData.items;
  if (items) {
    for (let i = 0; i < items.length; i++) {
      if (items[i].type && items[i].type.startsWith("image/")) {
        return items[i].getAsFile();
      }
    }
  }
  if (e.clipboardData.files && e.clipboardData.files.length > 0) {
    for (let f of e.clipboardData.files) {
      if (f.type && f.type.startsWith("image/")) {
        return f;
      }
    }
  }
  return null;
}

const chatInput = $("q");
if (chatInput) {
  chatInput.addEventListener("paste", async function (e) {
    // 1. Kiểm tra nếu trong clipboard có ảnh (ví dụ chụp màn hình Snipping Tool, Ctrl+C ảnh)
    const imgFile = extractImageFromClipboard(e);
    if (imgFile) {
      e.preventDefault();
      uploadImageFile(imgFile);
      return;
    }

    const plainText = e.clipboardData ? e.clipboardData.getData("text/plain") : "";
    const hasFiles = e.clipboardData && e.clipboardData.files && e.clipboardData.files.length > 0;

    // Khi copy file trong Windows Explorer, plainText thường rỗng hoặc là danh sách file
    if (!plainText || hasFiles) {
      const files = await fetchClipboardFiles();
      if (files && files.length > 0) {
        e.preventDefault();
        insertTextAtCursor(this, formatFilePaths(files));
      }
    }
  });

  // Hỗ trợ kéo thả file từ Windows Explorer vào ô chat
  chatInput.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  });

  chatInput.addEventListener("drop", async function (e) {
    e.preventDefault();
    if (e.dataTransfer?.files?.length) {
      // Ưu tiên nếu kéo thả ảnh trực tiếp
      for (const f of e.dataTransfer.files) {
        if (f.type && f.type.startsWith("image/")) {
          uploadImageFile(f);
          return;
        }
      }

      const paths = Array.from(e.dataTransfer.files)
        .map((f) => f.path || f.name)
        .filter(Boolean);
      const fullPaths = paths.filter((p) => /^[a-zA-Z]:\\|^\\\\/.test(p));
      if (fullPaths.length > 0) {
        insertTextAtCursor(this, formatFilePaths(fullPaths));
        return;
      }
    }
    const files = await fetchClipboardFiles();
    if (files && files.length > 0) {
      insertTextAtCursor(this, formatFilePaths(files));
    }
  });
}

// Bắt phím Ctrl+V khi người dùng vừa chuyển từ Explorer sang cửa sổ Kuro (chưa kịp click vào ô chat)
document.addEventListener("paste", async (e) => {
  const active = document.activeElement;
  const isInput = active && (active.tagName === "INPUT" || active.tagName === "TEXTAREA");
  if (isInput && active.id !== "q") {
    return;
  }
  if (!isInput && chatInput) {
    const imgFile = extractImageFromClipboard(e);
    if (imgFile) {
      e.preventDefault();
      uploadImageFile(imgFile);
      return;
    }

    const plainText = e.clipboardData ? e.clipboardData.getData("text/plain") : "";
    const hasFiles = e.clipboardData && e.clipboardData.files && e.clipboardData.files.length > 0;
    if (!plainText || hasFiles) {
      const files = await fetchClipboardFiles();
      if (files && files.length > 0) {
        e.preventDefault();
        insertTextAtCursor(chatInput, formatFilePaths(files));
      }
    }
  }
});

// Xử lý gửi tin nhắn và lệnh slash
$("f").onsubmit = async (e) => {
  e.preventDefault();
  hideSlashMenu();
  if (isCurrentSessionBusy()) {
    stopSession(session);
    return;
  }
  const text = $("q").value.trim();
  if (!text) return;

  // Xử lý lệnh gạch chéo
  if (text.startsWith("/")) {
    const parts = text.slice(1).split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const arg = parts.slice(1).join(" ").trim();

    if (cmd === "help") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      const helpHtml = `
### 🛠️ DANH MỤC LỆNH GẠCH CHÉO (SLASH COMMANDS)

| Lệnh | Ý nghĩa & Cách dùng |
| :--- | :--- |
| **\`/compact\`** | Thu gọn và tóm tắt hội thoại hiện tại để giải phóng cửa sổ ngữ cảnh |
| **\`/context\`** | Kiểm tra thống kê phiên: tin nhắn, số token, agent, ký ức đang dùng |
| **\`/skill <tên_skill>\`** | Chỉ định nạp quy trình của một skill cụ thể để xử lý bài toán |
| **\`/plan <công việc>\`** | Yêu cầu AI lập kế hoạch chi tiết từng bước, phân tích rủi ro trước khi làm |
| **\`/goal <mục tiêu>\`** | Chế độ bám đuổi mục tiêu: AI tập trung làm triệt để không dừng giữa chừng |
| **\`/model\`** | Xem model hiện tại hoặc đổi model trên thanh điều khiển |
| **\`/clear\`** *(hoặc \`/new\`)* | Tạo phiên hội thoại mới sạch sẽ |
| **\`/<slug_skill>\`** | Kích hoạt trực tiếp 21 skill ngành (ví dụ: \`/bien-phap-thi-cong\`, \`/tinh-toan-ky-thuat\`, \`/kiem-toan-ket-cau-phu-tro\`, \`/qs-khoi-luong-du-toan\`, \`/tien-do-san-luong\`...) |
      `;
      addMessage("bot", md(helpHtml));
      return;
    }

    if (cmd === "version" || cmd === "update") {
      $("q").value = "";
      openVersionDialog();
      return;
    }

    if (cmd === "clear" || cmd === "new" || cmd === "reset") {
      $("q").value = "";
      newSession();
      return;
    }

    if (cmd === "model") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      const effProv = activeSessionProvider || defaultProvider || "claude";
      const provName = (window._providers && window._providers[effProv]?.ten) || effProv;
      const curModel = activeSessionModel || "Mặc định của hãng";
      addMessage("bot", md(`Phiên hiện tại đang dùng: **${provName}** - Model: **${curModel}**. Bạn có thể đổi nhanh nhà cung cấp & model ngay tại nút chọn mô hình ở thanh công cụ dưới khung chat.`));
      return;
    }

    if (cmd === "context") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      $("history-sidebar").classList.remove("collapsed");
      syncHistoryToggleBtn();
      switchInspectorTab("context");
      loadSessionContext(session);
      if (!session) {
        addMessage("bot", md("*(Phiên mới chưa có tin nhắn nào được lưu)*"));
        return;
      }
      try {
        const res = await fetch(`/api/sessions/${session}/context`);
        const ctx = await res.json();
        const ctxHtml = `
### 📊 THÔNG SỐ NGỮ CẢNH PHIÊN (CONTEXT INSPECTOR)
- **Cộng sự phụ trách:** **${DOMPurify.sanitize(currentAgent().name)}**
- **Cửa sổ Context:** \`${formatTokens(ctx.usage?.window_size || 1000000)} tokens\`
- **Tổng Token đã dùng:** \`${formatTokens(ctx.usage?.total_tokens || 0)} (${ctx.usage?.percent || 0}%)\`
- **Messages:** \`${formatTokens(ctx.breakdown?.messages?.tokens || 0)} (${ctx.breakdown?.messages?.percent || 0}%)\`
- **Memory files:** \`${formatTokens(ctx.breakdown?.memory_files?.tokens || 0)} (${ctx.breakdown?.memory_files?.percent || 0}%)\`
- **System & MCP tools:** \`${formatTokens((ctx.breakdown?.system_tools?.tokens || 0) + (ctx.breakdown?.mcp_tools?.tokens || 0))}\`
- **Skills ngành:** \`${formatTokens(ctx.breakdown?.skills?.tokens || 0)}\`
- **Không gian còn lại (Free space):** \`${formatTokens(ctx.breakdown?.free_space?.tokens || 0)}\`

*(Chi tiết phân rã màu đã được mở tại Tab **Ngữ cảnh** ở cột bên phải)*
        `;
        addMessage("bot", md(ctxHtml));
      } catch (err) {
        addMessage("bot", md("Không lấy được thông số ngữ cảnh: " + err));
      }
      return;
    }

    if (cmd === "compact") {
      $("q").value = "";
      compactCurrentSession();
      return;
    }

    if (cmd === "remote" || cmd === "mobile") {
      $("q").value = "";
      showRemoteDialog();
      return;
    }

    // Nếu là lệnh /plan
    if (cmd === "plan") {
      const prompt = `[CHẾ ĐỘ LẬP KẾ HOẠCH - PLAN MODE]\nTrước khi bắt tay vào thực hiện, hãy lập kế hoạch chi tiết từng bước cho yêu cầu sau. Phân tích: căn cứ tiêu chuẩn, dữ liệu đầu vào cần có, các bước thực hiện, điểm kiểm soát (Hold Points) và rủi ro tiềm ẩn:\n\n${arg}`;
      sendChatMessage(text, prompt);
      return;
    }

    // Nếu là lệnh /goal
    if (cmd === "goal") {
      const prompt = `[CHẾ ĐỘ MỤC TIÊU BỀN BỈ - GOAL MODE]\nHãy tập trung giải quyết triệt để và trọn vẹn mục tiêu sau đây, không dừng lại giữa chừng khi bài toán chưa hoàn tất:\n\n${arg}`;
      sendChatMessage(text, prompt);
      return;
    }

    // Nếu là /skill <tên_skill> hoặc /<slug_skill>
    const targetSkill = cmd === "skill" ? arg.split(/\s+/)[0] : cmd;
    const skillArg = cmd === "skill" ? arg.slice(targetSkill.length).trim() : arg;
    const isSkillMatch = skillsList.some((s) => s.slug === targetSkill);

    if (isSkillMatch) {
      const prompt = `[KÍCH HOẠT SKILL: ${targetSkill}]\nHãy đọc và tuân thủ nghiêm ngặt quy trình của skill \`${targetSkill}\` trong thư mục skill để xử lý yêu cầu sau:\n\n${skillArg || 'Áp dụng quy trình chuẩn của skill này để hướng dẫn và triển khai.'}`;
      sendChatMessage(text, prompt);
      return;
    }
  }

  // Tin nhắn thông thường - kèm chế độ Plan/Goal nếu người dùng chọn mode
  let effectivePrompt = undefined;
  if (currentChatMode === "plan") {
    effectivePrompt = `[CHẾ ĐỘ LẬP KẾ HOẠCH - PLAN MODE]\nTrước khi bắt tay vào thực hiện, hãy lập kế hoạch chi tiết từng bước cho yêu cầu sau. Phân tích: căn cứ tiêu chuẩn, dữ liệu đầu vào cần có, các bước thực hiện, điểm kiểm soát (Hold Points) và rủi ro tiềm ẩn:\n\n${text}`;
  } else if (currentChatMode === "goal") {
    effectivePrompt = `[CHẾ ĐỘ MỤC TIÊU BỀN BỈ - GOAL MODE]\nHãy tập trung giải quyết triệt để và trọn vẹn mục tiêu sau đây, không dừng lại giữa chừng khi bài toán chưa hoàn tất:\n\n${text}`;
  }
  sendChatMessage(text, effectivePrompt);
};

function sendChatMessage(displayText, promptToSend) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    alert("Chưa kết nối được với máy chủ Kuro. Vui lòng đợi trong giây lát...");
    return;
  }
  setBusy(true, session);

  // Xử lý tệp & ảnh đính kèm nếu có
  let attHtml = "";
  let attPrompt = "";
  if (pendingAttachments.length > 0) {
    attHtml = pendingAttachments.map(a => {
      const isImg = a.isImage || (a.file && a.file.type && a.file.type.startsWith("image/"));
      if (isImg) {
        return `
          <div class="msg-image-wrap">
            <img src="${a.url || a.previewUrl}" alt="${a.filename}" onclick="window.open(this.src,'_blank')" title="Bấm để xem ảnh phóng to">
          </div>
        `;
      }
      return `
        <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 12px; margin:4px 0; background:rgba(34,211,238,0.08); border:1px solid var(--line-hi); border-radius:6px; font-size:12.5px;">
          <span>📄</span>
          <b>${escapeHtml(a.filename)}</b>
          <small style="color:var(--muted)">(${escapeHtml(a.path || a.url)})</small>
        </div>
      `;
    }).join("");
    attPrompt = pendingAttachments.map(a => `\n[Tệp đính kèm: ${a.path || a.filename}]`).join("");
  }

  const uMsg = addMessage("user", "");
  if (attHtml) {
    uMsg.innerHTML = attHtml + (displayText ? `<div>${escapeHtml(displayText)}</div>` : "");
  } else {
    uMsg.textContent = displayText;
  }

  const sentAttachments = [...pendingAttachments];
  pendingAttachments = [];
  renderAttachmentChips();

  $("q").value = "";
  $("q").style.height = "auto";
  const wsPath = currentWorkspace && currentWorkspace.path ? currentWorkspace.path : "";
  const sessObj = session ? currentSessions.find(s => s.id === session) : null;
  const ag = typeof currentAgent === "function" ? currentAgent() : null;
  const chosenProvider = (session
    ? (activeSessionProvider || (sessObj && sessObj.provider) || "")
    : (pendingSessionProvider || (ag && ag.provider) || "")) || "";
  const chosenModel = (session
    ? (activeSessionModel !== undefined ? activeSessionModel : ((sessObj && sessObj.model) || ""))
    : (pendingSessionProvider ? pendingSessionModel : (pendingSessionModel || (ag && ag.model) || ""))) || "";
  ws.send(JSON.stringify({
    session: session,
    text: (promptToSend || displayText) + attPrompt,
    agent: selectedAgent,
    workspace: wsPath,
    provider: chosenProvider,
    model: chosenModel,
    attachments: sentAttachments
  }));

  startSessionAutoSync(session);

  if (typeof updateChatNavTicks === "function") {
    setTimeout(updateChatNavTicks, 80);
  }
}

// Bắt sự kiện click nút gửi/dừng
if ($("btn-send")) {
  $("btn-send").onclick = (e) => {
    if (isCurrentSessionBusy()) {
      e.preventDefault();
      e.stopPropagation();
      stopSession(session);
    }
  };
}

// Modal Tạo Agent mới
$("btn-create-agent").onclick = () => {
  $("caf").reset();
  $("ca-msg").textContent = "";
  populateAgentProviderSelect("ca-provider", "ca-model-list", "");
  if ($("ca-model")) $("ca-model").value = "";
  renderMembersCheckboxes("ca-members-list", []);
  $("create-agent-dialog").showModal();
};
$("ca-close").onclick = () => $("create-agent-dialog").close();

$("caf").onsubmit = async (e) => {
  e.preventDefault();
  const members = Array.from(document.querySelectorAll("#ca-members-list input[type=checkbox]:checked")).map((cb) => cb.value);
  const data = {
    name: $("ca-name").value.trim(),
    slug: $("ca-slug").value.trim().toLowerCase(),
    group: $("ca-group").value.trim() || "Chuyên môn",
    role: $("ca-role").value.trim(),
    provider: $("ca-provider") ? $("ca-provider").value.trim() : "",
    model: $("ca-model") ? $("ca-model").value.trim() : "",
    prompt: $("ca-prompt").value.trim(),
    members: members
  };
  const msg = $("ca-msg");
  msg.textContent = "Đang lưu...";
  try {
    const res = await fetch("/api/agents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const j = await res.json();
    if (res.ok) {
      msg.textContent = "Đã tạo thành công!";
      $("create-agent-dialog").close();
      await loadAgents();
      selectAgent(j.slug);
    } else {
      msg.textContent = j.detail || "Lỗi tạo Agent";
    }
  } catch (err) {
    msg.textContent = "Lỗi kết nối máy chủ";
  }
};

// Modal Chỉnh sửa Agent
if ($("ea-close")) $("ea-close").onclick = () => $("edit-agent-dialog").close();

if ($("eaf")) {
  $("eaf").onsubmit = async (e) => {
    e.preventDefault();
    const slug = $("ea-slug").value;
    const members = Array.from(document.querySelectorAll("#ea-members-list input[type=checkbox]:checked")).map((cb) => cb.value);
    const data = {
      name: $("ea-name").value.trim(),
      group: $("ea-group").value.trim() || "Chuyên môn",
      role: $("ea-role").value.trim(),
      provider: $("ea-provider") ? $("ea-provider").value.trim() : "",
      model: $("ea-model") ? $("ea-model").value.trim() : "",
      prompt: $("ea-prompt").value.trim(),
      members: members
    };
    const msg = $("ea-msg");
    msg.textContent = "Đang lưu...";
    try {
      const res = await fetch(`/api/agents/${encodeURIComponent(slug)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      const j = await res.json();
      if (res.ok) {
        msg.textContent = "Đã cập nhật!";
        $("edit-agent-dialog").close();
        await loadAgents();
        if (selectedAgent === slug) {
          updateActiveAgentUI();
        }
      } else {
        msg.textContent = j.detail || "Lỗi cập nhật";
      }
    } catch (err) {
      msg.textContent = "Lỗi kết nối máy chủ";
    }
  };
}

// Xử lý nút THÊM AGENT (Tải lên file .zip, .md, .skill)
const btnUpload = $("btn-upload-agent");
const fileInput = $("agent-file-input");
if (btnUpload && fileInput) {
  btnUpload.onclick = () => fileInput.click();

  fileInput.onchange = async () => {
    const files = Array.from(fileInput.files || []);
    if (!files.length) return;

    let totalImported = 0;
    let errors = [];

    for (const f of files) {
      const fd = new FormData();
      fd.append("file", f);
      try {
        const res = await fetch("/api/agents/upload", {
          method: "POST",
          body: fd
        });
        const j = await res.json();
        if (res.ok) {
          totalImported += j.count || 1;
        } else {
          errors.push(`${f.name}: ${j.detail || 'Lỗi không xác định'}`);
        }
      } catch (err) {
        errors.push(`${f.name}: Lỗi kết nối`);
      }
    }

    fileInput.value = "";
    await loadAgents();

    if (totalImported > 0) {
      alert(`Đã tích hợp thành công ${totalImported} Agent vào hệ thống!`);
    }
    if (errors.length) {
      alert("Một số tệp không thể tích hợp:\n" + errors.join("\n"));
    }
  };
}

// Modal Cấu hình nhóm & Workflow Agent Tổng
if ($("cg-close")) $("cg-close").onclick = () => $("config-group-dialog").close();

if ($("cgf")) {
  $("cgf").onsubmit = async (e) => {
    e.preventDefault();
    const oldName = $("cg-old-name").value;
    const name = $("cg-name").value.trim();
    const role = $("cg-role").value.trim();
    const workflow = $("cg-workflow").value.trim();
    if (!name) return;

    const msg = $("cg-msg");
    msg.textContent = "Đang lưu cấu hình...";
    try {
      const res = await fetch("/api/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ old_name: oldName, name, role, workflow })
      });
      const j = await res.json();
      if (res.ok) {
        msg.textContent = "Đã lưu thành công!";
        $("config-group-dialog").close();

        if (selectedAgent === ("group:" + oldName)) {
          selectedAgent = "group:" + name;
          localStorage.setItem("kuro_active_agent", selectedAgent);
        }

        await loadAgents();
      } else {
        msg.textContent = j.detail || "Lỗi lưu cấu hình nhóm";
      }
    } catch (err) {
      msg.textContent = "Lỗi kết nối máy chủ";
    }
  };
}

// ========================================================
// CÀI ĐẶT HỆ THỐNG (ĐA NHÀ CUNG CẤP AI CHẠY SONG SONG)
// ========================================================
let modelTheoAi = {};
let lastSettingsData = null;
let providerModelsCache = {};
let modelMenuFilterProvider = "all";
let modelMenuSearchQuery = "";

async function fetchModelsForSettingsCard(provider) {
  if (providerModelsCache[provider]) return providerModelsCache[provider];
  try {
    const res = await fetch(`/api/models?provider=${encodeURIComponent(provider)}`);
    if (!res.ok) return [];
    const data = await res.json();
    const list = (data.models || []).filter(m => m && m.id);
    providerModelsCache[provider] = list;
    return list;
  } catch {
    return [];
  }
}

async function populateCardModelSelect(provider, cardEl) {
  const modelSel = cardEl.querySelector(".prov-model-select");
  const modelInput = cardEl.querySelector(".prov-model-input");
  const datalist = cardEl.querySelector(".prov-model-datalist");
  if (!modelSel || !modelInput) return;

  const models = await fetchModelsForSettingsCard(provider);
  if (!models.length) {
    modelSel.style.display = "none";
    return;
  }
  modelSel.innerHTML = "";
  const defOpt = document.createElement("option");
  defOpt.value = "";
  defOpt.textContent = `-- Mặc định của hãng (${models.length} model có sẵn) --`;
  modelSel.appendChild(defOpt);
  models.forEach((m) => {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = `${m.ten} (${m.id})`;
    modelSel.appendChild(opt);
  });
  const customOpt = document.createElement("option");
  customOpt.value = "__custom__";
  customOpt.textContent = "✏️ Nhập model tùy biến khác...";
  modelSel.appendChild(customOpt);

  if (datalist) {
    datalist.innerHTML = "";
    models.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.label = m.ten;
      datalist.appendChild(opt);
    });
  }
  modelSel.style.display = "block";

  const syncSelect = () => {
    const v = modelInput.value.trim().toLowerCase();
    const match = Array.from(modelSel.options).find(o => o.value.toLowerCase() === v);
    modelSel.value = match ? match.value : (v ? "__custom__" : "");
  };
  syncSelect();

  if (!modelSel._bound) {
    modelSel._bound = true;
    modelSel.onchange = () => {
      const v = modelSel.value;
      if (v === "__custom__") {
        modelInput.focus();
        modelInput.select();
      } else {
        modelInput.value = v;
        const metaEl = cardEl.querySelector(".prov-card-meta-model");
        if (metaEl) metaEl.textContent = v ? `Model: ${v}` : "Model: Mặc định";
      }
    };
    modelInput.addEventListener("input", () => {
      syncSelect();
      const metaEl = cardEl.querySelector(".prov-card-meta-model");
      const v = modelInput.value.trim();
      if (metaEl) metaEl.textContent = v ? `Model: ${v}` : "Model: Mặc định";
    });
  }
}

function buildProviderCard(p, info, pcfg, isDefault) {
  const card = document.createElement("div");
  card.className = `prov-card${pcfg.enabled || isDefault ? " enabled" : ""}${isDefault ? " is-default" : ""}`;
  card.dataset.provider = p;

  const isCli = info.group === "cli";
  const shortTag = info.short || p;
  const provCls = getProviderClass(p);

  let statusHtml = "";
  if (isDefault) statusHtml += `<span class="prov-pill-def">Mặc định</span>`;
  if (isCli) {
    if (pcfg.cli_installed) {
      statusHtml += `<span class="prov-pill-ok">CLI sẵn sàng</span>`;
    } else {
      statusHtml += `<span class="prov-pill-warn">Chưa cài CLI</span>`;
    }
  } else if (pcfg.needs_key) {
    statusHtml += pcfg.has_key
      ? `<span class="prov-pill-ok">Key ${escapeHtml(pcfg.key_hint)}</span>`
      : `<span class="prov-pill-warn">Chưa có key</span>`;
  } else if (p === "ollama") {
    statusHtml += `<span class="prov-pill-ok">Offline</span>`;
  }

  const modelKey = `KURO_MODEL_${p.toUpperCase()}`;
  const keyKey = `KURO_AI_KEY_${p.toUpperCase()}`;
  const urlKey = `KURO_BASE_URL_${p.toUpperCase()}`;
  const modelMeta = pcfg.model ? `Model: ${pcfg.model}` : "Model: Mặc định";

  const showKeyField = !isCli && p !== "ollama";
  const showUrlField = !isCli && p !== "anthropic";

  card.innerHTML = `
    <div class="prov-card-head">
      <div class="prov-card-left">
        <label class="prov-switch" title="${isDefault ? "AI mặc định luôn bật" : "Bật để xuất hiện trong thanh chọn nhanh của khung chat"}">
          <input type="checkbox" class="prov-enable-cb" data-provider="${escapeHtml(p)}" ${(pcfg.enabled || isDefault) ? "checked" : ""} ${isDefault ? "disabled" : ""}>
          <span class="prov-switch-track"></span>
        </label>
        <div class="prov-card-info">
          <div class="prov-card-title">
            <span class="prov-tag ${provCls}">${escapeHtml(shortTag)}</span>
            <span>${escapeHtml(info.ten || p)}</span>
            ${statusHtml}
          </div>
          <div class="prov-card-meta">
            <span class="prov-card-meta-model">${escapeHtml(modelMeta)}</span>
          </div>
        </div>
      </div>
      <div class="prov-card-actions">
        <button type="button" class="btn prov-toggle-cfg">Cấu hình ▾</button>
      </div>
    </div>
    <div class="prov-card-body">
      <small style="margin-top:0; margin-bottom:6px;">${escapeHtml(info.goi_y || "")}</small>
      ${p === "claude" ? `
        <div style="margin:6px 0 8px;">
          <button class="btn prov-claude-login" type="button">Đăng nhập Claude CLI</button>
          <span class="prov-claude-msg" role="status" style="margin-left:8px; font-size:12px;"></span>
        </div>
      ` : ""}
      ${showKeyField ? `
        <label>API key (${escapeHtml(shortTag)})</label>
        <div class="row">
          <input type="password" name="${keyKey}" autocomplete="off" data-secret="1" spellcheck="false"
            placeholder="${pcfg.has_key ? `Đã lưu (${escapeHtml(pcfg.key_hint)}) - để trống = giữ nguyên` : "Nhập API key..."}">
          <button class="btn" type="button" data-clear="${keyKey}">Xóa</button>
        </div>
      ` : ""}
      ${showUrlField ? `
        <label>Địa chỉ máy chủ (${escapeHtml(shortTag)})</label>
        <input type="text" name="${urlKey}" spellcheck="false" value="${escapeHtml(pcfg.base_url || "")}" data-orig="${escapeHtml(pcfg.base_url || "")}"
          placeholder="${escapeHtml(pcfg.default_url || "Để trống = địa chỉ mặc định của hãng")}">
      ` : ""}
      <label>Model mặc định (${escapeHtml(shortTag)})</label>
      <select class="prov-model-select dialog-select" style="display:none; margin-bottom:6px; width:100%;" aria-label="Chọn model ${escapeHtml(shortTag)}"></select>
      <input type="text" class="prov-model-input" name="${modelKey}" spellcheck="false"
        value="${escapeHtml(pcfg.model || "")}" data-orig="${escapeHtml(pcfg.model || "")}"
        placeholder="Để trống = model mặc định của hãng" list="dl-model-${escapeHtml(p)}">
      <datalist class="prov-model-datalist" id="dl-model-${escapeHtml(p)}"></datalist>
      <div class="test" style="margin-top:10px;">
        <button type="button" class="btn prov-test-btn">Lưu &amp; kiểm tra ${escapeHtml(shortTag)}</button>
        <span class="prov-test-msg" role="status" style="font-size:12px;"></span>
      </div>
    </div>
  `;

  // Mở rộng/thu gọn cấu hình chi tiết của từng hãng
  const toggleBtn = card.querySelector(".prov-toggle-cfg");
  toggleBtn.onclick = async () => {
    const isOpen = card.classList.toggle("open");
    toggleBtn.textContent = isOpen ? "Thu gọn ▴" : "Cấu hình ▾";
    if (isOpen) {
      await populateCardModelSelect(p, card);
    }
  };

  // Gạt bật/tắt provider song song
  const cb = card.querySelector(".prov-enable-cb");
  cb.onchange = () => {
    card.classList.toggle("enabled", cb.checked);
  };

  // Nút đăng nhập Claude CLI
  const claudeBtn = card.querySelector(".prov-claude-login");
  if (claudeBtn) {
    const claudeMsg = card.querySelector(".prov-claude-msg");
    claudeBtn.onclick = async () => {
      claudeBtn.disabled = true;
      claudeMsg.className = "prov-claude-msg";
      try {
        if (await claudeLoggedIn()) {
          claudeMsg.className = "prov-claude-msg ok";
          claudeMsg.textContent = "Đã đăng nhập Claude CLI.";
          return;
        }
        const r = await fetch("/api/claude-login", { method: "POST" });
        if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || "Không mở được cửa sổ đăng nhập");
        claudeMsg.textContent = "Đã mở cửa sổ đăng nhập. Hoàn tất trên trình duyệt (chờ tối đa 3 phút)...";
        for (let i = 0; i < 60; i++) {
          await new Promise((ok) => setTimeout(ok, 3000));
          if (await claudeLoggedIn()) {
            claudeMsg.className = "prov-claude-msg ok";
            claudeMsg.textContent = "Đã đăng nhập Claude CLI. Bấm Kiểm tra kết nối.";
            return;
          }
        }
        claudeMsg.className = "prov-claude-msg err";
        claudeMsg.textContent = "Chưa thấy đăng nhập xong. Bấm lại để thử.";
      } catch (e) {
        claudeMsg.className = "prov-claude-msg err";
        claudeMsg.textContent = e.message;
      } finally {
        claudeBtn.disabled = false;
      }
    };
  }

  // Nút Lưu & kiểm tra kết nối độc lập cho từng hãng
  const testBtn = card.querySelector(".prov-test-btn");
  const testMsg = card.querySelector(".prov-test-msg");
  testBtn.onclick = async () => {
    if (!cb.checked) {
      cb.checked = true;
      card.classList.add("enabled");
    }
    if (!(await saveSettings({ keepOpen: true, silentNoChange: true }))) return;
    testMsg.className = "prov-test-msg";
    testMsg.textContent = `Đang kiểm tra ${shortTag} (tối đa 90 giây)...`;
    testBtn.disabled = true;
    try {
      const mVal = (card.querySelector(".prov-model-input")?.value || "").trim();
      const resp = await fetch("/api/test-ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: p, model: mVal })
      });
      const j = await resp.json().catch(() => ({}));
      testMsg.className = j.ok ? "prov-test-msg ok" : "prov-test-msg err";
      testMsg.textContent = j.ok
        ? `Kết nối ${shortTag} thành công ("${j.text}")`
        : `Chưa kết nối được: ${j.error || j.detail || "không có trả lời"}`;
    } catch (err) {
      testMsg.className = "prov-test-msg err";
      testMsg.textContent = `Lỗi kiểm tra: ${err.message}`;
    } finally {
      testBtn.disabled = false;
    }
  };

  return card;
}

function renderProvidersSettings(r, defaultProviderOverride = null) {
  const container = $("s-providers-list");
  if (!container) return;
  const defProv = defaultProviderOverride !== null ? defaultProviderOverride : (r.settings.KURO_PROVIDER.value || "");
  const pcfgs = r.providers_config || {};

  // Ghi nhớ những card đang mở rộng nếu re-render
  const openSet = new Set(Array.from(container.querySelectorAll(".prov-card.open")).map(el => el.dataset.provider));
  container.innerHTML = "";

  const cliKeys = Object.keys(r.providers).filter(k => (r.providers[k].group || "api") === "cli");
  const apiKeys = Object.keys(r.providers).filter(k => (r.providers[k].group || "api") !== "cli");

  const appendGroup = (title, keys) => {
    if (!keys.length) return;
    const hdr = document.createElement("div");
    hdr.className = "prov-group-title";
    hdr.textContent = title;
    container.appendChild(hdr);
    for (const k of keys) {
      const info = r.providers[k];
      const pcfg = pcfgs[k] || { enabled: k === defProv, model: r.model_theo_ai?.[k] || "" };
      const card = buildProviderCard(k, info, pcfg, k === defProv);
      if (openSet.has(k) || (openSet.size === 0 && k === defProv)) {
        card.classList.add("open");
        const tbtn = card.querySelector(".prov-toggle-cfg");
        if (tbtn) tbtn.textContent = "Thu gọn ▴";
        populateCardModelSelect(k, card).catch(() => {});
      }
      container.appendChild(card);
    }
  };

  appendGroup("Tài khoản CLI trên máy (chạy song song không cần API key)", cliKeys);
  appendGroup("Nhà cung cấp API Key & Local (Ollama)", apiKeys);
}

async function openSettings() {
  const r = await (await fetch("/api/settings")).json();
  lastSettingsData = r;
  window._providers = r.providers;
  modelTheoAi = r.model_theo_ai || {};

  const sel = $("s-KURO_PROVIDER");
  sel.replaceChildren(
    new Option("- Chưa chọn -", ""),
    ...Object.entries(r.providers).map(([k, v]) => new Option(v.ten, k))
  );
  sel.value = sel.dataset.orig = r.settings.KURO_PROVIDER.value || "";

  // Đổ các trường ngoài khối Lõi AI (Telegram, Allowed Tools...)
  for (const [k, meta] of Object.entries(r.settings)) {
    if (k === "KURO_PROVIDER" || k === "KURO_ENABLED_PROVIDERS" || k.startsWith("KURO_MODEL") || k.startsWith("KURO_AI_KEY") || k.startsWith("KURO_BASE_URL")) {
      continue;
    }
    const el = $("sf").elements[k];
    if (!el) continue;
    if (meta.set) {
      el.value = "";
      el.placeholder = "Đã lưu (" + meta.hint + ") - để trống = giữ nguyên";
    } else {
      el.value = el.dataset.orig = meta.value || "";
      el.placeholder = "";
    }
    delete el.dataset.clear;
  }

  renderProvidersSettings(r);
  showCore(r);
  if (!$("settings").open) {
    $("settings").showModal();
  }
  loadKhoLich().catch(() => {});
}

// Việc theo lịch và kho skill (specs/002). Chữ từ repo gán bằng textContent, không qua innerHTML.
function khoRow(ten, meta, btnText, onClick) {
  const row = document.createElement("div");
  row.className = "kho-row";
  const left = document.createElement("div");
  const b = document.createElement("b"); b.textContent = ten;
  const m = document.createElement("div"); m.className = "meta"; m.textContent = meta;
  left.append(b, m);
  row.append(left);
  for (const [t, fn] of btnText ? [[btnText, onClick]] : []) {
    const btn = document.createElement("button");
    btn.type = "button"; btn.className = "btn"; btn.textContent = t;
    btn.onclick = async () => { btn.disabled = true; try { await fn(btn); } finally { btn.disabled = false; } };
    row.append(btn);
  }
  return row;
}

async function loadKhoLich() {
  const post = (url, body) => fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  const lich = await (await fetch("/api/lich")).json();
  $("s-lich").replaceChildren(...lich.viec.map((v) => {
    const lan = v.lan_chay ? `lần chạy gần nhất ${v.lan_chay.luc.replace("T", " ")}` : "chưa chạy lần nào";
    const row = khoRow(v.ten || v.id, `${v.cron} · ${v.enabled ? "đang bật" : "đang tắt"} · ${lan}`, "Chạy thử", async (btn) => {
      btn.textContent = "Đang chạy...";
      const j = await (await post(`/api/lich/${encodeURIComponent(v.id)}/chay`)).json();
      btn.textContent = "Chạy thử";
      row.querySelector(".meta").textContent = (j.ket_qua || j.detail || "").slice(0, 200);
    });
    const tg = document.createElement("button");
    tg.type = "button"; tg.className = "btn"; tg.textContent = v.enabled ? "Tắt" : "Bật";
    tg.onclick = async () => { await post(`/api/lich/${encodeURIComponent(v.id)}`, { enabled: !v.enabled }); loadKhoLich(); };
    row.append(tg);
    return row;
  }));
  const k = await (await fetch("/api/kho")).json();
  const rows = k.nguon.map((n) => khoRow(n.ten, `${n.so_skill} skill · ${n.giay_phep} · commit ${n.commit.slice(0, 7)}${n.can_bash ? " · " + n.can_bash : ""}`));
  rows.push(...k.goi_ma.map((g) => khoRow(`Mã: ${g.id}`, g.da_duyet ? `đã duyệt ${g.ngay || "(đi kèm bản Kuro)"}` : "chưa duyệt hoặc đã đổi sau khi duyệt: Kuro không chạy",
    g.da_duyet ? null : "Duyệt", async () => {
      const r = await post("/api/kho/duyet", { skill: g.id });
      if (r.ok) loadKhoLich();
    })));
  rows.push(...k.ban_moi_cho_duyet.map((p) => khoRow(`Bản mới chờ duyệt: ${p}`, "người bảo trì đọc ở kho/_cho-duyet/ rồi chạy lại tools/dong_bo_kho.py")));
  $("s-kho").replaceChildren(...rows);
}

async function claudeLoggedIn() {
  const r = await fetch("/api/claude-login");
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.detail || "Lỗi kiểm tra đăng nhập");
  return j.loggedIn;
}

$("s-KURO_PROVIDER").onchange = () => {
  const newDef = $("s-KURO_PROVIDER").value;
  if (!lastSettingsData) return;
  // Cập nhật trạng thái mặc định trên các thẻ hiện có mà không mất giá trị người dùng đang nhập dở
  const cards = document.querySelectorAll("#s-providers-list .prov-card");
  cards.forEach((card) => {
    const p = card.dataset.provider;
    const isDef = p === newDef;
    card.classList.toggle("is-default", isDef);
    const cb = card.querySelector(".prov-enable-cb");
    if (cb) {
      if (isDef) {
        cb.checked = true;
        cb.disabled = true;
        card.classList.add("enabled");
      } else {
        cb.disabled = false;
      }
    }
    const titleEl = card.querySelector(".prov-card-title");
    if (titleEl) {
      const oldDefPill = titleEl.querySelector(".prov-pill-def");
      if (isDef && !oldDefPill) {
        const sp = document.createElement("span");
        sp.className = "prov-pill-def";
        sp.textContent = "Mặc định";
        titleEl.appendChild(sp);
      } else if (!isDef && oldDefPill) {
        oldDefPill.remove();
      }
    }
  });
};

async function saveSettings(opts = {}) {
  const body = {};
  for (const el of $("sf").querySelectorAll("[name]")) {
    if (el.dataset.secret ? (el.value || el.dataset.clear) : (el.value !== el.dataset.orig)) {
      body[el.name] = el.value;
    }
  }

  // Gom danh sách nhà cung cấp đang bật đồng thời
  const enabledCbs = Array.from(document.querySelectorAll("#s-providers-list .prov-enable-cb"));
  if (enabledCbs.length) {
    const defProv = $("s-KURO_PROVIDER").value;
    const enabledList = enabledCbs.filter(cb => cb.checked || cb.dataset.provider === defProv).map(cb => cb.dataset.provider);
    const nextEnabled = enabledList.join(",");
    const prevEnabled = (lastSettingsData && lastSettingsData.enabled_providers) ? lastSettingsData.enabled_providers.join(",") : "";
    const origEnv = (lastSettingsData && lastSettingsData.settings?.KURO_ENABLED_PROVIDERS?.value) || "";
    if (nextEnabled !== prevEnabled || (!origEnv && enabledList.length > 0)) {
      body["KURO_ENABLED_PROVIDERS"] = nextEnabled;
    }
  }

  const msg = $("s-msg");
  if (!Object.keys(body).length) {
    if (!opts.silentNoChange) {
      msg.className = "";
      msg.textContent = "Chưa có gì thay đổi.";
    }
    return true;
  }
  const r = await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const j = await r.json().catch(() => ({}));
  msg.className = r.ok ? "" : "err";
  msg.textContent = !r.ok ? (j.detail || "Lưu thất bại") : j.restart ? "Đã lưu. Khởi động lại Kuro để áp dụng Telegram." : "Đã lưu. Có hiệu lực ngay cho các lượt chat kế tiếp.";
  if (r.ok) {
    providerModelsCache = {};
    if (!opts.keepOpen) {
      await openSettings();
    } else {
      // Cập nhật lại orig của các input để bấm test lần nữa không gửi lại
      const fresh = await (await fetch("/api/settings")).json();
      lastSettingsData = fresh;
      showCore(fresh);
      for (const el of $("sf").querySelectorAll("[name]")) {
        if (el.dataset.secret) {
          el.value = "";
          delete el.dataset.clear;
        } else {
          el.dataset.orig = el.value;
        }
      }
    }
    loadModels().catch(() => {});
    fetchAndRenderQuota().catch(() => {});
  }
  return r.ok;
}
$("sf").onsubmit = (e) => {
  e.preventDefault();
  saveSettings();
};

$("sf").addEventListener("click", (e) => {
  const k = e.target.dataset.clear;
  if (!k) return;
  const el = $("sf").elements[k];
  if (!el) return;
  el.value = "";
  el.dataset.clear = "1";
  el.placeholder = "Sẽ xóa khi bấm Lưu";
});

$("gear").onclick = $("gear2").onclick = openSettings;
$("s-close").onclick = () => $("settings").close();

// ========================================================
// BỘ CHỌN NHANH MODEL ĐA NHÀ CUNG CẤP (CHẠY SONG SONG THEO PHIÊN)
// ========================================================
let pendingSessionProvider = "";
let pendingSessionModel = "";
let activeSessionProvider = "";
let activeSessionModel = "";
let defaultProvider = "";
let defaultModel = "";
let modelGroups = [];

let currentChatMode = "auto"; // auto | plan | goal
let availableModelsList = [];

// Tải toàn bộ danh sách model của các nhà cung cấp AI đang bật song song
async function loadModels() {
  const r = await (await fetch("/api/models?scope=enabled")).json();
  modelGroups = r.groups || [];
  defaultProvider = r.default_provider || "";
  defaultModel = r.default_model || "";
  availableModelsList = [];
  for (const g of modelGroups) {
    for (const m of (g.models || [])) {
      availableModelsList.push({ ...m, provider: g.provider, provider_short: g.short });
    }
  }

  const sel = $("model-pick");
  if (sel) {
    sel.hidden = true;
    if (availableModelsList.length) {
      const opts = availableModelsList.map((m) => new Option(`[${m.provider_short}] ${m.ten}`, m.id));
      opts.unshift(new Option("Model mặc định", ""));
      sel.replaceChildren(...opts);
    }
  }

  // Ưu tiên provider + model của session đang mở
  const sessObj = session ? currentSessions.find(s => s.id === session) : null;
  const ag = typeof currentAgent === "function" ? currentAgent() : null;
  const effProv = sessObj
    ? (sessObj.provider || activeSessionProvider || "")
    : (pendingSessionProvider || (ag && ag.provider) || "");
  const effModel = sessObj
    ? (sessObj.model || "")
    : (pendingSessionProvider ? pendingSessionModel : (pendingSessionModel || (ag && ag.model) || ""));

  activeSessionProvider = effProv;
  activeSessionModel = effModel;
  if (sel) sel.value = effModel;
  updateModelPillUI(effModel, effProv);
  renderModelMenuPopover(effModel, effProv);
  updateContextEnvModel(effModel, effProv);
}

function findModelLabel(modelId, providerId = "") {
  if (!modelId) return "";
  if (providerId) {
    const grp = modelGroups.find(g => g.provider === providerId);
    if (grp) {
      const m = (grp.models || []).find(x => x.id === modelId);
      if (m && m.ten) return m.ten;
    }
  }
  const match = availableModelsList.find(m => m.id === modelId);
  return match ? match.ten : modelId;
}

function updateContextEnvModel(modelId, providerId = "") {
  const envModel = $("ctx-env-model");
  if (!envModel) return;
  const p = providerId || activeSessionProvider || defaultProvider;
  const pShort = getProviderShort(p);
  const label = findModelLabel(modelId, p) || "Mặc định";
  envModel.textContent = pShort ? `[${pShort}] ${label}` : label;
}

function updateModelPillUI(modelId, providerId = "") {
  const pillLabel = $("model-pill-label");
  if (!pillLabel) return;
  const p = providerId || activeSessionProvider || defaultProvider;
  const pShort = getProviderShort(p);
  const pCls = getProviderClass(p);
  const grp = modelGroups.find(g => g.provider === p);
  const effectiveModelId = modelId || (grp && grp.default_model) || "";
  const label = modelId
    ? findModelLabel(modelId, p)
    : (effectiveModelId ? `Mặc định · ${findModelLabel(effectiveModelId, p)}` : "Model mặc định");

  if (pShort) {
    pillLabel.innerHTML = `<span class="prov-tag ${pCls}" style="margin-right:5px;">${escapeHtml(pShort)}</span><span>${escapeHtml(label)}</span>`;
  } else {
    pillLabel.textContent = label;
  }
}

function renderModelMenuPopover(activeVal, activeProv = "") {
  const container = $("model-menu-items");
  const controls = $("model-menu-controls");
  const tabsEl = $("model-menu-tabs");
  const searchEl = $("model-menu-search");
  if (!container) return;

  const effProv = activeProv || activeSessionProvider || defaultProvider;
  const totalModels = modelGroups.reduce((acc, g) => acc + (g.models ? g.models.length : 0) + 1, 0);

  // Nút cài đặt nhanh kết nối AI
  const cfgBtn = $("btn-model-menu-settings");
  if (cfgBtn && !cfgBtn._bound) {
    cfgBtn._bound = true;
    cfgBtn.onclick = (e) => {
      e.stopPropagation();
      hideBottomPopovers();
      openSettings();
    };
  }

  // Hiển thị tab lọc hãng + ô tìm kiếm khi có từ 2 nhà cung cấp trở lên hoặc nhiều model
  if (controls && tabsEl) {
    const showControls = modelGroups.length > 1 || totalModels > 8;
    controls.style.display = showControls ? "flex" : "none";
    if (showControls) {
      if (modelMenuFilterProvider !== "all" && !modelGroups.some(g => g.provider === modelMenuFilterProvider)) {
        modelMenuFilterProvider = "all";
      }
      tabsEl.innerHTML = "";
      if (modelGroups.length > 1) {
        const allTab = document.createElement("button");
        allTab.type = "button";
        allTab.className = `model-menu-tab${modelMenuFilterProvider === "all" ? " active" : ""}`;
        allTab.textContent = `Tất cả (${modelGroups.length})`;
        allTab.onclick = (e) => {
          e.stopPropagation();
          modelMenuFilterProvider = "all";
          renderModelMenuPopover(activeVal, activeProv);
        };
        tabsEl.appendChild(allTab);

        for (const g of modelGroups) {
          const t = document.createElement("button");
          t.type = "button";
          t.className = `model-menu-tab${modelMenuFilterProvider === g.provider ? " active" : ""}`;
          t.textContent = g.short || g.provider;
          t.onclick = (e) => {
            e.stopPropagation();
            modelMenuFilterProvider = g.provider;
            renderModelMenuPopover(activeVal, activeProv);
          };
          tabsEl.appendChild(t);
        }
      }
      if (searchEl && !searchEl._bound) {
        searchEl._bound = true;
        searchEl.onclick = (e) => e.stopPropagation();
        searchEl.oninput = () => {
          modelMenuSearchQuery = searchEl.value.trim().toLowerCase();
          renderModelMenuPopover(activeSessionModel, activeSessionProvider);
        };
      }
    }
  }

  const q = modelMenuSearchQuery;
  const groupsToShow = modelGroups.filter(g => modelMenuFilterProvider === "all" || g.provider === modelMenuFilterProvider);

  if (!groupsToShow.length) {
    container.innerHTML = `<div style="padding:12px 14px; font-size:12px; color:var(--muted);">Chưa bật nhà cung cấp AI nào. Bấm <b>⚙ Kết nối</b> để cấu hình.</div>`;
    return;
  }

  let html = "";
  for (const g of groupsToShow) {
    const p = g.provider;
    const pCls = getProviderClass(p);
    const defLabel = g.default_model ? `Mặc định (${findModelLabel(g.default_model, p)})` : "Model mặc định";
    const items = [{ id: "", ten: defLabel, isDefaultOpt: true }, ...(g.models || [])];
    const filtered = q
      ? items.filter(m =>
          (m.ten || "").toLowerCase().includes(q) ||
          (m.id || "").toLowerCase().includes(q) ||
          (g.name || "").toLowerCase().includes(q) ||
          (g.short || "").toLowerCase().includes(q)
        )
      : items;
    if (!filtered.length) continue;

    const cliWarn = (g.cli_installed === false) ? `<span style="color:var(--amber); font-size:9.5px;">chưa cài CLI</span>` : "";
    html += `
      <div class="model-menu-group-hdr">
        <span style="display:inline-flex; align-items:center; gap:6px;">
          <span class="prov-tag ${pCls}">${escapeHtml(g.short || p)}</span>
          <span>${escapeHtml(g.name || p)}</span>
        </span>
        ${cliWarn}
      </div>
    `;
    for (const m of filtered) {
      const isAct = (p === effProv) && ((m.id || "") === (activeVal || ""));
      html += `
        <button type="button" class="model-menu-item ${isAct ? "active" : ""}" data-provider="${escapeHtml(p)}" data-model-id="${escapeHtml(m.id || "")}">
          <span class="model-item-main">
            <span class="model-item-name">${escapeHtml(m.ten || m.id)}</span>
          </span>
          ${isAct ? '<span class="model-check">✓</span>' : ""}
        </button>
      `;
    }
  }

  container.innerHTML = html || `<div style="padding:12px 14px; font-size:12px; color:var(--muted);">Không tìm thấy model khớp "${escapeHtml(q)}".</div>`;

  container.querySelectorAll(".model-menu-item").forEach(btn => {
    btn.onclick = async () => {
      const chosenProv = btn.dataset.provider || defaultProvider || "";
      const chosenModel = btn.dataset.modelId || "";
      await selectModelForSession(chosenModel, chosenProv);
      hideBottomPopovers();
    };
  });
}

async function selectModelForSession(chosenModel, chosenProvider = "") {
  const prov = chosenProvider || activeSessionProvider || defaultProvider || "";
  activeSessionProvider = prov;
  activeSessionModel = chosenModel;
  const sel = $("model-pick");
  if (sel) sel.value = chosenModel;
  updateModelPillUI(chosenModel, prov);
  renderModelMenuPopover(chosenModel, prov);
  updateContextEnvModel(chosenModel, prov);

  const pShort = getProviderShort(prov);
  if (session) {
    try {
      const r = await fetch(`/api/sessions/${session}/model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: prov, model: chosenModel })
      });
      const sessObj = currentSessions.find(s => s.id === session);
      if (sessObj) {
        sessObj.provider = prov;
        sessObj.model = chosenModel;
      }
      renderSessionList();
      loadSessionContext(session).catch(() => {});
      if (typeof fetchAndRenderQuota === "function") fetchAndRenderQuota().catch(() => {});
      $("state").textContent = r.ok ? `Phiên này đang dùng ${pShort || "AI"}` : "Lỗi lưu model";
      setTimeout(() => { if (!busy) $("state").textContent = "Sẵn sàng"; }, 2200);
    } catch (err) {
      console.error("Lỗi cập nhật model session:", err);
    }
  } else {
    pendingSessionProvider = prov;
    pendingSessionModel = chosenModel;
    if (typeof fetchAndRenderQuota === "function") fetchAndRenderQuota().catch(() => {});
    $("state").textContent = `Phiên mới sẽ dùng ${pShort || "AI"}`;
    setTimeout(() => { if (!busy) $("state").textContent = "Sẵn sàng"; }, 2200);
  }
}

function hideBottomPopovers() {
  const attachMenu = $("attach-menu-popover");
  const modelMenu = $("model-menu-popover");
  const modeMenu = $("mode-menu-popover");
  const thinkMenu = $("thinking-menu-popover");
  const flyConnectors = $("flyout-connectors");
  const flyPlugins = $("flyout-plugins");
  const quotaMenu = $("quota-menu-popover");
  if (attachMenu) attachMenu.style.display = "none";
  if (modelMenu) modelMenu.style.display = "none";
  if (modeMenu) modeMenu.style.display = "none";
  if (thinkMenu) thinkMenu.style.display = "none";
  if (flyConnectors) flyConnectors.style.display = "none";
  if (flyPlugins) flyPlugins.style.display = "none";
  if (quotaMenu) quotaMenu.style.display = "none";
}

// Bắt sự kiện click ra ngoài để đóng các popover dưới đáy
document.addEventListener("click", (e) => {
  if (!e.target.closest("#btn-chat-plus") && !e.target.closest("#attach-menu-popover") &&
      !e.target.closest("#btn-model-pill") && !e.target.closest("#model-menu-popover") &&
      !e.target.closest("#btn-thinking-pill") && !e.target.closest("#thinking-menu-popover") &&
      !e.target.closest("#btn-mode-pill") && !e.target.closest("#mode-menu-popover") &&
      !e.target.closest("#btn-quota-ring") && !e.target.closest("#quota-menu-popover")) {
    hideBottomPopovers();
  }
});

// Nút cộng (+) mở menu đính kèm
const btnChatPlus = $("btn-chat-plus");
if (btnChatPlus) {
  btnChatPlus.onclick = (e) => {
    e.stopPropagation();
    const menu = $("attach-menu-popover");
    const isVisible = menu && menu.style.display === "flex";
    hideBottomPopovers();
    if (menu && !isVisible) {
      menu.style.display = "flex";
    }
  };
}

// Xử lý các lựa chọn trong menu dấu cộng
if ($("menu-attach-file")) {
  $("menu-attach-file").onclick = async () => {
    hideBottomPopovers();
    // Thử gọi Native Windows File Picker trước
    try {
      const res = await fetch("/api/fs/pick-native-file", { method: "POST" });
      const data = await res.json();
      if (data.ok && data.files && data.files.length) {
        insertTextAtCursor($("q"), formatFilePaths(data.files));
        return;
      }
    } catch (_) {}
    // Fallback sang input file web chuẩn
    const fi = $("general-file-input");
    if (fi) {
      fi.accept = "*/*";
      fi.click();
    }
  };
}

if ($("menu-attach-folder")) {
  $("menu-attach-folder").onclick = async () => {
    hideBottomPopovers();
    // Mở Native Folder Browser để chọn thư mục chèn vào chat
    try {
      const res = await fetch("/api/workspaces/browse-native", { method: "POST" });
      const data = await res.json();
      if (data.ok && data.path) {
        insertTextAtCursor($("q"), `"${data.path}" `);
      }
    } catch (e) {
      console.error("Lỗi chọn thư mục:", e);
    }
  };
}

if ($("menu-attach-slash")) {
  $("menu-attach-slash").onclick = () => {
    hideBottomPopovers();
    const q = $("q");
    if (q) {
      q.value = "/" + q.value.replace(/^\/+/, "");
      q.focus();
      q.setSelectionRange(q.value.length, q.value.length);
      handleSlashInput();
    }
  };
}

// Flyout Trình kết nối
const menuWrapConnectors = $("menu-wrap-connectors");
const flyConnectors = $("flyout-connectors");
if (menuWrapConnectors && flyConnectors) {
  $("menu-attach-connectors").onclick = (e) => {
    e.stopPropagation();
    const isShow = flyConnectors.style.display === "flex";
    if ($("flyout-plugins")) $("flyout-plugins").style.display = "none";
    flyConnectors.style.display = isShow ? "none" : "flex";
  };
  menuWrapConnectors.onmouseenter = () => {
    if ($("flyout-plugins")) $("flyout-plugins").style.display = "none";
    flyConnectors.style.display = "flex";
  };
}

// Flyout Plugin & Kỹ năng
const menuWrapPlugins = $("menu-wrap-plugins");
const flyPlugins = $("flyout-plugins");
if (menuWrapPlugins && flyPlugins) {
  $("menu-attach-plugins").onclick = (e) => {
    e.stopPropagation();
    const isShow = flyPlugins.style.display === "flex";
    if ($("flyout-connectors")) $("flyout-connectors").style.display = "none";
    flyPlugins.style.display = isShow ? "none" : "flex";
  };
  menuWrapPlugins.onmouseenter = () => {
    if ($("flyout-connectors")) $("flyout-connectors").style.display = "none";
    flyPlugins.style.display = "flex";
  };
}

// Tìm kiếm plugin trong flyout
const pluginSearch = $("plugin-flyout-search");
if (pluginSearch) {
  pluginSearch.oninput = () => {
    const term = (pluginSearch.value || "").trim().toLowerCase();
    document.querySelectorAll(".flyout-sub-plugin-item").forEach(item => {
      const title = (item.querySelector(".plugin-item-title")?.textContent || "").toLowerCase();
      const desc = (item.querySelector(".plugin-item-desc")?.textContent || "").toLowerCase();
      item.style.display = (!term || title.includes(term) || desc.includes(term)) ? "flex" : "none";
    });
  };
}

// Bấm vào plugin/kỹ năng trong flyout
document.querySelectorAll(".flyout-sub-plugin-item").forEach(btn => {
  btn.onclick = () => {
    const skill = btn.dataset.skill;
    hideBottomPopovers();
    const q = $("q");
    if (q && skill) {
      q.value = `/${skill} `;
      q.focus();
      q.setSelectionRange(q.value.length, q.value.length);
      handleSlashInput();
    }
  };
});

if ($("btn-conn-manage")) {
  $("btn-conn-manage").onclick = () => {
    hideBottomPopovers();
    openSettings();
  };
}
if ($("btn-conn-browse")) {
  $("btn-conn-browse").onclick = () => {
    hideBottomPopovers();
    openSettings();
  };
}
const openPluginsHandler = () => {
  hideBottomPopovers();
  switchInspectorTab("context");
  $("history-sidebar").classList.remove("collapsed");
  syncHistoryToggleBtn();
};
if ($("btn-plugin-manage")) $("btn-plugin-manage").onclick = openPluginsHandler;
if ($("btn-plugin-browse")) $("btn-plugin-browse").onclick = openPluginsHandler;

// Nút chọn Model Pill
const btnModelPill = $("btn-model-pill");
if (btnModelPill) {
  btnModelPill.onclick = (e) => {
    e.stopPropagation();
    const menu = $("model-menu-popover");
    const isVisible = menu && menu.style.display === "flex";
    hideBottomPopovers();
    if (menu && !isVisible) {
      modelMenuSearchQuery = "";
      const s = $("model-menu-search");
      if (s) s.value = "";
      renderModelMenuPopover(activeSessionModel, activeSessionProvider);
      menu.style.display = "flex";
    }
  };
}

// Nút chọn Mức suy nghĩ (Thinking Pill)
let currentThinkingMode = "high";
const btnThinkingPill = $("btn-thinking-pill");
if (btnThinkingPill) {
  btnThinkingPill.onclick = (e) => {
    e.stopPropagation();
    const menu = $("thinking-menu-popover");
    const isVisible = menu && menu.style.display === "flex";
    hideBottomPopovers();
    if (menu && !isVisible) {
      menu.style.display = "flex";
    }
  };
}

const thinkingItems = document.querySelectorAll("#thinking-menu-popover .mode-menu-item");
thinkingItems.forEach(item => {
  item.onclick = () => {
    const t = item.dataset.thinking;
    currentThinkingMode = t;
    thinkingItems.forEach(i => {
      const isCur = i.dataset.thinking === t;
      i.classList.toggle("active", isCur);
      const spanCheck = i.querySelector(".mode-item-title span:last-child");
      if (spanCheck) spanCheck.textContent = isCur ? "✓" : "";
    });
    const labelMap = { high: "Cao", standard: "Tiêu chuẩn", off: "Tắt" };
    const labelEl = $("thinking-pill-label");
    if (labelEl) labelEl.textContent = labelMap[t] || "Cao";
    hideBottomPopovers();
  };
});

// Nút chọn Chế độ thực thi (Mode)
const btnModePill = $("btn-mode-pill");
if (btnModePill) {
  btnModePill.onclick = (e) => {
    e.stopPropagation();
    const menu = $("mode-menu-popover");
    const isVisible = menu && menu.style.display === "flex";
    hideBottomPopovers();
    if (menu && !isVisible) {
      menu.style.display = "flex";
    }
  };
}

// Xử lý chọn Mode (Auto, Plan, Goal)
const modeItems = document.querySelectorAll("#mode-menu-popover .mode-menu-item");
modeItems.forEach(item => {
  item.onclick = () => {
    const mode = item.dataset.mode;
    currentChatMode = mode;
    modeItems.forEach(i => {
      const isCur = i.dataset.mode === mode;
      i.classList.toggle("active", isCur);
      const check = i.querySelector(".mode-item-title span:last-child");
      if (check && !check.textContent.includes("(") && !check.textContent.includes("✓")) {
        // bỏ qua
      }
    });
    const labelMap = { auto: "Tự động", plan: "Kế hoạch", goal: "Mục tiêu" };
    const labelEl = $("mode-pill-label");
    if (labelEl) labelEl.textContent = labelMap[mode] || "Tự động";
    hideBottomPopovers();
  };
});

// ========================================================
// HẠN MỨC SỬ DỤNG AI (BLOCK 5 GIỜ & TUẦN)
// ========================================================
let lastQuotaData = null;

async function fetchAndRenderQuota() {
  try {
    const sid = (typeof session !== "undefined") ? session : "";
    const prov = activeSessionProvider || pendingSessionProvider || "";
    const qs = new URLSearchParams();
    if (sid) qs.set("session_id", sid);
    if (prov) qs.set("provider", prov);
    const res = await fetch(`/api/quota?${qs.toString()}`);
    if (!res.ok) return;
    const data = await res.json();
    lastQuotaData = data;

    const pct5h = data.block_5h.percent;
    const pctWeek = data.weekly.percent;

    // 1. Cập nhật vòng tròn SVG Quota (Xanh dương khi còn nhiều -> Vàng nhạt khi cao -> Đỏ khi gần hết)
    const quotaColor = (pct5h >= 90) ? "var(--quota-danger)" : (pct5h >= 70) ? "var(--quota-warn)" : "var(--quota-ok)";
    const circle = $("quota-circle-bar");
    if (circle) {
      const maxLen = 47.12;
      const offset = maxLen * (1 - Math.min(100, pct5h) / 100);
      circle.style.strokeDashoffset = offset;
      circle.style.stroke = quotaColor;
    }

    const dot = $("quota-center-dot");
    if (dot) {
      dot.style.background = quotaColor;
      dot.style.boxShadow = `0 0 5px ${quotaColor}`;
    }

    const pShort = data.provider_short || getProviderShort(data.provider);
    const btn = $("btn-quota-ring");
    if (btn) {
      btn.title = `Hạn mức ${pShort || "AI"}: Block 5h ${pct5h}% (${data.block_5h.reset_in}) · Tuần ${pctWeek}% (Bấm để xem chi tiết)`;
    }

    // 2. Cập nhật dữ liệu Popover
    if ($("quota-model-name")) {
      const mLabel = data.model_name || data.model_id || "Model mặc định";
      $("quota-model-name").textContent = pShort ? `[${pShort}] ${mLabel}` : mLabel;
    }
    if ($("quota-5h-val")) $("quota-5h-val").textContent = `${pct5h}%`;
    if ($("quota-5h-bar")) {
      $("quota-5h-bar").style.width = `${Math.min(100, pct5h)}%`;
      $("quota-5h-bar").className = "quota-progress-fill" + (pct5h >= 90 ? " danger" : pct5h >= 70 ? " warn" : "");
    }
    if ($("quota-5h-reset")) $("quota-5h-reset").textContent = `Làm mới lúc ${data.block_5h.reset_time} (${data.block_5h.reset_in})`;
    if ($("quota-5h-count")) $("quota-5h-count").textContent = `${data.block_5h.used_count}/${data.block_5h.max_count} lượt hỏi`;

    if ($("quota-week-val")) $("quota-week-val").textContent = `${pctWeek}%`;
    if ($("quota-week-bar")) {
      $("quota-week-bar").style.width = `${Math.min(100, pctWeek)}%`;
      $("quota-week-bar").className = "quota-progress-fill week" + (pctWeek >= 90 ? " danger" : pctWeek >= 70 ? " warn" : "");
    }
    if ($("quota-week-reset")) $("quota-week-reset").textContent = `Làm mới: ${data.weekly.reset_day}`;
    if ($("quota-week-count")) $("quota-week-count").textContent = `${data.weekly.used_count}/${data.weekly.max_count} lượt tuần này`;

    if ($("quota-status-badge")) {
      $("quota-status-badge").textContent = data.status_text;
    }

    // 3. Thống kê nhanh theo từng nhà cung cấp AI đang bật song song
    const byProvEl = $("quota-by-provider");
    if (byProvEl) {
      const list = data.by_provider || [];
      if (list.length > 1) {
        byProvEl.style.display = "flex";
        byProvEl.innerHTML = list.map(item => `
          <div class="quota-prov-row ${item.provider === data.provider ? "active" : ""}">
            <span>${escapeHtml(item.short)}</span>
            <span>5h: ${item.used_5h} (${item.pct_5h}%) · Tuần: ${item.used_week}</span>
          </div>
        `).join("");
      } else {
        byProvEl.style.display = "none";
      }
    }
  } catch (err) {
    console.warn("Lỗi tải hạn mức quota:", err);
  }
}

// Bắt sự kiện click nút Quota Ring
const btnQuotaRing = $("btn-quota-ring");
if (btnQuotaRing) {
  btnQuotaRing.onclick = (e) => {
    e.stopPropagation();
    const menu = $("quota-menu-popover");
    const isVisible = menu && menu.style.display === "block";
    hideBottomPopovers();
    if (menu && !isVisible) {
      menu.style.display = "block";
      fetchAndRenderQuota();
    }
  };
}

const btnRefreshQuota = $("btn-refresh-quota");
if (btnRefreshQuota) {
  btnRefreshQuota.onclick = (e) => {
    e.stopPropagation();
    fetchAndRenderQuota();
  };
}

// Xử lý input file chọn tài liệu / ảnh từ nút máy tính
const genFileInput = $("general-file-input");
if (genFileInput) {
  genFileInput.onchange = (e) => {
    const files = Array.from(e.target.files || []);
    for (const f of files) {
      uploadGeneralFile(f);
    }
    genFileInput.value = "";
  };
}

// Xóa tham số tạm ?_r= sau khi tải lại trang bằng Ctrl+F5
try {
  const curUrl = new URL(window.location.href);
  if (curUrl.searchParams.has("_r")) {
    curUrl.searchParams.delete("_r");
    window.history.replaceState({}, "", curUrl.pathname + curUrl.search + curUrl.hash);
  }
} catch (_) {}

// Tải lại giao diện Kuro (hỗ trợ cả Kuro App Desktop pywebview lẫn trình duyệt)
async function reloadKuroApp(hard = true) {
  try {
    if (hard && "caches" in window) {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    }
  } catch (_) {}

  try {
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.reload_app === "function") {
      await window.pywebview.api.reload_app(hard);
      return;
    }
  } catch (_) {}

  if (hard) {
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.set("_r", String(Date.now()));
    window.location.replace(nextUrl.toString());
  } else {
    window.location.reload();
  }
}

// Phím tắt toàn cục: Ctrl+F5 / Ctrl+Shift+R (tải lại sạch bỏ cache), F5 / Ctrl+R trên Kuro Desktop, Ctrl+U chọn file
window.addEventListener("keydown", (e) => {
  const key = (e.key || "").toLowerCase();
  const isCtrlOrMeta = e.ctrlKey || e.metaKey;
  const isDesktop = !!(window.pywebview && window.pywebview.api);

  // Ctrl + F5 hoặc Ctrl + Shift + R: tải lại sạch (bỏ cache) ngay cả trên Kuro App Desktop
  if ((isCtrlOrMeta && e.key === "F5") || (isCtrlOrMeta && e.shiftKey && key === "r")) {
    e.preventDefault();
    e.stopPropagation();
    reloadKuroApp(true);
    return;
  }

  // F5 hoặc Ctrl + R trên Kuro Desktop (WebView2 debug=False mặc định tắt phím tắt trình duyệt)
  if (isDesktop && (e.key === "F5" || (isCtrlOrMeta && !e.shiftKey && key === "r"))) {
    e.preventDefault();
    e.stopPropagation();
    reloadKuroApp(false);
    return;
  }

  if (e.ctrlKey && key === "u") {
    e.preventDefault();
    if ($("menu-attach-file")) {
      $("menu-attach-file").click();
    }
  }
}, true);

// Hiển thị tên Core AI & số lượng kết nối song song ở góc chân
function showCore(r) {
  const id = r.settings.KURO_PROVIDER.value;
  const baseName = id && r.providers[id] ? r.providers[id].ten.split(" (")[0] : "Chưa chọn";
  const enabledCount = (r.enabled_providers || []).length;
  $("core").textContent = (id && enabledCount > 1) ? `${baseName} (+${enabledCount - 1} AI)` : baseName;
}

fetch("/api/settings").then((r) => r.json()).then((r) => {
  window._providers = r.providers;
  showCore(r);
  if (!r.settings.KURO_PROVIDER.value) openSettings();
}).catch(() => {});

// ===================== QUẢN LÝ PHIÊN BẢN & CẬP NHẬT (THEO KIẾN TRÚC JAVIS OS) =====================
let versionData = {
  current: "1.5.11",
  latest: "1.5.11",
  behind: 0,
  update_available: false,
  notes: []
};
let updatePollingTimer = null;

async function checkUpdate(force = false) {
  try {
    const res = await fetch(`/api/version?check=${force ? "1" : "0"}`);
    if (!res.ok) return;
    const u = await res.json();
    versionData = u;

    // Cập nhật các nhãn số phiên bản
    const curText = "v" + (u.current || "1.5.11");
    const sideBadge = $("sidebar-version-badge");
    const hdrBtn = $("btn-version-header");
    const hdrText = $("header-version-text");

    if (sideBadge) {
      sideBadge.textContent = curText;
      sideBadge.classList.toggle("has-update", !!u.update_available);
      sideBadge.title = u.update_available
        ? `Đã có Kuro bản mới v${u.latest}! Bấm để cập nhật`
        : `Phiên bản Kuro: ${curText} (Mới nhất)`;
    }
    if (hdrText) hdrText.textContent = curText;
    if (hdrBtn) {
      hdrBtn.classList.toggle("has-update", !!u.update_available);
      hdrBtn.title = u.update_available
        ? `Đã có Kuro bản mới v${u.latest}! Bấm để cập nhật`
        : `Phiên bản Kuro: ${curText} (Mới nhất)`;
    }

    // Hiển thị hoặc ẩn banner thông báo bản mới
    const box = $("update");
    if (box) {
      if (u.update_available) {
        $("update-banner-title").textContent = `ĐÃ CÓ PHIÊN BẢN MỚI v${u.latest}`;
        $("update-banner-text").textContent = `Bạn đang dùng ${curText}. Nhánh GitHub đã có các cập nhật mới.`;
        box.classList.remove("hidden");
        box.hidden = false;
      } else {
        box.classList.add("hidden");
        box.hidden = true;
      }
    }
    return u;
  } catch (e) {
    console.error("Lỗi kiểm tra phiên bản:", e);
  }
}

function openVersionDialog() {
  const u = versionData || { current: "1.5.11", latest: "1.5.11", update_available: false, notes: [] };
  const esc = (t) => DOMPurify.sanitize(t, { ALLOWED_TAGS: [] });

  $("vd-current-ver").textContent = "v" + (u.current || "1.5.11");
  $("vd-latest-ver").textContent = "v" + (u.latest || u.current || "1.5.11");

  const alertBox = $("vd-update-alert-box");
  const progBox = $("vd-progress-box");
  progBox.style.display = "none";

  if (u.update_available) {
    $("vd-latest-status").innerHTML = `<span class="badge-new">🎉 Có bản mới v${esc(u.latest)}</span>`;
    alertBox.style.display = "flex";
    const notesContainer = $("uab-notes-list");
    if (u.notes && u.notes.length) {
      notesContainer.innerHTML = `<b>Nội dung cập nhật mới:</b><ul>${u.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>`;
    } else {
      notesContainer.innerHTML = `<i>Phiên bản v${esc(u.latest)} đã được phát hành trên GitHub.</i>`;
    }
  } else {
    $("vd-latest-status").innerHTML = `<span class="badge-ok">✓ Đang dùng bản mới nhất</span>`;
    alertBox.style.display = "none";
  }

  $("version-dialog").showModal();
}

async function runSelfUpdate(skipConfirm = false) {
  if (!skipConfirm && !confirm("Bắt đầu cập nhật Kuro lên phiên bản mới? Hệ thống sẽ kéo mã nguồn và tự động khởi động lại dịch vụ.")) return;

  const alertBox = $("vd-update-alert-box");
  const progBox = $("vd-progress-box");
  alertBox.style.display = "none";
  progBox.style.display = "flex";

  $("vd-progress-text").textContent = "Đang bắt đầu cập nhật...";
  setUpdateStepper("pull");

  try {
    const res = await fetch("/api/update", { method: "POST" });
    const d = await res.json();
    if (!res.ok) {
      alert("Không thể khởi động cập nhật: " + (d.detail || d.error));
      progBox.style.display = "none";
      alertBox.style.display = "flex";
      return;
    }

    // Bắt đầu vòng lặp theo dõi tiến trình (poll status)
    if (updatePollingTimer) clearInterval(updatePollingTimer);
    updatePollingTimer = setInterval(pollUpdateProgress, 1200);
  } catch (e) {
    alert("Lỗi khi gọi lệnh cập nhật: " + e.message);
    progBox.style.display = "none";
    alertBox.style.display = "flex";
  }
}

function setUpdateStepper(phase) {
  const steps = ["step-pull", "step-install", "step-restart", "step-done"];
  const lines = ["line-1", "line-2", "line-3"];
  const phaseOrder = {
    preparing: 0,
    pulling: 0,
    installing: 1,
    restarting: 2,
    success: 3,
  };

  const currentIdx = phaseOrder[phase] !== undefined ? phaseOrder[phase] : 0;

  steps.forEach((sId, idx) => {
    const el = $(sId);
    if (!el) return;
    el.classList.toggle("done", idx < currentIdx || (phase === "success" && idx === 3));
    el.classList.toggle("active", idx === currentIdx && phase !== "success");
  });

  lines.forEach((lId, idx) => {
    const el = $(lId);
    if (!el) return;
    el.classList.toggle("done", idx < currentIdx);
  });
}

async function pollUpdateProgress() {
  try {
    const res = await fetch("/api/update/status");
    if (!res.ok) {
      // Server đang khởi động lại, kiểm tra health
      checkServerHealthAfterUpdate();
      return;
    }
    const d = await res.json();
    const st = d.state || {};

    if (d.log_tail) {
      $("vd-update-log").textContent = d.log_tail;
      const wrap = $("vd-update-log").parentElement;
      wrap.scrollTop = wrap.scrollHeight;
    }

    if (st.phase === "pulling") {
      $("vd-progress-text").textContent = "Đang tải mã nguồn mới từ GitHub...";
      setUpdateStepper("pull");
    } else if (st.phase === "installing") {
      $("vd-progress-text").textContent = "Đang cập nhật các gói thư viện Python...";
      setUpdateStepper("install");
    } else if (st.phase === "restarting") {
      $("vd-progress-text").textContent = "Đang khởi động lại máy chủ Kuro...";
      setUpdateStepper("restart");
      checkServerHealthAfterUpdate();
    } else if (st.result === "success") {
      $("vd-progress-text").textContent = "Hoàn tất cập nhật!";
      setUpdateStepper("success");
      finishUpdateAndReload();
    } else if (st.result === "error") {
      if (updatePollingTimer) clearInterval(updatePollingTimer);
      $("vd-progress-text").textContent = "❌ Cập nhật thất bại: " + (st.error || "Xem chi tiết nhật ký bên dưới.");
      alert("Cập nhật không thành công: " + (st.error || "Chi tiết trong update.log"));
    }
  } catch (e) {
    // Nếu fetch lỗi do server đang tắt để restart, chuyển sang kiểm tra health
    checkServerHealthAfterUpdate();
  }
}

let healthChecking = false;
function checkServerHealthAfterUpdate() {
  if (healthChecking) return;
  healthChecking = true;

  const hTimer = setInterval(async () => {
    try {
      const r = await fetch("/health", { cache: "no-store" });
      if (r.ok) {
        clearInterval(hTimer);
        if (updatePollingTimer) clearInterval(updatePollingTimer);
        setUpdateStepper("success");
        finishUpdateAndReload();
      }
    } catch (_) {
      // Đang chờ server lên
    }
  }, 1500);
}

function finishUpdateAndReload() {
  $("vd-progress-text").textContent = "🎉 Cập nhật thành công!";
  $("vd-reload-notice").style.display = "block";
  setTimeout(() => {
    window.location.reload();
  }, 2000);
}

// Gán sự kiện cho các nút điều khiển phiên bản & cập nhật
$("sidebar-version-badge") && ($("sidebar-version-badge").onclick = openVersionDialog);
$("btn-version-header") && ($("btn-version-header").onclick = openVersionDialog);
$("btn-open-update-modal") && ($("btn-open-update-modal").onclick = openVersionDialog);
$("btn-dismiss-update") && ($("btn-dismiss-update").onclick = () => {
  $("update").classList.add("hidden");
  $("update").hidden = true;
});
$("btn-close-version-dialog") && ($("btn-close-version-dialog").onclick = () => $("version-dialog").close());
$("btn-close-version-dialog2") && ($("btn-close-version-dialog2").onclick = () => $("version-dialog").close());
$("btn-check-update-manual") && ($("btn-check-update-manual").onclick = async () => {
  $("btn-check-update-manual").textContent = "🔄 Đang kiểm tra...";
  const u = await checkUpdate(true);
  openVersionDialog();
  $("btn-check-update-manual").textContent = "🔄 Kiểm tra bản mới trên GitHub";
  if (u && !u.update_available) {
    alert(`✓ Hệ thống đã kiểm tra trên GitHub:\nBạn đang sử dụng phiên bản mới nhất (v${u.current || "1.5.10"}).\nNếu muốn kéo lại toàn bộ mã nguồn và cập nhật lại thư viện, bạn có thể bấm nút "⚡ Cập nhật lại từ GitHub".`);
  }
});
$("btn-force-update") && ($("btn-force-update").onclick = () => {
  if (confirm("Chạy cập nhật lại toàn bộ mã nguồn và thư viện từ nhánh main trên GitHub?")) {
    runSelfUpdate(true);
  }
});
$("btn-start-update") && ($("btn-start-update").onclick = () => runSelfUpdate(false));

// ===================== CÂY THƯ MỤC DỰ ÁN (PROJECT EXPLORER) =====================
let fsExpanded = new Set();
let fsShowHidden = false;
let currentPreviewPath = "";
let fsRootData = null;

function isExplorerTabActive() {
  const viewExp = $("view-explorer");
  return Boolean(viewExp && viewExp.style.display === "flex");
}

function syncExplorerWatchState() {
  const active = isExplorerTabActive() && !document.hidden;
  if (ws && ws.readyState === WebSocket.OPEN) {
    try {
      ws.send(JSON.stringify({ type: "fs_watch", active }));
    } catch (_) {}
  }
}

// Chuyển đổi tab giữa Danh sách Cộng sự và Cây thư mục dự án
function switchSidebarTab(tabName) {
  const isExplorer = tabName === "explorer";
  $("tab-btn-agents").classList.toggle("active", !isExplorer);
  $("tab-btn-explorer").classList.toggle("active", isExplorer);
  $("view-agents").style.display = isExplorer ? "none" : "flex";
  $("view-explorer").style.display = isExplorer ? "flex" : "none";

  syncExplorerWatchState();
  if (isExplorer) {
    refreshFsTree({ silent: Boolean(fsRootData) });
  }
}

$("tab-btn-agents").onclick = () => switchSidebarTab("agents");
$("tab-btn-explorer").onclick = () => switchSidebarTab("explorer");
$("btn-toggle-explorer").onclick = () => {
  const isExp = $("view-explorer").style.display === "flex";
  switchSidebarTab(isExp ? "agents" : "explorer");
};

// Biểu tượng tệp tin theo định dạng (chuẩn Antigravity IDE / VS Code)
function getFileBadge(ext) {
  ext = (ext || "").toLowerCase();
  if (ext === ".md") return `<span class="f-badge md">M↓</span>`;
  if (ext === ".html" || ext === ".htm") return `<span class="f-badge html">&lt;/&gt;</span>`;
  if (ext === ".py") return `<span class="f-badge py">Py</span>`;
  if (ext === ".xlsx" || ext === ".xls" || ext === ".csv") return `<span class="f-badge xls">田</span>`;
  if (ext === ".docx" || ext === ".doc") return `<span class="f-badge doc">W</span>`;
  if (ext === ".pdf") return `<span class="f-badge pdf">PDF</span>`;
  if (ext === ".dwg" || ext === ".dxf" || ext === ".rvt") return `<span class="f-badge cad">CAD</span>`;
  if (ext === ".zip" || ext === ".rar" || ext === ".7z" || ext === ".tar" || ext === ".gz") return `<span class="f-badge zip">ZIP</span>`;
  if (ext === ".bat" || ext === ".ps1" || ext === ".sh" || ext === ".vbs" || ext === ".cmd") return `<span class="f-badge sh">&gt;_</span>`;
  if (ext === ".json" || ext === ".yaml" || ext === ".yml" || ext === ".toml") return `<span class="f-badge json">{}</span>`;
  if ([".png", ".jpg", ".jpeg", ".ico", ".svg", ".webp"].includes(ext)) return kuroIcon("ic-image", "ic-xs", "ic-image");
  return kuroIcon("ic-file-text", "ic-xs", "ic-muted");
}

function formatBytes(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

// ==========================================
// WORKSPACE MANAGER (QUẢN LÝ THƯ MỤC DỰ ÁN)
// ==========================================
let currentWorkspace = { path: "", name: "" };
let currentWorkspaceRules = null;
let recentWorkspaces = [];

function updateWorkspaceRulesBadge(rules) {
  currentWorkspaceRules = rules || null;
  const pill = $("ws-rules-status-pill");
  const txt = $("ws-rules-status-text");
  if (!pill || !txt) return;
  if (!rules) {
    pill.className = "ws-rules-pill";
    txt.innerHTML = `${kuroIcon("ic-settings", "ic-xs")} <span>Quy tắc dự án</span>`;
    return;
  }
  const mode = rules.mode || "unset";
  if (mode === "rules") {
    pill.className = "ws-rules-pill ok";
    txt.innerHTML = `${kuroIcon("ic-check-circle", "ic-xs", "ic-green")} <span>Theo QUY_TAC_LAM_VIEC.md</span>`;
  } else if (mode === "none") {
    pill.className = "ws-rules-pill";
    txt.textContent = "Không áp dụng quy tắc mặc định";
  } else {
    pill.className = "ws-rules-pill warn";
    txt.innerHTML = `${kuroIcon("ic-alert-triangle", "ic-xs", "ic-amber")} <span>Chưa thiết lập quy tắc dự án</span>`;
  }
}

async function openWorkspaceRulesDialog(isNewProjectPrompt = false) {
  const dlg = $("workspace-rules-dialog");
  if (!dlg) return;
  try {
    const res = await fetch("/api/workspaces/rules");
    if (!res.ok) return;
    const data = await res.json();
    updateWorkspaceRulesBadge(data);

    if ($("wsr-ws-name")) $("wsr-ws-name").textContent = data.workspace_name || currentWorkspace.name || "Dự án";
    if ($("wsr-ws-path")) $("wsr-ws-path").textContent = data.workspace || currentWorkspace.path || "";

    const noteEl = $("wsr-prompt-note");
    if (noteEl) {
      if (isNewProjectPrompt || data.needs_prompt) {
        noteEl.textContent = "Dự án này chưa có quy tắc làm việc. Bạn có muốn áp dụng Kuro Standard (tạo 3 thư mục và tệp QUY_TAC_LAM_VIEC.md) cho thư mục này không?";
        noteEl.style.display = "block";
      } else if (data.has_rules) {
        noteEl.textContent = "Kuro làm việc theo tệp QUY_TAC_LAM_VIEC.md trong thư mục dự án. Sửa tệp (bên dưới hoặc mở trực tiếp) là đổi quy tắc.";
        noteEl.style.color = "var(--green)";
        noteEl.style.display = "block";
      } else {
        noteEl.style.display = "none";
      }
    }

    const customEl = $("wsr-custom-text");
    if (customEl) {
      customEl.value = data.content || "";
      customEl.dataset.template = data.template || "";
    }
    const detailsEl = $("wsr-custom-details");
    if (detailsEl) detailsEl.open = Boolean(data.has_rules);

    if ($("wsr-msg")) $("wsr-msg").textContent = "";
    const applyBtn = $("btn-wsr-apply");
    if (applyBtn) {
      applyBtn.textContent = data.has_rules
        ? "✓ Đã có QUY_TAC_LAM_VIEC.md (Đảm bảo đủ 3 thư mục)"
        : "✅ Áp dụng Kuro Standard";
    }
    if (!dlg.open) dlg.showModal();
  } catch (err) {
    console.error("Lỗi mở hộp thoại quy tắc dự án:", err);
  }
}

async function applyWorkspaceRulesChoice(mode, opts = {}) {
  const msgEl = $("wsr-msg");
  if (msgEl) msgEl.textContent = "Đang lưu...";
  try {
    const payload = { mode };
    if (opts.content !== undefined) payload.content = opts.content;
    const res = await fetch("/api/workspaces/rules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Không lưu được quy tắc");
    updateWorkspaceRulesBadge(data);
    await refreshFsTree({ silent: false });

    if (mode === "standard") {
      if ($("state") && !busy) {
        $("state").textContent = "Đã áp dụng Kuro Standard (3 thư mục & QUY_TAC_LAM_VIEC.md)";
        setTimeout(() => { if (!busy && $("state")) $("state").textContent = "Sẵn sàng"; }, 2800);
      }
      if ($("workspace-rules-dialog")?.open && !opts.keepOpen) $("workspace-rules-dialog").close();
    } else if (mode === "none") {
      if ($("workspace-rules-dialog")?.open && !opts.keepOpen) $("workspace-rules-dialog").close();
    } else if (msgEl) {
      msgEl.textContent = data.has_rules
        ? "Đã lưu QUY_TAC_LAM_VIEC.md vào gốc dự án."
        : "Đã bỏ QUY_TAC_LAM_VIEC.md, dự án làm việc bình thường.";
    }
  } catch (err) {
    if (msgEl) msgEl.textContent = "Lỗi: " + err.message;
  }
}

function handleWorkspaceRulesAfterSwitch(rules) {
  updateWorkspaceRulesBadge(rules);
  if (rules && rules.needs_prompt) {
    openWorkspaceRulesDialog(true);
  }
}

$("ws-rules-status-pill") && ($("ws-rules-status-pill").onclick = () => openWorkspaceRulesDialog(false));
$("btn-ws-rules-open") && ($("btn-ws-rules-open").onclick = () => openWorkspaceRulesDialog(false));
$("btn-wsr-close") && ($("btn-wsr-close").onclick = () => $("workspace-rules-dialog")?.close());
$("btn-wsr-apply") && ($("btn-wsr-apply").onclick = () => applyWorkspaceRulesChoice("standard"));
$("btn-wsr-decline") && ($("btn-wsr-decline").onclick = () => applyWorkspaceRulesChoice("none"));
$("btn-wsr-fill-template") && ($("btn-wsr-fill-template").onclick = () => {
  const ta = $("wsr-custom-text");
  if (ta && !ta.value.trim()) ta.value = ta.dataset.template || "";
  if (ta) ta.focus();
});
$("btn-wsr-save-custom") && ($("btn-wsr-save-custom").onclick = () => {
  const ta = $("wsr-custom-text");
  applyWorkspaceRulesChoice("keep", { content: ta ? ta.value : "", keepOpen: true });
});

async function loadWorkspaces() {
  try {
    const res = await fetch("/api/workspaces");
    if (!res.ok) return;
    const data = await res.json();
    currentWorkspace = {
      path: data.active,
      name: data.name
    };
    recentWorkspaces = data.recent || [];
    updateWorkspaceUI();
    if (data.rules) updateWorkspaceRulesBadge(data.rules);
  } catch (err) {
    console.error("Lỗi nạp workspace:", err);
  }
}

function updateWorkspaceUI() {
  const nameEl = $("ws-active-name");
  const pathEl = $("ws-active-path");
  const hdrNameEl = $("header-ws-name");
  if (nameEl) nameEl.textContent = currentWorkspace.name || "Dự án";
  if (pathEl) {
    pathEl.textContent = currentWorkspace.path || "...";
    pathEl.title = currentWorkspace.path || "";
  }
  if (hdrNameEl) hdrNameEl.textContent = currentWorkspace.name || "Dự án";
  renderRecentWorkspaces();
}

function renderRecentWorkspaces() {
  const listEl = $("ws-recent-list");
  const sidebarListEl = $("sidebar-recent-ws-list");
  const countEl = $("recent-ws-count");

  const recents = recentWorkspaces || [];
  if (countEl) countEl.textContent = recents.length;

  // 1. Render trong modal dialog
  if (listEl) {
    listEl.innerHTML = "";
    if (recents.length === 0) {
      listEl.innerHTML = `<div style="color:var(--muted); font-size:12px; padding:12px; text-align:center;">Chưa có lịch sử thư mục dự án nào.</div>`;
    } else {
      recents.forEach((ws) => {
        const isAct = currentWorkspace && currentWorkspace.path.toLowerCase() === ws.path.toLowerCase();
        const item = document.createElement("div");
        item.className = "ws-recent-item " + (isAct ? "active" : "");
        const timeText = ws.last_opened ? `<span style="color:var(--cyan-soft); font-size:10.5px; margin-left:6px;">(${formatWsTime(ws.last_opened)})</span>` : "";
        item.innerHTML = `
          <div class="ws-recent-left">
            <span style="display:inline-flex;align-items:center;">${isAct ? kuroIcon("ic-folder-open", "ic-md", "ic-accent") : kuroIcon("ic-folder", "ic-md", "ic-folder")}</span>
            <div class="ws-recent-meta">
              <div class="ws-recent-name">${DOMPurify.sanitize(ws.name || ws.path)} ${timeText}</div>
              <div class="ws-recent-path">${DOMPurify.sanitize(ws.path)}</div>
            </div>
          </div>
          <div class="ws-recent-actions">
            ${isAct ? '<span class="ws-active-badge">Đang mở</span>' : '<button class="btn-ws-switch" type="button">MỞ NGAY</button>'}
            <button class="btn-recent-del" type="button" title="Xóa khỏi danh sách gần đây">✕</button>
          </div>
        `;

        item.onclick = async (e) => {
          if (e.target.closest(".btn-recent-del")) {
            e.stopPropagation();
            await removeRecentWorkspace(ws.path);
            return;
          }
          await switchWorkspace(ws.path, ws.name);
        };
        listEl.appendChild(item);
      });
    }
  }

  // 2. Render nhanh trong Panel CÂY THƯ MỤC
  if (sidebarListEl) {
    sidebarListEl.innerHTML = "";
    if (recents.length === 0) {
      sidebarListEl.innerHTML = `<div style="color:var(--muted); font-size:10.5px; padding:6px; text-align:center;">Chưa có dự án cũ</div>`;
    } else {
      recents.slice(0, 10).forEach((ws) => {
        const isAct = currentWorkspace && currentWorkspace.path.toLowerCase() === ws.path.toLowerCase();
        const item = document.createElement("div");
        item.className = "recent-ws-item " + (isAct ? "active" : "");
        item.title = `${ws.path}\nBấm để chuyển sang dự án này`;
        const timeStr = ws.last_opened ? formatWsTime(ws.last_opened) : "";
        item.innerHTML = `
          <span style="display:inline-flex;align-items:center;flex:none;">${isAct ? kuroIcon("ic-folder-open", "ic-xs", "ic-accent") : kuroIcon("ic-folder", "ic-xs", "ic-folder")}</span>
          <div class="recent-ws-meta">
            <span class="recent-ws-name">${DOMPurify.sanitize(ws.name || ws.path)}</span>
            <span class="recent-ws-path">${DOMPurify.sanitize(ws.path)}</span>
          </div>
          <div class="recent-ws-actions">
            ${timeStr ? `<span class="recent-ws-time">${timeStr}</span>` : ""}
            <button class="recent-ws-del" type="button" title="Xóa khỏi danh sách">✕</button>
          </div>
        `;
        item.onclick = async (e) => {
          if (e.target.closest(".recent-ws-del")) {
            e.stopPropagation();
            await removeRecentWorkspace(ws.path);
            return;
          }
          await switchWorkspace(ws.path, ws.name);
        };
        sidebarListEl.appendChild(item);
      });
    }
  }
}

function formatWsTime(ts) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  const now = new Date();
  const diffSec = Math.floor((now - d) / 1000);
  if (diffSec < 60) return "Vừa mở";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} phút trước`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} giờ trước`;
  return `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
}

let currentBrowsePath = "";
let currentBrowseName = "";

async function loadSystemDrives() {
  const container = $("ws-drives-list");
  if (!container) return;
  try {
    const res = await fetch("/api/fs/drives");
    if (!res.ok) return;
    const data = await res.json();
    container.innerHTML = "";
    if (!data.drives || !data.drives.length) {
      container.innerHTML = `<span style="color:var(--muted); font-size:11.5px;">Không tìm thấy ổ đĩa.</span>`;
      return;
    }
    data.drives.forEach((d) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn-ws-drive";
      btn.innerHTML = `💾 <b>${d.letter}:\\</b>`;
      btn.title = d.name;
      btn.onclick = () => browseDirectory(d.path, d.name);
      container.appendChild(btn);
    });
  } catch (e) {
    console.error("Lỗi nạp danh sách ổ đĩa:", e);
  }
}

async function browseDirectory(path, name) {
  if (!path) return;
  currentBrowsePath = path;
  currentBrowseName = name || path;
  const pathLabel = $("ws-current-browse-path");
  const upBtn = $("btn-ws-browse-up");
  const grid = $("ws-dirs-grid");
  const pickBtn = $("btn-ws-pick-current");
  const hint = $("ws-browse-hint");

  if (pathLabel) pathLabel.textContent = path;
  if (grid) grid.innerHTML = `<div style="grid-column:1/-1; color:var(--muted); font-size:11.5px; padding:8px;">Đang tải thư mục...</div>`;

  try {
    const res = await fetch(`/api/fs/directories?path=${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error("Không thể đọc thư mục này");
    const data = await res.json();

    if (upBtn) {
      if (data.parent) {
        upBtn.style.display = "inline-block";
        upBtn.onclick = () => browseDirectory(data.parent);
      } else {
        upBtn.style.display = "none";
      }
    }

    if (pickBtn) {
      pickBtn.style.display = "inline-block";
      pickBtn.textContent = `✓ CHỌN "${data.name}" LÀM WORKSPACE`;
      pickBtn.onclick = () => switchWorkspace(currentBrowsePath, data.name);
    }

    if (hint) {
      hint.textContent = `Thư mục đang chọn: ${path}`;
    }

    if ($("ws-input-path")) $("ws-input-path").value = path;

    if (!grid) return;
    grid.innerHTML = "";
    if (!data.directories || !data.directories.length) {
      grid.innerHTML = `<div style="grid-column:1/-1; color:var(--muted); font-size:11.5px; padding:12px; text-align:center;">Thư mục này không có thư mục con. Bấm nút chọn bên dưới để sử dụng thư mục này.</div>`;
      return;
    }

    data.directories.forEach((dir) => {
      const card = document.createElement("div");
      card.className = "ws-dir-card";
      card.title = dir.path;
      card.innerHTML = `<span>📁</span> <span style="overflow:hidden; text-overflow:ellipsis;">${DOMPurify.sanitize(dir.name)}</span>`;
      card.onclick = () => browseDirectory(dir.path, dir.name);
      grid.appendChild(card);
    });
  } catch (err) {
    if (grid) grid.innerHTML = `<div style="grid-column:1/-1; color:var(--hazard-hi); font-size:11.5px; padding:8px;">${DOMPurify.sanitize(err.message)}</div>`;
  }
}

async function browseNativeWorkspace(triggerBtn = null) {
  // 1. Ưu tiên cao nhất: Nếu đang chạy trên ứng dụng Desktop Windows (Native App qua pywebview)
  if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.choose_folder === "function") {
    const origTriggerHtml = triggerBtn ? triggerBtn.innerHTML : "";
    const statusEl = $("state");
    if (triggerBtn) triggerBtn.innerHTML = "⏳";
    if (statusEl) statusEl.textContent = "Đang chọn thư mục...";
    try {
      const chosen = await window.pywebview.api.choose_folder(currentWorkspace.path || "");
      if (chosen) {
        await switchWorkspace(chosen);
        if (statusEl) statusEl.textContent = `Đã chọn: ${currentWorkspace.name}`;
        setTimeout(() => { if (!busy && statusEl) statusEl.textContent = "Sẵn sàng"; }, 3000);
        try { $("workspace-dialog").close(); } catch (e) {}
      } else {
        if (statusEl) statusEl.textContent = "Đã hủy chọn thư mục";
        setTimeout(() => { if (!busy && statusEl) statusEl.textContent = "Sẵn sàng"; }, 2000);
      }
      return;
    } catch (err) {
      console.warn("[DesktopApp] Lỗi chọn thư mục native:", err);
    } finally {
      if (triggerBtn) triggerBtn.innerHTML = origTriggerHtml;
    }
  }

  // 2. Nếu đang chạy trên điện thoại: mở ngay bộ duyệt trực quan
  const isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
  if (isMobile) {
    openWorkspaceDialog();
    return;
  }

  const btnNative = $("btn-ws-browse-native");
  const origNativeHtml = btnNative ? btnNative.innerHTML : "";
  const origTriggerHtml = triggerBtn ? triggerBtn.innerHTML : "";
  const statusEl = $("state");
  const origStatus = "Sẵn sàng";

  if (triggerBtn) {
    triggerBtn.innerHTML = `⏳`;
    triggerBtn.disabled = true;
  }
  if (btnNative) {
    btnNative.innerHTML = `<span>⏳</span> <span>ĐANG MỞ HỘP THOẠI WINDOWS...</span>`;
    btnNative.disabled = true;
  }
  if (statusEl) statusEl.textContent = "Đang mở hộp thoại Windows...";

  // Tạo AbortController để tự động hủy sau 15 giây nếu Windows không phản hồi
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const res = await fetch("/api/workspaces/browse-native", {
      method: "POST",
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    const data = await res.json();
    if (data.ok && data.path) {
      currentWorkspace = {
        path: data.path,
        name: data.name
      };
      recentWorkspaces = data.recent || [];
      updateWorkspaceUI();
      fsExpanded.clear();
      await refreshFsTree();
      await loadSessions(selectedAgent);
      if (statusEl) statusEl.textContent = `Đã chọn: ${data.name}`;
      setTimeout(() => { if (!busy && statusEl) statusEl.textContent = "Sẵn sàng"; }, 3000);
      try { $("workspace-dialog").close(); } catch (e) {}
      if (data.rules) handleWorkspaceRulesAfterSwitch(data.rules);
    } else if (data.cancelled) {
      if (statusEl) statusEl.textContent = "Đã hủy chọn thư mục";
      setTimeout(() => { if (!busy && statusEl) statusEl.textContent = origStatus; }, 2000);
    } else {
      // Nếu server không mở được cửa sổ Windows, mở ngay dialog duyệt ổ đĩa trực quan
      openWorkspaceDialog();
      if (statusEl) statusEl.textContent = "Duyệt ổ đĩa trực quan";
      setTimeout(() => { if (!busy && statusEl) statusEl.textContent = origStatus; }, 2000);
    }
  } catch (e) {
    clearTimeout(timeoutId);
    console.warn("Native picker timeout hoặc lỗi kết nối, chuyển sang bộ duyệt trực quan:", e);
    openWorkspaceDialog();
    if (statusEl) statusEl.textContent = "Duyệt ổ đĩa trực quan";
    setTimeout(() => { if (!busy && statusEl) statusEl.textContent = origStatus; }, 2000);
  } finally {
    if (triggerBtn) {
      triggerBtn.innerHTML = origTriggerHtml;
      triggerBtn.disabled = false;
    }
    if (btnNative) {
      btnNative.innerHTML = origNativeHtml;
      btnNative.disabled = false;
    }
  }
}

function openWorkspaceDialog() {
  const errEl = $("ws-open-error");
  if (errEl) errEl.style.display = "none";
  $("ws-input-path").value = currentWorkspace.path || "";
  renderRecentWorkspaces();
  loadSystemDrives();
  if (currentWorkspace.path) {
    browseDirectory(currentWorkspace.path, currentWorkspace.name);
  }
  $("workspace-dialog").showModal();
}

async function switchWorkspace(path, name) {
  if (!path) return;
  const statusEl = $("state");
  if (statusEl) statusEl.textContent = "Đang chuyển thư mục...";
  try {
    const res = await fetch("/api/workspaces/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path, name: name, create: true })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Không thể mở thư mục này");
    }

    currentWorkspace = {
      path: data.active,
      name: data.name
    };
    recentWorkspaces = data.recent || [];
    updateWorkspaceUI();
    renderRecentWorkspaces();

    // 1. Làm mới cây thư mục tệp tin của dự án mới
    fsExpanded.clear();
    await refreshFsTree();

    // 2. Chuyển đổi và cô lập lịch sử hội thoại của Agent theo dự án mới
    await loadSessions(selectedAgent);

    if (statusEl) statusEl.textContent = `Thư mục: ${data.name}`;
    setTimeout(() => { if (!busy && statusEl) statusEl.textContent = "Sẵn sàng"; }, 2500);

    try {
      const dlg = $("workspace-dialog");
      if (dlg && dlg.open) dlg.close();
    } catch (e) {}

    // 3. Kiểm tra quy tắc làm việc của dự án vừa mở: có rồi thì dùng luôn, chưa có thì đề xuất Kuro Standard
    if (data.rules) {
      handleWorkspaceRulesAfterSwitch(data.rules);
    }
  } catch (err) {
    console.error("Lỗi chuyển workspace:", err);
    if (statusEl) statusEl.textContent = "Lỗi đổi thư mục";
    setTimeout(() => { if (!busy && statusEl) statusEl.textContent = "Sẵn sàng"; }, 2500);
    const errEl = $("ws-open-error");
    if (errEl) {
      errEl.textContent = err.message;
      errEl.style.display = "block";
    }
  }
}

async function removeRecentWorkspace(path) {
  try {
    const res = await fetch(`/api/workspaces/recent?path=${encodeURIComponent(path)}`, {
      method: "DELETE"
    });
    const data = await res.json();
    if (data.ok) {
      recentWorkspaces = data.recent || [];
      renderRecentWorkspaces();
    }
  } catch (e) {
    console.error("Lỗi xóa recent workspace:", e);
  }
}

let fsDirty = false;
let fsAutoRefreshTimer = null;
let fsRefreshing = false;

// Tự động làm mới cây thư mục (chỉ chạy khi tab Thư mục đang bật và cửa sổ đang hiển thị)
function scheduleFsAutoRefresh(delayMs = 350) {
  if (!isExplorerTabActive() || document.hidden) {
    fsDirty = true;
    return;
  }
  const searchInput = $("fs-search");
  if (searchInput && searchInput.value.trim()) {
    // Không xóa kết quả người dùng đang tìm kiếm
    fsDirty = true;
    return;
  }
  if (fsAutoRefreshTimer) clearTimeout(fsAutoRefreshTimer);
  fsAutoRefreshTimer = setTimeout(() => {
    fsAutoRefreshTimer = null;
    if (isExplorerTabActive() && !document.hidden) {
      refreshFsTree({ silent: true });
    }
  }, delayMs);
}

document.addEventListener("visibilitychange", () => {
  syncExplorerWatchState();
  if (!document.hidden && isExplorerTabActive()) {
    scheduleFsAutoRefresh(200);
  }
});

window.addEventListener("focus", () => {
  syncExplorerWatchState();
  if (isExplorerTabActive()) {
    scheduleFsAutoRefresh(200);
  }
});

// Tải và hiển thị cây thư mục
async function refreshFsTree(opts = {}) {
  const silent = Boolean(opts && opts.silent);
  if (fsRefreshing) {
    fsDirty = true;
    return;
  }
  fsRefreshing = true;
  fsDirty = false;
  if (!silent && $("fs-status")) $("fs-status").textContent = "Đang tải...";
  const treeEl = $("fs-tree");
  const prevScrollTop = treeEl ? treeEl.scrollTop : 0;
  try {
    const res = await fetch(`/api/fs/tree?sub=&show_hidden=${fsShowHidden}`);
    const nextData = await res.json();
    fsRootData = nextData;
    if (fsRootData.workspace_name) {
      currentWorkspace.name = fsRootData.workspace_name;
      currentWorkspace.path = fsRootData.workspace_path;
      updateWorkspaceUI();
    }
    renderFsRoot();
    if (treeEl) treeEl.scrollTop = prevScrollTop;
    if ($("fs-status")) $("fs-status").textContent = "Đã đồng bộ";
  } catch (err) {
    if (!silent && $("fs-status")) $("fs-status").textContent = "Lỗi đọc thư mục";
    console.error("Lỗi fs tree:", err);
  } finally {
    fsRefreshing = false;
  }
}

let selectedFsItem = null;
let fsClipboard = null; // { action: "copy", path: string, is_dir: boolean, name: string }
let fsSearchTimer = null;

function getParentPath(p) {
  if (!p) return "";
  const parts = p.replace(/\\/g, "/").split("/").filter(Boolean);
  parts.pop();
  return parts.join("/");
}

function getTargetParent(item) {
  if (!item || !item.path) return "";
  if (item.is_dir) return item.path;
  return getParentPath(item.path);
}

function renderFsRoot() {
  const container = $("fs-tree");
  container.innerHTML = "";
  if (!fsRootData || !fsRootData.items) return;

  const wsName = fsRootData.workspace_name || currentWorkspace.name || "Dự án";
  const wsPath = fsRootData.workspace_path || currentWorkspace.path || "";

  // Root node: THƯ MỤC DỰ ÁN LÀM VIỆC
  const rootNode = document.createElement("div");
  rootNode.className = "tree-node";

  const rootItem = document.createElement("div");
  rootItem.className = "tree-item";
  rootItem.title = `Thư mục làm việc: ${wsPath}\nBấm chuột phải để thao tác tệp/thư mục`;
  rootItem.innerHTML = `
    <span class="tree-caret open">${kuroIcon("ic-chevron-right", "ic-xs")}</span>
    <span class="tree-icon">${kuroIcon("ic-folder-open", "ic-xs", "ic-accent")}</span>
    <strong class="tree-name" style="color:var(--amber); text-transform:uppercase;">${DOMPurify.sanitize(wsName)} (DỰ ÁN)</strong>
  `;

  const rootChildren = document.createElement("div");
  rootChildren.className = "tree-children";

  renderFsItems(fsRootData.items, rootChildren);

  rootItem.onclick = () => {
    document.querySelectorAll(".tree-item.active").forEach((el) => el.classList.remove("active"));
    rootItem.classList.add("active");
    selectedFsItem = { path: "", is_dir: true, name: wsName };
    const isOpen = rootChildren.style.display !== "none";
    rootChildren.style.display = isOpen ? "none" : "flex";
    rootItem.querySelector(".tree-caret").className = "tree-caret " + (isOpen ? "" : "open");
  };

  rootItem.oncontextmenu = (e) => {
    e.preventDefault();
    e.stopPropagation();
    document.querySelectorAll(".tree-item.active").forEach((el) => el.classList.remove("active"));
    rootItem.classList.add("active");
    selectedFsItem = { path: "", is_dir: true, name: wsName };
    showFsContextMenu(e.clientX, e.clientY);
  };

  rootNode.appendChild(rootItem);
  rootNode.appendChild(rootChildren);
  container.appendChild(rootNode);

  container.oncontextmenu = (e) => {
    if (e.target === container) {
      e.preventDefault();
      selectedFsItem = { path: "", is_dir: true, name: wsName };
      showFsContextMenu(e.clientX, e.clientY);
    }
  };
}

function renderFsItems(items, containerEl) {
  containerEl.innerHTML = "";
  items.forEach((it) => {
    const node = document.createElement("div");
    node.className = "tree-node";

    const itemEl = document.createElement("div");
    itemEl.className = "tree-item";
    itemEl.dataset.path = it.path;

    if (it.is_dir) {
      const isExpanded = fsExpanded.has(it.path);
      itemEl.innerHTML = `
        <span class="tree-caret ${isExpanded ? 'open' : ''}">${kuroIcon("ic-chevron-right", "ic-xs")}</span>
        <span class="tree-icon">${isExpanded ? kuroIcon("ic-folder-open", "ic-xs", "ic-folder") : kuroIcon("ic-folder", "ic-xs", "ic-folder")}</span>
        <span class="tree-name">${DOMPurify.sanitize(it.name)}</span>
      `;

      const childrenEl = document.createElement("div");
      childrenEl.className = "tree-children";
      childrenEl.style.display = isExpanded ? "flex" : "none";

      itemEl.onclick = async () => {
        document.querySelectorAll(".tree-item.active").forEach((el) => el.classList.remove("active"));
        itemEl.classList.add("active");
        selectedFsItem = it;

        const currentlyExpanded = fsExpanded.has(it.path);
        if (currentlyExpanded) {
          fsExpanded.delete(it.path);
          childrenEl.style.display = "none";
          itemEl.querySelector(".tree-caret").className = "tree-caret";
          itemEl.querySelector(".tree-icon").innerHTML = kuroIcon("ic-folder", "ic-xs", "ic-folder");
        } else {
          fsExpanded.add(it.path);
          childrenEl.style.display = "flex";
          itemEl.querySelector(".tree-caret").className = "tree-caret open";
          itemEl.querySelector(".tree-icon").innerHTML = kuroIcon("ic-folder-open", "ic-xs", "ic-folder");

          if (!childrenEl.hasChildNodes()) {
            childrenEl.innerHTML = `<span style="padding:4px 8px; font-size:11px; color:var(--muted);">Đang mở...</span>`;
            try {
              const res = await fetch(`/api/fs/tree?sub=${encodeURIComponent(it.path)}&show_hidden=${fsShowHidden}`);
              const subData = await res.json();
              renderFsItems(subData.items, childrenEl);
            } catch (e) {
              childrenEl.innerHTML = `<span style="padding:4px 8px; font-size:11px; color:var(--amber);">Lỗi mở thư mục</span>`;
            }
          }
        }
      };

      itemEl.ondblclick = (e) => {
        e.stopPropagation();
        revealFileNative(it.path);
      };

      itemEl.oncontextmenu = (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.querySelectorAll(".tree-item.active").forEach((el) => el.classList.remove("active"));
        itemEl.classList.add("active");
        selectedFsItem = it;
        showFsContextMenu(e.clientX, e.clientY);
      };

      node.appendChild(itemEl);
      node.appendChild(childrenEl);

      // Nếu đã expand từ trước
      if (isExpanded) {
        fetch(`/api/fs/tree?sub=${encodeURIComponent(it.path)}&show_hidden=${fsShowHidden}`)
          .then((r) => r.json())
          .then((subData) => renderFsItems(subData.items, childrenEl))
          .catch(() => {});
      }
    } else {
      // File item
      itemEl.innerHTML = `
        <span class="tree-caret empty"></span>
        <span class="tree-icon">${getFileBadge(it.ext)}</span>
        <span class="tree-name">${DOMPurify.sanitize(it.name)}</span>
        <span class="tree-size">${formatBytes(it.size)}</span>
      `;

      itemEl.onclick = () => {
        document.querySelectorAll(".tree-item.active").forEach((el) => el.classList.remove("active"));
        itemEl.classList.add("active");
        selectedFsItem = it;
        openFilePreview(it.path, it.name, it.ext);
      };

      itemEl.ondblclick = (e) => {
        e.stopPropagation();
        openFileNative(it.path);
      };

      itemEl.oncontextmenu = (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.querySelectorAll(".tree-item.active").forEach((el) => el.classList.remove("active"));
        itemEl.classList.add("active");
        selectedFsItem = it;
        showFsContextMenu(e.clientX, e.clientY);
      };

      node.appendChild(itemEl);
    }

    containerEl.appendChild(node);
  });
}

// Tìm kiếm tệp trong toàn bộ thư mục dự án (Recursive Search)
$("fs-search").oninput = (e) => {
  clearTimeout(fsSearchTimer);
  const q = e.target.value.trim();
  if (!q) {
    if (fsRootData) renderFsRoot();
    $("fs-status").textContent = "Sẵn sàng";
    return;
  }
  fsSearchTimer = setTimeout(async () => {
    $("fs-status").textContent = "Đang tìm kiếm...";
    try {
      const res = await fetch(`/api/fs/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      renderFsSearchResults(q, data.items || []);
      $("fs-status").textContent = `Tìm thấy ${(data.items || []).length} kết quả`;
    } catch (err) {
      $("fs-status").textContent = "Lỗi tìm kiếm";
    }
  }, 220);
};

function renderFsSearchResults(query, items) {
  const container = $("fs-tree");
  container.innerHTML = "";

  const header = document.createElement("div");
  header.className = "fs-search-header";
  header.innerHTML = `
    <span>KẾT QUẢ TÌM KIẾM (${items.length})</span>
    <button type="button" class="btn-link" id="btn-close-fs-search" style="font-size:11px; color:var(--cyan-soft);">✕ Đóng</button>
  `;
  container.appendChild(header);

  const btnClose = header.querySelector("#btn-close-fs-search");
  if (btnClose) {
    btnClose.onclick = () => {
      $("fs-search").value = "";
      renderFsRoot();
      $("fs-status").textContent = "Sẵn sàng";
    };
  }

  if (!items.length) {
    const empty = document.createElement("div");
    empty.style.padding = "24px 16px";
    empty.style.textAlign = "center";
    empty.style.color = "var(--muted)";
    empty.style.fontSize = "12px";
    empty.innerHTML = `Không tìm thấy tệp hoặc thư mục nào khớp với <b>"${escapeHtml(query)}"</b>`;
    container.appendChild(empty);
    return;
  }

  const list = document.createElement("div");
  list.className = "fs-search-list";

  items.forEach(it => {
    const itemEl = document.createElement("div");
    itemEl.className = "fs-search-item";
    itemEl.title = `${it.path}\nDouble-click để mở bằng Windows`;
    
    const icon = it.is_dir ? "📁" : getFileBadge(it.ext);
    itemEl.innerHTML = `
      <span class="tree-icon" style="flex:none;">${icon}</span>
      <div class="fs-search-main">
        <div class="fs-search-name">${highlightMatch(it.name, query)}</div>
        <div class="fs-search-path">${escapeHtml(it.path)}</div>
      </div>
      <div class="fs-search-size">${it.size ? formatBytes(it.size) : ''}</div>
    `;

    itemEl.onclick = () => {
      document.querySelectorAll(".fs-search-item.active").forEach(el => el.classList.remove("active"));
      itemEl.classList.add("active");
      selectedFsItem = it;
      if (!it.is_dir) {
        openFilePreview(it.path, it.name, it.ext);
      }
    };

    itemEl.ondblclick = () => {
      if (it.is_dir) {
        revealFileNative(it.path);
      } else {
        openFileNative(it.path);
      }
    };

    itemEl.oncontextmenu = (e) => {
      e.preventDefault();
      e.stopPropagation();
      document.querySelectorAll(".fs-search-item.active").forEach(el => el.classList.remove("active"));
      itemEl.classList.add("active");
      selectedFsItem = it;
      showFsContextMenu(e.clientX, e.clientY);
    };

    list.appendChild(itemEl);
  });

  container.appendChild(list);
}

function highlightMatch(text, query) {
  if (!query) return escapeHtml(text);
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, "gi");
  return escapeHtml(text).replace(regex, '<span style="color:var(--amber); font-weight:bold;">$1</span>');
}

// Context Menu Chuột phải trên cây thư mục
function showFsContextMenu(x, y) {
  const menu = $("fs-context-menu");
  if (!menu) return;

  const isDir = selectedFsItem && selectedFsItem.is_dir;
  const pasteBtn = $("ctx-fs-paste");
  if (pasteBtn) {
    pasteBtn.style.display = fsClipboard ? "flex" : "none";
  }

  menu.style.display = "block";
  const w = menu.offsetWidth || 210;
  const h = menu.offsetHeight || 260;
  const left = Math.min(x, window.innerWidth - w - 10);
  const top = Math.min(y, window.innerHeight - h - 10);
  menu.style.left = `${Math.max(10, left)}px`;
  menu.style.top = `${Math.max(10, top)}px`;
}

function hideFsContextMenu() {
  const menu = $("fs-context-menu");
  if (menu) menu.style.display = "none";
}

document.addEventListener("click", (e) => {
  const menu = $("fs-context-menu");
  if (menu && menu.style.display !== "none" && !menu.contains(e.target)) {
    hideFsContextMenu();
  }
});

// Thao tác tệp / thư mục (File Operations)
async function promptNewFile(item) {
  const parent = getTargetParent(item);
  const name = prompt(parent ? `Tạo tệp tin mới trong thư mục "${parent}":` : "Tạo tệp tin mới tại thư mục gốc:", "tai_lieu.txt");
  if (!name || !name.trim()) return;
  try {
    const res = await fetch("/api/fs/new-file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parent, name: name.trim() })
    });
    const data = await res.json();
    if (res.ok) {
      $("fs-status").textContent = `Đã tạo tệp: ${data.name}`;
      if (parent) fsExpanded.add(parent);
      await refreshFsTree();
    } else {
      alert("Lỗi: " + (data.detail || "Không thể tạo tệp"));
    }
  } catch (err) {
    alert("Lỗi tạo tệp: " + err.message);
  }
}

async function promptNewFolder(item) {
  const parent = getTargetParent(item);
  const name = prompt(parent ? `Tạo thư mục mới trong "${parent}":` : "Tạo thư mục mới tại thư mục gốc:", "Thu_muc_moi");
  if (!name || !name.trim()) return;
  try {
    const res = await fetch("/api/fs/new-folder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parent, name: name.trim() })
    });
    const data = await res.json();
    if (res.ok) {
      $("fs-status").textContent = `Đã tạo thư mục: ${data.name}`;
      if (parent) fsExpanded.add(parent);
      await refreshFsTree();
    } else {
      alert("Lỗi: " + (data.detail || "Không thể tạo thư mục"));
    }
  } catch (err) {
    alert("Lỗi tạo thư mục: " + err.message);
  }
}

async function promptRename(item) {
  if (!item || !item.path) return;
  const newName = prompt(`Đổi tên "${item.name}" thành:`, item.name);
  if (!newName || !newName.trim() || newName.trim() === item.name) return;
  try {
    const res = await fetch("/api/fs/rename", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: item.path, new_name: newName.trim() })
    });
    const data = await res.json();
    if (res.ok) {
      $("fs-status").textContent = `Đã đổi tên thành: ${data.new_name}`;
      await refreshFsTree();
    } else {
      alert("Lỗi: " + (data.detail || "Không thể đổi tên"));
    }
  } catch (err) {
    alert("Lỗi đổi tên: " + err.message);
  }
}

async function confirmDelete(item) {
  if (!item || !item.path) return;
  const isDir = item.is_dir;
  const msg = isDir 
    ? `Bạn có chắc chắn muốn xóa thư mục "${item.name}" và toàn bộ tệp bên trong không?`
    : `Bạn có chắc chắn muốn xóa tệp tin "${item.name}" không?`;
  if (!confirm(msg)) return;
  try {
    const res = await fetch("/api/fs/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: item.path })
    });
    const data = await res.json();
    if (res.ok) {
      $("fs-status").textContent = `Đã xóa: ${item.name}`;
      await refreshFsTree();
    } else {
      alert("Lỗi: " + (data.detail || "Không thể xóa"));
    }
  } catch (err) {
    alert("Lỗi xóa: " + err.message);
  }
}

function copyFsItem(item) {
  if (!item || !item.path) return;
  fsClipboard = { action: "copy", path: item.path, is_dir: item.is_dir, name: item.name };
  if ($("btn-fs-paste")) $("btn-fs-paste").style.display = "inline-block";
  $("fs-status").textContent = `Đã sao chép: ${item.name}`;
}

async function pasteFsItem(item) {
  if (!fsClipboard || !fsClipboard.path) return;
  const targetDir = item && item.is_dir ? item.path : getTargetParent(item);
  try {
    const res = await fetch("/api/fs/copy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ src: fsClipboard.path, dest: targetDir })
    });
    const data = await res.json();
    if (res.ok) {
      $("fs-status").textContent = `Đã dán: ${data.new_name}`;
      if (targetDir) fsExpanded.add(targetDir);
      await refreshFsTree();
    } else {
      alert("Lỗi dán: " + (data.detail || "Không thể sao chép tệp"));
    }
  } catch (err) {
    alert("Lỗi sao chép: " + err.message);
  }
}

async function openFileNative(path, openWith = false) {
  try {
    const res = await fetch("/api/fs/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path || "", open_with: Boolean(openWith) })
    });
    if (res.ok) {
      const msg = openWith ? "Đã mở hộp thoại chọn phần mềm Windows" : "Đã mở tệp bằng phần mềm Windows";
      if ($("fs-status")) {
        $("fs-status").textContent = msg;
        setTimeout(() => { if ($("fs-status")) $("fs-status").textContent = "Sẵn sàng"; }, 2200);
      }
      if ($("state") && !busy) {
        $("state").textContent = msg;
        setTimeout(() => { if (!busy && $("state")) $("state").textContent = "Sẵn sàng"; }, 2200);
      }
    } else {
      const err = await res.json().catch(() => ({}));
      alert("Không thể mở: " + (err.detail || "Lỗi máy chủ"));
    }
  } catch (e) {
    alert("Lỗi mở bằng Windows: " + e.message);
  }
}

async function revealFileNative(path) {
  try {
    const res = await fetch("/api/fs/reveal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path || "" })
    });
    if (res.ok) {
      const msg = "Đã mở thư mục trong Windows Explorer";
      if ($("fs-status")) {
        $("fs-status").textContent = msg;
        setTimeout(() => { if ($("fs-status")) $("fs-status").textContent = "Sẵn sàng"; }, 2200);
      }
      if ($("state") && !busy) {
        $("state").textContent = msg;
        setTimeout(() => { if (!busy && $("state")) $("state").textContent = "Sẵn sàng"; }, 2200);
      }
    } else {
      const err = await res.json().catch(() => ({}));
      alert("Không thể mở Explorer: " + (err.detail || "Lỗi máy chủ"));
    }
  } catch (e) {
    alert("Lỗi mở Explorer: " + e.message);
  }
}

// ========================================================
// MENU TÙY CHỌN MỞ FILE KHI CLICK VÀO ĐƯỜNG DẪN TRONG CÂU TRẢ LỜI KURO
// ========================================================
function hideFileActionPopover() {
  const pop = $("file-action-popover");
  if (pop) pop.style.display = "none";
}

function showFileActionPopover(filePath, anchorEl) {
  const pop = $("file-action-popover");
  if (!pop || !filePath) return;

  const meta = getFileMeta(filePath);
  const name = getFileBaseName(filePath);
  const ext = getFileExt(filePath);

  pop.innerHTML = "";

  const hdr = document.createElement("div");
  hdr.className = "fap-header";
  const nameEl = document.createElement("div");
  nameEl.className = "fap-name";
  nameEl.innerHTML = `${kuroIcon(meta.iconId || "ic-file-text", "ic-sm", meta.colorCls || "")}<span>${escapeHtml(name)}</span>`;
  const pathEl = document.createElement("div");
  pathEl.className = "fap-path";
  pathEl.textContent = filePath;
  pathEl.title = filePath;
  hdr.append(nameEl, pathEl);
  pop.appendChild(hdr);

  const addItem = (iconHtml, label, onClick, isPrimary = false) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "fap-item" + (isPrimary ? " primary" : "");
    btn.innerHTML = `${iconHtml}<span>${escapeHtml(label)}</span>`;
    btn.onclick = async (ev) => {
      ev.stopPropagation();
      hideFileActionPopover();
      await onClick();
    };
    pop.appendChild(btn);
  };

  addItem(kuroIcon("ic-external-link", "ic-xs"), `Mở bằng ${meta.app}`, () => openFileNative(filePath, false), true);
  addItem(kuroIcon("ic-wrench", "ic-xs"), "Chọn phần mềm mở khác (Open With...)", () => openFileNative(filePath, true));
  addItem(kuroIcon("ic-folder-open", "ic-xs", "ic-folder"), "Mở thư mục chứa tệp (Explorer)", () => revealFileNative(filePath));

  if (meta.text && typeof openFilePreview === "function") {
    const sep1 = document.createElement("div");
    sep1.className = "fap-sep";
    pop.appendChild(sep1);
    addItem(kuroIcon("ic-eye", "ic-xs"), "Xem nhanh nội dung trong Kuro", () => openFilePreview(filePath, name));
  }

  const sep2 = document.createElement("div");
  sep2.className = "fap-sep";
  pop.appendChild(sep2);
  addItem(kuroIcon("ic-copy", "ic-xs"), "Sao chép đường dẫn", async () => {
    try {
      await navigator.clipboard.writeText(filePath);
      if ($("state") && !busy) {
        $("state").textContent = "Đã sao chép đường dẫn tệp";
        setTimeout(() => { if (!busy && $("state")) $("state").textContent = "Sẵn sàng"; }, 1800);
      }
    } catch (_) {}
  });

  // Hiển thị tạm để đo kích thước và căn chỉnh gọn trong khung cửa sổ
  pop.style.display = "block";
  pop.style.left = "0px";
  pop.style.top = "0px";
  const rect = anchorEl.getBoundingClientRect();
  const popRect = pop.getBoundingClientRect();
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  let left = rect.left;
  if (left + popRect.width > vw - 12) {
    left = Math.max(12, vw - popRect.width - 12);
  }
  let top = rect.bottom + 6;
  if (top + popRect.height > vh - 12) {
    top = Math.max(12, rect.top - popRect.height - 6);
  }
  pop.style.left = `${Math.round(left)}px`;
  pop.style.top = `${Math.round(top)}px`;
}

// Event delegation trên khung chat #log: click vào bất kỳ đường dẫn file nào đều hiện menu mở bằng Windows
if ($("log")) {
  $("log").addEventListener("click", (e) => {
    const btn = e.target.closest(".kuro-file-link");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    const fp = btn.getAttribute("data-file-path");
    if (fp) showFileActionPopover(fp, btn);
  });
}

document.addEventListener("click", (e) => {
  if (!e.target.closest("#file-action-popover") && !e.target.closest(".kuro-file-link")) {
    hideFileActionPopover();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") hideFileActionPopover();
});

// Bắt sự kiện Toolbar Explorer & Workspace Manager
$("btn-fs-new-file") && ($("btn-fs-new-file").onclick = () => promptNewFile(selectedFsItem || { path: "", is_dir: true }));
$("btn-fs-new-folder") && ($("btn-fs-new-folder").onclick = () => promptNewFolder(selectedFsItem || { path: "", is_dir: true }));
$("btn-fs-paste") && ($("btn-fs-paste").onclick = () => pasteFsItem(selectedFsItem || { path: "", is_dir: true }));
$("btn-fs-refresh").onclick = refreshFsTree;
$("btn-fs-collapse").onclick = () => {
  fsExpanded.clear();
  renderFsRoot();
};
$("btn-fs-hidden").onclick = () => {
  fsShowHidden = !fsShowHidden;
  $("btn-fs-hidden").style.color = fsShowHidden ? "var(--cyan)" : "var(--muted)";
  refreshFsTree();
};

// Bắt sự kiện Context Menu items
$("ctx-fs-open") && ($("ctx-fs-open").onclick = () => { if (selectedFsItem) openFileNative(selectedFsItem.path); hideFsContextMenu(); });
$("ctx-fs-reveal") && ($("ctx-fs-reveal").onclick = () => { if (selectedFsItem) revealFileNative(selectedFsItem.path); hideFsContextMenu(); });
$("ctx-fs-new-file") && ($("ctx-fs-new-file").onclick = () => { promptNewFile(selectedFsItem); hideFsContextMenu(); });
$("ctx-fs-new-folder") && ($("ctx-fs-new-folder").onclick = () => { promptNewFolder(selectedFsItem); hideFsContextMenu(); });
$("ctx-fs-copy") && ($("ctx-fs-copy").onclick = () => { copyFsItem(selectedFsItem); hideFsContextMenu(); });
$("ctx-fs-paste") && ($("ctx-fs-paste").onclick = () => { pasteFsItem(selectedFsItem); hideFsContextMenu(); });
$("ctx-fs-rename") && ($("ctx-fs-rename").onclick = () => { promptRename(selectedFsItem); hideFsContextMenu(); });
$("ctx-fs-delete") && ($("ctx-fs-delete").onclick = () => { confirmDelete(selectedFsItem); hideFsContextMenu(); });

// Phím tắt bàn phím khi chọn tệp trong cây thư mục
document.addEventListener("keydown", (e) => {
  // Chỉ nhận phím tắt file manager nếu không gõ trong ô input/textarea
  const active = document.activeElement;
  if (active && (active.tagName === "INPUT" || active.tagName === "TEXTAREA")) return;
  if (!selectedFsItem) return;

  if (e.key === "F2") {
    e.preventDefault();
    promptRename(selectedFsItem);
  } else if (e.key === "Delete") {
    e.preventDefault();
    confirmDelete(selectedFsItem);
  } else if (e.ctrlKey && e.key.toLowerCase() === "c") {
    e.preventDefault();
    copyFsItem(selectedFsItem);
  } else if (e.ctrlKey && e.key.toLowerCase() === "v" && fsClipboard) {
    e.preventDefault();
    pasteFsItem(selectedFsItem);
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (!selectedFsItem.is_dir) {
      openFileNative(selectedFsItem.path);
    }
  }
});

if ($("btn-toggle-recent-ws")) {
  $("btn-toggle-recent-ws").onclick = () => {
    const list = $("sidebar-recent-ws-list");
    if (!list) return;
    const isHide = list.style.display === "none";
    list.style.display = isHide ? "flex" : "none";
    $("btn-toggle-recent-ws").textContent = isHide ? "Thu gọn" : "Mở rộng";
  };
}

if ($("btn-fs-workspace")) $("btn-fs-workspace").onclick = function() { browseNativeWorkspace(this); };
if ($("ws-banner")) $("ws-banner").onclick = function() { browseNativeWorkspace(this); };
if ($("btn-ws-banner-switch")) $("btn-ws-banner-switch").onclick = function(e) { e.stopPropagation(); browseNativeWorkspace(this); };
if ($("btn-fs-workspace-footer")) $("btn-fs-workspace-footer").onclick = () => openWorkspaceDialog();
if ($("btn-workspace-header")) $("btn-workspace-header").onclick = function() { browseNativeWorkspace(this); };

if ($("btn-close-ws-dialog")) $("btn-close-ws-dialog").onclick = () => $("workspace-dialog").close();
if ($("btn-close-ws-dialog2")) $("btn-close-ws-dialog2").onclick = () => $("workspace-dialog").close();
if ($("btn-ws-browse-native")) $("btn-ws-browse-native").onclick = browseNativeWorkspace;

if ($("btn-ws-open-submit")) {
  $("btn-ws-open-submit").onclick = async () => {
    const p = $("ws-input-path").value.trim();
    if (!p) {
      const errEl = $("ws-open-error");
      if (errEl) {
        errEl.textContent = "Vui lòng nhập đường dẫn thư mục làm việc.";
        errEl.style.display = "block";
      }
      return;
    }
    await switchWorkspace(p);
  };
}

if ($("btn-ws-create-sample")) {
  $("btn-ws-create-sample").onclick = async () => {
    const projName = prompt("Nhập tên thư mục dự án mới muốn tạo:", "DuAn_CauMyThuan");
    if (!projName) return;
    const cleanName = projName.trim().replace(/[\/\\:*?"<>|]/g, "_");
    const samplePath = `C:\\Kuro-os\\Kuro\\projects\\${cleanName}`;
    $("ws-input-path").value = samplePath;
    await switchWorkspace(samplePath, cleanName);
  };
}

if ($("btn-fs-brain")) {
  $("btn-fs-brain").onclick = async () => {
    switchSidebarTab("explorer");
    await refreshFsTree();
  };
}

// Mở modal xem trước tệp tin
window.previewFile = function(filePath, fileName) {
  const name = fileName || (filePath || "").split("/").pop() || "file";
  const ext = "." + (name.split(".").pop() || "").toLowerCase();
  openFilePreview(filePath, name, ext);
};

async function openFilePreview(filePath, fileName, ext) {
  currentPreviewPath = filePath;
  $("fp-icon").innerHTML = getFileBadge(ext);
  $("fp-title").textContent = fileName;
  $("fp-path").textContent = filePath;
  $("fp-body").innerHTML = `<div style="color:var(--muted); padding:20px; text-align:center;">Đang đọc nội dung...</div>`;
  $("file-preview-dialog").showModal();

  const BINARY_EXTS = [
    ".xlsx", ".xls", ".xlsm", ".xlsb", ".xltx",
    ".docx", ".doc", ".docm", ".dotx",
    ".pptx", ".ppt", ".pptm",
    ".pdf",
    ".dwg", ".dxf", ".dgn",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".exe", ".dll", ".bin", ".iso", ".msi",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico"
  ];

  if (BINARY_EXTS.includes((ext || "").toLowerCase())) {
    renderBinaryFilePreview(filePath, fileName, ext);
    return;
  }

  try {
    const res = await fetch(`/api/fs/file?path=${encodeURIComponent(filePath)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      $("fp-body").innerHTML = `<div style="color:var(--amber); padding:20px;">${DOMPurify.sanitize(err.detail || "Không đọc được tệp tin này.")}</div>`;
      return;
    }
    const data = await res.json();
    if (data.is_binary) {
      renderBinaryFilePreview(filePath, fileName, ext, data.size);
      return;
    }
    const content = data.content;

    if (ext === ".md") {
      $("fp-body").innerHTML = md(content);
    } else {
      $("fp-body").innerHTML = `<pre><code>${DOMPurify.sanitize(content)}</code></pre>`;
    }
  } catch (err) {
    $("fp-body").innerHTML = `<div style="color:var(--amber); padding:20px;">Lỗi kết nối khi đọc tệp.</div>`;
  }
}

function renderBinaryFilePreview(filePath, fileName, ext, size) {
  let appHint = "phần mềm chuyên dụng";
  let iconId = "ic-file-text";
  let colorCls = "ic-muted";
  const e = (ext || "").toLowerCase();
  if (e.includes("xls")) {
    appHint = "Microsoft Excel";
    iconId = "ic-file-spreadsheet";
    colorCls = "ic-xls";
  } else if (e.includes("doc")) {
    appHint = "Microsoft Word";
    iconId = "ic-file-text";
    colorCls = "ic-doc";
  } else if (e.includes("ppt")) {
    appHint = "Microsoft PowerPoint";
    iconId = "ic-file-text";
    colorCls = "ic-amber";
  } else if (e === ".pdf") {
    appHint = "Trình đọc PDF / Adobe Acrobat";
    iconId = "ic-file-text";
    colorCls = "ic-pdf";
  } else if (e === ".dwg" || e === ".dxf") {
    appHint = "AutoCAD";
    iconId = "ic-compass";
    colorCls = "ic-cad";
  } else if (e === ".zip" || e === ".rar" || e === ".7z") {
    appHint = "WinRAR / 7-Zip";
    iconId = "ic-file-archive";
    colorCls = "ic-archive";
  }
  const icon = kuroIcon(iconId, "ic-xl", colorCls);

  $("fp-body").innerHTML = `
    <div class="binary-file-card">
      <div class="bfc-icon">${icon}</div>
      <h2 class="bfc-name">${DOMPurify.sanitize(fileName)}</h2>
      <div class="bfc-meta">Định dạng: <b>${(ext || "").toUpperCase()}</b> ${size ? '· Dung lượng: ' + formatBytes(size) : ''}</div>
      <p class="bfc-desc">
        Đây là tệp tin chuyên dụng. Bạn có thể mở trực tiếp bằng <b>${appHint}</b> cài trên máy tính Windows để làm việc, kiểm tra công thức tính và bảng biểu đầy đủ.
      </p>
      <div class="bfc-btns">
        <button type="button" class="btn main" id="btn-bfc-open" style="font-size:13px; padding:10px 18px;">
          🚀 Mở bằng ${appHint} trên Windows
        </button>
        <button type="button" class="btn" id="btn-bfc-reveal" style="font-size:13px; padding:10px 18px;">
          📂 Mở thư mục trong Explorer
        </button>
      </div>
    </div>
  `;

  const btnOpen = $("btn-bfc-open");
  const btnRev = $("btn-bfc-reveal");
  if (btnOpen) btnOpen.onclick = () => openFileNative(filePath);
  if (btnRev) btnRev.onclick = () => revealFileNative(filePath);
}

// Đóng modal xem trước
$("btn-fp-close").onclick = () => $("file-preview-dialog").close();

// Nút mở file và thư mục trong modal
if ($("btn-fp-open-native")) {
  $("btn-fp-open-native").onclick = () => {
    if (currentPreviewPath) openFileNative(currentPreviewPath);
  };
}
if ($("btn-fp-reveal")) {
  $("btn-fp-reveal").onclick = () => {
    if (currentPreviewPath) revealFileNative(currentPreviewPath);
  };
}

// Nút "Hỏi Kuro về file này": Chèn đường dẫn file vào ô chat
$("btn-fp-chat").onclick = () => {
  $("file-preview-dialog").close();
  const currentVal = $("q").value.trim();
  const insertText = `@${currentPreviewPath} `;
  $("q").value = currentVal ? `${currentVal}\n${insertText}` : `Hãy đọc và phân tích file ${insertText}: `;
  $("q").focus();
  $("q").style.height = "auto";
  $("q").style.height = Math.min($("q").scrollHeight, 200) + "px";
};

// ===================== ĐỒNG BỘ ĐIỆN THOẠI & REMOTE CONTROL =====================
let currentRemoteData = null;
let currentRemoteMode = "tailscale"; // "tailscale" hoặc "wifi"

// Mặc định Kuro chỉ cho máy này dùng; bật thì điện thoại quét QR (có mã ghép) mới vào được. Đổi cần mở lại Kuro.
function veNutDienThoai(dangMo, daLuu) {
  const txt = $("remote-lan-text"), btn = $("btn-remote-lan");
  if (!txt || !btn) return;
  txt.textContent = daLuu
    ? "Đã lưu. Tắt Kuro rồi mở lại để áp dụng."
    : dangMo
      ? "Đang cho điện thoại kết nối. Chỉ thiết bị đã quét mã QR dưới đây mới vào được."
      : "Kuro đang chỉ cho máy này dùng. Mã QR dưới đây chưa dùng được cho tới khi bật.";
  btn.textContent = dangMo ? "Tắt kết nối điện thoại" : "Bật cho điện thoại kết nối";
  btn.onclick = async () => {
    btn.disabled = true;
    try {
      const r = await fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ KURO_HOST: dangMo ? "127.0.0.1" : "0.0.0.0" }) });
      if (!r.ok) throw new Error((await r.json()).detail || r.status);
      veNutDienThoai(!dangMo, true);
    } catch (e) {
      txt.textContent = "Không lưu được: " + e.message;
    } finally {
      btn.disabled = false;
    }
  };
}

async function showRemoteDialog() {
  const dlg = $("remote-dialog");
  if (!dlg) return;

  const qrImg = $("remote-qr-img");
  const priUrl = $("remote-primary-url");
  const pillsBox = $("remote-ip-pills");
  const urlLabel = $("remote-url-label");
  const tsCard = $("tailscale-card-info");
  const tsAccountBadge = $("ts-account-badge");
  const tsPeerNotice = $("ts-peer-notice");
  const tsPeerName = $("ts-peer-name");

  if (priUrl) priUrl.textContent = "Đang kiểm tra địa chỉ mạng & Tailscale...";
  if (pillsBox) pillsBox.innerHTML = "";

  dlg.showModal();

  try {
    const res = await fetch("/api/network/remote");
    if (!res.ok) throw new Error("Không lấy được thông tin mạng");
    const data = await res.json();
    currentRemoteData = data;
    veNutDienThoai(data.listening_all);

    const hasTs = data.tailscale && data.tailscale.running && data.tailscale_ip;

    if (hasTs) {
      if (tsCard) tsCard.style.display = "flex";
      if (tsAccountBadge) tsAccountBadge.textContent = data.tailscale.user ? (data.tailscale.user.name || data.tailscale.user.login) : "Đã đăng nhập";
      if (tsPeerNotice && data.tailscale.peers && data.tailscale.peers.length > 0) {
        const peer = data.tailscale.peers[0];
        if (tsPeerName) tsPeerName.textContent = `${peer.name} (${peer.os})`;
        tsPeerNotice.style.display = "block";
      } else if (tsPeerNotice) {
        tsPeerNotice.style.display = "none";
      }
      setRemoteMode("tailscale");
    } else {
      if (tsCard) tsCard.style.display = "none";
      setRemoteMode("wifi");
    }

    if (pillsBox && Array.isArray(data.all_ips)) {
      pillsBox.innerHTML = "";
      data.all_ips.forEach((item) => {
        const pill = document.createElement("button");
        pill.type = "button";
        pill.className = "ip-pill";
        pill.title = `Bấm để tạo mã QR cho ${item.ip} (${item.type})`;
        pill.innerHTML = `<span>${item.type.includes("Tailscale") ? "🔒" : "🌐"}</span> <b>${DOMPurify.sanitize(item.ip)}</b> <small style="color:var(--muted);">(${DOMPurify.sanitize(item.type)})</small>`;
        pill.onclick = async () => {
          if (priUrl) priUrl.textContent = item.url;
          if (urlLabel) urlLabel.textContent = `ĐỊA CHỈ TRUY CẬP (${item.type.toUpperCase()}):`;
          if (qrImg) qrImg.style.opacity = "0.5";
          try {
            const r2 = await fetch(`/api/network/remote?url=${encodeURIComponent(item.url)}`);
            if (r2.ok) {
              const d2 = await r2.json();
              if (d2.qr_code && qrImg) qrImg.src = d2.qr_code;
            }
          } catch (e) {
            console.error("Lỗi đổi QR:", e);
          } finally {
            if (qrImg) qrImg.style.opacity = "1";
          }
        };
        pillsBox.appendChild(pill);
      });
    }
  } catch (err) {
    if (priUrl) priUrl.textContent = `http://${location.hostname}:${location.port || 7788}`;
    console.error("Lỗi showRemoteDialog:", err);
  }
}

function setRemoteMode(mode) {
  currentRemoteMode = mode;
  const qrImg = $("remote-qr-img");
  const priUrl = $("remote-primary-url");
  const urlLabel = $("remote-url-label");
  const tabTs = $("tab-remote-tailscale");
  const tabWifi = $("tab-remote-wifi");
  const data = currentRemoteData;
  if (!data) return;

  if (mode === "tailscale" && data.tailscale_ip) {
    if (tabTs) tabTs.classList.add("active");
    if (tabWifi) tabWifi.classList.remove("active");
    if (priUrl) priUrl.textContent = data.tailscale_url;
    if (urlLabel) urlLabel.textContent = "ĐỊA CHỈ TAILSCALE VPN (DÙNG CHO 4G/NGOÀI MẠNG):";
    if (qrImg && data.tailscale_qr) qrImg.src = data.tailscale_qr;
  } else {
    if (tabTs) tabTs.classList.remove("active");
    if (tabWifi) tabWifi.classList.add("active");
    if (priUrl) priUrl.textContent = data.primary_url;
    if (urlLabel) urlLabel.textContent = "ĐỊA CHỈ TRUY CẬP (WI-FI / LAN NỘI BỘ):";
    if (qrImg && data.qr_code) qrImg.src = data.qr_code;
  }
}

function closeRemoteDialog() {
  const dlg = $("remote-dialog");
  if (dlg) dlg.close();
}

$("btn-remote-header") && ($("btn-remote-header").onclick = showRemoteDialog);
$("ctx-env-remote-row") && ($("ctx-env-remote-row").onclick = showRemoteDialog);
$("btn-close-remote-dialog") && ($("btn-close-remote-dialog").onclick = closeRemoteDialog);
$("btn-close-remote-dialog2") && ($("btn-close-remote-dialog2").onclick = closeRemoteDialog);

if ($("tab-remote-tailscale")) $("tab-remote-tailscale").onclick = () => setRemoteMode("tailscale");
if ($("tab-remote-wifi")) $("tab-remote-wifi").onclick = () => setRemoteMode("wifi");

$("btn-copy-remote-url") && ($("btn-copy-remote-url").onclick = async () => {
  const urlEl = $("remote-primary-url");
  const url = urlEl ? urlEl.textContent.trim() : "";
  if (!url) return;
  try {
    await navigator.clipboard.writeText(url);
    const orig = $("btn-copy-remote-url").textContent;
    $("btn-copy-remote-url").textContent = "✓ Đã sao chép!";
    setTimeout(() => {
      $("btn-copy-remote-url").textContent = orig;
    }, 2000);
  } catch (e) {
    alert("Đã chọn địa chỉ: " + url);
  }
});

// Đăng ký Service Worker cho PWA
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").then((reg) => {
      console.log("[PWA] Service Worker registered:", reg.scope);
    }).catch((err) => {
      console.log("[PWA] Service Worker registration skipped:", err);
    });
  });
}

// ========================================================
// ========================================================
// THANH VẠCH ĐIỀU HƯỚNG CÂU HỎI TẬP TRUNG (CHAT NAV HUB)
// ========================================================
let navPopoverTimer = null;

function updateChatNavTicks() {
  const rail = $("chat-nav-rail");
  const log = $("log");
  const popover = $("chat-nav-popover");
  const countEl = $("chat-nav-hub-count");
  const container = $("chat-nav-ticks-container");
  if (!rail || !log) return;

  const userMsgs = Array.from(log.querySelectorAll(".msg.user"));
  if (userMsgs.length <= 1) {
    rail.style.display = "none";
    if (popover) popover.style.display = "none";
    return;
  }

  rail.style.display = "flex";
  if (countEl) countEl.textContent = userMsgs.length;

  const targetContainer = container || rail;
  targetContainer.innerHTML = "";

  userMsgs.forEach((msgEl, idx) => {
    const tick = document.createElement("div");
    tick.className = "chat-nav-tick";
    tick.dataset.idx = idx;

    const rawSnippet = (msgEl.textContent || "").trim().replace(/^BẠN \(KỸ SƯ\)\s*/i, "").replace(/\s+/g, " ");
    tick.title = `Câu hỏi #${idx + 1}: ${rawSnippet.slice(0, 50)}`;

    tick.addEventListener("mouseenter", () => {
      showChatNavPopover(idx, userMsgs, tick);
    });

    tick.addEventListener("click", (e) => {
      e.stopPropagation();
      msgEl.scrollIntoView({ behavior: "smooth", block: "center" });
      msgEl.classList.add("highlight-flash");
      setTimeout(() => msgEl.classList.remove("highlight-flash"), 1200);
      hideChatNavPopover();
    });

    targetContainer.appendChild(tick);
  });

  // Bắt sự kiện nút bấm Hub Icon để mở/đóng danh sách
  const hubBtn = $("chat-nav-hub-btn");
  if (hubBtn && !hubBtn._bound) {
    hubBtn._bound = true;
    hubBtn.onclick = (e) => {
      e.stopPropagation();
      if (popover && popover.style.display !== "none") {
        hideChatNavPopover();
      } else {
        const msgs = Array.from($("log").querySelectorAll(".msg.user"));
        showChatNavPopover(0, msgs, hubBtn);
      }
    };
  }

  updateActiveTickOnScroll();
}

// Cập nhật vạch đang active khi người dùng cuộn nội dung chat
function updateActiveTickOnScroll() {
  const log = $("log");
  const container = $("chat-nav-ticks-container") || $("chat-nav-rail");
  if (!log || !container) return;

  const userMsgs = Array.from(log.querySelectorAll(".msg.user"));
  const ticks = Array.from(container.querySelectorAll(".chat-nav-tick"));
  if (userMsgs.length === 0 || ticks.length === 0) return;

  const viewTop = log.scrollTop;
  const viewBottom = viewTop + log.clientHeight;

  let activeIdx = 0;
  for (let i = 0; i < userMsgs.length; i++) {
    const m = userMsgs[i];
    if (m.offsetTop <= viewTop + log.clientHeight * 0.45) {
      activeIdx = i;
    } else {
      break;
    }
  }

  ticks.forEach((t, i) => {
    t.classList.toggle("active", i === activeIdx);
  });
}

function showChatNavPopover(centerIdx, userMsgs, targetTick) {
  clearTimeout(navPopoverTimer);
  const popover = $("chat-nav-popover");
  const rail = $("chat-nav-rail");
  if (!popover || !rail) return;

  const total = userMsgs.length;
  const itemsHtml = [];
  for (let i = 0; i < total; i++) {
    const el = userMsgs[i];
    const text = (el.textContent || "").trim().replace(/^BẠN \(KỸ SƯ\)\s*/i, "").replace(/\s+/g, " ");
    const isCenter = (i === centerIdx);
    itemsHtml.push(`
      <div class="chat-nav-item ${isCenter ? 'highlighted' : ''}" data-idx="${i}" title="${escapeHtml(text)}">
        <span style="color:var(--amber); font-weight:600; margin-right:4px;">#${i + 1}</span> ${escapeHtml(text.slice(0, 50))}${text.length > 50 ? '...' : ''}
      </div>
    `);
  }

  popover.innerHTML = `
    <div class="chat-nav-popover-header">
      <span>MỤC LỤC CÂU HỎI (${total})</span>
      <span style="font-size:10px; color:var(--muted); font-family:var(--body);">Bấm để cuộn đến</span>
    </div>
    <div class="chat-nav-list">${itemsHtml.join("")}</div>
  `;

  popover.style.top = `65px`;
  popover.style.right = `48px`;
  popover.style.display = "flex";

  popover.querySelectorAll(".chat-nav-item").forEach(item => {
    item.addEventListener("click", () => {
      const idx = parseInt(item.dataset.idx, 10);
      const targetEl = userMsgs[idx];
      if (targetEl) {
        targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
        targetEl.classList.add("highlight-flash");
        setTimeout(() => targetEl.classList.remove("highlight-flash"), 1200);
      }
      hideChatNavPopover();
    });
  });

  popover.onmouseenter = () => clearTimeout(navPopoverTimer);
  popover.onmouseleave = () => scheduleHideChatNavPopover();
}

function scheduleHideChatNavPopover() {
  clearTimeout(navPopoverTimer);
  navPopoverTimer = setTimeout(() => {
    hideChatNavPopover();
  }, 280);
}

function hideChatNavPopover() {
  const popover = $("chat-nav-popover");
  if (popover) popover.style.display = "none";
}

if ($("chat-nav-rail")) {
  $("chat-nav-rail").onmouseleave = scheduleHideChatNavPopover;
}

document.addEventListener("click", (e) => {
  const popover = $("chat-nav-popover");
  const rail = $("chat-nav-rail");
  if (popover && popover.style.display !== "none") {
    if (!popover.contains(e.target) && (!rail || !rail.contains(e.target))) {
      hideChatNavPopover();
    }
  }
});

const scrollBottomBtn = $("btn-scroll-bottom");
const logContainer = $("log");
if (scrollBottomBtn && logContainer) {
  logContainer.addEventListener("scroll", () => {
    const distFromBottom = logContainer.scrollHeight - logContainer.scrollTop - logContainer.clientHeight;
    if (distFromBottom > 130) {
      scrollBottomBtn.style.display = "flex";
    } else {
      scrollBottomBtn.style.display = "none";
    }
    if (typeof updateActiveTickOnScroll === "function") {
      updateActiveTickOnScroll();
    }
  });

  scrollBottomBtn.addEventListener("click", () => {
    logContainer.scrollTo({ top: logContainer.scrollHeight, behavior: "smooth" });
  });
}

window.addEventListener("resize", () => {
  if (typeof updateChatNavTicks === "function") {
    updateChatNavTicks();
  }
});

// Chuyển đổi giao diện Sáng nổi khối Soft UI (mặc định) <-> Tối Navy Đêm đồng bộ
function syncThemeUI() {
  const isDark = document.body.classList.contains("theme-dark");
  const iconEl = $("theme-toggle-icon");
  const textEl = $("theme-toggle-text");
  const metaEl = document.getElementById("meta-theme-color");
  if (iconEl) iconEl.innerHTML = kuroIcon(isDark ? "ic-sun" : "ic-moon", "ic-sm");
  if (textEl) textEl.textContent = isDark ? "Bản sáng" : "Bản tối";
  if (metaEl) metaEl.setAttribute("content", isDark ? "#09101c" : "#dfe6f0");
}
const btnThemeToggle = $("btn-theme-toggle");
if (btnThemeToggle) {
  syncThemeUI();
  btnThemeToggle.addEventListener("click", () => {
    document.body.classList.add("theme-switching");
    const nowDark = document.body.classList.toggle("theme-dark");
    try {
      localStorage.setItem("kuro_ui_theme", nowDark ? "dark" : "light");
    } catch (_) {}
    syncThemeUI();
    void document.body.offsetWidth;
    requestAnimationFrame(() => document.body.classList.remove("theme-switching"));
  });
}

// Khởi chạy
updateSendButtonState();
connect();
loadSkills();
loadWorkspaces().then(async () => {
  await loadAgents();
  await loadSessions(selectedAgent);
  await refreshFsTree();
});
loadModels().catch(() => {});
fetchAndRenderQuota().catch(() => {});
checkUpdate().catch(() => {});
setInterval(() => checkUpdate().catch(() => {}), 3600e3);

