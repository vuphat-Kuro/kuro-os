const $ = (id) => document.getElementById(id);
const md = (t) => DOMPurify.sanitize(marked.parse(t || ""));

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

// Icon chuyên môn theo từng Agent
const AGENT_ICONS = {
  "kuro-core": MASCOT_SVG,
  "ky-su-bien-phap": `<svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M2 18h20"></path><path d="M4 18v-4a8 8 0 0 1 16 0v4"></path><path d="M12 4v2"></path><path d="M12 10h.01"></path>
  </svg>`,
  "ky-su-kiem-toan-phu-tro": `<svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>`,
  "ky-su-qs": `<svg viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2"></rect><line x1="8" y1="6" x2="16" y2="6"></line>
    <line x1="16" y1="14" x2="16" y2="14.01"></line><line x1="12" y1="14" x2="12" y2="14.01"></line><line x1="8" y1="14" x2="8" y2="14.01"></line>
    <line x1="16" y1="18" x2="16" y2="18.01"></line><line x1="12" y1="18" x2="12" y2="18.01"></line><line x1="8" y1="18" x2="8" y2="18.01"></line>
  </svg>`,
  "ky-su-qaqc": `<svg viewBox="0 0 24 24" fill="none" stroke="#c084fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
    <rect x="8" y="2" width="8" height="4" rx="1"></rect><path d="m9 14 2 2 4-4"></path>
  </svg>`,
  "ky-su-ke-hoach": `<svg viewBox="0 0 24 24" fill="none" stroke="#67e8f9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line>
    <line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line>
    <path d="m8 14 2 2 4-4"></path>
  </svg>`,
  "dieu-phoi-bim": `<svg viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="m21 16-9 5-9-5V8l9-5 9 5v8Z"></path><path d="M3.27 6.96 12 12.01l8.73-5.05"></path><path d="M12 22.08V12"></path>
  </svg>`,
};

