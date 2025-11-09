import os
import pytest

os.environ['TESTING'] = 'true'

from fastapi.testclient import TestClient
from Backend.app import app
from Backend.db_session import SessionLocal, DB_NAME
from Backend.models.experiment import Experiment
from Backend.models.participant import Participant
from Backend.models.trial.trial import Trial
from Backend.models.handover import Handover
from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse

@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    if DB_NAME not in ['testdb', 'postgres_test']:
        raise RuntimeError(
            f"❌ Tests would run agains '{DB_NAME}'!\n"
            f"Expected db: 'testdb'\n"
        )
    print(f"✅ Tests run for database: {DB_NAME}")

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    session = SessionLocal()
    # Cleanup before Test
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
    # Cleanup after Test
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
    return TestClient(app)