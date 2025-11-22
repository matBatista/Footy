"""
xg_utils.py

Utilitários para transformar "força ofensiva/defensiva" + xG Ability
em expected goals (λ_home, λ_away) e probabilidades de resultado
usando Poisson.

Compatível com Python 3.9 (sem uso de `|` em type hints).
"""

import math
from typing import Dict, Tuple


def calibrate_goal_expectancy(
    home_xg_ability: float,
    away_xg_ability: float,
    base_total_goals: float = 2.6,
    min_lambda: float = 0.05,
) -> Tuple[float, float]:
    """
    Converte métricas de "xG ability" em expected goals (λ_home, λ_away).

    Ideia:
    - Somamos as habilidades de xG (home + away) para obter um "total ability".
    - Escalamos isso para bater com um total de gols médios da liga
      (por exemplo ~ 2.6 gols por jogo).
    - Isso gera λ_home e λ_away que podem ser usados em Poisson.

    Parâmetros
    ----------
    home_xg_ability : float
        Métrica de "força ofensiva x defensiva" do mandante (já calculada no modelo).
    away_xg_ability : float
        Métrica análoga para o visitante.
    base_total_goals : float
        Total médio de gols na liga (padrão ~ 2.6).
    min_lambda : float
        Limite inferior para λ (para evitar zero exato).

    Retorna
    -------
    (lambda_home, lambda_away) : Tuple[float, float]
        Expected goals (média Poisson) para mandante e visitante.
    """
    # Evita divisão por zero
    total_ability = home_xg_ability + away_xg_ability
    if total_ability <= 0.0:
        # fallback neutro (1.3 x 1.3)
        return base_total_goals / 2.0, base_total_goals / 2.0

    scale = base_total_goals / total_ability

    lam_home = max(home_xg_ability * scale, min_lambda)
    lam_away = max(away_xg_ability * scale, min_lambda)

    return lam_home, lam_away


def poisson_pmf(k: int, lam: float) -> float:
    """
    PMF da distribuição de Poisson: P(X = k) para média lam.

    Parâmetros
    ----------
    k : int
        Número de gols.
    lam : float
        Média (expected goals).

    Retorna
    -------
    float : probabilidade P(X = k)
    """
    if lam <= 0.0:
        return 0.0
    if k < 0:
        return 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def match_outcome_probabilities(
    lambda_home: float,
    lambda_away: float,
    max_goals: int = 10,
) -> Dict[str, float]:
    """
    Calcula P(H), P(D), P(A) usando um modelo de gols Poisson independentes.

    - Gols do mandante ~ Poisson(lambda_home)
    - Gols do visitante ~ Poisson(lambda_away)

    Somamos sobre a grade 0..max_goals para aproximar as probabilidades.

    Parâmetros
    ----------
    lambda_home : float
        Expected goals do mandante.
    lambda_away : float
        Expected goals do visitante.
    max_goals : int
        Máximo de gols considerado na soma (quanto maior, mais preciso,
        mas mais lento; 8..10 é ok para uso prático).

    Retorna
    -------
    dict : { "H": prob_home_win, "D": prob_draw, "A": prob_away_win }
    """
    p_home = 0.0
    p_draw = 0.0
    p_away = 0.0

    # Pré-calcula PMFs unidimensionais
    home_p = [poisson_pmf(i, lambda_home) for i in range(max_goals + 1)]
    away_p = [poisson_pmf(j, lambda_away) for j in range(max_goals + 1)]

    # Soma sobre todas as combinações de placares
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p_ij = home_p[i] * away_p[j]
            if i > j:
                p_home += p_ij
            elif i == j:
                p_draw += p_ij
            else:
                p_away += p_ij

    # Pequeno ajuste de normalização (erro numérico)
    total = p_home + p_draw + p_away
    if total > 0:
        p_home /= total
        p_draw /= total
        p_away /= total

    return {"H": p_home, "D": p_draw, "A": p_away}