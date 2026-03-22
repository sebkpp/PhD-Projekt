from Backend.db.questionnaires.questionnaire_response_repository import QuestionnaireResponseRepository
from Backend.db.stimuli_repository import StimuliRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import Experiment
from Backend.services.data_analysis.inferential_service import run_inferential_analysis

import math
from collections import defaultdict
import pandas as pd


# ---------------------------------------------------------------------------
# Instrument-aware scoring functions
# ---------------------------------------------------------------------------

def score_nasa_tlx(responses: dict[str, float]) -> dict:
    """
    Score NASA-TLX questionnaire responses.

    responses: {"mental_demand": 75, "physical_demand": 30, ...}
    Subscales: mental_demand, physical_demand, temporal_demand, performance, effort, frustration
    Total score = mean of all present subscales (robust: ignores missing ones).

    Returns: {"subscales": responses, "total_score": float, "instrument": "nasa_tlx"}
    """
    known_subscales = {
        "mental_demand", "physical_demand", "temporal_demand",
        "performance", "effort", "frustration"
    }
    present = {k: v for k, v in responses.items() if k in known_subscales}
    if present:
        total_score = sum(present.values()) / len(present)
    else:
        total_score = 0.0
    return {
        "subscales": responses,
        "total_score": round(total_score, 4),
        "instrument": "nasa_tlx",
    }


def score_sus(responses: list[float]) -> dict:
    """
    Score SUS (System Usability Scale) responses.

    responses: list of 10 values on a 1–5 scale.
    Odd-index items (0,2,4,6,8): (value - 1) * 2.5
    Even-index items (1,3,5,7,9): (5 - value) * 2.5
    Total score = sum of all 10 transformed values (0–100).

    Grade: score >= 85 → "A", >= 70 → "B", >= 50 → "C", >= 35 → "D", else "F"

    Returns: {"total_score": float, "instrument": "sus", "grade": str}
    """
    transformed = []
    for i, value in enumerate(responses):
        if i % 2 == 0:  # odd items (1-based: 1,3,5,7,9) → 0-based even index
            transformed.append((value - 1) * 2.5)
        else:            # even items (1-based: 2,4,6,8,10) → 0-based odd index
            transformed.append((5 - value) * 2.5)
    total_score = round(sum(transformed), 4)

    if total_score >= 85:
        grade = "A"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 50:
        grade = "C"
    elif total_score >= 35:
        grade = "D"
    else:
        grade = "F"

    return {
        "total_score": total_score,
        "instrument": "sus",
        "grade": grade,
    }


def score_attrakdiff2(responses: dict[str, list[float]]) -> dict:
    """
    Score AttrakDiff2 questionnaire responses.

    responses: {"PQ": [1,2,3,...], "HQS": [...], "HQI": [...], "ATT": [...]}
    Values on -3 to +3 scale.
    Subscale score = mean of items in that subscale.
    Total score = mean of all subscale means.
    hq_total = mean of HQS and HQI subscale means.

    Returns: {"subscales": {"PQ": float, "HQS": float, "HQI": float, "ATT": float},
              "total_score": float, "hq_total": float, "instrument": "attrakdiff2"}
    """
    subscale_means: dict[str, float] = {}
    for subscale, items in responses.items():
        if items:
            subscale_means[subscale] = round(sum(items) / len(items), 4)

    total_score = round(sum(subscale_means.values()) / len(subscale_means), 4) if subscale_means else 0.0

    hq_scores = [subscale_means[k] for k in ("HQS", "HQI") if k in subscale_means]
    hq_total = round(sum(hq_scores) / len(hq_scores), 4) if hq_scores else 0.0

    return {
        "subscales": subscale_means,
        "total_score": total_score,
        "hq_total": hq_total,
        "instrument": "attrakdiff2",
    }


def score_iso_metrics(responses: dict[str, list[float]]) -> dict:
    """
    Score ISO-Metrics questionnaire responses.

    responses: {"subscale1": [values], "subscale2": [values], ...}
    Subscale score = mean of items in that subscale.
    Total score = mean of all subscale means.

    Returns: {"subscales": {subscale: float}, "total_score": float, "instrument": "iso_metrics"}
    """
    subscale_means: dict[str, float] = {}
    for subscale, items in responses.items():
        if items:
            subscale_means[subscale] = round(sum(items) / len(items), 4)

    total_score = round(sum(subscale_means.values()) / len(subscale_means), 4) if subscale_means else 0.0

    return {
        "subscales": subscale_means,
        "total_score": total_score,
        "instrument": "iso_metrics",
    }


def score_questionnaire(instrument: str, responses: dict | list) -> dict | None:
    """
    Dispatcher: calls the appropriate scoring function based on instrument type.

    instrument: "nasa_tlx", "sus", "attrakdiff2", "iso_metrics", unknown → None
    responses: dict or list depending on instrument.

    Returns scored result dict, or None for unknown instruments.
    """
    instrument_lower = instrument.lower() if instrument else ""
    if instrument_lower == "nasa_tlx":
        return score_nasa_tlx(responses)
    elif instrument_lower == "sus":
        return score_sus(responses)
    elif instrument_lower == "attrakdiff2":
        return score_attrakdiff2(responses)
    elif instrument_lower == "iso_metrics":
        return score_iso_metrics(responses)
    else:
        return None

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

def compute_trial_item_stats(df, trial_stimuli_map, trial_number_map=None):
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
            "stimuli_conditions": stimuli_conditions,
            "trial_number": trial_number_map.get(t_id) if trial_number_map else None,
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
    trial_number_map = {t.trial_id: t.trial_number for t in trials}
    trial_ids = [trial.trial_id for trial in trials]
    trial_stimuli_map = s_repo.get_stimuli_for_trials(trial_ids)

    responses = qr_repo.get_questionnaire_responses_for_trials(trial_ids)

    df = build_response_dataframe(responses)
    if df.empty:
        return {"experiment_id": experiment_id, "participants": {}, "trial_item_stats": {}, "mean_diffs": {}}
    stats = compute_trial_item_stats(df, trial_stimuli_map, trial_number_map)
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
    grouped by stimulus condition, and run N-condition inferential tests per item (RM-ANOVA/Friedman for k≥3, paired t-test/Wilcoxon for k=2).

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
            "<item_name>": {"test_used": str, "main_effect": {"p_value": float, "significant": bool, ...}, "posthoc": [...]} | None
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

        # Build inferential tests (N conditions per item using run_inferential_analysis)
        inferential: dict[str, dict | None] = {}
        if len(conditions) >= 2:
            for item_name in sorted(item_names):
                cond_dict = {
                    cond: condition_item_values[cond].get(item_name, [])
                    for cond in conditions
                    if condition_item_values[cond].get(item_name)
                }
                if len(cond_dict) >= 2 and all(len(v) >= 3 for v in cond_dict.values()):  # n>=3 triggers non-parametric path inside run_inferential_analysis (Shapiro-Wilk needs n>3)
                    inferential[item_name] = run_inferential_analysis(cond_dict)
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