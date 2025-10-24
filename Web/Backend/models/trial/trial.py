from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class Trial(Base):
    __tablename__ = "trial"

    trial_id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiment.experiment_id"), nullable=False)
    trial_number = Column(Integer, nullable=False)
    is_finished = Column(Boolean, default=False)

    experiment = relationship("Experiment", back_populates="trials")
    handovers = relationship("Handover", back_populates="trial")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="trial")
    slots = relationship("TrialSlot", back_populates="trial", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "trial_id": self.trial_id,
            "experiment_id": self.experiment_id,
            "trial_number": self.trial_number,
            "is_finished": self.is_finished,
            "slots": [
                {
                    "trial_slot_id": slot.trial_slot_id,
                    "slot": slot.slot,
                    "stimuli": [
                        {
                            "name": stimulus.stimulus.name,
                            "stimulus_id": stimulus.stimulus.stimulus_id,
                            "stimulus_type": stimulus.stimulus.stimulus_type.type_name
                        }
                        for stimulus in getattr(slot, "stimuli", [])
                    ]
                }
                for slot in self.slots
            ]
        }