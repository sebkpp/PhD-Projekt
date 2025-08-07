from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base  # je nachdem, wie du Base definiert hast

class StimulusType(Base):
    __tablename__ = 'stimulus_type'

    stimulus_type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, nullable=False)

    stimuli = relationship("Stimulus", back_populates="stimulus_type")


class Stimulus(Base):
    __tablename__ = 'stimuli'

    stimulus_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stimulus_type_id = Column(Integer, ForeignKey('stimulus_type.stimulus_type_id'), nullable=False)

    stimulus_type = relationship("StimulusType", back_populates="stimuli")

class StimuliCombination(Base):
    __tablename__ = "stimuli_combination"

    stimulus_combination_id = Column(Integer, primary_key=True)
    combination = Column(String, unique=True, nullable=False)

    participants = relationship("TrialParticipantItem", back_populates="stimulus_combination")
    items = relationship("StimulusCombinationItem", back_populates="combination")


class StimulusCombinationItem(Base):
    __tablename__ = "stimulus_combination_item"

    stimulus_combination_id = Column(Integer, ForeignKey("stimuli_combination.stimulus_combination_id"), primary_key=True)
    stimulus_id = Column(Integer, ForeignKey("stimuli.stimulus_id"), primary_key=True)

    combination = relationship("StimuliCombination", back_populates="items")
