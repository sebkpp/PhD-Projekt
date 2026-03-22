from Backend.db.experiment.experiment_repository import ExperimentRepository
from Backend.db.handover_repository import HandoverRepository
from Backend.db.trial.trial import TrialRepository


def get_handovers_for_trial(session, trial_id):
    repo = HandoverRepository(session)
    return repo.get_handovers_for_trial(trial_id)

def save_handover(session, handover_data):
    repo = HandoverRepository(session)
    return repo.create_handover(handover_data)

def get_handovers_for_experiment(session, experiment_id):
    t_repo = TrialRepository(session)
    trials = t_repo.get_by_experiment_id(experiment_id)
    all_handovers = []
    for trial in trials:
        handovers = get_handovers_for_trial(session, trial.trial_id)
        all_handovers.extend(handovers)
    return all_handovers


def update_handover_phases(session, handover_id: int, patch_data: dict):
    repo = HandoverRepository(session)
    return repo.update_handover_phases(handover_id, patch_data)