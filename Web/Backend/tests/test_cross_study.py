import pytest
from Backend.services.data_analysis.cross_study_service import (
    calc_mean_ci, compare_studies_descriptive, forest_plot_data
)


def test_calc_mean_ci_basic():
    values = [100, 110, 120, 130, 140]
    result = calc_mean_ci(values)
    assert result["mean"] == pytest.approx(120.0)
    assert result["n"] == 5
    assert result["ci_lower"] < result["mean"]
    assert result["ci_upper"] > result["mean"]


def test_calc_mean_ci_single_value():
    result = calc_mean_ci([42.0])
    assert result["mean"] == pytest.approx(42.0)
    assert result["ci_lower"] == pytest.approx(42.0)
    assert result["ci_upper"] == pytest.approx(42.0)


def test_calc_mean_ci_empty():
    result = calc_mean_ci([])
    assert result["mean"] is None
    assert result["n"] == 0


def test_compare_studies_descriptive_basic():
    study_data = {
        "HS1_visual": [300, 320, 310, 330, 315],
        "HS2_audio": [280, 295, 288, 270, 285],
        "HS3_tactile": [260, 275, 268, 255, 270],
    }
    result = compare_studies_descriptive(study_data, metric="transfer_duration_ms")
    assert result["is_descriptive_only"] is True
    assert "warning" in result
    assert result["baseline_ms"] == 300.0
    assert set(result["conditions"].keys()) == {"HS1_visual", "HS2_audio", "HS3_tactile"}
    for cond_data in result["conditions"].values():
        assert "mean" in cond_data
        assert "ci_lower" in cond_data
        assert "n" in cond_data


def test_compare_studies_no_baseline_for_other_metrics():
    result = compare_studies_descriptive({"A": [1, 2, 3]}, metric="nasa_tlx_score")
    assert result["baseline_ms"] is None


def test_forest_plot_data_sorted():
    effect_sizes = {
        "HS2: A": {"d": 0.4, "ci_lower": 0.1, "ci_upper": 0.7, "n": 15, "study": "HS2"},
        "HS1: V": {"d": 0.8, "ci_lower": 0.4, "ci_upper": 1.2, "n": 20, "study": "HS1"},
        "HS3: T": {"d": 1.2, "ci_lower": 0.7, "ci_upper": 1.7, "n": 18, "study": "HS3"},
    }
    rows = forest_plot_data(effect_sizes)
    assert rows[0]["d"] == 1.2  # größter zuerst
    assert rows[-1]["d"] == 0.4  # kleinster zuletzt
    assert len(rows) == 3
