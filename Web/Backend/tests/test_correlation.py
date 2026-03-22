import pytest
from Backend.services.data_analysis.correlation_service import (
    check_normality, calc_correlation, calc_correlation_matrix
)

def test_normality_normal_data():
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 3.0, 4.0]
    p, is_normal = check_normality(data)
    assert isinstance(p, float)
    assert isinstance(is_normal, bool)

def test_normality_too_few():
    p, is_normal = check_normality([1.0, 2.0])
    assert p == 1.0
    assert is_normal is True

def test_calc_correlation_positive():
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [2, 4, 5, 4, 5, 7, 8, 9, 10, 12]
    result = calc_correlation(x, y)
    assert result is not None
    assert result["r"] > 0.9
    assert result["method"] in ("pearson", "spearman")
    assert "interpretation" in result
    assert result["n"] == 10

def test_calc_correlation_too_few():
    result = calc_correlation([1, 2], [3, 4])
    assert result is None

def test_calc_correlation_matrix_basic():
    variables = {
        "transfer_time": [300, 320, 310, 290, 305, 315, 308, 298, 312, 322],
        "nasa_tlx": [60, 65, 58, 55, 62, 67, 59, 57, 63, 68],
        "ppi": [25, 20, 28, 32, 24, 19, 27, 31, 23, 18],
    }
    result = calc_correlation_matrix(variables)
    assert result["n_pairs"] == 3  # C(3,2) = 3
    assert len(result["pairs"]) == 3
    assert "alpha_corrected" in result
    for pair in result["pairs"]:
        assert "var_a" in pair
        assert "var_b" in pair
        assert "r" in pair
        assert "significant" in pair

def test_calc_correlation_matrix_bonferroni():
    """Bonferroni-Korrektur: p_corrected = p_uncorrected * n_pairs (max 1.0)."""
    variables = {
        "a": list(range(1, 11)),
        "b": list(range(1, 11)),  # perfekte Korrelation
    }
    result = calc_correlation_matrix(variables)
    pair = result["pairs"][0]
    # n_pairs=1, also p_corrected = p_uncorrected * 1
    assert pair["p_corrected"] == pytest.approx(pair["p_uncorrected"], abs=0.01)
