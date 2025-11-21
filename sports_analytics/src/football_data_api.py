import os
from typing import Optional, Dict, Any

import requests
import pandas as pd


BASE_URL = "https://api.football-data.org/v4"
DEFAULT_COMPETITION_CODE = "PL"


class FootballDataApiError(Exception):
    """Custom exception for Football-Data.org API errors."""
    pass


def _get_api_token() -> str:
    token = os.getenv("FOOTBALL_DATA_API_TOKEN")
    if not token:
        raise FootballDataApiError(
            "FOOTBALL_DATA_API_TOKEN not set in environment. "
            "Export it in your shell, e.g.: export FOOTBALL_DATA_API_TOKEN='YOUR_TOKEN'"
        )
    return token


def _build_headers() -> Dict[str, str]:
    token = _get_api_token()
    return {
        "X-Auth-Token": token,
        "Accept": "application/json",
    }


def fetch_competition_matches_raw(
    competition_code: str = DEFAULT_COMPETITION_CODE,
    season: Optional[int] = None,
    status: Optional[str] = "FINISHED",
) -> Dict[str, Any]:
    """
    Call /v4/competitions/{code}/matches and return raw JSON.
    """
    url = f"{BASE_URL}/competitions/{competition_code}/matches"
    params: Dict[str, Any] = {}

    if season is not None:
        params["season"] = season
    if status is not None:
        params["status"] = status

    response = requests.get(url, headers=_build_headers(), params=params, timeout=15)

    if response.status_code != 200:
        raise FootballDataApiError(
            f"API request failed ({response.status_code}): {response.text}"
        )

    return response.json()


def matches_json_to_df(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Normalize the matches JSON into a DataFrame with:

    - date
    - league
    - home_team
    - away_team
    - home_goals
    - away_goals
    - status
    """
    matches = json_data.get("matches", [])
    if not matches:
        return pd.DataFrame(
            columns=[
                "date",
                "league",
                "home_team",
                "away_team",
                "home_goals",
                "away_goals",
                "status",
            ]
        )

    league_code = json_data.get("competition", {}).get("code")

    rows = []
    for m in matches:
        date = m.get("utcDate")
        status = m.get("status")

        home_team = m.get("homeTeam", {}).get("name")
        away_team = m.get("awayTeam", {}).get("name")

        full_time = m.get("score", {}).get("fullTime", {})
        home_goals = full_time.get("home")
        away_goals = full_time.get("away")

        rows.append(
            {
                "date": date,
                "league": league_code,
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "status": status,
            }
        )

    return pd.DataFrame(rows)


def fetch_competition_matches_df(
    competition_code: str = DEFAULT_COMPETITION_CODE,
    season: Optional[int] = None,
    status: Optional[str] = "FINISHED",
) -> pd.DataFrame:
    json_data = fetch_competition_matches_raw(
        competition_code=competition_code,
        season=season,
        status=status,
    )
    return matches_json_to_df(json_data)