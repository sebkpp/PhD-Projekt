from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class TrialSlot(Base):
    __tablename__ = "trial_slot"

    trial_slot_id = Column(Integer, primary_key=True)
    trial_id = Column(Integer, ForeignKey("trial.trial_id", ondelete="CASCADE"), nullable=False)
    slot = Column(Integer, nullable=False)

    avatar_visibility_id = Column(Integer, ForeignKey("avatar_visibility.avatar_visibility_id"))

    trial = relationship("Trial", back_populates="slots")
    stimuli = relationship("TrialSlotStimulus", back_populates="slot", cascade="all, delete-orphan")
    assignments = relationship("TrialParticipantSlot", back_populates="slot", cascade="all, delete-orphan")

    __table_args__ = (
        # ein Slot pro Trial darf nur einmal existieren
        {"sqlite_autoincrement": True},
    )

    def to_dict(self):
        return {
            "trial_slot_id": self.trial_slot_id,
            "trial_id": self.trial_id,
            "slot": self.slot,
            "avatar_visibility_id": self.avatar_visibility_id,
            "stimuli": [stimulus.to_dict() for stimulus in self.stimuli],
            "assignments": [assignment.to_dict() for assignment in self.assignments]
        }