import requests
import pandas as pd

from src.football_data_api import BASE_URL, _build_headers


def fetch_top_scorers(competition_code: str = "PL", limit: int = 40) -> pd.DataFrame:
    """
    Fetch top scorers from football-data.org API.
    Returns a DataFrame with: player_name, team_name, goals
    """
    url = f"{BASE_URL}/competitions/{competition_code}/scorers"
    params = {"limit": limit}

    response = requests.get(url, headers=_build_headers(), params=params, timeout=10)

    if response.status_code != 200:
        raise ValueError(f"Error fetching scorers: {response.text}")

    data = response.json()
    rows = []

    for entry in data.get("scorers", []):
        player = entry.get("player", {})
        team = entry.get("team", {})
        goals = entry.get("goals")

        rows.append(
            {
                "player_name": player.get("name"),
                "team_name": team.get("name"),
                "goals": goals,
            }
        )

    return pd.DataFrame(rows)