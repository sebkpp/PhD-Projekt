# Backend/tests/test_performance_analysis.py
"""
Unit tests for analyze_study_performance — focuses on the inferential
analysis path (k=2 and k≥3) via mocked DB repositories.
"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import numpy as np

import pytest

from Backend.services.data_analysis.performance_analysis_service import analyze_study_performance


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def _make_handover(base_ts: datetime, offsets_s: tuple[float, float, float, float]):
    """Return a mock Handover object with TIMESTAMP attributes."""
    h = MagicMock()
    h.giver_grasped_object = base_ts + timedelta(seconds=offsets_s[0])
    h.receiver_touched_object = base_ts + timedelta(seconds=offsets_s[1])
    h.receiver_grasped_object = base_ts + timedelta(seconds=offsets_s[2])
    h.giver_released_object = base_ts + timedelta(seconds=offsets_s[3])
    h.grasped_object = "scalpel"
    h.giver = 1
    h.receiver = 2
    return h


def _make_trial(trial_id: int, experiment_id: int):
    t = MagicMock()
    t.trial_id = trial_id
    t.experiment_id = experiment_id
    return t


def _make_experiment(experiment_id: int, study_id: int):
    e = MagicMock()
    e.experiment_id = experiment_id
    e.study_id = study_id
    return e


def _make_handovers_for_condition(n: int, base_phase1: float = 1.0,
                                   base_time: datetime | None = None) -> list:
    """Create n Handover mocks with realistic timing for a given condition."""
    rng = np.random.default_rng(42)
    base_time = base_time or datetime(2024, 1, 1, 10, 0, 0)
    handovers = []
    for i in range(n):
        phase1 = base_phase1 + rng.normal(0, 0.2)
        phase2 = 0.5 + rng.normal(0, 0.1)
        phase3 = 0.3 + rng.normal(0, 0.05)
        # offsets: giver_grasped=0, receiver_touched=phase1,
        #          receiver_grasped=phase1+phase2, giver_released=phase1+phase2+phase3
        base = base_time + timedelta(seconds=i * 10)
        handovers.append(_make_handover(base, (0, phase1, phase1 + phase2,
                                               phase1 + phase2 + phase3)))
    return handovers


# ---------------------------------------------------------------------------
# Two-condition test (k=2 path)
# ---------------------------------------------------------------------------

def test_analyze_study_performance_two_conditions():
    """Performance-Analyse funktioniert mit 2 Bedingungen (k=2 Pfad)."""
    study_id = 1
    n_experiments = 10  # must be > 3 for run_inferential_analysis to return a result

    # Build mock experiments — each experiment has one trial per condition
    experiments = [_make_experiment(i + 1, study_id) for i in range(n_experiments)]

    # Trials: experiment i → trial 2*i (cond_A) and trial 2*i+1 (cond_B)
    def make_trials(experiment_id):
        return [
            _make_trial(experiment_id * 2,     experiment_id),
            _make_trial(experiment_id * 2 + 1, experiment_id),
        ]

    # Stimuli: trial 2*i → cond_A, trial 2*i+1 → cond_B
    def make_stimuli_map(trials):
        return {
            trials[0].trial_id: [{"name": "cond_A"}],
            trials[1].trial_id: [{"name": "cond_B"}],
        }

    def make_handovers_for_trial(trial_id):
        # cond_A trials have even trial_id, cond_B have odd
        if trial_id % 2 == 0:
            return _make_handovers_for_condition(3, base_phase1=1.0)
        else:
            return _make_handovers_for_condition(3, base_phase1=2.0)

    session = MagicMock()
    session.query.return_value.filter_by.return_value.all.return_value = experiments

    with patch("Backend.services.data_analysis.performance_analysis_service.TrialRepository") as MockTrialRepo, \
         patch("Backend.services.data_analysis.performance_analysis_service.HandoverRepository") as MockHandoverRepo, \
         patch("Backend.services.data_analysis.performance_analysis_service.StimuliRepository") as MockStimuliRepo:

        mock_trial_repo = MockTrialRepo.return_value
        mock_handover_repo = MockHandoverRepo.return_value
        mock_stimuli_repo = MockStimuliRepo.return_value

        def get_trials(experiment_id):
            return make_trials(experiment_id)

        mock_trial_repo.get_by_experiment_id.side_effect = get_trials

        def get_stimuli_for_trials(trial_ids):
            # Reconstruct experiment_id from the first trial_id
            trials = [_make_trial(tid, tid // 2) for tid in trial_ids]
            return make_stimuli_map(trials)

        mock_stimuli_repo.get_stimuli_for_trials.side_effect = get_stimuli_for_trials
        mock_handover_repo.get_handovers_for_trial.side_effect = make_handovers_for_trial

        result = analyze_study_performance(session, study_id)

    assert result, "Result should not be empty"
    assert result["study_id"] == study_id
    assert set(result["conditions"]) == {"cond_A", "cond_B"}
    assert "performance" in result
    assert "by_condition" in result["performance"]
    assert "inferential" in result["performance"]

    inferential = result["performance"]["inferential"]
    assert isinstance(inferential, dict)
    # With 10 experiments (n=10 > 3), run_inferential_analysis should return a result
    assert inferential["total"] is not None, "total metric must have inferential result with n=10"
    for metric in ("total", "phase1", "phase2", "phase3"):
        assert metric in inferential
        if inferential[metric] is not None:
            assert "test_used" in inferential[metric]
            assert isinstance(inferential[metric]["test_used"], str)
            assert inferential[metric]["n_conditions"] == 2


# ---------------------------------------------------------------------------
# Three-condition test (k≥3 path)
# ---------------------------------------------------------------------------

def test_analyze_study_performance_three_conditions():
    """Performance-Analyse funktioniert mit 3 Bedingungen (k≥3 Pfad)."""
    study_id = 2
    n_experiments = 10  # enough for RM-ANOVA (need ≥5 for RM-ANOVA path)

    experiments = [_make_experiment(i + 1, study_id) for i in range(n_experiments)]

    COND_NAMES = ["cond_A", "cond_B", "cond_C"]
    BASE_TIMES = [1.0, 1.8, 2.5]

    def make_trials(experiment_id):
        return [
            _make_trial(experiment_id * 3,     experiment_id),
            _make_trial(experiment_id * 3 + 1, experiment_id),
            _make_trial(experiment_id * 3 + 2, experiment_id),
        ]

    def make_stimuli_map(trial_ids):
        result = {}
        for idx, tid in enumerate(trial_ids):
            result[tid] = [{"name": COND_NAMES[idx % 3]}]
        return result

    def make_handovers_for_trial(trial_id):
        cond_idx = trial_id % 3
        return _make_handovers_for_condition(3, base_phase1=BASE_TIMES[cond_idx])

    session = MagicMock()
    session.query.return_value.filter_by.return_value.all.return_value = experiments

    with patch("Backend.services.data_analysis.performance_analysis_service.TrialRepository") as MockTrialRepo, \
         patch("Backend.services.data_analysis.performance_analysis_service.HandoverRepository") as MockHandoverRepo, \
         patch("Backend.services.data_analysis.performance_analysis_service.StimuliRepository") as MockStimuliRepo:

        mock_trial_repo = MockTrialRepo.return_value
        mock_handover_repo = MockHandoverRepo.return_value
        mock_stimuli_repo = MockStimuliRepo.return_value

        mock_trial_repo.get_by_experiment_id.side_effect = make_trials

        def get_stimuli_for_trials(trial_ids):
            return make_stimuli_map(trial_ids)

        mock_stimuli_repo.get_stimuli_for_trials.side_effect = get_stimuli_for_trials
        mock_handover_repo.get_handovers_for_trial.side_effect = make_handovers_for_trial

        result = analyze_study_performance(session, study_id)

    assert result, "Result should not be empty"
    assert result["study_id"] == study_id
    assert set(result["conditions"]) == set(COND_NAMES)
    assert "performance" in result
    assert "inferential" in result["performance"]

    inferential = result["performance"]["inferential"]
    assert isinstance(inferential, dict)
    assert inferential["total"] is not None, "total metric must have inferential result with n=10"
    for metric in ("total", "phase1", "phase2", "phase3"):
        assert metric in inferential
        if inferential[metric] is not None:
            inf_result = inferential[metric]
            assert "test_used" in inf_result, f"test_used missing for metric {metric}"
            assert isinstance(inf_result["test_used"], str)
            assert inf_result["n_conditions"] == 3
            assert inf_result["test_used"] in ("rm_anova", "rm_anova_gg", "friedman")


# ---------------------------------------------------------------------------
# Edge-case: empty study returns empty dict
# ---------------------------------------------------------------------------

def test_analyze_study_performance_empty_study():
    """analyze_study_performance returns {} when study has no experiments."""
    session = MagicMock()
    session.query.return_value.filter_by.return_value.all.return_value = []

    result = analyze_study_performance(session, 999)
    assert result == {}


# ---------------------------------------------------------------------------
# calc_stats unit tests
# ---------------------------------------------------------------------------

from Backend.services.data_analysis.performance_analysis_service import (
    calc_stats,
    analyze_experiment_performance,
)


def test_calc_stats_normal():
    data = [
        {"phase1": 1.0, "phase2": 0.5, "phase3": 0.3, "total": 1.8},
        {"phase1": 1.2, "phase2": 0.6, "phase3": 0.4, "total": 2.2},
        {"phase1": 0.9, "phase2": 0.4, "phase3": 0.2, "total": 1.5},
        {"phase1": 1.1, "phase2": 0.55, "phase3": 0.35, "total": 2.0},
    ]
    result = calc_stats(data)
    assert "phase1_mean" in result
    assert "total_mean" in result
    assert isinstance(result["phase1_mean"], float)
    # Shapiro-Wilk requires n > 3
    assert result["phase1_normality_p"] is not None


def test_calc_stats_single_row():
    """With n=1 row, std/CI/skew return None/NaN paths -- no exception."""
    data = [{"phase1": 1.0, "phase2": 0.5, "phase3": 0.3, "total": 1.8}]
    result = calc_stats(data)
    assert result["phase1_mean"] == pytest.approx(1.0)
    # Shapiro-Wilk needs n > 3 -> normality_p is None
    assert result["phase1_normality_p"] is None


# ---------------------------------------------------------------------------
# analyze_experiment_performance integration test
# ---------------------------------------------------------------------------

def test_analyze_experiment_performance_empty(experiment_id):
    """Returns {} when experiment has no trials with handover data."""
    from Backend.db_session import SessionLocal
    session = SessionLocal()
    result = analyze_experiment_performance(session, experiment_id)
    session.close()
    assert result == {}


def test_analyze_experiment_performance_happy(
    db_session, experiment_id, participant_id
):
    """Happy path: one trial with one handover returns performance stats."""
    from datetime import datetime, timedelta
    from Backend.models.trial.trial import Trial
    from Backend.models.handover import Handover
    from Backend.db_session import SessionLocal

    t0 = datetime(2024, 1, 1, 10, 0, 0)
    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()
    db_session.add(Handover(
        trial_id=trial.trial_id,
        giver=participant_id,
        receiver=participant_id,
        grasped_object="scalpel",
        giver_grasped_object=t0,
        receiver_touched_object=t0 + timedelta(seconds=1),
        receiver_grasped_object=t0 + timedelta(seconds=1, milliseconds=500),
        giver_released_object=t0 + timedelta(seconds=2),
    ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_performance(session, experiment_id)
    session.close()

    assert "by_trial" in result
    assert trial.trial_id in result["by_trial"]


def test_analyze_study_performance_empty_smoke(study_id):
    """Smoke test: analyze_study_performance returns {} for a study with no experiments."""
    from Backend.db_session import SessionLocal
    session = SessionLocal()
    result = analyze_study_performance(session, study_id)
    session.close()
    assert result == {}
