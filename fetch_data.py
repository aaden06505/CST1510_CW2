"""Fetch GitHub repository data and save it as DATA/raw.csv."""

from pathlib import Path

import pandas as pd
import requests

URL = "https://api.github.com/orgs/python/repos"
PARAMS = {"per_page": 100}
RECORDS_KEY = None

RENAME = {
    "stargazers_count": "stars",
}
KEEP = [
    "name",
    "language",
    "stars",
    "forks",
    "open_issues",
    "visibility",
    "html_url",
]
MUST_HAVE = ["name", "language"]

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


def get_data(url, params):
    """Return the API's JSON reply, or None if the request fails."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Turn the records into a pandas table."""
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    """Rename columns, select columns and remove incomplete rows."""
    df = df.rename(columns=RENAME)
    df = df[KEEP]
    # Repositories without a detected language remain useful records.
    df["language"] = df["language"].fillna("Unknown")
    return df.dropna(subset=MUST_HAVE)


def save_data(df, path):
    """Save the table as a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    data = get_data(URL, PARAMS)
    if data is not None:
        table = make_table(data, RECORDS_KEY)
        table = tidy_data(table)
        print(table.head())
        save_data(table, RAW_FILE)