# Backend/services/data_analysis/inferential_service.py
import math
import itertools
import numpy as np
import pandas as pd
import scipy.stats as scipy_stats
import pingouin as pg
import scikit_posthocs as sp

from Backend.utils.stats_utils import cohens_d
from Backend.services.data_analysis.effect_size_service import (
    cliffs_delta, omega2p_from_anova, kendalls_w_from_friedman,
    interpret_cohens_d, interpret_cliffs_delta,
)


def _shapiro_p(values: list) -> float | None:
    if len(values) > 3:
        _, p = scipy_stats.shapiro(values)
        return round(float(p), 4)
    return None


def run_inferential_analysis(conditions: dict[str, list]) -> dict | None:
    """
    conditions: {"cond_name": [per-experiment-mean, ...], ...}
    Returns inferential result dict or None if not enough data.
    """
    k = len(conditions)
    if k < 2:
        return None

    cond_names = list(conditions.keys())
    values_list = [conditions[c] for c in cond_names]
    min_n = min(len(v) for v in values_list)

    if min_n < 3:
        return None

    # Normality check
    normality = {c: _shapiro_p(conditions[c]) for c in cond_names}
    all_normal = all(p is not None and p >= 0.05 for p in normality.values())

    if k == 2:
        return _run_k2(cond_names, values_list, normality, all_normal)
    else:
        return _run_kn(cond_names, values_list, normality, all_normal, min_n)


def _run_k2(cond_names, values_list, normality, all_normal):
    a, b = values_list[0], values_list[1]
    try:
        if all_normal:
            stat, p = scipy_stats.ttest_rel(a, b)
            test_name = "paired_ttest"
        else:
            stat, p = scipy_stats.wilcoxon(a, b)
            test_name = "wilcoxon"
    except Exception:
        return None

    p_val = float(p) if not math.isnan(p) else None
    d = cohens_d(a, b)
    cd = cliffs_delta(a, b)
    return {
        "test_used": test_name,
        "n_conditions": 2,
        "normality": normality,
        "sphericity_p": None,
        "sphericity_correction": "none",
        "main_effect": {
            "statistic": float(stat),
            "p_value": p_val,
            "significant": bool(p_val < 0.05) if p_val is not None else None,
            "effect_eta2p": None,
            "effect_omega2p": None,
            "effect_kendalls_w": None,
            "effect_size_d": d,
            "effect_size_d_interpretation": interpret_cohens_d(d) if d is not None else None,
            "effect_size_cliffs_delta": cd,
            "effect_size_cliffs_delta_interpretation": interpret_cliffs_delta(cd) if cd is not None else None,
        },
        "posthoc": [],
    }


