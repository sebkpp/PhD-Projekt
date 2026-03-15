import math
from collections import defaultdict
from datetime import datetime

from Backend.db.handover_repository import HandoverRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import Experiment, AreaOfInterest
from Backend.services.data_analysis.inferential_service import run_inferential_analysis


def calc_saccade_rate(saccade_count: int, duration_ms: float) -> float | None:
    """Sakkaden pro Sekunde. None wenn duration_ms <= 0."""
    if duration_ms <= 0:
        return None
    return (saccade_count / duration_ms) * 1000


def calc_transitions(aoi_sequence: list[str]) -> dict[str, int]:
    """
    Zählt aufeinanderfolgende AOI-Wechsel.
    Returns: {"{from}->{to}": count, ...}
    Beispiel: ["obj", "hand", "obj"] → {"obj->hand": 1, "hand->obj": 1}
    Ignoriert aufeinanderfolgende gleiche AOIs.
    """
    transitions: dict[str, int] = {}
    prev = None
    for aoi in aoi_sequence:
        if prev is not None and aoi != prev:
            key = f"{prev}->{aoi}"
            transitions[key] = transitions.get(key, 0) + 1
        prev = aoi
    return transitions


def calc_ppi(
    eye_tracking_records: list[dict],
    phase: int = 3,
    environment_aoi: str = "environment",
) -> float | None:
    """
    PPI = dwell_time(environment_aoi, phase=phase) / total_duration(phase) × 100

    eye_tracking_records: Liste von Dicts mit Feldern:
        - "aoi_name" (oder "area_of_interest_name"): str
        - "phase": int (1, 2 oder 3)
        - "dwell_time_ms": float
        - "duration_ms": float (Gesamtdauer dieser Phase)

    Returns: None wenn keine Phase-Daten vorhanden.
    Returns: float 0.0-100.0
    """
    phase_records = [r for r in eye_tracking_records if r.get("phase") == phase]
    if not phase_records:
        return None
    # duration_ms is the total phase duration (same value repeated per record); use max
    total_duration = max((r.get("duration_ms", 0) for r in phase_records), default=0)
    if total_duration <= 0:
        return None
    env_dwell = sum(
        r.get("dwell_time_ms", 0)
        for r in phase_records
        if r.get("aoi_name", r.get("area_of_interest_name", "")) == environment_aoi
    )
    return (env_dwell / total_duration) * 100


def analyze_aoi_inferential(
    condition_aoi_durations: dict[str, dict[str, list]],
) -> dict[str, dict | None]:
    """
    Run inferential analysis per AOI across N conditions.

    condition_aoi_durations: {condition_name: {aoi_name: [durations...]}}
    Returns: {aoi_name: inferential_result_or_None}
    """
    all_aoi_names: set[str] = set()
    for aoi_map in condition_aoi_durations.values():
        all_aoi_names.update(aoi_map.keys())

    results: dict[str, dict | None] = {}
    for aoi_name in all_aoi_names:
        conditions: dict[str, list] = {}
        for cond_name, aoi_map in condition_aoi_durations.items():
            durations = aoi_map.get(aoi_name, [])
            if durations:
                conditions[cond_name] = durations
        results[aoi_name] = run_inferential_analysis(conditions) if len(conditions) >= 2 else None

    return results


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


def _assign_phase(et_starttime, handover) -> int | None:
    """
    Determine which handover phase (1, 2, 3) an eye-tracking record belongs to.
    Phase 1 (Coordination): giver_grasped_object → receiver_touched_object
    Phase 2 (Grasp):        receiver_touched_object → receiver_grasped_object
    Phase 3 (Transfer):     receiver_grasped_object → giver_released_object
    Returns None if timestamps are missing or ET is outside all phases.
    Note: 'if t1 and t2' short-circuits on None — no TypeError risk.
    """
    if et_starttime is None:
        return None
    t1 = handover.giver_grasped_object
    t2 = handover.receiver_touched_object
    t3 = handover.receiver_grasped_object
    t4 = handover.giver_released_object
    if t1 and t2 and t1 <= et_starttime < t2:
        return 1
    if t2 and t3 and t2 <= et_starttime < t3:
        return 2
    if t3 and t4 and t3 <= et_starttime <= t4:
        return 3
    return None


