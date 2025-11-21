import os
import pandas as pd


def get_data_path(filename: str = "matches.csv") -> str:
    """Return absolute path to a file in the data/ folder."""
    base_dir = os.path.dirname(os.path.dirname(__file__))  # project root
    return os.path.join(base_dir, "data", filename)


def load_matches(filename: str = "matches.csv") -> pd.DataFrame:
    """
    Load match data from CSV into a pandas DataFrame.
    """
    path = get_data_path(filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)

    # Minimal required columns (extra columns are ok)
    expected_cols = {
        "date",
        "league",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals",
    }
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")

    return df