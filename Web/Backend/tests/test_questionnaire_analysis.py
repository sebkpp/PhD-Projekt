"""Tests for instrument-aware questionnaire scoring functions."""
import pytest

from Backend.services.data_analysis.questionnaire_analysis_service import (
    score_nasa_tlx,
    score_sus,
    score_attrakdiff2,
    score_iso_metrics,
    score_questionnaire,
)


# ---------------------------------------------------------------------------
# NASA-TLX
# ---------------------------------------------------------------------------

def test_score_nasa_tlx_complete():
    responses = {
        "mental_demand": 80,
        "physical_demand": 60,
        "temporal_demand": 70,
        "performance": 50,
        "effort": 90,
        "frustration": 40,
    }
    result = score_nasa_tlx(responses)
    assert result["total_score"] == pytest.approx(65.0)
    assert result["instrument"] == "nasa_tlx"
    assert result["subscales"] == responses


def test_score_nasa_tlx_partial():
    """Missing subscales are ignored (mean of present ones)."""
    result = score_nasa_tlx({"mental_demand": 80, "effort": 60})
    assert result["total_score"] == pytest.approx(70.0)
    assert result["instrument"] == "nasa_tlx"


def test_score_nasa_tlx_single_subscale():
    result = score_nasa_tlx({"frustration": 100})
    assert result["total_score"] == pytest.approx(100.0)


def test_score_nasa_tlx_empty():
    result = score_nasa_tlx({})
    assert result["total_score"] == pytest.approx(0.0)
    assert result["instrument"] == "nasa_tlx"


def test_score_nasa_tlx_ignores_unknown_keys():
    """Unknown keys that are not NASA-TLX subscales are ignored in scoring."""
    result = score_nasa_tlx({"mental_demand": 50, "unknown_scale": 100})
    assert result["total_score"] == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# SUS
# ---------------------------------------------------------------------------

def test_score_sus_standard():
    # Perfect usability: odd items (1-based 1,3,5,7,9 = 0-based even indices) = 5,
    # even items (1-based 2,4,6,8,10 = 0-based odd indices) = 1
    responses = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(100.0)
    assert result["grade"] == "A"
    assert result["instrument"] == "sus"


def test_score_sus_poor():
    responses = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]  # poor usability
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(0.0)
    assert result["grade"] == "F"


def test_score_sus_grade_b():
    # Construct a response that gives ~75 score
    # For a uniform mid score: odd items 4, even items 2 → (4-1)*2.5=7.5 and (5-2)*2.5=7.5 each → 75
    responses = [4, 2, 4, 2, 4, 2, 4, 2, 4, 2]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(75.0)
    assert result["grade"] == "B"


def test_score_sus_grade_c():
    # odd items 3, even items 3 → (3-1)*2.5=5, (5-3)*2.5=5 → total 50
    responses = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(50.0)
    assert result["grade"] == "C"


def test_score_sus_grade_d():
    # Aim for ~37.5 (>= 35, < 50)
    # odd items 2.5, even items 3.5 is not integer, use: odd=2, even=4
    # (2-1)*2.5=2.5, (5-4)*2.5=2.5 → 25 per pair, 5 pairs → 25. That's F.
    # Let's try odd=2, even=2: (2-1)*2.5=2.5, (5-2)*2.5=7.5 → 50 per pair... no
    # Try odd=2, even=4 → 2.5 + 2.5=5 per pair, 5 pairs → 25 = F
    # Try odd=3, even=4 → 5 + 2.5=7.5 per pair → 37.5 = D
    responses = [3, 4, 3, 4, 3, 4, 3, 4, 3, 4]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(37.5)
    assert result["grade"] == "D"


def test_score_sus_grade_f():
    # odd=1, even=5 → 0 + 0 = 0 per pair → total 0
    responses = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]
    result = score_sus(responses)
    assert result["total_score"] == pytest.approx(0.0)
    assert result["grade"] == "F"


# ---------------------------------------------------------------------------
# AttrakDiff2
# ---------------------------------------------------------------------------

