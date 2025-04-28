import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="./.env")

# Get API URL from .env
API_URL = os.getenv("API_URL")
BATCH_SIZE = 50000  # API max batch limit

def fetch_all_data(base_url: str, batch_size: int = BATCH_SIZE) -> list:
    """Fetch all records using pagination."""
    all_data = []
    offset = 0

    while True:
        params = {
            "$limit": batch_size,
            "$offset": offset
        }

        print(f"📦 Fetching rows {offset} to {offset + batch_size}...")
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            batch = response.json()
        except Exception as e:
            print(f"❌ Request failed at offset {offset}: {e}")
            break

        if not batch:
            print("No more data returned. Done!")
            break

        all_data.extend(batch)
        offset += batch_size

    print(f"\n Finished. Total records fetched: {len(all_data)}")
    return all_data

def save_raw_data(data: list, path: str = "data/raw_data.json") -> None:
    """Save full dataset to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Raw data saved to {path}")

def main():
    if not API_URL:
        print("❌ API_URL is missing from the .env file.")
        return
    data = fetch_all_data(API_URL)
    if data:
        save_raw_data(data)

if __name__ == "__main__":
    main()
