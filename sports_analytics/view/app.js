// BASE URL DO BACKEND
const API_BASE = "http://127.0.0.1:8000";

// ELEMENTOS DO DOM
const homeSelect = document.getElementById("homeTeam");
const awaySelect = document.getElementById("awayTeam");
const predictBtn = document.getElementById("predictBtn");
const predictionResult = document.getElementById("predictionResult");
const loadFixturesBtn = document.getElementById("loadFixturesBtn");
const fixturesContainer = document.getElementById("fixturesContainer");

const competitionSelect = document.getElementById("competitionCode");
const nSeasonsInput = document.getElementById("nSeasons");
const trainBtn = document.getElementById("trainBtn");
const trainResult = document.getElementById("trainResult");

// Formatador dd/mm/yyyy HH:mm com timezone local da máquina
function formatDateTimeLocal(dateStr) {
  const d = new Date(dateStr);
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = d.getFullYear();
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

function formatPercent(x) {
  return (x * 100).toFixed(1) + "%";
}

// =============================
// CARREGAR TIMES PARA OS SELECTS
// =============================
async function loadTeams() {
  try {
    const res = await fetch(API_BASE + "/teams");
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    const teams = data.teams || [];

    homeSelect.innerHTML = "";
    awaySelect.innerHTML = "";

    for (const t of teams) {
      const optH = document.createElement("option");
      const optA = document.createElement("option");
      optH.value = optA.value = t;
      optH.textContent = optA.textContent = t;

      homeSelect.appendChild(optH);
      awaySelect.appendChild(optA);
    }

    if (teams.length >= 2) awaySelect.selectedIndex = 1;

    predictBtn.disabled = false;
  } catch (err) {
    console.error("Error loading teams:", err);
    predictionResult.innerHTML =
      '<span class="text-red-400">Failed to load teams from API.</span>';
  }
}

// =============================
// PREDICT BY FORM
// =============================
async function predictByForm() {
  const home = homeSelect.value;
  const away = awaySelect.value;

  if (!home || !away || home === away) {
    predictionResult.innerHTML =
      '<span class="text-orange-400">Select two different teams.</span>';
    return;
  }

  predictionResult.textContent = "Loading prediction...";

  try {
    const url =
      API_BASE +
      "/predict_by_form?home_team=" +
      encodeURIComponent(home) +
      "&away_team=" +
      encodeURIComponent(away);

    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) {
      predictionResult.innerHTML =
        '<span class="text-red-400">Error: ' +
        (data.detail || "Unknown error") +
        "</span>";
      return;
    }

    const p = data.probabilities;

    predictionResult.innerHTML =
      `<div class="mb-1 text-sm">
        <span class="font-semibold text-slate-50">${data.home_team}</span>
        <span class="text-slate-400"> vs </span>
        <span class="font-semibold text-slate-50">${data.away_team}</span>
      </div>

      <div class="space-y-0.5">
        <div><span class="inline-block w-14 text-slate-400">Home:</span> ${formatPercent(p.home_win)}</div>
        <div><span class="inline-block w-14 text-slate-400">Draw:</span> ${formatPercent(p.draw)}</div>
        <div><span class="inline-block w-14 text-slate-400">Away:</span> ${formatPercent(p.away_win)}</div>
      </div>

      <div class="text-xs text-slate-400 mt-1">
        Top scorers goals: home ${data.home_top_scorer_goals}, away ${data.away_top_scorer_goals}
      </div>`;
  } catch (err) {
    console.error("Error predicting:", err);
    predictionResult.innerHTML =
      '<span class="text-red-400">Failed to call prediction API.</span>';
  }
}

