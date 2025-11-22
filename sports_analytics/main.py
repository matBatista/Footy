import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from joblib import dump, load

from src.advanced_model import train_match_outcome_model
from src.features import build_match_feature_table
from src.football_data_api import fetch_competition_matches_df, FootballDataApiError

# -------------------------------------------------------------------
# FastAPI app + CORS
# -------------------------------------------------------------------
app = FastAPI(title="Footy Prob - Multi-league API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste se quiser restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Paths / globals
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Guarda lista de times por liga (atualizada no treino)
_TEAMS_BY_COMP: Dict[str, List[str]] = {}
_LAST_TRAINED_COMP: Optional[str] = None


def get_model_paths(competition_code: str) -> Dict[str, Path]:
    code = competition_code.upper()
    return {
        "model": MODELS_DIR / f"advanced_model_{code}.joblib",
        "features": MODELS_DIR / f"feature_cols_{code}.txt",
        "meta": MODELS_DIR / f"advanced_model_meta_{code}.json",
    }


def save_model_bundle(
    competition_code: str,
    model,
    feature_cols: List[str],
    *,
    n_games: int,
    season: int,
) -> None:
    paths = get_model_paths(competition_code)

    # modelo
    dump(model, paths["model"])

    # feature cols
    with paths["features"].open("w", encoding="utf-8") as f:
        for col in feature_cols:
            f.write(col + "\n")

    # metadados
    meta = {
        "competition_code": competition_code,
        "season": season,
        "n_games": n_games,
    }
    with paths["meta"].open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


@lru_cache(maxsize=16)
def load_model_bundle(competition_code: str):
    paths = get_model_paths(competition_code)
    if not paths["model"].exists():
        raise HTTPException(
            status_code=404,
            detail=f"Modelo para {competition_code} ainda não foi treinado.",
        )

    model = load(paths["model"])

    if not paths["features"].exists():
        raise HTTPException(
            status_code=500,
            detail=f"Arquivo de features para {competition_code} não encontrado.",
        )

    with paths["features"].open("r", encoding="utf-8") as f:
        feature_cols = [line.strip() for line in f if line.strip()]

    meta = {}
    if paths["meta"].exists():
        with paths["meta"].open("r", encoding="utf-8") as f:
            meta = json.load(f)

    print(f"[model_loader] Loaded model for {competition_code}: {paths['model'].name}")
    return model, feature_cols, meta


def fetch_upcoming_matches_df(
    competition_code: str,
    season: Optional[int] = None,
) -> pd.DataFrame:
    """
    Busca partidas FUTURAS (status SCHEDULED) direto da API.
    Usa a mesma função base da API, apenas mudando o status.
    """
    try:
        df = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season,
            status="SCHEDULED",
        )
    except FootballDataApiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if df is None or df.empty:
        return pd.DataFrame()

    return df


@app.on_event("startup")
def on_startup():
    print("API iniciada - suporte multi-liga ativo.")


# -------------------------------------------------------------------
# /train_model
# -------------------------------------------------------------------
@app.post("/train_model")
async def train_model(
    request: Request,
    competition_code: Optional[str] = Query(None),
    season: Optional[int] = Query(None),
    n_games: Optional[int] = Query(5),
):
    """
    Treina (ou re-treina) o modelo para uma liga específica.

    Aceita:
    - Body JSON: {
        "competition_code": "BSA",
        "season": 2025,
        "n_games": 5
      }
    - OU query string:
        /train_model?competition_code=BSA&season=2025&n_games=5
    - OU campos alternativos: "competition", "league", "year"
    """
    global _LAST_TRAINED_COMP, _TEAMS_BY_COMP

    # tenta ler o body JSON
    try:
        body = await request.json()
        if not isinstance(body, dict):
            body = {}
    except Exception:
        body = {}

    # prioridade: body > querystring
    comp = (
        body.get("competition_code")
        or body.get("competition")
        or body.get("league")
        or competition_code
    )
    season_val = (
        body.get("season")
        or body.get("year")
        or season
    )

    # n_games pode vir do body, query ou default
    n_games_val = int(body.get("n_games") or (n_games if n_games is not None else 5))

    if not comp or season_val is None:
        raise HTTPException(
            status_code=400,
            detail="Campos obrigatórios: competition_code e season.",
        )

    competition_code = str(comp).upper()
    season_int = int(season_val)

    print(
        f"[train_model] Treinando modelo para {competition_code} "
        f"season {season_int} (n_games={n_games_val})"
    )

    # buscar somente jogos finalizados
    try:
        df_all = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season_int,
            status="FINISHED",
        )
    except FootballDataApiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if df_all is None or df_all.empty:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Nenhum dado de partidas finalizadas encontrado para "
                f"{competition_code} season {season_int}."
            ),
        )

    # atualiza lista de times
    teams = sorted(
        set(df_all["home_team"].unique()).union(set(df_all["away_team"].unique()))
    )
    _TEAMS_BY_COMP[competition_code] = teams
    _LAST_TRAINED_COMP = competition_code

    # treina modelo
    model, acc, report, _, feature_cols = train_match_outcome_model(
        df_all,
        n_games=n_games_val,
    )

    save_model_bundle(
        competition_code=competition_code,
        model=model,
        feature_cols=feature_cols,
        n_games=n_games_val,
        season=season_int,
    )

    load_model_bundle.cache_clear()

    return {
        "competition_code": competition_code,
        "season": season_int,
        "n_games": n_games_val,
        "accuracy": float(acc),
        "n_matches": int(len(df_all)),
        "n_teams": len(teams),
        "feature_count": len(feature_cols),
        "classification_report": report,
    }


