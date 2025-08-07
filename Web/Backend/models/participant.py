from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from Backend.db_session import Base

class Participant(Base):
    __tablename__ = "participant"

    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    handedness = Column(String, nullable=False)

    def __repr__(self):
        return f"<Participant(id={self.participant_id}, age={self.age}, gender='{self.gender}', handedness='{self.handedness}')>"
