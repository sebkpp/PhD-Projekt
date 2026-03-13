from fastapi.testclient import TestClient
from starlette import status
from starlette.status import HTTP_200_OK

from Backend.app import app

client = TestClient(app)


def _get_or_create_experiment() -> int:
    """Creates a study and experiment, returns experiment_id."""
    study_resp = client.post("/studies/", json={"status": "Aktiv"})
    assert study_resp.status_code == 201
    study_id = study_resp.json()["study_id"]
    exp_resp = client.post("/experiments/", json={
        "name": "Trial Test Experiment",
        "study_id": study_id
    })
    assert exp_resp.status_code == 201
    return exp_resp.json()["experiment_id"]


def _create_trial(experiment_id: int = None):
    if experiment_id is None:
        experiment_id = _get_or_create_experiment()
    payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": 1, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    resp = client.post(f"/experiments/{experiment_id}/trials", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED


def _get_first_trial_id() -> int:
    from Backend.db_session import SessionLocal
    from Backend.models.trial.trial import Trial
    session = SessionLocal()
    trial = session.query(Trial).first()
    session.close()
    assert trial is not None
    return trial.trial_id


def test_trial_create_validation():
    # invalid Payload (missing trials)
    payload = {"questionnaires": []}
    response = client.post("/experiments/1/trials", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT  # FastAPI-Validation


def test_create_and_get_trial():
    experiment_id = _get_or_create_experiment()

    # Trial creation
    trial_payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": 1, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    res_post = client.post(f"/experiments/{experiment_id}/trials", json=trial_payload)
    assert res_post.status_code == status.HTTP_201_CREATED
    assert res_post.json()["status"] == "ok"

    # Trial retrieval
    res_get = client.get(f"/experiments/{experiment_id}/trials")
    assert res_get.status_code == HTTP_200_OK
    trials = res_get.json()
    assert isinstance(trials, list)
    assert trials[0]["trial_number"] == 1


def test_get_current_trial():
    resp = client.get("/trials/current")
    assert resp.status_code == status.HTTP_200_OK
    assert "trial_id" in resp.json()


def test_start_trial():
    _create_trial()
    trial_id = _get_first_trial_id()
    resp = client.post(f"/trials/{trial_id}/start")
    assert resp.status_code == status.HTTP_200_OK
    assert "message" in resp.json()


def test_end_trial():
    _create_trial()
    trial_id = _get_first_trial_id()
    client.post(f"/trials/{trial_id}/start")
    resp = client.post(f"/trials/{trial_id}/end")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


def test_get_trial_by_id():
    _create_trial()
    trial_id = _get_first_trial_id()
    resp = client.get(f"/trials/{trial_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["trial_id"] == trial_id


def test_get_participants_for_trial():
    _create_trial()
    trial_id = _get_first_trial_id()
    resp = client.get(f"/trials/{trial_id}/participants")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)
