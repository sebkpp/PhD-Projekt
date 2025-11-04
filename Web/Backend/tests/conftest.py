import pytest
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.experiment import Experiment
from Backend.models.participant import Participant
from Backend.models.trial.trial import Trial
from Backend.models.handover import Handover
from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    session = SessionLocal()
    # Wichtig: zuerst die abhängigen Tabellen löschen (child tables)
    session.query(Handover).delete()
    session.query(QuestionnaireResponse).delete()
    session.query(QuestionnaireItem).delete()
    session.query(Questionnaire).delete()
    session.query(Trial).delete()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.commit()
    session.close()
    yield
    # Nach jedem Test nochmal das gleiche, falls Test selbst was hinterlässt
    session = SessionLocal()
    session.query(Handover).delete()
    session.query(QuestionnaireResponse).delete()
    session.query(QuestionnaireItem).delete()
    session.query(Questionnaire).delete()
    session.query(Trial).delete()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.commit()
    session.close()

@pytest.fixture(scope="function")
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