function getAgentIcon(slug) {
  return AGENT_ICONS[slug] || `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/></svg>`;
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
  "ky-su-qs": [
    "Bóc tách khối lượng bê tông, cốt thép và ván khuôn kết cấu mố trụ cầu M1",
    "Rà soát đối chiếu chênh lệch khối lượng bản vẽ BVTC so với khối lượng Hợp đồng EPC",
    "Lập biểu tổng hợp khối lượng phụ lục phát sinh ngoài phạm vi hợp đồng xây lắp"
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

function setBusy(b) {
  busy = b;
  document.body.classList.toggle("busy", b);
  $("typing-indicator").style.display = b ? "inline" : "none";
  if (b) mood(null);
  $("state").textContent = b ? "Đang xử lý" : "Sẵn sàng";
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
  return d;
}

function currentAgent() {
  return agents.find((a) => a.slug === selectedAgent) || agents[0] || { slug: "kuro-core", name: "Kuro Core", role: "" };
}

// Lấy danh sách Agents từ server
async function loadAgents() {
  try {
    const res = await fetch("/api/agents");
    agents = await res.json();
    $("agent-count").textContent = agents.length;
    renderAgentList();
    updateActiveAgentUI();
  } catch (e) {
    console.error("Lỗi tải agents:", e);
  }
}

// Render danh sách Agents (Cộng sự)
function renderAgentList() {
  const listEl = $("agent-list");
  listEl.innerHTML = "";
  const filter = ($("agent-search").value || "").trim().toLowerCase();

  const filtered = agents.filter((a) => {
    return !filter || a.name.toLowerCase().includes(filter) || (a.role && a.role.toLowerCase().includes(filter)) || a.slug.includes(filter);
  });

  const coreAgents = filtered.filter((a) => a.is_core);
  const specAgents = filtered.filter((a) => !a.is_core);

  if (coreAgents.length) {
    const title = document.createElement("div");
    title.className = "sec-title";
    title.textContent = "Hệ thống";
    listEl.appendChild(title);
    coreAgents.forEach((a) => listEl.appendChild(createAgentCard(a)));
  }

  if (specAgents.length) {
    const title = document.createElement("div");
    title.className = "sec-title";
    title.textContent = "Chuyên ngành (Đã ghim)";
    listEl.appendChild(title);
    specAgents.forEach((a) => listEl.appendChild(createAgentCard(a)));
  }

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "session-empty";
    empty.textContent = "Không tìm thấy cộng sự nào.";
    listEl.appendChild(empty);
  }
}

function createAgentCard(agent) {
  const card = document.createElement("div");
  card.className = "agent-card" + (agent.is_core ? " core-agent" : "") + (agent.slug === selectedAgent ? " on" : "");
  card.onclick = () => selectAgent(agent.slug);

  card.innerHTML = `
    <div class="agent-avatar">${getAgentIcon(agent.slug)}</div>
    <div class="agent-info">
      <div class="agent-top-line">
        <span class="agent-name">${DOMPurify.sanitize(agent.name)}</span>
        <span class="agent-badge-tag ${agent.is_core ? 'sys' : ''}">${DOMPurify.sanitize(agent.badge || 'Chuyên môn')}</span>
      </div>
      <p class="agent-desc">${DOMPurify.sanitize(agent.role || '')}</p>
    </div>
  `;
  return card;
}

// Khi người dùng bấm chọn một Agent
async function selectAgent(slug) {
  if (selectedAgent === slug && session) return;
  selectedAgent = slug;
  localStorage.setItem("kuro_active_agent", slug);

  // Cập nhật highlight thẻ Agent
  renderAgentList();
  updateActiveAgentUI();

  // Tải danh sách phiên riêng của Agent này
  await loadSessions(slug);

  // Mở phiên mới cho Agent này
  newSession();
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

// Tìm kiếm Agent
$("agent-search").oninput = renderAgentList;

// Tải lịch sử phiên cho Agent được chọn
async function loadSessions(agentSlug) {
  agentSlug = agentSlug || selectedAgent;
  try {
    const res = await fetch(`/api/sessions?agent=${encodeURIComponent(agentSlug)}`);
    currentSessions = await res.json();
    renderSessionList();
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

function createSessionItem(s) {
  const el = document.createElement("div");
  el.className = "session-item" + (s.id === session ? " on" : "");
  el.onclick = () => openSession(s.id);

  el.innerHTML = `
    <div class="session-title" title="${DOMPurify.sanitize(s.title)}">${DOMPurify.sanitize(s.title)}</div>
    <div class="session-time">${formatSessionTime(s.updated)}</div>
    <button class="btn-del-session" type="button" title="Xóa phiên này">🗑</button>
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
  $("log").replaceChildren();
  renderSessionList();

  try {
    const res = await fetch(`/api/sessions/${id}`);
    const msgs = await res.json();
    const a = currentAgent();
    for (const m of msgs) {
      if (m.role === "user") {
        addMessage("user", "").textContent = m.text;
      } else {
        addMessage("bot", md(m.text), a.name.toUpperCase());
      }
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
  $("q").focus();
}

$("new").onclick = newSession;
$("btn-new-conv").onclick = newSession;

// Đóng mở cột Lịch sử
$("btn-toggle-history").onclick = () => {
  $("history-sidebar").classList.toggle("collapsed");
};
$("btn-close-history").onclick = () => {
  $("history-sidebar").classList.add("collapsed");
};

// Đóng mở danh sách Agent trên điện thoại/màn hình nhỏ
$("btn-menu-agents").onclick = () => {
  $("agents-sidebar").classList.toggle("collapsed");
};

// Kết nối WebSocket
function connect() {
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.type === "session") {
      session = m.id;
      return;
    }
    const a = currentAgent();
    if (!bot) {
      bot = addMessage("bot", "", a.name.toUpperCase());
      botText = "";
    }
    if (m.type === "text") {
      botText += m.text;
      bot.innerHTML = md(botText);
    } else if (m.type === "tool") {
      bot.insertAdjacentHTML("beforeend", `<span class="tool">${DOMPurify.sanitize(m.name)}</span>`);
    } else if (m.type === "error") {
      botText += `\n\n**Lỗi:** ${m.text}`;
      bot.innerHTML = md(botText);
      mood("err");
    } else if (m.type === "final") {
      if (!botText && m.text) bot.innerHTML = md(m.text);
      bot = null;
      setBusy(false);
      loadSessions(selectedAgent);
      if (!document.body.classList.contains("err")) mood("happy");
    }
    $("log").scrollTop = $("log").scrollHeight;
  };
  ws.onopen = () => {
    document.body.classList.add("online");
    $("net").textContent = "Ổn định";
  };
  ws.onclose = () => {
    document.body.classList.remove("online");
    $("net").textContent = "Mất nối";
    if (busy) setBusy(false);
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

// Xử lý gửi tin nhắn và lệnh slash
$("f").onsubmit = async (e) => {
  e.preventDefault();
  hideSlashMenu();
  const text = $("q").value.trim();
  if (!text || busy) return;

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

    if (cmd === "clear" || cmd === "new" || cmd === "reset") {
      $("q").value = "";
      newSession();
      return;
    }

    if (cmd === "model") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      const cur = $("model-pick").value || "Mặc định";
      addMessage("bot", md(`Model AI hiện đang cấu hình: **${cur}**. Bạn có thể đổi nhanh tại thanh chọn model góc trên bên phải.`));
      return;
    }

    if (cmd === "context") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      if (!session) {
        addMessage("bot", md("*(Phiên mới chưa có tin nhắn nào được lưu)*"));
        return;
      }
      try {
        const res = await fetch(`/api/sessions/${session}/context`);
        const ctx = await res.json();
        const ctxHtml = `
### 📊 THÔNG SỐ NGỮ CẢNH PHIÊN (CONTEXT)
- **Mã phiên:** \`${ctx.id}\`
- **Cộng sự phụ trách:** **${DOMPurify.sanitize(currentAgent().name)}**
- **Bộ não AI:** \`${ctx.provider}\` (Model: \`${ctx.model}\`)
- **Số tin nhắn:** ${ctx.message_count} tin
- **Tổng dung lượng ký tự:** ${ctx.total_chars.toLocaleString()} ký tự
- **Ước tính Token:** ~${ctx.estimated_tokens.toLocaleString()} tokens
- **Ký ức dài hạn (Brain Memory):** ${ctx.memory_bytes} bytes
        `;
        addMessage("bot", md(ctxHtml));
      } catch (err) {
        addMessage("bot", md("Không lấy được thông số ngữ cảnh: " + err));
      }
      return;
    }

    if (cmd === "compact") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      if (!session) {
        addMessage("bot", md("*(Phiên mới chưa có đủ tin nhắn để thu gọn)*"));
        return;
      }
      setBusy(true);
      const loadingMsg = addMessage("bot", "*(Đang thu gọn và cô đọng ngữ cảnh hội thoại, vui lòng đợi...)*");
      try {
        const res = await fetch(`/api/sessions/${session}/compact`, { method: "POST" });
        const j = await res.json();
        setBusy(false);
        if (j.compacted) {
          loadingMsg.remove();
          await openSession(session);
          addMessage("bot", md("✅ **Đã thu gọn ngữ cảnh thành công!** Phiên chat đã được tóm tắt tinh gọn để giải phóng bộ nhớ."));
        } else {
          loadingMsg.innerHTML = md(j.msg || "Chưa thể compact phiên này.");
        }
      } catch (err) {
        setBusy(false);
        loadingMsg.innerHTML = md("Lỗi khi thu gọn ngữ cảnh: " + err);
      }
      return;
    }

    // Nếu là lệnh /plan
    if (cmd === "plan") {
      $("q").value = "";
      const prompt = `[CHẾ ĐỘ LẬP KẾ HOẠCH - PLAN MODE]\nTrước khi bắt tay vào thực hiện, hãy lập kế hoạch chi tiết từng bước cho yêu cầu sau. Phân tích: căn cứ tiêu chuẩn, dữ liệu đầu vào cần có, các bước thực hiện, điểm kiểm soát (Hold Points) và rủi ro tiềm ẩn:\n\n${arg}`;
      addMessage("user", "").textContent = text;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      setBusy(true);
      ws.send(JSON.stringify({ session: session, text: prompt, agent: selectedAgent }));
      return;
    }

    // Nếu là lệnh /goal
    if (cmd === "goal") {
      $("q").value = "";
      const prompt = `[CHẾ ĐỘ MỤC TIÊU BỀN BỈ - GOAL MODE]\nHãy tập trung giải quyết triệt để và trọn vẹn mục tiêu sau đây, không dừng lại giữa chừng khi bài toán chưa hoàn tất:\n\n${arg}`;
      addMessage("user", "").textContent = text;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      setBusy(true);
      ws.send(JSON.stringify({ session: session, text: prompt, agent: selectedAgent }));
      return;
    }

    // Nếu là /skill <tên_skill> hoặc /<slug_skill>
    const targetSkill = cmd === "skill" ? arg.split(/\s+/)[0] : cmd;
    const skillArg = cmd === "skill" ? arg.slice(targetSkill.length).trim() : arg;
    const isSkillMatch = skillsList.some((s) => s.slug === targetSkill);

    if (isSkillMatch) {
      $("q").value = "";
      const prompt = `[KÍCH HOẠT SKILL: ${targetSkill}]\nHãy đọc và tuân thủ nghiêm ngặt quy trình của skill \`${targetSkill}\` trong thư mục skill để xử lý yêu cầu sau:\n\n${skillArg || 'Áp dụng quy trình chuẩn của skill này để hướng dẫn và triển khai.'}`;
      addMessage("user", "").textContent = text;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      setBusy(true);
      ws.send(JSON.stringify({ session: session, text: prompt, agent: selectedAgent }));
      return;
    }
  }

  // Tin nhắn thông thường
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    alert("Chưa kết nối được với máy chủ Kuro. Vui lòng đợi trong giây lát...");
    return;
  }
  setBusy(true);
  addMessage("user", "").textContent = text;
  $("q").value = "";
  $("q").style.height = "auto";
  ws.send(JSON.stringify({ session: session, text: text, agent: selectedAgent }));
};

