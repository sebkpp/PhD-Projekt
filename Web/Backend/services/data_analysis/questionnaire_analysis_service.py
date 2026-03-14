from Backend.db.questionnaires.questionnaire_response_repository import QuestionnaireResponseRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import Experiment
from Backend.utils.stats_utils import run_paired_test

import math
from collections import defaultdict
import pandas as pd

def build_response_dataframe(responses):
    return pd.DataFrame([{
        "participant_id": r.participant_id,
        "trial_id": r.trial_id,
        "questionnaire_id": r.questionnaire_item.questionnaire.questionnaire_id,
        "questionnaire_name": r.questionnaire_item.questionnaire.name,
        "questionnaire_item_id": r.questionnaire_item_id,
        "item_name": r.questionnaire_item.item_name,
        "response_value": r.response_value
    } for r in responses])

def compute_trial_item_stats(df, trial_stimuli_map):
    stats = {}
    trial_item_stats = (
        df.groupby(["trial_id", "questionnaire_id", "questionnaire_name", "questionnaire_item_id", "item_name"])
        .agg(mean=("response_value", "mean"),
             std=("response_value", "std"))
        .reset_index()
    )
    grouped = trial_item_stats.groupby(["trial_id", "questionnaire_name"])
    for (t_id, q_name), group in grouped:
        t_id = int(t_id)
        stimuli = trial_stimuli_map.get(t_id, [])
        stimuli_conditions = [
            {"name": s["name"], "type": s.get("stimulus_type", "stimulus")}
            for s in stimuli
        ]
        stats.setdefault(t_id, {
            "stimuli_conditions": stimuli_conditions
        }).setdefault("questionnaires", {}).setdefault(q_name, {
            "items": []
        })
        # Sortiere und baue Array
        items_sorted = group.sort_values("questionnaire_item_id")
        for _, row in items_sorted.iterrows():
            stats[t_id]["questionnaires"][q_name]["items"].append({
                "item_name": row["item_name"],
                "questionnaire_item_id": int(row["questionnaire_item_id"]),
                "mean": float(row["mean"]),
                "std": float(row["std"])
            })
    return stats

def compute_mean_diffs(stats):
    mean_diffs = {}
    trial_ids_sorted = sorted(stats.keys())
    if len(trial_ids_sorted) >= 2:
        t1, t2 = trial_ids_sorted[0], trial_ids_sorted[1]
        for q_name in stats[t1]["questionnaires"]:
            items1 = stats[t1]["questionnaires"][q_name]["items"]
            items2 = stats[t2]["questionnaires"].get(q_name, {}).get("items", [])
            # Map für schnellen Zugriff
            items2_map = {item["item_name"]: item for item in items2}
            # Sortiere nach questionnaire_item_id
            diffs = []
            for item1 in sorted(items1, key=lambda x: x["questionnaire_item_id"]):
                item_name = item1["item_name"]
                if item_name in items2_map:
                    diff = items2_map[item_name]["mean"] - item1["mean"]
                    diffs.append({
                        "item_name": item_name,
                        "questionnaire_item_id": item1["questionnaire_item_id"],
                        "value": diff
                    })
            mean_diffs[q_name] = diffs
    return mean_diffs

def build_participant_result(responses):
    result = {}
    responses_sorted = sorted(responses, key=lambda r: r.questionnaire_item_id)
    for r in responses_sorted:
        p_id = r.participant_id
        t_id = r.trial_id
        q_name = r.questionnaire_item.questionnaire.name
        result.setdefault(p_id, {}).setdefault(t_id, {}).setdefault(q_name, {
            "responses": []
        })["responses"].append({
            "item_name": r.questionnaire_item.item_name,
            "questionnaire_item_id": r.questionnaire_item_id,
            "response_value": r.response_value,
        })
    return result

