from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from Backend.db_session import Base

from Backend.models.participant import Participant
from Backend.models.avatar_visibility import AvatarVisibility
from Backend.models.stimulus import StimuliCombination

class Trial(Base):
    __tablename__ = "trial"

    trial_id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiment.experiment_id"), nullable=False)
    trial_number = Column(Integer, nullable=False)

    participants = relationship("TrialParticipantItem", back_populates="trial")


class TrialParticipantItem(Base):
    __tablename__ = "trial_participant_item"

    trial_id = Column(Integer, ForeignKey("trial.trial_id"), primary_key=True)
    participant_id = Column(Integer, ForeignKey("participant.participant_id"), primary_key=True)
    avatar_visibility_id = Column(Integer, ForeignKey("avatar_visibility.avatar_visibility_id"), nullable=False)
    stimulus_combination_id = Column(Integer, ForeignKey("stimuli_combination.stimulus_combination_id"), nullable=False)


    trial = relationship("Trial", back_populates="participants")
    participant = relationship("Participant")
    avatar_visibility = relationship("AvatarVisibility")
    stimulus_combination = relationship("StimuliCombination", back_populates="participants")


