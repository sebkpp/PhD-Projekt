from Backend.db.experiment.experiment_repository import ExperimentRepository
from Backend.db.participant_repository import ParticipantRepository
from Backend.db.study.study_config_repository import create_study_config, get_study_config_by_study_id, \
    update_study_config
from Backend.db.study.study_questionnaire_repository import StudyQuestionnaireRepository
from Backend.db.study.study_repository import StudyRepository
from Backend.db.study.study_stimuli_repository import create_study_stimuli, delete_study_stimuli, \
    get_stimuli_type_id_by_name, get_study_stimuli
from Backend.models import Experiment


def get_all_studies(session):
    repo = StudyRepository(session)
    return repo.get_all()

def get_study_by_id(session, study_id):
    s_repo = StudyRepository(session)
    study = s_repo.get_by_id(study_id)
    study_config = get_study_config_by_study_id(session, study_id)
    study_stimuli = get_study_stimuli(session, study_id)

    sq_repo = StudyQuestionnaireRepository(session)

    # Fragebögen abrufen
    questionnaires = sq_repo.get_by_study_id(study_id)

    stimuli_list = [
        {
            "stimuli_type_id": s.stimuli_type_id,
            "name": getattr(s.stimuli_type, "type_name", None)  # falls Beziehung vorhanden
        }
        for s in study_stimuli
    ]


    if study:
        study.config = study_config
        study._questionnaires = questionnaires  # temporäres Attribut
        study._stimuli = stimuli_list

    return study

def create_study(session, data):
    study_fields = {k: v for k, v in data.items() if k not in ["config", "stimuli", "questionnaires"]}

    s_repo = StudyRepository(session)
    study = s_repo.create(study_fields)

    study_config = create_study_config(session, study.study_id, data.get("config", {}))
    stimuli_data = data.get("stimuli", [])
    for stim in stimuli_data:
        # Falls stim ein dict ist, extrahiere die ID
        if isinstance(stim, dict):
            stimuli_type_id = stim.get("stimuli_type_id")
        else:
            stimuli_type_id = stim
        if stimuli_type_id:
            create_study_stimuli(session, study.study_id, stimuli_type_id)

    questionnaires = data.get("questionnaires", [])
    sq_repo = StudyQuestionnaireRepository(session)
    for idx, q in enumerate(questionnaires):
        sq_repo.create(study.study_id, q["questionnaire_id"], idx)
    session.flush()
    return study

def update_study(session, study_id, data):

    s_repo = StudyRepository(session)
    study = s_repo.get_by_id(study_id)
    study_config = get_study_config_by_study_id(session, study_id)

    if not study:
        return None

    stimuli_data = data.get("stimuli", [])
    if stimuli_data is not None:
        # Alle Stimuli für die Studie löschen
        delete_study_stimuli(session, study_id, None)
        # Neue Stimuli hinzufügen (Existenzprüfung nicht nötig)
        for stimuli_type in stimuli_data:
            if isinstance(stimuli_type, dict):
                stimuli_type_id = stimuli_type.get("stimuli_type_id")
            elif isinstance(stimuli_type, str):
                stimuli_type_id = get_stimuli_type_id_by_name(session, stimuli_type)
            else:
                stimuli_type_id = stimuli_type
            if stimuli_type_id:
                create_study_stimuli(session, study_id, stimuli_type_id)


    # Felder aus config einzeln setzen
    new_study_config_data = data.get("config", {})

    if study_config and new_study_config_data:
        update_study_config(session, study_config.study_config_id, new_study_config_data)

    for key, value in data.items():
        if key not in ["questionnaires", "config", "stimuli"]:
            setattr(study, key, value)

    sq_repo = StudyQuestionnaireRepository(session)
    # Update Questionnaires
    if "questionnaires" in data:
        sq_repo.delete_all_by_study_id(study_id)
        for idx, q in enumerate(data["questionnaires"]):
            sq_repo.create(study_id, q["questionnaire_id"], idx)

    session.flush()
    return study

def delete_study(session, study_id):
    from Backend.models.study.study_config import StudyConfig
    session.query(StudyConfig).filter_by(study_id=study_id).delete()
    repo = StudyRepository(session)
    return repo.delete(study_id)

def get_experiments_by_study(session, study_id):
    repo = ExperimentRepository(session)
    experiments = repo.get_by_study(study_id)
    result = []
    for exp in experiments:
        exp_dict = exp.to_dict()
        # Nur die Trials serialisieren
        exp_dict["trials"] = [trial.to_dict() for trial in exp.trials]
        result.append(exp_dict)
    return result

def get_participants_by_study(session, study_id):
    e_repo = ExperimentRepository(session)
    experiments = e_repo.get_by_study(study_id)
    p_repo = ParticipantRepository(session)

    participants = []
    for exp in experiments:
        participants.extend(p_repo.get_participants_by_experiment(exp.experiment_id))

    return participants

def close_study(session, study_id):
    s_repo = StudyRepository(session)
    study = s_repo.get_by_id(study_id)
    if not study:
        return None
    if study.ended_at is not None:
        return study  # Bereits geschlossen
    s_repo.set_ended_at(study)

    # Alle zugehörigen Experimente ebenfalls abschließen
    e_repo = ExperimentRepository(session)
    experiments = e_repo.get_by_study(study_id)
    for experiment in experiments:
        if isinstance(experiment, Experiment):
            if experiment.completed_at is None:
                e_repo.set_completed_at(experiment)

    return study