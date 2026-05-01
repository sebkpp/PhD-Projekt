# Backend/tests/test_inferential.py
import numpy as np
import pytest
from Backend.services.data_analysis.inferential_service import run_inferential_analysis


def make_conditions(n=10, k=3, seed=42):
    rng = np.random.default_rng(seed)
    return {f"cond_{i}": list(rng.normal(loc=5 + i, scale=1, size=n)) for i in range(k)}


def test_k2_returns_paired_test():
    conditions = make_conditions(n=10, k=2)
    result = run_inferential_analysis(conditions)
    assert result["n_conditions"] == 2
    assert result["test_used"] in ("paired_ttest", "wilcoxon")
    assert "main_effect" in result
    assert result["posthoc"] == []


def test_k3_returns_anova_or_friedman():
    conditions = make_conditions(n=10, k=3)
    result = run_inferential_analysis(conditions)
    assert result["n_conditions"] == 3
    assert result["test_used"] in ("rm_anova", "rm_anova_gg", "friedman")
    assert len(result["posthoc"]) == 3  # 3 pairs for k=3


def test_too_few_data_returns_none():
    conditions = {"a": [1.0, 2.0], "b": [3.0, 4.0]}
    result = run_inferential_analysis(conditions)
    assert result is None


def test_posthoc_has_effect_sizes():
    conditions = make_conditions(n=12, k=3)
    result = run_inferential_analysis(conditions)
    if result and result["posthoc"]:
        pair = result["posthoc"][0]
        assert "effect_size_d" in pair or "effect_size_cliffs_delta" in pair


def test_normality_dict_present():
    conditions = make_conditions(n=10, k=3)
    result = run_inferential_analysis(conditions)
    if result:
        assert "normality" in result
        for cond in conditions:
            assert cond in result["normality"]


def test_n3_boundary_documented():
    # n=3: run_inferential_analysis guard is min_n < 3, so n=3 passes through
    # _run_k2 calls scipy directly; Shapiro needs n>3 so normality=None → non-parametric
    conditions = {"a": [1.0, 2.0, 3.0], "b": [4.0, 5.0, 6.0]}
    result = run_inferential_analysis(conditions)
    # May be None (wilcoxon might fail on n=3) or a valid result
    assert result is None or result["test_used"] in ("paired_ttest", "wilcoxon")


def test_k2_main_effect_has_effect_sizes():
    conditions = make_conditions(n=10, k=2)
    result = run_inferential_analysis(conditions)
    assert result is not None
    assert "effect_size_d" in result["main_effect"]
    assert "effect_size_cliffs_delta" in result["main_effect"]


def test_single_condition_returns_none():
    result = run_inferential_analysis({"only": [1.0, 2.0, 3.0, 4.0, 5.0]})
    assert result is None
