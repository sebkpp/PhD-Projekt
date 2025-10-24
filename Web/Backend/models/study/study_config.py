from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class StudyConfig(Base):
    __tablename__ = "study_config"

    study_config_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), default=None)
    description = Column(Text, default=None)
    principal_investigator = Column(String(255), default=None)
    study_id = Column(Integer, ForeignKey("study.study_id"))
    trial_number = Column(Integer, default=None)
    trials_permuted = Column(Boolean, default=None)

    study = relationship("Study", back_populates="config")

    def to_dict(self):
        return {
            "study_config_id": self.study_config_id,
            "name": self.name,
            "description": self.description,
            "principal_investigator": self.principal_investigator,
            "study_id": self.study_id,
            "trial_number": self.trial_number,
            "trials_permuted": self.trials_permuted
        }