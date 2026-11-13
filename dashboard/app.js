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

const MASCOT_IMG = `<img src="/kuro_logo_256.png" alt="Kuro Core" style="width:100%; height:100%; object-fit:contain; border-radius:50%; display:block;" />`;

// Icon chuyên môn theo từng Agent
const AGENT_ICONS = {
  "kuro-core": MASCOT_IMG,
  "ky-su-bien-phap": `<svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M2 18h20"></path><path d="M4 18v-4a8 8 0 0 1 16 0v4"></path><path d="M12 4v2"></path><path d="M12 10h.01"></path>
  </svg>`,
  "ky-su-kiem-toan-phu-tro": `<svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>`,
  "ky-su-kiem-toan-ho-mong-cvt": `<svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 21h18"></path><path d="M5 21V7l7-4 7 4v14"></path><path d="M9 10v11"></path><path d="M15 10v11"></path>
  </svg>`,
  "ky-su-qs": `<svg viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="4" y="2" width="16" height="20" rx="2"></rect><line x1="8" y1="6" x2="16" y2="6"></line>
    <line x1="16" y1="14" x2="16" y2="14.01"></line><line x1="12" y1="14" x2="12" y2="14.01"></line><line x1="8" y1="14" x2="8" y2="14.01"></line>
    <line x1="16" y1="18" x2="16" y2="18.01"></line><line x1="12" y1="18" x2="12" y2="18.01"></line><line x1="8" y1="18" x2="8" y2="18.01"></line>
  </svg>`,
  "xac-nhan-thanh-quyet-toan": `<svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
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

function setBusy(b) {
  busy = b;
  document.body.classList.toggle("busy", b);
  $("typing-indicator").style.display = b ? "inline" : "none";
  if (b) mood(null);
  $("state").textContent = b ? "Đang xử lý" : "Sẵn sàng";
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

// Icon và quản lý nhóm cho từng Agent
const GROUP_ICONS = {
  "Hệ thống": "🛡️",
  "Kỹ thuật & Thi công": "🏗️",
  "Quản lý & Hồ sơ": "📋",
  "BIM & Số hóa": "🌐",
  "Tổ đội & Quy trình": "👥",
  "Chuyên môn": "⚙️",
};

function getGroupIcon(groupName) {
  return GROUP_ICONS[groupName] || "📁";
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
  if (!bar) return;
  bar.innerHTML = "";

  // Tạo chip "Tất cả"
  const allChip = document.createElement("button");
  allChip.type = "button";
  allChip.className = "filter-chip" + (currentGroupFilter === "all" ? " active" : "");
  allChip.textContent = `Tất cả (${agents.length})`;
  allChip.onclick = () => {
    currentGroupFilter = "all";
    renderGroupFilterChips();
    renderAgentList();
  };
  bar.appendChild(allChip);

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

  sortedGroups.forEach((grp) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "filter-chip" + (currentGroupFilter === grp ? " active" : "");
    chip.textContent = `${getGroupIcon(grp)} ${grp} (${groupCounts[grp]})`;
    chip.onclick = () => {
      currentGroupFilter = (currentGroupFilter === grp) ? "all" : grp;
      renderGroupFilterChips();
      renderAgentList();
    };
    bar.appendChild(chip);
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
        ${!isSys ? `<button class="agent-group-btn" title="Cấu hình nhóm & Workflow Agent Tổng" type="button" data-config-grp="${encodeURIComponent(grpName)}">✏️</button>` : ""}
      </div>
      <div class="agent-group-meta">
        ${hasWorkflow ? `
          <button type="button" class="agent-group-chat-btn" data-chat-grp="${encodeURIComponent(grpName)}" title="Giao việc và chat trực tiếp với Agent Điều phối Tổng của nhóm này">
            ⚡ AGENT TỔNG
          </button>
        ` : ""}
        <span class="agent-group-count">${groupAgents.length}</span>
        <span class="agent-group-chevron">▼</span>
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
      <div class="agent-avatar">${isTeam ? '👥' : getAgentIcon(agent.slug)}</div>
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
        <div style="font-size:11px; padding:4px 6px; background:rgba(34,211,238,.08); border:1px solid rgba(34,211,238,.2); border-radius:3px; color:var(--cyan-soft); margin-bottom:4px;">
          👥 <b>Điều phối ${agent.members.length} Agent:</b> ${DOMPurify.sanitize(memberNames)}
        </div>
      `;
    }

    html += `
      <div class="agent-details">
        ${teamMembersHtml}
        <p class="agent-desc">${DOMPurify.sanitize(agent.role || 'Trợ lý kỹ sư hạ tầng chuyên trách.')}</p>
        <div class="agent-card-actions">
          ${!agent.is_core ? `
            <button type="button" class="btn-agent-act" data-edit-agent="${agent.slug}" title="Chỉnh sửa thông tin, đổi nhóm hoặc chọn Agent điều phối">✏️ Sửa / Điều phối</button>
            <button type="button" class="btn-agent-act danger" data-delete-agent="${agent.slug}" title="Xóa cộng sự này">🗑️ Xóa</button>
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

  // Mở phiên mới cho Agent này
  newSession();

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

  // Cập nhật model riêng của session
  const sessObj = currentSessions.find(s => s.id === id);
  if (sessObj && sessObj.model !== undefined && $("model-pick")) {
    const val = sessObj.model || "";
    $("model-pick").value = val;
    updateModelPillUI(val);
    renderModelMenuPopover(val);
  } else if ($("model-pick")) {
    fetch(`/api/sessions/${id}/info`).then(r => r.ok ? r.json() : null).then(info => {
      if (info && $("model-pick")) {
        const val = info.model || "";
        $("model-pick").value = val;
        updateModelPillUI(val);
        renderModelMenuPopover(val);
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
  
  // Đồng bộ model mặc định/pending cho phiên mới
  const defaultModelVal = pendingSessionModel || "";
  if ($("model-pick")) $("model-pick").value = defaultModelVal;
  updateModelPillUI(defaultModelVal);
  renderModelMenuPopover(defaultModelVal);

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
              <span>🔧</span>
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
              <span>📝</span>
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
              <span>⚡</span>
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
              <span>🤖</span>
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
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:6px;">
            <span>📄</span>
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
        session = m.id;
        return;
      }

      // 4. Nhận tin nhắn User gửi từ thiết bị khác (PC hoặc ĐT)
      if (m.type === "user_message") {
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
        if (session !== m.session) {
          session = m.session;
        }
        const lastMsg = $("log").querySelector(".msg:last-child");
        if (!lastMsg || !lastMsg.classList.contains("user") || lastMsg.textContent.trim() !== (m.text || "").trim()) {
          addMessage("user", "").textContent = m.text;
        }
        setBusy(true);
        return;
      }

      // 5. Luồng sinh câu trả lời Streaming từ AI
      const a = currentAgent();
      if (!bot && (m.type === "text" || m.type === "tool" || m.type === "error" || m.type === "final" || m.type === "turn_complete")) {
        bot = addMessage("bot", "", a.name.toUpperCase());
        botText = "";
      }
      if (m.type === "text") {
        botText += m.text;
        scheduleBotRender();
      } else if (m.type === "tool") {
        if (bot) {
          bot.insertAdjacentHTML("beforeend", `<span class="tool">${DOMPurify.sanitize(m.name)}</span>`);
        }
      } else if (m.type === "error") {
        botText += `\n\n**Lỗi:** ${m.text}`;
        if (bot) {
          bot.innerHTML = md(botText);
        }
        mood("err");
      } else if (m.type === "final") {
        renderPending = false;
        if (!botText && m.text) {
          botText = m.text;
        }
        if (bot) {
          try {
            bot.innerHTML = md(botText || m.text || "_(Đã hoàn tất)_");
          } catch (err) {
            bot.textContent = botText;
          }
        }
        bot = null;
        setBusy(false);
        if (autoSyncTimer) clearInterval(autoSyncTimer);
        loadSessions(selectedAgent);
        loadSessionContext(session);
        if (!document.body.classList.contains("err")) mood("happy");
      } else if (m.type === "turn_complete") {
        renderPending = false;
        const ans = (m.answer || "").trim();
        if (!session || m.session === session) {
          if (!bot) {
            bot = addMessage("bot", "", a.name.toUpperCase());
          }
          if (ans) {
            botText = ans;
          }
          try {
            bot.innerHTML = md(botText || "_(Đã hoàn tất)_");
          } catch (err) {
            bot.textContent = botText;
          }
          bot = null;
          setBusy(false);
          if (autoSyncTimer) clearInterval(autoSyncTimer);
          loadSessions(selectedAgent);
          loadSessionContext(session);
          if (!document.body.classList.contains("err")) mood("happy");
          $("log").scrollTop = $("log").scrollHeight;
        }
      } else if (m.type === "session_saved") {
        loadSessions(selectedAgent);
      } else if (m.type === "workspace_changed") {
        if (m.active && (!currentWorkspace.path || m.active.toLowerCase() !== currentWorkspace.path.toLowerCase())) {
          currentWorkspace.path = m.active;
          currentWorkspace.name = m.name;
          recentWorkspaces = m.recent || [];
          updateWorkspaceUI();
          refreshFsTree();
          loadSessions(selectedAgent);
        }
      }
      $("log").scrollTop = $("log").scrollHeight;
    } catch (err) {
      console.error("Lỗi xử lý websocket message:", err);
    }
  };
  ws.onopen = () => {
    document.body.classList.add("online");
    $("net").textContent = "Ổn định";
    startWsPing();
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
  setBusy(true);

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
  const chosenModel = (session ? ($("model-pick") ? $("model-pick").value : "") : pendingSessionModel) || "";
  ws.send(JSON.stringify({
    session: session,
    text: (promptToSend || displayText) + attPrompt,
    agent: selectedAgent,
    workspace: wsPath,
    model: chosenModel,
    attachments: sentAttachments
  }));

  startSessionAutoSync(session);

  if (typeof updateChatNavTicks === "function") {
    setTimeout(updateChatNavTicks, 80);
  }
}

// Modal Tạo Agent mới
$("btn-create-agent").onclick = () => {
  $("caf").reset();
  $("ca-msg").textContent = "";
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

let pendingSessionModel = "";

let currentChatMode = "auto"; // auto | plan | goal
let availableModelsList = [];

// Đổi model riêng cho từng cuộc hội thoại (hoặc phiên mới)
async function loadModels() {
  const r = await (await fetch("/api/models")).json();
  const sel = $("model-pick");
  availableModelsList = r.models || [];
  if (sel) {
    sel.hidden = true;
    if (availableModelsList.length) {
      const opts = availableModelsList.map((m) => new Option(m.ten, m.id));
      if (!availableModelsList.some((m) => m.id === "")) opts.unshift(new Option("Model mặc định", ""));
      sel.replaceChildren(...opts);
      if (r.current && ![...sel.options].some((o) => o.value === r.current)) sel.add(new Option(r.current, r.current));
    }
  }

  // Ưu tiên model của session đang mở nếu có
  const sessObj = currentSessions.find(s => s.id === session);
  const activeVal = sessObj && sessObj.model !== undefined ? sessObj.model : (pendingSessionModel || r.current || "");
  if (sel) sel.value = activeVal;
  updateModelPillUI(activeVal);
  renderModelMenuPopover(activeVal);
}

function updateModelPillUI(modelId) {
  const pillLabel = $("model-pill-label");
  if (!pillLabel) return;
  if (!modelId) {
    pillLabel.textContent = "Model mặc định";
    return;
  }
  const match = availableModelsList.find(m => m.id === modelId);
  pillLabel.textContent = match ? match.ten : modelId;
}

function renderModelMenuPopover(activeVal) {
  const container = $("model-menu-items");
  if (!container) return;
  const list = [{ id: "", ten: "Model mặc định" }, ...availableModelsList];
  container.innerHTML = list.map(m => `
    <button type="button" class="model-menu-item ${m.id === activeVal ? 'active' : ''}" data-model-id="${m.id}">
      <span>${escapeHtml(m.ten)}</span>
      ${m.id === activeVal ? '<span class="model-check">✓</span>' : ''}
    </button>
  `).join("");

  container.querySelectorAll(".model-menu-item").forEach(btn => {
    btn.onclick = async () => {
      const chosen = btn.dataset.modelId || "";
      await selectModelForSession(chosen);
      hideBottomPopovers();
    };
  });
}

async function selectModelForSession(chosen) {
  const sel = $("model-pick");
  if (sel) sel.value = chosen;
  updateModelPillUI(chosen);
  renderModelMenuPopover(chosen);

  if (session) {
    try {
      const r = await fetch(`/api/sessions/${session}/model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: chosen })
      });
      const sessObj = currentSessions.find(s => s.id === session);
      if (sessObj) sessObj.model = chosen;
      $("state").textContent = r.ok ? "Đã lưu model cho phiên" : "Lỗi lưu model";
      setTimeout(() => { if (!busy) $("state").textContent = "Sẵn sàng"; }, 2000);
    } catch (err) {
      console.error("Lỗi cập nhật model session:", err);
    }
  } else {
    pendingSessionModel = chosen;
    $("state").textContent = "Đã chọn model phiên mới";
    setTimeout(() => { if (!busy) $("state").textContent = "Sẵn sàng"; }, 2000);
  }
}

function hideBottomPopovers() {
  const attachMenu = $("attach-menu-popover");
  const modelMenu = $("model-menu-popover");
  const modeMenu = $("mode-menu-popover");
  if (attachMenu) attachMenu.style.display = "none";
  if (modelMenu) modelMenu.style.display = "none";
  if (modeMenu) modeMenu.style.display = "none";
}

// Bắt sự kiện click ra ngoài để đóng các popover dưới đáy
document.addEventListener("click", (e) => {
  if (!e.target.closest("#btn-chat-plus") && !e.target.closest("#attach-menu-popover") &&
      !e.target.closest("#btn-model-pill") && !e.target.closest("#model-menu-popover") &&
      !e.target.closest("#btn-mode-pill") && !e.target.closest("#mode-menu-popover")) {
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

if ($("menu-attach-context")) {
  $("menu-attach-context").onclick = () => {
    hideBottomPopovers();
    const q = $("q");
    if (q) {
      q.value = "/context";
      $("f").requestSubmit();
    }
  };
}

if ($("menu-attach-skills")) {
  $("menu-attach-skills").onclick = () => {
    hideBottomPopovers();
    const q = $("q");
    if (q) {
      q.value = "/skill ";
      q.focus();
      q.setSelectionRange(q.value.length, q.value.length);
      handleSlashInput();
    }
  };
}

// Nút chọn Model Pill
const btnModelPill = $("btn-model-pill");
if (btnModelPill) {
  btnModelPill.onclick = (e) => {
    e.stopPropagation();
    const menu = $("model-menu-popover");
    const isVisible = menu && menu.style.display === "flex";
    hideBottomPopovers();
    if (menu && !isVisible) {
      menu.style.display = "flex";
    }
  };
}

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

// Phím tắt Ctrl+U để mở nhanh chọn file
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key.toLowerCase() === "u") {
    e.preventDefault();
    if ($("menu-attach-file")) {
      $("menu-attach-file").click();
    }
  }
});

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
  $("vd-input-ver").value = u.current || "1.5.11";
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
  const val = (input.value || "1.5.11").trim().replace(/^v/i, "");
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
  const u = await checkUpdate(true);
  openVersionDialog();
  $("btn-check-update-manual").textContent = "🔄 Kiểm tra bản mới trên GitHub";
  if (u && !u.update_available) {
    alert(`✓ Hệ thống đã kiểm tra trên GitHub:\nBạn đang sử dụng phiên bản mới nhất (v${u.current || "1.5.10"}).\nNếu muốn kéo lại toàn bộ mã nguồn và cập nhật lại thư viện, bạn có thể bấm nút "⚡ Cập nhật lại từ GitHub".`);
  }
});
$("btn-force-update") && ($("btn-force-update").onclick = () => {
  if (confirm("Chạy cập nhật lại toàn bộ mã nguồn và thư viện từ nhánh main trên GitHub?")) {
    runSelfUpdate();
  }
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

// ==========================================
// WORKSPACE MANAGER (QUẢN LÝ THƯ MỤC DỰ ÁN)
// ==========================================
let currentWorkspace = { path: "", name: "" };
let recentWorkspaces = [];

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
            <span style="font-size:18px;">${isAct ? "💼" : "📂"}</span>
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
          <span style="font-size:13px; flex:none;">${isAct ? "💼" : "📁"}</span>
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

// Tải và hiển thị cây thư mục
async function refreshFsTree() {
  $("fs-status").textContent = "Đang tải...";
  try {
    const res = await fetch(`/api/fs/tree?sub=&show_hidden=${fsShowHidden}`);
    fsRootData = await res.json();
    if (fsRootData.workspace_name) {
      currentWorkspace.name = fsRootData.workspace_name;
      currentWorkspace.path = fsRootData.workspace_path;
      updateWorkspaceUI();
    }
    renderFsRoot();
    $("fs-status").textContent = "Đã đồng bộ";
  } catch (err) {
    $("fs-status").textContent = "Lỗi đọc thư mục";
    console.error("Lỗi fs tree:", err);
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
    <span class="tree-caret open">▶</span>
    <span class="tree-icon">💼</span>
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
        <span class="tree-caret ${isExpanded ? 'open' : ''}">▶</span>
        <span class="tree-icon">${isExpanded ? '📂' : '📁'}</span>
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

async function openFileNative(path) {
  try {
    const res = await fetch("/api/fs/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: path || "" })
    });
    if (res.ok) {
      $("fs-status").textContent = "Đã mở bằng Windows";
      setTimeout(() => { $("fs-status").textContent = "Sẵn sàng"; }, 2000);
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
      $("fs-status").textContent = "Đã mở thư mục trong Explorer";
      setTimeout(() => { $("fs-status").textContent = "Sẵn sàng"; }, 2000);
    } else {
      const err = await res.json().catch(() => ({}));
      alert("Không thể mở Explorer: " + (err.detail || "Lỗi máy chủ"));
    }
  } catch (e) {
    alert("Lỗi mở Explorer: " + e.message);
  }
}

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
  let icon = "📄";
  const e = (ext || "").toLowerCase();
  if (e.includes("xls")) {
    appHint = "Microsoft Excel";
    icon = "📊";
  } else if (e.includes("doc")) {
    appHint = "Microsoft Word";
    icon = "📝";
  } else if (e.includes("ppt")) {
    appHint = "Microsoft PowerPoint";
    icon = "📑";
  } else if (e === ".pdf") {
    appHint = "Trình đọc PDF / Adobe Acrobat";
    icon = "📕";
  } else if (e === ".dwg" || e === ".dxf") {
    appHint = "AutoCAD";
    icon = "📐";
  } else if (e === ".zip" || e === ".rar" || e === ".7z") {
    appHint = "WinRAR / 7-Zip";
    icon = "📦";
  }

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
// THANH VẠCH ĐIỀU HƯỚNG CÂU HỎI & NÚT CUỘN XUỐNG ĐÁY (THEO UI JAVIS)
// ========================================================
let navPopoverTimer = null;

function updateChatNavTicks() {
  const rail = $("chat-nav-rail");
  const log = $("log");
  const popover = $("chat-nav-popover");
  if (!rail || !log) return;

  const userMsgs = Array.from(log.querySelectorAll(".msg.user"));
  if (userMsgs.length <= 1) {
    rail.style.display = "none";
    if (popover) popover.style.display = "none";
    return;
  }

  rail.style.display = "block";
  rail.innerHTML = "";

  const logHeight = Math.max(log.scrollHeight, 1);

  userMsgs.forEach((msgEl, idx) => {
    const tick = document.createElement("div");
    tick.className = "chat-nav-tick";
    tick.dataset.idx = idx;

    const pct = Math.min(Math.max((msgEl.offsetTop / logHeight) * 100, 2), 97);
    tick.style.top = `${pct}%`;

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

    rail.appendChild(tick);
  });
}

function showChatNavPopover(centerIdx, userMsgs, targetTick) {
  clearTimeout(navPopoverTimer);
  const popover = $("chat-nav-popover");
  const rail = $("chat-nav-rail");
  if (!popover || !rail) return;

  const maxItems = 15;
  const total = userMsgs.length;
  let start = Math.max(0, centerIdx - Math.floor(maxItems / 2));
  let end = Math.min(total, start + maxItems);
  if (end - start < maxItems) {
    start = Math.max(0, end - maxItems);
  }

  const itemsHtml = [];
  for (let i = start; i < end; i++) {
    const el = userMsgs[i];
    const text = (el.textContent || "").trim().replace(/^BẠN \(KỸ SƯ\)\s*/i, "").replace(/\s+/g, " ");
    const isCenter = (i === centerIdx);
    itemsHtml.push(`
      <div class="chat-nav-item ${isCenter ? 'highlighted' : ''}" data-idx="${i}" title="${escapeHtml(text)}">
        ${i + 1}. ${escapeHtml(text.slice(0, 50))}${text.length > 50 ? '...' : ''}
      </div>
    `);
  }

  popover.innerHTML = `
    <div class="chat-nav-popover-header">
      <span>CÂU HỎI TRONG ĐOẠN NÀY (${start + 1}-${end}/${total})</span>
      <span style="font-size:10px; color:var(--muted); font-family:var(--body);">Bấm để nhảy</span>
    </div>
    <div class="chat-nav-list">${itemsHtml.join("")}</div>
  `;

  const tickRect = targetTick.getBoundingClientRect();
  const popTop = Math.max(10, Math.min(tickRect.top - 60, window.innerHeight - 420));
  popover.style.top = `${popTop}px`;
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
  }, 220);
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

// Khởi chạy
connect();
loadSkills();
loadWorkspaces().then(async () => {
  await loadAgents();
  await loadSessions(selectedAgent);
  await refreshFsTree();
});
loadModels().catch(() => {});
checkUpdate().catch(() => {});
setInterval(() => checkUpdate().catch(() => {}), 3600e3);

