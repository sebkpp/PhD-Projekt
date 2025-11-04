from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from Backend.db_session import Base

from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional, List

from Backend.models.study.study_config import StudyConfigResponse
from Backend.models.study.study_questionnaire import StudyQuestionnaireResponse
from Backend.models.study.study_stimuli import StudyStimuliResponse


class Study(Base):
    __tablename__ = 'study'

    study_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    started_at = Column(Date)
    ended_at = Column(Date)
    status = Column(String(255))

    experiments = relationship('Experiment', back_populates='study')
    study_questionnaires = relationship(
        "StudyQuestionnaire",
        back_populates="study",
        cascade="all, delete-orphan"
    )
    config = relationship("StudyConfig", uselist=False, back_populates="study")
    stimuli = relationship("StudyStimuli", back_populates="study", cascade="all, delete-orphan")


    @property
    def questionnaires(self):
        return getattr(self, "_questionnaires", [])

    @property
    def stimuli_data(self):
        return getattr(self, "_stimuli", [])

    def to_dict(self):
        data = {
            "study_id": self.study_id,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "config": self.config.to_dict() if self.config else None,
            "experiments": [exp.to_dict() for exp in self.experiments],
            "questionnaires": [
                {
                    "questionnaire_id": sq.questionnaire_id,
                    "order_index": sq.order_index,
                    "name": sq.questionnaire.name if sq.questionnaire else None
                }
                for sq in self.study_questionnaires
            ],
            "stimuli": self.stimuli_data,

        }
        return data


class StudyBase(BaseModel):
    status: Optional[str] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None


class StudyCreate(StudyBase):
    pass


class StudyUpdate(StudyBase):
    pass


class StudyResponse(BaseModel):
    study_id: int
    status: Optional[str] = Field(None, description="Status of the study")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp of the study")
    started_at: Optional[date] = Field(None, description="Start date of the study")
    ended_at: Optional[date] = Field(None, description="End date of the study")
    config: Optional[StudyConfigResponse] = Field(None, description="Configuration details of the study")
    questionnaires: Optional[List[StudyQuestionnaireResponse]] = Field(None, description="List of questionnaires associated with the study")
    stimuli: Optional[List[StudyStimuliResponse]] = Field(None, description="List of stimuli types associated with the study")

    class Config:
        orm_mode = True