from datetime import datetime

from pydantic import BaseModel

class DataBase(BaseModel):
    timestamp: datetime
    wind_speed: float
    power: float
    ambient_temperature: float

class DataCreate(DataBase):
    pass

class Data(DataBase):
    id: int
    
    class Config:
        orm_mode: True
