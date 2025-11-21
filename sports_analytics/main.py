from typing import List, Optional
import os

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from joblib import load, dump

from src.data_loader import load_matches, get_data_path
from src.features import build_match_feature_table
from src.football_data_api import fetch_competition_matches_df, FootballDataApiError
from src.advanced_model import train_match_outcome_model
from src.season_utils import get_current_season, get_training_seasons


MODEL_PATH = "models/pl_advanced_model.joblib"
FEATURE_COLS_PATH = "models/pl_feature_cols.txt"
DATA_FILENAME = "matches_api.csv"


class OutcomeProbs(BaseModel):
    home_win: float
    draw: float
    away_win: float


class TeamsResponse(BaseModel):
    teams: List[str]


class Fixture(BaseModel):
    date: str
    league: Optional[str]
    home_team: str
    away_team: str
    matchday: Optional[int] = None

class FixturesResponse(BaseModel):
    fixtures: List[Fixture]


class FixtureWithPrediction(BaseModel):
    date: str
    league: Optional[str]
    home_team: str
    away_team: str
    home_top_scorer_goals: Optional[float] = None
    away_top_scorer_goals: Optional[float] = None
    probabilities: OutcomeProbs
    matchday: Optional[int] = None


class FixturesWithPredictionsResponse(BaseModel):
    fixtures: List[FixtureWithPrediction]


class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    home_top_scorer_goals: Optional[float] = None
    away_top_scorer_goals: Optional[float] = None
    probabilities: OutcomeProbs


class TrainRequest(BaseModel):
    competition_code: str = "PL"
    n_past_seasons: int = 3


class TrainResponse(BaseModel):
    competition_code: str
    current_season: int
    training_seasons: List[int]
    accuracy: float
    n_matches: int
    message: str
    generic_model_path: str
    league_model_path: str

app = FastAPI(title="Footy Analytics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois podemos restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None
_feature_cols: Optional[List[str]] = None
_feature_df: Optional[pd.DataFrame] = None


def _load_feature_cols() -> List[str]:
    if not os.path.exists(FEATURE_COLS_PATH):
        raise RuntimeError(f"Feature columns file not found: {FEATURE_COLS_PATH}")
    with open(FEATURE_COLS_PATH) as f:
        cols = [line.strip() for line in f if line.strip()]
    return cols


@app.on_event("startup")
def startup_event():
    """Load model and data once when the API starts."""
    global _model, _feature_cols, _feature_df

    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")

    _model = load(MODEL_PATH)
    _feature_cols = _load_feature_cols()

    df = load_matches(DATA_FILENAME)
    _feature_df = build_match_feature_table(df, n_games=5)

    print(f"Loaded model with classes: {_model.classes_}")
    print(f"Feature columns: {_feature_cols}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/teams", response_model=TeamsResponse)
def get_teams():
    """
    Return the list of distinct teams present in the loaded dataset.
    This is useful for frontends to know the exact team names to use in /predict.
    """
    if _feature_df is None:
        raise HTTPException(status_code=500, detail="Features not loaded")

    home_teams = set(_feature_df["home_team"].unique())
    away_teams = set(_feature_df["away_team"].unique())
    teams = sorted(home_teams.union(away_teams))

    return TeamsResponse(teams=teams)


@app.get("/fixtures", response_model=FixturesResponse)
def get_fixtures(
    competition_code: str = Query("PL", description="Competition code, e.g. 'PL'"),
    season: Optional[int] = Query(
        None, description="Season year, e.g. 2023. If omitted, current season is used."
    ),
):
    """
    Return upcoming scheduled fixtures for a given competition using the live API.
    This does NOT rely on the local CSV, it calls the football-data.org API directly.
    """
    try:
        df = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season,
            status="SCHEDULED",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Error fetching fixtures from upstream API: {e}"
        )

    if df.empty:
        return FixturesResponse(fixtures=[])

    fixtures: List[Fixture] = []
    for _, row in df.sort_values("date").iterrows():
        fixtures.append(
            Fixture(
                date=str(row["date"]),
                league=row.get("league"),
                home_team=row["home_team"],
                away_team=row["away_team"],
                matchday=row.get("matchday"),
            )
        )

    return FixturesResponse(fixtures=fixtures)


