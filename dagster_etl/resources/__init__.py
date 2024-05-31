from dagster import ConfigurableResource

import httpx
from datetime import datetime, timedelta

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

class AlvoDBResource(ConfigurableResource):
    database_url: str = DATABASE_URL

    # def __init__(self, database_url: str = DATABASE_URL):
    #     self.database_url = database_url
    #     self.engine = create_engine(self.database_url)
    #     self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    # def get_session(self) -> Session:
    #     return self.SessionLocal()
