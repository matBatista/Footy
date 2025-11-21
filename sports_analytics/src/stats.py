import pandas as pd


def add_result_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column 'home_result' with values:
    - 'H' (home win)
    - 'A' (away win)
    - 'D' (draw)
    """
    df = df.copy()

    def _result(row):
        if row["home_goals"] > row["away_goals"]:
            return "H"
        elif row["home_goals"] < row["away_goals"]:
            return "A"
        else:
            return "D"

    df["home_result"] = df.apply(_result, axis=1)
    return df


def team_summary(df: pd.DataFrame, team_name: str) -> dict:
    """
    Old version: keeps only home stats.
    Kept here in case we want simple stats later.
    """
    df = add_result_column(df)

    home_matches = df[df["home_team"] == team_name]

    played = len(home_matches)
    goals_for = home_matches["home_goals"].sum()
    goals_against = home_matches["away_goals"].sum()

    wins = (home_matches["home_result"] == "H").sum()
    draws = (home_matches["home_result"] == "D").sum()
    losses = (home_matches["home_result"] == "A").sum()

    return {
        "team": team_name,
        "games_played_home": int(played),
        "goals_for_home": int(goals_for),
        "goals_against_home": int(goals_against),
        "wins_home": int(wins),
        "draws_home": int(draws),
        "losses_home": int(losses),
    }


def team_summary_full(df: pd.DataFrame, team_name: str) -> dict:
    """
    Compute stats for a team:
    - home + away games
    - goals for / against
    - wins / draws / losses
    - win/draw/loss percentages
    """
    df = add_result_column(df)

    home = df[df["home_team"] == team_name]
    away = df[df["away_team"] == team_name]

    # Home numbers
    home_played = len(home)
    home_goals_for = home["home_goals"].sum()
    home_goals_against = home["away_goals"].sum()
    home_wins = (home["home_result"] == "H").sum()
    home_draws = (home["home_result"] == "D").sum()
    home_losses = (home["home_result"] == "A").sum()

    # Away numbers
    away_played = len(away)
    away_goals_for = away["away_goals"].sum()
    away_goals_against = away["home_goals"].sum()
    # Note: from home_result POV:
    # - if home_result == 'A' -> away team won
    # - if home_result == 'D' -> draw
    # - if home_result == 'H' -> away team lost
    away_wins = (away["home_result"] == "A").sum()
    away_draws = (away["home_result"] == "D").sum()
    away_losses = (away["home_result"] == "H").sum()

    total_played = home_played + away_played
    total_goals_for = home_goals_for + away_goals_for
    total_goals_against = home_goals_against + away_goals_against
    total_wins = home_wins + away_wins
    total_draws = home_draws + away_draws
    total_losses = home_losses + away_losses

    def pct(part, whole):
        return round((part / whole) * 100, 1) if whole > 0 else 0.0

    return {
        "team": team_name,
        # Totals
        "games_played": int(total_played),
        "goals_for": int(total_goals_for),
        "goals_against": int(total_goals_against),
        "wins": int(total_wins),
        "draws": int(total_draws),
        "losses": int(total_losses),

        # Percentages
        "win_rate": pct(total_wins, total_played),
        "draw_rate": pct(total_draws, total_played),
        "loss_rate": pct(total_losses, total_played),

        # Split: home
        "games_played_home": int(home_played),
        "wins_home": int(home_wins),
        "draws_home": int(home_draws),
        "losses_home": int(home_losses),

        # Split: away
        "games_played_away": int(away_played),
        "wins_away": int(away_wins),
        "draws_away": int(away_draws),
        "losses_away": int(away_losses),
    }
