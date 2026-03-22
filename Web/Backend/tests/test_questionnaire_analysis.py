"""Tests for instrument-aware questionnaire scoring functions."""
import pytest

from Backend.services.data_analysis.questionnaire_analysis_service import (
    score_nasa_tlx,
    score_sus,
    score_attrakdiff2,
    score_iso_metrics,
    score_questionnaire,
)


# ---------------------------------------------------------------------------
# NASA-TLX
# ---------------------------------------------------------------------------

def test_score_nasa_tlx_complete():
    responses = {
        "mental_demand": 80,
        "physical_demand": 60,
        "temporal_demand": 70,
        "performance": 50,
        "effort": 90,
        "frustration": 40,
    }
    result = score_nasa_tlx(responses)
    assert result["total_score"] == pytest.approx(65.0)
    assert result["instrument"] == "nasa_tlx"
    assert result["subscales"] == responses


def test_score_nasa_tlx_partial():
    """Missing subscales are ignored (mean of present ones)."""
    result = score_nasa_tlx({"mental_demand": 80, "effort": 60})
    assert result["total_score"] == pytest.approx(70.0)
    assert result["instrument"] == "nasa_tlx"


def test_score_nasa_tlx_single_subscale():
    result = score_nasa_tlx({"frustration": 100})
    assert result["total_score"] == pytest.approx(100.0)


def test_score_nasa_tlx_empty():
    result = score_nasa_tlx({})
    assert result["total_score"] == pytest.approx(0.0)
    assert result["instrument"] == "nasa_tlx"


def test_score_nasa_tlx_ignores_unknown_keys():
    """Unknown keys that are not NASA-TLX subscales are ignored in scoring."""
    result = score_nasa_tlx({"mental_demand": 50, "unknown_scale": 100})
    assert result["total_score"] == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# SUS
# ---------------------------------------------------------------------------

def test_score_sus_standard():
    # Perfect usability: odd items (1-based 1,3,5,7,9 = 0-based even indices) = 5,
    # even items (1-based 2,4,6,8,10 = 0-based odd indices) = 1
    responses = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(100.0)
    assert result["grade"] == "A"
    assert result["instrument"] == "sus"


def test_score_sus_poor():
    responses = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]  # poor usability
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(0.0)
    assert result["grade"] == "F"


def test_score_sus_grade_b():
    # Construct a response that gives ~75 score
    # For a uniform mid score: odd items 4, even items 2 → (4-1)*2.5=7.5 and (5-2)*2.5=7.5 each → 75
    responses = [4, 2, 4, 2, 4, 2, 4, 2, 4, 2]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(75.0)
    assert result["grade"] == "B"


def test_score_sus_grade_c():
    # odd items 3, even items 3 → (3-1)*2.5=5, (5-3)*2.5=5 → total 50
    responses = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(50.0)
    assert result["grade"] == "C"


def test_score_sus_grade_d():
    # Aim for ~37.5 (>= 35, < 50)
    # odd items 2.5, even items 3.5 is not integer, use: odd=2, even=4
    # (2-1)*2.5=2.5, (5-4)*2.5=2.5 → 25 per pair, 5 pairs → 25. That's F.
    # Let's try odd=2, even=2: (2-1)*2.5=2.5, (5-2)*2.5=7.5 → 50 per pair... no
    # Try odd=2, even=4 → 2.5 + 2.5=5 per pair, 5 pairs → 25 = F
    # Try odd=3, even=4 → 5 + 2.5=7.5 per pair → 37.5 = D
    responses = [3, 4, 3, 4, 3, 4, 3, 4, 3, 4]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(37.5)
    assert result["grade"] == "D"


def test_score_sus_grade_f():
    # odd=1, even=5 → 0 + 0 = 0 per pair → total 0
    responses = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(0.0)
    assert result["grade"] == "F"


# ---------------------------------------------------------------------------
# AttrakDiff2
# ---------------------------------------------------------------------------

