from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from Backend.db_session import Base
from datetime import datetime

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