const setupEl = document.getElementById("setup");
const draftUi = document.getElementById("draft-ui");
const setupForm = document.getElementById("setup-form");
const setupBanner = document.getElementById("setup-banner");
const nameInput = document.getElementById("user-name");
const slotSelect = document.getElementById("user-slot");
const orderModeSelect = document.getElementById("order-mode");
const slotPicker = document.getElementById("slot-picker");
const shuffleMySlotBtn = document.getElementById("shuffle-my-slot");
const liveSimHint = document.getElementById("live-sim-hint");
const leaguePanel = document.getElementById("league-panel");
const seatList = document.getElementById("seat-list");
const clearSeatsBtn = document.getElementById("clear-seats");
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
const cpuThisPickBtn = document.getElementById("cpu-this-pick");
const undoBtn = document.getElementById("undo");
const dumpCaseBtn = document.getElementById("dump-case");
const logDisagreeBtn = document.getElementById("log-disagree");

let draftId = localStorage.getItem("draftId");
let state = null;
let recs = [];
let overlay = null;
let grade = null;
let hits = [];
let active = 0;
let deadline = 0;
let clockTimer = null;
let cpuBusy = false;
let autopicking = false;
let takeCollapsed = localStorage.getItem("takeCollapsed") === "1";
let presets = [];
let nTeams = 12;

function fillSlotOptions(n) {
  nTeams = n;
  const prev = slotSelect.value || localStorage.getItem("userSlot") || "1";
  slotSelect.innerHTML = "";
  for (let i = 1; i <= n; i++) {
    const opt = document.createElement("option");
    opt.value = String(i);
    const r2 = n + 1 - i;
    opt.textContent = `${i} (${i}.01 / 2.${String(r2).padStart(2, "0")})`;
    slotSelect.appendChild(opt);
  }
  const ok = [...slotSelect.options].some((o) => o.value === prev);
  slotSelect.value = ok ? prev : "1";
}

fillSlotOptions(12);
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
  const secs = state.pick_clock_seconds || 60;
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
  overlay = payload.overlay || null;
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

function isLiveSim() {
  return state?.pick_mode === "live_sim";
}

function canHumanPick() {
  return Boolean(state?.can_human_pick);
}

