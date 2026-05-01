"""
Korrelationsanalyse zwischen abhängigen Variablen.
Auto-Selection: Pearson wenn beide Variablen normalverteilt, sonst Spearman.
Mehrfachkorrektur via Bonferroni über alle Paare.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import shapiro, pearsonr, spearmanr
from itertools import combinations


def check_normality(values: list[float]) -> tuple[float, bool]:
    """
    Shapiro-Wilk Normalitätstest.
    Returns: (p_value, is_normal)
    is_normal = p > 0.05
    Requires n >= 3. Wenn n < 3: returns (1.0, True) — angenommen normal.
    """
    if len(values) < 3:
        return (1.0, True)
    stat, p = shapiro(values)
    return (float(p), bool(p > 0.05))


# Public alias used in tests and external callers
test_normality = check_normality


def calc_correlation(x: list[float], y: list[float]) -> dict | None:
    """
    Auto-Selection: Pearson wenn beide normal, sonst Spearman.
    Returns None wenn n < 3.
    Returns:
    {
        "method": "pearson" | "spearman",
        "r": float,  # Korrelationskoeffizient
        "p": float,  # p-Wert (unkorrigiert)
        "n": int,
        "interpretation": str  # "stark positiv/negativ", "mittel", "schwach", "kein"
    }
    """
    n = min(len(x), len(y))
    if n < 3:
        return None
    x_arr = np.array(x[:n], dtype=float)
    y_arr = np.array(y[:n], dtype=float)

    _, x_normal = check_normality(list(x_arr))
    _, y_normal = check_normality(list(y_arr))

    if x_normal and y_normal:
        r, p = pearsonr(x_arr, y_arr)
        method = "pearson"
    else:
        r, p = spearmanr(x_arr, y_arr)
        method = "spearman"

    # Interpretation nach Cohen (1988)
    abs_r = abs(r)
    if abs_r >= 0.5:
        interp = "stark positiv" if r > 0 else "stark negativ"
    elif abs_r >= 0.3:
        interp = "mittel positiv" if r > 0 else "mittel negativ"
    elif abs_r >= 0.1:
        interp = "schwach positiv" if r > 0 else "schwach negativ"
    else:
        interp = "kein"

    return {
        "method": method,
        "r": round(float(r), 4),
        "p": round(float(p), 4),
        "n": n,
        "interpretation": interp,
    }


def calc_correlation_matrix(variables: dict[str, list[float]]) -> dict:
    """
    Berechnet alle Paarkorrelationen zwischen den Variablen.
    Bonferroni-Korrektur über alle Paare.

    variables: {"var_name": [values], ...}

    Returns:
    {
        "pairs": [
            {
                "var_a": str,
                "var_b": str,
                "r": float,
                "p_uncorrected": float,
                "p_corrected": float,  # Bonferroni
                "significant": bool,   # p_corrected < 0.05
                "method": str,
                "interpretation": str,
                "n": int,
            }
        ],
        "n_pairs": int,
        "alpha_corrected": float,  # 0.05 / n_pairs
    }
    """
    names = list(variables.keys())
    pairs_list = list(combinations(names, 2))
    n_pairs = len(pairs_list)
    alpha = 0.05
    alpha_corrected = alpha / n_pairs if n_pairs > 0 else alpha

    pairs = []
    for var_a, var_b in pairs_list:
        result = calc_correlation(variables[var_a], variables[var_b])
        if result is None:
            pairs.append({
                "var_a": var_a, "var_b": var_b,
                "r": None, "p_uncorrected": None, "p_corrected": None,
                "significant": False, "method": None, "interpretation": None, "n": 0,
            })
            continue
        p_corr = min(result["p"] * n_pairs, 1.0)
        pairs.append({
            "var_a": var_a,
            "var_b": var_b,
            "r": result["r"],
            "p_uncorrected": result["p"],
            "p_corrected": round(p_corr, 4),
            "significant": p_corr < 0.05,
            "method": result["method"],
            "interpretation": result["interpretation"],
            "n": result["n"],
        })

    return {
        "pairs": pairs,
        "n_pairs": n_pairs,
        "alpha_corrected": round(alpha_corrected, 6),
    }
