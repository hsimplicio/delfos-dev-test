from pydantic import Field
from dagster import ConfigurableResource

import httpx
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alvodb import crud, schemas, models


API_URL = "http://localhost:8000/data"

class FonteAPIResource(ConfigurableResource):
    api_url: str = API_URL

    def get(
        self,
        date: str,
        columns: list[str] = None
    ) -> httpx.Response:
        try:
            # Convert date string to datetime object
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)

            # Format dates for query parameters
            start_timestamp = start_date.isoformat()
            end_timestamp = end_date.isoformat()

            # Build the query parameters
            if not columns:
                columns = ["wind_speed", "power"]
            params = {
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "columns": columns
            }

            # Send GET request to the API
            response = httpx.get(self.api_url, params=params)

            # Raise an exception if the request was unsuccessful
            response.raise_for_status()

            # Extract the JSON data from the response
            data = response.json()

            return data

        except httpx.HTTPStatusError as e:
            print(f"Error fetching data: {e}")
            return None


DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5433/Alvo"

class AlvoDB:

    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_tables(self, signals: list[str]):
        # Create tables if they do not exist
        models.Base.metadata.create_all(bind=self.engine)

        # Populate signal table with the possible signals
        if "timestamp" in signals:
            signals.remove("timestamp")
        
        for signal in signals:
            db_signal = self.read_signal(signal)
            if not db_signal:
                self.create_signal(schemas.SignalCreate(name=signal))
    
    def read_signal(self, signal_name: str):
        with next(self.get_session()) as session:
            result = crud.read_signal(session, signal_name)
        return result

    def read_all_signals(self):
        with next(self.get_session()) as session:
            result = crud.read_all_signals(session)
        return result

    def create_signal(self, signal: schemas.SignalCreate):
        with next(self.get_session()) as session:
            result = crud.create_signal(session, signal)
        return result
    
    def create_data(self, data: schemas.DataCreate):
        with next(self.get_session()) as session:
            result = crud.create_data(session, data)
        return result


class AlvoDBResource(ConfigurableResource):

    database_url: str = Field(
        description=(
            "URL to connect to the database. Defaults to postgresql+psycopg2://postgres:postgres@localhost:5433/Alvo"
        ),
        default=DATABASE_URL
    )

    @property
    def alvodb(self) -> AlvoDB:
        return AlvoDB(self.database_url)

    def init_tables(self, signals: list[str]):
        """
        Create both tables and populate signal table
        """
        self.alvodb.init_tables(signals)
    
    def read_signal(self, signal_name: str):
        return self.alvodb.read_signal(signal_name)

    def read_all_signals(self):
        return self.alvodb.read_all_signals()

    def create_signal(self, signal: schemas.SignalCreate):
        return self.alvodb.create_signal(signal)
    
    def create_data(self, data: schemas.DataCreate):
        return self.alvodb.create_data(data)
    