# from Backend.db.experiment.experiment_questionnaire_repo import ExperimentQuestionnaireRepository
from datetime import datetime, timezone

from Backend.db.experiment.experiment_repository import (
    ExperimentRepository,
)
from Backend.db.questionnaires.questionnaire_respository import QuestionnaireRepository

def create_experiment(session, data):
    repo = ExperimentRepository(session)

    settings = data.get("experimentSettings", {})
    experiment = repo.create(
        settings.get("study_id"),
        settings.get("description"),
        settings.get("researcher")
    );

    experiment_id = experiment.experiment_id

    return experiment

def save_experiment_questionnaires(session, experiment_id, questionnaire_ids):
    e_repo = ExperimentRepository(session)
    q_repo = QuestionnaireRepository(session)
    experiment = e_repo.get_by_id(experiment_id)
    questionnaires = q_repo.get_questionnaires_by_list_of_ids(questionnaire_ids)
    experiment.questionnaires = questionnaires

def get_experiment_by_id(session, experiment_id):
    repo = ExperimentRepository(session)
    return repo.get_by_id(experiment_id)

def set_experiment_started_at(session, experiment_id):
    repo = ExperimentRepository(session)
    experiment = repo.get_by_id(experiment_id)
    repo.set_started_at(experiment)

def set_experiment_completed_at(session, experiment_id):
    repo = ExperimentRepository(session)
    experiment = repo.get_by_id(experiment_id)
    repo.set_completed_at(experiment)

def get_next_open_experiment(session):
    """
    Returns the oldest open experiment (started_at IS NULL, completed_at IS NULL)
    with its next unfinished trial and slot->gender data.
    Raises ValueError with a code string on all error cases.
    """
    from Backend.models.experiment import Experiment
    from Backend.models.trial.trial import Trial
    from Backend.models.trial.trial_slot import TrialSlot
    from Backend.models.trial.trial_participant_slot import TrialParticipantSlot
    from Backend.models.participant import Participant

    experiment = (
        session.query(Experiment)
        .filter(Experiment.started_at.is_(None), Experiment.completed_at.is_(None))
        .order_by(Experiment.created_at.asc())
        .first()
    )
    if experiment is None:
        raise ValueError("no_open_experiment")

    next_trial = (
        session.query(Trial)
        .filter(
            Trial.experiment_id == experiment.experiment_id,
            Trial.is_finished == False
        )
        .order_by(Trial.trial_number.asc())
        .first()
    )
    if next_trial is None:
        raise ValueError("no_unfinished_trial")

    slots = (
        session.query(TrialSlot.slot, Participant.gender)
        .join(TrialParticipantSlot,
              TrialSlot.trial_slot_id == TrialParticipantSlot.trial_slot_id)
        .join(Participant,
              TrialParticipantSlot.participant_id == Participant.participant_id)
        .filter(TrialSlot.trial_id == next_trial.trial_id)
        .all()
    )
    if len(slots) < 2:
        raise ValueError("slots_not_assigned")

    return {
        "experiment_id": experiment.experiment_id,
        "trial_id": next_trial.trial_id,
        "slots": [{"slot": s.slot, "gender": s.gender} for s in slots],
    }