def test_score_attrakdiff2():
    responses = {"PQ": [2, 1, 3], "HQS": [1, 2], "HQI": [3, 3], "ATT": [2]}
    result = score_attrakdiff2(responses)
    assert "PQ" in result["subscales"]
    assert result["subscales"]["PQ"] == pytest.approx(2.0)
    assert result["subscales"]["HQS"] == pytest.approx(1.5)
    assert result["subscales"]["HQI"] == pytest.approx(3.0)
    assert result["subscales"]["ATT"] == pytest.approx(2.0)
    assert "hq_total" in result
    assert result["hq_total"] == pytest.approx(2.25)  # (1.5 + 3.0) / 2
    assert result["instrument"] == "attrakdiff2"


def test_score_attrakdiff2_total_score():
    responses = {"PQ": [2.0], "HQS": [2.0], "HQI": [2.0], "ATT": [2.0]}
    result = score_attrakdiff2(responses)
    assert result["total_score"] == pytest.approx(2.0)


def test_score_attrakdiff2_negative_values():
    responses = {"PQ": [-3, -1], "HQS": [-2], "HQI": [1, -1], "ATT": [0]}
    result = score_attrakdiff2(responses)
    assert result["subscales"]["PQ"] == pytest.approx(-2.0)
    assert result["subscales"]["HQS"] == pytest.approx(-2.0)
    assert result["subscales"]["HQI"] == pytest.approx(0.0)
    assert result["subscales"]["ATT"] == pytest.approx(0.0)
    assert result["instrument"] == "attrakdiff2"


def test_score_attrakdiff2_partial_subscales():
    """Works with only some subscales present."""
    responses = {"PQ": [1, 2], "ATT": [3]}
    result = score_attrakdiff2(responses)
    assert "PQ" in result["subscales"]
    assert "ATT" in result["subscales"]
    assert result["hq_total"] == pytest.approx(0.0)  # no HQS/HQI


# ---------------------------------------------------------------------------
# ISO-Metrics
# ---------------------------------------------------------------------------

def test_score_iso_metrics():
    responses = {"suitability": [3, 4], "self_descriptiveness": [2, 5, 1]}
    result = score_iso_metrics(responses)
    assert result["subscales"]["suitability"] == pytest.approx(3.5)
    assert result["subscales"]["self_descriptiveness"] == pytest.approx(8 / 3, abs=1e-3)
    assert result["instrument"] == "iso_metrics"


def test_score_iso_metrics_total():
    responses = {"a": [4.0], "b": [2.0]}
    result = score_iso_metrics(responses)
    assert result["total_score"] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Dispatcher: score_questionnaire
# ---------------------------------------------------------------------------

def test_score_questionnaire_dispatcher_nasa_tlx():
    result = score_questionnaire("nasa_tlx", {"mental_demand": 50})
    assert result is not None
    assert result["instrument"] == "nasa_tlx"


def test_score_questionnaire_dispatcher_sus():
    result = score_questionnaire("sus", [3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
    assert result is not None
    assert result["instrument"] == "sus"


def test_score_questionnaire_dispatcher_attrakdiff2():
    result = score_questionnaire("attrakdiff2", {"PQ": [1, 2]})
    assert result is not None
    assert result["instrument"] == "attrakdiff2"


def test_score_questionnaire_dispatcher_iso_metrics():
    result = score_questionnaire("iso_metrics", {"scale_a": [3, 4]})
    assert result is not None
    assert result["instrument"] == "iso_metrics"


def test_score_questionnaire_dispatcher_unknown():
    result = score_questionnaire("unknown_instrument", {})
    assert result is None


def test_score_questionnaire_dispatcher_none_instrument():
    result = score_questionnaire(None, {})
    assert result is None


def test_score_questionnaire_dispatcher_case_insensitive():
    result = score_questionnaire("NASA_TLX", {"mental_demand": 50})
    assert result is not None
    assert result["instrument"] == "nasa_tlx"
