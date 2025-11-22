import pandas as pd
import numpy as np
from src.data_loader import get_data_path


def prepare_base_matches(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to finished matches, add 'result' column, sort by date.
    result: 'H' (home win), 'D' (draw), 'A' (away win)
    """
    df = df.copy()

    # Only use finished matches for training
    if "status" in df.columns:
        df = df[df["status"] == "FINISHED"]

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    def _result(row):
        if row["home_goals"] > row["away_goals"]:
            return "H"
        elif row["home_goals"] < row["away_goals"]:
            return "A"
        else:
            return "D"

    df["result"] = df.apply(_result, axis=1)
    return df


def _build_team_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a 'long' table: one row per (team, match).
    Columns: match_idx, date, team, is_home, goals_for, goals_against, result
    result is from the TEAM point of view: 1 = win, 0 = draw, -1 = loss
    """
    rows = []

    for idx, row in df.iterrows():
        # Home team perspective
        rows.append(
            {
                "match_idx": idx,
                "date": row["date"],
                "team": row["home_team"],
                "is_home": 1,
                "goals_for": row["home_goals"],
                "goals_against": row["away_goals"],
                "result": 1 if row["home_goals"] > row["away_goals"] else (0 if row["home_goals"] == row["away_goals"] else -1),
            }
        )
        # Away team perspective
        rows.append(
            {
                "match_idx": idx,
                "date": row["date"],
                "team": row["away_team"],
                "is_home": 0,
                "goals_for": row["away_goals"],
                "goals_against": row["home_goals"],
                "result": 1 if row["away_goals"] > row["home_goals"] else (0 if row["away_goals"] == row["home_goals"] else -1),
            }
        )

    team_df = pd.DataFrame(rows)
    team_df = team_df.sort_values(["team", "date"]).reset_index(drop=True)
    return team_df


def _add_rolling_form_features(team_df: pd.DataFrame, n_games: int = 5) -> pd.DataFrame:
    """
    For each team, compute rolling stats over the LAST n_games *before* the match.

    Features:
      - goals_for_avg
      - goals_against_avg
      - goal_diff_avg
      - win_rate
      - points_avg
      - momentum
      - clean_sheet_rate
      - conceded_avg
      - weighted_points (more weight to recent matches)
    """

    def _weighted_avg_points(x: np.ndarray) -> float:
        # Weighted average of points with higher weight for more recent games
        n = len(x)
        if n == 0:
            return 0.0
        weights = np.arange(1, n + 1, dtype=float)
        return float((x * weights).sum() / weights.sum())

    def _apply_group(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("date")
        # Use shift(1) so that we NEVER use current match info to build its own features
        g["goals_for_avg"] = g["goals_for"].shift(1).rolling(n_games, min_periods=1).mean()
        g["goals_against_avg"] = g["goals_against"].shift(1).rolling(n_games, min_periods=1).mean()
        g["goal_diff_avg"] = (g["goals_for"] - g["goals_against"]).shift(1).rolling(n_games, min_periods=1).mean()
        g["win_rate"] = g["result"].shift(1).eq(1).rolling(n_games, min_periods=1).mean()

        # Add advanced rolling features
        # Points: win=3, draw=1, loss=0
        g["points"] = g["result"].map({1: 3, 0: 1, -1: 0})
        g["points_avg"] = g["points"].shift(1).rolling(n_games, min_periods=1).mean()

        # Momentum = sum of last N points
        g["momentum"] = g["points"].shift(1).rolling(n_games, min_periods=1).sum()

        # Clean sheet rate: goals_against == 0
        g["clean_sheet_rate"] = g["goals_against"].shift(1).eq(0).rolling(n_games, min_periods=1).mean()

        # Conceded average
        g["conceded_avg"] = g["goals_against"].shift(1).rolling(n_games, min_periods=1).mean()

        # Weighted points form (more weight to the most recent matches)
        g["weighted_points"] = (
            g["points"]
            .shift(1)
            .rolling(n_games, min_periods=1)
            .apply(_weighted_avg_points, raw=True)
        )

        return g

    team_df = team_df.groupby("team", group_keys=False).apply(_apply_group)
    return team_df


def merge_scorer_features(feat_df: pd.DataFrame, competition_code: str = "PL") -> pd.DataFrame:
    """
    Adds player-based attacking strength for home and away teams.
    Uses top scorers data: scorers_{competition_code}.csv
    """
    scorer_path = get_data_path(f"scorers_{competition_code.lower()}.csv")

    try:
        scorers = pd.read_csv(scorer_path)
    except FileNotFoundError:
        print("Scorers file not found — run fetch_scorers.py first.")
        return feat_df

    # For each team, get the top scorer's goals
    team_max = (
        scorers.groupby("team_name")["goals"]
        .max()
        .reset_index()
        .rename(columns={"goals": "top_scorer_goals"})
    )

    # Merge into home team
    feat_df = feat_df.merge(
        team_max.rename(columns={"team_name": "home_team"}),
        on="home_team",
        how="left",
    ).rename(columns={"top_scorer_goals": "home_top_scorer_goals"})

    # Merge into away team
    feat_df = feat_df.merge(
        team_max.rename(columns={"team_name": "away_team"}),
        on="away_team",
        how="left",
    ).rename(columns={"top_scorer_goals": "away_top_scorer_goals"})

    # Replace NaN (teams without scorer info) with 0
    feat_df["home_top_scorer_goals"] = feat_df["home_top_scorer_goals"].fillna(0)
    feat_df["away_top_scorer_goals"] = feat_df["away_top_scorer_goals"].fillna(0)

    return feat_df


def build_match_feature_table(df: pd.DataFrame, n_games: int = 5) -> pd.DataFrame:
    """
    Main entrypoint:
      - takes raw matches df (from CSV or API)
      - returns df with:
          - result ('H','D','A')
          - strong features for home & away team based on last n_games.
    """
    base = prepare_base_matches(df)
    base = base.reset_index(drop=True)
    base["match_idx"] = base.index

    team_df = _build_team_long(base)
    team_df = _add_rolling_form_features(team_df, n_games=n_games)

    # Split back into home/away feature sets
    home = team_df[team_df["is_home"] == 1].copy()
    away = team_df[team_df["is_home"] == 0].copy()

    home_feats = home[
        [
            "match_idx",
            "goals_for_avg",
            "goals_against_avg",
            "goal_diff_avg",
            "win_rate",
            "points_avg",
            "momentum",
            "clean_sheet_rate",
            "conceded_avg",
            "weighted_points",
        ]
    ].rename(
        columns={
            "goals_for_avg": "home_goals_for_avg",
            "goals_against_avg": "home_goals_against_avg",
            "goal_diff_avg": "home_goal_diff_avg",
            "win_rate": "home_win_rate",
            "points_avg": "home_points_avg",
            "momentum": "home_momentum",
            "clean_sheet_rate": "home_clean_sheet_rate",
            "conceded_avg": "home_conceded_avg",
            "weighted_points": "home_weighted_points",
        }
    )

    away_feats = away[
        [
            "match_idx",
            "goals_for_avg",
            "goals_against_avg",
            "goal_diff_avg",
            "win_rate",
            "points_avg",
            "momentum",
            "clean_sheet_rate",
            "conceded_avg",
            "weighted_points",
        ]
    ].rename(
        columns={
            "goals_for_avg": "away_goals_for_avg",
            "goals_against_avg": "away_goals_against_avg",
            "goal_diff_avg": "away_goal_diff_avg",
            "win_rate": "away_win_rate",
            "points_avg": "away_points_avg",
            "momentum": "away_momentum",
            "clean_sheet_rate": "away_clean_sheet_rate",
            "conceded_avg": "away_conceded_avg",
            "weighted_points": "away_weighted_points",
        }
    )

    feat_df = (
        base
        .merge(home_feats, on="match_idx", how="left")
        .merge(away_feats, on="match_idx", how="left")
    )

    # Add scorer-based features
    feat_df = merge_scorer_features(feat_df)

    return feat_df