function pickLabel() {
  if (!state) return "No draft yet";
  if (state.complete) return "Draft complete";
  if (state.is_user_turn) return `Pick ${state.current_pick} · YOUR PICK`;
  const label = (state.team_labels || [])[state.current_team - 1] || `Team ${state.current_team}`;
  if (isLiveSim()) return `Pick ${state.current_pick} · enter ${label}'s pick`;
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
    if (isLiveSim()) {
      const label = (state.team_labels || [])[state.current_team - 1] || `Team ${state.current_team}`;
      takeBody.innerHTML = `<p class="muted">Live sim — search and enter <strong>${label}</strong>'s pick. Your TAKE opens on your turn.</p>`;
      return;
    }
    takeBody.innerHTML = `<p class="muted">CPU is picking…</p>`;
    return;
  }
  if (!recs.length) {
    takeBody.innerHTML = `<p class="muted">No remaining players ranked.</p>`;
    return;
  }
  const top = recs[0];
  const ovRec = (overlay?.recommend || []).find((r) => r.player_id === top.player_id) || {};
  const rest = recs
    .slice(1)
    .map((p) => {
      const o = (overlay?.recommend || []).find((r) => r.player_id === p.player_id) || {};
      const fpBits = [
        o.fp_ecr != null ? `FP ${fmt(o.fp_ecr)}` : null,
        o.fp_proj != null ? `FPproj ${fmt(o.fp_proj)}` : null,
      ]
        .filter(Boolean)
        .join(" · ");
      return `<li><span class="pos ${p.position}">${p.position}</span> ${p.name}
         <div class="muted">${p.marginal != null ? `Δ ${fmt(p.marginal)} · ` : ""}ADP ${fmt(p.adp_espn)} · ECR ${fmt(p.ecr_fp_ppr)}${fpBits ? ` · ${fpBits}` : ""}</div></li>`;
    })
    .join("");
  const marg =
    top.marginal != null
      ? `Δ ${fmt(top.marginal)} starter pts · ${fmt(top.lineup_before)} → ${fmt(top.lineup_after)}`
      : "";
  const fpLine = [
    ovRec.fp_ecr != null ? `FP ECR ${fmt(ovRec.fp_ecr)}` : null,
    ovRec.fp_proj != null ? `FP proj ${fmt(ovRec.fp_proj)}` : null,
  ]
    .filter(Boolean)
    .join(" · ");
  const fpTop = (overlay?.top_remaining || [])
    .slice(0, 5)
    .map((p) => `${p.name} (${fmt(p.fp_ecr)})`)
    .join(" · ");
  const divergeNote = overlay?.take_vs_fp?.note
    ? `<p class="muted overlay-note">${overlay.take_vs_fp.note}</p>`
    : "";
  const fpBlock =
    overlay?.available
      ? `<h2 style="margin-top:0.9rem">FP consensus <span class="muted">(overlay)</span></h2>
         ${fpTop ? `<p class="muted">${fpTop}</p>` : `<p class="muted">No FP API ranks remaining.</p>`}
         ${divergeNote}
         <p class="muted" style="font-size:0.75rem">${overlay.disclaimer || ""}</p>`
      : `<p class="muted" style="margin-top:0.75rem">FP overlay empty — run <code>python -m draftopt.fp_overlay</code></p>`;
  takeBody.innerHTML = `
    <p class="primary"><span class="pos ${top.position}">${top.position}</span> ${top.name}</p>
    <p class="muted">${top.why || ""}</p>
    <p class="muted">${marg}${marg ? " · " : ""}ADP ${fmt(top.adp_espn)} · ECR ${fmt(top.ecr_fp_ppr)}${fpLine ? ` · ${fpLine}` : ""}</p>
    <h2 style="margin-top:0.9rem">Next</h2>
    <ol>${rest}</ol>
    ${fpBlock}`;
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
  const modeLabel = isLiveSim() ? " · live sim" : "";
  draftSub.textContent = `id ${state?.draft_id || "—"} · ${state?.n_teams || nTeams}-team PPR snake · ${state?.n_rounds || "?"} rounds${rosterLabel}${modeLabel}`;
  const picking = canHumanPick();
  search.disabled = !picking;
  filterPos.disabled = !picking;
  filterTeam.disabled = !picking;
  filterSort.disabled = !picking;
  search.classList.toggle("search-disabled", search.disabled);
  if (state?.complete) search.placeholder = "Draft complete";
  else if (state?.is_user_turn) search.placeholder = "Type a player, then Enter";
  else if (isLiveSim()) {
    const label = (state.team_labels || [])[state.current_team - 1] || "them";
    search.placeholder = `Enter ${label}'s pick…`;
  } else search.placeholder = "Waiting for CPU…";
  // Hide K filter option if league has no K
  const kOpt = [...filterPos.options].find((o) => o.value === "K");
  if (kOpt && state?.roster?.slots) {
    kOpt.hidden = !state.roster.slots.K;
  }
  if (undoBtn) {
    undoBtn.textContent = isLiveSim() ? "Undo last pick" : "Undo my pick";
  }
  if (cpuThisPickBtn) {
    cpuThisPickBtn.classList.toggle(
      "hidden",
      !isLiveSim() || !state || state.complete || state.is_user_turn
    );
  }
  renderBoard();
  renderTake();
  if (picking && !state.complete) search.focus();
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
  if (!isLiveSim()) {
    await cpuLoop();
  }
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
  if (!draftId || !state || !canHumanPick()) return;
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
    if (state?.is_user_turn) startClock();
  }
}

async function cpuThisPick() {
  if (!draftId || !state || !isLiveSim() || state.is_user_turn || state.complete) return;
  try {
    const payload = await api(`/api/drafts/${draftId}/cpu`, { method: "POST" });
    const last = payload.state.picks[payload.state.picks.length - 1];
    showBanner(banner, `CPU filled ${last ? last.name : "a pick"} for this seat`);
    search.value = "";
    hits = [];
    applyPayload(payload);
    await afterStateChange();
  } catch (err) {
    showBanner(banner, err.message);
  }
}

async function dumpAutopsyCase() {
  if (!draftId) return;
  try {
    const data = await api(`/api/drafts/${draftId}/autopsy/case`, { method: "POST" });
    const top = (data.recommend || [])[0];
    showBanner(
      banner,
      `Case dumped · draft ${draftId} → ${data.path}` +
        (top ? ` · TAKE ${top.name} (M ${top.marginal})` : "")
    );
  } catch (err) {
    showBanner(banner, err.message);
  }
}

