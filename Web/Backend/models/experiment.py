# models/experiment.py

from sqlalchemy import Column, Integer, String
from Backend.db_session import Base

class Experiment(Base):
    __tablename__ = 'experiment'

    experiment_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    researcher = Column(String, nullable=True)
