import random
from datetime import datetime, timedelta, date

from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Data


# Function to seed initial data
def create_initial_data(db: Session):
    # Check if data already exists
    if not db.scalars(select(Data).limit(1)).first():
        initial_timestamp = datetime(2024, 5, 20, 0, 0, 0)
        data = []
        print("Populating database..", end="")
        for i in range(10 * 24 * 60):  # 10 days * 24 hours * 60 minutes
            timestamp = initial_timestamp + timedelta(minutes=i)
            wind_speed = random.uniform(0, 30)  # Random wind speed between 0 and 30
            power = random.uniform(0, 100)  # Random power between 0 and 100
            ambient_temperature = random.uniform(-20, 40)  # Random temperature between -20 and 40
            item = Data(timestamp=timestamp, wind_speed=wind_speed, power=power, ambient_temperature=ambient_temperature)
            data.append(item)
        print(".")
        db.add_all(data)
        db.commit()
    print("Database populated.")


def read_data_by_id(db: Session, data_id: int):
    result = db.scalars(select(Data).where(Data.id == data_id).limit(1)).first()
    return result


def read_data(
    db: Session,
    start_timestamp: datetime | None = None,
    end_timestamp: datetime | None = None,
    columns: list[str] | None = None
):
    # Select only specified columns if provided
    if columns:
        valid_columns = [c.name for c in Data.__table__.columns]
        selected_columns = [getattr(Data, col) for col in columns if col in valid_columns]
        if not selected_columns:
            raise ValueError("Invalid column names")
        
        # Response always contains timestamp
        if Data.timestamp not in selected_columns:
            selected_columns.insert(0, Data.timestamp)
        
        stmt = select(*selected_columns)
    else:
        stmt = select(Data)

    # Filter by timestamps if any
    if start_timestamp:
        stmt = stmt.where(Data.timestamp >= start_timestamp)
    if end_timestamp:
        stmt = stmt.where(Data.timestamp < end_timestamp)

    # Execute the query, obtain list[Row]
    query = db.execute(stmt).all()

    # Transform to list[Dict]
    result = [row._mapping for row in query]

    return result
