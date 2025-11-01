from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from Backend.db_session import Base

experiment_questionnaire = Table(
    "experiment_questionnaire",
    Base.metadata,
    Column("experiment_id", Integer, ForeignKey("experiment.experiment_id"), primary_key=True),
    Column("questionnaire_id", Integer, ForeignKey("questionnaire.questionnaire_id"), primary_key=True)
)

class Experiment(Base):
    __tablename__ = "experiment"

    experiment_id = Column(Integer, primary_key=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    researcher = Column(String)
    study_id = Column(Integer, ForeignKey('study.study_id'), nullable=False)

    trials = relationship("Trial", back_populates="experiment")
    questionnaires = relationship(
        "Questionnaire",
        secondary=experiment_questionnaire,
        back_populates="experiments"
    )
    study = relationship('Study', back_populates='experiments')


    def to_dict(self):
        return {
            "experiment_id": self.experiment_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "researcher": self.researcher,
            "study_id": self.study_id,
            "trials": [trial.to_dict() for trial in self.trials]
        }