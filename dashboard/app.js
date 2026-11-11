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
  if (window.innerWidth <= 768) {
    closeAllDrawers();
  }

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
  if (window.innerWidth <= 768) {
    $("history-sidebar").classList.add("open");
    $("agents-sidebar").classList.remove("open");
    const backdrop = $("sidebar-backdrop");
    if (backdrop) backdrop.classList.add("active");
  } else {
    $("history-sidebar").classList.toggle("collapsed");
  }
  if (currentInspectorTab === "context") {
    loadSessionContext(session);
  }
}

function closeHistorySidebar() {
  $("history-sidebar").classList.remove("open");
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

$("btn-toggle-history").onclick = () => {
  if ($("history-sidebar").classList.contains("open")) {
    closeHistorySidebar();
  } else {
    openHistorySidebar();
  }
};
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
  if ($("agents-sidebar").classList.contains("open")) {
    closeAgentsSidebar();
  } else {
    openAgentsSidebar();
  }
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

  // Tin nhắn thông thường
  sendChatMessage(text);
};

function sendChatMessage(displayText, promptToSend) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    alert("Chưa kết nối được với máy chủ Kuro. Vui lòng đợi trong giây lát...");
    return;
  }
  setBusy(true);
  addMessage("user", "").textContent = displayText;
  $("q").value = "";
  $("q").style.height = "auto";
  const wsPath = currentWorkspace && currentWorkspace.path ? currentWorkspace.path : "";
  ws.send(JSON.stringify({
    session: session,
    text: promptToSend || displayText,
    agent: selectedAgent,
    workspace: wsPath
  }));
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
}

function renderRecentWorkspaces() {
  const listEl = $("ws-recent-list");
  if (!listEl) return;
  listEl.innerHTML = "";

  if (!recentWorkspaces || recentWorkspaces.length === 0) {
    listEl.innerHTML = `<div style="color:var(--muted); font-size:12px; padding:12px; text-align:center;">Chưa có lịch sử thư mục dự án nào.</div>`;
    return;
  }

  recentWorkspaces.forEach((ws) => {
    const isAct = currentWorkspace && currentWorkspace.path.toLowerCase() === ws.path.toLowerCase();
    const item = document.createElement("div");
    item.className = "ws-recent-item " + (isAct ? "active" : "");
    item.innerHTML = `
      <div class="ws-recent-left">
        <span style="font-size:18px;">${isAct ? "💼" : "📂"}</span>
        <div class="ws-recent-meta">
          <div class="ws-recent-name">${DOMPurify.sanitize(ws.name || ws.path)}</div>
          <div class="ws-recent-path">${DOMPurify.sanitize(ws.path)}</div>
        </div>
      </div>
      <div class="ws-recent-actions">
        ${isAct ? '<span class="ws-active-badge">Đang mở</span>' : '<button class="btn-ws-switch" type="button">MỞ</button>'}
        <button class="btn-recent-del" type="button" title="Xóa khỏi danh sách gần đây">✕</button>
      </div>
    `;

    item.onclick = async (e) => {
      if (e.target.closest(".btn-recent-del")) {
        e.stopPropagation();
        await removeRecentWorkspace(ws.path);
        return;
      }
      if (!isAct) {
        await switchWorkspace(ws.path, ws.name);
      }
    };

    listEl.appendChild(item);
  });
}

function openWorkspaceDialog() {
  const errEl = $("ws-open-error");
  if (errEl) errEl.style.display = "none";
  $("ws-input-path").value = currentWorkspace.path || "";
  renderRecentWorkspaces();
  $("workspace-dialog").showModal();
}

async function switchWorkspace(path, name) {
  if (!path) return;
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

    // 1. Làm mới cây thư mục tệp tin của dự án mới
    fsExpanded.clear();
    await refreshFsTree();

    // 2. Chuyển đổi và cô lập lịch sử hội thoại của Agent theo dự án mới
    await loadSessions(selectedAgent);

    $("workspace-dialog").close();
  } catch (err) {
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
  rootItem.title = `Thư mục làm việc: ${wsPath}\nBấm để mở/thu gọn`;
  rootItem.innerHTML = `
    <span class="tree-caret open">▶</span>
    <span class="tree-icon">💼</span>
    <strong class="tree-name" style="color:var(--amber); text-transform:uppercase;">${DOMPurify.sanitize(wsName)} (DỰ ÁN)</strong>
  `;

  const rootChildren = document.createElement("div");
  rootChildren.className = "tree-children";

  renderFsItems(fsRootData.items, rootChildren);

  rootItem.onclick = () => {
    const isOpen = rootChildren.style.display !== "none";
    rootChildren.style.display = isOpen ? "none" : "flex";
    rootItem.querySelector(".tree-caret").className = "tree-caret " + (isOpen ? "" : "open");
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

// Toolbar Explorer & Workspace Manager
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

if ($("btn-fs-workspace")) $("btn-fs-workspace").onclick = openWorkspaceDialog;
if ($("ws-banner")) $("ws-banner").onclick = openWorkspaceDialog;
if ($("btn-ws-banner-switch")) $("btn-ws-banner-switch").onclick = (e) => { e.stopPropagation(); openWorkspaceDialog(); };
if ($("btn-fs-workspace-footer")) $("btn-fs-workspace-footer").onclick = openWorkspaceDialog;
if ($("btn-workspace-header")) $("btn-workspace-header").onclick = openWorkspaceDialog;

if ($("btn-close-ws-dialog")) $("btn-close-ws-dialog").onclick = () => $("workspace-dialog").close();
if ($("btn-close-ws-dialog2")) $("btn-close-ws-dialog2").onclick = () => $("workspace-dialog").close();

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

