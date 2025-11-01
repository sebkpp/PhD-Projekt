from Backend.db.handover_repository import HandoverRepository
import pandas as pd
from collections import defaultdict
import scipy.stats as stats
import math

def sanitize_stats(stats):
    for k, v in stats.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            stats[k] = None
        if isinstance(v, tuple):
            stats[k] = tuple(None if (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) else x for x in v)
    return stats

def calc_stats(data):
    df = pd.DataFrame(data)
    def conf_int(series):
        n = len(series)
        if n < 2:
            return (None, None)
        mean = series.mean()
        sem = series.sem(ddof=1)
        t = stats.t.ppf(0.975, n-1)
        ci = t * sem
        return round(mean - ci, 2), round(mean + ci, 2)

    def shapiro_p(series):
        if len(series) > 3:
            return round(stats.shapiro(series).pvalue, 4)
        return None

    def coeff_var(series):
        mean = series.mean()
        std = series.std(ddof=1)
        return round(std / mean, 2) if mean != 0 else None

    return {
        "phase1_mean": round(df["phase1"].mean(), 2),
        "phase2_mean": round(df["phase2"].mean(), 2),
        "phase3_mean": round(df["phase3"].mean(), 2),
        "total_mean": round(df["total"].mean(), 2),
        "phase1_median": round(df["phase1"].median(), 2),
        "phase2_median": round(df["phase2"].median(), 2),
        "phase3_median": round(df["phase3"].median(), 2),
        "total_median": round(df["total"].median(), 2),
        "phase1_std": round(df["phase1"].std(ddof=1), 2),
        "phase2_std": round(df["phase2"].std(ddof=1), 2),
        "phase3_std": round(df["phase3"].std(ddof=1), 2),
        "total_std": round(df["total"].std(ddof=1), 2),
        "phase1_var": round(df["phase1"].var(ddof=1), 2),
        "phase2_var": round(df["phase2"].var(ddof=1), 2),
        "phase3_var": round(df["phase3"].var(ddof=1), 2),
        "total_var": round(df["total"].var(ddof=1), 2),
        "phase1_confint": conf_int(df["phase1"]),
        "phase2_confint": conf_int(df["phase2"]),
        "phase3_confint": conf_int(df["phase3"]),
        "total_confint": conf_int(df["total"]),
        "phase1_cv": coeff_var(df["phase1"]),
        "phase2_cv": coeff_var(df["phase2"]),
        "phase3_cv": coeff_var(df["phase3"]),
        "total_cv": coeff_var(df["total"]),
        "phase1_normality_p": shapiro_p(df["phase1"]),
        "phase2_normality_p": shapiro_p(df["phase2"]),
        "phase3_normality_p": shapiro_p(df["phase3"]),
        "total_normality_p": shapiro_p(df["total"]),
        "phase1_min": round(df["phase1"].min(), 2),
        "phase1_max": round(df["phase1"].max(), 2),
        "phase2_min": round(df["phase2"].min(), 2),
        "phase2_max": round(df["phase2"].max(), 2),
        "phase3_min": round(df["phase3"].min(), 2),
        "phase3_max": round(df["phase3"].max(), 2),
        "total_min": round(df["total"].min(), 2),
        "total_max": round(df["total"].max(), 2),
        "phase1_q1": round(df["phase1"].quantile(0.25), 2),
        "phase1_q3": round(df["phase1"].quantile(0.75), 2),
        "phase1_iqr": round(df["phase1"].quantile(0.75) - df["phase1"].quantile(0.25), 2),
        "phase2_q1": round(df["phase2"].quantile(0.25), 2),
        "phase2_q3": round(df["phase2"].quantile(0.75), 2),
        "phase2_iqr": round(df["phase2"].quantile(0.75) - df["phase2"].quantile(0.25), 2),
        "phase3_q1": round(df["phase3"].quantile(0.25), 2),
        "phase3_q3": round(df["phase3"].quantile(0.75), 2),
        "phase3_iqr": round(df["phase3"].quantile(0.75) - df["phase3"].quantile(0.25), 2),
        "total_q1": round(df["total"].quantile(0.25, interpolation="hazen"), 2),
        "total_q3": round(df["total"].quantile(0.75, interpolation="hazen"), 2),
        "total_iqr": round(df["total"].quantile(0.75, interpolation="hazen") - df["total"].quantile(0.25, interpolation="hazen"), 2),
        "phase1_skew": round(df["phase1"].skew(), 2),
        "phase2_skew": round(df["phase2"].skew(), 2),
        "phase3_skew": round(df["phase3"].skew(), 2),
        "total_skew": round(df["total"].skew(), 2),
        "phase1_kurtosis": round(df["phase1"].kurtosis(), 2),
        "phase2_kurtosis": round(df["phase2"].kurtosis(), 2),
        "phase3_kurtosis": round(df["phase3"].kurtosis(), 2),
        "total_kurtosis": round(df["total"].kurtosis(), 2),
        "n": len(df)
    }

def analyze_experiment_performance(session, experiment_id):
    h_repo = HandoverRepository(session)
    handovers = h_repo.get_handovers_by_experiment(experiment_id)
    if not handovers:
        return {}

    # Objektunabhängig gruppieren
    grouped_by_trial = defaultdict(list)
    # Objektabhängig gruppieren
    grouped_by_trial_and_object = defaultdict(lambda: defaultdict(list))
    grouped_by_giver = defaultdict(list)
    grouped_by_receiver = defaultdict(list)

    for h in handovers:
        if not all([h.giver_grasped_object, h.receiver_touched_object, h.receiver_grasped_object, h.giver_released_object]):
            continue
        phase1 = (h.receiver_touched_object - h.giver_grasped_object).total_seconds()
        phase2 = (h.receiver_grasped_object - h.receiver_touched_object).total_seconds()
        phase3 = (h.giver_released_object - h.receiver_grasped_object).total_seconds()
        total = (h.giver_released_object - h.giver_grasped_object).total_seconds()
        # Trial-basiert
        grouped_by_trial[h.trial_id].append({
            "phase1": phase1,
            "phase2": phase2,
            "phase3": phase3,
            "total": total
        })
        # Trial + Objekt-basiert
        grouped_by_trial_and_object[h.trial_id][h.grasped_object].append({
            "phase1": phase1,
            "phase2": phase2,
            "phase3": phase3,
            "total": total
        })
        data_point = {
            "phase1": phase1,
            "phase2": phase2,
            "phase3": phase3,
            "total": total
        }
        grouped_by_giver[h.giver].append(data_point)
        grouped_by_receiver[h.receiver].append(data_point)

    stats_by_giver = {giver: sanitize_stats(calc_stats(data)) for giver, data in grouped_by_giver.items()}
    stats_by_receiver = {receiver: sanitize_stats(calc_stats(data)) for receiver, data in grouped_by_receiver.items()}

    stats_by_trial = {}
    for trial_id, data in grouped_by_trial.items():
        stats = calc_stats(data)
        stats_by_trial[trial_id] = sanitize_stats(stats)
        stats["total_values"] = [d["total"] for d in data]
        stats_by_trial[trial_id] = stats

    stats_by_trial_and_object = {}
    for trial_id, obj_dict in grouped_by_trial_and_object.items():
        stats_by_trial_and_object[trial_id] = {}
        for obj, data in obj_dict.items():
            stats_by_trial_and_object[trial_id][obj] = sanitize_stats(calc_stats(data))


    return {
        "by_trial": stats_by_trial,
        "by_trial_and_object": stats_by_trial_and_object,
        "by_giver": stats_by_giver,
        "by_receiver": stats_by_receiver
    }