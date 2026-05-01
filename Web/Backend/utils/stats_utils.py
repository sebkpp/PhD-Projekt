# Backend/utils/stats_utils.py
import math
import numpy as np
import scipy.stats as scipy_stats


def sanitize_stats(stats_dict: dict) -> dict:
    for k, v in stats_dict.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            stats_dict[k] = None
        if isinstance(v, tuple):
            stats_dict[k] = tuple(
                None if (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else x
                for x in v
            )
    return stats_dict


def cohens_d(values_a: list, values_b: list) -> float | None:
    if len(values_a) < 2 or len(values_b) < 2:
        return None
    mean_diff = np.mean(values_a) - np.mean(values_b)
    pooled_std = np.sqrt(
        (np.std(values_a, ddof=1) ** 2 + np.std(values_b, ddof=1) ** 2) / 2
    )
    if pooled_std > 0:
        d = float(mean_diff / pooled_std)
        return None if (math.isnan(d) or math.isinf(d)) else d
    return 0.0


def run_paired_test(values_a: list, values_b: list) -> dict | None:
    """
    Auto-selects paired t-test or Wilcoxon. Requires n > 3 per group.
    Guard: n <= 3 → return None (spec: Shapiro-Wilk needs n >= 4).
    """
    if len(values_a) <= 3 or len(values_b) <= 3:
        return None
    _, p_a = scipy_stats.shapiro(values_a)
    _, p_b = scipy_stats.shapiro(values_b)
    try:
        if p_a >= 0.05 and p_b >= 0.05:
            stat, p = scipy_stats.ttest_rel(values_a, values_b)
            test_name = "paired_ttest"
        else:
            stat, p = scipy_stats.wilcoxon(values_a, values_b)
            test_name = "wilcoxon"
    except Exception:
        return None

    stat_val = None if (isinstance(stat, float) and math.isnan(stat)) else float(stat)
    p_val = None if (isinstance(p, float) and math.isnan(p)) else float(p)
    return {
        "test": test_name,
        "statistic": stat_val,
        "p_value": p_val,
        "effect_size_d": cohens_d(values_a, values_b),
        "significant": bool(p_val < 0.05) if p_val is not None else None,
    }
