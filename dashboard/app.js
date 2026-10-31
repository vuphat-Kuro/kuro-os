const $ = (id) => document.getElementById(id);
const md = (t) => DOMPurify.sanitize(marked.parse(t || ""));
let session = null, ws, bot = null, botText = "", busy = false;

function setBusy(b) {
  busy = b;
  document.body.classList.toggle("busy", b);
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
    else if (m.type === "error") { botText += `\n\n**Lỗi:** ${m.text}`; bot.innerHTML = md(botText); }
    else if (m.type === "final") {
      if (!botText && m.text) bot.innerHTML = md(m.text);
      bot = null; setBusy(false); loadSessions();
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
async function openSettings() {
  const r = await (await fetch("/api/settings")).json();
  $("s-status").innerHTML = `<span class="chip ${r.claude_cli ? "ok" : "no"}">Claude CLI ${r.claude_cli ? "có" : "chưa cài"}</span>` +
    `<span class="chip ${r.telegram_on ? "ok" : "no"}">Telegram ${r.telegram_on ? "đang chạy" : "tắt"}</span>`;
  for (const [k, v] of Object.entries(r.settings)) {
    const el = $("sf").elements[k];
    if (el.dataset.secret) { el.value = ""; delete el.dataset.clear; el.placeholder = v.set ? `Đã lưu ${v.hint} - gõ để thay` : "Chưa có"; continue; }
    if (el.tagName === "SELECT" && ![...el.options].some((o) => o.value === v.value)) el.add(new Option(v.value, v.value));
    el.value = el.dataset.orig = v.value;
  }
  if (!$("settings").open) { $("s-msg").textContent = ""; $("settings").showModal(); }
}

$("sf").onsubmit = async (e) => {
  e.preventDefault();
  const body = {};
  for (const el of $("sf").querySelectorAll("[name]")) {
    if (el.dataset.secret ? el.value || el.dataset.clear : el.value !== el.dataset.orig) body[el.name] = el.value;
  }
  const msg = $("s-msg");
  if (!Object.keys(body).length) { msg.className = ""; msg.textContent = "Chưa có gì thay đổi."; return; }
  const r = await fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  msg.className = r.ok ? "" : "err";
  msg.textContent = !r.ok ? (j.detail || "Lưu thất bại") : j.restart ? "Đã lưu. Khởi động lại Kuro để áp dụng Telegram." : "Đã lưu. Có hiệu lực từ câu hỏi kế tiếp.";
  if (r.ok) openSettings();
};
$("sf").addEventListener("click", (e) => {
  const k = e.target.dataset.clear;
  if (!k) return;
  const el = $("sf").elements[k];
  el.value = ""; el.dataset.clear = "1"; el.placeholder = "Sẽ xóa khi bấm Lưu";
});
$("gear").onclick = $("gear2").onclick = openSettings;
$("s-close").onclick = () => $("settings").close();

// Báo bản mới: server tự hỏi GitHub 6 giờ một lần, trang hỏi server mỗi giờ.
async function checkUpdate() {
  const u = await (await fetch("/api/update")).json();
  const box = $("update");
  box.hidden = !u.behind;
  if (!u.behind) return;
  const esc = (t) => DOMPurify.sanitize(t, { ALLOWED_TAGS: [] });
  box.innerHTML = `<b>Có bản mới ${esc(u.latest)}</b>Bạn đang dùng ${esc(u.current)}. Bấm đúp <code>cap-nhat.bat</code> trong thư mục Kuro rồi chạy lại <code>run.bat</code>.` +
    (u.notes.length ? `<ul>${u.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : "");
}
checkUpdate().catch(() => {});
setInterval(() => checkUpdate().catch(() => {}), 3600e3);
