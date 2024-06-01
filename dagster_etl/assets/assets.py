from dagster import asset, AssetExecutionContext
import pandas as pd

from alvodb import start, crud, database, models, schemas
from dagster_etl.definitions import daily_partitions_def
from dagster_etl.resources import FonteAPIResource, AlvoDBResource

@asset(partitions_def=daily_partitions_def)
def fetch_data(
    context: AssetExecutionContext,
    fonte_conn: FonteAPIResource
) -> list:
    """
    This asset fetch 1-minute interval data
    for a specific day from the Fonte database using its API
    """
    partition_date_str = context.partition_key
    data = fonte_conn.get(partition_date_str)
    return data


@asset(partitions_def=daily_partitions_def)
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

@asset(partitions_def=daily_partitions_def)
def load_data(
    transform_data: pd.DataFrame,
    alvo_conn: AlvoDBResource
):
    """
    This asset loads the transformed data
    into two tables of Alvo database
    """
    # start.init_tables(transform_data.columns.values.tolist())
    alvo_conn.init_tables(transform_data.columns.values.tolist())

    df = transform_data
    
    # db = next(database.get_db())
    # signal_ids = {signal.name: signal.id for signal in crud.read_all_signals(db)}
    signal_ids = {signal.name: signal.id for signal in alvo_conn.read_all_signals()}
    
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
                # crud.create_data(db, data_entry)
                alvo_conn.create_data(data_entry)
    
    # db.close()
