import pytest
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.trial import Trial, TrialParticipantItem
from Backend.models.experiment import Experiment

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def experiment():
    session = SessionLocal()
    experiment = Experiment(name="Test-Experiment für Trials")
    session.add(experiment)
    session.commit()
    yield experiment
    # Clean up
    session.query(TrialParticipantItem).delete()
    session.query(Trial).delete()
    session.delete(experiment)
    session.commit()
    session.close()

def test_post_and_get_trials(client, experiment):

    # 🧪 Teilnehmer anlegen
    participant_1_data = {
        "age": 25,
        "gender": "male",
        "handedness": "right"
    }
    res1 = client.post("/api/participants", json=participant_1_data)
    assert res1.status_code == 201
    participant_1_id = res1.get_json()["participant_id"]

    participant_2_data = {
        "age": 30,
        "gender": "female",
        "handedness": "left"
    }
    res2 = client.post("/api/participants", json=participant_2_data)
    assert res2.status_code == 201
    participant_2_id = res2.get_json()["participant_id"]

    trial_payload = {
        "experiment_id": experiment.experiment_id,
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {
                        "avatar": 1,
                        "participant_id": participant_1_id,
                        "selectedStimuli": {
                            "vis": 7,
                            "aud": 12
                        }
                    },
                    "2": {
                        "avatar": 2,
                        "participant_id": participant_2_id,
                        "selectedStimuli": {
                            "tak": 20
                        }
                    }
                }
            }
        ]
    }

    # POST: Trials speichern
    res_post = client.post(f'/api/experiments/{experiment.experiment_id}/trials', json=trial_payload)
    assert res_post.status_code == 201
    assert res_post.get_json()["status"] == "ok"

    # GET: Trials abrufen
    res_get = client.get(f'/api/experiments/{experiment.experiment_id}/trials')
    assert res_get.status_code == 200
    trials = res_get.get_json()
    assert isinstance(trials, list)
    assert len(trials) == 1
    trial = trials[0]
    assert trial["trial_number"] == 1
    assert len(trial["participants"]) == 2

    session = SessionLocal()
    db_trials = session.query(Trial).all()
    assert len(db_trials) == 1
    assert db_trials[0].trial_number == 1

def test_post_trials_invalid_payload(client, experiment):
    # Fehlender experiment_id
    res = client.post(f'/api/experiments/{experiment.experiment_id}/trials', json={"trials": []})
    assert res.status_code == 400
    assert "error" in res.get_json()

    # Kein JSON
    res = client.post(f'api/experiments/{experiment.experiment_id}/trials', data="kein json", content_type='text/plain')
    assert res.status_code in (400, 415)

def test_post_trials_invalid_stimulus_id(client, experiment):
    payload = {
        "experiment_id": experiment.experiment_id,
        "trials": [
            {
                "trial_number": 1,
                "participants": {
                    "1": {
                        "avatar": 1,
                        "participant_id": 101,
                        "selectedStimuli": {
                            "vis": 9999  # ungültiger Stimulus
                        }
                    }
                }
            }
        ]
    }

    res = client.post(f'/api/experiments/{experiment.experiment_id}/trials', json=payload)
    assert res.status_code == 500
    assert "error" in res.get_json()
