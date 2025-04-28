# Chicago Food Inspection Data Pipeline

This project builds a complete data pipeline for Chicago food inspection data. It extracts data in JSON format from the Chicago Data Portal API, transforms and cleans the data, saves it into a cleaned CSV file, loads the cleaned data into a PostgreSQL database, and finally visualizes the data through a Streamlit dashboard.

## Table of Contents

- [About](#about)
- [Architecture](#architecture)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Usage](#usage)
- [Services](#services)
- [PostgreSQL Setup](#postgresqlsetup)
- [Streamlit](#streamlit)
- [Contributors](#contributors)

## About

This project automates the ETL (Extract, Transform, Load) process for Chicago food inspection data. After cleaning and standardizing the data, it is stored in a PostgreSQL database for efficient querying and analysis. A Streamlit web application provides an easy-to-use dashboard to visualize inspection results.

## Architecture

- **ETL Service**: Extracts data from the Chicago Data Portal API, transforms and cleans the dataset, and saves it to a CSV.
- **PostgreSQL Service**: A relational database where the cleaned data is loaded and stored.
- **Streamlit Service**: A web application that queries the PostgreSQL database and displays key insights through interactive visualizations.

Each service runs inside its own Docker container.

## Environment Variables

You must configure a `.env` file in the project root.  
An example file is provided as `.env.sample`.

Here are the variables you need to set:

| Variable      | Description                                  | Example Value                         |
|---------------|----------------------------------------------|---------------------------------------|
| `API_URL`     | Public API endpoint for food inspections     | `https://data.cityofchicago.org/resource/4ijn-s7e5.json` |
| `DB_HOST`     | Hostname for PostgreSQL (usually `db`)        | `db`                                  |
| `DB_PORT`     | Port number for PostgreSQL                   | `5432`                                |
| `DB_NAME`     | Database name                                | `database_name`                         |
| `DB_USER`     | Database username                            | `username`                            |
| `DB_PASSWORD` | Database password                            | `password`                            |

**Steps:**
1. Copy `.env.sample` and create a `.env` file:
    ```bash
    cp .env.sample .env
    ```
2. Fill in the necessary fields in `.env`.  
Example `.env`:

    ```bash
    API_URL="https://data.cityofchicago.org/resource/4ijn-s7e5.json"
    DB_NAME=database_name
    DB_USER=usernmae
    DB_PASSWORD=password
    DB_HOST=db
    DB_PORT=5432
    ```

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/chicago-food-inspection-pipeline.git
    ```

2. Navigate into the project directory:
    ```bash
    cd chicago-food-inspection-pipeline
    ```

3. Build and start all services using Docker Compose:
    ```bash
    docker compose up --build
    ```

Docker will pull/build the images for:
- ETL process
- PostgreSQL database
- Streamlit dashboard

## Usage

- After running `docker compose up --build`, the ETL service will automatically extract, transform, and load the data.
- PostgreSQL will be populated with the cleaned inspection data.
- Access the Streamlit dashboard in your browser at:
    ```
    http://localhost:8501
    ```

Make sure Docker Desktop and Postgres is running before starting the services.

## Services

| Service      | Description                                                  | Port |
|--------------|--------------------------------------------------------------|------|
| ETL          | Data extraction, transformation, and loading to PostgreSQL   | N/A  |
| PostgreSQL   | Relational database storing cleaned data                     | 5432 |
| Streamlit    | Interactive dashboard for data visualization                 | 8501 |

## PostgreSQL Setup

This project uses a PostgreSQL database container to store the cleaned food inspection data.

### Configuration

The PostgreSQL container is configured with the following settings:

| Setting        | Value (default)            |
|----------------|-----------------------------|
| Database Name  | `inspections`               |
| Username       | `postgres`                  |
| Password       | `postgres`                  |
| Hostname       | `db` (Docker service name)  |
| Port           | `5432`                      |

These settings are defined inside the `.env` file.  
Make sure your `.env` file matches these values unless you intentionally change them.

### Notes

- The ETL service connects to the database using the `DB_HOST=db` hostname.  
  (`db` refers to the PostgreSQL container name defined in the `docker-compose.yml` file.)
- The Streamlit app connects to the same database using the same credentials.
- The database is exposed internally within the Docker network.  
  (By default, it is **not accessible externally** unless you modify the `docker-compose.yml`.)

### Database Tables

Upon running the ETL service, two tables are created `inspections` and `facilities` which are automatically created (if they doesn't exist), and cleaned data is inserted into these tables.

You can query the database manually using any PostgreSQL client if needed.

Example SQL query:

```sql
SELECT * FROM inspections LIMIT 10;
```


## Streamlit 
<img width="1470" alt="Screenshot 2025-04-28 at 5 15 33 PM" src="https://github.com/user-attachments/assets/5fdf329d-ab73-416b-9230-f997a818c676" />

## Contributors
Zain Bharde:
- Dockerized the ETL pipeline and Streamlit dashboard
- Contributed to slide deck for presentation
- Created README
