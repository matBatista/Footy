from typing import List, Optional
import os

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from joblib import load, dump


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.data_loader import load_matches, get_data_path
from src.features import build_match_feature_table
from src.football_data_api import fetch_competition_matches_df, FootballDataApiError
from src.advanced_model import train_match_outcome_model, build_dataset
from src.season_utils import get_current_season, get_training_seasons

from src.xg_utils import (
    calibrate_goal_expectancy,
    match_outcome_probabilities,  # se ainda estiver usando em outros lugares
    build_xg_context_from_feature_df,
    compute_match_lambdas,
    poisson_outcome_probs,
)


# =============================================================================
# Configuração básica
# =============================================================================

# Modelo "genérico" atual em memória (último treino, qualquer liga)
MODEL_PATH = "models/advanced_model_generic.joblib"
FEATURE_COLS_PATH = "models/advanced_model_feature_cols_generic.txt"

# CSV local default (para debug / fallback, se quiser)
DATA_FILENAME = "matches_pl_2023.csv"

# Estrutura em memória
_model = None  # modelo carregado
_feature_cols: List[str] = []  # lista de colunas de features (na ordem usada no treino)
_feature_df: Optional[pd.DataFrame] = None  # feature table completa (todas as partidas da liga)


# =============================================================================
# Schemas Pydantic (request/response)
# =============================================================================


class TrainRequest(BaseModel):
    competition_code: str  # e.g., "PL", "BSA"
    season: Optional[int] = None  # se None, usamos get_current_season
    n_past_seasons: int = 3
    n_games: int = 5


class OutcomeProbs(BaseModel):
    home: float
    draw: float
    away: float


class FixtureWithPrediction(BaseModel):
    utc_date: str
    match_id: int
    competition_code: str
    season: int
    matchday: Optional[int] = None
    home_team: str
    away_team: str
    home_top_scorer_goals: Optional[float] = None
    away_top_scorer_goals: Optional[float] = None

    # Probabilidades vindas do modelo de classificação (RandomForest)
    probabilities: OutcomeProbs

    # Expected goals (fake xG) calibrados a partir de home_xg_ability / away_xg_ability
    lambda_home: float
    lambda_away: float

    # Probabilidades de resultado derivadas do modelo Poisson (xG-based)
    xg_probabilities: OutcomeProbs


class FixturesWithPredictionsResponse(BaseModel):
    fixtures: List[FixtureWithPrediction]


class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    home_top_scorer_goals: Optional[float] = None
    away_top_scorer_goals: Optional[float] = None
    probabilities: OutcomeProbs


class TrainResponse(BaseModel):
    message: str
    competition_code: str
    seasons_used: List[int]
    n_games: int
    accuracy: float
    model_path: str
    feature_cols_path: str


# =============================================================================
# FastAPI app + CORS
# =============================================================================

app = FastAPI(
    title="Footy Analytics API",
    description="Backend para previsão de resultados de futebol usando modelo avançado.",
    version="0.3.0",
)

# CORS: libera tudo em dev (incluindo origin "null")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ok porque allow_credentials=False
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Funções utilitárias
# =============================================================================


def _load_model_and_features_from_disk() -> None:
    """
    Tenta carregar um modelo e a lista de feature columns do disco
    (genéricos; último treino realizado).
    """
    global _model, _feature_cols

    if os.path.exists(MODEL_PATH):
        _model = load(MODEL_PATH)
        print(f"[startup] Modelo carregado de {MODEL_PATH}")
    else:
        print(f"[startup] Modelo {MODEL_PATH} não encontrado; será treinado via /train_model.")

    if os.path.exists(FEATURE_COLS_PATH):
        with open(FEATURE_COLS_PATH, "r", encoding="utf-8") as f:
            cols = [line.strip() for line in f if line.strip()]
        _feature_cols = cols
        print(f"[startup] Feature cols carregadas de {FEATURE_COLS_PATH}: {_feature_cols}")
    else:
        print(f"[startup] Arquivo {FEATURE_COLS_PATH} não encontrado; será preenchido no próximo treino.")


