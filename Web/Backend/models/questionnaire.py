from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class Questionnaire(Base):
    __tablename__ = 'questionnaire'

    questionnaire_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    experiments = relationship(
        "Experiment",
        secondary="experiment_questionnaire",
        back_populates="questionnaires"
    )
    items = relationship("QuestionnaireItem", back_populates="questionnaire")
    study_questionnaires = relationship(
        "StudyQuestionnaire",
        back_populates="questionnaire",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "questionnaire_id": self.questionnaire_id,
            "name": self.name,
        }


class QuestionnaireItem(Base):
    __tablename__ = 'questionnaire_item'

    questionnaire_item_id = Column(Integer, primary_key=True)
    questionnaire_id = Column(Integer, ForeignKey('questionnaire.questionnaire_id'), nullable=False)

    item_name = Column(String, nullable=False)  # z.B. 'mental_demand'

    questionnaire = relationship("Questionnaire", back_populates="items")
    responses = relationship("QuestionnaireResponse", back_populates="questionnaire_item")

    def to_dict(self):
        return {
            "questionnaire_item_id": self.questionnaire_item_id,
            "item_name": self.item_name,
            "questionnaire": self.questionnaire.to_dict() if self.questionnaire else None
        }


class QuestionnaireResponse(Base):
    __tablename__ = 'questionnaire_response'

    questionnaire_response_id = Column(Integer, primary_key=True)

    trial_id = Column(Integer, ForeignKey('trial.trial_id'), nullable=False)
    participant_id = Column(Integer, ForeignKey('participant.participant_id'), nullable=False)
    questionnaire_item_id = Column(Integer, ForeignKey('questionnaire_item.questionnaire_item_id'), nullable=False)

    response_value = Column(Float, nullable=False)

    trial = relationship("Trial", back_populates="questionnaire_responses")
    participant = relationship("Participant", back_populates="questionnaire_responses")
    questionnaire_item = relationship("QuestionnaireItem", back_populates="responses")

    def to_dict(self):
        return {
            "questionnaire_response_id": self.questionnaire_response_id,
            "trial_id": self.trial_id,
            "participant_id": self.participant_id,
            "questionnaire_item": self.questionnaire_item.to_dict() if self.questionnaire_item else None,
            "response_value": self.response_value
        }