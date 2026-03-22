from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from Backend.db_session import Base

class Participant(Base):
    __tablename__ = "participant"

    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    handedness = Column(String, nullable=False)


    handovers_given = relationship("Handover", foreign_keys="[Handover.giver]", back_populates="giver_participant")
    handovers_received = relationship("Handover", foreign_keys="[Handover.receiver]", back_populates="receiver_participant")
    eye_trackings = relationship("EyeTracking", back_populates="participant")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="participant")
    trial_assignments = relationship(
        "TrialParticipantSlot",
        back_populates="participant",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "participant_id": self.participant_id,
            "age": self.age,
            "gender": self.gender,
            "handedness": self.handedness
        }

    def __repr__(self):
        return f"<Participant(id={self.participant_id}, age={self.age}, gender='{self.gender}', handedness='{self.handedness}')>"


class ParticipantResponse(BaseModel):
    participant_id: int
    age: int
    gender: str
    handedness: str

    class Config:
        orm_mode = True