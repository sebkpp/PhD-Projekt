import pytest
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.handover import Handover
from Backend.models.participant import Participant
from Backend.models.trial.trial import Trial
from Backend.models.experiment import Experiment
from Backend.models.trial.trial import TrialParticipantItem
from Backend.models.stimulus import StimuliCombination

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def trial_with_participants(client):
    session = SessionLocal()

    # Experiment anlegen
    experiment = Experiment(name="Testexperiment")
    session.add(experiment)
    session.commit()

    # Teilnehmer anlegen
    participant = Participant(age=28, gender='male', handedness='right')
    session.add(participant)
    session.commit()

    # Trial anlegen
    trial = Trial(experiment_id=experiment.experiment_id, trial_number=1)
    session.add(trial)
    session.commit()

    # EXISTIERENDE stimulus_combination_id holen
    stimulus_combination = session.query(StimuliCombination).first()
    if stimulus_combination is None:
        raise RuntimeError("Keine StimuliCombination-Daten in der DB vorhanden. Bitte vor Test sicherstellen.")

    # TrialParticipantItem anlegen, um Teilnehmer dem Trial zuzuordnen
    tpi = TrialParticipantItem(
        trial_id=trial.trial_id,
        participant_id=participant.participant_id,
        avatar_visibility_id=1,  # hier ggf. gültige ID einfügen
        stimulus_combination_id=stimulus_combination.stimulus_combination_id
    )
    session.add(tpi)
    session.commit()

    yield {
        "experiment": experiment,
        "participant": participant,
        "trial": trial
    }

    # Aufräumen
    session.query(Handover).delete()
    session.query(TrialParticipantItem).delete()
    session.query(Trial).delete()
    session.query(Participant).delete()
    session.query(Experiment).delete()
    session.commit()
    session.close()


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

