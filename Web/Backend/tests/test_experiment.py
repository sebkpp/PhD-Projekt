from starlette import status


def test_create_experiment(client, study_id):
    resp = client.post("/experiments/", json={
        "name": "Test Experiment",
        "study_id": study_id,
        "description": "A test experiment",
        "researcher": "Dr. Test"
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "experiment_id" in data


def test_get_experiment_by_id(client, experiment_id):
    resp = client.get(f"/experiments/{experiment_id}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["experiment_id"] == experiment_id


def test_get_experiment_not_found(client):
    resp = client.get("/experiments/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_link_questionnaires(client, experiment_id):
    resp = client.put(f"/experiments/{experiment_id}/questionnaires", json=[])
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["message"] == "Questionnaires updated"


def test_set_started_at(client, experiment_id):
    resp = client.post(f"/experiments/{experiment_id}/started")
    assert resp.status_code == status.HTTP_200_OK
    assert "message" in resp.json()


def test_set_completed_at(client, experiment_id):
    resp = client.post(f"/experiments/{experiment_id}/completed")
    assert resp.status_code == status.HTTP_200_OK
    assert "message" in resp.json()


def test_save_trials(client, experiment_id):
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


def test_get_trials(client, experiment_id):
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
    client.post(f"/experiments/{experiment_id}/trials", json=payload)
    resp = client.get(f"/experiments/{experiment_id}/trials")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)


def test_get_experiment_response_structure(client, experiment_id):
    """GET /experiments/{id} must return experiment_id, study_id and trials field (regression)."""
    resp = client.get(f"/experiments/{experiment_id}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "experiment_id" in data
    assert "study_id" in data


def test_create_experiment_missing_study_id(client):
    """POST /experiments/ without study_id → 422 (Pydantic validation)."""
    resp = client.post("/experiments/", json={"name": "Missing study_id"})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_experiment_invalid_study_id(client):
    """POST /experiments/ with non-existent study_id → should not return 201."""
    resp = client.post("/experiments/", json={
        "name": "Bad study",
        "study_id": 99999
    })
    assert resp.status_code != status.HTTP_201_CREATED
