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