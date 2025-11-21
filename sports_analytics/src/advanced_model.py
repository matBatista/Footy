import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from src.features import build_match_feature_table

import numpy as np

def build_dataset(df: pd.DataFrame):
    feat_df = build_match_feature_table(df, n_games=5)

    # Drop matches with no rolling history
    feat_df = feat_df.dropna(
        subset=[
            "home_goals_for_avg",
            "home_goals_against_avg",
            "home_goal_diff_avg",
            "home_win_rate",
            "away_goals_for_avg",
            "away_goals_against_avg",
            "away_goal_diff_avg",
            "away_win_rate",
        ]
    )

    feature_cols = [
        "home_goals_for_avg",
        "home_goals_against_avg",
        "home_goal_diff_avg",
        "home_win_rate",
        "away_goals_for_avg",
        "away_goals_against_avg",
        "away_goal_diff_avg",
        "away_win_rate",
        "home_top_scorer_goals",
        "away_top_scorer_goals",
    ]

    X = feat_df[feature_cols]
    y = feat_df["result"]  # 'H','D','A'

    return X, y, feat_df, feature_cols


def train_match_outcome_model(df: pd.DataFrame):
    X, y, feat_df, feature_cols = build_dataset(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        shuffle=False,
    )

    classes = np.unique(y_train)
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y_train,
    )
    class_weight_dict = {cls: w for cls, w in zip(classes, class_weights)}

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
        class_weight=class_weight_dict,
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    return model, acc, report, (X_test, y_test), feature_cols