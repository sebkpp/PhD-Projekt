import math
import numpy as np


def cliffs_delta(x: list, y: list) -> float | None:
    if not x or not y:
        return None
    dominance = sum(
        1 if xi > yj else (-1 if xi < yj else 0)
        for xi in x for yj in y
    )
    return dominance / (len(x) * len(y))


def interpret_cohens_d(d: float) -> str:
    d = abs(d)
    if d < 0.2:
        return "vernachlässigbar"
    if d < 0.5:
        return "klein"
    if d < 0.8:
        return "mittel"
    return "groß"


def interpret_eta2p(eta2p: float) -> str:
    if eta2p < 0.06:
        return "klein"
    if eta2p < 0.14:
        return "mittel"
    return "groß"


def interpret_cliffs_delta(d: float) -> str:
    d = abs(d)
    if d < 0.15:
        return "vernachlässigbar"
    if d < 0.33:
        return "klein"
    if d < 0.47:
        return "mittel"
    return "groß"


def omega2p_from_anova(ss_effect: float, df_effect: float,
                        ss_error: float, df_error: float) -> float | None:
    """Bias-corrected ω²p from ANOVA sum-of-squares."""
    if df_error == 0:
        return None
    ms_error = ss_error / df_error
    ss_total = ss_effect + ss_error
    denominator = ss_total + ms_error
    if denominator == 0:
        return None
    result = (ss_effect - df_effect * ms_error) / denominator
    result = max(0.0, result)  # can be slightly negative → clamp to 0
    return None if (math.isnan(result) or math.isinf(result)) else round(result, 4)


def kendalls_w_from_friedman(data: np.ndarray) -> float | None:
    """
    Compute Kendall's W from a subjects × conditions matrix.
    W = 12 * S / (k² * (n³ - n))  where S = sum of squared deviations of rank sums.
    """
    n, k = data.shape  # n=subjects, k=conditions
    if n < 2 or k < 2:
        return None
    rank_sums = data.sum(axis=0)  # sum of ranks per condition
    mean_rank_sum = rank_sums.mean()
    S = np.sum((rank_sums - mean_rank_sum) ** 2)
    denominator = k ** 2 * (n ** 3 - n)
    if denominator == 0:
        return None
    w = 12 * S / denominator
    return round(float(w), 4)
