from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class TrialParticipantSlot(Base):
    __tablename__ = "trial_participant_slot"

    trial_slot_id = Column(Integer, ForeignKey("trial_slot.trial_slot_id", ondelete="CASCADE"), primary_key=True)
    participant_id = Column(Integer, ForeignKey("participant.participant_id", ondelete="CASCADE"), primary_key=True)

    slot = relationship("TrialSlot", back_populates="assignments")
    participant = relationship("Participant", back_populates="trial_assignments")