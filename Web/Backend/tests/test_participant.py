from starlette import status


def test_register_participant(client):
    resp = client.post("/api/participants/", json={
        "age": 25,
        "gender": "m",
        "handedness": "right"
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "participant_id" in data
    assert data["participant_id"] is not None


def test_register_participant_validation(client):
    # missing 'age' field
    resp = client.post("/api/participants/", json={
        "gender": "m",
        "handedness": "right"
    })
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_player_join(client):
    resp = client.post("/api/participants/join", json={"player_id": "1"})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["status"] == "joined"
    assert data["player_id"] == "1"


def test_player_join_invalid(client):
    resp = client.post("/api/participants/join", json={"player_id": "99"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_player_heartbeat_after_join(client):
    client.post("/api/participants/join", json={"player_id": "1"})
    resp = client.post("/api/participants/heartbeat", json={"player_id": "1"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "heartbeat"


def test_player_heartbeat_invalid(client):
    resp = client.post("/api/participants/heartbeat", json={"player_id": "99"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_connection_status(client):
    resp = client.get("/api/participants/connection_status")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, dict)
    assert "1" in data
    assert "2" in data


def test_readiness_status_set_and_get(client):
    resp_set = client.post("/api/participants/readiness_status", json={
        "slot": "surgeon",
        "ready": True
    })
    assert resp_set.status_code == status.HTTP_200_OK
    assert resp_set.json()["ready"] is True

    resp_get = client.get("/api/participants/readiness_status")
    assert resp_get.status_code == status.HTTP_200_OK
    data = resp_get.json()
    assert "surgeon" in data
    assert data["surgeon"] is True


def test_get_participants_by_experiment(client, experiment_id):
    resp = client.get(f"/api/participants/experiment/{experiment_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)


def test_submit_participant(client, experiment_id, participant_id):
    # Create a trial with slot 1
    trial_payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": participant_id, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    client.post(f"/experiments/{experiment_id}/trials", json=trial_payload)

    resp = client.post("/api/participants/submit", json={
        "experiment_id": experiment_id,
        "slot": 1,
        "participant_id": participant_id
    })
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


def test_get_submission_status(client, experiment_id, participant_id):
    trial_payload = {
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {"avatar": 1, "participant_id": participant_id, "selectedStimuli": {"vis": 7}}
                }
            }
        ],
        "questionnaires": []
    }
    client.post(f"/experiments/{experiment_id}/trials", json=trial_payload)
    client.post("/api/participants/submit", json={
        "experiment_id": experiment_id,
        "slot": 1,
        "participant_id": participant_id
    })

    resp = client.get(f"/api/participants/status/{experiment_id}/1")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), dict)
