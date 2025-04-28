import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from extract import fetch_all_data, save_raw_data
from transform import load_raw_data, clean_data, save_clean_data
from load import load_data

# Extract data
API_URL = os.getenv("API_URL")
if not API_URL:
    print("❌ API_URL is missing from the .env file.")
data = fetch_all_data(API_URL)
if data:
    print("Data has been saved")
    save_raw_data(data)
    
# Transform data
RAW_PATH = "data/raw_data.json"
CLEAN_PATH = "data/cleaned_data.csv"
df = load_raw_data(RAW_PATH)
cleaned_df = clean_data(df)
save_clean_data(cleaned_df, CLEAN_PATH)
print("Data has been cleaned!")

# Load Data  
# Create database engine
engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Load and clean data
df = pd.read_csv("data/cleaned_data.csv", engine="python")
df_cleaned = df.dropna(subset=["license_"])

# Create facilities table DataFrame
facilities_df = df_cleaned[[
    "license_", "dba_name", "aka_name", "facility_type", "risk",
    "address", "city", "state", "zip", "latitude", "longitude", "location_human_address"
]].copy()
facilities_df = facilities_df.rename(columns={"license_": "license_number"})
facilities_df = facilities_df.rename(columns={"location_human_address": "location"})
facilities_df["license_number"] = pd.to_numeric(facilities_df["license_number"], errors="coerce").astype("Int64")
facilities_df["zip"] = pd.to_numeric(facilities_df["zip"], errors="coerce").astype("Int64")
facilities_df["latitude"] = pd.to_numeric(facilities_df["latitude"], errors="coerce")
facilities_df["longitude"] = pd.to_numeric(facilities_df["longitude"], errors="coerce")
facilities_df = facilities_df.drop_duplicates(subset="license_number")

# Create inspections table DataFrame
inspections_df = df_cleaned[[
    "inspection_id", "license_", "inspection_date",
    "inspection_type", "risk", "results", "violations"
]].copy()
inspections_df = inspections_df.rename(columns={"license_": "license_number"})
inspections_df["inspection_id"] = pd.to_numeric(inspections_df["inspection_id"], errors="coerce").astype("Int64")
inspections_df["license_number"] = pd.to_numeric(inspections_df["license_number"], errors="coerce").astype("Int64")
inspections_df["inspection_date"] = pd.to_datetime(inspections_df["inspection_date"], errors="coerce")

# Insert into database
facilities_df.to_sql("facilities", engine, if_exists="append", index=False)
inspections_df.to_sql("inspections", engine, if_exists="append", index=False)

print("✅ ETL completed: data inserted into facilities and inspections tables.")
# df = pd.read_csv("./data/cleaned_data.csv")
# load_data(df)

# Access streamlit: http://localhost:8501