@app.get("/fixtures_with_predictions", response_model=FixturesWithPredictionsResponse)
def get_fixtures_with_predictions(
    competition_code: str = Query("PL", description="Competition code, e.g. 'PL'"),
    season: Optional[int] = Query(
        None, description="Season year, e.g. 2023. If omitted, current season is used."
    ),
):
    """
    Return upcoming fixtures for a competition along with model predictions (H/D/A probabilities)
    based on the current form of each team.
    """
    if _model is None or _feature_df is None or _feature_cols is None:
        raise HTTPException(status_code=500, detail="Model or features not loaded")

    try:
        df_fixtures = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season,
            status="SCHEDULED",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error fetching fixtures from upstream API: {e}",
        )

    if df_fixtures.empty:
        return FixturesWithPredictionsResponse(fixtures=[])

    # Helper to get the latest feature values for a team when it plays as 'home' in our synthetic match
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

        away_rows = _feature_df[_feature_df["away_team"] == team_name].sort_values("date")
        if away_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No historical matches found for team {team_name}.",
            )
        last = away_rows.iloc[-1]
        return {
            "home_goals_for_avg": float(last["away_goals_for_avg"]),
            "home_goals_against_avg": float(last["away_goals_against_avg"]),
            "home_goal_diff_avg": float(last["away_goal_diff_avg"]),
            "home_win_rate": float(last["away_win_rate"]),
            "home_top_scorer_goals": float(last.get("away_top_scorer_goals", 0.0)),
        }

    # Helper to get the latest feature values for a team when it plays as 'away' in our synthetic match
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
                detail=f"No historical matches found for team {team_name}.",
            )
        last = home_rows.iloc[-1]
        return {
            "away_goals_for_avg": float(last["home_goals_for_avg"]),
            "away_goals_against_avg": float(last["home_goals_against_avg"]),
            "away_goal_diff_avg": float(last["home_goal_diff_avg"]),
            "away_win_rate": float(last["home_win_rate"]),
            "away_top_scorer_goals": float(last.get("home_top_scorer_goals", 0.0)),
        }

    fixtures_with_pred: List[FixtureWithPrediction] = []

    for _, row in df_fixtures.sort_values("date").iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]

        try:
            home_vals = _get_home_role_features(home_team)
            away_vals = _get_away_role_features(away_team)
        except HTTPException as e:
            # If we have no historical data for this team, skip this fixture
            if e.status_code == 404:
                continue
            # Other errors should still bubble up
            raise

        X_row = {}
        for col in _feature_cols:
            if col.startswith("home_"):
                X_row[col] = home_vals[col]
            elif col.startswith("away_"):
                X_row[col] = away_vals[col]
            else:
                X_row[col] = 0.0

        X = pd.DataFrame([X_row])
        proba = _model.predict_proba(X)[0]
        classes = list(_model.classes_)
        prob_map = {cls: float(p) for cls, p in zip(classes, proba)}

        home_p = prob_map.get("H", 0.0)
        draw_p = prob_map.get("D", 0.0)
        away_p = prob_map.get("A", 0.0)

        fixtures_with_pred.append(
            FixtureWithPrediction(
                date=str(row["date"]),
                league=row.get("league"),
                home_team=home_team,
                away_team=away_team,
                home_top_scorer_goals=home_vals["home_top_scorer_goals"],
                away_top_scorer_goals=away_vals["away_top_scorer_goals"],
                probabilities=OutcomeProbs(
                    home_win=home_p,
                    draw=draw_p,
                    away_win=away_p,
                ),
                matchday=row.get("matchday"),
            )
        )

    return FixturesWithPredictionsResponse(fixtures=fixtures_with_pred)


@app.get("/predict", response_model=PredictionResponse)
def predict(
    home_team: str = Query(
        ..., description="Home team name as in the data, e.g., 'Arsenal FC'"
    ),
    away_team: str = Query(
        ..., description="Away team name as in the data, e.g., 'Chelsea FC'"
    ),
):
    """
    Predict match outcome probabilities (H/D/A) based on latest available form
    and scorer-based features from historical matches.
    """
    if _model is None or _feature_df is None or _feature_cols is None:
        raise HTTPException(status_code=500, detail="Model or features not loaded")

    subset = _feature_df[
        (_feature_df["home_team"] == home_team)
        & (_feature_df["away_team"] == away_team)
    ].sort_values("date")

    if subset.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No historical matches found for {home_team} vs {away_team}. "
                f"Check team names (exact as in API)."
            ),
        )

    latest_row = subset.iloc[-1]
    X = latest_row[_feature_cols].to_frame().T

    proba = _model.predict_proba(X)[0]
    classes = list(_model.classes_)  # e.g. ['A','D','H']

    prob_map = {cls: float(p) for cls, p in zip(classes, proba)}

    home_p = prob_map.get("H", 0.0)
    draw_p = prob_map.get("D", 0.0)
    away_p = prob_map.get("A", 0.0)

    return PredictionResponse(
        home_team=home_team,
        away_team=away_team,
        home_top_scorer_goals=float(latest_row.get("home_top_scorer_goals", 0.0)),
        away_top_scorer_goals=float(latest_row.get("away_top_scorer_goals", 0.0)),
        probabilities=OutcomeProbs(
            home_win=home_p,
            draw=draw_p,
            away_win=away_p,
        ),
    )


