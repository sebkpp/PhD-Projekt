from starlette import status


def _setup_trial(client, experiment_id: int, participant_id: int) -> int:
    """Creates a trial and returns the trial_id."""
    payload = {
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
    client.post(f"/experiments/{experiment_id}/trials", json=payload)

    from Backend.db_session import SessionLocal
    from Backend.models.trial.trial import Trial
    session = SessionLocal()
    trial = session.query(Trial).first()
    session.close()
    assert trial is not None
    return trial.trial_id


def _create_second_participant(client) -> int:
    resp = client.post("/api/participants/", json={"age": 30, "gender": "f", "handedness": "left"})
    assert resp.status_code == 201
    return resp.json()["participant_id"]


def test_save_handover(client, experiment_id, participant_id):
    trial_id = _setup_trial(client, experiment_id, participant_id)
    receiver_id = _create_second_participant(client)
    resp = client.post(f"/handovers/trials/{trial_id}", json={
        "giver": participant_id,
        "receiver": receiver_id
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "handover_id" in data
    assert data["handover_id"] is not None


def test_get_handovers_for_trial(client, experiment_id, participant_id):
    trial_id = _setup_trial(client, experiment_id, participant_id)
    receiver_id = _create_second_participant(client)
    client.post(f"/handovers/trials/{trial_id}", json={
        "giver": participant_id,
        "receiver": receiver_id
    })
    resp = client.get(f"/handovers/trials/{trial_id}")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["trial_id"] == trial_id


def test_get_handovers_for_experiment(client, experiment_id, participant_id):
    trial_id = _setup_trial(client, experiment_id, participant_id)
    receiver_id = _create_second_participant(client)
    client.post(f"/handovers/trials/{trial_id}", json={
        "giver": participant_id,
        "receiver": receiver_id
    })
    resp = client.get(f"/handovers/experiments/{experiment_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)
