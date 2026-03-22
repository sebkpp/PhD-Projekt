from starlette import status


def test_create_study(client):
    resp = client.post("/studies/", json={"status": "Aktiv"})
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "study_id" in data
    assert data["study_id"] is not None


def test_list_studies(client):
    client.post("/studies/", json={"status": "Aktiv"})
    resp = client.get("/studies/")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_study_by_id(client, study_id):
    resp = client.get(f"/studies/{study_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["study_id"] == study_id


def test_get_study_response_structure(client, study_id):
    """GET /studies/{id} must return config, stimuli and questionnaires – no 500 recursion."""
    resp = client.get(f"/studies/{study_id}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "config" in data
    assert "stimuli" in data
    assert "questionnaires" in data
    assert isinstance(data["stimuli"], list)
    assert isinstance(data["questionnaires"], list)


def test_get_study_not_found(client):
    resp = client.get("/studies/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_study(client, study_id):
    resp = client.put(f"/studies/{study_id}", json={"status": "Beendet"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "Beendet"


def test_delete_study(client, study_id):
    resp = client.delete(f"/studies/{study_id}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_delete_study_not_found(client):
    resp = client.delete("/studies/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_experiments_by_study(client, study_id, experiment_id):
    resp = client.get(f"/studies/{study_id}/experiments")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)
    assert any(e["experiment_id"] == experiment_id for e in data)


def test_get_experiments_by_study_includes_trials_field(client, study_id, experiment_id):
    """Each experiment in GET /studies/{id}/experiments must have a trials key."""
    resp = client.get(f"/studies/{study_id}/experiments")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    exp = next(e for e in data if e["experiment_id"] == experiment_id)
    assert "trials" in exp
    assert isinstance(exp["trials"], list)


def test_get_experiments_by_study_trials_with_slots(client, study_id, experiment_id):
    """Saved trials must appear with slot data in GET /studies/{id}/experiments."""
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
    client.post(f"/experiments/{experiment_id}/trials", json=trial_payload)

    resp = client.get(f"/studies/{study_id}/experiments")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    exp = next(e for e in data if e["experiment_id"] == experiment_id)
    assert len(exp["trials"]) == 1
    trial = exp["trials"][0]
    assert "slots" in trial
    assert isinstance(trial["slots"], list)


def test_close_study(client, study_id):
    resp = client.post(f"/studies/{study_id}/close")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["ended_at"] is not None


def test_get_experiments_by_study_not_found(client):
    """GET /studies/9999/experiments → 404 for unknown study."""
    resp = client.get("/studies/9999/experiments")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_participants_by_study_not_found(client):
    """GET /studies/9999/participants → 404 for unknown study."""
    resp = client.get("/studies/9999/participants")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
