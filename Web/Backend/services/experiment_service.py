# from Backend.db.experiment.experiment_questionnaire_repo import ExperimentQuestionnaireRepository
from datetime import datetime, timezone

from Backend.db.experiment.experiment_repository import (
    ExperimentRepository,
)
from Backend.db.questionnaires.questionnaire_respository import QuestionnaireRepository
from Backend.db.trial.trial import TrialRepository
from Backend.db.trial.trial_slot_repository import TrialSlotRepository
from Backend.db.trial.trial_slot_stimulus import TrialSlotStimulusRepository


def create_experiment(session, data):
    repo = ExperimentRepository(session)

    settings = data.get("experimentSettings", {})
    experiment = repo.create(
        settings.get("study_id"),
        settings.get("description"),
        settings.get("researcher")
    );

    experiment_id = experiment.experiment_id
    trial_config = settings.get("trialConfig", {})
    if trial_config:
        t_repo = TrialRepository(session)
        ts_repo = TrialSlotRepository(session)
        tss_repo = TrialSlotStimulusRepository(session)
        for idx, (trial_name, slots) in enumerate(trial_config.items(), start=1):
            trial = t_repo.create(experiment_id, idx)
            trial_id = trial.trial_id
            for slot_idx, (slot_name, slot_data) in enumerate(slots.items(), start=1):
                trial_slot = ts_repo.create(trial_id, slot_idx)
                active_stimuli = slot_data.get("active_stimuli", [])
                for stim_type, stim_data in active_stimuli.items():
                    stimulus_id = int(stim_data.get("selected_stimuli_id"))
                    tss_repo.create(trial_slot.trial_slot_id, stimulus_id)

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