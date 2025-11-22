from datetime import datetime
from typing import List


def get_current_season() -> int:
    """
    Retorna a temporada atual no padrão football-data.org (Europa).

    Convenção:
      - 2023 representa 2023/2024
      - 2024 representa 2024/2025

    Regra:
      - De julho (7) a dezembro (12): season = ano atual
      - De janeiro (1) a junho (6):   season = ano atual - 1
    """
    today = datetime.utcnow()
    year = today.year

    if today.month >= 7:
        return year
    else:
        return year - 1


def get_training_seasons(current_season: int, n_past: int = 3) -> List[int]:
    """
    Retorna uma lista de temporadas ANTERIORES à temporada atual informada.

    Exemplo:
      current_season = 2025, n_past = 3
        -> [2024, 2023, 2022]
    """
    return [current_season - i for i in range(1, n_past + 1)]