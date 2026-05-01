# Backend/tests/test_stats_utils.py
import math
import numpy as np
from Backend.utils.stats_utils import sanitize_stats, cohens_d, run_paired_test


def test_sanitize_stats_removes_nan():
    result = sanitize_stats({"a": float("nan"), "b": 1.0})
    assert result["a"] is None
    assert result["b"] == 1.0


def test_sanitize_stats_removes_inf():
    result = sanitize_stats({"x": float("inf")})
    assert result["x"] is None


def test_sanitize_stats_tuple():
    result = sanitize_stats({"t": (float("nan"), 2.0)})
    assert result["t"] == (None, 2.0)


def test_cohens_d_basic():
    d = cohens_d([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
    assert d is not None
    assert abs(d) > 0


def test_cohens_d_too_few():
    assert cohens_d([1.0], [2.0]) is None


def test_cohens_d_zero_std():
    # Both groups identical → pooled_std=0 → return 0.0
    result = cohens_d([2.0, 2.0, 2.0], [2.0, 2.0, 2.0])
    assert result == 0.0


def test_run_paired_test_needs_n_gt_3():
    # n=3 → None (guard: n <= 3 → return None)
    result = run_paired_test([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
    assert result is None


def test_run_paired_test_normal_data():
    rng = np.random.default_rng(42)
    a = list(rng.normal(5, 1, 10))
    b = list(rng.normal(7, 1, 10))
    result = run_paired_test(a, b)
    assert result is not None
    assert result["test"] in ("paired_ttest", "wilcoxon")
    assert "p_value" in result
    assert "effect_size_d" in result


def test_run_paired_test_returns_significant_flag():
    # Very different groups → should be significant
    rng = np.random.default_rng(0)
    a = list(rng.normal(0, 0.1, 10))
    b = list(rng.normal(10, 0.1, 10))
    result = run_paired_test(a, b)
    assert result is not None
    assert result["significant"] is True
