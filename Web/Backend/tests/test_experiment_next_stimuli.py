from fastapi.testclient import TestClient
from starlette import status
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.avatar_visibility import AvatarVisibility
from Backend.models.experiment import Experiment
from Backend.models.trial.trial import Trial
from Backend.models.trial.trial_slot import TrialSlot
from Backend.models.trial.trial_participant_slot import TrialParticipantSlot
from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus
from Backend.models.participant import Participant
from Backend.models.stimulus import Stimulus, StimulusType, StimulusVisual
from Backend.models.study.study import Study

client = TestClient(app)


def _get_or_create_avatar_visibility(db):
    """Returns an avatar_visibility_id, creating a row if none exists."""
    av = db.query(AvatarVisibility).first()
    if av is None:
        av = AvatarVisibility(avatar_visibility_name="full", label="Ganze Figur")
        db.add(av)
        db.flush()
    return av.avatar_visibility_id


def _setup_open_experiment_with_stimuli():
    """Creates study -> experiment (open) -> trial -> 2 slots -> 2 participants -> stimulus on slot 1."""
    db = SessionLocal()
    try:
        av_id = _get_or_create_avatar_visibility(db)

        study = Study(status="Aktiv")
        db.add(study)
        db.flush()

        experiment = Experiment(study_id=study.study_id, researcher="test")
        db.add(experiment)
        db.flush()

        trial = Trial(experiment_id=experiment.experiment_id, trial_number=1)
        db.add(trial)
        db.flush()

        p1 = Participant(age=30, gender="Male", handedness="Right")
        p2 = Participant(age=25, gender="Female", handedness="Right")
        db.add_all([p1, p2])
        db.flush()

        slot1 = TrialSlot(trial_id=trial.trial_id, slot=1, avatar_visibility_id=av_id)
        slot2 = TrialSlot(trial_id=trial.trial_id, slot=2, avatar_visibility_id=av_id)
        db.add_all([slot1, slot2])
        db.flush()

        db.add(TrialParticipantSlot(trial_slot_id=slot1.trial_slot_id, participant_id=p1.participant_id))
        db.add(TrialParticipantSlot(trial_slot_id=slot2.trial_slot_id, participant_id=p2.participant_id))
        db.flush()

        visual_type = StimulusType(type_name="visual")
        db.add(visual_type)
        db.flush()

        stimulus = Stimulus(name="outer_hand", stimulus_type_id=visual_type.stimulus_type_id)
        db.add(stimulus)
        db.flush()

        db.add(StimulusVisual(stimulus_id=stimulus.stimulus_id, stimulus_name="outer_hand"))
        db.flush()

        db.add(TrialSlotStimulus(trial_slot_id=slot1.trial_slot_id, stimulus_id=stimulus.stimulus_id))
        db.commit()
        return experiment.experiment_id, trial.trial_id
    finally:
        db.close()


def test_next_experiment_response_includes_stimuli_field():
    """Every slot in the /experiments/next response must have a 'stimuli' key."""
    _setup_open_experiment_with_stimuli()
    resp = client.get("/experiments/next")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    for slot in data["slots"]:
        assert "stimuli" in slot, f"Slot {slot.get('slot')} is missing 'stimuli' key"


def test_next_experiment_slot_with_stimulus_has_data():
    """Slot 1 must contain exactly 1 stimulus with name 'outer_hand'."""
    _setup_open_experiment_with_stimuli()
    resp = client.get("/experiments/next")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    slots_by_number = {s["slot"]: s for s in data["slots"]}
    slot1 = slots_by_number[1]
    assert len(slot1["stimuli"]) == 1
    assert slot1["stimuli"][0]["stimulus"]["name"] == "outer_hand"


def test_next_experiment_slot_without_stimulus_has_empty_list():
    """Slot 2 has no stimuli assigned and must return stimuli == []."""
    _setup_open_experiment_with_stimuli()
    resp = client.get("/experiments/next")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    slots_by_number = {s["slot"]: s for s in data["slots"]}
    assert slots_by_number[2]["stimuli"] == []
