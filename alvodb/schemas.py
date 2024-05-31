from datetime import datetime

from pydantic import BaseModel

class SignalBase(BaseModel):
    name: str

class SignalCreate(SignalBase):
    pass

class DataBase(BaseModel):
    timestamp: datetime
    signal_id: int
    value: float

class DataCreate(DataBase):
    pass