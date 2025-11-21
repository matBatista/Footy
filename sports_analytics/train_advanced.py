from src.data_loader import load_matches
from src.advanced_model import train_match_outcome_model


def main():
    df = load_matches("matches_api.csv")
    model, acc, report, _, _ = train_match_outcome_model(df)

    print(f"Advanced model accuracy: {acc:.3f}")
    print("Classification report:")
    print(report)


if __name__ == "__main__":
    main()