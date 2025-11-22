import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
)

from src.features import build_match_feature_table


def build_dataset(df: pd.DataFrame, n_games: int = 5):
    """
    Constrói X, y e a lista de colunas de features a partir do DataFrame bruto
    de partidas (saído do fetch_competition_matches_df).

    Usa build_match_feature_table para criar as features de forma, pontos,
    defesa, etc.

    Parâmetros
    ----------
    n_games : int
        Quantidade de jogos anteriores a considerar nas métricas de forma.
    """
    # Gera a feature table com N jogos anteriores
    feat_df = build_match_feature_table(df, n_games=n_games)

    # -------------------------------------------------
    # Attack / Defense strength (força ofensiva/defensiva)
    # -------------------------------------------------
    base_cols = {
        "home_goals_for_avg",
        "home_goals_against_avg",
        "away_goals_for_avg",
        "away_goals_against_avg",
    }
    if base_cols.issubset(feat_df.columns):
        eps = 1e-6  # evita divisão por zero

        # Médias da liga para normalização
        home_gf_mean = feat_df["home_goals_for_avg"].mean() + eps
        home_ga_mean = feat_df["home_goals_against_avg"].mean() + eps
        away_gf_mean = feat_df["away_goals_for_avg"].mean() + eps
        away_ga_mean = feat_df["away_goals_against_avg"].mean() + eps

        # Força ofensiva/defensiva normalizada (1.0 = média da liga)
        feat_df["home_attack_strength"] = (
            feat_df["home_goals_for_avg"] / home_gf_mean
        )
        feat_df["home_defense_weakness"] = (
            feat_df["home_goals_against_avg"] / home_ga_mean
        )

        feat_df["away_attack_strength"] = (
            feat_df["away_goals_for_avg"] / away_gf_mean
        )
        feat_df["away_defense_weakness"] = (
            feat_df["away_goals_against_avg"] / away_ga_mean
        )
    else:
        print(
            "[advanced_model] Aviso: não foi possível calcular attack/defense "
            f"strength, colunas base ausentes em feat_df: {base_cols - set(feat_df.columns)}"
        )

    # -------------------------------------------------
    # xG Ability fake + artilheiro normalizado
    # (Step 2 / 4 do nosso plano)
    # -------------------------------------------------
    scorer_cols = {"home_top_scorer_goals", "away_top_scorer_goals"}
    wp_cols = {"home_weighted_points", "away_weighted_points"}
    if scorer_cols.issubset(feat_df.columns) and wp_cols.issubset(feat_df.columns):
        eps = 1e-6
        # Normalização dos gols dos artilheiros (máximo da liga)
        max_scorer = max(
            float(feat_df["home_top_scorer_goals"].max() or 0.0),
            float(feat_df["away_top_scorer_goals"].max() or 0.0),
        ) + eps

        feat_df["home_top_scorer_norm"] = (
            feat_df["home_top_scorer_goals"].fillna(0.0) / max_scorer
        )
        feat_df["away_top_scorer_norm"] = (
            feat_df["away_top_scorer_goals"].fillna(0.0) / max_scorer
        )

        # Garante colunas base de força
        for col in [
            "home_attack_strength",
            "home_defense_weakness",
            "away_attack_strength",
            "away_defense_weakness",
        ]:
            if col not in feat_df.columns:
                feat_df[col] = 1.0  # neutro

        # xG Ability para o mandante (FAKE xG)
        feat_df["home_xg_ability"] = (
            feat_df["home_attack_strength"].fillna(1.0)
            * feat_df["away_defense_weakness"].fillna(1.0)
            * 0.4
            + feat_df["home_weighted_points"].fillna(0.0) * 0.3
            + feat_df["home_top_scorer_norm"].fillna(0.0) * 0.3
        )

        # xG Ability para o visitante (FAKE xG)
        feat_df["away_xg_ability"] = (
            feat_df["away_attack_strength"].fillna(1.0)
            * feat_df["home_defense_weakness"].fillna(1.0)
            * 0.4
            + feat_df["away_weighted_points"].fillna(0.0) * 0.3
            + feat_df["away_top_scorer_norm"].fillna(0.0) * 0.3
        )
    else:
        print(
            "[advanced_model] Aviso: não foi possível calcular xg_ability; "
            f"faltando colunas: {scorer_cols.union(wp_cols) - set(feat_df.columns)}"
        )

    # -------------------------------------------------
    # "Posição na tabela" aproximada (ranking por força)
    # -------------------------------------------------
    rank_base_cols = {
        "home_team",
        "away_team",
        "home_weighted_points",
        "away_weighted_points",
    }
    if rank_base_cols.issubset(feat_df.columns):
        # Construímos um "power ranking" por time, usando a média dos
        # weighted_points (mandante + visitante)
        home_perf = feat_df[["home_team", "home_weighted_points"]].rename(
            columns={"home_team": "team", "home_weighted_points": "strength"}
        )
        away_perf = feat_df[["away_team", "away_weighted_points"]].rename(
            columns={"away_team": "team", "away_weighted_points": "strength"}
        )

        team_perf = pd.concat([home_perf, away_perf], ignore_index=True)
        team_strength = team_perf.groupby("team")["strength"].mean()

        # Rank: melhor time = 1 (ascending=False)
        team_rank = team_strength.rank(ascending=False, method="min").astype(int)

        # Número de times (para normalização)
        num_teams = int(team_rank.max())

        # Mapeia de volta para a tabela de features
        feat_df["home_rank"] = feat_df["home_team"].map(team_rank)
        feat_df["away_rank"] = feat_df["away_team"].map(team_rank)

        # Posição normalizada (0 ~ topo da tabela, 1 ~ lanterna)
        feat_df["home_rank_norm"] = feat_df["home_rank"] / num_teams
        feat_df["away_rank_norm"] = feat_df["away_rank"] / num_teams

        # Diferença de posição: positivo => visitante teoricamente mais forte
        feat_df["rank_diff"] = feat_df["away_rank"] - feat_df["home_rank"]
    else:
        print(
            "[advanced_model] Aviso: não foi possível calcular ranking de tabela; "
            f"faltando colunas: {rank_base_cols - set(feat_df.columns)}"
        )

    # -------------------------------------------------
    # Seleção das features
    # -------------------------------------------------
    desired_feature_cols = [
        # home side - forma e gols
        "home_goals_for_avg",
        "home_goals_against_avg",
        "home_goal_diff_avg",
        "home_win_rate",
        "home_points_avg",
        "home_momentum",
        "home_clean_sheet_rate",
        "home_conceded_avg",
        "home_weighted_points",
        "home_top_scorer_goals",
        "home_top_scorer_norm",
        # home side - força ofensiva/defensiva e tabela
        "home_attack_strength",
        "home_defense_weakness",
        "home_xg_ability",
        "home_rank",
        "home_rank_norm",
        # away side - forma e gols
        "away_goals_for_avg",
        "away_goals_against_avg",
        "away_goal_diff_avg",
        "away_win_rate",
        "away_points_avg",
        "away_momentum",
        "away_clean_sheet_rate",
        "away_conceded_avg",
        "away_weighted_points",
        "away_top_scorer_goals",
        "away_top_scorer_norm",
        # away side - força ofensiva/defensiva e tabela
        "away_attack_strength",
        "away_defense_weakness",
        "away_xg_ability",
        "away_rank",
        "away_rank_norm",
        # diferença de posição
        "rank_diff",
    ]

    existing_cols = set(feat_df.columns)
    feature_cols = [c for c in desired_feature_cols if c in existing_cols]

    missing = [c for c in desired_feature_cols if c not in existing_cols]
    if missing:
        print(
            "[advanced_model] Aviso: as seguintes features não existem em feat_df "
            "e serão ignoradas: "
            f"{missing}"
        )

    if feature_cols:
        feat_df = feat_df.dropna(subset=feature_cols)
    else:
        raise ValueError(
            "Nenhuma feature válida encontrada em feat_df. "
            "Verifique build_match_feature_table."
        )

    X = feat_df[feature_cols]
    # resultado em 'H', 'D', 'A'
    y = feat_df["result"]

    return X, y, feat_df, feature_cols


