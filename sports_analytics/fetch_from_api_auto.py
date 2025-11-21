# fetch_from_api_auto.py
import pandas as pd

from src.football_data_api import fetch_competition_matches_df
from src.data_loader import get_data_path
from src.season_utils import get_current_season, get_training_seasons


def main():
    competition_code = "PL"  # mais pra frente dá pra parametrizar por env/config

    current_season = get_current_season()
    train_seasons = get_training_seasons(n_past=3)

    print(f"Current season (for prediction): {current_season}")
    print(f"Training seasons for {competition_code}: {train_seasons}")

    dfs: list[pd.DataFrame] = []

    for season in train_seasons:
        print(f"Fetching {competition_code} season {season}...")
        df_season = fetch_competition_matches_df(
            competition_code=competition_code,
            season=season,
            status="FINISHED",
        )
        if df_season.empty:
            print(f"  -> no matches returned for season {season}")
            continue

        df_season["season"] = season
        dfs.append(df_season)

    if not dfs:
        print("No data fetched for any training season. Aborting.")
        return

    df_all = pd.concat(dfs, ignore_index=True)
    print(f"Total matches across seasons {train_seasons}: {len(df_all)}")

    output_path = get_data_path("matches_api.csv")
    df_all.to_csv(output_path, index=False)
    print(f"Saved combined training data to {output_path}")


if __name__ == "__main__":
    main()