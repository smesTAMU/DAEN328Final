import pandas as pd
import json
import os
from pandas import json_normalize

RAW_PATH = "data/raw_data.json"
CLEAN_PATH = "data/cleaned_data.csv"

def load_raw_data(path: str) -> pd.DataFrame:
    """Load raw JSON and flatten nested fields like 'location'."""
    with open(path, "r") as f:
        raw_json = json.load(f)
    print(f"Loaded {len(raw_json)} records from {path}")
    return json_normalize(raw_json)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the raw dataframe."""
    print("🧼 Starting cleaning process...")

    # Lowercase column names
    df.columns = [col.lower().replace("location.", "location_") for col in df.columns]

    # Drop duplicates (safe now that nested fields are flattened)
    df = df.drop_duplicates()

    # Convert date fields
    for col in ['inspection_date', 'license_start_date', 'license_end_date']:
        if col in df.columns:
            df.loc[:, col] = pd.to_datetime(df[col], errors='coerce')

    # Convert zip/lat/long to numeric
    for col in ['zip', 'latitude', 'longitude', 'location_latitude', 'location_longitude']:
        if col in df.columns:
            df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with no inspection ID (critical)
    if 'inspection_id' in df.columns:
        df = df.dropna(subset=['inspection_id'])
        
        # Drop redundant location columns if they match the top-level ones
    if (
        'latitude' in df.columns and
        'location_latitude' in df.columns and
        df['latitude'].equals(df['location_latitude'])
    ):
        df = df.drop(columns='location_latitude')

    if (
        'longitude' in df.columns and
        'location_longitude' in df.columns and
        df['longitude'].equals(df['location_longitude'])
    ):
        df = df.drop(columns='location_longitude')


    print(f"Cleaned data: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def save_clean_data(df: pd.DataFrame, path: str) -> None:
    """Save cleaned DataFrame to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Cleaned data saved to {path}")

def main():
    df = load_raw_data(RAW_PATH)
    cleaned_df = clean_data(df)
    save_clean_data(cleaned_df, CLEAN_PATH)

if __name__ == "__main__":
    main()
