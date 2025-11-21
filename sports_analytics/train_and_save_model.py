import os
from joblib import dump

from src.data_loader import load_matches
from src.advanced_model import train_match_outcome_model


def main():
    df = load_matches("matches_api.csv")

    model, acc, report, _, feature_cols = train_match_outcome_model(df)

    print(f"Advanced model accuracy: {acc:.3f}")
    print("Classification report:")
    print(report)

    os.makedirs("models", exist_ok=True)

    model_path = "models/pl_advanced_model.joblib"
    meta_path = "models/pl_feature_cols.txt"

    dump(model, model_path)
    print(f"Saved model to {model_path}")

    with open(meta_path, "w") as f:
        for col in feature_cols:
            f.write(col + "\n")
    print(f"Saved feature columns to {meta_path}")


if __name__ == "__main__":
    main()