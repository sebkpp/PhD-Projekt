from collections import OrderedDict

from Backend.db.questionnaires.questionnaire_response_repository import (
    QuestionnaireResponseRepository
)
from Backend.db.questionnaires.questionnaire_respository import QuestionnaireRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import TrialParticipantSlot, TrialSlot


def save_questionnaire_responses(session, participant_id: int, trial_id: int, questionnaire_name: str, responses: dict):
    q_repo = QuestionnaireRepository(session)
    questionnaire = q_repo.get_questionnaire_by_name(questionnaire_name)

    if not questionnaire:
        raise ValueError(f"Fragebogen '{questionnaire_name}' nicht gefunden.")

    qr_repo = QuestionnaireResponseRepository(session)

    items = q_repo.get_questionnaire_items(questionnaire.questionnaire_id)
    item_map = {item.item_name: item for item in items}

    for item_name in responses.keys():
        if item_name not in item_map:
            new_item = q_repo.add_questionnaire_item(questionnaire.questionnaire_id, item_name)
            item_map[item_name] = new_item

    for item_name, response_value in responses.items():
        item = item_map[item_name]
        qr_repo.add_questionnaire_response(participant_id, trial_id, item.questionnaire_item_id, response_value)

    session.commit()
    return {"status": "ok", "message": f"{len(responses)} Antworten gespeichert."}

def load_questionnaire_responses(session, participant_id: int, trial_id: int, questionnaire_name: str):
    q_repo = QuestionnaireRepository(session)

    questionnaire = q_repo.get_questionnaire_by_name(questionnaire_name)
    if not questionnaire:
        raise ValueError(f"Fragebogen '{questionnaire_name}' nicht gefunden.")

    qr_repo = QuestionnaireResponseRepository(session)
    items = q_repo.get_questionnaire_items(questionnaire.questionnaire_id)
    item_ids = [item.questionnaire_item_id for item in items]
    responses = qr_repo.get_questionnaire_responses(participant_id, trial_id, item_ids)
    item_id_to_name = {item.questionnaire_item_id: item.item_name for item in items}

    result = {}
    for r in responses:
        item_name = item_id_to_name.get(r.questionnaire_item_id, f"item_{r.questionnaire_item_id}")
        result[item_name] = r.response_value

    return result

def are_all_questionnaires_in_trial_done(session, participant_id: int, trial_id: int) -> bool:
    q_repo = QuestionnaireRepository(session)
    qr_repo = QuestionnaireResponseRepository(session)

    questionnaires = q_repo.get_by_trial_id(trial_id)
    if not questionnaires:
        return False

    for questionnaire in questionnaires:
        items = q_repo.get_questionnaire_items(questionnaire.questionnaire_id)
        item_ids = [item.questionnaire_item_id for item in items]
        responses = qr_repo.get_questionnaire_responses(participant_id, trial_id, item_ids)
        if len(responses) < len(item_ids):
            return False
    return True

def are_all_questionnaires_done(session, participant_id: int, experiment_id: int) -> bool:
    t_repo = TrialRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    for trial in trials:
        trial_id = trial.trial_id if hasattr(trial, "trial_id") else trial["trial_id"]
        if not are_all_questionnaires_in_trial_done(session, participant_id, trial_id):
            return False
    return True


def get_questionnaire_responses_for_experiment(session, experiment_id):
    qr_repo = QuestionnaireResponseRepository(session)
    t_repo = TrialRepository(session)

    trials = t_repo.get_by_experiment_id(experiment_id)
    trial_map = {trial.trial_id: trial for trial in trials}
    trial_ids = list(trial_map.keys())

    trial_slots = session.query(TrialSlot).filter(
        TrialSlot.trial_id.in_(trial_ids)
    ).all()
    slot_id_to_trial_id = {slot.trial_slot_id: slot.trial_id for slot in trial_slots}


    tps_entries = session.query(TrialParticipantSlot).filter(
        TrialParticipantSlot.trial_slot_id.in_(slot_id_to_trial_id.keys())
    ).all()

    tps_map = {}
    for entry in tps_entries:
        trial_id = slot_id_to_trial_id.get(entry.trial_slot_id)
        if trial_id is not None:
            tps_map.setdefault((trial_id, entry.participant_id), []).append(entry.trial_slot_id)

    responses = qr_repo.get_questionnaire_responses_for_trials(trial_ids)
    result = {}
    for r in responses:
        p_id = r.participant_id
        t_id = r.trial_id
        q = r.questionnaire_item.questionnaire
        q_id = q.questionnaire_id
        q_name = q.name

        result.setdefault(p_id, {}).setdefault(t_id, {}).setdefault(q_id, {
            "questionnaire_id": q_id,
            "name": q_name,
            "responses": []
        })["responses"].append({
            "questionnaire_item_id": r.questionnaire_item_id,
            "item_name": r.questionnaire_item.item_name,
            "response_value": r.response_value
        })

    participants = []
    for p_id, trials_dict in result.items():
        participant = {"participant_id": p_id, "trials": []}
        for t_id, questionnaires in trials_dict.items():
            trial_obj = trial_map.get(t_id)
            trial_dict = trial_obj.to_dict() if trial_obj else {}
            slot_ids = tps_map.get((t_id, p_id), [])
            slots = [
                slot for slot in trial_dict.get("slots", [])
                if slot["trial_slot_id"] in slot_ids
            ]
            stimuli = []
            for slot in slots:
                stimuli.extend(slot.get("stimuli", []))
            trial = OrderedDict([
                ("trial_id", t_id),
                ("stimuli", stimuli),
                ("questionnaires", list(questionnaires.values()))
            ])
            participant["trials"].append(trial)
        participants.append(participant)

    return {"participants": participants}