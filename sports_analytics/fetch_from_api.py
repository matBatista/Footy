from src.football_data_api import fetch_competition_matches_df
from src.data_loader import get_data_path


def main():
    competition_code = "PL"
    season = 2023

    print(f"Fetching matches for {competition_code} season {season}...")
    df = fetch_competition_matches_df(competition_code=competition_code, season=season)

    print(f"Fetched {len(df)} matches.")
    if df.empty:
        print("No matches returned. Check competition code, season, or API plan.")
        return

    output_path = get_data_path("matches_api.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved matches to {output_path}")


if __name__ == "__main__":
    main()