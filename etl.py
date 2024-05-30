import httpx
import argparse
from datetime import datetime, timedelta
import pandas as pd

from alvodb import start, crud, database, models, schemas

API_URL = "http://localhost:8000/data"
ALVO_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5433/Alvo"

def fetch_data(date: str, columns: list):
    try:
        # Convert date string to datetime object
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)

        # Format dates for query parameters
        start_timestamp = start_date.isoformat()
        end_timestamp = end_date.isoformat()

        # Build the query parameters
        params = {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "columns": columns
        }

        # Send GET request to the API
        response = httpx.get(API_URL, params=params)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Extract the JSON data from the response
        data = response.json()
        return data

    except httpx.HTTPStatusError as e:
        print(f"Error fetching data: {e}")
        return None


def transform_data(data):
    df = pd.DataFrame(data)

    # Ensure the 'timestamp' column is a datetime type
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Set 'timestamp' as the DataFrame index to use df.resample()
    df.set_index('timestamp', inplace=True)

    agg_methods = ['mean', 'min', 'max', 'std']
    agg_dict = {col: agg_methods for col in df.columns.values}

    # Resample the data in 10-minute intervals and aggregate
    aggregated_data = df.resample('10min').agg(agg_dict)

    # Flat columns names. Ex: wind_speed_mean
    aggregated_data.columns = ['_'.join(col).strip() for col in aggregated_data.columns.values]

    # Reset the index to make 'timestamp' a column again
    aggregated_data.reset_index(inplace=True)

    print(aggregated_data)

    return aggregated_data


def load_data(data):
    start.init_tables()

    df = pd.DataFrame(data)
    
    db = next(database.get_db())

    signal_ids = {signal.name: signal.id for signal in db.query(models.Signal).all()}
    
    for index, row in df.iterrows():
        timestamp = row['timestamp']
        for signal in ['power', 'wind_speed', 'ambient_temperature']:
            for agg_method in ['mean', 'min', 'max', 'std']:
                column_name = f"{signal}_{agg_method}"
                if column_name in row:
                    value = row[column_name]
                    data_entry = schemas.DataCreate(
                        timestamp=timestamp,
                        signal_id=signal_ids[signal],
                        value=value,
                        aggregation_method=agg_method
                    )
                    crud.create_data(db, data_entry)


def main(date: str, columns: list):
    data = fetch_data(date, columns)

    if data:
        transformed_data = transform_data(data)
        load_data(transformed_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL script to fetch and process data from API")
    parser.add_argument("date", help="The date for which to fetch data (format: YYYY-MM-DD)")
    parser.add_argument("--columns", nargs="+", help="List of columns to fetch", default=["wind_speed", "power"])
    
    args = parser.parse_args()
    main(args.date, args.columns)
