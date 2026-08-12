const setupEl = document.getElementById("setup");
const draftUi = document.getElementById("draft-ui");
const setupForm = document.getElementById("setup-form");
const setupBanner = document.getElementById("setup-banner");
const nameInput = document.getElementById("user-name");
const slotSelect = document.getElementById("user-slot");
const rosterSelect = document.getElementById("roster-preset");
const rosterDesc = document.getElementById("roster-desc");
const resumeBtn = document.getElementById("resume");
const search = document.getElementById("search");
const form = document.getElementById("search-form");
const playerRows = document.getElementById("player-rows");
const filterPos = document.getElementById("filter-pos");
const filterTeam = document.getElementById("filter-team");
const filterSort = document.getElementById("filter-sort");
const boardEl = document.getElementById("board");
const boardWrap = document.getElementById("board-wrap");
const layoutEl = document.getElementById("layout");
const takeEl = document.getElementById("take");
const takeBody = document.getElementById("take-body");
const metaEl = document.getElementById("pick-meta");
const draftSub = document.getElementById("draft-sub");
const banner = document.getElementById("banner");
const clockEl = document.getElementById("clock");
const gradeModal = document.getElementById("grade-modal");
const gradeBody = document.getElementById("grade-body");
const gradeMethod = document.getElementById("grade-method");
const showGradeBtn = document.getElementById("show-grade");

let draftId = localStorage.getItem("draftId");
let state = null;
let recs = [];
let grade = null;
let hits = [];
let active = 0;
let deadline = 0;
let clockTimer = null;
let cpuBusy = false;
let autopicking = false;
let takeCollapsed = localStorage.getItem("takeCollapsed") === "1";
let presets = [];

for (let i = 1; i <= 10; i++) {
  const opt = document.createElement("option");
  opt.value = String(i);
  opt.textContent = `${i} (${i}.01 / ${11 - i}.10)`;
  slotSelect.appendChild(opt);
}
nameInput.value = localStorage.getItem("userName") || "";
slotSelect.value = localStorage.getItem("userSlot") || "1";

function showBanner(el, msg) {
  el.textContent = msg || "";
  el.classList.toggle("hidden", !msg);
}

async function api(path, opts) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function showDraft() {
  setupEl.classList.add("hidden");
  draftUi.classList.remove("hidden");
  applyTakeCollapse();
}

function showSetup() {
  stopClock();
  gradeModal.classList.add("hidden");
  setupEl.classList.remove("hidden");
  draftUi.classList.add("hidden");
  resumeBtn.classList.toggle("hidden", !localStorage.getItem("draftId"));
  nameInput.focus();
}

function applyTakeCollapse() {
  layoutEl.classList.toggle("take-collapsed", takeCollapsed);
  localStorage.setItem("takeCollapsed", takeCollapsed ? "1" : "0");
}

function setTakeCollapsed(v) {
  takeCollapsed = v;
  applyTakeCollapse();
}

