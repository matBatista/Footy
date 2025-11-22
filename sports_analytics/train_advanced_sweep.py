"""
Treino exploratório para avaliar o impacto de n_games nas features de forma.

Uso:
    python train_advanced_sweep.py

Por padrão, testa n_games em [3, 5, 7, 10] para uma liga/temporada específica.
Ajuste competition_code e season conforme necessário.
"""

from typing import Optional, List
from datetime import datetime

from src.football_data_api import fetch_competition_matches_df
from src.advanced_model import train_match_outcome_model


def run_sweep(
    competition_code: str = "BSA",
    season: Optional[int] = None,
    n_values: Optional[List[int]] = None,
) -> None:
    # Se não for informada, usa a temporada atual (ano corrente)
    if season is None:
        season = datetime.now().year

    if n_values is None:
        n_values = [3, 5, 7, 10]

    print(f"Carregando dados para {competition_code} - season {season}...")
    df = fetch_competition_matches_df(competition_code=competition_code, season=season)

    for n in n_values:
        print("\n" + "=" * 60)
        print(f"Treinando modelo com n_games={n}")
        print("=" * 60)
        model, acc, report, _, _ = train_match_outcome_model(df, n_games=n)
        print(f"Holdout accuracy (n_games={n}): {acc:.3f}")
        print("\nClassification report:")
        print(report)


if __name__ == "__main__":
    # BSA usando a temporada atual automaticamente
    run_sweep(competition_code="BSA", season=None)