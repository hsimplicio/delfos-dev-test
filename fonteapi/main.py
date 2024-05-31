from contextlib import asynccontextmanager
from datetime import datetime, date
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Statup tasks
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    crud.create_initial_data(db)
    db.close()
    
    yield

    # Shutdown tasks
    pass

app = FastAPI(lifespan=lifespan)


@app.get("/data")
def get_data(
    start_timestamp: Annotated[datetime | None, Query()] = None,
    end_timestamp: Annotated[datetime | None, Query()] = None,
    columns: Annotated[list[str], Query()] = None,
    db: Session = Depends(get_db)
):
    try:
        db_data = crud.read_data(db, start_timestamp, end_timestamp, columns)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return db_data


@app.get("/data/{data_id}", response_model=schemas.Data)
def get_data_by_id(data_id: int, db: Session = Depends(get_db)):
    db_data = crud.read_data_by_id(db, data_id)
    if db_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_data