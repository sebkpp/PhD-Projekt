from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base  # je nachdem, wie du Base definiert hast

class StimulusType(Base):
    __tablename__ = 'stimulus_type'

    stimulus_type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, nullable=False)

    stimuli = relationship("Stimulus", back_populates="stimulus_type")
    studies = relationship("StudyStimuli", back_populates="stimuli_type")

class Stimulus(Base):
    __tablename__ = 'stimuli'

    stimulus_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stimulus_type_id = Column(Integer, ForeignKey('stimulus_type.stimulus_type_id'), nullable=False)

    stimulus_type = relationship("StimulusType", back_populates="stimuli")
    stimulus_items = relationship("StimulusCombinationItem", back_populates="stimulus")
    visuals = relationship("StimulusVisual", back_populates="stimulus")
    auditives = relationship("StimulusAuditiv", back_populates="stimulus")
    tactiles = relationship("StimulusTactile", back_populates="stimulus")
    trial_slots = relationship(
        "TrialSlotStimulus",
        back_populates="stimulus",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "stimulus_id": self.stimulus_id,
            "name": self.name,
            "stimulus_type": self.stimulus_type.type_name if self.stimulus_type else None,
            "visuals": [visual.stimulus_name for visual in self.visuals],
            "auditives": [
                {
                    "frequency": auditive.frequency,
                    "volume": auditive.volume
                } for auditive in self.auditives
            ],
            "tactiles": [
                {
                    "pattern": tactile.pattern,
                    "intensity": tactile.intensity
                } for tactile in self.tactiles
            ]
        }

class StimuliCombination(Base):
    __tablename__ = "stimuli_combination"

    stimulus_combination_id = Column(Integer, primary_key=True)
    combination = Column(String, unique=True, nullable=False)

    stimulus_items = relationship("StimulusCombinationItem", back_populates="combination")

class StimulusCombinationItem(Base):
    __tablename__ = "stimulus_combination_item"

    stimulus_combination_id = Column(Integer, ForeignKey("stimuli_combination.stimulus_combination_id"), primary_key=True)
    stimulus_id = Column(Integer, ForeignKey("stimuli.stimulus_id"), primary_key=True)

    stimulus = relationship("Stimulus", back_populates="stimulus_items")
    combination = relationship("StimuliCombination", back_populates="stimulus_items")

class StimulusVisual(Base):
    __tablename__ = "stimulus_visual"

    stimulus_id = Column(Integer, ForeignKey("stimuli.stimulus_id"), primary_key=True)
    stimulus_name = Column(String(255), nullable=False)

    stimulus = relationship("Stimulus", back_populates="visuals")


class StimulusAuditiv(Base):
    __tablename__ = "stimulus_auditiv"

    stimulus_id = Column(Integer, ForeignKey("stimuli.stimulus_id"), primary_key=True)
    frequency = Column(Integer, nullable=False)
    volume = Column(Integer, nullable=False)

    stimulus = relationship("Stimulus", back_populates="auditives")


class StimulusTactile(Base):
    __tablename__ = "stimulus_tactile"

    stimulus_id = Column(Integer, ForeignKey("stimuli.stimulus_id"), primary_key=True)
    pattern = Column(String(255), nullable=False)
    intensity = Column(Integer, nullable=False)

    stimulus = relationship("Stimulus", back_populates="tactiles")