// Modal Tạo cộng sự mới
$("btn-create-agent").onclick = () => {
  $("caf").reset();
  $("ca-msg").textContent = "";
  $("create-agent-dialog").showModal();
};
$("ca-close").onclick = () => $("create-agent-dialog").close();

$("caf").onsubmit = async (e) => {
  e.preventDefault();
  const data = {
    name: $("ca-name").value.trim(),
    slug: $("ca-slug").value.trim().toLowerCase(),
    group: $("ca-group").value.trim(),
    role: $("ca-role").value.trim(),
    prompt: $("ca-prompt").value.trim()
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
      msg.textContent = j.detail || "Lỗi tạo cộng sự";
    }
  } catch (err) {
    msg.textContent = "Lỗi kết nối máy chủ";
  }
};

// Cài đặt hệ thống
let modelTheoAi = {};
async function openSettings() {
  const r = await (await fetch("/api/settings")).json();
  modelTheoAi = r.model_theo_ai;
  const sel = $("s-KURO_PROVIDER");
  sel.replaceChildren(
    new Option("- Chưa chọn -", ""),
    ...Object.entries(r.providers).map(([k, v]) => new Option(v.ten, k))
  );
  sel.value = r.settings.KURO_PROVIDER.value || "";
  for (const [k, meta] of Object.entries(r.settings)) {
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
  showProvider();
  $("settings").showModal();
}

function showProvider() {
  const p = $("s-KURO_PROVIDER").value;
  const info = window._providers ? window._providers[p] : null;
  $("s-keyrow").style.display = p === "antigravity" || p === "codex" || !p ? "none" : "block";
}

$("s-KURO_PROVIDER").onchange = () => {
  const m = $("s-KURO_MODEL");
  m.value = m.dataset.orig = modelTheoAi[$("s-KURO_PROVIDER").value || "claude"] || "";
  showProvider();
};

async function saveSettings() {
  const body = {};
  for (const el of $("sf").querySelectorAll("[name]")) {
    if (el.dataset.secret ? el.value || el.dataset.clear : el.value !== el.dataset.orig) body[el.name] = el.value;
  }
  const msg = $("s-msg");
  if (!Object.keys(body).length) {
    msg.className = "";
    msg.textContent = "Chưa có gì thay đổi.";
    return true;
  }
  const r = await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const j = await r.json().catch(() => ({}));
  msg.className = r.ok ? "" : "err";
  msg.textContent = !r.ok ? (j.detail || "Lưu thất bại") : j.restart ? "Đã lưu. Khởi động lại Kuro để áp dụng Telegram." : "Đã lưu. Có hiệu lực từ câu hỏi kế tiếp.";
  if (r.ok) {
    await openSettings();
    loadModels().catch(() => {});
  }
  return r.ok;
}
$("sf").onsubmit = (e) => {
  e.preventDefault();
  saveSettings();
};

$("s-test").onclick = async () => {
  const out = $("s-test-msg");
  if (!$("s-KURO_PROVIDER").value) {
    out.className = "err";
    out.textContent = "Chọn AI trước đã.";
    return;
  }
  if (!(await saveSettings())) return;
  out.className = "";
  out.textContent = "Đang hỏi thử AI (tối đa 90 giây)...";
  $("s-test").disabled = true;
  try {
    const j = await (await fetch("/api/test-ai", { method: "POST" })).json();
    out.className = j.ok ? "ok" : "err";
    out.textContent = j.ok ? `Kết nối được. AI trả lời: "${j.text}"` : `Chưa kết nối được: ${j.error || "không có trả lời"}`;
  } finally {
    $("s-test").disabled = false;
  }
};

$("sf").addEventListener("click", (e) => {
  const k = e.target.dataset.clear;
  if (!k) return;
  const el = $("sf").elements[k];
  el.value = "";
  el.dataset.clear = "1";
  el.placeholder = "Sẽ xóa khi bấm Lưu";
});

$("gear").onclick = $("gear2").onclick = openSettings;
$("s-close").onclick = () => $("settings").close();

// Đổi model nhanh trên thanh điều khiển
async function loadModels() {
  const r = await (await fetch("/api/models")).json();
  const sel = $("model-pick");
  sel.hidden = !r.models.length;
  if (!r.models.length) return;
  const opts = r.models.map((m) => new Option(m.ten, m.id));
  if (!r.models.some((m) => m.id === "")) opts.unshift(new Option("Model mặc định", ""));
  sel.replaceChildren(...opts);
  if (r.current && ![...sel.options].some((o) => o.value === r.current)) sel.add(new Option(r.current, r.current));
  sel.value = r.current;
}

$("model-pick").onchange = async (e) => {
  const r = await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ KURO_MODEL: e.target.value })
  });
  $("state").textContent = r.ok ? "Đã đổi model" : "Đổi model lỗi";
  setTimeout(() => { if (!busy) $("state").textContent = "Sẵn sàng"; }, 2000);
};

