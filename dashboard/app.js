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
    if (!session && currentSessions.length > 0) {
      await openSession(currentSessions[0].id);
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
  loadSessionContext(id);

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
  loadSessionContext(null);
  $("q").focus();
}

$("new").onclick = newSession;
$("btn-new-conv").onclick = newSession;

// Đóng mở cột Lịch sử & Ngữ cảnh
$("btn-toggle-history").onclick = () => {
  $("history-sidebar").classList.toggle("collapsed");
  if (!$("history-sidebar").classList.contains("collapsed") && currentInspectorTab === "context") {
    loadSessionContext(session);
  }
};
$("btn-close-history").onclick = () => {
  $("history-sidebar").classList.add("collapsed");
};

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
    $("ctx-env-model").textContent = env.model || $("model-pick").value || "Mặc định";

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
      el.className = "ctx-bar-seg";
      el.style.width = Math.max(1, seg.percent) + "%";
      el.style.backgroundColor = seg.color || "#475569";
      el.title = `${seg.name}: ${formatTokens(seg.tokens)} (${seg.percent}%)`;
      bar.appendChild(el);
    });

    // 4. Render Breakdown List
    const list = $("ctx-breakdown-list");
    list.innerHTML = "";
    barSegments.forEach(key => {
      const seg = breakdown[key];
      if (!seg) return;
      const row = document.createElement("div");
      row.className = "ctx-break-row";
      row.innerHTML = `
        <div class="ctx-break-left">
          <span class="ctx-color-dot" style="background:${esc(seg.color)};"></span>
          <span class="ctx-break-name">${esc(seg.name)}</span>
        </div>
        <div class="ctx-break-right">
          <span class="ctx-break-tokens">${formatTokens(seg.tokens)}</span>
          <span class="ctx-break-pct">${seg.percent}%</span>
        </div>
      `;
      list.appendChild(row);
    });

    // 5. Cập nhật các bộ đếm
    const counts = data.counts || {};
    $("ctx-count-mcp").textContent = counts.mcp_tools_count || 0;
    $("ctx-count-mem").textContent = counts.memory_files_count || 0;
    $("ctx-count-skills").textContent = counts.skills_count || 0;
    $("ctx-count-agents").textContent = counts.custom_agents_count || 0;

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
        const ext = art.name.split(".").pop().toUpperCase();
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:6px;">
            <span>📄</span>
            <span class="ctx-art-name">${esc(art.name)}</span>
          </div>
          <span class="ctx-art-ext">${esc(ext)}</span>
        `;
        item.onclick = () => previewFile(art.path, art.name);
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
  $("agents-sidebar").classList.toggle("collapsed");
};

// Kết nối WebSocket
function connect() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${proto}//${location.host}/ws`);
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
      loadSessionContext(session);
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
  { cmd: "/version", name: "/version", desc: "Xem và đặt số phiên bản Kuro OS hiện tại", needArg: false },
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
      const cur = $("model-pick").value || "Mặc định";
      addMessage("bot", md(`Model AI hiện đang cấu hình: **${cur}**. Bạn có thể đổi nhanh tại thanh chọn model góc trên bên phải.`));
      return;
    }

    if (cmd === "context") {
      $("q").value = "";
      addMessage("user", "").textContent = text;
      $("history-sidebar").classList.remove("collapsed");
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

// ===================== QUẢN LÝ PHIÊN BẢN & CẬP NHẬT (THEO KIẾN TRÚC JAVIS OS) =====================
let versionData = {
  current: "1.4.0",
  latest: "1.4.0",
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
    const curText = "v" + (u.current || "1.4.0");
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
  const u = versionData || { current: "1.4.0", latest: "1.4.0", update_available: false, notes: [] };
  const esc = (t) => DOMPurify.sanitize(t, { ALLOWED_TAGS: [] });

  $("vd-current-ver").textContent = "v" + (u.current || "1.4.0");
  $("vd-latest-ver").textContent = "v" + (u.latest || u.current || "1.4.0");
  $("vd-input-ver").value = u.current || "1.4.0";
  $("vd-save-status").textContent = "";
  $("vd-save-status").className = "save-status-msg";

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

function bumpVersion(type) {
  const input = $("vd-input-ver");
  const val = (input.value || "1.4.0").trim().replace(/^v/i, "");
  const parts = val.split(".").map((x) => parseInt(x, 10) || 0);
  while (parts.length < 3) parts.push(0);

  if (type === "patch") {
    parts[2] += 1;
  } else if (type === "minor") {
    parts[1] += 1;
    parts[2] = 0;
  }
  input.value = parts.join(".");
}

async function saveVersionNumber() {
  const input = $("vd-input-ver");
  const statusMsg = $("vd-save-status");
  const val = (input.value || "").trim().replace(/^v/i, "");

  if (!/^\d+(\.\d+)*$/.test(val)) {
    statusMsg.textContent = "Số phiên bản không hợp lệ (ví dụ đúng: 1.4.1)";
    statusMsg.className = "save-status-msg err";
    return;
  }

  statusMsg.textContent = "Đang lưu số phiên bản...";
  statusMsg.className = "save-status-msg";

  try {
    const res = await fetch("/api/version", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: val }),
    });
    const d = await res.json();
    if (res.ok) {
      statusMsg.textContent = `Đã lưu thành công số phiên bản v${d.version}!`;
      statusMsg.className = "save-status-msg ok";
      await checkUpdate(false);
      $("vd-current-ver").textContent = "v" + d.version;
    } else {
      statusMsg.textContent = d.detail || "Lỗi khi lưu phiên bản";
      statusMsg.className = "save-status-msg err";
    }
  } catch (e) {
    statusMsg.textContent = "Lỗi kết nối máy chủ: " + e.message;
    statusMsg.className = "save-status-msg err";
  }
}

