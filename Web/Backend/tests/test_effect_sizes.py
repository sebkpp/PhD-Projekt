import numpy as np
import pytest
from Backend.services.data_analysis.effect_size_service import (
    cliffs_delta, interpret_cohens_d, interpret_eta2p, interpret_cliffs_delta,
    omega2p_from_anova, kendalls_w_from_friedman,
)


def test_cliffs_delta_positive():
    d = cliffs_delta([3, 4, 5], [1, 2, 3])
    assert d is not None
    assert d > 0


def test_cliffs_delta_negative():
    d = cliffs_delta([1, 2], [4, 5])
    assert d < 0


def test_cliffs_delta_empty():
    assert cliffs_delta([], [1, 2]) is None


def test_cliffs_delta_tie():
    assert cliffs_delta([2, 2], [2, 2]) == 0.0


def test_interpret_cohens_d():
    assert interpret_cohens_d(0.1) == "vernachlässigbar"
    assert interpret_cohens_d(0.4) == "klein"
    assert interpret_cohens_d(0.7) == "mittel"
    assert interpret_cohens_d(1.0) == "groß"


def test_interpret_eta2p():
    assert interpret_eta2p(0.005) == "klein"
    assert interpret_eta2p(0.08) == "mittel"
    assert interpret_eta2p(0.15) == "groß"


def test_omega2p_from_anova_basic():
    result = omega2p_from_anova(ss_effect=10, df_effect=2, ss_error=20, df_error=18)
    assert result is not None
    assert 0.0 <= result <= 1.0


def test_omega2p_zero_df_error():
    assert omega2p_from_anova(10, 2, 20, 0) is None


def test_kendalls_w_from_friedman():
    # 5 subjects, 3 conditions
    data = np.array([[3, 1, 2], [1, 3, 2], [2, 1, 3], [3, 2, 1], [1, 2, 3]], dtype=float)
    w = kendalls_w_from_friedman(data)
    assert w is not None
    assert 0.0 <= w <= 1.0


def test_kendalls_w_too_few():
    data = np.array([[1, 2]], dtype=float)
    assert kendalls_w_from_friedman(data) is None