def analyze_experiment_questionnaires(session, experiment_id):
    qr_repo = QuestionnaireResponseRepository(session)
    t_repo = TrialRepository(session)
    s_repo = StimuliRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    trial_ids = [trial.trial_id for trial in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

    responses = qr_repo.get_questionnaire_responses_for_trials(trial_ids)

    df = build_response_dataframe(responses)
    stats = compute_trial_item_stats(df, trial_stimuli_map)
    mean_diffs = compute_mean_diffs(stats)
    result = build_participant_result(responses)

    return {
        "experiment_id": experiment_id,
        "participants": result,
        "trial_item_stats": stats,
        "mean_diffs": mean_diffs
    }


def _safe_float(v):
    """Return None for NaN/Inf, otherwise round to 4 dp."""
    if v is None:
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return round(float(v), 4)


def analyze_study_questionnaires(session, study_id: int) -> dict:
    """
    Aggregate questionnaire responses across all experiments in a study,
    grouped by stimulus condition, and run paired inferential tests per item.

    Returns:
    {
      "study_id": ...,
      "n_participants": ...,
      "conditions": [...],
      "questionnaires": {
        "<questionnaire_name>": {
          "by_condition": {
            "<condition>": { "<item_name>": {"mean": float, "std": float, "n": int}, ... }
          },
          "inferential": {
            "<item_name>": {"test": ..., "statistic": ..., "p_value": ..., "effect_size_d": ..., "significant": bool}
          }
        }
      }
    }
    """
    experiments = session.query(Experiment).filter_by(study_id=study_id).all()
    if not experiments:
        return {}

    qr_repo = QuestionnaireResponseRepository(session)
    t_repo = TrialRepository(session)
    s_repo = StimuliRepository(session)

    # participant_id → item_name → condition → list of response values
    # Structure: {participant_id: {questionnaire_name: {item_name: {condition: [values]}}}}
    participant_item_condition: dict = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )

    # Also track all unique (questionnaire_name, item_name) pairs
    all_questionnaire_items: dict[str, set] = defaultdict(set)  # q_name → set of item_names
    all_participants: set = set()
    all_conditions: set = set()

    for experiment in experiments:
        trials = t_repo.get_by_experiment_id(experiment.experiment_id)
        if not trials:
            continue
        trial_ids = [t.trial_id for t in trials]
        trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

        # Build trial_id → condition_name mapping
        trial_condition_map: dict[int, str] = {}
        for trial in trials:
            stimuli = trial_stimuli_map.get(trial.trial_id, [])
            if stimuli:
                trial_condition_map[trial.trial_id] = stimuli[0]["name"]

        responses = qr_repo.get_questionnaire_responses_for_trials(trial_ids)
        for r in responses:
            t_id = r.trial_id
            condition = trial_condition_map.get(t_id)
            if condition is None:
                continue
            p_id = r.participant_id
            q_name = r.questionnaire_item.questionnaire.name
            item_name = r.questionnaire_item.item_name
            value = r.response_value

            participant_item_condition[p_id][q_name][item_name][condition].append(value)
            all_questionnaire_items[q_name].add(item_name)
            all_participants.add(p_id)
            all_conditions.add(condition)

    if not participant_item_condition:
        return {}

    conditions = sorted(all_conditions)

    # Aggregate across participants: condition → item_name → list of per-participant means
    # per questionnaire
    questionnaire_results = {}
    for q_name, item_names in all_questionnaire_items.items():
        # condition → item_name → [values across all participants/responses]
        condition_item_values: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

        for p_id, q_data in participant_item_condition.items():
            if q_name not in q_data:
                continue
            item_data = q_data[q_name]
            for item_name in item_names:
                if item_name not in item_data:
                    continue
                for condition in conditions:
                    vals = item_data[item_name].get(condition, [])
                    if vals:
                        # Use mean per participant per condition
                        condition_item_values[condition][item_name].append(
                            sum(vals) / len(vals)
                        )

        # Build by_condition descriptive stats
        by_condition: dict[str, dict] = {}
        for condition in conditions:
            cond_stats: dict[str, dict] = {}
            for item_name in sorted(item_names):
                vals = condition_item_values[condition].get(item_name, [])
                n = len(vals)
                if n == 0:
                    cond_stats[item_name] = {"mean": None, "std": None, "n": 0}
                else:
                    mean_val = sum(vals) / n
                    if n > 1:
                        import statistics
                        std_val = statistics.stdev(vals)
                    else:
                        std_val = 0.0
                    cond_stats[item_name] = {
                        "mean": _safe_float(mean_val),
                        "std": _safe_float(std_val),
                        "n": n,
                    }
            by_condition[condition] = cond_stats

        # Build inferential tests (paired between conditions per item)
        inferential: dict[str, dict | None] = {}
        if len(conditions) >= 2:
            cond_a, cond_b = conditions[0], conditions[1]
            for item_name in sorted(item_names):
                vals_a = condition_item_values[cond_a].get(item_name, [])
                vals_b = condition_item_values[cond_b].get(item_name, [])
                # Pair up by participant order (both lists contain one value per participant)
                min_len = min(len(vals_a), len(vals_b))
                if min_len >= 3:
                    inferential[item_name] = run_paired_test(
                        vals_a[:min_len], vals_b[:min_len]
                    )
                else:
                    inferential[item_name] = None

        questionnaire_results[q_name] = {
            "by_condition": by_condition,
            "inferential": inferential,
        }

    return {
        "study_id": study_id,
        "n_participants": len(all_participants),
        "conditions": conditions,
        "questionnaires": questionnaire_results,
    }