def _load_local_feature_df() -> None:
    """
    Carrega um CSV local e gera uma feature table simplificada (sem xG),
    apenas para debug / fallback inicial. Depois de treinar via /train_model,
    _feature_df será substituído pelo feat_df completo (com xG etc.).
    """
    global _feature_df

    csv_path = get_data_path(DATA_FILENAME)
    if not os.path.exists(csv_path):
        print(f"[startup] CSV local {csv_path} não encontrado. _feature_df ficará None.")
        _feature_df = None
        return

    print(f"[startup] Carregando CSV local {csv_path}...")
    df = load_matches(DATA_FILENAME)
    _feature_df = build_match_feature_table(df, n_games=5)
    print(f"[startup] Feature table local construída com shape: {_feature_df.shape}")


@app.on_event("startup")
def startup_event():
    """
    Evento de startup: tenta carregar modelo + features do disco e
    uma feature_df local (para debug). Após o primeiro /train_model,
    _feature_df passa a usar a tabela completa (build_dataset).
    """
    _load_model_and_features_from_disk()
    _load_local_feature_df()


# =============================================================================
# Endpoints básicos
# =============================================================================


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Footy Analytics API is running"}


@app.get("/health")
def health_check():
    """
    Endpoint simples de health check.
    """
    return {"status": "healthy"}


# =============================================================================
# Endpoint: listar times conhecidos (com base na feature_df carregada)
# =============================================================================


@app.get("/teams")
def get_teams():
    """
    Retorna a lista de times únicos presentes na feature table atual.

    Observação: neste momento, usamos a feature_df carregada na memória, que
    reflete a última liga/temporadas utilizadas. Em uma estrutura multi-liga
    mais avançada, poderíamos ter /teams?competition_code=BSA etc.
    """
    if _feature_df is None:
        raise HTTPException(status_code=500, detail="Feature table não carregada ainda.")

    teams = sorted(
        set(_feature_df["home_team"].dropna().unique())
        | set(_feature_df["away_team"].dropna().unique())
    )
    return {"teams": teams}


# =============================================================================
# Endpoint: previsão para um confronto específico (usando o histórico atual)
# (sem xG ainda, focado em modelo RF)
# =============================================================================