def test_score_attrakdiff2():
    responses = {"PQ": [2, 1, 3], "HQS": [1, 2], "HQI": [3, 3], "ATT": [2]}
    result = score_attrakdiff2(responses)
    assert "PQ" in result["subscales"]
    assert result["subscales"]["PQ"] == pytest.approx(2.0)
    assert result["subscales"]["HQS"] == pytest.approx(1.5)
    assert result["subscales"]["HQI"] == pytest.approx(3.0)
    assert result["subscales"]["ATT"] == pytest.approx(2.0)
    assert "hq_total" in result
    assert result["hq_total"] == pytest.approx(2.25)  # (1.5 + 3.0) / 2
    assert result["instrument"] == "attrakdiff2"


def test_score_attrakdiff2_total_score():
    responses = {"PQ": [2.0], "HQS": [2.0], "HQI": [2.0], "ATT": [2.0]}
    result = score_attrakdiff2(responses)
    assert result["total_score"] == pytest.approx(2.0)


def test_score_attrakdiff2_negative_values():
    responses = {"PQ": [-3, -1], "HQS": [-2], "HQI": [1, -1], "ATT": [0]}
    result = score_attrakdiff2(responses)
    assert result["subscales"]["PQ"] == pytest.approx(-2.0)
    assert result["subscales"]["HQS"] == pytest.approx(-2.0)
    assert result["subscales"]["HQI"] == pytest.approx(0.0)
    assert result["subscales"]["ATT"] == pytest.approx(0.0)
    assert result["instrument"] == "attrakdiff2"


def test_score_attrakdiff2_partial_subscales():
    """Works with only some subscales present."""
    responses = {"PQ": [1, 2], "ATT": [3]}
    result = score_attrakdiff2(responses)
    assert "PQ" in result["subscales"]
    assert "ATT" in result["subscales"]
    assert result["hq_total"] == pytest.approx(0.0)  # no HQS/HQI


# ---------------------------------------------------------------------------
# ISO-Metrics
# ---------------------------------------------------------------------------

def test_score_iso_metrics():
    responses = {"suitability": [3, 4], "self_descriptiveness": [2, 5, 1]}
    result = score_iso_metrics(responses)
    assert result["subscales"]["suitability"] == pytest.approx(3.5)
    assert result["subscales"]["self_descriptiveness"] == pytest.approx(8 / 3, abs=1e-3)
    assert result["instrument"] == "iso_metrics"


def test_score_iso_metrics_total():
    responses = {"a": [4.0], "b": [2.0]}
    result = score_iso_metrics(responses)
    assert result["total_score"] == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Dispatcher: score_questionnaire
# ---------------------------------------------------------------------------

def test_score_questionnaire_dispatcher_nasa_tlx():
    result = score_questionnaire("nasa_tlx", {"mental_demand": 50})
    assert result is not None
    assert result["instrument"] == "nasa_tlx"


def test_score_questionnaire_dispatcher_sus():
    result = score_questionnaire("sus", [3, 3, 3, 3, 3, 3, 3, 3, 3, 3])
    assert result is not None
    assert result["instrument"] == "sus"


def test_score_questionnaire_dispatcher_attrakdiff2():
    result = score_questionnaire("attrakdiff2", {"PQ": [1, 2]})
    assert result is not None
    assert result["instrument"] == "attrakdiff2"


def test_score_questionnaire_dispatcher_iso_metrics():
    result = score_questionnaire("iso_metrics", {"scale_a": [3, 4]})
    assert result is not None
    assert result["instrument"] == "iso_metrics"


def test_score_questionnaire_dispatcher_unknown():
    result = score_questionnaire("unknown_instrument", {})
    assert result is None


def test_score_questionnaire_dispatcher_none_instrument():
    result = score_questionnaire(None, {})
    assert result is None


def test_score_questionnaire_dispatcher_case_insensitive():
    result = score_questionnaire("NASA_TLX", {"mental_demand": 50})
    assert result is not None
    assert result["instrument"] == "nasa_tlx"


# ---------------------------------------------------------------------------
# Helper: mock ORM response object
# ---------------------------------------------------------------------------

def _make_response(participant_id, trial_id, q_id, q_name, item_id, item_name, value):
    from unittest.mock import MagicMock
    r = MagicMock()
    r.participant_id = participant_id
    r.trial_id = trial_id
    r.questionnaire_item_id = item_id
    r.response_value = value
    r.questionnaire_item.questionnaire.questionnaire_id = q_id
    r.questionnaire_item.questionnaire.name = q_name
    r.questionnaire_item.item_name = item_name
    return r


from Backend.services.data_analysis.questionnaire_analysis_service import (
    build_response_dataframe,
    compute_trial_item_stats,
    compute_mean_diffs,
    build_participant_result,
)


