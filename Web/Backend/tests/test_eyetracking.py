import pytest
from starlette import status
from Backend.models.eyetracking import AreaOfInterest
from Backend.db_session import SessionLocal


@pytest.fixture
def trial_id(client, experiment_id):
    """POST returns {"status": "ok"} — use GET to retrieve the trial_id."""
    resp = client.post(
        f"/experiments/{experiment_id}/trials",
        json={"trials": [{"trial_number": 1, "slots": []}], "questionnaires": []}
    )
    assert resp.status_code == 201, resp.text
    trials = client.get(f"/experiments/{experiment_id}/trials").json()
    assert len(trials) > 0
    return trials[0]["trial_id"]


@pytest.fixture
def two_participant_ids(client):
    ids = []
    for _ in range(2):
        resp = client.post(
            "/api/participants/",
            json={"age": 25, "gender": "m", "handedness": "right"}
        )
        assert resp.status_code == 201
        ids.append(resp.json()["participant_id"])
    return ids


@pytest.fixture
def handover_id(client, trial_id, two_participant_ids):
    resp = client.post(
        f"/handovers/trials/{trial_id}",
        json={"giver": two_participant_ids[0], "receiver": two_participant_ids[1]}
    )
    assert resp.status_code == 201
    return resp.json()["handover_id"]


@pytest.fixture
def aoi_id():
    """Seeds one AreaOfInterest row directly and returns its ID."""
    db = SessionLocal()
    existing = db.query(AreaOfInterest).filter_by(aoi="instrument").first()
    if existing:
        aoi = existing
    else:
        aoi = AreaOfInterest(aoi="instrument", label="Instrument")
        db.add(aoi)
        db.commit()
        db.refresh(aoi)
    aoi_id = aoi.aoi_id
    db.close()
    return aoi_id


def test_eyetracking_create_success(client, handover_id, two_participant_ids, aoi_id):
    """POST creates an eye-tracking record and returns eye_tracking_id."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": handover_id,
            "aoi_id": aoi_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "eye_tracking_id" in data
    assert data["eye_tracking_id"] is not None


def test_eyetracking_create_missing_field(client, handover_id, two_participant_ids, aoi_id):
    """POST without aoi_id returns 422."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": handover_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_eyetracking_invalid_handover_id(client, two_participant_ids, aoi_id):
    """POST with non-existing handover_id returns 404."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": 99999,
            "aoi_id": aoi_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_eyetracking_invalid_participant_id(client, handover_id, aoi_id):
    """POST with non-existing participant_id returns 404."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": 99999,
            "handover_id": handover_id,
            "aoi_id": aoi_id,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_eyetracking_invalid_aoi_id(client, handover_id, two_participant_ids):
    """POST with non-existing aoi_id returns 404."""
    resp = client.post(
        "/eyetracking",
        json={
            "participant_id": two_participant_ids[0],
            "handover_id": handover_id,
            "aoi_id": 99999,
            "starttime": "2025-09-08T10:00:03.484",
            "endtime": "2025-09-08T10:00:03.641",
            "duration": 157,
        }
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND
