from dagster import asset

from datetime import datetime, timedelta
import httpx
import pandas as pd

from alvodb import start, crud, database, models, schemas

API_URL = "http://localhost:8000/data"

@asset
def fetch_data() -> list:
    """
    This asset daily fetch 1-minute interval data
    from the Fonte database API
    """
    try:
        # Convert date string to datetime object
        start_date = datetime(2024, 5, 21)
        end_date = start_date + timedelta(days=1)

        # Format dates for query parameters
        start_timestamp = start_date.isoformat()
        end_timestamp = end_date.isoformat()

        # Build the query parameters
        params = {
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "columns": ["wind_speed", "power"]
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


@asset()
def transform_data(fetch_data: list) -> pd.DataFrame:
    """
    This asset process the data to calculate
    mean, min, max, and std for each 10-minute interval
    """
    df = pd.DataFrame(fetch_data)

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

    return aggregated_data

@asset
def load_data(transform_data: pd.DataFrame):
    """
    This asset loads the transformed data
    into two tables of Alvo database
    """
    start.init_tables(transform_data.columns.values.tolist())

    df = pd.DataFrame(transform_data)
    
    db = next(database.get_db())

    signal_ids = {signal.name: signal.id for signal in crud.read_all_signals(db)}
    
    for index, row in df.iterrows():
        timestamp = row['timestamp']
        for signal_name in signal_ids:
            if signal_name in row:
                value = row[signal_name]
                data_entry = schemas.DataCreate(
                    timestamp=timestamp,
                    signal_id=signal_ids[signal_name],
                    value=value
                )
                crud.create_data(db, data_entry)