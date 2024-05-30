from datetime import datetime

from pydantic import BaseModel

class SignalBase(BaseModel):
    name: str

class DataCreate(SignalBase):
    pass

class DataBase(BaseModel):
    timestamp: datetime
    signal_id: int
    value: float
    aggregation_method: str

class DataCreate(DataBase):
    pass