// Hiển thị tên Core AI ở góc chân
function showCore(r) {
  const id = r.settings.KURO_PROVIDER.value;
  $("core").textContent = id ? r.providers[id].ten.split(" (")[0] : "Chưa chọn";
}

fetch("/api/settings").then((r) => r.json()).then((r) => {
  window._providers = r.providers;
  showCore(r);
  if (!r.settings.KURO_PROVIDER.value) openSettings();
}).catch(() => {});

// Kiểm tra bản cập nhật mới
async function checkUpdate() {
  const u = await (await fetch("/api/update")).json();
  const box = $("update");
  box.hidden = !u.behind;
  if (!u.behind) return;
  const esc = (t) => DOMPurify.sanitize(t, { ALLOWED_TAGS: [] });
  box.innerHTML = `<b>Có bản mới ${esc(u.latest)}</b>Bạn đang dùng ${esc(u.current)}. Bấm đúp <code>cap-nhat.bat</code> để cập nhật.` +
    (u.notes.length ? `<ul>${u.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>` : "");
}

// ===================== CÂY THƯ MỤC DỰ ÁN (PROJECT EXPLORER) =====================
let fsExpanded = new Set();
let fsShowHidden = false;
let currentPreviewPath = "";
let fsRootData = null;

// Chuyển đổi tab giữa Danh sách Cộng sự và Cây thư mục dự án
function switchSidebarTab(tabName) {
  const isExplorer = tabName === "explorer";
  $("tab-btn-agents").classList.toggle("active", !isExplorer);
  $("tab-btn-explorer").classList.toggle("active", isExplorer);
  $("view-agents").style.display = isExplorer ? "none" : "flex";
  $("view-explorer").style.display = isExplorer ? "flex" : "none";

  if (isExplorer && !fsRootData) {
    refreshFsTree();
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
  if ([".png", ".jpg", ".jpeg", ".ico", ".svg"].includes(ext)) return `🖼️`;
  return `📄`;
}

function formatBytes(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

// Tải và hiển thị cây thư mục
async function refreshFsTree() {
  $("fs-status").textContent = "Đang tải...";
  try {
    const res = await fetch(`/api/fs/tree?sub=&show_hidden=${fsShowHidden}`);
    fsRootData = await res.json();
    renderFsRoot();
    $("fs-status").textContent = "Đã đồng bộ";
  } catch (err) {
    $("fs-status").textContent = "Lỗi đọc thư mục";
    console.error("Lỗi fs tree:", err);
  }
}

function renderFsRoot() {
  const container = $("fs-tree");
  container.innerHTML = "";
  if (!fsRootData || !fsRootData.items) return;

  // Root node: KURO-WORKSPACE
  const rootNode = document.createElement("div");
  rootNode.className = "tree-node";

  const rootItem = document.createElement("div");
  rootItem.className = "tree-item";
  rootItem.innerHTML = `
    <span class="tree-caret open">▶</span>
    <span class="tree-icon">📂</span>
    <strong class="tree-name" style="color:var(--amber);">KURO (DỰ ÁN)</strong>
  `;

  const rootChildren = document.createElement("div");
  rootChildren.className = "tree-children";

  renderFsItems(fsRootData.items, rootChildren);

  rootItem.onclick = () => {
    const isOpen = rootChildren.style.display !== "none";
    rootChildren.style.display = isOpen ? "none" : "flex";
    rootItem.querySelector(".tree-caret").className = "tree-caret " + (isOpen ? "" : "open");
    rootItem.querySelector(".tree-icon").textContent = isOpen ? "📁" : "📂";
  };

  rootNode.appendChild(rootItem);
  rootNode.appendChild(rootChildren);
  container.appendChild(rootNode);
}

function renderFsItems(items, containerEl) {
  containerEl.innerHTML = "";
  const filter = ($("fs-search").value || "").trim().toLowerCase();

  const filtered = items.filter((it) => {
    return !filter || it.name.toLowerCase().includes(filter);
  });

  filtered.forEach((it) => {
    const node = document.createElement("div");
    node.className = "tree-node";

    const itemEl = document.createElement("div");
    itemEl.className = "tree-item";
    itemEl.dataset.path = it.path;

    if (it.is_dir) {
      const isExpanded = fsExpanded.has(it.path);
      itemEl.innerHTML = `
        <span class="tree-caret ${isExpanded ? 'open' : ''}">▶</span>
        <span class="tree-icon">${isExpanded ? '📂' : '📁'}</span>
        <span class="tree-name">${DOMPurify.sanitize(it.name)}</span>
      `;

      const childrenEl = document.createElement("div");
      childrenEl.className = "tree-children";
      childrenEl.style.display = isExpanded ? "flex" : "none";

      itemEl.onclick = async () => {
        const currentlyExpanded = fsExpanded.has(it.path);
        if (currentlyExpanded) {
          fsExpanded.delete(it.path);
          childrenEl.style.display = "none";
          itemEl.querySelector(".tree-caret").className = "tree-caret";
          itemEl.querySelector(".tree-icon").textContent = "📁";
        } else {
          fsExpanded.add(it.path);
          childrenEl.style.display = "flex";
          itemEl.querySelector(".tree-caret").className = "tree-caret open";
          itemEl.querySelector(".tree-icon").textContent = "📂";

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
        openFilePreview(it.path, it.name, it.ext);
      };

      node.appendChild(itemEl);
    }

    containerEl.appendChild(node);
  });
}

// Tìm kiếm tệp trong cây
$("fs-search").oninput = () => {
  if (fsRootData) renderFsRoot();
};

// Toolbar Explorer
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
$("btn-fs-brain").onclick = async () => {
  fsExpanded.add("brains");
  fsExpanded.add("brains/Brain Default");
  switchSidebarTab("explorer");
  await refreshFsTree();
};

// Mở modal xem trước tệp tin
async function openFilePreview(filePath, fileName, ext) {
  currentPreviewPath = filePath;
  $("fp-icon").innerHTML = getFileBadge(ext);
  $("fp-title").textContent = fileName;
  $("fp-path").textContent = filePath;
  $("fp-body").innerHTML = `<div style="color:var(--muted); padding:20px; text-align:center;">Đang đọc nội dung...</div>`;
  $("file-preview-dialog").showModal();

  try {
    const res = await fetch(`/api/fs/file?path=${encodeURIComponent(filePath)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      $("fp-body").innerHTML = `<div style="color:var(--amber); padding:20px;">${DOMPurify.sanitize(err.detail || "Không đọc được tệp tin này.")}</div>`;
      return;
    }
    const data = await res.json();
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

// Đóng modal xem trước
$("btn-fp-close").onclick = () => $("file-preview-dialog").close();

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

// Khởi chạy
connect();
loadSkills();
loadAgents().then(() => {
  loadSessions(selectedAgent);
});
loadModels().catch(() => {});
checkUpdate().catch(() => {});
setInterval(() => checkUpdate().catch(() => {}), 3600e3);

