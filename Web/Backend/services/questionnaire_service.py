from Backend.db.experiment.experiment_repository import ExperimentRepository
from Backend.db.questionnaires.questionnaire_respository import QuestionnaireRepository
from Backend.db.study.study_questionnaire_repository import StudyQuestionnaireRepository


def create_questionnaire(session, name):
    q_repo = QuestionnaireRepository(session)

    existing = q_repo.get_questionnaire_by_name(name)
    if existing:
        return existing

    return q_repo.create_questionnaire(name)

def add_questionnaire_item(session, questionnaire_id, item_name):
    q_repo = QuestionnaireRepository(session)
    return q_repo.add_questionnaire_item(questionnaire_id, item_name)


def get_questionnaire_by_name(session, name):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_questionnaire_by_name(name)

def get_questionnaire_items(session, questionnaire_id):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_questionnaire_items(questionnaire_id)

def create_questionnaire_with_items(session, name, item_names: list[str]):
    questionnaire = create_questionnaire(session, name)
    for item_name in item_names:
        add_questionnaire_item(session, questionnaire.questionnaire_id, item_name)
    return questionnaire

def get_all_questionnaires(session):
    q_repo = QuestionnaireRepository(session)
    questionnaires = q_repo.get_all_questionnaires()
    return [q.to_dict() for q in questionnaires]

def get_questionnaires_for_experiment(session, experiment_id):
    e_repo = ExperimentRepository(session)
    experiment = e_repo.get_by_id(experiment_id)
    return experiment.questionnaires if experiment else []

def get_questionnaires_by_study_id(session, study_id):
    sq_repo = StudyQuestionnaireRepository(session)
    return sq_repo.get_by_study_id(study_id)

def get_questionnaires_by_trial_id(session, trial_id):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_by_trial_id(trial_id)