@app.get("/predict_by_form", response_model=PredictionResponse)
def predict_by_form(
    home_team: str = Query(
        ..., description="Home team name as in the data, e.g., 'Arsenal FC'"
    ),
    away_team: str = Query(
        ..., description="Away team name as in the data, e.g., 'Chelsea FC'"
    ),
):
    """
    Predict match outcome probabilities (H/D/A) based on the *current form* of each team,
    without requiring a direct recent head-to-head match between them.
    """
    if _model is None or _feature_df is None or _feature_cols is None:
        raise HTTPException(status_code=500, detail="Model or features not loaded")

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

        away_rows = _feature_df[_feature_df["away_team"] == team_name].sort_values("date")
        if away_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No historical matches found for team {team_name}.",
            )
        last = away_rows.iloc[-1]
        return {
            "home_goals_for_avg": float(last["away_goals_for_avg"]),
            "home_goals_against_avg": float(last["away_goals_against_avg"]),
            "home_goal_diff_avg": float(last["away_goal_diff_avg"]),
            "home_win_rate": float(last["away_win_rate"]),
            "home_top_scorer_goals": float(last.get("away_top_scorer_goals", 0.0)),
        }

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
                detail=f"No historical matches found for team {team_name}.",
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

    X_row = {}
    for col in _feature_cols:
        if col.startswith("home_"):
            X_row[col] = home_vals[col]
        elif col.startswith("away_"):
            X_row[col] = away_vals[col]
        else:
            X_row[col] = 0.0

    X = pd.DataFrame([X_row])

    proba = _model.predict_proba(X)[0]
    classes = list(_model.classes_)
    prob_map = {cls: float(p) for cls, p in zip(classes, proba)}

    home_p = prob_map.get("H", 0.0)
    draw_p = prob_map.get("D", 0.0)
    away_p = prob_map.get("A", 0.0)

    return PredictionResponse(
        home_team=home_team,
        away_team=away_team,
        home_top_scorer_goals=home_vals["home_top_scorer_goals"],
        away_top_scorer_goals=away_vals["away_top_scorer_goals"],
        probabilities=OutcomeProbs(
            home_win=home_p,
            draw=draw_p,
            away_win=away_p,
        ),
    )


@app.post("/train_model", response_model=TrainResponse)
def train_model(req: TrainRequest):
    """
    Train (or retrain) the model for a given competition using the previous
    n_past_seasons before the current season. Updates the in-memory model and
    feature table used by the prediction endpoints.
    """
    global _model, _feature_cols, _feature_df

    if req.n_past_seasons <= 0:
        raise HTTPException(status_code=400, detail="n_past_seasons must be positive.")

    current_season = get_current_season()
    training_seasons = [
        s for s in get_training_seasons(req.n_past_seasons) if s < current_season
    ]

    if not training_seasons:
        raise HTTPException(status_code=400, detail="No valid training seasons computed.")

    df_list = []
    try:
        for season in training_seasons:
            df_season = fetch_competition_matches_df(
                competition_code=req.competition_code,
                season=season,
                status="FINISHED",
            )
            if df_season.empty:
                continue
            df_season["season"] = season
            df_list.append(df_season)
    except FootballDataApiError:
        # Trata erro de permissão/plano da football-data.org
        raise HTTPException(
            status_code=502,
            detail=(
                "Upstream football-data API denied access for this competition/season "
                "(likely subscription/plan limitation). "
                "Try with fewer seasons, another competition, or review your API key plan."
            ),
        )

    if not df_list:
        raise HTTPException(
            status_code=400,
            detail=(
                "No data fetched for requested seasons. This may be due to API plan "
                "restrictions for the selected competition or season range."
            ),
        )

    df_all = pd.concat(df_list, ignore_index=True)
    # build league/season specific model path, e.g. models/train_league_bsa_2025.joblib
    league_model_path = f"models/train_league_{req.competition_code.lower()}_{current_season}.joblib"

    # salva CSV combinado (opcional)
    try:
        out_path = get_data_path("matches_api.csv")
    except Exception:
        out_path = "matches_api.csv"

    # treina modelo
    model, acc, _, _, feature_cols = train_match_outcome_model(df_all)

    # salva modelo genérico (ativo) + colunas de features
    dump(model, MODEL_PATH)
    with open(FEATURE_COLS_PATH, "w") as f:
        for col in feature_cols:
            f.write(col + "\n")

    # salva também um modelo específico por liga/season
    try:
        dump(model, league_model_path)
    except Exception:
        # não quebrar o fluxo se o save específico falhar
        pass

    # atualiza objetos em memória
    _model = model
    _feature_cols = feature_cols
    _feature_df = build_match_feature_table(df_all, n_games=5)

    return TrainResponse(
        competition_code=req.competition_code,
        current_season=current_season,
        training_seasons=training_seasons,
        accuracy=float(acc),
        n_matches=len(df_all),
        message="Model trained and loaded successfully.",
        generic_model_path=MODEL_PATH,
        league_model_path=league_model_path,
    )