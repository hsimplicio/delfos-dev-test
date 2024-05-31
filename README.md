# Delfos Data Eng Test

This project consists of a FastAPI-based API and an ETL script that fetches data from the API, processes it, and loads it into a PostgreSQL database.

I opted for creating two PostgreSQL servers to represent the streaming of data. The server containing the `Fonte` database can be accessed through port `5432` and the one containing the `Alvo` database through port `5433`.

The initial data for the `Fonte` database is randomly generated at the initialization of its API.

- The chosen initial date is `2024-05-20T00:00:00`, and it can be modified `fonteapi/crud.py` on `line 15`.

## Prerequisites

- Docker
- Docker Compose
- Python 3.10 or higher

## Setup Instructions

1. **Clone the repository:**

    ```bash
    git clone https://github.com/hsimplicio/delfos-dev-test.git
    cd delfos-dev-test
    ```

2. **Create and activate a python vitual environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the requirements**

    ```bash
    pip install -r requirements.txt
    ```

4. **Build and start the Docker containers:**

    ```bash
    docker compose up --build -d
    ```

    This will set up two PostgreSQL databases and start the FastAPI server.

## Testing the Project

To test the project, follow these steps:

1. **Ensure the Docker containers are running:**

    ```bash
    docker compose up -d
    ```

2. **Run the ETL script:**

    To fetch and process data for a specific date, run the following command:

    ```bash
    python etl.py YYYY-MM-DD
    ```

    Replace `YYYY-MM-DD` with the desired date. Note: range between `2024-05-20` and `2024-05-29`.
    
    This command will:
    - Fetch data columns `power` and `wind_speed` from the API for the specified date.
    - Process the data to calculate mean, min, max, and std for each 10-minute interval.
    - Load the processed data into the second PostgreSQL database.
    
    To specify which columns to fetch, use the `--columns` parameter.

    ```bash
    python etl.py YYYY-MM-DD --columns power wind_speed ambient_temperature
    ```

4. **Verify the data:**

    You can connect to the PostgreSQL databases to verify the data using any PostgreSQL client. 

## Additional Notes

- The API is available at `http://localhost:8000`.
- The endpoint to fetch data is `/data`. The accepted query parameters are `start_timestamp`, `end_timestamp`, and `columns`.
- You can check the API documentation at `http://localhost:8000/docs`.
- The ETL script interacts with this API to fetch data, transform it, and load it into the second database.
- The project uses anonymous volumes for PostgreSQL data, so the data will not persist across `docker compose down` and `docker compose up` commands, and the pipeline can be tested with new data.

## Cleanup

To stop and remove the Docker containers, run:

```bash
docker compose down
```
