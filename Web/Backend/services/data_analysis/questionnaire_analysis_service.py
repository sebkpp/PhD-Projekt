from Backend.db.questionnaires.questionnaire_response_repository import QuestionnaireResponseRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.db.trial.trial import TrialRepository

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