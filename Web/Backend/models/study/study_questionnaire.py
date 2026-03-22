from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base

from pydantic import BaseModel, Field
from typing import Optional

class StudyQuestionnaire(Base):
    __tablename__ = "study_questionnaire"

    study_id = Column(Integer, ForeignKey("study.study_id", ondelete="CASCADE"), primary_key=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaire.questionnaire_id", ondelete="CASCADE"), primary_key=True)

    order_index = Column(Integer, default=0)  # Reihenfolge der Abfrage
    trigger_timing = Column(String(50))       # z. B. "pre_experiment", "post_trial", "post_experiment"

    # Beziehungen zu den Haupttabellen
    study = relationship("Study", back_populates="study_questionnaires")
    questionnaire = relationship("Questionnaire", back_populates="study_questionnaires")

class StudyQuestionnaireResponse(BaseModel):
    study_id: int = Field(..., description="ID of the associated study")
    questionnaire_id: int = Field(..., description="ID of the associated questionnaire")
    order_index: Optional[int] = Field(0, description="Order index of the questionnaire in the study")
    trigger_timing: Optional[str] = Field(None, description="Timing of the questionnaire trigger (e.g., 'pre_experiment', 'post_trial')")
    name: Optional[str] = Field(None, description="Name of the questionnaire")

    class Config:
        orm_mode = True