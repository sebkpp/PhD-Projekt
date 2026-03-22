"""Tests for eye_tracking_analysis_service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from Backend.services.data_analysis.eye_tracking_analysis_service import (
    calc_saccade_rate,
    calc_transitions,
    calc_ppi,
    analyze_aoi_inferential,
    _assign_phase,
    _compute_aoi_stats,
)


# ---------------------------------------------------------------------------
# calc_saccade_rate
# ---------------------------------------------------------------------------

def test_calc_saccade_rate_normal():
    assert calc_saccade_rate(10, 1000) == pytest.approx(10.0)


def test_calc_saccade_rate_zero_duration():
    assert calc_saccade_rate(5, 0) is None


def test_calc_saccade_rate_negative_duration():
    assert calc_saccade_rate(5, -100) is None


def test_calc_saccade_rate_zero_saccades():
    assert calc_saccade_rate(0, 1000) == pytest.approx(0.0)


def test_calc_saccade_rate_fractional():
    # 5 saccades in 500ms -> 10 per second
    assert calc_saccade_rate(5, 500) == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# calc_transitions
# ---------------------------------------------------------------------------

def test_calc_transitions_basic():
    result = calc_transitions(["obj", "hand", "obj", "partner"])
    assert result["obj->hand"] == 1
    assert result["hand->obj"] == 1
    assert result["obj->partner"] == 1


def test_calc_transitions_consecutive_same():
    """Consecutive identical AOIs are ignored."""
    result = calc_transitions(["obj", "obj", "hand"])
    assert result.get("obj->obj", 0) == 0
    assert result["obj->hand"] == 1


def test_calc_transitions_empty():
    assert calc_transitions([]) == {}


def test_calc_transitions_single():
    assert calc_transitions(["obj"]) == {}


def test_calc_transitions_all_same():
    result = calc_transitions(["obj", "obj", "obj"])
    assert result == {}


def test_calc_transitions_repeated_pair():
    result = calc_transitions(["a", "b", "a", "b"])
    assert result["a->b"] == 2
    assert result["b->a"] == 1


# ---------------------------------------------------------------------------
# calc_ppi
# ---------------------------------------------------------------------------

def test_calc_ppi_basic():
    records = [
        {"aoi_name": "environment", "phase": 3, "dwell_time_ms": 300, "duration_ms": 1000},
        {"aoi_name": "hand", "phase": 3, "dwell_time_ms": 700, "duration_ms": 1000},
    ]
    assert calc_ppi(records) == pytest.approx(30.0)


def test_calc_ppi_no_phase3():
    records = [{"aoi_name": "hand", "phase": 1, "dwell_time_ms": 500, "duration_ms": 1000}]
    assert calc_ppi(records) is None


def test_calc_ppi_zero_duration():
    records = [
        {"aoi_name": "environment", "phase": 3, "dwell_time_ms": 0, "duration_ms": 0},
    ]
    assert calc_ppi(records) is None


def test_calc_ppi_no_environment_aoi():
    records = [
        {"aoi_name": "hand", "phase": 3, "dwell_time_ms": 500, "duration_ms": 1000},
    ]
    # environment_aoi not present -> env_dwell = 0 -> PPI = 0%
    result = calc_ppi(records)
    assert result == pytest.approx(0.0)


def test_calc_ppi_100_percent():
    records = [
        {"aoi_name": "environment", "phase": 3, "dwell_time_ms": 1000, "duration_ms": 1000},
    ]
    assert calc_ppi(records) == pytest.approx(100.0)


def test_calc_ppi_alternative_field_name():
    """Supports 'area_of_interest_name' as fallback field."""
    records = [
        {"area_of_interest_name": "environment", "phase": 3, "dwell_time_ms": 400, "duration_ms": 1000},
        {"area_of_interest_name": "hand", "phase": 3, "dwell_time_ms": 600, "duration_ms": 1000},
    ]
    assert calc_ppi(records) == pytest.approx(40.0)


def test_calc_ppi_custom_phase():
    records = [
        {"aoi_name": "environment", "phase": 1, "dwell_time_ms": 200, "duration_ms": 500},
        {"aoi_name": "hand", "phase": 3, "dwell_time_ms": 700, "duration_ms": 1000},
    ]
    assert calc_ppi(records, phase=1) == pytest.approx(40.0)


def test_calc_ppi_inconsistent_duration_ms():
    """
    Documents behavior when duration_ms is inconsistent across records.
    max() is used — returns the largest value.
    """
    records = [
        {"aoi_name": "environment", "phase": 3, "dwell_time_ms": 300, "duration_ms": 800},
        {"aoi_name": "hand", "phase": 3, "dwell_time_ms": 200, "duration_ms": 1000},
    ]
    # max(800, 1000) = 1000; env_dwell = 300; PPI = 30.0
    result = calc_ppi(records)
    assert result == pytest.approx(30.0)


# ---------------------------------------------------------------------------
# analyze_aoi_inferential
# ---------------------------------------------------------------------------

def test_analyze_aoi_inferential_insufficient_conditions():
    """Single condition -> all results are None."""
    condition_aoi_durations = {
        "cond_a": {"hand": [100, 200, 300, 400, 500]},
    }
    result = analyze_aoi_inferential(condition_aoi_durations)
    assert result["hand"] is None


def test_analyze_aoi_inferential_two_conditions_insufficient_n():
    """n=2 per condition -> run_inferential_analysis returns None (needs n >= 3)."""
    condition_aoi_durations = {
        "cond_a": {"hand": [100, 200]},
        "cond_b": {"hand": [150, 250]},
    }
    result = analyze_aoi_inferential(condition_aoi_durations)
    # With n=2, inferential analysis should return None
    assert result["hand"] is None


def test_analyze_aoi_inferential_two_conditions_sufficient_n():
    """With enough data, returns an inferential result dict."""
    condition_aoi_durations = {
        "cond_a": {"hand": [100, 150, 120, 130, 140]},
        "cond_b": {"hand": [200, 250, 220, 230, 240]},
    }
    result = analyze_aoi_inferential(condition_aoi_durations)
    assert result["hand"] is not None
    assert "test_used" in result["hand"]
    assert "main_effect" in result["hand"]


def test_analyze_aoi_inferential_missing_aoi_in_one_condition():
    """AOI present in only one condition -> not enough conditions -> None."""
    condition_aoi_durations = {
        "cond_a": {"hand": [100, 200, 150, 180, 160], "partner": [50, 60, 70, 80, 90]},
        "cond_b": {"hand": [120, 210, 140, 170, 155]},
        # "partner" missing from cond_b
    }
    result = analyze_aoi_inferential(condition_aoi_durations)
    assert result["hand"] is not None  # present in both conditions
    assert result["partner"] is None   # only present in one condition


# ---------------------------------------------------------------------------
# Helpers for _assign_phase and _compute_aoi_stats
# ---------------------------------------------------------------------------

def _make_handover(t1, t2, t3, t4):
    """Return a mock Handover with the four phase-boundary timestamps."""
    h = MagicMock()
    h.giver_grasped_object = t1
    h.receiver_touched_object = t2
    h.receiver_grasped_object = t3
    h.giver_released_object = t4
    return h


BASE = datetime(2024, 1, 1, 10, 0, 0)


def _make_et(aoi_name=None, aoi_id=None, duration=100):
    """Return a mock EyeTracking object."""
    et = MagicMock()
    et.duration = duration
    if aoi_name is not None:
        aoi = MagicMock()
        aoi.aoi = aoi_name
        et.aoi = aoi
        et.aoi_id = None
    else:
        et.aoi = None
        et.aoi_id = aoi_id or 99
    return et


# ---------------------------------------------------------------------------
# _assign_phase
# ---------------------------------------------------------------------------

def test_assign_phase_1():
    t1 = BASE
    t2 = BASE + timedelta(seconds=1)
    t3 = BASE + timedelta(seconds=2)
    t4 = BASE + timedelta(seconds=3)
    h = _make_handover(t1, t2, t3, t4)
    et_start = BASE + timedelta(milliseconds=500)
    assert _assign_phase(et_start, h) == 1


def test_assign_phase_2():
    t1 = BASE
    t2 = BASE + timedelta(seconds=1)
    t3 = BASE + timedelta(seconds=2)
    t4 = BASE + timedelta(seconds=3)
    h = _make_handover(t1, t2, t3, t4)
    et_start = BASE + timedelta(seconds=1, milliseconds=500)
    assert _assign_phase(et_start, h) == 2


def test_assign_phase_3():
    t1 = BASE
    t2 = BASE + timedelta(seconds=1)
    t3 = BASE + timedelta(seconds=2)
    t4 = BASE + timedelta(seconds=3)
    h = _make_handover(t1, t2, t3, t4)
    et_start = BASE + timedelta(seconds=2, milliseconds=500)
    assert _assign_phase(et_start, h) == 3


def test_assign_phase_outside_all():
    t1 = BASE
    t2 = BASE + timedelta(seconds=1)
    t3 = BASE + timedelta(seconds=2)
    t4 = BASE + timedelta(seconds=3)
    h = _make_handover(t1, t2, t3, t4)
    et_start = BASE + timedelta(seconds=10)
    assert _assign_phase(et_start, h) is None


def test_assign_phase_starttime_none():
    h = _make_handover(BASE, BASE + timedelta(seconds=1), BASE + timedelta(seconds=2), BASE + timedelta(seconds=3))
    assert _assign_phase(None, h) is None


def test_assign_phase_all_handover_timestamps_none():
    h = _make_handover(None, None, None, None)
    assert _assign_phase(BASE, h) is None


# ---------------------------------------------------------------------------
# _compute_aoi_stats
# ---------------------------------------------------------------------------

def test_compute_aoi_stats_happy_path():
    aoi_map = {"object": "Objekt", "partner_face": "Gesicht"}
    ets = [
        _make_et(aoi_name="object", duration=200),
        _make_et(aoi_name="object", duration=300),
        _make_et(aoi_name="partner_face", duration=100),
    ]
    result = _compute_aoi_stats(ets, aoi_map, total_duration_ms=600)
    assert "object" in result
    assert result["object"]["fixation_count"] == 2
    assert result["object"]["total_duration_ms"] == 500
    assert result["partner_face"]["fixation_count"] == 1
    assert abs(result["object"]["percentage"] - 83.3333) < 0.01


def test_compute_aoi_stats_fallback_to_aoi_id():
    """When et.aoi is None, the key is str(et.aoi_id)."""
    ets = [_make_et(aoi_name=None, aoi_id=42, duration=150)]
    result = _compute_aoi_stats(ets, {}, total_duration_ms=150)
    assert "42" in result
    assert result["42"]["label"] == "42"  # no entry in aoi_map -> uses key as label


def test_compute_aoi_stats_zero_total_duration():
    """percentage is 0.0 when total_duration_ms is 0."""
    ets = [_make_et(aoi_name="object", duration=100)]
    result = _compute_aoi_stats(ets, {"object": "Objekt"}, total_duration_ms=0)
    assert result["object"]["percentage"] == 0.0


# ---------------------------------------------------------------------------
# _build_aoi_label_map integration tests
# ---------------------------------------------------------------------------

def test_build_aoi_label_map_happy(seed_aoi):
    """Returns a dict mapping aoi machine names to labels for seeded rows."""
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import _build_aoi_label_map
    session = SessionLocal()
    result = _build_aoi_label_map(session)
    session.close()
    assert "object" in result
    assert "environment" in result
    assert isinstance(result["object"], str)



# ---------------------------------------------------------------------------
# Integration test helpers
# ---------------------------------------------------------------------------

def _make_stimulus_chain(db_session, condition_name: str):
    """Create StimulusType (or reuse existing) → Stimulus and return stimulus_id."""
    from Backend.models.stimulus import StimulusType, Stimulus
    st = db_session.query(StimulusType).filter_by(type_name="condition").first()
    if st is None:
        st = StimulusType(type_name="condition")
        db_session.add(st)
        db_session.flush()
    stimulus = Stimulus(name=condition_name, stimulus_type_id=st.stimulus_type_id)
    db_session.add(stimulus)
    db_session.flush()
    return stimulus.stimulus_id


def _link_trial_stimulus(db_session, trial_id: int, stimulus_id: int):
    """Create TrialSlot → TrialSlotStimulus for a trial."""
    from Backend.models.trial.trial_slot import TrialSlot
    from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus
    slot = TrialSlot(trial_id=trial_id, slot=1)
    db_session.add(slot)
    db_session.flush()
    tss = TrialSlotStimulus(trial_slot_id=slot.trial_slot_id, stimulus_id=stimulus_id)
    db_session.add(tss)


def _add_eye_tracking(db_session, handover_id, participant_id, aoi_name, duration=200):
    """Insert one EyeTracking row linked to the given handover."""
    from Backend.db_session import SessionLocal
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    # Fetch the aoi_id from the seeded data (via a new query)
    tmp = SessionLocal()
    aoi = tmp.query(AreaOfInterest).filter_by(aoi=aoi_name).first()
    tmp.close()
    assert aoi is not None, f"AOI '{aoi_name}' not seeded"
    et = EyeTracking(
        handover_id=handover_id,
        participant_id=participant_id,
        aoi_id=aoi.aoi_id,
        duration=duration,
    )
    db_session.add(et)


# ---------------------------------------------------------------------------
# analyze_experiment_eye_tracking
# ---------------------------------------------------------------------------

def test_analyze_experiment_eye_tracking_empty(experiment_id):
    """Returns {} when experiment has no trials."""
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_eye_tracking
    session = SessionLocal()
    result = analyze_experiment_eye_tracking(session, experiment_id)
    session.close()
    assert result == {}


def test_analyze_experiment_eye_tracking_happy(
    db_session, experiment_id, participant_id
):
    """Happy path: one trial, one handover, two ET records."""
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_eye_tracking

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(trial_id=trial.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover)
    db_session.flush()
    _add_eye_tracking(db_session, handover.handover_id, participant_id, "object", 300)
    _add_eye_tracking(db_session, handover.handover_id, participant_id, "partner_face", 100)
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_eye_tracking(session, experiment_id)
    session.close()

    assert result["experiment_id"] == experiment_id
    assert len(result["by_trial"]) == 1
    trial_data = list(result["by_trial"].values())[0]
    assert "aoi_stats" in trial_data
    assert "object" in trial_data["aoi_stats"]


# ---------------------------------------------------------------------------
# analyze_study_eye_tracking
# ---------------------------------------------------------------------------

def test_analyze_study_eye_tracking_empty(study_id):
    """Returns {} when study has no experiments."""
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_study_eye_tracking
    session = SessionLocal()
    result = analyze_study_eye_tracking(session, study_id)
    session.close()
    assert result == {}


def test_analyze_study_eye_tracking_two_conditions(
    client, db_session, study_id, participant_id
):
    """Happy path: 2 experiments each with 1 trial + different condition."""
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_study_eye_tracking

    # Create two experiments in the same study
    resp_a = client.post("/experiments/", json={"name": "Exp A", "study_id": study_id})
    resp_b = client.post("/experiments/", json={"name": "Exp B", "study_id": study_id})
    assert resp_a.status_code == 201 and resp_b.status_code == 201
    exp_a_id = resp_a.json()["experiment_id"]
    exp_b_id = resp_b.json()["experiment_id"]

    # Create stimuli for two conditions
    stim_a_id = _make_stimulus_chain(db_session, "cond_A")
    stim_b_id = _make_stimulus_chain(db_session, "cond_B")

    # Trial A → cond_A
    trial_a = Trial(experiment_id=exp_a_id, trial_number=1)
    db_session.add(trial_a)
    db_session.flush()
    _link_trial_stimulus(db_session, trial_a.trial_id, stim_a_id)
    handover_a = Handover(trial_id=trial_a.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover_a)
    db_session.flush()
    _add_eye_tracking(db_session, handover_a.handover_id, participant_id, "object", 300)

    # Trial B → cond_B
    trial_b = Trial(experiment_id=exp_b_id, trial_number=1)
    db_session.add(trial_b)
    db_session.flush()
    _link_trial_stimulus(db_session, trial_b.trial_id, stim_b_id)
    handover_b = Handover(trial_id=trial_b.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover_b)
    db_session.flush()
    _add_eye_tracking(db_session, handover_b.handover_id, participant_id, "partner_face", 200)

    db_session.commit()

    session = SessionLocal()
    result = analyze_study_eye_tracking(session, study_id)
    session.close()

    assert result["study_id"] == study_id
    assert set(result["conditions"]) == {"cond_A", "cond_B"}
    assert "cond_A" in result["by_condition"]
    assert "cond_B" in result["by_condition"]


# ---------------------------------------------------------------------------
# analyze_experiment_eye_tracking_phases
# ---------------------------------------------------------------------------

def test_analyze_experiment_eye_tracking_phases_happy(
    db_session, experiment_id, participant_id
):
    """Phases are populated when handover timestamps are set."""
    from datetime import datetime, timedelta
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_eye_tracking_phases

    t0 = datetime(2024, 1, 1, 10, 0, 0)
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(
        trial_id=trial.trial_id,
        giver=participant_id,
        receiver=participant_id,
        giver_grasped_object=t0,
        receiver_touched_object=t0 + timedelta(seconds=1),
        receiver_grasped_object=t0 + timedelta(seconds=2),
        giver_released_object=t0 + timedelta(seconds=3),
    )
    db_session.add(handover)
    db_session.flush()
    # ET in phase 1 (starttime between t0 and t0+1s)
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    tmp_s = SessionLocal()
    aoi = tmp_s.query(AreaOfInterest).filter_by(aoi="object").first()
    tmp_s.close()
    et = EyeTracking(
        handover_id=handover.handover_id,
        participant_id=participant_id,
        aoi_id=aoi.aoi_id,
        duration=200,
        starttime=t0 + timedelta(milliseconds=500),
    )
    db_session.add(et)
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_eye_tracking_phases(session, experiment_id)
    session.close()

    assert result["experiment_id"] == experiment_id
    trial_data = list(result["by_trial"].values())[0]
    assert 1 in trial_data["phases"]
    assert "object" in trial_data["phases"][1]


def test_analyze_experiment_eye_tracking_phases_all_timestamps_none(
    db_session, experiment_id, participant_id
):
    """When all handover timestamps are None, phases are empty dicts — no exception."""
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_eye_tracking_phases

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(trial_id=trial.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover)
    db_session.flush()
    tmp_s = SessionLocal()
    aoi = tmp_s.query(AreaOfInterest).filter_by(aoi="object").first()
    tmp_s.close()
    db_session.add(EyeTracking(
        handover_id=handover.handover_id,
        participant_id=participant_id,
        aoi_id=aoi.aoi_id,
        duration=100,
    ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_eye_tracking_phases(session, experiment_id)
    session.close()
    trial_data = list(result["by_trial"].values())[0]
    # All phase dicts should be empty (ET has no phase assignment)
    for phase_num in (1, 2, 3):
        assert trial_data["phases"][phase_num] == {}


# ---------------------------------------------------------------------------
# analyze_experiment_eye_tracking_transitions
# ---------------------------------------------------------------------------

def test_analyze_experiment_eye_tracking_transitions_happy(
    db_session, experiment_id, participant_id
):
    """Transitions are counted from AOI sequence sorted by starttime."""
    from datetime import datetime, timedelta
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_eye_tracking_transitions

    t0 = datetime(2024, 1, 1, 10, 0, 0)
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(trial_id=trial.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover)
    db_session.flush()
    tmp_s = SessionLocal()
    aoi_obj = tmp_s.query(AreaOfInterest).filter_by(aoi="object").first()
    aoi_face = tmp_s.query(AreaOfInterest).filter_by(aoi="partner_face").first()
    tmp_s.close()
    # sequence: object → partner_face → object
    for i, (aoi, offset_s) in enumerate([(aoi_obj, 0), (aoi_face, 1), (aoi_obj, 2)]):
        db_session.add(EyeTracking(
            handover_id=handover.handover_id,
            participant_id=participant_id,
            aoi_id=aoi.aoi_id,
            duration=100,
            starttime=t0 + timedelta(seconds=offset_s),
        ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_eye_tracking_transitions(session, experiment_id)
    session.close()

    trial_data = list(result["by_trial"].values())[0]
    assert trial_data["aoi_sequence_length"] == 3
    assert trial_data["transitions"].get("object->partner_face") == 1
    assert trial_data["transitions"].get("partner_face->object") == 1


def test_analyze_experiment_eye_tracking_transitions_none_starttime(
    db_session, experiment_id, participant_id
):
    """ET with starttime=None sorts to front via datetime.min — no exception."""
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_eye_tracking_transitions

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(trial_id=trial.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover)
    db_session.flush()
    tmp_s = SessionLocal()
    aoi = tmp_s.query(AreaOfInterest).filter_by(aoi="object").first()
    tmp_s.close()
    db_session.add(EyeTracking(
        handover_id=handover.handover_id,
        participant_id=participant_id,
        aoi_id=aoi.aoi_id,
        duration=100,
        starttime=None,
    ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_eye_tracking_transitions(session, experiment_id)
    session.close()
    assert "by_trial" in result


# ---------------------------------------------------------------------------
# analyze_experiment_ppi
# ---------------------------------------------------------------------------

def test_analyze_experiment_ppi_happy(
    db_session, experiment_id, participant_id
):
    """PPI is computed when phase-3 ET with 'environment' AOI exists."""
    from datetime import datetime, timedelta
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_ppi

    t0 = datetime(2024, 1, 1, 10, 0, 0)
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(
        trial_id=trial.trial_id,
        giver=participant_id,
        receiver=participant_id,
        giver_grasped_object=t0,
        receiver_touched_object=t0 + timedelta(seconds=1),
        receiver_grasped_object=t0 + timedelta(seconds=2),
        giver_released_object=t0 + timedelta(seconds=3),
    )
    db_session.add(handover)
    db_session.flush()
    tmp_s = SessionLocal()
    aoi_env = tmp_s.query(AreaOfInterest).filter_by(aoi="environment").first()
    tmp_s.close()
    # ET in phase 3 (t3 <= starttime <= t4)
    db_session.add(EyeTracking(
        handover_id=handover.handover_id,
        participant_id=participant_id,
        aoi_id=aoi_env.aoi_id,
        duration=500,
        starttime=t0 + timedelta(seconds=2, milliseconds=500),
    ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_ppi(session, experiment_id)
    session.close()

    trial_data = list(result["by_trial"].values())[0]
    # participant_id == giver, so ppi_giver should be set
    assert trial_data["ppi_giver"] is not None
    assert trial_data["ppi_receiver"] is None


def test_analyze_experiment_ppi_no_phase3(
    db_session, experiment_id, participant_id
):
    """When no phase-3 ET records exist, ppi_giver and ppi_receiver are None."""
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_ppi

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    # Handover with all None timestamps → _assign_phase always returns None
    db_session.add(Handover(trial_id=trial.trial_id, giver=participant_id, receiver=participant_id))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_ppi(session, experiment_id)
    session.close()

    trial_data = list(result["by_trial"].values())[0]
    assert trial_data["ppi_giver"] is None
    assert trial_data["ppi_receiver"] is None


# ---------------------------------------------------------------------------
# analyze_experiment_saccade_rate
# ---------------------------------------------------------------------------

def test_analyze_experiment_saccade_rate_happy(
    db_session, experiment_id, participant_id
):
    """Saccade rate is non-None when ET records with distinct AOIs exist."""
    from datetime import datetime, timedelta
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_saccade_rate

    t0 = datetime(2024, 1, 1, 10, 0, 0)
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(trial_id=trial.trial_id, giver=participant_id, receiver=participant_id)
    db_session.add(handover)
    db_session.flush()
    tmp_s = SessionLocal()
    aoi_obj = tmp_s.query(AreaOfInterest).filter_by(aoi="object").first()
    aoi_env = tmp_s.query(AreaOfInterest).filter_by(aoi="environment").first()
    tmp_s.close()
    for i, (aoi, ts) in enumerate([(aoi_obj, t0), (aoi_env, t0 + timedelta(seconds=1))]):
        db_session.add(EyeTracking(
            handover_id=handover.handover_id,
            participant_id=participant_id,
            aoi_id=aoi.aoi_id,
            duration=500,
            starttime=ts,
        ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_saccade_rate(session, experiment_id)
    session.close()

    trial_data = list(result["by_trial"].values())[0]
    # participant is giver, so giver saccade rate should be computed
    assert trial_data["saccade_rate_giver"] is not None


def test_analyze_experiment_saccade_rate_empty(experiment_id):
    """Returns {} when experiment has no trials."""
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.eye_tracking_analysis_service import analyze_experiment_saccade_rate
    session = SessionLocal()
    result = analyze_experiment_saccade_rate(session, experiment_id)
    session.close()
    assert result == {}
