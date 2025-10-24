from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class StudyQuestionnaire(Base):
    __tablename__ = "study_questionnaire"

    study_id = Column(Integer, ForeignKey("study.study_id", ondelete="CASCADE"), primary_key=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaire.questionnaire_id", ondelete="CASCADE"), primary_key=True)

    order_index = Column(Integer, default=0)  # Reihenfolge der Abfrage
    trigger_timing = Column(String(50))       # z. B. "pre_experiment", "post_trial", "post_experiment"

    # Beziehungen zu den Haupttabellen
    study = relationship("Study", back_populates="study_questionnaires")
    questionnaire = relationship("Questionnaire", back_populates="study_questionnaires")