# ---------------------------------------------------------------------------
# build_response_dataframe
# ---------------------------------------------------------------------------

def test_build_response_dataframe_happy():
    responses = [
        _make_response(1, 10, 1, "NASA-TLX", 1, "mental_demand", 70.0),
        _make_response(1, 10, 1, "NASA-TLX", 2, "effort", 50.0),
    ]
    df = build_response_dataframe(responses)
    assert len(df) == 2
    assert set(df.columns) >= {"participant_id", "trial_id", "questionnaire_name", "item_name", "response_value"}


def test_build_response_dataframe_empty():
    df = build_response_dataframe([])
    assert df.empty


# ---------------------------------------------------------------------------
# compute_trial_item_stats
# ---------------------------------------------------------------------------

def test_compute_trial_item_stats_happy():
    responses = [
        _make_response(1, 10, 1, "NASA-TLX", 1, "mental_demand", 70.0),
        _make_response(2, 10, 1, "NASA-TLX", 1, "mental_demand", 80.0),
    ]
    df = build_response_dataframe(responses)
    stats = compute_trial_item_stats(df, {10: [{"name": "condA"}]}, {10: 1})
    assert 10 in stats
    assert "NASA-TLX" in stats[10]["questionnaires"]
    items = stats[10]["questionnaires"]["NASA-TLX"]["items"]
    mental_demand_item = next(i for i in items if i["item_name"] == "mental_demand")
    assert mental_demand_item["mean"] == pytest.approx(75.0)


def test_compute_trial_item_stats_trial_number_map_none():
    responses = [_make_response(1, 10, 1, "NASA-TLX", 1, "mental_demand", 60.0)]
    df = build_response_dataframe(responses)
    stats = compute_trial_item_stats(df, {}, trial_number_map=None)
    assert 10 in stats
    assert stats[10]["trial_number"] is None


# ---------------------------------------------------------------------------
# compute_mean_diffs
# ---------------------------------------------------------------------------

def test_compute_mean_diffs_two_trials():
    responses_t1 = [_make_response(1, 1, 1, "Q", 1, "item1", 60.0)]
    responses_t2 = [_make_response(1, 2, 1, "Q", 1, "item1", 80.0)]
    df = build_response_dataframe(responses_t1 + responses_t2)
    stats = compute_trial_item_stats(df, {}, trial_number_map=None)
    diffs = compute_mean_diffs(stats)
    assert "Q" in diffs
    assert len(diffs["Q"]) == 1
    assert abs(diffs["Q"][0]["value"] - 20.0) < 0.01


def test_compute_mean_diffs_single_trial():
    """Single trial -> diffs is empty dict (no pair to compare)."""
    responses = [_make_response(1, 1, 1, "Q", 1, "item1", 50.0)]
    df = build_response_dataframe(responses)
    stats = compute_trial_item_stats(df, {}, trial_number_map=None)
    diffs = compute_mean_diffs(stats)
    assert diffs == {}


# ---------------------------------------------------------------------------
# build_participant_result
# ---------------------------------------------------------------------------

def test_build_participant_result_happy():
    responses = [_make_response(1, 10, 1, "NASA-TLX", 1, "mental_demand", 70.0)]
    result = build_participant_result(responses)
    assert 1 in result
    assert 10 in result[1]
    assert "NASA-TLX" in result[1][10]
    response_values = [r["response_value"] for r in result[1][10]["NASA-TLX"]["responses"]]
    assert 70.0 in response_values


def test_build_participant_result_empty():
    result = build_participant_result([])
    assert result == {}


# ---------------------------------------------------------------------------
# Integration: analyze_experiment_questionnaires
# ---------------------------------------------------------------------------

def test_analyze_experiment_questionnaires_empty(experiment_id):
    """Returns empty structure when experiment has no responses (bug fix path)."""
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.questionnaire_analysis_service import analyze_experiment_questionnaires
    session = SessionLocal()
    result = analyze_experiment_questionnaires(session, experiment_id)
    session.close()
    # The bug fix ensures no crash and returns well-structured empty result
    assert result["experiment_id"] == experiment_id
    assert result["trial_item_stats"] == {}
    assert result["mean_diffs"] == {}


