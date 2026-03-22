from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base

from pydantic import BaseModel, Field
from typing import Optional

class StudyConfig(Base):
    __tablename__ = "study_config"

    study_config_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), default=None)
    description = Column(Text, default=None)
    principal_investigator = Column(String(255), default=None)
    study_id = Column(Integer, ForeignKey("study.study_id"))
    trial_number = Column(Integer, default=None)
    trials_permuted = Column(Boolean, default=None)
    study_type = Column(String(50), default='stimulus_comparison')

    study = relationship("Study", back_populates="config")

    def to_dict(self):
        return {
            "study_config_id": self.study_config_id,
            "name": self.name,
            "description": self.description,
            "principal_investigator": self.principal_investigator,
            "study_id": self.study_id,
            "trial_number": self.trial_number,
            "trials_permuted": self.trials_permuted,
            "study_type": self.study_type
        }

class StudyConfigResponse(BaseModel):
    study_config_id: int
    name: Optional[str] = Field(None, description="Name of the study configuration")
    description: Optional[str] = Field(None, description="Description of the study configuration")
    principal_investigator: Optional[str] = Field(None, description="Principal investigator of the study")
    study_id: Optional[int] = Field(None, description="ID of the associated study")
    trial_number: Optional[int] = Field(None, description="Number of trials in the study")
    trials_permuted: Optional[bool] = Field(None, description="Indicates if trials are permuted")
    study_type: Optional[str] = Field('stimulus_comparison', description="Type: avatar_comparison | stimulus_comparison | combination_comparison")

    class Config:
        orm_mode = True