@app.get("/predict", response_model=PredictionResponse)
def predict_match(
    home_team: str = Query(..., description="Nome exato do time mandante"),
    away_team: str = Query(..., description="Nome exato do time visitante"),
):
    """
    Faz a previsão da probabilidade de H/D/A para um confronto específico,
    usando o modelo carregado em memória e a feature_df atual.
    """
    if _model is None or _feature_df is None or not _feature_cols:
        raise HTTPException(
            status_code=500,
            detail="Modelo ou features não carregados. Treine via /train_model primeiro.",
        )

    # Helper: pega última linha de features em que o time aparece como mandante
    def _get_home_role_features(team_name: str) -> dict:
        home_rows = _feature_df[_feature_df["home_team"] == team_name].sort_values("date")
        if not home_rows.empty:
            last = home_rows.iloc[-1]
            return {
                "home_goals_for_avg": float(last["home_goals_for_avg"]),
                "home_goals_against_avg": float(last["home_goals_against_avg"]),
                "home_goal_diff_avg": float(last["home_goal_diff_avg"]),
                "home_win_rate": float(last["home_win_rate"]),
                "home_top_scorer_goals": float(last.get("home_top_scorer_goals", 0.0)),
            }

        # Se não achou como mandante, tenta como visitante e mapeia as colunas
        away_rows = _feature_df[_feature_df["away_team"] == team_name].sort_values("date")
        if away_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum histórico encontrado para o time {team_name}",
            )
        last = away_rows.iloc[-1]
        return {
            "home_goals_for_avg": float(last["away_goals_for_avg"]),
            "home_goals_against_avg": float(last["away_goals_against_avg"]),
            "home_goal_diff_avg": float(last["away_goal_diff_avg"]),
            "home_win_rate": float(last["away_win_rate"]),
            "home_top_scorer_goals": float(last.get("away_top_scorer_goals", 0.0)),
        }

    # Helper: pega última linha de features em que o time aparece como visitante
    def _get_away_role_features(team_name: str) -> dict:
        away_rows = _feature_df[_feature_df["away_team"] == team_name].sort_values("date")
        if not away_rows.empty:
            last = away_rows.iloc[-1]
            return {
                "away_goals_for_avg": float(last["away_goals_for_avg"]),
                "away_goals_against_avg": float(last["away_goals_against_avg"]),
                "away_goal_diff_avg": float(last["away_goal_diff_avg"]),
                "away_win_rate": float(last["away_win_rate"]),
                "away_top_scorer_goals": float(last.get("away_top_scorer_goals", 0.0)),
            }

        home_rows = _feature_df[_feature_df["home_team"] == team_name].sort_values("date")
        if home_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum histórico encontrado para o time {team_name}",
            )
        last = home_rows.iloc[-1]
        return {
            "away_goals_for_avg": float(last["home_goals_for_avg"]),
            "away_goals_against_avg": float(last["home_goals_against_avg"]),
            "away_goal_diff_avg": float(last["home_goal_diff_avg"]),
            "away_win_rate": float(last["home_win_rate"]),
            "away_top_scorer_goals": float(last.get("home_top_scorer_goals", 0.0)),
        }

    home_vals = _get_home_role_features(home_team)
    away_vals = _get_away_role_features(away_team)

    # Monta um DataFrame com as colunas de features na ordem esperada
    row = {}
    for col in _feature_cols:
        if col.startswith("home_") and col in home_vals:
            row[col] = home_vals[col]
        elif col.startswith("away_") and col in away_vals:
            row[col] = away_vals[col]
        else:
            # Features que não conseguimos preencher agora (ex: rank),
            # deixamos neutro (0.0).
            row[col] = 0.0

    X = pd.DataFrame([row], columns=_feature_cols)

    proba = _model.predict_proba(X)[0]
    classes = list(_model.classes_)  # e.g. ['A','D','H']
    prob_map = {cls: float(p) for cls, p in zip(classes, proba)}

    home_p = prob_map.get("H", 0.0)
    draw_p = prob_map.get("D", 0.0)
    away_p = prob_map.get("A", 0.0)

    # Normaliza para garantir soma 1
    total = home_p + draw_p + away_p
    if total > 0:
        home_p /= total
        draw_p /= total
        away_p /= total

    return PredictionResponse(
        home_team=home_team,
        away_team=away_team,
        home_top_scorer_goals=home_vals.get("home_top_scorer_goals"),
        away_top_scorer_goals=away_vals.get("away_top_scorer_goals"),
        probabilities=OutcomeProbs(home=home_p, draw=draw_p, away=away_p),
    )


# =============================================================================
# Endpoint: fixtures futuros + previsões (RF + xG)
# =============================================================================


