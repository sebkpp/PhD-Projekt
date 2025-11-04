from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base

from pydantic import BaseModel, Field
from typing import Optional

class StudyStimuli(Base):
    __tablename__ = "study_stimuli"

    study_id = Column(Integer, ForeignKey("study.study_id"), primary_key=True)
    stimuli_type_id = Column(Integer, ForeignKey("stimulus_type.stimulus_type_id"), primary_key=True)

    study = relationship("Study", back_populates="stimuli")
    stimuli_type = relationship("StimulusType", back_populates="studies")

    def to_dict(self):
        return {
            "study_id": self.study_id,
            "stimuli_type_id": self.stimuli_type_id
        }


class StudyStimuliResponse(BaseModel):
    study_id: int = Field(..., description="Id of the associated study")
    stimuli_type_id: int = Field(..., description="Id of the associated stimulus type")
    name: Optional[str] = Field(None, description="Name of the stimulus type")

    class Config:
        orm_mode = True