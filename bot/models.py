from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Weather(Base):
    __tablename__ = 'weather'
    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    info = Column(Text, nullable=False)
    created_at = Column(DateTime)

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    rate = Column(String, nullable=False)
    created_at = Column(DateTime)