def analyze_experiment_eye_tracking_phases(session, experiment_id: int) -> dict:
    """
    Per-trial, per-phase AOI dwell-time breakdown.
    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "phases": {
            1: { aoi_name: {"label": str, "total_duration_ms": int, "percentage": float} },
            2: { ... },
            3: { ... }
          }
        }
      }
    }
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
        # phase → aoi_name → list of durations
        phase_aoi_durations: dict[int, dict[str, list]] = {1: defaultdict(list), 2: defaultdict(list), 3: defaultdict(list)}
        phase_total_ms: dict[int, int] = {1: 0, 2: 0, 3: 0}

        for handover in handovers:
            for et in handover.eye_trackings:
                phase = _assign_phase(et.starttime, handover)
                if phase is None:
                    continue
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                dur = et.duration if et.duration is not None else 0
                phase_aoi_durations[phase][aoi_name].append(dur)
                phase_total_ms[phase] += dur

        phases_result = {}
        for phase_num in (1, 2, 3):
            total_ms = phase_total_ms[phase_num]
            phase_result = {}
            for aoi_name, durations in phase_aoi_durations[phase_num].items():
                total_dur = sum(durations)
                pct = (total_dur / total_ms * 100.0) if total_ms > 0 else 0.0
                phase_result[aoi_name] = {
                    "label": aoi_label_map.get(aoi_name, aoi_name),
                    "total_duration_ms": total_dur,
                    "percentage": round(pct, 4),
                }
            phases_result[phase_num] = phase_result

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "phases": phases_result,
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}


def analyze_experiment_eye_tracking_transitions(session, experiment_id: int) -> dict:
    """
    Per-trial AOI transition matrix (AOI sequence ordered by starttime).
    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "transitions": { "aoi_from->aoi_to": count, ... },
          "aoi_sequence_length": int
        }
      }
    }
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)
        all_et = []
        for handover in handovers:
            for et in handover.eye_trackings:
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                all_et.append((et.starttime, aoi_name))

        # Sort by starttime, build sequence
        all_et.sort(key=lambda x: x[0] if x[0] is not None else datetime.min)
        aoi_sequence = [aoi for _, aoi in all_et]
        transitions = calc_transitions(aoi_sequence)

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "transitions": transitions,
            "aoi_sequence_length": len(aoi_sequence),
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}


def analyze_experiment_ppi(session, experiment_id: int) -> dict:
    """
    Proactive Planning Index per trial, split by participant role (giver/receiver).

    PPI = dwell_time("environment", phase=3) / total_phase3_duration * 100

    Returns: {
      "experiment_id": int,
      "by_trial": {
        trial_id: {
          "trial_number": int,
          "stimuli_conditions": [...],
          "ppi_giver": float | None,
          "ppi_receiver": float | None
        }
      }
    }
    """
    t_repo = TrialRepository(session)
    h_repo = HandoverRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    if not trials:
        return {}

    trial_ids = [t.trial_id for t in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

    by_trial = {}
    for trial in trials:
        handovers = h_repo.get_handovers_for_trial(trial.trial_id)

        giver_records = []
        receiver_records = []

        for handover in handovers:
            for et in handover.eye_trackings:
                phase = _assign_phase(et.starttime, handover)
                if phase != 3:
                    continue
                aoi_name = et.aoi.aoi if et.aoi else str(et.aoi_id)
                dur = et.duration if et.duration is not None else 0
                # Phase 3 duration: giver_released_object - receiver_grasped_object in ms
                t3 = handover.receiver_grasped_object
                t4 = handover.giver_released_object
                if t3 and t4:
                    phase3_dur_ms = int((t4 - t3).total_seconds() * 1000)
                else:
                    phase3_dur_ms = 0
                record = {
                    "aoi_name": aoi_name,
                    "phase": 3,
                    "dwell_time_ms": dur,
                    "duration_ms": phase3_dur_ms,
                }
                if et.participant_id == handover.giver:
                    giver_records.append(record)
                else:
                    receiver_records.append(record)

        stimuli = trial_stimuli_map.get(trial.trial_id, [])
        by_trial[trial.trial_id] = {
            "trial_number": trial.trial_number,
            "stimuli_conditions": [
                {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
                for s in stimuli
            ],
            "ppi_giver": calc_ppi(giver_records) if giver_records else None,
            "ppi_receiver": calc_ppi(receiver_records) if receiver_records else None,
        }

    return {"experiment_id": experiment_id, "by_trial": by_trial}