// =============================
// FIXTURES COM PREDIÇÕES (APENAS RODADA ATUAL)
// =============================
async function loadFixturesWithPredictions() {
  fixturesContainer.textContent = "Loading fixtures and predictions...";

  const competition = competitionSelect.value || "PL";

  try {
    const url =
      API_BASE +
      "/fixtures_with_predictions?competition_code=" +
      encodeURIComponent(competition);

    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) {
      fixturesContainer.innerHTML =
        '<span class="text-red-400">Error: ' +
        (data.detail || "Unknown error") +
        "</span>";
      return;
    }

    const fixtures = data.fixtures || [];
    if (fixtures.length === 0) {
      fixturesContainer.innerHTML =
        '<span class="text-slate-400 text-xs">No scheduled fixtures available.</span>';
      return;
    }

    // descobrir qual é a rodada atual
    let filteredFixtures = fixtures;
    const sample = fixtures.find((f) => f.matchday != null);
    if (sample) {
      const rodada = sample.matchday;
      filteredFixtures = fixtures.filter((f) => f.matchday === rodada);
    }

    // montar tabela
    let html = `
      <div class="overflow-x-auto mt-2">
        <table class="min-w-full text-left text-xs sm:text-sm">
          <thead class="bg-slate-800/80">
            <tr>
              <th class="px-2 py-2 font-medium text-slate-300">Date (local)</th>
              <th class="px-2 py-2 font-medium text-slate-300">Match</th>
              <th class="px-2 py-2 font-medium text-slate-300">Home</th>
              <th class="px-2 py-2 font-medium text-slate-300">Draw</th>
              <th class="px-2 py-2 font-medium text-slate-300">Away</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
    `;

    for (const f of filteredFixtures) {
      const p = f.probabilities;
      html += `
        <tr class="hover:bg-slate-800/60">
          <td class="px-2 py-1.5 text-slate-400">${formatDateTimeLocal(f.date)}</td>
          <td class="px-2 py-1.5 text-slate-100">${f.home_team} vs ${f.away_team}</td>
          <td class="px-2 py-1.5">${formatPercent(p.home_win)}</td>
          <td class="px-2 py-1.5">${formatPercent(p.draw)}</td>
          <td class="px-2 py-1.5">${formatPercent(p.away_win)}</td>
        </tr>`;
    }

    html += "</tbody></table></div>";
    fixturesContainer.innerHTML = html;

  } catch (err) {
    console.error("Error loading fixtures:", err);
    fixturesContainer.innerHTML =
      '<span class="text-red-400">Failed to load fixtures.</span>';
  }
}

// =============================
// TREINAR MODELO
// =============================
async function trainModel() {
  const competition = competitionSelect.value;
  const nSeasons = parseInt(nSeasonsInput.value, 10) || 3;

  if (!competition) {
    trainResult.innerHTML =
      '<span class="text-orange-400">Selecione um campeonato.</span>';
    return;
  }

  trainResult.textContent =
    "Training model... (this may take some seconds)";

  try {
    const res = await fetch(API_BASE + "/train_model", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        competition_code: competition,
        n_past_seasons: nSeasons,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      trainResult.innerHTML =
        '<span class="text-red-400">Error: ' +
        (data.detail || "Unknown error") +
        "</span>";
      return;
    }

    trainResult.innerHTML = `
      <div class="mb-1 text-sm">
        <span class="font-semibold text-slate-100">Competition:</span>
        <span class="text-slate-300">${data.competition_code}</span>
      </div>
      <div class="text-xs text-slate-300">
        Seasons used: ${data.training_seasons.join(", ")}<br/>
        Matches: ${data.n_matches}<br/>
        Accuracy: ${(data.accuracy * 100).toFixed(1)}%
      </div>
      <div class="text-xs text-emerald-400 mt-1">${data.message}</div>
      <div class="text-[0.7rem] text-slate-500 mt-1">
        Generic model: ${data.generic_model_path}<br/>
        League model: ${data.league_model_path}
      </div>
    `;

    // Recarrega times e fixtures
    loadTeams();
    loadFixturesWithPredictions();

  } catch (err) {
    console.error("Error training model:", err);
    trainResult.innerHTML =
      '<span class="text-red-400">Failed to call train_model API.</span>';
  }
}

// EVENTOS
predictBtn.addEventListener("click", predictByForm);
loadFixturesBtn.addEventListener("click", loadFixturesWithPredictions);
trainBtn.addEventListener("click", trainModel);

// Carrega times ao abrir a página
loadTeams();