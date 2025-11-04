import pytest

from Backend.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
def test_post_handover(client, trial_with_participants):
    trial = trial_with_participants["trial"]
    participant = trial_with_participants["participant"]

    payload = {
        "grasped_object": "Cube",
        "giver_grasped_object": "2025-08-07T10:00:00Z",
        "receiver_touched_object": "2025-08-07T10:00:02Z",
        "receiver_grasped_object": "2025-08-07T10:00:04Z",
        "giver_released_object": 1,
        "giver": participant.participant_id,
        "receiver": None,
    }

    res = client.post(f"/api/trials/{trial.trial_id}/handovers", json=payload)
    assert res.status_code == 201
    json_data = res.get_json()
    assert "message" in json_data and json_data["message"] == "Handover gespeichert"
    assert "handover_id" in json_data

