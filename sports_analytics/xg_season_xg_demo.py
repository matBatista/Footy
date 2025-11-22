"""
xg_season_xg_demo.py

Script de demonstração para:
- Carregar uma temporada de uma liga (via API ou CSV).
- Construir a feature table usando advanced_model.build_dataset.
- Calcular λ_home / λ_away (expected goals) com base em home_xg_ability / away_xg_ability.
- Mostrar estatísticas e exemplos de probabilidades de resultado.

Uso:
    source venv/bin/activate
    python xg_season_xg_demo.py
"""

import os
from typing import Tuple

import pandas as pd

from src.advanced_model import build_dataset
from src.xg_utils import calibrate_goal_expectancy, match_outcome_probabilities
from src.football_data_api import fetch_competition_matches_df


def load_season_df(competition_code: str, season: int) -> pd.DataFrame:
    """
    Carrega dados de uma temporada usando a football-data API.
    Pressupõe FOOTBALL_DATA_API_TOKEN definido no ambiente.
    """
    print(f"Carregando dados para {competition_code} - season {season}...")
    df = fetch_competition_matches_df(
        competition_code=competition_code,
        season=season,
        status="FINISHED",
    )
    print(f"Total de partidas carregadas: {len(df)}")
    return df


def build_xg_table(
    competition_code: str,
    season: int,
    n_games: int = 5,
) -> pd.DataFrame:
    """
    Constrói uma tabela contendo, para cada jogo:
    - features usadas pelo modelo
    - home_xg_ability / away_xg_ability (vindos de advanced_model)
    - λ_home / λ_away (expected goals)
    - probabilidade de H/D/A (Poisson)
    """
    df = load_season_df(competition_code, season)

    # build_dataset já chama build_match_feature_table internamente
    # e já calcula home_xg_ability / away_xg_ability.
    _, _, feat_df, _ = build_dataset(df, n_games=n_games)

    # Garante que as colunas existem (devem existir com o advanced_model atual)
    if "home_xg_ability" not in feat_df.columns or "away_xg_ability" not in feat_df.columns:
        raise ValueError(
            "home_xg_ability / away_xg_ability não encontradas em feat_df. "
            "Verifique se advanced_model.build_dataset está atualizado."
        )

    lambda_home_list = []
    lambda_away_list = []
    p_home_list = []
    p_draw_list = []
    p_away_list = []

    for _, row in feat_df.iterrows():
        home_xg_ability = float(row["home_xg_ability"])
        away_xg_ability = float(row["away_xg_ability"])

        lam_home, lam_away = calibrate_goal_expectancy(
            home_xg_ability=home_xg_ability,
            away_xg_ability=away_xg_ability,
            base_total_goals=2.6,  # pode ajustar por liga
        )

        probs = match_outcome_probabilities(
            lambda_home=lam_home,
            lambda_away=lam_away,
            max_goals=8,
        )

        lambda_home_list.append(lam_home)
        lambda_away_list.append(lam_away)
        p_home_list.append(probs["H"])
        p_draw_list.append(probs["D"])
        p_away_list.append(probs["A"])

    feat_df = feat_df.copy()
    feat_df["lambda_home"] = lambda_home_list
    feat_df["lambda_away"] = lambda_away_list
    feat_df["p_home"] = p_home_list
    feat_df["p_draw"] = p_draw_list
    feat_df["p_away"] = p_away_list

    return feat_df


def main():
    # Ajuste aqui a liga/temporada que você quer testar
    competition_code = "BSA"
    season = 2025
    n_games = 5

    # Apenas valida se o token está presente
    if not os.environ.get("FOOTBALL_DATA_API_TOKEN"):
        print(
            "ATENÇÃO: FOOTBALL_DATA_API_TOKEN não encontrado no ambiente.\n"
            "Defina o token antes de rodar este script.\n"
        )
        return

    feat_df = build_xg_table(competition_code, season, n_games=n_games)

    print("\n==============================")
    print(f"Estatísticas de expected goals - {competition_code} {season}")
    print("==============================")

    print(
        "Média λ_home: {:.3f} | λ_away: {:.3f} | Total: {:.3f}".format(
            feat_df["lambda_home"].mean(),
            feat_df["lambda_away"].mean(),
            (feat_df["lambda_home"] + feat_df["lambda_away"]).mean(),
        )
    )

    # Se tivermos colunas de gols reais, podemos comparar
    goal_cols = {"home_goals", "away_goals"}
    if goal_cols.issubset(feat_df.columns):
        total_goals_real = (feat_df["home_goals"] + feat_df["away_goals"]).mean()
        print("Média de gols reais por jogo: {:.3f}".format(total_goals_real))

    # Mostra alguns exemplos de jogos
    print("\nAlguns exemplos de jogos com λ e probabilidades:")
    sample = feat_df.head(10)

    cols_to_show = [
        "home_team",
        "away_team",
        "lambda_home",
        "lambda_away",
        "p_home",
        "p_draw",
        "p_away",
    ]
    available = [c for c in cols_to_show if c in sample.columns]

    print(sample[available].to_string(index=False))


if __name__ == "__main__":
    main()