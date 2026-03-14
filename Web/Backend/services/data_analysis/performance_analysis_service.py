from Backend.db.handover_repository import HandoverRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import Experiment
from Backend.utils.stats_utils import sanitize_stats
from Backend.services.data_analysis.inferential_service import run_inferential_analysis
import pandas as pd
from collections import defaultdict
import scipy.stats as stats
import numpy as np

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
        stats["total_values"] = [d["total"] for d in data]
        stats_by_trial[trial_id] = sanitize_stats(stats)

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


def analyze_study_performance(session, study_id: int) -> dict:
    """
    Aggregate handover performance across all experiments in a study,
    grouped by stimulus condition, and run paired inferential tests.
    """
    experiments = (
        session.query(Experiment).filter_by(study_id=study_id).all()
    )
    if not experiments:
        return {}

    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    # condition → list of per-experiment means
    condition_phase1: dict[str, list] = defaultdict(list)
    condition_phase2: dict[str, list] = defaultdict(list)
    condition_phase3: dict[str, list] = defaultdict(list)
    condition_total: dict[str, list] = defaultdict(list)

    for experiment in experiments:
        trials = t_repo.get_by_experiment_id(experiment.experiment_id)
        if not trials:
            continue
        trial_ids = [t.trial_id for t in trials]
        trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

        # For this experiment, group per condition → collect all handover values
        exp_condition_data: dict[str, dict[str, list]] = defaultdict(
            lambda: {"phase1": [], "phase2": [], "phase3": [], "total": []}
        )

        for trial in trials:
            stimuli = trial_stimuli_map.get(trial.trial_id, [])
            if not stimuli:
                continue
            condition_name = stimuli[0]["name"]

            handovers = h_repo.get_handovers_for_trial(trial.trial_id)
            for h in handovers:
                if not all([
                    h.giver_grasped_object,
                    h.receiver_touched_object,
                    h.receiver_grasped_object,
                    h.giver_released_object,
                ]):
                    continue
                phase1 = (h.receiver_touched_object - h.giver_grasped_object).total_seconds()
                phase2 = (h.receiver_grasped_object - h.receiver_touched_object).total_seconds()
                phase3 = (h.giver_released_object - h.receiver_grasped_object).total_seconds()
                total = (h.giver_released_object - h.giver_grasped_object).total_seconds()
                exp_condition_data[condition_name]["phase1"].append(phase1)
                exp_condition_data[condition_name]["phase2"].append(phase2)
                exp_condition_data[condition_name]["phase3"].append(phase3)
                exp_condition_data[condition_name]["total"].append(total)

        # Compute per-experiment mean per condition and accumulate
        for cond_name, data in exp_condition_data.items():
            if data["total"]:
                condition_phase1[cond_name].append(float(np.mean(data["phase1"])))
                condition_phase2[cond_name].append(float(np.mean(data["phase2"])))
                condition_phase3[cond_name].append(float(np.mean(data["phase3"])))
                condition_total[cond_name].append(float(np.mean(data["total"])))

    if not condition_total:
        return {}

    conditions = sorted(condition_total.keys())

    # Build descriptive stats per condition using calc_stats (expects list of dicts)
    def _build_records(cond: str) -> list:
        p1 = condition_phase1.get(cond, [])
        p2 = condition_phase2.get(cond, [])
        p3 = condition_phase3.get(cond, [])
        tot = condition_total.get(cond, [])
        n = min(len(p1), len(p2), len(p3), len(tot))
        return [{"phase1": p1[i], "phase2": p2[i], "phase3": p3[i], "total": tot[i]} for i in range(n)]

    by_condition = {}
    for cond in conditions:
        records = _build_records(cond)
        if records:
            by_condition[cond] = sanitize_stats(calc_stats(records))
        else:
            by_condition[cond] = {}

    # Inferential tests (N conditions, one value per experiment per condition)
    inferential = {}
    if len(conditions) >= 2:
        for metric, bucket in [
            ("total", condition_total),
            ("phase1", condition_phase1),
            ("phase2", condition_phase2),
            ("phase3", condition_phase3),
        ]:
            cond_dict = {cond: bucket[cond] for cond in conditions}
            inferential[metric] = run_inferential_analysis(cond_dict)

    return {
        "study_id": study_id,
        "n_experiments": len(experiments),
        "conditions": conditions,
        "performance": {
            "by_condition": by_condition,
            "inferential": inferential,
        },
    }