from fastapi.testclient import TestClient

from Backend.app import app

client = TestClient(app)

def test_trial_create_validation():
    # invalid Payload (missing trials)
    payload = {"questionnaires": []}
    response = client.post("/api/experiments/1/trials", json=payload)
    assert response.status_code == 422  # FastAPI-Validation

def test_create_and_get_trial():
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
    res_post = client.post("/api/experiments/1/trials", json=trial_payload)
    assert res_post.status_code == 201
    assert res_post.json()["status"] == "ok"

    # Trial retrieval
    res_get = client.get("/api/experiments/1/trials")
    assert res_get.status_code == 200
    trials = res_get.json()
    assert isinstance(trials, list)
    assert trials[0]["trial_number"] == 1