function formatClock(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function stopClock() {
  if (clockTimer) clearInterval(clockTimer);
  clockTimer = null;
  deadline = 0;
  clockEl.hidden = true;
}

function startClock() {
  stopClock();
  if (!state || state.complete || !state.is_user_turn) return;
  const secs = state.pick_clock_seconds || 90;
  deadline = Date.now() + secs * 1000;
  clockEl.hidden = false;
  tickClock();
  clockTimer = setInterval(tickClock, 200);
}

function tickClock() {
  const left = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  clockEl.textContent = formatClock(left);
  clockEl.classList.toggle("warn", left <= 15);
  if (left <= 0) {
    stopClock();
    timeoutAutopick();
  }
}

function applyPayload(payload) {
  state = payload.state;
  recs = payload.recommend || [];
  grade = payload.grade || null;
  draftId = state.draft_id;
  localStorage.setItem("draftId", draftId);
  if (state.is_user_turn) setTakeCollapsed(false);
  else if (!state.complete) setTakeCollapsed(true);
  render();
  if (grade) {
    showGradeBtn.classList.remove("hidden");
    if (state.complete) openGrade();
  } else {
    showGradeBtn.classList.add("hidden");
  }
}

function pickLabel() {
  if (!state) return "No draft yet";
  if (state.complete) return "Draft complete";
  if (state.is_user_turn) return `Pick ${state.current_pick} · YOUR PICK`;
  const label = (state.team_labels || [])[state.current_team - 1] || `Team ${state.current_team}`;
  return `Pick ${state.current_pick} · ${label} is picking`;
}

function renderBoard() {
  boardEl.innerHTML = "";
  if (!state) return;
  boardEl.style.gridTemplateColumns = `2.2rem repeat(${state.n_teams}, minmax(6.4rem, 1fr))`;

  const blank = document.createElement("div");
  blank.className = "cell head corner";
  boardEl.appendChild(blank);
  for (let t = 1; t <= state.n_teams; t++) {
    const h = document.createElement("div");
    h.className = "cell head team" + (t === state.user_slot ? " you" : "");
    h.textContent = (state.team_labels || [])[t - 1] || `T${t}`;
    boardEl.appendChild(h);
  }
  let currentCell = null;
  for (let r = 0; r < state.n_rounds; r++) {
    const rh = document.createElement("div");
    rh.className = "cell head round";
    rh.textContent = `R${r + 1}`;
    boardEl.appendChild(rh);
    for (let t = 0; t < state.n_teams; t++) {
      const cell = document.createElement("div");
      const isCurrent =
        !state.complete &&
        state.current_round === r + 1 &&
        state.current_team === t + 1;
      cell.className =
        "cell" +
        (t + 1 === state.user_slot ? " you" : "") +
        (isCurrent ? " current" : "");
      const pick = state.board[r][t];
      if (pick) {
        cell.innerHTML = `<span class="pos ${pick.position}">${pick.position}</span>
          <span class="nm" title="${pick.name}">${pick.name}</span>
          <span class="meta">${pick.overall}</span>`;
      } else if (isCurrent) {
        cell.innerHTML = `<span class="meta">on the clock</span>`;
      }
      if (isCurrent) currentCell = cell;
      boardEl.appendChild(cell);
    }
  }
  if (currentCell) {
    requestAnimationFrame(() => {
      currentCell.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
    });
  }
}

function renderTake() {
  if (!state || state.complete) {
    takeBody.innerHTML = `<p class="muted">Draft complete. Open the scorecard for grades.</p>`;
    return;
  }
  if (!state.is_user_turn) {
    takeBody.innerHTML = `<p class="muted">CPU is picking…</p>`;
    return;
  }
  if (!recs.length) {
    takeBody.innerHTML = `<p class="muted">No remaining players ranked.</p>`;
    return;
  }
  const top = recs[0];
  const rest = recs
    .slice(1)
    .map(
      (p) =>
        `<li><span class="pos ${p.position}">${p.position}</span> ${p.name}
         <div class="muted">${p.marginal != null ? `Δ ${fmt(p.marginal)} · ` : ""}ADP ${fmt(p.adp_espn)} · ECR ${fmt(p.ecr_fp_ppr)}</div></li>`
    )
    .join("");
  const marg =
    top.marginal != null
      ? `Δ ${fmt(top.marginal)} starter pts · ${fmt(top.lineup_before)} → ${fmt(top.lineup_after)}`
      : "";
  takeBody.innerHTML = `
    <p class="primary"><span class="pos ${top.position}">${top.position}</span> ${top.name}</p>
    <p class="muted">${top.why || ""}</p>
    <p class="muted">${marg}${marg ? " · " : ""}ADP ${fmt(top.adp_espn)} · ECR ${fmt(top.ecr_fp_ppr)}</p>
    <h2 style="margin-top:0.9rem">Next</h2>
    <ol>${rest}</ol>`;
}

function fmt(v) {
  if (v == null || v === "") return "—";
  return typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(1)) : v;
}

function renderPlayerTable() {
  if (!hits.length) {
    playerRows.innerHTML = `<tr><td colspan="8" class="muted">No remaining players match.</td></tr>`;
    return;
  }
  playerRows.innerHTML = hits
    .map((p, i) => {
      return `<tr class="${i === active ? "active" : ""}" data-i="${i}">
        <td>${i === active ? "›" : ""}</td>
        <td>${p.name}</td>
        <td><span class="pos ${p.position}">${p.position || ""}</span></td>
        <td>${p.team || ""}</td>
        <td class="num">${fmt(p.adp)}</td>
        <td class="num">${fmt(p.ecr)}</td>
        <td class="num">${fmt(p.season_points)}</td>
        <td>${p.injury_status && p.injury_status !== "ACTIVE" ? p.injury_status : ""}</td>
      </tr>`;
    })
    .join("");
}

function populateTeamsFromHits() {
  const current = filterTeam.value;
  const existing = new Set([...filterTeam.options].map((o) => o.value).filter(Boolean));
  for (const t of [...new Set(hits.map((p) => p.team).filter(Boolean))].sort()) {
    if (existing.has(t)) continue;
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    filterTeam.appendChild(opt);
  }
  filterTeam.value = current;
}

