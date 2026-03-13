import math
from collections import defaultdict

from Backend.db.handover_repository import HandoverRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import Experiment, AreaOfInterest
from Backend.services.data_analysis.performance_analysis_service import sanitize_stats


def _sanitize_aoi_stats(aoi_stats: dict) -> dict:
    for aoi_name, s in aoi_stats.items():
        for k, v in s.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                s[k] = None
    return aoi_stats


def _build_aoi_label_map(session) -> dict:
    """Return {aoi_machine_name: label} for all AreaOfInterest rows."""
    aois = session.query(AreaOfInterest).all()
    return {a.aoi: a.label for a in aois}


def _compute_aoi_stats(eye_trackings, aoi_label_map: dict, total_duration_ms: int) -> dict:
    """
    Given a list of EyeTracking ORM objects, compute per-AOI aggregates.
    Returns {aoi_machine_name: {"label", "total_duration_ms", "percentage", "fixation_count", "mean_duration_ms"}}
    """
    aoi_buckets: dict[str, list] = defaultdict(list)
    for et in eye_trackings:
        aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
        aoi_buckets[aoi_name].append(et.duration if et.duration is not None else 0)

    result = {}
    for aoi_name, durations in aoi_buckets.items():
        total_dur = sum(durations)
        count = len(durations)
        mean_dur = total_dur / count if count > 0 else 0.0
        pct = (total_dur / total_duration_ms * 100.0) if total_duration_ms and total_duration_ms > 0 else 0.0
        label = aoi_label_map.get(aoi_name, aoi_name)
        val = {
            "label": label,
            "total_duration_ms": total_dur,
            "percentage": round(pct, 4),
            "fixation_count": count,
            "mean_duration_ms": round(mean_dur, 4),
        }
        # sanitize NaN/Inf floats
        for k, v in val.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                val[k] = None
        result[aoi_name] = val
    return result


def analyze_experiment_eye_tracking(session, experiment_id: int) -> dict:
    """
    Analyze eye tracking data for all trials in an experiment.
    Returns per-trial AOI stats.
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)
    aoi_label_map = _build_aoi_label_map(session)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)

        # Collect all eye_tracking records for this trial (across all handovers)
        all_eye_trackings = []
        for handover in handovers:
            all_eye_trackings.extend(handover.eye_trackings)

        total_duration_ms = sum(
            et.duration for et in all_eye_trackings if et.duration is not None
        )

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        stimuli_conditions = [
            {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
            for s in stimuli
        ]

        aoi_stats = _compute_aoi_stats(all_eye_trackings, aoi_label_map, total_duration_ms)

        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "total_duration_ms": total_duration_ms,
            "stimuli_conditions": stimuli_conditions,
            "aoi_stats": aoi_stats,
        }

    return {
        "experiment_id": experiment_id,
        "by_trial": by_trial,
    }


def analyze_study_eye_tracking(session, study_id: int) -> dict:
    """
    Aggregate eye tracking data for all experiments in a study,
    grouped by stimulus condition (inner_hand / outer_hand).
    """
    experiments = (
        session.query(Experiment).filter_by(study_id=study_id).all()
    )
    if not experiments:
        return {}

    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)
    aoi_label_map = _build_aoi_label_map(session)

    # condition_name → {aoi_name → list of durations}
    condition_aoi_durations: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    # condition_name → total_duration accumulator
    condition_total_ms: dict[str, int] = defaultdict(int)
    # condition_name → aoi_name → fixation count
    condition_aoi_fixations: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for experiment in experiments:
        trials = t_repo.get_by_experiment_id(experiment.experiment_id)
        if not trials:
            continue
        trial_ids = [t.trial_id for t in trials]
        trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

        for trial in trials:
            stimuli = trial_stimuli_map.get(trial.trial_id, [])
            if not stimuli:
                continue
            # Each trial has exactly one condition
            condition_name = stimuli[0]["name"]

            handovers = h_repo.get_handovers_for_trial(trial.trial_id)
            for handover in handovers:
                for et in handover.eye_trackings:
                    aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                    duration = et.duration if et.duration is not None else 0
                    condition_aoi_durations[condition_name][aoi_name].append(duration)
                    condition_total_ms[condition_name] += duration
                    condition_aoi_fixations[condition_name][aoi_name] += 1

    if not condition_aoi_durations:
        return {}

    by_condition = {}
    for condition_name, aoi_dur_map in condition_aoi_durations.items():
        total_ms = condition_total_ms[condition_name]
        aoi_stats = {}
        for aoi_name, durations in aoi_dur_map.items():
            total_dur = sum(durations)
            count = len(durations)
            mean_dur = total_dur / count if count > 0 else 0.0
            pct = (total_dur / total_ms * 100.0) if total_ms and total_ms > 0 else 0.0
            label = aoi_label_map.get(aoi_name, aoi_name)
            val = {
                "label": label,
                "total_duration_ms": total_dur,
                "percentage": round(pct, 4),
                "fixation_count": count,
                "mean_duration_ms": round(mean_dur, 4),
            }
            for k, v in val.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    val[k] = None
            aoi_stats[aoi_name] = val
        by_condition[condition_name] = {
            "total_duration_ms": total_ms,
            "aoi_stats": aoi_stats,
        }

    return {
        "study_id": study_id,
        "n_experiments": len(experiments),
        "conditions": list(condition_aoi_durations.keys()),
        "by_condition": by_condition,
    }
