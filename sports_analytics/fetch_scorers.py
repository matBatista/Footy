from src.football_data_players import fetch_top_scorers
from src.data_loader import get_data_path


def main():
    df = fetch_top_scorers("PL", limit=40)
    output_path = get_data_path("scorers_pl.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} scorers → {output_path}")


if __name__ == "__main__":
    main()