@app.get("/fixtures_with_predictions", response_model=FixturesWithPredictionsResponse)
def get_fixtures_with_predictions(
    competition_code: str = Query("PL", description="Competition code, e.g. 'PL'"),
    season: Optional[int] = Query(
        None, description="Season year, e.g. 2023. If omitted, current season is used."
    ),
):
    """
    Retorna as partidas futuras (status=SCHEDULED) de uma competição
    e, para cada fixture, calcula:

    - Probabilidades H/D/A do modelo de classificação (RandomForest)
    - λ_home / λ_away (expected goals, xG)
    - Probabilidades H/D/A derivadas do modelo Poisson baseado em xG
    """
    if _model is None or _feature_df is None or not _feature_cols:
        raise HTTPException(
            status_code=500,
            detail="Modelo ou features não carregados. Treine via /train_model primeiro.",
        )

    # Se a season não vier, usamos a current_season
    if season is None:
        season = get_current_season()

    try:
        df_fixtures = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season,
            status="SCHEDULED",
        )
    except FootballDataApiError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao buscar fixtures na API externa: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error fetching fixtures from upstream API: {e}",
        )

    if df_fixtures.empty:
        return FixturesWithPredictionsResponse(fixtures=[])

    # ---------------------------------------------------------------
    # Contexto de xG global calculado UMA vez, a partir de _feature_df
    # ---------------------------------------------------------------
    xg_ctx = build_xg_context_from_feature_df(_feature_df)

    fixtures_out: List[FixtureWithPrediction] = []

    for _, row in df_fixtures.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]

        subset = _feature_df[
            (_feature_df["home_team"] == home_team)
            & (_feature_df["away_team"] == away_team)
        ].sort_values("date")

        if subset.empty:
            # Fallback: usa último jogo do mandante como mandante + último do visitante como visitante.
            # Se um dos times (ou ambos) não tiver histórico, usamos valores neutros (0.0) em vez de pular o fixture.
            home_rows = _feature_df[_feature_df["home_team"] == home_team].sort_values("date")
            away_rows = _feature_df[_feature_df["away_team"] == away_team].sort_values("date")

            last_home = home_rows.iloc[-1] if not home_rows.empty else None
            last_away = away_rows.iloc[-1] if not away_rows.empty else None

            # Construir uma linha sintética com base nos últimos jogos isolados quando existirem;
            # caso contrário, preenchendo com valores neutros (0.0). Assim não perdemos jogos
            # de times recém‑promovidos, apenas marcamos features mais "fracas".
            synthetic = {}
            for col in _feature_cols:
                if col.startswith("home_"):
                    if last_home is not None and col in last_home.index:
                        synthetic[col] = float(last_home[col])
                    else:
                        synthetic[col] = 0.0
                elif col.startswith("away_"):
                    if last_away is not None and col in last_away.index:
                        synthetic[col] = float(last_away[col])
                    else:
                        synthetic[col] = 0.0
                else:
                    # features que não são home_/away_ (ex.: rank_diff) podem ficar neutras
                    synthetic[col] = 0.0

            latest_row = pd.Series(synthetic)
        else:
            latest_row = subset.iloc[-1]

        # ------------------------------
        # 1) Probabilidades do modelo RF
        # ------------------------------
        X = latest_row[_feature_cols].to_frame().T
        proba = _model.predict_proba(X)[0]
        classes = list(_model.classes_)

        prob_map = {cls: float(p) for cls, p in zip(classes, proba)}
        home_p = prob_map.get("H", 0.0)
        draw_p = prob_map.get("D", 0.0)
        away_p = prob_map.get("A", 0.0)

        total = home_p + draw_p + away_p
        if total > 0:
            home_p /= total
            draw_p /= total
            away_p /= total

        # ==========================================================================================
        # 2) λ_home / λ_away — cálculo via xG REAL usando feature_df + Poisson
        # ==========================================================================================
        lambda_home = 0.0
        lambda_away = 0.0
        p_home_xg = 0.0
        p_draw_xg = 0.0
        p_away_xg = 0.0

        if xg_ctx is not None:
            lh, la = compute_match_lambdas(home_team, away_team, xg_ctx)
            if lh is not None and la is not None:
                lambda_home = float(lh)
                lambda_away = float(la)
                p_home_xg, p_draw_xg, p_away_xg = poisson_outcome_probs(lambda_home, lambda_away)
        
        

        # ==========================================================================================
        # 3) Monta o objeto de resposta para o fixture
        # ==========================================================================================

        # Descobrir o campo de ID do jogo vindo da API
        if "id" in row.index:
            match_id_val = row["id"]
        elif "match_id" in row.index:
            match_id_val = row["match_id"]
        elif "matchId" in row.index:
            match_id_val = row["matchId"]
        else:
            match_id_val = None

        if pd.isna(match_id_val):
            match_id_val = None

        match_id_int = int(match_id_val) if match_id_val is not None else -1

         # Descobrir o campo de data vindo da API (utc_date / utcDate / date)
        if "utc_date" in row.index:
           utc_date_val = row["utc_date"]
        elif "utcDate" in row.index:
           utc_date_val = row["utcDate"]
        elif "date" in row.index:
           utc_date_val = row["date"]
        else:
           utc_date_val = None

        if pd.isna(utc_date_val):
           utc_date_val = None

        utc_date_str = str(utc_date_val) if utc_date_val is not None else ""

        fixtures_out.append(
            FixtureWithPrediction(
                utc_date=utc_date_str,
                match_id=match_id_int,
                competition_code=competition_code,
                season=int(row.get("season", season)),
                matchday=int(row.get("matchday") or 0),
                home_team=home_team,
                away_team=away_team,
                home_top_scorer_goals=float(
                    latest_row.get("home_top_scorer_goals", 0.0)
                )
                if not pd.isna(latest_row.get("home_top_scorer_goals", 0.0))
                else None,
                away_top_scorer_goals=float(
                    latest_row.get("away_top_scorer_goals", 0.0)
                )
                if not pd.isna(latest_row.get("away_top_scorer_goals", 0.0))
                else None,
                probabilities=OutcomeProbs(home=home_p, draw=draw_p, away=away_p),
                lambda_home=lambda_home,
                lambda_away=lambda_away,
                xg_probabilities=OutcomeProbs(
                    home=p_home_xg,
                    draw=p_draw_xg,
                    away=p_away_xg,
                ),
            )
        )

    return FixturesWithPredictionsResponse(fixtures=fixtures_out)


