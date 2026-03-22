import pytest
from starlette import status


@pytest.fixture
def trial_id(client, experiment_id):
    """Creates a trial and returns its trial_id.

    POST /experiments/{id}/trials returns {"status": "ok", "message": "..."}
    — no trial_id. Use GET /experiments/{id}/trials to retrieve the created record.
    """
    resp = client.post(
        f"/experiments/{experiment_id}/trials",
        json={"trials": [{"trial_number": 1, "slots": []}], "questionnaires": []}
    )
    assert resp.status_code == 201, resp.text
    trials = client.get(f"/experiments/{experiment_id}/trials").json()
    assert len(trials) > 0, "No trials found after creation"
    return trials[0]["trial_id"]


@pytest.fixture
def participant_ids(client):
    """Creates two participants and returns their IDs."""
    ids = []
    for _ in range(2):
        resp = client.post(
            "/api/participants/",
            json={"age": 25, "gender": "m", "handedness": "right"}
        )
        assert resp.status_code == 201, resp.text
        ids.append(resp.json()["participant_id"])
    return ids


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


def test_handover_init_creates_record(client, trial_id, participant_ids):
    """POST creates a handover record and returns handover_id."""
    resp = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1], "grasped_object": "Cube"}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "handover_id" in data
    assert data["handover_id"] is not None


def test_handover_init_missing_giver(client, trial_id):
    """POST without giver returns 422."""
    resp = client.post(
        f"/handovers/trials/{trial_id}",
        json={"receiver": 1}
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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


def test_get_handovers_for_trial_not_found(client):
    """GET /handovers/trials/9999 → 404 for unknown trial."""
    resp = client.get("/handovers/trials/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_get_handovers_for_experiment_not_found(client):
    """GET /handovers/experiments/9999 → 404 for unknown experiment."""
    resp = client.get("/handovers/experiments/9999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_handover_patch_phases_updates_timestamps(client, trial_id, participant_ids):
    """PATCH /phases sets timestamps; other fields remain NULL."""
    # Init
    init = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1]}
    )
    assert init.status_code == 201
    handover_id = init.json()["handover_id"]

    # Patch one timestamp
    resp = client.patch(
        f"/handovers/{handover_id}/phases",
        json={"giver_grasped_object": "2025-09-08T10:00:03.484"}
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["handover_id"] == handover_id


def test_handover_patch_partial_update(client, trial_id, participant_ids):
    """PATCH with one field does not overwrite other fields."""
    init = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1]}
    )
    handover_id = init.json()["handover_id"]

    # Set giver_grasped_object first
    client.patch(
        f"/handovers/{handover_id}/phases",
        json={"giver_grasped_object": "2025-09-08T10:00:03.484"}
    )

    # Set receiver_touched_object in second call
    resp = client.patch(
        f"/handovers/{handover_id}/phases",
        json={"receiver_touched_object": "2025-09-08T10:00:03.890"}
    )
    assert resp.status_code == status.HTTP_200_OK


def test_handover_patch_not_found(client):
    """PATCH on non-existing handover_id returns 404."""
    resp = client.patch(
        "/handovers/99999/phases",
        json={"is_error": True}
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_handover_patch_sets_is_error(client, trial_id, participant_ids):
    """PATCH can set is_error and error_type."""
    init = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": participant_ids[0], "receiver": participant_ids[1]}
    )
    handover_id = init.json()["handover_id"]

    resp = client.patch(
        f"/handovers/{handover_id}/phases",
        json={"is_error": True, "error_type": "drop"}
    )
    assert resp.status_code == status.HTTP_200_OK
