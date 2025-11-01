from Backend.db.experiment.experiment_repository import ExperimentRepository
from Backend.db.questionnaires.questionnaire_respository import QuestionnaireRepository
from Backend.db.study.study_repository import StudyRepository
from Backend.db.trial.trial import TrialRepository
from Backend.models import Trial
from Backend.services.participant_service import get_participants_by_experiment


def save_trials(session, experiment_id, trials, selected_questionnaires):
    trial_repo = TrialRepository(session)

    for trial_data in trials:

        # save trial to database
        trial_number = trial_data["trial_number"]
        trial = trial_repo.create(experiment_id, trial_number)

    return {
        "status": "ok",
        "message": f"{len(trials)} Trials erfolgreich gespeichert."
    }


def get_trials_for_experiment(session, experiment_id):
    t_repo = TrialRepository(session)
    print(f"Getting trials for experiment {experiment_id}")

    trials = t_repo.get_by_experiment_id(experiment_id)
    return [trial.to_dict() for trial in trials]

def get_trial(session, trial_id: int) -> Trial:
    t_repo = TrialRepository(session)
    trial = t_repo.get_by_id(trial_id)
    return trial

def send_start_signal_to_unity(trial_id):
    print(f"Startsignal für Trial {trial_id} an Unity gesendet")


def send_stop_signal_to_unity(trial_id):
    # Beispiel: UDP, MQTT, WebSocket, Dateisystem-Signal o. ä.
    print(f"Stopping trial {trial_id} and notifying Unity.")

def start_trial(session, trial_id: int):
    trial_repo = TrialRepository(session)
    trial = trial_repo.get_by_id(trial_id)
    if not trial:
        raise ValueError("Trial nicht gefunden")
    experiment_repo = ExperimentRepository(session)
    experiment = experiment_repo.get_by_id(trial.experiment_id)
    if experiment and experiment.started_at is None:
        experiment_repo.set_started_at(experiment)

    study_repo = StudyRepository(session)
    study = study_repo.get_by_id(experiment.study_id)
    if study and study.started_at is None:
        study_repo.set_started_at(study)

def finish_trial(session, trial_id: int):
    t_repo = TrialRepository(session)
    t_repo.set_trial_finished(trial_id)

    trial = t_repo.get_by_id(trial_id)

    experiment_id = trial.experiment_id
    all_trials = t_repo.get_by_experiment_id(experiment_id)
    all_finished = all(t.is_finished for t in all_trials)

    if all_finished:
        experiment_repo = ExperimentRepository(session)
        experiment = experiment_repo.get_by_id(experiment_id)
        if experiment and experiment.completed_at is None:
            experiment_repo.set_completed_at(experiment)

def save_experiment_questionnaires(session, experiment_id, selected_questionnaires):
    e_repo = ExperimentRepository(session)
    experiment = e_repo.get_by_id(experiment_id)
    if experiment:
        q_repo = QuestionnaireRepository(session)
        questionnaires = q_repo.get_questionnaires_by_list_of_ids(selected_questionnaires)
        experiment.questionnaires = questionnaires
        session.commit()


def get_participants_for_trial(session, trial_id):
    t_repo = TrialRepository(session)
    trial = t_repo.get_by_id(trial_id)
    if not trial:
        return []
    return get_participants_by_experiment(session, trial.experiment_id)