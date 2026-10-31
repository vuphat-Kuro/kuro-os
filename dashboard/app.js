const $ = (id) => document.getElementById(id);
const md = (t) => DOMPurify.sanitize(marked.parse(t || ""));
let session = null, ws, bot = null, botText = "", busy = false;

// Linh vật Kuro: chibi kỹ sư robot đội mũ bảo hộ, mặc áo phản quang; đèn mũ là lõi năng lượng.
// Biểu cảm đi theo class trên body (busy, happy, err) nên mọi bản trên trang đổi cùng lúc.
const MASCOT = `<svg viewBox="-100 -100 200 200" aria-hidden="true">
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
document.querySelectorAll(".mascot").forEach((el) => { el.innerHTML = MASCOT; });
// Mắt nhìn theo con trỏ.
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

function setBusy(b) {
  busy = b;
  document.body.classList.toggle("busy", b);
  if (b) mood(null);
  $("state").textContent = b ? "Đang xử lý" : "Sẵn sàng";
}

function add(cls, html) {
  const d = document.createElement("div");
  d.className = "msg " + cls;
  d.innerHTML = html;
  $("log").append(d);
  $("log").scrollTop = $("log").scrollHeight;
  return d;
}

function connect() {
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.type === "session") { session = m.id; return; }
    if (!bot) { bot = add("bot", ""); botText = ""; }
    if (m.type === "text") { botText += m.text; bot.innerHTML = md(botText); }
    else if (m.type === "tool") bot.insertAdjacentHTML("beforeend", `<span class="tool">${DOMPurify.sanitize(m.name)}</span>`);
    else if (m.type === "error") { botText += `\n\n**Lỗi:** ${m.text}`; bot.innerHTML = md(botText); mood("err"); }
    else if (m.type === "final") {
      if (!botText && m.text) bot.innerHTML = md(m.text);
      bot = null; setBusy(false); loadSessions();
      if (!document.body.classList.contains("err")) mood("happy");
    }
    $("log").scrollTop = $("log").scrollHeight;
  };
  ws.onopen = () => { document.body.classList.add("online"); $("net").textContent = "Ổn định"; };
  ws.onclose = () => {
    document.body.classList.remove("online"); $("net").textContent = "Mất nối";
    if (busy) setBusy(false);
    setTimeout(connect, 2000);
  };   // server khởi động lại thì tự nối lại
}

async function loadSessions() {
  const list = await (await fetch("/api/sessions")).json();
  $("sessions").replaceChildren(...list.map((s) => {
    const d = document.createElement("div");
    d.textContent = s.title;
    d.title = s.title;
    d.className = s.id === session ? "on" : "";
    d.onclick = () => openSession(s.id);
    return d;
  }));
}

async function openSession(id) {
  session = id;
  $("log").replaceChildren();
  for (const m of await (await fetch(`/api/sessions/${id}`)).json()) {
    if (m.role === "user") add("user", "").textContent = m.text;
    else add("bot", md(m.text));
  }
  loadSessions();
}

$("q").onkeydown = (e) => {
  if (e.key !== "Enter" || e.shiftKey) return;
  e.preventDefault();
  const text = $("q").value.trim();
  if (!text || busy || ws.readyState !== 1) return;
  setBusy(true);
  add("user", "").textContent = text;
  ws.send(JSON.stringify({ session, text }));
  $("q").value = "";
};
$("f").onsubmit = (e) => e.preventDefault();
$("new").onclick = () => { session = null; $("log").replaceChildren(); loadSessions(); $("q").focus(); };

const tick = () => { $("clock").textContent = new Date().toLocaleTimeString("vi-VN", { hour12: false }); };
tick(); setInterval(tick, 1000);
connect();
loadSessions();

// Cài đặt: khóa bí mật không bao giờ được trả về trình duyệt, ô trống nghĩa là giữ nguyên.
let providers = {};
async function openSettings() {
  const r = await (await fetch("/api/settings")).json();
  providers = r.providers;
  const sel = $("s-KURO_PROVIDER");
  if (sel.options.length === 1) for (const [id, p] of Object.entries(providers)) sel.add(new Option(p.ten, id));
  $("s-status").innerHTML = `<span class="chip ${r.claude_cli ? "ok" : "no"}">Claude Code ${r.claude_cli ? "có" : "chưa cài"}</span>` +
    `<span class="chip ${r.cli.codex ? "ok" : "no"}">Codex ${r.cli.codex ? "có" : "chưa cài"}</span>` +
    `<span class="chip ${r.cli.agy ? "ok" : "no"}">Antigravity ${r.cli.agy ? "có" : "chưa cài"}</span>` +
    `<span class="chip ${r.telegram_on ? "ok" : "no"}">Telegram ${r.telegram_on ? "đang chạy" : "tắt"}</span>`;
  for (const [k, v] of Object.entries(r.settings)) {
    const el = $("sf").elements[k];
    if (el.dataset.secret) { el.value = ""; delete el.dataset.clear; el.placeholder = v.set ? `Đã lưu ${v.hint} - gõ để thay` : "Chưa có"; continue; }
    el.value = el.dataset.orig = v.value;
  }
  // Lần đầu mở Kuro (chưa chọn AI): hộp này thành màn hình chào, chọn AI trước khi dùng.
  showCore(r);
  const first = !r.settings.KURO_PROVIDER.value;
  $("s-title").textContent = first ? "CHỌN AI CHO KURO" : "CÀI ĐẶT";
  if (first) $("s-status").insertAdjacentHTML("afterbegin", "<p>Chọn AI bạn có tài khoản hoặc key, rồi bấm <b>Lưu và kiểm tra kết nối</b>. Đổi lại lúc nào cũng được ở ⚙ Cài đặt.</p>");
  showProvider();
  if (!$("settings").open) { $("s-msg").textContent = ""; $("s-test-msg").textContent = ""; $("settings").showModal(); }
}

function showProvider() {
  const p = providers[$("s-KURO_PROVIDER").value] || {};
  $("s-hint").textContent = p.goi_y || "";
  $("s-keyrow").hidden = !p.key;
  $("s-urlrow").hidden = !p.url && $("s-KURO_PROVIDER").value !== "custom";
  $("s-KURO_BASE_URL").placeholder = p.url || "https://...";
}
$("s-KURO_PROVIDER").onchange = showProvider;

async function saveSettings() {
  const body = {};
  for (const el of $("sf").querySelectorAll("[name]")) {
    if (el.dataset.secret ? el.value || el.dataset.clear : el.value !== el.dataset.orig) body[el.name] = el.value;
  }
  const msg = $("s-msg");
  if (!Object.keys(body).length) { msg.className = ""; msg.textContent = "Chưa có gì thay đổi."; return true; }
  const r = await fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  msg.className = r.ok ? "" : "err";
  msg.textContent = !r.ok ? (j.detail || "Lưu thất bại") : j.restart ? "Đã lưu. Khởi động lại Kuro để áp dụng Telegram." : "Đã lưu. Có hiệu lực từ câu hỏi kế tiếp.";
  if (r.ok) await openSettings();
  return r.ok;
}
$("sf").onsubmit = (e) => { e.preventDefault(); saveSettings(); };

$("s-test").onclick = async () => {
  const out = $("s-test-msg");
  if (!$("s-KURO_PROVIDER").value) { out.className = "err"; out.textContent = "Chọn AI trước đã."; return; }
  if (!(await saveSettings())) return;
  out.className = ""; out.textContent = "Đang hỏi thử AI (tối đa 90 giây)...";
  $("s-test").disabled = true;
  try {
    const j = await (await fetch("/api/test-ai", { method: "POST" })).json();
    out.className = j.ok ? "ok" : "err";
    out.textContent = j.ok ? `Kết nối được. AI trả lời: "${j.text}"` : `Chưa kết nối được: ${j.error || "không có trả lời"}`;
  } finally { $("s-test").disabled = false; }
};
$("sf").addEventListener("click", (e) => {
  const k = e.target.dataset.clear;
  if (!k) return;
  const el = $("sf").elements[k];
  el.value = ""; el.dataset.clear = "1"; el.placeholder = "Sẽ xóa khi bấm Lưu";
});
$("gear").onclick = $("gear2").onclick = openSettings;
$("s-close").onclick = () => $("settings").close();
// Góc dưới thanh bên ghi AI đang dùng (chỉ tên hãng; tài khoản là tài khoản đăng nhập trên chính máy này).
function showCore(r) {
  const id = r.settings.KURO_PROVIDER.value;
  $("core").textContent = id ? r.providers[id].ten.split(" (")[0] : "Chưa chọn";
}
// Chưa chọn AI thì mở màn hình chọn AI ngay khi vào trang.
fetch("/api/settings").then((r) => r.json()).then((r) => { showCore(r); if (!r.settings.KURO_PROVIDER.value) openSettings(); }).catch(() => {});

// Báo bản mới: server tự hỏi GitHub 6 giờ một lần, trang hỏi server mỗi giờ.
async function checkUpdate() {
  const u = await (await fetch("/api/update")).json();
  const box = $("update");
  box.hidden = !u.behind;
  if (!u.behind) return;
  const esc = (t) => DOMPurify.sanitize(t, { ALLOWED_TAGS: [] });
  box.innerHTML = `<b>Có bản mới ${esc(u.latest)}</b>Bạn đang dùng ${esc(u.current)}. Bấm đúp <code>cap-nhat.bat</code> trong thư mục Kuro, cập nhật xong Kuro tự mở lại.` +
    (u.notes.length ? `<ul>${u.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : "");
}
checkUpdate().catch(() => {});
setInterval(() => checkUpdate().catch(() => {}), 3600e3);
