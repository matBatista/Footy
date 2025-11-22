"""
Utilitários para expected goals (xG) e distribuição de gols via Poisson.

Este módulo fornece:

- calibrate_goal_expectancy: transforma "força ofensiva/defensiva" em λ_home / λ_away
- match_outcome_probabilities: retorna dict {"H","D","A"} via Poisson
- build_xg_context_from_feature_df: constrói contexto de força de ataque/defesa por time
- compute_match_lambdas: calcula λ_home / λ_away para um confronto específico
- poisson_outcome_probs: mesma lógica do match_outcome_probabilities, mas retornando tupla
"""

from __future__ import annotations

from math import exp, factorial
from typing import Dict, Tuple, Optional

import pandas as pd


# -------------------------------------------------------------------------
# Poisson helpers
# -------------------------------------------------------------------------


def _poisson_pmf(k: int, lamb: float) -> float:
    """Poisson PMF simples."""
    if lamb <= 0:
        return 0.0
    return exp(-lamb) * (lamb**k) / factorial(k)


def poisson_outcome_probs(
    lambda_home: float, lambda_away: float, max_goals: int = 8
) -> Tuple[float, float, float]:
    """
    Calcula P(H), P(D), P(A) usando distribuição de Poisson para λ_home / λ_away.

    Retorna: (p_home, p_draw, p_away)
    """
    p_home = 0.0
    p_draw = 0.0
    p_away = 0.0

    for gh in range(0, max_goals + 1):
        ph = _poisson_pmf(gh, lambda_home)
        for ga in range(0, max_goals + 1):
            pa = _poisson_pmf(ga, lambda_away)
            p = ph * pa
            if gh > ga:
                p_home += p
            elif gh == ga:
                p_draw += p
            else:
                p_away += p

    # Normaliza por segurança
    total = p_home + p_draw + p_away
    if total > 0:
        p_home /= total
        p_draw /= total
        p_away /= total

    return p_home, p_draw, p_away


def match_outcome_probabilities(
    lambda_home: float, lambda_away: float, max_goals: int = 8
) -> Dict[str, float]:
    """
    Versão em dict da função acima.
    Retorna: {"H": p_home, "D": p_draw, "A": p_away}
    """
    p_home, p_draw, p_away = poisson_outcome_probs(lambda_home, lambda_away, max_goals)
    return {"H": p_home, "D": p_draw, "A": p_away}


# -------------------------------------------------------------------------
# Calibração de λ a partir de "força" (xG ability)
# -------------------------------------------------------------------------


def calibrate_goal_expectancy(
    home_xg_ability: float,
    away_xg_ability: float,
    base_total_goals: float = 2.6,
    home_advantage: float = 1.10,
) -> Tuple[float, float]:
    """
    Dado um "score" de força para mandante e visitante, converte isso em
    λ_home / λ_away garantindo que λ_home + λ_away ≈ base_total_goals.

    - home_xg_ability, away_xg_ability ~ 1.0 é "médio".
    - home_advantage > 1.0 dá um boost extra ao mandante.
    """
    home_xg = max(home_xg_ability, 0.01)
    away_xg = max(away_xg_ability, 0.01)

    # Aplica pequeno boost de vantagem de casa
    home_xg *= home_advantage

    total_ability = home_xg + away_xg
    if total_ability <= 0:
        # fallback totalmente neutro
        return base_total_goals * 0.55, base_total_goals * 0.45

    home_share = home_xg / total_ability
    away_share = away_xg / total_ability

    lambda_home = base_total_goals * home_share
    lambda_away = base_total_goals * away_share

    return lambda_home, lambda_away


# -------------------------------------------------------------------------
# Construção de contexto xG a partir de feature_df
# -------------------------------------------------------------------------


