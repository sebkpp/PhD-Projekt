import pytest
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.experiment import Experiment
from Backend.models.participant import Participant

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    # Vor jedem Test: Tabelle leeren
    session = SessionLocal()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.commit()
    session.close()
    yield
    # Nach jedem Test: Tabelle nochmal leeren (zur Sicherheit)
    session = SessionLocal()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.commit()
    session.close()

@pytest.fixture(scope="function")
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