def _run_kn(cond_names, values_list, normality, all_normal, min_n):
    # Build long-format DataFrame for pingouin / scikit-posthocs
    rows = []
    for i, cond in enumerate(cond_names):
        for subj_idx, val in enumerate(values_list[i]):
            rows.append({"subject": subj_idx, "condition": cond, "value": val})
    df = pd.DataFrame(rows)

    # Pre-compute condition lookup (used in post-hoc loops)
    cond_dict = dict(zip(cond_names, values_list))

    test_used = None
    main_effect = {}
    posthoc = []
    sphericity_p = None
    sphericity_correction = "none"
    used_rm_anova = False

    if all_normal and min_n >= 5:
        try:
            # Use correction=True to get sphericity columns in the output
            aov = pg.rm_anova(data=df, dv="value", within="condition",
                              subject="subject", correction=True, detailed=True)
            row = aov.iloc[0]

            # Pingouin with correction=True includes sphericity, p_spher, p_GG_corr columns
            spher_ok = True
            if "sphericity" in aov.columns:
                spher_val = aov["sphericity"].iloc[0]
                spher_ok = bool(spher_val) if spher_val is not None else True
            if "p_spher" in aov.columns:
                p_spher = aov["p_spher"].iloc[0]
                sphericity_p = float(p_spher) if p_spher is not None and not (isinstance(p_spher, float) and math.isnan(p_spher)) else None

            if not spher_ok:
                test_used = "rm_anova_gg"
                sphericity_correction = "greenhouse_geisser"
                # Use GG-corrected p-value
                p_main = float(row.get("p_GG_corr", row.get("p_unc", 1.0)) or 1.0)
                padjust_method = "bonf"
            else:
                test_used = "rm_anova"
                p_main = float(row.get("p_unc", 1.0) or 1.0)
                padjust_method = "bonf"  # pingouin supports 'bonf'; 'tukey' is not available

            # Pingouin column names: ng2 (not np2), DF (not ddof1), p_unc (not p-unc)
            eta2p = float(row.get("ng2", 0.0) or 0.0)
            ss_effect = float(row.get("SS", 0.0) or 0.0)
            df_effect = float(row.get("DF", 1.0) or 1.0)
            err_row = aov.iloc[1] if len(aov) > 1 else None
            ss_error = float(err_row["SS"]) if err_row is not None else None
            df_error = float(err_row["DF"]) if err_row is not None else None
            omega = omega2p_from_anova(ss_effect, df_effect, ss_error, df_error) if ss_error else None

            f_val = row.get("F", 0.0)
            f_val = float(f_val) if f_val is not None and not (isinstance(f_val, float) and math.isnan(f_val)) else 0.0

            main_effect = {
                "statistic": f_val,
                "p_value": p_main,
                "significant": bool(p_main < 0.05),
                "effect_eta2p": round(eta2p, 4),
                "effect_omega2p": omega,
                "effect_kendalls_w": None,
                "effect_size_d": None,
                "effect_size_cliffs_delta": None,
            }

            # pairwise_tests column names: p_unc, p_corr (not p-unc, p-corr)
            pairs_df = pg.pairwise_tests(data=df, dv="value", within="condition",
                                         subject="subject", padjust=padjust_method)
            for _, pr in pairs_df.iterrows():
                ca, cb = str(pr["A"]), str(pr["B"])
                va = cond_dict.get(ca, [])
                vb = cond_dict.get(cb, [])
                d = cohens_d(va, vb)
                cd = cliffs_delta(va, vb)
                p_unc_val = pr.get("p_unc", 1.0)
                p_corr_val = pr.get("p_corr", 1.0)
                p_unc_f = float(p_unc_val) if p_unc_val is not None else 1.0
                p_corr_f = float(p_corr_val) if p_corr_val is not None else 1.0
                posthoc.append({
                    "pair": [ca, cb],
                    "p_value": p_unc_f,
                    "p_adjusted": p_corr_f,
                    "correction": padjust_method,
                    "effect_size_d": d,
                    "effect_size_d_interpretation": interpret_cohens_d(d) if d is not None else None,
                    "effect_size_cliffs_delta": cd,
                    "effect_size_cliffs_delta_interpretation": interpret_cliffs_delta(cd) if cd is not None else None,
                    "significant": bool(p_corr_f < 0.05),
                })
            used_rm_anova = True
        except Exception:
            # Fallback to Friedman — reset state
            all_normal = False
            used_rm_anova = False

    if not used_rm_anova:
        try:
            posthoc = []  # Reset: prevent mixing partial RM-ANOVA with Friedman results
            data_matrix = np.array(values_list).T  # subjects × conditions
            stat, p = scipy_stats.friedmanchisquare(*values_list)
            test_used = "friedman"
            w = kendalls_w_from_friedman(data_matrix)
            main_effect = {
                "statistic": float(stat),
                "p_value": float(p),
                "significant": bool(p < 0.05),
                "effect_eta2p": None,
                "effect_omega2p": None,
                "effect_kendalls_w": w,
                "effect_size_d": None,
                "effect_size_cliffs_delta": None,
            }
            # posthoc_dunn requires long-format DataFrame with val_col and group_col
            dunn = sp.posthoc_dunn(df, val_col="value", group_col="condition", p_adjust="bonferroni")
            for ca, cb in itertools.combinations(cond_names, 2):
                p_adj = float(dunn.loc[ca, cb])
                cd = cliffs_delta(cond_dict[ca], cond_dict[cb])
                posthoc.append({
                    "pair": [ca, cb],
                    "p_value": None,
                    "p_adjusted": p_adj,
                    "correction": "bonferroni",
                    "effect_size_d": None,
                    "effect_size_d_interpretation": None,
                    "effect_size_cliffs_delta": cd,
                    "effect_size_cliffs_delta_interpretation": interpret_cliffs_delta(cd) if cd is not None else None,
                    "significant": bool(p_adj < 0.05),
                })
        except Exception:
            return None

    return {
        "test_used": test_used,
        "n_conditions": len(cond_names),
        "normality": normality,
        "sphericity_p": sphericity_p,
        "sphericity_correction": sphericity_correction,
        "main_effect": main_effect,
        "posthoc": posthoc,
    }
