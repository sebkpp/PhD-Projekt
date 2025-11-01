from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class TrialSlotStimulus(Base):
    __tablename__ = "trial_slot_stimulus"

    trial_slot_id = Column(Integer, ForeignKey("trial_slot.trial_slot_id", ondelete="CASCADE"), primary_key=True)
    stimulus_id = Column(Integer, ForeignKey("stimuli.stimulus_id"), primary_key=True)

    slot = relationship("TrialSlot", back_populates="stimuli")
    stimulus = relationship("Stimulus", back_populates="trial_slots")

    def to_dict(self):
        return {
            "trial_slot_id": self.trial_slot_id,
            "stimulus_id": self.stimulus_id,
            "stimulus": self.stimulus.to_dict() if self.stimulus else None
        }