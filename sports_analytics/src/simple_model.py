import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def build_home_win_dataset(df: pd.DataFrame):
    """
    Build a simple dataset to predict if the home team wins.

    Features:
        - home_team (categorical)
        - away_team (categorical)

    Target:
        - home_win: 1 if home_goals > away_goals, else 0
    """
    df = df.copy()
    df["home_win"] = (df["home_goals"] > df["away_goals"]).astype(int)

    X = df[["home_team", "away_team"]]
    y = df["home_win"]

    return X, y


def train_home_win_model(df: pd.DataFrame, test_size: float = 0.3, random_state: int = 42):
    """
    Train a simple model to predict if the home team wins.

    Returns:
        - trained pipeline (preprocessing + model)
        - accuracy on test set
        - full classification report (string)
    """
    X, y = build_home_win_dataset(df)

    # Basic safety checks (tiny dataset, only one class, etc.)
    if len(df) < 4:
        raise ValueError("Not enough matches to train a model. Add more rows to matches.csv.")

    if y.nunique() < 2:
        raise ValueError("All matches have the same outcome. Need both wins and non-wins to train.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y  # keep class balance
    )

    categorical_features = ["home_team", "away_team"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "teams",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            )
        ]
    )

    model = LogisticRegression(max_iter=1000)

    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    return clf, accuracy, report


def predict_home_win_probability(model, home_team: str, away_team: str) -> float:
    """
    Given a trained model and two team names, return the probability
    that the home team wins (between 0 and 1).
    """
    data = pd.DataFrame(
        [{"home_team": home_team, "away_team": away_team}]
    )
    proba = model.predict_proba(data)[0][1]  # [0]=sample, [1]=probability of class '1' (home_win)
    return float(proba)