function render() {
  metaEl.textContent = pickLabel();
  const rosterLabel = state?.roster?.label ? ` · ${state.roster.label}` : "";
  draftSub.textContent = `V0 · 10-team PPR snake · ${state?.n_rounds || "?"} rounds${rosterLabel}`;
  search.disabled = !state || !state.is_user_turn || state.complete;
  filterPos.disabled = search.disabled;
  filterTeam.disabled = search.disabled;
  filterSort.disabled = search.disabled;
  search.classList.toggle("search-disabled", search.disabled);
  search.placeholder = state && state.is_user_turn ? "Type a player, then Enter" : "Waiting for CPU…";
  // Hide K filter option if league has no K
  const kOpt = [...filterPos.options].find((o) => o.value === "K");
  if (kOpt && state?.roster?.slots) {
    kOpt.hidden = !state.roster.slots.K;
  }
  renderBoard();
  renderTake();
  if (state && state.is_user_turn && !state.complete) search.focus();
}

function openGrade() {
  if (!grade) return;
  gradeMethod.textContent = grade.method || "";
  gradeBody.innerHTML = `
    <p><strong>${grade.user.label}</strong> finished <strong>#${grade.user.rank}</strong>
    with ${grade.user.projected_points} projected pts
    (ADP value ${grade.user.adp_value >= 0 ? "+" : ""}${grade.user.adp_value}).</p>
    <table class="grade-table">
      <thead><tr><th>#</th><th>Team</th><th class="num">Proj pts</th><th class="num">ADP value</th></tr></thead>
      <tbody>
        ${grade.teams
          .map(
            (t) => `<tr class="${t.is_user ? "you-row" : ""}">
              <td>${t.rank}</td>
              <td>${t.label}</td>
              <td class="num">${t.projected_points}</td>
              <td class="num">${t.adp_value >= 0 ? "+" : ""}${t.adp_value}</td>
            </tr>`
          )
          .join("")}
      </tbody>
    </table>`;
  gradeModal.classList.remove("hidden");
}

async function afterStateChange() {
  render();
  if (!state || state.complete) {
    stopClock();
    if (state?.complete) setTakeCollapsed(true);
    await refreshSearch();
    return;
  }
  if (state.is_user_turn) {
    startClock();
    await refreshSearch();
    return;
  }
  stopClock();
  await refreshSearch();
  await cpuLoop();
}

async function cpuLoop() {
  if (cpuBusy) return;
  cpuBusy = true;
  try {
    while (state && !state.complete && !state.is_user_turn) {
      await sleep(450);
      const payload = await api(`/api/drafts/${draftId}/cpu`, { method: "POST" });
      applyPayload(payload);
      render();
    }
    if (state && state.is_user_turn && !state.complete) {
      startClock();
      await refreshSearch();
    }
  } catch (err) {
    showBanner(banner, err.message);
  } finally {
    cpuBusy = false;
  }
}

async function refreshSearch() {
  if (!draftId) return;
  const q = search.value.trim();
  const params = new URLSearchParams({
    q,
    position: filterPos.value || "ALL",
    team: filterTeam.value || "",
    sort: filterSort.value || "adp",
    limit: "50",
  });
  const data = await api(`/api/drafts/${draftId}/search?${params}`);
  hits = data.results || [];
  active = 0;
  populateTeamsFromHits();
  renderPlayerTable();
}