def train_match_outcome_model(df: pd.DataFrame, n_games: int = 5):
    """
    Treina um modelo RandomForest para prever o resultado do jogo (H/D/A).

    - Usa features de forma, pontos, momentum, defesa, artilheiro,
      força ofensiva/defensiva, xG Ability (fake) e posição aproximada
      na tabela (ranking baseado em weighted_points).
    - Usa class_weight='balanced' para lidar com desbalanceamento.
    - Faz cross-validation com F1-macro (multiclasse).

    Parâmetros
    ----------
    n_games : int
        Quantidade de jogos anteriores a considerar nas métricas de forma.
        (padrão = 5)
    """
    X, y, feat_df, feature_cols = build_dataset(df, n_games=n_games)

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    # Cross-validation (se o dataset permitir)
    try:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        f1_macro_scores = cross_val_score(
            model,
            X,
            y,
            cv=cv,
            scoring="f1_macro",
            n_jobs=-1,
        )
        print(
            "RF CV F1-macro: "
            f"{f1_macro_scores.mean():.3f} +/- {f1_macro_scores.std():.3f}"
        )
    except ValueError as e:
        print(f"[advanced_model] Cross-validation skipped: {e}")

    # Holdout final
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    print("Holdout accuracy:", acc)
    print(report)

    return model, acc, report, (X_test, y_test), feature_cols