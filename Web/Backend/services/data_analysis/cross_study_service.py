"""
Studienübergreifende deskriptive Auswertung.

WICHTIG: Cross-Study-Vergleiche sind NUR DESKRIPTIV.
Da verschiedene Studien verschiedene Teilnehmer haben, sind
inferenzielle Tests (t-Test, ANOVA) zwischen Studien nicht zulässig.
Nur Effektgrößen + Konfidenzintervalle werden nebeneinandergestellt.
"""
from __future__ import annotations
import numpy as np
from scipy import stats as scipy_stats
from typing import Optional


def calc_mean_ci(values: list[float], confidence: float = 0.95) -> dict:
    """
    Berechnet Mittelwert und Konfidenzintervall.
    Returns: {"mean": float, "ci_lower": float, "ci_upper": float, "n": int, "std": float}
    Bei n < 2: ci_lower = ci_upper = mean
    """
    n = len(values)
    if n == 0:
        return {"mean": None, "ci_lower": None, "ci_upper": None, "n": 0, "std": None}
    arr = np.array(values, dtype=float)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    if n < 2:
        return {"mean": round(mean, 3), "ci_lower": round(mean, 3), "ci_upper": round(mean, 3), "n": n, "std": 0.0}
    se = scipy_stats.sem(arr)
    ci = scipy_stats.t.interval(confidence, df=n-1, loc=mean, scale=se)
    return {
        "mean": round(mean, 3),
        "ci_lower": round(float(ci[0]), 3),
        "ci_upper": round(float(ci[1]), 3),
        "n": n,
        "std": round(std, 3),
    }


def compare_studies_descriptive(
    study_data: dict[str, dict[str, list[float]]],
    metric: str = "transfer_duration_ms",
) -> dict:
    """
    Deskriptiver Vergleich einer Metrik über mehrere Studien/Bedingungen hinweg.

    study_data: {
        "HS1_visual": [300, 320, 310, ...],    # Messwerte pro Bedingung/Studie
        "HS2_audio":  [280, 295, 288, ...],
        "HS3_tactile": [260, 275, 268, ...],
    }

    Returns:
    {
        "metric": str,
        "is_descriptive_only": True,  # IMMER True — Cross-Study = kein inferenzieller Test
        "warning": str,               # Hinweis auf Between-Subject-Problem
        "conditions": {
            "HS1_visual": {"mean": ..., "ci_lower": ..., "ci_upper": ..., "n": ..., "std": ...},
            ...
        },
        "baseline_ms": float | None,  # Realwelt-Baseline (300ms falls bekannt, sonst None)
    }
    """
    conditions = {}
    for condition_name, values in study_data.items():
        conditions[condition_name] = calc_mean_ci(values)

    return {
        "metric": metric,
        "is_descriptive_only": True,
        "warning": (
            "Cross-Study-Vergleiche sind nur deskriptiv. "
            "Da verschiedene Studien verschiedene Teilnehmer haben, "
            "sind inferenzielle Tests nicht zulässig."
        ),
        "conditions": conditions,
        "baseline_ms": 300.0 if metric == "transfer_duration_ms" else None,
    }


def forest_plot_data(
    effect_sizes: dict[str, dict],
) -> list[dict]:
    """
    Bereitet Daten für einen Forest Plot vor.

    effect_sizes: {
        "HS1: V vs. Baseline": {
            "d": 0.8, "ci_lower": 0.3, "ci_upper": 1.3, "n": 20, "study": "HS1"
        },
        ...
    }

    Returns: Liste von Dicts, sortiert nach Effektgröße (absteigend), mit "label", "d", "ci_lower", "ci_upper", "n", "study"
    """
    rows = []
    for label, data in effect_sizes.items():
        rows.append({
            "label": label,
            "d": data.get("d"),
            "ci_lower": data.get("ci_lower"),
            "ci_upper": data.get("ci_upper"),
            "n": data.get("n"),
            "study": data.get("study", ""),
        })
    rows.sort(key=lambda x: (x["d"] or 0), reverse=True)
    return rows