async function logDisagreement() {
  if (!draftId || !state) return;
  const take = recs[0];
  if (!take) {
    showBanner(banner, "No TAKE recommendation to disagree with.");
    return;
  }
  const chosenHit = hits[active];
  const chosenName = chosenHit
    ? chosenHit.name
    : window.prompt(`You prefer whom instead of ${take.name}?`, search.value.trim() || "");
  if (chosenHit && chosenHit.player_id === take.player_id) {
    showBanner(banner, "Selected player is already TAKE — nothing to log.");
    return;
  }
  if (!chosenHit && !chosenName) return;
  const category =
    window.prompt(
      "Category: opportunity_cost | bad_data | roster_construction | human_policy | uncertainty | rec_sensible | other",
      "opportunity_cost"
    ) || "other";
  const reason = window.prompt("Why? (short)", "") || "";
  try {
    const body = {
      recommended_player_id: take.player_id,
      category: category.trim(),
      reason,
    };
    if (chosenHit) body.chosen_player_id = chosenHit.player_id;
    else body.chosen_query = chosenName.trim();
    const data = await api(`/api/drafts/${draftId}/autopsy/disagree`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    showBanner(
      banner,
      `Logged disagree: TAKE ${data.recommended.name} → ${data.chosen.name} (${data.category})`
    );
  } catch (err) {
    showBanner(banner, err.message);
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

function orderMode() {
  return orderModeSelect.value || "pick_slot";
}

function rollRandomSlot() {
  const slot = 1 + Math.floor(Math.random() * nTeams);
  slotSelect.value = String(slot);
  localStorage.setItem("userSlot", String(slot));
  return slot;
}

function syncOrderModeUi() {
  const mode = orderMode();
  const pickSeat = mode === "pick_slot" || mode === "live_sim";
  const live = mode === "live_sim";
  slotPicker.classList.toggle("hidden", !pickSeat);
  shuffleMySlotBtn.classList.toggle("hidden", mode !== "random_slot");
  liveSimHint.classList.toggle("hidden", !live);
  leaguePanel.classList.toggle("hidden", !live);
  if (live) rebuildLiveSeatRows();
  else seatList.innerHTML = "";
}

function savedLiveSeats() {
  try {
    const raw = JSON.parse(localStorage.getItem("liveSeats") || "{}");
    return raw && typeof raw === "object" ? raw : {};
  } catch {
    return {};
  }
}

function rebuildLiveSeatRows() {
  const mySlot = Number(slotSelect.value) || 1;
  const mine = nameInput.value.trim() || "You";
  const saved = savedLiveSeats();
  seatList.innerHTML = "";
  for (let s = 1; s <= nTeams; s++) {
    const row = document.createElement("div");
    row.className = "opponent-row";
    const lab = document.createElement("label");
    lab.textContent = `Slot ${s}`;
    const input = document.createElement("input");
    input.type = "text";
    input.maxLength = 40;
    input.dataset.slot = String(s);
    if (s === mySlot) {
      input.value = mine;
      input.readOnly = true;
      input.placeholder = "You";
    } else {
      input.value = saved[String(s)] || "";
      input.placeholder = `Name for slot ${s}`;
      input.addEventListener("input", persistLiveSeats);
    }
    row.appendChild(lab);
    row.appendChild(input);
    seatList.appendChild(row);
  }
}

function persistLiveSeats() {
  const map = {};
  for (const input of seatList.querySelectorAll("input[data-slot]")) {
    if (input.readOnly) continue;
    const v = input.value.trim();
    if (v) map[input.dataset.slot] = v;
  }
  localStorage.setItem("liveSeats", JSON.stringify(map));
  return map;
}

function collectLiveTeamNames(userName) {
  const map = persistLiveSeats();
  const mySlot = Number(slotSelect.value) || 1;
  map[String(mySlot)] = userName;
  return map;
}

async function newDraftFromSetup() {
  const user_name = nameInput.value.trim();
  const user_slot = Number(slotSelect.value) || 1;
  const roster_preset = rosterSelect.value || "league_default";
  let mode = orderMode();
  if (!user_name) {
    showBanner(setupBanner, "Enter your name.");
    return;
  }
  localStorage.setItem("userName", user_name);
  localStorage.setItem("userSlot", String(user_slot));
  localStorage.setItem("rosterPreset", roster_preset);
  const live = mode === "live_sim";
  const order_mode = "pick_slot";
  localStorage.setItem("orderMode", mode);
  localStorage.setItem("liveSim", live ? "1" : "0");

  const body = {
    user_name,
    roster_preset,
    order_mode,
    user_slot,
    pick_mode: live ? "live_sim" : "user_only",
  };
  if (live) body.team_names = collectLiveTeamNames(user_name);

  try {
    const payload = await api("/api/drafts", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const st = payload.state || {};
    if (st.user_slot) {
      localStorage.setItem("userSlot", String(st.user_slot));
      slotSelect.value = String(st.user_slot);
    }
    showBanner(setupBanner, "");
    showBanner(banner, "");
    applyPayload(payload);
    showDraft();
    if (mode === "random_slot") {
      showBanner(
        banner,
        `You are slot ${st.user_slot} (${st.user_slot}.01 / 2.${String(nTeams + 1 - st.user_slot).padStart(2, "0")}).`
      );
    }
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
orderModeSelect.addEventListener("change", () => {
  const mode = orderMode();
  localStorage.setItem("orderMode", mode);
  localStorage.setItem("liveSim", mode === "live_sim" ? "1" : "0");
  if (mode === "random_slot") {
    const slot = rollRandomSlot();
    showBanner(setupBanner, `Your seat set to slot ${slot}. Start draft to lock it in.`);
  } else {
    showBanner(setupBanner, "");
  }
  syncOrderModeUi();
});
slotSelect.addEventListener("change", () => {
  localStorage.setItem("userSlot", slotSelect.value);
  if (orderMode() === "live_sim") {
    persistLiveSeats();
    rebuildLiveSeatRows();
  }
});
nameInput.addEventListener("input", () => {
  if (orderMode() !== "live_sim") return;
  const mySlot = Number(slotSelect.value) || 1;
  const mine = nameInput.value.trim() || "You";
  for (const input of seatList.querySelectorAll("input[data-slot]")) {
    if (Number(input.dataset.slot) === mySlot) input.value = mine;
  }
});
if (clearSeatsBtn) {
  clearSeatsBtn.addEventListener("click", () => {
    localStorage.removeItem("liveSeats");
    rebuildLiveSeatRows();
  });
}
shuffleMySlotBtn.addEventListener("click", () => {
  const slot = rollRandomSlot();
  showBanner(setupBanner, `Your seat set to slot ${slot}. Start draft to lock it in.`);
});
resumeBtn.addEventListener("click", resumeDraft);
rosterSelect.addEventListener("change", updateRosterDesc);
if (cpuThisPickBtn) {
  cpuThisPickBtn.addEventListener("click", () => {
    cpuThisPick().catch((err) => showBanner(banner, err.message));
  });
}
if (dumpCaseBtn) {
  dumpCaseBtn.addEventListener("click", () => {
    dumpAutopsyCase().catch((err) => showBanner(banner, err.message));
  });
}
if (logDisagreeBtn) {
  logDisagreeBtn.addEventListener("click", () => {
    logDisagreement().catch((err) => showBanner(banner, err.message));
  });
}
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
    if (st.n_teams) fillSlotOptions(Number(st.n_teams));
    slotSelect.value = localStorage.getItem("userSlot") || "1";
    const savedLive = localStorage.getItem("liveSim");
    const savedOrder = localStorage.getItem("orderMode") || "pick_slot";
    if (savedLive !== "0") {
      orderModeSelect.value = "live_sim";
    } else if (savedOrder === "random_slot") {
      orderModeSelect.value = "random_slot";
    } else {
      orderModeSelect.value = "pick_slot";
    }
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
    syncOrderModeUi();
    const setupSub = document.querySelector("#setup .sub");
    if (setupSub && st.n_teams && st.pick_clock_seconds) {
      setupSub.textContent = `${st.n_teams}-team PPR snake · ${st.pick_clock_seconds}-second clock on your pick`;
    }
    if (!st.players) {
      showBanner(setupBanner, "No players in the database. Run: python -m draftopt.ingest");
    }
  } catch {
    showBanner(setupBanner, "Cannot reach the draft server. Run: python -m draftopt.serve --port 8001");
    syncOrderModeUi();
  }
  resumeBtn.classList.toggle("hidden", !localStorage.getItem("draftId"));
  nameInput.focus();
})();
