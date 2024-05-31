from sqlalchemy import Column, Integer, DateTime, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Signal(Base):
    __tablename__ = "signal"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Data(Base):
    __tablename__ = "data"

    timestamp = Column(DateTime, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey('signal.id'), primary_key=True)
    value = Column(Float, nullable=False)

    signal = relationship("Signal")
