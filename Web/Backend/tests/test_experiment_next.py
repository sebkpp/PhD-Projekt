from fastapi.testclient import TestClient
from starlette import status
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.experiment import Experiment
from Backend.models.trial.trial import Trial
from Backend.models.trial.trial_slot import TrialSlot
from Backend.models.trial.trial_participant_slot import TrialParticipantSlot
from Backend.models.participant import Participant
from Backend.models.study.study import Study
from Backend.models.avatar_visibility import AvatarVisibility
from datetime import datetime, timezone

client = TestClient(app)


def _get_or_create_avatar_visibility(db):
    """Returns an avatar_visibility_id, creating a row if none exists."""
    av = db.query(AvatarVisibility).first()
    if av is None:
        av = AvatarVisibility(avatar_visibility_name="full", label="Ganze Figur")
        db.add(av)
        db.flush()
    return av.avatar_visibility_id


def _setup_open_experiment_with_participants(gender_slot1="Male", gender_slot2="Female"):
    """Creates study → experiment (open) → trial → 2 slots → 2 participants."""
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

        p1 = Participant(age=30, gender=gender_slot1, handedness="Right")
        p2 = Participant(age=25, gender=gender_slot2, handedness="Right")
        db.add_all([p1, p2])
        db.flush()

        slot1 = TrialSlot(trial_id=trial.trial_id, slot=1, avatar_visibility_id=av_id)
        slot2 = TrialSlot(trial_id=trial.trial_id, slot=2, avatar_visibility_id=av_id)
        db.add_all([slot1, slot2])
        db.flush()

        db.add(TrialParticipantSlot(trial_slot_id=slot1.trial_slot_id, participant_id=p1.participant_id))
        db.add(TrialParticipantSlot(trial_slot_id=slot2.trial_slot_id, participant_id=p2.participant_id))
        db.commit()
        return experiment.experiment_id, trial.trial_id
    finally:
        db.close()


def test_get_next_experiment_returns_oldest_open():
    exp_id, trial_id = _setup_open_experiment_with_participants()
    resp = client.get("/experiments/next")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["experiment_id"] == exp_id
    assert data["trial_id"] == trial_id
    assert len(data["slots"]) == 2
    slots_by_number = {s["slot"]: s["gender"] for s in data["slots"]}
    assert slots_by_number[1] == "Male"
    assert slots_by_number[2] == "Female"


def test_get_next_experiment_skips_started():
    db = SessionLocal()
    try:
        av_id = _get_or_create_avatar_visibility(db)
        study = Study(status="Aktiv")
        db.add(study)
        db.flush()

        # Create a started experiment (should be skipped)
        started_exp = Experiment(
            study_id=study.study_id,
            researcher="test",
            started_at=datetime.now(timezone.utc)
        )
        db.add(started_exp)
        db.flush()
        started_exp_id = started_exp.experiment_id

        # Create an open experiment with participants (should be returned)
        open_exp = Experiment(study_id=study.study_id, researcher="test")
        db.add(open_exp)
        db.flush()
        open_exp_id = open_exp.experiment_id

        trial = Trial(experiment_id=open_exp.experiment_id, trial_number=1)
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
        db.commit()
    finally:
        db.close()

    resp = client.get("/experiments/next")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["experiment_id"] == open_exp_id
    assert data["experiment_id"] != started_exp_id


def test_get_next_experiment_slots_not_assigned_returns_409():
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
        slot1 = TrialSlot(trial_id=trial.trial_id, slot=1, avatar_visibility_id=av_id)
        db.add(slot1)
        db.commit()
    finally:
        db.close()

    resp = client.get("/experiments/next")
    assert resp.status_code == status.HTTP_409_CONFLICT
