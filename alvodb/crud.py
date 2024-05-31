from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models, schemas


def read_signal(db: Session, signal_name: str):
    result = db.scalars(select(models.Signal).where(models.Signal.name == signal_name).limit(1)).first()
    return result

def read_all_signals(db: Session):
    result = db.scalars(select(models.Signal)).all()
    return result


def create_signal(db: Session, signal: schemas.SignalCreate):
    db_signal = models.Signal(name=signal.name)
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal


def create_data(db: Session, data: schemas.DataCreate):
    db_data = models.Data(**data.model_dump())
    db.add(db_data)
    db.commit()
    return db_data
