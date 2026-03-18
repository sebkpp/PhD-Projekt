import pytest


@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    from Backend.db_session import DB_NAME
    if not DB_NAME == 'testdb':
        raise RuntimeError(
            f"❌ Tests would run agains '{DB_NAME}'!\n"
            f"Expected db: 'testdb'\n"
        )
    print(f"✅ Tests run for database: {DB_NAME}")


def _delete_all(session):
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import EyeTracking
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.models.trial.trial import Trial
    from Backend.models.participant import Participant
    from Backend.models.experiment import Experiment
    from Backend.models.study.study import Study
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.models.study.study_stimuli import StudyStimuli
    from Backend.models.study.study_config import StudyConfig

    session.query(EyeTracking).delete()
    session.query(Handover).delete()
    session.query(QuestionnaireResponse).delete()
    session.query(QuestionnaireItem).delete()
    session.query(Questionnaire).delete()
    session.query(Trial).delete()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.query(StudyQuestionnaire).delete()
    session.query(StudyStimuli).delete()
    session.query(StudyConfig).delete()
    session.query(Study).delete()
    session.commit()


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    from Backend.db_session import SessionLocal
    session = SessionLocal()
    _delete_all(session)
    session.close()
    yield
    session = SessionLocal()
    _delete_all(session)
    session.close()


@pytest.fixture(scope="function")
def client():
    from fastapi.testclient import TestClient
    from Backend.app import app
    return TestClient(app)


@pytest.fixture(scope="function")
def study_id(client):
    """Creates a study and returns its study_id."""
    resp = client.post("/studies/", json={"status": "Aktiv"})
    assert resp.status_code == 201
    return resp.json()["study_id"]


@pytest.fixture(scope="function")
def experiment_id(client, study_id):
    """Creates an experiment in the fixture study and returns its experiment_id."""
    resp = client.post("/experiments/", json={"name": "Test Experiment", "study_id": study_id})
    assert resp.status_code == 201
    return resp.json()["experiment_id"]


@pytest.fixture(scope="function")
def participant_id(client):
    """Creates a participant and returns its participant_id."""
    resp = client.post("/api/participants/", json={"age": 25, "gender": "m", "handedness": "right"})
    assert resp.status_code == 201
    return resp.json()["participant_id"]