async function pickCurrent() {
  if (!draftId || !state || !state.is_user_turn) return;
  const chosen = hits[active];
  const body = chosen
    ? { player_id: chosen.player_id }
    : { query: search.value.trim() };
  if (!body.player_id && !body.query) return;
  try {
    stopClock();
    const payload = await api(`/api/drafts/${draftId}/picks`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    showBanner(banner, "");
    search.value = "";
    hits = [];
    renderPlayerTable();
    applyPayload(payload);
    await afterStateChange();
  } catch (err) {
    showBanner(banner, err.message);
    startClock();
  }
}

async function timeoutAutopick() {
  if (autopicking || !draftId || !state || !state.is_user_turn) return;
  autopicking = true;
  try {
    const payload = await api(`/api/drafts/${draftId}/autopick`, { method: "POST" });
    const last = payload.state.picks[payload.state.picks.length - 1];
    showBanner(banner, `Clock expired — autodrafted ${last ? last.name : "the recommended player"}`);
    search.value = "";
    hits = [];
    renderPlayerTable();
    applyPayload(payload);
    await afterStateChange();
  } catch (err) {
    showBanner(banner, err.message);
  } finally {
    autopicking = false;
  }
}

function updateRosterDesc() {
  const preset = presets.find((p) => p.id === rosterSelect.value);
  rosterDesc.textContent = preset
    ? `${preset.description} · ${preset.n_rounds} draft rounds`
    : "";
}

async function newDraftFromSetup() {
  const user_name = nameInput.value.trim();
  const user_slot = Number(slotSelect.value) || 1;
  const roster_preset = rosterSelect.value || "league_default";
  if (!user_name) {
    showBanner(setupBanner, "Enter your name.");
    return;
  }
  localStorage.setItem("userName", user_name);
  localStorage.setItem("userSlot", String(user_slot));
  localStorage.setItem("rosterPreset", roster_preset);
  try {
    const payload = await api("/api/drafts", {
      method: "POST",
      body: JSON.stringify({ user_slot, user_name, roster_preset }),
    });
    showBanner(setupBanner, "");
    showBanner(banner, "");
    applyPayload(payload);
    showDraft();
    await afterStateChange();
  } catch (err) {
    showBanner(setupBanner, err.message);
  }
}

async function resumeDraft() {
  const id = localStorage.getItem("draftId");
  if (!id) return;
  try {
    const payload = await api(`/api/drafts/${id}`);
    applyPayload(payload);
    showDraft();
    await afterStateChange();
  } catch {
    localStorage.removeItem("draftId");
    draftId = null;
    showBanner(setupBanner, "Last draft is gone. Start a new one.");
    resumeBtn.classList.add("hidden");
  }
}

async function undo() {
  if (!draftId) return;
  try {
    stopClock();
    const payload = await api(`/api/drafts/${draftId}/undo`, { method: "POST" });
    showBanner(banner, "");
    applyPayload(payload);
    await afterStateChange();
  } catch (err) {
    showBanner(banner, err.message);
  }
}

setupForm.addEventListener("submit", (e) => {
  e.preventDefault();
  newDraftFromSetup();
});
resumeBtn.addEventListener("click", resumeDraft);
rosterSelect.addEventListener("change", updateRosterDesc);
document.getElementById("new-draft").addEventListener("click", () => {
  localStorage.removeItem("draftId");
  draftId = null;
  state = null;
  grade = null;
  showSetup();
});

form.addEventListener("submit", (e) => {
  e.preventDefault();
  pickCurrent();
});

function onFilterChange() {
  refreshSearch().catch((err) => showBanner(banner, err.message));
}
search.addEventListener("input", onFilterChange);
filterPos.addEventListener("change", onFilterChange);
filterTeam.addEventListener("change", onFilterChange);
filterSort.addEventListener("change", onFilterChange);

search.addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (hits.length) active = (active + 1) % hits.length;
    renderPlayerTable();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    if (hits.length) active = (active - 1 + hits.length) % hits.length;
    renderPlayerTable();
  } else if (e.key === "Escape") {
    search.value = "";
    hits = [];
    renderPlayerTable();
  }
});

playerRows.addEventListener("mousedown", (e) => {
  const tr = e.target.closest("tr[data-i]");
  if (!tr) return;
  active = Number(tr.dataset.i);
  pickCurrent();
});

document.getElementById("undo").addEventListener("click", undo);
document.getElementById("toggle-take").addEventListener("click", () => setTakeCollapsed(!takeCollapsed));
document.getElementById("collapse-take").addEventListener("click", () => setTakeCollapsed(true));
takeEl.addEventListener("click", () => {
  if (takeCollapsed) setTakeCollapsed(false);
});
showGradeBtn.addEventListener("click", openGrade);
document.getElementById("close-grade").addEventListener("click", () => gradeModal.classList.add("hidden"));

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
    e.preventDefault();
    undo();
  }
  if (e.key === "]" && !e.ctrlKey && !e.metaKey && document.activeElement !== search && document.activeElement !== nameInput) {
    setTakeCollapsed(!takeCollapsed);
  }
});

(async function init() {
  try {
    const st = await api("/api/status");
    presets = st.roster_presets || [];
    rosterSelect.innerHTML = "";
    for (const p of presets) {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.label;
      rosterSelect.appendChild(opt);
    }
    rosterSelect.value = localStorage.getItem("rosterPreset") || "league_default";
    updateRosterDesc();
    if (!st.players) {
      showBanner(setupBanner, "No players in the database. Run: python -m draftopt.ingest");
    }
  } catch {
    showBanner(setupBanner, "Cannot reach the draft server. Run: python -m draftopt.serve --port 8001");
  }
  resumeBtn.classList.toggle("hidden", !localStorage.getItem("draftId"));
  nameInput.focus();
})();