def test_analyze_experiment_questionnaires_happy(
    db_session, experiment_id, participant_id
):
    """Happy path: trial with questionnaire responses returns structured data."""
    from Backend.models.trial.trial import Trial
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.questionnaire_analysis_service import analyze_experiment_questionnaires

    trial = Trial(experiment_id=experiment_id, trial_number=1)
    db_session.add(trial)
    db_session.flush()

    q = Questionnaire(name="NASA-TLX")
    db_session.add(q)
    db_session.flush()
    item = QuestionnaireItem(questionnaire_id=q.questionnaire_id, item_name="mental_demand", order_index=0)
    db_session.add(item)
    db_session.flush()
    db_session.add(QuestionnaireResponse(
        trial_id=trial.trial_id,
        participant_id=participant_id,
        questionnaire_item_id=item.questionnaire_item_id,
        response_value=70.0,
    ))
    db_session.commit()

    session = SessionLocal()
    result = analyze_experiment_questionnaires(session, experiment_id)
    session.close()

    assert result["experiment_id"] == experiment_id
    assert trial.trial_id in result["trial_item_stats"]


# ---------------------------------------------------------------------------
# Integration: analyze_study_questionnaires
# ---------------------------------------------------------------------------

def test_analyze_study_questionnaires_empty(study_id):
    """Returns {} when study has no experiments."""
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.questionnaire_analysis_service import analyze_study_questionnaires
    session = SessionLocal()
    result = analyze_study_questionnaires(session, study_id)
    session.close()
    assert result == {}


def test_analyze_study_questionnaires_two_conditions(
    client, db_session, study_id, participant_id
):
    """Two conditions across experiments returns questionnaire data."""
    from Backend.models.trial.trial import Trial
    from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
    from Backend.models.stimulus import StimulusType, Stimulus
    from Backend.models.trial.trial_slot import TrialSlot
    from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus
    from Backend.db_session import SessionLocal
    from Backend.services.data_analysis.questionnaire_analysis_service import analyze_study_questionnaires

    # Two experiments in the same study
    resp_a = client.post("/experiments/", json={"name": "Exp A", "study_id": study_id})
    resp_b = client.post("/experiments/", json={"name": "Exp B", "study_id": study_id})
    exp_a_id = resp_a.json()["experiment_id"]
    exp_b_id = resp_b.json()["experiment_id"]

    # Shared questionnaire
    q = Questionnaire(name="SUS")
    db_session.add(q)
    db_session.flush()
    item = QuestionnaireItem(questionnaire_id=q.questionnaire_id, item_name="q1", order_index=0)
    db_session.add(item)
    db_session.flush()

    # Stimulus type + stimuli
    st = StimulusType(type_name="condition")
    db_session.add(st)
    db_session.flush()
    stim_a = Stimulus(name="cond_A", stimulus_type_id=st.stimulus_type_id)
    stim_b = Stimulus(name="cond_B", stimulus_type_id=st.stimulus_type_id)
    db_session.add_all([stim_a, stim_b])
    db_session.flush()

    for exp_id, stim, value in [(exp_a_id, stim_a, 3.0), (exp_b_id, stim_b, 4.0)]:
        trial = Trial(experiment_id=exp_id, trial_number=1)
        db_session.add(trial)
        db_session.flush()
        slot = TrialSlot(trial_id=trial.trial_id, slot=1)
        db_session.add(slot)
        db_session.flush()
        db_session.add(TrialSlotStimulus(trial_slot_id=slot.trial_slot_id, stimulus_id=stim.stimulus_id))
        db_session.flush()
        db_session.add(QuestionnaireResponse(
            trial_id=trial.trial_id,
            participant_id=participant_id,
            questionnaire_item_id=item.questionnaire_item_id,
            response_value=value,
        ))

    db_session.commit()

    session = SessionLocal()
    result = analyze_study_questionnaires(session, study_id)
    session.close()

    assert result["study_id"] == study_id
    assert "SUS" in result["questionnaires"]
    sus_data = result["questionnaires"]["SUS"]
    assert "by_condition" in sus_data
    assert len(sus_data["by_condition"]) == 2
    assert "cond_A" in sus_data["by_condition"]
    assert "cond_B" in sus_data["by_condition"]
    assert sus_data["by_condition"]["cond_A"]["q1"]["mean"] == pytest.approx(3.0)
    assert sus_data["by_condition"]["cond_B"]["q1"]["mean"] == pytest.approx(4.0)
