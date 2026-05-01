"""
Tests for the new analysis API endpoints added in Task 13.
These tests do NOT require a database connection — they exercise only the
computation endpoints (correlation, cross-study, PCA, clustering).
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from Backend.app import app

# Module-level client used only by pure-computation tests (lines below) that do not
# touch the database. DB-touching tests use the `client` fixture from conftest.py instead.
client = TestClient(app)


def test_correlation_endpoint_basic():
    payload = {
        "variables": {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 4.0, 3.0, 5.0, 6.0],
        }
    }
    response = client.post("/analysis/correlation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "pairs" in data
    assert data["n_pairs"] == 1


def test_correlation_endpoint_too_few_variables():
    payload = {"variables": {"x": [1.0, 2.0, 3.0]}}
    response = client.post("/analysis/correlation", json=payload)
    assert response.status_code == 400


def test_cross_study_endpoint():
    payload = {
        "study_data": {
            "HS1": [300.0, 320.0, 310.0, 290.0, 305.0],
            "HS2": [280.0, 295.0, 288.0, 270.0, 285.0],
        },
        "metric": "transfer_duration_ms"
    }
    response = client.post("/analysis/cross-study", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_descriptive_only"] is True
    assert data["baseline_ms"] == 300.0


def test_pca_endpoint_basic():
    payload = {
        "data": {
            "var_a": [1.0, 2.0, 3.0, 4.0, 5.0],
            "var_b": [5.0, 4.0, 3.0, 2.0, 1.0],
        },
        "n_components": 2
    }
    response = client.post("/analysis/pca", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "explained_variance_ratio" in data
    assert data["n_observations"] == 5


def test_pca_endpoint_too_few_variables():
    payload = {"data": {"only": [1.0, 2.0, 3.0]}, "n_components": 2}
    response = client.post("/analysis/pca", json=payload)
    assert response.status_code == 400


def test_clustering_endpoint_basic():
    payload = {
        "data": {
            "var_a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "var_b": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
        },
        "n_clusters": 2
    }
    response = client.post("/analysis/clustering", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert data["n_clusters"] == 2
    assert data["n_observations"] == 6


def test_clustering_endpoint_too_few_variables():
    payload = {"data": {"only": [1.0, 2.0, 3.0]}, "n_clusters": 2}
    response = client.post("/analysis/clustering", json=payload)
    assert response.status_code == 400

# ---------------------------------------------------------------------------
# Shared seed helper for analysis route tests
# ---------------------------------------------------------------------------

def _seed_minimal_handover_data(db_session, experiment_id, participant_id):
    """Seed: Trial → Handover → EyeTracking for analysis route 200 tests."""
    from datetime import datetime, timedelta
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.db_session import SessionLocal

    t0 = datetime(2024, 1, 1, 10, 0, 0)
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    handover = Handover(
        trial_id=trial.trial_id,
        giver=participant_id,
        receiver=participant_id,
        grasped_object="scalpel",
        giver_grasped_object=t0,
        receiver_touched_object=t0 + timedelta(seconds=1),
        receiver_grasped_object=t0 + timedelta(seconds=2),
        giver_released_object=t0 + timedelta(seconds=3),
    )
    db_session.add(handover)
    db_session.flush()
    tmp_s = SessionLocal()
    aoi = tmp_s.query(AreaOfInterest).filter_by(aoi="object").first()
    tmp_s.close()
    db_session.add(EyeTracking(
        handover_id=handover.handover_id,
        participant_id=participant_id,
        aoi_id=aoi.aoi_id,
        duration=300,
        starttime=t0 + timedelta(milliseconds=500),
    ))
    db_session.commit()
    return trial.trial_id, handover.handover_id


def _seed_minimal_questionnaire_data(db_session, trial_id, participant_id):
    """Seed: Questionnaire → Item → Response linked to a trial."""
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    q = Questionnaire(name="Q-Routes")
    db_session.add(q)
    db_session.flush()
    item = QuestionnaireItem(questionnaire_id=q.questionnaire_id, item_name="item1", order_index=0)
    db_session.add(item)
    db_session.flush()
    db_session.add(QuestionnaireResponse(
        trial_id=trial_id,
        participant_id=participant_id,
        questionnaire_item_id=item.questionnaire_item_id,
        response_value=60.0,
    ))
    db_session.commit()


# ---------------------------------------------------------------------------
# Experiment-level analysis endpoints — 200 paths
# ---------------------------------------------------------------------------

def test_experiment_eyetracking_200(client, db_session, experiment_id, participant_id):
    trial_id, _ = _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking")
    assert resp.status_code == 200
    assert "by_trial" in resp.json()


def test_experiment_eyetracking_phases_200(client, db_session, experiment_id, participant_id):
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking/phases")
    assert resp.status_code == 200
    assert "by_trial" in resp.json()


def test_experiment_eyetracking_transitions_200(client, db_session, experiment_id, participant_id):
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking/transitions")
    assert resp.status_code == 200
    assert "by_trial" in resp.json()


def test_experiment_ppi_200(client, db_session, experiment_id, participant_id):
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/ppi")
    assert resp.status_code == 200
    assert "by_trial" in resp.json()


def test_experiment_saccade_rate_200(client, db_session, experiment_id, participant_id):
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/eyetracking/saccade-rate")
    assert resp.status_code == 200
    assert "by_trial" in resp.json()


def test_experiment_performance_200(client, db_session, experiment_id, participant_id):
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/performance")
    assert resp.status_code == 200
    assert "by_trial" in resp.json()


def test_experiment_questionnaires_200(client, db_session, experiment_id, participant_id):
    trial_id, _ = _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    _seed_minimal_questionnaire_data(db_session, trial_id, participant_id)
    resp = client.get(f"/analysis/experiment/{experiment_id}/questionnaires")
    assert resp.status_code == 200
    assert "experiment_id" in resp.json()


# ---------------------------------------------------------------------------
# Study-level alias endpoint
# ---------------------------------------------------------------------------

def test_study_eye_tracking_hyphenated_alias_200(
    client, db_session, study_id, experiment_id, participant_id
):
    """GET /analysis/study/{id}/eye-tracking (hyphenated) returns 200."""
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.models.eyetracking import AreaOfInterest, EyeTracking
    from Backend.models.stimulus import StimulusType, Stimulus
    from Backend.models.trial.trial_slot import TrialSlot
    from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus
    from Backend.db_session import SessionLocal

    st = StimulusType(type_name="alias_cond")
    db_session.add(st)
    db_session.flush()
    stim = Stimulus(name="cond_alias", stimulus_type_id=st.stimulus_type_id)
    db_session.add(stim)
    db_session.flush()

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    slot = TrialSlot(trial_id=trial.trial_id, slot=1)
    db_session.add(slot)
    db_session.flush()
    db_session.add(TrialSlotStimulus(trial_slot_id=slot.trial_slot_id, stimulus_id=stim.stimulus_id))
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
        duration=200,
    ))
    db_session.commit()

    resp = client.get(f"/analysis/study/{study_id}/eye-tracking")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Export endpoints
# ---------------------------------------------------------------------------

def test_export_csv_200(client, db_session, study_id, experiment_id, participant_id):
    """GET /analysis/study/{id}/export/csv returns 200 with CSV content-type."""
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/study/{study_id}/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert len(resp.content) > 0


def test_export_xlsx_200(client, db_session, study_id, experiment_id, participant_id):
    """GET /analysis/study/{id}/export/xlsx returns 200 with XLSX content-type."""
    _seed_minimal_handover_data(db_session, experiment_id, participant_id)
    resp = client.get(f"/analysis/study/{study_id}/export/xlsx")
    assert resp.status_code == 200
    assert "spreadsheetml" in resp.headers.get("content-type", "")
    assert len(resp.content) > 0
