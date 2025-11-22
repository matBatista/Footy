// app.js - Frontend para Footy Analytics
// Assume backend rodando em http://127.0.0.1:8000

const API_BASE = "http://127.0.0.1:8000";

// Estado em memória para fixtures + filtros
let RAW_FIXTURES = [];
let CURRENT_MATCHDAY = null;

// Helpers básicos
function formatPercent(p) {
  if (p == null || isNaN(p)) return "-";
  return (p * 100).toFixed(1) + "%";
}

function formatDateTimeLocal(utcStr) {
  if (!utcStr) return "-";
  const d = new Date(utcStr);
  if (isNaN(d.getTime())) return utcStr;
  const datePart = d.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
  const timePart = d.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
  return `${datePart} ${timePart}`;
}

// Util: acha "current round" = menor matchday das próximas partidas
function computeCurrentMatchday(fixtures) {
  if (!fixtures || fixtures.length === 0) return null;
  let md = null;
  for (const f of fixtures) {
    const m = Number(f.matchday ?? 0);
    if (!m) continue;
    if (md === null || m < md) md = m;
  }
  return md;
}

// DOM pronto
document.addEventListener("DOMContentLoaded", () => {
  const homeTeamSelect = document.getElementById("homeTeam");
  const awayTeamSelect = document.getElementById("awayTeam");
  const predictBtn = document.getElementById("predictBtn");
  const predictionResult = document.getElementById("predictionResult");

  const loadFixturesBtn = document.getElementById("loadFixturesBtn");
  const fixturesContainer = document.getElementById("fixturesContainer");
  const fixturesRoundLabel = document.getElementById("fixturesRoundLabel");

  const fixturesRoundMode = document.getElementById("fixturesRoundMode");
  const fixturesTeamFilter = document.getElementById("fixturesTeamFilter");
  const sortFixturesBy = document.getElementById("sortFixturesBy");
  const showModelXg = document.getElementById("showModelXg");

  const competitionCodeSelect = document.getElementById("competitionCode");
  const nSeasonsInput = document.getElementById("nSeasons");
  const trainBtn = document.getElementById("trainBtn");
  const trainResult = document.getElementById("trainResult");

  // ---------------------------
  // 1) Carrega times para o prediction by form
  // ---------------------------
  async function loadTeams() {
    try {
      const res = await fetch(`${API_BASE}/teams`);
      if (!res.ok) {
        throw new Error("HTTP " + res.status);
      }
      const data = await res.json();

      let teams = [];
      if (Array.isArray(data)) {
        teams = data;
      } else if (Array.isArray(data.teams)) {
        teams = data.teams;
      }

      homeTeamSelect.innerHTML = "";
      awayTeamSelect.innerHTML = "";

      for (const t of teams) {
        const optHome = document.createElement("option");
        optHome.value = t;
        optHome.textContent = t;
        homeTeamSelect.appendChild(optHome);

        const optAway = document.createElement("option");
        optAway.value = t;
        optAway.textContent = t;
        awayTeamSelect.appendChild(optAway);
      }

      if (teams.length > 1) {
        homeTeamSelect.selectedIndex = 0;
        awayTeamSelect.selectedIndex = 1;
      }

      predictBtn.disabled = teams.length < 2;
    } catch (err) {
      console.error("Error loading teams:", err);
      predictionResult.innerHTML =
        '<span class="text-red-400">Failed to load teams.</span>';
    }
  }

  // ---------------------------
  // 2) Prediction by form
  // ---------------------------
  async function predictByForm() {
    const home = homeTeamSelect.value;
    const away = awayTeamSelect.value;

    if (!home || !away || home === away) {
      predictionResult.innerHTML =
        '<span class="text-amber-300">Choose two different teams.</span>';
      return;
    }

    predictionResult.innerHTML =
      '<span class="text-slate-300">Calculating...</span>';

    try {
      const res = await fetch(`${API_BASE}/predict_by_form`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          home_team: home,
          away_team: away,
        }),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const data = await res.json();
      const probs = data.probabilities || data.probs || {};
      const homeP = probs.home ?? probs.H ?? probs.home_win ?? 0;
      const drawP = probs.draw ?? probs.D ?? probs.draw_prob ?? 0;
      const awayP = probs.away ?? probs.A ?? probs.away_win ?? 0;

      // Qual o maior (palpite do modelo)?
      const maxVal = Math.max(homeP, drawP, awayP);
      let best = "H";
      if (maxVal === drawP) best = "D";
      if (maxVal === awayP) best = "A";

      const bestLabel =
        best === "H" ? `${home} win` : best === "A" ? `${away} win` : "Draw";

      predictionResult.innerHTML = `
        <div class="space-y-1">
          <div class="text-sm">
            <span class="font-semibold text-emerald-400">Model pick:</span>
            <span class="font-semibold">${bestLabel}</span>
          </div>
          <div class="text-xs text-slate-300">
            <span class="inline-block mr-2">Home (1): <span class="font-mono">${formatPercent(
              homeP
            )}</span></span>
            <span class="inline-block mr-2">Draw (X): <span class="font-mono">${formatPercent(
              drawP
            )}</span></span>
            <span class="inline-block mr-2">Away (2): <span class="font-mono">${formatPercent(
              awayP
            )}</span></span>
          </div>
        </div>
      `;
    } catch (err) {
      console.error("Error predicting by form:", err);
      predictionResult.innerHTML =
        '<span class="text-red-400">Prediction failed.</span>';
    }
  }

  // ---------------------------
  // 3) Render fixtures com filtros
  // ---------------------------
  function renderFixtures() {
    const fixturesContainer = document.getElementById("fixturesContainer");
    const fixturesRoundLabel = document.getElementById("fixturesRoundLabel");
    const fixturesRoundMode = document.getElementById("fixturesRoundMode");
    const fixturesTeamFilter = document.getElementById("fixturesTeamFilter");
    const sortFixturesBy = document.getElementById("sortFixturesBy");
    const showModelXg = document.getElementById("showModelXg");

    if (!RAW_FIXTURES || RAW_FIXTURES.length === 0) {
      fixturesContainer.innerHTML =
        '<span class="text-slate-400">No upcoming fixtures found.</span>';
      if (fixturesRoundLabel) {
        fixturesRoundLabel.textContent = "";
      }
      return;
    }

    let fixtures = [...RAW_FIXTURES];

    // round filter
    const mode = fixturesRoundMode ? fixturesRoundMode.value : "current";
    if (mode === "current" && CURRENT_MATCHDAY != null) {
      fixtures = fixtures.filter(
        (f) => Number(f.matchday ?? 0) === Number(CURRENT_MATCHDAY)
      );
    }

    // team filter
    const teamFilter = fixturesTeamFilter
      ? fixturesTeamFilter.value.trim().toLowerCase()
      : "";
    if (teamFilter) {
      fixtures = fixtures.filter((f) => {
        const h = (f.home_team || "").toLowerCase();
        const a = (f.away_team || "").toLowerCase();
        return h.includes(teamFilter) || a.includes(teamFilter);
      });
    }

    // sort
    const sortMode = sortFixturesBy ? sortFixturesBy.value : "time";
    if (sortMode === "confidence") {
      fixtures.sort((a, b) => {
        const pa = a.probabilities || {};
        const pb = b.probabilities || {};
        const ma = Math.max(pa.home ?? 0, pa.draw ?? 0, pa.away ?? 0);
        const mb = Math.max(pb.home ?? 0, pb.draw ?? 0, pb.away ?? 0);
        return mb - ma; // desc
      });
    } else {
      fixtures.sort((a, b) => {
        const da = new Date(a.utc_date || a.date || a.kickoff).getTime();
        const db = new Date(b.utc_date || b.date || b.kickoff).getTime();
        return da - db;
      });
    }

    if (fixturesRoundLabel) {
      const total = RAW_FIXTURES.length;
      const shown = fixtures.length;
      if (mode === "current" && CURRENT_MATCHDAY != null) {
        fixturesRoundLabel.textContent = `Showing matchday ${CURRENT_MATCHDAY} (${shown}/${total} fixtures)`;
      } else {
        fixturesRoundLabel.textContent = `Showing ${shown} of ${total} upcoming fixtures`;
      }
    }

    const showXg = !!(showModelXg && showModelXg.checked);

    let html = `
      <div class="mt-3 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/40">
        <table class="min-w-full text-[0.7rem] sm:text-xs">
          <thead class="bg-slate-900/80 text-slate-300">
            <tr>
              <th class="px-2 py-2 text-left">Date</th>
              <th class="px-2 py-2 text-left">Match</th>
              <th class="px-2 py-2 text-left">Round</th>
              <th class="px-2 py-2 text-left">Model 1X2</th>
              <th class="px-2 py-2 text-left">Max prob</th>
              <th class="px-2 py-2 text-left">λ (xG)</th>
    `;

    if (showXg) {
      html += `<th class="px-2 py-2 text-left">xG 1X2</th>`;
    }

    html += `
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
    `;

    for (const f of fixtures) {
      const probs = f.probabilities || {};
      const homeP = probs.home ?? 0;
      const drawP = probs.draw ?? 0;
      const awayP = probs.away ?? 0;

      const xgProbs = f.xg_probabilities || {};
      const xgHome = xgProbs.home ?? 0;
      const xgDraw = xgProbs.draw ?? 0;
      const xgAway = xgProbs.away ?? 0;

      let maxVal = homeP;
      let maxLabel = "1";
      if (drawP > maxVal) {
        maxVal = drawP;
        maxLabel = "X";
      }
      if (awayP > maxVal) {
        maxVal = awayP;
        maxLabel = "2";
      }

      const dateLocal = formatDateTimeLocal(
        f.utc_date || f.date || f.kickoff
      );

      html += `
        <tr class="hover:bg-slate-900/80">
          <td class="px-2 py-1.5 whitespace-nowrap text-slate-300">
            ${dateLocal}
          </td>
          <td class="px-2 py-1.5">
            <span class="font-semibold">${f.home_team}</span>
            <span class="text-slate-500"> vs </span>
            <span class="font-semibold">${f.away_team}</span>
          </td>
          <td class="px-2 py-1.5">
            MD ${f.matchday ?? "-"}
          </td>
          <td class="px-2 py-1.5">
            <div class="flex flex-col gap-0.5">
              <span>1: <span class="font-mono">${formatPercent(
                homeP
              )}</span></span>
              <span>X: <span class="font-mono">${formatPercent(
                drawP
              )}</span></span>
              <span>2: <span class="font-mono">${formatPercent(
                awayP
              )}</span></span>
            </div>
          </td>
          <td class="px-2 py-1.5">
            <span class="inline-flex items-center gap-1">
              <span class="font-mono text-emerald-300">${maxLabel}</span>
              <span class="font-mono text-slate-200">${formatPercent(
                maxVal
              )}</span>
            </span>
          </td>
          <td class="px-2 py-1.5">
            <div class="font-mono text-[0.7rem]">
              λ<sub>H</sub> = ${(f.lambda_home ?? 0).toFixed(2)}<br/>
              λ<sub>A</sub> = ${(f.lambda_away ?? 0).toFixed(2)}
            </div>
          </td>
      `;

      if (showXg) {
        html += `
          <td class="px-2 py-1.5">
            <div class="flex flex-col gap-0.5">
              <span>1: <span class="font-mono">${formatPercent(
                xgHome
              )}</span></span>
              <span>X: <span class="font-mono">${formatPercent(
                xgDraw
              )}</span></span>
              <span>2: <span class="font-mono">${formatPercent(
                xgAway
              )}</span></span>
            </div>
          </td>
        `;
      }

      html += `</tr>`;
    }

    html += "</tbody></table></div>";
    fixturesContainer.innerHTML = html;
  }

  // ---------------------------
  // 4) Carregar fixtures do backend
  // ---------------------------
  async function loadFixturesWithPredictions() {
    const fixturesContainer = document.getElementById("fixturesContainer");
    const competitionCode = competitionCodeSelect.value;

    fixturesContainer.innerHTML =
      '<span class="text-slate-300">Loading fixtures...</span>';

    try {
      const url = `${API_BASE}/fixtures_with_predictions?competition_code=${encodeURIComponent(
        competitionCode
      )}`;
      const res = await fetch(url);

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const data = await res.json();
      const fixtures = Array.isArray(data.fixtures) ? data.fixtures : [];

      RAW_FIXTURES = fixtures;
      CURRENT_MATCHDAY = computeCurrentMatchday(RAW_FIXTURES);

      renderFixtures();
    } catch (err) {
      console.error("Error loading fixtures:", err);
      fixturesContainer.innerHTML =
        '<span class="text-red-400">Failed to load fixtures.</span>';
      if (fixturesRoundLabel) fixturesRoundLabel.textContent = "";
    }
  }

  // ---------------------------
  // 5) Treinar modelo
  // ---------------------------
  async function trainModel() {
    const competitionCode = competitionCodeSelect.value;
    const nSeasons = parseInt(nSeasonsInput.value || "3", 10);

    trainResult.innerHTML =
      '<span class="text-slate-300">Training model...</span>';

    try {
      const res = await fetch(`${API_BASE}/train_model`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          competition_code: competitionCode,
          n_past_seasons: nSeasons,
        }),
      });

      const text = await res.text();
      let data = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch (e) {
        console.warn("Non-JSON response from /train_model:", text);
      }

      if (!res.ok) {
        const detail =
          (data && data.detail) || text || `HTTP ${res.status} error`;
        trainResult.innerHTML =
          '<span class="text-red-400">Error: ' + detail + "</span>";
        return;
      }

      const acc = data.holdout_accuracy ?? data.accuracy ?? null;
      const f1 = data.cv_f1_macro ?? data.f1_macro ?? null;
      const seasonsUsed = Array.isArray(data.seasons_used)
        ? data.seasons_used.join(", ")
        : "n/a";

      trainResult.innerHTML = `
        <div class="space-y-1">
          <div>
            <span class="font-semibold text-slate-100">Competition:</span>
            <span class="text-slate-300">${data.competition_code || competitionCode}</span>
          </div>
          <div>
            <span class="font-semibold text-slate-100">Seasons used:</span>
            <span class="text-slate-300">${seasonsUsed}</span>
          </div>
          <div>
            <span class="font-semibold text-slate-100">Holdout acc:</span>
            <span class="font-mono text-emerald-300">${
              acc != null ? acc.toFixed(3) : "n/a"
            }</span>
          </div>
          <div>
            <span class="font-semibold text-slate-100">CV F1-macro:</span>
            <span class="font-mono text-emerald-300">${
              f1 != null ? f1.toFixed(3) : "n/a"
            }</span>
          </div>
        </div>
      `;
    } catch (err) {
      console.error("Error training model:", err);
      trainResult.innerHTML =
        '<span class="text-red-400">Training failed.</span>';
    }
  }

  // ---------------------------
  // Listeners
  // ---------------------------
  predictBtn.addEventListener("click", predictByForm);
  loadFixturesBtn.addEventListener("click", loadFixturesWithPredictions);
  trainBtn.addEventListener("click", trainModel);

  if (fixturesRoundMode) {
    fixturesRoundMode.addEventListener("change", renderFixtures);
  }
  if (fixturesTeamFilter) {
    fixturesTeamFilter.addEventListener("input", renderFixtures);
  }
  if (sortFixturesBy) {
    sortFixturesBy.addEventListener("change", renderFixtures);
  }
  if (showModelXg) {
    showModelXg.addEventListener("change", renderFixtures);
  }

  // Inicializa times
  loadTeams();
});