def build_xg_context_from_feature_df(
    feat_df: pd.DataFrame,
) -> Optional[Dict]:
    """
    Constrói um contexto de xG a partir da feature table (_feature_df), que
    contém colunas agregadas por jogo:

      - home_team, away_team
      - home_goals_for_avg, away_goals_for_avg
      - home_goals_against_avg, away_goals_against_avg

    A ideia é derivar força ofensiva/defensiva relativa à média da liga.

    Retorna um dicionário:
    {
      "league_home_for": float,
      "league_away_for": float,
      "teams": {
         "Time X": {
            "att_home": float,
            "att_away": float,
            "def_home": float,
            "def_away": float,
         },
         ...
      }
    }
    """
    if feat_df is None or feat_df.empty:
        return None

    df = feat_df.copy()

    required_cols = [
        "home_team",
        "away_team",
        "home_goals_for_avg",
        "away_goals_for_avg",
        "home_goals_against_avg",
        "away_goals_against_avg",
    ]
    for c in required_cols:
        if c not in df.columns:
            # Sem colunas mínimas, não conseguimos fazer contexto de xG
            return None

    league_home_for = float(df["home_goals_for_avg"].mean())
    league_away_for = float(df["away_goals_for_avg"].mean())
    if league_home_for <= 0:
        league_home_for = 1.0
    if league_away_for <= 0:
        league_away_for = 1.0

    teams: Dict[str, Dict[str, float]] = {}

    all_teams = pd.unique(
        pd.concat([df["home_team"], df["away_team"]], ignore_index=True).dropna()
    )

    for team in all_teams:
        home_rows = df[df["home_team"] == team]
        away_rows = df[df["away_team"] == team]

        # Médias em casa
        if not home_rows.empty:
            home_for = float(home_rows["home_goals_for_avg"].mean())
            home_against = float(home_rows["home_goals_against_avg"].mean())
        else:
            home_for = league_home_for
            home_against = league_away_for

        # Médias fora
        if not away_rows.empty:
            away_for = float(away_rows["away_goals_for_avg"].mean())
            away_against = float(away_rows["away_goals_against_avg"].mean())
        else:
            away_for = league_away_for
            away_against = league_home_for

        # Força relativa à liga ( >1 = melhor ataque / defesa que média )
        att_home = home_for / league_home_for if league_home_for > 0 else 1.0
        att_away = away_for / league_away_for if league_away_for > 0 else 1.0

        # Para defesa, quanto MENOS sofre, melhor: usamos média da liga como ref.
        # Se time sofre menos que média, def_strength < 1, mas na composição
        # usamos o inverso para facilitar multiplicação.
        def_home_raw = home_against / league_away_for if league_away_for > 0 else 1.0
        def_away_raw = away_against / league_home_for if league_home_for > 0 else 1.0

        def_home = 1.0 / def_home_raw if def_home_raw > 0 else 1.0
        def_away = 1.0 / def_away_raw if def_away_raw > 0 else 1.0

        teams[team] = {
            "att_home": att_home,
            "att_away": att_away,
            "def_home": def_home,
            "def_away": def_away,
        }

    ctx = {
        "league_home_for": league_home_for,
        "league_away_for": league_away_for,
        "teams": teams,
    }
    return ctx


# -------------------------------------------------------------------------
# Cálculo de λ_home / λ_away para um confronto específico
# -------------------------------------------------------------------------


def compute_match_lambdas(
    home_team: str,
    away_team: str,
    xg_ctx: Dict,
    base_total_goals: float = 2.6,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Dado um contexto xG e dois times, estima as forças para o confronto:

      - home_xg_ability
      - away_xg_ability

    e converte em λ_home / λ_away via calibrate_goal_expectancy.

    Retorna (lambda_home, lambda_away) ou (None, None) se não tiver dados.
    """
    if xg_ctx is None:
        return None, None

    teams = xg_ctx.get("teams", {})
    if home_team not in teams or away_team not in teams:
        return None, None

    t_home = teams[home_team]
    t_away = teams[away_team]

    # Misturamos ataque em casa/fora e defesa em casa/fora com pesos simples
    home_attack_strength = 0.6 * t_home["att_home"] + 0.4 * t_home["att_away"]
    away_attack_strength = 0.6 * t_away["att_away"] + 0.4 * t_away["att_home"]

    home_defense_strength = 0.6 * t_home["def_home"] + 0.4 * t_home["def_away"]
    away_defense_strength = 0.6 * t_away["def_away"] + 0.4 * t_away["def_home"]

    # "Força total" ofensiva, já considerando defesa do oponente.
    home_xg_ability = home_attack_strength * away_defense_strength
    away_xg_ability = away_attack_strength * home_defense_strength

    lambda_home, lambda_away = calibrate_goal_expectancy(
        home_xg_ability=home_xg_ability,
        away_xg_ability=away_xg_ability,
        base_total_goals=base_total_goals,
    )

    return lambda_home, lambda_away