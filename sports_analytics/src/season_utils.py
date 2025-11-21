from datetime import datetime
from typing import List


def get_current_season() -> int:
    """
    Return the season number for football-data.org style European seasons.

    Convention:
      - Season 2023 represents 2023/2024
      - Season 2024 represents 2024/2025

    Logic:
      - If today is between July (7) and December (12) inclusive:
          season = current year
      - If today is between January (1) and June (6) inclusive:
          season = current year - 1
    """
    today = datetime.utcnow()
    year = today.year

    if today.month >= 7:
        return year
    else:
        return year - 1


def get_training_seasons(n_past: int = 3) -> List[int]:
    """
    Return a list of seasons to be used for training, immediately before the
    current season.

    Example:
      If current season = 2025 and n_past = 3:
        -> [2024, 2023, 2022]
    """
    current = get_current_season()
    return [current - i for i in range(1, n_past + 1)]