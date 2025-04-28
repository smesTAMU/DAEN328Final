# load.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def load_data(df):
    # Create database engine
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

    # Create facilities DataFrame
    facilities_df = df[[
        "license_", "dba_name", "aka_name", "facility_type", "risk",
        "address", "city", "state", "zip", "latitude", "longitude", "location_human_address"
    ]].copy()

    facilities_df = facilities_df.rename(columns={
        "license_": "license_number",
        "location_human_address": "location"
    })

    facilities_df["license_number"] = pd.to_numeric(facilities_df["license_number"], errors="coerce").astype("Int64")
    facilities_df["zip"] = pd.to_numeric(facilities_df["zip"], errors="coerce").astype("Int64")
    facilities_df["latitude"] = pd.to_numeric(facilities_df["latitude"], errors="coerce")
    facilities_df["longitude"] = pd.to_numeric(facilities_df["longitude"], errors="coerce")
    facilities_df = facilities_df.drop_duplicates(subset="license_number")

    # Create inspections DataFrame
    inspections_df = df[[
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

    print("ETL completed: data inserted into facilities and inspections tables.")
