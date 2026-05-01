from fastapi.testclient import TestClient
from starlette import status
from Backend.app import app
from Backend.db_session import SessionLocal
from Backend.models.avatar_visibility import AvatarVisibility
from Backend.models.experiment import Experiment
from Backend.models.trial.trial import Trial
from Backend.models.trial.trial_slot import TrialSlot
from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus
from Backend.models.stimulus import Stimulus, StimulusType, StimulusVisual, StimulusAuditiv
from Backend.models.study.study import Study

client = TestClient(app)


def _get_or_create_avatar_visibility(db):
    av = db.query(AvatarVisibility).first()
    if av is None:
        av = AvatarVisibility(avatar_visibility_name="full", label="Ganze Figur")
        db.add(av)
        db.flush()
    return av.avatar_visibility_id


def _setup_trial_with_stimuli():
    """Creates study -> experiment -> trial -> 2 slots -> stimuli. Returns trial_id."""
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
        slot2 = TrialSlot(trial_id=trial.trial_id, slot=2, avatar_visibility_id=av_id)
        db.add_all([slot1, slot2])
        db.flush()

        visual_type = StimulusType(type_name="visual")
        audio_type = StimulusType(type_name="auditory")
        db.add_all([visual_type, audio_type])
        db.flush()

        s_visual = Stimulus(name="outer_hand", stimulus_type_id=visual_type.stimulus_type_id)
        s_audio = Stimulus(name="low_medium", stimulus_type_id=audio_type.stimulus_type_id)
        db.add_all([s_visual, s_audio])
        db.flush()

        db.add(StimulusVisual(stimulus_id=s_visual.stimulus_id, stimulus_name="outer_hand"))
        db.add(StimulusAuditiv(stimulus_id=s_audio.stimulus_id, frequency=50, volume=50))
        db.flush()

        db.add(TrialSlotStimulus(trial_slot_id=slot1.trial_slot_id, stimulus_id=s_visual.stimulus_id))
        db.add(TrialSlotStimulus(trial_slot_id=slot1.trial_slot_id, stimulus_id=s_audio.stimulus_id))
        db.commit()
        return trial.trial_id
    finally:
        db.close()


def test_get_trial_stimuli_returns_slots():
    trial_id = _setup_trial_with_stimuli()
    resp = client.get(f"/trials/{trial_id}/stimuli")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
    slot1 = next(s for s in data if s["slot"] == 1)
    assert len(slot1["stimuli"]) == 2


def test_get_trial_stimuli_includes_visual_params():
    trial_id = _setup_trial_with_stimuli()
    resp = client.get(f"/trials/{trial_id}/stimuli")
    data = resp.json()
    slot1 = next(s for s in data if s["slot"] == 1)
    visual = next(s for s in slot1["stimuli"] if s["stimulus"]["stimulus_type"] == "visual")
    assert visual["stimulus"]["visuals"] == ["outer_hand"]


def test_get_trial_stimuli_includes_auditory_params():
    trial_id = _setup_trial_with_stimuli()
    resp = client.get(f"/trials/{trial_id}/stimuli")
    data = resp.json()
    slot1 = next(s for s in data if s["slot"] == 1)
    audio = next(s for s in slot1["stimuli"] if s["stimulus"]["stimulus_type"] == "auditory")
    assert audio["stimulus"]["auditives"][0]["frequency"] == 50
    assert audio["stimulus"]["auditives"][0]["volume"] == 50


def test_get_trial_stimuli_empty_slot_returns_empty_list():
    trial_id = _setup_trial_with_stimuli()
    resp = client.get(f"/trials/{trial_id}/stimuli")
    data = resp.json()
    slot2 = next(s for s in data if s["slot"] == 2)
    assert slot2["stimuli"] == []


def test_get_trial_stimuli_nonexistent_trial_returns_404():
    resp = client.get("/trials/99999/stimuli")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
