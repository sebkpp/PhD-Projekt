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
    from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus
    from Backend.models.trial.trial_slot import TrialSlot
    from Backend.models.participant import Participant
    from Backend.models.experiment import Experiment
    from Backend.models.study.study import Study
    from Backend.models.study.study_questionnaire import StudyQuestionnaire
    from Backend.models.study.study_stimuli import StudyStimuli
    from Backend.models.study.study_config import StudyConfig
    from Backend.models.stimulus import Stimulus, StimulusType

    session.query(EyeTracking).delete()
    session.query(Handover).delete()
    session.query(QuestionnaireResponse).delete()
    session.query(QuestionnaireItem).delete()
    session.query(Questionnaire).delete()
    session.query(TrialSlotStimulus).delete()
    session.query(TrialSlot).delete()
    session.query(Trial).delete()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.query(StudyQuestionnaire).delete()
    session.query(StudyStimuli).delete()
    session.query(StudyConfig).delete()
    session.query(Study).delete()
    session.query(Stimulus).delete()
    session.query(StimulusType).delete()
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


@pytest.fixture(scope="function")
def db_session():
    """Yields a SQLAlchemy session for direct ORM inserts in test setup.

    Success path: test calls db_session.commit() to persist data, then the
    service runs, then clean_db (separate session) deletes all rows.

    Failure path: if a test raises before committing, rollback() discards
    partial writes so clean_db finds a consistent state.
    """
    from Backend.db_session import SessionLocal
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="session", autouse=True)
def seed_aoi(verify_test_database):
    """Seed the 5 AreaOfInterest rows once per test session.

    clean_db does not delete area_of_interest rows, so these persist
    across all test functions without re-insertion.
    The verify_test_database parameter ensures this runs after DB verification.
    Uses upsert semantics: inserts each required AOI only if not already present.
    """
    from Backend.db_session import SessionLocal
    from Backend.models.eyetracking import AreaOfInterest
    session = SessionLocal()
    required = [
        ("partner_face", "Gesicht"),
        ("object", "Objekt"),
        ("own_hand", "Eigene Hand"),
        ("partner_hand", "Partnerhand"),
        ("environment", "Umgebung"),
    ]
    for aoi_name, label in required:
        if not session.query(AreaOfInterest).filter_by(aoi=aoi_name).first():
            session.add(AreaOfInterest(aoi=aoi_name, label=label))
    session.commit()
    session.close()


@pytest.fixture(scope="function")
def trial_id(db_session, experiment_id):
    """Creates a Trial row directly via ORM and returns its trial_id."""
    from Backend.models.trial.trial import Trial
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.commit()
    return trial.trial_id


@pytest.fixture(scope="function")
def handover_id(db_session, trial_id, participant_id):
    """Creates a Handover row directly via ORM and returns its handover_id."""
    from Backend.models.handover import Handover
    handover = Handover(
        trial_id=trial_id,
        giver=participant_id,
        receiver=participant_id,
        grasped_object="scalpel",
    )
    db_session.add(handover)
    db_session.commit()
    return handover.handover_id