async function runSelfUpdate() {
  if (!confirm("Bắt đầu cập nhật Kuro lên phiên bản mới? Hệ thống sẽ kéo mã nguồn và tự động khởi động lại dịch vụ.")) return;

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
  await checkUpdate(true);
  openVersionDialog();
  $("btn-check-update-manual").textContent = "🔄 Kiểm tra bản mới trên GitHub";
});
$("btn-save-version") && ($("btn-save-version").onclick = saveVersionNumber);
$("btn-bump-patch") && ($("btn-bump-patch").onclick = () => bumpVersion("patch"));
$("btn-bump-minor") && ($("btn-bump-minor").onclick = () => bumpVersion("minor"));
$("btn-start-update") && ($("btn-start-update").onclick = runSelfUpdate);

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

// ===================== ĐỒNG BỘ ĐIỆN THOẠI & REMOTE CONTROL =====================
let currentRemoteData = null;

async function showRemoteDialog() {
  const dlg = $("remote-dialog");
  if (!dlg) return;

  const qrImg = $("remote-qr-img");
  const priUrl = $("remote-primary-url");
  const pillsBox = $("remote-ip-pills");

  if (priUrl) priUrl.textContent = "Đang kiểm tra địa chỉ mạng...";
  if (pillsBox) pillsBox.innerHTML = "";

  dlg.showModal();

  try {
    const res = await fetch("/api/network/remote");
    if (!res.ok) throw new Error("Không lấy được thông tin mạng");
    const data = await res.json();
    currentRemoteData = data;

    if (qrImg && data.qr_code) {
      qrImg.src = data.qr_code;
    }
    if (priUrl) {
      priUrl.textContent = data.primary_url || `http://${data.primary_ip}:${data.port}`;
    }

    if (pillsBox && Array.isArray(data.all_ips)) {
      pillsBox.innerHTML = "";
      data.all_ips.forEach((item) => {
        const pill = document.createElement("button");
        pill.type = "button";
        pill.className = "ip-pill";
        pill.title = `Bấm để tạo mã QR cho ${item.ip} (${item.type})`;
        pill.innerHTML = `<span>🌐</span> <b>${DOMPurify.sanitize(item.ip)}</b> <small style="color:var(--muted);">(${DOMPurify.sanitize(item.type)})</small>`;
        pill.onclick = async () => {
          if (priUrl) priUrl.textContent = item.url;
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

function closeRemoteDialog() {
  const dlg = $("remote-dialog");
  if (dlg) dlg.close();
}

$("btn-remote-header") && ($("btn-remote-header").onclick = showRemoteDialog);
$("ctx-env-remote-row") && ($("ctx-env-remote-row").onclick = showRemoteDialog);
$("btn-close-remote-dialog") && ($("btn-close-remote-dialog").onclick = closeRemoteDialog);
$("btn-close-remote-dialog2") && ($("btn-close-remote-dialog2").onclick = closeRemoteDialog);

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

// Khởi chạy
connect();
loadSkills();
loadAgents().then(() => {
  loadSessions(selectedAgent);
});
loadModels().catch(() => {});
checkUpdate().catch(() => {});
setInterval(() => checkUpdate().catch(() => {}), 3600e3);

