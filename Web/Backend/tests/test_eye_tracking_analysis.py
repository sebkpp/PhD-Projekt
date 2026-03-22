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
