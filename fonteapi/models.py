from sqlalchemy import Column, Integer, DateTime, Float

from .database import Base


class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    wind_speed = Column(Float)
    power = Column(Float)
    ambient_temperature = Column(Float)