# =============================================================================
# Endpoint: treinar modelo (multi-liga, multi-temporada)
# =============================================================================


@app.post("/train_model", response_model=TrainResponse)
def train_model(req: TrainRequest):
    """
    Treina o modelo avançado usando N temporadas passadas para uma liga específica
    (competition_code). Também atualiza o modelo em memória e salva:

    - modelo genérico: MODEL_PATH
    - feature_cols: FEATURE_COLS_PATH

    Além disso, reconstrói _feature_df usando a mesma lógica de features do
    modelo avançado (build_dataset), incluindo xG Ability, ranks, etc.
    """
    global _model, _feature_cols, _feature_df

    comp = req.competition_code.upper()
    current_season = req.season if req.season is not None else get_current_season()

    seasons = get_training_seasons(current_season, req.n_past_seasons)
    print(
        f"[train_model] Treinando modelo para {comp} usando temporadas: "
        f"{seasons} (n_games={req.n_games})"
    )



    all_dfs = []
    for s in seasons:
        print(f"[train_model] Buscando partidas para {comp} season {s}...")
        try:
            df_s = fetch_competition_matches_df(
                competition_code=comp,
                season=s,
                status=None,  # pegamos todas as partidas da season
            )
            if df_s is None or df_s.empty:
                print(f"[train_model] Nenhuma partida retornada para {comp} {s}.")
                continue
            all_dfs.append(df_s)
        except FootballDataApiError as e:
            print(f"[train_model] Erro na API para {comp} {s}: {e}")
            continue

    if not all_dfs:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Nenhuma partida encontrada nas seasons {seasons} para {comp}. "
                "Verifique o subscription da API ou o competition_code."
            ),
        )

    df_train = pd.concat(all_dfs, ignore_index=True)
    print(f"[train_model] Dataset de treino combinado shape={df_train.shape}")

    # Treina o modelo avançado
    model, acc, report, _, feature_cols = train_match_outcome_model(
        df_train, n_games=req.n_games
    )

    print("[train_model] Classification report (holdout):")
    print(report)

    # Atualiza globais
    _model = model
    _feature_cols = feature_cols

    # Salva modelo genérico (último treinado) + feature cols
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    dump(_model, MODEL_PATH)
    print(f"[train_model] Modelo salvo em {MODEL_PATH}")

    with open(FEATURE_COLS_PATH, "w", encoding="utf-8") as f:
        for c in _feature_cols:
            f.write(c + "\n")
    print(f"[train_model] Feature cols salvas em {FEATURE_COLS_PATH}")

    # Reconstrói _feature_df com a MESMA lógica do advanced_model (incluindo xG)
    _, _, feat_df, _ = build_dataset(df_train, n_games=req.n_games)
    _feature_df = feat_df
    print(f"[train_model] Feature table reconstruída (build_dataset), shape={_feature_df.shape}")

    # Também salvamos um modelo específico por liga/season atual (opcional)
    league_model_path = f"models/train_league_{comp.lower()}_{current_season}.joblib"
    dump(_model, league_model_path)
    print(f"[train_model] Modelo específico da liga salvo em {league_model_path}")

    return TrainResponse(
        message="Modelo treinado com sucesso",
        competition_code=comp,
        seasons_used=seasons,
        n_games=req.n_games,
        accuracy=float(acc),
        model_path=MODEL_PATH,
        feature_cols_path=FEATURE_COLS_PATH,
    )