# -------------------------------------------------------------------
# /teams
# -------------------------------------------------------------------
@app.get("/teams")
def get_teams(competition_code: Optional[str] = Query(None)):
    """
    Retorna a lista de times da liga.
    - Se competition_code não for enviado, usa a última liga treinada.
    Resposta:
      { "teams": ["Team A", "Team B", ...] }
    """
    code = (competition_code or _LAST_TRAINED_COMP or "").upper()
    if not code:
        raise HTTPException(
            status_code=400,
            detail="competition_code não informado e nenhum modelo treinado ainda.",
        )

    teams = _TEAMS_BY_COMP.get(code)
    if not teams:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum time encontrado para {code}. Treine o modelo primeiro.",
        )

    return {"competition_code": code, "teams": teams}


# -------------------------------------------------------------------
# Helpers de features para fixtures
# -------------------------------------------------------------------
def _build_latest_team_feature_maps(
    df_all_finished: pd.DataFrame,
    n_games: int,
    feature_cols: List[str],
):
    """
    Constrói dois dicionários:
      - latest_home[team] -> última linha de features quando time jogou em casa
      - latest_away[team] -> última linha de features quando time jogou fora

    Isso nos permite montar o vetor X para partidas futuras.
    """
    feat_df = build_match_feature_table(df_all_finished, n_games=n_games)

    # Garante que temos as colunas necessárias
    missing = [c for c in feature_cols if c not in feat_df.columns]
    if missing:
        print(
            "[fixtures_with_predictions] Aviso: algumas features do modelo "
            "não existem em feat_df e serão ignoradas no lookup: ",
            missing,
        )

    feat_df = feat_df.sort_values("date")

    latest_home = (
        feat_df.groupby("home_team", group_keys=False)
        .tail(1)
        .set_index("home_team")
    )
    latest_away = (
        feat_df.groupby("away_team", group_keys=False)
        .tail(1)
        .set_index("away_team")
    )

    return latest_home, latest_away


# -------------------------------------------------------------------
# /fixtures_with_predictions
# -------------------------------------------------------------------
@app.get("/fixtures_with_predictions")
def get_fixtures_with_predictions(
    competition_code: str = Query(..., description="Código da liga, ex: BSA, PL, etc."),
):
    """
    Retorna as partidas futuras da liga + predições de resultado.
    """
    # Carrega modelo + metadados
    model, feature_cols, meta = load_model_bundle(competition_code)
    n_games = int(meta.get("n_games") or 5)
    season = meta.get("season")

    # 1) Carrega partidas finalizadas da season correspondente
    try:
        df_finished = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season,
            status="FINISHED",
        )
    except FootballDataApiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if df_finished is None or df_finished.empty:
        raise HTTPException(
            status_code=500,
            detail=f"Nenhum dado de partidas finalizadas encontrado para {competition_code} season {season}.",
        )

    # 2) Constrói mapas de features mais recentes por time
    latest_home, latest_away = _build_latest_team_feature_maps(
        df_finished, n_games=n_games, feature_cols=feature_cols
    )

    # 3) Carrega fixtures futuros
    fixtures_df = fetch_upcoming_matches_df(competition_code, season=season)
    if fixtures_df is None or fixtures_df.empty:
        return {"competition_code": competition_code, "fixtures": [], "predictions": []}

    predictions = []
    for _, row in fixtures_df.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]

        # Recupera última linha de features para cada time
        home_vals = latest_home.loc[home_team] if home_team in latest_home.index else None
        away_vals = latest_away.loc[away_team] if away_team in latest_away.index else None

        if home_vals is None or away_vals is None:
            predictions.append(
                {
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "utcDate": row.get("utc_date") or row.get("date"),
                    "pred": None,
                    "prob_H": None,
                    "prob_D": None,
                    "prob_A": None,
                    "reason": "Sem histórico suficiente para um dos times.",
                }
            )
            continue

        # Monta vetor X na mesma ordem de feature_cols
        X_row = {}
        for col in feature_cols:
            if col.startswith("home_"):
                X_row[col] = float(home_vals.get(col, 0.0))
            elif col.startswith("away_"):
                X_row[col] = float(away_vals.get(col, 0.0))
            else:
                X_row[col] = 0.0

        X_df = pd.DataFrame([X_row])

        proba = model.predict_proba(X_df.values)[0]
        classes = model.classes_
        pred_label = classes[proba.argmax()]

        def _get_prob_for(label: str) -> float:
            if label not in classes:
                return 0.0
            idx = list(classes).index(label)
            return float(proba[idx])

        predictions.append(
            {
                "homeTeam": home_team,
                "awayTeam": away_team,
                "utcDate": row.get("utc_date") or row.get("date"),
                "pred": pred_label,
                "prob_H": _get_prob_for("H"),
                "prob_D": _get_prob_for("D"),
                "prob_A": _get_prob_for("A"),
            }
        )

    return {
        "competition_code": competition_code,
        "season": season,
        "n_games": n_games,
        "fixtures": predictions,
    }